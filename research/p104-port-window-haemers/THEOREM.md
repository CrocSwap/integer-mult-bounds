# Proof note: port windows are a fractional Haemers bound, and w >= 53/6 on P104 (no kappa)

Tags: **[P]** hand proof, written out below; **[C]** exact computation reproduced by `check.py` or `check_sat.py` (one PASS line per claim); **[P+C]** both; **[R]** a solver run recorded in `data/sat_results.json`, not repeated by the checks. No kappa claim and no word are made here. No human has reviewed the proofs; their status is stated in section 8.

## 0. Setting and definitions

**Ports.** P120 is the set of the 120 vectors of F_2^9 of weight 3 mod 4. P104 is the 104-port set of `data/ports_p104.json` (a subset of P120: 70 ports of weight 3 and 34 of weight 7) [C]. The 16 vectors of P120 outside P104 are two odd 8-cliques; **P112** is P104 together with one of them (the two choices behave identically in every count below) [C]. Write dot(a,b) for the F_2 dot product; dot(a,a) = 1 for every port, because the weight is odd. Two distinct ports are **orthogonal** if dot = 0 and **adjacent** if dot = 1. The **odd graph** G(V) of a port set V has vertex set V and an edge for each adjacent pair. G(P104) is 55-regular and G(P120) is 63-regular [C].

**Block pattern, window.** Fix a field F and an integer k >= 1. A *k-block pattern* on V is a matrix B over F, with rows and columns indexed by V x [k], whose k x k blocks satisfy

- B_TT is invertible for every T in V, and
- B_ST = 0 and B_TS = 0 for all orthogonal pairs S != T (the mask).

B need not be symmetric. Put w_k(V;F) = min rank(B)/k over k-block patterns and **w(V;F) = inf_k w_k(V;F)**, the *window* of V.

**Quoted definition [BC, Section 2].** For a graph G and a field F, a matrix M over F indexed by V x [d] is a *d-representation* of G if M_vv = I_d for all v and M_uv = M_vu = O_d whenever uv is not an edge. The fractional Haemers bound is H_f(G;F) = inf { rank(M)/d : M a d-representation, d a positive integer }. For d = 1 this is Haemers' bound H(G;F), the least rank of a matrix with unit diagonal that vanishes on non-edges [H79]. H_f is attributed to Blasiak's thesis (Section 2.2) in [BC]; the thesis was not consulted here. [BC, Theorem 1] (first proved in the thesis, per [BC]): Theta(G) <= H_f(G;F) <= H(G;F), where Theta is the Shannon capacity; also alpha(G) <= Theta(G) for the independence number alpha. [BC, Section 2.1] gives equivalent forms, one of which, with pairs (A_v, B_v) of n x d matrices, A_v^T B_v = I_d and A_u^T B_v = A_v^T B_u = 0 for uv a non-edge, is the factorisation B = W U^T used below with n the inner dimension.

**Theorem 1 (identification) [P].** For every port set V and field F: w_k(V;F) is the minimum of rank(M)/k over k-representations M of G(V), and **w(V;F) = H_f(G(V);F)**. Consequently alpha(G(V)) <= w(V;F) <= w_k(V;F) <= H(G(V);F) for every k, and w_{kl} <= w_k.

*Proof.* Let B be a k-block pattern and D the block diagonal matrix with blocks B_TT^-1. Then DB has identity diagonal blocks, the same zero blocks (it only combines rows inside a block row) and the same rank. So the minimum over k-block patterns equals the minimum over those with B_TT = I_k, which are exactly the k-representations of G(V): non-edges of G(V) are the orthogonal pairs. This gives the first statement, and taking the infimum over k gives the second. The inequalities are [BC, Theorem 1] plus w_k <= w_1 = H, since B tensor I_l is a kl-block pattern of rank l rank(B), so w_{kl} <= w_k. ∎

The window in Theorem 1 is *defined* by the block mask. Whether a particular physical construction realises a k-block window with exactly this mask for k > 1 is not derived in this note.

