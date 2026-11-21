import InputFloor
import Mathlib.Data.Fintype.Card

namespace CarrierInputFloor

/-- The outer controller needs distinct positive axis addresses below the
largest width. This is impossible throughout the stated precision interval. -/
theorem no_fine_axes {p z : ℝ} {d width : ℕ} (hp : 64≤p) (hz : 6≤z)
    (cap : z≤5000000000000000) (bits : p=(2:ℝ)^z)
    (dimension : p^((1:ℝ)-1/100000000000000)/2≤d)
    (axis : (width:ℝ) ≤ 1+(p/6+3)/d)
    (chooseAxis : Fin d → Fin (2^width)) : ¬Function.Injective chooseAxis := by
  let g : ℝ := 1/100000000000000
  have hreal : 0<p := by linarith
  have hbase := Real.rpow_pos_of_pos hreal (1-g)
  have dpos : (0:ℝ)<d := (div_pos hbase (by norm_num : (0:ℝ)<2)).trans_le dimension
  have hmul : p^g*p^(1-g)=p := by
    rw [←Real.rpow_add hreal,show g+(1-g)=1 by ring,Real.rpow_one]
  have pw : (2:ℝ)^(z/100000000000000) = p^g := by
    rw [bits]
    change _ = ((2:ℝ)^z)^(1/100000000000000:ℝ)
    rw [←Real.rpow_mul (by norm_num)]; congr 1; ring
  have w : (width:ℝ) ≤ 1+(1/3+6/p)*(2:ℝ)^(z/100000000000000) := by
    rw [pw]
    apply axis.trans (add_le_add_right _ 1)
    rw [div_le_iff₀ dpos]
    have fact : p/6+3 = ((1/3+6/p)*p^g)*(p^(1-g)/2) := by
      calc
        p/6+3 = ((1/3+6/p)*p)/2 := by field_simp; ring
        _ = ((1/3+6/p)*(p^g*p^(1-g)))/2 := congrArg (fun x : ℝ ↦ ((1/3+6/p)*x)/2) hmul.symm
        _ = _ := by ring
    rw [fact]
    exact mul_le_mul_of_nonneg_left dimension (by positivity)
  have a : (2:ℝ)^((1-g)*z-1) ≤ d := by
    rw [Real.rpow_sub (by norm_num : (0:ℝ)<2),Real.rpow_one,mul_comm (1-g) z,
      Real.rpow_mul (by norm_num),←bits]
    exact dimension
  have h := impossible_geometry hp hz cap w a
  have hnat : 2^width < d := by
    rw [Real.rpow_natCast] at h
    exact_mod_cast h
  intro hi
  have counts := Fintype.card_le_of_injective chooseAxis hi
  simp only [Fintype.card_fin] at counts
  omega

#print axioms no_fine_axes
end CarrierInputFloor
