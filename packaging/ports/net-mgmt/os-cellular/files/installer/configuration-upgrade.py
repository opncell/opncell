#!/usr/bin/env python3
"""Preserve and relocate Open5GS configuration; never replace existing settings with defaults."""
from pathlib import Path
import os
import re
import shutil
import subprocess
import tempfile

DIAMETER = ('hss', 'mme', 'pcrf', 'smf')
LEGACY = '/usr/ports/open5gs/install'


def normalize(text):
    # Use IPv4 explicitly for the stock local database; preserve custom URIs.
    text = re.sub(r'(?m)^(\s*db_uri:\s*)mongodb://localhost/open5gs(?=\s*(?:#.*)?$)',
                  r'\1mongodb://127.0.0.1:27017/open5gs', text)
    return (text.replace(LEGACY + '/etc/', '/usr/local/etc/')
            .replace(LEGACY + '/lib/', '/usr/local/lib/')
            .replace(LEGACY + '/var/log/open5gs/', '/var/log/opncell/')
            .replace('/var/log/open5gs/', '/var/log/opncell/'))


def write(path, text, mode=0o600):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as stream:
        temp = Path(stream.name)
        os.chmod(temp, mode)
        stream.write(text)
    os.replace(temp, path)


def preserve(recovery, *, root=Path('/'), legacy=None, fresh=False):
    """Run before package deletion, including files outside the boot environment."""
    stage = Path(recovery) / 'preserved-configs'
    legacy = Path(legacy) if legacy else root / LEGACY.lstrip('/')
    for label, base in (('current', root / 'usr/local/etc'), ('legacy', legacy / 'etc')):
        for name in ('open5gs', 'freeDiameter'):
            source = base / name
            if source.is_dir():
                shutil.copytree(source, stage / label / name, symlinks=False)
    if not fresh:
        missing = [name for name in DIAMETER if not any(
            (stage / label / 'freeDiameter' / (name + '.conf')).is_file()
            for label in ('current', 'legacy'))]
        if missing:
            raise ValueError('Missing original freeDiameter configuration: ' + ', '.join(missing) +
                             '. Recover from backup/snapshot or pass the original --legacy-prefix.')
    return stage


def initialize_tls(root, runner=subprocess.run):
    """Fresh standalone install only; existing TLS material is never rotated."""
    tls = root / 'usr/local/etc/open5gs/tls'
    tls.mkdir(parents=True, exist_ok=True)
    if any(tls.iterdir()):
        # Validation below requires completeness; do not invent a second CA.
        return
    def openssl(*args):
        result = runner(['/usr/bin/openssl', *args], capture_output=True)
        if result.returncode:
            raise ValueError('Local TLS certificate initialization failed; existing files retained')
    ca, key = tls / 'ca.crt', tls / 'ca.key'
    openssl('req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-days', '365',
            '-subj', '/CN=OPNcell local Diameter CA', '-addext', 'basicConstraints=critical,CA:TRUE',
            '-keyout', str(key), '-out', str(ca))
    key.chmod(0o600)
    for name in DIAMETER:
        private, cert, csr = tls / (name + '.key'), tls / (name + '.crt'), tls / (name + '.csr')
        openssl('req', '-new', '-newkey', 'rsa:2048', '-nodes', '-subj', '/CN=' + name + '.localdomain',
                '-keyout', str(private), '-out', str(csr))
        private.chmod(0o600)
        openssl('x509', '-req', '-in', str(csr), '-CA', str(ca), '-CAkey', str(key),
                '-CAcreateserial', '-days', '365', '-out', str(cert))
        csr.unlink()


def empty_example_hnet(text):
    # Generated demonstration Hnet references are not provisioned subscriber keys.
    return re.sub(r'(?m)^  hnet:\s*\n(?:^(?: {3,}.*|\s*#.*|\s*)\n)*',
                  '  hnet: []\n', text)


def repair(recovery, defaults, *, root=Path('/'), fresh=False):
    defaults, recovery = Path(defaults), Path(recovery)
    base = root / 'usr/local/etc'
    for group, pattern in (('open5gs', '*.yaml'), ('freeDiameter', '*.conf')):
        names = {p.name for p in (base / group).glob(pattern)}
        for label in ('current', 'legacy'):
            names.update(p.name for p in (recovery / 'preserved-configs' / label / group).glob(pattern))
        if fresh:
            names.update(p.name for p in (defaults / group).glob(pattern))
        for name in sorted(names):
            target = base / group / name
            if target.is_file():
                source = target
            else:
                choices = [recovery / 'preserved-configs' / label / group / name
                           for label in ('current', 'legacy')]
                if fresh:
                    choices.append(defaults / group / name)
                source = next((p for p in choices if p.is_file()), None)
                if source is None:
                    raise ValueError('No preserved configuration for ' + str(target))
            text = normalize(source.read_text())
            if fresh and name == 'udm.yaml' and source == defaults / group / name:
                text = empty_example_hnet(text)
            if source != target or text != target.read_text():
                write(target, text)
    # Restore TLS/Hnet material missing from the installed tree without replacing keys.
    for label in ('current', 'legacy'):
        for group in ('tls', 'hnet'):
            source = recovery / 'preserved-configs' / label / 'open5gs' / group
            if source.is_dir():
                destination = base / 'open5gs' / group
                destination.mkdir(parents=True, exist_ok=True)
                for p in source.iterdir():
                    if p.is_file() and not (destination / p.name).exists():
                        shutil.copy2(p, destination / p.name)
    for private in (base / 'open5gs').rglob('*.key'):
        private.chmod(0o600)
    if fresh:
        initialize_tls(root)
    (root / 'var/log/opncell').mkdir(parents=True, exist_ok=True)
    missing = []
    for name in DIAMETER:
        config = base / 'freeDiameter' / (name + '.conf')
        if not config.is_file():
            missing.append(str(config))
            continue
        for line in config.read_text().splitlines():
            if not re.match(r'^\s*(?:TLS_Cred|TLS_CA|LoadExtension|Include|include)\b', line):
                continue
            for path in re.findall(r'"(/[^"\n]+)"', line):
                resolved = root / path.lstrip('/')
                if not resolved.is_file():
                    missing.append(path)
    for name in DIAMETER:
        config = base / 'open5gs' / (name + '.yaml')
        if not config.is_file():
            missing.append(str(config))
    if missing:
        raise ValueError('Required configuration resources missing: ' + ', '.join(sorted(set(missing))))
    return {'diameter': list(DIAMETER), 'legacy_paths_corrected': True}
