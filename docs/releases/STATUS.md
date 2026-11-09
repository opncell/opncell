# Release status

- 26.7.2_16: installed and tested on OPNcell-c. Diagnostics layout, hourly filter and Clear were confirmed; Download appears to work. Hourly log rotation still requires verification.
- 26.7.2_17 AVX test candidate: private catalog only. The official precompiled MongoDB artifact passed isolated database/index/restart tests on the AVX2 repo host; the packaged CPU-selection preflight also passed. Full OPNsense installation/migration testing remains outstanding.
- Public repository activation is separate from these source commits. This branch does not switch live package repositories.
- Profile Subscribed users count sorting remains outstanding.

The portable MongoDB 8.0.34_3 build and the official AVX-capable 8.0.34_1 artifact use separate catalogs. Do not mix them. Consult 26.7.2_17-avx-test.md for the exact-checksum exception to the official package's incorrect NOAVX metadata.

Historical scripts such as stage-public-repository.py retain release-specific paths. Review and update their target release and FreeBSD 14 compatibility route before publication; they are not generic activation commands for the current candidate.
