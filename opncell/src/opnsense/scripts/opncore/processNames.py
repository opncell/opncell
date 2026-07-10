#!/usr/local/bin/python3

import yaml
import subprocess
import ujson
import sys
import json

def main():
    network = ""

    if len(sys.argv) > 1:
        try:
            raw_arg = sys.argv[1]
            # Clean and parse JSON
            data = json.loads(raw_arg.strip())

            if isinstance(data, list):
                data = data[0]  # take first item if array

            if isinstance(data, dict):
                network = str(data.get("network", ""))
        except Exception as e:
            print(f"Error parsing argument: {e}", file=sys.stderr)
            network = ""

    process_names = []
    running_processes_names = []

    fourGServices = ["hss", "mme", "pcrf", "sgwu", "sgwc", "smf", "upf", "nrf", "scp"]
    upfServices = ["amf", "udm", "nssf", "smf", "udr", "pcf", "upf", "ausf"]
    fiveGSAServices = ["nrf", "scp", "amf", "smf", "upf", "ausf", "udm", "udr", "pcf", "nssf", "bsf"]
    fiveNSAGServices = ["hss", "mme", "pcrf", "sgwu", "sgwc", "smf", "upf"]

    target_keys = ['metrics', 'dns', 'tai', 'network_name', 'nsi', 's1ap', 'ngap']

    def extract_nested_key_value(data, target_keys, current_key=''):
        extracted = {}
        for key, value in data.items():
            new_key = f'{current_key}.{key}' if current_key else key
            if isinstance(value, dict):
                extracted.update(extract_nested_key_value(value, target_keys, new_key))
            elif isinstance(value, list):
                extracted[new_key] = value
            elif key in target_keys:
                extracted[new_key] = value
        return extracted

    # Get running processes
    try:
        output = subprocess.check_output(
            "ps aux | grep open5gs | awk '$8 ~ /^[IRS]/ {print $2}'",
            shell=True, text=True
        )
        pids = [p.strip() for p in output.strip().split("\n") if p.strip()]

        for pid in pids:
            try:
                name = subprocess.check_output(f"ps -p {pid} -o comm=", shell=True, text=True).strip()
                name = name.replace("open5gs-", "").rstrip("d")

                yaml_path = f'/usr/local/etc/open5gs/{name}.yaml'
                with open(yaml_path, 'r') as f:
                    yaml_data = yaml.safe_load(f)

                config = extract_nested_key_value(yaml_data, target_keys)
                process_names.append({"PID": pid, "Name": name, "config": config})
                running_processes_names.append(name)
            except:
                pass
    except:
        pass

    # MongoDB
    try:
        mongo_pid = subprocess.check_output(
            "ps aux | grep mongod | grep -v grep | awk '{print $2}' | head -n 1",
            shell=True, text=True
        ).strip()
        if mongo_pid:
            process_names.append({"PID": mongo_pid, "Name": "mongo", "config": {"mongod.bind": [{"address": "127.0.0.1"}]}})
        else:
            raise Exception
    except:
        process_names.append({"PID": "Stopped", "Name": "mongo", "config": {"mongod.bind": [{"address": "127.0.0.1"}]}})

    # Add not running processes
    try:
        if network == "enablefour":
            not_running = list(set(fourGServices) - set(running_processes_names))
        elif network == "enablefiveSA":
            not_running = list(set(fiveGSAServices) - set(running_processes_names))
        elif network == "enableupf":
            not_running = list(set(upfServices) - set(running_processes_names))
        elif network == "enablefiveNSA":
            not_running = list(set(fiveNSAGServices) - set(running_processes_names))
        else:
            not_running = []

        for process in not_running:
            process_names.append({"PID": "Stopped", "Name": process})
    except:
        pass

    print(ujson.dumps(process_names))

if __name__ == "__main__":
    main()