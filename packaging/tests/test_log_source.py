from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'opncell/src/opnsense/scripts/opncell'))
from log_source import resolve_log
from cleanup_log_links import cleanup


class LogSources(unittest.TestCase):
    def test_running_daemon_overrides_default(self):
        self.assertEqual(resolve_log('mme', '/usr/local/bin/open5gs-mmed -l /var/log/custom/mme.log -D'), Path('/var/log/custom/mme.log'))
        self.assertEqual(resolve_log('mongod', '/usr/local/bin/mongod --logpath /var/db/mongodb/mongod.log --fork'), Path('/var/db/mongodb/mongod.log'))
        self.assertEqual(resolve_log('hss', ''), Path('/var/log/opncell/hss.log'))
        with self.assertRaises(ValueError):
            resolve_log('../etc/passwd', '')

    def test_cleanup_preserves_targets_and_unknown_links(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            old = '/usr/ports/open5gs/install/var/log/open5gs/mme.log'
            (root / 'mme.log').symlink_to(old)
            (root / 'hss.log').symlink_to('/custom/hss.log')
            report = root / 'backup/links.json'
            cleanup(root, '', report)
            self.assertFalse((root / 'mme.log').is_symlink())
            self.assertTrue((root / 'hss.log').is_symlink())
            self.assertIn(old, report.read_text())

    def test_cleanup_skips_referenced_directory(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'mme.log').symlink_to('/usr/ports/open5gs/install/var/log/open5gs/mme.log')
            cleanup(root, str(root / 'mme.log'), root / 'backup.json')
            self.assertTrue((root / 'mme.log').is_symlink())
