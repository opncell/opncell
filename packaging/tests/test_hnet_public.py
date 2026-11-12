import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
import sys

script = Path(__file__).resolve().parents[2] / 'opncell/src/opnsense/scripts/opncell/list_hnet.py'
sys.path.insert(0, str(script.parent))
spec = importlib.util.spec_from_file_location('hnet_public', script)
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)

class HnetPublicTests(unittest.TestCase):
    def test_public_exports_match_pem_and_survive_regeneration(self):
        for scheme in (1, 2):
            with self.subTest(scheme=scheme), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                private = root / 'private.key'
                command = (['openssl', 'genpkey', '-algorithm', 'X25519'] if scheme == 1 else
                           ['openssl', 'ecparam', '-name', 'prime256v1', '-genkey', '-noout'])
                private.write_bytes(subprocess.check_output(command, stderr=subprocess.DEVNULL))
                original = private.read_bytes()
                pem, hex_key = h.derive_public_key(str(private), scheme)
                pem_file = root / 'reference.pub'
                pem_file.write_text(pem)
                command = ['openssl', 'pkey' if scheme == 1 else 'ec', '-pubin', '-in', str(pem_file), '-outform', 'DER']
                if scheme == 2:
                    command += ['-conv_form', 'compressed']
                der = subprocess.check_output(command, stderr=subprocess.DEVNULL)
                size = 32 if scheme == 1 else 33
                self.assertEqual(bytes.fromhex(hex_key), der[-size:])
                if scheme == 2:
                    self.assertIn(bytes.fromhex(hex_key)[0], (2, 3))
                public, hex_file = h.store_public_keys(7, pem, hex_key, root / 'public')
                public.unlink()
                hex_file.write_text('obsolete')
                h.store_public_keys(7, *h.derive_public_key(str(private), scheme), root / 'public')
                self.assertEqual(public.read_text(), pem)
                self.assertEqual(hex_file.read_text(), hex_key)
                self.assertEqual(private.read_bytes(), original)
                self.assertEqual(public.stat().st_mode & 0o777, 0o644)

    def test_invalid_ids_and_symlink_destination_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for value in (0, 256):
                with self.assertRaises(ValueError):
                    h.store_public_keys(value, 'pem', 'hex', root / 'public')
            (root / 'link').symlink_to(root / 'public')
            with self.assertRaises(ValueError):
                h.store_public_keys(1, 'pem', 'hex', root / 'link')
        with self.assertRaises(ValueError):
            h.derive_public_key('/unused', 3)
