# LINEAR56 (Nov 20, Opus, theory + exact finite checks). Own code in this dir. venv python, <= 2 procs, threads=1.
Why not a retread: DOUBLE56/TAU48/ARF only searched linear decoders (0 counterexamples) and left "f >= 56 inside R2" open.
This lane proves the wall for the whole linear class (any number of rows), in two independent ways, and works out the geometry.

VERDICT (LOUD, but modest): for EVERY half-integer LINEAR decoder of P104 (W = C X, V = C Y over Z4, any m):
  (A) C >= 56, and C = 56 only for the fully tight 8-row decoders (E8-56 type) [P + C];
  (B) rho_A >= 28 and rho_B >= 28, so rho_A + rho_B >= 56: the DOUBLE56 rho-conjecture holds on this class [P + C].
The [C] inputs are two exact finite facts: Kbar = B is forced, and every hyperplane section of P104 spans. Both are listed below.
Caveat (be honest): (A) uses the same mechanism as WALLQ96 Lemma A (rank-8 factors => price >= 7) and PRICE7's reduction
(C <= 55 needs a row of price <= 6). Linear rows never have price <= 6, so the linear class was never where the danger is.
Any Wall56 counterexample must use NON-linear rows whose support on one side spans a codim-2 subspace of F2^9.
f >= 56 (tau48 at J = all) on the linear class: NOT proved. [C] evidence only (§5).

## 0. Coordinates [P + C]
- C120 = integral E8 root coordinates (e8base.json); rows 0..103 = P104, rows 104..119 = Z16, the 16 REMOVED root lines. G = E8 Gram, B = G mod 2 (symplectic).
- [C] Q[s,t] = 1 + B(c_s,c_t) for s != t (Q = J + B). q(c) = 1 on all 120 points.
  So Q = H beta H^T with h_t = (1, cbar_t) in F2^9 and beta = 1 (+) B nondegenerate.
- R1 = affine functions on F2^8 (9-dim). R2 = P0 := polys of degree <= 2 with zero constant (36-dim; [C] injective on the 104 labels; the relation is q = 1).
  Lin = linear functions (8-dim) = kernel of the quad-part map pi: P0 -> Lambda^2 (28-dim).
