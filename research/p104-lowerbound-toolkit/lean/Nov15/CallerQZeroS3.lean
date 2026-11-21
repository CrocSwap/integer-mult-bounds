/- CallerQZero checkpoint steps, chunk 3. -/
import Nov15.CallerQZeroD
set_option linter.unusedSectionVars false
set_option linter.unusedVariables false
set_option maxHeartbeats 4000000
set_option linter.unusedSimpArgs false
namespace CallerQZero
open Matrix CallerWord
section steps
variable {S : Type} [CommRing S] [Algebra ℚ S]

theorem st27 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.add 1 3 (1/3) : Ev 4 3) * ck27 q i ((algebraMap ℚ S (1/390))) D = ck28 q i ((algebraMap ℚ S (1/390))) D + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![0, 0, 0, 0; (65 : S) * (algebraMap ℚ S (1/390)) * (D 1), (-3 : S) * (D 1), (-65 : S) * q * (algebraMap ℚ S (1/390)) * (D 0) * (D 1) + (65 : S) * q * i * (algebraMap ℚ S (1/390)) * (D 0) * (D 1) + (-65 : S) * q^3 * (algebraMap ℚ S (1/390)) * (D 0) * (D 1) + (-65 : S) * q^3 * i * (algebraMap ℚ S (1/390)) * (D 0) * (D 1), (5 : S) * (D 0) * (D 1); 0, 0, 0, 0; 0, 0, 0, 0] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck27, ck28, qp] <;> ring

theorem st28 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.add 0 3 (-2/3) : Ev 4 3) * ck28 q i ((algebraMap ℚ S (1/390))) D = ck29 q i ((algebraMap ℚ S (1/390))) D + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![(3 : S) * (D 1) + (-130 : S) * (algebraMap ℚ S (1/390)) * (D 1), (4 : S) * (D 1), (130 : S) * q * (algebraMap ℚ S (1/390)) * (D 0) * (D 1) + (-130 : S) * q * i * (algebraMap ℚ S (1/390)) * (D 0) * (D 1) + (130 : S) * q^3 * (algebraMap ℚ S (1/390)) * (D 0) * (D 1) + (130 : S) * q^3 * i * (algebraMap ℚ S (1/390)) * (D 0) * (D 1), (-5 : S) * (D 0) * (D 1); 0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck28, ck29, qp] <;> ring

theorem st29 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.scale 3 (-1/3) : Ev 4 3) * ck29 q i ((algebraMap ℚ S (1/390))) D = ck30 q i ((algebraMap ℚ S (1/390))) D + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0; (-65 : S) * (algebraMap ℚ S (1/390)) * (D 1), 0, (65 : S) * q * (algebraMap ℚ S (1/390)) * (D 0) * (D 1) + (-65 : S) * q * i * (algebraMap ℚ S (1/390)) * (D 0) * (D 1) + (65 : S) * q^3 * (algebraMap ℚ S (1/390)) * (D 0) * (D 1) + (65 : S) * q^3 * i * (algebraMap ℚ S (1/390)) * (D 0) * (D 1), 0] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck29, ck30, qp] <;> ring

theorem st30 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.add 3 2 (-1) : Ev 4 3) * ck30 q i ((algebraMap ℚ S (1/390))) D = ck31 q i ((algebraMap ℚ S (1/390))) D := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck30, ck31, qp] <;> ring

theorem st31 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.add 1 2 (2) : Ev 4 3) * ck31 q i ((algebraMap ℚ S (1/390))) D = ck32 q i ((algebraMap ℚ S (1/390))) D + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![0, 0, 0, 0; (6 : S) * (D 1), 0, (1 : S) * q * (D 0) * (D 1) + (-1 : S) * q * i * (D 0) * (D 1) + (1 : S) * q^3 * (D 0) * (D 1) + (1 : S) * q^3 * i * (D 0) * (D 1), (-6 : S) * (D 0) * (D 1); 0, 0, 0, 0; 0, 0, 0, 0] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck31, ck32, qp] <;> ring

