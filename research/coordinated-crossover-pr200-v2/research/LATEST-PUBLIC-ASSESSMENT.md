# Final public refresh: pinned heads and bounded composition checks

All five new snapshots were fetched read-only, pinned at the exact requested commit, checked clean with autocrlf=false, stored on F:, and exposed through D: junctions. No upload files were changed and nothing was published. Full provenance records are collected in `FINAL-NEW-PINS.json`.

Logical snapshot roots under D:/proof/research/beyond-nlogn-20261009-threshold/public/:

- pr210-8e678c6bd379
- pr213-b7af69342990
- pr212-9b6ad038f869
- pr208-5fcb7111a065
- pr197-8c5e1cf07c23

Physical roots are the same suffixes under F:/proof/research/beyond-nlogn-20261009/threshold/public/.

## New PR210

New witness: `source/research/coordinated-crossover-pr200/frames/opframe-bases.json`. It is the same list-of-[operation,basis] schema consumed by the native admission executable. It changes only operation frames, so it can be checked on the pinned frames-pr211 physical/target graph and packed-pr211 ledger baseline; gains must never be added numerically.

Its full 6416-entry witness passes native admission: 4528 distinct prime frames, 150444 value-span inclusions, exact physical/target path containment, and unchanged chain mass405456. The updated native receipt counts 273 genuinely different subspaces versus its current baseline and 2125 versus its parsed raw word; the public note says274/2124 under its own comparison convention. Keep these explicit counts separate from the6416 listed bases. The saved receipt is `pr210-final-admission/FRAME-ADMISSION.json`; profile is `pr210-final-admission/new-profile.json`. Its published ?=8548253614663/12500000000000000 remains below our packaged ?=427415195711/625000000000000.

The concrete union first takes all6416 new public frames and then replaces our220 coupled-cut indices. It has6477 entries (159 overlapping indices,61 extra indices), and fails the actual frame-path check with the exact diagnostic `FAIL nesting failure`. Diagnostic is preserved in `pr210-plus-cut-admission/FAILURE.txt`. It supplies no admitted combined gain.

## New PR213

The frame witness is byte-identical to frozen PR211: SHA25656b2ed0f6b867e8cafdc32ac70419cfda36d02838844572098b3fc77f8026e58. Arithmetic contains exactly `range(5)` finite stopped-leaf levels, starting from the concrete unpacked ordinary atom. It claims ?=683847872497761/10^18. This is a finite-depth change, not a use of the unattained limit, and remains below our packaged ?. Our combined packed-atom route already reaches its selected grid point with four levels; the parent separately checked that five levels select the same ?.

## Sole requested fallback

After the union failure, the14 frozen equal-frame component replacements from new PR210 `search/additional-frames.json` were applied over the parent's complete6258 replacement list. All14 indices were already present, so the list stays6258 entries. This is a different candidate, not a free additive gain. Candidate is `F:/proof/research/beyond-nlogn-20261009/threshold/retrieval/current-plus-plateau14-bases.json`. Full admission is being checked in `current-plus-plateau14-admission/`; the final outcome is appended below.

## Final bounded composition outcome

The sole 14-operation plateau fallback also failed the exact chronological nesting check: `FAIL nesting failure`. All 14 indices overlapped the existing 6,258-entry replacement list, so the proposed list still had 6,258 entries. The proposed full 6,477-entry PR210-plus-cut union failed the same check. Neither failed composition has an admitted physical profile or a priced kappa; no gains were added.

The new PR210 witness alone passed full admission: 6,416 listed bases, 4,528 distinct prime frames, 150,444 required value checks, and unchanged chain mass 405,456. Its native comparison recorded 273 changed operations against the current baseline and 2,125 against the parsed raw word; those conventions are kept separate from the public note's counts.

The accepted combined claim remains kappa = 427415195711/625000000000000 = 0.0006838643131376. Five finite levels do not improve its fixed-grid price over four. All five requested public heads are pinned in FINAL-NEW-PINS.json. All acquisition, compilation, admission, and pricing jobs owned by this lane have finished. No upload files were changed and nothing was published.
