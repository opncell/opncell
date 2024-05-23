#!/bin/sh

command="$1"
PIDFILE="$2"

"${command}" -D > /dev/null 2>&1

ps aux | grep ${command}  | awk '$8 == "Is" || $8 == "Ss" || $8 == "Rs" {print $2}' > ${PIDFILE} 


