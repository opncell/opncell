import argparse
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import tarfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/migrate-mongodb.py"
spec = importlib.util.spec_from_file_location("migration", SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.bundle = Path(self.tmp.name)
        self.doc = {"_id": {"$oid": "000000000000000000000001"}, "imsi": "001010000000001",
                    "security": {"sqn": {"$numberLong": "123"}},
                    "slice": [{"sst": {"$numberInt": "1"}, "session": [{"name": "internet"}]}]}
        self.data = self.bundle / "collection-0.ejson"
        self.data.write_text(json.dumps(self.doc) + "\n")
        self.collection = {"name": "subscribers", "type": "collection", "options": {}, "count": 1,
                           "indexes": [{"v": 2, "name": "_id_", "key": {"_id": 1}},
                                       {"v": 2, "name": "imsi_1", "key": {"imsi": 1}, "unique": True}],
                           "file": "collection-0.ejson", "sha256": m.digest(self.data)}
        self.manifest = {"format": 1, "database": "open5gs",
                         "source": {"version": "5.0.30", "path": "/legacy/db",
                                    "collections": [self.collection]}}
        m.atomic_json(self.bundle / "manifest.json", self.manifest)
        self.args = argparse.Namespace(command="restore", bundle=str(self.bundle),
            target_dbpath="/fresh/db", writers_stopped=True, shell="mongosh", uri="local",
            mongoexport="mongoexport", mongoimport="mongoimport")
        self.empty = {"version": "8.0.34", "path": "/fresh/db", "collections": []}
        self.full = {**self.empty, "collections": [copy.deepcopy(self.collection)]}

    def fake_export(self, args, name, path):
        Path(path).write_bytes(self.data.read_bytes())

    def test_nested_auth_and_leading_zero_imsi_preserved(self):
        self.assertEqual(m.load_bundle(self.bundle)["source"]["collections"][0]["count"], 1)
        with patch.object(m, "inventory", side_effect=[self.empty, self.full]), \
             patch.object(m, "shell", return_value={"ok": 1}), \
             patch.object(m, "run") as run, patch.object(m, "export", side_effect=self.fake_export):
            m.restore(self.args)
        self.assertTrue((self.bundle / "verification.json").exists())
        self.assertIn("--mode=insert", run.call_args.args[0])
        self.assertNotIn("--drop", run.call_args.args[0])

    def test_changed_export_refused(self):
        self.data.write_text("{}\n")
        with self.assertRaisesRegex(m.MigrationError, "checksum"):
            m.load_bundle(self.bundle)

    def test_manifest_path_traversal_refused(self):
        self.manifest["source"]["collections"][0]["file"] = "../secret"
        m.atomic_json(self.bundle / "manifest.json", self.manifest)
        with self.assertRaisesRegex(m.MigrationError, "Unsafe"):
            m.load_bundle(self.bundle)

    def test_custom_index_options_refused(self):
        self.collection["indexes"][1]["partialFilterExpression"] = {"enabled": True}
        with self.assertRaisesRegex(m.MigrationError, "unsupported index"):
            m.validate_collection(self.collection)

    def test_custom_collection_options_refused(self):
        self.collection["options"] = {"validator": {"imsi": {"$type": "string"}}}
        with self.assertRaisesRegex(m.MigrationError, "custom collection"):
            m.validate_collection(self.collection)

    def test_nonempty_target_never_modified(self):
        with patch.object(m, "inventory", return_value=self.full), patch.object(m, "run") as run:
            with self.assertRaisesRegex(m.MigrationError, "not empty"):
                m.restore(self.args)
        run.assert_not_called()

    def test_source_data_path_refused(self):
        with patch.object(m, "inventory", return_value={**self.empty, "path": "/legacy/db"}):
            self.args.target_dbpath = "/legacy/db"
            with self.assertRaisesRegex(m.MigrationError, "source path"):
                m.restore(self.args)

    def test_wrong_target_version_refused(self):
        with patch.object(m, "inventory", return_value={**self.empty, "version": "5.0.30"}):
            with self.assertRaisesRegex(m.MigrationError, "8.0"):
                m.restore(self.args)

    def test_import_failure_never_writes_success(self):
        with patch.object(m, "inventory", return_value=self.empty), \
             patch.object(m, "shell", return_value={"ok": 1}), \
             patch.object(m, "run", side_effect=m.MigrationError("import failed")):
            with self.assertRaises(m.MigrationError):
                m.restore(self.args)
        self.assertFalse((self.bundle / "verification.json").exists())
        self.assertTrue((self.bundle / "restore-started.json").exists())

    def test_numeric_type_change_detected(self):
        changed = copy.deepcopy(self.doc)
        changed["security"]["sqn"] = {"$numberInt": "123"}
        def changed_export(args, name, path):
            Path(path).write_text(json.dumps(changed) + "\n")
        with patch.object(m, "inventory", return_value=self.full), \
             patch.object(m, "export", side_effect=changed_export):
            with self.assertRaisesRegex(m.MigrationError, "BSON-type"):
                m.verify(self.args, self.manifest)

    def test_missing_unique_index_detected(self):
        self.full["collections"][0]["indexes"][1].pop("unique")
        with patch.object(m, "inventory", return_value=self.full):
            with self.assertRaisesRegex(m.MigrationError, "indexes differ"):
                m.verify(self.args, self.manifest)

    def test_completed_rerun_verifies_without_insert(self):
        m.atomic_json(self.bundle / "verification.json", {"status": "verified"})
        with patch.object(m, "inventory", return_value=self.full), \
             patch.object(m, "export", side_effect=self.fake_export), patch.object(m, "run") as run:
            m.restore(self.args)
        run.assert_not_called()

    def test_failed_export_unlocks_source(self):
        cold = self.bundle / "cold.tar.gz"
        with tarfile.open(cold, "w:gz") as archive:
            archive.add(self.data, arcname="legacy/db/WiredTiger")
            archive.add(self.data, arcname="conf/config.xml")
        args = argparse.Namespace(bundle=str(self.bundle / "new"), cold_backup=str(cold), writers_stopped=True, database_only=True)
        calls = []
        def shell(args, js):
            calls.append(js)
            return {"ok": 1}
        with patch.object(m, "inventory", return_value=self.manifest["source"]), \
             patch.object(m, "shell", side_effect=shell), \
             patch.object(m, "export", side_effect=m.MigrationError("export failed")):
            with self.assertRaisesRegex(m.MigrationError, "export failed"):
                m.prepare(args)
        self.assertIn("fsyncUnlock", calls[-1])
        self.assertFalse((self.bundle / "new/manifest.json").exists())

    def test_successful_prepare_records_backup(self):
        cold = self.bundle / "cold.tar.gz"
        with tarfile.open(cold, "w:gz") as archive:
            archive.add(self.data, arcname="legacy/db/WiredTiger")
            archive.add(self.data, arcname="conf/config.xml")
        args = argparse.Namespace(bundle=str(self.bundle / "prepared"), cold_backup=str(cold), writers_stopped=True, database_only=True)
        with patch.object(m, "inventory", return_value=copy.deepcopy(self.manifest["source"])), \
             patch.object(m, "shell", return_value={"ok": 1}), \
             patch.object(m, "export", side_effect=self.fake_export):
            m.prepare(args)
        prepared = m.load_bundle(args.bundle)
        self.assertEqual(prepared["cold_backup"]["sha256"], m.digest(cold))

    def test_duplicate_ids_refused(self):
        with self.data.open("a") as stream:
            stream.write(json.dumps(self.doc) + "\n")
        with self.assertRaisesRegex(m.MigrationError, "Duplicate"):
            m.documents(self.data)

    def test_unexpected_target_path_refused(self):
        with patch.object(m, "inventory", return_value={**self.empty, "path": "/unexpected/db"}):
            with self.assertRaisesRegex(m.MigrationError, "unexpected data"):
                m.restore(self.args)


if __name__ == "__main__":
    unittest.main()
