# A complementary-plane rule for the seven binary Schur states

This is an independent finite check of the seven ordered residual pairs in
[PR #4689](https://github.com/CrocSwap/integer-mult-bounds/pull/4689), pinned at
`3a72fbad148294aa9ca7f900a48dbb10e64232be`. It recovers every remaining
guard-depth count and stabilizer without enumerating GL₄(F₂). The result is a
transition rule for **these supplied representatives**, not an independent
classification of the seven orbits or the 172 admitted first-pivot split pairs.
There is no supplier admission or new κ.

## Rule and proof

Let `S,T` act on `V=F₂⁴`. Every ordered basis `(x,y,w₁,w₂)` gives a unique
decomposition `V=U⊕W`, where `U=span(x,y)` and `W=span(w₁,w₂)`. Conversely, each
ordered complementary pair of two-planes has six bases of `U` and six bases of
`W`. There are 35 two-planes, 16 complements per plane, hence
`35·16·6·6=20,160` bases. This partitions GL₄ without listing its elements.

For `U⊕W`, let `π:V→U` be projection along `W`. In basis `(x,y,w₁,w₂)`, the
leading two-by-two block of a map `A` is the matrix of `πA|U` in `(x,y)`.
Its determinant is one precisely when `πAx` and `πAy` are distinct nonzero
vectors. Its leading one-by-one entry is one precisely when
`πAx∈{x,x+y}`. Both statements follow by writing the two projected vectors
in the basis `(x,y)`; they require no idempotency assumption.

Therefore, for each `(U,W)` and each of the six ordered pairs `(x,y)` of
distinct nonzero vectors of `U`, the simultaneous first guard is
`πSx,πTx∈{x,x+y}`. The second guard additionally requires both projected
restrictions to be invertible. Multiply each successful choice by six for
the possible ordered bases of `W`. Summing over 560 decompositions yields
the number of bases reaching each depth. The rule is invariant under
simultaneous conjugacy: a change of coordinates bijects the complementary
plane pairs and preserves these projection tests.

All supplied representatives have `S=diag(0,0,1,1)`. A matrix stabilizing
`S` must preserve `ker S` and `im S`, so it is a two-by-two block diagonal
pair in `GL₂(F₂)×GL₂(F₂)`. There are only 36 such pairs. Filtering them by
`KT=TK` gives stabilizer sizes `36,4,1,1,4,4,1`. Dividing the basis counts
by each size gives orbit-element depth counts, rather than counting the
same orbit element repeatedly. The script checks the published values:

| State | Stabilizer | Depth 0 | Depth 1 | Depth 2 |
|---:|---:|---:|---:|---:|
| 1 | 36 | 280 | 180 | 100 |
| 2 | 4 | 3192 | 1380 | 468 |
| 3 | 1 | 15120 | 4674 | 366 |
| 4 | 1 | 14448 | 4896 | 816 |
| 5 | 4 | 3192 | 1380 | 468 |
| 6 | 4 | 3528 | 1242 | 270 |
| 7 | 1 | 14448 | 4896 | 816 |

Using PR #4689's **imported** split-pair multiplicities `1,3,126,18,3,3,18`,
the independently recovered depth-two basis counts sum to 93,564 complete
headers. This agrees with its reported fraction `2599/277760`. Agreement is
an audit of the continuation law and arithmetic; the imported multiplicities
and original all-header denominator are not independently reproved here.

## Reproduce

Python 3.10 or newer, standard library only:

```sh
python3 -B research/cbc3b1759ddd5fe5c461c509fecfae56/plane_count.py
python3 -O -B research/cbc3b1759ddd5fe5c461c509fecfae56/plane_count.py
```

Both end with `PASS_PLANE_TRANSITIONS full_guard_headers=93564
decompositions_per_state=560 no_GL4_enumeration`. The checker has no writes,
network access or predecessor imports. Its two-plane and complement totals,
seven stabilizers, all depth counts, and aggregate are explicit failures even
under `-O`. It does not enumerate GL₄, GL₅ or the first-pivot split pairs.

## Open next questions

Derive the first-pivot **state multiplicities** from image/kernel data without
enumerating the 496 split pairs, then connect this rule to a scalable state
recursion. The present 560-decomposition finite sum should be replaced by a
closed orbit or intersection formula before extrapolating to larger fields or
dimensions. Neither this binary count nor PR #4689's table prices a production
header, dirty restoration, stock, dispatch or a complete consumer.

Credit: Mihir Srivastava's PR #4689 supplies the seven representatives,
split-pair multiplicities and published counts. Its README credits ssafwann's
PR #4678, Nick Petalas's Schur/header work, Ryanson Jonathan's full-guard
census, lee-phys's dimension work and the normalizer lineage. This independent
rule was prepared by Sagar Thakrar with substantial OpenAI Codex assistance.
Apache-2.0.
