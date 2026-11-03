# Validation record

Environment: CPython 3.12.13 on macOS, November 3, 2026 (UTC).

The complete direct generation run passed:

```sh
python3.12 -I -B research/retirement-rebalanced-query-tree/verify.py --write-result
python3.12 -B scripts/research_package.py --package research/retirement-rebalanced-query-tree --check-only
python3.12 -W error -B scripts/research_package.py --package research/retirement-rebalanced-query-tree
```

Markers: `PASS_REBALANCED_RETIREMENT_KAPPA_00329492`,
`PASS_PACKAGE_METADATA_AND_PINS` and `PASS_REGISTERED_RESEARCH_PACKAGE`.
Registered normal and optimized replay both passed. The initial attempt rejected the inherited
31/32 tail decay. The final run uses the charged 97/100 decay and 10^(-27)
reserve, and includes the old decay as a negative control.

Coverage includes full PR6529 native regeneration and PR6545 caller replay,
all source controls, all 799 native columns, absolute phases, all 7,488
physical contacts, both new 1,225-coefficient caller engines, the dual pairs,
the exact complete invoice delta, both rational price engines, the compiler
and all 58 outer predicates. Every retained source receipt is checked after
its scientific checks. No source receipt replaces a computation.

Four extra source controls rejected a false archive SHA256, a false member
SHA256, a false Git blob and an omitted archive member. The candidate receipt
contains 13 endpoint and invoice rejection controls, in addition to the
unchanged source controls and analytic rejection checks.

Scientific commit: `6f779707dfddcece2e964f627cbd0df6d11bf41c`. Its parent is
canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. All 17 committed
package files pass byte and executable-mode comparison. The official export
passes integrity and declared-input checks:

```sh
python3.12 -B scripts/check_research_commit.py --package research/retirement-rebalanced-query-tree --check-modes
python3.12 -B scripts/export_research_package.py export --package research/retirement-rebalanced-query-tree --ref 6f779707dfddcece2e964f627cbd0df6d11bf41c --output /tmp/rebalanced-tree.tar
python3.12 -B scripts/export_research_package.py check /tmp/rebalanced-tree.tar --check-inputs
```

Both direct normal and optimized verifiers passed from that export with
all files read-only, no Git metadata and an empty PATH. The interpreter was
invoked by its absolute path from outside the export. All 18 files, including
the export manifest, kept their hashes and read-only modes after both runs.
This record was then updated; the scientific files were not changed.

Four source authentication controls also passed on CPython 3.12.13. The
original 23 outer source files were checked against the exact PR6545 Git
objects before their archive was made. Nested native and replay sources
authenticate through their unchanged source manifests on every run.

At this local validation freeze, hosted CI and independent scientific review
are pending. The PR records the later hosted status separately.

The checkout is shallow. The optional full-history preflight is not claimed.
The selected record has SHA256
`9b8d0eea95b3bf0dfcb7938a732a6439b87a2685dec2a5ab9e525b3b34debbfa`.
All five source framework assumptions remain. No selected-result change,
formal-kernel verification or materialized multiplier is claimed.
