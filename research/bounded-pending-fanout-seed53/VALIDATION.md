# Local validation

Checked on macOS arm64, CPython 3.11.15 and 3.14.8, on 2026-10-13 UTC.
Exact research base: `ce7ad1b6ab09452c3478723a2e96ed5ff212dc08`.
Final verifier stdout SHA256:
`d4fc755f22aa31ac062e20be2bd5222ca6c9001b14b2db4fa956825171c0bfba`.
Certificate SHA256:
`5e3c19a0731e5bc9093db5844b36e3f83c59725fd7ac95cea3b68f23e68f04a3`.

Commands run from the repository root with the user's RTK shell prefix:

```
rtk proxy python3.11 -I -B research/bounded-pending-fanout-seed53/verify.py
rtk proxy python3.11 -I -O -B research/bounded-pending-fanout-seed53/verify.py
rtk proxy python3.14 -I -O -B research/bounded-pending-fanout-seed53/verify.py
rtk proxy python3.11 -I -O -B research/bounded-pending-fanout-seed53/test_package.py
rtk proxy python3.14 -I -O -B research/bounded-pending-fanout-seed53/test_package.py
```

All pass. The final mathematical receipt agrees across interpreters and
optimization modes. Package checks confirm standalone relocation from an
unrelated working directory and byte-identical certificate regeneration.
Five real file mutations fail, including a changed producer paired with its
own regenerated certificate. No network is required by either public command.

The receipt covers 529 k/capacity cases, 46 complete child boundaries, 189
dense basis/mixed-state cases and their inverses, all free noncommutative
input columns of all three expanded programs, 14 rejected mathematical/input
controls and one explicit nonlinear counterexample. The exact finite BFS
minima are 4,6,6,10,8 on the five declared k/capacity pairs. No larger search
or exhaustive global circuit claim is made.

Selected-record integrity and all existing selected tests pass:

```
rtk proxy python3.11 -B scripts/verify_selected_result.py
rtk proxy python3.11 -B tests/test_selected_inventory_links.py
rtk proxy python3.11 -B tests/test_selected_proof_binding.py
rtk proxy python3.11 -B tests/test_selected_result.py
```

The suites run 8,12,5 tests respectively. Selected kappa remains
`836330098538459/500000000000000000`. No source in those checks was edited.
The final diff is confined to this new research directory; upstream/ and
existing certificates remain unchanged.

The 19:21 UTC refresh advanced origin/main to
`c0e3631dc24e3c24a861f7d3d79e0608481cccec`; it still selects PR1094 at the
same kappa and contains no conflicting package path. That is a handoff
observation, not a relabeling of the investigation base. Original PR889/938
heads and the four copied proof/notice pins remain fixed.

Full make verify, selected cold supplier replay, a physical tape implementation,
Linux execution, hosted CI completion, formalization and independent human
review were not performed. This package adds an abstract exact scheduling
interface and scoped query optimum; supplier integration and a kappa change
remain unestablished.
