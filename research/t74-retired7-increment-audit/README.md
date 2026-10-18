# Independent verification (no κ): #2802's seven-stage increment over #2751 (retired5 + retired7 stages); covers #2818's identical construction

**Status: independent verification (no κ). No defect found: all 28 named rules pass, and all 20 negative controls are
rejected by their named rules (7 of them must also be accepted by named rules, and are). A pass is necessary but not
sufficient for any T74 claim built on this construction. The T74/#1319 supplier admission, native lowering and PR1673
outer proof are still required. No selected frontier is changed.**

## What this decides

Refreshed 2026-10-16 02:10 UTC. PR heads are unchanged at the pins below.

1. **The word construction.** #2802's seven declared stages turn PR #2751's two BORROW-WORDs into the words with git
   blobs `91bd9c68f209…` (base) and `6c4a9a4395cf…` (extra). Fresh code checks this construction independently, and
   separates it from #2751 and PR #2766. Seven pending claims build on it:
   - #2802 and #2818 ship these words unchanged.
   - #2824 (head `f1826afe`), #2827 (head `4dc1286a`) and #2839 (head `2fdd289f`), all by Dugongue, vendor these words
     and #2802's fill (`6441c0be…`), then re-allocate or re-price.
   - #2833 (jeremykothe2, head `e9307b48`) uses #2818's `retired7_43{base,extra}.json` patch blobs (`f5497db5…`,
     `2e02c6a6…`) unchanged, then adds a `dirtentry` stage.
   - #2843 (mdumitrean, head `47a7227c`) merges #2833, #2824 and #2827, and adds a T124 allocation on #2833's words.

   These blob identities were read from the GitHub pull-request file lists at 02:10 UTC. They are not part of the
   verifier. Further downstream candidates on this base are being discussed in #2612; this list is dated.
2. **#2802's two changed acceptance checks.** Neither is an acceptance gap for κ.
   - R is bound to the words.
   - Alias occupancy holds for the shipped words. No check on the model's pricing path reads it, so in the finite
     model it is a conformance property, not a soundness condition for κ.
3. **Not covered.**
   - #2824/#2827's allocations, fills and reserves; #2839's block-norm accounting.
   - #2833's `dirtentry` stage and its re-derived fill; #2843's T124 allocation.
   - #2818's 10⁻³⁰⁰⁰ endpoint.
   - Native lowering, supplier admission and the outer proof.

## Reproduce

From the repository root, with `git` and Python (standard library only), in about 2 minutes and under 0.6 GB RSS:

```sh
python3 -I -B research/t74-retired7-increment-audit/verify.py --fetch
```

`--fetch` downloads `refs/pull/{2802,2751,2818,2766}/head` only when a pinned commit is absent, and writes only
`FETCH_HEAD`. Every input is checked against its sha256 pin in `increment_audit.py` (`PINS`). A missing or mismatching
input prints a `FAIL_T74_RETIRED7_INCREMENT_AUDIT inputs: …` line (exit 1). Expected last line:

```text
PASS_T74_RETIRED7_INCREMENT_AUDIT rules=28/28 controls=20/20 commit2802=17b2ee6ef3cf commit2818=175822aee7a1
```

`--out RECEIPT.json` rewrites the deterministic receipt shipped here. It records every rule's details, and for every
control its failing rules and the expectations it met. If the local zlib does not reproduce #2802's `FILL.json.gz`
bytes, a `NOTE:` line reports the fallback described under "Separating the new construction from its ancestors".

**Python versions.** Only Python 3.14 has been run. `VERIFY.json` registers the same argv for the repository hook
(`scripts/research_package.py`), which pins Python 3.12. That hook was **not** replayed locally, because only 3.14 is
installed; `--check-only` metadata validation passes. The sources parse under Python 3.10 syntax but were not executed
there.

## Terms

