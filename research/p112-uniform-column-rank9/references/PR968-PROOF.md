# Exact 8-term copy-cost floor on punctured complex E8 units

Every finite fact cited as **(Fk)** is checked by `verify.py`, using exact integer and F2
arithmetic. The rest is written argument. One standard theorem is cited rather than recomputed
(see (F6)).

## 1. Model

This is PR717's B14 decoder model, in the D2/D3 scope (DreamingOfClouds,
`research/format-limits-2/s5-6-decoders-spec/checks/e8model.py` at `4a97676`). Take the 120 root
lines of E8 with representatives r_i of norm 2, and let G_ij = ⟨r_i, r_j⟩. A **puncture** P is a set
of p lines, and the **live** lines are the rest. Each line has a label u_i ∈ F2^9 with a symmetric
form S9. PR717's construction gives

    S9(u_i, u_j) = (⟨r_i, r_j⟩ + 1) mod 2,                                   (1)

because the first eight label coordinates carry the E8 form mod 2 and the ninth is a unit
coordinate equal to 1 on every line. `verify.py` uses (1) directly as its definition.

An **exact 8-term decoder** is a pair of real matrices D and T, each of size live × 8, with
DTᵀ = 2G on all live pairs. Term k costs ρ_k: the F2 rank of the label pairing between its row
support R_k = {i : D_ik ≠ 0} and its column support A_k = {j : T_jk ≠ 0}. The copy cost is
cst = Σ_k ρ_k. On P112, the coordinate decoder has cst = 64. That is the value carried by the
selected complex supplier (T37 deficit 37·(8·112 − 9·64) = 11840).

**Normal form.** Suppose the live lines span R^8. This always holds when p ≤ 56, because no
hyperplane contains more than 63 lines. Then rank 2G_live = 8. So D and T have rank 8, and
their column spaces equal that of R, the live-root matrix. Hence D = RA and T = RB with
ABᵀ = 2I. Write a_k and b_k for the columns of A and B. Then ⟨a_k, b_l⟩ = 2δ_kl,
R_k = live ∩ C(a_k) and A_k = live ∩ C(b_k), where C(a) is the set of lines not orthogonal to a.
Two consequences:

- a_k ∦ b_l for k ≠ l;
- the a_k are pairwise non-parallel, and so are the b_k.

Conversely, any pair of dual bases gives an exact decoder on every live set.

## 2. Linear algebra over F2

(F0) The 120 × 120 pairing matrix (1) has F2 rank 9, and its 120 rows are distinct. So the labels
span a 9-dimensional space Λ on which S9 is nondegenerate. Distinct lines have distinct label
functionals λ_i = S9(u_i, ·).

For a set X of lines, let V_X = span{u_i : i ∈ X}. The pairing rank satisfies

    ρ(X, Y) = dim V_X − dim(V_X ∩ V_Y^⊥) ≥ dim V_X + dim V_Y − 9.             (2)

For a root α, let H_α = ker λ_α. If V_X = H_α and V_Y = H_β, then H_β^⊥ = span(u_β), so

    ρ = 8 − [u_β ∈ H_α] = 8 − [⟨α, β⟩ odd].                                  (3)

In particular α = β gives ρ = 8, because ⟨α, α⟩ = 2.

**Violators.** dim V_X ≤ 8 exactly when some nonzero functional λ vanishes on X. Equivalently,
X avoids Viol(λ) = {i : λ(u_i) = 1}. So a side with normal a can be brought to an 8-dimensional
span only by puncturing all of Viol(λ) ∩ C(a), for some λ. Getting dim ≤ 7 requires puncturing
(Viol(λ1) ∪ Viol(λ2)) ∩ C(a), for some independent pair λ1, λ2.

## 3. The finite census

The pairing (1) depends only on inner products, so it is W(E8)-invariant. Every hyperplane flat
of the E8 arrangement is W-conjugate to one of the eight standard flats ω_i^⊥, where ω_i are the
fundamental weights (Bourbaki, *Lie Groups*, Ch. V §3; Orlik–Solomon). **(F6)** This is the one
premise that is cited rather than computed.

