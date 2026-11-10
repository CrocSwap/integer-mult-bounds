# Both new off-diagonal pairs still leave the c=7 cover at 3

**Scoped exchange census. No new κ.** In the unchanged unsigned dirty
connector, keep the centre as the only failed diagonal index, and suppose
`(9, 15)` is not weight 3. Then `(10, 14)` and `(11, 13)` can be new at the
same time. On every such chain the weight-3 cover is exactly 3, not 20.

The same census covers the chains on which both pairs are weight 3 and
`(9, 15)` is the complement. Those chains are the three-new windows already
counted by open PR #7032. Their cover is exactly 4. That sharpens the “at
most 6” bound of #7032 on this subfamily only. It does not rerun that
census and it does not decide unrestricted `c = 7`.

The selected conditional κ remains `781451/250000000`.

## Hypothesis, inherited

A floor word has length 42 and calls each of six sources seven times. A
pair realizes a weight-3 mask when every coordinate of `q_s + q_t` lies in
`{0, 1, 7, 8, 14}` and exactly three lie in `{1, 8}`. The coordinate sum is
then `s + t = 3 + 7λ`.

Open PR #7016 proves that if exactly one index in `4..22` fails, that index
is the centre, and the states at `s = 4..21` are the free-type graph used
here: `S(s) = q_s + q_{45-s}` is a permutation of `(8, 8, 8, 7, 7, 7)`, the
state is the suffix usage on `[45-s, 42)` together with that mask, and the
only steps are a stay or a Johnson swap. This package rebuilds the graph
and does not repeat the one-index reduction. It does recheck that every
`s = 21` state is saturated and that every ordering of the three off-mask
centre letters produces a coordinate 6, so the centre is not weight 3.

Open PR #7032 classified the chains on which `(9, 15)` is weight 3. The
only such endpoint pairs are the 20 complement shapes, and the cover is at
most 7. The walks below in which `(9, 15)` is not a complement pair are
outside those 31,788 windows.

## Where both pairs can be weight 3

On the free-type graph the jointly realized weight-3 sums inside `s = 4..21`
are only `(12, 12)`, `(11, 13)`, `(10, 14)` and `(9, 15)`, with 20, 180, 180
and 20 hits. The `(12, 12)` hit is the diagonal mask already at `s = 12`.
Every `(10, 14)` or `(11, 13)` hit has equal endpoint masks, and the two
usages are one of the following shapes. There are 9 shapes per mask and the
graph realizes each once.

For a mask `M`, write `M^c` for its complement. A `(10, 14)` shape is
determined by `a ∈ M` and a 2-subset `{b, c} ⊂ M^c`:

- at `s = 10`, usage is 3 at `a`, 2 on `M \ {a}`, and 0 off `M`;
- at `s = 14`, usage is 3 on `M`, 1 on `{b, c}`, and 0 on the remaining
  source `r ∈ M^c`;
- the sum realizes `R10 = {a, b, c}`.

An `(11, 13)` shape is determined by `p ∈ M` and `q ∈ M^c`:

- at `s = 11`, usage is 2 at `p`, 3 on `M \ {p}`, and 0 off `M`;
- at `s = 13`, usage is 3 on `M`, 1 at `q`, and 0 on the other sources off
  `M`;
- the sum realizes `R11 = (M \ {p}) ∪ {q}`.

Both sums are weight 3 on one chain only when the two shapes use the same
mask and the states are joined by edges. Usage forces `p ≠ a`: the step
`s = 10 → s = 11` increments the remaining source `w ∈ M \ {a, p}`. The
step `s = 13 → s = 14` increments the other member of `{b, c}`, so
`q ∈ {b, c}`. There are `20 · 3 · 2 · 3 · 2 = 720` such types, and every
one is joined by an edge. `R10` and `R11` are distinct from each other and
from `M`.

## The image collapses to one or two masks

On every such chain the diagonal mask is `M` except possibly at `s = 12`.

