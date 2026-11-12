import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/configuration-upgrade.py'
spec = importlib.util.spec_from_file_location('configuration', SCRIPT)
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
BOOT = Path(__file__).resolve().parents[2] / 'opncell/src/opnsense/scripts/opncell/verify_boot.py'
spec = importlib.util.spec_from_file_location('boot', BOOT)
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


class ConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'root'
        self.legacy = self.root / c.LEGACY.lstrip('/')
        self.recovery = Path(self.tmp.name) / 'recovery'
        for name in c.DIAMETER:
            config = self.legacy / 'etc/freeDiameter' / (name + '.conf')
            config.parent.mkdir(parents=True, exist_ok=True)
            config.write_text('Identity = "' + name + '.custom";\nTLS_Cred = "' + c.LEGACY +
                              '/etc/open5gs/tls/' + name + '.crt", "' + c.LEGACY +
                              '/etc/open5gs/tls/' + name + '.key";\nLoadExtension = "' + c.LEGACY +
                              '/lib/freeDiameter/dict.fdx";\n')
            yaml = self.legacy / 'etc/open5gs' / (name + '.yaml')
            yaml.parent.mkdir(parents=True, exist_ok=True)
            yaml.write_text(name + ':\n  freeDiameter: ' + c.LEGACY + '/etc/freeDiameter/' + name + '.conf\n')
            tls = self.legacy / 'etc/open5gs/tls'
            tls.mkdir(exist_ok=True)
            (tls / (name + '.key')).write_text('private fixture')
            (tls / (name + '.crt')).write_text('public fixture')
        extension = self.root / 'usr/local/lib/freeDiameter/dict.fdx'
        extension.parent.mkdir(parents=True)
        extension.touch()

    def test_recover_original_settings_and_relocate_paths(self):
        c.preserve(self.recovery, root=self.root)
        c.repair(self.recovery, Path(self.tmp.name) / 'no-defaults', root=self.root)
        config = self.root / 'usr/local/etc/freeDiameter/hss.conf'
        self.assertIn('hss.custom', config.read_text())
        self.assertNotIn(c.LEGACY, config.read_text())
        private = self.root / 'usr/local/etc/open5gs/tls/hss.key'
        self.assertEqual(private.stat().st_mode & 0o777, 0o600)

    def test_stock_local_database_uri_uses_ipv4(self):
        for name in ('hss', 'pcrf', 'pcf', 'udr'):
            self.assertEqual(c.normalize('db_uri: mongodb://localhost/open5gs\n' + name + ': {}\n'),
                             'db_uri: mongodb://127.0.0.1:27017/open5gs\n' + name + ': {}\n')
        custom = 'db_uri: mongodb://database.example:27018/custom\n'
        self.assertEqual(c.normalize(custom), custom)

    def test_existing_configuration_wins(self):
        c.preserve(self.recovery, root=self.root)
        target = self.root / 'usr/local/etc/freeDiameter/hss.conf'
        target.parent.mkdir(parents=True)
        target.write_text('Identity = "operator.custom";\n')
        c.repair(self.recovery, Path(self.tmp.name) / 'no-defaults', root=self.root)
        self.assertIn('operator.custom', target.read_text())

    def test_missing_extension_blocks_activation(self):
        c.preserve(self.recovery, root=self.root)
        (self.root / 'usr/local/lib/freeDiameter/dict.fdx').unlink()
        with self.assertRaisesRegex(ValueError, 'dict.fdx'):
            c.repair(self.recovery, Path(self.tmp.name), root=self.root)

    def test_no_original_config_does_not_silently_use_defaults(self):
        (self.legacy / 'etc/freeDiameter/hss.conf').unlink()
        with self.assertRaisesRegex(ValueError, 'Missing original.*hss'):
            c.preserve(self.recovery, root=self.root)

    def test_default_hnet_examples_removed(self):
        self.assertEqual(c.empty_example_hnet('udm:\n  hnet:\n    - id: 1\n      key: /example\n  sbi:\n    server: []\n'),
                         'udm:\n  hnet: []\n  sbi:\n    server: []\n')


class BootTests(unittest.TestCase):
    def runner(self, enabled):
        def execute(command, **kwargs):
            name = command[1]
            if name == 'mongod':
                return subprocess.CompletedProcess(command, 0, 'mongod_enable="YES"\n', '')
            value = 'YES' if name[3:-1] in enabled else 'NO'
            return subprocess.CompletedProcess(command, 0, name + '_enable="' + value + '"\n', '')
        return execute

    def test_every_topology_checks_effective_rcvar(self):
        for network, selected in b.NETWORKS.items():
            self.assertEqual(b.check(network, self.runner(selected))['result'], 'verified')

    def test_disabled_selected_daemon_reported(self):
        result = b.check('enablefour', self.runner(()))
        self.assertEqual(result['result'], 'failed')
        self.assertIn('open5gs-hssd', result['message'])

    def test_extra_daemons_enabled_reported(self):
        result = b.check('enableupf', self.runner(b.ALL))
        self.assertEqual(result['result'], 'failed')


if __name__ == '__main__':
    unittest.main()
