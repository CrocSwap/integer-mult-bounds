# Complete classification at the seven-image endpoint

Every complete binary pattern-dimension-five pool with no matrix unit and
irreducible joint-image dimension seven has the known two-block form: two
disjoint normal triples and one link `(h+a)(h+b)^T`, where h is the sum of
the two hubs, a,b use fresh coordinates and `a dot b=1`.

The complete pool has exactly seven projectors. In a basis of its joint
image, every such action is six coordinate projectors and the all-one
seven-by-seven matrix. The normal form permits arbitrary fresh supports;
it is not a count of coordinate-permutation orbits.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json), and
[TASK.json](TASK.json). This closes question 2 of
[PR #7281](https://github.com/CrocSwap/integer-mult-bounds/pull/7281).
The new proof forces the two blocks for an arbitrary complete pool. The
earlier construction and the fixed-block link classification retain their
source credit. No irreducible image-basis subcollection is assumed.

With CPython 3.12 and its standard library, from the repository root:

```sh
python3.12 -I -W error -B research/no-edge-dim5-extremal-classification/verify.py
python3.12 -I -W error -B -O research/no-edge-dim5-extremal-classification/verify.py
python3.12 -B scripts/research_package.py --package research/no-edge-dim5-extremal-classification
```

Expected markers:

```text
PASS_NO_EDGE_DIM5_EXTREMAL_CLASSIFICATION
PASS_REGISTERED_RESEARCH_PACKAGE
```

The verifier checks all 40768 rank-one idempotents at widths seven and eight.
Three stated link domains contain 30679 candidates and 30376 distinct
unit-free spaces, with distinctness counted within each domain. Raw scans
and separate pattern lifts give the same complete pools. Every excluded
space has an exact invariant-subspace witness. The small normal-form lemma,
triple-plus-quad cases and prior positive/extra-pool controls also pass.
The finite domains support the written all-width reduction; they are not
an exhaustive search over all ambient coordinate embeddings.

No new kappa, paid BIT word, native operator or complete invoice is supplied.
The selected frontier and all five assumptions remain unchanged. Full
predecessor scientific replays, selected cold replay, Lean and Docker were
not run. The listed predecessor witnesses are rechecked. Independent human
and formal-kernel review are unclaimed.

## Open next questions

Realize the classified action in a legal paid BIT word, with the required
relation, cube-span and coordinate-call reduction and complete invoice.
Another search for a fresh-factor link in these two blocks will not supply
that missing word-level interface.

Prepared by Ali Romman with substantial OpenAI Codex assistance. New work is
Apache-2.0. See [CREDITS.md](CREDITS.md).
