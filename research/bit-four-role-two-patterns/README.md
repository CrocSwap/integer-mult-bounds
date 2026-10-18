# Four-role two-pattern pools: all are reducible, but 72 lack a full flag

**Finite exact scalar classification; no new supplier or kappa.** Among the 120
rank-one idempotents of M4(F2), 104 distinct off-diagonal patterns are nonzero.
They generate 4,964 distinct two-dimensional pattern spaces. Form each pool
from **all projectors with a nonzero pattern in the space**, excluding coordinate
projectors. Exactly 4,892 pools have a common complete binary flag. The remaining
72 are reducible, have common invariant subspaces in dimensions1 and3, and have
no invariant plane. There are no irreducible pools.

Under coordinate permutations and transpose there are148 orbits. The72 exceptions
have just two orbits, of sizes24 and48. Their packed row-major matrix-pattern
representatives are `(2,336,338)` and `(2,2512,2514)`. In each case the third
nonzero vector is **not** an off-diagonal pattern of a rank-one idempotent.
Each exceptional pool contains three projectors, because one realized pattern
has two lifts. The certificate retains every orbit and classification.

## Why the domain distinction matters

[PR1733](https://github.com/CrocSwap/integer-mult-bounds/pull/1733), inspected at
`01ac3f397eaaa9f7a72ecafc7f0fbf128571424a`, enumerates196 planes whose **three**
nonzero vectors are all realized. It finds176 with a common coordinate order
and20 with cyclic union. We independently show that **all196 have a common
complete binary flag**, including those20 cyclic-coordinate cases. Explicit
flags for all196 are supplied in `CERTIFICATE.json`; they are actual sets of
binary vectors, so they can be checked without finding a change-of-basis matrix.
The exact predecessor certificate is retained with Git-blob and SHA-256 pins in
`RELATED-SOURCE.json`. Its20 exceptions are compared after converting its
12-edge encoding to our16-bit row-major encoding.

The larger4,964-space domain allows the third pattern to be unrealized: two
independent occurring patterns still span a two-dimensional space. Its72
exceptions are all absent from the196-plane domain. Neither count contradicts
PR1733. Its fixed15-address chronological screen is not replayed or challenged.
We also reproduce the three-register predecessor's129spaces,123full-flag pools
and6irreducible exceptions. Its argument and PR1456's explicit next question
motivated this extension; we do not claim the pattern-space method as new.

## Completeness and evidence

Enumerate all nonzero x,y in F2^4 with y^T x=1 and form xy^T. Every rank-one
idempotent has this form, uniquely over F2. Remove diagonal entries, pair every
two distinct nonzero patterns and canonicalize {p,q,p+q}. This covers precisely
all two-dimensional spaces spanned by occurring patterns. For each pool, inspect
all65proper nonzero binary subspaces and all315complete flags. A separate
invariant-subspace chain dynamic program agrees on full-flag existence.

A second dense tuple implementation enumerates all65,536 binary4x4 matrices,
selects rank-one images by image cardinality and idempotence by actual action,
and independently rechecks every projector/subspace invariant relation. Tests
include the W3 known census, a triangular positive pool, a nonflag active cube,
and the distinction between reducibility and a full flag. Assertions and
floating-point arithmetic are not used. Source inputs are byte/Git pinned.

This result concerns scalar pools, not realized rational frame relations.
Coordinate projectors with independent addresses can intervene chronologically;
the pool's flag does not automatically survive those gates. No universal
four-register or two-relation rank floor follows here. No native compiler,
hosting, precision, cold supplier replay or new multiplication exponent is claimed.
The selected baseline still has the complex primitive binding.

## Reproduce

```sh
python3 -I -O -B research/bit-four-role-two-patterns/verify.py
python3.12 scripts/research_package.py --package research/bit-four-role-two-patterns
```

Expected: `PASS_FOUR_ROLE_TWO_PATTERNS` with spaces4964,flagged4892,
no_flag_reducible72,irreducible0. Runtime is bounded by120seconds; standard
library only. `--write` regenerates the certificate; ordinary replay compares it.

## Open next questions

Can either exceptional orbit participate in a legal two-relation word? Start
from the two recorded representatives, retain the missing third pattern and
impose exact relation signatures and formal endpoints. The blocker is realizing
rational rank-one frames with useful rank-saving targets and complete costs,
not merely producing another finite scalar census. TASK.json records this handoff.

## Credit and scope

Credit to Ali Romman and the retained bit-three-register-lower-bound source,
PR1456's arbitrary-role one-relation argument and next question, and the author
of PR1733 (OpenAI Codex) for the196-plane coordinate-order census and fixed-word
screen. Prepared for woklerx with substantial OpenAI Codex assistance. Apache-2.0.
No independent human review is claimed. Overlap checked486open PRs and471board
records at2026-10-14 11:13-11:15UTC, complete pagination; code diffs and arbitrary
closed work were not covered by that index. Exact1733sources were then inspected.
