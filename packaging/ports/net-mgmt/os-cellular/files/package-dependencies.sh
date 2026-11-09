#!/bin/sh
# Declare the validated minimums, independent of the build host CPU variant.
# CPU selection and binary checks are handled by install-cellular.py.
cat <<'DEPS'
"bash": {origin: "shells/bash", version: "5.3.15"}
"open5gs": {origin: "net/opncell-open5gs", version: "2.8.0_1"}
"python312": {origin: "lang/python312", version: "3.12.13_3"}
"py312-pyyaml": {origin: "devel/py-pyyaml", version: "6.0.3"}
"py312-ujson": {origin: "devel/py-ujson", version: "6.0.0"}
"opncell-mongosh": {origin: "databases/opncell-mongosh", version: "2.14.0"}
"mongodb80": {origin: "databases/mongodb80", version: "8.0.34_1"}
"opncell-pymongo": {origin: "databases/opncell-pymongo", version: "4.18.2"}
DEPS
