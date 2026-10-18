# Two temporal gauges on a shared complex ADD

**Finite scalar construction; no new kappa.** This result composes two exact
single-helper dyadic schedules, for L348 and L359, on the selected PR1263
218-helper word. Their schedules are nonzero at the same ADD, so the exact
coefficient cost has a coupled correction.

## Result

The separately optimized schedules save 161 and 242 real primitives per
invocation. Their naive sum predicts 403 real primitives. At shared ADD 24336,
the two exponent shifts interact: separate coefficient changes cost -1 and -4
real primitives, while the combined change costs -2. The shared coefficient
therefore adds back exactly 3 real primitives. The composed word saves **400
real / 800 complex primitives per orientation** over PR1263's static word.

| Orientation | PR1094 original | PR1263 static | L348+L359 temporal | Increment over PR1263 |
|---|---:|---:|---:|---:|
| Forward | 149,002 | 136,002 | 135,202 | 800 |
| Backward | 149,018 | 136,018 | 135,218 | 800 |

All 54 inserted scales (entry, transitions and any necessary terminal
restorations) are charged. The exact full invoice preserves the paid recursive
profile, charged 192-bit payload, and
52/68-bit positive prefixes. Both orientations preserve the complete formal
map on all 712 columns and leave every non-scalar event unchanged. The total
scalar saving against the PR1094 original is 13,800 complex primitives per
orientation.

This is a feasible composition of two separately optimal one-coordinate
schedules, not a jointly optimized two-coordinate schedule. No new kappa,
selected-supplier adoption, native/hosted admission, or multiplication theorem
is claimed.

## Assignment and overlap

- Track: Complex supplier; OS seed 28; exact base
  `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
- PR #1369 checks one-coordinate temporal schedules on all 19 eligible helpers
  with zero static gauge. PR #1310 checks all two-coordinate **constant**
  gauge moves and explicitly excludes phase-varying composition. This package
  tests a seed-selected pair of phase-varying schedules at a shared ADD.
- The final overlap refresh found PR #1376's L248/L253 temporal composition;
  those supports are disjoint. PR #1380's newer shared-ADD result optimizes a
  different pair, L225/L350, and tests 16 pairs all containing L225. Its
  certificate includes L225/L348 but not L348/L359. This package adds a
  distinct zero-static pair: it composes exact separately optimized L348/L359
  schedules and prices their +3-real shared-ADD correction. It does not claim
  the joint-optimality result established for PR #1380's own pair.
- Seed 28 indexes the two pairs whose one-coordinate minima both improve and
  are simultaneously nonzero at a shared ADD. It selects `(348,359)` at index
  `28 mod 2 = 0`. The initial index among all 171 pairs, `(288,491)`, had
  disjoint ADD sets; the evidence-driven pivot to the shared-ADD class makes
  the coefficient interaction test substantive.
- Other screened directions were the masked-decoder classes covered by
  #1212/#1213/#1224/#1226/#1236/#1304/#1320 and current discussion claims, and
  the helper-inventory coverage thresholds in #1348 and Discussion #1328.
- The pinned sprint coordination issue search found no open match; the local
  claim is in `CLAIM.md`.

The exact machine-readable schedules, invoices, column digests and control
results are in [`RESULT.json`](RESULT.json). The predecessor snapshots, Git
blob IDs, hashes, selected record and review are listed in `SOURCES.json`. The
exact PR1369 input code is vendored under
`vendor/pr1369/` with its source notices. Its one-coordinate optimizer is
replayed and compared to its pinned certificate before this composition is
priced.

## Reproduce

From the repository root, using the Python standard library:

```sh
python3 -I -O -B research/complex-temporal-pair-seed28/verify.py
```

Expected:

```text
PASS_COMPLEX_TEMPORAL_PAIR seed=28 helpers=348,359 shared_add=24336 cross=+3real saving=800complex/orientation controls=3 no_new_kappa
```

## Open next questions

Can a joint all-integer two-coordinate DP improve on the composition of
separately optimal schedules? That could price a better candidate at shared
ADDs rather than merely compose known one-coordinate minima. First step: derive
a proved finite two-dimensional exponent box from the dyadic ADD breakpoints
and the two restoration paths. The current contribution stops after one
seed-selected pair and makes no joint-optimality claim.

## Credit and disclosure

Credit Cinna Davis / @1337isnot1337's PR1369 single-coordinate temporal census,
Sagar Thakrar's PR1259 temporal-gauge method and PR696 lowerer, Philipp /
@mightyOil's PR1263 static word, and the retained PR1094/PR1161 lineage.
Credit bbMisk's PR1310 constant-pair stationarity result as the adjacent
predecessor, with its phase-varying exclusion retained. Credit PR #1376 and
Sagar Thakrar's PR #1380 for the concurrent distinct-pair and disjoint-support
comparisons documented above. Prepared by Cinna Davis with substantial OpenAI
Codex assistance for analysis, implementation, verification and writing. No
independent human review or subagents are claimed. Apache-2.0.
