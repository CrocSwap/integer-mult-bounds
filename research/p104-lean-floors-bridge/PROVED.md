# What is proved (Lean only)

Authors: DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Nothing here is a κ claim.
Every theorem below is kernel-checked in `lean/` (no `sorry`, no `axiom` declaration; axioms for every kernel-only file are
within {propext, Classical.choice, Quot.sound}, see CHECK.txt). Only `lean/native/` uses `Lean.ofReduceBool`.
"Input" means the Lean statement takes it as a hypothesis or as data; Lean proves nothing about it.

## 1. Lemma PG (`LemmaPG.lemmaPG`, `char_two_counterexample`)
K any field with 2 ≠ 0; V = E × F × W, dim E = dim F = 2, W any finite dimension; w ∈ End F with det w = 1;
T₊ = (−I_E) ⊕ w ⊕ I_W, T₋ = (−I_E) ⊕ (−w) ⊕ I_W. If rank(X − I), rank(X − T₊), rank(X − T₋) are all ≤ 2, then X² = I.
2 ≠ 0 is necessary: in characteristic 2, w = 1, W = K, X = I − (projection onto W) satisfy the hypotheses with X² ≠ I.

## 2. Core kill of the 546 outer words (`R25Kill.kill_outer`, `n_words`)
Model: pinned d = 2 core, two blocks E, F of dimension 2, δ an involution with det −1, s a reflection, at most 2 units in each of the
μ1 and μ2 products; field with 2 ≠ 0. A word that is outer at μ1 or μ2 gives False (`kill_mu1`, `kill_mu2`, `kill_outer`; uses LemmaPG).
`n_words` counts 630 = 84 middle + 546 outer by `decide`. **Not covered:** the 84 middle words, and the reduction from a general
realisation to this core (outside Lean).

## 3. Class-K floor: 780 paid helper stops = 1,081.31 D0 per call
Class K: the kept stream of the word is fixed (mains, hosted/owned moves, INIT/CLEAR, finals, kept ρ-rows at kept events); helpers are free,
including fresh frames; helper moves strictly ascend (dim strictly monotone on the chart order). The floor bounds the helper layer only,
and says nothing about words outside K.
- `FloorCert.cost_ge_real`, `stops_ge_780`: for every x ≥ 0 with A x ≥ b (892 × 18,868 support sub-LP) and cᵀx ≤ #paid stays, 780 ≤ #stays
  and total cost ≥ 780 · 2 ln 2. The dual (y = Y/8) is checked by kernel `decide` (FloorCertData/Check). Input: the rows A, b, c as data.
