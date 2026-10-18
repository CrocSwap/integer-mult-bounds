# Gauge rigidity of rank-8 E-graph-exact complex decoders

Every finite fact used below is marked **[check: X]** and is recomputed by `verify.py` (check id `X`),
with exact integer, F2 or rational arithmetic. One step (Lemma 4) is a propositional refutation that
`verify.py` replays from a shipped DRUP proof with its own unit-propagation checker. Everything else is
written argument. No step cites a SAT solver's answer. Numbers marked *(recorded)* are reported from
runs that `verify.py` does not repeat and are not load-bearing.

## 0. Setting and statement

The 120 root lines of E8 are represented by roots `r_i` of norm 2; `G_ij = <r_i, r_j>` is the integer Gram
matrix, with off-diagonal values in {0, +-1} **[check: A.gram-offdiag]**. Two distinct lines are
*orthogonal* if `G_ij = 0` and *odd* if `G_ij = +-1`. The label pairing of PR717 (B14 model) and PR968 is
`N_ij = (G_ij + 1) mod 2`: it is 1 on the diagonal and on orthogonal pairs (the *E-graph*) and 0 on odd
pairs; it has F2-rank 9 with distinct rows **[check: A.label-rank]**, and it equals the Gram matrix of
PR717's labels `u_i` in F2^9 under the form S9 by PR968, PROOF.md eq. (1).

A live set L is P120 (all lines) or P112 (all lines but the frame FRAME0 = {e_2a +- e_2a+1}, the frame of
PR717's `e8model.py` in the standard coordinates).
An element w of W(E8) permutes the lines and maps the Gram matrix to `S G' S` for a diagonal sign matrix S
(`G_{π(i)π(j)} = s_i s_j G_ij`, the signs coming from the chosen root representatives), so it preserves the
diagonal, orthogonality, the pairing N and the rank condition, and sign matrices lie in the diagonal torus:
if K solves (E) on w(L) then `Pᵀ K P` solves (E) on L, and `K = D (2G) D^{-1}` transports to the same form.
Since W(E8) acts transitively on the 2025 frames of E8 **[check: B.frame-transitivity]**, Theorem 1 for P112
holds verbatim for the complement of any frame — in particular for the Hamming coordinate frame {2e_i} that
the shipped complex word punctures (PR717 README row Y1), as well as for PR717's FRAME0.

**E-graph exactness (PR717 D1(a)).** In the copy-cost model a term whose row and column supports are
label-orthogonal costs 0. Every odd pair is label-orthogonal, so each odd entry of the target `2G` can be
fixed by a single cost-0 term. The costly terms `x_k y_k^T` therefore only have to satisfy

    K := sum_k x_k y_k^T,   K_ii = 4,   K_ij = 0 whenever r_i and r_j are orthogonal,          (E)

with the entries of K on odd pairs free. A decoder with exactly 8 costly terms has `rank K <= 8`.

**Theorem 1 (rigidity).** Let L be P112 or P120 and let K be a real L x L matrix of rank at most 8 that
satisfies (E). Then `rank K = 8` and there is a diagonal matrix D with nonzero diagonal such that

    K = D (2 G_L) D^{-1},     i.e.  K_ij = 2 G_ij d_i / d_j .

In particular no odd entry of K vanishes, and the solution set of (E) in rank 8 is a single orbit of the
diagonal torus.

**Corollary 2 (eight costly terms in the E-graph model).** On P112 every decoder with exactly 8 costly terms
has copy cost `cst >= 64`, and on P120 `cst >= 72`. More precisely the costly terms have PR968's normal form:
`x_k = D R a_k`, `y_k = D^{-1} R b_k` with `A B^T = 2 I_8`, so their supports are `C(a_k) ∩ L` and
`C(b_k) ∩ L` (the live lines not orthogonal to the normals), and PR968's theorem applies to `(RA, RB)`.

What this adds to the record. PR717 D1(b) obtains `cst >= 64` for exactly eight costly terms on P112 from a
census of hyperplane-flat complements; the step "the costly supports are hyperplane-flat complements
(fundamental-weight orbits)" is recorded there as ARGUED from the tangent-space rigidity (d) plus the orbit
census, with global rigidity only sampled (10 of 12 random starts, RECORDED). That step does not hold for a
general dual basis: the supports `C(a_k)` of Corollary 2 are hyperplane-flat complements only when the roots
orthogonal to `a_k` span a hyperplane, and a sampled dual basis has normals whose orthogonal roots span at
most six dimensions **[check: E.sample-normals]**. Theorem 1 proves the global rigidity statement, and
Corollary 2 replaces the flat-support step by PR968's normal form, whose puncture theorem (a census for
hyperplane-flat normals together with its Lemma 1 for all other normals) carries the floor. So the conclusion
of D1(b) is a theorem by a different route, and PR968's eight-term floor, proved there under all-pairs
exactness, holds under E-graph exactness for decoders with exactly eight costly terms, for p = 0 and for the
puncture of any frame.

