/- Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
   Exact phase-sector algebra, not native frame or whole-job admission. -/
import Mathlib.Data.Complex.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum

namespace GroupedPhase

def phase (negative : Bool) : ℂ := if negative then Complex.I else 1
def interaction (a b : Bool) : ℂ := if a && b then -1 else 1

theorem split_requires_interaction (a b : Bool) :
    phase a * phase b = phase (a != b) * interaction a b := by
  cases a <;> cases b <;> norm_num [phase, interaction]

theorem two_negative_sectors_distinguish_global :
    phase true * phase true ≠ phase (true != true) := by
  norm_num [phase]

noncomputable def realify (z : ℂ) : ℂ := (1+Complex.I)/2*z + (1-Complex.I)/2*z^3

theorem realify_polynomial (z : ℂ) :
    realify z ^ 2 - 1 = (z^4-1)*(1-Complex.I*z^2/2) := by
  dsimp [realify]
  ring_nf
  simp [Complex.I_sq]
  ring

theorem realify_fourth_root (z : ℂ) (hz : z^4=1) :
    realify z ^ 2 = 1 := by
  apply sub_eq_zero.mp
  simpa only [hz, sub_self, zero_mul] using realify_polynomial z

end GroupedPhase

#print axioms GroupedPhase.split_requires_interaction
#print axioms GroupedPhase.two_negative_sectors_distinguish_global
#print axioms GroupedPhase.realify_polynomial
#print axioms GroupedPhase.realify_fourth_root
