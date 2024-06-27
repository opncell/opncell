#!/usr/local/bin/python3

import subprocess
import sys
import json
import os
import ast

os.environ['PATH'] = '/usr/local/opnsense/scripts/opncore/opncore_db.sh:' + os.environ.get('PATH', '')
os.environ['PATH'] = '/bin/bash:' + os.environ.get('PATH', '')
os.environ['PATH'] = '/root/mongo/build/install/bin/:' + os.environ.get('PATH', '')
os.environ['PATH'] = '/root/mongo/build/install/bin/mongod:' + os.environ.get('PATH', '')
os.environ['PWD'] = '/usr/local/opnsense/scripts/opncore:' + os.environ.get('PWD', '')

if len(sys.argv) > 0:
    script_path = '/usr/local/opnsense/scripts/opncore/opncore_db.sh'
    x = sys.argv[1]
    y = x.replace('[', "")
    t = y.replace(']', '')
    json_data = json.loads(t)
    # print(type(json_data))

    imsi = []
    ip = []
    apn = []
    arp_priority = []
    dl = []
    unit = ['2']
    ul = []  # 2 is the unit for megabytes in mongodb
    arp_capability = []
    arp_vulnerability = []
    qos = []
    sst = []

    if isinstance(json_data, dict):
        # print(json_data)
        try:
            for key, value in json_data.items():
                if key == "imsi":
                    imsi.append(str(value))
                    # print(imsi[0])
                if key == "sst":
                    sst.append(str(value))
                if key == "apn":
                    if value != "":
                        apn.append(str(value))
                if key == "ip":
                    if value != "":
                        ip[0] = (str(value))
                if key == "dl":
                    if value != " ":
                        dl.append(str(value))
                if key == "unit":
                    if value != "":
                        unit.append(str(value))
                if key == "ul":
                    if value != "":
                        ul.append(str(value))
                if key == "QoS":
                    if value != "":
                        qos.append(str(value))
                if key == "arp_priority":
                    if value != "":
                        arp_priority.append(str(value))
                if key == "arp_capability":
                    if value != "":
                        arp_capability.append(str(value))
                if key == "arp_vulnerability":
                    if value != "":
                        arp_vulnerability.append(str(value))

            # print(imsi, sst, apn, dl, unit, ul, qos, arp_priority, arp_capability, arp_vulnerability)
            # print("here")
            output = subprocess.check_output([script_path] + ['set_apn'] + imsi + apn + sst + dl + unit + ul
                                             + qos + arp_priority + arp_capability + arp_vulnerability,
                                             text=True, stderr=subprocess.STDOUT)

        except:
            pass
else:
    print("No args")
