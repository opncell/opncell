#!/usr/local/bin/python3.13 -S
"""Read subscriber-list fields directly, without launching a JavaScript shell."""
import json
import sys

# Private client modules do not shadow the OPNsense Python environment.
sys.path.insert(0, "/usr/local/share/opncell-pymongo")


def fetch_users(client_factory=None):
    if client_factory is None:
        from pymongo import MongoClient
        client_factory = MongoClient
    with client_factory('mongodb://127.0.0.1:27017/open5gs', serverSelectionTimeoutMS=3000,
                        connectTimeoutMS=3000, socketTimeoutMS=5000) as client:
        rows = client.open5gs.subscribers.find({}, {'_id': 0, 'imsi': 1, 'slice.session.name': 1})
        result = []
        for doc in rows:
            names = [session['name'] for slice_ in doc.get('slice', [])
                     for session in slice_.get('session', []) if isinstance(session.get('name'), str)]
            result.append({'imsi': str(doc['imsi']), 'apn': ','.join(names)})
        return result


if __name__ == '__main__':
    try:
        print(json.dumps(fetch_users()))
    except Exception as exc:
        # Database failures must not masquerade as a successfully empty list.
        print('Cannot read subscriber list: ' + type(exc).__name__, file=sys.stderr)
        sys.exit(1)
