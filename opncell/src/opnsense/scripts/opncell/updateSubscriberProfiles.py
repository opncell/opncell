#!/usr/local/bin/python3

import json
import os
import shutil
import subprocess
import sys

from subscriber_identity import default_slice_selector, identity_fields, load_payload, mongosh_failure, pcc_rule_overrides, policy_fields, session_address_overrides, session_fields


# Keep Open5GS runtime authentication state outside the edit snapshot and update.
UPDATE = """
const subscriber = db.subscribers.findOne(
    {imsi: input.imsi}, {slice: 1, imsi: 1, msisdn: 1, ambr: 1, subscriber_status: 1, operator_determined_barring: 1, "security.k": 1, "security.opc": 1, "security.op": 1, "security.amf": 1}
);
if (!subscriber || !Array.isArray(subscriber.slice)) {
    print(JSON.stringify({result: "failed", message: "Subscriber or slice data not found"}));
    quit(1);
}
const original = subscriber.slice;
function sliceSelector(slice) {
    return String(Number(slice.sst)) + (slice.sd ? ":" + String(slice.sd).toLowerCase() : "");
}
const defaultSlices = original.filter(slice => slice.default_indicator && slice.session.length);
const security = subscriber.security || {};
const ambr = subscriber.ambr || {};
const downlink = ambr.downlink || {};
const uplink = ambr.uplink || {};
const sessions = original.flatMap(slice => slice.session);
const firstSession = sessions[0];
const ue = (firstSession && firstSession.ue) || {};
const ip = ue.ipv4 || ue.addr || "";
const token = require("crypto").createHash("sha256").update(EJSON.stringify(subscriber)).digest("hex");
function sortedSnapshot(value) {
    if (Array.isArray(value)) return value.map(sortedSnapshot);
    if (value !== null && typeof value === "object") {
        return Object.fromEntries(Object.keys(value).sort().map(key => [key, sortedSnapshot(value[key])]));
    }
    return value;
}
const canonicalToken = require("crypto").createHash("sha256").update(
    JSON.stringify(sortedSnapshot(EJSON.serialize(subscriber, {relaxed: false})))
).digest("hex");
if (input.read) {
    print(JSON.stringify({
        result: "success",
        user: {
            imsi: subscriber.imsi, ki: security.k || "", opc: security.opc || "",
            op: security.op || "", amf: security.amf || "", msisdn: (subscriber.msisdn || []).join(", "),
            ue_ambr_downlink: String(downlink.value == null ? "" : downlink.value),
            ue_ambr_downlink_unit: String(downlink.unit == null ? "" : downlink.unit),
            ue_ambr_uplink: String(uplink.value == null ? "" : uplink.value),
            ue_ambr_uplink_unit: String(uplink.unit == null ? "" : uplink.unit),
            subscriber_status: String(subscriber.subscriber_status == null ? "" : subscriber.subscriber_status),
            operator_determined_barring: String(subscriber.operator_determined_barring == null ? "" : subscriber.operator_determined_barring),
            session_addresses: "", pcc_rules: "",
            default_slice: defaultSlices.length === 1 ? sliceSelector(defaultSlices[0]) : "",
            ip, attached: sessions.map(session => session.name).join(","), edit_token: token
        }
    }));
    quit(0);
}
if (input.token && input.token !== token && input.token !== canonicalToken) {
    print(JSON.stringify({result: "failed", message: "Subscriber changed during edit. Reload and try again."}));
    quit(1);
}
const changes = input.changes || {};
const fields = {};
for (const field of ["subscriber_status", "operator_determined_barring"]) {
    if (typeof changes[field] === "number" &&
        (subscriber[field] == null || changes[field] !== Number(subscriber[field]))) {
        fields[field] = NumberInt(changes[field]);
    }
}
for (const direction of ["downlink", "uplink"]) {
    const rate = "ue_ambr_" + direction;
    const previous = ambr[direction] || {};
    for (const key of ["value", "unit"]) {
        const value = changes[key === "value" ? rate : rate + "_unit"];
        if (typeof value === "number" && (previous[key] == null || value !== Number(previous[key]))) {
            fields["ambr." + direction + "." + key] = NumberInt(value);
        }
    }
}
if (changes.imsi && changes.imsi !== subscriber.imsi) {
    fields.imsi = changes.imsi;
}
if (changes.ki && changes.ki.toUpperCase() !== (security.k || "").toUpperCase()) {
    fields["security.k"] = changes.ki;
}
if (changes.amf && changes.amf.toUpperCase() !== (security.amf || "").toUpperCase()) {
    fields["security.amf"] = changes.amf;
}
if (Array.isArray(changes.msisdn) && JSON.stringify(changes.msisdn) !== JSON.stringify(subscriber.msisdn || [])) {
    fields.msisdn = changes.msisdn;
}
if (changes.op && (security.opc || changes.op.toUpperCase() !== (security.op || "").toUpperCase())) {
    fields["security.op"] = changes.op;
    fields["security.opc"] = null;
}
if (changes.opc && (security.op || changes.opc.toUpperCase() !== (security.opc || "").toUpperCase())) {
    fields["security.opc"] = changes.opc;
    fields["security.op"] = null;
}
const selectedNames = new Set(input.profiles.map(profile => profile.apn));
const managedNames = new Set(input.managedNames);
const currentNames = new Set(sessions.map(session => session.name).filter(name => managedNames.has(name)));
const profilesChanged = !input.token || currentNames.size !== selectedNames.size ||
    [...selectedNames].some(name => !currentNames.has(name));
const slices = original.map(slice => ({
    ...slice,
    session: slice.session
        .filter(session => !profilesChanged || !managedNames.has(session.name) || selectedNames.has(session.name))
        .map(session => ({...session}))
}));
function integer(value) {
    const number = Number(value);
    if (value === "" || !Number.isInteger(number) || number < 0 || number > 2147483647) {
        throw new Error("Invalid profile number");
    }
    return NumberInt(number);
}
for (const profile of profilesChanged ? input.profiles : []) {
    const sst = integer(profile.sst);
    const matching = slices.filter(slice => Number(slice.sst) === Number(sst) &&
        String(slice.sd || "").toLowerCase() === (profile.sd || ""));
    let slice = matching.find(slice => slice.session.some(session => session.name === profile.apn));
    if (!slice && slices.some(candidate => candidate.session.some(session => session.name === profile.apn))) {
        throw new Error("Existing APN belongs to a different slice");
    }
    if (!slice && matching.length > 1) {
        throw new Error("Ambiguous slice");
    }
    slice = slice || matching[0];
    if (!slice) {
        slice = {_id: new ObjectId(), sst, default_indicator: slices.length === 0, session: []};
        if (profile.sd) {
            slice.sd = profile.sd;
        }
        slices.push(slice);
    }
    const index = slice.session.findIndex(session => session.name === profile.apn);
    const session = index === -1
        ? {_id: new ObjectId(), name: profile.apn, type: NumberInt(3), pcc_rule: []}
        : slice.session[index];
    const updated = {
        ...session,
        ...(profile.session_type ? {type: NumberInt(profile.session_type)} : {}),
        ...(typeof profile.lbo_roaming_allowed === "number" ? {lbo_roaming_allowed: Boolean(profile.lbo_roaming_allowed)} : {}),
        qos: {
            ...session.qos,
            index: integer(profile.QoS),
            arp: {
                ...(session.qos && session.qos.arp),
                priority_level: integer(profile.arp_priority),
                pre_emption_capability: integer(profile.arp_capability),
                pre_emption_vulnerability: integer(profile.arp_vulnerability)
            }
        },
        ambr: {
            ...session.ambr,
            downlink: {value: integer(profile.dl), unit: NumberInt(2)},
            uplink: {value: integer(profile.ul), unit: NumberInt(2)}
        }
    };
    if (index === -1) {
        slice.session.push(updated);
    } else {
        slice.session[index] = updated;
    }
}
const ipChanged = typeof changes.ip === "string" && changes.ip !== ip;
if (ipChanged) {
    const target = slices.flatMap(slice => slice.session)[0];
    if (!target) {
        throw new Error("A session is required for a static address");
    }
    target.ue = {...target.ue};
    delete target.ue.addr;
    delete target.ue.ipv4;
    if (changes.ip) {
        target.ue.ipv4 = changes.ip;
    }
}
let addressesChanged = false;
for (const [selector, settings] of Object.entries(changes.session_addresses || {})) {
    const matches = slices.flatMap(slice => slice.session.filter(
        session => sliceSelector(slice) + "/" + session.name === selector
    ));
    if (matches.length !== 1) {
        print(JSON.stringify({result: "failed", message: "Address override must identify one assigned session"}));
        quit(1);
    }
    const session = matches[0];
    for (const [endpoint, addresses] of Object.entries(settings)) {
        const updated = {...session[endpoint]};
        for (const [family, address] of Object.entries(addresses)) {
            const type = Number(session.type || 3);
            if (endpoint === "ue" && address !== null &&
                type !== 3 && type !== (family === "ipv4" ? 1 : 2)) {
                print(JSON.stringify({result: "failed", message: "UE address conflicts with the session type"}));
                quit(1);
            }
            if (endpoint === "ue" && family === "ipv4") {
                delete updated.addr;
            }
            if (address === null) {
                delete updated[family];
            } else {
                updated[family] = address;
            }
        }
        if (JSON.stringify(updated) !== JSON.stringify(session[endpoint] || {})) {
            session[endpoint] = updated;
            addressesChanged = true;
        }
    }
}
let pccChanged = false;
for (const [selector, rules] of Object.entries(changes.pcc_rules || {})) {
    const matches = slices.flatMap(slice => slice.session.filter(
        session => sliceSelector(slice) + "/" + session.name === selector
    ));
    if (matches.length !== 1) {
        print(JSON.stringify({result: "failed", message: "PCC rules must identify one assigned session"}));
        quit(1);
    }
    const session = matches[0];
    const updated = EJSON.deserialize(rules, {relaxed: false});
    if (EJSON.stringify(updated) !== EJSON.stringify(session.pcc_rule || [])) {
        session.pcc_rule = updated;
        pccChanged = true;
    }
}
let defaultChanged = false;
if (changes.default_slice) {
    const [sst, sd] = changes.default_slice;
    const target = String(sst) + (sd ? ":" + sd : "");
    const matches = slices.filter(slice => slice.session.length && sliceSelector(slice) === target);
    if (matches.length !== 1) {
        print(JSON.stringify({result: "failed", message: "Default slice must identify one assigned slice"}));
        quit(1);
    }
    for (const slice of slices) {
        const selected = slice === matches[0];
        if (Boolean(slice.default_indicator) !== selected) {
            slice.default_indicator = selected;
            defaultChanged = true;
        }
    }
}
if (profilesChanged || ipChanged || addressesChanged || pccChanged || defaultChanged) {
    fields.slice = slices;
}
try {
    const filter = {
        _id: subscriber._id, imsi: subscriber.imsi, slice: original,
        "security.k": security.k === undefined ? null : security.k,
        "security.opc": security.opc === undefined ? null : security.opc,
        "security.op": security.op === undefined ? null : security.op,
        "security.amf": security.amf === undefined ? null : security.amf,
        msisdn: subscriber.msisdn === undefined ? null : subscriber.msisdn,
        ambr: subscriber.ambr === undefined ? null : subscriber.ambr,
        subscriber_status: subscriber.subscriber_status === undefined ? null : subscriber.subscriber_status,
        operator_determined_barring: subscriber.operator_determined_barring === undefined ? null : subscriber.operator_determined_barring
    };
    const matched = Object.keys(fields).length === 0 ||
        db.subscribers.updateOne(filter, {$set: fields}).matchedCount === 1;
    print(JSON.stringify(matched
        ? {result: "success"}
        : {result: "failed", message: "Subscriber changed during edit. Reload and try again."}));
} catch (error) {
    print(JSON.stringify({result: "failed", message: error.code === 11000
        ? "The requested IMSI already exists"
        : error.code === 13 ? "MongoDB denied access to the subscriber database."
        : error.code === 121 ? "MongoDB rejected the subscriber because it does not match the database validation rules."
        : "MongoDB rejected the subscriber update. Check the MongoDB log."}));
}
"""


