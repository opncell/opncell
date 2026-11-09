import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'opncell/src/opnsense/scripts/opncell'))
import read_subscriber as reader


class SubscriberEditReadTests(unittest.TestCase):
    def test_one_projected_query_and_edit_fields(self):
        calls = []
        doc = {'imsi': '001010000000001', 'security': {'k': '11'*16, 'opc': '22'*16},
               'slice': [{'sst': 1, 'default_indicator': True, 'session': [
                   {'name': 'internet', 'ue': {'ipv4': '10.0.0.5'}, 'pcc_rule': []}]}]}
        class Client:
            def __init__(self, uri, **options): self.open5gs = self; self.subscribers = self
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def find_one(self, query, projection): calls.append((query, projection)); return doc
        with patch.object(reader, 'snapshot_token', return_value='token'):
            result = reader.read_subscriber(doc['imsi'], Client)
        self.assertEqual(result['result'], 'success')
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], {'imsi': doc['imsi']})
        self.assertNotIn('security.sqn', calls[0][1])
        self.assertEqual(result['user']['ip'], '10.0.0.5')
        self.assertEqual(result['user']['attached'], 'internet')
        self.assertEqual(result['user']['default_slice'], '1')
        self.assertEqual(result['user']['edit_token'], 'token')

    def test_invalid_imsi_does_not_connect(self):
        def connect(*args, **kwargs): self.fail('Invalid IMSI reached database')
        self.assertEqual(reader.read_subscriber('bad', connect)['result'], 'failed')

    def test_missing_subscriber_and_database_failure(self):
        class Client:
            def __init__(self, *args, **kwargs): self.open5gs = self; self.subscribers = self
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def find_one(self, *args): return None
        self.assertEqual(reader.read_subscriber('001010000000001', Client)['result'], 'failed')
        def connect(*args, **kwargs): raise RuntimeError('offline')
        with self.assertRaises(RuntimeError): reader.read_subscriber('001010000000001', connect)


if __name__ == '__main__': unittest.main()
