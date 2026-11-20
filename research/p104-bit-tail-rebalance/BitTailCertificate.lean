import Init.Data.Rat
import Lean.Elab.Tactic.Decide

/-!
The rational arithmetic in the finite BIT tensor certificate.
The three bounds are outward enclosures from the exact source moments.
-/

namespace P104BitTailRebalance

def paidMomentCap : Rat := 999999999998669 / 1000000000000000
def paidTailCap : Rat := 473009043448109 / 500000000000000
def targetTailCap : Rat := 94357873737351 / 100000000000000

def paidBudget : Rat :=
  1 / (1 + 416 * (1 - paidMomentCap)) + 2 * paidTailCap ^ (416 : Nat)

def discardedBudget : Rat := targetTailCap ^ (416 : Nat)

set_option maxRecDepth 8192 in
set_option maxHeartbeats 2000000 in
theorem verified_gap : paidBudget + discardedBudget < 1 - 333056567 / 10^18 := by
  decide +kernel

/-- Bounds on the two normalized charges suffice for strict separation. -/
theorem strict_separation (paid discarded : Rat)
    (hp : paid ≤ paidBudget) (hd : discarded ≤ discardedBudget) :
    paid + discarded < 1 := by
  have hsum : paid + discarded ≤ paidBudget + discardedBudget :=
    Rat.le_trans (Rat.add_le_add_right.mpr hp) (Rat.add_le_add_left.mpr hd)
  have hthreshold : ¬ (1 : Rat) ≤ 1 - 333056567 / 10^18 := by decide +kernel
  exact Rat.not_le.mp fun h =>
    hthreshold (Rat.le_trans (Rat.le_trans h hsum) (Rat.le_of_lt verified_gap))

theorem paid_cutoff_changes : (10 : Nat)^416 < 14^416 ∧ (14 : Nat)^416 < 15^416 := by
  decide +kernel

end P104BitTailRebalance

#print axioms P104BitTailRebalance.strict_separation
#print axioms P104BitTailRebalance.paid_cutoff_changes
