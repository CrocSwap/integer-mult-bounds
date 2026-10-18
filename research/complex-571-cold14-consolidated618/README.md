# complex-571-cold14: conditional κ 0.001625434703655052

This revision consolidates twelve helpers in PR610's literal owner map and raises
its conditional κ from **0.00162536523418317** to **0.001625434703655052**
(**+0.00427408%**). The conservative value is **0.001625434700837327**.
The native complex lower endpoint is **0.001628081043082841928025**;
the inherited bit supplier does not bind.

The dispatch remains jp8 ×71 / ck ×1. All provider words, recipes, external pins,
and verifier scripts are unchanged from PR610 at
`b7c680ea38b9a25a89fce189bb927b45842362d0`. Twelve helper placements change,
and two additional records change only their packed offsets. The global profile is
{1:178526, 2:24345, 3:33840, 4:13249, 5:5040, 6:2016, 8:576,
32:1, 35:1, 41:1, 48:2020}, with live 7168, physical 7682 and deficit 2560.

See [OWNER-CONSOLIDATION.md](OWNER-CONSOLIDATION.md) for the exact change,
source pins and reproduction. `data/CONSOLIDATION.json` records all twelve moves;
`tools/consolidate_owners.py` deterministically nominates them from PR610's map.
The search tool is not an admission dependency. Use the existing `verify.sh` or
`verify.py` commands below to rebuild and admit the frozen candidate.

Prepared by Jeremy Diviney with OpenAI Codex assistance. This revision awaits
independent review and inherits every conditional assumption in NOTICE.md.
DreamingOfClouds and the other predecessor authors retain credit for the circuits,
provider dispatch, verifier and original owner construction.

---

## Historical PR610 background

The text below is PR610's original report, retained for attribution and context.
Its numerical values and references to “this package” describe the pinned
predecessor; the current result is the one above.

# complex-571-cold14: conditional κ 0.00162536523418317

**Build on this at your own risk.** DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. This package awaits independent review.

## Result

κ = **0.00162536523418317** (conservative model 0.001625365231365566). That is **+0.252% over PR604** (this package's base, commit 1b795c5, κ 0.00162128508944984) and **+0.692% over PR601** (0.001614202339036103), on dispatch jp8 ×71, ck ×1. The value comes from `ASSEMBLY.json` of the strict `verify.py` run on this package's literal owner map. The paid profile is {1:178526, 2:24344, 3:33840, 4:13248, 5:5040, 6:2016, 8:576, 32:1, 39:3, 41:10, 43:1, 44:2, 48:2008} (live 7168, deficit 2560).

The complex side binds:

| quantity | value |
|---|---|
| native complex lower bound | 0.001628011347227810262234 |
| bit supplier value (PR543) | 0.0016538 (`bit_lower` 0.001653826988146798944268) |
| κ with the bit cap | 0.00162536523418317 |
| κ without the bit cap | 0.00162536523418317 |

The bit value is above the complex bound, so it does not bind, and κ is the same with or without the cap.

## What this package changes relative to PR604

PR604 (this directory at commit 1b795c5) dispatches ck ×44, atm3 ×22, jp8 ×6, each with the cold-ended word described in the next section. This package keeps the ck and jp8 provider words, every verifier script and every remaining build step of PR604 unchanged; the atm3 chain is removed because it is no longer dispatched. Only the dispatch and the literal owner map change (`data/PLAN.json`, `data/OWNERS.json.gz`), together with the expected values recorded in `data/SPEC.json`.

1. **Dispatch moves to jp8.** 71 of the 72 calls use the cold jp8 word; one call (stage 2, replica 5) uses the cold ck word. jp8's widths are better matched to the idle children: per call jp8 has 114 helpers of width 8 and 274 of width 9, against 94 and 262 for ck, and 46 of width 7 against 78. Width 8 fills a rank-8 child exactly, and 9 + 7, 8 + 8 and 5 + 9 + 9 + 9 fill rank 16 and rank 32 exactly. Its local cost per call lies between atm3's and ck's, but the hosting remainder is much lower: in the all-jp8 solution every idle child of rank 8, 16 and 32 is filled exactly, and the only idle remainders are whole rank-48 children.
2. **Exact integer owner map.** The map is the optimum of a per-owner-group integer model (CP-SAT). Each owner group chooses how many ports have each width pattern (a multiset of helper widths summing to at most the rank). Each port hosts at most one helper per call, so for every pattern class and call the number of hosted helpers is at most the class size, and each pattern's width counts are spread over distinct calls within the group's window. Any feasible integer solution expands literally by bipartite edge colouring (Kőnig); the package's verifier re-admits the resulting map independently. For the all-jp8 dispatch the model is solved to optimality in seconds and equals its LP bound (objective Σ r·ln(73/r) = 1567516.8, against 1567517.6 for the LP, the difference being the solver's integer rounding of objective coefficients), so the integer map loses nothing against the LP. The one ck call is then added by a warm-started repair model (patterns of the all-jp8 solution plus single-item exchanges), which gives objective 1567825.3; this is a feasible solution, not proved optimal.
3. **Why one ck call.** The package audit checks every provider against a second provider (substitution controls) and requires at least two dispatched providers; a pure jp8 dispatch is rejected. The ck word is used because it shares the width-4 and width-5 counts of jp8 (switching one call from jp8 to ck changes only 12 fewer nines, 20 fewer eights and 32 more sevens), so the exchange is small. The cost of the ck call is about 0.02% of b. The atm3 word is no longer dispatched, so its build chain and recipe files are removed from the package; `verify.py` builds only ck and jp8.

