# complex-571-cold14-f6: conditional κ 0.001625715867072461

## Definition

The witness `cold14` is the PR558 geometry (112 data columns, h = 9, 504 helpers, 8 centres, 9 stages × 8 replicas = 72 calls) served by 2 provider words, each a pinned base word followed by typed build steps: **jp8** (70 calls) = the frozen PR558 promoted word → `cold_kernel` (PR568 `data/EIGHT-COLD.json`) → `multicut` (PR568 `data/EIGHT-MULTICOLD.json`) → `frozen558_scalar_audits` (inherited static44 and rank-five audits; word unchanged) → `joint_prefix` (PR575, variant `eightcold`) → `hyperplane_end` (46 helpers end at a hyperplane U instead of FULL) → `cold_end` (14 cold helpers end at a dim-4 frame U instead of FULL, after a 142-gate rank-0 premix at the head of A, 56 lower-frame cleanup gates and an exact refactored cleanup); **atm3** (2 calls) = PR571's `frontier-composition/combined-prefix-word/FULL-WORD.json.gz` → `promote` (40 entrance promotions, PR569's constructor) → `greedy_kernels` (12 multi-cut cold kernels, PR568's constructor) → `frame_coalesce` (6 frame coalescences, PR583's constructor) → `gate_move_coalesce` (2 coalescences, each after moving an addition past commuting additions; 2 moves) → `hyperplane_end` (46 helpers end at a hyperplane U instead of FULL) → `cold_end` (14 cold helpers end at a dim-4 frame U instead of FULL, after a 142-gate rank-0 premix at the head of A, 56 lower-frame cleanup gates and an exact refactored cleanup). Each step runs a pinned, unchanged constructor plus its paired omission or negative-control audit; a hyperplane-ended helper starts at its entrance frame E, ends at the hyperplane U, and pays residual width |U| − |E|; a cold-ended helper starts cold (E = ∅) and ends at its low-dimensional frame U, so it pays |U|; every other helper ends at FULL, so its width stays h − |E|. The dispatch (which provider serves each (stage, replica) call), the asynchronous call order and the literal owner map are `data/PLAN.json` (`provider_calls`, `order`) and `data/OWNERS.json.gz`, at the dispatch jp8 ×70, atm3 ×2 (the aggregate free-dispatch hosting LP's jp8-heavy selection, with the two atm3 calls at times 0 and 2 so PR604's provider-at-wrong-call control finds an equal-parity partner); the owner map is an exact per-time-Hall exact-window MIP solution (RINS around the exact-window LP vertex; 150 s time limit, relative gap 1.43e-7) (see `data/cand.json`), and PLAN is the window MIP's PLAN with the provider registry re-derived from the admitted provider locals and `profile`/`assignment_sha256` recomputed from the map (ColdOwner mkplan.py); the resulting paid profile is {1:178744, 2:24336, 3:33617, 4:13328, 5:5040, 6:2016, 7:3, 8:576, 48:2025} with live 7168, physical 7682 and deficit 2560, giving κ = 1625715867072461/1000000000000000000 = 0.001625715867072461 (conservative model 0.001625715864253489).

## Files

