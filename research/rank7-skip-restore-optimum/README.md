# Restore-only optimum for PR #3042's six-skip words: every exact restore costs at least 10,868,103,087 (no new κ)

```text
Status / UTC update / priority revision: FINDING (scoped exact negative) · 2026-10-17 UTC · priority revision 6 · base main 18aacb21
Concrete question and changed premise: PR #3042 (dcharb78) removed six restore-phase visits from PR #2979's words with two
    declared restore edits; Nick Petalas's top claim PR #3054 uses the same six-skip words. PR #3057 and PR #3065 prove the
    restore (and joint A/B/restore) FRAMES optimal for the fixed scalar order. Can a different restore gate sequence (more
    carrier or pivot skips, any exact rewrite) lower the local frame bill when A/B, warps, cut, helper ends, start frames
    and buffers stay fixed and all frames are re-solved?
Established result and evidence status: no. On both providers every exact restore-only rewrite costs at least
    LB_forced + forced restore-phase visits = 10,867,765,164 + 337,923 = 10,868,103,087, the certified cost of PR #3042's
    words, which attain it. The same bound on PR #2979's words leaves exactly dcharb78's realized 29,976. Author-checked
    (AI-assisted), stdlib verifier; not maintainer-reviewed. Also corrects PR #3042's README attribution of the two edits.
Public artifact URL + exact commit: this package (see the PR).
Next useful task: A/B-phase re-synthesis (the 161,558 forced-cap units and the 192,384 kernel/preload visit units are
    forced by A/B), or a changed target port interface; restore-only search on these words is exhausted.
Active claim / expiry: released.
```

## Result

| word (both providers identical) | certified local cost | LB_forced (empty restore + 88 forced caps) | forced restore-phase visits | bound | gap |
|---|---:|---:|---:|---:|---:|
| PR #3042 six-skip words (`WORD-3042-{base,extra}`) | **10,868,103,087** | 10,867,765,164 | 337,923 | **10,868,103,087** | **0** |
| PR #2979 words (same A/B; calibration) | 10,868,133,063 | 10,867,765,164 | 337,923 | 10,868,103,087 | 29,976 |

Costs are the certified frame solver's integer local costs in units of 2⁻⁴⁰ at the base saving b = 0.001703676387993676
(c1 = 2,116,671, c2 = 4,228,346, c3 = 6,338,140, c4 = 8,446,713, c5 = 10,554,378). A visit that splits a climb of D ranks
into a + (D − a) costs c_a + c_{D−a} − c_D: 4,996 (1+1), 6,877 (1+2), 9,979 (2+2), 8,098 (1+3). The 51 visits of PR #3042's
literal frames are 20 × 4,996 + 23 × 6,877 + 8 × 9,979 = 337,923, and at profile level

```text
{1:2433, 2:712, 3:232, 4:108, 5:18, 8:8}  =  LB_forced {1:2370, 2:693, 3:255, 4:116, 5:18, 8:8}
                                             + 20 (2H1 - H2) + 23 (H1 + H2 - H3) + 8 (2H2 - H4).
```

The restore's total overhead over the unconstrained empty-restore optimum is 499,481 = 337,923 (forced visits) + 161,558
(forced entry caps acting on A/B chains). Both parts are forced by A/B and by what the restored helpers must contain.

## Theorem

Let W be `WORD-3042-base` or `WORD-3042-extra` (PR #3042 head `84cc406a`, `edits/FINAL-WORD-*.json.gz`, byte-identical in
`data/`). A *restore-only rewrite* W′ keeps the initial corrections, precondition, compensation, A (with its prelude), cut,
warps, B, start frames, helper end frames, removed helpers and private buffers of W, and replaces the restore by any
finite sequence of scalar gates; all frames (A, B and restore) are re-solved. W′ is *exact* if PR #2833's auditor
(BORROW-WORD branch, `vendor/audit_local.py`, unchanged) passes forward and dual on W′ with its frames written back. The
proof uses only the auditor's forward end-of-restore requirements (Lemma 1), so the bound holds for every restore that
meets them. Then

```text
cert(W') >= LB_forced(W) + 337,923 = 10,868,103,087 = cert(W),
```

