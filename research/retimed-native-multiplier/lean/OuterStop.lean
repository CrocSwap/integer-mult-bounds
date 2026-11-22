import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Algebra.Order.Floor.Ring
import Mathlib.Tactic

namespace RetimedOuter

private theorem le_two_rpow {t : ℝ} (ht : 0 ≤ t) : t ≤ (2 : ℝ) ^ t := by
  have hfloor : t < (⌊t⌋₊ : ℝ) + 1 := Nat.lt_floor_add_one t
  have hn : ⌊t⌋₊ + 1 ≤ 2 ^ ⌊t⌋₊ := ⌊t⌋₊.lt_two_pow_self
  have hc : (⌊t⌋₊ : ℝ) + 1 ≤ (2 : ℝ) ^ ⌊t⌋₊ := by exact_mod_cast hn
  have hp : (2 : ℝ) ^ (⌊t⌋₊ : ℝ) ≤ (2 : ℝ) ^ t :=
    Real.rpow_le_rpow_of_exponent_le (by norm_num) (Nat.floor_le ht)
  rw [Real.rpow_natCast] at hp
  exact le_trans hfloor.le (le_trans hc hp)

theorem log_absorption {s y g : ℝ} (hs : 512 ≤ s) (hy : s - 2 ≤ y) (hg : 0 < g) :
    (s + 1)^16 / (2 : ℝ)^(g*y) ≤ (17/g)^16 := by
  have hy0 : 0 ≤ y := by linarith
  have h0 : 0 ≤ g*y/16 := by positivity
  have hp := le_two_rpow h0
  have hprod : (s+1) ≤ (17/g) * (2 : ℝ)^(g*y/16) := by
    have hpre : s+1 ≤ (17/g) * (g*y/16) := by
      rw [show 17/g*(g*y/16) = 17*y/16 by field_simp]
      linarith
    exact hpre.trans (mul_le_mul_of_nonneg_left hp (by positivity))
  have hp16 := pow_le_pow_left₀ (by linarith : (0 : ℝ) ≤ s+1) hprod 16
  rw [mul_pow] at hp16
  have hchain : ((2 : ℝ)^(g*y/16))^16 = (2 : ℝ)^(g*y) := by
    rw [← Real.rpow_natCast, ← Real.rpow_mul (by norm_num : (0 : ℝ) ≤ 2)]
    norm_num
  rw [hchain] at hp16
  exact (div_le_iff₀ (by positivity)).2 hp16

set_option exponentiation.threshold 2000 in
theorem stop21_headroom : (17 * 10^21 : ℕ)^16 < 2^1182 := by norm_num

private theorem width_cube_step (k : ℕ) (hk : 4 ≤ k) : (k+1)^3 ≤ 2*k^3 := by
  obtain ⟨u, rfl⟩ := Nat.exists_eq_add_of_le hk
  ring_nf
  omega

set_option exponentiation.threshold 2000 in
theorem stopped_test_volume (e : ℕ) (he : 1024 ≤ e) :
    2^256 * e^3 ≤ 2^e := by
  induction e, he using Nat.le_induction with
  | base => norm_num
  | succ k hk ih =>
    calc
      2^256 * (k+1)^3 ≤ 2^256 * (2*k^3) :=
        Nat.mul_le_mul_left _ (width_cube_step _ (by omega))
      _ = 2 * (2^256*k^3) := by ring
      _ ≤ 2 * 2^k := Nat.mul_le_mul_left _ ih
      _ = 2^(k+1) := by rw [pow_succ]; omega

theorem stop21_physical_scan (e l : ℕ) (he : 1024 ≤ e)
    (width : l + 2 ≤ (3 * 10^21 + 2) * e) :
    2^32 * (l+2)^3 ≤ 2^e := by
  calc
    2^32 * (l+2)^3 ≤ 2^32 * ((3 * 10^21 + 2) * e)^3 :=
      Nat.mul_le_mul_left _ (Nat.pow_le_pow_left width 3)
    _ = (2^32 * (3 * 10^21 + 2)^3) * e^3 := by ring
    _ ≤ 2^256 * e^3 := Nat.mul_le_mul_right _ (by norm_num)
    _ ≤ 2^e := stopped_test_volume e he

theorem stop21_comparison_on_root (e : ℕ) (he : 1024 ≤ e) :
    2^32 * ((e+2).log2+3)^3 ≤ 2^e := by
  apply stop21_physical_scan e ((e+2).log2+1) he
  have h0 := Nat.log2_le_self (e+2)
  omega

theorem stop21_comparison_on_child (e M z h : ℕ) (he : 1024 ≤ e)
    (hM : M ≤ e) (hz : z < M*(e+1)) (parent_ran : h < z^(10^21)) :
    2^32 * ((h+2).log2+3)^3 ≤ 2^e := by
  have he' : e+1 ≤ 2^e := e.lt_two_pow_self
  have hm' : M ≤ 2^e := le_trans (le_trans hM (Nat.le_succ _)) he'
  have hz' : z ≤ 2^e * 2^e := hz.le.trans (Nat.mul_le_mul hm' he')
  have top : h < 2^((e+e)*10^21) := by
    have hh := Nat.pow_le_pow_left hz' (10^21)
    rw [← pow_add, ← pow_mul] at hh
    exact parent_ran.trans_le hh
  have hp : 0 < (2:ℕ)^((e+e)*10^21) := by positivity
  have cap : h+2 < 2^((e+e)*10^21 + 2) := by
    rw [pow_add]
    norm_num only [Nat.reducePow] at hp top ⊢
    omega
  have hw := (Nat.log2_lt (show h+2 ≠ 0 by omega)).2 cap
  apply stop21_physical_scan e ((h+2).log2+1) he
  omega

#print axioms log_absorption
#print axioms stop21_headroom
#print axioms stop21_comparison_on_root
#print axioms stop21_comparison_on_child
end RetimedOuter
