# Proof note: a root-word duality, a Gram-class floor for 16 to 24 deleted lines, flag-chain flattening, and exact frame and tile facts (no kappa)

Every claim carries one of: **[C]** exact computation reproduced by `check.py` (a PASS line per claim); **[P]** hand proof, re-derived line by line for this package; **[P+C]** both; **CONDITIONAL** (stated with its missing premise, not proved here). No kappa claim and no new word are made. Labels follow one rule: a verifier or package restriction is never called a law.

Label vocabulary: **SPEC** = a premise of the outer framework or a statement in the paper (quoted with file and line, checked by `check.py`); **package convention** = a choice of the existing construction that another legal object could replace; **verifier behaviour** = what the shipped checkers enforce; **derived** = follows from the others; **family assumption** = a hypothesis of this note only.

## 0. Quoted premises (checked against the repository by `check.py`, group Q)

| id | text | file:line | label |
|---|---|---|---|
| S1 | "its Fourier rank is d(L(S),L(T)), where d(L,L')=h-dim(L cap L')" | `notes/general-clifford-frames.tex:16` | SPEC (Clifford-frame family) |
| S2 | d(L_U,L_V)=dim U+dim V-2dim(U cap V) for subspace frames | `notes/general-clifford-frames.tex:27` | SPEC (Clifford-frame family) |
| S3 | "For U subset V, the exact transition T_V T_U^-1 has rank dim V - dim U" | `notes/general-clifford-frames.tex:67-68` | SPEC (Clifford-frame family) |
| S4 | "use one identical exact representative" at a common scalar gate | `notes/general-clifford-frames.tex:62` | package convention (not SPEC) |
| S5 | "assign an invertible R-linear operator ... called its frame" | `upstream/build/sections/03-motifs.tex:154` | SPEC |
| S6 | "A label is a nondegenerate subspace of a fixed bilinear space" | `upstream/build/sections/03-motifs.tex:203` | SPEC for the labelled construction; a choice of that construction |
| S7 | A_e = M_head(e) - M_tail(e), price rank_Q A_e | `upstream/build/sections/04-swap.tex:115`, `:197` | SPEC for the rational-matrix interchange contract only |
| S8 | "The number of directional kernels is precisely rho_edge" | `upstream/build/sections/05-layers.tex:82` | SPEC |

Consequence for pricing (derived from S1 and S7): the price used below, the F2 rank of the mask pairing, is the Clifford-frame family's Fourier-rank price. It is not the rank_Q price of S7, which belongs to the interchange contract. Nothing in this note uses rank_Q.

## 1. Theorem G: duality between isotropic transvection words and reflection words [P+C]

**Setting.** Work over a field of characteristic not 2 (checks: Q). A transvection is T = I - 2 x y^T with y^T x = 0 (isotropic); a reflection is r = I - 2 q p^T with p^T q = 1. For N transvections T_k = I_n - 2 x_k y_k^T put X = [x_1 ... x_N] (n x N), Y with rows y_k (N x n), G = Y X, so G_kl = y_k . x_l and diag G = 0. Let L be the strictly lower triangle of G, K = I + 2L (unit lower triangular, invertible) and Z = K - G = I + L - U, where U is the strictly upper triangle of G. Z has diagonal 1 and Z_ij = G_ij for i > j, Z_ij = -G_ij for i < j.

**Lemma G0 (product formula) [P+C].** For any vectors, T_N ... T_1 = I - 2 X K^-1 Y, where K = I + 2 L(G) and only the strictly lower triangle of G = YX enters (the diagonal never does).
*Proof.* Induction on N. N = 1: K = 1. Step: write W_m = T_m ... T_1 = I - 2 X_m K_m^-1 Y_m and g = (y_{m+1}.x_1, ..., y_{m+1}.x_m). Then y_{m+1}^T W_m = y_{m+1}^T - 2 g K_m^-1 Y_m, so W_{m+1} = T_{m+1} W_m = I - 2 [X_m x_{m+1}] [[K_m^-1, 0], [-2 g K_m^-1, 1]] [Y_m; y_{m+1}^T], and the middle matrix is the inverse of K_{m+1} = [[K_m, 0], [2g, 1]]. QED

