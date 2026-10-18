# PR2530 independent verification: words exact through cleanup and target endpoint; stock, endpoint enclosure and κ composition reproduce; no defect found

**Independent verification, no new κ.**
- **Catalogue card:** `independent-moment` (independent-verification track), refined to PR2530.
- **Frontier:** the selected frontier is unchanged (κ = 0.001672660197076918, #1094).
- **PR2530's status:** open and undispositioned on main; nothing here changes that.

[PR2530](https://github.com/CrocSwap/integer-mult-bounds/pull/2530) (zxv, head `b4012098`) claims a conditional
**κ ≈ 0.0017137379** for the T74 complex supplier. It adds eight dirty aliases to PR2462's words (430 → 422 helpers per
call) by restoring "jointly recoverable source partners" before handoffs. The aliases lift 12 more targets (16 in
total), whose residuals an A-phase prelude on line 30 corrects; all eight centre COPY paths become 7+1. It also
introduces a diagonal call order and a new 281,052-role owner fill.

`verify.py` re-checks PR2530's `research/source-partner-lifetimes` package with code independent of PR2530. It reads
the pinned files of PR2530, PR2462, PR2435, PR2269 and PR2474 as git data only and never imports or executes them.

## What this adds

Four concurrent audits cover parts of PR2530: PR2664, PR2661, PR2656 and PR2669. A fifth, rcfc-jreed's audit of
#2621, covers a descendant. Their heads were re-confirmed at 2026-10-15 20:57 UTC. None of the four checks the following for PR2530;
this package does:
1. **Both words end to end.** Both words are exact through the final cleanup and the target endpoint, in the forward
   and the dual orientation. A dual-only control shows that the dual replay adds coverage.
2. **Physical stock** 66,814, recounted from the words. This is a consistency check; see Conflicts.
3. **The endpoint and κ.** A directed-rounding enclosure of the endpoint `C`, and the grid conditions composing
   `κ = C − 10⁻⁷⁰ − 10⁻⁴⁶`.
4. **The verifier overrides**, diffed against PR2462's verifier.
5. **R-g owner charts:** 7,023 charts.

It also corroborates the other audits with another independent implementation:
- the lender handoffs and zero-climb gates (PR2664);
- the profile recount (PR2656);
- the windows (PR2661, PR2669);
- the fill rules R-a..R-e and the idle histogram (PR2661).

**Failure mode guarded against.** The lender values and the fill can pass (PR2664, PR2661) while one of these is wrong:
- the words' final cleanup or target endpoint;
- the physical stock;
- the composition from endpoint to κ.

This package closes that gap for the five checks listed under "What this adds". The native operator identity, the 63
outer inequalities, global admission, the word-to-receipt binding and the native precision inputs stay author-checked
(see Gaps).

## Findings for the PR2530 author (non-blocking)

- **The 24-digit outer endpoint** (set in `SPEC.json` and `build.py`) is stated only in the sibling
  `t74-owner-consolidation` README (line 21). It does not appear in the `source-partner-lifetimes` README, CLAIM.json or
  the PR body. PR2462's README states its 3000-digit setting. Choosing 24 digits forgoes about 7.0e-25 of κ
  (root − C).
- **The `prefix_l1` denominators** grow from 2 to 16, and `prefix_bits` does not charge them. This is inherited and
  well inside the 606-bit headroom. The `prefix_l1` values themselves come from PR2530's receipts.

## Existing independent checks (code read at these heads through the GitHub API about 19:40 UTC, heads re-confirmed 20:57 UTC on 2026-10-15; not replayed)

| Audit (head) | What it checks on PR2530's own objects | What it takes as given |
|---|---|---|
| [PR2664](https://github.com/CrocSwap/integer-mult-bounds/pull/2664) (commdata2338, `a0565b53`; [Discussion 2606](https://github.com/CrocSwap/integer-mult-bounds/discussions/2606)) | Forward lender values at handoff: each of the 8 new lenders holds its own input (646 inputs), with a backward substitution agreeing on all 16 observations. Zero frame climbs at all 9 recovery gates. Each gate replaced by the identity, plus 80/88-order, sign and early-handoff controls, judged at the handoff. B-map invariance under 28 relocations. | It does not check the dual words, cleanup, target endpoint, local rank ledger, owners, stock, admission or precision |
| [PR2661](https://github.com/CrocSwap/integer-mult-bounds/pull/2661) (commdata2338, `e12c36f7`) | All 1,332 windows with 666 bridges, matched against PR2530's PLAN. On PR2530's fill: strict windows, active-pair exclusion (R-e), family uniqueness, slices, prefix, all 149,184 bins, idle histogram and global profile. Widths from GF(2) spans. #2575's word JSON equals PR2530's. | The local paid profile is source-reported. No R-g charts, stock, endpoint or outer checks. |
| [PR2656](https://github.com/CrocSwap/integer-mult-bounds/pull/2656) (commdata2338, `fce1d93e`) | Word payloads byte-identical to PR2530's (via #2575), for both providers: local profile, inventory, mass 5251, centre cuts `{1:8,7:8}` and prelude `{1:16}`, recounted from the words' frame charges. Warp frame geometry, and cleanup frame availability. | "Complete dual word correctness is outside this package". No endpoint or cleanup values, and no stock. |
| [PR2669](https://github.com/CrocSwap/integer-mult-bounds/pull/2669) (commdata2338, `086d0173`) | Rebuilds 1,332 windows for each uniform shift of the order (`s = 0` is PR2530; `s = 4` is #2571's head), with the 444 rank-eight windows cross-checked | Provider profiles are declared inputs; no words or fill |
| rcfc-jreed's [comment on #2621](https://github.com/CrocSwap/integer-mult-bounds/pull/2621#issuecomment-6197718277) | #2621's own fill, order and root, on #2588's words | Nothing on PR2530's own words, order or fill |

## Result

Nothing failed and no counterexample was found. Every PR2530 number re-derived here reproduces.

Labels: **IR** is revision 5's "independently reproduced". This package adds two qualifiers:
- **corr.** means the item is also covered by the audits above.
- **CC** means the arithmetic is independently reproduced, but the rule is not independent of this author (see
  Conflicts).

| Claim of PR2530 | Check here | Result | Label |
|---|---|---|---|
| Both changed words (base and extra providers) are exact | Free-operator replay with all 646 live registers as independent dirty symbols and 78 zero buffers, forward (`Y_t += X_t`) and dual (`X −= Y`). Every warp record and A-phase warp item is checked: invertible, symplectic, Fourier rank 0. | PASS for both words, through the cleanup (4,529 items) and the target endpoint | IR (warp frame geometry corr. PR2656) |
| PR2530's shipped cleanup is its words' inverse-reverse | Literal comparison with our own re-derivation | Equal, item for item | IR |
| The 8 new lenders hold `X_r` at handoff; the 9 inserted gates (`49 −= 33`, `68 *= ½; 68 −= 4`, `31 += 12/2`, `88 += 80/2; 80 −= 88`, …) add no climbs | Exact forward rows before and after each gate; climbs at each gate; each gate mutated and rejected at the handoff, the target check and the dual final map | As claimed. The older lenders 4 and 12 hold the mixtures `(X4 − X68)/2` and `X12 + X31`, as PR2664 also notes. | IR (corr. PR2664) |
| Local profile `{1:2369,2:632,3:320,4:118,5:26,7:8}`, widths `{4:33,5:9,7:62,8:78,9:240}` | Literal frame-chain recount, bound to the words' reports | Equal in both words. All 8 centres are `[7,1]`, with 16 lifted targets. Mass 5251 = 3395 + 1792 + 64. | IR (corr. PR2656; widths also PR2661) |
| The structural change from PR2462 | Aligned diff | 32 echo reads deleted, 9 gates inserted, 8 warps added, prelude 28 → 88 items | IR |
| Diagonal order `(4·stage + replica, stage, replica)`, legal under the inherited interleaving rule | Formula; per-replica projection; the 30 per-replica template events | Exact match. No per-replica event carries a cross-replica field, and the two global tail events come last. | IR |
| Windows | Own block-level derivation with bridges, cross-checked against the PR2387 event rule | 1,332 windows, none empty; equal to PR2530's PLAN; the schedule hash matches | IR (corr. PR2661, PR2669) |
| Owner fill, 281,052 roles | R-a..R-e in two implementations: a new checker, and PR2387's `fill_check80.check_roles`. `fill_check80` receives the width and family fields derived here, so its R-a.width and R-e.family_identity agree by construction. On these windows the R-e active-pair rule follows from R-d, which is asserted. R-g charts via `fill_check80` only. R-f (physical) is replaced by the stock check. | PASS. Idle `{1:21976,3:6662,5:440,8:114,16:172,32:3,48:26488}`; global profile = PROFILE.json with the recounted local profile; 7,023 charts; in each call 224 active-pair and 422 host families are busy and disjoint | IR (corr. PR2661 for R-a..R-e and idle) |
| Fill order dependence (a characterisation, not a claim of PR2530) | Re-timing and an adjacent-swap scan | Under PR2462's order 60,541 roles leave their windows. Of the 665 adjacent swaps of calls from different replicas, 238 keep every role in its window and 427 do not; the first breaking swap is at position 5 (78 roles). No later claim reuses this fill. | IR |
| Physical stock 66,814 | `W + 8 + R + NZ + 2`, with R and NZ recounted from the words; namespace touched by the words | 66304 + 8 + 422 + 78 + 2. The same rule reproduces PR2435 (66826) and PR2462 (66822). | CC |
| Endpoint `C = 0.001713737921547504346752` | Rigorous fixed-point enclosure at `2⁻⁶⁴⁰` (directed-rounding exp and log) | Accepts at C (upper end < 1) and rejects at C + 1e-24 (lower end > 1); root − C ≈ 7.0e-25 | IR |
| κ = C − 10⁻⁷⁰ − 10⁻⁴⁶ | Exact grid-maximum conditions using the ledger's ε and q | They hold. This is the DIG = 24 instance of PR2462's parametric rule. The 63 outer inequalities themselves are author-checked (Gaps). | IR (composition only) |
| Verifier overrides | Diff of the old and new `independent_core.py` and `rebind.py`; scan for the old pins | Only the two target and centre-count pins change, plus the zero-buffer term in physical stock. No check is weakened. | IR |

## What later claims can take from this (local-only comparison of files at each head)

All heads were re-confirmed at 2026-10-15 20:48–20:56 UTC. Changed and new heads were read then, and unchanged
heads' files about 19:40 UTC.

| Later PR (author, head) | Words | Order | Fill | Endpoint |
|---|---|---|---|---|
| #2571 (rohanarun, `faff03cf`) | **PR2530's** (regenerated by PR2530's unchanged `build.py`) | uniform shift s = 4 (509 of 666 positions differ; the PR body still describes an earlier commit) | new | own, 24 digits |
| #2575 (jeremykothe2, `921c229b`) | **PR2530's** (payloads byte-identical) | **identical** | new | own, 3000 digits |
| #2588 (jeremykothe2, `8cd9dc88`) | changed (helpers 596/600 replace 648/649 for lenders 80/88) | **identical** | new | own |
| #2679 (philippeVV, `2e2cf565`) | changed (pre-life hosting, refit alias; 415 helpers) | **identical** | new | own |
| #2621 (themilkman216, `07c0e300`) | #2588's | new (430 differ) | new | own |
| #2673 (jeremykothe2, `45aadf0f`) | #2588's | new (613 differ) | new | own |
| #2696 (mason-hale, `5a42add7`), #2733 (mdumitrean, `a63c55ff`), #2745 (jeremykothe2, `4f485de0`), #2751 (tekuuu, `4cfbb0cc`), #2766 (DavidAriasC, `e6df920c`), #2767 (jeremykothe2, `e8b771ba`) | changed further (new assignments, compositions, refits) | #2673's | new, or another later PR's | own |

#2802 (mdumitrean), opened at 22:23 UTC on #2751's words, appeared after this comparison. Its files were not
compared. All heads above were unchanged at 22:26 UTC.

**Where PR2530's checks apply:**
- **Word checks:** #2571 and #2575.
- **Order and window checks:** #2575, #2588 and #2679.

No later claim reuses PR2530's fill. The comparisons use decompressed payload SHA-256s for words and fills, and a
position-by-position comparison of the order files. Changing the assignments can change the set of lenders whose
`K_op` is applied twice (see Gaps), and that was not compared.

## Gaps (none is a counterexample)

**Author-checked only (not re-derived here):**
- **Native operator identity.** The free-operator replay treats each warp as one abstract invertible letter. It
  therefore assumes that the native `K_op` is the same physical operator in the A prelude and at the B handoff,
  including Clifford phases and monomial lift. This applies to the 12 lenders whose `K_op` is applied in both:
  - 49, 83, 98, 101, 68, 80, 88 and 31 (new in PR2530);
  - 33, 55, 74 and 85 (from PR2436).

  PR2530's native receipts claim 512-column checks.
- **Strict global admission** (emitter, pooled-slot binding, finite invoice, native lowering) under the diagonal
  order with PR2530's fill.
- **The 63 strict outer inequalities.**
- **Word-to-receipt binding.** The receipts' `canonical_word_sha256` is the raw sha256 of a `CANONICAL-WORD.json.gz` that PR2530's native cold replay produces (`independent_core.py` binds it as a file hash).
  No file or archive member in PR2530's trees hashes to it, so the audited `evidence/eight-alias-*.json.gz` words are
  not bound here to the native receipts.
- **Native precision inputs.** The `prefix_l1` values come from PR2530's receipts. This package recomputes only the bit
  arithmetic: prefix bits 1442 ≤ 2048 and the row coefficient 19545 < 20161.

**Inherited premise:** free interleaving of independent replica controllers (the PR858/PR1297 lineage). PR2530 leans
on it heavily: 664 of 666 positions move.

**Local-only, outside the registered run:**
- the unmodified PR2462 outer scripts, run on PR2530's SPEC, regenerated PR2530's `OUTER-LEDGER.json` and
  `OUTER-INDEPENDENT.json` byte for byte (this executed inherited code);
- the downstream comparisons;
- the mutation testing of this checker.

## Controls

Every control names the rule that must reject it, and the run asserts that this rule fires. The PASS line counts
148 attempted and 148 rejected controls, from separate counters. A word mutation counts once per word. Distinct
mutant-and-check pairs number 99, from 74 distinct mutants.

| Group | Rejections (distinct) | What must reject it |
|---|---|---|
| Word mutations, full check | 18 (9) | `replay`, `warp` or `frame`. Examples: a dropped restoration, a flipped prelude coefficient, a wrong prelude operator, a missing inverse warp, an extra target read. |
| Dual-only mutant | 2 (1) | The dual replay's buffer check after cleanup. The mutant prepends `399 += zero buffer 977` to the cleanup; the forward replay is asserted to **accept** it. |
| Gate mutations (with 1 prelude mutant in the handoff group and 3 word endpoint mutants in the dual group) | 18 (9) full check; 20 (10) handoff rows; 24 (12) dual | the forward target check before cleanup; `restoration.handoff`; and the dual final map after a re-derived cleanup, through the main check's code path |
| Free-operator replay only | 6 (3) | `replay`, with the pre-checks bypassed |
| Recount against report | 4 (2) | `claims.profile_widths`: a gate gets an intermediate frame, so both of its registers' rank-2 climbs become 1+1, with charges, widths and mass unchanged. `claims.report_fields`: the report's profile is altered. |
| Cleanup, echo order, aliases partner | 6 (3) | `cleanup.literal`, `diff.echo_order`, `aliases.partner` |
| Order, windows, template, PLAN | 9 (9) | `order.diagonal`; `R-d.window` for PR2462's order (60,541 roles out) and for the swap at position 5; `order.projection`; `windows.block_vs_event`; `template.cross_replica_field`; `windows.active_pair_lemma`; `windows.plan` (a dropped call time, and a spurious extra window) |
| Fill and stock | 16 (16) | each rule in turn: R-a, R-b, R-c, R-d (both window ends), R-e (family, and the active pair alone), R-g (pending axes, charts), `physical.busy_families`, `physical.namespace_receipt` (a shifted interval, and the receipt's stock + 1). `fill_check80` must reject the fill controls with the same rule. |
| Endpoint and κ | 8 (8) | the endpoint and conservative endpoint at +1e-24; enclosure predicates at PR2462's endpoint (it straddles 1, so accepting on the wrong end is caught); `outer.grid` for κ + 1e-70 and for each end of the interval condition |
| Overrides and provenance | 17 (17) | an extra edited line in `independent_core.py` or `rebind.py`; an extra file carrying an old pin; an old-pin scan narrowed to one file; a reconstruction that keeps PR2435's base word instead of the overlay word; a wrong target pin; an extra or a missing member in the PR2435 archive and the PR2462 overlay; the PR2474 gain + 1e-40; a doubled `prefix_l1`; a stock rule without the zero-buffer term; a tampered vendored checker (`VendorPinMismatch`) |

**Plumbing controls (outside the counts).** A paid climb is injected into the recount data at each inserted gate. The
zero-climb check must reject every injection, which shows that it is not vacuous.

**Positive controls (3, counted as they run):**
- the same word checker reproduces PR2462's own profile, widths and 654 inputs on PR2462's base word;
- it does the same on PR2462's extra word;
- the enclosure at PR2462's 3000-digit endpoint gives `lo ≤ 1` and `hi ≥ 1 − 10⁻²⁹⁹⁰`.

**Mutation testing of the checker (local-only).** 62 mutations of this package's own code were each run on a copy
with `--out`, and every one makes the run FAIL. A stale `.pyc` planted for a vendored checker is never executed,
because the verified bytes themselves are compiled and run. They include:
- self-comparisons of every equality check;
- dropping the dual replay from both the main check and the controls;
- replacing the profile recount with the report;
- dropping the κ grid conditions or the R-g check;
- accepting the endpoint on the wrong side;
- weakening the window bounds, R-e, or the override, archive, receipt and vendored-pin checks.

## Reproduce

From the repository root, standard library only, about 2 min and about 1.1 GB of memory:

```sh
python3 -I -B research/t74-2530-source-partner-audit/verify.py --fetch
```

**What `--fetch` does.** It fetches any absent pinned commit into `refs/audit/prN` and writes nothing else: no
`FETCH_HEAD`, no automatic gc.
- **Requirements:** git ≥ 2.29 and network access.
- **Retention:** the five pinned commits are unmerged PR heads, so the replay stays reproducible only while GitHub
  retains them. A maintainer integrating this audit may want to archive the five pinned commits' objects, for example
  as a bundle of `refs/audit/pr*`. The 36 pinned blobs alone are not enough, because the run also walks the two pinned
  package trees and scans the 131 PR2462 `.py` files.
- **Isolation:** every git call drops `GIT_DIR` and the other variables that redirect or reconfigure the repository.

Any failure ends with a single `FAIL_T74_2530_INDEPENDENT_AUDIT` line. Expected final line:

```
PASS_T74_2530_INDEPENDENT_AUDIT words=2x646-inputs-fwd+dual profile={"1":2369,"2":632,"3":320,"4":118,"5":26,"7":8} roles=281052 idle={"1":21976,"3":6662,"5":440,"8":114,"16":172,"32":3,"48":26488} physical=66814 charts=7023 C=0.001713737921547504346752 kappa=C-1e-70-1e-46 negative_controls=148/148-rejected distinct_controls=99 positive_controls=3 pinned_inputs=38
```

**How the run is protected:**
- Every input is a pinned git object (blob and sha256) and is parsed as data only.
- The computed receipt must equal the committed `RESULT.json`; `--out` regenerates it.

**Modules:**
- `check_words.py`: words, gates, recount and cleanup.
- `check_fill.py`: order, windows, fill and stock.
- `check_accounting.py`: overrides, the recovered source, precision, endpoint and κ.

The registered command has only been run on CPython 3.14.4; the Python 3.12 replay was not run locally.

## Open next questions

These close obligations of PR2530's own claim. No further fill, order or word optimisation is proposed (family
expansion decision: none).

1. **Native `K_op` identity for the 12 lenders above.**
   - *Why:* #2571 and #2575 use exactly these words. The later claims reuse the same prelude and handoff warp
     mechanism with changed assignments; their `K_op` sets were not compared here.
   - *First step:* an independent re-implementation of the 512-column monomial check from the receipts' operator
     encoding.
   - *Blocker:* none.
2. **The 63 outer inequalities at PR2530's 24-digit setting**, re-derived with an own implementation of the inherited
   ledger formulas.
   - *Why:* PR2530's κ composition rests on them; later claims mostly use their own outer settings.
   - *Blocker:* the formulas must be restated from the PR2462 lineage.
3. **Second-platform global admission** under the diagonal order with PR2530's own fill.
   - *Why:* this matters only if PR2530 itself is considered for admission.
   - *Blocker:* it needs PR2530's `full_replay.py` with numpy, scipy and sympy, which this read-only package does not
     run.

## Independence, conflicts and credits

**Independence.** The checking code is independent of PR2530's code. It vendors two checkers by this author, pinned by
git blob and sha256 (`vendor/NOTICE.md`): `words_check.py` from PR2315 and `fill_check80.py` from PR2387. PR2315 is now
on main (`research/t74-borrow43-independent-check`); its copy differs from the vendored one only in a corrected
docstring credit.

**Conflicts.**
- **PR2530 credits this author.**
  - Its body credits "Sagar Thakrar/#2315 and #2442" and cites #2442 and #2466 as audits of its sibling package.
  - The sibling README credits PR2315 for buffer accounting, alongside Dugongue's PR2309, and PR2442 for an
    optimality audit.
- **PR2462 credits this author too**: PR2442/PR2446, PR2286 and PR1964. PR2462 is the diff baseline here and the
  source of the κ grid rule.
- **Effect on this package.**
  - The stock rule is Dugongue's PR2309 private-stock accounting, to which PR2315 contributed the cleanup-buffer
    finding, so the stock check is labelled CC.
  - None of PR2442, PR2446, PR2466, PR2286 or PR1964 is used as a check here.
  - The sibling package is used only as the source of the PR2435 archive, after a tree-equality check against PR2435's
    head.

**Credits:**
- **PR2530:** zxv.
- **The T74 line:**
  - jeremykothe2 (PR2435, PR2462, and the pinned inputs PR2269 and PR2474);
  - Tekalign / tekuuu (PR2436);
  - Vlado Vojdanovski / Vlado-V (PR2322);
  - Cinna Davis (PR2226, dirty borrowing and the alias rule, now on main as `research/anticipatory-dirty-borrowing`);
  - Dugongue (PR2309).
- **Hosting and interleaving:** Hao Yan (PR858) and Rohan Arun (the PR1297 lineage).
- **Concurrent independent audits:** commdata2338 (PR2664 and Discussion 2606, PR2661, PR2656, PR2669) and rcfc-jreed
  (#2621). Agreement with them is agreement of published values; their code was read, not replayed.

Prepared by Sagar Thakrar with substantial AI assistance (Claude Code, Anthropic, Claude Opus 5.5):
- AI auditors wrote the checks.
- An AI builder consolidated them.
- Three rounds of AI review found the positioning, overlap and control issues fixed here.

No independent human review is claimed. Apache-2.0.
