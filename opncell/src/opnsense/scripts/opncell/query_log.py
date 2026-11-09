#!/usr/local/bin/python3.13
"""Use the platform log parser with the actual cellular daemon destination."""
import json
from pathlib import Path
import runpy
import sys
from log_source import resolve_log

if len(sys.argv) == 3 and sys.argv[1] == "--source":
    print(json.dumps({"path": str(resolve_log(sys.argv[2]))}))
else:
    sys.path.insert(0, "/usr/local/opnsense/scripts/syslog")
    from log_matcher import LogMatcher
    original = LogMatcher.fetch_log_filenames

    def filenames(filename, module):
        if module == "opncell":
            return [str(resolve_log(filename))]
        return original(filename, module)

    LogMatcher.fetch_log_filenames = staticmethod(filenames)
    runpy.run_path("/usr/local/opnsense/scripts/syslog/queryLog.py", run_name="__main__")
