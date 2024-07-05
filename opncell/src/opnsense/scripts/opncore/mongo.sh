#!/bin/sh

DB_URI="mongodb://your_db_uri_here"

# Function to create APN sessions
create_apn_sessions() {
    apn_names=$1
    sst_values=$2
    dl_values=$3
    ul_values=$4
    qos_indices=$5
    arp_priorities=$6
    arp_capabilities=$7
    arp_vulnerabilities=$8

    sessions="["

    i=0
    while [ $i -lt ${#apn_names[@]} ]; do
        if [ $i -gt 0 ]; then
            sessions+=","
        fi
        sessions+="{
            \"name\": \"${apn_names[$i]}\",
            \"type\": NumberInt(3),
            \"qos\": {
                \"index\": NumberInt(${qos_indices[$i]}),
                \"arp\": {
                    \"priority_level\": NumberInt(${arp_priorities[$i]}),
                    \"pre_emption_capability\": NumberInt(${arp_capabilities[$i]}),
                    \"pre_emption_vulnerability\": NumberInt(${arp_vulnerabilities[$i]})
                }
            },
            \"ambr\": {
                \"downlink\": {
                    \"value\": NumberInt(${dl_values[$i]}),
                    \"unit\": NumberInt(0)
                },
                \"uplink\": {
                    \"value\": NumberInt(${ul_values[$i]}),
                    \"unit\": NumberInt(0)
                }
            },
            \"pcc_rule\": [],
            \"_id\": new ObjectId()
        }"
        i=$((i + 1))
    done

    sessions+="]"
    echo "$sessions"
}

if [ "$1" = "add" ]; then
    if [ "$#" -ge 4 ]; then
        IMSI=$2
        KI=$3
        OPC=$4

        shift 4

        apn_names=()
        sst_values=()
        dl_values=()
        ul_values=()
        qos_indices=()
        arp_priorities=()
        arp_capabilities=()
        arp_vulnerabilities=()

        while [ "$#" -gt 0 ]; do
            apn_names+=("$1")
            sst_values+=("$2")
            dl_values+=("$3")
            ul_values+=("$4")
            qos_indices+=("$5")
            arp_priorities+=("$6")
            arp_capabilities+=("$7")
            arp_vulnerabilities+=("$8")

            shift 8
        done

        sessions=$(create_apn_sessions apn_names sst_values dl_values ul_values qos_indices arp_priorities arp_capabilities arp_vulnerabilities)

        mongo --eval "db.subscribers.insertOne(
            {
                \"_id\": new ObjectId(),
                \"schema_version\": NumberInt(1),
                \"imsi\": \"$IMSI\",
                \"msisdn\": [],
                \"imeisv\": [],
                \"mme_host\": [],
                \"mm_realm\": [],
                \"purge_flag\": [],
                \"slice\":[
                {
                    \"sst\": NumberInt(1),
                    \"default_indicator\": true,
                    \"session\": $sessions,
                    \"_id\": new ObjectId()
                }],
                \"security\":
                {
                    \"k\" : \"$KI\",
                    \"op\" : null,
                    \"opc\" : \"$OPC\",
                    \"amf\" : \"8000\"
                },
                \"ambr\" :
                {
                    \"downlink\" : { \"value\": NumberInt(1000000000), \"unit\": NumberInt(0)},
                    \"uplink\" : { \"value\": NumberInt(1000000000), \"unit\": NumberInt(0)}
                },
                \"access_restriction_data\": 32,
                \"network_access_mode\": 0,
                \"subscriber_status\": 0,
                \"operator_determined_barring\": 0,
                \"subscribed_rau_tau_timer\": 12,
                \"__v\": 0
            }
        );" $DB_URI
        exit $?
    fi
fi