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

Committed-byte checks, export and read-only Git-free replay are pending at
this draft stage. Hosted CI and independent scientific review are also pending.

The checkout is shallow. The optional full-history preflight is not claimed.
The selected record has SHA256
`9b8d0eea95b3bf0dfcb7938a732a6439b87a2685dec2a5ab9e525b3b34debbfa`.
All five source framework assumptions remain. No selected-result change,
formal-kernel verification or materialized multiplier is claimed.
