#!/usr/local/bin/python3
import yaml
import subprocess
import ujson

process_names = []

result_dict = {}

# Define the target keys
target_keys = ['db_uri', 'freeDiameter', 'metrics','dns','tai','network_name','nsi']


def extract_nested_key_value(data, target_keys, current_key=''):
    extracted_data = {}
    for key, value in data.items():
        new_key = f'{current_key}.{key}' if current_key else key
        if isinstance(value, dict):
            extracted_data.update(extract_nested_key_value(value, target_keys, new_key))
        elif key in target_keys:
            extracted_data[new_key] = value
    return extracted_data


def running_processes():
    command = "ps aux | grep open5gs | awk '$8 == \"Is\" || $8 == \"Ss\" || $8 == \"Rs\" {print $2}'"
    output = subprocess.check_output(command, shell=True, text=True)

    pid_list = output.strip().split("\n")

    # Iterate through the list of PIDs
    for pid in pid_list:
        try:
            process_name = subprocess.check_output(f"ps -p {pid} -o comm=", shell=True, text=True).strip()
            name = process_name.replace("open5gs-", "").rstrip("d")
            yaml_file_path = '/usr/ports/open5gs/install/etc/open5gs/' + name + '.yaml'

            with open(yaml_file_path, 'r') as file:
                yaml_data = yaml.safe_load(file)
                extracted_data = extract_nested_key_value(yaml_data, target_keys)

            process_info = {"PID": pid, "Name": name, "config": extracted_data}

            process_names.append(process_info)

        except subprocess.CalledProcessError:
            print(f"Process with PID {pid} does not exist or an error occurred")

    print(ujson.dumps(process_names))

    return process_names
running_processes()
