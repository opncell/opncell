#!/bin/sh
# Compatibility entry point; the port owns the validated shared minimums.
set -eu
exec /bin/sh "$(dirname "$0")/../ports/net-mgmt/os-cellular/files/package-dependencies.sh"
