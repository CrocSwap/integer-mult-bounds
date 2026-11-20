import Init.Data.Rat
import Lean.Elab.Tactic.Decide

/-!
The rational arithmetic in the finite BIT tensor certificate.
The three bounds are outward enclosures from the exact source moments.
-/

namespace P104Grade14

def paidMomentCap : Rat := 499999999999967 / 500000000000000
def paidTailCap : Rat := 175703845856227 / 200000000000000
def targetTailCap : Rat := 29486835542931 / 31250000000000

def paidBudget : Rat :=
  1 / (1 + 832 * (1 - paidMomentCap)) + 2 * paidTailCap ^ (832 : Nat)

def discardedBudget : Rat := targetTailCap ^ (832 : Nat)

set_option maxRecDepth 8192 in
set_option maxHeartbeats 2000000 in
theorem verified_gap : paidBudget + discardedBudget < 1 - 54911999 / 10^18 := by
  decide +kernel

/-- Bounds on the two normalized charges suffice for strict separation. -/
theorem strict_separation (paid discarded : Rat)
    (hp : paid ≤ paidBudget) (hd : discarded ≤ discardedBudget) :
    paid + discarded < 1 := by
  have hsum : paid + discarded ≤ paidBudget + discardedBudget :=
    Rat.le_trans (Rat.add_le_add_right.mpr hp) (Rat.add_le_add_left.mpr hd)
  have hthreshold : ¬ (1 : Rat) ≤ 1 - 54911999 / 10^18 := by decide +kernel
  exact Rat.not_le.mp fun h =>
    hthreshold (Rat.le_trans (Rat.le_trans h hsum) (Rat.le_of_lt verified_gap))

theorem paid_cutoff_changes : (10 : Nat)^832 < 14^832 ∧ (14 : Nat)^832 < 16^832 := by
  decide +kernel

end P104Grade14

#print axioms P104Grade14.strict_separation
#print axioms P104Grade14.paid_cutoff_changes
