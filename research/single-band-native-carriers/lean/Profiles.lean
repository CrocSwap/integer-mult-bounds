import Mathlib.Tactic.NormNum

/-! Exact funding and activation at the installed ranks. -/
namespace Profiles

def funded (raw eta : ℚ) (debit : ℕ) (previous : ℚ) : List (ℕ × ℕ) → Bool
  | [] => true
  | (height, ticks) :: rest =>
    let b : ℚ := ticks / (10 : ℚ)^18
    let c := raw - (debit : ℚ) / height
    decide (0 < height ∧ previous < b ∧ b < eta ∧ b < (249*c+previous)/250) &&
      funded raw eta debit b rest

def compact : List (ℕ × ℕ) :=
  [(260000,3819896757624698),(1600000,3879928035646000)]

def highRate : List (ℕ × ℕ) :=
  [(25000000,3873797863410106),(160000000,3889931739863747),
   (1000000000,3890095626369561),(6000000000,3890112051915585),
   (36000000000,3890114745951102),(224000000000,3890115197377000)]

def priceMatch : List (ℕ × ℕ) :=
  [(175000000,3874446686267249),(1120000000,3890035713726604),
   (7000000000,3890112262836441),(42000000000,3890114821890024),
   (252000000000,3890115207602428),(1568000000000,3890115271496000)]

theorem ordinaryFunding :
    funded (2039/524288) (97/25000) 14 0 compact = true ∧
    funded (17108907955/4398046511104) (39/10000) 19 0 highRate = true ∧
    funded (17108907955/4398046511104) (39/10000) 19 0 priceMatch = true := by
  norm_num [funded, compact, highRate, priceMatch]

def positive (m : ℕ) (k b : ℚ) : Prop :=
  k + 4/(10:ℚ)^14 < b ∧ k + 5/(10:ℚ)^14 < 2043/524288 - 10/(m:ℚ)

theorem allConsumers :
    positive 610000 (387992803556/(10:ℚ)^14) (3879928035646/(10:ℚ)^15) ∧
    positive 1600000 (389011519729/(10:ℚ)^14) (3890115197377/(10:ℚ)^15) ∧
    positive 1600000 (389011527141/(10:ℚ)^14) (3890115271496/(10:ℚ)^15) := by
  norm_num [positive]

def entranceCuts (old : ℕ) : List (ℕ × ℕ) → ℕ
  | [] => old
  | (h,_) :: rest => entranceCuts
      (max ((250*(h+64)+248)/249) (if old=0 then 0 else h+old+64)) rest

theorem trueWidthCuts :
    entranceCuts 0 compact = 1861173 ∧ entranceCuts 0 highRate = 267185100786 ∧
    entranceCuts 0 priceMatch = 1870295703196 := by decide

#print axioms ordinaryFunding
#print axioms allConsumers
#print axioms trueWidthCuts

end Profiles
