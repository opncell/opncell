#!/bin/sh

user=epc
group=epc

mkdir -p /var/run/epc
chown $user:$group /var/run/epc
chmod 750 /var/run/epc

mkdir -p /usr/local/etc/epc
chown $user:$group /usr/local/etc/epc
chmod 750 /usr/local/etc/epc

# ensure that epccore can read the configuration files
chown -R $user:$group /usr/local/etc/epc
chown -R $user:$group /var/run/epc

# logfile (if used)
#touch /var/log/epc.log
#chown $user:$group /var/log/epc.log

# register Security Associations
/usr/local/opnsense/scripts/frr/register_sas
