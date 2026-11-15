# Proofs: dying roles, slack, and the Delta-Floor lemma (rho = 2 two-arm callers)

Common setting and notation (as in the #7606 / #7609 caller sections): rho = 2, N = n + 2 units T = I - 2xy^T with product -I;
stages are adjacent isotropic unit pairs on coordinate masks Z_s with t_s != -1; prefix commutation; thin units arbitrary; two arms
meeting in a pair of hubs H. Tags: [P] proved here, [C] exact computation re-run by a checker in this package, [C-param] priced
with PRICEKIT, [N] numerical (float solver, not a claim).

## Part I. DYINGPAIR

### Theorem: tight dying roles are impossible for every interior death stage [P]

Setting (rs2/rootcheck model, as NESTPROOF/DYINGGEN). rho = 2, N = n+2 units T = I - 2xy^T, product -I; stages = 2 adjacent isotropic units
in coordinate masks Z_s with t_s != -1; prefix commutation (P_u commutes with Pi_{Z_s} just before stage s); thin units arbitrary.
Two arms: left stages 0..m-1 (time order), right arm after the thin block; H = 2 hubs; some right stage r has Z_r meeting every left Z_j
only inside H. E_j = roles first appearing at left stage j; U_j = Z_0 u ... u Z_j. Normalised X~_a = X_a Z_a^-T, Y~_a = Y_a W_a^-T (K = WZ^T).
Layout: D (nonempty) is a subset of E_k, present in Z_k..Z_d, absent from Z_{K}, K = d+1, with d <= m-3 (so stage K+1 is still in the left arm).

Theorem. Suppose (T1) |U_j| = 2j+4 for every k < j <= d (no extra role enters at stages k+1..d), and (T2) |Z_K| <= 2K+3
(e.g. the B count 2K+4 minus the dying roles, plus at most |D|-1 extra roles). Then no such root exists. Covers singles and pairs, any
entry k, any death d <= m-3, one dying group per arm (the other arm's dying roles are outside every left mask, so do not enter).

Facts used (all already proved): Lemma S (SINGLEHUB): G[later, earlier] = W Z^T, G[earlier, later] = -W Z^T; K_ss = [[1,-g],[h,1]], t = gh.
Floor (CALLEROPEN 3.2, step 2, which never uses nesting): rows Y_0..Y_{j+1} against columns X_0..X_j, X_r|H form a NONSINGULAR square
matrix of size 2j+4 (needs Z_i meet Z_r only in H for i <= j+1). Hence (F1) X_0..X_j, X_r|H are 2j+4 independent vectors of R^{U_j};
(F2) the y's of stages 0..j+1 are independent (this is NESTPROOF's hypothesis H, now a consequence).

Step 0 (Q has no eigenvalue 2). Q_a = I - Y~_a^T X~_a = W^-1 (K_aa - G_aa) K_aa^-1 W, and (K-G)K^-1 = [[1+2t,-g],[-h,1]]/(1+t):
trace 2, det 1/(1+t), eigenvalues 1 +- sqrt(t/(1+t)). An eigenvalue 2 forces det 0: impossible. [C qcheck.py: 1+-i at t=-1/2, exact match]
Step 1 (R^D-content is forced). Rows Y_j (j <= K+1) vs columns X_0..X_K, X_r|H: full matrix F nonsingular (Floor at K, needs K+1 <= m-1).
Restricting rows and columns to Z_K changes F by Y|_D^T X|_D (the only roles outside Z_K touched by these columns are D), so
2K+4 = rank F <= |Z_K| + rank(X_{<K}|_D) <= 2K+3 + rank(X_{<K}|_D): rank(X_{<K}|_D) >= 1 (= |D| in the exactly tight case).
V := C(P_K - I) = C(X_{<K}) (P_K - I = -2 X M Y^T, M invertible, Y_{<K} independent by F2). Prefix commutation at K makes V
Pi_{Z_K}-invariant, so Pi_N V = V cap R^N and, as V lies in R^{U_d} with U_d \ Z_K = D, V cap R^D = Pi_D V != 0. Take 0 != v in V cap R^D.
Step 2 (sum zero). v = X_{<K} beta and Y_K^T v = 0 (D outside Z_K). Lemma S: Y_K^T v = W_K gamma, gamma = sum_i beta_i z_i; W_K invertible
(t != -1), so gamma = 0: v = sum_{a<=d} X~_a alpha_a with sum_a alpha_a = 0 (NESTPROOF L1).
Step 3 (top index is k). Let j = max{a : alpha_a != 0}. j < k is impossible (v would lie in R^{U_j}, disjoint from D). If k < j <= d: rows
E_j of v vanish (E_j is disjoint from D and from Z_a, a < j), so X~_j[E_j] alpha_j = 0 and rank X~_j[E_j] <= |E_j|-1. Then X_0..X_j, X_r|H
lie in R^{U_{j-1}} + (an (|E_j|-1)-dim subspace of R^{E_j}), of dim |U_j|-1 = 2j+3 by (T1), contradicting F1 (2j+4 independent). So j = k.
Step 4 (triangular recursion). For c < k, Z_c misses D, so 0 = Y~_c^T v = sum_a G~[c,a] alpha_a with G~[c,a] = +I (a<c), I-Q_c (a=c), -I (a>c).
With A_c = alpha_0+...+alpha_c and A_k = 0 this reads (2I - Q_c) A_c + Q_c A_{c-1} = 0. A_{-1} = 0 and Step 0 give A_0 = ... = A_{k-1} = 0,
so alpha_0 = ... = alpha_{k-1} = 0 and alpha_k = -A_{k-1} = 0: v = 0. Contradiction. QED
(k = 0 needs no Step 4; k = 1 is the identity Q_0 = 2I on Y~_0 for a pair.)

Scope / what is NOT covered: (i) slack: an extra role entering at a stage in (k, d] (breaks T1), or >= |D| extra roles at the death stage K
(breaks T2, e.g. a single plus one extra role at K); (ii) one arm with dying roles of different entry stages; (iii) d = m-2 (death at the
innermost stage: no left stage K+1; DYINGGEN's conditional kill stands there); (iv) t = -1 stages, rho != 2, non-two-arm (tree) callers.

## Part II. SLACK

Notation as in Part I.

A. True cap [P]. An idle line is ONE idle op covering stages a..b; at each stage k the lines alive give the complement of X_k in R^{Z_k}
with dual vectors (p ⟂ Y_k, q ⟂ X_k; CALLEROPEN cap_check.py computes |S| - max(rank Y|S, rank X|S); SINGLEHUB Lemma 5). One op has one
end-referred (p,q), so a line covering I=[a,b] has p,q in R^{Z_I}, Z_I = Z_a ∩..∩ Z_b, p ⟂ Y_a..Y_b, q ⟂ X_a..X_b:
   N(I) <= |Z_I| - max(rank Y_I|Z_I, rank X_I|Z_I).
Per boundary (|I|=2) rank <= 4, so "|S|-4" is the TIGHTEST per-boundary cap, never too generous. The pricer's error is elsewhere:
layout_price.lines()/step1.capS impose caps only on |I|=2; for nested masks Z_I = Z_a so longer intervals add nothing (B reproduced
1.0950/1.0031/0.9773 by icap.py too), but a role that dies (or a lone extra role) inflates the two-stage caps while the long lines the
greedy keeps must live in the smaller Z_I. icap.py imposes every interval.
B. Extended Crossing Lemma [P]. With a witness (hubs ⊂ S'), rank(Y_k,Y_k+1|S') = rank(X_k,X_k+1|S') = 4 if ANY of X_k, X_k+1, Y_k, Y_k+1
is supported in S'. Proof: CALLEROPEN 3.1 for X_k (K-G invertible); for X_k+1: c^T G_{k+1,k+1} = a^T G[k,k+1] = -c^T W_k+1 Z_k+1^T
gives c^T(G+K)=0 and G+K = [[1,0],[2h,1]] is invertible; Y-versions by transposition. Without one of these only rank >= 2 (witness) is proved.
C. Refined DYINGPAIR Step 3 [P]. If alpha_j != 0 is the top index (k<j<=d), X~_j[E_j] alpha_j = 0 gives rank X_j|E_j <= 1 (2 columns), so
X_0..X_j, X_r|H span <= |U_{j-1}| + 1 dims; F1 needs 2j+4: contradiction iff |U_{j-1}| <= 2j+2. With Step 1 run on the full dead set D_all and
intersected with R^D (dim >= 2K+4-|Z_K|-(|D_all|-|D|)), Steps 2,4 unchanged. KILL: |Z_K|+|D_all|-|D| <= 2K+3 and no extra role entered at
stages <= d-1. This kills an extra role entering exactly at d (e.g. pair k=0 d=1 + role at 1, +0.75% in the rank-4 model). run3: 22/140 killed.
Lone extra role e on [je,ee]: by NESTPROOF L2 (X and Y sides) either X_{<K} (resp. Y) are e-free -> B applies on every interval -> no gain,
or delta_e in span(X~_a, je<=a<=ee) with sum alpha = 0 (L1 + recursion for a<je) -- impossible for ee=je. So any gain needs a nonzero
reflection block b_K > 0 (NESTPROOF's open question), on BOTH sides, plus rank < 4 on the restricted sets.

D. Rank drop => reflection block, with first-touch conditions [P] (lone e on [je,ee], K=ee+1, interval I=[a,b] across the death, Z_I = Z_a \ e,
normalised G~[c,j] = +I (j<c), I-Q_c (j=c), -I (j>c); witness = right arm).
 Y side: a relation of rank(Y_a,Y_a+1|Z_I) is w = Y~_a mu - Y~_a+1 mu (witness forces equal coefficients) supported on E_a+1 u {e}. Pairing with
 X~_j: j<a gives w_e x~_j = 0; j=a gives w_e x~_a = -mu^T Q_a. So mu != 0 forces w_e != 0, x~_a != 0 and x~_j = 0 for j<a (x~ = e-row).
 X side: u = X~_a nu - X~_a+1 nu on E_a+1 u {e}; rows Y~_j, j<a: y~_j u_e = 0; row a: (2I-Q_a) nu = y~_a u_e, and 2I-Q_a is invertible (Step 0),
 so u_e != 0 and y~_a != 0. u lies in C(X_{<=K}); Pi_{Z_K}-splitting (NESTPROOF L2, with V_K+1 cap R^N = V_K cap R^N) gives delta_e in V_K.
 Likewise delta_e lies in C(Y). So a rank drop on the X and Y sides FORCES b_K > 0 on both sides (the hypothesis is automatic). It also needs
 X_a, Y_a to touch e while X_j, Y_j (j<a) do not. The window block T_W (2|W| transvections) must then map delta_e to -delta_e.
 NOT proved: a contradiction from these. The one extra role always leaves 1 spare dimension in the Floor count (|U_j| = 2j+5).

E. LONE ROLES CLOSED [P] (supersedes the "open" status of D for lone roles). Lone extra role e on [je,ee], K=ee+1,
interval I=[a,b] with je<=a<=ee<K<=b, Z_I = B_a (B masks nested). Normalised G~ (D above); x~_j, y~_j = e-rows of X~_j, Y~_j; witness r.
 Functional test. Pair rows Y_I|Z_I with column vectors c(gamma) = sum_{j<=t} X~_j gamma_j + X~_r|H gamma_r lying in R^{Z_I}. Row s (a<=s<=t)
 gives  sum_{j<s} gamma_j + (I-Q_s) gamma_s - sum_{s<j<=t} gamma_j - gamma_r;  a row c >= K gives Phi = sum_{j<=t} gamma_j - gamma_r.
 These 2(t-a+1)+2 functionals are independent on gamma-space (gamma_r only in Phi; then triangular with Q_s invertible). The domain
 {gamma : c(gamma) in R^{Z_I}} has codim <= rank of span(X_<=t) on U_t \ Z_I = {e} u E_a+1 u .. u E_t. So rank(Y_I|Z_I) >= 2(t-a)+4 - codim.
 (1) t = a, columns X_<=a: codim <= 1 (e row: sum_j x~_j gamma_j). A drop needs that constraint in span{Phi, Q_a gamma_a}, so x~_j = 0 for all j<a.
     Dual test (X side, rows Y_<=a + hubs): an X-drop needs y~_j = 0 for all j<a.
 (2) Case A (X_{<K} e-free): (1) with a constraint that is vacuous gives Y-rank 4.  Case B (delta_e = sum X~_j alpha_j, sum alpha = 0; NESTPROOF L2):
     top index t = max{alpha_j != 0} > je.  If t >= a+1: X~_t[E_t] alpha_t = 0 (E_t has no e), so X_t has rank <= 1 on E_t, and
     codim <= 1 + 2(t-a-1) + 1 = 2(t-a), giving Y-rank >= 4.  If t < a: the e row gives sum_{j<=t} x~_j alpha_j = 1, but (1) needs x~_j = 0 for j<a, so there is no Y-drop.
     If t = a: a Y-drop needs x~_{<a} = 0, and an X-drop needs y~_{<a} = 0. Then Y~_c^T delta_e = 0 for c<a, and the triangular recursion
     (2I-Q_c)A_c + Q_c A_{c-1} = 0 gives alpha_{<a} = 0. So delta_e = X~_a alpha_a with sum alpha = alpha_a = 0, a contradiction.
 Hence max(rank_X, rank_Y) on Z_I is 4 for EVERY interval across the death of a lone role, of any window length. The true cap is the rank-4 interval
 cap, and every lone role prices <= 0 (run2: -0.03..-0.05%). [C exact, win.py, sympy] Side check: for a 2-stage window block, every sum-zero vector of the
 window x's is a -1 eigenvector of the block (rank (A+I)|S0 = 0 identically). So b_K>0 costs nothing at the Gram level; the obstruction is the coordinate support used above.
F. Pair + slack (the remaining survivors) [P partial]. If the pair D enters at k < a and |U_k| = 2k+4, then X~_k[D] is invertible (F1 at k). The
 constraint functionals of D therefore always involve gamma_k, and the drop in (1) is <= #slack roles of Omega untouched by X_{<a} (<= 1 for one slack).
 So rank >= 3 there: the r=2 ceiling (+2.37%) is excluded, and the r=3 ceiling (+1.38%) stands. Intervals starting AT k (k>=1) are not covered. Not closed: the recursion
 in E needs Y~_c^T v = 0 for c<a, which fails because v carries D-content and D lies in Z_k.
Earlier RESULT lines (moved here): 3+1 L=4 nested control 0/14; balanced L=4 control 4/8 but B+lone role 0/12 (float solver cannot test this); rs3.py, t1.py, t2.py.

H. CORRECTION to F + reduction to one lemma [P].
 (1) Intervals starting AT the pair entry a=k>=1 with Z_I = U_{k-1}: rank(Y_I|Z_I) = rank(X_I|Z_I) = 2 EXACTLY. Every Y_s, s>=k, restricted to
     U_{k-1} = W_s x (fixed 2 x (2k+2) matrix): the columns X_0..X_{k-1}, X_r|H span R^{U_{k-1}} (F1), and G = +-W_s Z^T. Dually for X. So
     F's claim "rank-2 ceiling excluded" was wrong for k>=1. Conservative proved caps (run6.py: r = 4 - min(2,u), u = uncertified roles of
     Omega_a) give a ceiling of +2.19% (c=2 k=1 d=3 slack 0..3). 74/117 survivors are >= +0.5% (run6.out). k=0 survivors stay <= +1.38%.
 (2) Generalised kill [P, extends DYINGPAIR]: Delta = roles of U_d absent from Z_K. If all of Delta enters at one stage k', 2K+4-|Z_K| >= 1,
     and |U_{t-1}| <= 2t+2 for k'<t<=d, then no root exists (Step 1 on Delta, top index, recursion at k'). Example: single k=1 d=1 + slack at 1.
 (3) Reduction [P]. Across a death every Omega_a lies in Delta. A rank drop on Z_I needs a nonzero constraint row, i.e. X_{<K} touching Delta.
     By NESTPROOF L2 this means b_K = dim(V_K cap R^Delta) > 0. With b_K = 0 every interval has rank 4, and the whole menu prices <= +0.49% (run3/run4 'opt').
GAP LEMMA (hand-off; the only open piece). rho=2 two-arm root (NESTPROOF model: prefix commutation, product -I, t!=-1), left arm stages
 0..m-1, B-count masks |U_j| = 2j+4 plus ONE extra (slack) role s entering at je <= d-1, and a dying set D (|D| = 1 or 2, entering k, alive k..d).
 Delta = D u {s if s dies at K}, K = d+1 <= m-2. CLAIM: V_K cap R^Delta = 0, i.e. no nonzero v = sum_{j<=d} X~_j alpha_j with sum alpha = 0
 supported in Delta. Proved: Delta with a single entry stage and no slack entering in (k',d] [(2)]; lone s with no D [E: the rank stays 4
 even with b_K>0]. Open: (a) je <= k (s and D enter at different stages, or s enters before D); (b) k < je <= d-1 with top index t(v) in [je,d]
 (Step 3 has one spare dimension, |U_{t-1}| = 2t+3); (c) k=0, s dying at K, t(v) = a (PROOF F). If the CLAIM holds, slack is closed at <= +0.49%.
 If it fails, the best layout is pair k=1 d=3 + slack 0..3, with a ceiling of +2.19% [C-param, conservative caps]. The Block Rank Bound gives no kill (monotone).
 Suggested attack: (b) via a second top index on the Y side (dual v), or an exact mod-p search for v in a B-type root with one extra role.

## Part III. GAPLEMMA

Notation as in Parts I and II.
Delta = roles of U_d absent from Z_K (K = d+1 <= m-2), Delta_i = Delta cap U_i, B = V_K cap R^Delta (b = dim B),
B_{<=i} = {v in B : alpha_j(v) = 0 for j > i}, W_i := V_{i+1} cap R^Delta. Facts used: F1/F2 (Floor, valid for j <= m-2),
L1 (sum zero), L2 (splitting of V_K at K), Step 0 (2I - Q_c invertible), the recursion phi_c := Y~_c^T v = (2I-Q_c)A_c + Q_c A_{c-1}.

### P1. Delta-Floor Lemma [P]
For every 0 <= i <= d:  (a) W_i = B_{<=i};  (b) dim B_{<=i} <= |Delta_{i-1}| (Delta_{-1} = empty);  (c) dim B_{<=i} >= 2i+4 - |U_i \ Delta|.
Hence a root needs  |Delta_{i-1}| >= 2i+4 - |U_i \ Delta|  for every 0 <= i <= d.
Proof. (c) F1 at i: X_0..X_i, X_r|H are 2i+4 independent vectors; their span is S_i = V_{i+1} (+) R^H. Let pi delete the Delta
coordinates. If x + h lies in R^Delta (x in V_{i+1} <= V_K, h in R^H), split x by L2 at K: its R^{Z_K}-part is -h (H <= Z_K,
Delta <= N_K) and lies in V_K. F1 at d gives V_K cap R^H = 0, so h = 0. So ker(pi|S_i) = W_i and 2i+4 <= dim W_i + |U_i \ Delta|.
(a) x in W_i is supported off Z_K, so Y_K^T x = 0 and L1 gives sum-zero coefficients on stages <= i: x in B_{<=i}. The converse is clear.
(b) For x in B_{<=i}: A_i = 0. For c <= i-1, phi_c(x) = Y~_c[Delta cap Z_c]^T x only reads x on Delta_{i-1}. If x vanishes there, phi_c = 0
for c <= i-1 and the recursion (2I - Q_c invertible, A_{-1} = 0) gives A_0 = .. = A_{i-1} = 0. With A_i = 0 this means every alpha_j = 0, so x = 0. QED
Consequences [P, dfloor.py]: (i) every layout in which all own roles of the outermost entry stage die (k=0) fails at i=0 (|U_0 \ Delta| <= 3).
(ii) every PAIR (c=2) layout fails: k=1 with s entering 0 and dying at K fails at i=1 (|Delta_0| = 1 < 6-4). k=1 with s surviving, or entering at 1, also fails at i=1.
So GAP-LEMMA open cases (a),(b),(c) are CLOSED for pairs, and for singles with k=0. dfloor.py kills 102 of the 117 run6 survivors. The 15 left are all
c=1 k=1: family A (slack 0..d dying, d=1..5, run6 ceilings +1.58..+2.17%) and family A' (slack surviving, <= +0.97%).
[N check, loc2.py / chk2.py] With Lemma S + supports + block-diagonal P_K + b=2 but WITHOUT F1, the c=2 k=1 d=2 slack 0..2 left arm solves (22/40).
Every solution with t != -1 violates F1 at j=2 (a left x-combination is supported on the hubs), as P1 predicts. So F1 (the right witness) is the essential input.

### P2. Rank of the dying rows [P]
rank X_{<K}[Delta] <= b and rank Y_{<K}[Delta] <= b. Proof: block-diagonality at K gives X[Delta] R Y[Z]^T = 0 (Z = U_d \ Delta, R invertible).
Rows of X[Delta]R lie in ker Y[Z], which is {beta : Y beta in R^Delta} = (C(Y) cap R^Delta), of dim b (L3: P_K on R^{N_K} is I - 2 Pi, and
rank Pi = rank Pi^T). Dually for Y. Corollary: if no thin unit touches Delta, the rows of the total X on Delta are the left rows, and
product -I (X R Y^T = I_n) needs them independent: b = |Delta|. [C] the family-A d=1 local solution (locgen.py A1) has b=1 and X[D] = Y[D] = 0 exactly.

### P3. Family A (c=1, D = single entering 1, slack s on 0..d dying at K) [P]
P1 at i=1 gives dim B_{<=1} = 1, spanned by v1 = (X~_0 - X~_1) a with a != 0, so phi_0(v1) = (2I-Q_0)a = y~_0s v1_s forces y~_0s != 0.
Dually (the same lemma on the Y side; X~_0^T w = -Q_0^T Gamma_0, Q_0 invertible) x~_0s != 0.
(a) If b = 1: by P2 the D rows are proportional to the s rows; they vanish on stage 0 while x~_0s, y~_0s do not, so X[D] = Y[D] = 0:
    D is a PHANTOM (no content on the left arm; it only lives in thin units). Then D gives no constraint row, and SLACK PROOF E(1) on
    an interval [a,b] across the death with a >= 1 needs x~_0s = 0 (Y side) or y~_0s = 0 (X side): rank 4. Only a = 0 may drop (to 3).
    Priced with these proved caps (phantom_price.py): +0.37% (d=1), +0.23, +0.14, +0.08, +0.03% (d=5). All below +0.5%.
(b) If b = 2 (possible only for d >= 2, since b <= dim B_{<=1} + #{2<=t<=d : X~_t[E_t] singular} by the top-index filtration): R^Delta <= V_K,
    so e_s and e_D lie in V_K with sum-zero coefficients, and e_D has alpha_0 = 0 (phi_0(e_D) = 0). NOT closed. This is the only
    open piece of the >= +0.5% menu. (With thin units kept off Delta, b = 2 is forced, so family A d=1 dies and d >= 2 needs exactly this case.)

### P4. Caps in the open case (family A, b = 2) [P, uses SLACK PROOF E(1)]
Across the death, Omega_a <= {s, D}. A one-step drop on [a,b] needs a combination c_s(s-row) + c_D(D-row) of the constraint functionals with
c_s x~_js + c_D x~_jD = 0 for all j < a (E(1)). For a >= 1, j = 0: x~_0D = 0 and x~_0s != 0 (P3), so c_s = 0 and only the D row can drop: rank >= 3.
For a = 0 only s is touched by X_0: rank >= 3. So r >= 3 on every interval (run6 used r = 2). Priced (phantom_price.py): +0.97 (d=1, but d=1
cannot have b=2), +1.11 (d=2), +1.15 (d=3), +1.08 (d=4), +0.90% (d=5). Family A' (slack survives) stays <= +0.97% (run6 caps, already r = 3).
### P5. The open case is LOCALLY consistent [N, locgen.py A2b2, loc_A2b2_7.npy]
Left arm of family A d=2 (stages 0..2, 9 coords) with Lemma S, supports, x.y = 0, block-diagonal P_3 with P_3|Delta = -I_2, b = 2 sum-zero
vectors, F1 on the X and Y sides at j = 0,1,2 (with hub witness), and t = (-0.228, -0.775, -0.743): solved to 8.7e-15 (1 of 8 starts; the
b=1 spec A1 solved 1 of 4 with X[D] = Y[D] = 0, as P3(a) says). D is NOT a phantom there. So no argument confined to stages < K plus F1 can
close b = 2; a proof must use the stages >= K, the thin block or the right arm (e.g. Floor at K with rows Y_K, Y_K+1, or DYINGGEN Theorem 1 counts).
### P6. Extension round: reduction of the global question to the prefix M [P] + codimension [N]
Stages >= K, the right arm and (if b = |Delta|) the thin block never touch Delta, and P_K = diag(M, -I_Delta) with M = P_K|_{U_d \ Delta}.
So the total product is diag(Rest*M, -I_Delta*I) and every prefix commutation at stages >= K reads only Rest_partial*M. Lemma S is a
consequence of product -I, not an extra equation. Hence: a family-A root exists  <=>  (i) a left arm (3 stages for d=2) with P_K = diag(M,-I_2),
and (ii) a "rest" with Rest*M = -I, i.e. a root of the NON-dying layout L' = (B + one surviving extra role, one stage shorter) whose
first-two-stage prefix equals M. Since Delta is gone, L' has the same thin count.
[N codim.py] At loc_A2b2_7 the reachable set R = {M : diag(M,-I_2) = product of the masked left arm} has tangent dimension 33. The variety of
rank-4 prefixes on R^7 has dimension about 40, so R has codimension about 7. [N refac.py] A generic masked 2-stage M' is not refactorable (0/6 starts), which agrees with this.
So the open question is exactly whether the prefixes of L'-roots (a family whose dimension is unknown: no L' root has been built) meet R.
Not decided: no L' root exists in hand, the float solver fails at these sizes, and Groebner on the full system (hundreds of variables) is out of reach.

### HANDOFF (standalone; parked Nov 15)
Status: the slack/dying-role prize in the rho=2 two-arm B caller is NOT closed. Proved ceiling +1.15% (family A d=3, b=2); everything else is <= +0.97%.
OPEN QUESTION (exact). Family A = a single role D entering left stage 1, plus a slack role s on stages 0..d, both dead at K = d+1 (d >= 2), with b_K = 2
(R^{s,D} <= V_K). Let M = P_K restricted to U_d \ Delta (P_K = diag(M, -I_2)). Does some root of the non-dying layout L' (B + one surviving extra
role, one stage shorter, same thin count) have a first-two-stage prefix M' that lies in the reachable set R = {M : the masked 3-stage dying left arm
has P_K = diag(M,-I_2)}? R has codim ~7 among rank-4 prefixes on R^7 (d=2). Yes => family A exists (then price it, Block Rank Bound, PRICEKIT).
No => the caller closes at <= +0.97% (or <= +0.37% if A' also dies).
PROVED: P1 the Delta-Floor Lemma, which kills every pair layout and every k=0 layout (102/117 run6 survivors). P2 rank X[Delta] <= b_K, and b_K = |Delta| if thin units avoid Delta.
 P3 family A with b=1 => D is a phantom, <= +0.37%. P4 with b=2, rank >= 3 on every interval, <= +1.15%. P6 reduction to the prefix M (the rest sees only M).
TRIED / WHY IT FAILED: (1) a left-arm-only proof is impossible: locgen.py A2b2 gives a local root (8.7e-15, F1 on both sides, t != -1, D non-phantom).
 (2) refactoring generic masked 2-stage prefixes fails (refac.py 0/6), explained by the codim ~7 (codim.py: tangent dim 33).
 (3) no L' root was available. The float solver fails at L >= 4-6, and Groebner on the full system (hundreds of variables) is infeasible.
NEXT TECHNIQUE (most promising): build an EXACT L' root (B + 1 extra surviving role) with the DYINGEXACT build.py/ctlB.py pipeline (Sigma1 chain ->
 rank-2 splitting -> Schur block -> thin factorisation), extended by one role. Then compute the dimension of the L' prefix family at that root and
 test transversality against R (rank of [dPrefix | T_R]). If the sum spans the ambient space, Newton within the joint system gives a root, which can
 then be lifted mod p. For an obstruction instead: look for an invariant of M that every L' prefix satisfies (from Lemma S Gram with stage K, e.g. the
 2x2 E^T R~ data or Q_K) and that R violates. Compute it on loc_A2b2_7 vs a B-root prefix first.
