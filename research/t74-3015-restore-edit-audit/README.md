# Independent verification of PR #3015: the R1 restore edit on PR #2979's words (no κ; no defect found)

**Object.** Open [PR #3015](https://github.com/CrocSwap/integer-mult-bounds/pull/3015) (Jeremy Kothe, jeremykothe2;
head `e244296debb45fe6f4da84d29e4d64fbab55fda0`, package `research/rank7-joint-endframes-restore-edit`), which takes
[PR #2979](https://github.com/CrocSwap/integer-mult-bounds/pull/2979)'s words (Marius-Paul Dumitrean, mdumitrean;
head `be191346391661f4d35fc0d1508d0a6029572576`, merged, package `research/rank7-joint-endframes`) and PR #2979's
literal T74 allocation, and changes exactly one thing: the restore block `restore[178:180)` of both provider words.

```text
Status / UTC update / priority revision: DONE (audit) · 2026-10-16 19:35 UTC · priority revision 6 · base main d8e0f83f
Concrete question and changed premise: is PR #3015's single declared restore edit R1 exact, legal in the inherited
    frame model, and correctly priced through the complete T74 invoice to its claimed conditional κ?  (No premise
    of the construction is changed; this is an independent check with code that does not run either PR.)
Established result and evidence status: no defect found in the checked scope (independently checked, AI-assisted;
    no human review).  Both edited words are exact forward and dual through cleanup and the target endpoint over all
    632 independent inputs; the paid delta −2H1+H2 per call is exactly register 63's two rank-1 climbs merging into
    one rank-2 climb; the unchanged allocation gives the claimed complete profile, physical stock 66,813 and
    C = 0.001729150973534224428695 (κ = C − 1e-46 − 1e-70, +1.1699e-7 over PR #2979, both exact).  Up to the choice
    of carrier, R1 is the only improving rewrite of its class (adjacent same-target restore pairs, every legal third
    frame) on PR #2979's words, and none remains in that class on the edited words.  PR #3018's journal and PR #3021's
    composition (R1 + journal) reproduce from the same inputs.
Public artifact URL + exact commit: this package (see the PR); RESULT.json is the recomputed receipt.
Next useful task, success/stop test and rough runtime: a frame re-solve of the edited words (Open next questions);
    this package's replay takes about 3.5 minutes (`verify.py --fetch`).
Active claim / expiry, or released: released (no advance claim; bounded session).
```

## What this adds

