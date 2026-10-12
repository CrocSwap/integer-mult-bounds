import PR509Stream

/-!
A source-oriented interface for directed Clifford child recipes.

Apache-2.0. Prepared with OpenAI assistance; see NOTICE.md.

This module reuses LemmaG.Stream from PR509, exact upstream commit
7b9c720ecc9f483c383e7cd9c2ab81f06ee5df59. It does not repeat event induction.

The selected Python compiler executes right, the Gaussian Fourier block, then
left. Rank zero executes left alone and serializes a null right side. The
operators below are already interpreted linear equivalences: constructing them
from JSON, proving phase-correct child equality, and binding actual execution
remain explicit caller obligations. No finite certificate is assumed.

A source caller must supply its actual Gaussian block family, not substitute
ordinary normalized Hadamard gates. All equalities quantify over every payload.
-/
namespace CurrentMain.DirectedChildRecipes

open LemmaG LemmaG.Stream

/-- Interpreted child shape. This is not a raw JSON decoder or a correctness
certificate for the stored matrix, quadratic form, offset, or global phase. -/
structure Child (K M : Type*) [Semiring K] [AddCommMonoid M] [Module K M] where
  rank : Nat
  left : M ≃ₗ[K] M
  right : Option (M ≃ₗ[K] M)
  right_none_iff_rank_zero : right = none ↔ rank = 0

namespace Child

variable {K M : Type*} [Semiring K] [AddCommMonoid M] [Module K M]

/-- Positive-rank execution is right → block → left. A null right side executes
left alone; it does not request a block at rank zero. -/
def eval (blocks : Nat → M ≃ₗ[K] M) (c : Child K M) (v : M) : M :=
  match c.right with
  | none => c.left v
  | some right => c.left (blocks c.rank (right v))

theorem eval_rank_zero (blocks : Nat → M ≃ₗ[K] M) (c : Child K M)
    (hzero : c.rank = 0) (v : M) :
    eval blocks c v = c.left v := by
  simp only [eval, c.right_none_iff_rank_zero.mpr hzero]

theorem eval_some (blocks : Nat → M ≃ₗ[K] M) (c : Child K M)
    (right : M ≃ₗ[K] M) (hright : c.right = some right) (v : M) :
    eval blocks c v = c.left (blocks c.rank (right v)) := by
  simp only [eval, hright]

end Child

section Binding

variable {ι Λ K M : Type*}
variable [DecidableEq ι] [Semiring K] [AddCommMonoid M] [Module K M]

/-- An exact directed lookup supplies the upstream recipe predicate.

Coverage is required for every relabel in the supplied stream. In particular,
a caller cannot discard endpoint adapters or residual wrappers to claim a
complete invocation. Physical execution and all-payload operator correctness
are separate hypotheses, restricted to children actually used by the stream.
The target is T(new) after inverse T(old), with no reversed-key convention. -/
theorem recipesExact_of_children
    (T : Λ → M ≃ₗ[K] M) (blocks : Nat → M ≃ₗ[K] M)
    (lookup : Λ → Λ → Option (Child K M))
    (rec : Λ → Λ → M → M) (es : List (Event ι Λ K))
    (hcovered : ∀ r A B, Event.relabel r A B ∈ es →
      ∃ c, lookup A B = some c)
    (hphysical : ∀ r A B, Event.relabel r A B ∈ es →
      ∀ c, lookup A B = some c →
        ∀ v, rec A B v = Child.eval blocks c v)
    (hoperator : ∀ r A B, Event.relabel r A B ∈ es →
      ∀ c, lookup A B = some c →
        ∀ v, Child.eval blocks c v = T B ((T A).symm v)) :
    RecipesExact T rec es := by
  intro r A B he v
  obtain ⟨c, hc⟩ := hcovered r A B he
  exact (hphysical r A B he c hc v).trans (hoperator r A B he c hc v)

/-- Direct reuse of the accepted upstream conjugation theorem.

The initial register file h is arbitrary. WellLabelled, complete relabel
coverage, physical recipe execution, and exact phase-aware operator equality
are all retained. This is not a selected scalar-row, owner, or cost theorem. -/
theorem conjugation_of_children
    (T : Λ → M ≃ₗ[K] M) (blocks : Nat → M ≃ₗ[K] M)
    (lookup : Λ → Λ → Option (Child K M))
    (rec : Λ → Λ → M → M) (es : List (Event ι Λ K))
    (l : ι → Λ) (h : ι → M)
    (hcovered : ∀ r A B, Event.relabel r A B ∈ es →
      ∃ c, lookup A B = some c)
    (hphysical : ∀ r A B, Event.relabel r A B ∈ es →
      ∀ c, lookup A B = some c →
        ∀ v, rec A B v = Child.eval blocks c v)
    (hoperator : ∀ r A B, Event.relabel r A B ∈ es →
      ∀ c, lookup A B = some c →
        ∀ v, Child.eval blocks c v = T B ((T A).symm v))
    (hw : WellLabelled es l) :
    physRun rec es h =
      D T (labRun es l) (scalRun es (Dinv T l h)) := by
  exact LemmaG.Stream.conj' T rec es l h
    (recipesExact_of_children T blocks lookup rec es hcovered hphysical hoperator) hw

end Binding
end CurrentMain.DirectedChildRecipes

#print axioms CurrentMain.DirectedChildRecipes.Child.eval_rank_zero
#print axioms CurrentMain.DirectedChildRecipes.Child.eval_some
#print axioms CurrentMain.DirectedChildRecipes.recipesExact_of_children
#print axioms CurrentMain.DirectedChildRecipes.conjugation_of_children
