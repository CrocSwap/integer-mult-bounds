# Nine-term complex E8 decoders: normal form and reductions

Finite facts cited as **(Bk)**, **(Ck)**, ... are checked by `verify.py` with exact integer, F2 and
rational arithmetic. Everything else is a written argument. No premise is imported from an
unreviewed pull request; where a result of an open PR is *combined* with the statements below, it is
named as such.

## 1. Model

This is the B14 decoder model of PR717 as used by PR968 §1 and PR1077. The 120 root lines of E8 have
norm-2 representatives r_i and Gram matrix G. A puncture P removes p lines, leaving the live set L.
Labels lie in a nine-dimensional F2 space Λ with nondegenerate pairing
S9(u_i, u_j) = (⟨r_i, r_j⟩ + 1) mod 2. For a set X of lines write V_X for the span of its labels.

Let F be R or C (ordinary transpose, no conjugation). An **exact m-term decoder** is a pair
D, T ∈ F^{L×m} with D Tᵀ = 2G on all live pairs. Term k has row support X_k = {i : D_ik ≠ 0} and
column support Y_k = {j : T_jk ≠ 0}, and costs the PR446 Theorem C pairing rank
ρ_k = rank(S9 restricted to V_{X_k} × V_{Y_k}). The copy cost is cst = Σ_k ρ_k. Since the pairing is
symmetric, transposing a decoder (D ↔ T) preserves exactness and every term cost.

R ∈ R^{L×8} is the live-root matrix. **Standing hypothesis:** rank R = 8. This holds whenever
p ≤ 56, because a real root-spanned hyperplane contains at most 63 lines.

For a vector b let C(b) = {i ∈ L : ⟨r_i, b⟩ ≠ 0}. For complex b = u + iv, a real line is orthogonal
to b exactly when it is orthogonal to both u and v.

## 2. Theorem A (normal form for any number of terms)

Since RᵀR is real positive definite, it is invertible over F, and F^L = col(R) ⊕ ker(Rᵀ). (The
intersection is zero: R a ∈ ker Rᵀ gives RᵀR a = 0, so a = 0. The dimensions add up.) Write

    D = R A + N1,   T = R B + N2,   with Rᵀ N1 = Rᵀ N2 = 0,

where A = (RᵀR)⁻¹RᵀD and B = (RᵀR)⁻¹RᵀT are 8×m.

**Theorem A.** D Tᵀ = 2G holds if and only if

    (i) A Bᵀ = 2 I_8,   (ii) N1 Bᵀ = 0,   (iii) A N2ᵀ = 0,   (iv) N1 N2ᵀ = 0.

*Proof.* Here 2G = 2RRᵀ in true units. Expand

    D Tᵀ = R A Bᵀ Rᵀ + R A N2ᵀ + N1 Bᵀ Rᵀ + N1 N2ᵀ.

Let L⁺ = (RᵀR)⁻¹Rᵀ and Π = I − R L⁺. Then L⁺R = I, L⁺N = 0, ΠR = 0 and ΠN = N for N in ker Rᵀ.
Applying L⁺(·)L⁺ᵀ, Π(·)L⁺ᵀ, L⁺(·)Πᵀ and Π(·)Πᵀ to both sides isolates the four summands. The right
side 2RRᵀ gives 2I, 0, 0 and 0 respectively. Conversely, (i)–(iv) make the expansion equal to
R(2I)Rᵀ. ∎

From (i), rank A = rank B = 8 and m ≥ 8. Let ker A and ker B be the right kernels in F^m; each has
dimension m − 8. Condition (ii) says every row of N1 lies in ker B, and (iii) says every row of N2
lies in ker A.

**Lemma A′.** The bilinear pairing ker A × ker B → F, (y, z) ↦ yᵀz, is nondegenerate.

