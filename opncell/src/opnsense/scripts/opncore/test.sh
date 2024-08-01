#!/bin/sh

version=0.10.3

display_help() {
    echo "open5gs-dbctl: Open5GS Database Configuration Tool ($version)"
    echo "FLAGS: --db_uri=mongodb://localhost"
    echo "COMMANDS:" >&2
    echo "   add {imsi key opc}: adds a user to the database with default values"
    echo "   add {imsi ip key opc}: adds a user to the database with default values and a IPv4 address for the UE"
    echo "   addT1 {imsi key opc}: adds a user to the database with 3 differents apns"
    echo "   addT1 {imsi ip key opc}: adds a user to the database with 3 differents apns and the same IPv4 address for the each apn"
    echo "   remove {imsi}: removes a user from the database"
    echo "   reset: WIPES OUT the database and restores it to an empty default"
    echo "   static_ip {imsi ip4}: adds a static IP assignment to an already-existing user"
    echo "   static_ip6 {imsi ip6}: adds a static IPv6 assignment to an already-existing user"
    echo "   type {imsi type}: changes the PDN-Type of the first PDN: 1 = IPv4, 2 = IPv6, 3 = IPv4v6"
    echo "   help: displays this message and exits"
    echo "   default values are as follows: APN \"internet\", dl_bw/ul_bw 1 Gbps, PGW address is 127.0.0.3, IPv4 only"
    echo "   add_ue_with_apn {imsi key opc apn}: adds a user to the database with a specific apn,"
    echo "   add_ue_with_slice {imsi key opc apn sst sd}: adds a user to the database with a specific apn, sst and sd"
    echo "   update_apn {imsi apn slice_num}: adds an APN to the slice number slice_num of an existent UE"
    echo "   update_slice {imsi apn sst sd}: adds an slice to an existent UE"
    echo "   showall: shows the list of subscriber in the db"
    echo "   showpretty: shows the list of subscriber in the db in a pretty json tree format"
    echo "   showfiltered: shows {imsi key opc apn ip} information of subscriber"
    echo "   ambr_speed {imsi dl_value dl_unit ul_value ul_unit}: Change AMBR speed from a specific user and the  unit values are \"[0=bps 1=Kbps 2=Mbps 3=Gbps 4=Tbps ]\""
    echo "   subscriber_status {imsi subscriber_status_val={0,1} operator_determined_barring={0..8}}: Change TS 29.272 values for Subscriber-Status (7.3.29) and Operator-Determined-Barring (7.3.30)"

}

while test $# -gt 0; do
  case "$1" in
    --db_uri*)
      DB_URI=`echo $1 | sed -e 's/^[^=]*=//g'`
      shift
      ;;
    *)
      break
      ;;
  esac
done

DB_URI="${DB_URI:-mongodb://localhost/open5gs}"

# Function to create the documents array for insertMany
createDocumentsArray() {
    json_array="$1"
    documents="["

    json_array=$(echo "$json_array" | sed 's/},{/}|{/g' | tr -d '\n' | sed 's/^\[//;s/\]$//')

    for entry in $(echo "$json_array" | tr '|' ' '); do
        imsi=$(echo "$entry" | grep -o '"imsi":"[^"]*' | cut -d'"' -f4)
        ki=$(echo "$entry" | grep -o '"ki":"[^"]*' | cut -d'"' -f4)
        opc=$(echo "$entry" | grep -o '"opc":"[^"]*' | cut -d'"' -f4)

        document="{
            \"_id\": new ObjectId(),
            \"schema_version\": NumberInt(1),
            \"imsi\": \"$imsi\",
            \"msisdn\": [],
            \"imeisv\": [],
            \"mme_host\": [],
            \"mm_realm\": [],
            \"purge_flag\": [],
            \"slice\":[
            {
                \"sst\": NumberInt(1),
                \"default_indicator\": true,
                \"session\": [],
                \"_id\": new ObjectId()
            }],
            \"security\": {
                \"k\": \"$ki\",
                \"op\": null,
                \"opc\": \"$opc\",
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
        }"

        # Add document to documents array
        documents="$documents$document,"
    done

    # Remove the trailing comma and close the array
    documents="${documents%,}]"
    echo "$documents"
}

# Check if the number of arguments is correct
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <db_uri> <json_array>"
    exit 1
fi