**Theorem G.** Let N = n + rho. (a) If T_N ... T_1 = -I_n with every T_k isotropic, then rank Z = rho, and any rank factorisation Z = P Q^T (P, Q of size N x rho, rows p_i, q_j) gives p_i . q_i = 1 and reflections r_i = I_rho - 2 q_i p_i^T with r_N ... r_1 = -I_rho. (b) Conversely, reflections r_i = I_rho - 2 q_i p_i^T (p_i . q_i = 1) with r_N ... r_1 = -I_rho, put Z = P Q^T, define G by diag 0, G_ij = Z_ij (i > j), G_ij = -Z_ij (i < j). Then rank G = N - rho = n, and any rank factorisation G = Y X gives isotropic transvections with T_N ... T_1 = -I_n. (c) The two assignments are inverse bijections between GL_n-gauge classes of transvection words and GL_rho-gauge classes of reflection words: a class on either side is determined by its matrix G, respectively Z, and G and Z determine each other.

*Proof.* (a) By Lemma G0, the product is -I iff X K^-1 Y = I_n. Then E := K^-1 G = (K^-1 Y) X satisfies E^2 = K^-1 Y (X K^-1 Y) X = E, and K^-1 Y, X have rank n, so rank E = n. Hence K^-1 Z = I - E is idempotent of rank N - n = rho, and rank Z = rho. Z_ii = 1 gives p_i . q_i = 1. The reflection word has Gram matrix (p_i . q_j) = Z, whose strictly lower triangle equals that of G, so Lemma G0 (diagonal never enters) gives r_N ... r_1 = I - 2 Q^T K^-1 P with the same K. Now A := K^-1 P (rank rho, left-invertible) and B := Q^T (right-invertible) satisfy A B A B = A B (idempotence of K^-1 Z = A B), hence B A = I_rho, i.e. Q^T K^-1 P = I_rho and r_N ... r_1 = -I_rho.
(b) By Lemma G0 the reflection product is -I iff Q^T K^-1 P = I_rho. This forces rank P = rank Q = rho, so rank Z = rho, and K^-1 Z = (K^-1 P) Q^T is idempotent. Then E := I - K^-1 Z = K^-1 G is idempotent of rank N - rho = n, and rank G = n. For G = Y X (rank factorisation), E^2 = E reads (K^-1 Y)(X K^-1 Y) X = (K^-1 Y) X; cancelling the left-invertible K^-1 Y and the right-invertible X gives X K^-1 Y = I_n, so T_N ... T_1 = -I_n by Lemma G0; y_k . x_k = G_kk = 0.
(c) Gauge changes x -> g x, y^T -> y^T g^-1 fix G, and a rank-n factorisation of G is unique up to GL_n; likewise for Z. The maps G <-> Z are mutually inverse linear bijections between {diag 0} and {diag 1}. QED

**Checks [C]** (`checks/duality.py`, exact rationals): both directions and the product -I on the reduced words of w_0 for D4 (N = 12, rho = 4, n = 8), B3 (9, 3, 6), F4 (24, 4, 20), I2(4) and I2(6) (rho = 2), and on random rho = 2 words with N = 6, 8, 10, 12 (closed by solving for the last two reflections); a perturbed word fails on both sides.

**Corrections kept from the independent read.** (i) The idempotent of rank n is E = K^-1 G; it is I - E = K^-1 Z that has rank rho = N - n. (ii) The correspondence is on gauge classes, not on tuples. (iii) K is always invertible; characteristic not 2 enters only through the factor 2 in K.

**Not claimed.** The dictionary built on Theorem G (moduli count 2(rho-1)(n-1), the real-window law for three hosted pairs, and the Fricke and Margulis citations behind it) is not part of this note: those citations are not checkable inside the package, so the real-window statement is dropped.

## 2. Theorem O: a Gram-class floor for 16 to 24 deleted lines [P+C]

