# Publication validation

Python 3.12, standard library, base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

- `python3 -B scripts/research_package.py --package research/paired-query-only-bit`: PASS, including the primary reconstruction and the independently implemented reverse/operator/arithmetic check.
- `python3 -I -O -B research/paired-query-only-bit/check.py`: PASS. The independent checker separately requires assertions enabled and rejects optimized mode.
- `git diff --check` and the committed-byte/mode preflight: PASS for the tested package. No unrelated tracked paths are changed.
- The two verification commands are read-only. Exact caller/receipt hashes and the independent proof-relevant results are retained in the package; the primary receipt's elapsed time is observational only.

The optional `--check-source-history` preflight refused this deliberately shallow checkout because it requires full Git history. No full-history pass is claimed. Main-commit provenance validation and all vendored source byte checks passed; off-main source exports are authenticated locally by INPUT-PINS.json and require no foreign Git objects for replay.

No hosted CI, maintainer acceptance, formal proof-assistant verification or complete physical multiplier is claimed. The source tariff, compiler and five framework assumptions remain explicit in PROOF.md.
