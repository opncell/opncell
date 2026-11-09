#!/usr/bin/env python3
"""Offline OPNcell application-data migration; never upgrades WiredTiger files.

Requires canonical mongoexport/mongoimport and mongo (source) or mongosh (target).
An independently created cold backup is required before preparing a bundle.
"""
import argparse
from collections import Counter
from contextlib import contextmanager
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile


class MigrationError(Exception):
    pass


def require(ok, message):
    if not ok:
        raise MigrationError(message)


def run(argv):
    result = subprocess.run(argv, text=True, capture_output=True)
    # Do not echo command arguments: callers may use authenticated URIs.
    require(result.returncode == 0,
            f"{Path(argv[0]).name} failed (exit {result.returncode}); "
            "operation stopped. Check the local MongoDB log.")
    return result.stdout


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def documents(path):
    """Order-independent documents, preserving every canonical EJSON type tag."""
    result = Counter()
    ids = set()
    with Path(path).open() as stream:
        for line in stream:
            if not line.strip():
                continue
            doc = json.loads(line)
            require(isinstance(doc, dict) and "_id" in doc, "Invalid exported document")
            identity = json.dumps(doc["_id"], sort_keys=True, separators=(",", ":"))
            require(identity not in ids, "Duplicate _id in migration export")
            ids.add(identity)
            # Preserve BSON object key order, including embedded objects.
            encoded = json.dumps(doc, separators=(",", ":"), ensure_ascii=False)
            result[hashlib.sha256(encoded.encode()).hexdigest()] += 1
    return result


def atomic_json(path, value):
    path = Path(path)
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as stream:
        temp = Path(stream.name)
        os.chmod(temp, 0o600)
        json.dump(value, stream, indent=2)
        stream.write("\n")
    os.replace(temp, path)


@contextmanager
def lock(bundle):
    """Prevent simultaneous migrations using the same bundle."""
    import fcntl
    with (Path(bundle) / ".lock").open("a") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise MigrationError("This migration bundle is already in use")
        yield


def shell(args, js):
    # JSON output is enclosed in a marker; banners cannot be mistaken for data.
    command = ('var result=(function(){' + js + '})();'
               'print("OPNCELL_JSON:"+JSON.stringify(result));')
    raw = run([args.shell, "--norc", "--quiet", args.uri, "--eval", command])
    lines = [line[len("OPNCELL_JSON:"):] for line in raw.splitlines()
             if line.startswith("OPNCELL_JSON:")]
    require(len(lines) == 1, "Mongo shell returned no unambiguous migration result")
    return json.loads(lines[0])


def inventory(args):
    data = shell(args, '''
var info=db.getCollectionInfos();
return {version:db.version(),
 path:db.adminCommand({getCmdLineOpts:1}).parsed.storage.dbPath,
 collections:info.map(function(c){return {
 name:c.name,type:c.type,options:c.options,
 count:db.getCollection(c.name).countDocuments({}),
 indexes:db.getCollection(c.name).getIndexes()};})};
''')
    require(isinstance(data.get("path"), str), "Cannot establish the running MongoDB data path")
    return data


def validate_collection(c):
    require(re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", c["name"]) is not None,
            "Unsupported collection name; migration stopped without modifying source")
    require(c["type"] == "collection" and c["options"] == {},
            f"{c['name']}: custom collection options/views require a reviewed migration")
    require(isinstance(c["count"], int) and c["count"] >= 0, "Invalid collection count")
    for i in c["indexes"]:
        require(set(i) <= {"v", "ns", "key", "name", "unique", "sparse", "background"},
                f"{c['name']}: unsupported index options; no options will be discarded")
        require(isinstance(i.get("key"), dict) and i["key"], "Invalid index definition")
        require(all(v in (1, -1) for v in i["key"].values()),
                f"{c['name']}: only ordinary ascending/descending indexes are supported")


def index_spec(i):
    return {k: v for k, v in i.items() if k not in ("v", "ns", "background")}


def export(args, name, path):
    run([args.mongoexport, "--uri=" + args.uri, "--collection=" + name,
         "--jsonFormat=canonical", "--out=" + str(path)])
    os.chmod(path, 0o600)


