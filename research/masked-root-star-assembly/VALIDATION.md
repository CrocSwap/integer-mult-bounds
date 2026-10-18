# Validation receipt

Date: 2026-10-13. Base: `49b3157d1d89adcef16df8be98445451672be5ba`.
Environment: macOS 27.0.1 arm64, CPython 3.14.7, standard library only.
No floating-point acceptance decisions, downloaded solvers, or random
mathematical searches are used. The task-selection nonce is provenance only.

From the repository root, the following passed:

```sh
python3 -I -B research/masked-root-star-assembly/verify.py
python3 -I -B research/masked-root-star-assembly/independent.py
python3 -I -B research/masked-root-star-assembly/test_package.py
python3 scripts/research_package.py --package research/masked-root-star-assembly --check-only
python3 scripts/verify_selected_result.py
git diff --check
```

The two mathematical final lines are:

```
PASS_MASKED_ROOT_STAR_ASSEMBLY_FLOOR_64 atoms=57600 frames=1260 max_odd_clique=8 controls=8
PASS_MASKED_ROOT_STAR_INDEPENDENT frames=1260 pairs=57600 quadratic_dimension=8 floor=64 controls=5
```

All seven package tests passed (15.4 seconds on this host). They run
both checkers under `-I -O -B` from a temporary directory with spaces and
without repository files or Git; verify that replay changes no package
bytes; reject altered proof-relevant receipt fields and missing receipts;
and compare the two receipts' common mathematical premises. The primary
checker takes about 1.1 seconds and the independent checker about 3.8
seconds here. These are local verification timings, not multiplication
runtime claims or portable benchmarks.

Both certificates were initially generated through their explicit
`--write` commands and then checked by read-only replay. The primary
checker tests eight semantic controls. The independent checker tests five,
including an actual nine-vector counterexample if the quadratic condition
is omitted, and a cost-one singleton outside the exact-star support scope.

A separate AI reviewer checked the written proof, independently rebuilt
the support and frame facts and odd-clique counts, inspected both
implementations and ran both optimized checkers. No correctness issue was
reported. This is additional AI review, not independent human review or
proof-assistant certification.

The selected-record integrity check passed at
`836330098538459/500000000000000000`. It is an integrity check only;
the mathematical result does not depend on that selected kappa.

The registered replay manifest targets the repository's Python 3.12 CI
environment. That Python version is not installed on this host, so the
generic replay command itself was not run locally; its metadata and pins
passed, and each registered subprocess passed using Python 3.14.7.
Hosted CI, Lean, the full repository suite, native/hosted supplier replay
and `make frontier1094-verify` were not run for this additive scoped proof.
No selected record, frozen input or upstream file was changed.