| file | role |
|---|---|
| `data/WITNESS.json` | **inputs only**: geometry, pinned sources, the provider build chains above, dispatch and call order, and PLAN/OWNERS/recipes by SHA-256 |
| `data/EXPECTED.json` | **expected values only**, all derived by recomputation (`spec.py generate`): per-step word hashes and control counts, per-provider artifacts, programs and profiles, global profile and counts, κ. Bound to WITNESS.json by hash |
| `data/PLAN.json`, `data/OWNERS.json.gz` | dispatch, call order and literal owner map (inputs, pinned by WITNESS.json) |
| `data/recipes/` | the package's own step recipes (inputs, pinned by WITNESS.json); `data/recipes/ck-step0-greedy_kernels.json`, `data/recipes/ck-step1-frame_coalesce.json`, `data/recipes/ck-step2-gate_move_coalesce.json`, `data/recipes/ck-step3-hyperplane_end.json`, `data/recipes/ck-step4-cold_end.json.gz` is used only by `data/cand.json` (a menu provider the owner solve did not dispatch), not by the witness |
| `data/cand.json` | the search candidate (schema candidate/1), an input of the search side: the provider chains (PR604's), the dispatch rule and the PLAN rule, and the owner search (start map `owners.warm_owners`, solver settings, LP pattern inputs, objective and the solve result), with package-relative and `NAME:` source references. The verifiers do not read it |
| `PROOF-COMMUTING-PREFIX.md` | proof note for the construction (documentation; no verifier reads it) |
| `data/search/WARM-OWNERS.json.gz` | search input named by `data/cand.json` (`owners.warm_owners`): the R1 map (`data/OWNERS.json.gz` of research/complex-571-cold14-r1, byte for byte), used only to seed the aggregate LP's patterns. The shipped `data/OWNERS.json.gz` is the search's result; the verifiers do not read this file |
| `data/search/DISPATCH.json` | search input named by `data/cand.json` (`owners.search_inputs`): the dispatch {time: provider}: jp8 ×70, atm3 at times 0 and 2; the verifiers do not read this file |
| `data/search/LP-PATTERNS-AGG.json` | search input named by `data/cand.json` (`owners.search_inputs`): aggregate LP relaxation at the dispatch (crossover, tight 3), pattern-seeded from the R1 map; the verifiers do not read this file |
| `data/search/LP-PATTERNS-EX.json` | search input named by `data/cand.json` (`owners.search_inputs`): exact-window LP relaxation (crossover) at the dispatch over the base patterns plus aggregate-LP patterns with weight >= 0.01; the verifiers do not read this file |
| `data/search/TEMPLATE-PLAN.json` | search input named by `data/cand.json` (`owners.search_inputs`): PR604's data/PLAN.json, whose windows/order/registry template the nominator reuses; the verifiers do not read this file |
| `data/search/WARM-PLAN.json` | search input named by `data/cand.json` (`owners.search_inputs`): the R1 PLAN matching WARM-OWNERS.json.gz (pattern seeding of the aggregate LP); the verifiers do not read this file |
| `data/SPEC.json`, `verify.py`, `verify.sh`, `code/` | the combined spec and package verifier (PR604's verifier and code, byte for byte); they verify the same record |

`data/PLAN.json` carries `"status": "LITERAL_OWNER_NOMINATION_PENDING_ADMISSION"`. That label was written by the owner nominator before admission and is kept unchanged because WITNESS.json pins PLAN by hash; admission is what the verifiers below establish, and the label carries no meaning for them.

`SPEC.expected.entering_helper_roles` corrected from PR604's stale 16344 to the audited 16584 (audit_allcold.py, as pinned in EXPECTED.json); PR604's verify.py does not read this key.

## Verification

The pinned sources are not merged; fetch their pinned commits first:

```sh
git fetch origin pull/568/head:pr568 pull/571/head:pr571 pull/569/head:pr569 pull/575/head:pr575 pull/583/head:pr583
git worktree add --detach ../pr568 71c99ac935a33bb7b59a1b4a7af8725a939b0b90
git worktree add --detach ../pr571 b7bdc5a8de18fcf418cfb9c7d83a2b1097a5e4a3
git worktree add --detach ../pr569 897213a855b7fb8a1b8b0e552a2f5c42e6c1b326
git worktree add --detach ../pr575 eac6f7e378ab622dac50a2fd4b7ef6eab014de44
git worktree add --detach ../pr583 89be768f0157f5a3d8e4db69cf1748768605eac9
```

Generic verifier (`research/witness-spec-tools`, PR587 with the `frame_coalesce`, `gate_move_coalesce`, `hyperplane_end` and `cold_end` step types; its `code/build_hpe.py`, `code/hpe_controls_atc.py`, `code/build_cold_end.py`, `code/cold_end_controls.py`, `code/hpe_audit_and_transport.py` and `code/hpe_*_local.py` must be byte-identical to this package's `code/` copies, which define the hyperplane-end and cold-end constructors, their controls and the generalised native chain). It builds everything from `data/WITNESS.json` and only compares against `data/EXPECTED.json`:

```sh
T=research/witness-spec-tools
python3 $T/spec.py check --package research/complex-571-cold14-f6 \
  --source multicold=../pr568/research/complex-multicold \
  --source structural_gain=../pr571/research/structural-gain \
  --source larger_gain=../pr569/research/larger-gain \
  --source joint_prefix=../pr575/research/complex-joint-prefix \
  --source frame_coalescing=../pr583/research/kernel-frame-coalescing
python3 $T/verify.py --package research/complex-571-cold14-f6 --work /tmp/complex-571-cold14-f6 \
  --source multicold=../pr568/research/complex-multicold \
  --source structural_gain=../pr571/research/structural-gain \
  --source larger_gain=../pr569/research/larger-gain \
  --source joint_prefix=../pr575/research/complex-joint-prefix \
  --source frame_coalescing=../pr583/research/kernel-frame-coalescing
# kappa 0.001625715867072461
```

`verify.py` checks the package MANIFEST and every source, PLAN, OWNERS and recipe pin; replays PR558; rebuilds each provider word through its build chain (each step's input and output content hash pinned, 12 steps); localizes each word (hyperplane- and cold-ended words through the generalised native chain, with `0:U` wrappers for cold ends); then runs binding, the physical owner audit with 23 controller mutants, a fresh finite invoice, both exact moment engines, 114 assembly controls, the phase-timing controls and the generated-identity controls.

The original package verifier gives the same result from `data/SPEC.json`:

```sh
python3 -B research/complex-571-cold14-f6/verify.py --work /tmp/complex-571-cold14-f6-spec \
  --source multicold=../pr568/research/complex-multicold \
  --source structural_gain=../pr571/research/structural-gain \
  --source larger_gain=../pr569/research/larger-gain \
  --source joint_prefix=../pr575/research/complex-joint-prefix \
  --source frame_coalescing=../pr583/research/kernel-frame-coalescing
```

Both use only the Python standard library and require assertions (no `-O`). The result is conditional on the inherited assumptions listed in NOTICE.md.

## Construction and history (the package README as committed)

This package is PR604's `complex-571-cold14` (DreamingOfClouds) with only a new dispatch and literal owner map: jp8 ×70, atm3 ×2 (ck is on the menu but not dispatched), all three provider words PR604's. The dispatch follows the aggregate free-dispatch hosting LP (jp8 everywhere except two atm3 calls, placed at times 0 and 2 so each provider's first call has an other-provider partner of equal stage parity, as PR604's assembly controls require); the owner map comes from an exact per-time-Hall exact-window MIP at that dispatch, solved by RINS around the exact-window LP vertex. Only `data/OWNERS.json.gz`, `data/PLAN.json` and `data/SPEC.json` differ; the construction, code and controls are PR604's, byte for byte. The rest of this README is PR604's, with paths and Result numbers updated.

**Build on this at your own risk.** DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. This package awaits independent review.

### Result

κ = **0.001625715867072461** (conservative model 0.001625715864253489). That is **+0.713% over PR601** (0.001614202339036103) on dispatch jp8 ×70, atm3 ×2. The value comes from `ASSEMBLY.json` of the strict `verify.py` run on this package's literal owner map. The paid profile is {1:178744, 2:24336, 3:33617, 4:13328, 5:5040, 6:2016, 7:3, 8:576, 48:2025} (live 7168, deficit 2560).

The complex side binds:

| quantity | value |
|---|---|
| native complex lower bound | 814181561419308172413/500000000000000000000000 |
| bit supplier value (PR543) | 0.0016538 (`bit_lower` 0.001653826988146798944268) |
| κ with the bit cap | 0.001625715867072461 |
| κ without the bit cap | 0.001625715867072461 |

The bit value is above the complex bound, so it does not bind, and κ is the same with or without the cap.

### What changes relative to PR601

PR601 (jeremykothe2) dispatches three provider words: **ck**, **atm3** and **jp8**. In each word, 46 entering helpers per call end at a hyperplane. The mechanism comes from PR591, PR592 and PR601. The Lean side is Lemma A with an arbitrary terminal frame (PR593) and multi-gate tails (PR599).

This package appends one typed build step, `cold_end`, to each of the three chains, after `hyperplane_end`. In every call, 14 **cold** factory-scratch helpers end at a **4-dimensional frame U_b** instead of FULL, so their residual width drops from 9 to 4. These helpers are `S b.10`, one per factory block b: registers 234, 250, …, 442. The step has three parts.

1. **Premix.** 142 rank-0 gates at frame `[]` sit at the head of section A. For each block b, the premix swaps the dirt of `S b.0` and `S b.10`. It then fans the candidate's initial value out into `S b.1 … S b.7` with ±1 coefficients. The premix runs after the entry adapters and paid wrappers, so every gate on a cold-ended helper follows its pre-wrapper R_{0,U}^-1. The compensation reads no cold-ended helper.
2. **Lower-frame cleanup.** For each candidate h, four multi-gate tail gates run right after B at frame U_b:
   - `h += −½·P_a`
   - `h += P_b`
   - `P_c += h`
   - `P_d += h`

   Here P_a … P_d are data ports whose end-of-B frames lie in U_b. After these gates, h's row and column of the state are unit vectors. The 46 inherited hyperplane-end gates follow unchanged.
3. **Exact FULL remainder.** A dyadic Gauss–Jordan refactorisation of the rest of the inverse replaces the literal reversed-inverse cleanup. It touches no helper that ends below FULL.

**Why the premix makes this possible.** A helper h can end at a frame U only if two things hold at the end of B, under every monotone common-frame cleanup:
- the row of h in the inverse state map is supported on registers whose frames lie in U;
- the column of h (every register carrying h's initial dirt) is supported on registers whose frames lie in U.

The premix spreads each candidate's initial dirt over `S b.0 … S b.7`. That collapses its dirt column to three low-frame registers, which is what makes the dim-4 frame reachable.

Effect per call and per provider:
- the paid local profile changes by {1:+28, 5:+14, 6:−28};
- 14 helpers go from width 9 to width 4.

The dispatch and the literal owner map are re-solved for the new widths (`data/PLAN.json`, `data/OWNERS.json.gz`). They come from an annealing search started from PR601's map, using relocate, swap, ejection-chain, bin-evacuation and provider-flip moves. Every inherited window, family and capacity constraint is kept.

The approach borrows from the uncomputation literature: Bennett 1989; Gidney 2015 (borrowed dirty ancillas); Häner–Roetteler–Svore 2017.

### Why the cold ends are legitimate

**Labels and realisation.** PR599's `hpe_labels_multi` / `hpe_word_multi` (Lean) cover:
- any number of tail gates per helper, as target or partner;
- interleaved helpers;
- any terminal frame;
- an unrestricted entrance, so the cold case E = ⊥ is included.

`exact_cold` reduces (N) for (⊥, U) to a monomial factorisation of T_U, which is how `canonical_frame` defines T_U.

**(N) for every (0, U_b) pair.** This is checked exactly here. `hpe_adapters_local.py` verifies L^-1 T_U R^-1 = C_[4] ⊗ I, global phase included, for all 14 dim-4 pairs. It rejects these wrapper mutants:
- identity pre or post wrapper;
- no wrappers;
- FULL decode;
- width 9;
- wrong U;
- wrong phase.

PR599's `cold_hyperplane_width` lemma is the dim-8 case. Here the width |U| − |E| = 4 − 0 is the |final| − |start| rule that PR591's verifier already applies at every global site.

**The refactored cleanup is not trusted.** `hpe_audit_and_transport.py` accepts a non-literal cleanup only when the word carries `refactored_cleanup`. Such a cleanup must:
- touch only non-target registers;
- use only dyadic additions and signed binary scales;
- make the arbitrary-dirt endpoint replay of the full reordered program exact in both orientations.

The transport also checks the row and column cone conditions above for every helper that ends below FULL.

**Wrapper order.** Two independent checks enforce it:
- The transport rejects any zero-frame precondition or compensation gate that touches a cold-ended helper.
- The event-level replay (`hpe_audit_local.py`) requires every scalar on a wrapped helper to lie between that helper's pre and post residual adapters. A negative control that hoists a premix gate in front of the pre-wrapper must be rejected.

### Verifier changes (inert for words without cold ends)

- `code/hpe_audit_and_transport.py`:
  - cold helpers may end at a proper subframe U (here dim 4) with `0:U` wrappers;
  - the row/column cone pre-check;
  - the refactored-cleanup switch;
  - the zero-frame wrapper-order assertion.
- `code/hpe_emit_local.py`, `hpe_audit_local.py`, `hpe_adapters_local.py`:
  - `0:U` wrappers for cold low-frame ends;
  - the event-level wrapper-order check;
  - 7 event-level and 7–8 recipe-level cold mutants.
- `code/audit_allcold.py`, `invoice_allcold.py`, `assemble.py`: a cold helper may end below FULL with `0:U` wrappers, and these count as wrappers.
- New step `cold_end`:
  - `code/build_cold_end.py` splices the recipe data and recomputes the profile and widths from the frame chains;
  - `code/cold_end_controls.py` holds 14 raw-word mutants that must be rejected, including a premix moved into the precondition.
- `code/witness.py` adds `WITNESS_RECORD`, used for discovery bookkeeping only.

### Future optimization (results and open headroom)

All LP figures below are first-order bounds. They come from the aggregate hosting LP (the whole-owner model on PR601's windows, objective Σ r·ln(73/r)), calibrated against exact moment-engine prices. On PR601's own dispatch and widths, the LP lies within 0.005% of PR601's literal map.

| quantity | value |
|---|---|
| LP ceiling, fixed dispatch (PR601's ck 45 / atm3 21 / jp8 6, all cold) | ≈ +0.49% |
| LP ceiling, free dispatch over {ck, atm3, jp8} cold | ≈ +0.71% |
| this package's literal map | +0.713% |
| remaining owner-map headroom on the fixed dispatch | ≈ 0.12 pt |

- **Free dispatch is jp8-heavy.** The LP puts about 70 calls on jp8 and about 2 on atm3. The LP's idle remainder is pure rank-48 idle children, whereas the literal map still leaves some rank-16 and rank-32 idle children.
- **What limits jp8.** The time windows do not limit jp8. Time-refinability does: within each owner group, each port may host at most one helper per call. The aggregate optimum ignores this, and the exact per-port refinement of it is infeasible. Literal maps for jp8-heavy dispatches found so far are worse than PR601's dispatch.
- **Closing the gap.** An exact, edge-colourable owner model is the remaining owner-side lever: per-time Hall conditions, or a pattern-restricted model warm-started from this map.
- **End dimension (first-order).** Raising a unit's end frame from dim 4 to dim d needs the last tail gate at that frame, which lifts one partner. This adds 2ψ(d−4) + ψ(9−d) − ψ(5) to the local cost per unit, where ψ(r) = r·ln(73/r). That is +6.8, +10.6, +13.0 and +14.1 for d = 5…8. The remaining hosting headroom is about 1–2 per unit, so d = 4 is the best end dimension for these units.
- **Necessary condition, for any cleanup factorisation.** A helper h can end at a frame U only if, at the end of B, the supports of its row in the inverse state map and of its dirt column both lie in Q_U, the registers whose end-of-B frames lie in U. The transport checks this condition for every low-frame end. Choosing which units satisfy it, through the premix, is the supply question. This package uses 14 units per word. Their optimality per word is not certified here.

### Verification

Fetch the pinned sources exactly as for PR601, then run:

```sh
research/complex-571-cold14-f6/verify.sh /tmp/complex-571-cold14-f6 ..
# kappa 0.001625715867072461
```

`verify.py` uses only the standard library and requires assertions. It runs these stages:

1. It checks the MANIFEST and every source, PLAN, OWNERS and recipe pin.
2. It replays PR558.
3. It rebuilds the three provider words through their typed chains. That is 17 steps, each with pinned input and output content hashes and paired controls.
4. It localizes each word through the generalised native chain:
   - exact scalar replay and the cone pre-check;
   - both reflected ledgers;
   - the independent local replay with its mutants;
   - exact wrappers;
   - all phase edges.
5. It runs binding and the physical owner audit with its controller mutants.
6. It runs a fresh finite invoice and both exact moment engines.
7. It runs the assembly controls, the phase-timing controls and the generated-identity controls.

The result is conditional on the inherited assumptions listed in NOTICE.md.

### Credits

- **jeremykothe2**:
  - PR601, PR600, PR596, PR592 and PR591: hyperplane-ended helpers, the HPE verifier, and the packages and owner maps this one starts from;
  - PR593: Lean Lemma A with an arbitrary terminal frame.
- **icekylinx**: PR531 and PR535 (entrance and kernel machinery).
- **DreamingOfClouds**:
  - PR509 and PR516 (the Lemma A / Lemma G Lean line);
  - PR599 (multi-gate and cold hyperplane-end Lean);
  - PR484.
- The pinned PR568, PR569, PR571, PR575 and PR583 packages and their authors, as listed in NOTICE.md.

DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