The usage at `s = 10` is supported on `M`. Each step adds one suffix letter,
so every ancestor stays supported on `M`. A swap would increment a source
that leaves the mask, but the incremented source lies in `M`. Every
backward step is therefore a stay, and `s = 4..10` all carry `M`. The
ancestor cone of each of the 60 states at `s = 10` has size signature
`(3, 6, 8, 8, 6, 3, 1)` and 210 paths from `s = 4`. The three states at
`s = 9` are the three single decrements of the `s = 10` usage. One of them
is the complement usage, 2 on `M` and 0 off `M`.

The usage at `s = 14` is already 3 on `M`, so no swap remains. The tail
`s = 14..21` is stays on `M^c` and carries `M` through the saturated state.
The three children at `s = 15` increment `b`, `c` or `r`. The increment of
`r` is the complement usage, 1 on every source off `M`.

Between the shapes, `s = 12` has exactly three states. Two keep the mask
`M`: stay on `p` then on `q`, or stay on `q` then on `p`. The third swaps
`p` for `q` and then swaps `q` for `p`, and its mask is `R11`. No other
state at `s = 12` lies on the chain.

Thus the diagonal image is `{M}`, or `{M, R11}` when the swap is used. In
the second case `(11, 13)` is not new.

## What the off-diagonal slots add

The coordinate bounds on a centre-only chain are the same ones as in
#7016, and they are valid on this graph. Every free-type prefix at
`s = 4..21` has coordinates in `0..4`, and the `s = 4` prefix in fact has
coordinates in `0..2`, so the same is true for `s ≤ 3`. The centre check
gives coordinates in `{3, 4}` at `s = 22` and `s = 23`, and `q_24` is
`(4, 4, 4, 4, 4, 4)`, so later prefixes lie in `4..7`. These bounds block
82 off-diagonal slots. The only surviving slots are the 25 pairs inside
`s = 4..21` and the single block `(33, 33)`. The graph census above says
the 25 pairs contribute a new mask only at `(10, 14)`, `(11, 13)` and
`(9, 15)`.

On this family the remaining two slots do not leave the image.

- The final letter at `s = 4` lies in `M`, because the usage is one letter
  inside `M`. The only weight-3 value of `(0, 3)` is then `M`.
- A block usage at `s = 12`, three 3s and three 0s, is supported on `M`.
  Then `(33, 33)` realizes `M`. The other route, stay on `q` first, is not
  a block, so `(33, 33)` is not weight 3.

For `(9, 15)`, the nine sums of the three states at `s = 9` with the three
states at `s = 15` were read directly. Exactly one is weight 3: the
complement endpoints, and it realizes `M^c`. The other eight are not weight
3. `M^c` is disjoint from `M`, from `R10` and from `R11`.

## The cover

| chain | diagonal image | new masks | cover |
|---|---|---|---|
| `(9, 15)` not weight 3, `s = 12` carries `M` | `{M}` | `R10`, `R11` | 3 |
| `(9, 15)` not weight 3, `s = 12` carries `R11` | `{M, R11}` | `R10` | 3 |
| complement endpoints, `s = 12` carries `M` | `{M}` | `R10`, `R11`, `M^c` | 4 |
| complement endpoints, `s = 12` carries `R11` | `{M, R11}` | `R10`, `M^c` | 4 |

Both pairs are new exactly on the first and third rows. The third row is
the complement shape of #7032. Per mask there are 36 types and 2 routes
with mask `M` at `s = 12`. One of the nine endpoint pairs is the
complement, so that row has `36 · 2 = 72` windows from `s = 9` to `s = 15`,
matching the three-new count in #7032. The non-complement both-new windows
are the other eight endpoint pairs: `36 · 2 · 8 = 576` per mask. Every one
has cover 3.

The word below is one non-complement both-new chain. Its `s = 9` usage is
`(3, 1, 2, 0, 0, 0)`, not the complement `(2, 2, 2, 0, 0, 0)`, and its
`s = 15` usage is not 1 on every source off `M`.

```text
012220001121343344555345555443343121100022
```

The diagonal image is `{(0, 1, 2)}`. The only other weight-3 masks are
`(0, 3, 4)` at `(10, 14)` and `(0, 2, 3)` at `(11, 13)`. The cover is 3.
A one-letter change of the first letter is rejected.

The complement word of #7032,

```text
012001122012345334455345554433543210221100
```

