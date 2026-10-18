# Two hostee moves and seven retired-lender aliases on the joint twelve-source words: conditional κ ≈ 0.001717794984118634663827

This package derives from PR2751 (Tekalign, @tekuuu; head `4cfbb0cc`). It extends PR2751's two words in two steps:

1. **Five retired-lender aliases** 606<-550, 635<-551, 637<-552, 638<-553 and 639<-562, the construction of the
   `t74-joint-twelve-retired5` package (Marius-Paul Dumitrean; local and unpublished, branch `t74-joint-twelve-retired5`, b295183e).
   It is reproduced here unchanged as the stages `refit5 -> alias5 -> refit5c`.
2. **New here: two hostee moves that free two more lenders.**
   - The hostees of B-warps 30 and 31 currently live on the lenders 401 and 403. Those lenders' own lives end in A, before
     helpers 667 and 669 enter at B259 and B262.
   - Each hostee moves onto a free retired lender: 401 -> 564 and 403 -> 565. Lenders 564 and 565 last act at B911 and B912,
     before the hostees enter at B941 and B944. Each moved warp record is replaced in place, so op ids 30 and 31 are kept.
   - This frees 401 and 403 for two more retired-lender aliases of PR2679's kind: **667<-401 and 669<-403**.

**What makes the moves feasible.** An exact frame refit: the last gates of 564 and 565 are lowered from rank 6 to rank 5, which is
their exact propagated frame floor. The moved hostees enter at rank 5 already, so no follower raise is needed. The new aliases are
fixed-frame: lender frame dim 4 = follower entrance dim 4. The certified optimal frames of the final program also lower B1170/B1171,
the next gates of 504/505, from rank 6 to rank 5.

**Exact claim.** The exact rational κ is `C - 10^-46 - 10^-70`, with `C = 0.001717794984118634663827` (in `CLAIM.json`). Larger κ is
better in `O(n (log n)^(1-κ))`. No selected frontier is edited, and PR2751's own directory is unchanged.

| compared with | its exact κ (pinned in `evidence/`) | margin of this package |
|---|---|---|
| PR2751 (tekuuu) | `0.001717141586348426338109 - 10^-46 - 10^-70` | `+6.53397770208325718E-7` (exact `326698885104162859/500000000000000000000000`) |
| PR2766 (DavidAriasC) | `0.001717256973467002308270 - 10^-46 - 10^-70` | `+5.38010651632355557E-7` (exact `538010651632355557/1000000000000000000000000`) |
| PR2767 (jeremykothe2) | `0.0017172569734670023082709447…` (3000-digit outer claim) | `+5.38010651632355556055E-7` |
| retired5 (local, unpublished) | `0.001717409316335491643448 - 10^-46 - 10^-70` | `+3.85667783143E-7` |

**What is new here, and what is credited.**
- The certified frames include PR2766's frame refit of PR2751's words, unchanged: B1151 rank 6 -> 5, plus A0-A11, B771-788 and
  restore 60. PR2767 reaches the same κ by another route.
- The five retired-lender aliases are the retired5 construction, worth `+1.52342868489E-7` over PR2766/PR2767.
- The **new contribution of this package is the two hostee moves and the two aliases they enable**, worth `+3.85667783143E-7` over
  retired5.

## Reproduce

From the repository root, with Python 3.12 and no third-party dependencies, run the registered hook. It completes in about two
minutes and is limited to 17 minutes:

```sh
python3.12 -B scripts/research_package.py --package research/t74-joint-twelve-retired7
```

It runs four commands:
- `verify.py`: PR2751's literal review, adapted below. It prints `PASS_JOINT_TWELVE_RETIRED7_FINITE_REPLAY` and checks 271728 owner roles.
- `verify_retired7.py`: the seven-stage rebuild, the pinned PR2679 auditor on all eight states, 142 tamper controls, the literal owner
  fill, the 80-digit root, and κ against PR2751, PR2766 and PR2767.
- `packing_cap.py`: the generic packing ceiling.
- `test_integrity.py`: relocation and fail-closed controls.

Full cold release: install `requirements.txt`, then use a fresh directory outside the repository:

```sh
python3 -B research/t74-joint-twelve-retired7/full_replay.py --source /path/to/pr2679/research/gmx-t74-borrow43-handoff --work /tmp/FRESH-retired7
```

Without `--source`, the 491 pinned PR2679 files are downloaded and authenticated, exactly as in PR2751. The run then:
- applies this package's 36-file overlay: PR2751's 21 files, retired5's six stage inputs, the eight retired7 stage inputs and
  `new/borrow/retired7_controls.py`;
- builds four fresh native providers and the retained-parent admission;
- runs the complete admission: owner reconstruction, parent lift, rebind, discovery/unpin/freeze at PR2751's 24-digit endpoint
  precision, the outer ledger and the package's own `verify_release.py` (strict T74 replay and all controls).

