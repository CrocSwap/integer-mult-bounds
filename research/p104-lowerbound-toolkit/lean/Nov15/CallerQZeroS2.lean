/- CallerQZero checkpoint steps, chunk 2. -/
import Nov15.CallerQZeroD
set_option linter.unusedSectionVars false
set_option linter.unusedVariables false
set_option maxHeartbeats 4000000
set_option linter.unusedSimpArgs false
namespace CallerQZero
open Matrix CallerWord
section steps
variable {S : Type} [CommRing S] [Algebra ℚ S]

theorem st18 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.scale 0 (-3) : Ev 4 3) * ck18 q i ((algebraMap ℚ S (1/390))) D = ck19 q i ((algebraMap ℚ S (1/390))) D + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![0, (-4 : S), (2 : S) * (D 0), (1 : S) * (D 0) + (-1 : S) * q * (D 0) + (1 : S) * q * i * (D 0) + (-1 : S) * q^3 * (D 0) + (-1 : S) * q^3 * i * (D 0); 0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck18, ck19, qp] <;> ring

theorem st19 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.lam 1 (-1) : Ev 4 3) * ck19 q i ((algebraMap ℚ S (1/390))) D = ck20 q i ((algebraMap ℚ S (1/390))) D + (q ^ 4 - 1) • !![0, 0, 0, 0; 0, 0, (38025 : S) * q * (algebraMap ℚ S (1/390))^2 * (D 0) + (76050 : S) * q * i * (algebraMap ℚ S (1/390))^2 * (D 0) + (38025 : S) * q * i^2 * (algebraMap ℚ S (1/390))^2 * (D 0), (-390 : S) * q * (algebraMap ℚ S (1/390)) * (D 0) + (-780 : S) * q * i * (algebraMap ℚ S (1/390)) * (D 0) + (-390 : S) * q * i^2 * (algebraMap ℚ S (1/390)) * (D 0); 0, 0, 0, 0; 0, 0, 0, 0] + (i ^ 2 + 1) • !![0, 0, 0, 0; 0, 0, (76050 : S) * q * (algebraMap ℚ S (1/390))^2 * (D 0) + (-76050 : S) * q^3 * (algebraMap ℚ S (1/390))^2 * (D 0), (-780 : S) * q * (algebraMap ℚ S (1/390)) * (D 0) + (780 : S) * q^3 * (algebraMap ℚ S (1/390)) * (D 0); 0, 0, 0, 0; 0, 0, 0, 0] + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![0, 0, 0, 0; 0, 0, (2 : S) * (D 0) + (-2 : S) * i * (D 0) + (2 : S) * q^2 * (D 0) + (2 : S) * q^2 * i * (D 0) + (1 : S) * q^3 * (D 0) + (390 : S) * q^3 * (algebraMap ℚ S (1/390)) * (D 0), (-4 : S) * q^3 * (D 0); 0, 0, 0, 0; 0, 0, 0, 0] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck19, ck20, qp] <;> ring

theorem st20 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.host 0 1 (-1) (2) : Ev 4 3) * ck20 q i ((algebraMap ℚ S (1/390))) D = ck21 q i ((algebraMap ℚ S (1/390))) D + (q ^ 4 - 1) • !![0, 0, (-1 : S) * (D 0), (4 : S) * (D 0); 0, 0, (390 : S) * (algebraMap ℚ S (1/390)) * (D 0) + (-390 : S) * i * (algebraMap ℚ S (1/390)) * (D 0) + (390 : S) * q^2 * (algebraMap ℚ S (1/390)) * (D 0) + (390 : S) * q^2 * i * (algebraMap ℚ S (1/390)) * (D 0), (-2 : S) * (D 0) + (2 : S) * i * (D 0) + (-2 : S) * q^2 * (D 0) + (-2 : S) * q^2 * i * (D 0); 0, 0, 0, 0; 0, 0, 0, 0] + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![0, 0, (2 : S) * q * (D 0) + (-2 : S) * q * i * (D 0) + (2 : S) * q^3 * (D 0) + (2 : S) * q^3 * i * (D 0), (1 : S) * q * (D 0) + (-1 : S) * q * i * (D 0) + (1 : S) * q^3 * (D 0) + (1 : S) * q^3 * i * (D 0); 0, 0, (1 : S) * (D 0) + (-1 : S) * i * (D 0) + (1 : S) * q^2 * (D 0) + (1 : S) * q^2 * i * (D 0), (2 : S) * (D 0) + (-2 : S) * i * (D 0) + (2 : S) * q^2 * (D 0) + (2 : S) * q^2 * i * (D 0); 0, 0, 0, 0; 0, 0, 0, 0] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck20, ck21, qp] <;> ring

theorem st21 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.idle 0 {1} 0 : Ev 4 3) * ck21 q i ((algebraMap ℚ S (1/390))) D = ck22 q i ((algebraMap ℚ S (1/390))) D := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck21, ck22, qp] <;> ring

theorem st22 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.idle 1 {1} 0 : Ev 4 3) * ck22 q i ((algebraMap ℚ S (1/390))) D = ck23 q i ((algebraMap ℚ S (1/390))) D := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck22, ck23, qp] <;> ring

