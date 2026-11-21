import Mathlib.Data.Nat.Basic
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring

namespace UniformSpace

set_option exponentiation.threshold 1024

def firstS : ℕ := 355763540965265

def liveCost (s : ℕ) : ℕ := 12 * (128 * ((s+130) * (s+1)^8) + 64)

theorem slope {s levels head : ℕ} (hs : firstS ≤ s)
    (hl : 3300000000 * levels ≤ 60 * 3300000000 + 7 * s) (hh : 64 * head ≤ s) :
    8 * ((2 * levels + 4) * 262144 + 48 + 2 * head) < s := by
  unfold firstS at hs
  omega

theorem stripe_margin {s b : ℕ} (hs : firstS ≤ s) (hb : 8 * b < s) :
    1024 + b < s / 2 - 2 := by
  unfold firstS at hs
  omega

theorem consecutive_ratio (s : ℕ) (hs : 32 ≤ s) :
    (s+131)*(s+2)^8 ≤ 2*((s+130)*(s+1)^8) := by
  have h₁ : 32*(s+131) ≤ 33*(s+130) := by omega
  have h₂ : 32*(s+2) ≤ 33*(s+1) := by omega
  have h : 32^9*((s+131)*(s+2)^8) ≤ 33^9*((s+130)*(s+1)^8) := by
    calc
      _ = (32*(s+131))*(32*(s+2))^8 := by ring
      _ ≤ (33*(s+130))*(33*(s+1))^8 :=
        Nat.mul_le_mul h₁ (Nat.pow_le_pow_left h₂ 8)
      _ = _ := by ring
  norm_num at h
  omega

theorem control_step (s : ℕ) (hs : 32 ≤ s) : liveCost (s+1) ≤ 2*liveCost s := by
  have h := consecutive_ratio s hs
  change 12*(128*((s+131)*(s+2)^8)+64) ≤ 2*(12*(128*((s+130)*(s+1)^8)+64))
  omega

theorem control_base : liveCost firstS < 2^512 := by
  norm_num [liveCost, firstS]

theorem lift_base (start : ℕ) (within : liveCost start < 2^512) (h : 512 ≤ start-2) :
    liveCost start < 2^(start-2) :=
  lt_of_lt_of_le within (@Nat.pow_le_pow_right 2 (by decide) 512 (start-2) h)

theorem inductive_tail (start : ℕ) (hs' : 32 ≤ start) (hb : liveCost start < 2^(start-2))
    (s : ℕ) (hs : start ≤ s) : liveCost s < 2^(s-2) := by
  induction s, hs using Nat.le_induction with
  | base => exact hb
  | succ s hs ih =>
    have hs'' : 32 ≤ s := le_trans hs' hs
    have h := control_step s hs''
    rw [show (s+1)-2=(s-2)+1 by omega, pow_succ]
    omega

theorem private_tail (s : ℕ) (hs : firstS ≤ s) : liveCost s < 2^(s-2) :=
  inductive_tail firstS (by norm_num [firstS])
    (lift_base firstS control_base (by norm_num [firstS])) s hs

#print axioms slope
#print axioms stripe_margin
#print axioms consecutive_ratio
#print axioms control_step
#print axioms control_base
#print axioms private_tail

end UniformSpace
