#!/usr/local/bin/python3
"""Check effective rc settings, including rc.conf.d overrides rendered by configd."""
import json
import re
import subprocess
import sys

ALL = ('amf', 'ausf', 'bsf', 'hss', 'mme', 'nrf', 'nssf', 'pcf', 'pcrf',
       'scp', 'sgwc', 'sgwu', 'smf', 'udm', 'udr', 'upf')
EPC = ('hss', 'mme', 'pcrf', 'sgwc', 'sgwu', 'smf', 'upf', 'nrf', 'scp')
NETWORKS = {'enablefour': EPC, 'enablefiveNSA': EPC,
            'enablefiveSA': ('nrf', 'scp', 'amf', 'smf', 'upf', 'ausf', 'udm', 'udr', 'pcf', 'nssf', 'bsf'),
            'enableupf': ('upf',)}


def check(network, runner=subprocess.run):
    if network not in NETWORKS:
        return {'result': 'failed', 'message': 'Unknown cellular topology'}
    mismatches = []
    mongo = runner(['/usr/sbin/service', 'mongod', 'rcvar'], capture_output=True, text=True)
    if mongo.returncode or not re.search(r'^mongod_enable="YES"\s*$', mongo.stdout, re.M):
        mismatches.append('mongod (expected YES)')
    for daemon in ALL:
        name = 'epc' + daemon + 'd'
        result = runner(['/usr/sbin/service', name, 'rcvar'], capture_output=True, text=True)
        match = re.search(r'^' + re.escape(name) + r'_enable="([^"]*)"\s*$', result.stdout, re.M)
        expected = 'YES' if daemon in NETWORKS[network] else 'NO'
        if result.returncode or match is None or match.group(1).upper() != expected:
            mismatches.append('open5gs-' + daemon + 'd (expected ' + expected + ')')
    if mismatches:
        return {'result': 'failed', 'message': 'Effective boot settings do not match topology: ' + ', '.join(mismatches)}
    return {'result': 'verified'}


if __name__ == '__main__':
    try:
        print(json.dumps(check(sys.argv[1] if len(sys.argv) == 2 else '')))
    except OSError as exc:
        print(json.dumps({'result': 'failed', 'message': 'Cannot inspect boot settings: ' + str(exc)}))
