#!/usr/bin/env python3
"""Preserve an existing local MongoDB 8.0 installation during an OPNcell upgrade."""
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import sqlite3
import subprocess
import sys
import tarfile
import tempfile

PROJECTION = {'slice': 1, 'imsi': 1, 'msisdn': 1, 'ambr': 1, 'subscriber_status': 1,
              'operator_determined_barring': 1, 'security.k': 1, 'security.opc': 1,
              'security.op': 1, 'security.amf': 1}


def command(args):
    return subprocess.run(args, capture_output=True, text=True)


def mongo_process(text):
    found = []
    for line in text.splitlines():
        match = re.match(r'\s*(\d+)\s+(.*)', line)
        if not match:
            continue
        try:
            argv = shlex.split(match[2])
        except ValueError:
            continue
        if argv and Path(argv[0]).name == 'mongod':
            found.append((int(match[1]), argv))
    if len(found) > 1:
        raise ValueError('Multiple MongoDB processes found; existing settings require review')
    return found[0] if found else None


def option(argv, name):
    for index, item in enumerate(argv):
        if item == name and index + 1 < len(argv):
            return argv[index + 1]
        if item.startswith(name + '='):
            return item.split('=', 1)[1]
    return None


def setting(name, script, fallback):
    configured = command(['sysrc', '-n', name])
    if configured.returncode == 0 and configured.stdout.strip():
        return configured.stdout.strip()
    match = re.search(r'\$\{' + re.escape(name) + r'=["\x27]([^"\x27\n]+)["\x27]\}', script)
    return match[1] if match else fallback


def runtime_flags(argv):
    remaining = []
    index = 1
    while index < len(argv):
        item = argv[index]
        if item in ('--config', '-f', '--dbpath'):
            index += 2
            continue
        if item == '--fork' or item.startswith(('--config=', '--dbpath=')):
            index += 1
            continue
        remaining.append(item)
        index += 1
    if not any('disabledSecureAllocatorDomains=' in item for item in remaining):
        remaining.append('--setParameter=disabledSecureAllocatorDomains=*')
    return shlex.join(remaining)


def service_settings(process, script):
    argv = process[1] if process else []
    path = option(argv, '--dbpath') or setting('mongod_dbpath', script, None)
    if not path or not Path(path).is_absolute() or '\n' in path:
        raise ValueError('MongoDB data directory must be an absolute path')
    user = setting('mongod_user', script, 'mongodb')
    if process:
        result = command(['ps', '-o', 'user=', '-p', str(process[0])])
        if result.returncode == 0 and result.stdout.strip():
            user = result.stdout.strip()
    group = setting('mongod_group', script, 'wheel' if user == 'root' else user)
    flags = command(['sysrc', '-n', 'mongod_flags'])
    if process:
        flags = runtime_flags(argv)
    elif flags.returncode == 0 and flags.stdout.strip():
        flags = flags.stdout.strip()
    else:
        log = option(argv, '--logpath') or str(Path(path) / 'mongod.log')
        flags = '--logpath ' + shlex.quote(log) + ' --logappend --setParameter=disabledSecureAllocatorDomains=*'
    config = option(argv, '--config') or option(argv, '-f') or setting('mongod_config', script, '/usr/local/etc/mongodb.conf')
    if not Path(config).is_absolute() or '\n' in config:
        raise ValueError('MongoDB configuration file must be an absolute path')
    return {'mongod_config': config, 'mongod_dbpath': path, 'mongod_user': user, 'mongod_group': group, 'mongod_flags': flags}


def check_node_dependents(installed, query):
    """Allow replacement of development-only Node/npm, never an unrelated app."""
    remove_meta = False
    for name in installed:
        if not re.fullmatch(r'node[0-9]+', name) or name == 'node22':
            continue
        flavor = 'npm-' + name
        dependents = set(query(name))
        if dependents - {flavor}:
            raise ValueError('Cannot replace ' + name + ': another application depends on it')
        if flavor in installed:
            if set(query(flavor)) - {'npm'}:
                raise ValueError('Cannot replace ' + flavor + ': another application depends on it')
            if 'npm' in installed and 'npm' in query(flavor):
                if query('npm'):
                    raise ValueError('Cannot remove npm: another application depends on it')
                remove_meta = True
    return remove_meta


def client_type(api, repo, repos, recovery):
    fetch = recovery / 'client-fetch'
    fetch.mkdir()
    api.run(api.pkg_command(repos, 'fetch', '-y', '-r', repo, '-o', str(fetch), 'opncell-pymongo'))
    packages = list(fetch.rglob('opncell-pymongo-*.pkg'))
    # Hashed filenames and convenience symlinks can identify the same package.
    packages = list({p.resolve() for p in packages})
    api.require(len(packages) == 1, 'Could not identify the private database client package')
    runtime = recovery / 'client-runtime'
    runtime.mkdir()
    api.run(['tar', '-C', str(runtime), '-xf', str(packages[0])])
    sys.path.insert(0, str(runtime / 'usr/local/share/opncell-pymongo'))
    try:
        from pymongo import MongoClient
    except ImportError as error:
        raise ValueError('Could not load the packaged private database client') from error
    return MongoClient


