# Independent review of the two movable rank-eight certificates

Both certificates pass. For either actual frame V equal to 983 or 991,
every k-dimensional centre-query subspace costs at least `8k` native
rank in the stated contained-frame model. All eight queries therefore
cost at least 64. The review also proves the FULL extension below.

The reviewed proof `history-encoding/MOVABLE-RANK8-CUTS.md` has SHA256
`9e8ebc108a758883e9811798900bbaa7c42ffa90ac960953a7596d3427f50708`.
The reviewed certificate `MOVABLE-FULL-RANK-CUTS.json` has SHA256
`62c3b26274ef80a75bbc90b680ceeed9ed24fb158fd7db32594995859c875951`.
No material finding remains.

## Independent exact checks

The review imports no producer or flow code. It reads the pinned
snapshot payload and actual interface. It rebuilds all binary subspaces,
all actual frames contained in each V, all strict inclusion edges, and
the Hasse graph. It checks exact nonzero 8-by-8 source minors for all
source tests. These minors prove that every used restriction is injective
on the full eight-dimensional query space, and hence on each of its
subspaces.

The review substitutes `X=JY` in the actual snapshot rows and sets all
480 helper inputs and private inputs to zero. It checks the resulting
source supports. Every free observation in each accepted cut vanishes
on its source test. All FULL snapshots also vanish on this family.

Each case has seven upward-closed unit cuts. Every stated entering edge
is checked. Every direct inclusion edge is charged at most its dimension
increase, including edges outside the Hasse graph. The exact counts are

| V | Contained frames | Hasse edges | All strict inclusion edges |
|---|---:|---:|---:|
| 983 | 122 | 238 | 810 |
| 991 | 124 | 246 | 820 |

Frame zero is included. All snapshot times are granted. Thus the result
does not rely on a chronological schedule that might omit an observation.

## FULL extension

The producer proof requires the query fields to reach V before their
last completion. That requirement can be removed within the same cone.
Append FULL to each of its seven cuts. Add an eighth unit cut containing
only FULL, with any one of the verified full-rank source tests.

For an old contained edge, the charge is unchanged. For a direct edge
from U to FULL, the charge is

    charge(U -> V) + 1 <= 8 - dim(U) + 1.

This is at most the cost `9-dim(U)`. For U equal to V, the charge is
one. The independent checker tests every one of these added edges
directly, as well as the old edges.

All eight tests are injective on every requested k-dimensional query
subspace. Their demands therefore sum to `8k`. This proves the bound
for any network in which every proper frame is an actual subframe of
one chosen V. Branches can complete directly to FULL and merge there;
they need not materialize a common intermediate value at V.

## Scope and units

The native ranks are in the original nine-coordinate units. Repeating
each axis lambda times multiplies every stated native rank by lambda.
For an arbitrary payload dimension N, the source restrictions and the
capacity of each field both acquire the factor N. The bound in field
units remains `8k`.

The model retains the logical content of each frame transition. It
allows arbitrary scalar sharing and cancellation. It permits all actual
contained observations at all times, but it does not add observations
from another cone or a changed core. Synthetic intermediate frames and
unpriced changes to logical address meaning are outside this certificate.

The two certificates cannot be added or combined into a global bound
without checking the new edges and observations. No all-frame bound of
64, improved native word, or complete supplier invoice is claimed.

## Reproduction

Run from the repository root:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/cover-algebra/review_movable_rank8_cuts.py
```

The fresh run passes with assertions disabled. Its receipt is
`MOVABLE-RANK8-CUTS-REVIEW.json`. The receipt contains exact source
minors, all source pins, edge counts, and the review checker hash.
The search or optimality of its integer-flow routine is not part of
this review.
