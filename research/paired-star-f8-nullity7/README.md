# One F₈ nullity-7 class of two thin maps

## Scope

Same g=3, d=2 paired-star full-call contract as PR #5747: twelve F₂ resolutions, six full calls, and 720 orders. Exactly two thin maps. This package takes one affine class, the lexicographically first consistent gap pair of F₂-nullity 7, and asks whether its scalar extension to

F₈ = F₂[x]/(x³ + x + 1)

contains a point of rank sum 6 or 7.

The selected frontier stays κ = 781451/250000000. This is not a census of every F₈ class, and it does not reopen the partial F₄ census.

## Result

The class is resolutions (0, 0, 3), permutation index 4, gaps 2 and 5. Chronological order, rightmost factor first, is calls 1, 2, 0, 3, 4, 5. Nullity is 7. The two matrices are the seven-parameter shape in [PROOF.md](PROOF.md), and they differ by the same rank-4 star as the F₄ census.

Over every field of characteristic 2, every point of this shape has rank sum at least 8. The argument is a column partition of Zh and a 6×6 minor of Zg. It is a proof for this affine space, not an unrestricted nonexistence claim. The bound is attained at coefficient tuples (0,0,0,0,0,0,0), with ranks 4 and 4, and (0,0,0,0,0,0,1), with ranks 6 and 2.

The same shape over F₈ has exactly 8⁷ = 2,097,152 points. An exhaustive enumeration finds minimum 8, exactly two points at 8, and none below. The F₄ points of the same class, 4⁷ = 16,384 of them, also have minimum 8. The C enumerator and an independent Python Gaussian elimination agree on the F₈ checksum and histogram. That enumeration is a finite check of one field. The proof is what covers every characteristic-2 field.

## Reproduction

From the repository root, with Python 3.12 and gcc:

```sh
python3 -B research/paired-star-f8-nullity7/verify.py
```

The command checks the field, the block-rank formula, and the load-bearing constant ones, compiles `search.c`, and reruns the class derivation and both enumerators. It prints `PASS_PAIRED_STAR_F8_NULLITY7`.

## Open next questions

The structured questions are in `TASK.json`.

The useful next step is the next small-nullity class on this same contract, over F₈. The column partition used here is special to this shape. The capped F₄ classes are a different unfinished search and are not settled by this proof.

## Credit

The contract and the rank floor are PR #5747. The F₂ two-map census is `research/paired-star-two-thin-rank` (upstream PR #6940). The partial F₄ census that left a small-nullity F₈ class open is upstream PR #7006, fork commit `8889385a5bbe64df6f1378047b35d89e1aea355c`.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Independent human review and a proof-assistant proof are unclaimed.