## 1. Pivot reduction

Fix a live frame F: eight mutually orthogonal live lines. For f, f' in F, (E) gives `K[F, F] = 4 I_8`, so
`rank K >= 8`, hence `rank K = 8`. A rank-8 matrix with a nonsingular 8 x 8 submatrix on rows F and
columns F equals `K[:, F] K[F, F]^{-1} K[F, :]`, so

    K = (1/4) K[:, F] K[F, :].                                                               (1)

Write `a_i := K[i, F]` and `b_j := K[F, j]^T` (vectors in R^F). Then `K_ij = (1/4) a_i . b_j`, and (E) becomes

    a_f = b_f = 4 e_f  (f in F),      a_i . b_i = 16,      a_i . b_j = 0  (i != j orthogonal).       (2)

For a non-pivot line i and a pivot line f orthogonal to i, `a_if = K_if = 0`; so a_i and b_i are supported on

    T_i := { f in F : G_if != 0 }.

Conversely, if vectors a_i, b_j supported on F satisfy (2) then `K_ij := (1/4) a_i . b_j` satisfies (E) and has rank <= 8.

The pivot used by `verify.py`: for P120, F = FRAME0; for P112, F is the even class of one FRAME0-block
together with the even class of the complementary block (Section 2 explains these words), so that the
eight punctured lines are two whole classes relative to F, both fully punctured
**[check: A.pivot-frame, B.punctured-classes]**. The choice matters: Lemmas 3, 5 and 6 need every live
non-pivot line to lie in a complete class, and among the 1260 live frames of P112 only 28 have this property
(for a generic live frame eight classes lose one line each) *(recorded, from a reviewer's re-implementation)*;
one such pivot suffices.

## 2. D4 blocks relative to the pivot

**Lemma 2.** Relative to a frame F:

(a) every one of the 112 non-pivot lines i is odd to exactly four pivot lines and orthogonal to the other
four, and its inner products with the four are +-1 **[check: A.pivot-odd-four, A.pivot-signs]**. Write
`eps_i = (G_if)_{f in T_i}` in {+-1}^4 for its sign vector (defined up to the overall sign of r_i).

(b) The 14 distinct supports T form the Steiner system S(3,4,8) on F: any three pivot lines lie in exactly
one block, any two in exactly three, two distinct blocks meet in 0 or 2 points, and the complement of a
block is a block **[check: B.blocks-14, B.steiner]**. Each block carries 8 of the 112 non-pivot lines. The
parity of the number of minus signs in eps_i splits them into two *classes* of four; each class is a 4-frame
(four mutually orthogonal lines) and its 4 x 4 sign matrix `H_C = (eps_if)` has orthogonal rows and
orthogonal columns, i.e. is a Hadamard matrix **[check: B.classes-28, B.class-4frames, B.hadamard]**.
(The eight lines of a block together with its four pivot lines — twelve lines, 24 roots — form a D4 root
system, whose three mutually odd 4-frames are the pivot lines and the two classes.)

(c) Orthogonality rule: for distinct non-pivot lines, `|T_i ∩ T_j|` is 0, 2 or 4 and

    2 G_ij = sum over f in T_i ∩ T_j of eps_if eps_jf .                                                (3)

So i and j are orthogonal iff the overlap is empty, or the overlap is a pair {k, k'} with
`eps_ik eps_jk = - eps_ik' eps_jk'`, or the overlap is the whole support and i, j lie in the same class
**[check: B.orthogonality-rule]**. (For the last case: rows of the same class differ in an even number of
positions, two for distinct rows of a Hadamard matrix, giving `G_ij = 0`; rows of different classes differ
in an odd number d of positions, so `2 G_ij = 4 - 2d = +-2`.)

(d) In each complete live class (the only ones used below) and for each pair of columns {c, c'} of its
support, the products `eps_ic eps_ic'` take the value +1 on two rows and -1 on the other two
**[check: B.groups]** (columns of a Hadamard matrix are orthogonal). Call the two pairs of rows the *groups* of (C, {c, c'}). Two rows of one class have the same
parity, so the product of their entrywise products over all four columns is +1; hence the pairing for
{c, c'} equals the pairing for the complementary column pair. The three pairings so obtained are three
distinct perfect matchings of the four rows **[check: B.three-matchings]**: if the pairings for {a, b} and
{a, c} coincided, two rows i, j of a common group would satisfy
`eps_ia eps_ja = eps_ib eps_jb = eps_ic eps_jc`, hence also `eps_id eps_jd` equals that value (parity), so
`eps_i = +- eps_j`, contradicting the orthogonality of the rows of H_C.

(e) For P112 with the pivot of Section 1, the eight punctured lines are exactly two whole classes, in a block
and in its complementary block, and the remaining 26 classes are complete and live; for P120 all 28 classes
are complete. In both cases every block has a complete live class and every live non-pivot line lies in
one **[check: B.punctured-classes, D.block-live-class, D.complete-classes]**.

*Proof of (a).* `sum_f G_if^2 / 2 = |r_i|^2 = 2` because `f/sqrt2` is an orthonormal basis; `G_if = +-2`
would mean `r_i = +-f`, so exactly four entries are +-1. (b)-(e) are finite computations; the rule (3) is the
expansion of `<r_i, r_j>` in that orthonormal basis.  ∎

With Lemma 2, the equations (2) for non-pivot lines read:

    (E2)  a_ik b_jk + a_ik' b_jk' = 0           for i ⊥ j with  T_i ∩ T_j = {k, k'};
    (E4)  sum_{f in T} a_if b_jf = 0            for i != j in the same class (support T);
    (E0)  a_i . b_i = 16;

and there is no equation for odd pairs or for pairs with disjoint supports.

## 3. Class matrices

**Lemma 3.** Let C = {i_1, .., i_4} be a complete live class with support T, and let `A_C = (a_{i_p f})` and
`B_C = (b_{i_p f})` (4 x 4, rows indexed by the class, columns by T). Then `A_C B_C^T = 16 I_4`; in
particular A_C and B_C are nonsingular and `B_C = 16 A_C^{-T}`.

*Proof.* (E4) and (E0).  ∎

## 4. Zero exclusion

**Lemma 4.** For every live non-pivot line i and every f in T_i: `a_if != 0` and `b_if != 0`.

*Proof.* Consider the pattern of zero entries of all a_i and b_i on their supports (2·4·|L∖F| Boolean
unknowns, plus auxiliary variables: Tseitin equivalences for the products, and one-directional selectors for
the transversals, which can always be set consistently for a pattern that satisfies the condition). The following conditions are necessary for the pattern of any solution
of (2):

- (Z2) from each equation (E2), in both orders (a_i.b_j and a_j.b_i): the two products are both zero or both
  nonzero (if exactly one vanished the sum could not);
- (Z4) from each equation (E4): not exactly one of the four products is nonzero;
- (Z0) from each (E0): some product `a_if b_if` is nonzero;
- (ZT) from Lemma 3: the zero patterns of A_C and B_C of every complete class admit a transversal (a
  permutation of positions all nonzero), since a 4 x 4 matrix whose every transversal contains a zero is singular.

`verify.py` writes these conditions as a CNF with deterministic variable numbering, asserts the clause-family
counts and the digest of the CNF (a regression pin against the builder, not a certificate of necessity — that
rests on the four families being necessary conditions, as listed above) **[check: C.cnf-size, C.cnf-digest]**, and checks that the empty pattern
satisfies it **[check: C.trivial-pattern-satisfies]**. Conjoined with the clause "at least one entry is
zero", the CNF is unsatisfiable: the shipped file `proof-<L>.drup` is a reverse-unit-propagation refutation,
and `verify.py` replays it with its own propagation routine (deletion steps are ignored, which only enlarges
the clause database and keeps the replay sound) **[check: C.rup-refutation]**. Hence the only zero pattern
compatible with (2) is the empty one.

Only (Z2) and (Z0) are needed: the reduced CNF with just the two-term and diagonal families (its counts and
digest asserted as well) is refuted by the shipped `proof-<L>-two-diag.drup`
**[check: C.cnf-size-reduced, C.rup-refutation-reduced]**. So Lemma 4 does not depend on Lemma 3; (Z4) and
(ZT) are included in the full CNF only as additional necessary conditions. ((Z2) together with (ZT) alone
also suffices *(recorded)*.)  ∎

Remarks. Unit propagation alone refutes none of the 832 (P112) / 896 (P120) single-zero hypotheses
*(recorded)*; the refutation needs case analysis, which is why it is shipped as a proof rather than written
out. A deletion-minimal unsatisfiable core for one representative hypothesis (the variable ('a', 4, 2): line
4 and pivot line 2 in the global line numbering, on P112) still contains 380 of the 5076
equation groups — 311 two-term equations, 12 four-term equations, 37 diagonal conditions and 20
transversal conditions — over 73 lines *(recorded)*, so no short hand argument is offered. Any solver can
regenerate the proofs from the DIMACS file written by `verify.py --dimacs`; `make_proof.py` does so with
python-sat. The controls of Section F show that the checker rejects a proof with an inserted non-RUP lemma
and a proof truncated before its empty clause (a corruption that happens to leave every lemma RUP would,
correctly, still be accepted), and that the refutation genuinely uses the "some zero" clause.

## 5. Within-class structure

**Lemma 5.** Let C be a complete live class with support T and sign matrix H = H_C. There are nonzero
scalars `delta_i` (i in C) and `gamma_f` (f in T) such that

    a_if = delta_i  eps_if  gamma_f        and        b_if = 4 delta_i^{-1} eps_if gamma_f^{-1}.

*Proof.* Step 1 (parallel groups). Fix a column pair {c, c'} ⊂ T and a group {i, i'} of (C, {c, c'}), so that
`eps_ic eps_ic' = eps_i'c eps_i'c' =: s`. By Lemma 2(b) two other blocks S', S'' contain {c, c'}. Any line j
in them with `eps_jc eps_jc' = -s` is orthogonal to both i and i' by the rule (3) (the overlap is exactly
{c, c'}); at least one such j is live **[check: D.class-witnesses]**. The two equations (E2) say that the
vectors `(a_ic, a_ic')` and `(a_i'c, a_i'c')` are both orthogonal to `(b_jc, b_jc')`, which is nonzero by
Lemma 4. Two vectors of R^2 orthogonal to the same nonzero vector are parallel:

    a_ic a_i'c' = a_ic' a_i'c .                                                                      (4)

Step 2 (sign normalisation). Put `u_if := a_if eps_if` (all nonzero by Lemma 4). Since `eps_ic' = s eps_ic`
and `eps_i'c' = s eps_i'c`, equation (4) reads `s eps_ic eps_i'c (u_ic u_i'c' - u_ic' u_i'c) = 0`, i.e.

    u_ic / u_ic' = u_i'c / u_i'c'   for the two rows i, i' of a group of (C, {c, c'}).

Step 3 (solving the ratio relations). By Lemma 2(d) the three pairings of the rows are three distinct
perfect matchings; label the rows 1..4 and the columns a, b, c, d so that the pairings are {1,2}|{3,4} for
the column pairs {a,b} and {c,d}, {1,3}|{2,4} for {a,c} and {b,d}, and {1,4}|{2,3} for {a,d} and {b,c}.
Dividing each row of u by its first entry (this is the row scaling delta_i), write the rows as
`(1, x_i, y_i, z_i)`. The group relations are

    x_1 = x_2 =: x,  x_3 = x_4 =: X;   y_1 = y_3 =: y,  y_2 = y_4 =: Y;   z_1 = z_4 =: z,  z_2 = z_3 =: Z;
    y Z = Y z,  y z = Y Z   (pair {c,d});    x Z = X z,  x z = X Z   (pair {b,d});    x Y = X y,  x y = X Y   (pair {b,c}).

From `yZ = Yz` and `yz = YZ`: `y^2 zZ = Y^2 zZ`, so `Y = +-y` and correspondingly `Z = +-z`, `X = +-x` with
a common sign. Two cases remain:

- (i) `X = x, Y = y, Z = z`: all four rows of u are equal to `gamma := (1, x, y, z)`. Then
  `a_if = delta_i eps_if gamma_f`, which is the claim.
- (ii) `X = -x, Y = -y, Z = -z`: the rows of the row-normalised u are `(1,x,y,z), (1,x,-y,-z), (1,-x,y,-z),
  (1,-x,-y,z)`, i.e. `u = diag(delta) H_0 diag(gamma)` with H_0 the Sylvester matrix whose group structure is
  the one fixed above. The sign
  matrix H of the class has the same group structure for every column pair; two +-1 matrices with identical
  group structures agree up to row and column sign changes (normalise the first row and the first column of
  both to +1 — this does not change the groups — then the group of row 1 for the pair {a, c} identifies the
  rows with a +1 in column c). So `H = D_r H_0 D_c` for sign matrices D_r, D_c, and
  `A_C = diag(delta) (H_0 ∘ H) diag(gamma) = diag(delta) D_r J D_c diag(gamma)` with J the all-ones matrix,
  of rank 1. This contradicts Lemma 3.

Hence (i) holds. Finally `H H^T = 4 I` gives `H^{-T} = H / 4`, and Lemma 3 gives
`B_C = 16 A_C^{-T} = 16 diag(delta)^{-1} (H/4) diag(gamma)^{-1}`, which is the formula for b.  ∎

The control **[check: F.single-block-not-rigid, F.minor-obstruction]** exhibits a zero-free nonsingular class
matrix (the 4 x 4 Pascal matrix) that satisfies every equation inside its own block — Lemma 4 does not exclude
it — but is not a row/column scaling of H, and the group minor (4) that a live witness forces to vanish is
nonzero for it; the cross-block equations are what make the structure rigid.

## 6. Gluing the classes

Write `gamma^C` for the column scaling of class C from Lemma 5 (it is determined up to the common factor
that can be moved into the delta's).

**Lemma 6.** There are nonzero scalars `g_f` (f in F) and `c_C` (one per complete live class) with
`gamma^C_f = c_C g_f` for every complete live class C and every f in its support.

*Proof.* Let C, C' be complete live classes in distinct blocks S, S' with `S ∩ S' = {k, k'}`. For every j in
C', exactly two rows i of C are orthogonal to j, namely those with `eps_ik eps_ik' = -eps_jk eps_jk'`
(rule (3) with Lemma 2(d); checked for every such ordered pair of classes **[check: D.gluing-witnesses]**).
Substituting Lemma 5 into (E2) for such a pair i, j and dividing by `4 delta_i / delta_j`:

    eps_ik eps_jk gamma^C_k / gamma^C'_k  +  eps_ik' eps_jk' gamma^C_k' / gamma^C'_k'  =  0 .

Orthogonality with overlap {k, k'} means `eps_ik eps_jk = - eps_ik' eps_jk'`, so

    gamma^C_k / gamma^C_k'  =  gamma^C'_k / gamma^C'_k' .                                             (5)

Define `rho_kk' := gamma^C_k / gamma^C_k'` for any complete live class C whose block contains k and k'. By
(5) this does not depend on C: two classes of distinct blocks through {k, k'} are related directly, and two
classes of the same block are both related to a class of one of the two other blocks through {k, k'}
(Lemma 2(b)), which exists because every block has a complete live class **[check: D.block-live-class]**.
For three distinct pivot lines k, k', k'' there is exactly one block containing all three (Lemma 2(b)), it has
a complete live class, and in it `rho_kk' rho_k'k'' = rho_kk''`. Fix a base point k_0 in F and put
`g_k := rho_{k k_0}` (so `g_k0 = 1`). For any k, k': `rho_kk' = rho_{k k_0} rho_{k_0 k'} = g_k / g_k'` (the
triple {k, k', k_0} lies in a block; the degenerate cases are trivial). Hence for every class C and k, k' in
its support `gamma^C_k / gamma^C_k' = g_k / g_k'`, i.e. `gamma^C = c_C g|_T` for a scalar c_C.  ∎

## 7. Proof of Theorem 1

By Lemmas 5 and 6, for every live non-pivot line i (whose class is complete, Lemma 2(e)) and f in T_i,

    a_if = d'_i eps_if g_f,      b_if = 4 (d'_i g_f)^{-1} eps_if,        d'_i := delta_i c_C != 0,

and `a_if = b_if = 0` for f not in T_i, where also `eps_if = G_if = 0`. Put `d_i := d'_i / 2` for non-pivot
lines and `d_f := 1 / g_f` for pivot lines. Since `eps_if = G_if` on T_i,

    K_if = a_if = 2 G_if d_i / d_f,        K_fi = b_if = 2 G_if d_f / d_i,        K_ff' = 4 δ_ff' = 2 G_ff' .

So `K[:, F] = D (2 G[:, F]) D_F^{-1}` and `K[F, :] = D_F (2 G[F, :]) D^{-1}`. With `R` the live-root matrix
(rows r_i) and `R_F` its pivot rows, `R_F^T R_F = 2 I_8`, hence `G[:, F] G[F, :] = R R_F^T R_F R^T = 2 G`.
By (1),

    K = (1/4) D (2 G[:, F]) (2 G[F, :]) D^{-1} = D (2 G) D^{-1} .

`verify.py` recomputes this assembly in exact rational arithmetic for one fixed random choice of scalings per
live set: with the Lemma 5 forms
and glued column scalings `gamma^C = c_C g|_T`, every equation of (2) holds and `(1/4) K[:,F] K[F,:]` equals
`D (2G) D^{-1}` with exactly these d_i, d_f **[check: F.assembly-control]**; with class-dependent column
scalings (E0) and (E4) still hold but two-term equations fail, so Lemma 6 is a genuine constraint
**[check: F.assembly-needs-gluing]**. It also confirms that `D (2G) D^{-1}` has rank 8 and satisfies (E) for
a random rational D **[check: E.gauge-solves]**, and that the rank hypothesis is essential: `2G + e_i e_j^T`
on an odd pair satisfies (E), has rank 9 and is not of gauge form **[check: F.rank9-not-gauge]**.  ∎

## 8. Proof of Corollary 2

Let the costly terms be `x_1 y_1^T + ... + x_8 y_8^T = K` with K satisfying (E) (cost-0 terms contribute
nothing on the E-graph). By Theorem 1, `K = D R (2 I) R^T D^{-1}` with R of rank 8 (the live roots span R^8).
The column space of K is that of `D R`, and the row space is that of `D^{-1} R`; so the 112 x 8 (or 120 x 8)
matrices X = [x_k] and Y = [y_k] satisfy `X = D R A`, `Y = D^{-1} R B` for 8 x 8 matrices A, B, and
`R (A B^T - 2 I) R^T = 0` forces `A B^T = 2 I` because R has full column rank. The support of
`x_k = D R a_k` is `{ i : <r_i, a_k> != 0 } = C(a_k) ∩ L`, since D is diagonal with nonzero entries; likewise
for y_k **[check: E.factorisation, E.normal-form-supports]**.

Now `(R A, R B)` is itself an exact 8-term decoder in PR968's sense on the same live set: `(RA)(RB)^T =
R (2I) R^T = 2G` on all live pairs, and its terms have the same supports — hence the same per-term costs —
as the costly terms `x_k, y_k`, because D is diagonal and invertible. PR968's theorem (PROOF.md §4 there,
called Theorem 4 here for convenience) therefore applies to it literally and gives `cst >= 72 - p` for a
puncture of `p <= 15` lines: 64 on P112 (p = 8) and 72 on P120 (p = 0). The coordinate decoder attains both
bounds **[check: E.coordinate-decoder]**; a sampled dual basis gives eight terms of cost 9
**[check: E.sample-cost]**. Corollary 2 thereby inherits PR968's one cited, not recomputed, premise: the
classification of the hyperplane flats of the E8 arrangement into eight W(E8)-types (PR968 (F6)).  ∎

## 9. What is and is not covered

- **Exactly eight costly terms.** Corollary 2 needs exactly eight costly terms at the factorisation step
  (square A, B) and in PR968's Theorem 4. With nine or more costly terms Theorem 1 still describes the sum K
  whenever its rank is 8, but the factorisation is no longer determined and no statement about the term
  supports or costs follows; when `rank K >= 9`, Section 1 fails at the first step. PR717's mixed-β problem
  for n >= 9 is therefore untouched; in the E-graph model its locus is the rank >= 9 solutions of the same
  system together with the factorisations of the rank-8 solutions `D (2G) D^{-1}` into nine or more terms.
- **Live sets.** P112 (the complement of any frame, by W(E8)-transitivity), P120, and — by Section 10 — the
  336 P104 units of type (2,2,2,2). For P111, the 28 type-(4,4) P104 units and the 896 admissible P104 units
  (PR717's among them) Section 10 establishes zero exclusion and records exactly which further input of the
  proof is missing; rigidity there is not claimed (numerical evidence only).
- **Coefficients.** Stated for real coefficients, as in PR717 and PR968. The argument of Sections 1–7 is
  algebraic and uses only that the coefficients lie in a field of characteristic zero (division by 2 and 4,
  `y^2 = Y^2 => Y = +-y`, zero patterns, ranks), so Theorem 1 holds verbatim over C; Corollary 2 over C would
  additionally need PR968's theorem over C, which is the subject of PR1077 and is not invoked here.
- **Not a construction** and no κ change: the theorem constrains the eight-term class and leaves the
  copy-cost question for larger term counts open.
- **Concurrent result.** PR1191 (mightyOil, opened after this package was drafted) shows that E-graph
  exactness already forces the all-pairs identity when one factor is root-linear, for any term count; its
  hypothesis and the rank-8 hypothesis here are incomparable (the solutions `D(2G)D^{-1}` of Theorem 1 have
  factors `DRA`, `D^{-1}RB` that are in general not root-linear), and the two results together leave open,
  on P112, exactly the E-graph decoders of rank >= 9 with both factors off the root code.

## 10. Beyond one frame: what transfers to P111 and to the P104 units

The written proof uses four finite inputs about a live set L with a live pivot frame F: (I1) every live
non-pivot line lies in a complete class (Lemmas 3, 5); (I2) zero exclusion (Lemma 4); (I3) the group witnesses
of Lemma 5 Step 1; (I4) every block has a complete live class (Lemma 6). Section G of `verify.py` re-establishes
whichever of these hold on representative units beyond P112, with the pivot chosen (deterministically) to
minimise the number of incomplete classes, and transports the conclusions by symmetry.

**Transport.** The line permutations induced by the root reflections and by products of two root reflections
that map FRAME0 to itself (204 of them) generate a subgroup of the stabiliser of FRAME0 in W(E8). It acts
transitively on the 112 lines of P112, so all 112 single-line punctures P111 are equivalent, and it has
exactly three orbits on the 1260 frames inside P112, of sizes 28, 336 and 896, distinguished by how the frame
meets the classes relative to FRAME0 — types (4,4), (2,2,2,2) and (1,…,1) **[check: G.stabiliser-generators,
G.line-orbits, G.frame-orbits]**; PR968's 364 inadmissible frames are the first two orbits and its 896
admissible frames (PR717's P104 among them) the third **[check: G.pr717-p104-orbit]**. Since each such
permutation preserves orthogonality, N, the rank condition and the torus orbits (Section 0), every statement
below proved for a representative unit with pivot F holds for every unit of its orbit with the transported
pivot.

**Lemma 8 (zero exclusion beyond one frame).** With the pivots listed by `verify.py`, no entry of a_i or b_i
vanishes on its block for any rank-8 solution of (E) on P111, nor on any of the 1260 P104 units: for P111 and
for the types (2,2,2,2) and (1,…,1) the two-term and diagonal conditions alone refute "some entry is zero"; for
the type (4,4) those two families admit a zero pattern and the refutation uses all four families, i.e. Lemma 3
**[check: G.P111.zero-exclusion, G.P104-44.zero-exclusion, G.P104-2222.zero-exclusion,
G.P104-11111111.zero-exclusion]**.

**Theorem 1′ (the 336 units of type (2,2,2,2)).** For the representative unit `P112 minus {2,3,18,19,40,41,52,53}`
with pivot `{12,13,22,23,30,31,36,37}` all 24 live classes are complete, zero exclusion holds, every complete
class has its live group witnesses and every block has a complete live class
**[check: G.P104-2222.unit, G.P104-2222.class-witnesses, G.P104-2222.theorem-transfers]**. The proof of
Sections 1–7 therefore applies verbatim: every rank-≤8 solution of (E) on such a unit is `D (2G_L) D^{-1}`.
Corollary 2 follows as in Section 8 with PR968's floor at p = 16: every decoder with exactly eight costly terms
in the E-graph model on these 336 P104 units has cst ≥ 56.

**What does not transfer (recorded by the same checks).**

- *Type (4,4), 28 units.* The pivot that makes every live class complete is the third 4-frame of the two D4
  blocks spanned by the two punctured frames, so those two blocks have no live line at all and only 12 of the
  14 blocks carry a complete live class **[check: G.P104-44.unit]**. Lemma 6's cocycle step has no witness for
  triples inside those two blocks, so rigidity is not established there (numerically: 8 of 8 random starts
  converge to gauge-equivalent solutions, seed 5; *recorded*). Other pivots give all 14 blocks a live class but
  leave eight classes incomplete.
- *Type (1,…,1), 896 units (PR717's P104 among them).* Zero exclusion and the witnesses hold, but four classes
  keep only two live rows **[check: G.P104-11111111.unit]**; for a two-row class the group relations of Lemma
  5 constrain only one column pairing, leaving a one-parameter family inside the class, so Lemma 5 does not
  apply. (Numerically rigid: README, "Numerical probes".)
- *P111, 112 units.* Zero exclusion and the witnesses hold; one class keeps three live rows and its block has
  no complete class **[check: G.P111.unit]**. For a three-row class the relations of the three pairings still
  force the two cases of Lemma 5 Step 3 (with `z_1 = ±z` in place of the four-row computation), and case (ii)
  is excluded because the 3 × 4 class matrix has rank 3; writing out that variant and the gluing with a
  three-row class is the smallest next step, not done here.

The pivots, class profiles, CNF digests and proof hashes of all four units are pinned in `verify.py` and
written to the certificate.
