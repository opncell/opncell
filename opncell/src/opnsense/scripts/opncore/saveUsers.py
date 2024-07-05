#!/usr/local/bin/python3

import subprocess
import sys
import json
import os
import ast
import ujson

os.environ['PATH'] = '/usr/local/opnsense/scripts/opncore/opncore_db.sh:' + os.environ.get('PATH', '')
os.environ['PATH'] = '/bin/bash:' + os.environ.get('PATH', '')
os.environ['PATH'] = '/root/mongo/build/install/bin/:' + os.environ.get('PATH', '')
os.environ['PATH'] = '/root/mongo/build/install/bin/mongod:' + os.environ.get('PATH', '')
os.environ['PWD'] = '/usr/local/opnsense/scripts/opncore:' + os.environ.get('PWD', '')

if len(sys.argv) > 0:
    script_path = '/usr/local/opnsense/scripts/opncore/opncore_db.sh'
    x = sys.argv[1]
    y = x.replace('[', "")
    t = y.replace(']', '')

    json_data = json.loads(t)
    #json_data = json.loads(json_data2)
    # print(type(json_data))
    imsi = []
    num_profiles = 0
    ki = []
    opc = []
    ip = []
    arp_priority = []
    dl = []
    unit = ['2']  # 2 - Mbps
    ul = []
    arp_capability = []
    arp_vulnerability = []
    qos = []
    apn = []
    sst = []
    apn_dict = {}
    my_list = []
    new_slice = False
    result = "Failed"


    def append_index(append_key, var_value, var_index):
        result = append_key + var_index

        if result not in apn_dict:
            apn_dict[result] = []
        apn_dict[result].append(var_value)


    def otherAPNS(var_apn, var_index):
        global new_slice
        for var_key, var_value in var_apn.items():
            if var_key == "sst":
                append_index(var_key, var_value, var_index)
                if var_value != sst[0]:
                    new_slice = True
            if var_key == "apn":
                append_index(var_key, var_value, var_index)
            if var_key == "dl":
                append_index(var_key, var_value, var_index)
            if var_key == "ul":
                append_index(var_key, var_value, var_index)
            if var_key == "QoS":
                append_index(var_key, var_value, var_index)
            if var_key == "arp_priority":
                append_index(var_key, var_value, var_index)
            if var_key == "arp_capability":
                append_index(var_key, var_value, var_index)
            if var_key == "arp_vulnerability":
                append_index(var_key, var_value, var_index)

        if new_slice:
            # Add slice to existing UE
            subprocess.check_output(
                [script_path] + ['update_slice'] + imsi + apn_dict['apn' + var_index] + apn_dict['sst' + var_index] +
                apn_dict['dl' + var_index] + unit + apn_dict['ul' + var_index]
                + apn_dict['QoS' + var_index] + apn_dict['arp_priority' + var_index] + apn_dict[
                    'arp_capability' + var_index] + apn_dict['arp_vulnerability' + var_index],
                text=True, stderr=subprocess.STDOUT)
        else:
            # add an apn to already existent UE
            subprocess.check_output(
                [script_path] + ['update_apn'] + imsi + apn_dict['apn' + var_index] + apn_dict['sst' + var_index] +
                apn_dict['dl' + var_index] + unit + apn_dict['ul' + var_index]
                + apn_dict['QoS' + var_index] + apn_dict['arp_priority' + var_index] + apn_dict[
                    'arp_capability' + var_index] + apn_dict['arp_vulnerability' + var_index],
                text=True, stderr=subprocess.STDOUT)


    if isinstance(json_data, dict):
        try:
            num_profiles = json_data['count']
            firstAPN = json_data['1']
            for key, value in firstAPN.items():
                if key == "imsi":
                    imsi.append(str(value))
                if key == "ki":
                    ki.append(str(value))
                if key == "opc":
                    opc.append(str(value))
                if key == "sst":
                    sst.append(str(value))
                if key == "apn":
                    if value != "":
                        apn.append(str(value))
                if key == "ip":
                    if value != "":
                        ip.append(str(value))
                if key == "dl":
                    if value != " ":
                        dl.append(str(value))
                if key == "unit":
                    if value != "":
                        unit.append(str(value))
                if key == "ul":
                    if value != "":
                        ul.append(str(value))
                if key == "QoS":
                    if value != "":
                        qos.append(str(value))
                if key == "arp_priority":
                    if value != "":
                        arp_priority.append(str(value))
                if key == "arp_capability":
                    if value != "":
                        arp_capability.append(str(value))
                if key == "arp_vulnerability":
                    if value != "":
                        arp_vulnerability.append(str(value))

            if len(ip) > 0:

                output = subprocess.check_output([script_path] + ['add'] + imsi + ki + opc + sst + apn + dl + unit + ul
                                                 + qos + arp_priority + arp_capability + arp_vulnerability + ip,
                                                 text=True, stderr=subprocess.STDOUT)
            else:

                output = subprocess.check_output([script_path] + ['add'] + imsi + ki + opc + sst + apn + dl + unit + ul
                                                 + qos + arp_priority + arp_capability + arp_vulnerability,
                                                 text=True, stderr=subprocess.STDOUT)

            # After creating the UE, then add the other apns, (if they exist)
            for i in range(2, num_profiles + 1):
                for key, value in json_data.items():
                    if key == str(i):
                        otherAPNS(value, str(i))

            output_list = output.strip().split('\n')
            # print(output_list[0])
            if len(output_list) > 1:
                if output_list[-2] == "Success":
                    result = "Success"
            else:
                if output_list[0] == "Duplicate":
                    result = "Duplicate"
        except:
            pass
    print(ujson.dumps(result))