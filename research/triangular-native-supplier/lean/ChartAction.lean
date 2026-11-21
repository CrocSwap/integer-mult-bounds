import Mathlib.Algebra.Group.Subgroup.Basic

namespace TriangularChart

variable {G : Type*} [Group G]

def same (U : Subgroup G) : Setoid G where
  r a b := ∃ l : U, a = (l : G) * b
  iseqv := {
    refl := fun a => ⟨1, by simp⟩
    symm := by
      rintro a b ⟨l, rfl⟩
      exact ⟨l⁻¹, by simp⟩
    trans := by
      rintro a b c ⟨l, rfl⟩ ⟨m, rfl⟩
      exact ⟨l*m, by simp [mul_assoc]⟩ }

abbrev Charts (U : Subgroup G) := Quotient (same U)

def mark (U : Subgroup G) (g : G) : Charts U := Quotient.mk _ g

def move (U : Subgroup G) (S : G) : Charts U → Charts U :=
  Quotient.lift (fun g => mark U (g*S)) (by
    rintro a b ⟨l, rfl⟩
    exact Quotient.sound ⟨l, mul_assoc _ _ _⟩)

theorem move_mul (U : Subgroup G) (q : Charts U) (a b : G) :
    move U b (move U a q) = move U (a*b) q := by
  induction q using Quotient.inductionOn with
  | _ g => exact congrArg (mark U) (mul_assoc g a b)

theorem move_one (U : Subgroup G) (q : Charts U) : move U 1 q = q := by
  induction q using Quotient.inductionOn with
  | _ g => exact congrArg (mark U) (mul_one g)

def residual (U : Subgroup G) (rep : Charts U → G) (q : Charts U) (s : G) : G :=
  rep q * s * (rep (move U s q))⁻¹

theorem residual_mem (U : Subgroup G) (rep : Charts U → G)
    (marked : ∀ q, mark U (rep q) = q) (q : Charts U) (s : G) :
    residual U rep q s ∈ U := by
  have h : mark U (rep q * s) = mark U (rep (move U s q)) := by
    change move U s (mark U (rep q)) = _
    rw [marked, marked]
  obtain ⟨l, eq⟩ := Quotient.exact h
  unfold residual
  rw [eq]
  simp [mul_assoc]

theorem cocycle (U : Subgroup G) (rep : Charts U → G) (q : Charts U) (a b : G) :
    residual U rep q (a*b) = residual U rep q a * residual U rep (move U a q) b := by
  simp [residual, move_mul, mul_assoc]

theorem returned (U : Subgroup G) (rep : Charts U → G) (q : Charts U) (s : G) :
    residual U rep q s * residual U rep (move U s q) s⁻¹ = 1 := by
  rw [← cocycle]
  simp [residual, move_one]

#print axioms move_mul
#print axioms residual_mem
#print axioms cocycle
#print axioms returned

end TriangularChart
