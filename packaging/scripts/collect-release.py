#!/usr/local/bin/python3
"""Collect a dependency-complete FreeBSD package repository from existing binaries."""
import argparse
import hashlib
import json
import os
from pathlib import Path
from functools import cmp_to_key
import shutil
import subprocess

PINS = {
    "os-cellular": ("26.7.2_18", "b1c7de598f07c4b88fb13dc6cb57bd37b5c5c07c72d8c4377e8647205bd74e5a"),
    "open5gs": ("2.8.0_1", "99dd644f47608e2187702ba98a8f67fea72433bd62ec85484f69b1c4420ffc40"),
    "mongodb80": ("8.0.34_3", "58702bf6382c03478800c265cea34d7ceb76a977eb8ecf997f1d0e01e78d4797"),
    "opncell-mongosh": ("2.14.0", None),
    "opncell-pymongo": ("4.18.2", "e43d794640a0a49ce884d91f0b0aeeb9003cae6de88ac51cc33c71145f9d480c"),
}
# OPNsense 26.7 supplies this interpreter. Never replace its core Python package
# with one from a different distribution just to satisfy the private read helper.
PLATFORM_REQUIRES = {"python313": "3.13"}
SEARCH = [
    "/usr/home/codex/opncell-release/26.7.2_18/cpu-catalogs/noavx/All",
    "/usr/home/codex/opncell-release/26.7.2_6/packages",
    "/tmp/opncell-26.7-runtime", "/tmp/opncell-26.7-packages",
    "/tmp/opncell-mongosh-fetch", "/tmp/opncell-python-fetch",
    "/tmp/opncell-mongo8034-fetch",
    "/usr/local/poudriere/data/packages/15_1_amd64-fbsd15/All",
    "/usr/local/poudriere/data/packages/15_1_amd64-fbsd15/.building/All",
]


def version_compare(left, right):
    return {"<": -1, "=": 0, ">": 1}[subprocess.check_output(
        ["pkg", "version", "-t", left, right], text=True).strip()]


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def metadata(path):
    raw = subprocess.check_output(
        ["tar", "-xqOf", str(path), "+COMPACT_MANIFEST"], stderr=subprocess.DEVNULL)
    data = json.loads(raw)
    abi = data.get("abi", data.get("arch", "")).lower()
    if abi not in ("freebsd:15:amd64", "freebsd:15:*"):
        raise ValueError("Different ABI")
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--incoming", action="append", default=[])
    args = parser.parse_args()
    destination = args.destination.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    inventory = {}
    seen = set()
    roots = [Path.home() / "opncell-release", *map(Path, SEARCH), *map(Path, args.incoming)]
    for rank, root in enumerate(roots):
        if not root.exists():
            continue
        # Only known package directories are scanned, never source or database trees.
        for path in (root.glob("*.pkg") if rank == 0 else root.rglob("*.pkg")):
            try:
                real = path.resolve()
                if real in seen or not os.access(real, os.R_OK):
                    continue
                seen.add(real)
                data = metadata(real)
            except (OSError, ValueError, subprocess.CalledProcessError):
                continue
            name, version = data["name"], data["version"]
            if name in PINS and version != PINS[name][0]:
                continue
            if name == "python312" and version_compare(version, "3.12.15") < 0:
                continue
            inventory.setdefault(name, []).append((rank, real, data))
    # Prefer the existing tested runtime bundle. Use other candidates only when
    # a selected dependency requires a newer version.
    for candidates in inventory.values():
        candidates.sort(key=cmp_to_key(
            lambda a, b: (a[0] > b[0]) - (a[0] < b[0])
            or -version_compare(a[2]["version"], b[2]["version"])))
    pending = [(name, PINS[name][0]) for name in PINS]
    selected, missing, requirements = {}, {}, {}
    while pending:
        name, required = pending.pop()
        if name in PLATFORM_REQUIRES:
            if version_compare(PLATFORM_REQUIRES[name], required) < 0:
                missing[name] = required
            continue
        previous = requirements.get(name)
        if previous and version_compare(previous, required) > 0:
            required = previous
        requirements[name] = required
        old = selected.get(name)
        if old and version_compare(old[1]["version"], required) >= 0:
            continue
        candidate = next(((path, data) for _, path, data in inventory.get(name, [])
                          if version_compare(data["version"], required) >= 0), None)
        if candidate is None:
            missing[name] = required
            continue
        path, data = candidate
        selected[name] = (path, data)
        missing.pop(name, None)
        pending.extend((dependency, spec["version"]) for dependency, spec in data.get("deps", {}).items())
    # Drop dependencies belonging only to an older candidate that was superseded.
    reachable, pending_names = set(), list(PINS)
    while pending_names:
        name = pending_names.pop()
        if name in reachable or name not in selected:
            continue
        reachable.add(name)
        pending_names.extend(selected[name][1].get("deps", {}))
    selected = {name: selected[name] for name in reachable}
    report = {
        "release": "26.7.2_8",
        "platform_requires": PLATFORM_REQUIRES,
        "packages": {name: {"version": data["version"], "source": str(path)}
                     for name, (path, data) in sorted(selected.items())},
        "missing": missing,
    }
    (destination / "collection-report.json").write_text(json.dumps(report, indent=2) + "\n")
    if missing:
        print("Missing package candidates")
        for name, required in sorted(missing.items()):
            print(f"  {name} {required}")
        return 2
    packages = destination / "packages" / "All"
    packages.mkdir(parents=True, exist_ok=True)
    expected_files = {f"{name}-{data['version']}.pkg" for name, (_, data) in selected.items()}
    stale = {p.name for p in packages.glob("*.pkg")} - expected_files
    if stale:
        raise RuntimeError("Unexpected packages in output. Use a fresh destination: " + ", ".join(sorted(stale)))
    checksums, lock = [], []
    for name, (source, data) in sorted(selected.items()):
        checksum = digest(source)
        if name in PINS and PINS[name][1] and checksum != PINS[name][1]:
            raise RuntimeError("Tested package checksum mismatch: " + name)
        target = packages / f"{name}-{data['version']}.pkg"
        if target.exists() and digest(target) != checksum:
            raise RuntimeError("Existing output differs: " + str(target))
        if not target.exists():
            shutil.copyfile(source, target)
            target.chmod(0o644)
        checksums.append(f"{checksum}  packages/All/{target.name}\n")
        lock.append({
            "name": name, "version": data["version"], "origin": data["origin"],
            "abi": data.get("abi", data.get("arch")), "sha256": checksum,
            "dependencies": data.get("deps", {}), "options": data.get("options", {}),
        })
    (destination / "SHA256").write_text("".join(checksums))
    (destination / "packages.lock.json").write_text(json.dumps(lock, indent=2) + "\n")
    subprocess.run(["pkg", "repo", str(destination / "packages")], check=True)
    # Record the current audit result for review, including any known findings.
    audit_db = destination / "audit-db"
    audit_db.mkdir(exist_ok=True)
    audit = subprocess.run(["pkg", "-o", "PKG_DBDIR=" + str(audit_db), "audit", "-F", *[f"{p['name']}-{p['version']}" for p in lock]],
                           text=True, capture_output=True)
    (destination / "package-audit.txt").write_text(audit.stdout + audit.stderr)
    print(f"Collected {len(lock)} packages into {destination}")
    print(f"Package audit exit status: {audit.returncode}. Review package-audit.txt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
