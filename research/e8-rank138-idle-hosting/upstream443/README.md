# R740 kernel with 32 replicas and complete residual banks

The conditional candidate is **κ = 0.001138823042306561**, with bit lower endpoint
**0.001140121438872176364117**. Full verification is required before admission.
It exceeds PR #441 at `6160c13526f5f957902910b462164c93c1d8f39a` by about 0.00219%.

Eight replicas forced the previous search to drop kernel pivots so that residuals
filled whole width-64 banks. Four independent groups of eight replicas allow a
114-pivot kernel with entrance rank 138 to fill 2,891 banks per stage exactly.
This preserves two rank-one pivots that the eight-replica packing discarded.
All bank coordinates are occupied; there is no padding. The primitive ADD
sequence retains PR #440's 57 A-frame choices and PR #441's two B-frame stages
(112 and 42 changes, 126 net changed B gates). Both stages are rechecked on the
new kernel word.

| Quantity | Result |
| --- | ---: |
| Helpers / local arbitrary input columns | 740 / 980 |
| Replicas / local invocations | 32 / 288 |
| Kernel pivots / donor slots / entrance rank | 114 / 103 / 138 |
| Banks per stage | 2,891 |
| Live / physical families | 56,739 / 56,748 |
| One-replica unbanked global columns | 7,620 |
| Helper owner assignments | 213,120 |
| Rank deficit | 9,984 |
| Cited complex lower endpoint (#433) | 0.001183986549206329 |
| Binding side | Bit |

## Reproduction

Python 3.11 or newer, numpy, mpmath, sympy, a C++17 compiler and Boost headers:

```sh
python3 -m pip install -r research/e8-r740-replica32/parent436/requirements.txt
bash research/e8-r740-replica32/verify.sh /tmp/e8-r740-replica32-full
```

Set `PYTHON`, `CXX` or `BOOST_INCLUDE` when needed. `--quick` skips only the
parent's historical regressions. Every mode checks the frozen manifest and
parent source blobs, reconstructs PR #436 and both new transformations, verifies
local arbitrary-dirt columns, reflected copy chronology, exact frame projectors,
all replica owners and residual bank coordinates, 16 explicit orthogonal routes,
mutation controls, two rational moments, a fresh finite invoice, six bootstrap
levels and 47 strict outer inequalities. The next grid point is rejected.

## Scope

PR #442 reports a larger bound using an additional idle-data hosting extension.
This package isolates the gain from exact replica banking within the prior
helper-bank interface.

This is a finite conditional construction for the retained
`T(n) = O(n (log n)^(1-κ))` assembly. The complex supplier is cited from #433,
including its #425 mutable-basis interface; its construction and Gaussian-phase
audits are not rerun here. Astronomical cover enumeration, all-size compiler,
correlated dirty-bank, restored-work, precision, tape/common-grid and analytic
interfaces remain assumptions. This is not a Lean proof or an unconditional
integer-multiplication theorem. κ = 1 remains open.

Search scores only nominated candidates. The admitted witnesses, costs, maps and
strict comparisons use integers or exact rationals. See `PROOF.md`, `NOTICE.md`,
`SOURCE.json` and the unchanged parent package for dependencies and proof scope.