*Proof.* Let y ∈ ker A satisfy yᵀz = 0 for every z in ker B. The bilinear orthogonal complement of
ker B is the row space {Bᵀu} of B, because the row space is contained in it and both have dimension 8.
So y = Bᵀu, and 0 = A y = A Bᵀ u = 2u. Hence y = 0. The other side is symmetric. ∎

## 3. Corollary B (m = 9: at most one factor leaves the root code)

For m = 9, ker A = span(y) and ker B = span(z), with yᵀz ≠ 0 by Lemma A′. Then N1 = n zᵀ and
N2 = n′ yᵀ for some n, n′ ∈ ker Rᵀ, and (iv) reads (zᵀy) n n′ᵀ = 0. So **n = 0 or n′ = 0**. At least
one of D, T has every column in col(R). (C3) checks that putting junk on both sides breaks
exactness. (C4) gives an exact 10-term decoder with junk on both factors, so this corollary is
specific to m = 9. (C1) and (C2) decompose explicit decoders: random one-sided ones, and the shape of
PR1180's outside-code identity.

*Combination with concurrent work.* PR1180 (@woklerx, open, head `75b4086`) proves cst ≥ max(72 − p, 56)
for p ≤ 24 and any m, when **both** factors lie in col(R). With Corollary B, a 9-term decoder
outside PR1180's class therefore has *exactly one* factor outside the root code. This package does
not re-verify PR1180.

## 4. Corollary C (one-sided nine-term decoders are overcomplete representations)

Transpose if necessary so that N2 = 0. Write b_1..b_9 for the columns of B, so T_jk = ⟨r_j, b_k⟩.
They span F^8 and satisfy the single dependency Σ_k z_k b_k = 0.

**Corollary C.** (D, T) is exact if and only if every row d_i of D satisfies Σ_k d_ik b_k = 2 r_i.

*Proof.* (D Tᵀ)_ij = ⟨r_j, Σ_k d_ik b_k⟩. Since the live roots span R^8, this equals 2⟨r_j, r_i⟩ for
all live j exactly when Σ_k d_ik b_k = 2 r_i. ∎

So each live line independently picks any representation of 2r_i in the overcomplete frame {b_k}.
The representations of line i form the affine line c⁰_i + F·z, giving one free scalar t_i per line.
Row supports are the supports of the chosen representations, and the column supports are
Y_k = C(b_k). Every 8-term decoder is the case with no freedom.

## 5. Lemma D (merging) and the residual class

**Lemma D.** Suppose b_l = μ b_k for some l ≠ k. Replace the two terms by the single term with row
vector d_k + μ d_l and column normal b_k. This gives an exact decoder with one term fewer and no
larger cost.

*Proof.* Exactness is linear. The new row support is contained in X_k ∪ X_l, and the column support
is unchanged. The pairing rank is monotone in the row set and subadditive over a union of row sets. ∎

A zero column normal contributes a vanishing term of cost 0 and can be dropped. Let S = supp(z). If
|S| ≤ 2, then some b_k = 0 or two normals are proportional, and dropping or merging yields an exact
8-term decoder with no larger cost. PR968 (real) and PR1077 (complex), both on main, then give
cst ≥ max(72 − p, 56) for p ≤ 24. Hence:

> **For p ≤ 24, an exact nine-term decoder can beat the eight-term floor only if exactly one factor
> leaves the root code and its overcomplete frame has |S| ≥ 3 pairwise non-proportional normals in
> its dependency.** (The "exactly one factor" part uses the open PR1180 for the other case.)

## 6. Proposition E (unmasked terms are rigid)

For k ∉ S, b_k is not in the span of the other eight normals. Otherwise the unique dependency would
have z_k ≠ 0. So the coefficient of b_k is the same in every representation. It is given by a fixed
functional ã_k, and X_k = C(ã_k) is forced exactly as in an 8-term decoder. Only the |S| **masked**
terms have adjustable row supports.

## 7. Proposition F (ratio classes)

