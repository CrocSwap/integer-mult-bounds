# Audit: PR442 hosting windows and the partial width-seven rows of #1023 and #1281

**Adversarial audit: no new κ, and no existing check is changed.**

- Track: 60–74 (adversarial audit), assignment seed 72, drawn with the OS CSPRNG via Python `secrets`.
- Card: `uniform-transfer-audit` (a hosting implication). The scope is **refined** in [TASK.json](TASK.json).
- Base: `0b1cccf8`. The selected record frontier1094 (complex-bound) is unchanged. `verify.py` binds its certificate to the PR589 record and the engines used here.

## The audited claims

- **#1023 (ours, merged, `research/bit589-width-packing`).** It publishes partial width-seven rows: k helpers per call are converted to width 7.
  - Example: k = 37 optimistic gives 0.0017896275 (+3.24%).
  - The rows are described as achievable placements in #1023's slot model. They are reached by putting all 9k width-7 residuals in empty capacity-7 slots.
  - Its README lists window timing as an unchecked obligation.
- **#1281 (mightyOil, merged, `research/bit-partial-width7-optimum`).** It proves the exact optimum for every k = 0..74 in its mixed-width slot relaxation, both replica-local and pooled32.
  - It openly disclaims temporal constraints.
  - Its **open question 1** asks whether the relaxed optimum can be hosted chronologically for an actual width-seven helper. It proposes starting from PR1179's changed entry/exit contract, and testing both per-replica restrictions and possible cross-replica pooling.

This package settles one part of that question: **per-replica hosting on the frozen PR589 stage recipe**. That means the hosted audit's `hosted[(stage, helper)]` map with per-replica windows `s in W[i]`, whole residuals and no banks. PR1179's contract and cross-replica pooling stay open.

## The windows

[windows.py](windows.py) writes out the nine-stage idle schedule (K = 4, L = 9) and checks it two ways.

1. **It matches `global_k.py`.** At run time the schedule is compared, event by event and field by field, with a reference schedule built from the pinned `global_k.py`.
   - `global_k.py`'s own `recipe()` and its idle-insertion `if` block are extracted with `ast` and executed, with their asserts.
   - They run inside a transcription of the surrounding loop of `global_k.main()`: the level bookkeeping, the event appends, and the stage-order, bridge-level and exchange checks.
2. **Three window predicates agree.** This code, PR442's `hosting_core.windows`, and `audit_hosted_k.windows` (which enforces `s in W[i]` for every hosted slot) give identical windows on that one shared schedule.

All 14 frozen `selection9-p111` entries lie inside their windows.

