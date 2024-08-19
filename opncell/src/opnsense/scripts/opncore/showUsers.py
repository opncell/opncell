#!/usr/local/bin/python3

import yaml
import subprocess
import ujson
import sys
import json
import os


def fetch_users():
    os.environ['PATH'] = '/usr/local/opnsense/scripts/opncore/opncore_db.sh:' + os.environ.get('PATH', '')
    os.environ['PATH'] = '/bin/bash:' + os.environ.get('PATH', '')
    os.environ['PATH'] = '/root/mongo/build/install/bin/:' + os.environ.get('PATH', '')
    os.environ['PATH'] = '/root/mongo/build/install/bin/mongod:' + os.environ.get('PATH', '')
    os.environ['PWD'] = '/usr/local/opnsense/scripts/opncore:' + os.environ.get('PWD', '')

    script_path = '/usr/local/opnsense/scripts/opncore/opncore_db.sh'
    bash_script = f'{script_path} showfiltered'
    script_arguments = ['showfiltered']
    i = ['3147000348934279']
    # Use subprocess to run the Bash script
    user_details = []
    dets = {}

    try:
        output = subprocess.check_output([script_path] + script_arguments , text=True, stderr=subprocess.STDOUT)
        #  Run the Bash script
        output_list = output.strip().split('\n')

        # Parse each JSON object separately
        for json_str in output_list:
            try:
                data = json.loads(json_str)
                imsi = data.get("imsi")
                k = data.get("security", {}).get("k")
                opc = data.get("security", {}).get("opc")

                # Extract the "name" field from the "session" array if it exists
               # session = data.get("slice", [{}])[0].get("session", [{}])
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
               # print(f"Error parsing JSON: {e}")
                pass
        print(ujson.dumps(user_details))

    except subprocess.CalledProcessError as e:

        pass

    return user_details


fetch_users()
