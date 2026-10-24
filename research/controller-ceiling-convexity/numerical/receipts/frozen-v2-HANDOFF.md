# Local handoff: independent PR5405 three-value ceiling verification

Status: **PASS for the exact scoped arithmetic and independent monotonicity audit**.
The frozen exchange and strict-discrete-convexity proofs, plus this numerical
certificate, imply the unbounded source equation-(1) invoice-family ceiling for
`0.00302728825 <= kappa < 1`. No author DP/tail replay is needed. No kappa gain,
changed-profile PR5402 transfer, physical optimum, native or compiler admission,
or complete multiplication theorem is claimed.

Review `PROOF.md`, `check_ceiling.py`, the two manifests and
`receipts/arithmetic-v2.json`. The exact gate gives

```
C18 > 0.000000014914967918767741908079
C18-C17 < -0.271338621904872494155700553536
C19-C18 > 0.022748156490424972863108432493
```

Every displayed decimal is a rational with denominator 10^30. Exact finer
integer/Q endpoints are retained. The checker uses a fresh independent 2^256
integer interval implementation with rigorous atanh-log and Taylor-exp tails.
No source engine, author DP, numerical library, solver, native or Lean code is
imported. All 456 tiny invoice identity controls and five explicit negative
controls passed. Canonical n=0,...,5 and 16,...,20 masks match the closed formula
by exact symbolic coefficients.

The first arithmetic stage completed under the 60-second/256MiB cap in about
0.11 seconds external wall time and 19,248KiB maximum RSS. The v2 run strengthens
profile and sign rejection checks and preserves v1 raw receipts/source. See the
raw `/usr/bin/time -v` logs and `RUNS.json` for exact final runtime, commands and
source hashes. Neither run failed; no raw receipt was overwritten.

Reproduce from the project root, choosing a fresh output filename:

```
/usr/bin/time -v timeout 60s python3 -B outputs/controller5405-exact-successor-20261024/check_ceiling.py --receipt /tmp/controller5405-independent-new-run.json
```

The script itself enforces RLIMIT_AS=256MiB, a 60-second alarm and exclusive
receipt creation. Refusing an existing receipt is intentional.

Source PR5405 head: `314b56a6c0056c2358538f072c6fde9d365be44d`.
Retained canonical main: `1ec1119972c9aefe42525172d07b332fcff81cb4`.
The source equation and local profile remain premises; no standalone derivation
from the original Laurent/native construction was executed. Root owns fresh
upstream overlap, packaging and public writes. This worker stops at the local
reviewable handoff; no GitHub, Discussion, package or publication write occurred.

Credit and open next questions are in `PROOF.md`. Preserve Ali Romman, Cinna
Davis, zxv and all retained native/helper/compiler lineage, as well as root's
conjectures and the sole Astra theory proof. The result is local and has not had
independent human or formal-kernel review.
