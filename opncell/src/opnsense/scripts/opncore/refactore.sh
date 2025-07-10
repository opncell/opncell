#!/bin/sh

#DB_URI="mongodb://your_db_uri_here"
DB_URI="${DB_URI:-mongodb://localhost/open5gs}"
mongo --quiet --eval 'db.subscribers.createIndex({"imsi": 1}, {unique: true})' $DB_URI > /dev/null 2>&1

# Function to create APN sessions
create_apn_sessions() {
    first=1

    while [ "$#" -gt 0 ]; do
        apn_name=$1
        sst_value=$2
        dl_value=$3
        ul_value=$4
        qos_index=$5
        arp_priority=$6
        arp_capability=$7
        arp_vulnerability=$8

        if [ "$first" -eq 0 ]; then
            echo ","
        fi

        echo "{\"name\": \"$apn_name\", \"type\": NumberInt(3), \"qos\": { \"index\": NumberInt($qos_index), \"arp\": { \"priority_level\": NumberInt($arp_priority), \"pre_emption_capability\": NumberInt($arp_capability), \"pre_emption_vulnerability\": NumberInt($arp_vulnerability) } }, \"ambr\": { \"downlink\": { \"value\": NumberInt($dl_value), \"unit\": NumberInt(0) }, \"uplink\": { \"value\": NumberInt($ul_value), \"unit\": NumberInt(0) } }, \"pcc_rule\": [], \"_id\": new ObjectId() }"

        first=0
        shift 8
    done
}

if [ "$1" = "add" ]; then
    if [ "$#" -ge 4 ]; then
        IMSI=$2
        KI=$3
        OPC=$4

        shift 4

        # Create a temporary file to hold the sessions array
        temp_file=$(mktemp)
        echo "[" > "$temp_file"
        create_apn_sessions "$@" >> "$temp_file"
        echo "]" >> "$temp_file"
        sessions=$(cat "$temp_file")
        rm "$temp_file"

       output=$(mongo --quiet --eval "
        var result;
        try {
             db.subscribers.insertOne({
                \"_id\": new ObjectId(),
                \"schema_version\": NumberInt(1),
                \"imsi\": \"$IMSI\",
                \"msisdn\": [],
                \"imeisv\": [],
                \"mme_host\": [],
                \"mm_realm\": [],
                \"purge_flag\": [],
                \"slice\": [{
                    \"sst\": NumberInt($sst_value),
                    \"default_indicator\": true,
                    \"session\": $sessions,
                    \"_id\": new ObjectId()
                }],
                \"security\": {
                    \"k\": \"$KI\",
                    \"op\": null,
                    \"opc\": \"$OPC\",
                    \"amf\": \"8000\"
                },
                \"ambr\": {
                    \"downlink\": { \"value\": NumberInt(1000000000), \"unit\": NumberInt(0) },
                    \"uplink\": { \"value\": NumberInt(1000000000), \"unit\": NumberInt(0) }
                },
                \"access_restriction_data\": 32,
                \"network_access_mode\": 0,
                \"subscriber_status\": 0,
                \"operator_determined_barring\": 0,
                \"subscribed_rau_tau_timer\": 12,
                \"__v\": 0
            });
            print('Success');
        } catch (e) {
            if (e.code === 11000) {
                print('Error: Duplicate IMSI');
            } else {
                print('Error: ' + e);
            }
            quit(1);
        }" $DB_URI 2>&1)
        
          echo "$output"

        exit $?
    fi
fi
