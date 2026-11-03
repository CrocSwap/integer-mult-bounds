# A frame conversion and its inverse do not both emit

## Contract

The word is Ali Romman's PR #5708 scalar program,
`research/g20-conjugation-admission/WORD.json.gz`, together with that
package's `PATHS.json` and frame table. A published route is one triple
`(u, v, r)` in the route table. The cut algebra is the one in Nick Petalas's
free-carrier certificate: prefix rows and suffix columns over `F_2`, a
carrier bank of fields that share a frame shape, and the boundary pairing
of the eligible kernels outside one helper group. Queries change the frame
and do not change those normalized rows. This note does not rerun the
common-frame census. It asks whether one published conversion and the
inverse conversion can create a nonzero boundary pairing.

## No inverse route

The route table has 2369 edges. On every edge the destination dimension is
strictly smaller than the source dimension, and the recorded rank equals
that difference. Frame 1 is the only dimension-8 frame, and no edge enters
it. An inverse edge would raise dimension or repeat an endpoint pair. None
exists. A conversion followed by the inverse conversion therefore does not
emit.

## The opening schedule still needs frame 1

Helper 222 is one of the 413 public members of the large endpoint group.
It starts at frame 1 and is not an owned field. Its first six scalar
records, at event indices 5638 through 5643, are `ADD`s whose declared
frame is 1. The cut traversal accepts an `ADD` only when both endpoints
already occupy that frame. Because no route returns to frame 1, any
earlier published exit leaves those `ADD`s ill-typed.

## One published exit does open a singleton channel

At the opening cut the prefix is the identity. For every one of the 413
public helpers, the suffix column is supported inside the group and meets
that helper's own coordinate. The one-field carrier therefore has left
rank 1, right rank 1, boundary rank 1 and internal rank 1. Both necessary
scalar equations `a b = 1` and `c d = 1` hold for that singleton.

Frame 1 has 189 published edges into frame shapes that are empty at the
opening cut and lie strictly between the group's entrance and exit
dimensions: 9 of rank 1 and 180 of rank 2. `(1, 517, 1)` is one rank-1
edge. Moving helper 222 along that edge creates the singleton channel
above. The same pairing occurs for every other
public helper and every other empty compatible exit. The move is not a
typed continuation: the helper never returns to frame 1, so the six
opening `ADD`s fail.

## Non-member exits do not open a channel

A field outside a helper group never has an odd singleton boundary
pairing at any of the 14795 cuts. An exit into an empty shape is that
singleton case, so it stays rank 0. An exit into an occupied compatible
shape was passed to the same pairing routine whenever the new row could
enlarge either kernel. That span filter admitted 2650155 pairings. Every
boundary rank stayed 0. No published one-edge move of a non-member
exposes a boundary channel.

## The detector is not blind

After event 7407, field 208 occupies frame 622. The bank of frame 509
has 11 other fields, boundary rank 0 and right kernel 0. Adding field 208
raises the boundary rank to 1 and the internal rank to 1. The route table
has no edge `622 → 509`, so the census does not count this bank. The same
pairing routine records the hit. A route-legal channel would have been
counted.

## Invoice

There is no route-legal pair of queries, so there is no two-query
paid/target delta. The route moment used for these edges is
`Σ_r n_r r^t`. One rank-1 query contributes `1^t = 1` and does not change
a normalized target row. That increment is not an invoice of this word:
the following frame-1 `ADD`s are ill-typed. Selected κ stays
`781451/250000000`. The five framework assumptions remain. This is not a
supplier admission or a multiplication theorem.

## Credit

The word, the route table and the different-physical-role question are
Ali Romman's PR #5679 and PR #5708. The common-frame obstruction and the
cut algebra are Nick Petalas's. Gaussian elimination and rank-nullity are
classical. The route census and the opening-schedule obstruction are new.