theorem st23 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.lam 1 (1) : Ev 4 3) * ck23 q i ((algebraMap ℚ S (1/390))) D = ck24 q i ((algebraMap ℚ S (1/390))) D + (q ^ 4 - 1) • !![0, 0, 0, 0; (51904125 : S) * (algebraMap ℚ S (1/390))^3 * (D 1) + (-51904125 : S) * i^2 * (algebraMap ℚ S (1/390))^3 * (D 1) + (-1170 : S) * q * (algebraMap ℚ S (1/390)) * (D 1) + (1170 : S) * q * i * (algebraMap ℚ S (1/390)) * (D 1), (114075 : S) * (algebraMap ℚ S (1/390))^2 * (D 1) + (-114075 : S) * i^2 * (algebraMap ℚ S (1/390))^2 * (D 1) + (-1560 : S) * q * (algebraMap ℚ S (1/390)) * (D 1) + (1560 : S) * q * i * (algebraMap ℚ S (1/390)) * (D 1), (-195 : S) * (algebraMap ℚ S (1/390)) * (D 0) * (D 1) + (195 : S) * i^2 * (algebraMap ℚ S (1/390)) * (D 0) * (D 1) + (585 : S) * q * (algebraMap ℚ S (1/390)) * (D 0) * (D 1) + (-585 : S) * q * i * (algebraMap ℚ S (1/390)) * (D 0) * (D 1), (-190125 : S) * (algebraMap ℚ S (1/390))^2 * (D 0) * (D 1) + (190125 : S) * i^2 * (algebraMap ℚ S (1/390))^2 * (D 0) * (D 1) + (1170 : S) * q * (algebraMap ℚ S (1/390)) * (D 0) * (D 1) + (-1170 : S) * q * i * (algebraMap ℚ S (1/390)) * (D 0) * (D 1); 0, 0, 0, 0; 0, 0, 0, 0] + (i ^ 2 + 1) • !![0, 0, 0, 0; (-103808250 : S) * (algebraMap ℚ S (1/390))^3 * (D 1) + (103808250 : S) * q^2 * (algebraMap ℚ S (1/390))^3 * (D 1), (-228150 : S) * (algebraMap ℚ S (1/390))^2 * (D 1) + (228150 : S) * q^2 * (algebraMap ℚ S (1/390))^2 * (D 1), (390 : S) * (algebraMap ℚ S (1/390)) * (D 0) * (D 1) + (-390 : S) * q^2 * (algebraMap ℚ S (1/390)) * (D 0) * (D 1), (380250 : S) * (algebraMap ℚ S (1/390))^2 * (D 0) * (D 1) + (-380250 : S) * q^2 * (algebraMap ℚ S (1/390))^2 * (D 0) * (D 1); 0, 0, 0, 0; 0, 0, 0, 0] + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![0, 0, 0, 0; (1365 : S) * (algebraMap ℚ S (1/390)) * (D 1) + (532350 : S) * (algebraMap ℚ S (1/390))^2 * (D 1) + (-3 : S) * q * (D 1) + (3 : S) * q * i * (D 1) + (-3 : S) * q^3 * (D 1) + (-3 : S) * q^3 * i * (D 1), (3 : S) * (D 1) + (1170 : S) * (algebraMap ℚ S (1/390)) * (D 1) + (-4 : S) * q * (D 1) + (4 : S) * q * i * (D 1) + (-4 : S) * q^3 * (D 1) + (-4 : S) * q^3 * i * (D 1), (-2 : S) * (D 0) * (D 1), (-5 : S) * (D 0) * (D 1) + (-1950 : S) * (algebraMap ℚ S (1/390)) * (D 0) * (D 1) + (3 : S) * q * (D 0) * (D 1) + (-3 : S) * q * i * (D 0) * (D 1) + (3 : S) * q^3 * (D 0) * (D 1) + (3 : S) * q^3 * i * (D 0) * (D 1); 0, 0, 0, 0; 0, 0, 0, 0] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck23, ck24, qp] <;> ring

theorem st24 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.idle 2 {1} 0 : Ev 4 3) * ck24 q i ((algebraMap ℚ S (1/390))) D = ck25 q i ((algebraMap ℚ S (1/390))) D := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck24, ck25, qp] <;> ring

theorem st25 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.idle 3 {1} 0 : Ev 4 3) * ck25 q i ((algebraMap ℚ S (1/390))) D = ck26 q i ((algebraMap ℚ S (1/390))) D := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck25, ck26, qp] <;> ring

theorem st26 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.add 2 3 (1/3) : Ev 4 3) * ck26 q i ((algebraMap ℚ S (1/390))) D = ck27 q i ((algebraMap ℚ S (1/390))) D + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![0, 0, 0, 0; 0, 0, 0, 0; (-1 : S) * (D 1) + (65 : S) * (algebraMap ℚ S (1/390)) * (D 1), (2 : S) * (D 1), (-65 : S) * q * (algebraMap ℚ S (1/390)) * (D 0) * (D 1) + (65 : S) * q * i * (algebraMap ℚ S (1/390)) * (D 0) * (D 1) + (-65 : S) * q^3 * (algebraMap ℚ S (1/390)) * (D 0) * (D 1) + (-65 : S) * q^3 * i * (algebraMap ℚ S (1/390)) * (D 0) * (D 1), 0; 0, 0, 0, 0] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck26, ck27, qp] <;> ring

end steps
end CallerQZero
