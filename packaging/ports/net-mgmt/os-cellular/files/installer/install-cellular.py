#!/usr/bin/env python3
"""Install OPNcell on FreeBSD 15, optionally restoring a prepared MongoDB 5 bundle.

Run migrate-mongodb.py prepare on MongoDB 5 *before* the OS/package upgrade.
This installer does not perform the OPNsense major upgrade.
"""
import argparse
import importlib.util
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

spec = importlib.util.spec_from_file_location("migration", Path(__file__).with_name("migrate-mongodb.py"))
migration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration)
require, run = migration.require, migration.run
config_spec = importlib.util.spec_from_file_location('configuration', Path(__file__).with_name('configuration-upgrade.py'))
configuration = importlib.util.module_from_spec(config_spec)
config_spec.loader.exec_module(configuration)

DAEMONS = ("amf", "ausf", "bsf", "hss", "mme", "nrf", "nssf", "pcf", "pcrf",
           "scp", "sgwc", "sgwu", "smf", "udm", "udr", "upf")


def check_legacy_dependents():
    pending, seen = ["mongodb50"], set()
    allowed = {"mongodb50", "open5gs", "os-cellular"}
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        require(name in allowed, "Legacy MongoDB has unrelated dependent packages; review removal manually")
        seen.add(name)
        result = subprocess.run(["pkg-static", "query", "%rn", name], capture_output=True, text=True)
        require(result.returncode in (0, 1), "Cannot inspect legacy package dependents")
        pending.extend(result.stdout.splitlines())


def cpu_features(boot_messages):
    flags = set()
    for line in boot_messages.splitlines():
        if re.search(r'Features[^<]*<', line, re.I):
            for group in re.findall(r'<([^>]+)>', line):
                flags.update(group.upper().split(','))
    return flags


def cpu_profile(architecture, boot_messages):
    """Use kernel-reported flags; execution preflight remains authoritative."""
    if architecture not in ('amd64', 'x86_64'):
        return 'noavx'
    required = {'AVX', 'AVX2', 'XSAVE', 'OSXSAVE', 'FMA', 'F16C'}
    return 'avx' if required <= cpu_features(boot_messages) else 'noavx'


def cpu_support_message(architecture, boot_messages):
    flags = cpu_features(boot_messages)
    if architecture not in ('amd64', 'x86_64') or not flags:
        return 'AVX support could not be confirmed; using the compatible NOAVX build.'
    if 'AVX' not in flags:
        return 'AVX instructions not supported on this processor.'
    if cpu_profile(architecture, boot_messages) != 'avx':
        return 'AVX is supported, but the optimized build requirements are not met; using NOAVX.'
    return 'AVX2 instructions and required CPU features are supported on this processor.'


def detected_cpu_support_message():
    try:
        messages = Path('/var/run/dmesg.boot').read_text()
    except OSError:
        messages = ''
    return cpu_support_message(os.uname().machine, messages)


def detected_cpu_profile():
    try:
        messages = Path('/var/run/dmesg.boot').read_text()
    except OSError:
        messages = ''
    return cpu_profile(os.uname().machine, messages)


def select_repository(args):
    profile = detected_cpu_profile()
    if getattr(args, 'repository_base_url', None):
        print('Automatically selecting ' + profile.upper() + ' repository for this CPU')
        return args.repository, profile
    avx_repo = getattr(args, 'avx_repository', None)
    baseline_repo = getattr(args, 'noavx_repository', None) or args.repository
    if profile == 'avx' and avx_repo:
        print('CPU supports AVX2; selecting optimized MongoDB repository: ' + avx_repo)
        return avx_repo, 'avx'
    reason = 'optimized repository not configured' if profile == 'avx' else 'AVX2 requirements not confirmed'
    print('Selecting compatible NOAVX MongoDB repository (' + reason + '): ' + baseline_repo)
    return baseline_repo, 'noavx'


