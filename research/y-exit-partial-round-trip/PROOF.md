# A restored partial Y-exit round trip does not lower the paid moment

This is a paid-moment obstruction for one finite schedule. It is not a new κ,
not a decoder of the selected #6030 word, and not a claim about every centre
word. The selected value stays `781451/250000000`.

The schedule is the pinned round-three centre word
`research/sol1337-contact-frontier/inputs/round3-native.json.gz`, SHA-256
`7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05`, emitted by
the retained centre extension
`research/sol1337-contact-frontier/vendor/retained_verify.py`. Cao Yifan /
intqwq, PR #4610, is the source of the word. The all-112 round trip, and the
question this note answers, are
`research/y-exit-rank-lift-obstruction`.

## Hypotheses

A chart is one of the word's recorded frames. Its dimension is the length of
its basis. The retained span check makes that basis independent. A transport
from chart `A` to chart `B` is legal only when the two spans are strictly
nested, and its width is `abs(dim A - dim B)`. That width is the rank of the
paid child. A warp may change the current chart, but every warp considered
here preserves dimension. The emitted word has 240 warps, and each of them
does. A scalar add, scale, or warp pins every participating role to the chart
recorded on that event.

The emitted final charts stay in force: roles `0..631` end on
`canonical["final"]`, and the eight centre roles `632..639` end on the empty
chart `0`. In particular every rank-8 Y exit is restored. Roles `112..223`
are the Y block and roles `224..631` are the helper block, in the retained
centre-extension indexing.

## The emitted walk meets the variation bound

On one role, dimension changes only on transports, and each transport
contributes exactly its width to the total variation. A walk from dimension
`s` to dimension `t` therefore has rank mass at least `abs(t - s)`. Equality
holds exactly when the walk is monotone.

The checker walks all 640 roles on the emitted events. Every role meets
equality, the eight centre roles are a single downward step of width 8 onto
chart 0, and every other role only increases dimension. The total rank mass
is 5327, which is also the exponent-1 paid moment of the retained histogram

```text
{1: 2201, 2: 412, 3: 510, 4: 127, 5: 40, 8: 8}.
```

There is one frame of dimension 9, frame 1. Each of the 112 Y exits is a
distinct dimension-8 chart strictly inside that frame, and each Y role runs
from the empty chart to its exit. A round trip from that exit to frame 1 and
back is two nested width-1 transports. Any non-monotone integer walk from 0
to 8 has variation at least 10, because a variation strictly above the net
change jumps by at least 2.

## Exponent 1, with helper calls rewritten or deleted

Let a schedule use only nested transports of width `abs(Δ dim)` and
dimension-preserving warps, and let it preserve every start chart and every
emitted final chart. Its exponent-1 paid moment equals its rank mass, and
that mass is at least 5327. The emitted schedule attains 5327.

If `k ≥ 1` of the Y roles are not monotone, their extra variation contributes
at least `2k`, so the moment is at least `5327 + 2k`. A restored round trip
of any nonempty set of Y exits is one such schedule: those roles visit frame
1 and return, and the other final charts can stay monotone. Deleting or
rewriting helper transports cannot fund the difference while the helper
final charts stay, because those roles are already at their net variation.
Deleting a helper scalar add does not remove a paid child; it changes the
operator, and it still leaves the dimension lower bound in place.

So no chart-preserving route that round-trips one or more rank-8 Y exits
lowers the exponent-1 paid moment. The optimistic credit in the predecessor,
deleting the eight width-8 centre transports for 64 rank mass, drops the
centre roles off chart 0. It is not available under this endpoint. Even if
that credit were granted, `k ≥ 33` would still leave a positive gap at
exponent 1, since `2·33 - 64 = 2`. The chart-preserving argument does not
need that credit, and it covers every nonempty `k`, including `k = 1`.

## The scalar program fixes the histogram at every exponent

A stronger statement holds when the emitted scalar, scale, and warp events
stay in order, on their recorded charts. Every one of the 3298 transports is
followed, before the next transport of that role, by a participant event
whose chart is the transport's arrival chart. The checker counts one such
next pin for every transport. Some of those gaps also contain a
same-dimension warp, after an add on the arrival chart; the warp does not
remove the pin, and the following transport leaves the post-warp chart.

Removing a transport therefore leaves that next pin on the wrong chart.
Replacing the step costs at least the same width, because the width is
already the dimension gap. The paid histogram is forced.

Inserting a round trip after a Y role's last pinned event, out to frame 1 and
back, restores that exit and does not move any earlier pin. The checker does
this for Y role 112. The retained matrix is unchanged, and the histogram
gains exactly two rank-1 children. A rank-1 child contributes `1^θ = 1` at
every real exponent `θ`. The paid moment therefore rises by exactly `2k` at
every `θ` in `(0, 1]`, for a restored round trip of `k` exits, whenever the
other transports stay.

That is the route named by the predecessor's first open question, including
the clause that helper targets stay fixed. Helper-transport deletion is not
an extra degree of freedom under those pins.

## What is not claimed

No selected-word decoder, native phase, or κ changes. Unknown caller,
precision, and tape costs are not set to zero; the paid side of the inserted
round trip is already strictly higher. The one-way move onto frame 1, which
does not restore the rank-8 exits, is still the predecessor's second
question. A warp that changed dimension would be a different alphabet; the
emitted warps do not, and this note does not construct one. The argument is
this word's event list plus the variation lemma. It is not a search, and it
does not enumerate other centre words.
