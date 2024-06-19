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
    #json_data = json.loads(json_data2)
   # print(type(json_data))
    # create a temporary directory with write permissions- to use for file editing
    new_dir = '/tmp/yaml'
    os.makedirs(new_dir, exist_ok=True)
    os.chmod(new_dir, 0o777)

    if "general" in json_data and isinstance(json_data["general"], dict):
        new_addr = ''
        new_mcc = ''
        for key, value in json_data["general"].items():
            if key == 'sst':
                sst = value
            if key == 'tac':
                new_tac = value
            if key == 'mcc':
                new_mcc = value
            if key == 'mnc':
                new_mnc = value
            if key == 's1ap':
                new_addr = value
            if key == 'ue':
                ue = value
            if key == 'peer':
                peer = value
            if key == 'network':
                network = value
            if key == 'network_name':
                network_name = value



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
        # print(ujson.dumps(process_names))

        return process_names


    pList = running_processes()


    def config(service_list, process_name, pid, name):
        yaml_path = '/usr/ports/open5gs/install/etc/open5gs/'
        if process_name in service_list:
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
                yaml_data['global']['max']['ue'] = ue
                yaml_data['global']['max']['peer'] = peer
                yaml_data['logger']['file']['level'] = "debug"

            if process_name == 'upf':
                yaml_data['upf']['gtpu']['server'][0]['address'] = new_addr.strip("'")
                yaml_data['global']['max']['ue'] = ue
                yaml_data['global']['max']['peer'] = peer
                yaml_data['logger']['file']['level'] = "debug"

            if process_name == 'nrf':
                yaml_data['nrf']['serving'][0]['plmn_id']['mcc'] = new_mcc
                yaml_data['nrf']['serving'][0]['plmn_id']['mnc'] = new_mnc
                yaml_data['global']['max']['ue'] = ue
                yaml_data['global']['max']['peer'] = peer
                yaml_data['logger']['file']['level'] = "debug"

            if process_name == 'amf':
                yaml_data['amf']['ngap']['server'][0]['address'] = new_addr.strip("'")
                yaml_data['amf']['guami'][0]['plmn_id']['mcc'] = new_mcc
                yaml_data['amf']['guami'][0]['plmn_id']['mnc'] = new_mnc
                yaml_data['amf']['tai'][0]['plmn_id']['mcc'] = new_mcc
                yaml_data['amf']['tai'][0]['plmn_id']['mnc'] = new_mnc
                yaml_data['amf']['plmn_support'][0]['plmn_id']['mcc'] = new_mcc
                yaml_data['amf']['plmn_support'][0]['plmn_id']['mnc'] = new_mnc
                yaml_data['amf']['tai'][0]['tac'] = int(new_tac)
                yaml_data['amf']['network_name']['full'] = network_name
                yaml_data['logger']['file']['level'] = "debug"
                yaml_data['global']['max']['ue'] = ue
                yaml_data['global']['max']['peer'] = peer

            if process_name == 'mme':
                yaml_data['mme']['tai'][0]['tac'] = int(new_tac)
                yaml_data['mme']['s1ap']['server'][0]['address'] = new_addr.strip("'")
                yaml_data['mme']['gummei'][0]['plmn_id']['mcc'] = new_mcc
                yaml_data['mme']['gummei'][0]['plmn_id']['mnc'] = new_mnc
                yaml_data['mme']['tai'][0]['plmn_id']['mcc'] = new_mcc
                yaml_data['mme']['tai'][0]['plmn_id']['mnc'] =  new_mnc
                yaml_data['mme']['network_name']['full'] = network_name
                yaml_data['logger']['file']['level'] = "debug"
                yaml_data['global']['max']['ue'] = ue
                yaml_data['global']['max']['peer'] = peer

            if pid != 0:
                kill_command = "kill -9 " + pid
                output = subprocess.run(kill_command, shell=True, text=True)

            with open(new, 'w') as file:
                yaml.safe_dump(yaml_data, file,sort_keys=False, default_style=None, default_flow_style=False)

            copy_file = f"cp {new} {yaml_path}"
            os.system(copy_file)

            command = "/usr/ports/open5gs/install/bin/" + name + " -D "
            subprocess.run(command, shell=True, text=True)


    def configureProcess(process_name, pid, name):

        configurableServices = ['nrf', 'upf', 'amf']
        configurableFourServices = ['mme', 'sgwu']

        if network == 'enablefour':
            config(configurableFourServices, process_name, pid, name)
        else:
            config(configurableServices, process_name, pid, name)


    def reconfigure(process_list):
        # only edit what needs to be edited. mme + sgwu for 4g and 5g-nsa networks. amf + upf + nrf for 5gsa networks
        runningProcesses = []
        configurableServices = ['mme', 'sgwu', 'nrf', 'amf', 'upf']
        for process in process_list:
            name = process.get("Name", "")
            pid = process.get("PID", "")
            process_name = name.replace("open5gs-", "").rstrip("d")
            runningProcesses.append(process_name)
            configureProcess(process_name, pid, name)

        # get the processes that should be reconfigured, but they weren't running initially.

        difference_set = set(configurableServices) - set(runningProcesses)
        not_running_processes = list(difference_set)
        d = set(runningProcesses) - set(configurableServices)
        n_r = list(d)
        final_list = n_r + not_running_processes
        for process in final_list:
            name = "open5gs-" + process + "d"
            configureProcess(process, 0, name)


    reconfigure(pList)
else:
    print("No arguments passed")
