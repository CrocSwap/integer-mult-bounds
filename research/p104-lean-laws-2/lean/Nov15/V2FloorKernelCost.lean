/- V2FloorKernelCost (lane LEAN-KERNEL, Nov 16): flagcheck.c thresholds T(a,b) ≤ 2^30·w_θ(a,b) for the FLAG
certificates: joint θ = 79793/2^20 (proved here from V2FloorCost's log bounds), β θ = 1 (= V2FloorCost.T_beta). -/
import Nov15.V2FloorCost
import Nov15.V2FloorKernelData_j
import Nov15.V2FloorKernelData_b
namespace V2Floor
open Real Finset


theorem T_jk_1_2 : (T_jk 1 2 : ℝ) ≤ 2 ^ 30 * wt (79793 / 1048576 : ℝ) 1 2 := by
  obtain ⟨f1, f2, f3, f4, f5, f6, f7, f8, f9⟩ := flog_vals
  have hA := abs_le.mp bndA; have hB := abs_le.mp bndB; have hC := abs_le.mp bndC; have hD := abs_le.mp bndD
  simp only [T_jk, wt, Wb, Wa, B1]; norm_num [f1, f2, f3, f4, f5, f6, f7, f8, f9]
  nlinarith [hA.1, hA.2, hB.1, hB.2, hC.1, hC.2, hD.1, hD.2]

theorem T_jk_1_3 : (T_jk 1 3 : ℝ) ≤ 2 ^ 30 * wt (79793 / 1048576 : ℝ) 1 3 := by
  obtain ⟨f1, f2, f3, f4, f5, f6, f7, f8, f9⟩ := flog_vals
  have hA := abs_le.mp bndA; have hB := abs_le.mp bndB; have hC := abs_le.mp bndC; have hD := abs_le.mp bndD
  simp only [T_jk, wt, Wb, Wa, B1]; norm_num [f1, f2, f3, f4, f5, f6, f7, f8, f9]
  nlinarith [hA.1, hA.2, hB.1, hB.2, hC.1, hC.2, hD.1, hD.2]

theorem T_jk_1_4 : (T_jk 1 4 : ℝ) ≤ 2 ^ 30 * wt (79793 / 1048576 : ℝ) 1 4 := by
  obtain ⟨f1, f2, f3, f4, f5, f6, f7, f8, f9⟩ := flog_vals
  have hA := abs_le.mp bndA; have hB := abs_le.mp bndB; have hC := abs_le.mp bndC; have hD := abs_le.mp bndD
  simp only [T_jk, wt, Wb, Wa, B1]; norm_num [f1, f2, f3, f4, f5, f6, f7, f8, f9]
  nlinarith [hA.1, hA.2, hB.1, hB.2, hC.1, hC.2, hD.1, hD.2]

theorem T_jk_1_5 : (T_jk 1 5 : ℝ) ≤ 2 ^ 30 * wt (79793 / 1048576 : ℝ) 1 5 := by
  obtain ⟨f1, f2, f3, f4, f5, f6, f7, f8, f9⟩ := flog_vals
  have hA := abs_le.mp bndA; have hB := abs_le.mp bndB; have hC := abs_le.mp bndC; have hD := abs_le.mp bndD
  simp only [T_jk, wt, Wb, Wa, B1]; norm_num [f1, f2, f3, f4, f5, f6, f7, f8, f9]
  nlinarith [hA.1, hA.2, hB.1, hB.2, hC.1, hC.2, hD.1, hD.2]

theorem T_jk_1_6 : (T_jk 1 6 : ℝ) ≤ 2 ^ 30 * wt (79793 / 1048576 : ℝ) 1 6 := by
  obtain ⟨f1, f2, f3, f4, f5, f6, f7, f8, f9⟩ := flog_vals
  have hA := abs_le.mp bndA; have hB := abs_le.mp bndB; have hC := abs_le.mp bndC; have hD := abs_le.mp bndD
  simp only [T_jk, wt, Wb, Wa, B1]; norm_num [f1, f2, f3, f4, f5, f6, f7, f8, f9]
  nlinarith [hA.1, hA.2, hB.1, hB.2, hC.1, hC.2, hD.1, hD.2]

theorem T_jk_1_7 : (T_jk 1 7 : ℝ) ≤ 2 ^ 30 * wt (79793 / 1048576 : ℝ) 1 7 := by
  obtain ⟨f1, f2, f3, f4, f5, f6, f7, f8, f9⟩ := flog_vals
  have hA := abs_le.mp bndA; have hB := abs_le.mp bndB; have hC := abs_le.mp bndC; have hD := abs_le.mp bndD
  simp only [T_jk, wt, Wb, Wa, B1]; norm_num [f1, f2, f3, f4, f5, f6, f7, f8, f9]
  nlinarith [hA.1, hA.2, hB.1, hB.2, hC.1, hC.2, hD.1, hD.2]

theorem T_jk_1_8 : (T_jk 1 8 : ℝ) ≤ 2 ^ 30 * wt (79793 / 1048576 : ℝ) 1 8 := by
  obtain ⟨f1, f2, f3, f4, f5, f6, f7, f8, f9⟩ := flog_vals
  have hA := abs_le.mp bndA; have hB := abs_le.mp bndB; have hC := abs_le.mp bndC; have hD := abs_le.mp bndD
  simp only [T_jk, wt, Wb, Wa, B1]; norm_num [f1, f2, f3, f4, f5, f6, f7, f8, f9]
  nlinarith [hA.1, hA.2, hB.1, hB.2, hC.1, hC.2, hD.1, hD.2]

theorem T_jk_2_3 : (T_jk 2 3 : ℝ) ≤ 2 ^ 30 * wt (79793 / 1048576 : ℝ) 2 3 := by
  obtain ⟨f1, f2, f3, f4, f5, f6, f7, f8, f9⟩ := flog_vals
  have hA := abs_le.mp bndA; have hB := abs_le.mp bndB; have hC := abs_le.mp bndC; have hD := abs_le.mp bndD
  simp only [T_jk, wt, Wb, Wa, B1]; norm_num [f1, f2, f3, f4, f5, f6, f7, f8, f9]
  nlinarith [hA.1, hA.2, hB.1, hB.2, hC.1, hC.2, hD.1, hD.2]

theorem T_jk_2_4 : (T_jk 2 4 : ℝ) ≤ 2 ^ 30 * wt (79793 / 1048576 : ℝ) 2 4 := by
  obtain ⟨f1, f2, f3, f4, f5, f6, f7, f8, f9⟩ := flog_vals
  have hA := abs_le.mp bndA; have hB := abs_le.mp bndB; have hC := abs_le.mp bndC; have hD := abs_le.mp bndD
  simp only [T_jk, wt, Wb, Wa, B1]; norm_num [f1, f2, f3, f4, f5, f6, f7, f8, f9]
  nlinarith [hA.1, hA.2, hB.1, hB.2, hC.1, hC.2, hD.1, hD.2]

theorem T_jk_2_5 : (T_jk 2 5 : ℝ) ≤ 2 ^ 30 * wt (79793 / 1048576 : ℝ) 2 5 := by
  obtain ⟨f1, f2, f3, f4, f5, f6, f7, f8, f9⟩ := flog_vals
  have hA := abs_le.mp bndA; have hB := abs_le.mp bndB; have hC := abs_le.mp bndC; have hD := abs_le.mp bndD
  simp only [T_jk, wt, Wb, Wa, B1]; norm_num [f1, f2, f3, f4, f5, f6, f7, f8, f9]
  nlinarith [hA.1, hA.2, hB.1, hB.2, hC.1, hC.2, hD.1, hD.2]

theorem T_jk_2_6 : (T_jk 2 6 : ℝ) ≤ 2 ^ 30 * wt (79793 / 1048576 : ℝ) 2 6 := by
  obtain ⟨f1, f2, f3, f4, f5, f6, f7, f8, f9⟩ := flog_vals
  have hA := abs_le.mp bndA; have hB := abs_le.mp bndB; have hC := abs_le.mp bndC; have hD := abs_le.mp bndD
  simp only [T_jk, wt, Wb, Wa, B1]; norm_num [f1, f2, f3, f4, f5, f6, f7, f8, f9]
  nlinarith [hA.1, hA.2, hB.1, hB.2, hC.1, hC.2, hD.1, hD.2]

theorem T_jk_2_7 : (T_jk 2 7 : ℝ) ≤ 2 ^ 30 * wt (79793 / 1048576 : ℝ) 2 7 := by
  obtain ⟨f1, f2, f3, f4, f5, f6, f7, f8, f9⟩ := flog_vals
  have hA := abs_le.mp bndA; have hB := abs_le.mp bndB; have hC := abs_le.mp bndC; have hD := abs_le.mp bndD
  simp only [T_jk, wt, Wb, Wa, B1]; norm_num [f1, f2, f3, f4, f5, f6, f7, f8, f9]
  nlinarith [hA.1, hA.2, hB.1, hB.2, hC.1, hC.2, hD.1, hD.2]

theorem T_jk_2_8 : (T_jk 2 8 : ℝ) ≤ 2 ^ 30 * wt (79793 / 1048576 : ℝ) 2 8 := by
  obtain ⟨f1, f2, f3, f4, f5, f6, f7, f8, f9⟩ := flog_vals
  have hA := abs_le.mp bndA; have hB := abs_le.mp bndB; have hC := abs_le.mp bndC; have hD := abs_le.mp bndD
  simp only [T_jk, wt, Wb, Wa, B1]; norm_num [f1, f2, f3, f4, f5, f6, f7, f8, f9]
  nlinarith [hA.1, hA.2, hB.1, hB.2, hC.1, hC.2, hD.1, hD.2]

theorem T_jk_3_4 : (T_jk 3 4 : ℝ) ≤ 2 ^ 30 * wt (79793 / 1048576 : ℝ) 3 4 := by
  obtain ⟨f1, f2, f3, f4, f5, f6, f7, f8, f9⟩ := flog_vals
  have hA := abs_le.mp bndA; have hB := abs_le.mp bndB; have hC := abs_le.mp bndC; have hD := abs_le.mp bndD
  simp only [T_jk, wt, Wb, Wa, B1]; norm_num [f1, f2, f3, f4, f5, f6, f7, f8, f9]
  nlinarith [hA.1, hA.2, hB.1, hB.2, hC.1, hC.2, hD.1, hD.2]

theorem T_jk_3_5 : (T_jk 3 5 : ℝ) ≤ 2 ^ 30 * wt (79793 / 1048576 : ℝ) 3 5 := by
  obtain ⟨f1, f2, f3, f4, f5, f6, f7, f8, f9⟩ := flog_vals
  have hA := abs_le.mp bndA; have hB := abs_le.mp bndB; have hC := abs_le.mp bndC; have hD := abs_le.mp bndD
  simp only [T_jk, wt, Wb, Wa, B1]; norm_num [f1, f2, f3, f4, f5, f6, f7, f8, f9]
  nlinarith [hA.1, hA.2, hB.1, hB.2, hC.1, hC.2, hD.1, hD.2]

theorem T_jk_3_6 : (T_jk 3 6 : ℝ) ≤ 2 ^ 30 * wt (79793 / 1048576 : ℝ) 3 6 := by
  obtain ⟨f1, f2, f3, f4, f5, f6, f7, f8, f9⟩ := flog_vals
  have hA := abs_le.mp bndA; have hB := abs_le.mp bndB; have hC := abs_le.mp bndC; have hD := abs_le.mp bndD
  simp only [T_jk, wt, Wb, Wa, B1]; norm_num [f1, f2, f3, f4, f5, f6, f7, f8, f9]
  nlinarith [hA.1, hA.2, hB.1, hB.2, hC.1, hC.2, hD.1, hD.2]

theorem T_jk_3_7 : (T_jk 3 7 : ℝ) ≤ 2 ^ 30 * wt (79793 / 1048576 : ℝ) 3 7 := by
  obtain ⟨f1, f2, f3, f4, f5, f6, f7, f8, f9⟩ := flog_vals
  have hA := abs_le.mp bndA; have hB := abs_le.mp bndB; have hC := abs_le.mp bndC; have hD := abs_le.mp bndD
  simp only [T_jk, wt, Wb, Wa, B1]; norm_num [f1, f2, f3, f4, f5, f6, f7, f8, f9]
  nlinarith [hA.1, hA.2, hB.1, hB.2, hC.1, hC.2, hD.1, hD.2]

theorem T_jk_3_8 : (T_jk 3 8 : ℝ) ≤ 2 ^ 30 * wt (79793 / 1048576 : ℝ) 3 8 := by
  obtain ⟨f1, f2, f3, f4, f5, f6, f7, f8, f9⟩ := flog_vals
  have hA := abs_le.mp bndA; have hB := abs_le.mp bndB; have hC := abs_le.mp bndC; have hD := abs_le.mp bndD
  simp only [T_jk, wt, Wb, Wa, B1]; norm_num [f1, f2, f3, f4, f5, f6, f7, f8, f9]
  nlinarith [hA.1, hA.2, hB.1, hB.2, hC.1, hC.2, hD.1, hD.2]

theorem T_jk_4_5 : (T_jk 4 5 : ℝ) ≤ 2 ^ 30 * wt (79793 / 1048576 : ℝ) 4 5 := by
  obtain ⟨f1, f2, f3, f4, f5, f6, f7, f8, f9⟩ := flog_vals
  have hA := abs_le.mp bndA; have hB := abs_le.mp bndB; have hC := abs_le.mp bndC; have hD := abs_le.mp bndD
  simp only [T_jk, wt, Wb, Wa, B1]; norm_num [f1, f2, f3, f4, f5, f6, f7, f8, f9]
  nlinarith [hA.1, hA.2, hB.1, hB.2, hC.1, hC.2, hD.1, hD.2]

theorem T_jk_4_6 : (T_jk 4 6 : ℝ) ≤ 2 ^ 30 * wt (79793 / 1048576 : ℝ) 4 6 := by
  obtain ⟨f1, f2, f3, f4, f5, f6, f7, f8, f9⟩ := flog_vals
  have hA := abs_le.mp bndA; have hB := abs_le.mp bndB; have hC := abs_le.mp bndC; have hD := abs_le.mp bndD
  simp only [T_jk, wt, Wb, Wa, B1]; norm_num [f1, f2, f3, f4, f5, f6, f7, f8, f9]
  nlinarith [hA.1, hA.2, hB.1, hB.2, hC.1, hC.2, hD.1, hD.2]

theorem T_jk_4_7 : (T_jk 4 7 : ℝ) ≤ 2 ^ 30 * wt (79793 / 1048576 : ℝ) 4 7 := by
  obtain ⟨f1, f2, f3, f4, f5, f6, f7, f8, f9⟩ := flog_vals
  have hA := abs_le.mp bndA; have hB := abs_le.mp bndB; have hC := abs_le.mp bndC; have hD := abs_le.mp bndD
  simp only [T_jk, wt, Wb, Wa, B1]; norm_num [f1, f2, f3, f4, f5, f6, f7, f8, f9]
  nlinarith [hA.1, hA.2, hB.1, hB.2, hC.1, hC.2, hD.1, hD.2]

theorem T_jk_4_8 : (T_jk 4 8 : ℝ) ≤ 2 ^ 30 * wt (79793 / 1048576 : ℝ) 4 8 := by
  obtain ⟨f1, f2, f3, f4, f5, f6, f7, f8, f9⟩ := flog_vals
  have hA := abs_le.mp bndA; have hB := abs_le.mp bndB; have hC := abs_le.mp bndC; have hD := abs_le.mp bndD
  simp only [T_jk, wt, Wb, Wa, B1]; norm_num [f1, f2, f3, f4, f5, f6, f7, f8, f9]
  nlinarith [hA.1, hA.2, hB.1, hB.2, hC.1, hC.2, hD.1, hD.2]

theorem T_jk_5_6 : (T_jk 5 6 : ℝ) ≤ 2 ^ 30 * wt (79793 / 1048576 : ℝ) 5 6 := by
  obtain ⟨f1, f2, f3, f4, f5, f6, f7, f8, f9⟩ := flog_vals
  have hA := abs_le.mp bndA; have hB := abs_le.mp bndB; have hC := abs_le.mp bndC; have hD := abs_le.mp bndD
  simp only [T_jk, wt, Wb, Wa, B1]; norm_num [f1, f2, f3, f4, f5, f6, f7, f8, f9]
  nlinarith [hA.1, hA.2, hB.1, hB.2, hC.1, hC.2, hD.1, hD.2]

theorem T_jk_5_7 : (T_jk 5 7 : ℝ) ≤ 2 ^ 30 * wt (79793 / 1048576 : ℝ) 5 7 := by
  obtain ⟨f1, f2, f3, f4, f5, f6, f7, f8, f9⟩ := flog_vals
  have hA := abs_le.mp bndA; have hB := abs_le.mp bndB; have hC := abs_le.mp bndC; have hD := abs_le.mp bndD
  simp only [T_jk, wt, Wb, Wa, B1]; norm_num [f1, f2, f3, f4, f5, f6, f7, f8, f9]
  nlinarith [hA.1, hA.2, hB.1, hB.2, hC.1, hC.2, hD.1, hD.2]

theorem T_jk_5_8 : (T_jk 5 8 : ℝ) ≤ 2 ^ 30 * wt (79793 / 1048576 : ℝ) 5 8 := by
  obtain ⟨f1, f2, f3, f4, f5, f6, f7, f8, f9⟩ := flog_vals
  have hA := abs_le.mp bndA; have hB := abs_le.mp bndB; have hC := abs_le.mp bndC; have hD := abs_le.mp bndD
  simp only [T_jk, wt, Wb, Wa, B1]; norm_num [f1, f2, f3, f4, f5, f6, f7, f8, f9]
  nlinarith [hA.1, hA.2, hB.1, hB.2, hC.1, hC.2, hD.1, hD.2]

theorem T_jk_6_7 : (T_jk 6 7 : ℝ) ≤ 2 ^ 30 * wt (79793 / 1048576 : ℝ) 6 7 := by
  obtain ⟨f1, f2, f3, f4, f5, f6, f7, f8, f9⟩ := flog_vals
  have hA := abs_le.mp bndA; have hB := abs_le.mp bndB; have hC := abs_le.mp bndC; have hD := abs_le.mp bndD
  simp only [T_jk, wt, Wb, Wa, B1]; norm_num [f1, f2, f3, f4, f5, f6, f7, f8, f9]
  nlinarith [hA.1, hA.2, hB.1, hB.2, hC.1, hC.2, hD.1, hD.2]

theorem T_jk_6_8 : (T_jk 6 8 : ℝ) ≤ 2 ^ 30 * wt (79793 / 1048576 : ℝ) 6 8 := by
  obtain ⟨f1, f2, f3, f4, f5, f6, f7, f8, f9⟩ := flog_vals
  have hA := abs_le.mp bndA; have hB := abs_le.mp bndB; have hC := abs_le.mp bndC; have hD := abs_le.mp bndD
  simp only [T_jk, wt, Wb, Wa, B1]; norm_num [f1, f2, f3, f4, f5, f6, f7, f8, f9]
  nlinarith [hA.1, hA.2, hB.1, hB.2, hC.1, hC.2, hD.1, hD.2]

theorem T_jk_7_8 : (T_jk 7 8 : ℝ) ≤ 2 ^ 30 * wt (79793 / 1048576 : ℝ) 7 8 := by
  obtain ⟨f1, f2, f3, f4, f5, f6, f7, f8, f9⟩ := flog_vals
  have hA := abs_le.mp bndA; have hB := abs_le.mp bndB; have hC := abs_le.mp bndC; have hD := abs_le.mp bndD
  simp only [T_jk, wt, Wb, Wa, B1]; norm_num [f1, f2, f3, f4, f5, f6, f7, f8, f9]
  nlinarith [hA.1, hA.2, hB.1, hB.2, hC.1, hC.2, hD.1, hD.2]

theorem T_jk_le (a b : ℕ) (h1 : 1 ≤ a) (hab : a < b) (h8 : b ≤ 8) : (T_jk a b : ℝ) ≤ 2 ^ 30 * wt (79793 / 1048576 : ℝ) a b := by
  have ha7 : a ≤ 7 := by omega
  interval_cases a <;> interval_cases b <;> first | exact T_jk_1_2 | exact T_jk_1_3 | exact T_jk_1_4 | exact T_jk_1_5 | exact T_jk_1_6 | exact T_jk_1_7 | exact T_jk_1_8 | exact T_jk_2_3 | exact T_jk_2_4 | exact T_jk_2_5 | exact T_jk_2_6 | exact T_jk_2_7 | exact T_jk_2_8 | exact T_jk_3_4 | exact T_jk_3_5 | exact T_jk_3_6 | exact T_jk_3_7 | exact T_jk_3_8 | exact T_jk_4_5 | exact T_jk_4_6 | exact T_jk_4_7 | exact T_jk_4_8 | exact T_jk_5_6 | exact T_jk_5_7 | exact T_jk_5_8 | exact T_jk_6_7 | exact T_jk_6_8 | exact T_jk_7_8

theorem T_bk_le (a b : ℕ) (h1 : 1 ≤ a) (hab : a < b) (h8 : b ≤ 8) : (T_bk a b : ℝ) ≤ 2 ^ 30 * wt (1 : ℝ) a b := by
  have e : T_bk a b = T_beta a b := by
    have ha7 : a ≤ 7 := by omega
    interval_cases a <;> interval_cases b <;> rfl
  rw [e]; exact T_beta_le a b h1 hab h8
end V2Floor
