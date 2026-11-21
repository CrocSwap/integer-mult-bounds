import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring

noncomputable section
set_option maxRecDepth 8192
namespace NativeStock
open Finset
open scoped BigOperators

def H : ℝ := 240000000000000
noncomputable def N : ℝ := (2 : ℝ) ^ H
def a : ℝ := 97 / 25000
def seed : ℕ := (25000 * (2 * 240000000000000 + 12) + 24902) / 24903
def entry (j : ℕ) : ℕ := seed + j * (12 + 2 * 240000000000000)
noncomputable def R : ℕ → ℝ
  | 0 => 1
  | j + 1 => (2 : ℝ) ^ (entry j : ℝ) + 1

private theorem Npos : 1 ≤ N := Real.one_le_rpow (by norm_num) (by norm_num [H])
private theorem Rpos (j : ℕ) : 1 ≤ R j := by
  cases j with
  | zero => rfl
  | succ j => simp only [R]; have := Real.rpow_pos_of_pos (by norm_num : (0:ℝ)<2) (entry j : ℝ); linarith

private theorem square_eq : N ^ 2 = (2:ℝ) ^ (2*H) := by
  unfold N
  rw [← Real.rpow_natCast _ 2, ← Real.rpow_mul (by norm_num : (0:ℝ)≤2)]
  congr 1
  ring

