#!/bin/sh

user=root
group=wheel

mkdir -p /var/run/epc
chown -R $user:$group /var/run/epc
chmod 777 /var/run/epc

# logfile
mkdir -p /var/log/opncell
#ln -s /usr/ports/open5gs/install/var/log/open5gs/hss.log  /var/log/opncore/hss.log
chown -R $user:$group /var/log/opncell/hss.log
chmod +r /var/log/opncell/hss.log