**Model (family assumption, definitions).** Lines: the 120 root lines l_p of E8, scaled so that norm is 8 in the checker's coordinates (inner product ip(l_p,l_q) in {0, +-1, +-2} after dividing by 4). Mask: N[p,q] = 1 iff ip(l_p,l_q) is even (orthogonal or equal); rank_F2 N = 9 [C]. Labels: a map p -> label(p) in F2^9 and a nondegenerate symmetric form with N[p,q] = <label(p), label(q)> [C: the form <(a,v),(b,w)> = ab + v C w, C the Cartan matrix mod 2]. For a set P = lines minus D (|D| = d) a **Gram-class design** is a family of terms (u_k, w_k), u_k, w_k in C^8 (any number n >= 8 of terms), with M = sum_k u_k w_k^T invertible. Term k has top support S_k = {p in P : l_p . u_k != 0}, bottom support T_k, price rho_k = rank_F2 N[S_k, T_k], and the cost is c = sum_k rho_k. (A decoder O = E M E^T with N o O = I is of this form with M = I up to scale; allowing every invertible M only strengthens the statement.) The F2 rank price is the Clifford-frame family's price (S1, section 0).

**Theorem O.** For every D with 16 <= |D| <= 24 and every Gram-class design on P = lines minus D, c >= 56. Hence v - c <= (120 - |D|) - 56 = 64 - |D| <= 48, with v = |P|. At |D| = 16 the bound 56 is attained by an explicit design (data/p104_pairs.json), so v - c = 48 there.

*Proof.* Write a_k = 9 - dim span label(S_k) and b_k likewise for T_k.
1. *Cauchy-Binet [P].* M = U W^T with U, W the 8 x n matrices of the u_k, w_k; det M = sum over 8-subsets K of det U_K det W_K. Since det M != 0, some K has {u_k} and {w_k} both bases of C^8. All prices are nonnegative, so c >= sum_{k in K} rho_k.
2. *Sylvester [P].* N = L G L^T over F2 with L the 120 x 9 label matrix and G the invertible form (labels span F2^9 because rank N = 9). So rho_k = rank(L_S G L_T^T) >= dim span label(S_k) + dim span label(T_k) - 9 = 9 - a_k - b_k.
3. *Domination [P].* Let u != 0 and orth(u) = {p : l_p . u = 0}. Let X be the intersection of the root hyperplanes containing u (a flat of the arrangement, defined over Q, so the complex case is its complexification). The arrangement restricted to X is essential (the intersection of all root hyperplanes is 0), so X contains a ray r, and orth(u) is contained in orth(r), hence T(r) (the lines not orthogonal to r) is contained in T(u). Therefore span label(T(u) minus D) contains span label(T(r) minus D), i.e. a(u; D) <= a(r; D).
4. *Census [C].* W(E8) acts on the lines by isometries, hence preserves N, hence preserves dim span label(S) (it equals rank_F2 N[S, all lines]). Every ray of the arrangement is conjugate to one of the 8 fundamental-weight rays (a vector in the closed chamber lies on a 1-dimensional flat only at an extreme ray). For each of these 8 rays the cost cost_a(r) = |T(r)| - max over codimension-a subspaces W of F2^9 of #{p in T(r) : label(p) in W} is the least number of deleted lines that makes a >= a. [C] The values (|T|, cost_1, cost_2) are (57,1,25), (78,14,42), (83,27,51), (92,28,56), (97,33,61), (98,35,62), (104,40,68), (106,43,70); in particular cost_2 >= 25 for all 8 rays.
5. *Assembly [P].* If |D| <= 24 then a(u; D) <= 1 for every vector u: otherwise step 3 gives a ray r with a(r; D) >= 2, and D would contain at least cost_2(r) >= 25 lines of T(r) (step 4). The same holds for the bottoms. By step 2, rho_k >= 9 - a_k - b_k >= 7, and by step 1, c >= 8 * 7 = 56. With v = 120 - |D|, v - c <= 64 - |D|, which is <= 48 when |D| >= 16. QED

**Checks [C]** (`checks/omega_floor.py`): rank_F2 N = 9; labels reproduce N on all 14,400 pairs; sum of l l^T = 120 I (tight frame; the per-unit trace constant is 120/8 = 15, not used above); the census table; the design data (16 distinct lines, y_k . z_l = 0 for k != l, y_k . z_k = +-1, dual basis of the y_k proportional to the z_k); c = 56 with every rho_k = 7 on the 104 lines, c = 72 with every rho_k = 9 for the same eight terms on all 120 lines, c = 72 for generic dual bases, c = 64 for an orthoframe on its complement; 231 random designs with 16 <= |D| <= 24 (including D containing the 16 pair lines) satisfy the Cauchy-Binet subset, a <= 1, the Sylvester bound and c >= 56.