**Factorisation.** A matrix B with a k-block pattern has a full-rank factorisation B = W U^T with W, U of size kV x r, r = rank B. Write W_S, U_S in F^{k x r} for the block rows, so B_ST = W_S U_T^T. If B_vv = I for all v, then for v in V, W_v U_v^T = I_k.

## 1. Theorem 2: the values

**Theorem 2.**

1. **(P104, any field.)** For every field F and every k >= 1, every k-block pattern on P104 has rank >= ceil(53k/6) = 8k + ceil(5k/6). Hence **w(P104;F) >= 53/6 = 8.8333...**, and rank(B) >= 9k for k = 1, ..., 5 (the floors for k = 1..5 are 9, 18, 27, 36, 45). In particular there is no k = 2 pattern of rank 17, no k = 3 pattern of rank 26 and no k = 4 pattern of rank 34 or 35, over any field.
2. **(P112 and P120.)** For every field and every k, rank(B) >= 9k. In characteristic 2 the Gram matrix (dot(S,T)) has rank 9 and is a 1-block pattern, so **w(P112;F) = w(P120;F) = 9 exactly when char F = 2**, attained at k = 1.
3. **(Characteristic 2, upper bound.)** w(P104;F) <= 9 when char F = 2.
4. **(Odd characteristic.)** If char F != 2: **w(P104;F) >= 13**, w(P112;F) >= 14 and w(P120;F) >= 15. So the bound 9 of item 3 does not hold outside characteristic 2.
5. **(Open.)** For P104 in characteristic 2: 53/6 <= w <= 9. Whether w < 9 is not decided here. The first k for which the floor ceil(53k/6) of item 1 is below 9k is **k = 6, rank 53** (53 < 54); for k = 6, ..., 12 the floor is 53, 62, 71, 80, 89, 98, 106 [C].

Item 1 is Theorem 3 with the weights of section 2; item 2 is Theorem 3 on the other two systems and the Gram matrix; item 3 is the same Gram matrix restricted to P104 (a principal submatrix, so w is monotone under taking port subsets); item 4 is Theorem 4. The Gram matrices of P104, P112 and P120 over F_2 have unit diagonal, zeros on orthogonal pairs and rank 9 [C].

## 2. Theorem 3: the weighted star bound [P+C]

**Structure relative to an orthogonal 8-set.** Let K be a set of 8 pairwise orthogonal ports (they exist in all three systems; the largest orthogonal set has 8 ports, there are 1728, 4032 and 8640 of them in P104, P112, P120) [C]. Put v = 1 + sum(K) (all-ones vector plus the sum of K). Then dot(v,c) = 0 for c in K and dot(v,v) = 1, so K together with v is an orthonormal basis of F_2^9. Every port t is therefore t = sum over c in A of c, plus eps v, with A = A(t) = {c in K : dot(t,c) = 1} and eps = dot(t,v); and 1 = dot(t,t) = |A| + eps (mod 2). Call t outside K an **edge port** if |A(t)| = 2, and let Gamma(K) be the graph on K with one edge for each edge port, joining its two K-neighbours. Let E be the number of edge ports and d_c the degree of c in Gamma(K).

- **(H1)** Distinct edge ports have distinct pairs: the pair A fixes eps = 1 (|A| + eps odd), and t is determined by (A, eps). So Gamma(K) is a simple graph.
- **(H2)** Two edge ports t = c + d + v and t' = c + e + v sharing exactly one vertex c are orthogonal: dot(t,t') = dot(c,c) + dot(v,v) = 1 + 1 = 0.

Both are proofs for any port set of odd-weight vectors. They are also recorded as counted facts on every orthogonal 8-set of the three systems [C]. (Two edge ports with disjoint pairs are adjacent, dot = 1; not used.)

**Counts [C].** On the 1728 orthogonal 8-sets of P104, (E; degrees d_c) is (22; 5,5,5,5,6,6,6,6) for **960**, (22; 5,5,5,5,5,6,6,7) for 384 and (21; 5,5,5,5,5,5,6,6) for 384. On P112: (25; 6,6,6,6,6,6,7,7) for 3584 and (24; 6^8) for 448 sets (for each of the two choices). On P120: (28; 7^8) for all 8640. In P120 relative to K the ports have 1, 2, 5 or 6 odd K-neighbours, 8 + 28 + 56 + 28 of them.

