# DOUBLE56 D56 (Nov 20, Opus, theory + exact checks). Own code in this dir. venv python, 1 proc, threads=1.
Why not a retread: ORBITLP §3-4 stated the master form and Rado formula but had no lower-bound mechanism for rho_A + rho_B.
This lane dualises both maxima at once (Rado sets J, J') and shows where the 2-adic carry X must do the work.

VERDICT: the [CONJ] rho_A + rho_B >= 56 is NOT proved and NOT refuted. No counterexample in any family searched.
Proved: an ISOTROPIC-PAIR LEMMA that reduces the conjecture to one quantity (the rank of the tau-form), tight at E8.
Proved: the CLIQUE THEOREM (rho_A + rho_B >= n on any tau-trivial label set, e.g. the P104 frames).
Note: the conjecture implies m4(P104) >= 56, the open half-integer Wall56. So it is at least as hard as the six parked attacks.

## Setting
- Notation is as in ORBITLP §3. R_t = span{b_k o Q_t : t in D_k}; R'_s = span{a_k o Q_s : s in S_k}.
- By Rado: rho_B = min_J [dim V_J + n - |J|] with V_J = sum_{t in J} R_t. rho_A = min_J' [dim U_J' + n - |J'|] with U_J' = sum_{s in J'} R'_s.
- [C] rho is computed as the rank over GF(2^16) of a random choice (this is <= rho), together with a greedy Rado certificate (>= rho). On E8-56 the two agree.

## 1. ISOTROPIC-PAIR LEMMA [P] (any half-integer decoder, any number of rows, any label set)
Take any J, J'. Set Xs = F2^J ∩ U_J'^perp and Ys = F2^J' ∩ V_J^perp. Then:
 (a) x^T (I+X) y = 0 for all x in Xs, y in Ys.
 (b) x^T X y = sum_k tau(Q[x o a_k, y o b_k]). Each block Q[u,v] in this sum is an EVEN 0/1 matrix (all row and column sums even), and tau(M) = (entry sum of M)/2 mod 2.
 (c) With J, J' the Rado minimisers: rho_A + rho_B >= n - rank(X restricted to Xs x Ys).
Proof.
- (a) If w'_k[t] = 1 then t is in D_k, so row t of Y lies in R_t. So x^T Y y = sum_{t in J} x_t (Y_t . y) = 0, because y ⊥ V_J.
  Dually, column s of Z lies in R'_s, so x^T Z y = 0. Now use the HC identity I + X = Y + Z.
- (b) We have x^T X y = (x^T N y)/2 mod 2, and x^T N y = sum_k u_k^T Q v_k with u_k = x o a_k and v_k = y o b_k (as 0/1 integer vectors).
  Take s in supp v_k. Then s is in J' ∩ S_k, so a_k o Q_s lies in U_J'. Hence (Q u_k)_s = x . (a_k o Q_s) = 0 mod 2: the column sums are even. The row sums are even by the dual argument.
- (c) dim Xs >= |J| - dim U_J' and dim Ys >= |J'| - dim V_J. The pairing x^T y on Xs x Ys has rank >= dim Xs + dim Ys - n.
  By (a) this pairing equals x^T X y. So rank(X|) >= |J| + |J'| - dim U_J' - dim V_J - n = n - (rho_A + rho_B). ∎
- TIGHT AT E8 [C e8xy.py]: the minimisers are J = J' = all ports; U and V are 28-dim and mutually orthogonal (V ⊆ U^perp); dim Xs = dim Ys = 76; rank tau-form = 48 = 104 - 56; and (I+X) vanishes on Xs x Ys.
- [C lemmaA_chk.py] Checked on 4 more P104 decoders (E8 row subsets + random rows + completion): (a) holds and the bound holds.
- Contrast with the doubling bound rank(I+X): this lemma isolates exactly what X must contribute (rank of the tau-form on the Rado spaces).

## 2. CLIQUE THEOREM [P]
- Call Q tau-trivial if every even 0/1 submatrix of Q has entry sum = 0 mod 4.
- If Q is tau-trivial, then X vanishes on Xs x Ys, so rho_A + rho_B >= n for EVERY half-integer decoder (any rows).
- Which Q are tau-trivial [P]:
  - J_n: an even submatrix of J has |u|, |v| even, so its sum |u||v| = 0 mod 4.
  - I_n: an even submatrix of I is zero.
  - Direct sums of tau-trivial matrices (tau is additive over blocks).
- So on every P104 frame (Q = J_8) the master form gives >= 8: the clique floor, now as a master-form statement. It is tight (Hadamard pairs give 2 per 2-clique).
- [C clique_chk.py] Exhaustive check: J5, I5 and J3+J2 have 0 defects; the h = 3 star has 1 defect pair (u = v = all).
  300 random J_8 decoders: min rho sum = 8. SA on J_8: 8.
- P104 is NOT tau-trivial; the E8 decoder lives on the defect (rank 48 above).
  Restricting to frames cannot help: rho is a transversal rank, not additive over frames. Frame-local decoders give >= 13·8 = 104.

## 3. Searches for a counterexample [C]
- Linear decoders (W = R X, V = R Y over Z4):
  - The Z4 kernel of valid M is {0, 2v} (kerM.py), so the linear decoders are exactly the factorisations X Y^T = Gb (or Gb + 2v). E8-56 is one of them (linchk.py).
  - Random factorisations with m = 8..12 give rho = 36 + 36 = 72 = 2 dim(C*C), where C is the 9-dim label code; the a_k, b_k all lie in C.
  - All 168 transvection neighbours of E8-56 give 58 (= their cost). 150 split neighbours give 57..64. So E8-56 is a strict local minimum.
  - Annealing escapes to 70..72 and never goes below 56.
- E8-120 linear decoder: C = 72 = rho_A + rho_B (36 + 36). This is consistent with the analogous claim "rho = optimal cost".
- Asymmetric decoders (E8 row subsets + completion): rho_B goes down to 14, but rho_A = 104. No balanced decoder found.
- Small analogues (sa.py; star n=4, J4, J8, plus4 n=6, minus4 n=10): SA min rho = n everywhere, matching m4.
  CAVEAT: no symplectic port set below h = 9 has a sub-n decoder, so small cases cannot test 56-type tightness. They are not evidence.

## 4. What remains
- Wall56 (half-integer, any rows) <= [CONJ] rho_A + rho_B >= 56 <= [CONJ tau48]: at the Rado minimisers, rank(tau-form on Xs x Ys) <= 48 for every decoder of P104.
  tau48 is E8-tight. Its input is pure Q-structure: tau on even submatrices of the 13-frame graph, where cross-frame blocks have all row sums 4 and F2 rank 2-4.
- A proof of tau48 needs an upper bound on the tau-defect of P104. A suggested route: write Q = (J + S)/2 with S the symplectic character matrix (-1)^{B(p,q)}. Then tau(u,v) = (|u||v| + 1_u^T S 1_v)/4 mod 2, so tau48 becomes a statement about S restricted to the Rado spaces.
- Full-integer decoders: already >= n (ADICWALL, e = 0). Denominators > 2: the mod-4 reduction and this lemma do not apply; that would need a mod-8 analogue (three-level carries).
FILES: rho.py (rho via GF(2^16) + Rado), e8rho.py, e8xy.py / e8xy_lib.py, e8schur.py, clique_chk.py, lemmaA_chk.py, kerM.py, linchk.py, lin.py, nbr.py, anneal.py, e120.py, sa.py, frames13.py, verify.sh.
