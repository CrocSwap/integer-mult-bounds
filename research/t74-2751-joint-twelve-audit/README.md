# Audit #2751 independently and reconcile it with #2720's T74 centre floor (no κ; no defect found)

**Independent verification and audit, no new κ.**
- **Card:** `independent-moment`, refined to PR2751 and PR2720. The loop drew seed 63 (adversarial-audit track); this
  is the closest card for an independent check of a changed supplier claim.
- **Evidence status:** the Result table is *independently reproduced* here. Native, supplier-admission and outer
  stages remain *author-checked* (see Scope limits).
- **Frontier:** the selected frontier is unchanged (κ = 0.001672660197076918, #1094).
- **Status of the audited PRs:** PR2751 and PR2720 are open. Main's PR ledger (at `d311a18c`) records both as
  "partially reviewed": metadata and the changed-file inventory are collected, and substantive maintainer review is
  in progress. Neither is accepted, and nothing here changes that.

**The setting.**
- **PR2720** ([#2720](https://github.com/CrocSwap/integer-mult-bounds/pull/2720), petalas, head `813fae62`, "Prove the
  fixed-contract T74 inherited-correction floor") works under its hypotheses 1–3: separated sources, inherited
  partner-source helper paths, and a fixed target continuation.
  - Under these, the correction for partner sources 33, 55, 74 and 85 has rank four on target rows 23, 34, 50 and 108.
  - Under its further cut-bill premises, the centre cut then costs at least 4H7 + 4H1 + 4H8. Those premises are:
    line-30 cut frames, pinned incidences, a zero-frame reader per centre, rank-8 producers, descending private
    copies, and no target chart changes or nonmonotone target frame paths.
- **PR2751** ([#2751](https://github.com/CrocSwap/integer-mult-bounds/pull/2751), tekuuu, head `4cfbb0cc`) reaches 8H8,
  with all eight centre children at rank 8.
  - It reassigns the four partner aliases (33, 55, 74 and 85 move from removed helpers 640/641/642/644 to
    696/697/698/700), keeps PR2696's eight assignments, and moves the four pair recoveries `x += y/2; y −= x`.
  - It states that it "deliberately changes the old-four recovery paths held fixed by PR2720. It does not contradict
    that scoped cut obstruction" (README line 62; also PROOF.md line 17).
  - It claims 4(H8−H7−H1) per local word, and 2664(H8−H7−H1) in the complete profile, against PR2733 at `2761b52b`.
- **Downstream:** every pending T74 claim that I read above PR2733 rests on the eight rank-8 centre children (table
  below).

## What this adds

#2766's registered `independent_check.py` (DavidAriasC) already does three things:
- it recounts PR2751's word frames;
- it replays forward and dual, through cleanup, words that differ from PR2751's only in the B1151 frame, checking at
  every K47–K58 warp that the lender holds its own input;
- it confirms the B1151 difference.

#2768 (tekuuu) is the PR2751 author's complete native replay of PR2751's providers. This package corroborates the
first and adds coverage that neither has:

1. **The PR2720 reconciliation, computed.**
   - PR2720's matrix reproduces on its own input words, with det −1/16, residual, continuation, forced centres and
     invoice.
   - On PR2751's words the same projection is zero. The partner correction moves to targets 21, 37, 47 and 110 (det
     1/2), which no cut gate writes.
   - The PR2720 hypotheses are computed as booleans (table below). This independently confirms PR2751's own statement
     and localises the mechanism, the echo identities. PR2751 thereby answers PR2720's first open question
     constructively.
2. **The exact change set against PR2733@`2761b52b`:** the alias swap, the echo blocks, the moved recovery pairs and
   the charts of ops 47–50. The per-word delta is {1:−4, 7:−4, 8:+4}.
3. **The pair recoveries and lenders.**
   - The pre-states are (X_x−X_y)/2 and X_x+X_y for all four pairs, and both sources are restored.
   - Neither register is touched before its handoff, and there are no paid climbs.
   - All 12 lenders hold their own input at both the A prelude and the B handoff. This corroborates #2766's
     forward-only lender check, here in both providers with per-lender controls.
   - The cut census holds, and the shipped cleanup literally equals our own inverse-reverse.
4. **The pricing.**
   - The complete profile, from all 276,390 owner roles in two implementations.
   - The complete delta 2664(H8−H7−H1).
   - Physical stock 66,801.
   - A rigorous enclosure that accepts PR2751's C and rejects C + 1e-24. CLAIM.json's κ equals C − 1e-46 − 1e-70
     exactly.
5. **Downstream structure, and two comparisons** (parse only, not a replay):
   - The four pair recoveries (with PR2751's exact frames), the ops 47–50 charts on line 45, and the twelve lifted
     targets are present in the words of #2802, #2818, #2824, #2827 and #2833.
   - The #2766 and #2767 complete profiles are identical.
   - The comparison with PR2733's current head `a63c55ff`.

## Findings for the authors (non-blocking)

- **PR2751, wording of the recovery gates.**
  - PROOF.md calls the recovery gates "added". Against PR2696 and PR2733 the same gate pairs are *moved*, from
    B1034–1041 to B569–672, with identical algebra and frames. The pairs come from PR2530's source-partner recovery.
  - "Original operator IDs remain stable" is true for the ids. Ops 47–50, however, carry new G and E (U is unchanged
    as a span), and their handoffs move from B1042 to B1172–1177. Anyone matching by op id should compare the charts.
- **PR2751, the comparison point.** The 2664(H8−H7−H1) dominance is against PR2733@`2761b52b`, which PR2751's
  CLAIM.json pins. Against PR2733's current head `a63c55ff` (its separate refit package
  `research/concentrated-prelife-refit`), the change is 2664(H8−H7−H1) + 666(2H1−H2), which is not a dominance.
  PR2751 still wins: that head's profile is rejected at PR2751's C (M−1 = 2.53e-6), a C gap of 8.86e-7. This is
  computed in the registered run.
- **#2767, files carrying earlier profiles.** These files in `research/gmx-t74-borrow43-handoff/` carry values that
  differ from #2767's words and `new/PROFILE.json`, which carry the improved profile:
  - the top-level `PROFILE.json` equals PR2733@`2761b52b`'s complete profile;
  - README line 7 gives PR2733's local profile {…, 7:4, 8:4};
  - README lines 35 and 37 give still earlier values.

  The PROFILE.json comparison is computed in the registered run. The README lines were read at `e8b771ba` and
  `fd7c7a72` (local-only, not part of the registered run).

  If they deliberately describe predecessors, a label would help.

## Existing checks and overlap (refreshed 2026-10-16 04:19 UTC)

| Check (head) | What it covers for PR2751 | What it does not cover |
|---|---|---|
| #2766's registered `independent_check.py` (DavidAriasC, `e6df920c`) | Frame recount of PR2751's own words. A forward and dual free-operator replay, through cleanup, of #2766's words, which differ from PR2751's only in the B1151 frame, with a lender-holds-input check at warps 47–58. The B1151 difference itself. | Pair pre-states, the change set against PR2733, the PR2720 relation, the fill and complete profile, PR2751's endpoint and κ |
| #2768 (tekuuu, `e7fd43cf`) | The PR2751 author's complete native replay of PR2751's providers, with 512-column warp checks (author-checked, not independent) | — |
| [PR2804](https://github.com/CrocSwap/integer-mult-bounds/pull/2804) (this author) | PR2530's words, an ancestor; not PR2751 | — |

**Related work on different questions:**
- [PR2823](https://github.com/CrocSwap/integer-mult-bounds/pull/2823) (mdumitrean) certifies cold-host restoration
  obstructions on #2802's words.
- philippeVV's comment on #2802 concerns its followers.
- [PR2847](https://github.com/CrocSwap/integer-mult-bounds/pull/2847), from a separate session of this account,
  independently verifies #2802's increment over PR2751 (published 2026-10-16 02:17 UTC). It does not re-derive
  PR2751's recovery, which is checked here; the two packages are complementary.

**Where else I looked:**
- PR2751 and PR2720 have no PR comments or reviews.
- Main's PR ledger (at `d311a18c`, research/community-efficient1700-audit) records both as "partially reviewed":
  exact-head metadata and the changed-file inventory are collected, and substantive maintainer review is in progress.
- Discussion [2612](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612), where both were posted, holds
  the authors' RESULT/DONE posts, this audit's claim, this account's PR2847 result and follow-up T74 claims on this
  lineage (#2848, #2857); none audits PR2751 or PR2720.

The searches covered PR comments, PR bodies since 2026-10-15 18:00 UTC, and Discussions 2612, 1163 and 1166. Not
finding another check is not proof that none exists.

## Result

| Claim (PR) | Checked here | Result |
| --- | --- | --- |
| Both changed words are exact for arbitrary dirty inputs (PR2751 PROOF.md) | Free-operator replay, forward (Y += X) and dual (X -= Y), 639 independent inputs and 72 zero buffers, through cleanup and the target endpoint; the 36 initial corrections emulated exactly | exact in both words |
| Warp algebra | 65 B records and 24 A-prelude items (12 lenders x {K, K^-1}): invertible, symplectic, Fourier rank 0 | pass |
| All 12 lenders hold their original input | Exact rows before every A-prelude K_op and every B handoff | 12/12 hold X_r at both |
| The pair recoveries x += y/2; y -= x restore both sources | Exact pre-states (X_x-X_y)/2 and X_x+X_y, post-states X_x and X_y; adjacent; untouched before both handoffs; paid climbs at the 8 gates | all 4 pairs, 0 paid climbs |
| Cleanup | Shipped cleanup vs own inverse-reverse re-derivation | literal equality, 4540 items at FULL |
| Local profile {1:2366,2:646,3:297,4:120,5:26,8:8} | Literal frame recount (both words) | equal; widths {4:26,5:9,7:62,8:78,9:240}, 415 helpers, 72 buffers, mass 5223 |
| All eight centre children rank 8 | Recount COPY paths | 8 x [8] |
| Lifted targets 14,21,37,41,43,47,52,78,99,104,106,110 at [45], none read at the cut | Recount + cut census | equal; 176 unframed cut gates write 88 targets, none lifted |
| Delta 4(H8-H7-H1) per word vs PR2733@2761b52b | Exact structural diff + recount of both words | change set: alias swap, echo blocks, moved recovery pairs, charts of ops 47–50; per-section paid histograms equal except the cut ({1:4,7:4,8:4} → {8:8}); delta {1:-4,7:-4,8:+4} |
| PR2720: Q on rows (23,34,50,108) has det -1/16 (PR2696 words) | Own replay at the prelude boundary and at the cut; residual; continuation T | Q, det, residual, forced centres {9,92,224,240} and invoice {1:4,7:4,8:4} reproduced; rank T = 112; E_P + T Q_P = 0, i.e. PR2720's F_P + T Q_P = I_P with E_P = F_P − I_P |
| PR2751 escapes PR2720 | The same projection on PR2751's words | zero on (23,34,50,108); correction on (21,37,47,110), rank 4, det 1/2, none cut-written; T identical in PR2696, PR2733 and PR2751 |
| Each partner correction is the echo of the helper it replaces | Free-symbol replay of the deleted / re-instated echo blocks | exact for all 8 blocks |
| Complete profile {1:1593072,2:430236,3:204396,4:79920,5:22532,8:5328,32:1,48:26558} | 276,390 FILL rows, R-a..R-e and the R-c recount, two implementations, windows from PR2269's template | equal; idle {1:17316,3:6594,5:5216,32:1,48:26558} |
| Complete delta 2664(H8-H7-H1) vs PR2733 | PR2733's FILL priced the same way | delta {1:-2664,7:-2664,8:+2664}, identical idle profiles |
| Physical stock 66801 = 66304+415+8+72+2 | Helpers and private buffers recounted from the words | 66801 |
| Endpoint C = 0.001717141586348426338109 | Rigorous enclosure of M(a) (2^-640 fixed point) | M(C)-1 = -1.96e-24 (accepted); M(C+1e-24)-1 = +8.98e-25 (rejected); root - C = 6.857e-25 |
| κ = C − 1e-46 − 1e-70 | Exact rational arithmetic on CLAIM.json | CLAIM.json's κ equals C − 1e-46 − 1e-70 exactly |
| PR2751 vs PR2733's current head `a63c55ff` | Pinned refit CLAIM.json; same enclosure | delta {1:-1332,2:-666,7:-2664,8:+2664}; head profile rejected at PR2751's C (M−1 = 2.53e-6); C gap 8.859e-7 |
| Downstream structure | Parse of the words of #2802, #2818, #2824, #2827, #2833 | the four pairs with PR2751's frames, ops 47–50 charts on line 45, the 12 lifted targets: present in all five (#2833 shifted by 4 gates) |
| (#2766, #2767) identical complete profiles | Recount of their four words (#2767's inline B warps parsed) and both fills, two implementations | identical, {1:1591740,2:430902,...}, each equal to its declared profile |

## Reconciliation with PR2720: which of its hypotheses PR2751 changes

PR2720's hypotheses and premises are quoted verbatim from its pinned README (lines 23–42, 81–88 and 111–116; the
quotes are stored in `RESULT.json` and re-extracted from the pinned bytes on every run). They are evaluated as
computed booleans on PR2696's words, PR2720's own input, as the reference:
- **PR2733** is the positive control: it satisfies every evaluated item and pays exactly 4H7 + 4H1 + 4H8.
- **PR2751** changes the four partner aliases, which PR2720's family explicitly excludes ("It does not include
  changing the four partner aliases …").

| PR2720 item (verbatim clause, abbreviated) | Computed as | PR2733 | PR2751 |
| --- | --- | --- | --- |
| 1 "Keep the original recovery operations and inherited P-source helper paths" | 1a: P warp records (G, U, E) equal PR2696's; 1b: P prelude blocks use PR2696's operator, port and line; 1c: each P source aliases PR2696's removed helper | true | **false** (1a, 1b and 1c all false; the recovery operations are also moved) |
| 2, compensation clause: "Its additional source-dependent terms use only original R inputs" (h2a) | P-source compensation terms equal PR2696's (rows 23, 34, 50, 108 with PR2696's Q) | true | **false** (new P terms on rows 21, 37, 47, 110) |
| 2, continuation clause: "The target-to-target linear continuation … is unchanged. No continuation operation reads a target into a non-target" (h2b) | T equal to PR2696's, no target read into a non-target, T invertible | true | true |
| 2, last clause: "All target scales are nonzero and target ADDs have distinct endpoints" (h2c) | direct check | true | true |
| 3 "The original P-source response … is retained" | E_P equal to PR2696's | true | **false** (computed: E_P moves to rows 21, 37, 47, 110) |
| cut bill: "pinned centre-to-target cut incidences" | cut list equal to PR2696's | true | true |
| cut bill: "at least one zero-frame reader per centre" | every centre writes a level-0 target | true | true |
| cut bill: "Retain rank-eight producers" | every centre frame has dimension 8 | true | true |
| cut bill: "exact line-30 cut frames" of 23, 34, 50, 108 | declared target levels | true | **false** (those targets are no longer lifted) |
| cut bill: "the descending private-copy model used by PR2696" | not evaluated (assumed by construction in the floor computation) | — | — |
| cut bill: "No target chart changes or nonmonotone target frame paths" | not evaluated (the lifted-target set changes; see `diff.target_levels`) | — | — |

**The mechanism, checked gate by gate:**
- In PR2733 the partner sources 33, 55, 74 and 85 take the roles of removed helpers 640, 641, 642 and 644. Their
  early echo reads land on targets 23 and 50 (read at the cut by centres 9 and 240) and 34 and 108 (read by centres 92
  and 224).
- PR2751 assigns them instead to 696, 697, 698 and 700, with new charts K47–K50 that send the ports to line 45. Those
  echoes land on 21, 37, 47 and 110, which no cut gate writes.
- Each partner correction equals the echo of the helper it replaces, coefficient for coefficient.

**What PR2751 already states.** PR2751 states this relation itself: it "deliberately changes the old-four recovery
paths held fixed by PR2720" (README line 62). PR2720's first open question asks whether a changed recovery or
assignment involving {33, 55, 74, 85} can remove a forced correction; PR2751 answers it constructively. This package
is an independent, computed confirmation that also localises the change.

## Who builds on this (structure computed at the heads below)

| Later PR (author, head) | Relation to PR2751 | What carries over |
|---|---|---|
| #2766 (DavidAriasC, `e6df920c`) | PR2751's words with one frame changed (B1151), and PR2751's fill | the words' algebra, the partner reassignment and the reconciliation; the complete profile is checked here |
| #2767 (jeremykothe2, `e8b771ba`; its newer head `fd7c7a72` changes only receipt pins, outer-ledger files and its verify.py; every input pinned here is byte-identical) | reaches 8H8 by another route (post-cut partner corrections, inline B-phase warps), its own fill; with the same frame refit it reaches #2766's complete profile | the complete profile only; its PR2720 classification is open question 2 |
| #2802 (mdumitrean, `17b2ee6e`), #2818 (jeremykothe2, `175822ae`), #2824 (Dugongue, `f1826afe`), #2827 (Dugongue, `4dc1286a`) | identical word files (#2802's construction on PR2751's words) | the four pairs with PR2751's frames, ops 47–50 on line 45 and the 12 lifted targets are present (structural check); their words are not replayed here |
| #2833 (jeremykothe2, `e9307b48`) | #2802's construction with a dirt-entry rewrite | the same structure, shifted by four gates; not replayed here |

**Not checked here.** These claims were opened after the downstream set was fixed, before the 04:19 UTC refresh:
- #2839 (Dugongue, `2fdd289f`) ships #2802's word blobs `91bd9c68`/`6c4a9a43`, so the structural result carries over
  by blob identity.
- #2843 (mdumitrean, on #2833).
- #2848 (Lyy-iiis, on #2843's allocation).
- #2852 (dataisfire, on #2843 and #2833's words).
- #2853 (philippeVV, stacked on #2833).
- #2855 (Dugongue, on #2848).
- #2856 (mdumitrean, composing #2853's words).
- #2857 (Lyy-iiis, changed words from #2833).

## What is checked, and how

- **Modules:**
  - `audit_words.py`: words, warps, recount, census, lenders and pairs.
  - `audit_diff.py`: the change set against PR2733.
  - `audit_reconcile.py`: PR2720's objects, the quotes and the hypothesis booleans.
  - `audit_pricing.py`: the fill, complete profile, stock, endpoint and the PR2733-head comparison.
  - `audit_others.py`: #2766/#2767 and the downstream structure.
  - `audit_controls.py`: the negative controls.
- **Reused code.** `vendor/` holds this author's earlier checkers, pinned by git blob and SHA256 and executed from
  exactly the verified bytes: PR2315 `words_check.py`, PR2387 `fill_check80.py`, and PR2804's `audit_common.py`,
  `check_words.py`, `check_fill.py` and `check_accounting.py`.
- **PR files are data only.** Every PR file is read with `git show <commit>:<path>` and checked against its pinned
  blob and SHA256. No code of the audited PRs (#2751, #2720, #2696, #2733, #2766, #2767, #2802, #2818, #2824, #2827,
  #2833, #2269) is imported or executed.
- **Git isolation.** Every git call drops the GIT_* redirection, config-injection and config-file variables, and sets
  `GIT_NO_REPLACE_OBJECTS=1` and `GIT_NO_LAZY_FETCH=1`.

## Controls

There are 356 negative controls, 218 of them distinct; the PASS line reports 356/356 rejected.
- **Named rules.** Each control names the rule that must reject it, and the run fails if any other rule rejects it,
  or if a control is accepted.
- **Counting.** Attempts and rejections are counted separately.
- **Pipeline vs function controls.** "Pipeline" controls run the mutant through the main check. "Function" controls
  run the named check on a mutant that an earlier check would reject first; their names end in `: check_…`.
  - The lender, pair pre-state, pair-restored and centre-rank rules have function-level controls only, for that reason. The
    replay rejects those mutants earlier.

| Group | Count | Covers |
| --- | --- | --- |
| words_pipeline | 70 | replay (including a dual-only mutant that the forward replay accepts), warps, report, providers, registers, cut census (including a targets-written-only change), lifted, profile claim, counts, corrections, cleanup, pair adjacency, untouched x and y registers for all 4 pairs at both ends of the window |
| words_function | 92 | centres; lifted frames; lenders at the A prelude and B handoff for all 12 lenders, lender count and ops; pair gate identity, pre-states (x and y rows) and restored values for all 4 pairs; tracker |
| diff | 26 | fields, removed set, start frames, target levels, report, warps, cleanup, A, B, profile delta |
| reconcile_pipeline | 72 | Q support, det and matrix (computed and published side); cut; zero readers; cut floor; E_P; PR2751 zero-on-PR2720-rows, support, rank, det (including det −1/2), not-cut-written; T identity; 28 hypothesis controls, each flipping a named boolean through the pipeline and asserting the exact flipped list (including an h3 value change on an unchanged support) |
| reconcile_function | 23 | verbatim quotes (including blank-padded line ranges), provider agreement, echo identities, PR2720 input bytes, T rank, E_P + T Q_P |
| wiring | 4 | both providers ran the identical check spec; every self-check ran |
| fill_rules | 10 | R-a, R-b (overlap, prefix), R-d, R-e in both implementations |
| pricing | 31 | profile claim, two implementations (direct, through `price()` on PR2733's fill, and coverage of all four fills), mass, idle identity, delta, stock, endpoint accept/reject at C and at a straddle point, κ, improvement, fill format, widths, dispatch, order projection, windows, template, PR2733-head comparison |
| others | 11 | #2766/#2767 inputs, report, identity, declared profiles; #2767's top-level profile file and the wiring of its comparator |
| downstream | 11 | pair frames, pairs, charts, lifted targets, coverage; the parsed bytes match each pin and differ from PR2751's words |
| vendor_pins | 6 | each vendored or reused file with one appended line |

There are also 2 plumbing controls (16 injected paid climbs at the recovery gates), reported separately and outside the
count above.

**Positive controls (9, all executed):**
- the PR2733@`2761b52b` and PR2696 words pass the same pipeline and reproduce their own claimed profile, helpers and
  buffers (2 each);
- PR2733 satisfies every evaluated PR2720 item (both providers);
- PR2733's fill reproduces its global profile;
- the endpoint check accepts PR2733's C and rejects C + 1e-24;
- it does the same at PR2733's `a63c55ff` endpoint.

**Mutation test (local-only, not part of the registered run).** Each mutation was run on a copy with `--out`, and
every one ends with a FAIL line:
- 103 mutations of this checker, run against the second-round code;
- 7 new mutations and a 10-mutation sample of the earlier ones, re-run against the final code.

The mutations include:
- self-comparisons of each equality;
- dropping the dual or forward replay;
- weakening the matrix, determinant, rank and support checks;
- each hypothesis boolean hard-coded or weakened;
- the quote checks dropped;
- per-pair and per-lender checks restricted to one instance;
- the two-implementation comparison restricted to one fill;
- the endpoint accepted on the wrong side;
- the downstream checks dropped;
- the self-check calls removed from `verify.py`;
- the git-environment scrub removed.

## Reproduce

```sh
python3 -I -B research/t74-2751-joint-twelve-audit/verify.py --fetch
```

Here (CPython 3.14.4) a run takes about 3 min and peaks at about 1.0 GB. The `--out` run and two comparison runs gave
a byte-identical `RESULT.json`. Expected final line:

```
PASS_T74_2751_JOINT_TWELVE_AUDIT words=2x639-inputs-fwd+dual profile={"1":2366,"2":646,"3":297,"4":120,"5":26,"8":8} centres=8x[8] lenders=12 pairs=4 delta_vs_2733={"1":-4,"7":-4,"8":4} Q2720_det=-1/16 Q2751_det=1/2@21,37,47,110 changed=h1,h1a,h1b,h1c,h2a,h3,line30 complete={"1":1593072,"2":430236,"3":204396,"32":1,"4":79920,"48":26558,"5":22532,"8":5328} roles=276390 complete_delta={"1":-2664,"7":-2664,"8":2664} physical=66801 C=0.001717141586348426338109 kappa=C-1e-46-1e-70 vs_2733_head={"1":-1332,"2":-666,"7":-2664,"8":2664}@gap8.859e-07 pr2766_eq_pr2767=True downstream=2802,2818,2824,2827,2833 negative_controls=356/356-rejected distinct_controls=218 positive_controls=9 pinned_inputs=49
```

**What `--fetch` does.** It fetches only missing pinned commits, into `refs/audit/prN`; it needs git ≥ 2.29 and
network access. The pinned commits are unmerged PR heads, so the replay stays reproducible only while GitHub retains
them.

The registered command has been run only on CPython 3.14.4. The Python 3.12 replay was not run locally; the code is
syntax-checked for Python 3.8 and later.

## Scope limits

- **Warp letters are abstract.** The physical identity of each K_op shared by the A prelude and the B handoff,
  including the new charts of ops 47–50, is not checked (Clifford phases, monomial lifts). Only the chart algebra over
  GF(2) and the symplectic structure are checked.
- **The 36 initial corrections are uncharged** in the frame recount, as in PR2679, PR2733 and PR2751. They are an
  identical multiset in PR2733 and PR2751.
- **Author-checked stages.** Native precision, strict supplier and global admission, and the 63 outer inequalities
  are not re-derived. CLAIM.json's κ is checked as arithmetic on the enclosed C.
- **Inherited assumptions:** window semantics, free interleaving, and the stock terms 8 and 2.
- **PR2720's theorem is not re-proved.** Its hypotheses are evaluated as computed proxies, and two cut-bill premises
  are not evaluated (see the table).
- **One wiring path is guarded only by construction.** If `verify.py` passed a re-serialised copy of PR2733's profile
  in place of #2767's top-level PROFILE.json bytes, that observation would trivially hold. It is an observation about
  #2767's documentation, not a headline result.
- **Downstream PRs are only parsed.** Their words are checked structurally, not replayed. Only the complete profiles
  of #2766 and #2767 are recomputed.

## Open next questions

These close obligations of PR2751's own claim and of the reconciliation. No further word or fill optimisation is
proposed (family expansion decision: none).

1. **Are the new K47–K50 charts the same physical operators in the A prelude and at the B handoff?** This includes
   Clifford phases and monomial lifts.
   - *Why:* the free-operator replay proves the algebra for any invertible letter, so the native identity is
     author-checked only. #2766 and #2802 reuse these charts.
   - *First step:* re-implement the 512-column monomial check for ops 47–50 from PR2751's native receipts. The
     author-side coverage is PR2751's own warp checks and #2768's native replay; what is missing is an independent
     re-implementation.
   - *Blocker:* none.
2. **How do PR2720's hypotheses classify #2767?**
   - *Why:* #2767 reaches 8H8 by moving partner corrections past the cut, which appears to change hypothesis 2 instead
     of hypothesis 1.
   - *First step:* extend `audit_reconcile` to locate the P corrections in B (via `audit_others.parse_inline`), then
     evaluate the booleans on #2767's words. PR2720 also excludes "moving compensation past its boundary".
   - *Blocker:* none.
3. **Do PR2751's strict supplier admission and its 63 outer inequalities hold when re-derived independently?**
   - *Why:* κ = C − 1e-46 − 1e-70 is arithmetic on the checked C, given those author-checked stages.
   - *Blocker:* executing PR code, or restating the inherited ledger formulas.

## Independence, conflicts and credits

**Independence.** The checking code is independent of the audited PRs' code.

**Conflicts:**
- **Credits to this author.** PR2751's `SOURCE-NOTICE`, and PR2720's retained `inputs/UPSTREAM-NOTICE` and
  `GENERATOR-NOTICE.txt`, credit this author's PR1964 (Lemma G label/adapter checks and X/Y/Z mutants) in the
  inherited T74 lineage. PR2720's `inputs/PR2696-NOTICE` lists thakrarsagar among inherited contributors. Neither PR
  credits this author for the words, assignment or floor audited here.
- **Reused code.** This package reuses this author's own earlier checkers (PR2315, now on main; PR2387; PR2804).
- **Related audits by this account.** This author's PR2804 audited PR2530, an ancestor in PR2751's lineage. PR2847, from
  a separate session of this account, audits #2802's increment (see Overlap).

**Credits:**
- **Audited:** tekuuu (Tekalign), PR2751; petalas, PR2720.
- **Predecessors:**
  - mason-hale: PR2696, the eight assignments.
  - tekuuu: PR2436, the lifted-target compensation.
  - zxv: PR2530, the source-partner pair recoveries.
  - philippeVV (Philippe Van Velzen): PR2679, pre-life hosting.
  - jeremykothe2 (Jeremy Kothe): PR2462, PR2588, PR2673, PR2745 and the PR2269 template.
  - mdumitrean (Marius-Paul Dumitrean): PR2733 and its B1149 frame refit, which #2766 reuses.
  - Cinna Davis: PR2226, anticipatory dirty borrowing and the free-operator replay idea.
  - The credits in `vendor/NOTICE.md` also apply.
- **Related:** DavidAriasC (#2766 and its `independent_check.py`), jeremykothe2 (#2767, #2818, #2833), Dugongue (#2824,
  #2827).

Prepared by Sagar Thakrar with substantial AI assistance (Claude Code, Anthropic, Claude Opus 5.5):
- AI scouts chose the target.
- Three independent AI auditors did the checks, and AI builders consolidated and hardened them.
- Two rounds of AI review shaped the overlap statements, the reconciliation wording and the controls.

No independent human review is claimed. Apache-2.0.
