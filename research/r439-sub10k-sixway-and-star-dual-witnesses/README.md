# Sub-10,000-ADD Six-Way `r439` Composition (`9,974` ADDs) and Exact Dual Witnesses across Star-Edge, `UT_4(F_2)`, and Dyadic Borel Models

- **Primary Task:** `bit-helper-contract` (`docs/research/current-priorities.md`, priority revision `6`, portfolio weight `10%`, `scope_status: "unchanged"`)
- **Secondary Task:** `bit-new-register-model` (`docs/research/current-priorities.md`, priority revision `6`, portfolio weight `10%`)
- **Selected Global Upper Bound (Unchanged):** `kappa <= 0.001672660197076918` (**PR #1094**, `certificates/selected-result.json`). This package is a local structural witness and exact obstruction study on the `r439` (`4-4-20`) straight-line witness ladder and idealized register models; it does **not** claim a new global `kappa` bound (`no_new_kappa`).
- **Archival Intake Base Status:** The `r439` (`4-4-20`) witness baseline (**PR #589**, `24,305` ADDs) and its local optimization and obstruction lineage (**PR #1062**, **PR #1122**, **PR #1188**, **PR #1194**, **PR #1311**, **PR #1384**, **PR #1507**, **PR #1543**, **PR #1709**, **PR #1803**, **PR #1806**, **PR #1868**, **PR #1937**, **PR #2107**, **PR #2115**, **PR #2440**, **PR #2613**, **PR #2828**, **PR #2977**, and external comparators **PR #2408**, **PR #2374**, **PR #2316**, **PR #2312**) carry `"merged_for_archive_only"` and `"partially_reviewed"` status in `docs/research/pr-intake-decisions.json`; every cited prior result is treated strictly as a `"report (author-checked)"` (plural: `"reports (author-checked)"`).
- **Author:** `dcharb78, with AI assistance`
- **One-Command Verification:** `/opt/homebrew/bin/python3.12 -B research/r439-sub10k-sixway-and-star-dual-witnesses/verify.py` (~`4.4` seconds, Python 3.12 standard library only)

---

## Executive Summary

This research package addresses the Track 1 (`bit-mechanisms`, 20% combined portfolio weight in `docs/research/current-priorities.md` across `bit-helper-contract` and `bit-new-register-model`) question:

> *"Can one precisely specified helper-mixing word satisfy a replacement for the inherited H2/K interface?"*

Through four coupled, deterministically verified pillars (`verify.py` -> `RESULT.json`), this package establishes a constructive positive breakthrough on the actual `r439` (`4-4-20`) 661-column witness ladder while certifying three unconditional structural impossibility barriers across the star-edge, `F_2[UT_4(F_2)]`, and dyadic block-Borel register models:

1. **Pillar 1 — First Sub-10,000-ADD Constructive Witness on the `r439` (`4-4-20`) Ladder (`9,974` ADDs, `-518` vs. PR #1188, `-74` vs. PR #2440):**
   By composing five prior schedule/basis mechanisms from pinned verification inputs (**PR #1709** `research/r439-five-cycle-seed9f01` middle-column 5-cycle shears, **PR #1868** `research/r439-twisted-star-absorption-seed02` twisted B-section star shears, **PR #2115** `research/r439-deferred-target-basis-seed06` deferred-scatter / middle-column absorption, and **PR #2440** `research/r439-one-slot-multicolumn-interleave` 10-pair target-`445` scatter on **PR #1188** `research/r439-gl5-shortest`) into a 5-way witness at `10,034` ADDs (`10034`), and then applying **6 new pairwise-disjoint middle-column helper shears** (`(a_local, b_local)` = `(127, 240)`, `(16, 239)`, `(121, 128)`, `(422, 371)`, `(3, 235)`, `(238, 29)`) that save an additional `60` ADDs (`14 + 11 + 10 + 9 + 8 + 8`), we construct an explicit 6-way straight-line witness at **`9,974` ADDs** (`9974`). It passes all 661-column forward/reverse symbolic bitmask replays, the `91`-bit local evaluator, and the `174`-bit 9-stage evaluator (`F = 15,539` / `15539`, `B = 2,830,702` / `2830702`, `scatter_ADDs = 84`, `paid_rank_mass = 5,129` / `5129`).
2. **Pillar 2 — Whole-Section-`A` and Coupled `(a, c)` Star-Edge Absorption Theorem with `693` + `675` Explicit RREF Dual Hyperplane Witnesses:**
   Across all three canonical `r439` star-factored words (**PR #1062** `research/r439-bsection-stars-seed01` at `11,500` ADDs, **PR #1122** `research/r439-abc-star-composition` at `10,652` ADDs, and **PR #1188** `research/r439-gl5-shortest` at `10,492` ADDs), each word contains `236` star edges (`5` solvable edges `(506, 374)`, `(507, 355)`, `(514, 367)`, `(264, 536)`, `(326, 530)` and `231` obstructed edges). Removing the reader-horizon (`r_0`) restriction completely—allowing arbitrary monotone `a`-writes across the **entire section `A`** and arbitrary coupled `(a, c)` writes across both section `A` and section `C`—yields **`0` additional solvable star edges** (`5 / 236` solvable, `231 / 236` obstructed). `verify.py` constructs and verifies all **`693`** (`3 * 231`) explicit 661-bit RREF dual hyperplane witnesses and all **`675`** (`3 * 225`) explicit 1,322-bit coupled `(a, c)` RREF dual witnesses.
3. **Pillar 3 — Unconditional All-Length, All-Role `n_b >= 6` Theorem in `F_2[UT_4(F_2)]`:**
   Prior **PR #1803** / **PR #1806** (`research/ut4-fifteen-call-five-b`) and **PR #2828** (`research/bit-ut4-mixed-targets-barrier`, `"merged_for_archive_only"`, `"partially_reviewed"`) report (author-checked) that 5 `b`-calls fail at fixed total lengths `13` (`(4, 5, 4)`) and `15` (`(5, 5, 5)`). By proving that the `a`/`c` gap-word recurrence is a pure bilinear accumulation of prefix sums `(S_a(j), S_c(j))` independent of word length, we verify across all `256 / 256` pairs `(S_a, S_c)` that the reachable central accumulator fiber is the exact affine trace hyperplane `{q in M_2(F_2) : Tr(q) = Tr(S_a S_c)}`, and we evaluate all `3,600` (`3600`) zero-sum 5-`b` middle tuples `(n_0, ..., n_4)`. Across all `3,240` (`3240`) non-degenerate middles (`rank X_b = rank Y_b = 2`), **`0`** (`ut4_nondegenerate_compatible_pairs = 0`) length-unconstrained `(a, c)` profile pairs exist at **any finite word length `L` and any clean/dirty role count `m >= 3`**. Across the `360` degenerate middles (`rank X_b = 1` or `rank Y_b = 1`), only `16` middles (`3,145,728` / `3145728` profile pairs) survive the trace-hyperplane screen, and **100% (`3,145,728 / 3,145,728`)** identically annihilate `ACB[0, 0] = 0` or `BAC[0, 0] = 0`.
4. **Pillar 4 — Full 4x4 Block-Borel Schubert-Cell Invariance and 3-Call Parity Floor (`mW = 4`):**
   Prior **PR #1507**, **PR #2107**, **PR #2613** (`research/bit-full-borel-2adic-floor`), and **PR #2977** (`research/paired-diagonal-borel-gauge`, `"merged_for_archive_only"`, `"partially_reviewed"`) report (author-checked) 2-call trace obstructions, 2-adic valuation floors, and paired-diagonal Borel gauge analyses at `m = 2, W = 2`. We lift these to a purely combinatorial Schubert-cell parity invariant on `F_2[Gr_2(Q^4)]` under the **full 4x4 block-Borel group** (`B_full`, generated by `G_A, G_C in GL_2(F_2)` plus arbitrary strictly lower-block cleanup shears `L_{21} in M_2(F_2)`). Across `13,531` sampled 2-planes (`1` in `O_0`, `320` in `O_1`, `13,210` in `O_2`), `40,593` (`40593`) free block-Borel checks confirm exact Schubert-cell invariance (`0` upward jumps), `54,124` (`54124`) paid rank-1 shear checks confirm `Delta c <= 1`, and an exhaustive census of all `20,224` (`20224`) 3-call `(1 + 1 + 2)` configurations confirms **`0` survivors** (`dyadic_3call_parity_survivors = 0`) achieving `E_2 = I_2` and `E_1 = 0`, certifying the paid-rank floor `mW = 4` (`dyadic_paid_rank_floor = 4`) at `m = 2, W = 2`.

---

## Summary Table of Deterministically Verified Metrics (`RESULT.json`)

Every metric in `RESULT.json["summary"]` is reproduced below and verified by `verify.py`:

| Metric Key (`RESULT.json["summary"]`) | Exact Value | Formatted | Meaning / Verification Scope |
| :--- | :--- | :--- | :--- |
| `r439_sub10k_sixway_adds` | `9974` | `9,974` | Total ADDs of the new 6-way sub-10k `r439` (`4-4-20`) straight-line witness |
| `r439_fiveway_adds` | `10034` | `10,034` | Total ADDs of the 5-way composition (`PR #1709 + PR #1868 + PR #2115 + PR #2440` on `PR #1188`) |
| `r439_fourway_b_adds` | `10044` | `10,044` | Total ADDs of 4-Way Composition B (`PR #1709 + PR #1868 + PR #2115` on `PR #1188`) |
| `r439_fourway_a_adds` | `10045` | `10,045` | Total ADDs of 4-Way Composition A (`PR #1543 + PR #1868 + PR #2115` on `PR #1188`) |
| `r439_delta_vs_pr1188` | `-518` | `-518` | Net ADD reduction of the `9,974`-ADD witness relative to `PR #1188` (`10,492` ADDs) |
| `r439_delta_vs_pr2440` | `-74` | `-74` | Net ADD reduction of the `9,974`-ADD witness relative to `PR #2440` (`10,048` ADDs) |
| `r439_disjoint_shears_saving` | `60` | `60` | Net ADD reduction from the 6 new pairwise-disjoint middle-column helper shears (`14+11+10+9+8+8`) |
| `r439_scatter_adds` | `84` | `84` | Remaining middle-column deferred scatter ADDs after target-`445` 10-pair scatter (`94 -> 84`) |
| `r439_sub10k_F` | `15539` | `15,539` | Exact `F` cost metric (`ADDs + SUBs + 2*NEGs`) of the `9,974`-ADD witness |
| `r439_sub10k_B` | `2830702` | `2,830,702` | Exact bit-level operation metric `B` of the `9,974`-ADD witness |
| `r439_local_bits` | `91` | `91` | Verified bit width in the local `r439` evaluator (`local_ok = True`) |
| `r439_nine_stage_bits` | `174` | `174` | Verified bit width in the 9-stage `r439` composition evaluator (`nine_ok = True`) |
| `r439_paid_rank_mass` | `5129` | `5,129` | Invariant paid-rank mass across the `r439` star-factored witness ladder |
| `star_edges_per_word` | `236` | `236` | Total B-section star edges per word in `PR #1062`, `PR #1122`, and `PR #1188` |
| `star_solvable_edges_per_word` | `5` | `5` | Solvable star edges per word (`(506,374), (507,355), (514,367), (264,536), (326,530)`) |
| `star_obstructed_edges_per_word` | `231` | `231` | Obstructed star edges per word under both whole-section-`A` and coupled `(a, c)` absorption |
| `star_whole_a_dual_witnesses_total` | `693` | `693` | Verified 661-bit RREF dual hyperplane witnesses (`3 * 231`) across `PR #1062`, `PR #1122`, `PR #1188` |
| `star_coupled_ac_dual_witnesses_total` | `675` | `675` | Verified 1,322-bit coupled `(a, c)` RREF dual witnesses (`3 * 225`) across `A`-reader edges |
| `ut4_trace_hyperplane_matches` | `256` | `256` | Exact matches (`256 / 256`) for the affine trace-hyperplane fiber theorem `Tr(q) = Tr(S_a S_c)` |
| `ut4_zero_sum_five_b_middles` | `3600` | `3,600` | Total zero-sum 5-`b` middle sequences `(n_0, n_1, n_2, n_3, n_4)` in `F_2[UT_4(F_2)]` |
| `ut4_nondegenerate_middles` | `3240` | `3,240` | Non-degenerate zero-sum 5-`b` middles (`rank X_b = rank Y_b = 2`) |
| `ut4_nondegenerate_compatible_pairs` | `0` | `0` | Compatible `(a, c)` profile pairs at any word length `L` across all `3,240` non-degenerate middles |
| `ut4_degenerate_surviving_middles` | `16` | `16` | Degenerate zero-sum 5-`b` middles (`rank X_b = 1` or `rank Y_b = 1`) surviving the trace screen |
| `ut4_degenerate_compatible_pairs` | `3145728` | `3,145,728` | Degenerate compatible profile pairs (`100%` annihilating `ACB[0,0] = 0` or `BAC[0,0] = 0`) |
| `dyadic_borel_invariance_checks` | `40593` | `40,593` | Verified full 4x4 block-Borel Schubert-cell invariance checks (`13,531` planes * `3` generators) |
| `dyadic_rank1_shear_checks` | `54124` | `54,124` | Verified rank-1 upper-shear Schubert-cell step checks (`13,531` planes * `4` rank-1 shears) |
| `dyadic_3call_parity_configs` | `20224` | `20,224` | Exhaustively tested 3-call `(1 + 1 + 2)` parity configurations in the dyadic block-Borel model |
| `dyadic_3call_parity_survivors` | `0` | `0` | Surviving 3-call `(1 + 1 + 2)` configurations achieving `E_2 = I_2` and `E_1 = 0` |
| `dyadic_paid_rank_floor` | `4` | `4` | Certified paid-rank lower bound `mW = 4` at `m = 2, W = 2` under full block-Borel cleanup |

---

## Pillar 1: Constructive Six-Way Composition Breaking the `10,000`-ADD Barrier on `r439` (`9,974` ADDs)

### 1.1 The `r439` (`4-4-20`) Straight-Line Witness Progression

Prior archival packages (`"merged_for_archive_only"`, `"partially_reviewed"` in `docs/research/pr-intake-decisions.json`), all pinned in `SOURCES.json` with `"usage": "input"`, explored orthogonal local transformations on top of **PR #1188** (`research/r439-gl5-shortest`, `10,492` ADDs):
- **PR #1543** (`research/r439-neutral-helper-chain-seed17/CANDIDATE.json.gz`) reports (author-checked) a `-11` ADD schedule-safe retargeting (`10,492 -> 10,481` ADDs).
- **PR #1709** (`research/r439-five-cycle-seed9f01/CANDIDATE.json.gz`) reports (author-checked) a `-12` ADD cyclic 5-helper middle-column shear (`10,492 -> 10,480` ADDs).
- **PR #1868** (`research/r439-twisted-star-absorption-seed02/absorbed-pr1188.json.gz`) reports (author-checked) a `-3` ADD twisted B-section star shear (`10,492 -> 10,489` ADDs).
- **PR #2115** (`research/r439-deferred-target-basis-seed06/verify.py`) reports (author-checked) a `-433` ADD deferred-scatter / middle-column absorption schedule on top of **PR #1868** (`10,489 -> 10,056` ADDs, leaving `94` deferred middle-column scatter ADDs).
- **PR #2440** (`research/r439-one-slot-multicolumn-interleave/verify.py` and `WITNESS.json`) reports (author-checked) a `-8` ADD reduction on top of **PR #2115** (`10,056 -> 10,048` ADDs, reducing deferred scatter ADDs from `94` to `84`) by scattering middle-column target `445` into `10` middle-column pairs (`(264,536), (326,530), (359,517), (367,514), (371,520), (374,506), (383,551), (424,621), (446,640), (452,649)`).

In `verify.py`, we first establish that **PR #1543** (`-11` ADDs) and **PR #1709** (`-12` ADDs) commute cleanly with the **PR #1868 + PR #2115** deferred-scatter pipeline (`10,045` / `10045` ADDs for 4-Way Composition A and `10,044` / `10044` ADDs for 4-Way Composition B), and that combining **PR #1709 + PR #1868 + PR #2115 + PR #2440** yields a verified **5-way composition at `10,034` ADDs** (`10034`).

### 1.2 Six New Pairwise-Disjoint Middle-Column Helper Shears (`-60` ADDs -> `9,974` ADDs)

Within section `D` of the `r439` witness (`lo_m = 472` to `hi_m = 569`), middle-column basis targets `t` accumulate bipartite combinations of helper columns `a_wire = 222 + a_local` (with middle-column support mask `col[a]` of weight `w_a = popcount(col[a])`) and `b_wire = 222 + b_local` (with middle-column support mask `col[b]` of weight `w_b = popcount(col[b])`, recorded as `b_weight_before = w_b`). When `a_wire` and `b_wire` co-occur in `k = popcount(col[a] & col[b])` middle-column targets (`shared_target_count = k`), wrapping the middle-column block `[lo_m .. hi_m]` with:
- **1 setup gate before `lo_m`:** `a_wire ^= b_wire`
- **1 restore gate after `hi_m`:** `a_wire ^= b_wire`

causes every middle-column read of `a_wire` in `col[a]` to automatically carry `a_wire ^ b_wire`. Thus `b_wire` only needs to be read on the symmetric difference `col[b] ^ col[a]`, giving post-shear `b`-weight (`b_weight_after`):

$$w_b' = \operatorname{popcount}(\operatorname{col}[b] \oplus \operatorname{col}[a]) = w_b + w_a - 2k$$

Accounting for the `2` setup/restore gates, the exact net ADD reduction is:

$$\text{net\_saving} = w_b - w_b' - 2 = 2k - w_a - 2$$

As long as the selected pairs `{(a_wire_i, b_wire_i)}` are **pairwise disjoint**, their setup/restore brackets and middle-column support transformations do not interfere and their savings sum additively:

| Shear # | `a_local` | `b_local` | `a_wire` | `b_wire` | `shared_target_count` (`k`) | `b_weight_before` (`w_b`) | `b_weight_after` (`w_b' = popcount(col[b] ^ col[a])`) | `net_saving` (`w_b - w_b' - 2`) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | `127` | `240` | `349` | `462` | `16` | `16` | `0` | **`14` ADDs** |
| **2** | `16` | `239` | `238` | `461` | `14` | `19` | `6` | **`11` ADDs** |
| **3** | `121` | `128` | `343` | `350` | `12` | `12` | `0` | **`10` ADDs** |
| **4** | `422` | `371` | `644` | `593` | `11` | `14` | `3` | **`9` ADDs** |
| **5** | `3` | `235` | `225` | `457` | `10` | `12` | `2` | **`8` ADDs** |
| **6** | `238` | `29` | `460` | `251` | `10` | `12` | `2` | **`8` ADDs** |
| **Total** | — | — | **6 disjoint** | **6 disjoint** | **`73` shared reads** | **`85`** | **`13`** | **`60` ADDs** |

Applying all 6 disjoint middle-column shears to the `10,034`-ADD 5-way witness yields the **`9,974`-ADD (`9974`) 6-way witness**:

| Stage in `r439` (`4-4-20`) Progression | Total ADDs | Delta vs. `PR #1188` | Delta vs. `PR #2440` | Scatter ADDs | `F` | `B` | Local / 9-Stage Bits |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `PR #589` (selected `r439` base) | `24,305` | `+13,813` | `+14,257` | — | — | — | `91` / `173` |
| `PR #1062` (`r439-bsection-stars-seed01`) | `11,500` | `+1,008` | `+1,452` | — | — | — | `91` / `173` |
| `PR #1122` (`r439-abc-star-composition`) | `10,652` | `+160` | `+604` | — | — | — | `91` / `173` |
| `PR #1188` (`r439-gl5-shortest`) | `10,492` | `0` | `+444` | — | `13,667` | — | `91` / `173` |
| `PR #1868` (`r439-twisted-star-absorption-seed02`) | `10,489` | `-3` | `+441` | — | `13,667` | — | `91` / `173` |
| `PR #2115` (`r439-deferred-target-basis-seed06`) | `10,056` | `-436` | `+8` | `94` | `13,667` | `2,816,834` | `91` / `173` |
| `PR #2440` (`r439-one-slot-multicolumn-interleave`) | `10,048` | `-444` | `0` | `84` | `13,667` | `2,823,272` | `91` / `173` |
| **New 4-Way A** (`#1543+#1868+#2115`) | `10,045` (`10045`) | `-447` | `-3` | `94` | `13,835` | `2,820,600` | `91` / `173` |
| **New 4-Way B** (`#1709+#1868+#2115`) | `10,044` (`10044`) | `-448` | `-4` | `94` | `14,891` | `2,824,264` | `91` / `174` |
| **New 5-Way** (`#1709+#1868+#2115+#2440`) | `10,034` (`10034`) | `-458` | `-14` | `84` | `14,891` | `2,830,702` | `91` / `174` |
| **New 6-Way Sub-10k (+6 disjoint shears)** | **`9,974` (`9974`)** | **`-518`** | **`-74`** | **`84`** | **`15,539` (`15539`)** | **`2,830,702` (`2830702`)** | **`91` / `174`** |

---

## Pillar 2: Whole-Section-`A` and Coupled `(a, c)` Star-Edge Absorption Theorem (`693` + `675` RREF Dual Witnesses)

Prior **PR #1384** and **PR #1937** (`research/r439-multi-donor-star-absorption`, `"merged_for_archive_only"`, `"partially_reviewed"`) report (author-checked) that across the `236` B-section star edges `(a_star, b_star)` in **PR #1062** (`research/r439-bsection-stars-seed01`), **PR #1122** (`research/r439-abc-star-composition`), and **PR #1188** (`research/r439-gl5-shortest`), only `5` edges (`(506, 374), (507, 355), (514, 367), (264, 536), (326, 530)`) can be absorbed into `a`-writes when restricted to either the pre-`r_0` window (`[0, r_0)`) or the post-`r_0` window (`(r_0, |A|]`).

In `verify.py` (`run_pillar_2`), we construct the exact 661-row linear systems over `F_2` for every star edge across all three words (`PR #1062`, `PR #1122`, `PR #1188`) under four progressively broader models:
1. Pre-`r_0` `a`-only (`[0, r_0)`)
2. Post-`r_0` `a`-only (`(r_0, |A|]`)
3. **Entire section `A` `a`-only (`[0, |A|]`)** (both same-path and monotone-all variants)
4. **Coupled `(a, c)` absorption** combining the entire section-`A` `a`-write space (`[0, |A|]`) with section-`C` `c`-writes in `[r_0, |C|]` (and `[last_read, r_0)`) across the `661 + 661 = 1,322` joint output constraints.

**Result:** Across all three words (`PR #1062`, `PR #1122`, `PR #1188`), **all four models have the exact same `5` solvable star edges and `231` obstructed star edges** (`0` new solvable edges under whole-section-`A` or coupled `(a, c)` absorption). For every obstructed edge, RREF elimination produces an explicit minimum-index dual hyperplane witness `u` (`u^T M = 0` and `u^T target = 1`):
- **`693` (`3 * 231`) verified 661-bit RREF dual hyperplane witnesses** for whole-section-`A` monotone absorption (`star_whole_a_dual_witnesses_total = 693`).
- **`675` (`3 * 225`) verified 1,322-bit RREF dual hyperplane witnesses** for coupled `(a, c)` monotone absorption across the `230` `A`-reader edges per word (`star_coupled_ac_dual_witnesses_total = 675`).

---

## Pillar 3: Unconditional All-Length, All-Role `n_b >= 6` Theorem in `F_2[UT_4(F_2)]`

Prior **PR #1803** / **PR #1806** (`research/ut4-fifteen-call-five-b/vendor/predecessor.py` and `research/ut4-fifteen-call-five-b/census.py`) and **PR #2828** (`research/bit-ut4-mixed-targets-barrier`, `"merged_for_archive_only"`, `"partially_reviewed"`) report (author-checked) that in the unitriangular group-ring model `F_2[UT_4(F_2)]`, words with `n_b = 5` middle calls fail at fixed total lengths `13` (`(4, 5, 4)`) and `15` (`(5, 5, 5)`).

In `verify.py` (`run_pillar_3`), we prove an **all-length, all-role impossibility theorem** eliminating `n_b <= 5` at any finite word length `L = n_a + 5 + n_c` and any role count `m >= 3`:

1. **Exact Affine Trace-Hyperplane Fiber Theorem (`256 / 256` pairs):**
   Within each of the 6 gaps `j in {0, ..., 5}` separated by the 5 `b`-calls, `a`-calls (`g_1`) and `c`-calls (`g_3`) act on the gap state `(S_a, S_c, q) in M_2(F_2)^3` via `(S_a, S_c, q) -> (S_a + R, S_c, q + S_c R)` and `(S_a, S_c, q) -> (S_a, S_c + R, q + S_a R)`. Breadth-first closure over `M_2(F_2)^3` confirms across all **`256` (`ut4_trace_hyperplane_matches = 256`)** endpoint pairs `(S_a, S_c)` that the reachable central accumulator fiber is the exact 3-dimensional affine trace hyperplane:
   $$Q_{\text{reach}}(S_a, S_c) = \left\{\, q \in M_2(\mathbb{F}_2) \;:\; \operatorname{Tr}(q) = \operatorname{Tr}(S_a S_c) \,\right\}$$
2. **All-Length Census Across All `3,600` Zero-Sum 5-`b` Middles:**
   Partitioning the `3,600` (`ut4_zero_sum_five_b_middles = 3600`) zero-sum 5-`b` middles `(n_0, n_1, n_2, n_3, n_4)` by their 2-bit left/right coupling spans `X_b = span{x(n_j)}` and `Y_b = span{y(n_j)}`:
   - **Non-Degenerate Middles (`rank X_b = 2` and `rank Y_b = 2`): `3,240` (`3240`) middles.** Across all `3,240` non-degenerate middles and all `4^5 = 1,024` unconstrained prefix-sum profiles `(p_0, ..., p_4) in M_2(F_2)^5`, there are **`0` compatible `(a, c)` profile pairs** (`ut4_nondegenerate_compatible_pairs = 0`) at **any** finite word length `L`.
   - **Degenerate Middles (`rank X_b = 1` or `rank Y_b = 1`): `360` middles (`16` surviving, `3,145,728` pairs).** Only **`16`** (`ut4_degenerate_surviving_middles = 16`) degenerate middles (`8` with `x(n_j) in {1, 2}` and `8` with `y(n_j) in {1, 2}`) have non-zero compatible profile pairs (`3,145,728` / `3145728` pairs total across minimal realizable lengths `L in {13, ..., 27}`). On **100% (`3,145,728 / 3,145,728`)** of these degenerate pairs, every `b_j` has either its first row or first column identically zero, forcing `ACB[0, 0] = 0` or `BAC[0, 0] = 0` identically (whereas the `UT_4(F_2)` target requires `[1, 0; 0, 0]` on both).
   - **Role-Count Monotonicity (`m >= 3`):** Adding clean or dirty roles `m > 3` strictly appends block rows to the formal group-ring operator without relaxing the upper-left `3 x 3` role projection `(A, B, C)`. Thus `n_b >= 6` (and total length `L >= 14` via the direct `(4, 6, 4)` witness) holds unconditionally for all word lengths and all role counts `m >= 3`.

---

## Pillar 4: Full 4x4 Block-Borel Schubert-Cell Invariance and 3-Call Parity Floor (`mW = 4`)

Prior **PR #1507**, **PR #2107**, **PR #2613** (`research/bit-full-borel-2adic-floor/verify.py`), and **PR #2977** (`research/paired-diagonal-borel-gauge/verify.py`, `"merged_for_archive_only"`, `"partially_reviewed"`) report (author-checked) a 2-call helper-field trace obstruction, a restricted dyadic Gram/Schubert FAQ, a 2-adic valuation floor, and a paired-diagonal Borel gauge analysis.

In `verify.py` (`run_pillar_4`), we prove the paid-rank floor `mW = 4` (`dyadic_paid_rank_floor = 4`) at `m = 2, W = 2` without any 2-adic valuation or paired-diagonal gauge restriction under the **full 4x4 block-Borel group** (`B_full`):
1. **Full 4x4 Block-Borel Schubert-Cell Invariance (`40,593` checks):**
   Across all `13,531` sampled 2-planes (`1` in `O_0`, `320` in `O_1`, `13,210` in `O_2`), all **`40,593` (`40593`)** free block-Borel actions preserve the Schubert cell index (`0` upward jumps), while all **`54,124` (`54124`)** paid rank-1 upper shears (`H -> D`) shift the cell index by at most `+-1` (`Delta c <= 1`).
2. **Exhaustive 3-Call `(1 + 1 + 2)` Parity Exclusion (`20,224` configs, `0` survivors):**
   Testing all **`20,224` (`20224`)** valid 3-call `(1 + 1 + 2)` parity configurations `(u_1, v_1, u_2, v_2, M_3)` yields **`0` survivors** (`dyadic_3call_parity_survivors = 0`) achieving `E_2 = I_2` and `E_1 = 0`, certifying the paid-rank floor `mW = 4` (`dyadic_paid_rank_floor = 4`) at `m = 2, W = 2`.

---

## Single-Move Behavioral Negative Controls (`controls = 6`)

`verify.py` enforces 6 explicit behavioral negative controls (recorded in `RESULT.json["controls"]`):

1. **`control_1_overlapping_seventh_shear_corrupts_661_semantics`:** Appending an overlapping 7th middle-column shear (`349 ^= 461`, reusing `a_wire = 349` from Shear 1) without updating coupled middle-column target supports corrupts `2` output registers in the 661-column forward replay.
2. **`control_2_omitting_shear1_prep_or_undo_gate_breaks_targets`:** Omitting the 2 setup/restore gates of Shear 1 (`349 ^= 462`) while retaining the sheared middle-column reads breaks `62` output registers across the `16` shared middle-column target wires.
3. **`control_3_dual_hyperplane_witness_validation_and_corrupted_dual_rejection`:** All `693` whole-section-`A` 661-bit RREF dual hyperplane witnesses and `675` coupled `(a, c)` 1,322-bit RREF dual witnesses pass exact orthogonality (`u^T M = 0, u^T target = 1`), all `693` target-flipped dual witnesses are rejected, and `0` of the `5` solvable edges per word are falsely obstructed.
4. **`control_4_ut4_degenerate_rank1_middle_annihilates_acb00_or_bac00`:** Relaxing the non-degeneracy hypothesis (`rank X_b = rank Y_b = 2`) in `F_2[UT_4(F_2)]` admits exactly `16` degenerate zero-sum 5-`b` middles (`3,145,728` profile pairs), and 100% (`3,145,728 / 3,145,728`) of them identically annihilate `ACB[0, 0] = 0` or `BAC[0, 0] = 0`.
5. **`control_5_ut4_omitting_any_call_from_direct_464_word_fails`:** Omitting any 1 of the `14` calls (including any of the `6` middle `b`-calls) from the direct `(4, 6, 4)` formal `UT_4(F_2)` witness fails the 192-column formal target identity (`14 / 14` rejected).
6. **`control_6_dyadic_borel_single_block_and_illegal_upper_shear`:** A single rank-2 call (`paid_rank = 2`) has maximum `F_2`-rank `1 < 2` on `E_2`, whereas an illegal free upper shear `H -> D` jumps `V_D` directly to Schubert cell `O_2` at `paid_rank = 0`.

---

## Provenance, Pinned Verification Inputs, and External Comparators

- **Actual Parent Lineage and Pinned Verification Inputs (`SOURCES.json`):**
  `SOURCES.json` pins **19 upstream files** against `base_commit = "997e6a9ca7b4f95d50e366f61412fd640d72a88a"` by exact `sha256` and `git_blob`: **12 `"usage": "input"` files** (`6` `.json.gz` candidate archives and `1` `.json` witness file — `research/r439-bsection-stars-seed01/candidate.json.gz` [`#1062`], `research/r439-abc-star-composition/candidate.json.gz` [`#1122`], `research/r439-gl5-shortest/candidate.json.gz` [`#1188`], `research/r439-neutral-helper-chain-seed17/CANDIDATE.json.gz` [`#1543`], `research/r439-five-cycle-seed9f01/CANDIDATE.json.gz` [`#1709`], `research/r439-twisted-star-absorption-seed02/absorbed-pr1188.json.gz` [`#1868`], and `research/r439-one-slot-multicolumn-interleave/WITNESS.json` [`#2440`] — plus `5` `.py` modules — `research/r439-deferred-target-basis-seed06/verify.py` [`#2115`], `research/r439-one-slot-multicolumn-interleave/verify.py` [`#2440`], `research/ut4-fifteen-call-five-b/census.py` and `research/ut4-fifteen-call-five-b/vendor/predecessor.py` [`#1803` / `#1806`], and `research/bit-full-borel-2adic-floor/verify.py` [`#2613`]) and **7 `"usage": "provenance"` files** (`certificates/selected-result.json` [`#1094`], `docs/research/agent-task-catalog.json`, `research/r439-bsection-stars-seed01/verify.py` [`#1062`], `research/r439-copy-path-sharing-barrier/verify.py` [`#1194`], `research/r439-semantic-d-navigation/verify.py` [`#1311`], `research/r439-multi-donor-star-absorption/verify.py` [`#1937`], and `research/paired-diagonal-borel-gauge/verify.py` [`#2977`]).
- **External Comparators (`not read at runtime`):**
  **PR #2408**, **PR #2374**, **PR #2316**, and **PR #2312** are cited strictly as external comparators for PR-landscape positioning and are **not read at runtime** (and thus omitted from `SOURCES.json`).

---

## Open next questions

1. **Joint Coupled Multi-Shear Basis Optimization Below `9,974` ADDs:**
   The 6 middle-column helper shears in Pillar 1 were selected under a strict pairwise-disjoint wire constraint so their setup/restore brackets (`12` gates total) and support substitutions commute without cross-talk. Can a non-disjoint (triangular/cascaded) helper-shear sequence in `[lo_m, hi_m]` absorb overlapping `B`-wires whose residual weights (`b_weight_after in {2, 3, 6}`) are currently non-zero, pushing the `r439` (`4-4-20`) witness below `9,900` ADDs?
2. **Deferred-Scatter Absorption Beyond the Remaining `84` Scatter ADDs:**
   After absorbing target `445` (`94 -> 84` scatter ADDs via `research/r439-one-slot-multicolumn-interleave`), `84` deferred middle-column scatter ADDs remain at the end of section `C`. Can simultaneous basis retargeting across section `D` and section `C` absorb additional high-fanout middle-column targets without increasing `B`-section star reads?
3. **Six-`b` (`n_b = 6`) Minimum Total Length Below `14` Calls in `F_2[UT_4(F_2)]`:**
   With `n_b <= 5` unconditionally excluded at all finite word lengths `L` and all role counts `m >= 3` by Pillar 3, does there exist a `13`-call word with `n_b = 6` (such as `(3, 6, 4)` or `(4, 6, 3)`) in `F_2[UT_4(F_2)]`, or is `L = 14` (`(4, 6, 4)`) the unconditional all-length minimum across all `n_b >= 6`?
