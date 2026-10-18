# A final restored endpoint does not discharge a live COPY obligation

For one live copied helper functional l and an intervening invertible scalar
helper map U, legal ERASE requires **l U=l at the ERASE cut**, not merely eventual
helper restoration. On four dirty registers, exactly **1344 of 20160** binary
invertible maps satisfy that obligation for a specified nonzero l.

The exact local R439 candidate in PR1062 has nine COPY/ERASE intervals. For each
we insert a center-write immediately after COPY and its inverse immediately after
ERASE. All nine variants have the original endpoint if ERASE is incorrectly
treated as unconditional deletion. Every variant fails the actual chronological
equality check at ERASE. These are counterexamples to an endpoint-only proposed
relaxation, not bugs in the retained verifier, which correctly rejects them.

## Full boundary contract and proof

Let h be arbitrary dirty helper values, y arbitrary targets and t a fresh copy
register. COPY creates t=l h. A helper-only block changes h to U h while any
target reads use this unchanged t. At ERASE the center currently represents
l U h. Equality for every h is equivalent to l U=l: necessity follows on unit
inputs and sufficiency by linearity. Later applying U^-1 restores h and cannot
repair an earlier illegal ERASE. Conversely, if l U=l, then ERASE is legal and
U^-1 after it restores all helper inputs; target contributions are precisely the
ones from l h. This contract includes all dirty columns, not just clean sources.

Choose helper coordinates with l=e_0^T. The stabilizer consists of blocks
[[1,0],[v,B]], v arbitrary and B in GL(h-1,2), hence has order
2^(h-1) times product_{i=0}^{h-2}(2^(h-1)-2^i). For h=4 this is1344.
The written proof is for every h; the verifier independently exhausts all
four-by-four invertible row tuples and all16 dirty assignments per tuple.

## Paid scope

For a common-frame scalar block with g ADDs, the COPY and ERASE remain one pair
of the original rank r. U and its literal inverse cost2g scalar ADDs; no helper
role, copied object, frame descent, or extra copied information is free. The
two-ADD production countercontrols are semantic probes: their gates do not
claim a favorable or legally admitted frame schedule. We screen legality before
synthesis. Moving the restoring gate before ERASE repairs every bad example at
the same two-ADD invoice, while choosing an update that fixes the center is a
separate passing control. No savings or new supplier is proposed.

## Reproduce

`python -I -O -B research/bit-copy-live-stabilizer/verify.py`

Source hashes bind PR1062's exact payload and lifecycle specification. A new
integer-bitset engine checks all661 formal production columns, all9 chronological
counterexamples and both repairs. The GL4 check covers20160 matrices and322560
dirty assignments. Python3.12 registered replay and selected-integrity checks
pass. Native/full-provider/outer assembly and physical frame admission are not run.

PR1194/1306 address a closed frame-zero D boundary. This note treats the distinct
open-copy interval, where final restoration is too late. Existing omission
atlases delete gates; these variants add an inverse pair yet remain illegal.
Cached overlap and its freshness/coverage limits are in OVERLAP.json.

## Open next questions

For several simultaneous live copies, replace l by their row matrix L and test
L U=L. This may prune a future shared-copy mechanism before implementation;
first identify an actual simultaneous-copy proposal. No such production
replacement or favorable completed invoice is supplied here.

## Credit

Sagar Thakrar PR1062 and its literal COPY/ERASE checker, the PR967 helper-star
lineage, DreamingOfClouds PR589 and eumemic PR555. This note does not discover a
bug in their checks. Prepared by woklerx with substantial OpenAI Codex assistance.
Apache-2.0.