- `NativeFeas.floor_le_native`: the native's own point is feasible for all 892 rows with cᵀx = 1,964 (full LP 1,999), so 780 ≤ 1,964 ≤ 3,432. Input: the point as data.
- `FloorEndToEnd` (class-K counts, R1/F4/R3 rows, hd/fibre sums on a multi-chart op model with the verifier's legality) and `FloorGlue`/`Floor`
  derive hOnce, class N, hP, hvec from the model.
- `FloorD0.floor_D0_classK`: every class-K word has helper D0 ≥ 780 · 2 ln 2 ≥ 1,081.309 D0 per call. **H2 (extraction: the exported
  rows are the family instances with D₀, ranks, ψ certificates, type-A flags) is the only hypothesis** beyond the model. The per-stay cost κ = 2 ln 2
  is proved (`helperD0_ge`, f convex, f0 = 0).
- Scale: the native's helper D0 is about 9× the class-K floor.

## 4. V2 relay-model floor and the bridge to helper D0
Files: V2FloorBound, V2FloorCert, V2FloorCost, V2FloorData, V2FloorDefs_*, V2FloorChk_* (kernel slices), V2FloorFinal, V2Bridge, V2BridgeFinal (all kernel-only);
native/V2FloorNativeJoint (opt-in, uses `native_decide`).

**Units.** JB = the relaxed relay model: plans E of strict containments of subspaces of F₂⁹ (dims 1..8), priced by wcut θ (S2 edge cost plus line/hyperplane B1 terms).
JB numbers are values of that LP model. They bound helper D0 only through the bridge below, with the stated hypotheses.

**(a) The only unconditional helper-D0 floor** is class K's `FloorD0.floor_D0_classK`: 1,081.31 per call (780 · 2 ln 2), under the model and hypothesis H2 of section 3.
Nothing in this section is unconditional in that sense.

**(b) JB certificates and what they bound.**
- `V2FloorFinal.floor_joint` / `floor_beta`: for every plan E realising all forced pairs of the certificate data, the certified numerator sum / 2^30 ≤ cost_θ(E),
  given `IntFeasible` (the per-edge dual inequality over all subspaces). Joint: 1,839,727,178,682 / 2^30 = 1,713.38 (θ = 22257/2^19). β (θ = 1): 1,536,575,200,417 / 2^30 = 1,431.05.
- `V2Bridge.bridge` (every accepted word, any θ in [0,1]): JB_θ(relay E_W) ≤ helperD0 + Σ_h corr_θ(dim ini h, dim fin h). E_W = distinct (ι tail, ι head) of the helper MOVEs, ι strictly monotone with fdim ∘ ι = dim.
- `V2Bridge.bridge_0V`: if every helper is born at dim 0 and ends at dim 9, then JB_θ(relay E_W) ≤ helperD0 (the correction vanishes).
- `V2Bridge.bridge_beta_V` (θ = 1, helpers end at V, any birth dim): JB_β(E_W) ≤ helperD0 + B1 · #(line-born helpers).
- Composed (`V2BridgeFinal`):
  - `v2floor_helperD0_joint`: 1,713.38 ≤ helperD0 + Σ_h corr_θ. `v2floor_helperD0_beta`: 1,431.05 ≤ helperD0 + Σ_h corr_1.
  - `v2floor_helperD0_joint_0V`: 1,713.38 ≤ helperD0 when every helper is born at dim 0 and ends at dim 9.
  - `v2floor_helperD0_beta_V`: 1,431.05 ≤ helperD0 + B1 · #(line-born helpers), helpers ending at V.
- Exact hypotheses of the composed theorems:
  1. `IntFeasible` for the certificate. Joint: discharged by `native/V2FloorNativeJoint.v2floor_joint_native`, which depends on `native_decide` (axiom `Lean.ofReduceBool`
     via `native_check_joint._native.native_decide.ax_1_1`). β: see CHECK.txt (native/ status). No kernel-only discharge is staged.
  2. `hreal`: the helper relay realises every forced pair (`V2FloorCert.Reach` on `relayE`). A named data hypothesis (r7-taint extraction, like H2). It is not a consequence of class K.
  3. `Accepted Pub H ini w` and the chart map (ι, dim); for the _0V / _V variants, the born/end conditions above.
- Without the _0V condition the correction is not small: on the #7623 native, Σ corr is about 1,414 (joint) and 1,403 (β) against helperD0 = 9,946.29, since 484 of 1,100 helpers are not {0}→V.
  (Numbers from a computation outside Lean.)

**(c) Free-endpoint relaxation has value 0 (proved on paper, no Lean theorem).** If helpers may be born and die at any charts, each forced pair (L_p, U_p) is bought by a one-move helper
L_p → U_p, with D0 = f(dU−dL) − f(dU−dL) = 0 and Reach holding trivially; the dual y = 0 is feasible, so the relaxation's value is exactly 0 (joint and β).
Consequence: a pair-realisation floor cannot force any stay, and D0 > 0 needs an extra constraint such as H2. The one-move witness is checked on all 2,625 pairs outside Lean (L_p ⊊ U_p).
The collapse statement itself is not a Lean theorem; the only formalised part is the per-helper identity D0 = Σ w0 − w0(d0,e) inside V2Bridge.

**(d) Scale.** In the relaxed JB model on the full lattice, the LP optimum lies between the certified 1,990.45 and about 3,127 (a pool primal bound); the native's own value is 3,791.5.
These are JB units, not helper D0 (native helper D0 is 9,946.29); see (b) for when JB bounds D0.

**Kernel-only cover (pending).** A kernel-only discharge of `IntFeasible` (V2FloorKernel*, hyperplane cover, `decide +kernel`) is built by a separate lane and is listed in CHECK.txt only if compiled.

## 5. Rebuild laws (TokenCancel op model: born/init/move/add/scale/clear/copy, any field)
- `RankLaw.rank_law`: legal run, SCALE factors ≠ 0, start rows span their tokens, non-V registers end on target, targets span the final tokens,
  U ⊇ V targets, U ⊓ span(non-V targets) = 0 ⇒ (V mix exists ⇔ no lossy CLEAR/COPY ∧ every V-ender end row ∈ U). `RankLawC.rank_law_proj`
  drops the last hypothesis (adds zero (U ⊓ N)-component and B ⊓ N ≤ A); `rank_law_indep` when B ⊓ N = 0.
- `HubSettle.prefix_valid`, `prefix_formula`: given one valid prefix and [R_n0; U0] spanning K^{G0}, every M with R_n0·M = F_n0, U0·M = G·V0, G invertible is valid
  (gauge is all of GL_n). `solve_inGL` is the "if" direction of the GL(A) criterion.
- `Gauge.run_gauge`, `valid_gauge(_A)`, `forest_gauge`: gauges changing only at SCALE/INIT/CLEAR commute with the run.
- `SwapWord.inject`, `inject_col`, `absorb`: with h = e_h at the injection point, injecting changes final rows only by multiples of e_h; absorbed if
  X0[G1] ⊆ B, e_h ∈ B, B ⊓ N = ⊥ (data facts, input).
- `DescentPrice` (abstract invoice model): `helper_price`, `owned_price`, telescoping identities.

## 6. Support lemmas imported by the above
ExportLaw (E1, E2, T4*; class N, ρ/π kill tokens; T4_card also needs hOnce), TokenCancel, JunkLB2 (T4_departer, T4_stop_cost), TokenRank, DepartD1, YRelay, DiffChain, SYLEQ.
Each file's .md states its model and exact hypotheses. Statements refuted along the way are in FALSE.md.
