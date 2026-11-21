# CALLERWORD CW (Nov 20, Opus, Lean + exact checks)
Owner rule: only Wall56 may stay unproved. BRIDGE left the caller models (CallerSGram/RC2/HP) BLOCKED because Lean had no SPEC-level
multi-call caller object. Not a retread: BRIDGE bridged the per-call word to networks. This lane builds the OUTER caller object and bridges it.

## 1. SPEC caller object (source = data, not run)
The verifier's caller replay is `caller(C)` in imb-native research/shared-wire-split-composition/independent.py, plus the #7113 IDLE_ODD edit
(7113_signed_model.py: `pscale(row, q=e[4], m=D^S)`) and operator_ring.py validate (distinct HOST fields).
Rows R[r] live in Q(i)[q, D_1..D_k]/(q^4-1). The start is e_r. The verifier requires the exact end R[r] = q^(dg0) D^(mask r) e_r.
- Lean `CallerWord.CWord`: the primitive events are add, scale, swap, query σ, lam σ, idle S σ (IDLE_ONE: σ=0; IDLE_ODD: σ=e[4]), and host s t a b.
- A J record is macro-expanded in code order: `jA` = 2 HOSTs (x,y,0,1), (u,v,α2,0), then D_t on x,y,u,v; `jB` = HOST(s,t,a,b), then D_t on s,t. A D_t contact is literally `idle x {t} 0`.
- `Legal` = WF ∧ the endpoint identity for EVERY commutative ℚ-algebra S with q^4 = 1 and i^2 = -1. This is equivalent to the verifier's formal identity: the formal ring is one such S, and every such S receives an evaluation map.
- Mapping: stages = calls (J); roles = caller registers; masks = target D-masks; pieces = D-incidence events (IDLE sets incl. J contacts); thin = q-odd QUERY/IDLE_ODD.

