#!/bin/sh

user=root
group=wheel

mkdir -p /var/run/epc
chown -R $user:$group /var/run/epc
chmod 777 /var/run/epc

# logfile
mkdir -p /var/log/opncell
touch /var/log/opncell/pcf.log
#ln -s /usr/ports/open5gs/install/var/log/open5gs/pcf.log  /var/log/opncore/pcf.log
chown -R $user:$group /var/log/opncell/pcf.log
chmod +r /var/log/opncell/pcf.log
