# Complete four-class guard frontier for the mixed caller

The exact PR6398 mixed caller has **61 componentwise minimal integer guard
allocations** for PR6473's sufficient field-error envelope. A dyadic bound
proves that every minimal allocation lies below exponent39; the actual largest
minimal exponent is16. The cutoff is proved, not chosen experimentally.

The full frontier supports any increasing precision tariff. For the declared
error-output digit volume, the optimal policy changes at three exact rational
thresholds. In scalar/LOCAL/QUERY/idle order, the four policies are
`(9,8,9,9)`, `(10,7,7,7)`, `(11,6,7,7)` and `(13,6,6,7)`.

Read [PROOF.md](PROOF.md), [guards.py](guards.py) and the complete certificate
in [RESULT.json](RESULT.json). This is an optimum for the inherited sufficient
envelope and a stated tariff. It is not the true physical precision optimum
or a new kappa.

## Scope and evidence

The source has 34 fields and 570 events. All four coefficient maxima occur
in field0, so one inequality covers all output rows. Exact source regeneration,
two different-coordinate frontier enumerations, all 244 failing immediate
neighbors, 84 microdomains with 109,525 tuples, exact tariff intervals/ties,
128 additional tariff vectors and source/invalid controls pass.

The complete compatible-normalizer error-site meter gives field-equivalent
weights `(397,36,17,30)`. At native-to-ordinary digit prices1,10,100, the
optimal volumes are4284,9780,57961, compared with uniform nine's4320,11043,78273.
These are logical digit-volume comparisons. They do not include a physical
route, conversion, range, cleanup or accelerated recursive tariff.

PR6510's normalizer clarification is retained: the four half-field operations
require a compatible translation pair. For arbitrary order-four Q, the
completed-normalizer defect bound is a separate input premise. The older
mixed caller is not selected PR6030. All five framework assumptions remain.

## Reproduce

```sh
python3.12 -I -Werror -B research/mixed-caller-guard-frontier/verify.py
python3.12 -I -O -Werror -B research/mixed-caller-guard-frontier/verify.py
python3.12 -B scripts/research_package.py --package research/mixed-caller-guard-frontier
```

Only the standard library is required. Exact source bytes and notices are
retained under `inputs/` and pinned in [SOURCES.json](SOURCES.json).
There is no external runtime input.

## Open next questions

Which native backend realizes the four absolute field tolerances and what is
its actual cost as a function of each guard? Bind one exact backend, including
coordinate count, grids, conversions and cleanup, then minimize that tariff
over the retained frontier. An allocation alone does not supply the backend.

Can event-specific precision improve this classwise envelope? Extract every
suffix error column and retain all output inequalities. The four-class result
does not solve that larger integer problem or the exact physical error model.

## Credit

New finite bound, frontier, tariff proof and checks: Ali Romman with substantial
OpenAI Codex assistance; no subagents. Credit Ali Romman PR6473/6477 and
PR6398/6348, ToikY PR6510/6433, Cinna Davis's native interface and all retained
native/compiler authors. PR6473 owns the error envelope and nine-uniform-bit
theorem. PR6477's two-rate word remains separate. Classical product order,
precision allocation and affine tariff comparisons retain credit. Original
source proof/README files retain their notices. New work is Apache-2.0.