def prepare(args):
    require(args.writers_stopped, "Stop all provisioning/radio writers and pass --writers-stopped")
    backup = Path(args.cold_backup).resolve(strict=True)
    require(backup.is_file() and backup.stat().st_size > 0, "Cold backup is empty")
    # Read every archive member to detect truncated/corrupt gzip or tar streams.
    with tarfile.open(backup, "r:gz") as archive:
        members = set()
        for member in archive:
            members.add(member.name.lstrip("/"))
            stream = archive.extractfile(member) if member.isfile() else None
            if stream:
                with stream:
                    while stream.read(1024 * 1024):
                        pass
    bundle = Path(args.bundle)
    bundle.mkdir(mode=0o700, parents=True, exist_ok=False)
    with lock(bundle):
        source = inventory(args)
        require(source["version"].startswith("5."), "Source must be MongoDB 5.x")
        require(Path(source["path"]).is_absolute(), "Source MongoDB data path must be absolute")
        require(source["path"].strip("/") + "/WiredTiger" in members,
                "Cold backup does not contain the running source database's WiredTiger files")
        require("conf/config.xml" in members, "Cold backup does not contain OPNsense config.xml")
        for c in source["collections"]:
            validate_collection(c)
        # A write lock blocks *all* writers, including web provisioning, during export.
        locked = shell(args, 'return db.adminCommand({fsync:1,lock:true});')
        require(locked.get("ok") == 1, "Could not lock source database for consistent export")
        try:
            source = inventory(args)
            for n, c in enumerate(source["collections"]):
                validate_collection(c)
                c["file"] = f"collection-{n}.ejson"
                path = bundle / c["file"]
                export(args, c["name"], path)
                require(sum(documents(path).values()) == c["count"], "Export count mismatch")
                c["sha256"] = digest(path)
        finally:
            unlocked = shell(args, 'return db.adminCommand({fsyncUnlock:1});')
            require(unlocked.get("ok") == 1, "SOURCE REMAINS LOCKED: run db.fsyncUnlock() before service use")
        manifest = {"format": 1, "database": "open5gs", "source": source,
                    "cold_backup": {"path": str(backup), "sha256": digest(backup)},
                    "scope": "Application collections only; database users/roles are not exported"}
        if not getattr(args, 'database_only', False):
            helper = Path(__file__).with_name('configuration-upgrade.py')
            spec = importlib.util.spec_from_file_location('configuration', helper)
            configuration = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(configuration)
            configuration.preserve(bundle, legacy=getattr(args, 'legacy_prefix', None))
            manifest['configuration_files'] = {
                str(p.relative_to(bundle)): digest(p)
                for p in (bundle / 'preserved-configs').rglob('*') if p.is_file()}
        atomic_json(bundle / "manifest.json", manifest)
        print("SUCCESS: consistent migration export prepared; cold backup and indexes recorded")


def load_bundle(bundle):
    bundle = Path(bundle)
    m = json.loads((bundle / "manifest.json").read_text())
    require(m.get("format") == 1 and m.get("database") == "open5gs", "Unknown migration bundle format")
    require(m["source"]["version"].startswith("5."), "Bundle source is not MongoDB 5.x")
    for name, checksum in m.get('configuration_files', {}).items():
        relative = Path(name)
        require(not relative.is_absolute() and '..' not in relative.parts and
                relative.parts[0] == 'preserved-configs', 'Unsafe preserved configuration path')
        path = bundle / relative
        require(not path.is_symlink() and digest(path) == checksum, 'Preserved configuration checksum mismatch')
    names = set()
    for n, c in enumerate(m["source"]["collections"]):
        validate_collection(c)
        require(c["name"] not in names, "Duplicate collection in manifest")
        names.add(c["name"])
        require(c["file"] == f"collection-{n}.ejson", "Unsafe migration file path")
        path = bundle / c["file"]
        require(not path.is_symlink(), "Export must not be a symlink")
        require(digest(path) == c["sha256"], "Migration export checksum mismatch")
        require(sum(documents(path).values()) == c["count"], "Migration export count mismatch")
    return m


def target_check(args, m):
    target = inventory(args)
    require(target["version"].startswith("8.0."), "Target must be MongoDB 8.0.x")
    actual = Path(target["path"]).resolve()
    require(actual == Path(args.target_dbpath).resolve(), "Target server is using an unexpected data directory")
    require(actual != Path(m["source"]["path"]).resolve(),
            "Target path equals MongoDB 5 source path; use a separate fresh directory")
    return target


