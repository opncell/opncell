# OPNcell packaging

The current appliance-tested plugin is **26.7.2_26**. **26.7.2_27** freezes that functionality with the Subscriber List spacing correction for upgrade acceptance on 10.11.0.52 and fresh-install acceptance on 10.11.0.55/56. Revision **26.7.2_18** remains the published CPU-routing release for OPNsense 26.7 on FreeBSD 15 amd64. See [release status](../docs/releases/STATUS.md).

The candidate installer entry point is `scripts/install-cellular.py`, with
`scripts/migrate-mongodb.py` beside it. Its optional `--migration-bundle` restores
MongoDB 5 application records into a fresh MongoDB 8.0 directory and verifies them
before enabling database startup. Prepare the bundle before replacing MongoDB 5.
See [the migration procedure](../docs/mongodb-installation-migration.md) for scope,
required tools, supported collection/index definitions, and pending appliance tests.
CPU-aware installation is published, while full installer/migration acceptance remains pending; ordinary pkg installation does not perform CPU detection.

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

The validated scope covers upgrades and local provisioning/service behavior. A full fresh installation still requires configuration sample and certificate provisioning acceptance. The sample-staging helper is prepared for a future Open5GS port build. It is not part of the tested Open5GS 2.8.0_1 binary.

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
