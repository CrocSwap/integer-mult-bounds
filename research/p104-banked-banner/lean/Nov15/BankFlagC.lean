/-
BankFlagC .  
GENERALISED CUT LEMMA (P-CUTMASS, rank form) on the BankNC0b Net model: for any chart predicate P (e.g. P c := c ∈ D_j),
rows R whose output chart is outside P and columns S whose input chart is inside P, the number of banks crossing P → P^c is
at least the rank of the cross block O[R,S] (as linear independence of its rows).  cut_lemma of BankNC0b is the case
R = S = {f : A f ∈ P, B f ∉ P} with a principal minor.  Corollary (P-BLOCK, rank step): any NONSINGULAR square submatrix
of the cross block (R ≃ S, det ≠ 0) already forces #banks ≥ |R|, so "crossings + extras" follows once a nonsingular
(crossings+extras)-sized cross submatrix is exhibited.  Kernel only: no sorry, no native_decide, no new axioms.
-/
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.LinearAlgebra.Dimension.StrongRankCondition
import Mathlib.LinearAlgebra.StdBasis
import Nov15.BankNC0b

namespace BankFlagC
open Finset Submodule BankNC0

variable {K : Type} {Chart Fld Bank : Type} [Field K] [Fintype Fld] [DecidableEq Fld]
  [Fintype Bank] [LinearOrder Bank]

theorem cut_rank (N : Net K Chart Fld Bank) (P : Chart → Prop) [DecidablePred P]
    (R S : Finset Fld) (hR : ∀ r ∈ R, ¬ P (N.B r)) (hS : ∀ s ∈ S, P (N.A s))
    (hli : LinearIndependent K (fun r : R => (fun s : S => N.O r s))) :
    R.card ≤ (Finset.univ.filter (fun k => P (N.src k) ∧ ¬ P (N.dst k))).card := by
  classical
  set W : Submodule K (Fld → K) := span K
    ({v | ∃ g, ¬ P (N.A g) ∧ v = Pi.single g 1} ∪
     {v | ∃ j, P (N.src j) ∧ ¬ P (N.dst j) ∧ v = N.d j}) with hW
  have claim1 : ∀ k, ¬ P (N.src k) → N.d k ∈ W := by
    intro k
    induction k using WellFoundedLT.induction with
    | _ k ih =>
      intro hk
      refine (span_le.mpr ?_) (N.read k)
      rintro v (⟨g, hg, rfl⟩ | ⟨j, hj, hd, rfl⟩)
      · exact subset_span (Or.inl ⟨g, by rw [hg]; exact hk, rfl⟩)
      · by_cases hs : P (N.src j)
        · exact subset_span (Or.inr ⟨j, hs, by rw [hd]; exact hk, rfl⟩)
        · exact ih j hj hs
  have claim2 : ∀ f, ¬ P (N.B f) → N.O f ∈ W := by
    intro f hf
    refine (span_le.mpr ?_) (N.out f)
    rintro v (⟨g, hg, rfl⟩ | ⟨j, hd, rfl⟩)
    · exact subset_span (Or.inl ⟨g, by rw [hg]; exact hf, rfl⟩)
    · by_cases hs : P (N.src j)
      · exact subset_span (Or.inr ⟨j, hs, by rw [hd]; exact hf, rfl⟩)
      · exact claim1 j hs
  set T : Finset Bank := Finset.univ.filter (fun k => P (N.src k) ∧ ¬ P (N.dst k)) with hT
  let r : (Fld → K) →ₗ[K] (S → K) := LinearMap.funLeft K K (fun c : S => (c : Fld))
  let w : Finset (S → K) := T.image (fun j => r (N.d j))
  have hmem : Set.range (fun c : R => r (N.O c)) ≤ (span K (w : Set (S → K)) : Set (S → K)) := by
    rintro _ ⟨c, rfl⟩
    have h1 : N.O c ∈ W := claim2 c (hR c c.2)
    have h2 : r (N.O c) ∈ W.map r := Submodule.mem_map_of_mem h1
    rw [hW, Submodule.map_span] at h2
    refine (span_le.mpr ?_) h2
    rintro _ ⟨v, hv | hv, rfl⟩
    · obtain ⟨g, hg, rfl⟩ := hv
      have : r (Pi.single g 1) = 0 := by
        funext c'
        have : (c' : Fld) ≠ g := fun h => hg (h ▸ hS c' c'.2)
        simp [r, LinearMap.funLeft, Pi.single_apply, this]
      rw [this]; exact zero_mem _
    · obtain ⟨j, hj1, hj2, rfl⟩ := hv
      apply subset_span
      simp only [w, Finset.coe_image, Set.mem_image, Finset.mem_coe]
      exact ⟨j, by rw [hT, Finset.mem_filter]; exact ⟨Finset.mem_univ _, hj1, hj2⟩, rfl⟩
  have hli' : LinearIndependent K (fun c : R => r (N.O c)) := hli
  have := linearIndependent_le_span' _ hli' (w : Set (S → K)) hmem
  rw [Cardinal.mk_fintype] at this
  have h3 : Fintype.card R ≤ Fintype.card (w : Set (S → K)) := by exact_mod_cast this
  simp only [Finset.coe_sort_coe, Fintype.card_coe] at h3
  have h5 : w.card ≤ T.card := Finset.card_image_le
  omega

/-- P-BLOCK, rank step: a nonsingular square submatrix of the cross block forces |R| crossing banks. -/
theorem cut_rank_det (N : Net K Chart Fld Bank) (P : Chart → Prop) [DecidablePred P]
    (R S : Finset Fld) (e : R ≃ S) (hR : ∀ r ∈ R, ¬ P (N.B r)) (hS : ∀ s ∈ S, P (N.A s))
    (hdet : (Matrix.of (fun (r : R) (s : R) => N.O r (e s))).det ≠ 0) :
    R.card ≤ (Finset.univ.filter (fun k => P (N.src k) ∧ ¬ P (N.dst k))).card := by
  apply cut_rank N P R S hR hS
  have h := Matrix.linearIndependent_rows_of_det_ne_zero hdet
  -- reindex columns along e
  have : LinearIndependent K (fun r : R => (fun s : S => N.O r s) ∘ (fun s : R => e s)) := h
  exact LinearIndependent.of_comp (LinearMap.funLeft K K (fun s : R => e s)) this

/-- cut_lemma recovered (R = S = field crossings, principal minor). -/
theorem cut_principal (N : Net K Chart Fld Bank) (P : Chart → Prop) [DecidablePred P]
    (R : Finset Fld) (hR : ∀ r ∈ R, P (N.A r) ∧ ¬ P (N.B r))
    (hdet : (Matrix.of (fun (r : R) (s : R) => N.O r s)).det ≠ 0) :
    R.card ≤ (Finset.univ.filter (fun k => P (N.src k) ∧ ¬ P (N.dst k))).card :=
  cut_rank_det N P R R (Equiv.refl _) (fun r h => (hR r h).2) (fun s h => (hR s h).1) hdet

end BankFlagC
#print axioms BankFlagC.cut_rank
#print axioms BankFlagC.cut_rank_det
