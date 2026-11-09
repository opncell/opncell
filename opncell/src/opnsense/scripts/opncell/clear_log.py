#!/usr/local/bin/python3
"""Clear direct daemon logs without unlinking a writer's open file."""
import json
import os
from pathlib import Path
import stat
import sys

from log_source import SCOPES, resolve_log


def clear_log(scope, directory=None):
    if scope not in SCOPES:
        raise ValueError("Unknown cellular log")
    # Include dated history read by the Diagnostics viewer. Never follow links.
    active = resolve_log(scope) if directory is None else directory / (scope + ".log")
    directory = active.parent
    paths = [active]
    history = directory / scope
    if history.is_dir() and not history.is_symlink():
        paths.extend(sorted(history.glob(scope + "_*.log")))
    cleared = []
    for path in paths:
        try:
            fd = os.open(path, os.O_WRONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        except FileNotFoundError:
            continue
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise ValueError("Log is not a regular file")
            os.ftruncate(fd, 0)
            cleared.append(str(path))
        finally:
            os.close(fd)
    if not cleared:
        raise FileNotFoundError("No cellular log file exists for " + scope)
    return {"status": "ok", "files": cleared}


if __name__ == "__main__":
    try:
        if len(sys.argv) != 2:
            raise ValueError("Exactly one log scope is required")
        print(json.dumps(clear_log(sys.argv[1])))
    except (OSError, ValueError) as error:
        print(json.dumps({"status": "failed", "message": str(error)}))
        sys.exit(1)
