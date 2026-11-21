# LEANDX (Nov 20) -- lean/decoder-duality/Nov15/LevelCutDX.lean: kernel-only, rc=0, no sorry; axioms [propext, choice, Quot.sound] (axioms.log)
Imports Nov15.LevelCutRelay (Cd, sum_Cd_le, NetW.relay_dim, Nmat, ind). Build: runlean.sh, ~10 s.

## (1) DX  [P, Lean]
- `Mstar G H F da db l` = G * (sum_{i<n} W_i^(state 2)) * F, W the 3-state automaton (0: no a>=l yet; 1: seen, not crossed; 2: crossed),
  state is a function of the walk prefix so each walk is counted once. Crossing at node j <=> some i<=j with da v_i >= l > db v_j.
- `dx_rank_le` : rank Mstar_l <= |C_l|. Proof: state-2 walks enter state 2 only at a node of C_l (uses relay rule db c <= da d), giving
  X2 = Nmat H * ind C * (...) (identity (1-H) X2 = ind C + sum_i Sinj_i, `Sinj` supported on C: `ind_Sinj`).
- `dx_D_ge` : sum_{l in L} rank Mstar_l <= sum_k (da k - db k);  `netw_dx_D_ge` : same for NetW (D).
- Non-vacuity `ToyDX.dx_gt_yc` (lwcx-type, gatherer a1/b0 -> hub a2/b1): sum_{l=1,2} rank M_l (YC, Mnode) = 0, sum rank Mstar_l = 2 <= D = 2 (tight).

## (2) zero-drop contraction  [P, Lean]
- `contract_core` (ring-level): P idempotent, P H P = 0, N=(1-H)^-1, N''=(1-H'')^-1 => N = T N'' U + P, with
  T=(1-P)+PH, U=(1-P)+HP, H''=(1-P)H(1-P)+HPH (P = ind {k}).
- `contract_identity` : G N F = cG N'' cF + G[.,k] F[k,.]  (exact, any strictly lower triangular H).
- `contractW N k (a_k <= b_k)` : a legal NetW (same n, a, b, c; relay rule, F/G rules, hM all re-proved); node k Dead (`contractW_dead`),
  dead nodes stay dead (`contractW_dead_keep`); `corr_odd`: the dropped term vanishes on odd cells, so M is unchanged on odd+diagonal cells.
- `exists_contracted` : iterate => no live node with a_k <= b_k. `contracted_live_le_D` : if all b_k <= a_k, same a,b,c, every live node has
  drop >= 1 and #live <= D = sum drop; so a counterexample to D>=56 (D<=55) has <= 55 live nodes.
- Non-vacuity `ToyContract.toy_contract` (3-chain, middle node a=b): contracted H'' legal, D=2 unchanged, G N F = 1 = G'' N'' F'' + 0.

## Gaps / honest notes for NG.md
1. Mstar is DEFINED by the automaton; "sum over crossing walks" is by construction, not a Lean theorem (no list-of-walks bijection, no M = M* + M_noncrossing, no Lean proof that M_l (YC) is a sub-sum of M*_l). DX > YC is shown only on the toy; no rank-comparison theorem is claimed (none is true in general without the walk identification).
2. NG's complement/clique-cut (rank M*_l >= omega_odd(...)) and DX-inv (mu_l) are NOT formalised.
3. Contraction hypothesis is the subspace inclusion a_k <= b_k (NG: a_k = b_k); NetW has no field b_k <= a_k, so "every live node has drop >= 1" needs the extra hypothesis hba : forall k, b k <= a k (natural: a chart contains its b). Without it ℕ-drop 0 and a_k incomparable-with-b_k nodes survive.
4. Contraction isolates the node (Dead) instead of deleting it (same n); "<= 55 nodes" is stated as #non-dead nodes <= D.
5. NetW non-vacuity toy impossible (hM ranges over all 104 labels); both toys are abstract (da/db/G/H/F).
