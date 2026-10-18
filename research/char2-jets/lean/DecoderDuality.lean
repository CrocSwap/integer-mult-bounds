import Mathlib

/-!
# Decoder duality certificates

Two rank lower bounds ("duality certificates") behind the decoder lower bounds,
both obtained from one abstract lemma (`hadamard_diag_rank_sum`):

* `lemmaB`   : the lift identity, `B` over the same field `K` as the decomposition `P, Q`.
* `lemmaCR2` : the char-2 realisation, `B` over `𝔽₂`, realised by vectors `P~, Q~`
               over a field of characteristic 2 supported inside the supports of `P, Q`.
-/

open Matrix

namespace DecoderDuality

/-! ## Generic linear-algebra helpers -/

section Helpers

variable {F : Type*} [Field F]

/-- Rank is subadditive. -/
theorem rank_add_le {m n : Type*} [Fintype m] [Fintype n] (A B : Matrix m n F) :
    (A + B).rank ≤ A.rank + B.rank := by
  unfold Matrix.rank
  rw [Matrix.mulVecLin_add]
  calc Module.finrank F (LinearMap.range (A.mulVecLin + B.mulVecLin))
      ≤ Module.finrank F ↥(LinearMap.range A.mulVecLin ⊔ LinearMap.range B.mulVecLin) :=
        Submodule.finrank_mono (LinearMap.range_add_le _ _)
    _ ≤ _ := Submodule.finrank_add_le_finrank_add_finrank _ _

/-- Rank of a finite sum is at most the sum of the ranks. -/
theorem rank_sum_le {m n ι : Type*} [Fintype m] [Fintype n] (s : Finset ι)
    (f : ι → Matrix m n F) : (∑ i ∈ s, f i).rank ≤ ∑ i ∈ s, (f i).rank := by
  classical
  induction s using Finset.induction_on with
  | empty => simp
  | insert a s ha ih =>
    rw [Finset.sum_insert ha, Finset.sum_insert ha]
    exact (rank_add_le _ _).trans (Nat.add_le_add_left ih _)

/-- **Support restriction.** If `p` vanishes off `S` and `q` vanishes off `U`, then
`rank (diag p * B * diag q) ≤ rank (B restricted to S × U)`. -/
theorem rank_diag_mul_mul_diag_le {m n : Type*} [Fintype m] [Fintype n]
    [DecidableEq m] [DecidableEq n] (B : Matrix m n F) (p : m → F) (q : n → F)
    (S : Finset m) (U : Finset n) (hp : ∀ t, p t ≠ 0 → t ∈ S) (hq : ∀ s, q s ≠ 0 → s ∈ U) :
    (diagonal p * B * diagonal q).rank ≤
      (B.submatrix ((↑) : S → m) ((↑) : U → n)).rank := by
  let X : Matrix m S F := fun t i => if (i : m) = t then p t else 0
  let Y : Matrix U n F := fun k s => if (k : n) = s then q s else 0
  have key : diagonal p * B * diagonal q = X * B.submatrix ((↑) : S → m) ((↑) : U → n) * Y := by
    ext t s
    rw [mul_diagonal, diagonal_mul, mul_apply]
    by_cases hs : s ∈ U
    · rw [Fintype.sum_eq_single ⟨s, hs⟩]
      · simp only [Y, if_pos rfl, mul_apply, submatrix_apply]
        by_cases ht : t ∈ S
        · rw [Fintype.sum_eq_single ⟨t, ht⟩]
          · simp only [X, if_pos rfl]
          · intro i hi
            have : (i : m) ≠ t := fun h => hi (Subtype.ext h)
            simp only [X, if_neg this, zero_mul]
        · have hpt : p t = 0 := by
            by_contra h; exact ht (hp t h)
          rw [hpt]
          simp only [zero_mul]
          symm
          rw [Finset.sum_mul]
          apply Finset.sum_eq_zero
          intro i _
          have : (i : m) ≠ t := fun h => ht (h ▸ i.2)
          simp only [X, if_neg this, zero_mul]
      · intro k hk
        have : (k : n) ≠ s := fun h => hk (Subtype.ext h)
        simp only [Y, if_neg this, mul_zero]
    · have hqs : q s = 0 := by
        by_contra h; exact hs (hq s h)
      rw [hqs, mul_zero]
      symm
      apply Finset.sum_eq_zero
      intro k _
      have : (k : n) ≠ s := fun h => hs (h ▸ k.2)
      simp only [Y, if_neg this, mul_zero]
  rw [key]
  exact (rank_mul_le_left _ _).trans (rank_mul_le_right _ _)