For each type, `verify.py` checks all 511 hyperplanes and all 130,305 pairs of functionals. The
table gives |C(ω)|, the smallest and second-smallest |Viol(λ) ∩ C(ω)|, and the codimension-2
minimum π7:

| flat type | flat lines | C | min | next | π7 |
|---|---|---|---|---|---|
| E7 (root normal) | 63 | 57 | **1** | 24 | **25** |
| D7 | 42 | 78 | **14** | 34 | 42 |
| E6+A1 | 37 | 83 | 27 | 28 | 51 |
| A7 | 28 | 92 | 28 | 35 | 56 |
| D5+A2 | 23 | 97 | 33 | 41 | 61 |
| A6+A1 | 22 | 98 | 35 | 35 | 62 |
| A4+A3 | 16 | 104 | 40 | 43 | 68 |
| A4+A2+A1 | 14 | 106 | 43 | 43 | 70 |

The checked facts:

- **(F1)** Every C(ω) has a label span of dimension 9.
- **(F2)** This is checked for all 120 roots directly. For a root α, the unique 1-line violator
  set is {α}, through λ_α. Every other λ needs ≥ 24 lines.
- **(F3)** The W-orbit of the D7 normal has 1080 directions, enumerated by reflections. Each has
  a unique minimizing λ_ω with 14 violators, and the next has ≥ 34. Any two distinct D7 directions
  have violator sets whose union is ≥ 21. No λ_ω equals a root functional λ_α.
- **(F4)** Every other hyperplane type needs at least 27 violators.
- **(F5)** Over all types, π7 ≥ 25.

**Lemma 1 (non-hyperplane normals).** Suppose the roots orthogonal to a span at most 6
dimensions. Then |Viol(λ) ∩ C(a)| ≥ 16 for every λ, and π7(a) ≥ 25.

*Proof.* Let U be the span of the roots orthogonal to a, so dim U ≤ 6. Extend a root basis of U
by roots to a root basis of R^8. Dropping two different added roots gives two distinct
root-spanned hyperplanes H1 and H2, both containing U. Their normals ω1 and ω2 are hyperplane-flat
normals with C(ω_i) ⊆ C(a). So

    Viol(λ) ∩ C(a) ⊇ (Viol(λ) ∩ C(ω1)) ∪ (Viol(λ) ∩ C(ω2)).

Suppose this set had at most 15 lines. Then, by the census, each (ω_i, λ) would be a pair
(root α_i, λ_{α_i}) or (D7 normal, its λ_ω). With the same λ for both, there are three cases:

- two roots: λ_{α1} = λ_{α2} forces α1 = α2 by (F0), so H1 = H2;
- root and D7: impossible, since no λ_ω is a root functional (F3);
- two D7 normals: their violator sets have union ≥ 21 (F3).

Each case is a contradiction. For π7, one containing hyperplane is enough, by (F5). ∎

## 4. Theorem

Let P be a puncture with p = |P| ≤ 24, and let (A, B) be an exact 8-term decoder on the live
lines.

**(a)** cst ≥ 56.

**(b)** If p ≤ 15, then cst ≥ 72 − p.

**(c)** Hence cst/v ≥ 7/13 for every p ≤ 24, where v = 120 − p. Equality holds exactly when
p = 16 and cst = 56. Both bounds are attained at every p: cst_min(p) = 72 − p for 0 ≤ p ≤ 16, and
cst_min(p) = 56 for 16 ≤ p ≤ 24.

*Proof of (a).* By (F5) and Lemma 1, bringing any side down to a span of dimension ≤ 7 needs at
least 25 > p punctures. So every live support spans at least 8 dimensions, and (2) gives ρ_k ≥ 7.

*Proof of (b).* Call a side **reduced** if its live label span has dimension 8. By (a), every
unreduced side has dimension 9. By (2), s_k := 9 − ρ_k is at most the number of reduced sides of
term k. A reduced side with normal a needs some λ with |Viol(λ) ∩ C(a)| ≤ p ≤ 15. By (F2)–(F4)
and Lemma 1, only two kinds qualify:

