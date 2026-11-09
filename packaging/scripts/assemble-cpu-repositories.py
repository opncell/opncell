#!/usr/bin/env python3
"""Assemble separate CPU catalogs without activating or modifying a live repo."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def assemble(args):
    destination = Path(args.destination)
    if destination.exists():
        raise ValueError('Destination must be new; existing repositories are not overwritten')
    inputs = [Path(args.plugin), Path(args.noavx), Path(args.avx)]
    for path in inputs:
        if not path.is_file():
            raise ValueError('Missing input: ' + str(path))
    if digest(args.avx) != '979998024cc113ecb656f7bd848ebd3855044c7151a827e6d602b4335a479164':
        raise ValueError('AVX artifact differs from the tested official package')
    if digest(args.noavx) != '58702bf6382c03478800c265cea34d7ceb76a977eb8ecf997f1d0e01e78d4797':
        raise ValueError('NOAVX artifact differs from the Atom-tested package')
    legacy = Path(args.legacy_abi14).resolve(strict=True)
    if not (legacy / 'meta.conf').is_file():
        raise ValueError('Legacy ABI14 catalog is missing')
    common = [p for p in Path(args.common).glob('*.pkg')
              if not p.name.startswith(('mongodb80-', 'os-cellular-'))]
    if not common:
        raise ValueError('Common dependency package directory is empty')
    destination.mkdir(parents=True)
    report = {'catalogs': {}, 'abi14': str(legacy), 'public_activated': False}
    for profile, mongo in [('noavx', Path(args.noavx)), ('avx2', Path(args.avx))]:
        catalog = destination / profile
        packages = catalog / 'All'
        packages.mkdir(parents=True)
        for source in common + [Path(args.plugin), mongo]:
            shutil.copy2(source, packages / source.name)
        checksums = {p.name: digest(p) for p in sorted(packages.glob('*.pkg'))}
        (catalog / 'SHA256.json').write_text(json.dumps(checksums, indent=2) + '\n')
        subprocess.run([args.pkg_tool, 'repo', str(catalog)], check=True)
        report['catalogs'][profile] = {'packages': len(checksums), 'mongodb': mongo.name,
                                       'plugin_sha256': digest(args.plugin)}
    for name, target in [('FreeBSD:15:amd64', 'noavx'), ('FreeBSD:15:amd64-avx2', 'avx2'),
                         ('FreeBSD:15:amd64-noavx', 'noavx'), ('FreeBSD:14:amd64', str(legacy))]:
        (destination / name).symlink_to(target, target_is_directory=True)
    (destination / 'cpu-catalogs.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['destination', 'common', 'plugin', 'noavx', 'avx', 'legacy-abi14']:
        parser.add_argument('--' + key, required=True)
    parser.add_argument('--pkg-tool', default='pkg')
    assemble(parser.parse_args())
