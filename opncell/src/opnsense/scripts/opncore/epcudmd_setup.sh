#!/bin/sh

user=root
group=wheel

mkdir -p /var/run/epc
chown -R $user:$group /var/run/epc
chmod 777 /var/run/epc

# logfile
mkdir -p /var/log/opncore
ln -s /usr/ports/open5gs/install/var/log/open5gs/udm.log  /var/log/opncore/udm.log
chown -R $user:$group /var/log/opncore/udm.log
chmod +r /var/log/opncore/udm.log
