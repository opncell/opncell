import importlib.util
import os
from pathlib import Path
import tempfile
import sys
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[2] / 'opncell/src/opnsense/scripts/opncell/clear_log.py'
sys.path.insert(0, str(SCRIPT.parent))
spec = importlib.util.spec_from_file_location('clear_log', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ClearLogTests(unittest.TestCase):
    def test_open_writer_keeps_inode_and_appends_after_clear(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'mme.log'
            with path.open('a') as writer:
                writer.write('old record\n')
                writer.flush()
                inode = path.stat().st_ino
                module.clear_log('mme', Path(directory))
                writer.write('new record\n')
                writer.flush()
            self.assertEqual(path.stat().st_ino, inode)
            self.assertEqual(path.read_text(), 'new record\n')

    def test_history_cleared_without_touching_other_daemons(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'mme').mkdir()
            history = root / 'mme/mme_20261109.log'
            history.write_text('history')
            (root / 'hss.log').write_text('keep')
            module.clear_log('mme', root)
            self.assertEqual(history.read_text(), '')
            self.assertEqual((root / 'hss.log').read_text(), 'keep')

    def test_reject_unknown_scope_symlink_and_missing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / 'protected'
            target.write_text('keep')
            (root / 'mme.log').symlink_to(target)
            with self.assertRaises(OSError):
                module.clear_log('mme', root)
            with self.assertRaises(ValueError):
                module.clear_log('../protected', root)
            with self.assertRaises(FileNotFoundError):
                module.clear_log('hss', root)
            self.assertEqual(target.read_text(), 'keep')

    def test_clear_resolves_mongo_destination_instead_of_stale_viewer_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            active = root / 'database/mongod.log'
            active.parent.mkdir()
            active.write_text('active record')
            stale = root / 'opncell/mongod.log'
            stale.parent.mkdir()
            stale.write_text('old record')
            with patch.object(module, 'resolve_log', return_value=active):
                module.clear_log('mongod')
            self.assertEqual(active.read_text(), '')
            self.assertEqual(stale.read_text(), 'old record')
