# OPNcell packaging

The current published and appliance-tested plugin is **26.7.2_32**. Repository upgrades passed on three FreeBSD 15 appliances; the built-in firmware package action was also verified. One appliance subsequently passed an OPNsense 26.7.9 upgrade and reboot with all selected cellular services running. See [release status](../docs/releases/STATUS.md) and [revision 32 notes](../docs/releases/26.7.2_32.md).

The installer entry points are `scripts/install-cellular.sh` and `scripts/install-cellular.py`. Existing MongoDB 8.0 installations use `upgrade-cellular.py` to preserve database paths, service settings and subscriber provisioning. CPU-aware selection chooses the validated NOAVX or AVX2 catalog and checks the candidate binary before installation. Ordinary pkg installation does not perform CPU detection.

The optional `--migration-bundle` restores prepared MongoDB 5 application records into a fresh MongoDB 8.0 directory and verifies them before enabling database startup. Prepare the bundle before replacing MongoDB 5. See [the migration procedure](../docs/mongodb-installation-migration.md) for supported collections/indexes and recovery steps. The legacy logical migration was appliance-tested; arbitrary database layouts and unattended end-to-end major OS migrations are not implied.

| Directory | Contents |
|---|---|
| `ports/net-mgmt/os-cellular` | Cumulative plugin port and patches |
| `ports/databases/opncell-mongosh` | MongoDB Shell 2.14.0 companion port |
| `patches` | Open5GS freeDiameter FreeBSD fix |
| `scripts` | Dependency metadata, package collection, and configuration sample staging |
| `../docs/releases/26.7.2_6.md` | Installation, upgrade, verification, and recovery playbook |

The release collector copies the tested binaries and resolves their runtime dependency closure. It verifies known checksums and creates a local package repository, package lock, checksum list, and vulnerability report. Source rebuilds use the preserved distfiles and port recipes collected from the build host. The generated MongoDB Shell distfile and its npm lockfile must be retained for reproducibility.

Run on the FreeBSD build host as the release user:

```sh
python3.12 packaging/scripts/collect-release.py /usr/home/codex/opncell-release/26.7.2_6
```

A missing dependency stops collection before the repository is assembled. Fetch missing package candidates into a separate incoming directory, then rerun with `--incoming PATH`. Inspect `package-audit.txt` before distributing a collected bundle.

Fresh-install configuration and certificate provisioning, first topology setup, and subsequent reboot startup were verified on a clean boot-environment clone. The sample-staging helper remains separate from the tested Open5GS 2.8.0_1 binary.

Use a fresh destination for another release. Keep generated packages and working files outside Git.

## CPU catalog assembly and staging

`assemble-cpu-repositories.py` builds separate AVX2 and NOAVX catalogs from the
same plugin and dependency packages. It checks the two validated MongoDB package
hashes and retains the working FreeBSD 14 catalog route. It never activates the
public repository. `stage-public-repository.py` requires an empty release
directory, copies both catalogs, and verifies public HTTP file hashes and ABI
routes. Activating the live symlink remains a separate final step.

The port declares shared minimum dependency versions itself; builds no longer
need an external ACTUAL-PACKAGE-DEPENDS override. This allows the same plugin
artifact in both CPU catalogs without using the build host's MongoDB revision as
a universal minimum. CPU selection and binary validation remain installer policy.
