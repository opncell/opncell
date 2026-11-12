import argparse
import importlib.util
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/upgrade-cellular.py'
spec = importlib.util.spec_from_file_location('existing_upgrade', SCRIPT)
u = importlib.util.module_from_spec(spec)
spec.loader.exec_module(u)


class ExistingUpgradeTests(unittest.TestCase):
    def test_process_discovery_ignores_shell_arguments_and_handles_quoted_paths(self):
        text = '12 sh -c "mongod --dbpath /wrong"\n34 /usr/local/bin/mongod --dbpath "/data/cellular db" --logpath=/var/log/mongo.log\n'
        pid, argv = u.mongo_process(text)
        self.assertEqual(pid, 34)
        self.assertEqual(u.option(argv, '--dbpath'), '/data/cellular db')
        self.assertEqual(u.option(argv, '--logpath'), '/var/log/mongo.log')
        self.assertIsNone(u.mongo_process('12 /usr/local/bin/open5gs-mmed\n'))
        with self.assertRaisesRegex(ValueError, 'Multiple'):
            u.mongo_process(text + '56 /usr/local/bin/mongod --port 27018\n')

    def test_legacy_rc_defaults_and_live_identity_are_preserved(self):
        script = ': ${mongod_dbpath="/legacy/data/db"}\n: ${mongod_user="root"}\n: ${mongod_group="wheel"}\n'
        def run(args):
            return subprocess.CompletedProcess(args, 0 if args[0]=='ps' else 1,
                                               'root\n' if args[0]=='ps' else '', '')
        with patch.object(u, 'command', side_effect=run):
            values = u.service_settings((42, ['/usr/local/bin/mongod', '--dbpath', '/actual/db', '--logpath', '/logs/current.log']), script)
        self.assertEqual(values['mongod_dbpath'], '/actual/db')
        self.assertEqual(values['mongod_user'], 'root')
        self.assertEqual(values['mongod_group'], 'wheel')
        self.assertIn('/logs/current.log', values['mongod_flags'])

    def test_runtime_security_flags_are_not_dropped(self):
        argv = ['/usr/local/bin/mongod', '--config', '/custom/mongo.conf', '--dbpath=/actual/db',
                '--fork', '--auth', '--bind_ip', '127.0.0.1', '--keyFile', '/private/key file']
        flags = u.shlex.split(u.runtime_flags(argv))
        self.assertIn('--auth', flags)
        self.assertIn('/private/key file', flags)
        self.assertIn('--bind_ip', flags)
        self.assertNotIn('--fork', flags)
        self.assertNotIn('/actual/db', flags)

    def test_explicit_service_overrides_take_precedence(self):
        def run(args):
            value = {'mongod_dbpath':'/custom/db', 'mongod_user':'mongodb', 'mongod_group':'mongodb',
                     'mongod_flags':'--logpath /custom/log --logappend'}.get(args[-1], '')
            return subprocess.CompletedProcess(args, 0, value+'\n', '')
        with patch.object(u, 'command', side_effect=run):
            values = u.service_settings(None, '')
        self.assertEqual(values['mongod_dbpath'], '/custom/db')
        self.assertEqual(values['mongod_flags'], '--logpath /custom/log --logappend')

    def test_node_and_npm_cleanup_only_for_development_dependencies(self):
        installed = ['mongodb80','node24','npm-node24','npm']
        refs = {'node24':['npm-node24'], 'npm-node24':['npm'], 'npm':[]}
        self.assertTrue(u.check_node_dependents(installed, lambda name: refs.get(name, [])))
        self.assertFalse(u.check_node_dependents(['mongodb80','node22'], lambda name: []))
        for name in ['node24', 'npm-node24', 'npm']:
            changed = {**refs, name:refs[name]+['unrelated-app']}
            with self.assertRaisesRegex(ValueError, 'application'):
                u.check_node_dependents(installed, lambda key: changed.get(key, []))

    def test_plan_mode_never_mutates_packages_or_services(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);db=root/'existing-db';db.mkdir()
            recovery=root/'recovery'
            args=argparse.Namespace(migration_bundle=None, recovery_dir=str(recovery), plan_only=True)
            candidate={'version':'8.0.34_1','binary_sha256':'new','package_sha256':'package','cpu_profile':'avx'}
            def require(ok, message):
                if not ok: raise ValueError(message)
            def run(command):
                if command[:3]==['pkg-static','query','-a']: return 'mongodb80\nnode22\n'
                if command[:3]==['pkg-static','query','%v']: return '8.0.29\n'
                if command[:2]==['pkg-static','version']: return '<\n'
                if command[0]=='ps': return '42 /usr/local/bin/mongod --dbpath '+str(db)+'\n'
                if 'fetch' in command: return ''
                raise AssertionError('Unexpected mutation: '+str(command))
            api=SimpleNamespace(require=require, run=run,
                candidate_repository=Mock(return_value=('OPNcell','avx',root/'repos','config')),
                preflight_binary=Mock(return_value=candidate), migration=SimpleNamespace(digest=lambda p:'old',atomic_json=lambda p,v:p.write_text(u.json.dumps(v))),
                pkg_command=lambda repos,*args:['pkg-static',*args], install_candidate=Mock(side_effect=AssertionError('Plan installed packages')))
            before={'version':'8.0.29','dbpath':str(db),'subscribers':3,'provisioning_sha256':'same'}
            def command(args):
                return subprocess.CompletedProcess(args,1,'The following 2 package(s) will be affected\n','')
            with patch.object(u,'client_type',return_value=object()),patch.object(u,'inventory',return_value=before), \
                 patch.object(u,'service_settings',return_value={'mongod_dbpath':str(db)}), \
                 patch.object(u.Path,'read_text',return_value='rc script'),patch.object(u,'command',side_effect=command), \
                 patch.object(u,'backup',side_effect=AssertionError('Plan changed recovery/service state')):
                u.upgrade(args,api)
            api.install_candidate.assert_not_called()
            self.assertTrue(u.json.loads((recovery/'upgrade-plan.json').read_text())['plan_only'])

    def test_binary_update_backups_and_restarts_mongodb_even_if_package_step_fails(self):
        for fail in (False, True):
            with self.subTest(package_failure=fail), tempfile.TemporaryDirectory() as directory:
                root = Path(directory);db = root/'db';db.mkdir();(db/'WiredTiger').write_bytes(b'fixture')
                recovery = root/'recovery';events=[];state={'running':True}
                args=argparse.Namespace(migration_bundle=None,recovery_dir=str(recovery),plan_only=False,config_defaults=str(root/'defaults'))
                def require(ok,message):
                    if not ok:raise ValueError(message)
                def run(command):
                    if command[:3]==['pkg-static','query','-a']:return 'mongodb80\nnode22\n'
                    if command[:3]==['pkg-static','query','%v']:return '8.0.29'
                    if command[:2]==['pkg-static','version']:return '<'
                    if command[0]=='ps':return '42 /usr/local/bin/mongod --dbpath '+str(db) if state['running'] else ''
                    if command[:3]==['service','mongod','onestop']:
                        events.append('stop');state['running']=False;return ''
                    if command[:3]==['service','mongod','onestart']:
                        events.append('start');state['running']=True;return ''
                    if command[0]=='sysrc' or 'fetch' in command:return ''
                    raise AssertionError(command)
                def install(*args):
                    events.append('install')
                    if fail:raise ValueError('package fixture failure')
                candidate={'version':'8.0.34_1','binary_sha256':'new'}
                api=SimpleNamespace(require=require,run=run,
                    candidate_repository=lambda *args:('OPNcell','avx',root/'repos','config'),
                    preflight_binary=lambda *args:candidate,
                    migration=SimpleNamespace(digest=lambda path:'old',atomic_json=lambda p,v:p.write_text(u.json.dumps(v))),
                    pkg_command=lambda repos,*args:['pkg-static',*args],install_candidate=install,
                    configuration=SimpleNamespace(repair=Mock()),persist_repository=Mock())
                record={'version':'8.0.34','dbpath':str(db),'subscribers':3,'provisioning_sha256':'unchanged'}
                service={'mongod_dbpath':str(db),'mongod_config':'/fixture/mongo.conf','mongod_user':'root','mongod_group':'wheel','mongod_flags':'--logappend'}
                with patch.object(u,'client_type',return_value=object()),patch.object(u,'inventory',return_value=record), \
                     patch.object(u,'service_settings',return_value=service),patch.object(u.Path,'read_text',return_value='rc'), \
                     patch.object(u,'command',return_value=subprocess.CompletedProcess([],1,'The following 2 package(s) will be affected','')), \
                     patch.object(u,'backup',side_effect=lambda *args:events.append('backup')):
                    if fail:
                        with self.assertRaisesRegex(ValueError,'package fixture failure'):u.upgrade(args,api)
                    else:u.upgrade(args,api)
                self.assertTrue((recovery/'mongodb.cold-before.tar.gz').is_file())
                self.assertEqual(events,['backup','stop','install','start'])
                self.assertTrue(state['running'])
                self.assertEqual(api.persist_repository.call_count,0 if fail else 1)


if __name__ == '__main__': unittest.main()
