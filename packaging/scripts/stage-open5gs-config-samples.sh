#!/bin/sh
# Stage configuration samples and print the corresponding FreeBSD plist entries.
set -eu

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 GENERATED_CONFIG_DIR STAGED_PREFIX" >&2
    exit 64
fi

source_dir=$1
stage_prefix=$2
open5gs="amf ausf bsf hss mme nrf nssf pcf pcrf scp sgwc sgwu smf udm udr upf"
diameter="hss mme pcrf smf"

for daemon in $open5gs; do
    test -s "$source_dir/open5gs/$daemon.yaml"
done
for daemon in $diameter; do
    test -s "$source_dir/freeDiameter/$daemon.conf"
done

install -d "$stage_prefix/etc/open5gs" "$stage_prefix/etc/freeDiameter"
for daemon in $open5gs; do
    destination="$stage_prefix/etc/open5gs/$daemon.yaml.sample"
    install -m 0644 "$source_dir/open5gs/$daemon.yaml" "$destination"
    case "$daemon" in
        hss|pcrf|pcf|udr)
            sed -i '' 's|^db_uri: mongodb://localhost/open5gs$|db_uri: mongodb://127.0.0.1:27017/open5gs|' "$destination"
            ;;
        udm)
            # Drop the generated example Hnet list while retaining the UDM settings.
            awk '/^  hnet:/{print "  hnet: []"; skip=1; next} /^  [[:alnum:]_]+:/{skip=0} skip == 0' \
                "$source_dir/open5gs/udm.yaml" > "$destination"
            ;;
    esac
    printf '@sample etc/open5gs/%s.yaml.sample\n' "$daemon"
done

for daemon in $diameter; do
    install -m 0644 "$source_dir/freeDiameter/$daemon.conf" "$stage_prefix/etc/freeDiameter/$daemon.conf.sample"
    printf '@sample etc/freeDiameter/%s.conf.sample\n' "$daemon"
done
