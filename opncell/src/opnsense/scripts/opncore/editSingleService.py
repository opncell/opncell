#!/usr/local/bin/python3

import yaml
import subprocess
import ujson
import sys
import json
import os

if len(sys.argv) > 1:

    x = sys.argv[1]
    y = x.replace('[', "")
    t = y.replace(']', '')
    json_data = json.loads(t)
   # json_data = json.loads(json_data2)
    # create a temporary directory with write permissions- to use for file editing
    new_dir = '/tmp/yaml'
    os.makedirs(new_dir, exist_ok=True)
    os.chmod(new_dir, 0o777)
    print(json_data)
    print(type(json_data))
    server = ''
    pid = ''
    new_addr = ''
    configurableServices = ['sgwu', 'sgwc', 'amf', 'scp', 'pcf', 'nssf', 'smf', 'ausf', 'upf', 'mme']
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            if key == 'server':
                server = value
            if key == 'ip':
                new_addr = value
            if key == 'pid':
                pid = value
    #print(pid,server,new_addr)
    def config(service_list, name, process_pid):
        yaml_path = '/usr/local/etc/open5gs/'
        process_name = name.strip('d')
        print(process_name)
        if process_name in service_list:
            print(name) 
            yaml_file = yaml_path + process_name + '.yaml'
            # Copy the file to a directory where you have write permissions i.e /tmp/yaml .
            # (/tmp/ folder because we copy the files back to where the service expects them, after the edit)

            copy_file = f"cp {yaml_file} {new_dir}/"
            os.system(copy_file)
            new = '/tmp/yaml/' + process_name + '.yaml'
            os.chmod(new, 0o777)  # make file writable as well

            # Read the YAML file
            with open(yaml_file, 'r') as file:
                yaml_data = yaml.safe_load(file)

            # Replace values in the configuration--It's faster to access individual elements than loop through
            # the whole file

            if process_name == 'sgwu':
                yaml_data['sgwu']['gtpu']['server'][0]['address'] = new_addr.strip("'")

            elif process_name == 'sgwc':
                yaml_data['sgwc']['gtpc']['server'][0]['address'] = new_addr.strip("'")

            elif process_name == 'amf':
                yaml_data['amf']['ngap']['server'][0]['address'] = new_addr.strip("'")

            elif process_name == 'mme':
                yaml_data['mme']['s1ap']['server'][0]['address'] = new_addr.strip("'")

            elif process_name == 'upf':
                yaml_data['upf']['gtpu']['server'][0]['address'] = new_addr.strip("'")

            elif process_name == 'ausf':
                yaml_data['ausf']['sbi']['server'][0]['address'] = new_addr.strip("'")

            elif process_name == 'smf':
                yaml_data['smf']['gtpu']['server'][0]['address'] = new_addr.strip("'")

            elif process_name == 'nssf':
                yaml_data['nssf']['sbi']['server'][0]['address'] = new_addr.strip("'")

            elif process_name == 'pcf':
                yaml_data['pcf']['sbi']['server'][0]['address'] = new_addr.strip("'")

            elif process_name == 'scp':
                yaml_data['scp']['sbi']['server'][0]['address'] = new_addr.strip("'")

            if process_pid != 0:
                kill_command = "kill -9 " + process_pid
                output = subprocess.run(kill_command, shell=True, text=True)

            with open(new, 'w') as file:
                yaml.safe_dump(yaml_data, file, sort_keys=False, default_flow_style=False)

            copy_file = f"cp {new} {yaml_path}"
            os.system(copy_file)

            command = "/usr/ports/open5gs/install/bin/" + 'open5gs-' + name + " -D "
            subprocess.run(command, shell=True, text=True)

    config(configurableServices, server, pid)
else:
    print("No arguments passed")
