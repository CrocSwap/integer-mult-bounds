/- Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
   Scoped linear-algebra gate for a word of rank-one phase perturbations.
   The Clifford-to-symplectic interpretation and tape admission are separate. -/
import Mathlib.LinearAlgebra.Span.Basic
import Mathlib.Tactic.Abel

namespace PhaseRankGate

variable {K V D : Type*} [Field K] [AddCommGroup V] [Module K V]
  [AddCommGroup D] [Module K D]

def update (u : V) (a : V →ₗ[K] K) : V →ₗ[K] V :=
  LinearMap.id + a.smulRight u

def word : List (V × (V →ₗ[K] K)) → V →ₗ[K] V
  | [] => LinearMap.id
  | (u, a) :: rest => (update u a).comp (word rest)

def defects : List (V × (V →ₗ[K] K)) → Submodule K V
  | [] => ⊥
  | (u, _) :: rest => Submodule.span K {u} ⊔ defects rest

theorem word_defect_mem (steps : List (V × (V →ₗ[K] K))) (x : V) :
    word steps x - x ∈ defects steps := by
  induction steps with
  | nil => simp [word, defects]
  | cons head rest ih =>
    rcases head with ⟨u, a⟩
    have hu : a (word rest x) • u ∈ defects ((u, a) :: rest) := by
      apply (show Submodule.span K {u} ≤ defects ((u, a) :: rest) from le_sup_left)
      exact Submodule.smul_mem _ _ (Submodule.subset_span (by simp))
    have hr : word rest x - x ∈ defects ((u, a) :: rest) :=
      (show defects rest ≤ defects ((u, a) :: rest) from le_sup_right) ih
    convert (defects ((u, a) :: rest)).add_mem hu hr using 1 <;>
      simp [word, update, LinearMap.add_apply, LinearMap.comp_apply] <;> abel

theorem range_le_of_defect (f g : D →ₗ[K] V) (S : Submodule K V)
    (h : ∀ x, f x - g x ∈ S) :
    LinearMap.range f ≤ LinearMap.range g ⊔ S := by
  rintro y ⟨x, rfl⟩
  have hg : g x ∈ LinearMap.range g ⊔ S :=
    (show LinearMap.range g ≤ LinearMap.range g ⊔ S from le_sup_left) ⟨x, rfl⟩
  have hs : f x - g x ∈ LinearMap.range g ⊔ S :=
    (show S ≤ LinearMap.range g ⊔ S from le_sup_right) (h x)
  convert (LinearMap.range g ⊔ S).add_mem hg hs using 1 <;> abel

theorem fixed_word_range_bound (steps : List (V × (V →ₗ[K] K)))
    (f : D →ₗ[K] V) :
    LinearMap.range ((word steps).comp f) ≤ LinearMap.range f ⊔ defects steps :=
  range_le_of_defect ((word steps).comp f) f
    (defects steps) (fun x => word_defect_mem steps (f x))

theorem common_encoding_add (E : V →ₗ[K] V) (x y : V) (c : K) :
    E (x + c • y) = E x + c • E y := by simp

theorem gauge_telescope {G : Type*} [Group G] (e0 e1 e2 a b : G) :
    (e2*b*e1⁻¹)*(e1*a*e0⁻¹) = e2*(b*a)*e0⁻¹ := by
  simp [mul_assoc]

end PhaseRankGate

#print axioms PhaseRankGate.word_defect_mem
#print axioms PhaseRankGate.range_le_of_defect
#print axioms PhaseRankGate.fixed_word_range_bound
#print axioms PhaseRankGate.common_encoding_add
#print axioms PhaseRankGate.gauge_telescope
