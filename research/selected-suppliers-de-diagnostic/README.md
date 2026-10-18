# selected-suppliers-de-diagnostic

**Independent verification and diagnostic only. No new kappa; the selected
record is unchanged.**

Contributor: Navinor (with help from opencode). Apache-2.0. Task card:
[TASK-CARD.md](TASK-CARD.md); structured metadata: [TASK.json](TASK.json).

## What is checked

One selected pricing claim and one prescribed diagnostic, for both supplier
ledgers of the selected record
([`certificates/selected-result.json`](../../certificates/selected-result.json)):

1. **Moment acceptance of the whole completed construction.** The priced bill
   of a ledger with width `m`, live stock `W`, histogram `n_r` and bad-residue
   surcharge coefficient `c_s` is

   `f(a) = (1/(mW)) · Σ_r n_r r (m/r)^a + c_s m^a`.

   The exact moment is the acceptance test: the recorded endpoints must give
   `f(a) < 1` strictly, and the next `10^-24` grid point must give `f(a) > 1`.
   This package recomputes both signs for the complex k8/T16 gauge44 ledger
   (`m = 73`, `W = 14,336`, `N = 144`, no surcharge) and the bit PR589
   p111-tuned nine-stage ledger (`m = 64`, `W = 28,416`, surcharge
   `c_s = 32·m·Σn_r / (10^16 W)`) with an implementation disjoint from the
   retained engines.

2. **The `a < D/E` small-saving diagnostic** of
   [autoresearch.md](../../autoresearch.md) section 2, which the repository
   states without an in-repo proof. With `D = mW − Σ n_r r` and
   `E = Σ n_r r ln(m/r)` (and `D_eff = D − c_s mW`, `E_eff = E + c_s mW ln m`
   when the surcharge is present) the diagnostic is rigorous:

   **Lemma.** `f` is convex on `ℝ`, `f(0) = 1 − D_eff/(mW) < 1` and
   `f'(0) = E_eff/(mW) > 0`. The tangent at `a = 0` reaches 1 at
   `a = D_eff/E_eff`, and convexity gives `f(a) > f(0) + a f'(0)` for `a > 0`.
   Hence the exact root `a*` satisfies **`a* < D_eff/E_eff` strictly** whenever
   `D_eff > 0`. For `c_s = 0` this is exactly `a* < D/E`.

   The lemma turns the diagnostic into a valid *screen*: a proposed histogram
   whose `D/E` is below a target saving cannot reach it. The exact moment
   remains the acceptance test.

## Results

| Ledger | recorded endpoint `a` | moment residual at `a` | at `a + 10^-24` | certified `D/E` ceiling | `D/E ÷ a` | screening extremum |
|---|---|---|---|---|---|---|
| complex (m=73, W=14336) | 0.001675462676808103522925 | −1.304215e-24 | +1.624723e-24 | **0.001680590709754321699421** | 1.003061 | 0.013708749 (cap 51) |
| bit (m=64, W=28416) | 0.001733427039589844234749 | −1.598690e-24 | +1.669360e-24 | **0.001738557248401367986042** | 1.002960 | 0.016127138 (cap 45) |

- The residual intervals agree with both recorded engines' residuals in
  `research/community-frontier1094-audit/ASSEMBLY.json` (`mercator` and
  `base_two`), and reproduce the accept/reject sharpness at the next grid
  point. The complex values match the independently recorded
  `moment_minus_one` of
  `research/community-frontier1094-audit/INDEPENDENT1094.json` digit for digit.
- The diagnostic overestimates the exact root by about **0.30%** on the
  complex ledger and **0.29%** on the bit ledger at the current small savings:
  it is nearly sharp here, and safe as a screen in this regime.
- The ledger aggregates are reconstructed from the published histograms and
  checked against the coverage identities: complex `D = 73W − Σ n_r r =
  W − 64N = 5,120` (which also re-derives `W = 14,336` from the histogram and
  `N = 144`), and bit `D = 64W − Σ n_r r = T(2Kv − L·cst) = 32(2·4·111 − 9·63)
  = 10,272`.