def inventory(factory):
    from bson.json_util import dumps, CANONICAL_JSON_OPTIONS
    try:
        with factory('mongodb://127.0.0.1:27017/open5gs', serverSelectionTimeoutMS=3000,
                     connectTimeoutMS=3000, socketTimeoutMS=5000) as client:
            docs = list(client.open5gs.subscribers.find({}, PROJECTION).sort('imsi', 1))
            data = dumps(docs, json_options=CANONICAL_JSON_OPTIONS, sort_keys=True, separators=(',', ':'))
            return {'version': client.server_info()['version'], 'subscribers': len(docs),
                    'provisioning_sha256': hashlib.sha256(data.encode()).hexdigest(),
                    'dbpath': client.admin.command('getCmdLineOpts')['parsed']['storage']['dbPath']}
    except Exception as error:
        raise ValueError('Cannot inspect the existing local database; no package changes performed') from error


def backup(api, recovery, dbpath, running, factory, config='/usr/local/etc/mongodb.conf'):
    api.configuration.preserve(recovery, fresh=False)
    with tarfile.open(recovery / 'configuration.before.tar.gz', 'w:gz') as archive:
        for name in ['/conf/config.xml', '/etc/rc.conf', '/etc/rc.conf.local', '/etc/rc.conf.d',
                     '/usr/local/etc/rc.conf.d', '/usr/local/etc/rc.d', '/usr/local/etc/pkg/repos',
                     '/usr/local/etc/mongodb.conf', '/usr/local/etc/open5gs', '/usr/local/etc/freeDiameter',
                     '/usr/local/bin/mongosh', config]:
            if Path(name).exists():
                archive.add(name, arcname=name.lstrip('/'))
    with sqlite3.connect('file:/var/db/pkg/local.sqlite?mode=ro', uri=True) as source:
        with sqlite3.connect(recovery / 'packages.before.sqlite') as destination:
            source.backup(destination)
    be = command(['bectl', 'list', '-H']) if shutil.which('bectl') else None
    if be and be.returncode == 0:
        name = 'pre-opncell-' + recovery.name[-28:]
        api.run(['bectl', 'create', name])
        (recovery / 'boot-environment.txt').write_text(name + '\n')
    if running:
        from bson.json_util import dumps, CANONICAL_JSON_OPTIONS
        with factory('mongodb://127.0.0.1:27017/open5gs', serverSelectionTimeoutMS=3000,
                     socketTimeoutMS=5000) as client:
            with (recovery / 'subscribers.before.ejson').open('w') as stream:
                for doc in client.open5gs.subscribers.find({}):
                    stream.write(dumps(doc, json_options=CANONICAL_JSON_OPTIONS) + '\n')
            (recovery / 'subscriber-indexes.before.ejson').write_text(
                dumps(client.open5gs.subscribers.index_information(), json_options=CANONICAL_JSON_OPTIONS))


