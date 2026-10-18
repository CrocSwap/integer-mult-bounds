/-
Copyright (c) 2026 conorholds. All rights reserved.
Released under Apache 2.0 license as described in the repository LICENSE.
Prepared with substantial OpenAI Codex assistance.
-/
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas

/-!
# The coefficient-preserving one-exception root-swap argument

This file formalizes the first case of Section 3 of `e8-d0-root-swaps/PROOF.md`.
The finite family `q` generates the correction space by actual scalar linear
combinations; a witness cannot independently choose values on its union support.
The coefficient field `K` and label field `F` are independent. For E8, specialize
`F` to the binary field, `root` to the root representatives, and `pairing` to beta.

The main result is `one_exception_weighted_bound`: when all members except a
distinguished one have root-support rank bounded by label-support rank, every
swap-eligible root together has rank at most the total label-support weight.
The intermediate `one_exception_rank_bound` isolates the regular-support span.
This proves the at-most-one-exception case of Theorem A. No E8 geometric input,
exceptional-support classification, two-factor lemma, or C7 weighted-basis
reduction is asserted here.
-/

noncomputable section

open scoped BigOperators
open Submodule

namespace RootSwapOneExceptional

attribute [local instance] Classical.propDecidable

variable {K F E J V W : Type*}
variable [Field K] [Field F] [Fintype J]
variable [AddCommGroup V] [Module K V]
variable [AddCommGroup W] [Module F W]

/-- An actual vector in the scalar span of the specified coefficient family. -/
def combination (q : J → E → K) (c : J → K) (t : E) : K :=
  ∑ j, c j * q j t

/-- A swap witness has a nonzero own coordinate and vanishes at all other
orthogonal coordinates. The root itself is allowed in the support. -/
def Eligible (orthogonal : E → E → Prop) (q : J → E → K) (t : E) : Prop :=
  ∃ c : J → K, combination q c t ≠ 0 ∧
    ∀ s, s ≠ t → orthogonal s t → combination q c s = 0

/-- The coefficient representation agrees exactly with the submodule span;
this is the bridge to a correction space presented by a basis or generating family. -/
theorem combination_mem_span (q : J → E → K) (c : J → K) :
    combination q c ∈ Submodule.span K (Set.range q) := by
  apply (Submodule.mem_span_range_iff_exists_fun K).mpr
  refine ⟨c, ?_⟩
  ext t
  simp [combination, Finset.sum_apply, smul_eq_mul]

/-- Eligibility is equivalent to an actual vector in the generated subspace,
with precisely the original own-coordinate and orthogonal-coordinate conditions. -/
theorem eligible_iff_span_witness (orthogonal : E → E → Prop)
    (q : J → E → K) (t : E) :
    Eligible orthogonal q t ↔
      ∃ tau : E → K, tau ∈ Submodule.span K (Set.range q) ∧ tau t ≠ 0 ∧
        ∀ s, s ≠ t → orthogonal s t → tau s = 0 := by
  constructor
  · rintro ⟨c, hc, hz⟩
    exact ⟨combination q c, combination_mem_span q c, hc, hz⟩
  · rintro ⟨tau, htau, hown, hzero⟩
    obtain ⟨c, hc⟩ := (Submodule.mem_span_range_iff_exists_fun K).mp htau
    have hcs : ∀ s, combination q c s = tau s := by
      intro s
      simpa [combination, Finset.sum_apply, smul_eq_mul] using congrFun hc s
    refine ⟨c, ?_, ?_⟩
    · rwa [hcs]
    · intro s hst horth
      rw [hcs]
      exact hzero s hst horth

/-- Coordinates eligible for a swap whose root vector is outside `O`. -/
def Outside (orthogonal : E → E → Prop) (q : J → E → K)
    (root : E → V) (O : Submodule K V) : Set E :=
  {t | Eligible orthogonal q t ∧ root t ∉ O}

/-- Binary label rank is the intended specialization of this support weight. -/
def supportWeight (label : E → W) (q : E → K) : ℕ :=
  Module.finrank F (Submodule.span F (label '' {t | q t ≠ 0}))

/-- Away from `O`, all actual witnesses retain the same distinguished member,
with their own single scalar coefficient. -/
theorem combination_outside (q : J → E → K) (e : J)
    (root : E → V) (O : Submodule K V)
    (regular : ∀ j, j ≠ e → ∀ t, q j t ≠ 0 → root t ∈ O)
    (c : J → K) (t : E) (ht : root t ∉ O) :
    combination q c t = c e * q e t := by
  classical
  unfold combination
  apply Finset.sum_eq_single e
  · intro j _ hje
    have hz : q j t = 0 := by
      by_contra hn
      exact ht (regular j hje t hn)
    simp [hz]
  · simp

