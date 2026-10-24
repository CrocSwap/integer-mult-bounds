# Independent logical review of the new clean-J core

All four local programs pass the independent exact operator check. Both
PR3133 providers give the forward map `(x,y,h)->(x,y+Jx,h)` and the
backward map `(x,y,h)->(x-Jy,y,h)`, where `J=I-R^T R/4` for the actual
112-port source matrix R. Each word costs 164,514 real scalar primitives
and has native rank mass 5,073.

This file accepts the logical map, arbitrary-helper restoration, frame
bindings, zero-buffer contract, and local counts. Fresh verification of
the physical native recipes is a separate pending step. This file does
not accept a new global controller, owner allocation, private hosting
bound, precision bound, or complete kappa calculation.

## Pinned input and method

The reviewed proof is `../new-core-transfer-20261017/CLEAN-J-TRANSFER.md`,
SHA-256 `d12fca8b1abf95b20b9561334fb3d879d28ce880f6793a461ede0223fce1e2a0`.
The complete decompressed program payload has SHA-256
`a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa`.
The producer receipt has SHA-256
`c173491679101d121a0fb43156c73ab62d9031e62b6a969a8ab80912bc36630e`.
The source and canonical pins are in the independent receipt.

The review imports no producer or source interpreter. It checks the
published PR3148 source bytes and their object equality with the local
PR3133 words. It checks the complete compact role inventory against the
source's removed-helper list. It compares every retained native record
and the complete retained scalar suffix against the source program.

The independent operator method propagates output coefficients backward.
Coefficients belong to the rational group algebra of free invertible
warp generators. A scalar ADD propagates the target output coefficients
into the source column. A warp prepends its signed generator to each
operator word, with adjacent inverse cancellation. The producer instead
propagates input rows forward and appends generators. The two methods
give the same complete matrix.

Each program has 632 arbitrary live inputs and eight arbitrary C inputs.
The check also observes all 91 zero-buffer output rows. An allocation
sets only that buffer's input to zero. The logical check does not erase
a buffer at its free event. A separate lifetime pass proves that no
buffer has a later use. Thus a zero observed output proves that the
buffer is zero at its actual free event.

## Findings

Every one of the 408 helper input columns is the corresponding unit
column, with an empty operator word. All helper input effects cancel
from the data outputs. C0 ends at zero. C1 through C7 retain their
arbitrary physical inputs because no event uses them. All 91 buffer
output rows are zero. The zero buffers have a clean-input contract;
they are not counted as arbitrary borrowed fields.

The new H has 367 coefficients on 106 helper roles. Every such role
has input frame I and output frame FULL. The new source H differs
from the old campaign H. The correction uses the new H, with one
serial C0 query per centre row. It preserves its source in both
directions. It clears no borrowed helper.

For the forward centre-deleted word, the helper debt is `-K H h` in
Y. The prefix adds `K H h` before that word. For the backward word,
the debt is `H^T R y/4` in the helpers. The prefix subtracts this
quantity before that word. The independent full-word calculation
verifies these cancellations on arbitrary inputs, including every
warp path and all cleanup gates.

Each complete word contains 23,388 events. The input correction has
832 events and costs 8,526 real primitives. Deletion removes exactly
eight rank-eight private centre children. All 5,115 other native
records remain unchanged: 3,507 climbs, 240 warps, 978 ordinary
adapters, and 390 residual adapters. The child profile is
`{1:2433,2:724,3:228,4:102,5:20}`.

The forward invoice is `158148-2160+8526=164514`. The backward invoice
is `158196-2208+8526=164514`. A separate count of every scalar event
agrees. Every scalar frame and retained native entry frame matches.
All live endpoint frames match the canonical source.

Controls remove the input correction or change one of its coefficients.
Each control gives a different complete operator. The checks do not
rely on random inputs or a finite specialization of a warp matrix.

## Warp convention and phase boundary

The source emitter describes backward warps as conjugates of forward
warps. The source phase table uses the forward K_G convention. This
distinction must be explicit in the physical review.

The checked backward word is an identity over free invertible warp
generators. Therefore its endpoint map holds under either consistent
substitution: K_G or conjugate(K_G), with inverse occurrences assigned
the corresponding inverse. No relation between the forward and backward
generator substitutions is used in this proof. This observation permits
a choice of physical warp convention; it does not replace a check of
the exact chart transport, monomial rank, and global phase for that
choice.

The retained phase evidence alone is not treated as a fresh physical
replay. The new canonical providers have 1,130 frames, and their proper
helper terminal spaces must be used in the residual wrappers. The
physical review must check those actual instances, including width-six
helpers and the exact target adapters. It must not substitute the older
T74 frame set or silently use FULL for a proper terminal space.

## Reproduction

Run with a new output path:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/check_new_core.py --out work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/NEW-CORE-LOGICAL-REVIEW-FINAL.json
```

The checker prints one `PASS_640_ARBITRARY_COLUMNS_AND_91_ZERO_OUTPUTS`
line for each of the four programs, followed by
`PASS_INDEPENDENT_NEW_CORE_LOGICAL_TRANSFER`. It ran with exact rational
arithmetic and optimization enabled. The source interpreter was not
imported or run by this independent checker.

OpenAI Codex assisted the review under the user's direction. No PR,
commit, or push is authorized. Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
