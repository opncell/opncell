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
       # z = json.loads(t)
        json_data = json.loads(t)
        #print(type(json_data))
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                if key == "imsi":
                    imsi.append(value)
        showAll = ['showfiltered']
        showOne = ['showone']

    # Use subprocess to run the Bash script
        user_details = []
        try:
            if not imsi:
                output = subprocess.check_output([script_path] + showAll, text=True, stderr=subprocess.STDOUT)
            else:
                output = subprocess.check_output([script_path] + showOne + imsi, text=True, stderr=subprocess.STDOUT)
                #  Run the Bash script
                output_list = output.strip().split('\n')
                # Parse each JSON object separately
                for json_str in output_list:
                    try:
                        data = json.loads(json_str)
                        #print(data)
                        imsi = data.get("imsi")
                        k = data.get("security", {}).get("k")
                        opc = data.get("security", {}).get("opc")
                        slice_array = data.get("slice", [])
                        names = []
               # print(type(slice_array))
                        for slice_data in slice_array:
                   # print(slice_array)
                            session_array = slice_data.get("session", [])
                            for session_data in session_array:
                                name = session_data.get("name")
                                names.append(name)
                #names = [session_data.get("name") for session_data in session]
                            names_str = ",".join(names)
                        dets = {"imsi": imsi, "ki": k, "opc": opc, "apn": names_str}
                        user_details.append(dets)

                    except json.JSONDecodeError as e:
                        pass
        except subprocess.CalledProcessError as e:
            pass

        print(ujson.dumps(user_details))

    fetch()
else:
    print("No arguments passed")
