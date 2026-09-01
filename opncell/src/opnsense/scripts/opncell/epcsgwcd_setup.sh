#!/bin/sh

user=root
group=wheel

mkdir -p /var/run/epc
chown -R $user:$group /var/run/epc
chmod 777 /var/run/epc

# logfile
mkdir -p /var/log/opncell
touch /var/log/opncell/sgwc.log
#ln -s /usr/ports/open5gs/install/var/log/open5gs/sgwc.log  /var/log/opncore/sgwc.log
chown -R $user:$group /var/log/opncell/sgwc.log
chmod +r /var/log/opncell/sgwc.log
