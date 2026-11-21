/- CallerQZero checkpoint steps, chunk 1. -/
import Nov15.CallerQZeroD
set_option linter.unusedSectionVars false
set_option linter.unusedVariables false
set_option maxHeartbeats 4000000
set_option linter.unusedSimpArgs false
namespace CallerQZero
open Matrix CallerWord
section steps
variable {S : Type} [CommRing S] [Algebra ℚ S]

theorem st9 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.add 0 2 (-2) : Ev 4 3) * ck9 q i ((algebraMap ℚ S (1/390))) D = ck10 q i ((algebraMap ℚ S (1/390))) D + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![0, 0, 0, (1 : S) * q * (D 0) + (-1 : S) * q * i * (D 0) + (1 : S) * q^3 * (D 0) + (1 : S) * q^3 * i * (D 0); 0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck9, ck10, qp] <;> ring

theorem st10 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.scale 2 (2) : Ev 4 3) * ck10 q i ((algebraMap ℚ S (1/390))) D = ck11 q i ((algebraMap ℚ S (1/390))) D + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, (-1 : S) * q * (D 0) + (1 : S) * q * i * (D 0) + (-1 : S) * q^3 * (D 0) + (-1 : S) * q^3 * i * (D 0); 0, 0, 0, 0] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck10, ck11, qp] <;> ring

theorem st11 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.add 3 1 (1/3) : Ev 4 3) * ck11 q i ((algebraMap ℚ S (1/390))) D = ck12 q i ((algebraMap ℚ S (1/390))) D + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0; 0, 0, (156 : S) * q * (algebraMap ℚ S (1/390)) * (D 0) + (-2535 : S) * q * (algebraMap ℚ S (1/390))^2 * (D 0) + (-156 : S) * q * i * (algebraMap ℚ S (1/390)) * (D 0) + (2535 : S) * q * i * (algebraMap ℚ S (1/390))^2 * (D 0) + (156 : S) * q^3 * (algebraMap ℚ S (1/390)) * (D 0) + (-2535 : S) * q^3 * (algebraMap ℚ S (1/390))^2 * (D 0) + (156 : S) * q^3 * i * (algebraMap ℚ S (1/390)) * (D 0) + (-2535 : S) * q^3 * i * (algebraMap ℚ S (1/390))^2 * (D 0), (-13 : S) * (algebraMap ℚ S (1/390)) * (D 0) + (-65 : S) * q * (algebraMap ℚ S (1/390)) * (D 0) + (65 : S) * q * i * (algebraMap ℚ S (1/390)) * (D 0) + (-65 : S) * q^3 * (algebraMap ℚ S (1/390)) * (D 0) + (-65 : S) * q^3 * i * (algebraMap ℚ S (1/390)) * (D 0)] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck11, ck12, qp] <;> ring

theorem st12 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.add 2 1 (-10/3) : Ev 4 3) * ck12 q i ((algebraMap ℚ S (1/390))) D = ck13 q i ((algebraMap ℚ S (1/390))) D + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![0, 0, 0, 0; 0, 0, 0, 0; 0, 0, (-2 : S) * (D 0) + (65 : S) * q * (algebraMap ℚ S (1/390)) * (D 0) + (25350 : S) * q * (algebraMap ℚ S (1/390))^2 * (D 0) + (-65 : S) * q * i * (algebraMap ℚ S (1/390)) * (D 0) + (-25350 : S) * q * i * (algebraMap ℚ S (1/390))^2 * (D 0) + (65 : S) * q^3 * (algebraMap ℚ S (1/390)) * (D 0) + (25350 : S) * q^3 * (algebraMap ℚ S (1/390))^2 * (D 0) + (65 : S) * q^3 * i * (algebraMap ℚ S (1/390)) * (D 0) + (25350 : S) * q^3 * i * (algebraMap ℚ S (1/390))^2 * (D 0), (130 : S) * (algebraMap ℚ S (1/390)) * (D 0) + (1 : S) * q * (D 0) + (650 : S) * q * (algebraMap ℚ S (1/390)) * (D 0) + (-1 : S) * q * i * (D 0) + (-650 : S) * q * i * (algebraMap ℚ S (1/390)) * (D 0) + (1 : S) * q^3 * (D 0) + (650 : S) * q^3 * (algebraMap ℚ S (1/390)) * (D 0) + (1 : S) * q^3 * i * (D 0) + (650 : S) * q^3 * i * (algebraMap ℚ S (1/390)) * (D 0); 0, 0, 0, 0] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck12, ck13, qp] <;> ring

theorem st13 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.add 0 1 (4/3) : Ev 4 3) * ck13 q i ((algebraMap ℚ S (1/390))) D = ck14 q i ((algebraMap ℚ S (1/390))) D + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![0, 0, (2 : S) * (D 0) + (-26 : S) * q * (algebraMap ℚ S (1/390)) * (D 0) + (-10140 : S) * q * (algebraMap ℚ S (1/390))^2 * (D 0) + (26 : S) * q * i * (algebraMap ℚ S (1/390)) * (D 0) + (10140 : S) * q * i * (algebraMap ℚ S (1/390))^2 * (D 0) + (-26 : S) * q^3 * (algebraMap ℚ S (1/390)) * (D 0) + (-10140 : S) * q^3 * (algebraMap ℚ S (1/390))^2 * (D 0) + (-26 : S) * q^3 * i * (algebraMap ℚ S (1/390)) * (D 0) + (-10140 : S) * q^3 * i * (algebraMap ℚ S (1/390))^2 * (D 0), (-52 : S) * (algebraMap ℚ S (1/390)) * (D 0) + (-1 : S) * q * (D 0) + (-260 : S) * q * (algebraMap ℚ S (1/390)) * (D 0) + (1 : S) * q * i * (D 0) + (260 : S) * q * i * (algebraMap ℚ S (1/390)) * (D 0) + (-1 : S) * q^3 * (D 0) + (-260 : S) * q^3 * (algebraMap ℚ S (1/390)) * (D 0) + (-1 : S) * q^3 * i * (D 0) + (-260 : S) * q^3 * i * (algebraMap ℚ S (1/390)) * (D 0); 0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck13, ck14, qp] <;> ring