/-- The two terms at each entrance pay for the atom floor and the growing atom. -/
theorem entry_bill (j : ℕ) :
    2048 * N^2 * max (R j) ((2:ℝ)^(a * entry j)) ≤ (2:ℝ)^(entry j : ℝ) := by
  have cp : (2048:ℝ) = (2:ℝ)^(11:ℝ) := by norm_num
  have cp' : 2048 * N^2 = (2:ℝ)^(11 + 2*H) := by
    rw [cp,square_eq,←Real.rpow_add (by norm_num : (0:ℝ)<2)]
  have hseed : 11+2*H ≤ (1-a)*(seed:ℝ) := by norm_num [H,a,seed]
  have hs : (seed:ℝ) ≤ entry j := by
    exact_mod_cast Nat.le_add_right seed (j * (12 + 2 * 240000000000000))
  have hroom : 11 + 2*H + a*entry j ≤ entry j := by
    have := mul_le_mul_of_nonneg_left hs (by norm_num [a] : 0 ≤ 1-a)
    linarith
  rw [mul_max_of_nonneg _ _ (by positivity), max_le_iff]
  constructor
  · cases j with
    | zero =>
      rw [R, mul_one, cp']
      apply Real.rpow_le_rpow_of_exponent_le (by norm_num)
      norm_num [entry,seed,H]
    | succ j =>
      have he : (entry (j+1):ℝ) = (entry j:ℝ) + 12 + 2*H := by
        simp [entry,H]
        ring
      have he₀ : (1:ℝ) ≤ 2^(entry j:ℝ) := Real.one_le_rpow (by norm_num) (Nat.cast_nonneg _)
      calc
        _ ≤ 2048*N^2 * (2^(entry j:ℝ) * 2) := by
          apply mul_le_mul_of_nonneg_left _ (by positivity)
          dsimp [R]
          linarith
        _ = 2^(entry (j+1):ℝ) := by
          rw [cp', he, ←mul_assoc, ←Real.rpow_add (by norm_num : (0:ℝ)<2),
              show (entry j:ℝ)+12+2*H=(11+2*H+(entry j:ℝ))+1 by ring,
              Real.rpow_add (by norm_num : (0:ℝ)<2) _ 1,Real.rpow_one]
  · rw [cp',←Real.rpow_add (by norm_num : (0:ℝ)<2)]
    exact Real.rpow_le_rpow_of_exponent_le (by norm_num) hroom

private theorem depth_growth {z : ℝ} (hz : 0≤z) :
    1 + z/4 ≤ (2:ℝ)^((1-a)*z) := by
  have hl := Real.one_sub_inv_le_log_of_pos (by norm_num : (0:ℝ)<2)
  have hl' : (1:ℝ)/2 ≤ Real.log 2 := by linarith
  have le := Real.add_one_le_exp (Real.log 2*((1-a)*z))
  rw [Real.rpow_def_of_pos (by norm_num : (0:ℝ)<2)]
  unfold a at *
  nlinarith [mul_le_mul_of_nonneg_right hl' hz]

/-- Six unrounded debts fit strictly inside one quarter of the input width
after the single final rounding. The debts include older high coordinates. -/
theorem live_stock (j : Fin 6) {t k : ℝ} (row depth : Fin 6 → ℝ)
    (entered : (entry j:ℝ) ≤ t)
    (shape : ∀ i, 0 ≤ row i ∧ row i ≤ 4*N^2*max (R j) ((2:ℝ)^(a*t)) ∧
                  0 ≤ depth i ∧ depth i ≤ 3+t/H)
    (borrow : k ≤ 1+∑ i, depth i*row i) : k < (2:ℝ)^t/4 := by
  let cut : ℝ := entry j
  let base := max (R j) ((2:ℝ)^(a*cut))
  let A := (2:ℝ)^(a*(t-cut))
  let D := (2:ℝ)^((1-a)*(t-cut))
  have ht : cut≤t := entered
  have hD : 1+(t-cut)/4 ≤ D := depth_growth (by linarith)
  have hA : 1≤A := Real.one_le_rpow (by norm_num) (mul_nonneg (by norm_num [a]) (sub_nonneg.mpr ht))
  have hD' : 1≤D := by linarith
  have hb : 1≤base := (Rpos j).trans (le_max_left _ _)
  have hcut : cut≤13*H := by
    have hj : j.val ≤ 5 := Nat.le_of_lt_succ j.isLt
    have hn : entry j ≤ entry 5 := Nat.add_le_add_left (Nat.mul_le_mul_right _ hj) _
    have hv : (entry 5:ℝ) ≤ 13*H := by norm_num [entry,seed,H]
    exact (Nat.cast_le.mpr hn).trans hv
  have hd : 3+t/H ≤ 16*D := by
    have h₁ : cut/H≤13 := (div_le_iff₀ (by norm_num [H])).mpr hcut
    have h₂ : (t-cut)/H≤(t-cut)/4 := div_le_div_of_nonneg_left (by linarith) (by norm_num) (by norm_num [H])
    have h₃ : t/H=cut/H+(t-cut)/H := by ring
    linarith
  have hs : max (R j) ((2:ℝ)^(a*t)) ≤ base*A := by
    apply max_le
    · calc
        R j ≤ base := le_max_left _ _
        _ ≤ base*A := le_mul_of_one_le_right (by linarith) hA
    · calc
        (2:ℝ)^(a*t) = (2:ℝ)^(a*cut)*A := by
          rw [←Real.rpow_add (by norm_num : (0:ℝ)<2)]
          congr 1
          ring
        _ ≤ base*A := mul_le_mul_of_nonneg_right (le_max_right _ _) (by linarith)
  have hsum : (∑ i, depth i*row i) ≤ 6*(16*D*(4*N^2*(base*A))) := by
    calc
      _ ≤ ∑ _ : Fin 6, 16*D*(4*N^2*(base*A)) := by
        apply Finset.sum_le_sum
        intro i _
        obtain ⟨h₁,h₂,_,h₃⟩ := shape i
        exact mul_le_mul (h₃.trans hd)
          (h₂.trans (mul_le_mul_of_nonneg_left hs (by positivity))) h₁ (by linarith)
      _ = _ := by simp
  have eq : (2:ℝ)^cut * (A*D) = 2^t := by
    dsimp [A,D]
    rw [←Real.rpow_add (by norm_num : (0:ℝ)<2),←Real.rpow_add (by norm_num : (0:ℝ)<2)]
    congr 1
    ring
  have h := mul_le_mul_of_nonneg_right (entry_bill j) (mul_nonneg (by linarith : 0≤A) (by linarith : 0≤D))
  change 2048*N^2*base*(A*D) ≤ 2^cut*(A*D) at h
  rw [eq] at h
  have one : 1 ≤ N^2*base*(A*D) :=
    one_le_mul_of_one_le_of_one_le (one_le_mul_of_one_le_of_one_le (one_le_pow₀ Npos) hb)
      (one_le_mul_of_one_le_of_one_le hA hD')
  nlinarith

/-- Iterating the old atom-width ceiling forces the full five descents. -/
theorem old_five (x : Fin 6 → ℝ)
    (down : ∀ i : Fin 5, 250 * (x i.castSucc - 1) ≤ x i.succ) :
    250^5 * (x 0 - 250/249) ≤ x 5 := by
  have h0 := down 0
  have h1 := down 1
  have h2 := down 2
  have h3 := down 3
  have h4 := down 4
  change 250*(x 0-1) ≤ x 1 at h0
  change 250*(x 1-1) ≤ x 2 at h1
  change 250*(x 2-1) ≤ x 3 at h2
  change 250*(x 3-1) ≤ x 4 at h3
  change 250*(x 4-1) ≤ x 5 at h4
  linarith

#print axioms entry_bill
#print axioms live_stock
#print axioms old_five
end NativeStock
