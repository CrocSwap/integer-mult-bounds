# Independent audit of four helper-input lifts

This package checks the scalar schedule in Ali Romman's merged
[PR #6349](https://github.com/CrocSwap/integer-mult-bounds/pull/6349),
head `af7cb6c67f8fc7d82a2e4aee2dd2f07481bf6690`, archived on canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. It answers the review requested in
[discussion #1166 comment 19341394](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19341394).

No new kappa is claimed. The selected frontier stays
`781451/250000000`. The reported conditional value `0.003129111` is not
re-derived here.

## What was checked

On the pinned PR6314 source word and the pinned lifted word, a separate
replay agrees with the proof's local invoice:

- All 799 scalar columns of both words end at the identity. Owned lifetimes
  are 32 and peak ownership is 13.
- The only initial-chart changes are roles 496, 649, 663 and 508, from frame
  3 to frames 595, 597, 105 and 1093. Final frames are unchanged.
- Each input direction `h` has a unit primary coordinate, disjoint support,
  and an inverse `I - (h - e_p) e_p^T`. Replaying `h` through the source
  chronology reproduces the stated departure response.
- The new chart is contained in every nonzero departure frame of that
  response. Frame 1093, basis `[30, 42, 384]`, is the GF(2) span intersection
  of frames 118 and 733.
- The two dirty-carrier sandwiches leave the wide carrier short one primary
  input and the narrow carrier short half a primary input, including the
  intervening additions that do not use those carriers. The six trailing
  output additions are the inverse basis.
- Ten frame-3 reads of the four primaries are absent from the lifted word.
  Role 649 is injected into 198 at frame 597, and role 663 into 179 at frame
  105, with the stated carrier subtractions.
- Helper rank is `dim(final) - dim(initial)` off the 208 main roles. The four
  lifts change ranks `9→8`, `9→8`, `9→8` and `9→6`. The histograms therefore
  move by paid `H1+H2+H3+2H4-4H5` and productive `H6+3H8-4H9`. Scalar
  allowances are 127042 and 127088. Paid rank masses are 5952 and 5946.

Four mutations fail closed: deleting the first carrier subtraction, deleting
one output correction, reversing the 649 injection, and replacing frame 1093
by `[1, 2, 4]`.

## What was not checked

Native Pauli images, absolute phases, the physical caller, both rational
price engines, the compiler threshold and the 58 outer predicates were not
run. The five framework assumptions remain. This audit does not accept
PR6349 and does not cover PR6350 or PR6353.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3 -W error -B research/p104-input-lift-direction-audit/verify.py
python3 -O -W error -B research/p104-input-lift-direction-audit/verify.py
python3 scripts/research_package.py --package research/p104-input-lift-direction-audit --check-only
python3 scripts/research_package.py --package research/p104-input-lift-direction-audit
```

The direct verifier hashes the three pinned inputs and does not need Git or
network. The registered runner also checks provenance blobs. Each scientific
command finishes in a few seconds. Status:
`PASS_P104_INPUT_LIFT_DIRECTION_AUDIT`.

## Open next questions

The signed Pauli image of one changed helper normalizer is still unchecked.
That is the smallest native gate for this word; the predecessor checker and
`native_all_columns` are the blocker. Separately, PR6353's later word needs
its own initial-frame reading before these four ranks are reused. [TASK.json](TASK.json)
records both first steps.

## Credit

Audit: unpaidmoon, with substantial Cursor Grok assistance. Apache-2.0.

Construction and author checks: Ali Romman, with substantial OpenAI Codex
assistance, in PR6349. Source word: DreamingOfClouds, with Claude Opus 5.5
assistance, in PR6314, retaining PR6167. The frame and endpoint rules follow
the published scalar model of that chain; this package reimplements them and
does not vendor the checker.
