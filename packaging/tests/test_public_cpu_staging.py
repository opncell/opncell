import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/stage-public-repository.py'
spec = importlib.util.spec_from_file_location('cpu_stage', SCRIPT)
stage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stage)


class PublicStagingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / 'source'
        for profile in ['noavx', 'avx2']:
            catalog = self.source / profile
            (catalog / 'All').mkdir(parents=True)
            payload = (profile + '-package').encode()
            (catalog / 'All/test-1.pkg').write_bytes(payload)
            (catalog / 'SHA256.json').write_text(json.dumps({'test-1.pkg': hashlib.sha256(payload).hexdigest()}))
            (catalog / 'meta.conf').write_text(profile)
        self.legacy = self.root / 'legacy'
        self.legacy.mkdir()
        (self.legacy / 'meta.conf').write_text('legacy')
        for name, target in [('FreeBSD:15:amd64', 'noavx'), ('FreeBSD:15:amd64-avx2', 'avx2'),
                             ('FreeBSD:14:amd64', str(self.legacy))]:
            (self.source / name).symlink_to(target, target_is_directory=True)
        self.args = argparse.Namespace(source=str(self.source), destination=str(self.root / 'new-release'),
            base_url='http://example.test/staged', report=str(self.root / 'report.json'))

    def test_stages_and_verifies_both_cpu_routes_and_legacy(self):
        with patch.object(stage, 'remote_digest', side_effect=lambda url, relative: stage.digest(self.source / relative)):
            stage.stage(self.args)
        report = json.loads(Path(self.args.report).read_text())
        self.assertFalse(report['public_activated'])
        self.assertTrue(report['abi14_preserved'])
        self.assertEqual((Path(self.args.destination) / 'FreeBSD:14:amd64').resolve(), self.legacy.resolve())

    def test_existing_release_is_never_overwritten(self):
        destination = Path(self.args.destination)
        destination.mkdir()
        (destination / 'keep').write_text('keep')
        with self.assertRaisesRegex(ValueError, 'empty'):
            stage.stage(self.args)
        self.assertEqual((destination / 'keep').read_text(), 'keep')

    def test_corrupted_source_is_rejected_before_public_copy(self):
        (self.source / 'noavx/All/test-1.pkg').write_text('changed')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            stage.stage(self.args)
        self.assertFalse(Path(self.args.destination).exists())