def upgrade(args, api):
    api.require(not args.migration_bundle, 'MongoDB 8 is already installed; do not supply a MongoDB 5 migration bundle')
    recovery = Path(args.recovery_dir).resolve()
    recovery.mkdir(mode=0o700, parents=True, exist_ok=False)
    print('Mode: upgrade existing MongoDB 8.0 and OPNcell', flush=True)
    print('Recovery files: ' + str(recovery), flush=True)
    installed = api.run(['pkg-static', 'query', '-a', '%n']).splitlines()
    api.require(not any(name.startswith('mongodb') and name != 'mongodb80' for name in installed),
                'Other MongoDB packages are installed; review the package set before upgrading')
    current = api.run(['pkg-static', 'query', '%v', 'mongodb80']).strip()
    api.require(current.startswith('8.0.'), 'Only in-place MongoDB 8.0 patch upgrades are supported')
    repo, profile, repos, contents = api.candidate_repository(args, recovery)
    with tempfile.TemporaryDirectory(prefix='cpu-probe-', dir=recovery) as directory:
        candidate = api.preflight_binary(repo, Path(directory), profile, repos)
    relation = api.run(['pkg-static', 'version', '-t', current.split('_')[0], candidate['version'].split('_')[0]]).strip()
    api.require(relation != '>', 'Refusing to downgrade the MongoDB upstream version')
    factory = client_type(api, repo, repos, recovery)
    process = mongo_process(api.run(['ps', 'axww', '-o', 'pid=', '-o', 'command=']))
    service = service_settings(process, Path('/usr/local/etc/rc.d/mongod').read_text())
    before = inventory(factory) if process else None
    if before:
        api.require(before['version'].startswith('8.0.'), 'Running MongoDB is not an 8.0 server')
        service['mongod_dbpath'] = before['dbpath']
    dbpath = Path(service['mongod_dbpath'])
    api.require(dbpath.is_absolute() and dbpath.is_dir(), 'Existing database directory is unavailable; nothing was changed')
    old_binary = Path('/usr/local/bin/mongod')
    replace = not old_binary.is_file() or api.migration.digest(old_binary) != candidate['binary_sha256']
    def dependents(name):
        result = command(['pkg-static', 'query', '%rn', name])
        api.require(result.returncode in (0, 1), 'Cannot inspect Node.js dependents')
        return result.stdout.splitlines()
    remove_meta = check_node_dependents(installed, dependents)
    if any(re.fullmatch(r'node[0-9]+', name) and name != 'node22' for name in installed):
        processes = api.run(['ps', 'axww', '-o', 'command='])
        for line in processes.splitlines():
            try:
                argv = shlex.split(line)
            except ValueError:
                continue
            api.require(not argv or Path(argv[0]).name not in ('node', 'nodejs'),
                        'A Node.js application is running; stop it before replacing the legacy runtime')
    # Populate file metadata so the preview includes Node runtime conflicts.
    api.run(api.pkg_command(repos, 'fetch', '-y', '-r', repo, 'os-cellular', 'mongodb80', 'opncell-mongosh'))
    preview = command(api.pkg_command(repos, 'install', '-n', '-r', repo, 'os-cellular', 'mongodb80', 'opncell-mongosh'))
    (recovery / 'package-preview.txt').write_text(preview.stdout + preview.stderr)
    preview_text = preview.stdout + preview.stderr
    valid_preview = ('Your packages are up to date.' in preview_text or 'All packages are up to date.' in preview_text
                     or re.search(r'The following [0-9]+ package\(s\) will be affected', preview_text))
    api.require(preview.returncode in (0, 1) and valid_preview and 'missing dependency' not in preview_text.lower(),
                'Package preview failed; review the recovery log before upgrading')
    print(preview.stdout + preview.stderr, flush=True)
    api.migration.atomic_json(recovery / 'upgrade-plan.json', {
        'mode': 'upgrade', 'candidate': candidate, 'database_path': str(dbpath),
        'mongodb_restart_required': replace or not process, 'remove_unused_npm_meta': remove_meta,
        'subscriber_count': before['subscribers'] if before else None, 'plan_only': getattr(args, 'plan_only', False)})
    if getattr(args, 'plan_only', False):
        print('SUCCESS: upgrade plan verified; packages and service settings unchanged.', flush=True)
        return
    if replace or not process:
        size = sum(p.stat().st_size for p in dbpath.resolve().rglob('*') if p.is_file())
        api.require(shutil.disk_usage(recovery).free > size + 256 * 1024 * 1024,
                    'Insufficient free space for a cold database backup; free space before upgrading')
    print('Creating configuration, package and database recovery files...', flush=True)
    backup(api, recovery, dbpath, bool(process), factory, service['mongod_config'])
    stopped = False
    try:
        if replace and process:
            print('Stopping MongoDB briefly for its patch/CPU package update...', flush=True)
            api.run(['service', 'mongod', 'onestop'])
            api.require(mongo_process(api.run(['ps', 'axww', '-o', 'pid=', '-o', 'command='])) is None,
                        'MongoDB did not stop; no package changes performed')
            stopped = True
        if replace or not process:
            print('Creating a cold database backup...', flush=True)
            with tarfile.open(recovery / 'mongodb.cold-before.tar.gz', 'w:gz') as archive:
                archive.add(dbpath.resolve(), arcname=str(dbpath).lstrip('/'))
        print('Preserving existing MongoDB service settings...', flush=True)
        api.run(['sysrc'] + [name + '=' + value for name, value in service.items()])
        if remove_meta:
            print('Removing the unused npm metapackage before the packaged Node runtime replacement...', flush=True)
            api.run(['pkg-static', 'delete', '-y', 'npm'])
        api.install_candidate(repo, repos, candidate)
        api.configuration.repair(recovery, Path(args.config_defaults), fresh=False)
    finally:
        if stopped or not process:
            live = mongo_process(api.run(['ps', 'axww', '-o', 'pid=', '-o', 'command=']))
            if live is None:
                api.run(['service', 'mongod', 'onestart'])
    after = inventory(factory)
    api.require(after['dbpath'] == str(dbpath) and after['version'].startswith(candidate['version'].split('_')[0]),
                'Database path/version verification failed; recovery files retained')
    if before:
        api.require(after['subscribers'] == before['subscribers'] and after['provisioning_sha256'] == before['provisioning_sha256'],
                    'Subscriber provisioning changed during the upgrade; recovery files retained for review')
    api.run(['sysrc', 'mongod_enable=YES'])
    api.persist_repository(args, recovery, contents)
    api.migration.atomic_json(recovery / 'installation.json', {
        'status': 'verified', 'mode': 'upgrade', 'cpu_profile': profile, 'candidate': candidate,
        'database_path_preserved': True, 'subscribers': after['subscribers'],
        'provisioning_verified': before is not None, 'repository_persisted': contents is not None})
    print('SUCCESS: OPNcell upgrade verified; existing database and cellular configuration preserved.', flush=True)
