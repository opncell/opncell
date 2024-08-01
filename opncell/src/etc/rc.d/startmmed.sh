#!/bin/sh

command="$1"
PIDFILE="$2"
service_name="$3"
config_file="$4"
log_file="$5"
"${command}" -c "${config_file}" -l "${log_file}" -D > /dev/null 2>&1
pgrep open5gs-"${service_name}" > "${PIDFILE}"

#ps aux | grep ${command}  | awk '$8 == "Is" || $8 == "Ss" || $8 == "Rs" {print $2}' > ${PIDFILE}
