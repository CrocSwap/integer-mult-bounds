# No facet of the mode zonotope has a depth gap

Prepared for apoursh with substantial Anthropic Claude assistance. Apache-2.0.

## Setting

M is the 112×8 mode matrix of Dillon Amburgey's PR4933, from
`research/coded-native-caller/NORMALIZERS.json`, with rows m_i. #6312
(`research/mode-preserving-rounding`) defines the least uniform radius R of exact
mode-preserving rounding and proves R ≥ 1. #6333 (`research/mode-fiber-radius-three-halves`)
proves R ≤ 3/2. #6320 (`research/mode-fiber-radius-bounds`, Theorem A) shows
R = 1 if and only if every lattice point of L = Mᵀℤ^112 in the open zonotope
Mᵀ(0,1)^112 is a 0/1 subset sum of the rows.

In centred coordinates, y = 2t − Σ_i m_i and Z = Σ_i [−1,1] m_i. Then:

    R = 1  ⇔  every y ∈ 2L ∩ int Z lies in K = {Σ_i κ_i m_i : κ ∈ {±1}^112}.

## 1. The depth obstruction

Let θ be a primitive integer normal of a facet of Z. The rows with ⟨m_i,θ⟩ = 0
span the facet hyperplane. Put h = Σ_i |⟨m_i,θ⟩| = max_Z ⟨θ,·⟩, let g be the gcd
of the nonzero |⟨m_i,θ⟩|, and let V be the multiset {|⟨m_i,θ⟩|/g ≠ 0} with sum T.

Every sign sum y ∈ K satisfies

    ⟨θ,y⟩ = h − 2g·σ,   σ = Σ_{i: κ_i ≠ sgn⟨m_i,θ⟩} |⟨m_i,θ⟩|/g,

so σ is a subset sum of V. The rows generate L, so ⟨θ,2L⟩ = 2gℤ, and the
lattice layers of 2L meeting Z are exactly ⟨θ,·⟩ = h − 2gk for 0 ≤ k ≤ T.
**If some k is not a subset sum of V, no sign sum lies on that layer.** A
lattice point of 2L in the interior of Z on that layer would then disprove
R = 1. Near a facet, these layers are wide, nearly full copies of the facet,
so this is the most direct candidate counterexample.

## 2. Theorem

**For every facet normal θ of Z, the subset sums of V are exactly {0, 1, …, T}.**
Moreover the smallest element of V is 1, and sorted V = (v_1 ≤ v_2 ≤ …)
satisfies v_(k+1) ≤ 1 + v_1 + ⋯ + v_k. Also g ∈ {1, 2}.

Consequently the shadow of K on every facet normal equals the shadow of
2L ∩ Z, and no facet of Z carries a depth obstruction to R = 1. Z has
**422,224** facet hyperplanes, each giving two opposite facets. They fall into
**41** orbits under the symmetry group described below.

*Proof (finite, exact; verify.py).*

1. **Symmetry.** Up to sign, the rows are all 8 sign classes on each of the 14
   weight-four words of H8 (#6320 §1, rechecked). The ±row set is therefore
   invariant under every coordinate sign flip and every permutation preserving
   H8 (|Aut H8| = 1344). Call this group of signed permutations Γ. Γ permutes
   facets, and the multiset V, its gcd and the theorem's properties are
   Γ-invariant.
2. **Representatives.** ORBITS.json lists 41 vectors |θ|. Each is a primitive
   normal whose zero rows have corank 1, so each is a facet. They are pairwise
   inequivalent under Aut(H8), and each satisfies the theorem.
3. **Completeness.** For each representative facet H, verify.py enumerates every
   rank-6 flat F ⊂ H. It does this exactly, rank by rank, closing each flat with
   integer orthogonal complements. It then forms every hyperplane F + m_e
   spanned by rows. Each such hyperplane lies in a listed orbit, so the union S
   of the 41 orbits is closed under "shares a rank-6 flat". Every ridge of Z is
   parallel to a rank-6 flat shared by its two facets, and the facet–ridge graph
   of a polytope is connected. S is nonempty, so it contains every facet.
4. **Count.** The orbit of θ under Γ, up to ±, has |Aut-images of |θ||·2^(nnz θ)/2
   elements. Summing over the 41 orbits gives 422,224. ∎

## 3. Controls

* The non-facet direction θ = (5,3,0,…,0) **does** have a gap: the values
  {2, 3, 5, 8} miss 1. So the property is specific to facets, not automatic.
  (That direction is the normal cone of a codimension-2 face. Whether its gap
  meets an interior lattice point is not examined here.)
* Removing the last listed orbit breaks the closure check.

## Scope

This rules out one family of potential counterexamples to R = 1: a missing
depth layer just inside a single facet. It does not prove R = 1. Obstructions
at faces of codimension ≥ 2, where two or more normals constrain the flipped
rows jointly, and obstructions not detectable by any single linear shadow
remain possible. 1 ≤ R ≤ 3/2 is unchanged.

This concerns the exact-mode contract of #6312 only. It supplies no physical
rounder, tape or error bill. κ, the selected frontier and its five assumptions
are unchanged. The written argument is author-checked with exact finite
corroboration; no independent human or proof-kernel review is claimed.
