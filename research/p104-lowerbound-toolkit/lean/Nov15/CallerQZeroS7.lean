/- CallerQZero checkpoint steps, chunk 7. -/
import Nov15.CallerQZeroD
set_option linter.unusedSectionVars false
set_option linter.unusedVariables false
set_option maxHeartbeats 4000000
set_option linter.unusedSimpArgs false
namespace CallerQZero
open Matrix CallerWord
section steps
variable {S : Type} [CommRing S] [Algebra ℚ S]

theorem st63 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.add 1 0 (-21/4) : Ev 4 3) * ck63 q i ((algebraMap ℚ S (1/390))) D = ck64 q i ((algebraMap ℚ S (1/390))) D + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![0, 0, 0, 0; (-20475 : S) * q * (algebraMap ℚ S (1/390))^2 * (D 1) * (D 2) + (20475 : S) * q * i * (algebraMap ℚ S (1/390))^2 * (D 1) * (D 2) + (-20475 : S) * q^3 * (algebraMap ℚ S (1/390))^2 * (D 1) * (D 2) + (-20475 : S) * q^3 * i * (algebraMap ℚ S (1/390))^2 * (D 1) * (D 2), 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck63, ck64, qp] <;> ring

theorem st64 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.scale 0 (39/2) : Ev 4 3) * ck64 q i ((algebraMap ℚ S (1/390))) D = ck65 q i ((algebraMap ℚ S (1/390))) D + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![(195 : S) * q * (algebraMap ℚ S (1/390)) * (D 1) * (D 2) + (-195 : S) * q * i * (algebraMap ℚ S (1/390)) * (D 1) * (D 2) + (195 : S) * q^3 * (algebraMap ℚ S (1/390)) * (D 1) * (D 2) + (195 : S) * q^3 * i * (algebraMap ℚ S (1/390)) * (D 1) * (D 2), 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck64, ck65, qp] <;> ring

theorem st65 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.lam 0 (1) : Ev 4 3) * ck65 q i ((algebraMap ℚ S (1/390))) D = ck66 q i ((algebraMap ℚ S (1/390))) D + (q ^ 4 - 1) • !![(38025 : S) * q * (algebraMap ℚ S (1/390))^2 * (D 1) * (D 2) + (-38025 : S) * q * i^2 * (algebraMap ℚ S (1/390))^2 * (D 1) * (D 2), 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0] + (i ^ 2 + 1) • !![(-76050 : S) * q * (algebraMap ℚ S (1/390))^2 * (D 1) * (D 2) + (76050 : S) * q^3 * (algebraMap ℚ S (1/390))^2 * (D 1) * (D 2), 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0] + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![(1 : S) * q * (D 1) * (D 2) + (390 : S) * q * (algebraMap ℚ S (1/390)) * (D 1) * (D 2), 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck65, ck66, qp] <;> ring

theorem st66 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.lam 1 (1) : Ev 4 3) * ck66 q i ((algebraMap ℚ S (1/390))) D = ck67 q i ((algebraMap ℚ S (1/390))) D + (q ^ 4 - 1) • !![0, 0, 0, 0; 0, (38025 : S) * q * (algebraMap ℚ S (1/390))^2 * (D 1) * (D 2) + (-38025 : S) * q * i^2 * (algebraMap ℚ S (1/390))^2 * (D 1) * (D 2), 0, 0; 0, 0, 0, 0; 0, 0, 0, 0] + (i ^ 2 + 1) • !![0, 0, 0, 0; 0, (-76050 : S) * q * (algebraMap ℚ S (1/390))^2 * (D 1) * (D 2) + (76050 : S) * q^3 * (algebraMap ℚ S (1/390))^2 * (D 1) * (D 2), 0, 0; 0, 0, 0, 0; 0, 0, 0, 0] + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![0, 0, 0, 0; 0, (1 : S) * q * (D 1) * (D 2) + (390 : S) * q * (algebraMap ℚ S (1/390)) * (D 1) * (D 2), 0, 0; 0, 0, 0, 0; 0, 0, 0, 0] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck66, ck67, qp] <;> ring

theorem st67 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.lam 2 (1) : Ev 4 3) * ck67 q i ((algebraMap ℚ S (1/390))) D = ck68 q i ((algebraMap ℚ S (1/390))) D + (q ^ 4 - 1) • !![0, 0, 0, 0; 0, 0, 0, 0; 0, 0, (38025 : S) * q * (algebraMap ℚ S (1/390))^2 * (D 0) * (D 1) * (D 2) + (-38025 : S) * q * i^2 * (algebraMap ℚ S (1/390))^2 * (D 0) * (D 1) * (D 2), 0; 0, 0, 0, 0] + (i ^ 2 + 1) • !![0, 0, 0, 0; 0, 0, 0, 0; 0, 0, (-76050 : S) * q * (algebraMap ℚ S (1/390))^2 * (D 0) * (D 1) * (D 2) + (76050 : S) * q^3 * (algebraMap ℚ S (1/390))^2 * (D 0) * (D 1) * (D 2), 0; 0, 0, 0, 0] + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![0, 0, 0, 0; 0, 0, 0, 0; 0, 0, (1 : S) * q * (D 0) * (D 1) * (D 2) + (390 : S) * q * (algebraMap ℚ S (1/390)) * (D 0) * (D 1) * (D 2), 0; 0, 0, 0, 0] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck67, ck68, qp] <;> ring

theorem st68 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.lam 3 (1) : Ev 4 3) * ck68 q i ((algebraMap ℚ S (1/390))) D = ck69 q i ((algebraMap ℚ S (1/390))) D + (q ^ 4 - 1) • !![0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, (38025 : S) * q * (algebraMap ℚ S (1/390))^2 * (D 0) * (D 1) * (D 2) + (-38025 : S) * q * i^2 * (algebraMap ℚ S (1/390))^2 * (D 0) * (D 1) * (D 2)] + (i ^ 2 + 1) • !![0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, (-76050 : S) * q * (algebraMap ℚ S (1/390))^2 * (D 0) * (D 1) * (D 2) + (76050 : S) * q^3 * (algebraMap ℚ S (1/390))^2 * (D 0) * (D 1) * (D 2)] + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, (1 : S) * q * (D 0) * (D 1) * (D 2) + (390 : S) * q * (algebraMap ℚ S (1/390)) * (D 0) * (D 1) * (D 2)] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck68, ck69, qp] <;> ring


end steps
end CallerQZero