where cert is the exact frame optimum of the BORROW-WORD frame model (monotone register chains, paid rank jumps,
fixed interfaces: start/end frames, cut equality, warp entry equality, fixed centre descents). The class contains every
restore-only edit considered so far on these words (carrier/pivot skips, R2-style shared covectors, the PR #3056 and
PR #3060 replacements of `restore[175:179]`, which tie) and, with R′ = R, the frame reassignments of PR #3057 and PR #3065
(in this package's frame model).

## Proof

Write 𝓡 for the 91 restored helpers (end frames E_c, all below FULL), e_q for the restore-entry rows of the 632 live
registers in the auditor's free algebra, and F_r for register r's frame at its last vertex before the restore. L_r and
U_r are the solver's forward lower bound and the upper bound from r's other registers at that vertex, computed in the
capped empty-restore graph; they hold for every restore-only rewrite because A/B are unchanged.

1. **Auditor semantics.** After the restore the auditor requires, in its forward replay, every restored helper c to hold
   exactly its own input row x_c (`vendor/audit_local.py` line 444), no other live register to contain the variable c
   (line 445) and the target map (line 442); the restore may not write a target (line 340), a non-target may not read a
   target (line 335), and the restore holds no warps (line 323). These are the only facts the bound uses. They do not
   constrain the other final rows, and the derived inverse-reverse cleanup inverts them. Control: appending `0 += 1` or
   `62 += 70` at FULL to the restore changes two non-restored final rows; with frames re-solved the auditor passes forward
   and dual at cost delta 0, while appending `249 += 251` fails (`certificates/CONTROLS.json`). Keeping every final row
   identical is therefore sufficient for exactness but not necessary.
2. **Forced coordinates.** The 632 restore-entry rows are linearly independent (exact elimination, rank 632), so each
   x_c has unique coordinates M[c] in them. A restore is a product of invertible scalar gates, so the final row of c is
   Σ_q R′[c][q] e_q and exactness forces R′[c] = M[c] for every exact W′. The current restore realizes exactly these M.
3. **Forced caps.** If M[c][r] ≠ 0 (r ≠ c), the (c, r) entry of the product of elementary gates is a sum over gate paths
   r → u₁ → … → c; on such a path consecutive gate frames are nested and the last is inside E_c, and the first gate reads r,
   so F_r ⊆ E_c. Hence F_r ⊆ cap_r = ∩ E_c over r's restored receivers: **88 caps**.
4. **Merge.** In any feasible frame assignment φ of W′, replace every register's restore-phase climbs by one end climb.
   The result is feasible for the capped empty-restore problem (Lemma 3) and cheaper by Σ_r ov_r(φ), where ov_r =
   Σ c_{jᵢ} − c_{Σ jᵢ} ≥ 0 (weights are subadditive). So cert(W′) ≥ LB_forced + Σ_r ov_r(φ), with LB_forced =
   10,867,765,164 computed by exact elimination.
5. **Delivery and cleaning.** If M[c][r] ≠ 0, r is read at a restore-phase frame inside E_c by a register y with
   L_y ⊆ that frame ⊆ E_y. If a non-restored r enters the restore holding a restored input variable, it must be written
   below FULL: the span of restored-input parts of the registers at FULL never shrinks (FULL registers only meet FULL
   registers) and must end at 0.
6. **Departure (dual vectors).** Suppose r stays inside a frame G until, at time t, it jumps to its end frame E_r. Let A_t
   be the matrix of the restore prefix (rows = register rows in the e-basis) and d_r(t) = A_t⁻¹ e_r its dual vector, and
   O = {c ∈ 𝓡 : c ≠ r, E_r ⊄ E_c}. Then d_r(t) ≠ 0 and ⟨M[c], d_r(t)⟩ = 0 for c ∈ O, since after t no gate path leads
   from r to c. A gate `t += k·s` changes only d_s (by −k·d_t), so d_r changes only when r is read, by a register whose
   frame is inside G, and recursively; hence d_r(t) is supported on Z = {r} ∪ {y : L_y ⊆ G}. **If M[O][Z] has full column
   rank |Z|, r cannot stay inside G and then leave to E_r.** (This replaces lane K's partner-only rank test, whose columns
   omitted the registers that can sit strictly inside G; on these words both exclude the same frames.)
7. **Carriers.** Content sitting at a frame F (or inside a restored source's end V) that must reach a receiver which
   cannot sit there is carried upward by a register that sits there. A non-restored carrier then has two restore-phase
   jumps (≥ 2c1 − c2 = 4,996); a restored carrier is free only if its end meets E_c above F (resp. outside V); a BLOCKED
   register has no gate at its entry frame, so carrying needs a third jump, which costs at least β + 4,996 here.

**Classification** (`restore_bound.py`, all frames enumerated exactly). A register r with restored receivers or leaks is
*BLOCKED* when some receiver c with E_r ⊄ E_c (or its leak) admits no partner s with L_r + L_s ⊆ U_r ∩ E_c ∩ E_s of
dimension < 9. Then r has no gate at F_r and at least two restore-phase jumps; β_r is the minimum overhead over every
admissible entry dimension, every two-jump first frame G (enumerated; a reader must sit at G and the departure test must
pass) and every chain of three or more jumps. Every *OPEN* non-restored register is tested at every admissible entry frame
F ∈ [L_r, U_r ∩ cap_r]: if no F admits a skip (reader + departure), r pays a visit; if every skip frame leaves a receiver
that needs a non-free carrier, the group {r} ∪ (non-restored registers that can sit at F) pays one visit (*zero-sum*).
Lifts out of a restored source's end are charged the same way. Overlapping groups are merged and charged once; BLOCKED
members are admitted only when carrying costs them ≥ β + 4,996. Result on both providers: **42 BLOCKED registers,
Σ β = 292,959; 9 disjoint payer groups, 9 × 4,996 = 44,964; bound = LB_forced + 337,923 = cert(W).** ∎

## The 51 visits of PR #3042's literal frames, all forced

| restore block | visiting registers | units | verdict |
|---|---|---:|---|
| PR2857/PR2894 kernel-preload pairs | 3, 44, 46, 69, 105, 306, 308, 310, 322, 324, 326, 351, 367, 383, 399, 408, 412, 414, 424, 428, 430, 434, 436, 438, 439, 440, 444, 446, 475, 486 | 192,384 | 24 BLOCKED; 46/521, 367/496, 399/472, 446/545 zero-sum; 69, 444 departure-forced |
| stage-1 group gates (W_A..W_D) | 5, 7, 34, 54, 73, 226, 228, 230, 231, 232, 236, 238, 363, 395 | 103,043 | 14 BLOCKED |
| n45 (PR2942, pivots 249/251/265/267 at V45) | 2, 70, 71, 72 (6 → V45 → 9, 6,877 each) | 27,508 | 4 BLOCKED |
| PR2908/PR2917 extraction outputs | 23, 35 | 9,992 | zero-sum with 39, 77 |
| n42 (PR2979 + R1_E42) | 61 (V45 → E42 → 9) | 4,996 | forced lift |

* **Normal 45.** The entry lower bounds of 2, 70, 71, 72 and of the pivots 249, 251, 265, 267 are eight pairwise-distinct
  6-dimensional subspaces inside V45 = ⟨256, 128, 64, 35, 16, 11, 5⟩ (they span it). For each visitor r and each of its
  restored receivers c, U_r ∩ E_c = L_r and no other register s has L_s ⊆ L_r ⊆ E_s: no partner, entry frame forced to
  L_r, first frame inside V45, hence the (1, 2) split 6 → V45 → 9 at 6,877.
* **The (2, 2) registers** 5, 34, 44, 54, 73, 105, 414, 430 would save 1,881 each with a (1, 3) split. Each has three
  6-dim candidate first frames: two admit no register at all, and at the third M[O][Z] has full column rank (|Z| = 6, 8
  or 10), so Lemma 6 excludes it.
* **Zero-sum** (23 and 39, 35 and 77, 46 and 521, 367 and 496, 399 and 472, 446 and 545): at every skip frame the receiver
  (511, 499, 589, 543, 567, 591) cannot sit there, no restored register can carry the content above it inside the
  receiver's end, and the only possible carrier is one non-restored register, so one of the pair visits.
* **Departure-forced** 69 and 444: every admissible entry frame either has no reader or fails Lemma 6 (|Z| = 2).
* **61's lift.** 230 (end E42 = ⟨256, 128, 64, 34, 16, 10, 4, 1⟩) needs the entry contents of the V45-ended pivots 249 and
  265 (M[230] has ±1/4 on 2, 34, 45, 54, 71, 92, 103, 228, 249, 265, 299, 331). No restored register can sit inside
  V45 ∩ E42 and climb out of V45 inside E42, so a register of {0, 2, 61, 62, 63, 70, 71, 72, 76, 94, 233, 235} must make a
  V45 → E42 → 9 visit (the blocked 2, 70, 71, 72 would need a third jump: 11,873 = 6,877 + 4,996). In PR #3042's words
  61 does it.

## Calibration on PR #2979's words

PR #2979 (same A/B, same caps, same LB_forced) costs 10,868,133,063 with 54 literal visits (367,899 units). Against the
same bound its unforced part is exactly 29,976 = 6 × 4,996: the BLOCKED 5, 54, 73 pay 14,975 instead of β = 9,979, 22 and
40 visit without any forcing, and the lift group pays twice (61 and 63). These are precisely dcharb78's six skips 63, 54,
40, 22, 73, 5 (PR #3042 keeps 61 as the lifter). The bound therefore predicted PR #3042's realized gain exactly, and
PR #3042 attains it; nothing further is available to restore-only rewrites.

## Erratum to PR #3042's README (documentation only)

Applying each declared block of PR #3042's `edits/EDITS.json` alone to PR #2979's words (exact splice, frames re-solved;
`certificates/ERRATUM-3042.json`, both providers):

| block | certified delta | profile delta | registers that skip | PR #3042 README says |
|---|---:|---|---|---|
| R1_E42 (`restore[162:188]`) | **−19,984** | −8 H1 + 4 H2 | 63, 54, 40, **22** | −14,888 for 63, 54, 40 |
| R2_E7 (`restore[190:203]`) | **−9,992** | −4 H1 + 2 H2 | 73, 5 | −14,938 for 22, 73, 5 |
| both | **−29,976** | −12 H1 + 6 H2 | all six | −29,826 |

Register 22 skips through R1_E42's gate `22 += −2·34`; R2_E7's gates touch only 5, 59, 73, 96, 363, 395. The declared
blocks replace 26 gates by 33 and 13 by 15 (the README lists 26 → 29 and 13 → 14; the restore grows from 203 to 212
gates). Applying both blocks reproduces PR #3042's final words exactly, so its profile, allocation and κ are unaffected.

## Verification

```sh
python3 -B research/rank7-skip-restore-optimum/run_registered.py      # ~70 s, Python standard library (3.12; 3.14 also runs)
python3 -B scripts/research_package.py --package research/rank7-skip-restore-optimum
```

`run_registered.py` checks the complete inventory (MANIFEST.json) and pins, reruns `verify.py` and `census.py` in a
temporary directory, requires their regenerated receipts to equal `certificates/` byte for byte, and binds lane K's stored
receipts (evidence/laneK/) to the recomputation. `verify.py` (13 s) recomputes per provider: the exact frame optimum
(10,868,103,087, the declared profile, 743 variables in 210 components, largest 94, as PR #3065 reports independently),
the free-algebra restore-entry rows (vendored PR2833 `walg_apply`), their rank, the forced coordinates and that the current
restore realizes them, the auditor on the word, the 88 caps, LB_forced, the classification and bound, the 51 literal
visits and their charges, the normal-45 facts; then the calibration, the erratum and the controls:

* auditor semantics: two appended FULL gates pass at delta 0, a gate into a restored helper fails;
* attainment: PR #3056's three-ADD and PR #3060's four-gate words for `restore[175:179]` are exact and tie the bound;
* twelve rejections: mislabeled provider, flipped byte, a dropped cap (LB_forced falls to 10,867,757,066), a dropped
  visit, a perturbed entry row, three cheaper restores that violate exactness (empty restore −499,481; deleting R44
  −6,877 leaves 498 in 475; deleting R82 −4,996 leaves 584 dirty; each rejected by Lemma 1 and by the auditor), a wrong
  claimed cost, an optimality claim for PR #2979, the departure lemma restricted to receivers containing the frame (admits
  the eight (1, 3) splits, bound 10,868,088,039), and caps read from the restore map of an emptied restore (0 caps).

`frames_exact.py` is a numpy-free port of the certified solver used for every price in this lineage (our r12 BORROW-WORD
harness on the #1186 frame toolkit, `research/exact-frame-toolkit/frames.py`): same model, same exact elimination, same
weights from the vendored `research/frame-domain-ceiling` engines; it reproduces all four certified optima and LB_forced.
`evidence/laneK/CROSSCHECK.json` runs lane K's current `bound.py`/`lbforced.py` (the version that takes the supplied M,
pinned in `evidence/laneK/`) on the four words with their own and with an emptied restore: bound, LB_forced and caps agree
in all eight cases. This package derives M from the restore-entry rows, never from the restore.

### Empirical controls (not part of the proof)

* **Deletion census** (recomputed completely): of the 212 single-gate restore deletions per provider, 10 keep the Lemma 1
  conditions; all cost delta 0.
* **Tail-exchange census** (lane K; candidate list re-derived here, 1 in 25 records re-checked): 8,098 exchanges per
  provider of a visiting register r with a non-restored s (exact swap at r's first restore touch or at R0, restore
  relabelled); 6,378 exact, 990 frame-feasible, minimum delta 0, none negative.
* Lane K's A/B censuses scored by this bound (local evidence on the base provider, not re-run and not part of the
  theorem; `evidence/laneK/FULLAB-SUMMARY.json`): 25,846 single-gate moves over all A/B gates, 6,387 read splits, 640
  write-sink variants, 99 merges and 350 commuting pairs, no positive gap. One move scored a gap of 9,992 only because it
  lands a target write in the restore, which the auditor forbids; it is excluded.

## Scope

Covered: every restore gate sequence at fixed A/B scalar programs, with all frames re-solved, at the certified solver's
weights. PR #3057 fixes every scalar operation and changes restore frames only; PR #3065 changes A/B/restore frames jointly
for the fixed scalar order (uniformly in b, with a relaxation at fixed interfaces). This package changes the restore's
scalar program arbitrarily but keeps A/B fixed. Not covered: A/B gate changes (lane K's scored A/B censuses are local
evidence only), helper ends, entrances, warps, buffers, the width inventory, packing or allocation, physical or native
costs, and other words. No κ is changed; PR #3042's and PR #3054's admissions are untouched.

## Open next questions

* **A/B-phase re-synthesis.** The restore's 499,481-unit overhead over the unconstrained empty-restore optimum is forced
  by A/B: 161,558 units of entry caps acting on A/B chains and 337,923 units of forced visits, of which 192,384 sit in the
  30 PR2857/PR2894 kernel/preload restore pairs. Only an A-phase (input block) or B-phase re-synthesis that changes the
  forced coordinates M or the entry bounds L/U can move them. First step: recompute M, the caps and this bound for a
  candidate A/B block before pricing it (`restore_bound.bound` takes any word).
* **Fixed target port hyperplanes.** Our r15 searches of A/B moves, start-frame raises and narrowing (lane reports, not
  packaged) all stopped at the same constraint: target writes in late B and the A-end target levels are pinned by the
  targets' 8-dim port-perpendicular end frames. A changed target port interface (PR2312 lineage) looks like the common
  wall for local levers on these words; it changes the source contract and needs a complete replacement bound.

## Credit

dcharb78 (PR #3042) for the six-skip words and the carrier/pivot skips; Jeremy Kothe (PR #3015) for R1 and the declared
restore-edit stage; Nick Petalas for PR #3054 (T740 with the six skips), PR #3057 and PR #3065 (frame optima), PR #3056
and PR #3060 (restore blocks used here as attainment controls) and T740; Marius-Paul Dumitrean for PR #2979 and its
lineage; icekylinx for PR #2833's auditor (vendored unchanged); Mason Hale (PR #2917) and Jeremy Diviney (PR #2908) for the
paired extractions. Details and retained files: [CREDITS.md](CREDITS.md), [NOTICE](NOTICE), [SOURCES.json](SOURCES.json).
Prepared by Marius-Paul Dumitrean with substantial AI assistance (Claude Code); author-checked, no independent review is
claimed. Apache-2.0.
