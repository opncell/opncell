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
    process_names = []
    running_processes_names = []
    network = ""

    if isinstance(json_data, dict):
      #  print(json_data)
        try:
            for key, value in json_data.items():
                if key == "network":
                    network = str(value)
        except:
            pass
    
    # print(network)
    result_dict = {}
    # Define the target keys
    target_keys = ['metrics','dns','tai','network_name','nsi','s1ap','ngap']
    
    fourGServices = ["hss", "mme", "pcrf",  "sgwu", "sgwc","smf", "upf"]
    fiveNSAGServices = ["hss", "mme","pcrf",  "sgwu",  "sgwc","smf",  "upf"]
    fiveGSAServices = ["nrf", "scp", "amf", "smf", "upf", "ausf", "udm", "udr","pcf", "nssf","bsf"]
    
    
    def extract_nested_key_value(data, target_keys, current_key=''):
        extracted_data = {}
        for key, value in data.items():
            new_key = f'{current_key}.{key}' if current_key else key
            if isinstance(value, dict):
                extracted_data.update(extract_nested_key_value(value, target_keys, new_key))
            elif value == 'server':
                nested_key = value
                extracted_data.update(extract_nested_key_value(value, target_keys, nested_key))
            elif isinstance(value, list):
                extracted_data[new_key] = value
            elif key in target_keys:
                extracted_data[new_key] = value
        return extracted_data
    
    
    def running_processes():
        command = "ps aux | grep open5gs | awk '$8 == \"Is\" || $8 == \"Ss\" || $8 == \"Rs\" {print $2}'"
       # command_mongo = "ps aux | grep mongod | awk '$8 == \"Is\" || $8 == \"I\" || $8 == \"S\" {print $2}'"
        command_mongo = "ps aux | grep mongod | grep -v grep | awk '{print $2}' | head -n 1"
        output = subprocess.check_output(command, shell=True, text=True)
        output_mongo = subprocess.check_output(command_mongo, shell=True, text=True)
        pid_list = output.strip().split("\n")
       # print(output_mongo)
        try:
            pid_mongo = output_mongo.strip().split("\n")
            process_name_mongo = subprocess.check_output(f"ps -p {pid_mongo[0]} -o comm=", shell=True, text=True).strip()
            p = {"PID":pid_mongo[0], "Name":process_name_mongo, "config":{"mongod.bind": [{"address":"127.0.0.1"}]}}
        except:
            #pass
            p = {"PID": "Stopped", "Name": "mongod", "config":{"mongod.bind": [{"address":"127.0.0.1"}]}}
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
                running_processes_names.append(name)
    
                process_names.append(process_info)
    
            except subprocess.CalledProcessError:
                pass
             #   print(f"Process with PID {pid} does not exist or an error occurred")
        try:
            not_running_processes = {}
            if network == 'enablefour':
                difference_set = set(fourGServices) - set(running_processes_names)
                not_running_processes = list(difference_set)
            elif network == 'enablefiveSA':
                difference_set = set(fiveGSAServices) - set(running_processes_names)
                not_running_processes = list(difference_set)
            elif network == 'enablefiveNSA':
                difference_set = set(fiveNSAGServices) - set(running_processes_names)
                not_running_processes = list(difference_set)
    
            for process in not_running_processes:
                pr = {"PID": "Stopped", "Name": process}
                process_names.append(pr)
            process_names.append(p)
        except:
            pass
        print(ujson.dumps(process_names))
        # print(ujson.dumps(pid_mongo))
    
        return process_names
    running_processes()
else:
    print("No arguments")
