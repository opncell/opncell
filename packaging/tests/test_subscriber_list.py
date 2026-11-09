import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[2] / 'opncell/src/opnsense/scripts/opncell/showUsers.py'
spec = importlib.util.spec_from_file_location('list_users', SCRIPT)
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)


class SubscriberReadTests(unittest.TestCase):
    def test_one_query_preserves_imsi_and_omits_secrets(self):
        calls = []
        class Client:
            def __init__(self, uri, **options):
                calls.append(('connect', uri, options))
                self.open5gs = self
                self.subscribers = self
            def __enter__(self): return self
            def __exit__(self, *args): calls.append(('close',))
            def find(self, filter_, projection):
                calls.append(('find', filter_, projection))
                return [{'imsi': '001010000000001', 'security': {'k': 'secret'},
                         'slice': [{'session': [{'name': 'internet'}, {'name': 'ims'}]}]}]
        rows = s.fetch_users(Client)
        self.assertEqual(rows, [{'imsi': '001010000000001', 'apn': 'internet,ims'}])
        self.assertNotIn('security', str(calls))
        self.assertEqual(sum(call[0] == 'find' for call in calls), 1)
        self.assertEqual(calls[-1], ('close',))

    def test_database_error_propagates_instead_of_empty_success(self):
        def failed(*args, **kwargs): raise RuntimeError('database unavailable')
        with self.assertRaises(RuntimeError):
            s.fetch_users(failed)


if __name__ == '__main__':
    unittest.main()
