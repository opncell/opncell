#!/bin/sh

user=root
group=wheel

mkdir -p /var/run/epc
chown -R $user:$group /var/run/epc
chmod 777 /var/run/epc

# logfile
mkdir -p /var/log/opncell
touch /var/log/opncell/mme.log
chown -R $user:$group /var/log/opncell/mme.log
chmod +r /var/log/opncell/mme.log
