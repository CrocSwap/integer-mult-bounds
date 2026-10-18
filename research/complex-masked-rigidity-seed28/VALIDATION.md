# Local validation receipt

Date: 2026-10-13. Environment: macOS 27.0.1 arm64, CPython 3.14.7.
Base: `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`.

Completed:

```sh
python3 -I -B research/complex-masked-rigidity-seed28/verify.py
python3 -I -O -B research/complex-masked-rigidity-seed28/verify.py
python3 -I -O -B research/complex-masked-rigidity-seed28/tensor_oracle.py
python3 -B -m unittest discover -s tests -p test_selected_result.py
git diff --check
```

Both checker modes pass with identical deterministic receipts. The main
command checks 7744 covariance entries, a 12544-entry nine-term positive
identity, seven semantic controls, and the independent certificate. The
oracle enumerates all 1260 second frames and all 1373 domains and checks
143584 local spans using 122 nonsingular integer minors. Its three further
controls cover diagonal deletion, ordered-pair orientation and a duplicate
basis row. Nonzero determinant modulo 3 certifies nonzero integer
determinant; no probabilistic rank inference is used.

An additional subprocess test replaced one row of the first saved witness
with a duplicate and invoked `tensor_oracle.py --check` under `-I -O -B`.
It exited nonzero at `saved certificate differs from exact regeneration`.
Verification uses explicit exceptions and remains enabled under `-O`.

The unchanged selected-record integrity suite passes all five tests.
This is a metadata/source integrity check, not the selected construction's
cold replay. Only the new scoped directory is added.

One measured main replay took 0.43 seconds wall time (0.40 user, 0.01
system), including the independent oracle. This is a single local runtime
observation, not a comparative performance claim.

A separate AI agent reviewed the written proof and main checker and found
no actionable mathematical defect. Another review independently rebuilt
the roots, checked every witness's coverage and evaluated all 122 integer
determinants with Bareiss elimination: every absolute determinant was
4096 and its residue agreed with the oracle. These reviews are not
independent human review or proof-assistant verification.

Not run or claimed: full selected-frontier cold replay, unrelated historical
suites, native supplier admission, hosted Linux CI, or an all-size integer
multiplication proof. No changed supplier is proposed.
