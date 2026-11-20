/-
BankNC0b (lane LEAN-NC0, Nov 18).  See cards/WILD/LEANSWARM/NC0.md.
(b) Cut lemma.  Abstract banked network: fields f (input x_f born at chart A f, output at chart B f), banks k
(one scalar each: a linear form of the values at chart `src k`, delivered to chart `dst k`).
Values are coefficient vectors in (Fld → K) (coefficients of the inputs).  Transport between charts happens ONLY
through banks (P-LOC / P-HLOC: no unpaid operation moves a value between charts); same-chart combination is free
(span); fan-out is free (a bank's d k may be read by many later banks).  The order on Bank is the execution
order (P-ACYC).  For any chart set P: (#fields entering P^c from P) ≤ (#banks entering P^c from P),
whenever every principal minor of the output matrix O is nonzero.
Kernel only: no sorry, no native_decide.
-/
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.LinearAlgebra.Dimension.StrongRankCondition
import Mathlib.LinearAlgebra.StdBasis
import Mathlib.Order.WellFounded
import Mathlib.Data.Fintype.Card

namespace BankNC0
open Finset Submodule

structure Net (K : Type) (Chart Fld Bank : Type) [Field K] [DecidableEq Fld] [LinearOrder Bank] where
  A : Fld → Chart
  B : Fld → Chart
  src : Bank → Chart
  dst : Bank → Chart
  d : Bank → Fld → K
  O : Matrix Fld Fld K
  /-- each bank reads a form of its source chart: inputs born there + earlier deliveries there -/
  read : ∀ k, d k ∈ span K ({v | ∃ g, A g = src k ∧ v = Pi.single g 1} ∪
                            {v | ∃ j, j < k ∧ dst j = src k ∧ v = d j})
  /-- each output is a form of its chart's content -/
  out : ∀ f, O f ∈ span K ({v | ∃ g, A g = B f ∧ v = Pi.single g 1} ∪
                           {v | ∃ j, dst j = B f ∧ v = d j})

variable {K : Type} {Chart Fld Bank : Type} [Field K] [Fintype Fld] [DecidableEq Fld]
  [Fintype Bank] [LinearOrder Bank]

/-- (b) per-cut lemma: rank across a cut ≥ number of fields crossing it. -/
theorem cut_lemma (N : Net K Chart Fld Bank)
    (hminor : ∀ C : Finset Fld,
      (N.O.submatrix (fun c : C => (c : Fld)) (fun c : C => (c : Fld))).det ≠ 0)
    (P : Chart → Prop) [DecidablePred P] :
    (Finset.univ.filter (fun f => P (N.A f) ∧ ¬ P (N.B f))).card ≤
    (Finset.univ.filter (fun k => P (N.src k) ∧ ¬ P (N.dst k))).card := by
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
  set C : Finset Fld := Finset.univ.filter (fun f => P (N.A f) ∧ ¬ P (N.B f)) with hC
  set T : Finset Bank := Finset.univ.filter (fun k => P (N.src k) ∧ ¬ P (N.dst k)) with hT
  have hCm : ∀ c : C, P (N.A c) ∧ ¬ P (N.B c) := fun c => by
    exact (Finset.mem_filter.mp c.2).2
  let r : (Fld → K) →ₗ[K] (C → K) := LinearMap.funLeft K K (fun c : C => (c : Fld))
  have hli : LinearIndependent K (fun c : C => r (N.O c)) :=
    Matrix.linearIndependent_rows_of_det_ne_zero (hminor C)
  let w : Finset (C → K) := T.image (fun j => r (N.d j))
  have hmem : Set.range (fun c : C => r (N.O c)) ≤ (span K (w : Set (C → K)) : Set (C → K)) := by
    rintro _ ⟨c, rfl⟩
    have h1 : N.O c ∈ W := claim2 c (hCm c).2
    have h2 : r (N.O c) ∈ W.map r := Submodule.mem_map_of_mem h1
    rw [hW, Submodule.map_span] at h2
    refine (span_le.mpr ?_) h2
    rintro _ ⟨v, hv | hv, rfl⟩
    · obtain ⟨g, hg, rfl⟩ := hv
      have : r (Pi.single g 1) = 0 := by
        funext c'
        have : (c' : Fld) ≠ g := fun h => hg (h ▸ (hCm c').1)
        simp [r, LinearMap.funLeft, Pi.single_apply, this]
      rw [this]; exact zero_mem _
    · obtain ⟨j, hj1, hj2, rfl⟩ := hv
      apply subset_span
      simp only [w, Finset.coe_image, Set.mem_image, Finset.mem_coe]
      exact ⟨j, by rw [hT, Finset.mem_filter]; exact ⟨Finset.mem_univ _, hj1, hj2⟩, rfl⟩
  have := linearIndependent_le_span' _ hli (w : Set (C → K)) hmem
  rw [Cardinal.mk_fintype] at this
  have h3 : Fintype.card C ≤ Fintype.card (w : Set (C → K)) := by exact_mod_cast this
  simp only [Finset.coe_sort_coe, Fintype.card_coe] at h3
  have h5 : w.card ≤ T.card := Finset.card_image_le
  show C.card ≤ T.card
  omega

end BankNC0
