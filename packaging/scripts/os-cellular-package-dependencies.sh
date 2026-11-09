#!/bin/sh
# Resolve the files-only plugin's runtime manifest from installed and verified packages.
set -eu

mongosh_package=/usr/local/poudriere/data/packages/15_1_amd64-fbsd15/All/opncell-mongosh-2.14.0.pkg
mongo_package=/usr/local/poudriere/data/packages/15_1_amd64-fbsd15/All/mongodb80-8.0.34_3.pkg
pymongo_package=/usr/home/codex/opncell-release/26.7.2_8/packages/All/opncell-pymongo-4.18.2.pkg
format='"%n": {origin: "%o", version: "%v"}'

test -r "$mongosh_package"
test -r "$mongo_package"
test -r "$pymongo_package"
test "$(pkg query -F "$mongosh_package" '%n-%v %o')" =     'opncell-mongosh-2.14.0 databases/opncell-mongosh'
test "$(pkg query -F "$mongo_package" '%n-%v %o')" =     'mongodb80-8.0.34_3 databases/mongodb80'
pkg info -e 'open5gs>=2.8.0_1'
pkg info -e 'python312>=3.12'
for package in bash open5gs python312 py312-pyyaml py312-ujson; do
    pkg query "$format" "$package"
done
pkg query -F "$mongosh_package" "$format"
pkg query -F "$mongo_package" "$format"
pkg query -F "$pymongo_package" "$format"
