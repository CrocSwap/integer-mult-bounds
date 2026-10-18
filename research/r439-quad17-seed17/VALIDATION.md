# Executed verification

2026-10-13, CPython 3.12.3 on Linux. No third-party mathematical dependencies.

Passed:

```sh
python3 -I -B research/r439-quad17-seed17/verify.py
python3 -B scripts/research_package.py --package research/r439-quad17-seed17 --check-only
python3 -B scripts/research_package.py --package research/r439-quad17-seed17
python3 -B scripts/research_baseline.py
python3 -B scripts/verify_selected_result.py
git diff --check
```

The first command checks the complete deterministic certificate, both complete
factorization graphs, both reverse-endpoint censuses, source pins, exact inverse,
parent literal cleanup structure, nonuniform independent-coordinate examples
and eight rejection controls. The metadata check is not mathematical acceptance;
the baseline checks bindings/arithmetic only. The selected-record check verifies
its source inventory and supplements without replaying the entire supplier.

No full bit/complex supplier, native 5/9/11-stage, hosted invoice or outer
assembly is changed or replayed. No historical global artifact regeneration is
required for this isolated audit. The applicable repository guidance calls for
checks affected by the change; `make verify` and the selected cold replay are
not used as evidence for this local result.
