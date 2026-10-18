import Mathlib.LinearAlgebra.Dual.Lemmas
import Mathlib.Algebra.Field.ZMod
import Mathlib.Data.Finset.Card
import Lean

set_option autoImplicit false

/-! The geometric lemma in PR2920, without any circuit or cost assertion. -/
namespace P104AffineComplement

abbrev F₂ := ZMod 2

variable {V : Type*} [AddCommGroup V] [Module F₂ V]

/-- On the odd section, the two kernel tests are complementary. -/
theorem complementary_tests (f q : V →ₗ[F₂] F₂) (x : V) (hx : q x = 1) :
    ((f + q) x = 0 ↔ f x ≠ 0) := by
  have htwo : ∀ a : F₂, a = 0 ∨ a = 1 := by decide
  have htwo_one : (1 : F₂) + 1 = 0 := by decide
  rcases htwo (f x) with h | h <;> simp [LinearMap.add_apply, hx, h, htwo_one]

/-- The odd demand set is covered, without overlap, by the two kernels. -/
theorem kernel_partition (D : Set V) (f q : V →ₗ[F₂] F₂)
    (hodd : ∀ x ∈ D, q x = 1) :
    D ∩ (LinearMap.ker f : Set V) ∪ D ∩ (LinearMap.ker (f + q) : Set V) = D ∧
    Disjoint (D ∩ (LinearMap.ker f : Set V))
      (D ∩ (LinearMap.ker (f + q) : Set V)) := by
  constructor
  · ext x
    simp only [Set.mem_union, Set.mem_inter_iff, LinearMap.mem_ker]
    constructor
    · rintro (⟨hx, _⟩ | ⟨hx, _⟩) <;> exact hx
    · intro hx
      by_cases hf : f x = 0
      · exact Or.inl ⟨hx, hf⟩
      · exact Or.inr ⟨hx, (complementary_tests f q x (hodd x hx)).mpr hf⟩
  · rw [Set.disjoint_left]
    intro x hx hy
    exact ((complementary_tests f q x (hodd x hx.1)).mp hy.2) hx.2

/-- A split demand set forces both linear forms to be nonzero. -/
theorem split_forms_nonzero (D : Set V) (f q : V →ₗ[F₂] F₂)
    (hodd : ∀ x ∈ D, q x = 1)
    (hin : ∃ x ∈ D, f x = 0) (hout : ∃ x ∈ D, f x ≠ 0) :
    f ≠ 0 ∧ f + q ≠ 0 := by
  rcases hin with ⟨x, hx, hfx⟩
  rcases hout with ⟨y, _, hfy⟩
  constructor
  · intro hf
    exact hfy (by simp [hf])
  · intro hfq
    have hz : (f + q) x = 0 := by simp [hfq]
    have ho : (f + q) x = 1 := by simp [LinearMap.add_apply, hfx, hodd x hx]
    exact zero_ne_one (hz.symm.trans ho)

/-- Every nonzero binary linear functional has a codimension-one kernel. -/
theorem kernel_codimension_one [FiniteDimensional F₂ V]
    (f : V →ₗ[F₂] F₂) (hf : f ≠ 0) :
    Module.finrank F₂ (LinearMap.ker f) + 1 = Module.finrank F₂ V := by
  exact Module.Dual.finrank_ker_add_one_of_ne_zero hf

/-- In dimension eight, any nontrivial odd-section split gives two 7-planes. -/
theorem eight_dimensional_cover [FiniteDimensional F₂ V]
    (hdim : Module.finrank F₂ V = 8) (D : Set V) (f q : V →ₗ[F₂] F₂)
    (hodd : ∀ x ∈ D, q x = 1)
    (hin : ∃ x ∈ D, f x = 0) (hout : ∃ x ∈ D, f x ≠ 0) :
    Module.finrank F₂ (LinearMap.ker f) = 7 ∧
    Module.finrank F₂ (LinearMap.ker (f + q)) = 7 ∧
    D ∩ (LinearMap.ker f : Set V) ∪ D ∩ (LinearMap.ker (f + q) : Set V) = D ∧
    Disjoint (D ∩ (LinearMap.ker f : Set V))
      (D ∩ (LinearMap.ker (f + q) : Set V)) := by
  have hn := split_forms_nonzero D f q hodd hin hout
  have h₁ := kernel_codimension_one f hn.1
  have h₂ := kernel_codimension_one (f + q) hn.2
  have hp := kernel_partition D f q hodd
  exact ⟨by omega, by omega, hp.1, hp.2⟩

/-- Finite demand counts partition exactly; no maximality assumption is needed. -/
theorem finite_partition_counts (D : Finset V) (f q : V →ₗ[F₂] F₂)
    (hodd : ∀ x ∈ D, q x = 1) :
    (D.filter (fun x => f x = 0)).card +
      (D.filter (fun x => (f + q) x = 0)).card = D.card := by
  classical
  have he : D.filter (fun x => (f + q) x = 0) = D.filter (fun x => ¬ f x = 0) := by
    apply Finset.filter_congr
    intro x hx
    exact complementary_tests f q x (hodd x hx)
  rw [he]
  exact Finset.filter_card_add_filter_neg_card_eq_card _

/-- Omitting the odd-section premise permits overlapping kernel membership. -/
theorem even_point_counterexample :
    ∃ x : F₂, (LinearMap.id : F₂ →ₗ[F₂] F₂) x = 0 ∧
      ((LinearMap.id : F₂ →ₗ[F₂] F₂) + (LinearMap.id : F₂ →ₗ[F₂] F₂)) x = 0 := by
  exact ⟨0, by simp, by simp⟩

/-- Omitting nontriviality permits a full-dimensional first kernel. -/
theorem zero_form_counterexample :
    ∃ D : Set F₂, ∃ f q : F₂ →ₗ[F₂] F₂,
      (∀ x ∈ D, q x = 1) ∧ LinearMap.ker f = ⊤ := by
  exact ⟨{1}, 0, LinearMap.id, by simp, by simp⟩

end P104AffineComplement

/- Dependency audit adapted from research/cyclic-schur-lean/Audit.lean,
   prepared for Ali Romman. It checks every theorem in this namespace. -/
open Lean Elab Command in
def auditP104AffineComplement : CommandElabM Unit := do
  let env ← getEnv
  let mut count := 0
  for (name, _) in env.constants do
    if (`P104AffineComplement).isPrefixOf name then
      if getOriginalConstKind? env name == some .axiom then
        throwError "Package axiom: {name}"
      if getOriginalConstKind? env name == some .thm then
        count := count + 1
        let axioms ← collectAxioms name
        for axiomName in axioms do
          unless #[`propext, `Classical.choice, `Quot.sound].contains axiomName do
            throwError "Forbidden axiom in {name}: {axiomName}"
        logInfo m!"AXIOMS {name}: {axioms.toList}"
  unless count == 13 do
    throwError "Expected eight statements and five generated proofs, got {count}"
  logInfo "PASS_P104_AFFINE_COMPLEMENT_LEAN statements=8 declarations=13 standard_axioms_only"

run_cmd auditP104AffineComplement
