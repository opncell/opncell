import argparse
import contextlib
import io
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/install-cellular.py"
spec = importlib.util.spec_from_file_location("installer", SCRIPT)
i = importlib.util.module_from_spec(spec)
spec.loader.exec_module(i)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        bundle = root / "bundle"
        bundle.mkdir()
        cold = root / "cold.tar.gz"
        cold.write_bytes(b"test fixture")
        self.manifest = {"source": {"path": "/old/db"},
                         "cold_backup": {"path": str(cold), "sha256": i.migration.digest(cold)}}
        self.args = argparse.Namespace(migration_bundle=str(bundle), target_dbpath=str(root / "fresh"),
            recovery_dir=str(root / "recovery"), repository="OPNcell")

    def process(self, command, **kwargs):
        return subprocess.CompletedProcess(command, 1 if command[0] == "pgrep" else 0, "", "")

    def test_cpu_profiles(self):
        flags = 'Features2=0x1<AVX,XSAVE,OSXSAVE,FMA,F16C>\nStructured Extended Features=0x2<AVX2,BMI1>'
        self.assertEqual(i.cpu_profile('amd64', flags), 'avx')
        self.assertEqual(i.cpu_profile('amd64', flags.replace('AVX2,', '')), 'noavx')
        self.assertEqual(i.cpu_profile('amd64', flags.replace('OSXSAVE,', '')), 'noavx')
        self.assertEqual(i.cpu_profile('amd64', 'Features2=<XSAVE,OSXSAVE,SSE4.2>'), 'noavx')
        self.assertEqual(i.cpu_profile('amd64', ''), 'noavx')
        self.assertEqual(i.cpu_profile('aarch64', flags), 'noavx')

    def test_repository_selection(self):
        self.args.avx_repository = 'OPNcellAVX'
        self.args.noavx_repository = 'OPNcellNOAVX'
        with patch.object(i.Path, 'read_text', return_value=''), patch.object(i, 'cpu_profile', return_value='avx'):
            self.assertEqual(i.select_repository(self.args), ('OPNcellAVX', 'avx'))
            self.args.avx_repository = None
            self.assertEqual(i.select_repository(self.args), ('OPNcellNOAVX', 'noavx'))
        self.args.avx_repository = 'OPNcellAVX'
        with patch.object(i.Path, 'read_text', return_value=''), patch.object(i, 'cpu_profile', return_value='noavx'):
            self.assertEqual(i.select_repository(self.args), ('OPNcellNOAVX', 'noavx'))

    def test_profile_mismatch_is_rejected_before_binary_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / 'mongodb80-8.0.34_3.pkg'
            package.touch()
            def command(args):
                return 'NOAVX=on' if '%Ok=%Ov' in args else ('8.0.34_3' if '%v' in args else '')
            with patch.object(i, 'run', side_effect=command) as calls:
                with self.assertRaisesRegex(i.migration.MigrationError, 'CPU profile'):
                    i.preflight_binary('OPNcellAVX', Path(directory), 'avx')
                self.assertFalse(any('--version' in call.args[0] for call in calls.call_args_list))

    def test_only_exact_tested_avx_artifact_gets_metadata_exception(self):
        digest = next(iter(i.TESTED_AVX_PACKAGES))
        self.assertEqual(i.candidate_policy('avx', '8.0.34_1', ['NOAVX=on'], digest), '8.0.34_1')
        self.assertEqual(i.candidate_policy('noavx', '8.0.34_1', ['NOAVX=on'], digest), '8.0.34_3')
        for version, checksum in [('8.0.34_1', 'wrong'), ('8.0.34_2', digest)]:
            with self.assertRaises(i.migration.MigrationError):
                i.candidate_policy('avx', version, ['NOAVX=on'], checksum)
        self.assertEqual(i.candidate_policy('avx', '8.0.34_4', ['NOAVX=off'], 'other'), '8.0.34_3')

    def test_automatic_cpu_urls(self):
        self.args.repository_base_url = 'file:///private/cpu-catalogs/'
        for profile, suffix in [('avx', '-avx2'), ('noavx', '')]:
            recovery = Path(self.tmp.name) / profile
            recovery.mkdir()
            with patch.object(i, 'detected_cpu_profile', return_value=profile):
                name, selected, directory, contents = i.candidate_repository(self.args, recovery)
            self.assertEqual(selected, profile)
            config = i.json.loads(contents)
            self.assertEqual(config[name]['url'], 'file:///private/cpu-catalogs/${ABI}' + suffix)
            self.assertEqual((directory / 'OPNcell.conf').read_text(), contents)

    def test_persistent_route_preserves_old_config_and_other_repositories(self):
        root = Path(self.tmp.name)
        self.args.repos_dir = str(root / 'repos')
        directory = Path(self.args.repos_dir)
        directory.mkdir()
        (directory / 'OPNcell.conf').write_text('old config')
        (directory / 'OPNsense.conf').write_text('platform config')
        recovery = root / 'preserved'
        recovery.mkdir()
        config = i.repository_config('OPNcell', 'https://example.test/${ABI}-avx2')
        i.persist_repository(self.args, recovery, config)
        self.assertEqual((directory / 'OPNcell.conf').read_text(), config)
        self.assertEqual((recovery / 'OPNcell.conf.before-cpu-selection').read_text(), 'old config')
        self.assertEqual((directory / 'OPNsense.conf').read_text(), 'platform config')

    def test_preflight_only_never_installs_or_persists_configuration(self):
        self.args.repository_base_url = 'file:///private/cpu-catalogs'
        self.args.repos_dir = str(Path(self.tmp.name) / 'live-repos')
        candidate = {'version':'8.0.34_1', 'cpu_profile':'avx', 'package_sha256':'test', 'binary_sha256':'test'}
        with patch.object(i, 'run', return_value='15.1-RELEASE') as run, \
             patch.object(i, 'detected_cpu_profile', return_value='avx'), \
             patch.object(i, 'preflight_binary', return_value=candidate):
            i.preflight_only(self.args)
        self.assertFalse(Path(self.args.repos_dir).exists())
        self.assertFalse(any('install' in call.args[0] or 'delete' in call.args[0] for call in run.call_args_list))
        report = i.json.loads((Path(self.args.recovery_dir) / 'preflight.json').read_text())
        self.assertFalse(report['packages_installed'])
        self.assertFalse(report['persistent_configuration_changed'])

    def test_cpu_variant_switch_forces_only_exact_tested_mongodb(self):
        candidate = {'version':'8.0.34_1', 'binary_sha256':'tested'}
        with patch.object(i, 'run', return_value='8.0.34_1') as run, \
             patch.object(i.migration, 'digest', side_effect=['portable', 'tested']):
            i.install_candidate('OPNcell', Path('/private/repos'), candidate)
        forced = [call.args[0] for call in run.call_args_list if '-f' in call.args[0]]
        self.assertEqual(len(forced), 1)
        self.assertEqual(forced[0][-1], 'mongodb80-8.0.34_1')
        self.assertIn('REPOS_DIR=/private/repos', forced[0])

    def test_matching_binary_skips_forced_variant_replacement(self):
        candidate = {'version':'8.0.34_3', 'binary_sha256':'tested'}
        with patch.object(i, 'run', return_value='8.0.34_3') as run, \
             patch.object(i.migration, 'digest', return_value='tested'):
            i.install_candidate('OPNcell', None, candidate)
        self.assertFalse(any('-f' in call.args[0] for call in run.call_args_list))

    def test_wrong_installed_binary_is_rejected_after_replacement(self):
        candidate = {'version':'8.0.34_1', 'binary_sha256':'tested'}
        with patch.object(i, 'run', return_value='8.0.34_1'), \
             patch.object(i.migration, 'digest', return_value='unexpected'):
            with self.assertRaisesRegex(i.migration.MigrationError, 'binary differs'):
                i.install_candidate('OPNcell', None, candidate)

    def test_cpu_info_reports_flavor_without_running_commands_or_writing(self):
        self.args.repository_base_url = 'https://example.test/repo'
        for profile, label in [('avx', 'AVX2'), ('noavx', 'NOAVX')]:
            output = io.StringIO()
            with patch.object(i, 'detected_cpu_profile', return_value=profile), \
                 patch.object(i, 'run', side_effect=AssertionError('CPU check must not query packages')), \
                 patch.object(i.subprocess, 'run', side_effect=AssertionError('CPU check must not execute programs')), \
                 patch.object(i.Path, 'write_text', side_effect=AssertionError('CPU check must not write files')), \
                 contextlib.redirect_stdout(output):
                self.assertEqual(i.cpu_info(self.args), profile)
            self.assertIn('Selected MongoDB flavor: ' + label, output.getvalue())
            self.assertIn('no catalog query, download or installation', output.getvalue())

    def test_cpu_failure_happens_before_package_deletion(self):
        with patch.object(i.os, "geteuid", return_value=0), \
             patch.object(i, "run", return_value="15.1-RELEASE\n") as run, \
             patch.object(i.subprocess, "run", side_effect=self.process), \
             patch.object(i.migration, "load_bundle", return_value=self.manifest), \
             patch.object(i, "preflight_binary", side_effect=i.migration.MigrationError("SIGILL")):
            with self.assertRaisesRegex(i.migration.MigrationError, "SIGILL"):
                i.install(self.args)
        self.assertFalse(any("delete" in call.args[0] for call in run.call_args_list))
        self.assertFalse(Path(self.args.target_dbpath).exists())

    def test_existing_target_refused_before_package_actions(self):
        Path(self.args.target_dbpath).mkdir()
        with patch.object(i.os, "geteuid", return_value=0), \
             patch.object(i, "run", return_value="15.1-RELEASE\n"), \
             patch.object(i.subprocess, "run", side_effect=self.process), \
             patch.object(i.migration, "load_bundle", return_value=self.manifest), \
             patch.object(i, "preflight_binary") as probe:
            with self.assertRaisesRegex(i.migration.MigrationError, "already exists"):
                i.install(self.args)
        probe.assert_not_called()

    def test_unknown_dependents_block_removal(self):
        with patch.object(i.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "unrelated-app\n", "")):
            with self.assertRaisesRegex(i.migration.MigrationError, "unrelated"):
                i.check_legacy_dependents()

    def test_wrong_os_blocks_install(self):
        with patch.object(i.os, "geteuid", return_value=0), patch.object(i, "run", return_value="14.3-RELEASE"):
            with self.assertRaisesRegex(i.migration.MigrationError, "FreeBSD 15"):
                i.install(self.args)


if __name__ == "__main__":
    unittest.main()
