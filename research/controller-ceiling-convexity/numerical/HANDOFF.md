# Local handoff: independent PR5405 three-value ceiling verification

Status: **PASS for the exact scoped arithmetic and independent monotonicity audit**.
The frozen exchange and strict-discrete-convexity proofs, plus this numerical
certificate, imply the unbounded source equation-(1) invoice-family ceiling for
`0.00302728825 <= kappa < 1`. No author DP/tail replay is needed. No kappa gain,
changed-profile PR5402 transfer, physical optimum, native or compiler admission,
or complete multiplication theorem is claimed.

Review `PROOF.md`, `check_ceiling.py`, the two manifests and
`receipts/arithmetic-v3.json` and `FINAL-MANIFEST-v3.json`. The exact gate gives

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
0.11 seconds external wall time and 19,248KiB maximum RSS. The independent
reviewer identified that v2's assertion-based acceptance checks could disappear
under `python -O`. V3 replaces every assertion with explicit require/raise code.
Both final ordinary and optimized runs pass, with identical proof-relevant output
and the same arithmetic endpoints as v1/v2. Exact v2 checker, proof, handoff and
manifest bytes and all raw run receipts remain retained under `receipts/`. See
the raw `/usr/bin/time -v` logs and `RUNS-v3.json` for final runtime, commands,
source hashes and the transparent correction. No arithmetic run failed and no
raw receipt was overwritten; v2 is superseded as the acceptance checker.

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

Source representation correction: `SOURCE-REPRESENTATION-BRIDGE.json` binds the
original 10,030-byte monitor copy (SHA256 `5c82c9f...`) to the independently
fetched 10,029-byte upstream proof (SHA256
`77dc9ce552be7dc9c9a32850c2f2cf0eff92cfe2e0a0e316db210a1667a8d32b`, Git blob
`5ad89d4ba1836d47798bdb856e3726c70a7b1922`). Exact byte comparison proves the
monitor is upstream followed by one extra LF. The original copies/theory pins
remain unchanged, and both upstream bytes and reviewer fetch response are retained.
