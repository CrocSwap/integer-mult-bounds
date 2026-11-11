# The one-way Y-exit move onto frame 1 is not a retained endpoint

This is a scoped proof on one finite schedule. It is not a new κ, not a
decoder of the selected word, and not a claim about every centre word or
every conceivable endpoint contract. The selected value stays
`363005817/100000000000`, the value in `certificates/selected-result.json`
at base `e54523517d0f03e58352e647c403a5af3e525a57`. This package does not
edit that record.

The schedule is the pinned round-three centre word
`research/sol1337-contact-frontier/inputs/round3-native.json.gz`, SHA-256
`7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05`, emitted
by `research/sol1337-contact-frontier/vendor/retained_verify.py`. Cao Yifan
/ intqwq, PR #4610, is the source of the word. The all-Y round trip and the
question this note answers are
`research/y-exit-rank-lift-obstruction`. Open PR #7102 prices the restored
partial round trip. Its restored-exit hypothesis is false for the move
below, and this argument does not use that theorem.

## Hypotheses

A chart is one of the word's recorded frames. Its dimension is the length of
its basis. The retained `span` check makes that basis independent, so the
span has size `2` to that dimension. A transport from chart `A` to chart `B`
is legal only when the two spans are strictly nested, and its width is

    abs(dim A - dim B).

That width is the rank of the paid child. A warp on the emitted list may
change the current chart. Each of the 240 emitted warps preserves dimension.
The variation bound below assumes that hypothesis. It does not say that
every opcode in a larger alphabet preserves dimension.

The retained endpoint is the chart tuple

    canonical["final"] + [0, 0, 0, 0, 0, 0, 0, 0].

Roles `0..631` end on `canonical["final"]`. The eight centre roles
`632..639` end on the empty chart `0`. The retained `replay` also requires
the paid histogram

    {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40, 8: 8}.

Its invoice check runs before the chart check, so a histogram mismatch
rejects a schedule before the chart tuple is reported. The chart comparison
below is made by the same walk with the invoice allowed to change.

The one-way move of a set `S` of Y roles appends, after each role's last
pinned event and not before it, one transport from that role's emitted exit
chart to frame 1. It does not append the return. Roles `112..223` are the Y
block.

## Chart comparison

There is one frame of dimension 9, frame 1, with basis

    [256, 128, 64, 32, 16, 8, 4, 2, 1]

and span size 512. Every X exit uses frame 1. Each of the 112 Y exits is a
distinct dimension-8 chart, none of them is frame 1, and each of those spans
is a strict subspace of frame 1. The transport from a Y exit to frame 1
therefore has width 1.

Y role 112 is the comparison asked for. Its emitted exit is chart 142, basis

    [256, 128, 64, 32, 16, 9, 4, 3],

span size 256. The integer 1 lies in the span of frame 1 and does not lie in
the span of chart 142. After the one-way transport, role 112's current chart
is 1, not 142.

This is an exhaustive census of the Y block on this word. The block length
`canonical["v"]` is 112, the roles are exactly `[112, 224)`, and every
recorded final in that range was read. It is not a census of other words.

## The retained endpoint rejects the move

The emitted walk of every Y role is monotone from the empty chart to its
dimension-8 exit, with rank mass 8. Its last pinned event is an add on that
exit chart.

Place the width-1 transport after that add. No later event names the role,
so every earlier pin still sees the chart it recorded. The transport does
not change the role's linear row. Replaying the schedule reproduces the
retained 640 rows. The paid histogram gains one rank-1 child for each moved
exit. The chart walk ends with each moved role on frame 1, so the retained
tuple fails, and the mismatches are exactly the moved roles.

Place the same transport immediately before role 112's last add, and rewrite
only that role's final chart to frame 1. The add still requires chart 142,
and the common-chart check fails. The scalar program does not survive a
one-way insertion in front of the exit pin.

Thus the retained endpoint does not accept the one-way move of role 112, nor
the one-way move of all 112 Y exits. The rejection of the post-pin insertion
is the chart tuple. The operator is the same.

