#!/usr/local/bin/python3.13 -S
"""Export provisioning fields; omit authentication counters and runtime state."""
import json
import sys
sys.path.insert(0, '/usr/local/share/opncell-pymongo')

FIELDS = ('imsi', 'ki', 'opc', 'op', 'amf', 'msisdn', 'profiles',
          'ue_ambr_downlink', 'ue_ambr_downlink_unit', 'ue_ambr_uplink', 'ue_ambr_uplink_unit',
          'subscriber_status', 'operator_determined_barring', 'default_slice', 'session_addresses', 'pcc_rules')


def integer_text(value):
    # Legacy documents can store integer policy values as BSON doubles.
    # Preserve nonintegral values so normal validation rejects them.
    if value is None:
        return ''
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def provisioning_rules(value):
    # MongoDB adds nested object IDs; they are not provisioning inputs.
    if isinstance(value, dict):
        return {key: provisioning_rules(item) for key, item in value.items() if key != '_id'}
    if isinstance(value, list):
        return [provisioning_rules(item) for item in value]
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def export_row(doc):
    row = dict.fromkeys(FIELDS, '')
    row['imsi'] = str(doc['imsi'])
    for field, key in (('ki', 'k'), ('opc', 'opc'), ('op', 'op'), ('amf', 'amf')):
        row[field] = doc.get('security', {}).get(key) or ''
    row['msisdn'] = ','.join(doc.get('msisdn', []))
    for direction in ('downlink', 'uplink'):
        rate = doc.get('ambr', {}).get(direction, {})
        row['ue_ambr_' + direction] = integer_text(rate.get('value'))
        row['ue_ambr_' + direction + '_unit'] = integer_text(rate.get('unit'))
    for field in ('subscriber_status', 'operator_determined_barring'):
        row[field] = integer_text(doc.get(field))
    profiles, addresses, rules, defaults = [], {}, {}, []
    for slice_ in doc.get('slice', []):
        selector = integer_text(slice_['sst']) + (':' + slice_['sd'].lower() if slice_.get('sd') else '')
        if slice_.get('default_indicator'):
            defaults.append(selector)
        for session in slice_.get('session', []):
            key = selector + '/' + session['name']
            profiles.append(key)
            endpoints = {}
            for endpoint in ('ue', 'smf'):
                value = session.get(endpoint, {})
                value = {family: value[family] for family in ('ipv4', 'ipv6') if value.get(family)}
                if value:
                    endpoints[endpoint] = value
            if endpoints:
                addresses[key] = endpoints
            if session.get('pcc_rule'):
                rules[key] = provisioning_rules(session['pcc_rule'])
    if len(defaults) == 1:
        row['default_slice'] = defaults[0]
    for field, value in (('profiles', profiles), ('session_addresses', addresses), ('pcc_rules', rules)):
        row[field] = json.dumps(value, separators=(',', ':'))
    return row


def fetch_export(client_factory=None):
    if client_factory is None:
        from pymongo import MongoClient
        client_factory = MongoClient
    projection = {'_id': 0, 'imsi': 1, 'security.k': 1, 'security.opc': 1, 'security.op': 1,
                  'security.amf': 1, 'msisdn': 1, 'ambr': 1, 'subscriber_status': 1,
                  'operator_determined_barring': 1, 'slice': 1}
    with client_factory('mongodb://127.0.0.1:27017/open5gs', serverSelectionTimeoutMS=3000,
                        connectTimeoutMS=3000, socketTimeoutMS=5000) as client:
        return [export_row(doc) for doc in client.open5gs.subscribers.find({}, projection).sort('imsi', 1)]


if __name__ == '__main__':
    try:
        print(json.dumps({'status': 'ok', 'fields': FIELDS, 'rows': fetch_export()}))
    except Exception as error:
        print('Cannot export subscribers: ' + type(error).__name__, file=sys.stderr)
        sys.exit(1)
