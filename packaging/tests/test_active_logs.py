import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[2] / 'opncell/src/opnsense/scripts/opncell/active_logs.py'
sys.path.insert(0, str(SCRIPT.parent))
spec = importlib.util.spec_from_file_location('active_logs', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ActiveLogsTests(unittest.TestCase):
    def test_only_real_cellular_process_names_are_included(self):
        rows = module.active_logs('''101 Is /usr/local/bin/open5gs-mmed
102 S /usr/local/bin/mongod
103 S /usr/bin/grep
104 S /usr/local/bin/open5gs-amfd-backup
105 S /usr/bin/python3.12
''')
        self.assertEqual([row['scope'] for row in rows], ['mongod', 'mme'])
        self.assertEqual(rows[1]['pids'], [101])

    def test_zombies_and_missing_processes_are_excluded(self):
        self.assertEqual(module.active_logs('101 Z open5gs-mmed\n102 X mongod\n'), [])
        self.assertEqual(module.active_logs(''), [])

    def test_multiple_active_pids_are_grouped_without_hiding_them(self):
        rows = module.active_logs('101 S open5gs-mmed\n102 S open5gs-mmed\n')
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['pids'], [101, 102])

    def test_stopped_fiveg_daemons_are_not_inferred_from_old_log_files(self):
        rows = module.active_logs('101 S open5gs-mmed\n102 S open5gs-sgwud\n')
        self.assertNotIn('amf', [row['scope'] for row in rows])
        self.assertNotIn('mongod', [row['scope'] for row in rows])

    def test_freebsd_column_arguments_are_separate(self):
        with patch.object(module.subprocess, 'check_output', return_value='101 Is /usr/local/bin/open5gs-mmed\n') as ps:
            rows = module.active_logs()
        self.assertEqual(ps.call_args.args[0], ['/bin/ps', 'axww', '-o', 'pid=', '-o', 'stat=', '-o', 'comm='])
        self.assertEqual(rows[0]['scope'], 'mme')
