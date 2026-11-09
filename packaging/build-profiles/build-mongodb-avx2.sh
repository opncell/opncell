#!/bin/sh
# Run as root on opncell-repo. Defaults to a dry run; --build starts compilation.
set -eu
[ "$(id -u)" -eq 0 ] || { echo 'Run this launcher as root on opncell-repo.' >&2; exit 1; }
case "${1:-}" in
    '') mode=-n ;;
    --build) mode= ;;
    *) echo 'Usage: build-mongodb-avx2.sh [--build]' >&2; exit 1 ;;
esac
base=/usr/home/codex/opncell-release/migration-lab
old=/usr/local/poudriere/data/packages/15_1_amd64-fbsd15
new=/usr/local/poudriere/data/packages/15_1_amd64-fbsd15-avx2
# A dedicated set keeps AVX packages out of the portable build output.
if ! poudriere ports -l | awk '$1 == "mongo8034avx2" { found=1 } END { exit !found }'; then
    poudriere ports -c -p mongo8034avx2 -m null -M "$base/avx2-overlay"
fi
install -d "$new/All" "$new/Latest"
# Reuse the committed dependency cache. Hard links save disk space.
if [ ! -e "$new/.opncell-seeded" ]; then
    cp -ln "$old"/All/*.pkg "$new/All/"
    [ -e "$new/All/pkg-2.9.0.pkg" ]
    ln -sf ../All/pkg-2.9.0.pkg "$new/Latest/pkg.pkg"
    touch "$new/.opncell-seeded"
fi
conf=/usr/local/etc/poudriere.d/15_1_amd64-fbsd15-avx2-make.conf
if [ ! -e "$conf" ]; then
    printf '%s\n' 'MAKE_JOBS_NUMBER=2' > "$conf"
fi
# Unquoted mode is intentionally either the single -n flag or empty.
poudriere bulk $mode -b latest -J 1 -z avx2 -j 15_1_amd64 -p fbsd15 -O mongo8034avx2 databases/mongodb80
