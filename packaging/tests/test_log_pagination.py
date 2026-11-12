import importlib.util
from pathlib import Path
import sys
import unittest
scripts = Path(__file__).resolve().parents[2] / 'opncell/src/opnsense/scripts/opncell'
sys.path.insert(0, str(scripts))
spec = importlib.util.spec_from_file_location('cellular_query_log', scripts/'query_log.py')
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)

class LogPaginationTests(unittest.TestCase):
    def test_page_sizes_all_and_exact_totals(self):
        records = [{'id': i} for i in range(123)]
        for limit in (50, 100, 5000, 0):
            rows, total = q.page_records(iter(records), limit, 0)
            self.assertEqual(total, 123)
            self.assertEqual(rows, records if limit == 0 else records[:limit])
        first, _ = q.page_records(iter(records), 50, 0)
        second, _ = q.page_records(iter(records), 50, 50)
        last, total = q.page_records(iter(records), 50, 100)
        self.assertEqual(first + second + last, records)
        self.assertEqual((len(last), total), (23, 123))

    def test_cutoff_is_applied_before_count_and_page(self):
        records = [{'timestamp': value} for value in (
            '2026-11-10T13:00:01+00:00', '2026-11-10T13:00:00Z', '2026-11-10T12:59:59+00:00')]
        since = 1794315600  # 2026-11-10 13:00:00 UTC
        self.assertEqual(q.page_records(iter(records), 50, 0, since), (records[:2], 2))
        self.assertEqual(q.page_records(iter(records), 1, 1, since), (records[1:2], 2))
        self.assertEqual(q.page_records(iter(records[2:]), 0, 0, since), ([], 0))
        self.assertFalse(q.matching_time({'timestamp': None}, since))

    def test_text_export_uses_identical_time_filter_and_limit(self):
        records = [{'timestamp':'2026-11-10T13:00:00Z','id':i} for i in range(5)]
        emitted=[]
        rows,total=q.page_records(records,2,1,1794315600,emitted.append)
        self.assertEqual((rows,total),([],5))
        self.assertEqual(emitted,records[1:3])