- **W2751, W2802.** The parent words (#2751) and final words (#2802). There are two of each: `base` and `extra`. The
  providers, the fill dispatch and #2802's code call the base word's provider `gauge44`.
- **Stages.** The *retired5 stages* are `refit5 → alias5 → refit5c`. The *retired7 stages* are
  `refit7 → hostmove2 → alias7 → refit7c`. "retired7" in file and rule names follows #2802's package name
  (`t74-joint-twelve-retired7`). In this text it means only the last four stages.
- **Alias, lender, follower.** In an alias h←L, a removed *follower* helper h reuses the register of a *lender* L
  after L's own life. A B-warp K_G on L marks the hand-over. A *hostee move* re-hosts an existing warp's hostee on a
  different lender.
- **Occupancy.** No lender event occurs at or after its alias warp, and no follower event occurs before it.
- **Dead write.** A write to a lender after the lender's last read in its own life. For 401 the last read is A3159
  (`add 400 += −1·401`), and A3160, A3163, A3167 and A3175 are dead writes.
- **Numbering.** "Warp N" is #2802's 1-based op id: the record `warps[N−1]` of the word. Gate positions such as A3175,
  B259 or restore60 are 0-based indices into their section.

## Statement

PR #2802 (Marius-Paul Dumitrean, head `17b2ee6ef3cf1468e78a6267f0ecbc9a0e6f60dd`, `research/t74-joint-twelve-retired7/`)
turns PR #2751's two T74 BORROW-WORDs (Tekalign, head `4cfbb0cc8314d7fb4e8e754545a49a42eb590a69`) into new words in
seven declared stages. Together these contain:
- seven retired-lender aliases: 606←550, 635←551, 637←552, 638←553, 639←562, 667←401 and 669←403;
- two hostee moves: warp 30 from 401 to 564, and warp 31 from 403 to 565;
- the refit frames.

#2802 then drops the seven followers' roles from PR #2751's owner fill. It claims κ = C − 10⁻⁴⁶ − 10⁻⁷⁰ with
C = 0.001717794984118634663827, which is +5.38×10⁻⁷ over #2766/#2767.

We wrote fresh standard-library code and ran it on both words. PR code was read only as pinned data, never imported
or executed. All arithmetic is exact, except the moment-root bracket in item 7, which is rigorous through a written
error budget. The matrix realisation in item 3 is a randomized second method; the free-algebra replay is the exact one.

1. **S1 event diff.** Every difference between W2751 and W2802 is a declared stage edit.
   - **Relabels.** Exactly 63 B gates are relabelled: 35 by `alias5`, 14 by `hostmove2` and 14 by `alias7`. They sit at
     exactly the positions of the declared delete/insert pairs.
   - **Frames.** Exactly 62 frames change: 26 by `refit5`, 32 by `refit5c`, 2 by `refit7` and 2 by `refit7c`. Each is
     present at its declared final value.
   - **Warps and helper lists.** Warps 30/31 are replaced in place and warps 66–72 are appended. `removed` gains the
     seven followers, and `start_extra` loses only them.
   - **Everything else is unchanged** (equal as parsed JSON): `ports`, `centers`, `center_frames`, `target_levels`,
     `precondition`, `compensation`, `initial_corrections`, `prelude_events`, `helper_final` and `cut`. A, restore and B
     keep their lengths, and their gates are unchanged apart from these relabels.
   - **Stage rebuild.** Substituting each stage file's fields, as #2802 does, and re-deriving the cleanup reproduces
     W2802 exactly. This checks that the stage files are consistent; it is not an independent derivation. The
     independent evidence is the S1 diff plus `S1-STAGE-RECORDS`. Every intermediate state passes the frame chain, its
     declared profile and inventory, and both replays. Profiles (helpers, mass) per state:
     - `refit5`: 415, 5223;
     - `alias5`, `refit5c`, `refit7` and `hostmove2`: 410, 5198;
     - `alias7` and `refit7c`: 408, 5188.
2. **S2 occupancy timeline.** Each register's forward event list (corrections, wrapper, A, cut, B, restore) is split at
   that register's warps. That gives 704 segments: 632 live registers + 72 B warps in the final word, and 639 + 65 in
   the parent. The count equals the size of the register namespace because, in both words, there are as many removed
   registers as warps. Every final segment is exactly one parent role, with the same events and the same gates up to
   the declared relabel, in time order. The new warps:

   | follower ← lender (warp) | lender's last own event | warp before | follower's first event |
   |---|---|---|---|
   | 606 ← 550 (66) | B901 | B947 | B947 |
   | 635 ← 551 (67) | B902 | B1024 | B1024 |
   | 637 ← 552 (68) | B909 | B1027 | B1027 |
   | 638 ← 553 (69) | B910 | B1030 | B1030 |
   | 639 ← 562 (70) | B903 | B1033 | B1033 |
   | 667 ← 401 (71) | **A3175** (27 A + 54 compensation events) | B259 | B259 |
   | 669 ← 403 (72) | **A3174** (26 A + 60 compensation events) | B262 | B262 |
   | hostee of warp 30 → 564 | B911 | B941 (was B941 on 401) | B941 |
   | hostee of warp 31 → 565 | B912 | B944 (was B941 on 403) | B944 |

   Further checks on the timeline:
   - No lender has a restore event, and no follower has an event before its warp.
   - The old lenders 401/403 keep no hostee event.
   - The cleanup is the exact inverse-reverse of the recorded program. It is re-derived and equals the shipped
     4,547 items. Within each register's cleanup, the order is therefore mirrored: follower, inverse warp, lender.
   - The dual orientation applies g⁻ᵀ item by item in the same order, and each g⁻ᵀ touches the same registers as g. So
     the timeline, and this check, are the same in both orientations.
3. **S2 replay.** An exact replay over ℚ⟨free group⟩ treats all 632 live registers as independent dirty symbols and
   the 72 private zero buffers as zero.
   - It passes forward (Yᵢ ← Yᵢ + Xᵢ) and dual (Xᵢ ← Xᵢ − Yᵢ). The dual treats K⁻ᵀ as new free letters.
   - Before cleanup, each restored helper is its own input and is read by no other register.
   - A second, independent method realises every K_op as a random invertible 4×4 matrix over GF(2⁶¹−1), with K⁻ᵀ the
     actual inverse transpose. It also passes forward and dual, for 2 seeds.
4. **S3 frames.** The check covers 72 B warps and 24 prelude warp items. For each:
   - G is invertible over GF(2), dim U = dim E, G(U) = E and G⁻ᵀ(U^⊥) = E^⊥;
   - the binary-symplectic image of K_G is symplectic and maps L_U onto L_E.

   Each B warp's U equals the lender's **actual propagated frame**, taken from our own literal frame chain. The new
   and moved warps are 30, 31 and 66–70 (dim 5) and 71–72 (dim 4). Every gate climbs monotonically.

   Refit exactness, against the propagated floor (the join of the incident registers' pre-gate frames):

   | stage | frames at the floor |
   |---|---|
   | `refit5` | 26/26 |
   | `refit7` | 2/2: B911/B912, dim 6→5 |
   | `refit7c` | 2/2: B1170/B1171, dim 6→5 |
   | `refit5c` | 25/32 |

   Seven `refit5c` frames sit above the floor: B771, B773, B776, B778, B783 and B788 (dim 5, floor 4), and restore60
   (dim 8, floor 6). **They cost nothing.** Lowering any one of them, or all seven, to the floor keeps the chain legal
   and leaves the local profile unchanged (`S3-ABOVE-FLOOR-NEUTRAL`). They are #2802's own `refit5c` choices; PR2766's
   word does not contain them (see the attribution section below).
5. **S4 profile.** Our recount gives the local profile `{1:2382,2:648,3:268,4:128,5:26,8:8}` (mass 5188) on both words.
   - This equals the word reports and both providers' `actual_paid_profile`.
   - A second frame chain represents subspaces by canonical reduced bases instead of element sets. It gives the same
     profile and inventory, confirms every warp's U and G(U) = E, and reproduces the parent's profile.
   - The width inventory is `{4:26,5:2,7:62,8:78,9:240}` = 408 helpers. The ordered widths dim(end) − dim(entrance)
     equal the providers' `widths`.
6. **S5 fill with word-derived R.** R = 408 and the per-helper widths are derived **from the words**, not from the
   providers.
   - The fill's 271,728 = 666 × 408 roles cover each call's helper set exactly once.
   - Each role lies strictly inside its window. We rebuilt the 1,332 windows from GLOBAL-TEMPLATE and ORDER.
   - No family hosts two helpers in one call.
   - Bins are disjoint, within capacity and prefix-compact. The idle remainders are
     `{1:17316,3:6594,5:9878,32:1,48:26558}`.
   - Independently, FILL equals FILL2751 minus exactly the 4,662 = 666 × 7 roles of the seven followers, with every bin
     and in-bin order preserved over 122,625 bins.
7. **S6 price (repeat check).**
   - The complete profile is `{1:1603728,2:431568,3:185082,4:85248,5:27194,8:5328,32:1,48:26558}`. Its mass is
     4,816,512 = 2·73·33,152 − 2·11,840.
   - Let f(z) = Σ nᵣ (r/73)^(1−z). Then f(C) < 66,304 < f(C + 10⁻²⁴).
   - f is evaluated at 80 digits. Python's Decimal `ln`/`exp` are correctly rounded, half-even, whatever the context
     rounding mode; the other operations use directed rounding. A written error budget, in `root_bracket`, bounds the
     relative error below 3×10⁻⁷⁸. The bracket is widened by a 10⁻⁷⁰ relative slack in a 100-digit directed context.
   - After widening, f(C) is 4.36×10⁻²⁰ below 66,304 and f(C + 10⁻²⁴) is 1.46×10⁻¹⁹ above it.
   - κ = C − 10⁻⁴⁶ − 10⁻⁷⁰ exactly. The margins are:
     - over #2751: `326698885104162859/500000000000000000000000`;
     - over #2766: `538010651632355557/1000000000000000000000000`;
     - over #2767: 5.380106516323555560552…×10⁻⁷.
8. **#2818 (Jeremy Kothe, head `175822aee7a1858ec653f7f92d7a750aec2c2795`).**
   - These files are byte-identical to #2802's: its words (`new/borrow/words/BORROW-WORD-43{base,extra}.json.gz`),
     `new/borrow-fill/FILL.json.gz`, `ORDER.json` and `new/BORROW-PROVIDERS.json`.
   - Its DISPATCH is the same map, and every field of its `retired7_43{base,extra}.json` patch equals #2802's final word.
   - The verdict above therefore covers #2818's construction. Its 10⁻³⁰⁰⁰ endpoint certificate is not checked here.

**Positive control.** The same code runs on the #2751 parent. It reproduces that profile
`{1:2366,2:646,3:297,4:120,5:26,8:8}` (415 helpers), both replays, and the parent fill of 276,390 roles with R = 415.
The fill's complete profile equals #2751's claim.

## Separating the new construction from its ancestors

#2802's κ composes three steps over #2751. Each is priced here with the same code and bracketed with the same root
evaluator. #2802's README already states this split, and #2802 records retired5's endpoint, fill hash and local
profile in `evidence/retired5/`. This audit **independently reproduces** those recorded values; it does not originate
them.

| step | what is checked | endpoint C (root in [C, C + 10⁻²⁴]) | gain |
|---|---|---|---|
| PR2766 (DavidAriasC) | PR2766's own pinned word differs from W2751 only at B1151 (dim 6→5), the same frame as #2802's `refit5c`. Recounted, it gives PR2766's reported local profile (H1 −2, H2 +1 per call). With FILL2751 that yields PR2766's claimed complete profile. | 0.001717256973467002308270 | (PR2766's claim) |
| retired5 stages: `refit5`, `alias5`, `refit5c` | Rebuilt as the `refit5c` state. Its fill is FILL2751 minus the five followers, re-tiled. Local profile `{1:2386,2:642,3:274,4:128,5:26,8:8}` and endpoint equal #2802's records. The reconstructed fill's gzip sha256 equals #2802's recorded `3501f6bd…` (see the note on the fill hash below). | 0.001717409316335491643448 | +1.52342868489335178×10⁻⁷ over PR2766 |
| retired7 stages: `refit7`, `hostmove2`, `alias7`, `refit7c` | All rules above | 0.001717794984118634663827 | **+385667783143020379/10²⁴ ≈ 3.857×10⁻⁷ over retired5** |

**Provenance of the 20 frames.** #2802's README lists "PR2766's frame refit … B1151 … plus A0–A11, B771–788 and
restore 60". PR2766's own word changes **only B1151**. The other 19 `refit5c` frames are not in PR2766's word:
A0–A11 (dim 1→0), B771/773/776/778/783/788 (4→5) and restore60 (6→8). They are cost-neutral. Applied alone to W2751,
they leave its profile unchanged. Reverted to W2751's values in the final word, they leave the final profile unchanged
and the chain legal. Together with B1151 they give exactly PR2766's profile. All seven above-floor frames are among
these 19.

**Who did what.** Both steps are first published in #2802 by the same author. Retired5 was the author's local branch.
Its words are not shipped as files, but they are rebuilt here from #2802's published stage files (`S1-STAGE-CHAIN`).
Only its fill is unpublished; #2802 records its endpoint, local profile and fill hash. The part #2802 labels new is the
retired7 stages.

**Note on the fill hash.** #2802 hashes the gzip bytes of its fills, and gzip output depends on the zlib build.
`ATTRIBUTION-RETIRED5` first checks that our serializer reproduces #2802's pinned `FILL.json.gz` bytes exactly. Only
then does it compare the reconstructed retired5 fill with #2802's recorded `fill_sha256`. This was the case on the
machine that produced the shipped receipt (zlib 1.3.1; `fill_gzip_sha256_equals_recorded: true`). Otherwise the rule
reports that comparison as not applicable and still requires the reconstruction's canonical-JSON sha256 to equal a pin
recorded here (`ef4bd5d4…`, the same fill content), and `verify.py` prints a `NOTE:` line. The same serializer does
not reproduce #2751's `FILL2751.json.gz` bytes; that file is never compared by gzip hash.

## The two acceptance checks #2802 changed

**R read from the providers.** `independent_owners.check` sets R to the length of the providers' widths, and those
widths are themselves under test. This is **not an open gap**:
- #2802's `verify.py` `compact()` requires the new provider widths to equal the parent widths re-indexed by the
  word-derived live set.
- The inherited ENTRANCE-WIDTH-BINDING stage of `new/rebuild_borrow.py` binds the word-derived widths to the providers.
  Its code is present both in #2802's overlay and in #2818. #2802's recorded release logs show
  `ENTRANCE-WIDTH-BINDING ... bound True` for both words (author-recorded; not re-run here).
- Our S5 makes the binding explicit and independent. Control C8 keeps follower 667 live: providers and fill still say
  408, but the words say 409. Control C11 adds helper index 408. `S5-FILL-WORD-DERIVED-R` rejects both.

**Alias occupancy and the replaced control.** For `alias7`, #2802 replaced the control "warp before lender retirement"
with "warp after the follower's first gate", because 401/403 retire in A. Only 401/403 do. Lenders 550–553/562 retire
in B (B901–B910) and keep the original control. No shipped control moves 401's or 403's own event past its alias warp,
so we built such mutants from their A events. 401's last read is A3159 and its last write is the dead write A3175
(`add 401 += 41`). 403's last read is A3145 and its last write is the dead write A3174. The table summarises the
mutants:

| mutant | both scalar replays | frame chain (S3S4, second recount, refits) | fill (S5) and price (S6) | rejected by |
|---|---|---|---|---|
| C4a 401 / C4c 403: last (dead) write moved into B right after the alias warp, own frame | accept | reject: `frame not monotone` at B259 / B262 | S5 accepts; S6 fails only because S3S4 failed | the frame chain. OCC, S1-DIFF and S1-STAGE-RECORDS report errors caused by the inserted B gate shifting later B indices and warp positions; these fire first, and OCC's segment-equality check would also reject the moved event, which lies inside the lender's final segment. X-2818 fails on any edit |
| C4b 401: last (dead) write moved to the end of restore, own frame | accept | reject (not monotone) | S5 accepts; S6 fails as above | OCC (`final segment of 401 … not exactly follower 667`) and the frame chain; S1-DIFF/X-2818 as an undeclared edit |
| C4d 401 / C4e 403: last (dead) write moved to the end of restore **at frame FULL** | accept | **accept** | **accept**: profile, fill and price unchanged | **only** OCC-TIMELINE, plus S1-DIFF and X-2818 as an undeclared edit |
| C4f 401: last read (A3159, `add 400 += −1·401`) moved to the end of restore at FULL | **reject**: `forward target 0 wrong before cleanup` | accept | accept | the replays; OCC, S1-DIFF and X-2818 |
| C4g 401: last write *before* its last read (A3158, `add 401 += 400`) moved to the end of restore at FULL | **reject**: matrix `wrong on register 112`, free `forward target 0 wrong before cleanup` | accept | accept | the replays; OCC, S1-DIFF and X-2818 |

The verifier checks the C4a–C4c replay cells and every cell of the C4d–C4g rows as `must_accept` and `exact_failing`
expectations. The other cells are read from each control's recorded failing set in `RECEIPT.json`.

This has three consequences.

1. **Occupancy is a conformance property, not a soundness condition for κ, in the finite model.** No rule on the
   model's pricing path reads occupancy. Our replays, frame chain, recount, fill and price do not, and neither does the
   pinned PR2679 auditor (read, not run). A word that violates occupancy but passes those rules is therefore correct in
   the model's sense and is priced by its own profile. C4d/C4e show that such words exist; here their price is
   identical.
   - *Why C4d passes.* The moved write is dead. Follower 667 borrows the register dirty, and the targets come out the
     same with the changed content it finds there (both replays confirm this for these words). The cleanup is
     re-derived as the inverse-reverse of the whole recorded program, so it undoes the moved write first.
   - *What the replay catches.* A moved read (C4f) or a moved write that the lender still reads (C4g) changes what is
     computed, and both replays reject it.

   These are examples, not a classification of every possible occupancy violation. The structural statement above is
   what carries the conclusion.
2. **Which checks enforce occupancy** (all read, not run):
   - **#2802.** The registered `verify_retired7.py` enforces it structurally, not semantically.
     - Every stage must leave A and restore unchanged apart from declared refit frames ("alias5 records",
       "hostmove2 changes nothing else", "alias7 records"). The final word must equal the rebuilt chain ("declared
       stages rebuild the candidate word"). No event of 401/403, which lie in A, can therefore move.
     - On the pre-alias states it checks "lenders retired before their followers enter" (retired5, on W2751) and
       "alias7 lenders retired before their followers enter". After `hostmove2` it checks "old lenders untouched after
       their A lives".
     - The `alias5`/`alias7` B edits are checked only against their own declarations (`kernel_gate_edit` equals
       `declared_gate_edit`). #2802 checks that an edit is exactly a relabel from the warp position only for
       `hostmove2`. That the declared alias edits are exactly the follower relabels is established here by S1-DIFF and
       S1-STAGE-RECORDS.

     The pinned PR2679 auditor and the retired7 tamper suite contain no occupancy predicate. Their monotone climb
     should reject C4a/C4b/C4c-type mutants. We expect them to accept C4d-type mutants, since our implementations of
     the same replay, frame chain and profile do.
   - **#2818.** `rebuild_borrow.py` applies retired7 as one patch whose A, B, removed, start_extra and warps fields
     replace the parent's. Its checks are: the B edit equals the patch's own declaration, some fields are unchanged,
     the final word equals the rebuilt state, plus the auditor and five stage controls. We found no occupancy predicate.
     #2818's words are byte-identical to #2802's, so OCC-TIMELINE establishes occupancy for them directly.
3. **What is missing is at most a regression control**, not an acceptance check. A control that expects
   `frame not monotone` would not cover C4d-type moves. An optional regression control could add a C4d-type mutant
   against #2802's stage-structure check, or an occupancy predicate to #2818's patch check. Neither is needed for κ in
   the finite model.

Unchecked here: whether any layer outside the finite model relies on occupancy, for example a native lowering or
physical hosting that assigns one role per register segment. PR2226 `PROOF.md` §1 speaks of a "retiring field". Its
identity, that R_in = T_E K_G T_U⁻¹ has Fourier rank zero, is an exact operator-level (Clifford) statement, phases
included, and does not refer to the field's later use. This audit checks only its model-level conditions: G(U) = E,
G⁻ᵀ(U^⊥) = E^⊥ and K_G(L_U) = L_E, with U the propagated frame. C4d satisfies them. The exact native form is Open Q3.

## Negative controls

A control counts only if the named rule rejects the mutant, every `must_accept` rule accepts it, the failing set
matches `exact_failing` where one is given, and no rule crashes. The cleanup of every word mutant is re-derived from
its own forward program, so a stale cleanup is never the reason for a rejection. Each mutant is re-checked by every
rule except four kinds: the parent positive control, the stage-chain rules, the attribution rules and the above-floor
neutrality rule. Those rebuild, reprice or vary unmutated inputs, and run once on the pinned inputs. Word controls
mutate the base word unless marked *extra*; C8 mutates both words, C11 the fill and C14 #2818's copy of the base word.

| control | rule | reason recorded |
|---|---|---|
| C1 `refit7` B911 undone (dim 6) | S3S4-FRAMES-PROFILE | warp frame mismatch: op 30 lender 564 |
| C2 hostee move 401→564 reverted | OCC-TIMELINE | follower 667 outlives the segment (401 would host 667 and hostee 30 at once) |
| C3 warp 66 placed before lender 550's last gate B901 | OCC-TIMELINE | lender 550 has an own event at/after its alias warp |
| C4a 401's last (dead) A write moved into B after warp 71 | S3S4-FRAMES-PROFILE | frame not monotone: register 401 at B259 (both replays must accept) |
| C4b 401's last (dead) A write moved to the end of restore | OCC-TIMELINE | final segment of 401 after warp 71 is not exactly follower 667 (both replays must accept) |
| C4c *extra*: 403's last (dead) A write moved into B after warp 72 | S3S4-FRAMES-PROFILE-extra | frame not monotone: register 403 at B262 (both replays must accept) |
| C4d 401's last (dead) A write moved to the end of restore at FULL | OCC-TIMELINE | final segment of 401 after warp 71 is not exactly follower 667. Must be accepted by the replays, frames, recount, refits, stage records, fill and price; fails exactly {OCC-TIMELINE, S1-DIFF, X-2818} |
| C4e *extra*: 403's last (dead) A write moved to the end of restore at FULL | OCC-TIMELINE-extra | final segment of 403 after warp 72 is not exactly follower 669. Same acceptance and exact-failure expectations as C4d |
| C4f 401's last A read (A3159, `add 400 += −1·401`) moved to the end of restore at FULL | S2-REPLAY-FREE | forward target 0 wrong before cleanup. Must be accepted by the frames, recount, refits, stage records, fill and price; fails exactly {both replays, OCC-TIMELINE, S1-DIFF, X-2818} |
| C4g 401's last A write before its last read (A3158, `add 401 += 400`) moved to the end of restore at FULL | S2-REPLAY-MATRIX | matrix realisation (forward, seed 1) wrong on register 112. Same acceptance and exact-failure expectations as C4f |
| C5 warp 71 after follower 667's first gate | OCC-TIMELINE | follower 667 has an event before alias warp 71 |
| C6 wrong G on warp 71 | S3S4-FRAMES-PROFILE | G(U) != E |
| C7 consistent (U′, G(U′)) on warp 71, U′ ≠ propagated frame | S3S4-FRAMES-PROFILE | warp frame mismatch: op 71 lender 401 |
| C8 removed follower 667 kept live | S5-FILL-WORD-DERIVED-R | role count 271728 != 666 × word-derived 409 |
| C9 lenders of warps 71/72 swapped (declaration conformance) | OCC-TIMELINE | alias warp 71 is not on lender 401 |
| C10 first restore gate dropped | S2-REPLAY-FREE | restored helper 572 not its own input |
| C11 fill inflated to R + 1 helper indices | S5-FILL-WORD-DERIVED-R | role count 272394 != 666 × 408 |
| C12 one hostee-30 gate left on 401 | S1-DIFF | B941 is not the declared relabel |
| C13 undeclared frame raise (B1500 → FULL) | S1-DIFF | undeclared frame changes |
| C14 #2818 base word altered by one sign | X-2818-SAME-CONSTRUCTION | words differ |

## Scope, inherited assumptions and unresolved obligations

- **Model.** We check the finite BORROW-WORD model as written in PR2226 `PROOF.md` and the PR2679/PR2751 lineage:
  frames, rank-zero K_G warps, COPY charges, derived cleanup and windows. The model itself is not validated. Its
  conventions are taken as the specification: free warps, free cleanup at FULL, idle children priced by remainder, and
  the window rule rebuilt from the template.
- **Not re-derived here.** PR #2751's twelve-source recovery, its 4(H8−H7−H1) delta and the PR2720 reconciliation. A
  sibling session claimed these in #2612. We use W2751 as a pinned parent and check that #2802's copies are
  byte-identical to #2751's own files.
- **Author-recorded in #2802's release; not independently re-checked here.**
  - The native lowering of both final words, including Clifford recipes and warp-recipe checks for the new warps 30,
    31 and 66–72 (`evidence/retired7/NATIVE-RECEIPT.json`, `NATIVE-STANDALONE.json`).
  - The strict T74 assembly (`RELEASE-VERIFY-RESULT.json`, stage `strict-t74`). That record carries κ
    0.001714849224721887, not the claimed κ. This is the supplier-only κ of the strict supplier assembly under its
    older outer witness, the same value that #2818's `CLAIM.json` reports as `kappa` and explains in `kappa_layers`.
  - The modern outer arithmetic that yields the claimed κ (`ADMISSION-RESULT.json`, `complex_lower` = C).
  - This audit checks the new warps only through their binary-symplectic image.
- **Inherited and open.**
  - By #2802's own scope statement: the all-size compiler, common-label/mutable-source realization, whole-call hosting,
    precision/tape, exact recovery, analytic transfer, the PR559 recurrence correction and the PR589 bit H1–H5
    assumptions.
  - The T74/#1319 supplier admission and the PR1673 capped phase-cell fusion outer.
  - The physical stock identity 66,794 = 66,304 + 408 + 8 + 72 + 2. Of its components, R = 408 and the 72 buffers
    (= |helper_final|) agree with the words.
  - The "at most two aliases" census and philippeVV's 670/671 pigeonhole in #2802.
  - #2818's 10⁻³⁰⁰⁰ endpoint.
- **Claim strength.** This is a finite exact check of one construction, not a proof of the multiplication theorem.
  A pass removes no inherited obligation.

## Changes after review (round 1)

AI review passes in the same loop raised these points; all are addressed here.
- **Overstated claim about occupancy.** The previous text said only frame monotonicity and occupancy reject C4a/C4b,
  and proposed controls "expecting frame not monotone". Per the receipt, S1-DIFF and X-2818 also reject them. Variant
  C4d shows that frame monotonicity does not protect occupancy. The section above, and controls C4c–C4f, replace that
  text.
- **Wrong frame provenance.** The 20 frames had been attributed to PR2766 as #2802 lists them. PR2766's word changes
  only B1151; rule `ATTRIBUTION-PR2766-WORD` now checks against PR2766's pinned word.
- **Split not credited to #2802.** The retired5/retired7 split had been presented as derived here. It is #2802's own
  split; the rule now also matches #2802's recorded retired5 endpoint, profile and fill hash.
- **Root-bracket slack applied at too low a precision.** Our own re-reading found that the 10⁻⁷⁰ slack was applied in
  Python's default 28-digit context, where it rounds away. The earlier PASS stood only because the actual margins
  (three root brackets, six margins, minimum 1.046×10⁻²⁰) exceed 28-digit rounding (≤ 5×10⁻²⁴). The widening is now
  done at 100 digits with directed rounding, and the error budget is written down.
- **Verifier output.** The verifier now emits the 24 prelude warp items, the 35/14/14 relabel split and refit7c's
  dims. A pin mismatch now prints a FAIL line instead of a traceback.

## Changes after review (round 2)

AI review passes in the same loop raised these points; all are addressed here. No number, rule verdict or conclusion
changed; one control was added.
- **Occupancy wording too general.** "A lender write moved past its alias warp at FULL is correct" holds for dead
  writes, not for every write; a referee mutant moving 401's write A3158 was rejected by both replays. "So … cannot
  change κ" inferred a universal from two examples. The conclusion now rests on the structural fact that no pricing
  check reads occupancy, explains why C4d passes, and new control C4g (with `must_accept`/`exact_failing` for C4f and
  C4g) machine-checks that a moved write the lender still reads is rejected by the replays.
- **PR2226 §1 overstated.** The model checks only the binary-symplectic conditions of the Clifford identity, not the
  identity itself; the paragraph now says so.
- **Fill-hash fallback undisclosed.** The zlib-dependent comparison and its canonical-JSON fallback are now described,
  and `verify.py` prints a `NOTE:` line if the fallback runs.
- **strict-t74 κ.** The release record carries the supplier-only κ, not the claimed κ; the scope list now says so.
- **Precision.** Scoped "no shipped control" to 401/403; marked the optional regression control as optional; described
  #2802's structural checks exactly (pure-relabel check only for `hostmove2`); retired5's words are rebuilt from
  published stage files; the native inputs of Open Q1/Q3 are obtainable through #2802's `full_replay.py`; stated that
  C8, C11 and C14 do not mutate only the base word; stated the 1-based warp and 0-based gate numbering; corrected the
  bracket count; moved Reproduce up; and refreshed "What this decides" (#2839 and #2843 added).

## Open next questions

1. **Does any layer outside the finite model rely on alias occupancy?** *Why:* in the model, a C4d-type violation is
   correct and identically priced. Occupancy therefore matters only if the native lowering, physical hosting or
   routing reads a warp as the hand-over point of a register. *First step:* inspect whether #2802's native lowering
   (full release) assigns roles per register segment. If it does, add a C4d-type mutant against #2802's stage-structure
   check and an occupancy predicate to #2818's patch check. *Access:* not blocked. #2802's `full_replay.py` downloads
   and authenticates the 491 pinned PR2679 files and rebuilds the native providers; it needs the packages in #2802's
   `requirements.txt` (author-recorded cold run: 411 s). An independent check should read its outputs as data.
2. **Is the whole refit frame assignment optimal under the moment cost?** `refit5c` claims "certified optimal". *Why:*
   a better assignment could only raise κ. It cannot invalidate the checked value, and the seven above-floor frames
   carry no cost. *First step:* an independent exact optimiser over all gates' frames with the same COPY pricing.
   *Blocked by:* a written objective for the #1186 `optimal_frames` certificate.
3. **Do the new warps 30, 31 and 66–72 have exact native Clifford/Gaussian lifts in both orientations?** *Why:* #2802
   records them, but this audit checks K_G only through its binary-symplectic image. *First step:* instantiate the
   exact Gaussian products of each new K_G and check every column, as PR2226 did for its 80 pairs. *Access:* the native
   inputs are rebuilt by #2802's `full_replay.py` from the pinned PR2679 sources, as in Q1.

## Credits and provenance

- **Checked work.**
  - Marius-Paul Dumitrean (mdumitrean), PR #2802: the retired5 and retired7 stages, the census and the recorded
    retired5 evidence.
  - Jeremy Kothe (jeremykothe2), PR #2818: repackages #2802 with a finer endpoint (concurrent work). Also the
    PR2673/#2745 lineage, the gmx-t74-borrow43 machinery, and PR #2767, whose κ is one of the margins checked here.
  - Tekalign (tekuuu), PR #2751: the parent words, fill transform and independent checkers.
  - Philippe Van Velzen (philippeVV), PR #2679/#2559: the retired-lender alias and the pre-life hostings.
  - Cinna Davis, PR #2226: anticipatory dirty borrowing and the free-operator replay idea.
  - Mason Hale, PR #2696: the eight-lender assignment.
  - DavidAriasC, PR #2766: the B1151 refit of #2751's words, composed from mdumitrean's PR2733 refit.
  - Vlado Vojdanovski (Vlado-V), PR #2322: the coherent handoff in the word lineage.
  - zxv, PR #2530.
- **Downstream claims named in "What this decides".** Dugongue (#2824, #2827, #2839), jeremykothe2 (#2833) and
  mdumitrean (#2843). Their own stages are not checked here.
- **Related prior audit.** commdata2338's PR #2656 independently audited PR #2588's swapped-alias frame bill and lender
  handoffs. That is the same kind of check applied here to #2802's aliases. No code or data from it is used.
- **Related work by the same account (disclosed).**
  - The merged `research/t74-borrow43-independent-check` (PR #2315) was a semantic reference for the BORROW-WORD model;
    no code was copied.
  - Sibling PR #2804 audits #2530's words and the #2679 order/windows.
  - The concurrent sibling #2612 claim covers #2751's twelve-source recovery.
  - The pinned PR2679 auditor and the #2802/#2818 scripts were read as data only.
- **Base and assignment.** Base `544a7e82810e30cab61c297cb2e2ea86127fe944` (priority revision 5). Sprint track 60–74
  (adversarial audit), OS seed 71. Claim: Discussion #1163 comment 18961174. Canonical thread: Discussion #2612.
- **AI assistance.** Prepared by thakrarsagar with substantial AI assistance from Claude (Anthropic, Claude Opus 5.5).
  One session wrote and ran the code and these notes. AI review passes in the same loop (reproducibility,
  mathematics, provenance, referee) reviewed them in two rounds, and two revisions addressed their findings. No human
  has checked the findings by hand. Apache-2.0.