The restored-exit argument does not apply. That argument assumes the walk
returns to the rank-8 chart. The schedule just replayed does not return.

## The predecessor gap of at least 48

Let `θ` be a real number in `(0, 1]`. A rank-1 child contributes `1^θ = 1`.
For an integer rank `r ≥ 2`, `r^θ ≤ r`, because
`r^θ = exp(θ ln r)` and `θ ln r ≤ ln r`. Equality holds for every such `θ`
when `r = 1`, and for `r > 1` only at `θ = 1`.

The one-way move of all 112 exits adds 112 rank-1 children. The emitted
invoice has eight transports of width 8, one per centre role. Subtracting
any submultiset of those widths removes at most 64 from the moment, because
a deleted rank-`r` child saves at most `r`. The difference is therefore at
least

    112 - 64 = 48.

Subtracting all eight widths gives 48 at `θ = 1`. For `θ < 1` the same eight
widths save only `8 · 8^θ < 64`, so the difference is strictly larger than
48. This is the predecessor's one-way bound. It still replaces each rank-8
Y exit by frame 1. Spending the whole credit also drops every centre off
chart 0, because those eight transports are the unique steps onto the empty
chart. The arithmetic does not exhibit a schedule.

That credit is not a second accepted schedule. Role 632's transport is
`(632, chart 254, chart 0, width 8)`, and the next event that names role 632
is an add on chart 0. Deleting the transport leaves the role on chart 254,
and the add fails. The same shape holds for the other seven centres: each
transport onto chart 0 is followed by an add on chart 0. The gap of 48 is an
optimistic rank-mass bound for a route that abandons the centre endpoint. It
is not the price of a completed retained word, and it is not the price of
the frame-1 endpoint in the next section.

## The changed endpoint that accepts the move

Replace the final chart of each moved Y role by frame 1, and keep every
other coordinate of the retained tuple. In particular every centre still
ends on chart 0, and every helper final stays. Call this the frame-1
replacement tuple for that set of exits.

The post-pin one-way schedule ends on this tuple. Its linear rows equal the
retained rows. Its paid histogram is the retained histogram with the rank-1
count increased by `k = |S|`. Each added child has rank 1, so the paid
moment rises by exactly `k` at every real `θ` in `(0, 1]`. No scalar event
is inserted. The X exits already use frame 1; sharing that chart adds no
transport and removes none.

For the assigned move, `S` is every Y exit and `k = 112`. The eight width-8
centre transports remain, so the predecessor credit of 64 is not taken. The
moment increase is 112, which is strictly larger than 48. The helper target
histogram on roles `[224, 632)` stays

    {4: 28, 7: 7, 8: 47, 9: 326},

because those finals are unchanged. Each moved Y role's net dimension rises
from 8 to 9.

The same alphabet makes 112 sharp. A walk from dimension 0 to dimension 9,
using nested transports and dimension-preserving warps, has rank mass at
least 9. Each emitted Y walk has rank mass 8 and is monotone, and one
width-1 transport raises it to 9. While a helper's final chart stays, that
helper's rank mass cannot fall below its emitted net, so frozen helper
finals cannot fund the increase.

The frame-1 replacement tuple is a different endpoint contract. Accepting it
does not make the move an endpoint of the retained tuple.

## What is not claimed

No selected-frontier change and no new κ. No decoder of the selected word,
no native phase, and no physical caller. Unknown caller, precision, and tape
costs are not set to zero; on the contract that accepts the move, the paid
side is already strictly higher.

This is not a proof that every imaginable endpoint contract rejects the
move. A contract that also changes a helper final or a centre chart is
outside the two tuples compared here. No dimension-changing warp is
constructed, and none is excluded; the emitted warps preserve dimension,
and a different warp alphabet is a separate question. The argument is this
word's frames and event list. It is not a search, and it does not enumerate
other centre words.

The integer powers checked by the program support `r^a ≤ r^b` for integers
`0 ≤ a ≤ b`. The comparison for real `θ` is the exponential argument above.
