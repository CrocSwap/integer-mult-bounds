# Kernel cap: the width rule, the pivot ceiling, and a 112-pivot kernel for the R715 bit word

**Method + knowledge package. Bit supplier (exact, eleven stages, PR #442 whole-residual hosting, no cross-family split, target mixing, same word
as PR #463): c = 1295910576589222380953/10²⁴ ≈ 1.295911·10⁻³, +0.839% over R715's 1.285129·10⁻³.**
With PR #458's complex supplier, unchanged: **κ = 1294233365881801/1000000000000000000 ≈ 1.294233365881801·10⁻³, bit-bound, +0.838% over PR #463**.
Nothing in the word, the hosting rule, the mixing or the complex supplier changes. Only the *kernel selection* does: 112 rank-1 pivots
(PR #463: 84 pivots with entrance ranks 1, 2, 4) chosen by seeded annealing instead of PR #443's greedy search. **112 is the exact maximum of that pivot
model on R715** (§2, certified by an exact computation that `verify.py --light` reruns), so the pivot count cannot be improved within it (the choice of donors among 112-pivot selections still moves `c`, §3).

## 1. The width rule (what sets the width of a residual)
**Rule.** A helper register `h` whose start frame has dimension `e_h` leaves, in every local invocation, the residual `D_P` with `P` the
coordinate projector of width **8 − e_h**. In the kernel word only *kernel pivots* have a nonzero start frame, so exactly the pivots have a
narrow residual (width `8 − rank(entrance)`); every other helper has width 8, at every stage.

**Derivation.** (a) The dirty local invocation acts on the stream owning a helper residual as an exact coordinate factor `D_P`
(`idle-axis-hosting/PROOF.md` §1(a), PR386-BIT-GEOMETRY, #434), and its endpoint is the partial swap `D_{I−σ_E}` of the entrance projector σ_E
(`e8-r740-replica32/PROOF.md`, "Residual routes": the rows of the entrance isometry `N`, `NNᵀ = 4I`, span `E`, the remaining rows map `E⊥`
isometrically onto a coordinate block; reversal has the same residual projector `I − P_E`). `rank(I − P_E) = 8 − dim E`. (b) A helper has a
nonzero start frame only if the kernel gave it one: `replica_kernel.kernel` asserts that every helper starts at the zero frame and sets
`start[p] = E` for pivots `p` only. Target mixing (`mix_target.py`) edits D/B gates of the *target* registers 120–239 and never a helper's start.

**Exact check** (`verify.py`, LIGHT and FULL): the width of every helper is computed three independent ways and they agree on all 715 helpers.
(i) From the kernel word's start frames (`kernel_cap.width_rule_check`: `width = 8 − dim(start frame)`, `width < 8` exactly for the selected
pivots, equal to `8 − |entrance|`); (ii) from the exported PR #249 records of the *mixed* word (`249-states.json` initial frame ids and
`frames.json` dimensions) — this also shows mixing leaves helper widths untouched; (iii) in FULL, by the independent hosted audit
(`audit_hosted_k.py` recomputes `8 − dim(initial frame)` from the records and rejects a wrong residual width: a mutation is in its control list).
Result: **112 residuals of width 7, 603 of width 8**.

## 2. The pivot ceiling (what is proved and what is computed)
Setting (PR #443's `kernel()` conditions, re-asserted by `kernel_cap.check_selection`, which adds the coordinate-flat requirement of the verified
residual-isometry format, as `kernel_rebuild` does; `kernel()` itself accepts any flat): a pivot `p` enters at a coordinate flat `E` of frame lines
inside `first(p)`; its delivery vector `resp(p) ∈ F₂¹²⁰` (the targets it feeds in the D phase) is dropped and recreated by donors `D`, each with
`E ⊆ first(d)`, `resp(p) = ⊕ resp(D)`; pivots and donors are disjoint and a donor serves one entrance.

**Proved** (pure linear algebra, given those conditions):
1. *Only carriers qualify.* `E ≠ 0` forces a frame line inside `first(p)`: on R715 **263 of 706 helpers** (the set `C`).
2. *WLOG rank-1 coordinate entrances* (as far as the listed conditions go; the exact replay is checked on the shipped selection). Replacing every entrance flat by one of its frame lines keeps every entry valid (smaller `E` is contained in
   `first` of every member; merging classes only enlarges donor pools), so the maximal number of pivots over *all* coordinate selections is attained by
   rank-1 selections. (Rank > 1 only narrows a residual further; it never adds a pivot.)
3. *The problem is a partition problem.* With classes `T_i ⊆ S_i = {h ∈ C : frame line i ∈ first(h)}` (disjoint), the best class `i` gives
   `|T_i| − rank_F₂ resp(T_i)` pivots (donors = a basis, pivots = the other members), so
   `max pivots = |C| − min_{partitions} Σ_i rank resp(T_i)`.
4. *Ceiling.* `Σ_i rank resp(T_i) ≥ rank resp(⋃T_i)` (subadditivity) and `|U| − rank(U)` is monotone in `U`, hence
   **pivots ≤ |C| − rank resp(C) = 263 − 86 = 177** (valid, but loose: the exact maximum below is 112).
5. *Parity.* PR #443's 32-replica bank equation `32(8R − Σ entrance ranks) ≡ 0 (mod 64)` needs an even entrance-rank total, so an odd rank-1 count
   loses one pivot (111 → 110).
6. *Scope.* The 177 holds for coordinate entrances only. With any flat allowed (as upstream `kernel()` does), all 706 helpers qualify and the same
   argument gives `|H| − rank resp(H) = 706 − 120 = 586`, in a format this package does not verify. Both bounds stay as stated, scoped bounds; both are loose.

**Computed** (exact F₂ elimination, `code/kernel_cap.py`, data in `data/cap-analysis.json`): `|C| = 263`, `rank resp(C) = 86`, class sizes
65–81 and class ranks 37–43 per frame line (class nullities 25–39), 232 of the 263 carriers lie in the span of the others of some class (the only ones
that can be pivots), and the matroid of delivery vectors has one big component (208 elements) beside components of 28 and 14 and 13 coloops.

**Exact maximum: 112 (computer-assisted exhaustive search on the retimed R715 word, certified by `code/exact_pivots.py`; `verify.py --light` recomputes it and asserts 112).** The partition problem of item 3 is a
*min-sum-rank list partition*: it minimises a sum of ranks, so it is not a matroid union, intersection or parity problem (those maximise rank), and it is NP-hard
when the number of classes is unbounded (vertex cover reduces to it). It is nevertheless solved exactly here, with 8 classes and the block structure of the
delivery vectors:
1. The matroid of the 263 delivery vectors splits into connected components of 208 (rank 63), 28 (rank 5) and 14 (rank 5) elements plus 13 coloops; the
   objective is additive over components.
2. The components of 28 and 14 are solved by an exhaustive dynamic programme over the tuples of class spans: minimum sum-rank 12 and 5, i.e. 16 and 9 pivots.
3. The 208-element component consists of 13 block-local groups (supports inside one group of targets joined by vectors of weight ≤ 4) and 24 coupling
   elements (12 with a two-line list). Blocks have disjoint coordinates, so ranks add over blocks: **lower bound** = Σ exact block minima (DP, 100) +
   the minimum over all 2¹² coupling assignments of Σ_i rank(coupling part of class i modulo the largest span the blocks could give it) (20) = **120**.
   An exhaustive depth-first search over the block-optimal span tuples, pruned by the optimistic completion "every remaining block at its maximal span",
   shows 120 **infeasible** and exhibits 121 (hence minimum sum-rank 121, i.e. 87 pivots).
4. Total **87 + 16 + 9 = 112** pivots; 112 is even, so the parity rule drops none. The exact maximum equals the annealing plateau (14 of 16 restarts at 112,
   never 113) and the shipped selection. The 177 above and the 586 of item 6 are therefore valid but loose bounds
   (the CP-SAT relation model of `select_kernel.py --ilp`, restricted to ≤ 3 donors per pivot, stalls at 110–111 with an unclosed bound: a restriction, not a proof).
Scope of the 112: the model of items 2–3 (rank-1 coordinate entrances, one entrance class per donor, 8 frame lines of the R715 word; PR #443's conditions as
re-asserted by `kernel_cap.check_selection`). It is a statement about that format, not about formats where a donor serves nested entrances or entrances are
not coordinate flats (those are outside it, as for the 177). Entrances at any of the 120 root lines (outside the verified format, which needs coordinate
isometries) were searched only, in the same kind of budget, and did not beat 111; they are not covered by the exact result.

Why it matters: the model price of a rank-1 pivot is about +0.03% of `c` here (§4). The 177 ceiling would have been about +2.9% (§4); the exact maximum
shows it is not reachable, so the pivot count on R715 within this format is used up: 112 is the optimum.

**Method credit.** The min-sum-rank formulation, the component and block decomposition, the per-block exact DP, the coupling-assignment lower bound and the
search with optimistic completion come from the matroid-optimisation pass of DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Related
literature on partitioning with a sum of submodular (here: rank) costs: submodular multiway partition / load balancing (Svitkina and Fleischer 2008;
Chekuri and Ene 2011). The same method gives **101 pivots on the R687 read-then-climb word** (100 after the parity rule); that is computed outside this package
and will be reported in a follow-up PR.

## 3. The selection method
`code/select_kernel.py WORD`: draw an initial class assignment, then anneal single-helper class moves with the exact objective `Σ_i rank resp(T_i)`
(Metropolis, linear cooling 0.6 → 0.03). It turns the best assignment into PR #443 entries `[[frame line], pivot, donors]` (donors = greedy F₂ basis of
each class; each pivot written over that basis), applies the parity rule, and checks every entry with the exact conditions
(`kernel_cap.check_selection`). `code/kernel_from_selection.py` builds the word with PR #443's kernel (unchanged), PR #436's retiming, exact replay
and the interface check, and writes the residual isometries; it also runs six mutants of the selection (a dropped donor, a pivot as its own
donor or as another entry's donor, an entrance moved to another frame line, an odd entrance-rank total, an entrance not spanned by frame lines) that the
checker must reject (listed in `EXPECTED.json`). The pinned search is `--seed 3 --iters 150000 --restarts 1`
(`verify.py` FULL reruns it and requires the file `data/kernel-selection.json` byte for byte). Among eight seeds the 112-pivot selections differ
only in which helpers act as donors, which moves the local paid profile and so `c` between 1.295564·10⁻³ and 1.295911·10⁻³; the shipped seed is
the best of those eight (an exact-priced choice among equal pivot counts, not a different construction).

## 4. The verified word and what a pivot is worth
FULL mode runs the complete bit pipeline on the new kernel: relaxed all-column checker (kernel and mixed words), C++ cohort legality, formal
columns at five and eleven stages, record mutants, Gram, mixing check with four rejected mutants, eleven-stage geometry/template/parent audit,
hosting selection **rediscovered with HiGHS and required equal** to `data/selection.json`, hosted audit (16 mutations rejected), assembly; then PR #458's
complex supplier from scratch and the exact composition (two moment engines per side, six bootstrap levels, 47 strict outer inequalities, and the
next-grid / zero-η / zero-β / unit-β rejection controls). Local paid profile per call (C++ legality): {"1": 2385, "2": 1041, "3": 249, "4": 289, "5": 114, "6": 58, "8": 9}.

| kernel | pivots | helper widths | local paid profile (per call) | whole-residual hosting c | vs R715 |
| --- | ---: | --- | --- | ---: | ---: |
| R715 greedy kernel (PR #443 search, 84 mixed-rank pivots) | 84 | {"4": 2, "6": 24, "7": 58, "8": 631} | {1: 2438, 2: 1031, 3: 240, 4: 287, 5: 114, 6: 58, 8: 9} | 1.2851287·10⁻³ | +0.000% |
| 0 rank-1 pivots | 0 | {"8": 715} | {1: 2274, 2: 871, 3: 428, 4: 263, 5: 140, 6: 58, 8: 9} | infeasible (host-all fails) | - |
| 56 rank-1 pivots | 56 | {"7": 56, "8": 659} | {1: 2362, 2: 981, 3: 310, 4: 273, 5: 130, 6: 58, 8: 9} | 1.2722668·10⁻³ | -1.001% |
| 70 rank-1 pivots | 70 | {"7": 70, "8": 645} | {1: 2369, 2: 997, 3: 293, 4: 275, 5: 128, 6: 58, 8: 9} | 1.2781050·10⁻³ | -0.547% |
| 84 rank-1 pivots | 84 | {"7": 84, "8": 631} | {1: 2375, 2: 1011, 3: 279, 4: 281, 5: 122, 6: 58, 8: 9} | 1.2839216·10⁻³ | -0.094% |
| 98 rank-1 pivots | 98 | {"7": 98, "8": 617} | {1: 2380, 2: 1030, 3: 260, 4: 281, 5: 122, 6: 58, 8: 9} | 1.2899955·10⁻³ | +0.379% |
| 112 rank-1 pivots | 112 | {"7": 112, "8": 603} | {1: 2385, 2: 1041, 3: 249, 4: 289, 5: 114, 6: 58, 8: 9} | 1.2959106·10⁻³ | +0.839% |

Each rank-1 pivot is worth about +0.033% of `c`; R715's 84 greedy pivots (total entrance rank 114) beat 84 rank-1 pivots by 0.094%, so extra entrance rank on a
pivot is worth roughly 0.003% per unit (rank-2 upgrades of the selected pivots are not explored here).

`hosting_model.py` (CP-SAT, whole-residual rule, exact two-engine endpoint) reproduces the pipeline's hosted endpoint to the last digit and is how
the scan is priced. Under the same model, 177 rank-1 pivots would give +2.9% (the proved ceiling, loose and not reachable: the exact maximum is 112; not claimed) and 240 (all A2 rank-7 copies full)
+5.8% relative to 112; k = 0 is infeasible (the width-8 slots of the 240 copies cannot hold the 7,865 residuals): narrow residuals are
required, not just helpful.

## 5. Comparison (honest)
* Over PR #463 (84 mixed-rank pivots, same word, same pipeline): bit c +0.839%, κ +0.838%.
* Over #472 (κ ≈ 1.292100·10⁻³ as quoted) +0.165%.
* Against the current lemma-less frontier this package is behind: **−0.108% vs #473** (κ = 1.295630·10⁻³, as updated on Oct 11, now the frontier) and
  **−0.098% vs #478** (κ = 1.295509·10⁻³). The first 112-pivot selection tried (seed 1, c = 1.295564·10⁻³) landed, in κ, within 0.003% of #473 *as first
  posted* (1.293922·10⁻³), **by kernel choice alone, without retiming or reordering**; the pinned best-of-eight seed adds 0.027% on top of that. This is
  selection tuning, nowhere near the ≥ 1% bar for a standalone result; the point of the package is the method, the rule and the ceiling, not the
  frontier. Whether it stacks with #473's retiming and #470's reordered deliveries is not tested.
* The bit side now sits 0.1% under PR #458's complex endpoint (1.297204·10⁻³): further bit gains here are capped by the complex supplier.

## 6. Reproduce
```sh
python -m pip install -r research/e8-r740-replica32/parent436/requirements.txt scipy ortools
python -B research/e8-r715-kernel-cap/verify.py /abs/new/out --light        # about two minutes, no C++
python -B research/e8-r715-kernel-cap/verify.py /abs/new/out                # FULL: about 40 minutes with a C++17 compiler and Boost
python -B research/e8-r715-kernel-cap/code/exact_pivots.py research research/e8-r715-eleven-stage-whole/data/word-r715.json.gz exact.json   # exact maximum: 112
python -B research/e8-r715-kernel-cap/code/select_kernel.py research research/e8-r715-eleven-stage-whole/data/word-r715.json.gz sel.json --seed 3 --iters 150000 --restarts 1
```
FULL accepts `--complex-output=DIR`, `--complex-upstream=DIR`, `--reuse-parent443=DIR` (already verified parents) and `--quick`.
Contents: `code/kernel_cap.py` (candidates, ceiling, exact selection and width checks), `code/exact_pivots.py` (exact pivot maximum: block DP and
exhaustive search, about 10 s plus the word load), `code/select_kernel.py` (annealing, optional CP-SAT),
`code/kernel_from_selection.py`, `code/hosting_model.py`, `code/scan_pivots.py`; `data/` (selection, kernel and mixed words, isometries, hosting
selection, ceiling analysis); `compose.py`; `EXPECTED.json`, `SOURCE.json`, `MANIFEST.json`, `NOTICE.md`.

## 7. Scope
Conditional like its parents (inherited compiler/dirty-helper/precision/analytic assumptions, PR #450's Lemma M for the bit target mixing,
PR #458's adapters). No cross-copy or cross-family lemma is used. The ceiling and the exact maximum in §2 are statements about the shared-donor kernel format of PR #443;
formats where a donor serves nested entrances, or entrances that are not coordinate flats, are outside it. No unconditional theorem or Lean proof is claimed.