The selection hosts nothing in children 1, 3 and 5. So the decisive singleton windows rest on the `global_k.py` match.
- A test drops one bridge from the schedule. The three predicates still agree with each other on that schedule, while child 1's window widens to stages 0–2; the anchor rejects it.
- Further tests mutate single fields (an idle rank or pair, a sweep's stage or pair, a bridge end), and the anchor rejects each one.

| Idle child | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|---|
| Capacity | 14 | **7** | 28 | **7** | 42 | **7** | 42 | 28 | 14 |
| Admissible stages | 0–1 | **2** | 0–3 | **4** | 0–5 | **6** | 3–8 | 5–8 | 7–8 |

**Each capacity-7 child admits exactly one stage.** Per replica, at most 3k of the 9k width-7 residuals can sit in 7-slots. The window-free rows of #1023 and #1281 use all 9k.

## Results ([RESULT.json](RESULT.json))

For every k = 0..74, `verify.py` computes the **exact window-respecting optimum** and does three things:

- **Builds and checks an explicit residual-level placement at run time** (`verify.build`). Every slot is checked for its window, its width and its offset; cells must be disjoint; and every (stage, helper) must be hosted exactly once. RESULT.json records the placement's per-replica idle histogram and its width-7 distribution. `build(k, plan, slots)` returns the checked slot list (child, copy, offset, width, stage, helper); a test rebuilds the k = 1 placement this way.
- **Prices the placement's bit endpoint** under both of #1023's local brackets, using the pinned engines and the inherited surcharge.
- **Certifies that no window-feasible replica-local placement reaches the next 1e-24 grid point.** The certificate is tight: it equals the engine moment of the explicit histogram to within 1e-50.

k = 0 reproduces the selected bit endpoint 0.001733427039589844234749.

Selected rows, with the gain over the selected bit endpoint:

| k | Bracket | Window-respecting optimum | Window-free optimum (#1281 profile) | Retained |
|---|---|---|---|---|
| 1 | optimistic | 0.001734347102 (+0.053%) | 0.001734846264 (+0.082%) | 0.648 |
| 1 | pessimistic | 0.001734104523 (+0.039%) | 0.001734603545 (+0.068%) | 0.576 |
| 2 | optimistic | 0.001735271920 (+0.106%) | 0.001736327170 (+0.167%) | 0.636 |
| 2 | pessimistic | 0.001734786312 (+0.078%) | 0.001735840971 (+0.139%) | 0.563 |
| 10 | optimistic | 0.001743225534 (+0.565%) | 0.001748291126 (+0.857%) | 0.659 |
| 10 | pessimistic | 0.001740777922 (+0.424%) | 0.001745829269 (+0.715%) | 0.593 |
| 37 | optimistic | 0.001770809187 (+2.157%) | 0.001789671631 (+3.245%) | 0.665 |
| 37 | pessimistic | 0.001761884716 (+1.642%) | 0.001780556367 (+2.719%) | 0.604 |
| 74 | optimistic | 0.001809907119 (+4.412%) | 0.001849754238 (+6.711%) | 0.657 |
| 74 | pessimistic | 0.001792188010 (+3.390%) | 0.001831249661 (+5.643%) | 0.601 |

Notes on the table:
- Endpoints are truncated; percentages and retained fractions are rounded.
- The certified bound for each row is the next 1e-24 grid point above the window-respecting endpoint.
- The window-free column is this package's pricing of #1281's closed-form idle profile. #1281 itself prices k = 0, 1, 2, 37 and 74.

### How the published rows fare

- **#1023:** all 8 published partial rows (k = 1, 10, 37 and 74; both brackets) lie above their certified bounds. None is reachable under the windows.
- **#1281, replica-local:**
  - #1281's closed-form local optimum is transcribed here (`windowfree_idle`) and checked against its merged `EXPECTED.json`. That file is digest-pinned and read as data; no #1281 code is run.
  - All 75 idle profiles agree. All 9 of #1281's priced cases are reproduced exactly, in local endpoint and local histogram.
  - Its optimality is #1281's result; this package does not re-derive it.
  - Priced here under both brackets, all 148 local rows (k = 1..74) lie above the per-replica bound. 8 of them are also priced by #1281.
- **#1281, pooled32:** its 8 priced rows with k > 0 also lie above the per-replica bound. Pooling moves residuals between replicas, so these rows are ruled out only for replica-local placements. See the cross-replica caveat below.
- **#1023's all-width-7 optimum `{42:340, 21:1}` stays window-feasible.** Max-flow finds 104 feasible sextet splits, so its +17–23% figure is not affected by the windows.

### How much of the gain survives

Across k = 1..74, the window-respecting optimum keeps 63.6–67.1% of the window-free gain (optimistic bracket), or 56.3–60.7% (pessimistic). Put the other way, the window-free rows overstate the gain by about 1.5× (1.49–1.57×) or about 1.7× (1.65–1.78×). The ratio is roughly flat in k.

These figures hold under #1023's one-unit local pricing, the frozen recipe and replica-local hosting. None of this changes κ: the selected record is complex-bound, and these are bit headroom figures.

## Why it is exact (proof sketch; the code asserts each checked fact)

1. **Lemma A (exchange): some optimum puts every stage-2, 4 and 6 width-7 residual alone in a copy of child 1, 3 or 5.**
   - Cost per copy is F(r) = 64^a r^(1−a) + λ for r > 0, with F(0) = 0. Here λ ≥ 0 is the per-child surcharge term.
   - F is subadditive on r ≥ 0: r^(1−a) is concave with value 0 at 0, and λ is counted once.
   - A capacity-7 copy cannot hold a width-8 residual and holds at most one width-7 residual. Child 1 has 222 > k copies.
   - Moving a stage-2 width-7 residual from a copy with r unused units into an empty copy of child 1 changes the cost by F(r + 7) − F(r) + F(0) − F(7) ≤ 0.
2. **Width-8 placement is unconstrained (checked for every k ≤ 74).**
   - The windows are stage intervals, so Hall's condition for the stage → child transport reduces to intervals.
   - For every proper interval J, the full width-8 capacity of the children whose windows lie in J is at most the width-8 supply of J.
3. **The width-7 residuals reduce to two nested chains.** After Lemma A, 6k width-7 residuals remain, from stages 0, 1, 3, 5, 7 and 8, over children 0, 2, 4, 6, 7 and 8. A distribution B is feasible exactly when all of the following hold:
   - B0 ≤ 2k, B0 + B2 ≤ 3k, B0 + B2 + B4 ≤ 4k;
   - B8 ≤ 2k, B8 + B7 ≤ 3k, B8 + B7 + B6 ≤ 4k;
   - ΣB = 6k.

   This is derived from all 45 interval Hall constraints, asserted for every k. It is also confirmed by brute force: max-flow is checked against the chain predicate on every distribution of the 6k residuals, all 462 at k = 1 and all 6188 at k = 2, and they agree on every one.
4. **Exact lower bound.**
   - Cost splits three ways:
     - copies holding width-7 residuals (a per-child knapsack over copy types);
     - copies holding only width-8 slack (#1281's periodic V(S), recomputed and checked at each a);
     - the 7-slots.
   - An integer DP runs over (chain sums, slack mod 5). It uses outward-rounded lower bounds of F at 2^−200 from the pinned engine.
   - The DP drops the copy limits and S ≥ 0, so it is a relaxation and gives a rigorous lower bound.
5. **Attainment and certificate.**
   - The DP minimiser is expanded into the explicit placement above, whose cost equals the DP value exactly.
   - At a′ = c* + 1e−24, the local moment lower bound plus 32 times the DP bound exceeds 1.
   - So every replica-local placement, uniform across replicas or not, has an endpoint below a′. This is grid optimality at each row's own endpoint.

## Controls ([test_package.py](test_package.py), 14 tests)

- **C-W0 (schedule anchor).** The schedule equals the `global_k.py` reference. Dropping one bridge is rejected, as is each of six single-field mutations.
- **C-W1.** #1023's k = 1 placement fills 9 capacity-7 copies per replica, one per stage. The windows admit only stages 2, 4 and 6 there, so at least 6 residuals sit outside their window.
- **C-W2.** The window-free local rows lie above the certified bound, while the window-respecting endpoints lie below it.
- **C-W3.** #1281's local and pooled32 priced rows (k > 0) lie above the per-replica bound, and all 75 idle profiles match. At k = 1 the test recomputes the certificate at the recorded bound and reads #1281's values from its own file.
- **C-W4.** The all-width-7 optimum is window-feasible.
- **C-W5 (dropped constraint).** Dropping the chain constraint B0 ≤ 2k breaks the brute-force agreement.
- **C-W5 (perturbed window).** Widening child 0's window to stages 0–3 breaks the chain structure.

Also covered:
- #1023's eight rows are all unreachable.
- k = 0 reproduces the selected endpoint, and its certificate is recomputed and checked for tightness.
- The exhaustive brute-force reduction holds at k = 2.
- The width-8 Hall conditions are vacuous.
- The record binding holds, and the explicit k = 1 placement hosts every (stage, helper) inside its window.

## Reproduce

```sh
python3 -I -B research/bit589-width7-windows-seed72/verify.py        # about 140 s of CPU; PASS_BIT589_WIDTH7_WINDOWS
python3 -I -B -m unittest discover -s research/bit589-width7-windows-seed72 -p test_package.py
python3 scripts/research_package.py --package research/bit589-width7-windows-seed72 --check-only
python3.12 scripts/research_package.py --package research/bit589-width7-windows-seed72
```

- **Requirements.** Standard-library Python 3.10 or later. The pinned engines, record and slot model come from merged #1023's `packing.py`, which is imported read-only. `verify.py --kmax K` runs a partial check (`PASS_PARTIAL`).
- **Where it was run.** `verify.py` and the tests pass on Python 3.12.15 and 3.14.8 (macOS 26.5, arm64). `--check-only` passes.
- **Registered replay.** The python3.12 replay passes (`PASS_REGISTERED_RESEARCH_PACKAGE`, 80 s of wall time on an unloaded host). An earlier attempt timed out at 600 s only because the host was heavily loaded (load average about 100). `verify.py` itself needs about 140 s of CPU.

## Scope and remaining obligations

- **Hosting format.**
  - This applies to the PR442/PR589 nine-stage template with replica-local hosting, whole residuals, no banks and the frozen stage recipe. (#743 proves the 2P + 1 stage lower bound that this format attains.)
  - A changed recipe, split residuals or banks lie outside it.
  - Open #1487 (ianlibanio) varies the nine-stage recipe for width-8 hosting. Its recipes may have other capacity-7 windows, which this package does not check.
- **Cross-replica owner maps are open.** The selected complex T16 supplier uses cross-replica interleaved owner maps (`owner_replica ≠ replica`). Such a map could admit other replicas' calls at other stages into the 7-slot windows. That case is **not** ruled out here.
- **Windows are necessary, not sufficient.**
  - Projector compatibility is still open. #1307's caveat applies: slots that split q⊥ lie outside its completion-free argument, and that covers width-7 residuals in 14-, 28- and 42-slots.
  - Owner inactivity is still open.
  - A physical width-7 helper is still open: #1128, #1179, #1256, #1271, and #1393 (discussion #1362).

  So the window optimum is itself only an upper bound for real hosting, while the unreachability direction holds.
- **Pricing assumption.** The prices keep #1023's assumption that each converted helper removes one unit from one local child.
- **Uniqueness.** Histograms are not shown to be unique; ties exist, for example at k = 2.
- **Inherited assumptions.** All of them remain:
  - all-size compilation;
  - common-label/mutable-source realization;
  - whole-call hosting;
  - precision/tape;
  - analytic transfer;
  - bit H1–H5;
  - the bit bad-residue surcharge, which every price above keeps.

  This is not a construction and not a formal proof of the multiplication theorem.

## Relation to earlier work

- **#1023.** Its partial rows are window-free relaxation values; this package gives the window-respecting values. #1023's frozen files are left untouched.
- **#1281.** Its optima are correct for the relaxation it states.
  - This package settles the per-replica, frozen-recipe part of the window question in its open question 1. Under the frozen PR589 stage recipe, whole residuals and no banks (`s in W[i]`), the relaxed optimum cannot be hosted chronologically by any replica-local placement. The exact window-respecting optimum is given instead.
  - The rest of that question stays open: the PR1179 boundary-contract audit (#1179, adamgall), the cross-replica pooling test, and the physical helper, source-access and restoration parts.
  - Whether PR1179's changed entrance leaves these stage windows unchanged is not checked here.
- **#1256.** Its two-slot relaxation moves a width-seven residual into a formerly idle rank-seven slot and leaves the owner/window assignment open. Under this recipe, that move is window-feasible only for a residual hosted at stage 2, 4 or 6 (children 1, 3 and 5). Residuals from the other six stages need a larger host.

## Open next questions

1. **Can cross-replica (T16-style) interleaved owner maps lift the one-stage 7-slot windows for the bit supplier?** This is one route to #1281's pooled rows; a changed recipe, split residuals or banks are others.
   - First step: compute windows on an interleaved bit timeline and rerun the DP.
   - Blocked by: a cross-replica DP. `wopt.solve` and the `global_k.py` anchor are specific to this per-replica schedule.
2. **Does another nine-stage recipe widen the capacity-7 windows?** #1487 enumerates recipes for width-8 hosting only.
   - First step: generalise `wopt`'s two-chain DP to arbitrary interval windows (or use a min-cost-flow bound), then apply it to #1487's hostable recipes.
   - Blocked by: the generalised DP. `wopt.solve` currently asserts this recipe's chain structure.
3. **Do the window-respecting placements pass projector compatibility (#1307) for mixed-width slots?**
   - First step: regenerate the k = 1 placement with `verify.build` and run #1307's projector check on it.

## Credit

- #1023: Sagar Thakrar.
- #1281: mightyOil (Philipp), with OpenAI Codex GPT-6 Astra assistance.
- PR442: DaysSky, the hosting windows.
- PR444: chafreaky, the ownership/window audit that `audit_hosted_k` extends.
- PR443: chafreaky, the `global_kernel.py` recipe that `global_k.py` generalises.
- PR439: chafreaky, the explicit residual bank routes.
- PR386 and PR436: Zhihao Chen and eumemic, the global identity and template.
- PR463, PR510 and PR589: DreamingOfClouds, the hosted audit and the bit supplier.
- PR555: eumemic.
- Also cited:
  - #743: 0xjohnnydev;
  - #1179: adamgall;
  - #1256: RossRichardson;
  - #1393: 1337isnot1337;
  - #1487: ianlibanio;
  - #1128: aliromman;
  - #1307: commdata2338.
- The retained moment-engine authors.

Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from Claude (Anthropic) via Claude Code. Parallel read-only scout and judge subagents found the window obstruction. A post-PR adversarial review found overclaims and the missing schedule anchor, which the second commit fixes. A recheck found smaller gaps, which the third commit closes. New material is Apache-2.0.
