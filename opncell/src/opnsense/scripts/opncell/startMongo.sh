#!/bin/sh
# All plugin start paths use the packaged rc service and its configured data path.
set -eu
umask 077
if [ "${1:-}" != "--locked" ]; then
    exec /usr/bin/lockf -t 15 /var/run/opncell-mongodb-start.lock "$0" --locked
fi
if /usr/sbin/service mongod onestatus >/dev/null 2>&1; then
    echo OK
    exit 0
fi
# Do not start a second instance against another data directory or kill its owner.
if /usr/bin/sockstat -4l -p 27017 | /usr/bin/awk 'NR > 1 { found = 1 } END { exit !found }'; then
    echo 'MongoDB port 27017 is already occupied; inspect the existing listener.' >&2
    exit 1
fi
/usr/sbin/service mongod onestart
/usr/sbin/service mongod onestatus >/dev/null
echo OK