def main():
    try:
        payload = load_payload(sys.argv[1])
        if "changes" in payload:
            changes = payload["changes"]
            try:
                payload["changes"] = {**identity_fields(changes), **policy_fields(changes)}
                pcc_rules = pcc_rule_overrides(changes)
                if pcc_rules:
                    payload["changes"]["pcc_rules"] = pcc_rules
                addresses = session_address_overrides(changes)
                if addresses:
                    payload["changes"]["session_addresses"] = addresses
                selected = default_slice_selector(changes)
                if selected is not None:
                    payload["changes"]["default_slice"] = selected
            except ValueError as error:
                print(json.dumps({"result": "failed", "message": str(error)}))
                return
            if "ip" in changes:
                payload["changes"]["ip"] = changes["ip"]
        if "profiles" in payload:
            payload["profiles"] = [
                {**profile, **session_fields(profile)} for profile in payload["profiles"]
            ]
        uri = os.environ.get("DB_URI") or "mongodb://127.0.0.1:27017/open5gs"
        command = "const input = " + json.dumps(payload) + ";\n" + UPDATE
        mongosh = shutil.which("mongosh")
        if not mongosh and not shutil.which("npx"):
            print(json.dumps({"result": "failed", "message": "MongoDB Shell (mongosh) is required for subscriber management"}))
            return
        shell = [mongosh] if mongosh else ["npx", "mongosh"]
        output = subprocess.run(
            shell + ["--quiet", uri, "--eval", command],
            capture_output=True, text=True, check=False,
        )
        lines = output.stdout.strip().splitlines()
        if not lines:
            print(json.dumps({"result": "failed", "message": mongosh_failure(output.stderr)}))
            return
        result = json.loads(lines[-1])
        print(json.dumps(result))
    except (IndexError, ValueError):
        print(json.dumps({"result": "failed", "message": "MongoDB Shell returned an invalid response. Reload the subscriber before retrying."}))
    except OSError:
        print(json.dumps({"result": "failed", "message": "Could not execute MongoDB Shell. Check its installation and permissions."}))


if __name__ == "__main__":
    main()
