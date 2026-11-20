import Std

/-! Exact arithmetic for the two suppliers at the fixed #7830 mixed price.
The six BIT caps are the outward entries of BIT.json, separation.upper_caps.
Their derivation from each rank histogram is a separate numerical proof. -/
namespace MixedFunding

def alpha : Rat := 249999999999998000563 / 250000000000000000000
def lowFirst : Rat := 720828660325258853331 / 2000000000000000000000
def lowOther : Rat := 9460180868969874332523 / 10000000000000000000000
def highFirst : Rat := 5969937509690282459981 / 10000000000000000000000
def highOther : Rat := 9247497622443579677377 / 10000000000000000000000
def dropped : Rat := 1178602023822729540311 / 1250000000000000000000

def paidAndDropped : Rat :=
  1 / (1 + 480 * (1-alpha)) +
  2 * lowFirst * lowOther ^ (479 : Nat) +
  2 * highFirst * highOther ^ (479 : Nat) + dropped ^ (480 : Nat)

def complexPaid : Rat :=
  1 / (1 + 1920 / 10^27) + 4 * (31 / 32) ^ (1920 : Nat)

set_option maxHeartbeats 4000000
set_option maxRecDepth 16384

theorem bit_moment : paidAndDropped < 1 - 12309863319385 / 10^25 := by decide +kernel
theorem complex_moment : complexPaid < 1 := by decide +kernel

def rawBit : Rat := 3879928046148 / 10^15
def trialC : Rat := 387992803563 / 10^14
def finalClaim : Rat := 387992803556 / 10^14
def uniformLoss : Rat := 1 / 400000000000
def coverLoss : Rat := 1 / 125000000000
def covered : Rat := rawBit - uniformLoss - coverLoss
def seed : Rat := 12039 / 3125000
def stages : List Rat :=
  [seed, 3879818243504 / 10^15, 3879927596478 / 10^15, 3879928033890 / 10^15,
   3879928035639 / 10^15, 3879928035646 / 10^15]
def validStages (old : Rat) : List Rat → Prop
  | [] => True
  | c :: rest => old < c ∧ c < (249 * covered + old) / 250 ∧ c < 1 / 250 ∧ validStages c rest
instance stagesDec (old : Rat) : (xs : List Rat) → Decidable (validStages old xs)
  | [] => isTrue True.intro
  | c :: xs =>
    letI := stagesDec c xs
    inferInstanceAs (Decidable (_ ∧ _ ∧ _ ∧ validStages c xs))

theorem cold_through_six_stages : validStages 0 stages := by decide +kernel
theorem supplier_room :
    trialC = finalClaim + 7 / 10^14 ∧
    3879928035646 / (10^15 : Rat) - trialC = 1 / 62500000000000 ∧
    rawBit < 97 / 25000 ∧ trialC < 97 / 25000 ∧ 97 / (25000 : Rat) < 1 / 250 :=
  by decide +kernel

/-- Raising both positive sides to 625 verifies bounds for the two real powers,
because 480 * (97/25000) = 1164/625 and 1920 * (97/25000) = 4656/625. -/
theorem ambient_upper :
    (134 : Nat)^1164 < 9160^625 ∧ (153 : Nat)^4656 < 18900000000000000^625 ∧
    (9160 : Nat) < 2^64 ∧ (18900000000000000 : Nat) < 2^2381 := by decide +kernel

theorem eta_guards :
    (9160 * 250 : Nat)*13^64 < 249*15^64 ∧
    (18900000000000000 * 250 : Nat)*63^2381 < 249*64^2381 := by decide +kernel

theorem logarithm_guards :
    (11 : Nat)^15 < 16^13 ∧ 4*11^(480*15) ≤ 134^(480*13) ∧
    (11 : Nat)^64 < 12^63 ∧ 2*11^(1920*64) ≤ 153^(1920*63) := by decide +kernel

theorem fixed_carriers :
    (1285200000000000 + 1 : Nat)^64 < 2^3213 ∧
    (15171300000000000000 + 1 : Nat)^2381 < 2^151713 ∧
    1285200000000000 = (400000000000 : Nat)*3213 ∧
    15171300000000000000 = (10^14 : Nat)*151713 := by decide +kernel

end MixedFunding

#print axioms MixedFunding.bit_moment
#print axioms MixedFunding.complex_moment
#print axioms MixedFunding.cold_through_six_stages
#print axioms MixedFunding.supplier_room
#print axioms MixedFunding.ambient_upper
#print axioms MixedFunding.eta_guards
#print axioms MixedFunding.logarithm_guards
#print axioms MixedFunding.fixed_carriers