- **(i)** a is a root α, with λ = λ_α, and α ∈ P (a *self-line* reduction);
- **(ii)** a is a D7 normal ω, with its 14-line set ⊆ P.

By (F3), case (ii) can occur for at most one direction ω, because p < 21.

*If (ii) occurs:* By the normal form, ω is not a column normal of any term other than its own.
Transposing (D ↔ T) preserves exactness and costs, so assume ω = a_1. For l ≠ 1, ⟨a_1, b_l⟩ = 0,
so b_l ⊥ ω. A reduced column side l ≠ 1 is therefore a self-line β_l ∉ C(ω). Its line lies in
P minus the 14-line set, which has at most p − 14 ≤ 1 lines. The β_l are distinct, so at most one
of these seven column sides is reduced. That gives Σ s_k ≤ 16 − 6 = 10 < 14 ≤ p.

*If (ii) does not occur:* Every reduced side is a self-line reduction. Lines from different
terms are distinct: the a's are distinct, the b's are distinct, and a_k ∦ b_l for k ≠ l. Term k
uses two distinct lines unless a_k ∥ b_k. In that case ρ_k = 8 by (3), so s_k = 1, the number of
lines it uses. So Σ s_k ≤ |P| = p in every case, and cst = 72 − Σ s_k ≥ 72 − p.

*Proof of (c).* For p ≤ 15:

    13(72 − p) − 7(120 − p) = 96 − 6p > 0.

For 16 ≤ p ≤ 24, cst/v ≥ 56/(120 − p) ≥ 56/104. `verify.py` (section E) builds an exact
decoder attaining max(72 − p, 56) for every p = 0..24:

- for p ≤ 8: the coordinate decoder with p frame lines punctured;
- for 8 < p ≤ 16: a frame-pair decoder (§5) with p − 8 partner lines punctured;
- for p > 16: the frame-pair decoder with p − 16 further lines punctured. Spans cannot fall below
  8 dimensions, by (a). ∎

## 5. Frame-pair decoders

Let F0 be the coordinate frame and F1 another frame, i.e. 8 mutually orthogonal lines disjoint
from F0. A **frame-pair decoder** takes eight row normals: S ⊆ F0 and T ⊆ F1, with |S| + |T| = 8.
Each row normal is paired with a column partner from the other frame, chosen so that:

- the partner is non-orthogonal to its own row normal;
- the partner is orthogonal to every other row normal.

Lines from two distinct frames are 0 or ±1 apart, so every pair is odd. The 16 lines are exactly
F0 ∪ F1, so on P = F0 ∪ F1 every term has both self-lines punctured, and (3) gives ρ = 7.

**(F7)** There are 1260 frames inside P112. Of these:

- 896 admit frame-pair decoders, with exactly 8 each. All 7168 decoders satisfy AᵀB = 2I and have
  eight cost-7 terms; one is also rechecked entry by entry.
- 364 admit none. These are the frames in which some pair of F1 lines shares four F0-neighbours.
  They form two relative positions: 336 connected and 28 of type K4,4 ∪ K4,4.

PR717 D3 drew its P104 clique at random. It is an admissible frame of this kind. Its recorded
decoder, along with both recorded P111 decoders, has exactly the root-pair structure. Each cost-7
term is an odd pair of root normals whose two lines are both punctured, and no other term is.
The per-term costs computed from (1) equal those recorded by PR717's own label code.

## 6. Scope

The following are **not** covered:

- decoders with n ≥ 9 terms;
- decoders that are exact only on PR717's E-graph and fix the odd entries with cost-0 terms. This
  is the scope of D1(a), whose mixed-β open problem remains open;
- punctures of more than 24 lines;
- whether a word can realize the asymmetric (α ≠ β) centres. PR717 recorded, without shipping, a
  negative buildability price for these decoders.

Section G of `verify.py` gives a favorable budget only, not a construction.
