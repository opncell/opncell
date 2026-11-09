"""Resolve the same daemon log for viewing, exporting, and clearing."""
from pathlib import Path
import shlex
import subprocess

SCOPES = frozenset("amf ausf bsf hss mme nrf nssf pcf pcrf scp sgwc sgwu smf udm udr upf mongod".split())


def resolve_log(scope, processes=None):
    if scope not in SCOPES:
        raise ValueError("Unknown cellular log")
    if processes is None:
        processes = subprocess.check_output(["/bin/ps", "axww", "-o", "command="], text=True)
    executable = "mongod" if scope == "mongod" else "open5gs-" + scope + "d"
    for line in processes.splitlines():
        try:
            args = shlex.split(line)
        except ValueError:
            continue
        if not args or Path(args[0]).name != executable:
            continue
        option = "--logpath" if scope == "mongod" else "-l"
        for index, arg in enumerate(args):
            value = args[index + 1] if arg == option and index + 1 < len(args) else None
            if arg.startswith(option + "="):
                value = arg.split("=", 1)[1]
            if value and Path(value).is_absolute() and ".." not in Path(value).parts:
                return Path(value)
    return Path("/var/db/mongodb/mongod.log") if scope == "mongod" else Path("/var/log/opncell") / (scope + ".log")
