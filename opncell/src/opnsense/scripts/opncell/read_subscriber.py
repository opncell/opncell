#!/usr/local/bin/python3.13 -S
"""Load one edit snapshot without starting MongoDB Shell."""
import hashlib
import json
import re
import sys
sys.path.insert(0, '/usr/local/share/opncell-pymongo')
from export_subscribers import export_row

PROJECTION = {'slice': 1, 'imsi': 1, 'msisdn': 1, 'ambr': 1, 'subscriber_status': 1,
              'operator_determined_barring': 1, 'security.k': 1, 'security.opc': 1,
              'security.op': 1, 'security.amf': 1}


def snapshot_token(doc):
    from bson.json_util import dumps, CANONICAL_JSON_OPTIONS
    encoded = dumps(doc, json_options=CANONICAL_JSON_OPTIONS, sort_keys=True,
                    separators=(',', ':'), ensure_ascii=False)
    return hashlib.sha256(encoded.encode('utf-8')).hexdigest()


def read_subscriber(imsi, client_factory=None):
    if not isinstance(imsi, str) or not re.fullmatch(r'[0-9]{5,16}', imsi):
        return {'result': 'failed', 'message': 'Invalid IMSI'}
    if client_factory is None:
        from pymongo import MongoClient
        client_factory = MongoClient
    with client_factory('mongodb://127.0.0.1:27017/open5gs', serverSelectionTimeoutMS=3000,
                        connectTimeoutMS=3000, socketTimeoutMS=5000) as client:
        doc = client.open5gs.subscribers.find_one({'imsi': imsi}, PROJECTION)
    if not doc or not isinstance(doc.get('slice'), list):
        return {'result': 'failed', 'message': 'Subscriber or slice data not found'}
    user = export_row(doc)
    user.pop('profiles', None)
    sessions = [session for slice_ in doc['slice'] for session in slice_.get('session', [])]
    user['attached'] = ','.join(session['name'] for session in sessions)
    ue = sessions[0].get('ue', {}) if sessions else {}
    user['ip'] = ue.get('ipv4') or ue.get('addr') or ''
    user['edit_token'] = snapshot_token(doc)
    return {'result': 'success', 'user': user}


if __name__ == '__main__':
    try:
        print(json.dumps(read_subscriber(sys.argv[1] if len(sys.argv) == 2 else '')))
    except Exception as error:
        print(json.dumps({'result': 'failed', 'message': 'Could not load subscriber. Check MongoDB and retry.'}))
        print('Subscriber read failed: ' + type(error).__name__, file=sys.stderr)
        sys.exit(1)