**Scope (what is not claimed).** (i) |D| <= 15: the argument above gives c >= 56 only, which is weaker than 72 - |D|; the bound v - c <= 48 for the P111 and P112 port sets is not claimed. (ii) |D| >= 25: a >= 2 becomes possible (cost_2 = 25) and the bound would need joint counts of the high-codimension stars; those counts are not part of this note. (iii) Carriers outside col(E) (tops or bottoms not of the form E u), other line systems (E7, E6, D_n have different values), plane ports, and any price other than the F2 mask rank. (iv) The theorem is about the Gram model; it says nothing about an actual word whose owned layer is not shown to be a Gram design (see Theorem F and its conditional corollary). (v) Port sets other than subsets of the 120 E8 lines.

## 3. Theorem F: flag chains flatten onto the mask at no higher price [P+C]

**Model (family assumption).** Ports have labels in F2^9 with the form of section 2, N[s,p] = <label(s), label(p)>. A *flag chain* is a program whose frames descend, F_0 contains F_1 contains ... contains F_m (subspaces of F2^9), with events in this time order: a *read* at level i adds a vector r_i to an accumulator, supported on ports p with label(p) in F_i; a *write* at level j adds the current accumulator, scaled by a vector w_j supported on ports s with label(s) orthogonal to F_j, into s. The price of the chain is the sum of move ranks, which telescopes to dim F_0 - dim F_m (S3 for nested frames). The read and write support rules are the family's pinning rules (ports read inside the frame, written on its orthogonal complement); they are not a SPEC clause.

**Theorem F.** Let w = sum of all write vectors and r = sum of all read vectors, and let X[s,p] be the coefficient with which p's read reaches s's write. Then N o X = N o (w r^T), and the chain's price dim F_0 - dim F_m is at least rho(supp w, supp r) = rank_F2 N[supp w, supp r].
*Proof.* Suppose N[s,p] = 1 and p is read at level i, s written at level j, with the read after the write in time. Levels are non-decreasing in time, so i >= j, label(p) in F_i, F_i contained in F_j, and label(s) is orthogonal to F_j, so N[s,p] = <label(s), label(p)> = 0, a contradiction. So on N pairs every read precedes every write, X[s,p] = (sum of writes at s)(sum of reads at p) = w(s) r(p). Price: all reads lie in F_0 and all writes in F_m^perp; the pairing of F_m^perp with F_0 under a nondegenerate form has rank dim F_0 - dim(F_0 cap F_m) = dim F_0 - dim F_m. QED

**Checks [C]** (`checks/flatten.py`, ports = all 120 lines): on 60 random nested chains (depth 1 to 4, reads and writes interleaved) N o X = N o (w r^T) at every N entry (13,376 nonzero entries tested) and the price bound holds; control: with non-nested frames the identity fails on 37 of 60 random programs.

**Corollary F2 [P, CONDITIONAL on its hypothesis].** Suppose a word is a disjoint union of flag chains whose flattened terms (w_k, r_k), after a diagonal sign gauge on ports (which does not change supports), form a Gram-class design on P = lines minus D with 16 <= |D| <= 24. Then its total price is at least sum_k rho(supp w_k, supp r_k) >= 56 (Theorem O). Every floor proved for rank-one decompositions in the Gram class therefore transfers to such flag networks of any staging depth. Membership of a particular word in this class is not shown here, and non-flag networks (forks with reads or writes after the fork, relays, owned ascent) are outside the corollary.

## 4. The naive transfer fails at A2 [C + P]

