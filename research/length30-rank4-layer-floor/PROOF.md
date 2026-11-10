# A rank-4 length-30 sojourn cannot have 16 layer-0 points

This note proves one size restriction. It does not decide whether a universal
length-30 word exists. The inherited gap `28 <= f(8) <= 32` stays in force,
and the selected exponent is unchanged.

The rank-at-most-2 obstruction, the rank-3 bent lower bound, and the 4+4
prefix-set obstruction are the length-30 sojourn package, upstream pull
request 6943. The rank-3 exhaustive blockage, and the pair floors 16, 15 and
12 at ranks 4, 5 and 6, are open pull request 7015. None of those arguments
is repeated here. Rank 5, rank 6 and length 28 are not examined.

## Statement

Work in the restored binary singleton model. Let a closed word of length 30
have a source of multiplicity 2 whose open sojourn uses exactly four other
sources. If the word is universal, the complementary layer has at least 17
distinct projections and the sojourn layer has at most 13.

In particular, inside the stated rank-4 window of 8 to 14 layer-1
projections, the complementary layer cannot have size 16. A sojourn with 14
layer-1 projections is therefore impossible, and every surviving sojourn in
that window has at least 17 layer-0 projections and at most 13 layer-1
projections.

## Model and normalization

Sources are the standard basis of `F_2^8`. Prefixes of a word are
`q_0 = 0` and `q_t = e_{w_1} + ... + e_{w_t}`. Restoration means `q_30 = 0`.
The word is universal when `P + P = F_2^8` for `P = {q_0, ..., q_29}`.
Addition is XOR.

Fix a multiplicity-2 source `α` and write `f < g` for its positions. Delete
coordinate `α`. The open sojourn `w_(f+1), ..., w_(g-1)` uses four other
sources. Those sources span a coordinate 4-flat `V`, the sojourn projections
`Q1` lie in one coset of `V`, and `Q1 + Q1` is contained in `V`. Universality
is equivalent to

```text
Q0 + Q1 = F_2^7,
(Q0 + Q0) ∪ (Q1 + Q1) = F_2^7.
```

Rotate the closed word so that one occurrence of `α` is the first letter, and
translate prefixes so that the prefix immediately before that letter is `0`.
The prefix before the first occurrence has `α`-bit 0, so the translation does
not swap layers. Differences are unchanged. After renaming the four sojourn
sources to `{0,1,2,3}` and `α` to `7`,

```text
0 ∈ Q0,  0 ∈ Q1,  Q1 ⊆ V = span{e_0, e_1, e_2, e_3}.
```

Write `F_2^7 = V × W` with `W` the complementary coordinate 3-flat. Both `Q0`
and `Q1` meet the identity coset of `V`, and `Q1` lies in that coset.

## The size window at rank 4

`Q1 + Q1` misses every vector outside `V`. Those 112 vectors are nonzero, and
each must lie in `Q0 + Q0`. At most `C(|Q0|, 2)` distinct nonzero sums are
available, so `|Q0| >= 16`. The same count is the pair floor recorded for
rank 4 by pull request 7015; the short derivation above is included so this
note does not depend on that program.

The two layers partition the 30 prefixes, so `|Q0| + |Q1| <= 30`. Every coset
fiber `S` of `Q0` must satisfy `S + Q1 = V`. Thus
`|S| >= ceil(16 / |Q1|)`, and `|Q0|` is at least eight times that quantity.
Write `m(|Q1|)` for that product. A pair `(layer-0 size, layer-1 size)` can
occur only when the layer-0 size is at least `max(16, m(|Q1|))` and the two
sizes sum to at most 30.

The verifier enumerates these necessary pairs. The only layer-1 sizes that
survive are `6` and `8, 9, ..., 14`.

- `|Q1| = 6` forces `m = 24`, hence `|Q0| = 24`. This case is outside the
  8-to-14 window in the stated first step, and it is not censused here.
- `|Q1| = 7` forces `m = 24`, and `24 + 7 = 31`, so it is impossible.
- For `8 <= |Q1| <= 14`, `m = 16`, so `|Q0| >= 16`.
- `|Q1| >= 15` forces the pair floor `|Q0| >= 16` to make the total exceed 30.

Pull request 7015 describes the rank-4 window as `8 <= |Q1| <= 14`. The
inequalities above also admit `|Q1| = 6`. This note uses the inequalities and
does not treat that extra case as excluded.

Now suppose `|Q0| = 16`. Then `|Q1| <= 14`, and `m(|Q1|) <= 16` forces
`|Q1| >= 8`. Every fiber therefore has size exactly two. The identity fiber
contains `0`, so it is `{0, d}` for some nonzero `d`.

The case `|Q1| = 14` is entirely inside this boundary: `|Q0| >= 16` and
`14 + 16 = 30`, so both sizes are exact and the fibers are the two-point
configuration above.

