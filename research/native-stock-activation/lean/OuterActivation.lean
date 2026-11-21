import Lean.Elab.Tactic.Omega

namespace OuterActivation

/-- PERIODIC.md sends a ticket to a physical slot. -/
def ticket (x z : Nat) : Nat := if z < 5 * x then z / 5 else z - 4 * x

/-- Three real tickets in one row cannot be three consecutive physical slots. -/
theorem requiredGap (x j q : Nat) (hq : 4 ≤ q) (cut : x = 0 ∨ 8 ≤ q) :
    ticket x j + 2 < ticket x (j + 2 * q) := by
  rcases cut with h | h
  · subst x
    simp [ticket]
    omega
  · unfold ticket
    split <;> split <;> omega

/-- All controls and the real row field fit on one side after removing spectator bits. -/
theorem fitsExterior (L stripe left body rows control suffix : Nat)
    (stripeBound : 16 * stripe ≤ L)
    (bodyBound : 64 * body ≤ L) (rowBound : 16 * rows ≤ L)
    (controlBound : 64 * (3 * control) ≤ L) (suffixBound : 16 * suffix ≤ L) :
    body + rows + 3 * control + suffix ≤ max left (L - stripe - left - body) := by
  rcases Nat.le_total left (L - stripe - left - body) with h | h
  · rw [Nat.max_eq_right h]
    omega
  · rw [Nat.max_eq_left h]
    omega

set_option exponentiation.threshold 1024 in
/-- The retained repeated port has a three-slot first raw head, even at one column. -/
theorem poweredRootWitness : 17^264 ≤ (129:Nat)^264 ∧ 3 ≤ (129:Nat)^263 := by
  decide

/-- The entire real CRT control field has at least 1/101 of the address. -/
theorem crtField (L G : Nat) (positive : 0 < G) (room : 10100 * G ≤ L) :
    L ≤ 101 * ((L / (100 * G)) * G) := by
  have rest := Nat.mod_lt L (by omega : 0 < 100 * G)
  have exactSum := Nat.div_add_mod L (100 * G)
  have regroup : 100 * G * (L / (100 * G)) =
      100 * ((L / (100 * G)) * G) := by
    simp [Nat.mul_comm, Nat.mul_left_comm, Nat.mul_assoc]
  rw [regroup] at exactSum
  omega

/-- A binary-to-ternary exchange inside the true CRT has adequate width. -/
theorem completeEntrance (p L H e E : Nat) (positive : 0 < E) (start : 4096 * E ≤ p)
    (address : p ≤ 12 * L) (field : L ≤ 101 * H) (trits : H ≤ 2 * e) :
    E < e := by omega

theorem chosenBinaryConstants :
    (25000 * (2 * 240000000000000 + 12) + 24902) / 24903 = 481869654258536 ∧
    481869654258536 + 5 * (2 * 240000000000000 + 12) = 2881869654258596 := by
  decide

#print axioms requiredGap
#print axioms fitsExterior
#print axioms poweredRootWitness
#print axioms crtField
#print axioms completeEntrance
#print axioms chosenBinaryConstants

end OuterActivation
