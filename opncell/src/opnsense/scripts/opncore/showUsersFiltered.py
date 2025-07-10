#!/usr/local/bin/python3

"""
    Copyright (c) 2015-2021 Ad Schellevis <ad@opnsense.org>
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.

    THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES,
    INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
    AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
    AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
    OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
    SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
    INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
    CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
    ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
    POSSIBILITY OF SUCH DAMAGE.

    --------------------------------------------------------------------------------------
    list pf states
"""
import ujson
import argparse

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
#        print(ujson.dumps(user_details))

    except subprocess.CalledProcessError as e:
        #print(f"Error running the Bash script: {e}")
        #print(f"Command output: {e.output}")
        pass

    return user_details

if __name__ == '__main__':


    # parse input arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('--sort_by', help='sort by (field asc|desc)', default='')
    inputargs = parser.parse_args()


    result = {
        'details': fetch_users()
    }
    # result = {
    #     'details': query_states(rule_label=inputargs.label, filter_str=inputargs.filter)
    # }
    # sort results
    if inputargs.sort_by.strip() != '':
        sort_key = inputargs.sort_by.split()[0]
        sort_desc = inputargs.sort_by.split()[-1] == 'desc'
        result['details'] = sorted(
            result['details'],
            key=lambda k: str(k[sort_key]).lower() if sort_key in k else '',
            reverse=sort_desc
        )

    result['total_entries'] = len(result['details'])
    # apply offset and limit
    # if inputargs.offset.isdigit():
    #     result['details'] = result['details'][int(inputargs.offset):]
    # if inputargs.limit.isdigit() and len(result['details']) >= int(inputargs.limit):
    #     result['details'] = result['details'][:int(inputargs.limit)]

    result['total'] = len(result['details'])

    print(ujson.dumps(result['details']))
