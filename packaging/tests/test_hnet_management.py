import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

scripts = Path(__file__).resolve().parents[2] / 'opncell/src/opnsense/scripts/opncell'
sys.path.insert(0, str(scripts))
import hnet_management as h

PHRASE = 'test-only bundle passphrase 123'

def key(scheme=2):
    command = (['openssl', 'genpkey', '-algorithm', 'X25519'] if scheme == 1 else
               ['openssl', 'ecparam', '-name', 'prime256v1', '-genkey', '-noout'])
    return subprocess.check_output(command, stderr=subprocess.DEVNULL)

class HnetManagementTests(unittest.TestCase):
    def setUp(self):
        try:
            import yaml
        except ImportError:
            self.skipTest('PyYAML required for Hnet transaction integration tests')
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.calls = []
        self.running = True
        def runtime(action):
            self.calls.append(action)
            return self.running if action == 'status' else True
        self.manager = h.HnetManager(self.root, runtime)
        self.manager.directory.mkdir(parents=True)
        self.private = key()
        (self.manager.directory / 'original.key').write_bytes(self.private)
        self.config = {'logger': {'file': {'path': '/operator/log'}}, 'udm': {'sbi': {'operator': 'preserve'},
                       'hnet': [{'id': 1, 'scheme': 2, 'key': '/usr/local/etc/open5gs/hnet/original.key'}]}}
        self.manager.config.write_text(json.dumps(self.config))

    def bundle(self, private=None, key_id=1, scheme=2):
        private = private or key(scheme)
        public = h.material(private, scheme)
        return h.encrypt_bundle([{'id': key_id, 'scheme': scheme, 'private_key': private.decode(),
                                  'fingerprint': public['fingerprint']}], PHRASE)

    def plan(self, bundle):
        return self.manager.handle({'operation': 'plan', 'bundle': bundle, 'passphrase': PHRASE})

    def apply(self, bundle, plan, replace=False):
        return self.manager.handle({'operation': 'import', 'bundle': bundle, 'passphrase': PHRASE,
                                    'state': plan['state'], 'replace_conflicts': replace})

    def test_encryption_round_trip_wrong_passphrase_and_tampering(self):
        bundle = self.bundle(self.private)
        self.assertNotIn('PRIVATE KEY', json.dumps(bundle))
        self.assertEqual(h.decrypt_bundle(bundle, PHRASE)[0]['private_key'].encode(), self.private)
        for broken, phrase in ((bundle, PHRASE + '!'), ({**bundle, 'payload': bundle['payload'][:-4]+'AAAA'}, PHRASE),
                              ({**bundle, 'iterations': 1}, PHRASE)):
            with self.assertRaisesRegex(ValueError, 'Incorrect passphrase'):
                h.decrypt_bundle(broken, phrase)
        for phrase in ('short', 'long enough\nwith newline'):
            with self.assertRaises(ValueError):
                h.encrypt_bundle([], phrase)

    def test_rejects_scheme_mismatch_and_duplicate_ids(self):
        for private, scheme in ((key(1), 2), (key(2), 1)):
            with self.assertRaisesRegex(ValueError, 'protection scheme'):
                h.material(private, scheme)
        item = {'id': 1, 'scheme': 2, 'private_key': self.private.decode(),
                'fingerprint': h.material(self.private, 2)['fingerprint']}
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            h.decrypt_bundle(h.encrypt_bundle([item, item], PHRASE), PHRASE)
        for invalid in (True, 0, 256, 1.5, '1'):
            with self.assertRaises(ValueError): h.number(invalid)

    def test_noop_import_does_not_restart_or_rotate_keys(self):
        bundle = self.bundle(self.private)
        plan = self.plan(bundle)
        self.assertEqual(plan['entries'][0]['action'], 'unchanged')
        result = self.apply(bundle, plan)
        self.assertFalse(result['udm_restarted'])
        self.assertNotIn('restart', self.calls)
        self.assertEqual((self.manager.directory/'original.key').read_bytes(), self.private)
        self.assertEqual(self.manager.config.read_text(), json.dumps(self.config))

    def test_conflict_requires_approval_and_detects_stale_preview(self):
        bundle = self.bundle()
        plan = self.plan(bundle)
        self.assertEqual(plan['entries'][0]['action'], 'replace')
        with self.assertRaisesRegex(ValueError, 'explicit replacement'):
            self.apply(bundle, plan)
        (self.manager.directory/'original.key').write_bytes(key())
        with self.assertRaisesRegex(ValueError, 'changed since preview'):
            self.apply(bundle, plan, True)
        self.assertNotIn('restart', self.calls)
        self.assertFalse(self.manager.backups.exists())

    def test_import_add_retains_other_keys_and_config(self):
        bundle = self.bundle(key_id=7, scheme=1)
        plan = self.plan(bundle)
        self.assertEqual(plan['retained_ids'], [1])
        result = self.apply(bundle, plan)
        config, entries = self.manager.load()
        self.assertEqual([e['id'] for e in entries], [1, 7])
        self.assertEqual(config['logger'], self.config['logger'])
        self.assertEqual(config['udm']['sbi'], self.config['udm']['sbi'])
        self.assertEqual((self.manager.directory/'original.key').read_bytes(), self.private)
        self.assertEqual((Path(result['backup'])/'hnet.tar.gz').stat().st_mode & 0o777, 0o600)
        self.assertEqual((self.manager.public/'hnet_pubkey_7.pub.hex').read_text(), h.material(
            self.manager.read_private(entries[1]['key']), 1)['hex'])
        self.assertTrue(result['udm_restarted'])

    def test_replacement_deletes_old_file_after_success(self):
        bundle = self.bundle()
        result = self.apply(bundle, self.plan(bundle), True)
        self.assertTrue(result['udm_restarted'])
        self.assertFalse((self.manager.directory/'original.key').exists())
        _, entries = self.manager.load()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['id'], 1)
        self.assertNotEqual(h.material(self.manager.read_private(entries[0]['key']), 2)['fingerprint'],
                            h.material(self.private, 2)['fingerprint'])

    def test_failed_restart_restores_reference_and_private_key(self):
        self.manager.runtime = lambda action: action == 'status'
        bundle = self.bundle()
        with self.assertRaisesRegex(ValueError, 'previous configuration restored'):
            self.apply(bundle, self.plan(bundle), True)
        self.assertEqual(self.manager.load()[0], self.config)
        self.assertEqual(list(self.manager.directory.glob('*.key')), [self.manager.directory/'original.key'])
        self.assertEqual((self.manager.directory/'original.key').read_bytes(), self.private)

    def test_delete_last_key_removes_reference_and_public_exports(self):
        self.manager.refresh(self.config['udm']['hnet'])
        fingerprint = h.material(self.private, 2)['fingerprint']
        with self.assertRaisesRegex(ValueError, 'changed'):
            self.manager.handle({'operation':'delete','id':1,'fingerprint':'stale'})
        result = self.manager.handle({'operation':'delete','id':1,'fingerprint':fingerprint})
        self.assertEqual(self.manager.load()[1], [])
        self.assertEqual(list(self.manager.directory.glob('*.key')), [])
        self.assertEqual(list(self.manager.public.glob('hnet_pubkey_*')), [])
        self.assertTrue((Path(result['backup'])/'hnet.tar.gz').is_file())

    def test_stopped_udm_is_not_started(self):
        self.running = False
        bundle = self.bundle(key_id=2)
        result = self.apply(bundle, self.plan(bundle))
        self.assertFalse(result['udm_restarted'])
        self.assertNotIn('restart', self.calls)

    def test_generation_reuses_transaction_and_refreshes_runtime(self):
        result = self.manager.handle({'operation':'generate','scheme':1})
        self.assertEqual((result['id'], result['scheme']), (2,1))
        self.assertEqual(self.manager.load()[0]['udm']['sbi'], self.config['udm']['sbi'])
        self.assertEqual(len(result['public_key_hex']), 64)
        self.assertIn('restart', self.calls)