## The sixteen-point layer is an exact packing

Assume `|Q0| = 16` and every fiber has two points. Each fiber contributes one
unordered pair, and that pair has quotient difference `0`, so it does not meet
the complement of `V`. The remaining pairs are the cross pairs

```text
C(16, 2) - 8 = 112.
```

Every cross pair joins different cosets, so its sum lies outside `V`. There
are 112 such sums and 112 outside targets. A cover exists only when these
sums are all distinct.

Equivalently, for each nonzero `δ ∈ W` the four fiber pairs `{w, w+δ}` have
pairwise disjoint sumsets whose union is `V`. Two-point sets `A = {a, a+d}`
and `B = {b, b+e}` have `|A + B| = 4` if and only if `d ≠ e`. Both differences
are nonzero because the fibers are two-point sets. Therefore all eight
differences are distinct, and each four-point sumset is a coset of the
2-dimensional span of its two differences.

## Symmetry reduction

Let `A` be a linear automorphism of `V` with `A(d) = e_0`, extended by the
identity on `W`. It fixes `0`, preserves each coset of `V`, and preserves
sums. The image of the identity fiber is `{0, e_0}`. Every sixteen-point
configuration is equivalent to one whose identity fiber is `{0, 1}` when
vectors in `V` are written as integers `0, ..., 15`. The verifier checks that
each of the 15 nonzero vectors starts a basis of `F_2^4`, so such an `A`
exists for every `d`.

After this normalization the census domain is finite: the identity fiber is
fixed, and each of the other seven fibers is one of the `C(16, 2) = 120`
two-point subsets. That is `120^7` tuples.

## The census

Order the two-point subsets as `itertools.combinations(range(16), 2)`. The
search assigns fibers `0, 1, ..., 7` in that order, with fiber `0` fixed as
subset index `0`, the mask `{0, 1}`.

When fiber `t` is assigned, every earlier fiber `u < t` completes the pair
for `δ = u XOR t`. The search rejects the assignment unless that pair's
sumset has size 4 and is disjoint from the sumsets of pairs already completed
for the same `δ`. If all four pairs for a `δ` are complete and their union is
not `V`, the assignment is rejected.

This prune is sound. There are exactly four pairs for each `δ`. The partner
of `t` is unique, and the other three pairs lie among the remaining six
fibers. All three are already assigned if and only if `t = 7`. Thus the
cover test runs only when the direction is complete, while every collision is
rejected as soon as both of its pairs have been assigned. A tuple that covers
every direction survives every test. No surviving tuple exists.

The C program enumerates the pruned tree with incremental direction masks.
An independent Python enumeration recomputes each completed direction from
the fibers chosen so far. Restricted to second-fiber index `1`, it visits
the same number of nodes and also finds no cover. The C program additionally
checks a fixed eight-fiber fixture: its odd quotient directions partition
`V` and its even directions do not. That fixture shows the partition test
can succeed and can fail.

The recorded outcome is zero solutions. The full normalized tree visits
57,685,490 nodes. The independent recount of second-fiber index 1 visits
515,051 nodes, also with zero solutions.

## Conclusion

No universal closed length-30 word has a multiplicity-2 sojourn of rank 4
with exactly 16 distinct layer-0 projections. In the stated window
`8 <= |Q1| <= 14`, the layer-0 size is therefore at least 17. Combined with
`|Q0| + |Q1| <= 30`, the layer-1 size is at most 13. The fourteen-point
layer-1 boundary is empty. The separate necessary case `|Q1| = 6`,
`|Q0| = 24`, is already above 17 layer-0 points and is not affected by this
census.

The same counting does not forbid 17 or more layer-0 points. One fiber of
size 3 and seven fibers of size 2 produce `6 + 4 + 4 + 4 = 18` sums in each
direction against 16 targets, so two units of slack remain and the exact
packing stops.

## What this does not say

The recorded word

```text
1 5 4 0 4 3 6 4 7 4 1 7 6 4 2 6 5 6 7 0 6 5 6 2 5 0 3 7 4 0
```

still has 30 distinct prefixes and coverage 255, missing only mask 131. Its
rank-4 sojourn, at source 2, has 21 layer-0 projections and 9 layer-1
projections. Both sizes meet the new bounds. The witness is not removed, and
coverage 255 is not a new obstruction.

No universal length-30 word is constructed or ruled out. Ranks 5 and 6 keep
the floors 15 and 12 from pull request 7015; those floors were not
re-censused. Length 28 is not treated. The length-32 Gray concatenation
remains universal, so `f(8) <= 32` is unchanged. No supplier, readout
schedule, or selected frontier is changed. `f(7) = 24` is not used and was
not replayed.

The census is exhaustive for the normalized sixteen-point fibers. It is not
a heuristic search, and a failed search outside this finite domain would not
be a proof of the same statement.
