#!/usr/bin/env python3
"""Copy and HTTP-verify a new dual-CPU repository; never activate its public link."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import urllib.parse
import urllib.request


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def remote_digest(base_url, relative):
    url = base_url.rstrip('/') + '/' + urllib.parse.quote(relative, safe='/:')
    result = hashlib.sha256()
    with urllib.request.urlopen(url, timeout=60) as response:
        while chunk := response.read(1024 * 1024):
            result.update(chunk)
    return result.hexdigest()


def stage(args):
    source = Path(args.source).resolve(strict=True)
    destination = Path(args.destination)
    if destination.is_symlink():
        raise ValueError('Destination must be a new release directory, not a live symlink')
    destination = destination.resolve()
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError('Source and destination must be separate directories')
    if destination.exists() and any(destination.iterdir()):
        raise ValueError('Destination must be empty; existing releases are never overwritten')
    expected = {}
    for profile in ['noavx', 'avx2']:
        manifest = json.loads((source / profile / 'SHA256.json').read_text())
        if not manifest:
            raise ValueError('Empty package manifest: ' + profile)
        for name, checksum in manifest.items():
            if Path(name).name != name or not name.endswith('.pkg'):
                raise ValueError('Invalid package filename')
            path = source / profile / 'All' / name
            if digest(path) != checksum:
                raise ValueError('Source package hash mismatch: ' + name)
            expected[str(path.relative_to(source))] = checksum
        for path in (source / profile).iterdir():
            if path.is_file():
                expected[str(path.relative_to(source))] = digest(path)
    for path in source.iterdir():
        if path.is_file() and not path.is_symlink():
            expected[path.name] = digest(path)
    for name in ['FreeBSD:14:amd64', 'FreeBSD:15:amd64', 'FreeBSD:15:amd64-avx2']:
        if not (source / name / 'meta.conf').is_file():
            raise ValueError('Missing ABI/CPU route: ' + name)
    shutil.copytree(source, destination, symlinks=True, dirs_exist_ok=True)
    for relative, checksum in expected.items():
        if remote_digest(args.base_url, relative) != checksum:
            raise ValueError('HTTP hash mismatch: ' + relative)
    for name in ['FreeBSD:14:amd64', 'FreeBSD:15:amd64', 'FreeBSD:15:amd64-avx2']:
        if remote_digest(args.base_url, name + '/meta.conf') != digest(source / name / 'meta.conf'):
            raise ValueError('HTTP ABI/CPU route mismatch: ' + name)
    report = {'staged_url': args.base_url, 'http_files_verified': len(expected),
              'abi14_preserved': True, 'cpu_routes': ['noavx', 'avx2'], 'public_activated': False}
    Path(args.report).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['source', 'destination', 'base-url', 'report']:
        parser.add_argument('--' + name, required=True)
    stage(parser.parse_args())