Statement tested: "if sum_k a_k b_k^T is N-diagonal with nonzero diagonal, then sum_k rho_k is at least the Gram value." On A2 (the three lines e1-e2, e2-e3, e1-e3 in the plane x+y+z = 0; inner products +-1, so N = I_3) a Gram-class design (a_k = E u_k, b_k = E w_k, sum u_k w_k^T = the projector onto the plane) costs at least 4, while the identity decoder O = I_3 (three terms e_p e_p^T, each of price 1) has N o O = I and costs 3. So the statement is false as written, and holds only after padding or restricting the carriers.
*Proof of c_Gram(A2) >= 4 [P with exact checks].* A plane vector is orthogonal to at most one line, so supports have size 2 or 3 and every term has price rho = |S cap T| >= 1; price 1 iff u is orthogonal to a line i and w to a line j != i. Rank 2 needs at least two terms, so total price <= 3 leaves the price multisets (1,1), (1,1,1), (1,2). The first two never sum to the projector (exact linear algebra over all 6 term types, repeats allowed). For (1,2): a price-1 term lambda u w^T leaves a remainder Pi - lambda u w^T of determinant 1 - lambda (w.u) on the plane, which must vanish; the remainder is then u_B w_B^T with u_B proportional to line j and w_B to line i, supports 3 x 3, price 3, never 2. The forced remainder also attains cost 4. [C] `checks/a2.py`.
A4 (c_Gram >= 12 against the identity decoder 10) is not part of this note.

## 5. Lagrangian frames: the geodesic interval and a 1-Lipschitz retraction [P + C for h <= 4]

Notation: vectors of F2^h x F2^h are written (x, z); the symplectic form is x.z' + z.x'; L_0 = {(0,z)}, L_F = {(u,u)}; for a subspace U, L_U = {(u, u+v) : u in U, v in U^perp}; d(L,L') = h - dim(L cap L') (S1, S2).

**Theorem I [P+C].** A Lagrangian L lies on a geodesic from L_0 to L_F, i.e. d(L_0,L) + d(L,L_F) = h, iff L = L_U for a subspace U. Hence the subspace frames are exactly the interval.
*Proof.* If dim(L cap L_0) + dim(L cap L_F) = h, then, because L_0 cap L_F = 0, L = (L cap L_0) + (L cap L_F), say L = {(0,z): z in Z} + {(w,w): w in W}. Isotropy of (0,z) and (w,w) gives z . w = 0, so Z is contained in W^perp, and dimension h gives Z = W^perp, L = L_W. Conversely dim(L_W cap L_0) = h - dim W and dim(L_W cap L_F) = dim W. QED

**Theorem R [P+C].** rho(L) := L_{pi_1(L)}, with pi_1(L) = {x : (x,z) in L for some z}, is a retraction of all Lagrangians onto {L_U} that does not increase the adjacency distance: for L, L' with dim(L cap L') = h - 1, d(rho L, rho L') <= 1.
*Proof.* Since L is Lagrangian, L cap L_0 = {(0,z) : z in pi_1(L)^perp}, so pi_1(L) is determined by Z = L cap L_0. Let M = L cap L', Z = L cap L_0, Z' = L' cap L_0. If a in Z minus L' and b in Z' minus L existed, then a, b are orthogonal (L_0 isotropic), both orthogonal to M (a in L, b in L'), so M + <a,b> is isotropic; its dimension exceeds h unless a + b lies in M, which forces b = (a+b) + a in L, a contradiction. So Z is contained in L' (hence in Z') or Z' is contained in L (hence in Z): the two are nested, and as Z' cap L = Z cap L' their dimensions differ by at most 1. With U = pi_1(L), V = pi_1(L') nested of dimensions differing by at most 1, S2 gives d(L_U, L_V) = |dim U - dim V| <= 1. rho fixes every L_U since pi_1(L_U) = U. QED