For k ∈ S we have d_ik = c⁰_ik + t_i z_k, which vanishes iff t_i = −c⁰_ik / z_k. Therefore the masked
terms avoided by line i are exactly one class of equal ratios. (E3) checks this on every frame.

For k ≠ k′ in S, the quantity c_k z_{k′} − c_{k′} z_k does not depend on the choice of representation
c of 2x, because t cancels. It is linear in x, so it equals ⟨v_{kk′}, 2x⟩ for a unique vector
v_{kk′}.

**Proposition F.** v_{kk′} ≠ 0, and every line avoiding both masked terms k and k′ satisfies
⟨v_{kk′}, r_i⟩ = 0.

*Proof.* The vector 2e_k is a representation of 2b_k. For it, the quantity is 2z_{k′} ≠ 0. A line
avoiding both terms has c_k = c_{k′} = 0. ∎

(E1)–(E2) check this on five frames. For a deficiency functional (codeword) w of a row side, let
K(X) = {w : supp(w) ∩ X = ∅}, so that dim V_X = 9 − dim K(X).

- **F1.** If w ∈ K(X_k) ∩ K(X_{k′}) with k ≠ k′ masked, then the live part of supp(w) lies in the
  proper subspace v_{kk′}^⊥.
- **F2.** If w ∈ K(X_k) and w′ ∈ K(X_{k′}), then L ∩ supp(w) ∩ supp(w′) lies in v_{kk′}^⊥.

## 8. Proposition G (the unpunctured unit P120)

**(B1)** All 511 nonzero codeword supports span R^8. If C(b) ∩ supp(w) = ∅ for some b ≠ 0, then
supp(w) would lie in the proper subspace b^⊥ (real and imaginary parts), which is impossible. So
**every** C(b) on P120 has label span Λ.

Consequently V_Y^⊥ = 0 for every column side, and ρ_k = dim V_{X_k} exactly. (F2) checks this
formula on every frame decoder. Unmasked row sides have full span as well. For a one-sided 9-term
decoder on P120 this gives

    cst = 81 − Σ_{k∈S} δ_k,   δ_k = 9 − dim V_{X_k}.

**G1.** cst < 72 requires Σ_{k∈S} δ_k ≥ 10. Since |S| ≤ 9, some masked row side must have δ_k ≥ 2.
By **(B5)**, U2 = 84, so that side has at most 36 lines and at least 84 lines avoid its term. In
particular, if every masked δ_k ≤ 1, then cst ≥ 72.

**G2.** By F1 and B1, the deficiency spaces K(X_k), k ∈ S, intersect pairwise trivially. By F2, every
cross pair (w ∈ K(X_k), w′ ∈ K(X_{k′}), w ≠ w′) is one of the **39,255** pairs whose support
intersection does not span R^8 **(B3–B4)**:

- 255 complementary pairs, with empty intersection;
- 35,640 pairs whose intersection of 28 or 32 lines has rank 7;
- 3,360 pairs whose 36-line intersection has rank 6.

Moreover, the hyperplane in question must be v_{kk′}^⊥. Because so many non-spanning pairs exist,
the pairwise argument alone does **not** exclude a P120 counterexample. This is recorded as an open
case, not a theorem.

## 9. What is and is not proved

Proved here: Theorem A, Lemma A′, Corollaries B and C, Lemma D, and Propositions E, F and G (with the
finite facts B1–B5). Together with PR968/PR1077 these give the residual-class statement of §5. The
"exactly one factor" refinement additionally uses the open PR1180.

Not proved: a copy-cost floor for one-sided 9-term decoders with |S| ≥ 3 (on P120, P112 or any p);
decoders with m ≥ 10 (two-sided junk is possible, see C4); masked-identity (E-graph only) decoders
(see #1191); punctures with p > 56; and any physical realization. The frames and annealing in
`verify.py` §F and `search.py` are finite evidence, not proofs. This is not a formal verification of
the multiplication theorem.
