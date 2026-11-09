"""Validate subscriber identity fields before building MongoDB writes."""

import base64
import ipaddress
import json
import os
import re
import stat


def identity_fields(values, *, creating=False):
    fields = {}
    patterns = {
        "imsi": r"[0-9]{5,16}",
        "ki": r"[0-9a-fA-F]{32}",
        "opc": r"[0-9a-fA-F]{32}",
        "op": r"[0-9a-fA-F]{32}",
        "amf": r"[0-9a-fA-F]{4}",
    }
    for field, pattern in patterns.items():
        if field not in values:
            continue
        value = values[field]
        if not isinstance(value, str):
            raise ValueError(f"Invalid {field}")
        value = value.strip()
        if value and not re.fullmatch(pattern, value):
            raise ValueError(f"Invalid {field}")
        fields[field] = value
    if fields.get("op") and fields.get("opc"):
        raise ValueError("Enter OP or OPc, not both")
    if creating and not (fields.get("imsi") and fields.get("ki") and (fields.get("op") or fields.get("opc"))):
        raise ValueError("IMSI, subscriber key and one operator key are required")
    if "msisdn" in values:
        if not isinstance(values["msisdn"], str):
            raise ValueError("Invalid MSISDN")
        text = values["msisdn"].strip()
        numbers = [item.strip() for item in text.split(",")] if text else []
        if len(numbers) > 2 or any(not re.fullmatch(r"[0-9]{1,15}", item) for item in numbers):
            raise ValueError("Enter up to two MSISDNs, each with 1 to 15 digits")
        fields["msisdn"] = numbers
    return fields


def policy_fields(values):
    fields = {}
    limits = {"subscriber_status": 1, "operator_determined_barring": 8}
    for direction in ("downlink", "uplink"):
        rate = f"ue_ambr_{direction}"
        unit = f"{rate}_unit"
        limits[rate] = 2147483647
        limits[unit] = 4
    for field, maximum in limits.items():
        value = values.get(field, "")
        if value == "":
            continue
        if not isinstance(value, str) or not re.fullmatch(r"[0-9]{1,10}", value) or int(value) > maximum:
            raise ValueError(f"Invalid {field}")
        fields[field] = int(value)
    for direction in ("downlink", "uplink"):
        rate = f"ue_ambr_{direction}"
        if (rate in fields) != (f"{rate}_unit" in fields):
            raise ValueError(f"Enter both UE-AMBR {direction} value and unit")
        if rate in fields and fields[rate] * 1000 ** fields[f"{rate}_unit"] > 2**64 - 1:
            raise ValueError(f"UE-AMBR {direction} exceeds the supported rate")
    return fields


def session_fields(profile):
    sst = str(profile.get("sst", ""))
    if not re.fullmatch(r"[0-9]{1,3}", sst) or not 1 <= int(sst) <= 255:
        raise ValueError("SST must be between 1 and 255")
    fields = {"sst": int(sst)}
    sd = profile.get("sd") or ""
    if sd:
        if not isinstance(sd, str) or not re.fullmatch(r"[0-9a-fA-F]{6}", sd) or sd.lower() == "ffffff":
            raise ValueError("SD must be six hexadecimal digits other than FFFFFF")
        fields["sd"] = sd.lower()
    for field, allowed in {"session_type": ("1", "2", "3"), "lbo_roaming_allowed": ("0", "1")}.items():
        value = profile.get(field) or ""
        if value:
            if value not in allowed:
                raise ValueError(f"Invalid {field}")
            fields[field] = int(value)
    return fields


def default_slice_selector(values):
    value = values.get("default_slice", "")
    if not isinstance(value, str):
        raise ValueError("Invalid default slice")
    value = value.strip()
    if not value:
        return None
    match = re.fullmatch(r"([0-9]{1,3})(?::([0-9a-fA-F]{6}))?", value)
    if not match:
        raise ValueError("Default slice must be SST or SST:SD")
    fields = session_fields({"sst": match[1], "sd": match[2]})
    return fields["sst"], fields.get("sd")


def session_overrides(values, field):
    raw = values.get(field, "")
    if not isinstance(raw, str) or len(raw) > 16384:
        raise ValueError(f"Invalid {field}")
    if not raw.strip():
        return {}
    try:
        entries = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError(f"{field} must be valid JSON") from error
    if not isinstance(entries, dict):
        raise ValueError(f"{field} must be keyed by SST[:SD]/APN")
    result = {}
    for selector, settings in entries.items():
        slice_id, separator, dnn = selector.partition("/")
        slice_key = default_slice_selector({"default_slice": slice_id})
        if not separator or not slice_key or not re.fullmatch(r"[a-zA-Z0-9_.-]{1,255}", dnn):
            raise ValueError("Invalid session selector")
        sst, sd = slice_key
        key = f"{sst}{':' + sd if sd else ''}/{dnn}"
        if key in result:
            raise ValueError("Duplicate session override")
        result[key] = settings
    return result