- [P] PAIRING = REMOVED-POINT EVALUATION: for f, g in R2, sum_{t in P104} f g = sum_{z in Z16} f(z) g(z).
  Proof: sum over all 120 nonsingular points = sum_{x in F2^8} q(x) f(x) g(x) = 0 because deg(q f g) <= 6 < 8. [C] Equal Gram matrices. ev_Z16(P0) has rank 14 and the pairing has rank 12 (ARF's 12/24 split explained).
  So on P120, R2 is totally isotropic; deleting points is what creates pairing.
- [C] Z16 has linear rank 8 and affine rank 7 (it lies in a hyperplane lambda = 1). Its B-graph is the 4-cube Q4.

## 1. Decoder law [C kcoset.py]
- Z4 solutions K of c_t^T K c_s = 2 delta_ts (mod 4) on odd cells: exactly {G, G+2B}. The mod-2 kernel is {0, B} and Kbar = 0 does not lift.
  Hence Kbar = B, of rank 8, is FORCED. The same holds for affine-linear decoders (9x9 K, h_t = (1,c_t)): Kbar = 0 (+) B.
  P120: also Kbar = B (p120.py).
- [P] Kbar != 0 by hand: if K = 2K', then K' restricted to a frame would have Gram matrix I_8 on 8 labels spanning <= 4 dims.
- Rows: x_k, y_k in Z4^8. q_k = B^-1 xbar_k and p_k = B^-1 ybar_k (points). a_k(t) = B(q_k,c_t). Rank rows: xbar_k, ybar_k != 0.
  The law mod 2 is sum_rank q_k p_k^T = B^-1, so there are >= 8 rank rows.

## 2. Tight vs loose, and the exact linear-row price [P + C]
- [C] The Z4 vectors x (xbar != 0) with c_t.x != 2 mod 4 on all of P104 are exactly 32 = ±(tight lift) over 16 classes.
  These are q = z in Z16: the functional <., z> of a REMOVED root z, which takes the value ±2 only at ±z. On P120 there are 0 tight vectors.
- [C rowbound.py] Every one of the 510 affine hyperplane sections of P104 spans (homogenised) a hyperplane of F2^9.
  So Aff(D_k) = Aff_0(q_k) (8-dim) for a tight side and R1 (9-dim) for a loose side. Rows with x = 2e also give a hyperplane.
- [P] price_k = rank beta(H(D_k), H(S_k)). For a rank row:
  price = 8 - B(q_k,p_k) (tight/tight), 8 (one side loose), 9 (both loose). Every row active on both sides (mod 4) costs >= 7. [C] min = 7 over all 255^2 linear and affine row pairs.
- THEOREM A [P + C]: C >= sum over rank rows of (7 + #loose sides + [tight/tight and B(q,p)=0]) >= 7 * 8 = 56.
  EQUALITY: exactly 8 active rows, all tight on both sides, with q's and p's B-dual bases INSIDE Z16. [C m8tight.py] Z16 = {q} ⊔ {p}.
  There are 8 such (subset, K) choices for each K. Port-general: C_lin(P120) = 72 exactly: no tight sides gives 9 × 8, attained by E8-120 [P + C].

## 3. THEOREM B: rho_A, rho_B >= 28 for every linear decoder [P; inputs: Kbar invertible, P0 injective on labels]
- rho_B = transversal rank of {R_t}, R_t ∋ b_k o Q_t for every k with a_k(t) = 1, i.e. k in K_t := {k : B(q_k,c_t) = 1}.
  The quad part of b_k o Q_t is c_t ^ p_k. Projection can only lower transversal rank, so rho_B >= trank{ W_t }, with W_t = c_t ^ P_t^I and P_t^I = span{p_k : k in I ∩ K_t}.
- Choice of I: M = (B(q_j,p_k)) = A C with C A = B^-1 Kbar^T invertible. By Cauchy-Binet some 8-set I has det M_I = 1, so q_I and p_I are bases.
- ORDERING LEMMA GL [P]: every invertible M has a simultaneous ordering with rank M[1..k-1, 1..k] = k-1 for all k.
  Proof: induct on n. Pick the last index so that the other rows are independent; the principal submatrix keeps rank >= n-2.
  In such an order there is no nonzero alternating L with LM strictly upper triangular.
  Proof: downward induction. L e_k vanishes on span{m_1..m_k, e_k..e_n} = F2^n. [C glcheck.py: 600/600; lmtest.py: exhaustive n <= 4]
- RADO STEP [P]: let Omega be a d-dim space of alternating forms. Port t is good if omega(c_t, p_k) = 0 for all omega in Omega and all k in I ∩ K_t.
  G_Omega = span{ B(q_k,.) * omega(., p_k) : k in I, omega in Omega } vanishes on the good ports, so #bad >= dim G_Omega.
  Filtration Omega^(j) = {omega : omega(., p_i) = 0 for i <= j} (order from GL). The pieces B(q_j,.) * Lambda_j have total dimension d.
  A relation among the pieces gives an alternating L with LM_I strictly upper, so L = 0 and the sum is direct. So dim G_Omega >= d.
  Hence for every J: dim sum_{t in J} W_t >= |J| - 76. So trank = 28 and rho_B >= 28. rho_A is the same with q and p swapped.
- [C] Consistent with the data: 8-row tight-A family rho_B = 28, rho_A = 28..36, rho_A + rho_B = C (m8rho.py).
  60 random mod-2 decompositions, m = 8..16: quad transversal rank 28 (quadtr.py).
  The single-omega shortcut is FALSE (E8: one omega has 82 good ports, wht.c). The full filtration is needed.
- Consequence: C >= rho_A + rho_B >= 56 (doubling lemma), a second proof of Theorem A.
  rho_A + rho_B >= 56 needs NO section-spanning; it uses only Kbar invertible.

## 4. Port-general version
- Symplectic port sets: labels are points c_t of (F2^{2g}, B), Q[s,t] = 1 + B(c_s,c_t), Q_tt = 1. Linear decoders = Z4-linear in an integral lift.
  R1 = affine functions (2g+1). R2 = deg <= 2 polys mod the label relations.
  Pairing on R2 = evaluation on the complement inside any ambient set over which sum(q f g) = 0 (needs deg < 2g, i.e. 2g >= 7).
- [P] If Kbar has F2-rank 2g (forced) and P0 is injective on the labels: rho_A, rho_B >= C(2g,2), so C_lin >= 2g(2g-1).
  If every hyperplane section spans: C_lin >= sum over rank rows of (2g-1 + looseness).
  Tight sides need functionals with no value 2 on P. For E8-type P these are exactly the removed roots.
  So C_lin = 2g(2g-1) iff the removed set holds two B-dual bases (with the Z4 condition).
- P104 (g = 4): 56, tight. P120: 56 (rho) / 72 (exact C). Q96: >= 56; WALLQ96's 56-control lives on the P104 kernel lines.

## 5. f = dimU + dimV - rank<U,V> (tau48 at J = all) on linear decoders: NOT proved, no counterexample
- [P] U, V ⊆ R2. pi(U) = Lambda^2 because the q's span, so dim U = 28 + dim(U ∩ Lin) >= 28 (same for V).
  [P] f >= 56 <=> rank<U,V>_Z16 <= dim(U∩Lin) + dim(V∩Lin). This holds automatically when the right side is >= 12 (pairing rank <= 12).
  So a counterexample needs at most 11 loose-side dimensions in total.
- [P] Mechanism of tightness: fully tight 8-row decoders have U = Ann_P0(p's) and V = Ann_P0(q's). Z16 = {q} ⊔ {p} gives f·g = 0 pointwise on Z16.
- [C m8tight.py, exhaustive] All 8-row decoders with tight A side (2 × 8008 subsets): min f = 56. f = 56 for >= 2 loose B rows; nt = 1/0 give 57/58.
  Real-decoder annealing (realsa.py, 4 runs, 52k steps, exact moves preserving XY^T over Z4) and the mod-2 relaxation (relax_sa.py) never go below 56.
  These samplers are weak (they drift to 60).

## Next
- The linear class is closed for C and rho. Any remaining Wall56 counterexample needs non-linear rows of price <= 6.
  Theorem B's machinery (quad projection + ordering lemma + Rado) only needs the A-support to contain a hyperplane section.
  Try "D_k ⊇ a hyperplane section on at least one side" as the next class.
- f >= 56 on the linear class: reduce to the bipartite (q,p) row graph (U = sum ℓ_q A_q, A_q = Aff_0(p) iff q has a unique partner p in Z16) and an exact search on it.
FILES: lcore.py (geometry, U/V, f, cost), rowbound.py, kcoset.py, p120.py, m8tight.py, m8rho.py, relax.py, relax_sa.py, realsa.py, quadtr.py,
whtin.py + wht.c (single-omega counter), gtest.py, lmtest.py, glcheck.py, tightX.npy, logs sa*/rsa*.