theorem st14 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.scale 1 (5/3) : Ev 4 3) * ck14 q i ((algebraMap ℚ S (1/390))) D = ck15 q i ((algebraMap ℚ S (1/390))) D + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![0, 0, 0, 0; 0, 0, (-12675 : S) * q * (algebraMap ℚ S (1/390))^2 * (D 0) + (12675 : S) * q * i * (algebraMap ℚ S (1/390))^2 * (D 0) + (-12675 : S) * q^3 * (algebraMap ℚ S (1/390))^2 * (D 0) + (-12675 : S) * q^3 * i * (algebraMap ℚ S (1/390))^2 * (D 0), (-65 : S) * (algebraMap ℚ S (1/390)) * (D 0) + (-325 : S) * q * (algebraMap ℚ S (1/390)) * (D 0) + (325 : S) * q * i * (algebraMap ℚ S (1/390)) * (D 0) + (-325 : S) * q^3 * (algebraMap ℚ S (1/390)) * (D 0) + (-325 : S) * q^3 * i * (algebraMap ℚ S (1/390)) * (D 0); 0, 0, 0, 0; 0, 0, 0, 0] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck14, ck15, qp] <;> ring

theorem st15 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.add 3 0 (1/2) : Ev 4 3) * ck15 q i ((algebraMap ℚ S (1/390))) D = ck16 q i ((algebraMap ℚ S (1/390))) D + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0; 0, (1 : S) + (260 : S) * (algebraMap ℚ S (1/390)), (-130 : S) * (algebraMap ℚ S (1/390)) * (D 0) + (-195 : S) * q * (algebraMap ℚ S (1/390)) * (D 0) + (195 : S) * q * i * (algebraMap ℚ S (1/390)) * (D 0) + (-195 : S) * q^3 * (algebraMap ℚ S (1/390)) * (D 0) + (-195 : S) * q^3 * i * (algebraMap ℚ S (1/390)) * (D 0), (-1 : S) * (D 0) + (-65 : S) * (algebraMap ℚ S (1/390)) * (D 0) + (65 : S) * q * (algebraMap ℚ S (1/390)) * (D 0) + (-65 : S) * q * i * (algebraMap ℚ S (1/390)) * (D 0) + (65 : S) * q^3 * (algebraMap ℚ S (1/390)) * (D 0) + (65 : S) * q^3 * i * (algebraMap ℚ S (1/390)) * (D 0)] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck15, ck16, qp] <;> ring

theorem st16 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.add 2 0 (1) : Ev 4 3) * ck16 q i ((algebraMap ℚ S (1/390))) D = ck17 q i ((algebraMap ℚ S (1/390))) D + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![0, 0, 0, 0; 0, 0, 0, 0; 0, (-2 : S), (-2 : S) * (D 0), (1 : S) * q * (D 0) + (-1 : S) * q * i * (D 0) + (1 : S) * q^3 * (D 0) + (1 : S) * q^3 * i * (D 0); 0, 0, 0, 0] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck16, ck17, qp] <;> ring

theorem st17 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.add 1 0 (-7/2) : Ev 4 3) * ck17 q i ((algebraMap ℚ S (1/390))) D = ck18 q i ((algebraMap ℚ S (1/390))) D + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![0, 0, 0, 0; 0, (-3 : S) + (-1820 : S) * (algebraMap ℚ S (1/390)), (4 : S) * (D 0) + (910 : S) * (algebraMap ℚ S (1/390)) * (D 0) + (195 : S) * q * (algebraMap ℚ S (1/390)) * (D 0) + (-195 : S) * q * i * (algebraMap ℚ S (1/390)) * (D 0) + (195 : S) * q^3 * (algebraMap ℚ S (1/390)) * (D 0) + (195 : S) * q^3 * i * (algebraMap ℚ S (1/390)) * (D 0), (1 : S) * (D 0) + (455 : S) * (algebraMap ℚ S (1/390)) * (D 0) + (-2 : S) * q * (D 0) + (-455 : S) * q * (algebraMap ℚ S (1/390)) * (D 0) + (2 : S) * q * i * (D 0) + (455 : S) * q * i * (algebraMap ℚ S (1/390)) * (D 0) + (-2 : S) * q^3 * (D 0) + (-455 : S) * q^3 * (algebraMap ℚ S (1/390)) * (D 0) + (-2 : S) * q^3 * i * (D 0) + (-455 : S) * q^3 * i * (algebraMap ℚ S (1/390)) * (D 0); 0, 0, 0, 0; 0, 0, 0, 0] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck17, ck18, qp] <;> ring

end steps
end CallerQZero
