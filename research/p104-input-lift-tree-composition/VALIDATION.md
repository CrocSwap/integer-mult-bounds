# Validation

Environment: CPython 3.12.13, macOS 26.6.1, arm64. The verifier uses the standard
library and the exact pinned source archive. All times below are UTC.

At 2026-11-02T02:37, the complete receipt generation passed:

```sh
/tmp/kappa-1101-venv/bin/python -I -B research/p104-input-lift-tree-composition/verify.py --write-result
```

It checks every regenerated source and caller byte, all 799 input columns,
2,930 distinct native maps with absolute phases, 7,904 caller contacts, the full
invoice, two rational price engines, compiler and 58 outer predicates. Fourteen
semantic controls reject, including missing paid work and target debits.
The raw crossing is inside (0.00314981300605,0.00314981300606).

The package metadata and all 17 live source pins pass. The selected record
SHA256 remains 9b8d0eea95b3bf0dfcb7938a732a6439b87a2685dec2a5ab9e525b3b34debbfa.
The branch base is canonical main 7c49fe32c55de02c2c873655c804b16e4c3fef0a.

At 2026-11-02T02:44, both registered normal and optimized complete replays
passed. They produced the same retained receipt and all failure controls:

```sh
/tmp/kappa-1101-venv/bin/python -B scripts/research_package.py --package research/p104-input-lift-tree-composition
```

Committed-byte checks, export and sealed replay are next. Hosted CI and
independent scientific review are pending.
The repository is shallow; full source-history preflight is not yet claimed.