**Theorem 3.** Let V be one of P104, P112, P120 (more generally any port set of odd weight vectors), K an orthogonal 8-set in V with every K-vertex of degree >= 1 in Gamma(K) (otherwise delete it from the sums below; nothing changes), and a_c >= 0 weights on K with

 (W1) a_c + a_d <= 1 for every edge cd of Gamma(K), and (W2) a_c (d_c - 2) <= 2 for every c in K.

Put mu = sum over c in K of (1 + a_c) and rho = sum over edges cd of (1 - a_c - a_d). Then for every field F, every k and every k-block pattern B on V, writing rank B = 8k + j:

 **j/k >= (E - mu) / (mu + rho).**

**Values [C].** With a_c = 1/2 for all c (then rho = 0, mu = 12, and (W2) says d_c <= 6): P104, type (22; 5^4 6^4): **j/k >= 10/12 = 5/6**, so rank >= 8k + 5k/6 = 53k/6. With weights 1/2 on degrees 5 and 6 and 2/5 on degree 7: (22; 5,5,5,5,5,6,6,7) gives 101/126 and (21; 5^6,6,6) gives 3/4; P112 types give 1 (both types) and P120 (weight 2/5 everywhere, mu = 56/5, rho = 28/5) gives 1. The check recomputes each from the enumerated K, verifies (W1) and (W2), and also finds that no choice of weights from the multiples of 1/30, constant on degree classes, does better. Controls [C]: weights 1/2 on P120 violate (W2) and would give 4/3, above the value 1 that the rank-9 Gram representation attains; weights 3/5 violate (W1). The weights here are from a grid; no claim is made that they are optimal.

*Proof.* **Step 0: gauge.** Left-multiplying block rows by B_vv^-1 (as in Theorem 1) we may take B_vv = I_k for all v. Factor B = W U^T with r = rank B inner dimension. The ports of K have W_K U_K^T = I_{8k}, so W_K and U_K have rank 8k and r = 8k + j with j >= 0. Choose g in GL_r with W_K g = [I_{8k} 0]; then (U_K g^-T) = [I_{8k} Z] because (W g)(U g^-T)^T = I. Replace g by g h with h = [[I, 0], [Z^T, I]]: W_K stays [I 0] and U_K becomes [I 0]. So **W_K = U_K = [I_{8k} 0]**; call the first 8k coordinates the K-blocks (k coordinates per c in K) and the last j coordinates x.

For an edge port T with A(T) = {c, d} and c' in K, c' not in {c, d}: T is orthogonal to c', so the mask gives B_{c'T} = W_{c'} U_T^T = U_T[c']^T = 0 and B_{Tc'} = W_T[c'] = 0. So **W_T, U_T are supported on the blocks c, d and on x.**

Notation for an edge port T = cd: alpha_ST(c) = W_S[c] U_T[c]^T and X_ST = W_S[x] U_T[x]^T (k x k matrices).

**Step 1: stars.** For c in K let T_1, ..., T_m (m = d_c) be the edge ports at c. For S != T in this star, the supports meet in block c and in x only, because (H1) gives distinct pairs; so B_ST = alpha_ST(c) + X_ST, and this is 0 by (H2) and the mask. Put

 M_c = (alpha_ST(c)) and X_c = (X_ST), both mk x mk block matrices, and D_c = M_c + X_c.

By what was just said **D_c is block diagonal**, with diagonal blocks gamma_T(c) = alpha_TT(c) + X_TT. Let g_T(c) = rank gamma_T(c), s_T = rank X_TT, x_c = rank X_c. Then M_c = (stack of the W_S[c]) (stack of the U_T[c])^T factors through k dimensions, so rank M_c <= k, and X_c factors through j dimensions, so x_c <= j and s_T <= j.