/-- Rank cannot increase under a ring homomorphism of fields (extension of scalars).
Only this direction is needed. -/
theorem rank_map_le {K : Type*} [Field K] (f : F →+* K) {m n : Type*} [Fintype m] [Fintype n]
    (A : Matrix m n F) : (A.map f).rank ≤ A.rank := by
  rw [rank_eq_finrank_span_cols, rank_eq_finrank_span_cols]
  set W := Submodule.span F (Set.range A.col) with hW
  let b := Module.finBasis F W
  let g : Fin (Module.finrank F W) → (m → K) := fun i => fun t => f ((b i : m → F) t)
  have hsub : Submodule.span K (Set.range (A.map f).col) ≤ Submodule.span K (Set.range g) := by
    rw [Submodule.span_le]
    rintro _ ⟨s, rfl⟩
    have hmem : A.col s ∈ W := Submodule.subset_span ⟨s, rfl⟩
    have hrep := b.sum_repr ⟨A.col s, hmem⟩
    have hcol : (A.map f).col s = ∑ i, f (b.repr ⟨A.col s, hmem⟩ i) • g i := by
      ext t
      have h2 := congrArg (fun w : W => f ((w : m → F) t)) hrep
      simp only [Submodule.coe_sum, Submodule.coe_smul, Finset.sum_apply, Pi.smul_apply,
        smul_eq_mul, map_sum, map_mul] at h2
      simp only [col_apply, map_apply, Finset.sum_apply, Pi.smul_apply, smul_eq_mul, g]
      exact h2.symm
    rw [SetLike.mem_coe, hcol]
    exact Submodule.sum_mem _ fun i _ =>
      Submodule.smul_mem _ _ (Submodule.subset_span ⟨i, rfl⟩)
  calc Module.finrank K (Submodule.span K (Set.range (A.map f).col))
      ≤ Module.finrank K (Submodule.span K (Set.range g)) := Submodule.finrank_mono hsub
    _ ≤ Fintype.card (Fin (Module.finrank F W)) := finrank_range_le_card g
    _ = Module.finrank F W := Fintype.card_fin _

end Helpers

/-! ## The core lemma: Hadamard-diagonal identity ⇒ rank-sum bound -/

/-- **Core lemma.** Let `B : ι × ι` over a field `F`, and vectors `p j, q j : ι → F`
(`j : T`). If the Hadamard product `N t s = B t s * ∑ⱼ p j t * q j s` is diagonal with
nonzero diagonal, then for any sets `S j ⊇ supp (p j)`, `U j ⊇ supp (q j)`,
`|ι| ≤ ∑ⱼ rank (B restricted to S j × U j)`. -/
theorem hadamard_diag_rank_sum {F : Type*} [Field F] {ι T : Type*} [Fintype ι]
    [DecidableEq ι] [Fintype T] (B : Matrix ι ι F) (p q : T → ι → F)
    (S U : T → Finset ι)
    (hpS : ∀ j t, p j t ≠ 0 → t ∈ S j) (hqU : ∀ j s, q j s ≠ 0 → s ∈ U j)
    (hoff : ∀ t s, t ≠ s → B t s * ∑ j, p j t * q j s = 0)
    (hdiag : ∀ t, B t t * ∑ j, p j t * q j t ≠ 0) :
    Fintype.card ι ≤ ∑ j, (B.submatrix ((↑) : S j → ι) ((↑) : U j → ι)).rank := by
  classical
  let w : ι → F := fun t => B t t * ∑ j, p j t * q j t
  have hN : ∑ j, diagonal (p j) * B * diagonal (q j) = diagonal w := by
    ext t s
    rw [Matrix.sum_apply]
    simp only [mul_diagonal, diagonal_mul]
    have : ∑ j, p j t * B t s * q j s = B t s * ∑ j, p j t * q j s := by
      rw [Finset.mul_sum]; exact Finset.sum_congr rfl fun j _ => by ring
    rw [this]
    by_cases hts : t = s
    · subst hts; simp [w]
    · rw [diagonal_apply_ne _ hts]; exact hoff t s hts
  have hrank : (diagonal w).rank = Fintype.card ι := by
    rw [rank_diagonal]
    exact Fintype.card_congr (Equiv.subtypeUnivEquiv fun t => hdiag t)
  calc Fintype.card ι = (∑ j, diagonal (p j) * B * diagonal (q j)).rank := by rw [hN, hrank]
    _ ≤ ∑ j, (diagonal (p j) * B * diagonal (q j)).rank := rank_sum_le _ _
    _ ≤ _ := Finset.sum_le_sum fun j _ =>
        rank_diag_mul_mul_diag_le B (p j) (q j) (S j) (U j) (hpS j) (hqU j)

/-! ## Setup -/

section Setup

variable {K : Type*} [Field K] {v T : ℕ}

/-- `M t s = ∑ⱼ P t j * Q s j`. -/
def M (P Q : Fin v → Fin T → K) : Matrix (Fin v) (Fin v) K :=
  Matrix.of fun t s => ∑ j, P t j * Q s j

