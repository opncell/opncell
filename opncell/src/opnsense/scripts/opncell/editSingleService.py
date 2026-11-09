#!/usr/local/bin/python3

import ipaddress
import json
import sys
from pathlib import Path

import yaml

from atomic_yaml import replace_yaml


ENDPOINTS = {
    "sgwud": ("sgwu", "gtpu"),
    "sgwcd": ("sgwc", "gtpc"),
    "amfd": ("amf", "ngap"),
    "mmed": ("mme", "s1ap"),
    "upfd": ("upf", "gtpu"),
    "ausfd": ("ausf", "sbi"),
    "smfd": ("smf", "gtpu"),
    "nssfd": ("nssf", "sbi"),
    "pcfd": ("pcf", "sbi"),
    "scpd": ("scp", "sbi"),
}


def main():
    try:
        settings = json.loads(sys.argv[1])
        if isinstance(settings, list) and len(settings) == 1:
            settings = settings[0]
        daemon, endpoint = ENDPOINTS[settings["server"]]
        address = str(ipaddress.ip_address(settings["ip"]))
        path = Path("/usr/local/etc/open5gs") / f"{daemon}.yaml"
        with path.open(encoding="utf-8") as config:
            data = yaml.safe_load(config)
        data[daemon][endpoint]["server"][0]["address"] = address
        replace_yaml(path, data)
    except (IndexError, KeyError, OSError, TypeError, ValueError, yaml.YAMLError):
        print(json.dumps({"result": "failed", "message": "Could not update the service bind address"}))
        return
    print(json.dumps({"result": "saved"}))


if __name__ == "__main__":
    main()