*Rank lemma [P].* For matrices A, B of the same shape, rank(A + B) >= rank A + rank B - dim(col A ∩ col B) - dim(row A ∩ row B). *Proof:* write A = P Q, B = R S with P, R of full column rank a = rank A, b = rank B and Q, S of full row rank. Then A + B = [P R][Q; S]. The kernel of the left factor has dimension dim(col A ∩ col B), so it has rank a + b - dim(col A ∩ col B); the right factor has row space the sum of the row spaces of A and B, so rank a + b - dim(row A ∩ row B). Sylvester's inequality for a product through dimension a + b gives the claim. ∎

Apply it with A = D_c, B = -X_c, so A + B = M_c, and let y_c = x_c - dim(col D_c ∩ col X_c), y'_c = x_c - dim(row D_c ∩ row X_c), Y_c = (y_c + y'_c)/2 >= 0:

 k >= rank M_c >= rank D_c + x_c - (x_c - y_c) - (x_c - y'_c), and rank D_c = sum over T at c of g_T(c). So

 **(Star)** sum over T at c of g_T(c) <= k + x_c - y_c - y'_c <= k + j - 2 Y_c.

**Step 2: blocks.** The column space of X_TT is the projection to the T-th block of the column space of the T-th block column of X_c, hence lies in the T-projection pi_T of col X_c. A subspace V0 of col X_c of codimension y_c has pi_T(col X_c) of dimension at most dim pi_T(V0) + y_c. Take V0 = col D_c ∩ col X_c; its codimension in col X_c is y_c, and pi_T(V0) lies in pi_T(col D_c) = col gamma_T(c) (D_c is block diagonal), of dimension g_T(c). So s_T <= g_T(c) + y_c; the same argument with rows gives s_T <= g_T(c) + y'_c. Hence

 **(Block)** s_T <= g_T(c) + Y_c, and also s_T <= j.

**Step 3: edges.** For T = cd, I_k = B_TT = alpha_TT(c) + alpha_TT(d) + X_TT = gamma_T(c) + gamma_T(d) - X_TT. So

 **(Edge)** k <= g_T(c) + g_T(d) + s_T.

**Step 4: weighted sum.** For an edge T = cd take the convex combination of (Block) at c, (Block) at d and s_T <= j with weights a_c, a_d, 1 - a_c - a_d (nonnegative by (W1)): s_T <= a_c (g_T(c) + Y_c) + a_d (g_T(d) + Y_d) + (1 - a_c - a_d) j. Insert in (Edge) and sum over the E edge ports:

 E k <= sum over c of (1 + a_c) sum over T at c of g_T(c) + sum over c of a_c d_c Y_c + rho j.

Use (Star) with the factor 1 + a_c >= 0:

 E k <= mu (k + j) + rho j + sum over c of Y_c (a_c d_c - 2 - 2 a_c).

By (W2) each coefficient a_c (d_c - 2) - 2 is <= 0 and Y_c >= 0, so E k <= mu (k + j) + rho j, i.e. j (mu + rho) >= (E - mu) k. ∎

*Used ports.* The proof uses only K and its edge ports: 30 ports of P104 for the type (22; ...). The other 74 ports play no role.

**Proof of Theorem 2, items 1 and 2.** By Theorem 3 with the weights above, rank B = 8k + j >= 8k + 5k/6 on P104 and >= 9k on P112 and P120; ranks are integers. Item 2's upper bound is the Gram matrix of the system, a 1-block pattern over F_2 of rank <= 9 (it is a matrix of 9-dimensional vectors) [C]. P104 is a subset of P120, so item 3 follows by restriction. ∎

**Controls on the inequality chain [C].** `checks/star_bound.py` evaluates the gauge and every inequality of steps 1 to 3 (the rank lemma, rank M_c <= k, (Star), (Block), (Edge), block-diagonality of D_c) on explicit representations: the Gram representation of P104 and of P120 at k = 1 and, tensored with I_3 and random invertible port scalings, at k = 3 (j/k = 1, all inequalities hold with g = 0, s = 1, Y = 1); the 14-port representation of section 4 at k = 2 over F_2 and F_101; clique-cover representations of three small graphs; the rank lemma on 900 random pairs over F_2, F_3, F_101. A planted pair of edge ports at one vertex that share a coordinate trips the block-diagonality premise. These tests check the inequalities on real representations; they do not test sharpness, because no representation with j/k in [5/6, 1) on all of P104 is known.

## 3. Theorem 4: odd characteristic [P+C]

**Theorem 4.** Let char F != 2 and let V be P104, P112 or P120 with n = |V| ports. Then every k-block pattern M on V has rank(M) >= n k / 8; so w >= 13, 14, 15 respectively.

*Proof.* The odd graph on the 120 vectors of P120 is isomorphic to the orthogonality graph of the 120 root lines of E8 [C]: `data/e8_line_map.json` assigns to each vector a root r (doubled coordinates, so <r,s> = (r.s)/4), the roots are E8 roots of norm 2, and for distinct vectors s, t the roots satisfy <r_s, r_t> = 0 exactly when dot(s,t) = 1, and <r_s, r_t> = +-1 otherwise. Put O_ST = <r_S, r_T>/2 (this needs 2 invertible). Then O_SS = 1, O_ST = 0 for every *adjacent* pair, and O = (1/2) R R^T with R the n x 8 matrix of roots, so rank O <= 8. For a k-block pattern M with unit diagonal blocks put N = M o (O tensor J_k) (entrywise product; each entry O_ST repeated on a k x k block). The block (S,T) of N is M_ST O_ST: for non-adjacent pairs M_ST = 0 by the mask, for adjacent pairs O_ST = 0, and the diagonal blocks are I_k. So N = I_{nk}. N is the submatrix of the Kronecker product M tensor O with rows ((S,i), S) and columns ((T,j), T), so nk = rank N <= rank(M tensor O) = rank(M) rank(O) <= 8 rank(M). ∎

Checks [C]: the isomorphism and the root conditions; rank 8 of the root matrix over Q, and of O over F_3, F_5, F_7, F_101; unit diagonal and zeros on adjacent pairs; N = I on random fitting matrices over F_101 at k = 2 (n k = 208, 224, 240). Controls: replacing one root breaks the adjacency correspondence (65 pairs wrong); a planted nonzero entry of O on an adjacent pair is detected; modulo 2 the integer matrix 8 O vanishes, so the argument is unavailable in characteristic 2, where the Gram matrix of rank 9 exists. No upper bound is claimed in odd characteristic.

## 4. The 14-port representation at k = 2 [C]

Let K0 be the orthogonal 8-set of port indices 62, 63, 69, 74, 81, 86, 91, 99 (indices into `data/ports_p104.json`) and S14 = K0 together with the six ports 57, 67, 68, 95, 100, 101, each of which has exactly two odd neighbours in K0. `data/witness14.json` gives, for each of the 14 ports, two of 17 coordinates; W_T = U_T has rows e_a, e_b for its coordinates (a, b), so B = U U^T is the 28 x 28 integer matrix of coordinate overlaps. Then:

- the 150 ordered pairs of orthogonal ports have zero blocks (0 violations), every diagonal block is I_2, and
- **rank B = 17 over Q, over F_2 and over F_3** (the matrix has 0/1 entries and U is a 0/1 matrix with 17 columns, so the rank is at most 17 over every field).

So **w_2(S14;F) <= 17/2 < 9 over every field**: on this 14-port subset a pattern with rank below 9k occurs. The K0 ports alone force rank 16 = 8k. Controls [C]: giving one port a coordinate of an orthogonal port creates forced-zero violations; an adjacent pair sharing a coordinate has a nonzero block (so it could not be declared a forced zero); repeating a coordinate inside a port makes its diagonal block singular. On five of the ports (62, 68, 101, 63, 95), which induce a 5-cycle in the odd graph [C], the pattern is the two-coordinate clique cover of the cycle, whose rate is H_f(C_5) = 5/2 [BC, Proposition 4: H_f(C_{2k+1};F) = k + 1/2 for every field].

Consistency with Theorem 3: on all of P104 the floor at k = 2 is 18 (Theorem 2 item 1), above 17; the 14-port subset has no 22-edge star, so Theorem 3 gives nothing there.

Widening the integer window (rank a multiple of k) to the rational rank/k is the concept-stretching step of Lakatos, *Proofs and Refutations* (1976): the 14-port subset is the local counterexample to "rank >= 9k", and Theorem 2 is the corrected statement.

## 5. The k = 2, rank-17 formula over F_2 [R + C]

For the full port set P104 the statement "a 2-block pattern of rank <= 17 over F_2 exists" is encoded as a CNF formula in `checks/satenc.py`: labels W_T, U_T (2 x 17 over F_2) for the 96 ports outside K0, with the K0 gauge of Theorem 3 step 0 (K0 on coordinates 0..15, extra coordinate 16, labels supported on the blocks of the odd K0-neighbours and on the extra coordinate), B_TT = I_2, and zero blocks on all 2140 orthogonal pairs among the 96 ports. The gauge and the support restriction are justified by Theorem 3 step 0; B_TT = I_2 by Theorem 1.

| formula | variables | clauses | result (kissat 4.0.4) [R] |
|---|---|---|---|
| 14 ports, inner dimension 16 | 529 | 1569 | UNSAT |
| 14 ports, inner dimension 17 | 777 | 2353 | SAT |
| 104 ports, inner dimension 16 | 188,625 | 657,057 | UNSAT |
| **104 ports, inner dimension 17** | **223,137** | **776,065** | **UNSAT** (7 s) |
| 104 ports, inner dimension 18 | 258,529 | 898,593 | SAT (40 s) |

**Proof file.** For the 104-port, inner-dimension-17 formula, kissat's binary DRAT proof (25,763,276 bytes; `data/full_k2_rank17_f2.drat.xz`) was checked with drat-trim in forward mode: **s VERIFIED** (74 s; 468,331 of 1,085,973 lemmas and 740,968 of 776,065 clauses in the core) [R]. `check_sat.py` regenerates each formula byte for byte from `checks/satenc.py` and compares counts and sha256, decompresses the proof and compares its sha256; it does not run kissat or drat-trim. Run kissat and drat-trim on the regenerated file to repeat it.

**What this shows.** Over F_2, no 2-block pattern of rank <= 17 exists on P104 (with the stated gauge). Theorem 3 proves the same fact over **every** field (the floor at k = 2 is 18), so the solver result is a cross-check of the encoding, not an extra input. Controls [C]: the exact 14-port representation of section 4 satisfies all 2353 clauses of the 14-port formula at 17 while a mutant of it does not; the Gram representation tensor I_2 satisfies all 898,593 clauses of the full formula at 18 while one flipped bit does not.

## 6. Theorem 5: tensor width, and column restriction [P+C]

**Tensor lift.** If B is a k-block pattern then B tensor I_f is a kf-block pattern of rank f rank(B) (the same mask, with each block I_f-expanded). So the lift of any one-block pattern has ratio w_1: the Gram matrix of P104 tensor I_f has rank 9f over F_2 for f = 1..4 [C]. **A tensor lift never gives a window below the one-block value 9** (in characteristic 2); by Theorem 2 item 1 a window below 9 on P104 needs a block representation of size k >= 6 that is not a tensor lift of a one-block one.

**Column restriction (b).** Let Omega be a matrix indexed by ports and Omega_k = Omega tensor I_k, indexed by ports x [k]. A *term* is a rank-one matrix x y^T on ports x [k], with supports R = supp x and A = supp y, and its *price* is rank Omega_k[R, A]. Suppose a family of terms has sum D whose slice D^(i) (the entries at ((S,i),(T,i))) satisfies, for every i, the constraints of a one-copy requirement (whatever they are, the same for each i); let c_1 be the least total price of a family of terms realising a one-copy requirement against Omega, and c_k the least total price for the k-copy requirement. Then **c_k >= k c_1**.

*Proof [P].* Restrict each term to the copy i: x^(i), y^(i) are the parts of x, y on ports x {i}, with supports R^(i), A^(i). Omega_k[R, A] is block diagonal over the copies with blocks Omega[R^(i), A^(i)], so its rank is the sum over i of rank Omega[R^(i), A^(i)]. For each i the terms x^(i) y^(i)T sum to the slice D^(i), which meets the one-copy requirement, so their total price is >= c_1. Summing over the k copies gives the claim. ∎

Checks [C]: on 200 random supports in ports x [3], rank((Gram tensor I_3)[R, A]) equals the sum over copies of rank Gram[R_i, A_i]; for the non-tensor window Gram tensor J_3 the identity fails on random supports. The lemma has no content for a window that is not a tensor product: for the block pattern B itself the rank is the objective, and rank is not additive over copies there.

## 7. What is open

1. **w(P104;F_2) is in [53/6, 9].** Is it 9? The first k at which a rank below 9k is not excluded by Theorem 3 is k = 6, rank 53. Bukh and Cox do not show that the infimum in H_f is attained [BC].
2. Theorem 3 uses 30 of the 104 ports (K and the 22 edge ports of a K of type (22; 5^4 6^4)). Whether weights on more ports, or other port subsets, raise 53/6 to 9 is open; the type with E = 22 and the weights above give 5/6 and no better value is claimed.
3. Odd characteristic: only the lower bounds 13, 14, 15 are proved.
4. This note builds no word and gives no kappa. A tensor lift of width f gives rank 9f; any window below 9 needs a new block representation, which this note does not construct.

## 8. Status, hypotheses, scope

| item | statement | label |
|---|---|---|
| window = H_f | Theorem 1: the block mask is the Bukh-Cox d-representation | [P]; the definition of the window by the block mask is this note's, and its physical realisation for k > 1 is not derived |
| H1, H2 | distinct pairs; edge ports at one vertex are orthogonal | [P] (orthonormal basis K + v) and [C] on every K |
| Theorem 3 | star bound | [P+C]: proof above, inequalities evaluated on explicit representations; weights from a grid, optimality not claimed |
| Theorem 4 | odd characteristic | [P+C] with the explicit isomorphism |
| Gram upper bound | rank 9 in characteristic 2 | [C] |
| 14-port representation | rank 17 at k = 2 | [C] exact, over Q, F_2, F_3; integral, so <= 17 over every field |
| 104-port formula UNSAT at 17 | F_2, gauge as stated | [R] with a drat-trim-verified proof; Theorem 3 gives it over every field |
| column restriction | c_k >= k c_1 | [P+C]; tensor windows only |

**Review.** Theorem 3 and the odd-characteristic argument were re-derived line by line by a second model session (gauge, rank lemma, the star, block and edge inequalities, the weighted sum, the graph facts, the E8 map and column restriction), with its own scripts written from the port list alone. No human has reviewed any proof in this note. Citations: the definitions and theorem numbers of [BC] were read in the paper's text; [Bl] and [H79] were not read, only their bibliographic data confirmed.

**Not claimed.** No bound on kappa; no word; the values of w in odd characteristic beyond the lower bounds; any value of w on P104 above 53/6 in characteristic 2; optimality of the weights; that the block mask is the right model of any particular construction for k > 1.

## References

- [BC] B. Bukh, C. Cox, *On a fractional version of Haemers' bound*, IEEE Transactions on Information Theory 65(6), 3340-3348 (2019); arXiv:1802.00476 (v2, 13 Dec 2018). Definitions: Section 2 (d-representation, H_f) and 2.1; Theorem 1; Proposition 4 (the 5-cycle).
- [Bl] A. Blasiak, *A graph-theoretic approach to network coding*, PhD thesis, Cornell University, August 2013 (Section 2.2, as cited in [BC]).
- [H79] W. H. Haemers, *On some problems of Lovasz concerning the Shannon capacity of a graph*, IEEE Transactions on Information Theory 25(2), 231-232 (1979).
- I. Lakatos, *Proofs and Refutations: The Logic of Mathematical Discovery*, J. Worrall and E. Zahar (eds.), Cambridge University Press, 1976.
- kissat 4.0.4 (A. Biere et al.) and drat-trim (M. Heule et al.), used as external programs for section 5.
