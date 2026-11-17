/-
SPECBREAK RB4 general rank lemma (item 1), Source: internal notes item 1, RB1/RESULT.md (definitions of Delta, V, e1).
See SpecRankP.md for the exact statements.
-/
import Mathlib.LinearAlgebra.Determinant
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.Matrix.ToLin
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.Abel

open Module LinearMap

set_option linter.unusedSectionVars false

namespace SpecRankP

variable {K W : Type*} [Field K] [AddCommGroup W] [Module K W] [FiniteDimensional K W]

/-- If `P - 1` maps into `V`, `dim V ≤ 2`, `P s₀ = -s₀`, `P e₁ = e₁` with `s₀, e₁ ∈ V` independent,
then `det P = -1`. -/
theorem det_neg_one (V : Submodule K W) (hV : finrank K V ≤ 2) (P : W →ₗ[K] W)
    (hP : ∀ w, P w - w ∈ V) (s0 e1 : W) (hs0 : s0 ∈ V) (he1 : e1 ∈ V)
    (hind : ∀ a b : K, a • s0 + b • e1 = 0 → a = 0 ∧ b = 0)
    (hPs : P s0 = -s0) (hPe : P e1 = e1) : P.det = -1 := by
  have hmap : ∀ v ∈ V, P v ∈ V := fun v hv => by
    have := V.add_mem (hP v) hv
    simpa using this
  have he : V ≤ V.comap P := fun v hv => hmap v hv
  rw [LinearMap.det_eq_det_mul_det V P he]
  have hq : V.mapQ V P he = LinearMap.id := by
    refine LinearMap.ext fun x => ?_
    obtain ⟨w, rfl⟩ := Submodule.Quotient.mk_surjective V x
    simp only [Submodule.mapQ_apply, LinearMap.id_apply]
    exact (Submodule.Quotient.eq V).2 (hP w)
  rw [hq, LinearMap.det_id, mul_one]
  let x0 : V := ⟨s0, hs0⟩
  let x1 : V := ⟨e1, he1⟩
  have hli : LinearIndependent K ![x0, x1] := by
    rw [Fintype.linearIndependent_iff]
    intro g hg
    have h' : g 0 • s0 + g 1 • e1 = 0 := by
      have := congrArg Subtype.val hg
      simpa [Fin.sum_univ_two, x0, x1] using this
    have := hind _ _ h'
    intro i; fin_cases i
    · exact this.1
    · exact this.2
  have hcard : Fintype.card (Fin 2) = finrank K V := by
    have := hli.fintype_card_le_finrank
    simp only [Fintype.card_fin] at this ⊢
    omega
  let b := basisOfLinearIndependentOfCardEqFinrank hli hcard
  have hb : ∀ i, b i = ![x0, x1] i := fun i => by
    simp [b]
  rw [← LinearMap.det_toMatrix b, Matrix.det_fin_two]
  have e0 : (P.restrict he) (b 0) = -(b 0) := by
    rw [hb]; exact Subtype.ext (by simpa [x0] using hPs)
  have e1' : (P.restrict he) (b 1) = b 1 := by
    rw [hb]; exact Subtype.ext (by simpa [x1] using hPe)
  simp [LinearMap.toMatrix_apply, e0, e1']

/-- **RB4 general rank lemma, abstract form.** `S` a subspace on which `Δ = -1`, a vector `e₁ ∉ S`
with `Δ e₁ = e₁`, `V ∋ e₁` with `dim V ≤ 2`, `im(P - 1) ⊆ V`, `det P = 1`, char ≠ 2.
Then `dim S ≤ rank(Δ - P)`. -/
theorem rank_ge (h2 : (2 : K) ≠ 0) (S V : Submodule K W) (Δ P : W →ₗ[K] W)
    (hΔS : ∀ s ∈ S, Δ s = -s) (e1 : W) (hΔe : Δ e1 = e1) (heS : e1 ∉ S)
    (hV : finrank K V ≤ 2) (heV : e1 ∈ V) (hP : ∀ w, P w - w ∈ V) (hdet : P.det = 1) :
    finrank K S ≤ finrank K (range (Δ - P)) := by
  set f := Δ - P with hf
  have hfw : ∀ w, f w = Δ w - P w := fun w => rfl
  have hfs : ∀ s ∈ S, f s = -((2 : K) • s) - (P s - s) := by
    intro s hs
    rw [hfw, hΔS s hs, two_smul]; abel
  have hc : ∀ s ∈ S, f s ∈ V → s ∈ V := by
    intro s hs hfv
    have h2s : (2 : K) • s ∈ V := by
      have : (2 : K) • s = -(f s) - (P s - s) := by rw [hfs s hs]; abel
      rw [this]; exact V.sub_mem (V.neg_mem hfv) (hP s)
    have := V.smul_mem (2 : K)⁻¹ h2s
    rwa [smul_smul, inv_mul_cancel₀ h2, one_smul] at this
  have hfe : f e1 ∈ V := by
    have : f e1 = -(P e1 - e1) := by rw [hfw, hΔe]; abel
    rw [this]; exact V.neg_mem (hP e1)
  have hSV : finrank K (S ⊓ V : Submodule K W) ≤ 1 := by
    have hlt : (S ⊓ V) < V := lt_of_le_of_ne inf_le_right (fun h => heS (by
      have : e1 ∈ S ⊓ V := by rw [h]; exact heV
      exact this.1))
    have := Submodule.finrank_lt_finrank_of_lt hlt
    omega
  let fS : S →ₗ[K] W := f.comp S.subtype
  have hrn := LinearMap.finrank_range_add_finrank_ker fS
  have hrangeS : range fS = Submodule.map f S := by
    rw [LinearMap.range_comp, Submodule.range_subtype]
  have hrange : Submodule.map f S ≤ range f := by
    rw [← hrangeS]; exact LinearMap.range_comp_le_range _ _
  by_cases hk : ker fS = ⊥
  · have h0 : finrank K (ker fS) = 0 := by rw [hk]; simp
    have : finrank K S ≤ finrank K (Submodule.map f S) := by rw [← hrangeS]; omega
    exact this.trans (Submodule.finrank_mono hrange)
  · obtain ⟨⟨s0, hs0S⟩, hs0k, hs0ne⟩ := (Submodule.ne_bot_iff _).1 hk
    have hfs0 : f s0 = 0 := by simpa [fS] using hs0k
    have hs0ne' : s0 ≠ 0 := fun h => hs0ne (Subtype.ext h)
    have hs0V : s0 ∈ V := hc s0 hs0S (by rw [hfs0]; exact V.zero_mem)
    -- kernel dimension ≤ 1
    have hkle : finrank K (ker fS) ≤ 1 := by
      rw [← Submodule.finrank_map_subtype_eq S (ker fS)]
      refine le_trans (Submodule.finrank_mono ?_) hSV
      rintro w ⟨⟨s, hs⟩, hsk, rfl⟩
      refine ⟨hs, hc s hs ?_⟩
      have : f s = 0 := by simpa [fS] using hsk
      rw [this]; exact V.zero_mem
    -- S ⊓ V is spanned by s0
    have hspan : ∀ s ∈ S, s ∈ V → ∃ c : K, s = c • s0 := by
      intro s hs hsV
      let v0 : (S ⊓ V : Submodule K W) := ⟨s0, hs0S, hs0V⟩
      have hv0 : v0 ≠ 0 := fun h => hs0ne' (congrArg Subtype.val h)
      have hpos : 0 < finrank K (S ⊓ V : Submodule K W) :=
        Module.finrank_pos_iff_exists_ne_zero.2 ⟨v0, hv0⟩
      have h1 : finrank K (S ⊓ V : Submodule K W) = 1 := by omega
      obtain ⟨c, hc'⟩ := (finrank_eq_one_iff_of_nonzero' v0 hv0).1 h1 ⟨s, hs, hsV⟩
      exact ⟨c, (congrArg Subtype.val hc').symm⟩
    have hind : ∀ a b : K, a • s0 + b • e1 = 0 → a = 0 ∧ b = 0 := by
      intro a b hab
      have hb : b = 0 := by
        by_contra hb
        apply heS
        have : e1 = (-(a / b)) • s0 := by
          have : b • e1 = -(a • s0) := eq_neg_of_add_eq_zero_right hab
          calc e1 = b⁻¹ • (b • e1) := by rw [smul_smul, inv_mul_cancel₀ hb, one_smul]
            _ = (-(a / b)) • s0 := by rw [this, smul_neg, smul_smul]; simp [div_eq_inv_mul]
        rw [this]; exact S.smul_mem _ hs0S
      subst hb
      simp only [zero_smul, add_zero, smul_eq_zero] at hab
      exact ⟨hab.resolve_right hs0ne', rfl⟩
    have hfe0 : f e1 ≠ 0 := by
      intro h0
      have hPe : P e1 = e1 := by
        have : Δ e1 - P e1 = 0 := h0
        rw [hΔe] at this; exact (sub_eq_zero.1 this).symm
      have hPs : P s0 = -s0 := by
        have : Δ s0 - P s0 = 0 := hfs0
        rw [hΔS s0 hs0S] at this; exact (sub_eq_zero.1 this).symm
      have := det_neg_one V hV P hP s0 e1 hs0V heV hind hPs hPe
      rw [hdet] at this
      apply h2
      have : (1 : K) + 1 = 0 := by linear_combination this
      simpa [one_add_one_eq_two] using this
    have hnot : f e1 ∉ Submodule.map f S := by
      rintro ⟨s, hs, hse⟩
      obtain ⟨c, rfl⟩ := hspan s hs (hc s hs (by rw [hse]; exact hfe))
      apply hfe0
      rw [← hse, map_smul, hfs0, smul_zero]
    have hdim := Submodule.finrank_sup_span_singleton hnot
    have hle : (Submodule.map f S ⊔ Submodule.span K {f e1} : Submodule K W) ≤ range f := by
      refine sup_le hrange ?_
      rw [Submodule.span_le]; rintro _ rfl; exact ⟨e1, rfl⟩
    have h1 := Submodule.finrank_mono hle
    have h3 : finrank K S ≤ finrank K (Submodule.map f S) + 1 := by
      rw [← hrangeS]; omega
    omega


/-! ## Matrix form in the RB1 coordinates (e₁ | S = 4 coordinates | ancillas) -/
section Mat
open Matrix

/-- `Δ = -1` on the four `S`-coordinates, `+1` on `e₁` and the ancillas. -/
def Dl (K : Type*) [Field K] (ι : Type*) [DecidableEq ι] : Matrix (Unit ⊕ Fin 4 ⊕ ι) (Unit ⊕ Fin 4 ⊕ ι) K :=
  Matrix.diagonal (Sum.elim (fun _ => 1) (Sum.elim (fun _ => -1) (fun _ => 1)))

/-- **RB4 item 1, concrete form.** char ≠ 2, `V` a subspace of dimension ≤ 2 containing `e₁`,
`im(P - I) ⊆ V`, `det P = 1` ⇒ `rank(Δ - P) ≥ 4`. -/
theorem rank_ge_four {K : Type*} [Field K] {ι : Type*} [Fintype ι] [DecidableEq ι]
    (h2 : (2 : K) ≠ 0) (P : Matrix (Unit ⊕ Fin 4 ⊕ ι) (Unit ⊕ Fin 4 ⊕ ι) K)
    (V : Submodule K (Unit ⊕ Fin 4 ⊕ ι → K)) (hV : finrank K V ≤ 2)
    (he1 : (Pi.single (Sum.inl ()) 1 : Unit ⊕ Fin 4 ⊕ ι → K) ∈ V)
    (hP : ∀ w, P *ᵥ w - w ∈ V) (hdet : P.det = 1) :
    4 ≤ (Dl K ι - P).rank := by
  let S : Submodule K (Unit ⊕ Fin 4 ⊕ ι → K) :=
    Submodule.span K (Set.range fun i : Fin 4 => (Pi.single (Sum.inr (Sum.inl i)) 1 : Unit ⊕ Fin 4 ⊕ ι → K))
  have hli : LinearIndependent K (fun i : Fin 4 => (Pi.single (Sum.inr (Sum.inl i)) 1 : Unit ⊕ Fin 4 ⊕ ι → K)) := by
    have := (Pi.basisFun K (Unit ⊕ Fin 4 ⊕ ι)).linearIndependent
    have h := this.comp (fun i : Fin 4 => (Sum.inr (Sum.inl i) : Unit ⊕ Fin 4 ⊕ ι))
      (fun a b h => by simpa using h)
    convert h using 1
    funext i
    simp [Pi.basisFun_apply]
  have hS : finrank K S = 4 := by
    simpa using finrank_span_eq_card hli
  have hΔS : ∀ s ∈ S, Matrix.toLin' (Dl K ι) s = -s := by
    intro s hs
    refine Submodule.span_induction ?_ ?_ ?_ ?_ hs
    · rintro _ ⟨i, rfl⟩
      ext j
      simp [Dl, Matrix.toLin'_apply, Matrix.mulVec_diagonal, Pi.single_apply]
      aesop
    · simp
    · intro x y _ _ hx hy; rw [map_add, hx, hy]; abel
    · intro a x _ hx; rw [map_smul, hx]; simp
  have hΔe : Matrix.toLin' (Dl K ι) (Pi.single (Sum.inl ()) 1) = Pi.single (Sum.inl ()) 1 := by
    ext j
    simp only [Dl, Matrix.toLin'_apply, Matrix.mulVec_diagonal, Pi.single_apply]
    split_ifs with h <;> simp [h]
  have heS : (Pi.single (Sum.inl ()) 1 : Unit ⊕ Fin 4 ⊕ ι → K) ∉ S := by
    intro hm
    have hmem : ∀ x ∈ S, x (Sum.inl ()) = 0 := by
      intro x hx
      refine Submodule.span_induction ?_ ?_ ?_ ?_ hx
      · rintro _ ⟨i, rfl⟩; simp [Pi.single_apply]
      · simp
      · intro x y _ _ hx hy; simp [hx, hy]
      · intro a x _ hx; simp [hx]
    have := hmem _ hm
    simp at this
  have := rank_ge h2 S V (Matrix.toLin' (Dl K ι)) (Matrix.toLin' P) hΔS _ hΔe heS hV he1
    (fun w => by simpa [Matrix.toLin'_apply] using hP w) (by rw [LinearMap.det_toLin']; exact hdet)
  rw [hS] at this
  have e : (Dl K ι - P).rank = finrank K (range (Matrix.toLin' (Dl K ι) - Matrix.toLin' P)) := by
    rw [← map_sub]; rfl
  rw [e]; exact this

end Mat

/-- Sharpness: the hypothesis `det P = 1` cannot be dropped (here `dim S = 1`, `P = Δ`, `det P = -1`,
`rank(Δ - P) = 0`). -/
theorem det_needed :
    ∃ (P Δ : Matrix (Fin 2) (Fin 2) ℚ), (∀ w, P.mulVec w - w ∈ (⊤ : Submodule ℚ (Fin 2 → ℚ))) ∧
      P.det = -1 ∧ (Δ - P).rank = 0 := by
  refine ⟨Matrix.diagonal ![-1, 1], Matrix.diagonal ![-1, 1], fun _ => trivial, ?_, ?_⟩
  · simp [Matrix.det_fin_two]
  · simp

end SpecRankP

#print axioms SpecRankP.det_neg_one
#print axioms SpecRankP.rank_ge
#print axioms SpecRankP.rank_ge_four
#print axioms SpecRankP.det_needed
