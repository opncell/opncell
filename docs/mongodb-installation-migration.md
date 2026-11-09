# MongoDB 5 to 8.0 installation migration

Status: implementation and mocked failure-path tests pass. Full installer validation
on FreeBSD and the Atom C3858 remains pending. Do not publish the installer or the
new MongoDB candidate until that acceptance test succeeds.

## Installation entry point

`packaging/scripts/install-cellular.py` installs the plugin and restores a prepared
migration bundle. Keep `migrate-mongodb.py` and `configuration-upgrade.py` beside it,
with the sibling `defaults` directory. These use Python's standard
library; migration also requires `mongoexport`, `mongoimport`, and a Mongo shell.
The source may use the existing `mongo` executable. The target uses `mongosh`.
Tools must already be staged; the installer does not download executables via npm.

MongoDB 5 cannot open MongoDB 8 data files, and MongoDB 8 must never open the
legacy data directory. This procedure exports application records and indexes and
imports them into a separate fresh directory. It does not perform an in-place
WiredTiger upgrade or change feature compatibility version.

The preparation phase must run while MongoDB 5 is still installed and running.
A package post-install hook is too late to export from a removed MongoDB 5 binary.
OPNsense's OS upgrade stays separate from this installer.

## Before the OS or package replacement

1. Stop radio/core writers and provisioning changes. Preserve their boot settings.
2. Stop MongoDB and create a cold backup of its actual command-line data path,
   MongoDB configuration, service script, and OPNsense `config.xml`. Retain an
   independent off-host copy and a rollback boot environment.
3. Restart only MongoDB 5 for the export. Keep provisioning/core writers stopped.
4. Run, using paths appropriate to the staged tools:

```csh
python3 migrate-mongodb.py prepare --bundle /root/cellular-migration-5-to-8 --cold-backup /root/preupgrade.tar.gz --shell /usr/local/bin/mongo --mongoexport /root/tools/mongoexport --writers-stopped
```

Preparation validates the gzip/tar backup, locks MongoDB against writes during
export, exports all supported `open5gs` collections as canonical Extended JSON,
records counts/indexes/source path, and saves SHA256 checksums in `manifest.json`.
It also preserves Open5GS/freeDiameter configurations, TLS and Hnet material from
the current and legacy installation directories, before their packages are removed.
If the original prefix is mounted elsewhere, pass `--legacy-prefix PATH`.
MongoDB is unlocked in a finally block. If the machine or exporter is forcibly
terminated during a lock, inspect the source and run `db.fsyncUnlock()` before use.
Do not treat an incomplete bundle without `manifest.json` as usable.

The bundle is private (0700 directory, 0600 files). It contains subscriber secrets.
Collection options, views, special indexes and system collections are deliberately
rejected until supported. The tool does not discard their definitions silently.
Database accounts, roles, other databases, replication configuration, and TLS
settings are not migrated. This first installer supports local unauthenticated
standalone MongoDB only. Preserve any such configuration separately.

5. Copy the complete bundle and cold backup off-host. Stop MongoDB. Disable
   `mongod` and all Open5GS boot services before the supported OPNsense OS upgrade.

## On FreeBSD 15

After the OPNsense upgrade is complete and all MongoDB/Open5GS processes are stopped:

```csh
python3 install-cellular.py --migration-bundle /root/cellular-migration-5-to-8 --recovery-dir /root/cellular-install-recovery --mongoexport /root/tools/mongoexport --mongoimport /root/tools/mongoimport
```

Both the recovery directory and `/var/db/opncell-mongodb80` must be new. The installer:

- Validates bundle checksums and the retained cold backup.
- Fetches the MongoDB package from the selected repository and executes its version
  command on this CPU before removing installed packages. Version 8.0.34_3 or newer
  in the 8.0 series is required; a version number alone is not a CPU compatibility test.
- Archives current Open5GS, freeDiameter, MongoDB, boot and OPNsense configurations.
- Restores missing original Diameter files, corrects legacy file paths, and checks
  required certificates/extensions. Existing identities, peer addresses and keys
  win over defaults. Fresh installations use packaged defaults and locally generated
  Diameter TLS material; private keys are never part of a distributed package.
- Keeps cellular/MongoDB boot services disabled during replacement and refuses
  legacy removal if unrelated packages depend on it.
- Replaces legacy packages, creates `/var/db/opncell-mongodb80`, and configures
  MongoDB on loopback port 27017 with an explicit matching service data path.
  Both previous data directories remain untouched.
- Creates collections and unique indexes, inserts records without upsert or drop,
  and compares every re-exported document, BSON type, collection count and index.
- Enables MongoDB boot startup only after verification. Open5GS activation remains
  a topology Apply action in the plugin.

