#!/bin/sh

user=root
group=wheel

mkdir -p /var/run/epc
chown -R $user:$group /var/run/epc
chmod 777 /var/run/epc

# logfile (if used)
mkdir -p /var/log/opncore
cp -r /usr/ports/open5gs/install/var/log/open5gs/.  /var/log/opncore/
chown -R $user:$group /var/log/opncore
