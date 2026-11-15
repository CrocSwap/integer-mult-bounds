# P104 tooling: lift the input-lift and BIT-pin gate ceilings

DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

Tooling/framework change only. No word, no kappa claim. The pinned
`research/shared-wire-split-composition/interval_gate.py` is **not edited**
(its sha256 is pinned in `certificates/frontier7000-source.json`); this package
ships a patched copy, `interval_gate_signed.py`, and the diff.

## Problem: two ceilings just above the frontier

The official complex-word gate cannot certify any word above these kappa values
(percent over the #7617 frontier, kappa .00365760025222):

| Ceiling | Value | Over #7617 | Cause |
|---|---|---|---|
| Input-lift check | .0037765 | +3.24% | absolute curvature 94.216 |
| Default BIT pin | .00376669 | +2.98% | pin from #6726 |
| **After this patch** | **kappa < .00385248 - 7g** | **+5.33%** | admitted BIT saving |
| Lift proof alone (signed) | .006957747 | +90% | signed curvature 51.137 |

1. The lift check asserts `d1 + lift_cap*curv < 0` for
   L(k) = sum_{7,3,5} r^(1-k) - sum_{9,4,1,1} r^(1-k) with d1 = -0.355801 and
   curv = sum over *all* ranks of r ln^2 r = 94.2157, giving -d1/94.2157 = .0037765.
   Above that the gate sets lift_cap = tested and the assertion fails, although the
   lift is positive up to kappa about .05.
2. The default pin .00376669 forces tested < pin. The admitted ordinary BIT
   saving is .00385248 (12039/3125000 in `certificates/frontier7000/CLAIM.json`;
   #7001 admission, `README.md` lines 36-37, `PROOF-REVIEW.md:389` of
   pr7000-application: "The completed BIT saving .00385248 supplies the weaker
   .00376669 premise"). Its premise status is unchanged: conditional on the same
   five assumptions.

## Fix (three hunks, see `interval_gate.diff`)

- `curvature` sums only the negative-coefficient ranks: N = 9 ln^2 9 + 4 ln^2 4 + 2*1*0 = 51.1374.
  `abs_curvature` is still computed and reported.
- `lift_cap = cap if cap <= LIFT_RANGE (.0069) else tested`.
- `BIT_PIN = '.00385248'` is the default (function and CLI), with the citation in a comment;
  `assert cap <= F(BIT_PIN)` rejects a pin above the admitted saving
  (the original accepted any `--bit-pin`).

Certifiable ceiling: tested < pin, i.e. kappa < .00385248 - 7g (tested = claim + 7g).
The lift proof alone reaches -d1/N = .006957747.

## Proof that the signed bound is valid

Write L(k) = sum s_i r_i^(1-k), s = +1 on {7,3,5}, -1 on {9,4,1,1}; k >= 0, r >= 1.

1. 0 < r^(-k) = exp(-k ln r) <= 1.
2. L(0) = 0 and L'(0) = -d1 = 0.355801 > 0.
3. L''(k) = sum_pos r ln^2 r r^-k - sum_neg r ln^2 r r^-k >= -N, since the positive part is >= 0 and the negative part is <= N by (1).
4. L'(k) = L'(0) + int_0^k L'' >= -d1 - kN. If d1 + cap*N < 0, L' > 0 on [0, cap], so L is strictly increasing and L(k) > 0 on (0, cap].
5. Taylor with integral remainder gives L(k) >= -k d1 - k^2 N/2, which is the gate's per-price assertion; it is weaker with N in place of curv, hence still valid.
6. Interval direction: the gate tests the upper ends, d1_hi + cap*N_hi < 0, and d1 <= d1_hi, N <= N_hi.

The absolute bound |L''| <= sum_all r ln^2 r was valid but dropped the sign of the positive part. All other
gate checks (alpha, gamma, delta, eta, log-power, compiler gap, 54+4 outer, main-moment monotonicity) are untouched.

## Lean status

`LiftPositivity.lean` (no `sorry`, no `native_decide`, no `set_option`; axioms propext, Classical.choice, Quot.sound)
proves `lift_pos` (0 < kappa <= 69/10000 implies lift kappa > 0), `lift_strictMonoOn` and
`signed_gate_inequality` (d1 + (69/10000) N < 0 in exact reals). Logs of 3, 5, 7 come from Mathlib's log 2 bounds
plus the log(1-x) series remainder.

**Checked under Lean v4.33 / Mathlib 55b7917; not yet built under the repo pin (v4.21 / Mathlib 308445d).**
The file carries the import for the repo pin, `Mathlib.Data.Complex.ExponentialBounds`
(`Mathlib.Analysis.Complex.ExponentialBounds` in the newer Mathlib used for the check). Every lemma used exists at
308445d; tactic behaviour (`nlinarith`) under v4.21 is unverified.

## Tests

`python3 -I -B research/p104-gate-ceiling-lift/tests/gate_test.py` (registered in `VERIFY.json`; 32 cases, exit 0 only if all
have the expected outcome):

- #7000 recorded invoice: the pinned original reproduces its recorded gate fields; the signed gate passes and at the old pin differs only in input-lift fields.
- #7617 (claim .00365760025222) and #7615 (.00365455370060): original and signed both pass; for each, 3 corrupted invoices, a claim above the crossing and a gap numerator != 1 are rejected.
- Pin ceiling (synthetic invoice crossing .0038777): tested = pin - 1e-16 passes; tested = pin, pin + 1e-16, and a `--bit-pin` above .00385248 are rejected; the original at the old pin behaves as before.
- Lift ceiling: with the pin guard relaxed, lift caps .00695774704 and .0069577 pass; .006957747045 and .0069578 fail at the lift assertion; LIFT_RANGE branch cases.
- Mutants of the signed bound (curvature sign flipped, pos/neg histograms swapped, d1 sign flipped) are rejected; LIFT_RANGE = .1 with the real pin still passes.

`data/frontier_invoices.json` holds the rank histograms of the #7617 and #7615 complete invoices (frontier word x #7113 caller)
as computed by our pricer; they are gate-logic inputs. #7617 itself did not run this gate, so the claim/tested parameters
used here (g = 1e-16) are ours. Synthetic invoices test gate logic only and are not words.

## Caveats

- The lift histogram {7,3,5}/{9,4,1,1} is hard-coded and inherited from #7000; a word that changes its input lifts is not covered.
- The five conditional assumptions behind the BIT premise are inherited unchanged; only the margin to the pin changes.
- The Lean check is not yet reproduced under the repo's Lean/Mathlib pin (above).
- Ceiling statements are for the gate's logic; this package certifies no word.

## Open next questions

- Does `LiftPositivity.lean` build under Lean v4.21 / Mathlib 308445d? First step: build it with the repo-pin import already applied.
- Can the input-lift histogram be computed from each word's actual invoice instead of being hard-coded? First step: derive it from the invoice and rerun the signed bound.
