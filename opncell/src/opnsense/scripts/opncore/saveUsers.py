#!/usr/local/bin/python3

import subprocess
import sys
import json
import os
import ujson

os.environ['PATH'] = '/usr/local/opnsense/scripts/opncore/opncore_db.sh:' + os.environ.get('PATH', '')
os.environ['PATH'] = '/bin/bash:' + os.environ.get('PATH', '')
os.environ['PATH'] = '/root/mongo/build/install/bin/:' + os.environ.get('PATH', '')
os.environ['PATH'] = '/root/mongo/build/install/bin/mongod:' + os.environ.get('PATH', '')
os.environ['PWD'] = '/usr/local/opnsense/scripts/opncore:' + os.environ.get('PWD', '')

if len(sys.argv) > 1:
    script_path = '/usr/local/opnsense/scripts/opncore/opncore_db.sh'
    x = sys.argv[1]
    y = x.replace('[', "")
    t = y.replace(']', '')
    ip = ""

    json_data = json.loads(t)
    #json_data = json.loads(json_data2)

    if isinstance(json_data, dict):
        try:
            num_profiles = int(json_data['count'])
            first_apn = json_data['1']

            imsi = first_apn["imsi"]
            ki = first_apn["ki"]
            opc = first_apn["opc"]
            if "ip" in first_apn:
                ip = first_apn["ip"]

            # Create the argument list
            if ip == "":
                args = [script_path, 'add', imsi, ki, opc]
                for i in range(1, num_profiles + 1):
                    profile = json_data[str(i)]
                    args.extend([
                        profile["apn"],
                        profile["sst"],
                        profile["dl"],
                        profile["ul"],
                        profile["QoS"],
                        profile["arp_priority"],
                        profile["arp_capability"],
                        profile["arp_vulnerability"]
                    ])
               # print(args)
                    # Call the shell script with the arguments
                output = subprocess.check_output(args, text=True, stderr=subprocess.STDOUT)
            else:
                args = [script_path, 'add_with_ip', imsi, ki, opc]
                for i in range(1, num_profiles + 1):
                    profile = json_data[str(i)]
                    args.extend([
                        profile["apn"],
                        profile["sst"],
                        profile["dl"],
                        profile["ul"],
                        profile["QoS"],
                        profile["arp_priority"],
                        profile["arp_capability"],
                        profile["arp_vulnerability"],
                        profile["ip"]
                    ])
                #print(args)
                    # Call the shell script with the arguments
                output = subprocess.check_output(args, text=True, stderr=subprocess.STDOUT)

            output_list = output.strip().split('\n')
         #   print(output_list)
            if len(output_list) > 1 and output_list[-2] == "Success":
                result = "Success"
            elif output_list[0] == "Success":
                result = "Success"
            elif "Duplicate" in output_list[0]:
                result = "Duplicate"
            else:
                result = "Failed"
        except Exception as e:
            result = f"Error: {str(e)}"
    else:
        result = "Invalid JSON data"
else:
    result = "No input provided"

print(ujson.dumps(result))
