# Release status

- 26.7.2_26: OPNcell-c acceptance confirmed for fast subscriber edits, integral policy display and successful saves.
- 26.7.2_27: frozen acceptance build with the Subscriber List top spacing aligned to Profile List. OPNcell-c (10.11.0.52) is the existing tested installation and will receive the package upgrade; 10.11.0.55 and 10.11.0.56 are fresh FreeBSD 15 installation targets. SSH access setup and acceptance remain pending. Changes after this freeze require a new revision. The versioned HTTP staging URL passed 117 file-hash checks, both CPU-route binary preflights passed on the build host (NOAVX route selection simulated), and the preserved ABI14 catalog parsed with 86 packages. The public live link remains revision 18.


- 26.7.2_16: installed and tested on OPNcell-c. Diagnostics layout, hourly filter and Clear were confirmed; Download appears to work. Hourly log rotation still requires verification.
- 26.7.2_19: private Diagnostics candidate with running-daemon list, independent All row/timeframe selectors and CPU-info messaging; appliance acceptance pending.
- 26.7.2_18: public dual CPU catalogs activated on 2026-11-09. HTTP checks and stable-URL CPU preflights passed; full installer acceptance remains pending. See 26.7.2_18.md.
- 26.7.2_17 AVX test candidate (superseded by 18): private catalog only. The official precompiled MongoDB artifact passed isolated database/index/restart tests on the AVX2 repo host; the packaged CPU-selection preflight also passed. Full OPNsense installation/migration testing remains outstanding.
- Public repository activation is separate from these source commits. This branch does not switch live package repositories.
- Profile Subscribed users count sorting remains outstanding.

The portable MongoDB 8.0.34_3 build and the official AVX-capable 8.0.34_1 artifact use separate catalogs. Do not mix them. Consult 26.7.2_17-avx-test.md for the exact-checksum exception to the official package's incorrect NOAVX metadata.

stage-public-repository.py now stages a new dual CPU release without activating it. It verifies HTTP hashes and preserves the working FreeBSD 14 route before any live-link change.
