# The next F₈ nullity-7 class of two thin maps

## Scope

Same g=3, d=2 paired-star full-call contract as PR #5747: twelve F₂ resolutions, six full calls, and 720 orders. Exactly two thin maps. PR #7028 settled the lexicographically first consistent gap pair of F₂-nullity 7, resolutions (0, 0, 3), permutation index 4, and gaps 2 and 5. This package takes the next distinct affine class in that same order and asks whether its scalar extension to

F₈ = F₂[x]/(x³ + x + 1)

contains a point of rank sum 6 or 7.

The selected frontier stays κ = 781451/250000000. This is not a census of every F₈ class, and it does not reopen the partial F₄ census.

## Result

The class is resolutions (0, 0, 3), permutation index 8, and gaps 2 and 5. Chronological order, rightmost factor first, is calls 0, 3, 1, 2, 4, 5. Nullity is 7. Permutation index 5, calls 2, 1, 0, 3, 4, 5, has the same reduced basis as permutation index 4, so it is the settled class again and is not counted here.

The two matrices are the seven-parameter shape in [PROOF.md](PROOF.md). They still differ by the rank-4 star, but the free support is not the settled one. Rows 2 and 5 share columns {2, 5}. Rows 3 and 4 are separate diagonal entries. The column partition used for permutation 4 does not describe this shape.

Over every field of characteristic 2, every point of this shape has rank sum at least 8. The argument is the column split of Zh above, a 4×4 minor of Zg at c₆ = 0, and a four-vector reduction at c₆ = 1. It is a proof for this affine space, not an unrestricted nonexistence claim. The bound is attained at coefficient tuples (0,0,0,0,0,0,0), with ranks 4 and 4, and (0,0,0,0,0,0,1), with ranks 6 and 2.

The same shape over F₈ has exactly 8⁷ = 2,097,152 points. An exhaustive enumeration finds minimum 8, exactly two points at 8, and none below. The C enumerator and an independent Python Gaussian elimination agree on the checksum 3440682239519878741 and on the histogram. PR #7028 records checksum 6631801623909619557 for the settled class, so the two censuses are not the same multiset of ranks. This enumeration is a finite check of one field. The proof is what covers every characteristic-2 field.

Evidence class: a scoped proof for one affine space, plus an exhaustive finite census of that space over F₈. The census domain is finite, the loop runs through every coefficient tuple, and both implementations count 8⁷ points. It is not a heuristic search. It does not speak for the classes after this one.

## Reproduction

From the repository root, with Python 3.12 and gcc:

```sh
python3 -B research/paired-star-f8-perm8-nullity7/verify.py
```

The command checks the field, the block-rank formula, the c₆ = 1 reduction, and the load-bearing constant ones. It derives the class by the lex scan, compiles `search.c`, and requires the two enumerators to agree. It prints `PASS_PAIRED_STAR_F8_PERM8_NULLITY7`.

`search.c` also checks the diagonal commuting-control identity used by the F₄ census. That identity tests the polynomial product. It is not a point of this class.

## Open next questions

The structured questions are in `TASK.json`.

- Does the next distinct nullity-7 class after resolutions (0, 0, 3), permutation 8, and gaps (2, 5) have rank sum at least 8 over every field of characteristic 2? The split of rows {2, 5} onto columns {2, 5} is special to this shape. The first step is to continue the lex scan past permutation 8 and read the next support. Nothing external blocks that step.
- Does one nullity-8 class on this same contract have an F₈ point of rank sum 6 or 7? Its point count is 8⁸, so this direct enumeration does not fit, and neither seven-parameter shape applies.

## Credit

The contract and the rank floor are PR #5747. The F₂ two-map census is `research/paired-star-two-thin-rank` (upstream PR #6940). The partial F₄ census is upstream PR #7006. The lex-first nullity-7 class, and the scan this package continues, are upstream PR #7028, fork commit `b1d471c158d3b71e79464752219f52e1eff2d95d`.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Independent human review and a proof-assistant proof are unclaimed.
