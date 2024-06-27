#!/usr/local/bin/python3

import yaml
import subprocess
import ujson
import sys
import json
import os

if len(sys.argv) > 0:
    def fetch():
        result = "Failed"
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
        json_data = json.loads(t)
        #json_data = json.loads(json_data2)
        if isinstance(json_data, dict):
            for key, value in json_data.items():
            
                if key == "imsi":
                    imsi.append(value)

        remove = ['remove']

        try:
            if imsi:
                delete_output = subprocess.check_output([script_path] + remove + imsi, text=True,
                                                        stderr=subprocess.STDOUT)
                if int(delete_output) > 0:
                    result = "deleted"
            print(ujson.dumps(result))

        except subprocess.CalledProcessError as e:
            pass

    fetch()

else:
    print("No arguments passed")
