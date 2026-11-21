import Invoice

namespace CarrierStock
open Finset
open scoped BigOperators

/-- Doubling to a positive real power dominates the specified linear change
of depth after the first funded width. -/
private theorem extra_growth {z : ℝ} (hz : 0≤z) :
    1+z/4 ≤ (2:ℝ)^((249/250:ℝ)*z) := by
  have hl := Real.one_sub_inv_le_log_of_pos (by norm_num : (0:ℝ)<2)
  have hl' : (1:ℝ)/2 ≤ Real.log 2 := by linarith
  have le := Real.add_one_le_exp (Real.log 2*((249/250)*z))
  rw [Real.rpow_def_of_pos (by norm_num : (0:ℝ)<2)]
  nlinarith [mul_le_mul_of_nonneg_right hl' hz]

/-- Six complete low/high reserves fit strictly below one half of the
ordinary width. All logarithms inside the stage debts use radix three. -/
theorem six_reserves {u k N H cut : ℝ} (batch width depth : Fin 6→ℝ)
    (hH : 4≤H) (hN : 1≤N) (hc : 0≤cut) (hT : cut≤3*H) (hu : cut≤u)
    (cost_at_cut : 4096*N^2 ≤ (2:ℝ)^((249/250:ℝ)*cut))
    (shape : ∀ j, 0≤batch j ∧ batch j≤N^2 ∧ 0≤width j ∧
      width j≤2*(2:ℝ)^(u/250) ∧ 0≤depth j ∧ depth j≤3+u/H)
    (debt : k≤1+∑ j, depth j*(batch j+N^2*width j)) :
    k<(2:ℝ)^u/2 := by
  let x := (2:ℝ)^(u/250)
  let y := (2:ℝ)^((249/250:ℝ)*(u-cut))
  have hx : 1≤x := Real.one_le_rpow (by norm_num) (by linarith)
  have hxpos : 0<x := by linarith
  have hy : 1+(u-cut)/4 ≤ y := extra_growth (by linarith)
  have hy₀ : 1≤y := by linarith
  have hN' : 1 ≤ N^2 := one_le_pow₀ hN
  have hscale : 3+u/H ≤ 6*y := by
    have hu₁ : u/H=cut/H+(u-cut)/H := by ring
    have hcH : cut/H ≤ 3 := (div_le_iff₀ (by linarith)).mpr (by linarith)
    have hdH : (u-cut)/H ≤ (u-cut)/4 := div_le_div_of_nonneg_left (by linarith) (by norm_num) hH
    linarith
  have hbill : (∑ j, depth j*(batch j+N^2*width j)) ≤ 6*((6*y)*(3*N^2*x)) := by
    calc
      _ ≤ ∑ _j : Fin 6, (6*y)*(3*N^2*x) := by
        apply Finset.sum_le_sum
        intro j _
        obtain ⟨b₀,hb,w₀,hw,d₀,hd⟩ := shape j
        have c := mul_le_mul_of_nonneg_left hw (sq_nonneg N)
        have z := mul_le_mul_of_nonneg_left hx (sq_nonneg N)
        exact mul_le_mul (hd.trans hscale) (by dsimp [x] at *; nlinarith)
          (add_nonneg b₀ (mul_nonneg (sq_nonneg N) w₀)) (by linarith)
      _ = _ := by simp
  have auth : 4096*N^2*y*x ≤ (2:ℝ)^u := by
    have h := mul_le_mul_of_nonneg_right cost_at_cut (mul_nonneg (by linarith : 0≤y) hxpos.le)
    have ex : (2:ℝ)^((249/250:ℝ)*cut) * y * x = 2^u := by
      dsimp [x,y]
      rw [←Real.rpow_add (by norm_num : (0:ℝ)<2),←Real.rpow_add (by norm_num : (0:ℝ)<2)]
      congr 1
      ring
    rw [←ex]
    simpa only [mul_assoc] using h
  have huge : 1 ≤ N^2*y*x := one_le_mul_of_one_le_of_one_le (one_le_mul_of_one_le_of_one_le hN' hy₀) hx
  nlinarith

/-- This is the literal integer exponent for the actual binary uniform rank. -/
theorem current {u k : ℝ} (b w d : Fin 6→ℝ) (hu : 481927710843386≤u)
    (shape : ∀ j, 0≤b j ∧ b j≤((2:ℝ)^CarrierGuards.bitH)^2 ∧ 0≤w j ∧
      w j≤2*(2:ℝ)^(u/250) ∧ 0≤d j ∧ d j≤3+u/CarrierGuards.bitH)
    (debt : k≤1+∑ j, d j*(b j+((2:ℝ)^CarrierGuards.bitH)^2*w j)) :
    k<(2:ℝ)^u/2 := by
  have hreserve : (4096:ℝ)*((2:ℝ)^CarrierGuards.bitH)^2 ≤ 2^((249/250:ℝ)*481927710843386) := by
    have shift : (4096:ℝ)=(2:ℝ)^(12:ℝ) := by norm_num
    rw [shift,←Real.rpow_natCast 2 CarrierGuards.bitH,←Real.rpow_natCast _ 2,
      ←Real.rpow_mul (by norm_num : (0:ℝ)≤2),←Real.rpow_add (by norm_num : (0:ℝ)<2)]
    apply Real.rpow_le_rpow_of_exponent_le (by norm_num)
    norm_num [CarrierGuards.bitH]
  exact six_reserves b w d (by norm_num [CarrierGuards.bitH]) (one_le_pow₀ (by norm_num : (1:ℝ)≤2))
    (by norm_num) (by norm_num [CarrierGuards.bitH]) hu hreserve shape debt

#print axioms six_reserves
#print axioms current
end CarrierStock
