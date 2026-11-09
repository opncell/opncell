#!/usr/local/bin/python3
"""List real, non-zombie cellular processes without matching grep arguments."""
import json
from pathlib import Path
import subprocess
import sys
from log_source import SCOPES


def active_logs(processes=None):
    if processes is None:
        processes = subprocess.check_output(['/bin/ps', 'axww', '-o', 'pid=,stat=,comm='], text=True)
    names = {('mongod' if scope == 'mongod' else 'open5gs-' + scope + 'd'): scope for scope in SCOPES}
    found = {}
    for line in processes.splitlines():
        fields = line.strip().split(None, 2)
        if len(fields) != 3 or not fields[0].isdigit() or int(fields[0]) <= 0:
            continue
        if fields[1].startswith(('Z', 'X')):
            continue
        name = Path(fields[2]).name
        if name not in names:
            continue
        scope = names[name]
        row = found.setdefault(scope, {'name': name, 'scope': scope, 'pids': []})
        row['pids'].append(int(fields[0]))
    return sorted(found.values(), key=lambda row: row['name'])


if __name__ == '__main__':
    try:
        print(json.dumps({'status': 'ok', 'rows': active_logs()}))
    except (OSError, subprocess.CalledProcessError) as error:
        print(json.dumps({'status': 'failed', 'message': 'Cannot inspect active cellular daemons'}))
        sys.exit(1)