/-- Both the distinguished coefficient and its own-coordinate value are nonzero. -/
theorem outside_witness_nonzero (q : J → E → K) (e : J)
    (root : E → V) (O : Submodule K V)
    (regular : ∀ j, j ≠ e → ∀ t, q j t ≠ 0 → root t ∈ O)
    (c : J → K) (t : E) (ht : root t ∉ O)
    (hc : combination q c t ≠ 0) : c e ≠ 0 ∧ q e t ≠ 0 := by
  rw [combination_outside q e root O regular c t ht] at hc
  exact mul_ne_zero_iff.mp hc

/-- The shared-coefficient argument: eligible roots outside `O` cannot be
orthogonal to one another. This does not replace the space by union support. -/
theorem outside_pairwise_nonorthogonal
    (orthogonal : E → E → Prop) (q : J → E → K) (e : J)
    (root : E → V) (O : Submodule K V)
    (regular : ∀ j, j ≠ e → ∀ t, q j t ≠ 0 → root t ∈ O)
    {s t : E} (hs : s ∈ Outside orthogonal q root O)
    (ht : t ∈ Outside orthogonal q root O) (hst : s ≠ t) :
    ¬ orthogonal s t := by
  obtain ⟨cs, hcs, _⟩ := hs.1
  obtain ⟨ct, hct, hzero⟩ := ht.1
  have hsne := (outside_witness_nonzero q e root O regular cs s hs.2 hcs).2
  have htne := (outside_witness_nonzero q e root O regular ct t ht.2 hct).1
  intro horth
  have hz := hzero s hst horth
  rw [combination_outside q e root O regular ct s hs.2] at hz
  exact (mul_ne_zero htne hsne) hz

/-- A family with a diagonal-one/off-diagonal-zero pairing is independent;
positivity or an ordered field is not needed, so this applies in characteristic two. -/
theorem independent_of_pairing {I : Type*} [Fintype I]
    (v : I → W) (pairing : W →ₗ[F] W →ₗ[F] F)
    (diagonal : ∀ i, pairing (v i) (v i) = 1)
    (offDiagonal : ∀ i j, i ≠ j → pairing (v i) (v j) = 0) :
    LinearIndependent F v := by
  classical
  apply Fintype.linearIndependent_iff.mpr
  intro c hc i
  have h := congrArg (pairing (v i)) hc
  simp only [map_sum, map_smul, map_zero] at h
  have hs : (∑ j, c j • pairing (v i) (v j)) = c i := by
    calc
      _ = c i • pairing (v i) (v i) := by
        apply Finset.sum_eq_single i
        · intro j _ hji
          rw [offDiagonal i j (Ne.symm hji), smul_zero]
        · simp
      _ = c i := by rw [diagonal i, smul_eq_mul, mul_one]
  exact hs.symm.trans h

variable [Fintype E] [FiniteDimensional F W]

/-- The outside eligible labels are independent and lie in the distinguished
support span, so their number is at most that member's support weight. -/
theorem outside_card_le_supportWeight
    (orthogonal : E → E → Prop) (q : J → E → K) (e : J)
    (root : E → V) (O : Submodule K V) (label : E → W)
    (pairing : W →ₗ[F] W →ₗ[F] F)
    (diagonal : ∀ t, pairing (label t) (label t) = 1)
    (nonorthogonal : ∀ s t, s ≠ t → ¬ orthogonal s t →
      pairing (label s) (label t) = 0)
    (regular : ∀ j, j ≠ e → ∀ t, q j t ≠ 0 → root t ∈ O) :
    Fintype.card (Outside orthogonal q root O) ≤ supportWeight (F := F) label (q e) := by
  classical
  let A := Outside orthogonal q root O
  have hlin : LinearIndependent F (fun t : A => label t) := by
    apply independent_of_pairing _ pairing
    · intro t
      exact diagonal t
    · intro s t hst
      apply nonorthogonal s t
      · exact fun h => hst (Subtype.ext h)
      · exact outside_pairwise_nonorthogonal orthogonal q e root O regular
          s.property t.property (fun h => hst (Subtype.ext h))
  let U := Submodule.span F (label '' {t | q e t ≠ 0})
  have hmem : ∀ t : A, label t ∈ U := by
    intro t
    obtain ⟨c, hc, _⟩ := t.property.1
    have hqt := (outside_witness_nonzero q e root O regular c t t.property.2 hc).2
    exact Submodule.subset_span ⟨t, hqt, rfl⟩
  let v : A → U := fun t => ⟨label t, hmem t⟩
  have hlinU : LinearIndependent F v := by
    apply LinearIndependent.of_comp U.subtype
    exact hlin
  exact hlinU.fintype_card_le_finrank

variable [FiniteDimensional K V]

