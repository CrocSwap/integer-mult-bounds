/- CallerQZero checkpoint steps, chunk 0. -/
import Nov15.CallerQZeroD
set_option linter.unusedSectionVars false
set_option linter.unusedVariables false
set_option maxHeartbeats 4000000
set_option linter.unusedSimpArgs false
namespace CallerQZero
open Matrix CallerWord
section steps
variable {S : Type} [CommRing S] [Algebra ℚ S]

theorem st0 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.lam 3 (-1) : Ev 4 3) * ck0 q i ((algebraMap ℚ S (1/390))) D = ck1 q i ((algebraMap ℚ S (1/390))) D := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck0, ck1, qp] <;> ring

theorem st1 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.host 2 3 (-1) (1/2) : Ev 4 3) * ck1 q i ((algebraMap ℚ S (1/390))) D = ck2 q i ((algebraMap ℚ S (1/390))) D + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, (-195 : S) * (algebraMap ℚ S (1/390)) + (195 : S) * i * (algebraMap ℚ S (1/390)) + (-195 : S) * q^2 * (algebraMap ℚ S (1/390)) + (-195 : S) * q^2 * i * (algebraMap ℚ S (1/390))] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck1, ck2, qp] <;> ring

theorem st2 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.idle 2 {0} 0 : Ev 4 3) * ck2 q i ((algebraMap ℚ S (1/390))) D = ck3 q i ((algebraMap ℚ S (1/390))) D := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck2, ck3, qp] <;> ring

theorem st3 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.idle 3 {0} 0 : Ev 4 3) * ck3 q i ((algebraMap ℚ S (1/390))) D = ck4 q i ((algebraMap ℚ S (1/390))) D := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck3, ck4, qp] <;> ring

theorem st4 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.lam 3 (1) : Ev 4 3) * ck4 q i ((algebraMap ℚ S (1/390))) D = ck5 q i ((algebraMap ℚ S (1/390))) D + (q ^ 4 - 1) • !![0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0; 0, 0, (38025 : S) * q * (algebraMap ℚ S (1/390))^2 * (D 0) + (-38025 : S) * q * i * (algebraMap ℚ S (1/390))^2 * (D 0), (7414875 : S) * (algebraMap ℚ S (1/390))^3 * (D 0) + (-7414875 : S) * i^2 * (algebraMap ℚ S (1/390))^3 * (D 0)] + (i ^ 2 + 1) • !![0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, (-14829750 : S) * (algebraMap ℚ S (1/390))^3 * (D 0) + (14829750 : S) * q^2 * (algebraMap ℚ S (1/390))^3 * (D 0)] + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, (195 : S) * (algebraMap ℚ S (1/390)) * (D 0) + (76050 : S) * (algebraMap ℚ S (1/390))^2 * (D 0)] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck4, ck5, qp] <;> ring

theorem st5 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.add 1 3 (-1/5) : Ev 4 3) * ck5 q i ((algebraMap ℚ S (1/390))) D = ck6 q i ((algebraMap ℚ S (1/390))) D + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![0, 0, 0, 0; 0, 0, (-7605 : S) * q * (algebraMap ℚ S (1/390))^2 * (D 0) + (7605 : S) * q * i * (algebraMap ℚ S (1/390))^2 * (D 0) + (-7605 : S) * q^3 * (algebraMap ℚ S (1/390))^2 * (D 0) + (-7605 : S) * q^3 * i * (algebraMap ℚ S (1/390))^2 * (D 0), (-39 : S) * (algebraMap ℚ S (1/390)) * (D 0); 0, 0, 0, 0; 0, 0, 0, 0] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck5, ck6, qp] <;> ring

theorem st6 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.add 0 3 (-2/5) : Ev 4 3) * ck6 q i ((algebraMap ℚ S (1/390))) D = ck7 q i ((algebraMap ℚ S (1/390))) D + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![0, 0, (-39 : S) * q * (algebraMap ℚ S (1/390)) * (D 0) + (-15210 : S) * q * (algebraMap ℚ S (1/390))^2 * (D 0) + (39 : S) * q * i * (algebraMap ℚ S (1/390)) * (D 0) + (15210 : S) * q * i * (algebraMap ℚ S (1/390))^2 * (D 0) + (-39 : S) * q^3 * (algebraMap ℚ S (1/390)) * (D 0) + (-15210 : S) * q^3 * (algebraMap ℚ S (1/390))^2 * (D 0) + (-39 : S) * q^3 * i * (algebraMap ℚ S (1/390)) * (D 0) + (-15210 : S) * q^3 * i * (algebraMap ℚ S (1/390))^2 * (D 0), (-78 : S) * (algebraMap ℚ S (1/390)) * (D 0); 0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck6, ck7, qp] <;> ring

theorem st7 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.scale 3 (-8/5) : Ev 4 3) * ck7 q i ((algebraMap ℚ S (1/390))) D = ck8 q i ((algebraMap ℚ S (1/390))) D + ((390 : S) * (algebraMap ℚ S (1/390)) - 1) • !![0, 0, 0, 0; 0, 0, 0, 0; 0, 0, 0, 0; 0, 0, (-156 : S) * q * (algebraMap ℚ S (1/390)) * (D 0) + (-60840 : S) * q * (algebraMap ℚ S (1/390))^2 * (D 0) + (156 : S) * q * i * (algebraMap ℚ S (1/390)) * (D 0) + (60840 : S) * q * i * (algebraMap ℚ S (1/390))^2 * (D 0) + (-156 : S) * q^3 * (algebraMap ℚ S (1/390)) * (D 0) + (-60840 : S) * q^3 * (algebraMap ℚ S (1/390))^2 * (D 0) + (-156 : S) * q^3 * i * (algebraMap ℚ S (1/390)) * (D 0) + (-60840 : S) * q^3 * i * (algebraMap ℚ S (1/390))^2 * (D 0), (-312 : S) * (algebraMap ℚ S (1/390)) * (D 0)] := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck7, ck8, qp] <;> ring

theorem st8 (q i : S) (D : Fin 3 → S) :
    evMat q i D (.add 1 2 (1) : Ev 4 3) * ck8 q i ((algebraMap ℚ S (1/390))) D = ck9 q i ((algebraMap ℚ S (1/390))) D := by
  simp only [evMat, k0, k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20, k21, k22, k23, k24, k25, k26, k27, k28, k29, k30, k31, k32, k33, k34, k35, k36, k37, k38, k39, khalf]
  ext r c; fin_cases r <;> fin_cases c <;>
    simp [E1, Matrix.mul_apply, Fin.sum_univ_four, Matrix.one_apply, ck8, ck9, qp] <;> ring

end steps
end CallerQZero
