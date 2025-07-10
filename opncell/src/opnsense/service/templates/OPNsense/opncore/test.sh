#!/bin/bash

TARGET="$1"
PASSWORD="opnsense"

#scripts
cp -r  -q  /usr/local/opnsense/scripts/ > /dev/null 2>&1

#Controllers
cp -r  -q  /usr/local/opnsense/mvc/app/controllers/OPNsense/OPNCell /usr/plugins/devel/opncore/src/opnsense/mvc/app/controllers/OPNsense/ > /dev/null 2>&1

#models
cp -r  -q  /usr/local/opnsense/mvc/app/models/OPNsense/ > /dev/null 2>&1

#views
cp -r  -q  /usr/local/opnsense/mvc/app/views/OPNsense/ > /dev/null 2>&1

#Conf
cp -r  -q  /usr/local/opnsense/service/conf/actions.d > /dev/null 2>&1

#rc scripts
cp -r  -q  /usr/local/etc/rc.d > /dev/null 2>&1

#Logformats
cp -r  -q  /usr/local/opnsense/scripts/syslog/logformats > /dev/null 2>&1

#Templates
cp -r  -q  /usr/local/opnsense/service/templates/OPNsense/ > /dev/null 2>&1