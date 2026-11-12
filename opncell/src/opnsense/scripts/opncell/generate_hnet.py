#!/usr/local/bin/python3
"""Generate Hnet keys through the same validated transaction used by import/delete."""
import base64
import json
import subprocess
import sys
from hnet_management import HnetManager

if __name__ == '__main__':
    try:
        data = json.loads(base64.b64decode(sys.argv[1], validate=True))
        scheme = data.get('scheme', 2)
        print(json.dumps(HnetManager().handle({'operation': 'generate', 'scheme': scheme})))
    except (ValueError, OSError, IndexError, TypeError, subprocess.SubprocessError) as error:
        message = str(error) if isinstance(error, ValueError) else 'Unable to generate Hnet key; check configuration and file permissions'
        print(json.dumps({'result': 'failed', 'error': message}))
