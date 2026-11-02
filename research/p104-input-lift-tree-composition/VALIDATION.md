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

At science commit `b5515d69f5dfc4b3a9f1692516a383fefa7ed754`, the
committed-byte and executable-mode check passed for all 28 package/input files.
The official export and declared-input coverage check passed for all 17 live
inputs. Export SHA256:
`bbf05333f2893af30aab32ca1c2b7ccb58f058810834671a2fd868ba18ee4b76`.

At 2026-11-02T02:46, the complete optimized export replay passed with all input
files read-only, `PATH=/nonexistent` and no Git. All 29 exported files and all
36 path modes were unchanged. Two actual byte mutations in disposable exported
inputs also rejected before scientific replay: a damaged native word failed
its source hash, and a changed kappa literal failed the declared-price edit
check. Both bytes and modes were restored and checked again.

```sh
python3 -B scripts/check_research_commit.py --package research/p104-input-lift-tree-composition --check-modes
python3 -B scripts/export_research_package.py export --package research/p104-input-lift-tree-composition --ref b5515d69f5dfc4b3a9f1692516a383fefa7ed754 --output /tmp/kappa-composition-export-b5515d69f.tar.gz
python3 -B scripts/export_research_package.py check /tmp/kappa-composition-export-b5515d69f.tar.gz --check-inputs
```

The optional full source-history preflight stopped with
`source-history check requires full Git history`. This checkout is shallow.
All source pins resolve at the declared canonical base, which is an ancestor
of the publication commit; no side-branch source pin is used. The complete
Git-free export replay passed as stated above. Full history was not fetched.

The canonical main refresh at 2026-11-02T02:45 still gives the declared base.
Hosted CI and independent scientific review are pending. The selected result
and all frozen predecessors remain unchanged. The gain remains small; the
one-percent donor target is not met.