def session_address_overrides(values):
    result = {}
    for key, settings in session_overrides(values, "session_addresses").items():
        if not isinstance(settings, dict) or set(settings) - {"ue", "smf"}:
            raise ValueError("Invalid session address entry")
        result[key] = {}
        for endpoint, addresses in settings.items():
            if not isinstance(addresses, dict) or set(addresses) - {"ipv4", "ipv6"}:
                raise ValueError("Use ipv4 or ipv6 address fields")
            result[key][endpoint] = {}
            for family, value in addresses.items():
                if value is not None:
                    if not isinstance(value, str) or "%" in value:
                        raise ValueError("Invalid session IP address")
                    address = ipaddress.ip_address(value)
                    if address.version != int(family[-1]):
                        raise ValueError("Session address does not match its IP version")
                    value = str(address)
                result[key][endpoint][family] = value
    return result



def pcc_rule_overrides(values):
    def integer(value, minimum, maximum):
        if type(value) is not int or not minimum <= value <= maximum:
            raise ValueError("PCC rule number is out of range")
        return {"$numberInt": str(value)}

    result = session_overrides(values, "pcc_rules")
    for rules in result.values():
        if not isinstance(rules, list) or len(rules) > 8:
            raise ValueError("A session supports up to eight PCC rules")
        for rule in rules:
            if not isinstance(rule, dict) or set(rule) != {"flow", "qos"}:
                raise ValueError("Each PCC rule needs flow and qos")
            flows = rule["flow"]
            if not isinstance(flows, list) or not 1 <= len(flows) <= 15:
                raise ValueError("A PCC rule needs one to fifteen flows")
            for flow in flows:
                if not isinstance(flow, dict) or set(flow) != {"direction", "description"}:
                    raise ValueError("Each flow needs direction and description")
                description = flow["description"]
                if not isinstance(description, str) or len(description) > 255 or not re.fullmatch(
                    r"permit out [ -~]+ from [ -~]+ to [ -~]+", description
                ):
                    raise ValueError("Invalid PCC flow description")
                flow["direction"] = integer(flow["direction"], 1, 2)
            qos = rule["qos"]
            if not isinstance(qos, dict) or not {"index", "arp"} <= qos.keys() or qos.keys() - {"index", "arp", "mbr", "gbr"}:
                raise ValueError("PCC QoS requires index and ARP")
            qos["index"] = integer(qos["index"], 1, 255)
            arp = qos["arp"]
            if not isinstance(arp, dict) or set(arp) != {
                "priority_level", "pre_emption_capability", "pre_emption_vulnerability"
            }:
                raise ValueError("PCC ARP requires priority, capability and vulnerability")
            arp["priority_level"] = integer(arp["priority_level"], 1, 15)
            for key in ("pre_emption_capability", "pre_emption_vulnerability"):
                arp[key] = integer(arp[key], 1, 2)
            rates = {}
            for rate_name in ("mbr", "gbr"):
                if rate_name not in qos:
                    continue
                rate = qos[rate_name]
                if not isinstance(rate, dict) or not rate or set(rate) - {"downlink", "uplink"}:
                    raise ValueError("PCC rates must contain downlink or uplink")
                for direction, limit in rate.items():
                    if not isinstance(limit, dict) or set(limit) != {"value", "unit"}:
                        raise ValueError("Each PCC bit rate requires value and unit")
                    value, unit = limit["value"], limit["unit"]
                    limit["value"] = integer(value, 0, 2147483647)
                    limit["unit"] = integer(unit, 0, 4)
                    bits = value * 1000 ** unit
                    if bits > 2**64 - 1:
                        raise ValueError("PCC rate exceeds the supported limit")
                    rates[rate_name, direction] = bits
            for direction in ("downlink", "uplink"):
                if ("mbr", direction) in rates and rates.get(("gbr", direction), 0) > rates["mbr", direction]:
                    raise ValueError("Guaranteed bit rate exceeds maximum bit rate")
    return result



def load_payload(argument):
    if not argument.startswith("file:"):
        return json.loads(base64.b64decode(argument, validate=True))
    path = argument[5:]
    if not re.fullmatch(r"/tmp/opncell-subscriber-[a-zA-Z0-9]+", path):
        raise ValueError("Invalid subscriber payload path")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        metadata = os.fstat(stream.fileno())
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_mode & 0o077:
            raise ValueError("Subscriber payload must be a private regular file")
        payload = stream.read(49153)
        if len(payload) > 49152:
            raise ValueError("Subscriber payload is too large")
        return json.loads(payload)


def mongosh_failure(output, *, operation="save"):
    """Return a useful error without exposing database URIs or subscriber secrets."""
    error = output.lower()
    if "authentication failed" in error or "auth failed" in error:
        return "MongoDB authentication failed. Check the database credentials."
    if "not authorized" in error or "unauthorized" in error:
        return "MongoDB denied access to the subscriber database."
    if any(term in error for term in ("econnrefused", "server selection", "serverselection", "enotfound", "etimedout")):
        return "Could not connect to MongoDB. Check its service and connection settings."
    if "document failed validation" in error:
        return "MongoDB rejected the subscriber because it does not match the database validation rules."
    return f"MongoDB Shell did not confirm the {operation}. Check the subscriber list before retrying."