- **Screening extremum.** If a repacking kept `m`, `W` and the rank mass and
  moved fractional rank mass up to the halving-guard cap (`m² > 2r²`, i.e.
  `r ≤ 51` for `m = 73` and `r ≤ 45` for `m = 64`), `D/E` could rise to about
  0.0137 (complex) and 0.0161 (bit). Both exceed the `1/99 ≈ 0.010101`
  planning target, so the `D/E` screen alone does **not** exclude target-scale
  gain from repacking; that needs the exact moment plus a coverage/realizability
  argument. For the complex local word that argument exists: the packing
  ceiling of
  [PR #1240](https://github.com/CrocSwap/integer-mult-bounds/pull/1240)
  (0.001690054109089 for the fixed local word, with idle-mass optimization)
  supersedes the per-histogram ceiling above and already rules out the target
  there. The bit word has no such realizability analysis; its question is open.

## Method and independence

`verify.py` imports nothing from the repository's retained engines
(`moment.py`, `base_two_moment.py`, the atanh prime chain of
`research/pending-claims-independent-pricing`, or the Mercator/base-two
transcriptions in `research/community-batch970-audit/submitted/957/`). Exact
rational arithmetic throughout; every enclosure comes from an explicit
inequality, and no floating point is used.

- `ln` is enclosed by **rational square-root bisection**: `x^(1/2^k)` is
  bracketed by repeated integer square roots on a `2^-320` dyadic grid
  (`k = 112`), then `ln(1+u)` is bracketed by `u − u²/2 ≤ ln(1+u) ≤ u`.
  This shares no series with the three retained log engines.
- Independent cross-check: `ln` by **bisection inverting a certified Taylor
  exponential**. Both methods must agree on every `ln(m/r)` used.
- `exp` is a Taylor partial sum with an explicit rational geometric tail bound
  (order 48; the largest exponent used in the bill is `a·ln 73 < 0.0073`, tail
  below `10^-150`). This matches the standard approach of the retained engines
  and is disclosed as such.
- Positive fixtures: the exactly solvable single-rank ledger `H={1:1},
  m=2, W=1`, whose root is exactly `a* = 1 < 1/ln 2 = D/E`; agreement with the
  recorded residual intervals; and the reconstructed ledger identities.
- Semantic failure controls, each required to be rejected: tampered assembly
  pin; bit ledger priced at the wrong width `m = 73`; a one-count histogram
  mutation that breaks the complex coverage identity; a child rank outside
  `(0, m)`; a zero-deficit ledger; claiming the endpoint two grid steps up as
  accepting; doubling the bit surcharge (breaks acceptance); negative surcharge
  in the diagnostic.

## Limits

- The paid profiles are taken from the published ledgers
  (`ASSEMBLY.json` `complex_profile`; `EXPECTED.json` `nine.profile`, pinned by
  the git blob recorded in the assembly's `bit_supplier` block). This package
  does not rebuild either word from its original operations; that reconstruction
  exists for the complex owner map through the audits composed in
  `research/community-batch1099-audit/check_frontier1094.py`, but not in this
  package.
- The conservative (surcharge-on-complex) endpoints of `ASSEMBLY.json` are not
  rechecked here.
- `D/E` bounds the root of one fixed histogram. It is not a repacking bound and
  not a realizability statement (see the screening extremum above).
- Nothing here verifies the inherited all-size/compiler, common-label/
  mutable-source realization, whole-call hosting, precision/tape, analytic
  transfer or bit H1–H5 obligations. This is not a multiplication theorem.

## Reproduce

From the repository root (Python 3.10+, standard library only, seconds):

```sh
python3 -B research/selected-suppliers-de-diagnostic/verify.py
python3 scripts/research_package.py --package research/selected-suppliers-de-diagnostic --check-only
```

Observed: `PASS_INDEPENDENT_DE_DIAGNOSTIC`, 12 controls. Machine-readable
output: [RESULT.json](RESULT.json).

## Open next questions

- **Bit-word realizability ceiling.** Question: does any repacking of the
  PR589 bit word's rank mass under its own coverage law stay below `1/99`?
  Why it matters: the bit side is currently non-binding, but the screening
  extremum (0.0161) shows the `D/E` screen alone cannot settle it. First step:
  adapt the idle-mass/coverage-law argument of
  [PR #1240](https://github.com/CrocSwap/integer-mult-bounds/pull/1240)
  to the bit coverage identity `D = T(2Kv − L·cst)` and the 32-replica
  template. Blocker: the bit word's admissible idle inventory and hosting
  constraints are not yet written as a local profile law.
- **Ledger reconstruction for the bit supplier.** Question: can `nine.profile`
  be rebuilt from the original gate operations of the pinned
  `tune/bitE8mut-p111-tuned.json.gz` word rather than taken from EXPECTED.json?
  Why it matters: it would close the last aggregate the selected assembly
  trusts without a from-operations audit. First step: compute the per-frame
  transition ranks of the word file and compare against `word.local_histogram`
  and `nine.profile`. Blocker: the paid-rank charging convention lives in the
  supplier's own checker, so a code-disjoint restatement is a substantial
  piece of work.

## Credit

Prepared by Navinor (with help from opencode). Predecessor credit: the pricing
model and the `a < D/E` diagnostic are Douglas Colkitt's (autoresearch.md,
`research/pending-claims-independent-pricing`); the complex ledger is Rohan
Arun's #1094 construction on Jeremy Kothe's packing chain, audited by Josie
Elliston and Sagar Thakrar; the bit supplier is the [PR 589](https://github.com/CrocSwap/integer-mult-bounds/pull/589)
by DreamingOfClouds / [PR 555](https://github.com/CrocSwap/integer-mult-bounds/pull/555)
by eumemic lineage
(with their credited predecessors, retained unchanged by the selected record); the
fixed-word packing-ceiling lineage (including
[PR #1240](https://github.com/CrocSwap/integer-mult-bounds/pull/1240)) is
static44, PR525, PR643 and the author of that PR. Substantial AI assistance
is disclosed: with help from opencode.