**Checks [C]** (`checks/lagr.py`, exhaustive for h = 1, 2, 3, 4): |LG(h)| = 3, 15, 135, 2295; Theorem I; the distance formula S2 on all pairs of subspaces; d equals the graph distance (all sources for h <= 3, two sources for h = 4); pi_1(L) = (L cap L_0)^perp; rho fixes every L_U; zero violations of d(rho L, rho L') <= 1 over all 68,850 ordered adjacent pairs at h = 4. The proofs above are for every h; the checks cover h <= 4.

**Consequence for networks [CONDITIONAL].** Replace every gate frame by rho of it: terminals in the family are fixed and no edge rank (S1) rises. This reading needs two premises not proved here: every Lagrangian is the label L(T) = T^-1 L_0 of an exact Clifford operator T (S1), and the network's functional identity depends only on its terminal frames (the common-frame identity of S5). The claim "d is the graph distance for every h" is standard for dual polar graphs and is checked for h <= 4.

**Exact tile caps [C]** (`checks/caps.py`). For the 104 lines left after deleting the 16 lines of data/p104_pairs.json, labels in F2^9, a subspace A of dimension a and B = A + <w> of dimension a + 1, let area(A,B) = #{ports with label in A} x #{ports orthogonal to B}. Over all subspaces (exhaustive; 43,435, 788,035 and 3,309,747 subspaces, equal to the Gaussian binomials) the maximum area is 32 = 2 x 16 for (a, a+1) = (2,3), 32 = 4 x 8 for (3,4), and 36 = 6 x 6 for (4,5). These are counting facts about this port set. That every tile of a geodesic main is dominated by such a linear tile is not claimed here.

## 6. Owned lifetimes: the Schur law, and the leak identity [P+C]

**Schur law (linear algebra).** Let T_f be an invertible matrix on cells P + O (rows are output cells, columns input cells), where each owned lifetime i is born at an input cell in O_b and dies at an output cell in O_d, |O_b| = |O_d|. Define the public map by compression, T_pub = T_f[P,P] (owned inputs zero, owned outputs discarded; **package convention**, the stated definition of T_pub). Then T_pub is invertible iff Tinv_f[O_b,O_d] is, and then
Tinv_pub = Tinv_f[P,P] - Tinv_f[P,O_d] Tinv_f[O_b,O_d]^-1 Tinv_f[O_b,P].
*Proof.* Jacobi's complementary-minor identity gives det T_f[P,P] = det T_f . det Tinv_f[O_b,O_d] up to sign, and the inverse of a block of T_f is the Schur complement of the complementary block of Tinv_f. QED. [C] `checks/schur_leak.py`: exact on 58 random instances and on 22 singular ones. Word-level replays of this law are not part of the package.

**Leak identity (elementary).** At a cut T = B A and for each register i define the four rank-one terms f_i[y,x'] = B[y,i] A[i,x'], r_i[x,y'] = Ainv[x,i] Binv[i,y'], L_X,i[x,x'] = Ainv[x,i] A[i,x'], L_Y,i[y,y'] = B[y,i] Binv[i,y']. Then sum_i f_i = T[Y,X], sum_i r_i = Tinv[X,Y], sum_i L_X,i = I, sum_i L_Y,i = I, and entrywise
L_X,i[x,x'] L_Y,i[y,y'] = r_i[x,y'] f_i[y,x']
(a product of the same four numbers). All four terms are invariant under a diagonal rescaling of the registers. Consequence, stated with its scope: if register i carries both a nonzero forward term f_i[y,x'] and a nonzero reverse term r_i[x,y'] on the quadruple (x,x',y,y'), then both of its leak entries L_X,i[x,x'] and L_Y,i[y,y'] are nonzero. It says nothing about cancellation across several registers. [C] `checks/schur_leak.py`: exact on 40 random cuts.

## 7. Hypothesis ledger

| item | statement | label |
|---|---|---|
| H-field | characteristic not 2, rational checks | derived (the factor 2 in K) |
| H-F2 | rank_F2 of the mask pairing is the price | SPEC for Clifford frames (S1, S3); package convention for the 120-line mask N |
| H-N | N = even inner product mask on the 120 E8 lines | family assumption (the unit) |
| H-Gram | tops and bottoms in col(E), M invertible | family assumption; Theorem O does not cover carriers outside it |
| H-pin | reads inside the frame, writes on its orthogonal complement | family assumption (pinning rule), not SPEC |
| H-chain | a chain is a disjoint nested flag; edges disjoint between chains | family assumption |
| H-rep | one identical exact representative per gate | package convention (S4), not SPEC |
| H-lab | labels are nondegenerate subspaces | SPEC for the labelled construction; a choice of it (S6) |
| H-Cliff | every Lagrangian is a frame label; common-frame identity | SPEC premises (S1, S5), used only in the conditional reading of Theorem R |
| H-compress | T_pub = T_f[P,P] with owned inputs zero, outputs discarded | package convention |
| H-nested | descent only; ascent breaks Theorem F (control in section 3) | derived (Theorem F proof) |