For reference, the all-jp8 integer map priced with the same moment engine has native complex lower 0.001628331263669 (+0.02% above this package's 0.001628011347228). It is not packaged, because a one-provider dispatch is rejected by the audit.

## The cold-end construction (inherited from PR604; changes relative to PR601)

PR601 (jeremykothe2) dispatches three provider words: **ck**, **atm3** and **jp8**; PR604 and this package build on the same three words. In each word, 46 entering helpers per call end at a hyperplane. The mechanism comes from PR591, PR592 and PR601. The Lean side is Lemma A with an arbitrary terminal frame (PR593) and multi-gate tails (PR599).

The construction appends one typed build step, `cold_end`, to each provider chain (ck, atm3 and jp8 in PR604; this package builds ck and jp8), after `hyperplane_end`. In every call, 14 **cold** factory-scratch helpers end at a **4-dimensional frame U_b** instead of FULL, so their residual width drops from 9 to 4. These helpers are `S b.10`, one per factory block b: registers 234, 250, …, 442. The step has three parts.

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

The dispatch and the literal owner map were re-solved for the new widths in PR604 (`data/PLAN.json`, `data/OWNERS.json.gz`: annealing from PR601's map, then an exact pattern-restricted owner model warm-started from the annealed map). This package replaces them as described above. Every inherited window, family and capacity constraint is kept.

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

All LP figures below are first-order bounds. They come from the aggregate hosting LP (the whole-owner model on PR601's windows, objective Σ r·ln(73/r)), calibrated against exact moment-engine prices. On PR601's own dispatch and widths, the LP lies within 0.005% of PR601's literal map. One unit of the objective is worth about 6.4e-5 % of b.

| quantity | G = Σ r·ln(73/r) | gain over PR601 |
|---|---|---|
| PR604's map (fixed dispatch ck 44 / atm3 22 / jp8 6) | 1571748.9 | +0.439% |
| this package (jp8 71 / ck 1) | 1567825.3 | +0.692% (exact κ) |
| all-jp8 dispatch, integer optimum (= LP bound) | 1567516.8 | ≈ +0.71% |
| LP ceiling, free dispatch over {ck, atm3, jp8} cold | 1567420.3 | ≈ +0.72% |

The objective values in this table are CP-SAT objectives with rounded coefficients; the exact sums Σ r·ln(73/r) are about 0.5–0.8 higher (for the all-jp8 map, 1567517.62).

- **Remaining gap to the free-dispatch ceiling: about 0.026 pt of b (405 units of G).** About 0.020 pt (308 units) is the single ck call: a one-provider dispatch is rejected by the audit's substitution controls, and the repair model for that call was not run to optimality. About 0.006 pt (97 units) is the LP's preference for about 2.4 atm3 calls, which needs a third provider word and a dispatch that the integer model can absorb.
- **Time-refinability did not bind.** Adding per-pattern, one-helper-per-port-per-call constraints leaves the LP optimum unchanged: the LP vertex (113 non-zero pattern entries over the 72 classes of owner groups with equal rank and window) is already refinable. The gap that the annealed maps showed against the jp8-heavy ceiling was search, not structure. A free-dispatch integer model (dispatch as binary variables) did not converge in the time tried; the fixed-dispatch model with a repair step did.
- **Open choices.** Which call takes the second provider (stage 2 replica 5 was the best of three tried, 0, 30 and 71 in call order), whether atm3 is the better second provider, and whether the second provider can be placed on a call where the repair costs less than 308 units.
- **Cold units: maximal in a stated scope (separate analysis, not an admission dependency).** Within monotone frames, a rank-0 premix and a fixed forward word with 46 hyperplane-ended helpers, there are at most 14 dim-4 ends per provider word: 14 dim-4 classes, each of rank 1, none at dim 3. Each unit is forced: its cleanup vector is unique, and the cold helper `S b.10` in place beats the `S b.9` / `S b.13` pivots. After these units the dim-5 and dim-6 classes have no residual capacity. Entering ends are capped at 48; PR601 ships 46, and the two premixed entering pairs that would reach 48 are worth about +0.010% b on PR601's fixed dispatch (not re-priced on this dispatch, and not in this package, because their wrapper-order audit has not been run). Still open: extra ends at dim 7 or dim 8. Dim 7 was searched exhaustively and dim 8 was sampled (about 10,000 pairs per provider); no positive pair was found, but the CP-SAT bound did not close.
- **End dimension (first-order).** Raising a unit's end frame from dim 4 to dim d needs the last tail gate at that frame, which lifts one partner. This adds 2ψ(d−4) + ψ(9−d) − ψ(5) to the local cost per unit, where ψ(r) = r·ln(73/r). That is +6.8, +10.6, +13.0 and +14.1 for d = 5…8. The remaining hosting headroom is about 1–2 per unit, so d = 4 is the best end dimension for these units.
- **Necessary condition, for any cleanup factorisation.** A helper h can end at a frame U only if, at the end of B, the supports of its row in the inverse state map and of its dirt column both lie in Q_U, the registers whose end-of-B frames lie in U. The transport checks this condition for every low-frame end. Choosing which units satisfy it, through the premix, is the supply question. This package uses 14 units per word; the "Cold units" bullet above gives the scope in which that count is maximal.

### Future research: other provider words

The 14 dim-4 cold units are not specific to the three words used here. A cone/lattice census finds the same 14 classes on every other pre-hyperplane word tested from the PR567–PR588 lineage (PR569's width-7 and four-cold words, PR571's combined words, the jp8 intermediate words, the atm3 and ck kernel words); only PR569's 60-promotion width-7 word carries none, and no word carries more than 14. PR569's four-cold-eight word with 40 standard and 8 non-first hyperplane ends plus the 14 cold units replays exactly (21021 gates, compensation 8544) and has the profile and widths predicted from the 14-unit change. In the first-order LP, jp8 is the best single word in that lineage (G 1567517.6; PR569's four-cold-eight is 542 units worse, 0.034% of b). With every lineage word as a column, plus composite options (jp8 with partial multi-gate groups × 7-wide promotions × 12 kernels), the joint LP gains at most about 0.007–0.008% b over the three-word cold LP, and the best composite mixes jp8 with partial multi-gate and 7-wide promotions. Substituting jp8-like words into the ck slots of PR604's fixed dispatch gains about 0.12–0.13%, which the jp8-heavy dispatch here supersedes. Small levers estimated on PR604's fixed dispatch and not re-priced on this one: PR569's four-cold-eight with 40 width-4 promotions (about +0.064% b), the atm3 step-0 promotion (about +0.017%) and the combined72 word (about +0.009%). All are LP estimates; none is built or verified in this package. The lineage words are the work of their PR authors (Jeremy Kothe, Dominik Scholz, Jonathan Capalbo, Chafik Boukhalfa, as named in the pinned sources' history and NOTICE files).

## Verification

Fetch the pinned sources exactly as for PR601, then run:

```sh
research/complex-571-cold14/verify.sh /tmp/complex-571-cold14 ..
# kappa 0.00162536523418317
```

`verify.py` uses only the standard library and requires assertions. It runs these stages:

1. It checks the MANIFEST and every source, PLAN, OWNERS and recipe pin.
2. It replays PR558.
3. It rebuilds the two provider words (ck, jp8) through their typed chains. That is 11 steps, each with pinned input and output content hashes and paired controls.
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
  - PR604: the cold-end construction and the package this one is stacked on;
  - PR509 and PR516 (the Lemma A / Lemma G Lean line);
  - PR599 (multi-gate and cold hyperplane-end Lean);
  - PR484.
- The pinned PR568, PR569, PR571, PR575 and PR583 packages and their authors, as listed in NOTICE.md.

DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
