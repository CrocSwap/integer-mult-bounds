# Executed validation

Author-side validation on 2026-11-05 Asia/Shanghai (2026-11-04 UTC),
macOS arm64, CPython 3.12.13. No external scientific review is implied.
Canonical base 7c49fe32c55de02c2c873655c804b16e4c3fef0a and source PR6702
head edd6a37a9ff87b254fb7466184348d1432d0c8c0 were refreshed unchanged
before submission.

## Complete source and candidate runs

```sh
python3.12 -I -B research/p104-common-idle-double-retirement/verify.py --write-result
python3.12 -I -O -B research/p104-common-idle-double-retirement/verify.py
```

Both exited0 with
`PASS_CONDITIONAL_KAPPA_00330420_COMMON_IDLE_RETIREMENT`.
The final normal regeneration took 105.73s wall time and optimized
read-only replay108.31s on this machine. An earlier complete construction
run also passed before adding the signed-comparison/scalar integration.
The final normal run explicitly regenerated only the new RESULT.json;
the optimized run recomputed and compared that entire receipt exactly.

Both final runs executed every retained source check and saved-receipt
comparison unchanged, including source construction/zero-scratch controls,
800 native columns and 640,000 coefficient positions, absolute native
phases, owned lifetimes, old caller/retirement/compiler prices and
physical maps. The new checks then covered:

- The64 exact root character/stage cases and common two-coordinate idle
  block, with native basis maps checked over rational matrices.
- The34-input unretired caller and 35-input final caller, all 1,225 final
  forward and reverse-row coefficient positions.
- Both input and cut dual pairings, `Pd=Sb` and `aP=Sc`, and the ordinary
  G/J row/column identities at actual cut 353.
- All7,488 new physical main contacts,53,248 central-square columns,
  all 35×104 main target phases and every paired/individual whole idle.
- The complete event/formula invoice, all 563 native helper credits,
  independent fresh field34 and zero rank-mass delta in the exact gain.
- Both rational moment engines, the strict raw bracket, unique-crossing
  derivative,11/12 completion, explicit compiler rank and all 54+4 outer
  predicates. The old12/13 completion is explicitly rejected.
- Actual per-instruction scalar work/height, including coefficient 37,
  all 110 LAMBDA operations, and the new252,020,208 ordinary upper bound.
- Missing native/query/idle/normalization/basis gates, missing handoff or
  return, repeated fused axes, an unearned fresh central target, an unpaid
  native job and extra productive credit are rejected.

Full run logs are retained in `validation/normal.log` and
`validation/optimized.log`.

## Separately written logical engine and package pins

```sh
python3.12 -I -B research/p104-common-idle-double-retirement/independent_word.py
python3.12 -I -O -B research/p104-common-idle-double-retirement/independent_word.py
python3.12 -B scripts/research_package.py --package research/p104-common-idle-double-retirement --check-only
```

Both independent logical runs exited0 in about 0.1s and matched the complete
INDEPENDENT.json receipt. This standard-library implementation imports none
of the author's constructor, replay or algebra modules. It checks all 35
independent columns and the cut identities directly, plus five rejected
controls. It does not independently replay native phases. It was written
by a parallel AI agent in the same author session, not an external reviewer.

The metadata/provenance check returned
`PASS_PACKAGE_METADATA_AND_PINS (not a mathematical acceptance check)`.
All17 frozen top-level PR6702 files match both SHA256 and original Git blob
pins; the source verifier authenticates the nested runtime archives.

## Unrun or retained obligations

The selected frontier was not edited or cold-replayed. No global native
optimization, full all-size framework proof, Lean theorem, Docker build,
materialized winning compiler word or practical multiplication benchmark
was run. The same five framework assumptions, including native lifting,
movement/precision/tape rates and analytic recovery, remain explicit.
CI and archive integration, if obtained later, are separate from scientific
admission.