/-- The coefficient-preserving rank bound with one distinguished member.
The subspace `O` contains the root supports of every other family member.
Its dimension can therefore be bounded separately by their total weights. -/
theorem one_exception_rank_bound
    (orthogonal : E → E → Prop) (q : J → E → K) (e : J)
    (root : E → V) (O : Submodule K V) (label : E → W)
    (pairing : W →ₗ[F] W →ₗ[F] F)
    (diagonal : ∀ t, pairing (label t) (label t) = 1)
    (nonorthogonal : ∀ s t, s ≠ t → ¬ orthogonal s t →
      pairing (label s) (label t) = 0)
    (regular : ∀ j, j ≠ e → ∀ t, q j t ≠ 0 → root t ∈ O) :
    Module.finrank K (Submodule.span K (root '' {t | Eligible orthogonal q t})) ≤
      Module.finrank K O + supportWeight (F := F) label (q e) := by
  classical
  let A := Outside orthogonal q root O
  let R := Submodule.span K (Set.range (fun t : A => root t))
  have hspan : Submodule.span K (root '' {t | Eligible orthogonal q t}) ≤ O ⊔ R := by
    apply Submodule.span_le.mpr
    rintro _ ⟨t, ht, rfl⟩
    by_cases hO : root t ∈ O
    · exact (show O ≤ O ⊔ R from le_sup_left) hO
    · apply (show R ≤ O ⊔ R from le_sup_right)
      exact Submodule.subset_span ⟨⟨t, ht, hO⟩, rfl⟩
  calc
    _ ≤ Module.finrank K (O ⊔ R : Submodule K V) := Submodule.finrank_mono hspan
    _ ≤ Module.finrank K O + Module.finrank K R :=
      Submodule.finrank_add_le_finrank_add_finrank O R
    _ ≤ Module.finrank K O + Fintype.card A :=
      Nat.add_le_add_left (finrank_range_le_card (R := K) (fun t : A => root t)) _
    _ ≤ Module.finrank K O + supportWeight (F := F) label (q e) :=
      Nat.add_le_add_left
        (outside_card_le_supportWeight orthogonal q e root O label pairing
          diagonal nonorthogonal regular) _

omit [Fintype J] in
/-- Dimension is subadditive for the span of finitely many subspaces. -/
theorem finrank_finset_sup_le (s : Finset J) (P : J → Submodule K V) :
    Module.finrank K (s.sup P : Submodule K V) ≤ ∑ j ∈ s, Module.finrank K (P j) := by
  classical
  induction s using Finset.induction_on with
  | empty => simp
  | @insert j s hjs ih =>
    rw [Finset.sup_insert, Finset.sum_insert hjs]
    exact (Submodule.finrank_add_le_finrank_add_finrank (P j) (s.sup P)).trans
      (Nat.add_le_add_left ih _)

/-- The complete at-most-one-exception case of Theorem A, expressed for a finite
scalar generating family. Each member other than `e` has root-support rank at
most its label-support rank. No such inequality is assumed for `e`. -/
theorem one_exception_weighted_bound
    (orthogonal : E → E → Prop) (q : J → E → K) (e : J)
    (root : E → V) (label : E → W)
    (pairing : W →ₗ[F] W →ₗ[F] F)
    (diagonal : ∀ t, pairing (label t) (label t) = 1)
    (nonorthogonal : ∀ s t, s ≠ t → ¬ orthogonal s t →
      pairing (label s) (label t) = 0)
    (regularRank : ∀ j, j ≠ e →
      Module.finrank K (Submodule.span K (root '' {t | q j t ≠ 0})) ≤
        supportWeight (F := F) label (q j)) :
    Module.finrank K (Submodule.span K (root '' {t | Eligible orthogonal q t})) ≤
      ∑ j, supportWeight (F := F) label (q j) := by
  classical
  let P : J → Submodule K V := fun j =>
    Submodule.span K (root '' {t | q j t ≠ 0})
  let s : Finset J := Finset.univ.erase e
  let O : Submodule K V := s.sup P
  have regular : ∀ j, j ≠ e → ∀ t, q j t ≠ 0 → root t ∈ O := by
    intro j hje t hqt
    have hj : j ∈ s := Finset.mem_erase.mpr ⟨hje, Finset.mem_univ j⟩
    have hp : P j ≤ O := Finset.le_sup hj
    exact hp (Submodule.subset_span ⟨t, hqt, rfl⟩)
  have hO : Module.finrank K O ≤ ∑ j ∈ s, supportWeight (F := F) label (q j) := by
    apply (finrank_finset_sup_le s P).trans
    apply Finset.sum_le_sum
    intro j hj
    exact regularRank j (Finset.mem_erase.mp hj).1
  calc
    _ ≤ Module.finrank K O + supportWeight (F := F) label (q e) :=
      one_exception_rank_bound orthogonal q e root O label pairing
        diagonal nonorthogonal regular
    _ ≤ (∑ j ∈ s, supportWeight (F := F) label (q j)) +
        supportWeight (F := F) label (q e) := Nat.add_le_add_right hO _
    _ = ∑ j, supportWeight (F := F) label (q j) :=
      Finset.sum_erase_add Finset.univ
        (fun j => supportWeight (F := F) label (q j)) (Finset.mem_univ e)

#print axioms one_exception_rank_bound
#print axioms one_exception_weighted_bound

end RootSwapOneExceptional
