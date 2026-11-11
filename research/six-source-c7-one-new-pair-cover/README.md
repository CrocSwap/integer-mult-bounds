# One different-mask pair at c=7 has weight-3 cover 3 or 4

**Scoped exchange census. No new κ.** In the unchanged unsigned dirty
connector, keep the centre as the only failed index in `4..22`. Suppose
`s = 10` and `s = 14` share a diagonal mask, `s = 11` and `s = 13` share a
different diagonal mask, and exactly one of the sums `(10, 14)` and `(11, 13)`
is weight 3. The weight-3 cover is then 3 or 4. It is 4 exactly when `(9, 15)`
is the complement pair, and 3 for the other eight endpoint pairs. Both values
occur on every one of the 180 shapes.

The selected conditional κ remains `363005817/100000000000` from
`certificates/selected-result.json`. This package does not change it.

## Hypothesis, inherited

A floor word has length 42 and calls each of six sources seven times. A pair
realizes a weight-3 mask when every coordinate of `q_s + q_t` lies in
`{0, 1, 7, 8, 14}` and exactly three lie in `{1, 8}`. The coordinate sum is
then `s + t = 3 + 7λ`.

Open PR #7016 proves that if exactly one index in `4..22` fails, that index
is the centre, and the states at `s = 4..21` are the free-type graph used
here. This package rebuilds that graph and rechecks the centre, the prefix
bounds, and the 82/25/1 slot partition. It does not repeat the one-index
reduction. On this graph the only jointly realized weight-3 sums inside
`s = 4..21` are `(12, 12)`, `(11, 13)`, `(10, 14)` and `(9, 15)`, with 20,
180, 180 and 20 hits. Every `(10, 14)` or `(11, 13)` hit has equal endpoint
masks and is one of the 180 shapes below.

Open PR #7045 classified the 2,160 paths on which both sums are weight 3.
Those paths force the two masks to agree, and the cover is 3, or 4 on the
complement endpoints already counted by #7032. The walks below are the other
orientation: the masks differ, so at most one sum is weight 3.

## The weight-3 end cannot be (11, 13)

An `(11, 13)` shape is a mask `N`, a pivot `p ∈ N` and a source `q ∉ N`.
The usage at `s = 13` is already 3 on `N` and 1 at `q`. A swap increments a
source in the current mask, and every source in `N` is at usage 3, so every
legal step keeps `N`. Every successor of each of the 180 shapes has mask `N`.
A chain through that shape therefore has mask `N` at `s = 14`. Sharing a mask
at `(10, 14)` then forces that mask to be `N` as well. Under the different-mask
hypothesis the weight-3 end is a `(10, 14)` shape, and `(11, 13)` is not
weight 3.

## The twelve routes on a (10, 14) shape

A `(10, 14)` shape is a mask `M`, an anchor `a ∈ M` and a 2-subset `{b, c}` of
`M^c`. Write `r` for the remaining source off `M` and `R = {a, b, c}`.

- at `s = 10`, usage is 3 at `a`, 2 on `M \ {a}`, and 0 off `M`;
- at `s = 14`, usage is 3 on `M`, 1 on `{b, c}`, and 0 at `r`;
- the sum realizes `R`, which meets `M` only in the anchor, so `R` is neither
  `M` nor `M^c`.

The usage at `s = 10` is supported on `M`, so every ancestor stays on `M`: a
swap increments a source outside the new mask. The prefix `s = 4..10` carries
`M`, the ancestor cone has size signature `(3, 6, 8, 8, 6, 3, 1)`, and each of
the 60 states at `s = 10` has 210 paths from `s = 4`. Each of the three `s = 9`
parents, including the complement usage, has at least one of those paths. The
usage at `s = 14` is already 3 on `M`, so the tail `s = 14..21` is stays off
`M`. Each of the three `s = 15` children, including the complement usage,
reaches the saturated state on `M`.

From `s = 10`, a step that changes the mask swaps one non-anchor
`u ∈ M \ {a}` out and brings in one source `x ∉ M`. The resulting mask is
`N = (M \ {u}) ∪ {x}`. The checker follows every successor. The routes that
return to the shape at `s = 14` with mask `N` again at `s = 13` are exactly
twelve, four masks `N` times three routes:

| route at `s = 12` | `(33, 33)` |
|---|---|
| mask `N` | `M`, the block supported on `M` |
| mask `N` | not weight 3 |
| mask `R` | `M` |

In every route `x ∈ {b, c}`, so `N` meets `M` in two sources and meets `M^c`
in one. Thus `M`, `N` and `R` are pairwise distinct, and none of them is
`M^c`. The three routes share one state at `s = 11` and one state at `s = 13`.
The sum of those two states is not weight 3. There are `180 · 12 = 2,160`
such routes, and no further different-mask route joins a shape.

## The cover

On every such route the diagonal image is `{M, N}`, or `{M, N, R}` when
`s = 12` carries `R`. The same three masks are the whole weight-3 image,
except for the complement endpoints:

- `(0, 3)` realizes `M` on every `s = 4` state of the prefix cone.
- `(10, 14)` realizes `R`.
- `(11, 13)` is not weight 3.
- `(12, 12)` repeats the mask already at `s = 12`.
- `(33, 33)` realizes `M` on the two block routes and is not weight 3 on the
  other route.
- `(9, 15)` realizes `M^c` for the one complement pair among the three `s = 9`
  parents and three `s = 15` children, and the other eight sums are not
  weight 3.

`M^c` is new. The slot bounds leave no other pair. The prefix and the tail do
not depend on the route, so both endpoint choices extend every route.

| endpoints | masks realized | cover |
|---|---|---|
| not the complement pair | `M`, `N`, `R` | 3 |
| complement pair | `M`, `N`, `R`, `M^c` | 4 |

The cover-3 word uses `M = {0, 1, 2}`, `N = {0, 2, 3}`, `R = {0, 3, 4}`, the
non-complement parent `(3, 1, 2, 0, 0, 0)` and the non-block route. Its
diagonal image is `{M, N}`. The only other weight-3 mask is `R` at `(10, 14)`.

```text
012221000134213555443345344555332411000122
```

The cover-4 word uses the same `M`, `N` and `R`, the complement endpoints, and
the route whose `s = 12` state carries `R`. Then `(9, 15)` realizes
`{3, 4, 5}` and `(33, 33)` repeats `M`.

```text
012221100034215554433345334455534210001122
```

A swap of the first letter with position 21 keeps the source counts and is
rejected.

## What this does not say

The cover 3 or 4 applies only to centre-only free-type chains on which the two
pairs share different masks and exactly one sum is weight 3. It does not
classify the shared-mask walks on which the two masks agree and exactly one
sum is weight 3, nor the walks on which neither sum is weight 3. A chain with
two or more failed diagonal indices is not classified. Masks of weight other
than 3 are not listed. A completed weight-3 count would still not be a
depth-two block. No supplier, consumer, or selected frontier changes.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -W error -B research/six-source-c7-one-new-pair-cover/verify.py
python3.12 -I -O -W error -B research/six-source-c7-one-new-pair-cover/verify.py
python3.12 -B scripts/research_package.py --package research/six-source-c7-one-new-pair-cover --check-only
```

The marker is `PASS_SIX_SOURCE_C7_ONE_NEW_PAIR_COVER shapes=180/180 routes=2160 states_per_shape=4 routes_per_state=3 case_b_mask_changes=0 different_mask_weight3_other=0 cover_without_complement=3 cover_with_complement=4 witness_cover=3 complement_witness_cover=4 slots_blocked=82 graph_slots=25 joint=12/12:20,11/13:180,10/14:180,9/15:20 prefix_paths=210 cone=3,6,8,8,6,3,1 plain_word=012221000134213555443345344555332411000122 sharp_word=012221100034215554433345334455534210001122 controls=12`.

The twelve controls are the two step generators and the layer sizes, the
saturated terminal layer and the centre coordinate 6, the prefix bounds, the
82/25/1 slot partition, the joint census, the identification of the 180 hits
with the shapes and the frozen `(11, 13)` mask, the prefix cone with its 210
paths and a path to each `s = 9` parent, the tail and its three children, the
eight non-complement sums at `(9, 15)`, the 2,160 routes and their three
kinds, the two witness words, and the rejected count-preserving swap. No SAT
solver, Lean, or Docker replay is used.

## Open next questions

1. On a centre-only chain where `s = 10` and `s = 14` share a mask, `s = 11`
   and `s = 13` share that same mask, and exactly one of the two sums is
   weight 3, what is the weight-3 cover? *Why:* the different-mask half is
   settled at 3 or 4. The same-mask half is the remaining one-new-pair
   subfamily of the shared-mask walks counted by #7045, which classified only
   the subcase in which both sums are weight 3. *First step:* fix one of the
   180 shapes and enumerate the middles whose common mask equals the shape
   mask while the other sum is not weight 3. *Blocked by:* those middles were
   excluded here by the different-mask hypothesis.

## Credit

The depth-two interface and the weight identity are Nick Petalas's
(PR #4231, PR #4248, PR #6107), with the Ross Richardson PR #934 / PR #943
lineage. JosieElliston's PR #6141 leaves `c = 7` open. The empty diagonal
equality case is upstream PR #6941. The one-index exchange is upstream
PR #7016, head `3a89abb195ec9a63476c12042df5fbb0760e3534`. The complement
two-pair census is upstream PR #7032, head
`6616162b4c49e84ae67921013d03151297f86879`. The both-weight-3 non-complement
census, including the 2,160 paths and the question answered here, is upstream
PR #7045, head `59561147fe88ee9a1192715994b84faa0343c3f9`. This package starts
at that paper's open question 1 and does not repeat either pair theorem.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
