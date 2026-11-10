# The Y-exit round trip loses 160 rank mass

This is a paid-moment obstruction for one named route on the pinned round-three
centre word. It is not a new κ, a selected-word decoder, or a statement about
every centre route.

## Word and width law

The word is `research/sol1337-contact-frontier/inputs/round3-native.json.gz`,
SHA-256 `7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05`, the
same bytes `retained_verify.SOURCE_HASH` names. Cao Yifan / intqwq, PR #4610,
is the source of that word. The emitter used here is the retained centre
extension in `research/sol1337-contact-frontier/vendor/retained_verify.py`.

A canonical frame's dimension is the length of its basis. The retained `span`
check forces that basis to be independent, so the span has size `2` to that
dimension. A transport from frame `a` to frame `b` is legal only when the two
spans are strictly nested, and the emitter charges

    width = abs(dim a - dim b).

That is the rank of the paid Gaussian child. The same identity is the check in
`replay`.

`canonical["h"]` is 9 and `canonical["v"]` is 112. The non-centre output list
has length 632, so the block after two copies of `v` has length 408. The
emitter then appends eight centre roles, numbered 632 through 639. Roles
`[0, v)` are the X block and roles `[v, 2v)` are the Y block in the retained
centre-extension indexing. The geometric counts below are read off those
indices; they are not a second word.

## What the word contains

There is one frame of dimension 9, frame 1. Every X exit uses it. Each of the
112 Y exits uses a distinct frame of dimension 8, and each of those spans is a
strict subspace of frame 1. The transport from a Y exit frame to frame 1
therefore has width 1, and the return transport has width 1. Doing both for
every Y exit adds 224 rank-1 children and restores every exit chart.

The emitted invoice has exactly eight transports of width 8. Each is one
centre role, from its dimension-8 chart to the empty chart. Their rank mass is
`8 * 8 = 64`. The paid histogram is

    {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40, 8: 8},

matching `PAID` and `canonical["local_profile"]`. The helper target histogram,
final dimension minus start dimension on roles `[224, 632)`, stays

    {4: 28, 7: 7, 8: 47, 9: 326}.

The round trip does not edit those targets.

## Moment comparison

Let `θ` be a real number in `(0, 1]`. A rank-1 child contributes `1^θ = 1`.
For a positive integer rank `r`, `r^θ ≤ r`, because `t ↦ r^t` is strictly
increasing: `r^t = exp(t ln r)` and `ln r > 0` when `r ≥ 2`, while `r = 1`
gives equality. Equality holds for every such `θ` when `r = 1`, and for `r > 1`
only at `θ = 1`.

Delete any submultiset of the eight centre transports. The saved moment is at
most the deleted rank mass, which is at most 64. The round trip adds 224, so
the paid-moment change is at least

    224 - 64 = 160 > 0.

Deleting all eight calls attains 160 at `θ = 1`, since `8^1 = 8` and
`8 * 8 = 64`. For `θ < 1` that same deletion saves only `8 * 8^θ < 64`, so the
gap is strictly larger than 160. The constant 160 is sharp on the closed
interval and is realized by the actual centre budget at the endpoint `θ = 1`.

A one-way move of every Y exit onto frame 1, without the return, adds 112
rank-1 children and still leaves a gap of at least `112 - 64 = 48`. It does
not restore the rank-8 exit charts. The handoff's operation is the round trip,
which does restore them.

## What is not claimed

No helper target, scalar coefficient, native warp, or X exit changes. The
obstruction does not price a route that moves only some Y exits, deletes a
helper call, or replaces the centre transports by a different consumer. It
does not replay the centre-chain terminal, whose bill is 112 rank-8 children
and 114 rank-9 children rather than 224 rank-1 children. It does not reopen
the independent one-transvection census on the contact graph, and it does not
search the binary coframe class closed by PR #5698. The selected conditional
value `781451/250000000` is untouched. Unknown native, precision, tape, and
caller costs are not set to zero; the paid side of this route is already
strictly higher.