JSON_ARRAY=$1

# Create documents array for insertMany
DOCUMENTS=$(createDocumentsArray "$JSON_ARRAY")

# Execute the MongoDB insertMany command
mongo --eval "db.subscribers.insertMany($DOCUMENTS);" "$DB_URI"

exit $?


[{"imsi": "1.01E+12","ki": "D0273E35B38BDC0F1E47506EC2E8D88A","opc": "63A7F15BE32870C591C19E74916FFFCE"},{"imsi": "1.01E+12","ki": "52453687F381742335AA1D60BFAD3EF8","opc": "7F693264C6F0CC1460FE5C3AD818D4EB"
    },
    {
        "imsi": "1.01E+12",
        "ki": "0FE7965F9741BE8DE5FBC16488AF22C4",
        "opc": "B6ED29A4C49FC2846BB405E33BAA0664"
    },
    {
        "imsi": "1.01E+12",
        "ki": "B30A3C5C8BC86DB1DF438C31257EC23F",
        "opc": "B7B9024D2EB0384028597A1374911B79"
    },
    {
        "imsi": "1.01E+12",
        "ki": "557D8F9D020F353DE98B33CA96DCEF2D",
        "opc": "7A1FF1DE68B5D02FB7573E09E005BF5D"
    },
    {
        "imsi": "1.01E+12",
        "ki": "BC53D50A735472D6964EEC7611E3881C",
        "opc": "CDB526DA5FE37AFB3DDDBE54EB3B58EA"
    },
    {
        "imsi": "1.01E+12",
        "ki": "719F98B84995FE205610F4560CBEAA92",
        "opc": "DEC24DA8D95F64EF6E1E5AB2C4EBF5AD"
    },
    {
        "imsi": "1.01E+12",
        "ki": "0A8C2F76FACCDE7BA04791B8EA95406A",
        "opc": "A57B714853E6DA5F9174805DB7373BBB"
    },
    {
        "imsi": "1.01E+12",
        "ki": "BA33303BC72F0E17A9296FE43BD834F1",
        "opc": "5627AAB85A584CEEE6D1905A39E5D6AB"
    },
    {
        "imsi": "1.01E+12",
        "ki": "9A918F31AEC3ADF704300CE35DC5AE17",
        "opc": "381A540B4976C1523CAF80A01415C283"
    },
    {
        "imsi": "1.01E+12",
        "ki": "D74E222EC182B3D5B6002DF692C06028",
        "opc": "AE2A865836BFB713B4C81BD3516BA29B"
    },
    {
        "imsi": "1.01E+12",
        "ki": "BD5245AA0615CDEF98A3DC7F71385BE3",
        "opc": "E411DB66095B1446C2F0E48BEE0A7603"
    },
    {
        "imsi": "1.01E+12",
        "ki": "02B88F713729FB3026B1619625F48A6F",
        "opc": "26EE891916D533957A246AB33B5B7951"
    },
    {
        "imsi": "1010000000113",
        "ki": "EFF68F3CE01349570FE6C3ABF730D1B0",
        "opc": "C453C7386171A6C9932D7C8E5D990AFE"
    },
    {
        "imsi": "1.01E+12",
        "ki": "B58EC473759DDA42EA06126E515D0FC2",
        "opc": "6E2EF4E4F1AEFB27579A22E4FEE5A562"
    },
    {
        "imsi": "1010000000115",
        "ki": "AC6CA464EB2A7F67D2224877CAD7FEF8",
        "opc": "A2D1E48D71A75E5B452CC4F5768B6CF3"
    },
    {
        "imsi": "1010000000116",
        "ki": "09AE9DB894E035ED85A05CF06D02164E",
        "opc": "E00CA1C4F5CAEB77B29B89B1943001D9"
    },
    {
        "imsi": "1010000000117",
        "ki": "8244A683FF913557AC9824AF87B5F829",
        "opc": "124771B04A39763E56A44F11D1E62887"
    },
    {
        "imsi": "1010000000118",
        "ki": "D7346C384CE5D1716BA66EDE7EE73F11",
        "opc": "EF876AE901013D284E99B88C4612A945"
    },
    {
        "imsi": "1.01E+12",
        "ki": "847176D340E00E38225BC07FE58F563D",
        "opc": "1493617E13F105BE01C03B85F56F7FA3"
    }
]