#!/bin/sh

user=root
group=wheel

mkdir -p /var/run/epc
chown -R $user:$group /var/run/epc
chmod 777 /var/run/epc

# logfile
mkdir -p /var/log/opncell
touch /var/log/opncell/amf.log

chown -R $user:$group /var/log/opncell/amf.log
chmod +r /var/log/opncell/amf.log
