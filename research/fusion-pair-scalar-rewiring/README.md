# No H1+H1 → H2 fusion pair in the #4610 word by free scalar rewiring

**Negative result, no new κ.** #5226 (DreamingOfClouds) prices the whole gap between
Cao Yifan's #4610 word and the bar 0.0030233 as fragmentation loss, and #5243
(Clear1nsight) verifies the compiler target κ = 0.0030220 for one hypothetical
`H1+H1→H2` fusion per native call, asking for a physical pair. This package shows
that **no pair of consecutive rank-1 climbs on one field of the #4610 word can be
fused into one rank-2 climb by free scalar rewiring** (same-frame dyadic ADDs,
COPY/CLEAR of owned storage, any time, any field), in either orientation.

## What is checked (`verify.py`, 2 s, standard library)

Per orientation the word has 3,290 climbs, 2,201 of rank 1, and 1,363 pairs of
consecutive rank-1 climbs `E → F → G` on one field (509 fields).

| step | exact statement on the word | count |
|---|---|---|
| S1 | no pair is idle: some event touches the field while it stands in the intermediate frame F | 0 idle of 1,363 |
| S2 | pairs whose intermediate events are plain ADDs; in **every** one some partner field never occupies G at any time of the program, so the interaction cannot follow a merged climb | 1,261 of 1,261 |
| S3 | pairs whose partners all visit the start frame E (cold helpers at frame 0, helpers 241/240 … 417/416): each is blocked before the merged climb by exactly one main-field event on the partner at F, and that main never shares a frame with the helper later | 12, all blocked |
| relocation | frame-level relocation test (move every intermediate event to a time when field and partner share E or G, partner unchanged or only receiving commuting ADDs) | 0 relocatable |
| P | price order at t\* = 1 − 0.0030233: one fusion gains 2 − 2^t\* = 0.0041868 Λ per call; any repair that adds one paid rank-1 job costs 1; a descent costs ≥ 1.99022 (#5226 Theorem D); the bar needs 0.0209332 per call | always negative |

The remaining 102 pairs warp or scale the field between the climbs; warps are
bound to fixed frame pairs, so they are counted and left outside the claim.

Controls: deleting the single blocking main event of helper pair 241/240 makes
exactly that pair relocatable in both orientations (the test is not vacuous); a
corrupted climb rank is rejected by the nested-climb replay.

## Row-level searches (evidence, not replayed by CI)

`tools/compsearch.py` and `tools/cascade.py` run an exact rational row engine (the
convention of #5377's `native.py`) over the backward word and ask whether the
contribution lost by deleting the intermediate events can be repaid by free
same-frame ADDs whose exact rows span it: before or after the merged climb inside
the exact legal window (compsearch, 6 min), or anywhere downstream after
propagating through reads, warps and scalings (cascade, 50 min, greedy).
Results recorded in `RESULT.json`: 1,261 pairs, 2,111 deficits, 12 repayable
deficits (the partner-helper deficits of the 12 cold pairs, repaid at frame 0),
**0 fully repayable pairs**; cascade: 2,522 pair-variants, **0 successes**, 0
repayments. The forward word is the transpose of the backward word and shows
the same structural obstruction (S1–S3 are checked in both orientations).

## Reproduce

```sh
python3 -I -W error -B research/fusion-pair-scalar-rewiring/verify.py
python3 -B scripts/research_package.py --package research/fusion-pair-scalar-rewiring
# optional, minutes: exact row-level searches on the backward word
python3 -B research/fusion-pair-scalar-rewiring/tools/compsearch.py backward
python3 -B research/fusion-pair-scalar-rewiring/tools/cascade.py backward
```

Expected marker: `PASS_NO_FUSION_PAIR_SCALAR_REWIRING`.

## Scope

The claim is about the frozen #4610 word with its frames and native maps: a
fusion needs new frames or native maps (a changed mechanism), or an extra paid
transport for a partner, which never pays. Not covered: the 102 warp/scale pairs,
non-greedy repayment choices, owned-storage copies used as time shifters (they
cannot move content across frames), and relations among helper inputs (#5377,
#5383 and their audits). The forward row-level searches were not run to
completion.

## Open next questions

See `TASK.json`. The only way left to lower Λ by fusions is a changed native
word whose intermediate meeting frames are shared with G; pricing such a change
needs #5226's exchange table on the new word, not this one.

## Credit

Cao Yifan (intqwq, #4610) supplies the word; DreamingOfClouds (#5226) the
fragmentation framework and prices; Clear1nsight (#5243) the one-fusion target;
Ali Romman (#5377) the row convention. Mark (Matarener) with substantial Claude
Code (Claude) assistance. Apache-2.0; author-checked, not independent acceptance.
