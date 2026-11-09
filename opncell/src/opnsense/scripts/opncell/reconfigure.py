#!/usr/local/bin/python3

import yaml
import sys
import json
import base64

from atomic_yaml import replace_yaml

if len(sys.argv) > 1:

    try:
        decoded = base64.b64decode(sys.argv[1]).decode()
        #print(decoded)
        json_data = json.loads(decoded)
    except Exception as e:
        print(f"Error decoding input: {e}", file=sys.stderr)
        sys.exit(1)

    if "general" in json_data and isinstance(json_data["general"], dict):
        new_addr = ''
        sgwu_addr = json_data["general"].get("sgwu_gtpu")
        upf_addr = json_data["general"].get("upf_gtpu")
        sst = int(json_data["general"].get("sst", 1))
        if not 1 <= sst <= 255:
            sys.exit("SST must be between 1 and 255")
        new_mcc = ''
        for key, value in json_data["general"].items():
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


    def config(process_name):
        yaml_path = '/usr/local/etc/open5gs/'
        yaml_file = yaml_path + process_name + '.yaml'
        # Read the YAML file
        with open(yaml_file, 'r') as file:
            yaml_data = yaml.safe_load(file)

        # Replace values in the configuration--It's faster to access individual elements than loop through
        # the whole file
        if process_name == 'sgwu':
            yaml_data['sgwu']['gtpu']['server'][0]['address'] = (sgwu_addr or new_addr).strip("'")
            yaml_data['global']['max']['ue'] = ue
            yaml_data['global']['max']['peer'] = peer
            yaml_data['logger']['file']['level'] = "debug"

        if process_name == 'upf':
            gtpu = yaml_data['upf']['gtpu']['server'][0]
            if network in ('enablefour', 'enablefiveNSA'):
                # SGW-U owns the radio-facing GTP-U socket in EPC mode.
                if gtpu.get('address') == (sgwu_addr or new_addr).strip("'"):
                    gtpu['address'] = '127.0.0.7'
                return yaml_file, yaml_data
            if upf_addr:
                gtpu['address'] = upf_addr.strip("'")
            yaml_data['global']['max']['ue'] = ue
            yaml_data['global']['max']['peer'] = peer
            yaml_data['logger']['file']['level'] = "debug"

        if process_name == 'nrf':
            yaml_data['nrf']['serving'][0]['plmn_id']['mcc'] = new_mcc
            yaml_data['nrf']['serving'][0]['plmn_id']['mnc'] = new_mnc
            yaml_data['global']['max']['ue'] = ue
            yaml_data['global']['max']['peer'] = peer
            yaml_data['logger']['file']['level'] = "debug"

        if process_name == 'nssf':
            yaml_data['nssf']['sbi']['client']['nsi'][0]['s_nssai']['sst'] = sst

        if process_name == 'amf':
            yaml_data['amf']['ngap']['server'][0]['address'] = new_addr.strip("'")
            yaml_data['amf']['guami'][0]['plmn_id']['mcc'] = new_mcc
            yaml_data['amf']['guami'][0]['plmn_id']['mnc'] = new_mnc
            yaml_data['amf']['tai'][0]['plmn_id']['mcc'] = new_mcc
            yaml_data['amf']['tai'][0]['plmn_id']['mnc'] = new_mnc
            yaml_data['amf']['plmn_support'][0]['plmn_id']['mcc'] = new_mcc
            yaml_data['amf']['plmn_support'][0]['plmn_id']['mnc'] = new_mnc
            yaml_data['amf']['plmn_support'][0]['s_nssai'][0]['sst'] = sst
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

        return yaml_file, yaml_data

    services = {
        'enablefour': ('mme', 'sgwu', 'upf'),
        'enablefiveNSA': ('mme', 'sgwu', 'upf'),
        'enablefiveSA': ('amf', 'upf', 'nrf', 'nssf'),
        'enableupf': ('upf',),
    }
    configurations = [config(process_name) for process_name in services[network]]
    for yaml_file, yaml_data in configurations:
        replace_yaml(yaml_file, yaml_data)
    print(json.dumps({"result": "rendered"}))

else:
    print("No arguments passed")
