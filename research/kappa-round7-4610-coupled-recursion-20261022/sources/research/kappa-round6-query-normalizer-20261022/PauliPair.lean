/- Fixed in-place pair adapter for the actual global Pauli involution.
Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
This is an algebra theorem, not a tape-layout or kappa theorem. -/
import Mathlib.Data.Complex.Basic
import Mathlib.Tactic.Ring

namespace PauliPair
noncomputable section

def phase (eta x y : ℂ) : ℂ × ℂ :=
  ((x+y+eta*(x-y))/2, (x+y-eta*(x-y))/2)

/-- Four ADDs, four signed-power-of-two SCALEs, one exact phase. -/
def pairProgram (eta x y : ℂ) : ℂ × ℂ :=
  let a := x+y
  let b := -2*y+a
  let b := eta*b
  let a := a+b
  let b := -2*b+a
  (a/2,b/2)

theorem macro_eq_phase (eta x y : ℂ) : pairProgram eta x y = phase eta x y := by
  apply Prod.ext <;> simp only [pairProgram,phase] <;> ring

theorem composition (eta theta x y : ℂ) :
    phase eta (phase theta x y).1 (phase theta x y).2 = phase (eta*theta) x y := by
  apply Prod.ext <;> simp only [phase] <;> ring

theorem square_is_pauli_swap (x y : ℂ) :
    phase Complex.I (phase Complex.I x y).1 (phase Complex.I x y).2 = (y,x) := by
  rw [composition,Complex.I_mul_I]
  apply Prod.ext <;> simp only [phase] <;> ring

theorem phase_inverse (x y : ℂ) :
    phase (-Complex.I) (phase Complex.I x y).1 (phase Complex.I x y).2 = (x,y) := by
  rw [composition]
  simp only [neg_mul,Complex.I_mul_I,neg_neg]
  apply Prod.ext <;> simp only [phase] <;> ring

#print axioms macro_eq_phase
#print axioms composition
#print axioms square_is_pauli_swap
#print axioms phase_inverse

end
end PauliPair
