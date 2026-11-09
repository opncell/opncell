#!/usr/local/bin/python3
"""Remove only obsolete, unreferenced OPNcore log links; retain targets."""
import json
from pathlib import Path
import subprocess
from log_source import SCOPES


def cleanup(directory=Path('/var/log/opncore'), references='', backup=Path('/var/db/opncell/legacy-log-links.json')):
    removed = {}
    if str(directory) in references:
        return {'removed': [], 'skipped': 'Legacy log directory is still referenced'}
    for scope in SCOPES - {'mongod'}:
        path = directory / (scope + '.log')
        expected = '/usr/ports/open5gs/install/var/log/open5gs/' + scope + '.log'
        if path.is_symlink() and str(path.readlink()) == expected:
            removed[str(path)] = expected
    if removed:
        backup.parent.mkdir(parents=True, exist_ok=True)
        existing = json.loads(backup.read_text()) if backup.exists() else {}
        existing.update(removed)
        with backup.open('w') as output:
            json.dump(existing, output, indent=2)
        backup.chmod(0o600)
        for name, target in removed.items():
            path = Path(name)
            if path.is_symlink() and str(path.readlink()) == target:
                path.unlink()
    return {'removed': list(removed)}


if __name__ == '__main__':
    references = subprocess.check_output(['/bin/ps', 'axww', '-o', 'command='], text=True)
    for directory in ['/usr/local/etc/open5gs', '/usr/local/etc/rc.d', '/etc/rc.conf.d']:
        for path in Path(directory).glob('*'):
            if path.is_file():
                references += path.read_text(errors='replace')
    result = cleanup(references=references)
    if result.get('skipped'):
        print('Legacy log links retained: ' + result['skipped'])
    elif result['removed']:
        print('Removed ' + str(len(result['removed'])) + ' obsolete legacy log links; target files preserved.')
    else:
        print('No obsolete legacy log links needed removal.')
