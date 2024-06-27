#!/usr/local/bin/python3

import yaml
import subprocess
import ujson
import sys
import json
import os

if len(sys.argv) > 0:
    def fetch():
        os.environ['PATH'] = '/usr/local/opnsense/scripts/opncore/opncore_db.sh:' + os.environ.get('PATH', '')
        os.environ['PATH'] = '/bin/bash:' + os.environ.get('PATH', '')
        os.environ['PATH'] = '/root/mongo/build/install/bin/:' + os.environ.get('PATH', '')
        os.environ['PATH'] = '/root/mongo/build/install/bin/mongod:' + os.environ.get('PATH', '')
        os.environ['PWD'] = '/usr/local/opnsense/scripts/opncore:' + os.environ.get('PWD', '')
        # print(os.environ)

        script_path = '/usr/local/opnsense/scripts/opncore/opncore_db.sh'
        imsi = []
        x = sys.argv[1]
        y = x.replace('[', "")
        t = y.replace(']', '')
        #    z = json.loads(t)
        json_data = json.loads(t)
        # print(type(json_data))
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                #      print(key)
                if key == "imsi":
                    imsi.append(value)

        # print(imsi)

        showAll = ['showfiltered']
        remove = ['remove']

        # Use subprocess to run the Bash script
        user_details = []
        dets = {}

        try:
            if imsi:
                delete = subprocess.check_output([script_path] + remove + imsi, text=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            # print(f"Error running the Bash script: {e}")
            # print(f"Command output: {e.output}")
            pass

    fetch()
else:
    print("No arguments passed")