def repository_config(name, url):
    require(re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', name) is not None, 'Invalid repository name')
    require(url.startswith(('https://', 'http://', 'file:///')), 'Use an HTTP(S) or absolute file repository URL')
    return json.dumps({name: {'url': url, 'enabled': True, 'priority': 200}}, indent=2) + '\n'


def cpu_info(args):
    repo, profile = select_repository(args)
    flavor = 'AVX2 (AVX2, FMA and F16C required)' if profile == 'avx' else 'NOAVX'
    print('Selected MongoDB flavor: ' + flavor, flush=True)
    print(detected_cpu_support_message(), flush=True)
    base_url = getattr(args, 'repository_base_url', None)
    if base_url:
        suffix = '-avx2' if profile == 'avx' else ''
        print('Selected repository URL: ' + base_url.rstrip('/') + '/${ABI}' + suffix, flush=True)
    else:
        print('Selected repository: ' + repo, flush=True)
    print('CPU check complete; no catalog query, download or installation performed.', flush=True)
    return profile


def candidate_repository(args, recovery):
    name, profile = select_repository(args)
    base_url = getattr(args, 'repository_base_url', None)
    if not base_url:
        return name, profile, None, None
    suffix = '-avx2' if profile == 'avx' else ''
    url = base_url.rstrip('/') + '/${ABI}' + suffix
    contents = repository_config(name, url)
    print('Selected repository URL: ' + url)
    directory = recovery / 'candidate-repos'
    directory.mkdir(mode=0o700)
    (directory / 'OPNcell.conf').write_text(contents)
    return name, profile, directory, contents


def pkg_command(repos_dir, *arguments):
    prefix = ['pkg-static']
    if repos_dir is not None:
        prefix += ['-o', 'REPOS_DIR=' + str(repos_dir)]
    return prefix + list(arguments)


def persist_repository(args, recovery, contents):
    if contents is None:
        return
    directory = Path(getattr(args, 'repos_dir', '/usr/local/etc/pkg/repos'))
    destination = directory / 'OPNcell.conf'
    require(not destination.is_symlink(), 'Repository configuration is a symlink; review it before replacement')
    directory.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        require(destination.is_file(), 'Repository configuration is not a regular file')
        shutil.copy2(destination, recovery / 'OPNcell.conf.before-cpu-selection')
    with tempfile.NamedTemporaryFile(mode='w', prefix='.OPNcell-', dir=directory, delete=False) as stream:
        temporary = Path(stream.name)
        try:
            stream.write(contents)
            stream.flush()
            os.fsync(stream.fileno())
            temporary.chmod(0o644)
            os.replace(temporary, destination)
        finally:
            temporary.unlink(missing_ok=True)


# This official artifact advertises NOAVX but executes AVX instructions.
# It passed isolated database/index/restart testing on our Broadwell AVX2 host.
TESTED_AVX_PACKAGES = {
    '979998024cc113ecb656f7bd848ebd3855044c7151a827e6d602b4335a479164': '8.0.34_1'
}


def candidate_policy(profile, version, options, digest):
    require(profile in ('avx', 'noavx'), 'Unknown CPU profile')
    tested_avx = profile == 'avx' and TESTED_AVX_PACKAGES.get(digest) == version
    expected = 'NOAVX=on' if profile == 'noavx' else 'NOAVX=off'
    require(expected in options or tested_avx,
            'MongoDB package options do not match selected CPU profile: ' + profile)
    return '8.0.34_1' if tested_avx else '8.0.34_3'


def preflight_binary(repo, directory, profile="noavx", repos_dir=None):
    """Fetch and execute the candidate before removing any installed package."""
    print('Checking MongoDB ' + ('AVX2' if profile == 'avx' else 'NOAVX') +
          ' package: catalog lookup and download may take time...', flush=True)
    run(pkg_command(repos_dir, "fetch", "-y", "-r", repo, "-o", str(directory), "mongodb80"))
    packages = list(directory.rglob("mongodb80-*.pkg"))
    require(len(packages) == 1, "Cannot identify the candidate MongoDB package")
    package = packages[0]
    options = run(["pkg-static", "query", "-F", str(package), "%Ok=%Ov"]).splitlines()
    version = run(["pkg-static", "query", "-F", str(package), "%v"]).strip()
    package_digest = migration.digest(package)
    minimum = candidate_policy(profile, version, options, package_digest)
    require(run(["pkg-static", "version", "-t", version, minimum]).strip() in ("=", ">"),
            "Repository has no suitable MongoDB candidate (requires " + minimum + " or newer)")
    require(version.startswith("8.0."), "Installer supports MongoDB 8.0.x only")
    flavor = 'AVX2 (requires AVX2, FMA and F16C)' if profile == 'avx' else 'NOAVX'
    print('Selected MongoDB package: mongodb80-' + version, flush=True)
    print('Selected MongoDB flavor: ' + flavor, flush=True)
    print(detected_cpu_support_message(), flush=True)
    if profile == 'avx' and 'NOAVX=on' in options:
        print('Official package has an incorrect NOAVX label; exact tested SHA256 verified for AVX2 use.')
    # Read the package manifest instead of decompressing the whole archive twice.
    print("Reading executable path from package manifest...", flush=True)
    members = run(["pkg-static", "query", "-F", str(package), "%Fp"]).splitlines()
    candidates = [name for name in members if name.lstrip("/") == "usr/local/bin/mongod"]
    require(len(candidates) == 1, "MongoDB executable missing from package")
    binary = directory / "mongod-probe"
    print("Extracting MongoDB for CPU compatibility testing...", flush=True)
    with binary.open("wb") as out:
        result = subprocess.run(["tar", "-xOf", str(package), candidates[0]], stdout=out,
                                stderr=subprocess.DEVNULL)
    require(result.returncode == 0, "Cannot extract MongoDB CPU probe")
    binary.chmod(0o700)
    print("Running MongoDB CPU compatibility test...", flush=True)
    run([str(binary), "--version"])
    print("SUCCESS: mongodb80-" + version + " [" + ("AVX2" if profile == "avx" else "NOAVX") + "] runs on this CPU")
    return {"version": version, "binary_sha256": migration.digest(binary), "cpu_profile": profile, "package_sha256": package_digest}


def install_candidate(selected_repo, repos_dir, candidate):
    candidate_version = candidate['version']
    run(pkg_command(repos_dir, "install", "-y", "-r", selected_repo,
         "os-cellular", "open5gs", "mongodb80", "opncell-mongosh"))
    # Switching CPU variants can lower the FreeBSD port revision while keeping
    # the same MongoDB upstream version. Force only the exact tested MongoDB.
    if migration.digest(Path("/usr/local/bin/mongod")) != candidate["binary_sha256"]:
        run(pkg_command(repos_dir, "install", "-y", "-f", "-r", selected_repo, "mongodb80-" + candidate_version))
    # Catch a repository change between probe and installation.
    require(run(["pkg-static", "query", "%v", "mongodb80"]).strip() == candidate_version,
            "Installed MongoDB differs from the CPU-tested candidate; leave services stopped")
    require(migration.digest(Path('/usr/local/bin/mongod')) == candidate['binary_sha256'],
            "Installed MongoDB binary differs from the CPU-tested candidate; leave services stopped")
    run(["/usr/local/bin/mongod", "--version"])


def install(args):
    require(os.geteuid() == 0, "Run the installer as root")
    require(run(["freebsd-version", "-u"]).startswith("15."),
            "Complete the supported OPNsense/FreeBSD 15 upgrade before running this installer")
    probe = subprocess.run(["pgrep", "-lx", "open5gs-.*|mongod"], capture_output=True, text=True)
    require(probe.returncode == 1, "Stop all Open5GS and mongod processes before installation")
    bundle = Path(args.migration_bundle).resolve(strict=True) if args.migration_bundle else None
    manifest = migration.load_bundle(bundle) if bundle else None
    old = subprocess.run(["pkg-static", "info", "-e", "mongodb50"], capture_output=True)
    require(old.returncode in (0, 1), "Cannot inspect installed MongoDB packages")
    require(old.returncode != 0 or bundle, "MongoDB 5 found: prepare a migration bundle first")
    if not bundle:
        installed = run(["pkg-static", "query", "-a", "%n"]).splitlines()
        require(not any(name.startswith("mongodb") for name in installed),
                "Existing MongoDB package found; fresh installation requires a separate reviewed migration")
    if old.returncode == 0:
        check_legacy_dependents()
    target = Path(args.target_dbpath)
    require(target.is_absolute() and not target.is_symlink(), "Use an absolute, non-symlink target directory")
    target = target.resolve()
    require(not target.exists(), "Target data directory already exists; installer will not overwrite or reuse it")
    if manifest:
        require(target != Path(manifest["source"]["path"]).resolve(), "Target must differ from legacy data path")
        backup = Path(manifest["cold_backup"]["path"])
        require(backup.is_file() and migration.digest(backup) == manifest["cold_backup"]["sha256"],
                "Cold backup is missing or changed; restore the recorded backup before installation")
    else:
        # Fresh installs must not silently strand an unrecognised previous database.
        for path in (Path("/var/db/mongodb"), Path("/usr/local/bin/data/db")):
            require(not (path / "WiredTiger").exists(),
                    f"Existing database at {path}: provide a verified migration bundle")
    recovery = Path(args.recovery_dir).resolve()
    recovery.mkdir(mode=0o700, parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(prefix="cpu-probe-", dir=recovery) as directory:
        selected_repo, profile, repos_dir, repo_contents = candidate_repository(args, recovery)
        candidate = preflight_binary(selected_repo, Path(directory), profile, repos_dir)
        candidate_version = candidate['version']
    if bundle and (bundle / 'preserved-configs').is_dir():
        shutil.copytree(bundle / 'preserved-configs', recovery / 'preserved-configs')
    else:
        configuration.preserve(recovery, legacy=args.legacy_prefix, fresh=not bool(bundle))
    # Preserve current service configuration independently from the database backup.
    with tarfile.open(recovery / "configuration.tar.gz", "w:gz") as archive:
        for path in ("/etc/rc.conf", "/usr/local/etc/mongodb.conf", "/conf/config.xml",
                     "/usr/local/etc/open5gs", "/usr/local/etc/freeDiameter"):
            if Path(path).exists():
                archive.add(path, arcname=path.lstrip("/"))
    # Boot is deliberately held until restore and verification have succeeded.
    run(["sysrc", "mongod_enable=NO"] + [f"epc{d}d_enable=NO" for d in DAEMONS])
    if old.returncode == 0:
        run(["pkg-static", "delete", "-y", "mongodb50"])
    install_candidate(selected_repo, repos_dir, candidate)
    processes = subprocess.run(["pgrep", "-lx", "open5gs-.*|mongod"], capture_output=True)
    require(processes.returncode == 1, "Package scripts started a daemon; stop it before configuring the fresh database")
    configuration.repair(recovery, args.config_defaults, fresh=not bool(bundle))
    target.mkdir(mode=0o750)
    shutil.chown(target, user="mongodb", group="mongodb")
    config = Path("/usr/local/etc/mongodb.conf")
    # The minimal standalone configuration is intentional; old config is archived.
    import json
    content = ("# Installed by OPNcell; previous configuration is in the recovery archive.\n"
               "storage:\n  dbPath: " + json.dumps(str(target)) + "\n"
               "net:\n  bindIp: 127.0.0.1\n  port: 27017\n")
    config.write_text(content)
    config.chmod(0o644)
    run(["sysrc", "mongod_enable=NO", "mongod_dbpath=" + str(target)])
    run(["service", "mongod", "onestart"])
    if bundle:
        restore_args = argparse.Namespace(command="restore", bundle=str(bundle),
            uri="mongodb://127.0.0.1:27017/open5gs", shell=args.shell,
            mongoexport=args.mongoexport, mongoimport=args.mongoimport,
            target_dbpath=str(target), writers_stopped=True)
        try:
            migration.restore(restore_args)
        except Exception:
            subprocess.run(["service", "mongod", "onestop"], capture_output=True)
            raise
    else:
        # Fresh install: verify path and version before enabling database startup.
        check = argparse.Namespace(shell=args.shell, uri="mongodb://127.0.0.1:27017/open5gs")
        info = migration.inventory(check)
        require(info["version"].startswith("8.0.") and Path(info["path"]).resolve() == target,
                "Fresh MongoDB instance did not pass verification")
    persist_repository(args, recovery, repo_contents)
    run(["sysrc", "mongod_enable=YES"])
    migration.atomic_json(recovery / "installation.json", {
        "status": "verified", "mongodb_package": candidate_version,
        "cpu_profile": profile, "repository": selected_repo,
        "persistent_cpu_route": repo_contents is not None,
        "mongodb_binary_sha256": candidate['binary_sha256'],
        "mongodb_package_sha256": candidate['package_sha256'],
        "target_dbpath": str(target), "migration_bundle": str(bundle) if bundle else None,
        "cellular_services_enabled": False})
    print("SUCCESS: MongoDB is ready. Apply a topology to enable cellular services.")


def preflight_only(args):
    require(run(['freebsd-version', '-u']).startswith('15.'), 'Preflight requires FreeBSD 15')
    recovery = Path(args.recovery_dir).resolve()
    recovery.mkdir(mode=0o700, parents=True, exist_ok=False)
    repo, profile, repos_dir, contents = candidate_repository(args, recovery)
    with tempfile.TemporaryDirectory(prefix='cpu-probe-', dir=recovery) as temporary:
        result = preflight_binary(repo, Path(temporary), profile, repos_dir)
    result.update({'status': 'preflight-passed', 'repository': repo,
                   'persistent_configuration_changed': False, 'packages_installed': False})
    migration.atomic_json(recovery / 'preflight.json', result)
    print('SUCCESS: CPU package preflight passed; no packages or service configuration changed.')


def main():
    os.umask(0o077)
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--migration-bundle")
    p.add_argument("--target-dbpath", default="/var/db/opncell-mongodb80")
    p.add_argument("--recovery-dir", help="New private directory for configuration backup and report")
    p.add_argument("--repository", default="OPNcell", help="Repository name for the selected catalog")
    p.add_argument("--repository-base-url", default="http://repo.opncell.io/OPNcell-repo",
        help="CPU catalog base URL; use an empty string for manually configured named repositories")
    p.add_argument("--repos-dir", default="/usr/local/etc/pkg/repos", help="Where successful installs persist OPNcell.conf")
    modes = p.add_mutually_exclusive_group()
    modes.add_argument("--preflight-only", action="store_true", help="Download and execute the candidate without installing")
    modes.add_argument("--cpu-info", action="store_true", help="Instant CPU/flavor check; no catalog query or download")
    p.add_argument("--avx-repository", help="Full-stack repository with a tested AVX2 MongoDB build")
    p.add_argument("--noavx-repository", help="Full-stack NOAVX repository (defaults to --repository)")
    p.add_argument("--shell", default="/usr/local/bin/mongosh")
    p.add_argument("--mongoexport", default="mongoexport")
    p.add_argument("--mongoimport", default="mongoimport")
    p.add_argument("--legacy-prefix", help="Original Open5GS install prefix, including a mounted snapshot path")
    p.add_argument("--config-defaults", default=str(Path(__file__).resolve().parent.parent / 'defaults'))
    args = p.parse_args()
    if args.cpu_info:
        cpu_info(args)
        return
    if not args.recovery_dir:
        p.error('--recovery-dir is required for installation or full preflight')
    preflight_only(args) if args.preflight_only else install(args)


if __name__ == "__main__":
    try:
        main()
    except (migration.MigrationError, OSError, ValueError, KeyError, tarfile.TarError) as exc:
        print("FAILED: " + str(exc) + ". Do not apply a topology until resolved.", file=sys.stderr)
        sys.exit(1)