is the third row for the same mask: image `{(0, 1, 2)}`, plus
`(3, 4, 5)`, `(0, 3, 4)` and `(0, 1, 3)`. The cover is 4.

## The walks that only share a mask

The question also asks for every joint walk on which `s = 10` and `s = 14`
share a mask and `s = 11` and `s = 13` share a mask, whether or not the
sums are weight 3. A forward count and a backward count agree: there are
7,818,720 paths from `s = 10` to `s = 14` with those equalities. Both sums
are weight 3 on exactly the `720 · 3 = 2,160` paths through the shapes
above. On every other shared-mask path at least one of `(10, 14)` and
`(11, 13)` is not weight 3, so the two pairs are not both new. Those paths
are counted, not classified further. They are not a proof that the cover
is at most 19, and this package does not claim that bound.

## What this does not say

The cover 3 applies only to centre-only free-type chains on which both
`(10, 14)` and `(11, 13)` are weight 3 and `(9, 15)` is not. A chain with
two or more failed diagonal indices is not classified. Masks of weight
other than 3 are not listed. A completed weight-3 count would still not be
a depth-two block. The slot bounds are rechecked, but they are the same
obstruction as in #7016; they are not a new proof that `c = 7` is empty.
No supplier, consumer, or selected frontier changes.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -W error -B research/six-source-c7-noncomplement-pairs/verify.py
python3.12 -I -O -W error -B research/six-source-c7-noncomplement-pairs/verify.py
python3.12 -B scripts/research_package.py --package research/six-source-c7-noncomplement-pairs --check-only
```

The marker is `PASS_SIX_SOURCE_C7_NONCOMPLEMENT_PAIRS shapes=180/180 types=720/720 prefix_paths_per_state=210 cone=3,6,8,8,6,3,1 mids_per_type=3 mask_M_routes=2 both_new_windows_per_mask=576 complement_windows_per_mask=72 noncomplement_cover=3 complement_cover=4 witness_cover=3 witness_both_new=1 sharp_word_cover=4 slots_blocked=82 graph_slots=25 shared_mask_paths=7818720 shared_mask_paths_agree=1 controls=16`.

The sixteen controls are the two step generators and the layer sizes, the
one-letter usage increase, the saturated terminal layer and the centre
coordinate 6, the prefix bounds, the 82/25/1 slot partition, the joint
census, the complement usages at `(9, 15)`, the identification of the 180
hits with the shapes, the 720 types with their cones and 210 prefix paths,
the frozen tail and the three states at `s = 15`, the eight non-complement
sums at `(9, 15)`, the diagonal value of `(0, 3)` and of a block
`(33, 33)`, the agreement of the two shared-mask counts, the cover-3 word,
the cover-4 complement word, and the rejected one-letter mutation. No SAT
solver, Lean, or Docker replay is used.

## Open next questions

1. On a centre-only chain where `s = 10` and `s = 14` share a mask,
   `s = 11` and `s = 13` share a different mask, and exactly one of those
   two sums is weight 3, what is the weight-3 cover? *Why:* both sums being
   weight 3 forces the masks to agree and drops the cover to 3 or 4. A
   shared-mask walk with only one new pair is the remaining way the
   7,818,720 paths could approach a large cover. Separate endpoint
   equalities still suggest an image of size at most 16 and a cover of at
   most 19, and that counting is not proved here. *First step:* fix the
   weight-3 end to one of the 180 shapes and enumerate the states at the
   other pair whose common mask is different. *Blocked by:* those paths
   are outside the 2,160 both-shape paths classified here.

## Credit

The depth-two interface and the weight identity are Nick Petalas's
(PR #4231, PR #4248, PR #6107), with the Ross Richardson PR #934 / PR #943
lineage. JosieElliston's PR #6141 leaves `c = 7` open. The empty diagonal
equality case is upstream PR #6941. The one-index exchange is upstream
PR #7016, head `3a89abb195ec9a63476c12042df5fbb0760e3534`. The complement
two-pair census, including the 72 three-new windows and the cover-4 word,
is upstream PR #7032, head `6616162b4c49e84ae67921013d03151297f86879`. This
package starts at that paper's open question 1 and does not repeat the
complement collapse.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