The installer can also perform a fresh installation without `--migration-bundle`,
but refuses recognised legacy WiredTiger directories. It never treats an existing
database as a fresh install.

## Failure and repeat runs

Every command reports `SUCCESS` only for completed checks, or exits nonzero with
`FAILED`. Successful restore writes `verification.json`; installation writes
`installation.json` in the recovery directory. Import errors leave the new database
for diagnosis, stop MongoDB when caught by the installer, and keep boot disabled.
There is no automatic deletion or automatic rollback of imported records.

A non-empty target without a completed verification report is refused. After a
successful restore, repeating `migrate-mongodb.py restore` verifies existing data
instead of reinserting it. The installation entry point itself refuses an existing
target/recovery directory, so it cannot repeat package removal accidentally.

Standalone verification:

```csh
python3 migrate-mongodb.py verify --bundle /root/cellular-migration-5-to-8 --target-dbpath /var/db/opncell-mongodb80 --mongoexport /root/tools/mongoexport --writers-stopped
```

An export taken before subsequent provisioning writes does not include those later
writes. Establish the maintenance window before preparing the final migration bundle.
Never restore the old cold files over the fresh MongoDB 8 directory. Rollback uses
the old binary/boot environment with its original data or cold backup.

## References

- [MongoDB 8.0 upgrade path](https://www.mongodb.com/docs/v8.0/release-notes/8.0-upgrade-standalone/)
- [mongoexport](https://www.mongodb.com/docs/database-tools/mongoexport/)
- [mongoimport](https://www.mongodb.com/docs/database-tools/mongoimport/)

Canonical JSON is used for application-data migration. The independent cold backup
is retained because mongoexport alone is not a complete deployment backup.

## CPU-specific MongoDB selection

Revision 26.7.2_18 selects CPU-specific catalogs automatically. The default base
URL is `http://repo.opncell.io/OPNcell-repo`; supply `--repository-base-url` to test
a private staged release instead. On FreeBSD 15, the portable URL ends with
`${ABI}` and the AVX2 URL with `${ABI}-avx2`. The shared plugin package permits
both MongoDB port revisions; the portable catalog and installer policy still
require the tested NOAVX `_3` binary.

The optimized path requires kernel-reported AVX, AVX2, XSAVE, OSXSAVE, FMA and
F16C on amd64. AVX alone is insufficient. An unreadable or inconclusive feature
report selects NOAVX. Before removing packages, the installer checks package
options and executes the extracted candidate. The official `_1` AVX package
has incorrect NOAVX metadata; only its exact tested checksum receives an
exception, only on the AVX path. Every other candidate uses the normal checks.

After installation the binary digest must match the tested candidate. If
switching CPU variants requires a lower package revision, only the exact tested
MongoDB package is force-installed. This does not bypass the digest check.
The selected catalog is written atomically to OPNcell.conf only after database
restore/verification succeeds. Its previous contents are preserved in the
recovery directory. OPNsense.conf is untouched. Subsequent package upgrades
therefore continue using the selected CPU catalog.

Use preflight mode before installing:

```sh
python3 install-cellular.py --preflight-only --recovery-dir /root/cellular-cpu-preflight
```

Preflight writes a report in a new recovery directory, but does not install
packages, change service configuration, or persist a repository selection.
For a private staged release, add `--repository-base-url URL`. The revision 18 CPU routes are public and passed stable-URL preflight checks on 2026-11-09.

Advanced users with manually configured repository names can use
`--repository-base-url '' --avx-repository NAME --noavx-repository NAME`; those
existing named-repository configurations are not rewritten by the installer.

MongoDB 5.x migration remains part of the install flow from a prepared canonical
export and cold backup. Backup/export preparation is still separate. An existing
MongoDB 8.x deployment is not automatically treated as a fresh installation.
Full installation/migration acceptance on an AVX OPNsense appliance remains
pending; both real AVX and simulated non-AVX routing/binary preflights passed on
the repo host. The portable binary was previously tested on the Atom appliance.

### Immediate CPU-only information (revision 19 preview)

The preview installer accepts `--cpu-info` without a recovery directory. It reads
kernel CPU features, reports AVX2 or NOAVX and the intended repository route, and
returns without catalog queries, package downloads, extraction, installation or
configuration writes. The repo host completed this check in 0.174 seconds.

Use `--preflight-only --recovery-dir NEW_DIRECTORY` separately to verify the
actual package. Full preflight now displays the exact package version and CPU
flavor plus stage messages. It uses the package manifest to locate mongod,
avoiding a second full archive-decompression pass.

The preview bundle is separate from the unchanged published revision 18 package
and installer archive. It does not install revision 19 or change package catalogs.