Expected result: `PASS_T74_JOINT_TWELVE_COLD_COMPLETE_RELEASE 0.0017177949841186346638269999999999999999999998999999999999999999999999` (recorded cold run of the committed package: 411 s; see `evidence/retired7/FULL-REPLAY-RESULT.json`).
`--prepared-native-cache` is not supported: `REUSE-PINS.json` is PR2751's and describes PR2751's cache.

To regenerate all four words (PR2751's two, then this package's two through the declared stages) from source:

```sh
python3 -B research/t74-joint-twelve-retired7/generate.py --source /path/to/pr2679/research/gmx-t74-borrow43-handoff --out /tmp/FRESH-retired7-words
```

Expected: `PASS_REGENERATED_JOINT_TWELVE_RETIRED7_BOTH_WORDS`.

## Construction and cost

**Census** (on the retired5 words, with PR2679's exact frame lattice `new/borrow/refit/search` and the `pairs.py` rule):
- 52 followers remain. 48 enter at rank 1 (width 8) and 4 at rank 4 with ceiling 5 (width 5): 667, 669, 670 and 671. There are 404
  lenders, and no direct pair or chain is feasible.
- Every rank-1 follower stays infeasible, because every lender's exact floor is at least rank 4.
- Every existing B-warp hosting is treated as movable. 24 hosted lenders (warps 1-4 and 22-41) end their own lives before B259, with
  floor rank 4, and could take a rank-4 follower if their hostee moves to a free lender. Only two free lenders have floor <= 5 and
  retire before the hostees enter: 564 and 565.
- That gives 192 augmenting paths and at most **two** extra aliases.
- Warps 30 and 31 are chosen because their hostees already enter at rank 5. Moves of warps 1-4 or 22-29 need a 16-gate raise closure
  and price lower.

**Stages.** These are new stages of `new/rebuild_borrow.py` inside the overlay, run after retired5's `refit5c`:
- `refit7_43*.json`: two frames per word. The last gates of 564/565 (B911/B912) go from dim 6 to 5, recorded with their previous frames.
- `hostmove2_43*.json`: two warp records replaced in place (op 30: 401 -> 564 at B941; op 31: 403 -> 565 at B944; dim 5, explicit
  invertible `G`, `G(U)=E`), and 28 declared gate edits, which relabel the 14 hostee gates. Nothing else changes.
- `alias7_43*.json`: `alias_build.alias` 667<-401 and 669<-403, with dim 4 warps appended, 28 declared gate edits, and both helpers removed.
- `refit7c_43*.json`: the certified optimal frames of the final program, two frames (B1170/B1171, dim 6 -> 5), computed with the
  #1186 exact frame toolkit (`optimal_frames`, borrow-word model, certified).

Every one of the eight states passes the auditor.

**Inventory and profile.**
- 408 helpers {4:26, 5:2, 7:62, 8:78, 9:240}, 72 private buffers, 666 calls and 271728 hosted roles.
- live 66304; physical 66794 = 66304+408+8+72+2.
- Local profile `{1:2382,2:648,3:268,4:128,5:26,8:8}` on both words, against `{1:2386,2:642,3:274,4:128,5:26,8:8}` for retired5.

**Owner fill.** It is PR2751's fill with the seven removed helpers' roles dropped, renumbered and re-tiled as bin prefixes (`verify.py`
`compact`). The 1332 cells freed beyond retired5 become idle 5-remainders.
- Complete profile `{1:1603728,2:431568,3:185082,4:85248,5:27194,8:5328,32:1,48:26558}`; rank mass 4816512; idle `{1:17316,3:6594,5:9878,32:1,48:26558}`.
- The pattern relaxation of the owner fill (8/16/32/48 bins, the r8 model) has the same optimum as this realized compaction.
- The exact moment root lies strictly between `0.001717794984118634663827` and `0.001717794984118634663828`.
- The 80-digit root is `0.00171779498411863466382722991842817890408858438546231220090092725676198114516931`.

**Packing ceiling.** The generic coverage-law ceiling (`packing_cap.py`, the pinned `ceiling.ceiling()`) is about `0.00175808593463`,
with realized fraction `0.9770824908`. It is a packing cap, not a sharp optimum.

## Checker adaptations (diffs in `RETIRED7-CODE.patch`; the retired5 adaptations are in `RETIRED5-CODE.patch`)

1. **`verify.py`.** The candidate profile and endpoint are re-pinned. The declared stage chain gains `refit7 -> hostmove2 -> alias7 -> refit7c`.
   The compaction now removes seven helpers: the five retired5 ones plus 667 and 669.
2. **`verify_retired7.py`** (replaces `verify_retired5.py`). It adds the retired7 stage-structure checks and audits all eight states.
   It also runs `retired7_controls.py`, 25 controls per word, on top of retired5's 46 per word. The owner fill size is R 408.
3. **`retired7_controls.py`** (new; also in the overlay as `new/borrow/retired7_controls.py`, called by `rebuild_borrow.py`). Every
   mutant has its inverse-reverse cleanup re-derived, and a rejection for a stale-cleanup reason counts as a failure. The controls are:
   - each lender refit undone, which must be rejected by `warp frame mismatch`;
   - per move: warp lender reverted, move undone, warp before the new lender retires, and `G` wrong;
   - PR2679's alias suite on each new alias: borrowed read sign flipped, read doubled, write sign flipped, warp dropped, `G` wrong,
     warp after the follower's first gate, and helper kept with an entrance frame. "Warp after the first gate" replaces "warp before
     lender retirement", because these lenders retire in A, which leaves no B position before retirement;
   - one certified frame corrupted.
4. **`workflow/admit.py`.**
   - The derived-source pin is `9c72b4301057a6c204c40bb6584eb74b779e06618bcd98d706d726c3e2c92451`, with 506 files instead of 497.
   - The physical stock is 66794 instead of 66796 (R 408).
5. **`new/rebuild_borrow.py`** (overlay). It has the four stages with exact structure checks, and the retired7 controls call.

`generate.py`, `packing_cap.py` and `test_integrity.py` change only the stage list, the expected candidate values and the markers.
`independent_owners.py` is unchanged from retired5: it reads `R` from the providers.

## Verification and controls

**Full cold release.** `evidence/retired7/FULL-REPLAY-*.json`.
- All four native providers are fresh, with five stages each.
- The retained-parent admission passed.
- The complete admission passed: owners, parent lift, rebind, discovery, outer ledger and independent derivation.
- The package's own `verify_release.py` returned `PASS_RELEASE`. Its `rebuild-borrow-words` stage includes the retired5 and
  retired7 stage checks and controls.

**Registered hook.** It repeats the seven-stage rebuild with the vendored, byte-identical PR2679 auditor and all 142 tamper controls,
plus the literal owner fill and the exact arithmetic.

**Precision.** The endpoint is certified at `10^-24`: accept at `C`, reject at `C+10^-24`, with exact rationals. That is 16 orders of
magnitude below the `3.86e-7` margin over retired5. κ = `C - 10^-46 - 10^-70` exactly.

## Scope and inherited obligations

Finite exact admission is conditional evidence, not a formal proof of the complete multiplication theorem. The following remain
inherited from PR2751 and its lineage unchanged:
- all-size compiler and machine realization;
- common labels and source access;
- physical hosting and routing;
- precision and fixed-tape contracts;
- exact recovery and analytic transfer;
- recurrence;
- the bit-supplier and modern outer obligations.

No new discharge of those universal obligations is claimed. The selected accepted result and this pending derivative are distinct.
The census searched retired-lender aliases, with every existing B-warp hosting movable onto a free retired lender. No optimality is
claimed over other mechanisms.

## Credits

- **Tekalign (@tekuuu), PR2751:** the joint twelve-source construction, words, fill transform, independent checkers and full replay (the parent).
- **Cinna Davis (1337isnot1337), PR2226:** anticipatory dirty borrowing. Warps 30/31 are its borrows: helpers 603 and 605 borrow
  from lenders 401 and 403, as adapted to the T74 words.
- **Philippe Van Velzen (philippeVV), PR2679 (and PR2559):** the six pre-life hostings, the one-gate frame refit and the retired-lender
  alias 653<-563, which is the mechanism re-used for all seven aliases; also the exact refit/search frame tools and the alias builder.
- **Jeremy Kothe (jeremykothe2), PR2673/PR2745:**
  - the priority call order and window-optimal owner fill;
  - the composition of PR2696 with PR2679;
  - the gmx-t74-borrow43 package machinery, entrance raises and BORROW-WORD lineage (PR2588, PR2575, PR2526, PR2474, PR2462, PR2447,
    PR2435), including the T74 adaptation of PR2226's borrows and the base-word lenders 564/565.
- **Mason Hale, PR2696:** the eight-lender assignment.
- **DavidAriasC, PR2766:** the frame refit of PR2751's words, which is included in the certified frames.
- **Vlado Vojdanovski (Vlado-V), PR2322:** the coherent handoff.
- **Our PR1625:** the pivot-kernel shape. **Our PR1186:** the exact frame toolkit. **Our retired5 package:** the five aliases.

All notices and the lineage these packages retain are kept: see `SOURCE-NOTICE`, PR2751's `README.md` and `PROOF.md`.

## Open next questions

1. **Gate-level edits.** Can a gate-level (kernel) edit make the 48 rank-1-entrance followers alias-feasible? Every lender's exact floor is at least rank 4.
2. **Followers 670 and 671.** Both still lack a lender: the only free floor-5 lenders (564/565) are used by the moves. A third free
   lender would need a frame floor of at most 5 and retirement before B941.
3. **Stacking with PR2767.** Do these stages stack with PR2767's post-cut partner correction, or with other post-PR2751 constructions?

Prepared by Marius-Paul Dumitrean with substantial AI assistance (Anthropic Claude, via Claude Code). Apache-2.0.
