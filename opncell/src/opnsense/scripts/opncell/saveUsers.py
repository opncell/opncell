#!/usr/local/bin/python3

import ipaddress
import json
import os
import shutil
import subprocess
import sys

from subscriber_identity import default_slice_selector, identity_fields, load_payload, mongosh_failure, pcc_rule_overrides, policy_fields, session_address_overrides, session_fields


def int32(value):
    number = int(value)
    if not 0 <= number <= 2147483647:
        raise ValueError("Profile number outside supported range")
    return {"$numberInt": str(number)}


def ambr(downlink, uplink, unit):
    return {
        "downlink": {"value": int32(downlink), "unit": int32(unit)},
        "uplink": {"value": int32(uplink), "unit": int32(unit)},
    }


def build_subscriber(payload):
    identity = identity_fields(payload["1"], creating=True)
    policy = policy_fields(payload["1"])
    ue_ambr = ambr(1000000000, 1000000000, 0)
    for direction in ("downlink", "uplink"):
        rate = f"ue_ambr_{direction}"
        if rate in policy:
            ue_ambr[direction] = {"value": int32(policy[rate]), "unit": int32(policy[f"{rate}_unit"])}

    slices = {}
    pcc_overrides = pcc_rule_overrides(payload["1"])
    address_overrides = session_address_overrides(payload["1"])
    for index in range(1, int(payload["count"]) + 1):
        profile = payload[str(index)]
        options = session_fields(profile)
        sst, sd = options["sst"], options.get("sd")
        key = (sst, sd)
        if key not in slices:
            slice_config = {"sst": int32(sst), "default_indicator": not slices, "session": []}
            if sd is not None:
                slice_config["sd"] = sd
            slices[key] = slice_config
        sessions = slices[key]["session"]
        dnn = profile["apn"]
        if not dnn or any(session["name"] == dnn for session in sessions):
            raise ValueError("Missing or duplicate APN within a slice")

        session = {
            "name": dnn,
            "type": int32(options.get("session_type", 3)),
            "qos": {
                "index": int32(profile["QoS"]),
                "arp": {
                    "priority_level": int32(profile["arp_priority"]),
                    "pre_emption_capability": int32(profile["arp_capability"]),
                    "pre_emption_vulnerability": int32(profile["arp_vulnerability"]),
                },
            },
            "ambr": ambr(profile["dl"], profile["ul"], 2),
            "pcc_rule": [],
        }
        if "lbo_roaming_allowed" in options:
            session["lbo_roaming_allowed"] = bool(options["lbo_roaming_allowed"])
        if profile.get("ip"):
            address = ipaddress.ip_address(profile["ip"])
            if options.get("session_type", 3) not in ({4: 1, 6: 2}[address.version], 3):
                raise ValueError("Static IP does not match the session address family")
            session["ue"] = {f"ipv{address.version}": str(address)}
        selector = f"{sst}{':' + sd if sd else ''}/{dnn}"
        for endpoint, addresses in address_overrides.pop(selector, {}).items():
            target = session.setdefault(endpoint, {})
            for family, address in addresses.items():
                if address is None:
                    target.pop(family, None)
                else:
                    if endpoint == "ue" and options.get("session_type", 3) not in (
                        1 if family == "ipv4" else 2, 3
                    ):
                        raise ValueError("UE address conflicts with the session type")
                    target[family] = address
        session["pcc_rule"] = pcc_overrides.pop(selector, [])
        sessions.append(session)
    if pcc_overrides:
        raise ValueError("PCC rules refer to an unassigned session")
    if address_overrides:
        raise ValueError("Address override refers to an unassigned session")
    if not slices:
        raise ValueError("At least one profile is required")

    selected = default_slice_selector(payload["1"])
    if selected is not None:
        if selected not in slices:
            raise ValueError("Default slice is not assigned to the subscriber")
        for key, slice_config in slices.items():
            slice_config["default_indicator"] = key == selected

    return {
        "schema_version": int32(1),
        "imsi": identity["imsi"],
        "msisdn": identity.get("msisdn", []),
        "imeisv": [],
        "mme_host": [],
        "mme_realm": [],
        "purge_flag": [],
        "security": {
            "k": identity["ki"],
            "op": identity.get("op") or None,
            "opc": identity.get("opc") or None,
            "amf": identity.get("amf") or "8000",
        },
        "ambr": ue_ambr,
        "slice": list(slices.values()),
        "access_restriction_data": int32(32),
        "network_access_mode": int32(0),
        "subscriber_status": int32(policy.get("subscriber_status", 0)),
        "operator_determined_barring": int32(policy.get("operator_determined_barring", 0)),
        "subscribed_rau_tau_timer": int32(12),
        "__v": int32(0),
    }


INSERT = """
try {
    const subscribers = db.subscribers;
    subscribers.createIndex({imsi: 1}, {unique: true});
    for (const slice of subscriber.slice) {
        slice._id = new ObjectId();
        for (const session of slice.session) {
            session._id = new ObjectId();
        }
    }
    print(subscribers.insertOne(subscriber).acknowledged ? 'Success' : 'MongoDB did not acknowledge the subscriber insert');
} catch (error) {
    print(error.code === 11000 ? 'Duplicate'
        : error.code === 13 ? 'MongoDB denied access to the subscriber database.'
        : error.code === 121 ? 'MongoDB rejected the subscriber because it does not match the database validation rules.'
        : 'MongoDB rejected the subscriber insert. Check the MongoDB log.');
}
"""


def main():
    try:
        payload = load_payload(sys.argv[1])
        subscriber = build_subscriber(payload)
        uri = os.environ.get("DB_URI") or "mongodb://127.0.0.1:27017/open5gs"
        command = "const subscriber = EJSON.parse(" + json.dumps(json.dumps(subscriber)) + ", {relaxed: false});\n" + INSERT
        mongosh = shutil.which("mongosh")
        if not mongosh and not shutil.which("npx"):
            print(json.dumps("MongoDB Shell (mongosh) is required for subscriber management"))
            return
        shell = [mongosh] if mongosh else ["npx", "mongosh"]
        output = subprocess.run(
            shell + ["--quiet", uri, "--eval", command],
            capture_output=True, text=True, check=False,
        )
        lines = output.stdout.strip().splitlines()
        if output.returncode != 0 or not lines:
            print(json.dumps(mongosh_failure(output.stderr + output.stdout)))
            return
        print(json.dumps(lines[-1].strip()))
    except (IndexError, KeyError, TypeError, ValueError) as error:
        print(json.dumps("Invalid subscriber data: " + str(error)))
    except OSError:
        print(json.dumps("Could not execute MongoDB Shell. Check its installation and permissions."))



if __name__ == "__main__":
    main()
