/- Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
   Characteristic-two kernel algebra for active-Pauli gauge choices.
   The Clifford/chart binding and finite-dimensional rank corollary are separate. -/
import RankGate

namespace ActivePhasePalette

open PhaseRankGate
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]

theorem square_when_even (u : V) (a : V →ₗ[K] K)
    (charTwo : ∀ c : K, c+c=0) (even : a u=0) (x : V) :
    update u a (update u a x)=x := by
  change (x+a x • u)+a (x+a x • u) • u=x
  simp only [map_add, map_smul, smul_eq_mul, even, mul_zero, add_zero]
  rw [add_assoc, ← add_smul, charTwo]
  simp

theorem projection_when_odd (u : V) (a : V →ₗ[K] K)
    (charTwo : ∀ c : K, c+c=0) (odd : a u=1) (x : V) :
    update u a (update u a x)=update u a x := by
  change (x+a x • u)+a (x+a x • u) • u=x+a x • u
  simp only [map_add, map_smul, smul_eq_mul, odd, mul_one, charTwo, zero_smul, add_zero]

theorem kernel_when_odd (u : V) (a : V →ₗ[K] K)
    (charTwo : ∀ c : K, c+c=0) (odd : a u=1) :
    LinearMap.ker (update u a)=Submodule.span K {u} := by
  ext x
  constructor
  · intro hx
    have h : x+a x • u=0 := by simpa [update] using hx
    have heq : x= -(a x • u) := eq_neg_of_add_eq_zero_left h
    apply Submodule.mem_span_singleton.mpr
    exact ⟨-a x, by rw [neg_smul, ← heq]⟩
  · intro hx
    rcases Submodule.mem_span_singleton.mp hx with ⟨c, rfl⟩
    change c • u+a (c • u) • u=0
    simp only [map_smul, smul_eq_mul, odd, mul_one]
    rw [← add_smul, charTwo]
    simp

theorem odd_direction_nonzero (u : V) (a : V →ₗ[K] K) (odd : a u=1) : u≠0 := by
  intro h
  subst u
  simp at odd

end ActivePhasePalette

#print axioms ActivePhasePalette.square_when_even
#print axioms ActivePhasePalette.projection_when_odd
#print axioms ActivePhasePalette.kernel_when_odd
#print axioms ActivePhasePalette.odd_direction_nonzero
