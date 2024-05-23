#!/usr/local/bin/python3

import yaml
import subprocess
import ujson
import sys
import json

if len(sys.argv) > 1:

    x = sys.argv[1]
    y = x.replace('[', "")
    t = y.replace(']', '')
    json_data = json.loads(t)

    def running_processes():
        command = "ps aux | grep open5gs | awk '$8 == \"Is\" || $8 == \"Ss\" || $8 == \"Rs\" {print $2}'"
        output = subprocess.check_output(command, shell=True, text=True)

        pid_list = output.strip().split("\n")

        process_names = []

        # Iterate through the list of PIDs
        for pid in pid_list:
            try:
                process_name = subprocess.check_output(f"ps -p {pid} -o comm=", shell=True, text=True).strip()
                process_info = {"PID": pid, "Name": process_name}
                process_names.append(process_info)

            except subprocess.CalledProcessError:
                print(f"Process with PID {pid} does not exist or an error occurred")
        print(ujson.dumps(process_names))   #print for testing purposes.

        return process_names

    pList = running_processes()

    def update_yaml_data(yaml_data, update_key, user_provided_values):
        if isinstance(yaml_data, dict):
            for key, value in yaml_data.items():
                if key == update_key:
                    print(type(update_key))
                    if user_provided_values.isdigit():
                        integer_value = int(user_provided_values)
                        yaml_data[key] = integer_value
                    else:
                        val = user_provided_values.strip("'")
                        yaml_data[key] = val
                else:
                    update_yaml_data(value, update_key, user_provided_values)
        elif isinstance(yaml_data, list):
            for item in yaml_data:
                update_yaml_data(item, update_key, user_provided_values)


    def reconfigure(process_list):
        for process in process_list:
            name = process.get("Name", "")
            pid = process.get("PID", "")
            process_name = name.replace("open5gs-", "").rstrip("d")
            yaml_file_path = '/usr/ports/open5gs/install/etc/open5gs/' + process_name + '.yaml'

            permit = "chmod +x " + yaml_file_path
            output = subprocess.run(permit, shell=True, text=True)
            # Read the YAML file
            with open(yaml_file_path, 'r') as file:
                yaml_data = yaml.safe_load(file)

            if "general" in json_data and isinstance(json_data["general"], dict):
                for key, value in json_data["general"].items():
                    update_yaml_data(yaml_data, key, value)
            else:
                print("Invalid JSON data format. It should have a 'general' dictionary")

            with open(yaml_file_path, 'w') as file:
                yaml.dump(yaml_data, file, default_flow_style=False)

            # stop and restart the services with new config file
            kill_command = "kill -9 " + pid
            output = subprocess.run(kill_command, shell=True, text=True)
            command = "/usr/ports/open5gs/install/bin/" + name + " -D -c " + yaml_file_path
            output = subprocess.run(command, shell=True, text=True)

    reconfigure(pList)
else:
    print("No arguments passed")