def verify(args, m):
    target = target_check(args, m)
    expected = {c["name"]: c for c in m["source"]["collections"]}
    actual = {c["name"]: c for c in target["collections"]}
    require(set(expected) == set(actual), "Target collection inventory differs from source")
    with tempfile.TemporaryDirectory(prefix="opncell-verify-") as directory:
        for n, (name, c) in enumerate(expected.items()):
            require(actual[name]["count"] == c["count"], f"{name}: restored count mismatch")
            want = sorted((index_spec(i) for i in c["indexes"]), key=lambda i: i["name"])
            got = sorted((index_spec(i) for i in actual[name]["indexes"]), key=lambda i: i["name"])
            require(want == got, f"{name}: restored indexes differ")
            path = Path(directory) / f"verify-{n}.ejson"
            export(args, name, path)
            require(documents(path) == documents(Path(args.bundle) / c["file"]),
                    f"{name}: document or BSON-type verification failed")
    report = {"status": "verified", "target_version": target["version"],
              "target_dbpath": target["path"], "manifest_sha256": digest(Path(args.bundle) / "manifest.json"),
              "counts": {name: c["count"] for name, c in expected.items()},
              "documents_and_types_match": True, "indexes_match": True}
    atomic_json(Path(args.bundle) / "verification.json", report)
    print("SUCCESS: records, BSON types, counts, and indexes verified")


def restore(args):
    require(args.writers_stopped, "Keep all provisioning/radio writers stopped and pass --writers-stopped")
    with lock(args.bundle):
        m = load_bundle(args.bundle)
        target = target_check(args, m)
        if args.command == "verify" or (Path(args.bundle) / "verification.json").exists():
            verify(args, m)
            return
        require(not target["collections"], "Target database is not empty; refusing to overwrite or merge")
        # A failed import is intentionally retained for diagnosis; never drop data to retry.
        atomic_json(Path(args.bundle) / "restore-started.json", {"target": target["path"]})
        for c in m["source"]["collections"]:
            specs = [index_spec(i) for i in c["indexes"] if i["name"] != "_id_"]
            # Build indexes first, so uniqueness is enforced during import.
            script = ('var c=db.getCollection(' + json.dumps(c["name"]) + ');'
                      'var made=db.createCollection(' + json.dumps(c["name"]) + ');'
                      'if(!made.ok){throw new Error("Cannot create migration collection");}'
                      'var specs=' + json.dumps(specs) + ';'
                      'specs.forEach(function(i){var k=i.key;delete i.key;c.createIndex(k,i);});'
                      'return {ok:1};')
            shell(args, script)
            run([args.mongoimport, "--uri=" + args.uri, "--collection=" + c["name"],
                 "--file=" + str(Path(args.bundle) / c["file"]), "--stopOnError", "--mode=insert"])
        verify(args, m)


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("prepare", "restore", "verify", "check-bundle"))
    p.add_argument("--bundle", required=True)
    p.add_argument("--uri", default="mongodb://127.0.0.1:27017/open5gs")
    p.add_argument("--shell", default="mongosh", help="Use legacy mongo for prepare if mongosh is unavailable")
    p.add_argument("--mongoexport", default="mongoexport")
    p.add_argument("--mongoimport", default="mongoimport")
    p.add_argument("--cold-backup")
    p.add_argument("--target-dbpath")
    p.add_argument("--writers-stopped", action="store_true")
    p.add_argument("--legacy-prefix", help="Original Open5GS prefix to preserve before package removal")
    p.add_argument("--database-only", action="store_true", help="Export database only; installer still requires configuration recovery")
    return p


def main():
    os.umask(0o077)
    args = parser().parse_args()
    # Initial installer supports the local unauthenticated instance only.
    require(re.fullmatch(r"mongodb://127\.0\.0\.1:[0-9]+/open5gs", args.uri) is not None,
            "Installer migration requires a local open5gs URI; authenticated/remote migration needs separate configuration")
    if args.command == "prepare":
        require(args.cold_backup, "--cold-backup is required")
        prepare(args)
    elif args.command == "check-bundle":
        load_bundle(args.bundle)
        print("SUCCESS: migration bundle checksums and counts verified")
    else:
        require(args.target_dbpath, "--target-dbpath is required")
        restore(args)


if __name__ == "__main__":
    try:
        main()
    except (MigrationError, OSError, ValueError, KeyError, tarfile.TarError) as exc:
        print("FAILED: " + str(exc), file=sys.stderr)
        sys.exit(1)