theorem st32 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.add 0 2 (-1) : Ev 4 3) * ck32 q i ((algebraMap ℚ S (1/390))) D = ck33 q i ((algebraMap ℚ S (1/390))) D + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![0, (-3 : S) * (D 1), (-1 : S) * q * (D 0) * (D 1) + (1 : S) * q * i * (D 0) * (D 1) + (-1 : S) * q^3 * (D 0) * (D 1) + (-1 : S) * q^3 * i * (D 0) * (D 1), (6 : S) * (D 0) * (D 1) + (1 : S) * q * (D 0) * (D 1) + (-1 : S) * q * i * (D 0) * (D 1) + (1 : S) * q^3 * (D 0) * (D 1) + (1 : S) * q^3 * i * (D 0) * (D 1); 0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck32, ck33, qp] <;> ring

theorem st33 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.scale 2 (-1) : Ev 4 3) * ck33 q i ((algebraMap ℚ S (1/390))) D = ck34 q i ((algebraMap ℚ S (1/390))) D := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck33, ck34, qp] <;> ring

theorem st34 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.add 3 1 (2/3) : Ev 4 3) * ck34 q i ((algebraMap ℚ S (1/390))) D = ck35 q i ((algebraMap ℚ S (1/390))) D + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0; (-2 : S) * q * (D 1) + (2 : S) * q * i * (D 1) + (-2 : S) * q^3 * (D 1) + (-2 : S) * q^3 * i * (D 1), 0, (-4 : S) * (D 0) * (D 1) + (1 : S) * q * (D 0) * (D 1) + (-1 : S) * q * i * (D 0) * (D 1) + (1 : S) * q^3 * (D 0) * (D 1) + (1 : S) * q^3 * i * (D 0) * (D 1), (1 : S) * q * (D 0) * (D 1) + (-1 : S) * q * i * (D 0) * (D 1) + (1 : S) * q^3 * (D 0) * (D 1) + (1 : S) * q^3 * i * (D 0) * (D 1)] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck34, ck35, qp] <;> ring

theorem st35 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.add 2 1 (3/4) : Ev 4 3) * ck35 q i ((algebraMap ℚ S (1/390))) D = ck36 q i ((algebraMap ℚ S (1/390))) D + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![0, 0, 0, 0; 0, 0, 0, 0; (1755 : S) * (algebraMap ℚ S (1/390)) * (D 1), (-3 : S) * q * (D 1) + (-1170 : S) * q * (algebraMap ℚ S (1/390)) * (D 1) + (3 : S) * q * i * (D 1) + (1170 : S) * q * i * (algebraMap ℚ S (1/390)) * (D 1) + (-3 : S) * q^3 * (D 1) + (-1170 : S) * q^3 * (algebraMap ℚ S (1/390)) * (D 1) + (-3 : S) * q^3 * i * (D 1) + (-1170 : S) * q^3 * i * (algebraMap ℚ S (1/390)) * (D 1), (-2 : S) * (D 0) * (D 1) + (-1755 : S) * (algebraMap ℚ S (1/390)) * (D 0) * (D 1) + (-65 : S) * q * (algebraMap ℚ S (1/390)) * (D 0) * (D 1) + (65 : S) * q * i * (algebraMap ℚ S (1/390)) * (D 0) * (D 1) + (-65 : S) * q^3 * (algebraMap ℚ S (1/390)) * (D 0) * (D 1) + (-65 : S) * q^3 * i * (algebraMap ℚ S (1/390)) * (D 0) * (D 1), (-1755 : S) * (algebraMap ℚ S (1/390)) * (D 0) * (D 1) + (1 : S) * q * (D 0) * (D 1) + (390 : S) * q * (algebraMap ℚ S (1/390)) * (D 0) * (D 1) + (-1 : S) * q * i * (D 0) * (D 1) + (-390 : S) * q * i * (algebraMap ℚ S (1/390)) * (D 0) * (D 1) + (1 : S) * q^3 * (D 0) * (D 1) + (390 : S) * q^3 * (algebraMap ℚ S (1/390)) * (D 0) * (D 1) + (1 : S) * q^3 * i * (D 0) * (D 1) + (390 : S) * q^3 * i * (algebraMap ℚ S (1/390)) * (D 0) * (D 1); 0, 0, 0, 0] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck35, ck36, qp] <;> ring

end steps
end CallerQZero