open Classical in
/-- Row support `R_j = {t | P t j ≠ 0}`. -/
noncomputable def R (P : Fin v → Fin T → K) (j : Fin T) : Finset (Fin v) :=
  Finset.univ.filter fun t => P t j ≠ 0

open Classical in
/-- Column support `A_j = {s | Q s j ≠ 0}`. -/
noncomputable def A (Q : Fin v → Fin T → K) (j : Fin T) : Finset (Fin v) :=
  Finset.univ.filter fun s => Q s j ≠ 0

end Setup

/-! ## Lemma B (lift identity) -/

/-- **Lemma B.** `B` over the same field `K` as `P, Q`, with nonzero diagonal, such that
`B t s ≠ 0, t ≠ s ⇒ M t s = 0`, and `M t t ≠ 0`. Then `v ≤ ∑ⱼ rank (B[R_j, A_j])`. -/
theorem lemmaB {K : Type*} [Field K] {v T : ℕ} (P Q : Fin v → Fin T → K)
    (B : Matrix (Fin v) (Fin v) K)
    (hBdiag : ∀ t, B t t ≠ 0)
    (hBM : ∀ t s, B t s ≠ 0 → t ≠ s → M P Q t s = 0)
    (hMdiag : ∀ t, M P Q t t ≠ 0) :
    v ≤ ∑ j, (B.submatrix ((↑) : R P j → Fin v) ((↑) : A Q j → Fin v)).rank := by
  have h := hadamard_diag_rank_sum B (fun j t => P t j) (fun j s => Q s j) (R P) (A Q)
    (fun j t ht => by simp [R, ht]) (fun j s hs => by simp [A, hs])
    (fun t s hts => by
      by_cases hB : B t s = 0
      · rw [hB, zero_mul]
      · have := hBM t s hB hts
        simp only [M, of_apply] at this
        rw [this, mul_zero])
    (fun t => mul_ne_zero (hBdiag t) (by simpa [M] using hMdiag t))
  simpa using h

/-! ## Lemma CR2 (char-2 realisation) -/

/-- **Lemma CR2.** `B` over `𝔽₂` with `B t t ≠ 0`. `P, Q` over any field `K` (giving the
supports `R_j, A_j`), and `P~, Q~` over a field `L` of characteristic 2 with
`supp P~ t ⊆ supp P t`, `supp Q~ s ⊆ supp Q s`, `P~ t · Q~ s = 0` whenever `B t s = 1`,
`t ≠ s`, and `P~ t · Q~ t ≠ 0`. Then `v ≤ ∑ⱼ rank_𝔽₂ (B[R_j, A_j])`. -/
theorem lemmaCR2 {K L : Type*} [Field K] [Field L] [CharP L 2] {v T : ℕ}
    (P Q : Fin v → Fin T → K) (B : Matrix (Fin v) (Fin v) (ZMod 2))
    (Pt Qt : Fin v → Fin T → L)
    (hBdiag : ∀ t, B t t ≠ 0)
    (hPsupp : ∀ t j, Pt t j ≠ 0 → P t j ≠ 0)
    (hQsupp : ∀ s j, Qt s j ≠ 0 → Q s j ≠ 0)
    (hoff : ∀ t s, B t s = 1 → t ≠ s → ∑ j, Pt t j * Qt s j = 0)
    (hdiag : ∀ t, ∑ j, Pt t j * Qt t j ≠ 0) :
    v ≤ ∑ j, (B.submatrix ((↑) : R P j → Fin v) ((↑) : A Q j → Fin v)).rank := by
  let f : ZMod 2 →+* L := ZMod.castHom (dvd_refl 2) L
  have h01 : ∀ x : ZMod 2, x = 0 ∨ x = 1 := by decide
  have h := hadamard_diag_rank_sum (B.map f) (fun j t => Pt t j) (fun j s => Qt s j)
    (R P) (A Q)
    (fun j t ht => by simpa [R] using hPsupp t j ht)
    (fun j s hs => by simpa [A] using hQsupp s j hs)
    (fun t s hts => by
      rcases h01 (B t s) with hB | hB
      · simp [hB]
      · simp only [map_apply]; rw [hoff t s hB hts, mul_zero])
    (fun t => by
      have h1 : B t t = 1 := (h01 (B t t)).resolve_left (hBdiag t)
      simp only [map_apply, h1, map_one, one_mul]
      exact hdiag t)
  rw [Fintype.card_fin] at h
  refine h.trans (Finset.sum_le_sum fun j _ => ?_)
  exact rank_map_le f (B.submatrix _ _)

end DecoderDuality

#print axioms DecoderDuality.hadamard_diag_rank_sum
#print axioms DecoderDuality.lemmaB
#print axioms DecoderDuality.lemmaCR2
