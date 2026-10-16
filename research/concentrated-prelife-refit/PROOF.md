# One legal frame change and its exact paid gain

The source is the complete frozen PR2733 composition, pinned by its original
published head and artifact manifest in `SOURCE-HEADS.json`. Both orientation
providers receive precisely the same change at B gate 1149:

```
['add',393,515,1,1,[259,132,66,36,16,9]]
                 -> [259,148,66,36,9]
```

The first five gate fields stay fixed. Only the common frame changes from rank
six to rank five. The complete scalar word, 112 source and 112 target roles,
entrances, final frames, operator words, precondition/compensation, 36
anticipatory corrections, all warps and inverse cleanup remain identical.
`verify_refit.py` checks complete decoded-word equality after this declared edit
and the corresponding report update, not merely matching rank histograms.

## Legal frame witness

For register 393 the preceding B gate is 1141, with frame
`[407,66,36,9]` of rank four. Its following B gate is 1790, with rank-seven frame
`[256,132,65,36,16,9,3]`. For register 515 the preceding B gate is 894, with frame
`[259,148,66,36,9]` of rank five. Its following B gate is 1778, with rank-seven
frame `[259,128,66,32,16,9,4]`. There is no intervening warp between each
register's respective neighboring occurrences. Register 393's warp at 1130
precedes gate 1141 and is unchanged.

Over F2 the new frame contains both incoming subspaces and is contained in both
outgoing subspaces. It is a proper subspace of the old common frame. Thus the
unchanged elementary addition is legal, and all four adjacent climbs remain
legal. Their old bill is `H2+3H1`; their new bill is `2H2+H1`. The exact local
change is therefore `H2-2H1`.

The independent checker computes the complete frame invoice, all arbitrary-input
free-operator rows in the forward and dual orientations, and literal inverse
cleanup. A zero frame and a changed coefficient sign are rejected separately
for each provider. Native physical recipes and phases are additional obligations
of the complete cold replay; they are not inferred from the free-operator check.

## Complete cost and owner interface

The resulting local profile is
`{1:2368,2:647,3:297,4:120,5:26,7:4,8:4}`. Since every entry and exit is unchanged,
so is every helper width. The original literal owner fill/order applies without
any remapping, and every one of the 276,390 roles remains charged. There are 415
helpers per call and 72 private FULL buffers. Physical stock remains
`66304+415+8+72+2=66801`. Across 666 calls, the global profile changes only by
`666*(H2-2H1)` to

```
{1:1594404,2:430902,3:204396,4:79920,5:22532,7:2664,8:2664,32:1,48:26558}.
```

Its rank mass is still 4,816,512. For native normalization
`M(b)=sum_r H_r*(r/73)^(1-b)/66304`, the exact moment change is

```
Delta M(b) = 666*73^(b-1)/66304*(2^(1-b)-2) < 0,   0 < b < 1.
```

This proves native moment dominance throughout that interval. It does not, by
itself, prove any unexamined conservative surcharge or whole outer exponent.
Those are rederived in the fresh complete replay and bound to `CLAIM.json`.

## Chained reconstruction and checker adaptation

`generate.py` authenticates the complete frozen predecessor packages before and
after reconstructing both words. It appends the new refit to the original
B894 refit stage. The following alias653 patch replaces a complete B list, so
that patch is regenerated as well; otherwise it would silently restore the old
B1149 frame. Both final decoded words must match the committed expected words.
Compressed regeneration is compared by complete decoded payload, while frozen
source bytes retain exact hashes.

`REPLAY-DERIVATION.patch` describes the changes from the previous composition
engine and adapter. In addition to the three already declared candidate checker
adaptations, `new/rebuild_borrow.py` now requires precisely the original B894
refit and this B1149 refit. It checks the exact original and resulting B1149 gate,
the original B894 gate and dimension drop, and equality of every other B gate.
The resulting four modified derivative checker files are individually hash-bound;
other frozen proof/checker Python remains unchanged. Eight deliberate extra or
incorrect edits were independently rejected. Frozen upstream packages are never
edited in place.

## Scope of the endpoint ceiling and remaining obligations

The exact rational dual/lattice ceiling applies only to this fixed local profile,
415-helper width inventory, 666 calls and original bin multiset. It relaxes
window/family constraints, so covers every packing order under those premises.
A changed local word/profile, inventory, warp or bin geometry requires a new
bound. The finite 914-closure screen is not an all-frame optimum.

All-size machine/compiler and common-label realization, sequential physical
borrowing/hosting/routing, uniform precision and fixed tape, exact recovery and
analytic transfer, native recurrence corrections, the bit supplier and modern
outer phase-cell/radix/prime-padding assumptions remain inherited. Finite receipt
checks do not establish those uniform hypotheses or an unconditional integer
multiplication theorem. The selected repository result is unchanged.

Marius-Paul Dumitrean, with substantial OpenAI Codex assistance. Apache-2.0.
Source attribution and source-specific notices are retained in `NOTICE`.