## 2. Bridge theorems [P, Lean, kernel-only, axioms propext/Classical.choice/Quot.sound]
Files: lean/decoder-duality/Nov15/CallerWord.lean, CallerWordD.lean, CallerWordS.lean (oleans built).
- `stage_product` / `legal_frame`: every Legal word over ℂ is a CallerSGram frame.
  - One block per event; columns = nonzero q-odd slots.
  - A col = c·P1(j+1)^-1 e_x and B col = P1(j)^T e_y, where P1 = base prefix at q=1, D=1.
  - V_j = P1(j+1)^-1 X_j P1(j).
  - V_{N-1}..V_0 = diag((-1)^(ex r)); this is -I for odd targets (the #7113 family).
  - This is the Q-general stage-product identity: each HOST gives ≤ 2 columns, and each thin odd event gives 1.
- `role_count`: odd targets ⇒ rank K + n ≤ #columns and rank G = n (sgForward). So n ≤ 2k + Q (2 nonzero HOST coefficients per stage).
- `role_count_lam`: one nonzero 2x2 principal minor of K (λ ≠ -1) ⇒ n + 2 ≤ #columns, i.e. n ≤ 2k-2+Q.
- `linear_E1` (dual numbers, D_t0 = 1+ε): diag(1[t0 ∈ mask]) = Σ_incidences P1^-1 E_rr P1.
- `stage_incidence`: |{r : t0 ∈ mask r}| = #D_t0-incidences (J contacts + idle sets containing t0).
- `biorth`: W^T V = 1, with v_e = P1(e)^-1 e_r and w_e = P1(e)^T e_r. This is the y·x = δ law for pieces sharing a stage.
- `support_VW`: every v_e and w_e vanishes off E_t0.
- `host_cols` (generic) and `jB_cols` / `legal_jB_support` (J record of type B): every A and B row of a stage-t0 HOST column vanishes on roles with t0 ∉ mask. That is RC2/HP's hbh/hah with M = the caller's D-masks.
- Non-vacuity:
  - `toy_nonvac`: 2 roles, HOST + QUERY + 2 IDLE_ODD; 4 columns, sgProd = -1, rank G = 2.
  - `toy_masks` / `toy_inc_card`: |E_0| = 2 = #incidences.
  - `toy3_support`: a role outside the stage, with A and B rows 0.

## 3. #7113 data [C exact, cw1.py → cw1.log; controls cw1_controls.log]
Per type (A, B): the replay at q=±1, D=1 equals the target. n = 36 and there are 38 columns (34 HOST + 4 thin): Q = 4 for both types. ∏V = -I. rank G = 36 and rank K = 2, so n = 2k-2+Q is tight. The 2x2 minor hypothesis holds (B: all 17 stage blocks of K invertible).
Over 17 stages: stage incidence, W^T V = 1 and support have 0 violations. HOST-column support has 0 violations, type A's two-HOST J included. Each type has 4 degree-1 roles.
Controls:
- Dropping one B IDLE_ONE is caught on the D side (1 violation) and is invisible at q=±1, D=1, as the theory says.
- Setting one A QUERY to σ = 0 breaks q=-1 and ∏V, and leaves 37 columns.
- cw2.py → cw2.log (CP-SAT, 1 thread): a CONSISTENT piece attribution exists on #7113 for both types, even strict (v_e(r), w_e(r) ≠ 0). This holds although type B's register-index attribution is not a partition (QB §3). So #7113 B is a partition model under the right attribution.

## 4. Status per caller-model hypothesis
| hypothesis | status |
|---|---|
| stage product ∏V = -I (and the Q-general form with thin columns) | **bridged** [P Lean] (event-blocked frame) |
| regroup to Fin k × Fin 2 stage blocks (rc2_pair_sg/frame_bound shape) | not formalised. Type B is a reindex. Type A: cross term b_h2·a_h1 = δ_{v,y} = 0 for distinct fields [P paper] |
| role count n ≤ 2k+Q; n ≤ 2k-2+Q given λ ≠ -1 | **bridged** [P Lean] |
| role count EQUALITY n = 2k-2(+Q) | not derivable: design tightness (tight on #7113 [C]) |
| λ ≠ -1 (K_tt invertible) | **genuine branch restriction** (SK 7) |
| Q = 0 | **genuine branch restriction** (#7113 has Q = 4/type) |
| D ≥ 2 (SIGN1) | **genuine restriction** (#7113: 4 degree-1 roles/type) |
| masks = D-masks; frame supports ⊆ masks (hbh/hah) | **bridged** [P Lean] for jB; type-A J [C] |
| stage incidence (mask incidences = contacts + idle incidences) | **bridged** [P Lean] |
| MAINS (≥ 2 singleton contacts per stage) | count = J contacts per stage (schema: 2 for B, 4 for A), bridged as incidences; per-role main flags need the attribution |
| pieces x_supp / x_ker / biorth (CallerRC2.Pieces) | **derivable from v_e, w_e** (support_VW, biorth; x_ker = biorth against the stage's contacts) GIVEN an attribution; Lean assembly not done |
| consistent piece attribution (per-role partition; = LEANHP stage-form caveat) | **open** [CONJ in general]; exists on #7113 [C cw2] |

## 5. Next
1. Assemble CallerRC2.Pieces from (v_e, w_e) for a given attribution, and regroup into Fin k × Fin 2. Then CallerHP.frame_bound applies to legal words. Its only premises would be the branch hypotheses (Q = 0, λ ≠ -1, D ≥ 2), n-equality and an attribution.
2. Attribution existence: Hall-type argument from the invertible V_t|E_t blocks plus multi-stage events. Test on built frames C1/c33.

## 6. Round 2 (coordinator follow-up)
New Lean files, all kernel-only with std axioms and oleans built: CallerWordA.lean, CallerWordK.lean, CallerWordHP.lean.

### (3) Type-A two-HOST J support — DONE [P Lean]
`jA_cols` / `legal_jA_support` (CallerWordA.lean): the record is jA = HOST(x,y,0,1), HOST(u,v,α2,0), then IDLE {t} on x, y, u, v, with x, y, u, v distinct. Every frame column of either HOST vanishes on roles with t ∉ mask.
The key step: the first HOST's incidence vectors pass through H2 = 1 + α2 E_uv. Its explicit inverse (`host2_inv`) fixes e_x and e_y, and their rows.
So hbh/hah now hold with the D-masks for both J types of the #7113 schema.

### (2) Pieces assembly and regrouping — PARTIAL
- `jB_xker` [P Lean] (CallerWordK.lean): this is RC2's `x_ker` law. For any D_t0-incidence e other than the stage's two contacts, Σ_r v_e(r) B(r, p) = 0 on every HOST column p.
  - `host_rows` expresses the pre-HOST rows through the contacts' w-vectors; biorth then gives 0.
  - Combined with `support_VW` (= x_supp) and `biorth` (= Pieces.biorth for pieces sharing a stage), every analytic field of CallerRC2.Pieces is now derived. This holds once x = v_e and y = w_e are attached to (role, stage) by an attribution.
- NOT done in Lean (bookkeeping only):
  - (a) Building the `Pieces` record from an attribution function.
  - (b) Regrouping the event-blocked frame into Fin k × Fin 2 with β = stage. Inactive events have V_j = 1. Type A's two 1-column HOST blocks merge because b_h2·a_h1 = e_vᵀ e_y = 0 for distinct fields [P paper].
- Tightness: WLOG for the HP arithmetic, NOT (yet) for the RC2 input.
  - `total_le_le` / `frame_bound_le` (CallerWordHP.lean): KASYM's bound holds with n + 2 ≤ 2k in place of equality. Each role's dual budget is v2p = 17^s − 16^s > 0 (`v2p_pos`), so fewer roles only lower the total.
  - With role_count_lam this is exactly what a legal Q = 0 caller supplies.
  - RC2's hG (gBlk invertible) comes from sgG_blk_unit, which uses n + 2 = 2k: rank K ≤ m, then blk_unit. A non-tight frame has rank K ≤ 2k − n > 2, so hG is not derived there.
  - [CONJ] Padding a non-tight caller with roles of value ≥ 0 makes it tight without lowering ĉ. Not built.
- Branch hypotheses that remain: Q = 0, λ ≠ −1 (diag K blocks), D ≥ 2, tightness (RC2 side only).

### (1) Consistent piece attribution — OPEN (no proof, no counterexample)
- [P] Necessary structure:
  - (i) Per stage there is a bijection incidences → E_t with S_e ⊆ M_r, from invertibility of V_t|E_t.
  - (ii) Incidences sharing a stage are biorthogonal.
  - (iii) v_e lies in span{e_r : M_r ⊇ S_e}. This kills the obvious combinatorial counterexamples: two {1,2}-pieces would need two independent vectors in a 1-role span.
  - (iv) Expanding ∏(I + (D^{S_e} − 1) v_e w_eᵀ) = diag(D^{M_r}) in several variables kills products of pieces with S_e ∩ S_f ≠ ∅. The u^A coefficients give trace identities. Via a DVR / Littlewood–Richardson argument these yield only dominance conditions, which are weaker than an exact per-role partition.
- Why it matters: RC2's Pieces.biorth needs it ("r = r' ∧ pc equal ⇒ 1"). Per-stage bijections alone can give the same event two roles.
- [C] (cw2/cw3) A consistent attribution exists, both mask-only and strict (v_e(r), w_e(r) ≠ 0), on #7113 types A and B, on built C1 (k3) and on c33 (k6, 4 multi-stage pieces). Replay, stage incidence, biorth and support show 0 violations on all of them.
- Suggested escape: restate RC2 with pieces indexed by EVENTS instead of role instances (x = v_e, y = w_e, E(q) = support). Then no attribution is needed. Check whether rc2_avg's counting survives that change.
