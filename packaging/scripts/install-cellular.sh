#!/bin/sh
# Public bootstrap: fetch the complete versioned installer and verify its digest.
set -eu
umask 077
[ "$(uname -s)" = FreeBSD ] || { echo 'This installer requires OPNsense on FreeBSD.' >&2; exit 1; }
command -v opnsense-version >/dev/null 2>&1 || { echo 'This installer requires an OPNsense appliance.' >&2; exit 1; }
case "$(freebsd-version -u)" in
    15.*) ;;
    *) echo 'Complete the supported OPNsense upgrade to FreeBSD 15 first. MongoDB 5 data must be exported before that OS upgrade.' >&2; exit 1;;
esac
[ "$(uname -m)" = amd64 ] || { echo 'This package release supports amd64 appliances.' >&2; exit 1; }
[ "$(id -u)" = 0 ] || { echo 'Run the installer as root.' >&2; exit 1; }
python=/usr/local/bin/python3.13
[ -x "$python" ] || { echo 'The OPNsense Python 3.13 interpreter is required.' >&2; exit 1; }
repo=${OPNCELL_REPOSITORY_URL:-http://repo.opncell.io/OPNcell-repo}
work=$(mktemp -d /tmp/opncell-install.XXXXXX)
trap 'rm -rf "$work"' EXIT HUP INT TERM
printf '%s\n' 'Preparing the OPNcell installer...'
fetch -qo "$work/installer.tar.gz" "$repo/installer.tar.gz"
fetch -qo "$work/installer.sha256" "$repo/installer.sha256"
expected=$(awk 'NR == 1 {print $1}' "$work/installer.sha256")
[ "${#expected}" = 64 ] || { echo 'Invalid installer checksum.' >&2; exit 1; }
case "$expected" in *[!0-9a-f]*) echo 'Invalid installer checksum.' >&2; exit 1;; esac
actual=$(sha256 -q "$work/installer.tar.gz")
[ "$actual" = "$expected" ] || { echo 'Installer download verification failed.' >&2; exit 1; }
"$python" - "$work" <<'PY'
from pathlib import Path
import sys, tarfile
root = Path(sys.argv[1])
with tarfile.open(root / 'installer.tar.gz') as archive:
    archive.extractall(root, filter='data')
entries = list(root.glob('opncell-installer-*/installer/install-cellular.py'))
if len(entries) != 1:
    raise SystemExit('Could not locate the downloaded installer.')
(root / 'entrypoint').write_text(str(entries[0]))
PY
entry=$(cat "$work/entrypoint")
"$python" "$entry" --repository-base-url "$repo" "$@"