PR #2979's coordinated rank-7 lowering already had six independent audits when this session started (#2993 frame
paths and V45 subsets; #2987 and #3010 chronological packing; #3006 and #3008 V45 native endpoint and events; #3014
frozen-owner invoice), one improving journal (#3018, an integrality exchange on the fill) and two live construction
claims. PR #3015, the newest conditional candidate on the same words, had no independent replay, frame recount or
endpoint check: its only new ingredient is R1; its own review (`edits/edits_review.py`) applies the author's pure
applier and runs the inherited #2833 auditor; PR #3021's finite checker (petalas) verifies R1's address and
preimage, its 3×3 rational scalar identity, the changed sections and the re-derived inverse cleanup of both edited
words, but takes the paid profile and its delta from the word report. This package checks R1 with code that imports
or executes nothing of PR #3015, PR #2979, PR #3018 or PR #3021:

- **Scope A, the edit itself.** The candidate words equal PR #2979's words outside `restore`, `report` and
  `cleanup`, and the restore sections differ by exactly the declared hunk (own diff, not the author's applier). The
  three new gates equal the two old ones as a formal operator on registers 22, 61, 63. A fresh monotone frame-chain
  implementation (second implementation next to this contributor's vendored recount) reproduces both paid profiles
  and attributes the whole delta to **register 63**: its climbs `7→8` (at the old gate 179) and `8→9` (at the end)
  become one climb `7→9` (at the new gate 180). Registers 22 and 61 keep their climb dimensions (61's `7→8` and
  `8→9` only move to the new gates 179 and 180); the five other registers whose labels move are the restore gates
  after the hunk, shifted by one index.
- **Scope A, a census of R1's class.** Every adjacent pair of restore gates `t += q1·s1; t += q2·s2` at one frame
  F, rewritten either way round as `s += (q'/q)·s'; t += q·s; s −= (q'/q)·s'` with the first gate at the span of the
  two current frames (the cheapest legal choice), the second at F and the third at **every** subspace between F and
  the intersection of the two registers' next frames; every rewritten word is recounted (cleanup re-derived),
  nothing is asserted. On PR #2979's words: 47 such pairs, 94 pair/carrier candidates, 122 rewrites recounted;
  **exactly two candidates have an improving option, and they are the R1 pair in its two carrier orders** (both
  −2H1+H2); 12 candidates have only losing options (+2H1−H2, or +4H1−2H2 at an intermediate third frame: the carrier's next
  frame is above the absorbed register's, so a single rank-2 climb splits) and the rest are neutral. On the edited words: 44 pairs,
  88 candidates, 108 rewrites recounted, none improves. This is one class, not the author's search over all
  2–4-gate blocks (Scope limits); the second rewrite petalas reported at 19:40 UTC (a covector shared by two
  non-adjacent consumers, below) is outside it.
- **Scope B, the words.** Both edited words through this contributor's lineage checks: parse with the 36 initial
  corrections, warp algebra of the 72 records, frame recount against the word report and the declared profile and
  inventory, forward and dual free-operator replays through the 5,208-item cleanup to the target endpoint (632
  independent inputs), the own exact tracker, the literal cleanup against an own inverse-reverse re-derivation (one
  item more than PR #2979's, at FULL), and the 91 private buffers as exactly the `helper_final` endpoints.
- **Scope C, the invoice.** PR #2979's allocation (FILL, ORDER, DISPATCH byte-identical in PR #3015; the FILL's
  SHA-256 is bound in both CLAIM files) priced with the recounted local profiles of the edited words in two
  implementations (271,728 roles, rules R-a..R-e, the R-c recount): complete profile
  `{1:1644348, 2:470862, 3:159468, 4:71928, 5:13716, 8:5328, 48:28190}` = PROFILE.json = CLAIM.json, rank mass
  4,816,512, complete delta 666 × (−2H1+H2) against PR #2979, idle remainders unchanged, physical stock
  66,304 + 408 + 8 + 91 + 2 = 66,813.
- **Scope D, the endpoint.** C = 0.001729150973534224428695 accepted (M(C) − 1 ≈ −5.9e-25) and C + 1e-24 rejected
  (+2.3e-24) by an own rational-interval enclosure (ln by dyadic splitting and the atanh series, exp by Taylor with
  tail bound, outward rounding at 1e-60; any rank) and by the vendored 640-bit enclosure of PR #2804 (width 3e-191);
  κ = C − 1e-46 − 1e-70 equals the CLAIM; the gain over PR #2979, `58495443855455489/(5·10^23)` ≈ 1.1699e-7, is
  exact; PR #2979's profile is rejected at C; the 24-digit endpoint predicted from the profile alone equals C.
- **Scope E, PR #3018 and the PR #3021 composition.** PR #3018's 103-row journal (44 role moves, 59 offset-only
  compactions) applied to PR #2979's fill gives exactly PR #3018's RESULT profile
  `{1:1645684, 2:470196, 3:159472, 4:71928, 5:13710, 8:5328, 14:1, 48:28190}` and the 24-digit endpoint one grid
  step below its root bracket (the bracket lies in [C, C + 1e-24)). With R1's local profiles the composed profile is
  `{1:1644352, 2:470862, 3:159472, 4:71928, 5:13710, 8:5328, 14:1, 48:28190}` and the endpoint is
  **0.001729151203983018442998** (κ = endpoint − 1e-46 − 1e-70; +2.3045e-10 over PR #3015). This was computed here at
  about 18:40 UTC without having read PR #3021 (Nick Petalas, head `217edac2`), which published the same composition
  at 2026-10-16 18:21 UTC and has priority; it equals PR #3021's FINITE, OUTER-CLAIM and COMPOSITION records
  (profile, idle, physical, roles, κ and gain equal; PR #3021's root bracket lies in [C, C + 1e-24)). PR #3021's
  native/admission/outer release is author-run and not rerun here.

## Findings for the author (non-blocking)

1. **`TASK.json` is PR #2979's file, byte for byte** (git blob `cbc9bcc5b1d4a7ef69ae983ab0cba218cf6ef7d2` in both
   packages): author "Marius-Paul Dumitrean", task `complex-new-helper-inventory`, priority revision 5, base
   `484a8ade`, and an `actual_scope`, `evidence` and `open_questions` that describe PR #2979's three stages, not R1.
   The README and CLAIM.json credit R1 correctly; the task card does not. (`VERIFY.json`, `SOURCES.json`,
   `verify.py` and `producer.py` are also PR #2979's blobs; `run_registered.py` and `reproduce.py` differ.)
2. The README's status line is dated `2026-10-17`; the PR was opened on 2026-10-16 at 17:54 UTC. The head commit
   is stamped `2026-10-17 04:26 +11:00`, so this is the author's local date; the field asks for UTC.
3. The mechanism of the saving is not stated in the README ("lowers the paid frame bill by 4925 units"); it is
   register 63 alone (above). The unit price is not reproduced here; the exact κ gain is.
4. The class census above may be worth a sentence: on the edited words no further adjacent same-target rewrite of
   R1's kind improves, consistent with R1 being the first edit of the author's search.

## Existing checks and overlap (refreshed 2026-10-16 20:53 UTC)

| Where | What it checks | Relation to this package |
|---|---|---|
| PR #3015 `edits/edits_review.py` (author) | the candidate equals the parent with the declared hunks (author's applier), the inherited #2833 auditor forward and dual, seven tamper controls per word | reproduced here with an own diff, own replays and tracker, and the frame delta attributed; the stale-cleanup case is shown to pass both replays and to be caught only by the literal cleanup check |
| #3021 `verify.py` `check_word` (petalas) | R1's address and preimage, the exact 3×3 rational scalar identity, only restore/report/cleanup change, the width inventory unchanged, the report's delta `{1:−2, 2:1}`, the literal inverse cleanup with 91 buffers (both edited words) | the closest existing check of R1; it does not replay the words, recount frames or price the profile (the delta is read from the report), which this package does |
| #2993 (petalas) | #2979's frame paths, five groups, 16 V45 subsets | different object (stage 1 of #2979); no word semantics, no R1 |
| #2987, #3010 (RossRichardson) | chronological packing of #2979's fill; the k = 940 frozen-fill boundary | the same fill is reused unchanged by #3015; this package re-prices it under the new local profiles |
| #3006, #3008, #3014 (petalas) | V45 native endpoint and events; frozen-owner invoice on #2942's assignment | different objects |
| #3018 (petalas) | integrality exchange on #2979's fill | its journal is applied and its profile and endpoint reproduced here (Scope E) |
| #3021 (petalas, 18:21 UTC) | composition of R1 with #3018's journal, author chain run | its finite records equal the composition computed here (without having read it; it has priority); its release is not rerun |
| #3022, #3024 (petalas) | T148 and T740 packings of #2979's fill | outside this package |
| #3028, #3030 (petalas, 19:08 and 19:18 UTC) | T148 and T740 releases with R1's words (T740 root ≈ 0.001729152756004331) | outside this package; they inherit R1 and are not checked here |
| #3042 (dcharb78, 20:15 UTC), #3050 (petalas, 20:44 UTC), #3051 (jeremydiviney, 20:52 UTC) | six restore carrier/pivot skips on PR #2979's words (the same restore region, register 22 among them; −12H1+6H2 per call), their independent audit, and a T740 release of them | alternative rewrites of PR #2979's words, not of PR #3015's; none audits R1 |
| #3044 (petalas, 20:22 UTC) and the 20:51 UTC claim (Discussion 2612, comment 18982803) | the shared restore covector R2 composed with R1 through a fresh T74 release; a proposed contraction of four ADDs in `restore[175:179]` (registers 22 and 230) to three | compose with or sit next to R1; not audits of R1 |
| petalas, active claim 19:40 UTC (Discussion 2612, comment 18981612; expiry 20:30 UTC; local-only) | a second restore rewrite on #2979's words: `restore[162:178]` reads the covector `X40 − 2·X54` into registers 18 and 22; formed once at their common rank-7 frame and undone at FULL, so X54 climbs 7→9; per-call −2H1+H2, composed with R1 to `{1:2441, 2:708, 3:232, 4:108, 5:18, 8:8}` | outside R1's class (two non-adjacent consumers, two targets); not an audit of R1; bears on Open next question 2 |

No independent replay, frame recount or endpoint check of R1 existed on the board at 2026-10-16 20:53 UTC (PR #3015 had no
comments or reviews; PR #3021's `check_word` is the closest, above). The overlap helper (`scripts/find_overlap.py`
with a scratch cache outside the checkout, refreshed at 19:36 UTC: 276 open PRs and 1,756 discussion records, complete
pagination) and the PR comments of #3015, #2979, #3018 and #3021 were read.

## Result

| Check | Result |
|---|---|
| hunk | `restore[178:180)` → 3 gates in both words; words equal outside restore/report/cleanup; minimal hunk = declared hunk |
| net operator | old = new on {22, 61, 63}: `22 −= 61 + 63`, 61 and 63 unchanged |
| frames | all three new gates legal (monotone): `V45 ⊂ F8 ⊂ FULL`; V45 = E_7 ∩ E_42 ∩ E_45 (computed, rule `edit.v45`), the rank-7 subspace of #2979's stage 1 |
| local profile | `{1:2445, 2:706, 3:232, 4:108, 5:18, 8:8}` → `{1:2443, 2:707, 3:232, 4:108, 5:18, 8:8}` (two implementations); inventory `{4:26, 5:2, 6:16, 7:52, 8:99, 9:213}` and mass 5,139 unchanged |
| attribution | climb dimensions change for register 63 only: `[…, 4→7, 7→8, 8→9]` → `[…, 4→7, 7→9]` |
| words | forward and dual exact, 632 inputs, 36 corrections, 72 warps, 408 helpers, 91 buffers, cleanup 5,208 items = own re-derivation, all at FULL; own tracker: targets Y+X, restored registers own, buffers zero before cleanup, identity after |
| allocation | 271,728 roles pass R-a..R-e in both implementations; complete profile = PROFILE.json = CLAIM.json; mass 4,816,512; physical 66,813; idle `{1:17310, 3:4956, 5:1728, 48:28190}` and the delta `{1:−1332, 2:+666}` are the model's consequences of unchanged widths and fill, checked but not independent evidence |
| endpoint | C accepted, C + 1e-24 rejected (own and vendored enclosures agree); κ = C − 1e-46 − 1e-70; gain over #2979 exact; #2979's profile rejected at C; root 0.0017291509735342244286952066… |
| census | parent words: 47 pairs, 94 pair/carrier candidates, 122 rewrites recounted, 2 with an improving option (R1, both carriers), 12 with losing options only; edited words: 44 pairs, 88 candidates, 108 recounted, 0 improving |
| #3018 | journal applies (103 edits); profile and endpoint reproduced |
| #3021 | composed profile, idle, physical, roles, κ and gain equal; PR #3021's root bracket lies in [C, C + 1e-24) |
| controls | 117 negative controls rejected by their named rules (85 distinct; edit 44, words 20, fill rules 10, pricing 17, κ 21, journal 5), 8 positive controls, 7 vendor-pin controls; checker mutations: see below |

### Checker mutations

`verify.py --mutations` applies each of the 23 textual mutations of the local checkers (a disabled monotonicity
check, net-operator check, hunk checks, attribution and delta checks, two-implementation comparison, dual replay,
literal-cleanup check, declared-profile, count and tracker checks, profile/delta/idle/preimage comparisons,
accept/reject verdicts, κ and gain checks, the ln 2 constant) in a subprocess in `--fast` mode and counts a mutation
as killed only when the run ends with an audit rejection (a wrong answer or an accepted control; a crash does not
count): **23/23 killed, 0 survived** (local run, 2026-10-16 20:52 UTC, `--jobs 3`, about 14 minutes). A first sweep had three survivors (a disabled outside-hunk check masked by the length check, the
dual replay bypassed by a control that called it directly, a disabled enclosure-intersection check masked by the
verdict check); the controls were extended so that each is now killed.

## The R1 edit, as checked

```text
old (PR #2979, restore[178:180)):            new (PR #3015, restore[178:181)):
  add 22 ← −1·61   @ F8                        add 61 ← +1·63   @ V45   (rank 7)
  add 22 ← −1·63   @ F8                        add 22 ← −1·61   @ F8    (rank 8)
                                               add 61 ← −1·63   @ FULL  (rank 9)
F8  = ⟨256,128,64,34,16,10,4,1⟩,  V45 = ⟨256,128,64,35,16,11,5⟩ ⊂ F8 ⊂ FULL
```

Before the block both 61 and 63 are at V45. In the old block both must climb to F8 (one rank each) and later to
FULL (one rank each at the end). In the new block 63 is read at V45 and then at FULL only, so its two rank-1 climbs
become one rank-2 climb; 61 climbs as before. In the inherited pricing a rank-2 child costs less than two rank-1
children, hence −2H1+H2 per call, 666 calls, and the exact κ gain above. The cleanup, which inverts the non-target
gates in reverse order, gains one item; the parent's cleanup would still make both replays pass (same net operator),
which is why the literal cleanup is checked against an own re-derivation.

## Controls

Every negative control mutates a word, a fill, a claim or an expectation and runs it through the function the main
check uses; `audit_lib.expect` counts the attempt before the mutant runs and records the control only after the
rejecting rule id (and replay stage, where named) was asserted, so attempted and rejected are counted separately
(117 = 117). Highlights:

- a new gate dropped, a coefficient flipped, a ratio of 2: rejected by the own diff, the net-operator check, the
  forward replay (before cleanup) and the own tracker;
- the old frame kept on the new gates, or the third gate at F8 instead of FULL: legal words with no saving, rejected
  by the declared-profile check and by the attribution (no delta);
- one generator dropped from the first new frame: rejected by both frame implementations (non-nested climb);
- the parent's cleanup on the candidate: passes both replays (recorded) and is rejected by the literal cleanup check;
- a cleanup prepended with `helper += zero buffer`: passes the forward replay and the own tracker, rejected by the
  dual replay (buffers after cleanup);
- the symmetric rewrite with 63 as carrier: same delta, rejected by the attribution (the saving moves to 61);
- fill mutants (a role dropped, an overlap, a non-prefix bin, a role outside its window, a role on the caller's
  active pair), each rejected by its rule in both implementations; a legal re-hosting changes the profile and is
  rejected against PROFILE.json and against #2979's idle remainders; the parent's recounts against #3015's claim;
- endpoints at C ± 1e-24 and at each enclosure's straddle point, κ ± 1e-70, the claimed gain ± 1e-24, the
  improvement test with swapped roles, a shifted vendored enclosure, a prediction started above the root;
- PR #3018's journal with a wrong preimage, a repeated index, a changed helper, its last edit dropped (a non-prefix
  bin), and a profile with the rank-14 child at rank 13.

Positive controls: PR #2979's words through the same pipeline with their CLAIM profile; PR #2979's fill with the
parent recounts giving its PROFILE.json and CLAIM; PR #2979's endpoint; PR #3018's profile and endpoint; PR #3021's
composition; the R1 pair found by the census.

## Reproduce

```sh
# from the repository root; git >= 2.29 and network for --fetch (PR #3015, #3018 and #3021 heads into refs/audit/prN)
python3 -I -B research/t74-3015-restore-edit-audit/verify.py --fetch            # ~3.5 min, compares with RESULT.json
python3 -I -B research/t74-3015-restore-edit-audit/verify.py --fetch --out      # rewrites RESULT.json
python3 -I -B research/t74-3015-restore-edit-audit/verify.py --mutations --jobs 3   # ~15 min; every mutation must fail
python3.12 scripts/research_package.py --package research/t74-3015-restore-edit-audit   # registered replay (VERIFY.json)
```

Standard library only (Python 3.8 syntax; run here with CPython 3.14.4 on Linux, 4 cores; the registered 3.12 replay
was not run locally because no 3.12 interpreter is available, the command it registers was run directly). The run
reads the PR files with `git show` at the pinned commits and checks every blob id and SHA-256 (`SOURCES.json`);
nothing is written to the repository except, with `--fetch`, the fetched objects and `refs/audit/pr3015`,
`refs/audit/pr3018`, `refs/audit/pr3021`.

## Scope limits

- PR #3015's exhaustive search over all 2–4-gate restore-phase blocks (its Stack2979 harness, not shipped) is not
  reproduced; the census covers one class on both words.
- The three new frames are checked for legality and priced as given; a frame re-solve of the whole word is not done.
- The native chains, bootstrap, complete admission and outer release of PR #3015 and PR #3021 are author-run and not
  rerun; κ is checked as arithmetic on the complete profile under the inherited moment model with the inherited
  24-digit grid and margins.
- The fixed-inventory fractional cap certificate (`certificates/RELAX-CAP.json`) is not re-derived.
- PR #3018's sign proof and its own geometry checker are not re-derived; its journal is applied and priced under
  rules R-a..R-e.
- Window semantics and the free interleaving of independent replica controllers are inherited modelling assumptions.

## Open next questions

1. **Does a frame re-solve of the edited word beat `{1:2443, 2:707, 3:232, 4:108, 5:18, 8:8}`?** R1's frames came from
   the author's certified frame pricer; this package prices the given frames. First step: a monotone, gate-coupled
   frame optimizer over GF(2)^9 subspaces (shortest path per register with the gate constraints), run on the parent
   and the edited words. Blocked by: that optimizer has to be written; none of this contributor's checkers has one.
2. **Which other 2–4-gate restore blocks re-synthesise with the same net operator and a lower profile?** The census
   here finds R1 unique in its class and the class exhausted after it. First step: enumerate contiguous blocks and
   their equivalent gate sequences (commutations, carrier changes) and price them with the own chain. Blocked by: the
   allowed re-synthesis needs a specification; the author's harness is not shipped.
3. **Does PR #3021's release at 0.001729151203983018442998 survive an independent admission check?** The finite side
   is reproduced here; the native/prefix/outer side is author-run. First step: an independent reading of the admission
   receipts against the composed fill (as #2804's stock and prefix checks did for #2530). Blocked by: nothing but time.

## Independence, conflicts and credits

**Independence.** All code in this package and in `vendor/` is this contributor's (Sagar Thakrar, thakrarsagar;
substantial AI assistance from Claude Code, Anthropic). No file of PR #3015, #2979, #3018, #3021 or of the packages
they build on is imported or executed; their files are read as data at pinned commits. Two implementations are used
where the lineage's checks exist twice (frame recount, fill rules, moment enclosure).

**Conflicts.** None known. Other sessions of this account run in parallel on other tasks; none audits PR #3015 on the
board as of 2026-10-16 20:53 UTC (the account's open PRs are #2215 and #2361).

**Credits.** Jeremy Kothe (jeremykothe2) for PR #3015 (R1, the edit stage and its review), and for PR #2957/#2966's
rewrites in the words; Marius-Paul Dumitrean (mdumitrean) for PR #2979 (the words, the rank-7 overlay, the literal T74
allocation, the cap machinery) and PR #2942/#2930; Nick Petalas (petalas) for PR #3018, PR #3021 and the V45/native
audits; Ross Richardson for PR #2987/#3010; Mason Hale (PR2917), Jeremy Diviney (PR2908), Yiyang Lu (Lyy-iiis),
Tekalign (tekuuu), Dugongue, philippeVV, themilkman216, icekylinx (credited in PR #2979's and PR #3015's packages)
and Zhihao Chen (jacklightChen) (two contributors; checker lineage, see `vendor/NOTICE.md`), and the retained T74
lineage credited in PR #2979's and PR #3015's packages; Douglas Colkitt for the research framework. The vendored
checkers' own predecessor credits are in `vendor/NOTICE.md`. Apache-2.0.
