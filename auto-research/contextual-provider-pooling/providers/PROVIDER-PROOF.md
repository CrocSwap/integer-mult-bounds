# Epoch and selected-promotion provider construction

The source is the frozen TN27 epoch word. PR558 supplies two sets of four
post-center response-kernel pivots. This registry implements p0, p2, p4, p6,
and p8, with helper-index sets fixed in VARIANTS.json. It does not infer a
numerical result merely from entrance rank.

## Sufficient composition argument

The epoch rewrite changes the source presentation in A, with its exact terminal
inverse, and preserves the full arbitrary-dirt linear operator. The promotion
changes starting frames and 3 correction gates per selected pivot inside
B[320:488]. All 168 gates there are elementary additions whose destination set
and source set are disjoint. Their pairwise products therefore commute. Sorting
these gates by frame dimension preserves the scalar operator, not just its clean
input restriction. The constructor checks this disjointness and preserves the
scalar multiset of B; A is unchanged from the already reconstructed epoch word.

For each promoted helper, the new entrance contains its old rank-4 entrance and
has rank 5. Every correction sourced by that helper is moved to the new frame.
The exact nested-frame profile check validates every resulting chain. Cleanup is
regenerated as the inverse of every background operation in reverse order.
Since background operations do not read targets, their complete background
transformation and inverse restore arbitrary initial helper dirt. The scalar
replay also independently checks the compensation, endpoint, and dual endpoint
on all 728 initial columns, plus omission controls for every promoted pivot.
These checks do not certify physical owners, normalized adapters or the outer
recurrence: the complete local and global replay must additionally certify them.

## Nonlinear partial-group cost

The complete p4 group has exactly half the local profile delta of p8 versus p0.
The partial p2 and p6 choices do not interpolate that delta. Their combined
histogram excess over p8+p0 is +12 rank-1 -4 rank-2 +4 rank-3 -4 rank-4 calls.
This penalty must be included when pricing a time-dependent provider registry.
Each constructor receipt contains the complete local histogram and ordered
residual widths; no component gains may be added without that bill.

## Reproduction

Run:

    python -B build_providers.py --input EPOCH/FULL-WORD.json.gz --gk-dir GK --out NEW_OUTPUT --audit

EPOCH is the TN27 epoch constructor output. GK contains the preserved upstream
gk_word.py and gk_common.py implementation. NEW_OUTPUT must not exist. Input,
recipe, and output words are pinned by canonical JSON SHA-256 so CRLF and gzip
implementation differences cannot disguise semantic changes. Newly emitted
gzip uses compression level 9, mtime 0 and OS byte 255. p0 is copied unchanged.

PR558 receives credit for the rank-5 promotion. The epoch presentation was
already delivered in TN27. The new numerical mechanism, if fully admitted by
the global replay, is resource-aware heterogeneous use of these providers.
