# Sharp E8 A2 rank-five joint incidence 20

For the declared leading-one E8 labels R, any 27-line projective A2 fiber A,
and any ambient binary space V of dimension at most five,

```
|R intersect V| + |A intersect V| <=20.
```

The bound is sharp on full E8. This improves the sufficient 21 used by
[PR3257](https://github.com/CrocSwap/integer-mult-bounds/pull/3257).
For a piece, the two terms bound total support and singleton support in A.
Frame puncturing and deletion of one common support preserve this inequality.

PROOF.md gives the signed character-sum argument. Every fiber spans a binary
seven-space whose leading-one affine six-space has positive Gauss sum 8.
An inside support space contains at most ten roots. An outside support space
meets the fiber in at most eight points, and has at most 12 roots in total.
The latter global bound is the proof of
[PR3269](https://github.com/CrocSwap/integer-mult-bounds/pull/3269), recalled
in full at the required rank. The model binding checks all 3,360 large fibers
from all 1,120 A2 planes, so no inherited Weyl-transitivity premise is needed.
RESULT.json contains the exact receipts, a sharp ten-root witness and the
canonical 2,667-space histogram. A separate dense/norm implementation checks
all 80,730 five-label subsets of that fiber and its 216 equality closures.

## Reproduce

Use Python 3.12 and the standard library. From the repository root:

```sh
python3.12 -W error -B scripts/research_package.py --package research/e8-a2-joint-incidence20
```

The direct commands are:

```sh
python3.12 -W error -B research/e8-a2-joint-incidence20/verify.py
python3.12 -W error -B research/e8-a2-joint-incidence20/crosscheck.py
python3.12 -O -W error -B research/e8-a2-joint-incidence20/test_controls.py
```

They print `PASS_E8_A2_JOINT20`, `PASS_E8_A2_JOINT20_CROSSCHECK` and
`PASS_E8_A2_JOINT20_CONTROLS`. The registered runner also verifies metadata
and exact source pins. Direct replay authenticates a fixed three-row source
inventory and its allowed usages; changing the live geometry row to provenance
is rejected. Source mutation, missing/extra/duplicate inventories, malformed
hashes, a negative Gauss-sign counterexample and the sharp witness are controls.
Set `IMB_RUN_CACHE` to an external directory to keep transient control files there.

The only executable input outside this package is the pinned main-branch
`research/p112-root-simplex-exclusion/geometry.py`. Pending proof references
are exact commits and hashes in PREDECESSORS.json, not runtime dependencies.
The self-contained proof and direct replay need no pending Git objects.
CHECKS.json and REVIEW.json record the actual validation and review scope.

## Scope and sources

Canonical main 463113d675af7410ac91d53a4fed51ec6494eb9a, priority revision 6.
This is one narrow proof dependency and stronger inequality under the family
expansion gate. Whole-supplier source/frame/restoration/consumer costs remain
unknown and unchanged. It is not a new shortening threshold, literal caller,
full C5, decoder floor, supplier or kappa claim. The full E8 equality witness
does not assert sharpness after the fixed P112 puncture. Independent human
review, proof-kernel formalization, Lean, Docker and selected cold replay are
unrun. No historical global five-flat census is replayed.

Credit Nick Petalas's PR3257 and PR3269, David Arias's retained quadratic-model
work, DreamingOfClouds's PR3154 motivation, and the root-simplex/E8/P112 lineage
including joaqcoo. PREDECESSORS.json records exact reference bytes. Frozen
sources, shared tools and the selected result are unchanged. Apache-2.0.

## Open next questions

A separately normalized shortening argument can test whether incidence 20
closes its next common-support boundary. It must prove the normal-plane and
common-cut hypotheses itself; those do not follow from this binary lemma.
TASK.json gives its relevance, first check and blocker. This package starts
no second research round or construction expansion.
