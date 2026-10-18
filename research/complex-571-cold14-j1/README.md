# complex-571-cold14-j1: conditional κ 0.001620246754858718

This package is PR604's `complex-571-cold14` (DreamingOfClouds) with an improved literal owner map: an ejection-chain (depth 2) polish of PR604's map at the same dispatch (ck ×44, atm3 ×22, jp8 ×6). Only `data/OWNERS.json.gz`, `data/PLAN.json` (profile/windows) and `data/SPEC.json` (expected values) differ; the construction, code and controls are PR604's, byte for byte. The rest of this README is PR604's, with paths updated.

**Build on this at your own risk.** DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. This package awaits independent review.

## Result

κ = **0.001620147045734211** (conservative model 0.001620147042858282). That is **+0.368% over PR601** (0.001614202339036103) on dispatch ck ×44, atm3 ×22, jp8 ×6. The value comes from `ASSEMBLY.json` of the strict `verify.py` run on this package's literal owner map. The paid profile is {1:185869, 2:32471, 3:23609, 4:14128, 5:5040, 6:2016, 7:6, 8:581, 16:15, 24:1, 32:76, 48:2039} (live 7168, deficit 2560).

The complex side binds:

| quantity | value |
|---|---|
| native complex lower bound | 0.001622776181770995425298 |
| bit supplier value (PR543) | 0.0016538 (`bit_lower` 0.001653826988146798944268) |
| κ with the bit cap | 0.001620147045734211 |
| κ without the bit cap | 0.001620147045734211 |

The bit value is above the complex bound, so it does not bind, and κ is the same with or without the cap.

## What changes relative to PR601

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

## Why the cold ends are legitimate

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

## Verifier changes (inert for words without cold ends)

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

## Future optimization (results and open headroom)

All LP figures below are first-order bounds. They come from the aggregate hosting LP (the whole-owner model on PR601's windows, objective Σ r·ln(73/r)), calibrated against exact moment-engine prices. On PR601's own dispatch and widths, the LP lies within 0.005% of PR601's literal map.

| quantity | value |
|---|---|
| LP ceiling, fixed dispatch (PR601's ck 45 / atm3 21 / jp8 6, all cold) | ≈ +0.49% |
| LP ceiling, free dispatch over {ck, atm3, jp8} cold | ≈ +0.71% |
| this package's literal map | +0.368% |
| remaining owner-map headroom on the fixed dispatch | ≈ 0.12 pt |

- **Free dispatch is jp8-heavy.** The LP puts about 70 calls on jp8 and about 2 on atm3. The LP's idle remainder is pure rank-48 idle children, whereas the literal map still leaves some rank-16 and rank-32 idle children.
- **What limits jp8.** The time windows do not limit jp8. Time-refinability does: within each owner group, each port may host at most one helper per call. The aggregate optimum ignores this, and the exact per-port refinement of it is infeasible. Literal maps for jp8-heavy dispatches found so far are worse than PR601's dispatch.
- **Closing the gap.** An exact, edge-colourable owner model is the remaining owner-side lever: per-time Hall conditions, or a pattern-restricted model warm-started from this map.
- **End dimension (first-order).** Raising a unit's end frame from dim 4 to dim d needs the last tail gate at that frame, which lifts one partner. This adds 2ψ(d−4) + ψ(9−d) − ψ(5) to the local cost per unit, where ψ(r) = r·ln(73/r). That is +6.8, +10.6, +13.0 and +14.1 for d = 5…8. The remaining hosting headroom is about 1–2 per unit, so d = 4 is the best end dimension for these units.
- **Necessary condition, for any cleanup factorisation.** A helper h can end at a frame U only if, at the end of B, the supports of its row in the inverse state map and of its dirt column both lie in Q_U, the registers whose end-of-B frames lie in U. The transport checks this condition for every low-frame end. Choosing which units satisfy it, through the premix, is the supply question. This package uses 14 units per word. Their optimality per word is not certified here.

## Verification

Fetch the pinned sources exactly as for PR601, then run:

```sh
research/complex-571-cold14-j1/verify.sh /tmp/complex-571-cold14-j1 ..
# kappa 0.001620147045734211
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

## Credits

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
