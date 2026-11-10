# The port window of P104 is 9 in characteristic 2 (no kappa)

Tags: **[P]** hand proof, written out below; **[C]** exact computation reproduced by `check.py` (one PASS line per claim); **[P+C]** a proof whose inequalities `check.py` also evaluates on explicit representations; **[R]** a solver run recorded in `data/sat_rows.json`, not repeated by the checks; **[Q]** quoted from another source and not re-proved here. No kappa claim and no word are made. No human has reviewed the proofs; their status is in section 12.

## 0. Results

Setting, notation and the first results on the port window are those of #6933 (research/p104-port-window-haemers). Section 1 restates what is used. A *k-block pattern* on a port set V is a matrix with k x k blocks, invertible diagonal blocks and zero blocks on orthogonal pairs; the window w(V;F) is the infimum over k of rank/k.

1. **Edge inequality (E') [P+C].** In the proof of #6933 Theorem 3 (Step 2) the part of the block X_TT that is not new already lies inside the column space of gamma_T(c). Using that containment itself, and not only its dimension, removes the term s_T from the edge inequality and gives, for every edge port T = cd,

   **(E')  k <= g_T(c) + g_T(d) + min(Y_c, Y_d).**

2. **Theorem 3' [P+C].** If weights lambda_T in [0,1] on the edge ports give every non-isolated vertex a charge Lambda_c >= 2, every k-block pattern of rank 8k + j (more generally mk + j) has **j >= k**. This needs no field property and no weights to tune: it holds whenever every non-isolated vertex of Gamma(K) has degree at least 4.
3. **P104, P112, P120 [P+C].** Every orthogonal 8-set of P104 has n' = 8 and minimum degree 5 (the three K-types are recomputed); P112 and P120 have minimum degree 6 and 7. So **rank >= 9k for every k and every field on all three systems.** Hence **w(P104;F) >= 9 for every field, and w(P104;F) = 9 exactly in characteristic 2** (the Gram matrix has rank 9). #6933 had 53/6 on P104 and 9 on P112 and P120 with weights; the weights are no longer needed.
4. **A second proof [P+C].** A star inequality (LR) found independently proves j >= k when the minimum degree is at least 4, by a radical dimension count in place of (E'). Either proof alone gives the theorem.
5. **Corollaries [P+C].** H_f(G_{K_n}) = n+1 for n >= 5 over every field, and H_f(Petersen;F) >= 9/2 over every field. The Petersen statement was **not checked against the literature**.
6. **Field-only dependence [P+C].** w(V;F) depends only on the characteristic of F.
7. **Combined values [P, Q].** With #7014 (an explicit 13-clique cover of the odd graph of P104, rank 13 over every field) and #6933 Theorem 4 (w >= 13 outside characteristic 2): **w(P104) = 9 in characteristic 2 and 13 otherwise; P112 is 9 and 14; P120 is 9 and 15.**
8. **Solver rows [R].** kissat answers on F_2 instances inside P104, recorded with same-size controls; they agree with the theorem. A k = 6, rank 53 run on 30 ports was undecided at 20 minutes and is not used.

What this closes: the interval [53/6, 9] of #6933 for w(P104;F_2) and the question whether Theorem 3 extends to the floor 9. **No window below 9 exists in the block-mask model, so a fractional window saves nothing on P104.** What it does not close is in section 11.

## 1. Setting

**Ports.** P120 is the set of the 120 vectors of F_2^9 of weight 3 mod 4. P104 is the 104-port set of `data/ports_p104.json` (vendored byte for byte from #6933), a subset of P120. The 16 vectors of P120 outside P104 form two odd 8-cliques; P112 is P104 plus one of them [C]. dot(a,b) is the F_2 dot product; every port has dot(a,a) = 1 because its weight is odd. Distinct ports are **orthogonal** if dot = 0 and **adjacent** if dot = 1. G(V) is the graph on V with the adjacent pairs as edges.

**Block patterns.** For a field F and k >= 1, a *k-block pattern* on V is a matrix B over F, rows and columns indexed by V x [k], whose k x k blocks satisfy: B_TT is invertible for every T, and B_ST = B_TS = 0 for every orthogonal pair S != T. B need not be symmetric. w_k(V;F) = min rank(B)/k and **w(V;F) = inf_k w_k(V;F)**. For any graph G the same definition (zero blocks on non-adjacent pairs) gives w(G;F). #6933 Theorem 1: w(G(V);F) is the fractional Haemers bound H_f(G(V);F) of Bukh and Cox (the block pattern with identity diagonal blocks is word for word their d-representation), and at k = 1 it is Haemers' bound H(G;F). Nothing below needs that identification except in the statements about H_f in section 8.

**Normalisation.** Replacing each block row T of B by B_TT^{-1} times itself keeps the rank and all zero blocks. So in every proof below B_TT = I_k for all T.

**Configurations.** Let G be a graph and F a field. A **star configuration** (K, Gamma, (T_e)) in G consists of

- an independent set K of G of size m (for ports: m pairwise orthogonal ports),
- a simple graph Gamma on K, with E edges, degrees d_c, and n' non-isolated vertices,
- for each edge e = cd of Gamma a vertex T_e of G outside K, all distinct, such that **(C1)** T_e is adjacent to c and d and to no other vertex of K, and **(C2)** T_e and T_f are non-adjacent whenever e != f share an end.

The T_e are called edge ports. Adjacency between edge ports with disjoint pairs is left free and never used.

## 2. Gauge, stars, the rank lemma

Fix a configuration, a field F and a k-block pattern B on G with B_TT = I for all T. Write rank B = mk + j.

**Lemma 1 (gauge) [P].** j >= 0, and B = W U^T with W, U having r = mk + j columns and k rows per vertex of G (write W_T, U_T for the k x r row blocks, so B_TS = W_T U_S^T), such that, with the first mk coordinates grouped in m blocks of k (one per c in K) and the last j coordinates called x:
(a) W_c = U_c = [e-block of c, 0], i.e. the k x r matrix with I_k in block c and zeros elsewhere, for every c in K;
(b) for an edge port T = cd, W_T and U_T vanish outside the blocks c, d and x.

*Proof.* K is independent, so the blocks B_cc' are 0 for c != c' and I_k for c = c': W_K U_K^T = I_{mk}, where W_K, U_K stack the labels of K. Hence W_K and U_K have rank mk and r = mk + j with j >= 0. (This is the first step of the proof of #6933 Theorem 3.) Take a full-rank factorisation B = W U^T with r = rank B. Choose g in GL_r with W_K g = [I_{mk} 0]; then U_K g^{-T} = [I Z] for some Z, because (W_K g)(U_K g^{-T})^T = I_{mk}. Let h = [[I,0],[Z^T,I]]; then [I 0] h = [I 0] and [I Z] h^{-T} = [I 0]. Replacing W, U by W g h and U g^{-T} h^{-T} changes neither B nor the factorisation property and gives W_K = U_K = [I_{mk} 0], which is (a). For (b): if c' in K is not an end of T, then T and c' are non-adjacent by (C1), so the mask gives 0 = B_{c'T} = W_{c'} U_T^T = U_T[c']^T (block c' of U_T) and 0 = B_{Tc'} = W_T U_{c'}^T = W_T[c'] (block c' of W_T, because U_{c'} is the identity on block c'). ∎

**Notation.** For an edge port T with ends c, d and S, T edge ports: alpha_T(c) = W_T[c] U_T[c]^T, X_ST = W_S[x] U_T[x]^T (k x k each), gamma_T(c) = alpha_T(c) + X_TT, g_T(c) = rank gamma_T(c). By Lemma 1(b), B_TT = alpha_T(c) + alpha_T(d) + X_TT, and B_TT = I, so

 **(1)  I_k = gamma_T(c) + gamma_T(d) - X_TT.**

**The star at c.** Let T_1, ..., T_q (q = d_c) be the edge ports at c. Put M_c = (W_S[c] U_T[c]^T) (S, T in the star), X_c = (X_ST), D_c = M_c + X_c, all qk x qk. For S != T in the star the supports of W_S and U_T meet only in block c and in x (the other ends differ because Gamma is simple), so B_ST = W_S[c]U_T[c]^T + X_ST, and this is 0 by (C2) and the mask. Hence **D_c is block diagonal** with diagonal blocks gamma_T(c), and rank D_c = sum over T at c of g_T(c) =: G_c. Moreover M_c = (stack of the W_S[c]) (stack of the U_T[c])^T factors through k dimensions, so **rank M_c <= k**, and X_c factors through the j coordinates x, so x_c := rank X_c <= j. Define

 y_c = x_c - dim(col D_c ∩ col X_c),  y'_c = x_c - dim(row D_c ∩ row X_c),  Y_c = (y_c + y'_c)/2.

Then 0 <= y_c, y'_c <= x_c <= j, so 0 <= Y_c <= j.

**Lemma 2 (rank lemma) [P].** For matrices A, B of the same shape, rank(A+B) >= rank A + rank B - dim(col A ∩ col B) - dim(row A ∩ row B).

*Proof.* Write A = P Q, B = R S with P, R of full column rank a = rank A, b = rank B and Q, S of full row rank. Then A + B = [P R][Q; S]. The left factor has rank a + b - dim(col A ∩ col B), the right factor a + b - dim(row A ∩ row B), and Sylvester's inequality for a product through dimension a + b gives rank(A+B) >= (a+b-dc) + (a+b-dr) - (a+b). ∎

**Lemma 3 (Star) [P+C].** G_c <= k + x_c - y_c - y'_c <= k + j - 2 Y_c.

*Proof.* M_c = D_c + (-X_c). Lemma 2 with A = D_c, B = -X_c: k >= rank M_c >= G_c + x_c - (x_c - y_c) - (x_c - y'_c) = G_c - x_c + y_c + y'_c. ∎

## 3. Containment and the edge inequality (E')

**Lemma 4 (containment) [P+C].** Let T be an edge port with end c. There are subspaces R, R' of F^k with dim R <= y_c, dim R' <= y'_c, col X_TT ⊆ col gamma_T(c) + R and row X_TT ⊆ row gamma_T(c) + R'.

*Proof.* Let pi_T be the projection of F^{qk} onto the T-th block of k coordinates. Write col X_c = V0 ⊕ C with V0 = col D_c ∩ col X_c; then dim C = x_c - dim V0 = y_c. The columns of X_TT are the pi_T-images of the columns of the T-th block column of X_c, so col X_TT ⊆ pi_T(col X_c) = pi_T(V0) + pi_T(C). Since D_c is block diagonal, col D_c is the direct sum of the col gamma_S(c), so pi_T(col D_c) = col gamma_T(c) and pi_T(V0) ⊆ col gamma_T(c). Put R = pi_T(C), of dimension at most y_c. The row statement is the same argument for the transposed matrices (D_c^T is block diagonal with blocks gamma^T). ∎

**Proposition 5 (E') [P+C].** For every edge port T = cd:

 k <= g_T(c) + g_T(d) + min(y_c, y'_c, y_d, y'_d), hence **k <= g_T(c) + g_T(d) + min(Y_c, Y_d)**.

*Proof.* By (1), every column of I_k is a sum of columns of gamma_T(c), of gamma_T(d) and of X_TT. So F^k = col I_k ⊆ col gamma_T(c) + col gamma_T(d) + col X_TT ⊆ col gamma_T(c) + col gamma_T(d) + R by Lemma 4 (the part of col X_TT in col gamma_T(c) is absorbed). Counting dimensions, k <= g_T(c) + g_T(d) + y_c. The row version gives y'_c; the same argument with the roles of c and d exchanged gives y_d and y'_d. Finally min(y,y') <= (y+y')/2. ∎

The proof of #6933 Theorem 3 used only dim(col X_TT) <= g_T(c) + y_c (its (Block)) and then added the rank s_T of X_TT to g_T(c) + g_T(d) in (Edge). That counts g_T(c) twice, because the part of col X_TT that is not new is already inside col gamma_T(c). The containment lemma removes the double count.

## 4. Theorem 3'

**Theorem 6 (Theorem 3') [P+C].** Let (K, Gamma, (T_e)) be a star configuration in a graph G, F any field, B a k-block pattern on G of rank mk + j. Suppose lambda_T in [0,1] are given for the edge ports, and put, for each vertex c of K, Lambda_c = sum over the edge ports T at c of (lambda_T if c is the first end of T, else 1 - lambda_T), with a fixed orientation of each edge. Then

 **(a)** j / k >= (E - n') / ( n' + sum over c of (Lambda_c - 2)^+ ), and
 **(b)** if Lambda_c >= 2 for every non-isolated c, then **j >= k**. In particular j >= k if every non-isolated vertex of Gamma has degree >= 4 (take lambda_T = 1/2, so Lambda_c = d_c/2 >= 2).

*Proof.* Take min(Y_c, Y_d) <= lambda_T Y_c + (1 - lambda_T) Y_d in (E'), and sum over the E edge ports T = cd (c the first end):

 E k <= sum_c [ sum over T at c of g_T(c) + Lambda_c Y_c ].

Apply Lemma 3 at each of the n' vertices of positive degree (sum over T at c of g_T(c) = G_c <= k + j - 2 Y_c):

 E k <= sum_c [ k + j + (Lambda_c - 2) Y_c ] = n'(k + j) + sum_c (Lambda_c - 2) Y_c.

Since 0 <= Y_c <= j, (Lambda_c - 2) Y_c <= (Lambda_c - 2)^+ j, which gives (a). Under the hypothesis of (b), Lambda_c - 2 >= 0 and sum_c (Lambda_c - 2) = E - 2n' (the charges add to E), so E k <= n'(k + j) + (E - 2n') j = n' k + (E - n') j, that is (E - n')(k - j) <= 0. As E > n' (the charges add to E and each is at least 2, so E >= 2n' > n'), j >= k. ∎

No field property, symmetry, or k = 1 argument is used. The case of (a) with Lambda_c < 2 everywhere (for example Gamma = K_4) gives j/k >= (E - n')/n'.

## 5. Application to the port systems

**Lemma 7 (ports relative to an orthogonal 8-set) [P+C].** Let V be any set of odd-weight vectors of F_2^9 containing an orthogonal 8-set K (pairwise dot 0). Put v = all-ones + sum of K. Then K and v form an orthonormal basis of F_2^9 (dot(v,c) = 0, dot(v,v) = 1), so every port t is the sum of the c in A(t) = {c in K : dot(t,c) = 1} plus eps v, with eps = dot(t,v), and 1 = dot(t,t) = |A(t)| + eps. Call t outside K an *edge port* if |A(t)| = 2; then eps = 1. Let Gamma(K) have a vertex for each c in K and one edge cd for each edge port with A = {c,d}.
- **(H1)** distinct edge ports have distinct pairs, because t is determined by (A, eps); so Gamma(K) is simple.
- **(H2)** two edge ports t = c + d + v and t' = c + e + v (d != e) sharing exactly one vertex are orthogonal: dot(t,t') = dot(c,c) + dot(v,v) = 1 + 1 = 0.
- An edge port is adjacent to its two K-neighbours and orthogonal to the other six points of K.

So (K, Gamma(K), edge ports) is a star configuration in G(V): (C1) is the definition, (C2) is (H2), and K is independent in G(V). `check.py` recomputes (H1), (H2) on every orthogonal 8-set of every system as well [C].

**Counts [C].** The orthogonal 8-sets (there is no orthogonal 9-set): P104 1728, P112 4032 (either clique), P120 8640. K-types (E; sorted degrees):

| system | type | number of 8-sets | minimum degree |
|---|---|---|---|
| P104 | (22; 5,5,5,5,6,6,6,6) | 960 | 5 |
| P104 | (22; 5,5,5,5,5,6,6,7) | 384 | 5 |
| P104 | (21; 5,5,5,5,5,5,6,6) | 384 | 5 |
| P112 | (25; 6,6,6,6,6,6,7,7) | 3584 | 6 |
| P112 | (24; 6^8) | 448 | 6 |
| P120 | (28; 7^8) | 8640 | 7 |

In every case n' = 8, so lambda_T = 1/2 gives Lambda_c = d_c/2 >= 5/2 >= 2.

**Theorem 8 [P+C].** For P104, P112 and P120, every field F and every k, every k-block pattern has rank >= 9k. *Proof.* Theorem 6(b) on any one orthogonal 8-set: rank = 8k + j >= 9k. ∎

## 6. The window values

**Corollary 9 [P+C].** (i) w(P104;F) >= 9 for every field F, and w(P112;F), w(P120;F) >= 9. (ii) If char F = 2, the Gram matrix (dot(S,T)) has unit diagonal, zeros on orthogonal pairs, and rank <= 9 (a Gram matrix of vectors in a 9-dimensional space); it is a 1-block pattern on P120, hence by restriction on P112 and P104. So **w(P104;F) = w(P112;F) = w(P120;F) = 9 when char F = 2**, attained at k = 1. (iii) In particular no k-block pattern on P104 over any field has rank below 9k, for any k. The first case that #6933 left undecided, k = 6 with rank 53 < 54, is excluded.

**Combined values [Q].** #7014 (unpaidmoon) partitions the odd graph on the 104 ports into 13 pairwise disjoint cliques of size 8; the 104 x 13 indicator matrix W has W W^T with unit diagonal and zeros on orthogonal pairs, and rank 13 over every field, so w(P104;F) <= 13 for every F; adjoining one or both of the omitted 8-cliques gives 14 and 15 for P112 and P120. #6933 Theorem 4 gives w >= 13, 14, 15 when char F != 2. Together with Corollary 9:

| system | char F = 2 | char F != 2 |
|---|---|---|
| P104 | 9 | 13 |
| P112 | 9 | 14 |
| P120 | 9 | 15 |

The odd-characteristic values are the lower bounds of #6933 Theorem 4 and the upper bounds of #7014, both quoted; they are not re-derived here.

## 7. A second, independent proof: the star inequality (LR)

This proof uses the same gauge (Lemma 1) and the same stars, but not Lemma 2, not the containment lemma and not (E').

**Notation.** Fix an edge port T = cd and let T_1, ..., T_q be the edge ports at c. Let L_S be W_S restricted to the coordinates x and the block c (a k x (j+k) matrix) and R_S the same for U_S; lambda_S = rank L_S, rho_S = rank R_S; L and R are the stacks (qk x (j+k)); ell = rank L, rho = rank R.

**Proposition 10 (LR) [P+C].** For every edge port T = cd:

 **G_c + k <= j + 2 (g_T(c) + g_T(d)).**

*Proof.*
1. For S != T in the star, L_S R_T^T = B_ST = 0 (the supports of W_S, U_T meet in block c and x only), and L_T R_T^T = gamma_T(c). So L R^T = D_c is block diagonal and rank(L R^T) = G_c.
2. Let Z = rowsp L ∩ (rowsp R)^perp, the vectors of the row space of L that are orthogonal (standard bilinear form) to every row of R. The map v -> v R^T on rowsp L has kernel Z and image of dimension rank(L R^T) = G_c, so dim Z = ell - G_c. Z lies in (rowsp R)^perp, of dimension j + k - rho. So **ell - G_c <= j + k - rho.**
3. Z_S = rowsp L_S ∩ (rowsp R_S)^perp has dimension lambda_S - g_S(c) (same argument for one block). It lies in Z, because rowsp L_S is orthogonal to every R_{S'} with S' != S (step 1). So **lambda_S - g_S(c) <= ell - G_c**, and symmetrically **rho_S - g_S(c) <= rho - G_c.**
4. Adding the two inequalities of step 3 for S = T and using step 2: lambda_T + rho_T - 2 g_T(c) <= ell + rho - 2 G_c <= k + j - G_c.
5. By (1), alpha_T(c) = I - gamma_T(d), so rank alpha_T(c) >= k - g_T(d). Also lambda_T >= rank W_T[c] >= rank alpha_T(c), and the same for rho_T. So lambda_T + rho_T >= 2k - 2 g_T(d).
6. Combining 4 and 5: 2k - 2 g_T(d) - 2 g_T(c) <= k + j - G_c. ∎

**Theorem 11 [P+C].** If every non-isolated vertex of Gamma has degree >= 4, then j >= k.

*Proof.* Fix c of degree d_c and sum Proposition 10 over the d_c edge ports T at c: d_c (G_c + k) <= d_c j + 2 sum over T at c of e_T, with e_T = g_T(c) + g_T(d). Sum over c. Each e_T occurs at both its ends, and sum over T of e_T = sum over c of G_c. So

 sum_c d_c G_c + 2E k <= 2E j + 4 sum_c G_c, i.e. 2E (k - j) <= sum_c (4 - d_c) G_c <= 0

(isolated vertices have G_c = 0; the others have d_c >= 4). As E > 0, j >= k. ∎

(E') is an inequality per edge and carries the charges of Theorem 6(a); (LR) is an inequality per edge and star, summed with degree weights. Either gives Theorem 8.

## 8. Corollaries on the graphs G_Gamma

For a simple graph Gamma on n vertices let **G_Gamma** be the graph with vertex set V(Gamma) together with the edges of Gamma ("pairs"); a point is adjacent to the pairs containing it, two pairs are adjacent iff disjoint, and two points are never adjacent. (K = the points and T_e = the pairs form a star configuration: (C1) and (C2) are the definition.)

**Corollary 12 [P+C].** If Gamma has minimum degree >= 4, then **H_f(G_Gamma;F) = n+1 for every field F**; in particular H_f(G_{K_m};F) = m+1 for m >= 5.

*Proof.* Lower bound: Theorem 6(b) with n' = n and mk + j >= (n+1)k. Upper bound: in F^{n+1} with the bilinear form diag(1, ..., 1, -1) put x_c = e_c and x_T = e_c + e_d + e_v for T = cd. Then <x_a, x_a> = 1 for all points and pairs (1 + 1 - 1 for a pair); two points are orthogonal; a point and a pair not containing it are orthogonal; two pairs sharing a vertex give 1 - 1 = 0. Their Gram matrix has unit diagonal, zeros on non-adjacent pairs and rank <= n+1, so H(G_Gamma;F) <= n+1 and H_f <= H. ∎

`check.py` verifies this representation over F_2, F_3, F_5 for m = 5, 6, 7 [C]. #6933's weights gave only 16/3 for G_{K_5} and 20/3 for G_{K_6}.

**Corollary 13 (Petersen) [P+C].** G_{K_4} is the Petersen graph [C]: the map point a -> {a,5}, pair {b,c} -> {1,2,3,4} minus {b,c} is an isomorphism onto the Kneser graph K(5,2). Here Lambda_c = 3/2 < 2 at every vertex, n' = 4, E = 6, so Theorem 6(a) gives j/k >= 2/4 and **H_f(Petersen;F) >= 9/2 for every field F.** Since the Gram representation above gives H <= 5 (the F_2 rank of I + A is 5 [C]), the value is in [9/2, 5]. Over F_2 with k = 2 the rank-9 row (ratio 9/2) is recorded UNSAT [R] (section 10), so 9/2 is not attained at k = 2 over F_2.

**This corollary was not checked against the literature.** The Shannon capacity of the Petersen graph is 4 (alpha = 4 and the Lovasz number is 4; stated from memory, not rechecked), so the claim is above that capacity. If a representation of the Petersen graph of ratio below 9/2 is known, Theorem 6 is wrong, and that would be the quickest refutation. Bukh and Cox and Blasiak's thesis were not searched for a Petersen value.

## 9. Field-only dependence [P+C]

**Remark 14.** For every field E, w(V;E) = w(V;F_0), with F_0 the prime field of E; the same holds for w(G;E) for every graph G.

*Proof.* (a) *Subfields.* A k-block pattern over F_0 is one over E, so w(V;E) <= w(V;F_0).
(b) *Finite extensions.* Let L/F be an extension of degree s, and fix an F-basis of L. Replace each entry a of a k-block pattern B over L by the s x s matrix rho(a) of multiplication by a. rho is an injective ring homomorphism M_t(L) -> M_{st}(F), so it maps invertible blocks to invertible blocks and zero blocks to zero blocks, and rank_F rho(M) = s rank_L(M) (rho(M) is M as an F-linear map). So rho(B) is an sk-block pattern over F of ratio rank_L(B)/k: w(V;F) <= w(V;L). With (a), w(V;L) = w(V;F). (`check.py` verifies the homomorphism and the rank identity for F_4 over F_2 on 60 random matrices [C].)
(c) *Arbitrary fields.* Let B be a k-block pattern over E. Let A be the subring of E generated by F_0 and the entries of B and the inverses of the determinants of the diagonal blocks; A is a finitely generated F_0-algebra and a domain. Choose a maximal ideal m of A. By the Nullstellensatz (Zariski's lemma) A/m is a finite extension of F_0 (a finite field if char E > 0, a number field if char E = 0). Reduction modulo m keeps the diagonal blocks invertible (their determinants are units in A) and the zero blocks zero, and cannot raise the rank (minors that vanish keep vanishing). So there is a pattern over A/m of the same k and rank at most rank B; by (b) w(V;F_0) = w(V;A/m) <= rank B / k. Hence w(V;F_0) <= w(V;E). ∎

So "try F_4 or F_8" is not a new search space: w depends only on the characteristic. Theorem 6 does not need this; it holds for every field directly.

## 10. Solver cross-checks [R]

Rows of `data/sat_rows.json`: F_2 block patterns in the gauge of Lemma 1 (K on blocks; each edge port supported on the blocks of its odd K-neighbours and on j extra coordinates), unit diagonal blocks, zero blocks on all orthogonal pairs among the instance ports; rank = |K| k + j; solver kissat 4.0.4, 20-minute cap. **No DRAT proofs were produced for these rows**: each UNSAT is the solver's answer only. `check.py` recomputes each instance from `data/ports_p104.json`, applies Theorem 6 to it and compares with the recorded row; it does not run a solver, and the CNF files are not shipped. "SB" means each W_T is put in reduced row echelon form, which is a symmetry of the problem ((W_T, U_T) -> (g W_T, g^{-T} U_T), g in GL_k(F_2), keeps B_TT = I and all zero blocks) [P].

| instance | k | rank | result (time) | Theorem 6 says |
|---|---|---|---|---|
| Petersen: 4 points + 6 pair ports (10 ports; cubic, girth 5) | 4 | 17 (j=1) | UNSAT (SB, 8.5 s); undecided at 20 min without SB | infeasible (j >= 2) |
| same | 4 | 20 (j=4), control | SAT (0.0 s), decoded and re-checked | allowed |
| same | 2 | 9 (j=1) | UNSAT (SB 0.0 s; no SB 0.5 s) | allowed (j/k = 1/2 equals the threshold) |
| same | 2 | 10 (j=2), control | SAT (0.0 s), decoded and re-checked | allowed |
| G_{K_5}: 5 points + 10 pair ports (15 ports) | 3 | 16 (j=1) | UNSAT (SB, 0.6 s) | infeasible (j >= 3) |
| same | 3 | 17 (j=2) | UNSAT (SB, 57.2 s) | infeasible |
| same | 3 | 18 (j=3), control | SAT (SB, 689.7 s), decoded and re-checked | allowed (threshold attained) |
| 14-port subset of #6933 (K0 + 6 edge ports) | 2 | 17 (j=1), control | SAT, decoded and re-checked; the recorded witness itself, planted as unit clauses, is SAT; a mutant is rejected | allowed (minimum degree 1) |
| 30 ports (K of type (22; 5,5,5,5,6,6,6,6) + 22 edge ports) | 6 | 53 (j=5) | **undecided at 20 min** (SB; and without SB) | infeasible, not tested |
| same | 6 | 54 (j=6), control | undecided at 20 min (SB; and without SB) | allowed |

Every row that Theorem 6 predicts infeasible and that was decided came back UNSAT, and no decided row contradicts the theorem. The k = 6 rank 53 run on 30 ports was undecided at 20 minutes, and so was its same-size feasible control; **neither is used**, and nothing in this note depends on any row: Theorem 6 is a proof, the rows are a cross-check of it and of the encoding. The two 5-point rows use a different orthogonal 8-set from the 30-port row; only the sub-structure (5 points and all 10 pair ports) matters. The k = 2, rank 9 Petersen row sits at the threshold of Theorem 6(a) and says that no 2-block pattern of ratio 9/2 exists over F_2 for this instance.

## 11. Relation to #6933, and what is not closed

**Why Theorem 3 stopped at 53/6.** (E') replaces the pair (Block), (Edge) of #6933 by one inequality without the term s_T. A floating-point linear program over the old inequality system (per-edge, per-end weights; (Edge), (Block) with a family-wise Y, (Star), s <= j) on one K of type (22; 5,5,5,5,6,6,6,6) returned 5/6 as the optimum, including after adding every single-block family containing the pair port and the diagonal; this is recorded only, nothing here depends on it, and the data are not shipped. With the old system the value 53/6 could not be beaten by changing weights.

**Closed.** Open questions 1 and 2 of #6933: w(P104;F_2) = 9, and Theorem 3 extends to the floor 9 (Theorem 3', which uses only K and its edge ports). Every k-block pattern on P104 has rank >= 9k, so a tensor lift (ratio exactly 9, #6933 Theorem 5) is optimal in the block-mask model and **no fractional-window saving exists**. In odd characteristic the window is 13 by #7014 and #6933.

**Not closed, not claimed.**
- The window is defined by the block mask on whole k x k blocks with one block size k for all ports. A mask on sub-blocks, or port-dependent block sizes k_T, are different models. From (E') and (Star) one gets sum over T of k_T <= sum over c of k_c + (E - n') j for the star configuration, which leaves arithmetic room only for a window that prices edge ports below points; no such window is defined here, and nothing here says one helps.
- Nonlinear labels are not covered (the patterns are linear algebra over a field).
- That a physical construction realises a k-block window with exactly this mask for k > 1 was not derived in #6933 and is not derived here.
- The Petersen and G_{K_m} statements are not compared with the literature (section 8).
- The value of H_f(Petersen;F) between 9/2 and 5 is open.

## 12. Status, hypotheses, scope

| item | statement | label |
|---|---|---|
| gauge, stars, Lemmas 1 to 3 | steps 0 and 1 of #6933 Theorem 3, restated | [P+C] |
| containment, (E') | Lemma 4, Proposition 5 | [P+C]: proof above; inequalities evaluated on explicit representations, tight on the Gram representations and the 14-port witness |
| Theorem 3' | Theorem 6 | [P+C] |
| port facts | H1, H2, K-types, minimum degree | [P] and [C] on every orthogonal 8-set of P104, P112, P120 |
| second proof | Proposition 10, Theorem 11 | [P+C] |
| G_Gamma, Petersen | Corollaries 12, 13 | [P+C]; not compared with the literature |
| field-only dependence | Remark 14 | [P+C] (F_4 over F_2 checked); the Nullstellensatz is quoted |
| odd characteristic values | 13, 14, 15 | [Q] #7014 and #6933 Theorem 4 |
| solver rows | section 10 | [R], no DRAT |

**Review.** No human has reviewed any proof in this note. Two model sessions proved the result independently, by (E') and by (LR); a third model session read the proof of (E') line by line, found no broken step, and ran its own representation tests (106 valid representations of seven small graphs over F_2 and F_3 plus the port-system and witness cases, with planted violations that were caught). `check.py` repeats such tests with its own code written from the definitions. Representations in the checks seldom stress (E') with g > 0 and Y > 0 on the same edge in a P104-sized example; the small-graph representations do (check.py counts 1990 such edge ends), and the proof is what carries the general statement.

**Hypotheses used.** B_TT invertible for every port; zero blocks on all orthogonal pairs among K and the edge ports (the other ports of the system are not used); K independent; edge ports have distinct pairs and edge ports at one vertex are non-adjacent. No field property, no symmetry of B, and no k = 1 assumption.

**Not claimed.** No bound on kappa and no word; any window below 9 in a model other than the block mask; the literature status of the Petersen value; DRAT-checked solver rows.

## References

- [6933] research/p104-port-window-haemers (this repository, DreamingOfClouds): setting, Theorem 1 (window = fractional Haemers bound), Theorem 3 (weighted star bound), Theorem 4 (odd characteristic), Theorem 5, the 14-port pattern.
- [7014] unpaidmoon, pull request #7014 of this repository: partition of the odd graph on the 104 ports into 13 cliques of size 8.
- [BC] B. Bukh, C. Cox, *On a fractional version of Haemers' bound*, IEEE Transactions on Information Theory 65(6), 3340-3348 (2019); arXiv:1802.00476.
- [Bl] A. Blasiak, *A graph-theoretic approach to network coding*, PhD thesis, Cornell University, 2013 (as cited in [BC]).
- [H79] W. H. Haemers, *On some problems of Lovasz concerning the Shannon capacity of a graph*, IEEE Transactions on Information Theory 25(2), 231-232 (1979).
- kissat 4.0.4 (A. Biere et al.), used as an external program for section 10.
