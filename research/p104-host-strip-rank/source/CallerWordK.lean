/-
CallerWordK (lane CALLERWORD, Nov 20).  The KERNEL law of CallerRC2.Pieces (`x_ker`) derived for legal words:
for a type-B J record at stage t0 (HOST(s,t,a,b) at j, contacts IDLE s {t0}, IDLE t {t0} at j+1, j+2) and ANY other
D_t0-incidence e (e.g. a multi-stage idle piece containing t0),  Σ_r v_e(r) * B(r, p) = 0  for every frame column p of
that HOST.  Proof: the HOST's B rows are combinations of the contacts' w-vectors (host_rows), and W^T V = 1.
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Mathlib.Tactic.LinearCombination
import Nov15.CallerWordS

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace CallerWord
open Matrix Finset CallerSign

section ker
variable {n k : ℕ} (w : CWord n k) (t0 : Fin k)

/-- rows of the pre-HOST prefix in terms of the post-HOST prefix. -/
theorem host_rows (j : Fin w.evs.length) (s t : Fin n) (a b : ℚ) (hj : w.evs.get j = Ev.host s t a b)
    (hst : s ≠ t) (r : Fin n) :
    P1 w Complex.I j.val t r = P1 w Complex.I (j.val + 1) t r - algebraMap ℚ ℂ b * P1 w Complex.I (j.val + 1) s r ∧
    P1 w Complex.I j.val s r = (1 + algebraMap ℚ ℂ a * algebraMap ℚ ℂ b) * P1 w Complex.I (j.val + 1) s r
      - algebraMap ℚ ℂ a * P1 w Complex.I (j.val + 1) t r := by
  have hP : P1 w Complex.I (j.val + 1) = evMat (1 : ℂ) Complex.I (1 : Fin k → ℂ) (Ev.host s t a b : Ev n k)
      * P1 w Complex.I j.val := by
    unfold P1; rw [pre_succ, evAt_get w _ 1 1 j.val j.isLt, hj]
  have e1 := congrFun (congrFun hP s) r
  have e2 := congrFun (congrFun hP t) r
  simp only [evMat, Matrix.add_mul, Matrix.one_mul, Matrix.add_apply, E1_mul_apply, hst, hst.symm,
    if_true, if_false, add_zero, mul_one, one_pow, map_mul] at e1 e2
  constructor
  · linear_combination -e2 + algebraMap ℚ ℂ b * e1
  · linear_combination (-1 - algebraMap ℚ ℂ a * algebraMap ℚ ℂ b) * e1 + algebraMap ℚ ℂ a * e2

variable (hb : replay (1 : ℂ) Complex.I 1 w.evs = 1) (hL : LegalAt (1 : DN) iD (Dt t0) w)
include hb hL

theorem jB_xker (j : ℕ) (hj2 : j + 2 < w.evs.length) (s t : Fin n) (a b : ℚ) (hst : s ≠ t)
    (h0 : w.evs.get ⟨j, by omega⟩ = Ev.host s t a b)
    (h1 : w.evs.get ⟨j + 1, by omega⟩ = Ev.idle s {t0} 0)
    (h2 : w.evs.get ⟨j + 2, hj2⟩ = Ev.idle t {t0} 0)
    (e : Inc w t0) (he1 : e.1.val ≠ j + 1) (he2 : e.1.val ≠ j + 2)
    (p : Iota w) (hp : p.1.1.val = j) :
    ∑ r, incV w t0 r e * Bw w Complex.I r p = 0 := by
  have g1 : w.evs[j + 1]'(by omega) = Ev.idle s {t0} 0 := by simpa using h1
  have g2 : w.evs[j + 2]'hj2 = Ev.idle t {t0} 0 := by simpa using h2
  have i1 : inc t0 (w.evs.get ⟨j + 1, by omega⟩) = true := by rw [h1]; simp [inc]
  have i2 : inc t0 (w.evs.get ⟨j + 2, hj2⟩) = true := by rw [h2]; simp [inc]
  have hP2 : P1 w Complex.I (j + 2) = P1 w Complex.I (j + 1) := by
    unfold P1; rw [pre_succ, evAt_get w _ 1 1 (j + 1) (by omega), h1, idle_base, Matrix.one_mul]
  have hbi := (biorth w t0 hb hL).1
  let cs : Inc w t0 := ⟨_, i1⟩
  let ct : Inc w t0 := ⟨_, i2⟩
  have hne_s : cs ≠ e := by intro h; apply he1; rw [← h]
  have hne_t : ct ≠ e := by intro h; apply he2; rw [← h]
  -- Σ_r v_e(r) P1(j+1) s r = (W^T V)_{cs,e} = 0, same for t
  have zs : ∑ r, incV w t0 r e * P1 w Complex.I (j + 1) s r = 0 := by
    have := congrFun (congrFun hbi cs) e
    rw [Matrix.one_apply_ne hne_s] at this
    rw [← this]; simp only [Matrix.mul_apply, Matrix.transpose_apply, incW, Matrix.of_apply]
    refine Finset.sum_congr rfl fun r _ => ?_
    simp [cs, g1, reg, mul_comm]
  have zt : ∑ r, incV w t0 r e * P1 w Complex.I (j + 1) t r = 0 := by
    have := congrFun (congrFun hbi ct) e
    rw [Matrix.one_apply_ne hne_t] at this
    rw [← this]; simp only [Matrix.mul_apply, Matrix.transpose_apply, incW, Matrix.of_apply]
    refine Finset.sum_congr rfl fun r _ => ?_
    simp [ct, g2, reg, hP2, mul_comm]
  obtain ⟨jF, hjF⟩ : ∃ jF : Fin w.evs.length, jF.val = j := ⟨⟨j, by omega⟩, rfl⟩
  have h0' : w.evs.get jF = Ev.host s t a b := by
    have : jF = ⟨j, by omega⟩ := Fin.ext hjF
    rw [this]; exact h0
  have hr := host_rows w jF s t a b h0' hst
  rw [hjF] at hr
  obtain ⟨⟨j', c⟩, hc⟩ := p
  simp only at hp
  have hj' : j' = jF := Fin.ext (hp.trans hjF.symm)
  subst hj'
  have htm : tm w (j', c) = terms (Ev.host s t a b : Ev n k) c := by unfold tm; rw [h0']
  fin_cases c
  · simp only [Bw, Matrix.of_apply, htm, terms]
    show ∑ r, incV w t0 r e * P1 w Complex.I j'.val t r = 0
    rw [hjF]
    simp_rw [fun r => (hr r).1, mul_sub, Finset.sum_sub_distrib]
    rw [zt]
    simp_rw [mul_left_comm (incV w t0 _ e), ← Finset.mul_sum, zs]; simp
  · simp only [Bw, Matrix.of_apply, htm, terms]
    show ∑ r, incV w t0 r e * P1 w Complex.I j'.val s r = 0
    rw [hjF]
    simp_rw [fun r => (hr r).2, mul_sub, Finset.sum_sub_distrib]
    simp_rw [mul_left_comm (incV w t0 _ e), ← Finset.mul_sum, zs, zt]; simp

end ker
end CallerWord

#print axioms CallerWord.host_rows
#print axioms CallerWord.jB_xker
