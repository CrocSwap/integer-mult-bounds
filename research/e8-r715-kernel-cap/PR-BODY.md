> ⚠️ **Draft:** the heavy verification (full fresh-copy replays, CI) is still running. Build on this at your own risk.

Method and knowledge package on the R715 bit word (PR #463): **what sets the width of a residual, how many narrow residuals the shared-donor kernel can give on the retimed R715 word with coordinate entrances (the verified residual-isometry format: exactly 112), and a 112-pivot kernel selection by seeded annealing.** Conditional **κ = 1294233365881801/1000000000000000000 ≈ 1.294233365881801·10⁻³, bit-bound**: +0.838% over #463
and +0.165% over #472 (κ = 1.292099559·10⁻³). It is below the current lemma-less frontier: −0.108% vs #473 (κ = 1.295630·10⁻³, as updated on Oct 11, now the frontier) and −0.098% vs #478 (1.295509·10⁻³). This PR's point is the method and the bounds, not the frontier. The bit supplier is c = 1295910576589222380953/10²⁴ ≈ 1.295911·10⁻³ (+0.839% over R715). Same word, same
hosting rule, same mixing, #458's complex supplier unchanged: only the kernel selection changes, 84 → 112 pivots.

| side | supplier | endpoint |
| --- | --- | ---: |
| bit (binds) | R715 word, **112 rank-1 kernel pivots**, eleven stages, #442 whole-residual hosting, target mixing | c ≈ 1.295911·10⁻³ |
| complex | #458 paid-adapter kernel, unchanged | b ≈ 1.297204·10⁻³ |

**What is new**
1. **The width rule, checked exactly.** A residual's width is 8 − entrance rank, and only kernel pivots have a nonzero entrance: the helper hierarchy and the
   target mixing do not set it. Checked three ways on all 715 helpers (kernel-word frames, exported records of the mixed word, the independent hosted audit).
2. **The pivot ceiling and the exact maximum, for coordinate entrances** (the verified residual-isometry format). A pivot needs a frame line inside its first frame (263 of 706 helpers), and its delivery vector must be an XOR of donors of one
   entrance class. *Proved:* pivots ≤ |C| − rank = 263 − 86 = **177**, and rank-1 coordinate entrances lose nothing up to parity. *Exact maximum on the retimed R715 word: **112**, by a computer-assisted exhaustive search (independently re-audited), certified by
   `code/exact_pivots.py`* (rerun by `verify.py --light`, asserted equal to 112, about 10 s): the pivot problem is a min-sum-rank list partition (max pivots = |C| − min Σ_i rank of the class
   vectors; NP-hard in general, not a matroid union/intersection/parity problem), solved exactly here by splitting the delivery matroid into components (208 / 28 / 14 elements plus 13 coloops),
   exhaustive span-tuple DP on the small ones (16 and 9 pivots) and, on the 208, an exact block DP with a coupling-assignment lower bound and an exhaustive search (minimum sum-rank 121, so 87 pivots;
   120 shown infeasible): 87 + 16 + 9 = 112. The annealing plateau (14 of 16 restarts at 112, never 113) is therefore optimal. Priced by the model, a rank-1 pivot is worth ≈ +0.033% of c,
   so the pivot count on R715 is exhausted within this format (177 would have been ≈ +2.9%; it is not reachable; the donor choice among 112-pivot selections still moves c, README §3).
   *Scope:* the 177 and 586 are valid but loose scoped bounds; the 177 does not cover non-coordinate entrances. Upstream `kernel()` itself accepts any flat; there all 706 helpers qualify and the same argument
   gives only 706 − 120 = 586, in a format this package does not verify (it needs coordinate residual isometries). The exact 112 is a statement about the same coordinate, one-class-per-donor model;
   entrances at arbitrary root lines were only searched.
   *Follow-up:* the same exact method gives 101 pivots on the R687 read-then-climb word (100 after the parity rule); to be reported in a follow-up PR.
3. **The method:** `select_kernel.py` anneals the class assignment on the exact objective Σ rank (self-contained xorshift64*, reproducible from a seed),
   `kernel_from_selection.py` builds the word with #443's kernel unchanged. Pinned: `--seed 3 --iters 150000`.
4. Honest size: by kernel choice alone, without retiming or reordering, the first 112-pivot selection (c = 1.295564·10⁻³) landed, in κ, within 0.003% of #473 as first posted (1.293922·10⁻³);
   the shipped best-of-eight seed was 0.027% above that. #473 has since been updated (1.295630·10⁻³) and is 0.108% above this PR. This is selection tuning, not a ≥ 1% result.

**Verification** (`python -B research/e8-r715-kernel-cap/verify.py /abs/out [--light]`; CI workflow `e8-r715-kernel-cap`): LIGHT (about two minutes) checks integrity and
pins, recomputes the ceiling analysis from the pinned R715 word, **recomputes the exact pivot maximum and asserts 112**, checks the selection against #443's exact kernel conditions plus the F₂ response relation and the coordinate-flat condition,
rebuilds the kernel word (replay, interface) and the mixed word and compares them, checks the width rule, re-solves the hosting (CP-SAT) and prices it with the
exact engine, and runs the screen composition with #458's pinned endpoint. FULL adds the seeded search, #443's regressions, the relaxed all-column checker,
C++ cohort legality and formal columns at five and eleven stages, mixing mutants, Gram, eleven-stage template/audits, **hosting selection rediscovered with HiGHS and
required equal**, hosted audit, assembly, the pivot-count scan, #458's complex supplier from scratch, and the exact composition (two moment engines per side, six
bootstrap levels, all 47 strict outer inequalities, next-grid / zero-η / zero-β / unit-β rejection).

**Review points**
- The ceiling's proof (items 1–4 of README §2) is elementary. The new claim is the exact maximum 112: its certificate is the code in `code/exact_pivots.py` (component split, block DP,
  coupling lower bound, exhaustive search), rerun in LIGHT; please review that code and the min-sum-rank formulation of README §2 items 2–3 it relies on.
- The seed choice among equal pivot counts is an exact-priced selection (c between 1.295564 and 1.295911·10⁻³ across eight seeds).
- Inherited and unchanged: #450's Lemma M (bit target mixing, chained receivers), #458's paid adapters, the R715 hierarchy and its carrier bound (#463).
- The bit side is now 0.1% under #458's complex endpoint; further bit gains here are complex-capped.
Conditional like all parents; no unconditional theorem or Lean proof is claimed.

Credits: chafreaky (#417 shared-donor kernel and exact replay, #443 replica kernel and residual isometries, #451/#454 whole-residual rule, #458 paid adapters, #472),
rohanarun (#434 retiming with kernels, #435 banks, #460 composition and verifier structure, #467, #470 retimed kernel and reordered R715 deliveries, #473), eumemic (#436 R740 word,
#440/#441), DaysSky (#442 idle-axis hosting), Dylan Crow (#370 word, producer, checkers), Srikrishnabalaji (#465), Dugongue (#471, #476, #478), jacklightChen and Zhihao Chen
(#386/#425), icekylinx (#433), higherbeing (#448), Jacob Sussman and all source-pinned authors. Width-rule check, ceiling analysis, exact pivot maximum (min-sum-rank formulation, component/block decomposition, exhaustive search; related literature: submodular multiway partition, Svitkina-Fleischer 2008, Chekuri-Ene 2011),
annealing selection, kernel build from a selection, hosting re-solve, pivot scan, composition and verifier by DreamingOfClouds with
**Claude Opus 5.5 (Anthropic), via Claude Code**.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
