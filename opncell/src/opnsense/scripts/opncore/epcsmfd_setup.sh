#!/bin/sh

user=root
group=wheel

mkdir -p /var/run/epc
chown -R $user:$group /var/run/epc
chmod 777 /var/run/epc

# logfile
mkdir -p /var/log/opncore
ln -s /usr/ports/open5gs/install/var/log/open5gs/smf.log  /var/log/opncore/smf.log
chown -R $user:$group /var/log/opncore/smf.log
chmod +r /var/log/opncore/smf.log
