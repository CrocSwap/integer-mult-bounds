/-
CallerWordS (lane CALLERWORD, Nov 20).  SUPPORT of the stage-frame columns of a legal caller word.
A HOST event j (fields s ≠ t) whose two fields are D_t0-multiplied right after (the J record of type B: `jB`)
has every A and B column supported on E_t0 = {r : t0 ∈ mask r}: role r meets stage t0 in the frame
(maskOf A B) only if t0 ∈ mask r (the D-mask of the target).  This is the `hbh`/`hah` hypothesis of
CallerRC2 / CallerHP with M = the caller's D-masks.
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Mathlib.Tactic.LinearCombination
import Nov15.CallerWordD

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace CallerWord
open Matrix Finset CallerSign

section supp
variable {n k : ℕ} (w : CWord n k) (t0 : Fin k)

theorem E1_mul_apply (x y : Fin n) (c : ℂ) (P : Matrix (Fin n) (Fin n) ℂ) (r' r : Fin n) :
    (E1 x y c * P) r' r = if r' = x then c * P y r else 0 := by
  simp only [Matrix.mul_apply, E1, Matrix.of_apply]
  by_cases h : r' = x
  · simp [h]
  · simp [h]

variable (hb : replay (1 : ℂ) Complex.I 1 w.evs = 1) (hL : LegalAt (1 : DN) iD (Dt t0) w)
include hb hL

/-- generic form: the HOST's field rows/columns of P1(j+1) are incidence vectors of stage t0. -/
theorem host_cols (j : Fin w.evs.length) (s t : Fin n) (a b : ℚ) (hj : w.evs.get j = Ev.host s t a b)
    (hst : s ≠ t) (es et : Inc w t0)
    (hVs : ∀ r, (P1 w Complex.I (j.val + 1))⁻¹ r s = incV w t0 r es)
    (hVt : ∀ r, (P1 w Complex.I (j.val + 1))⁻¹ r t = incV w t0 r et)
    (hWs : ∀ r, P1 w Complex.I (j.val + 1) s r = incW w t0 r es)
    (hWt : ∀ r, P1 w Complex.I (j.val + 1) t r = incW w t0 r et)
    (r : Fin n) (hr : t0 ∉ w.mask r) (p : Iota w) (hp : p.1.1 = j) :
    Aw w Complex.I r p = 0 ∧ Bw w Complex.I r p = 0 := by
  have sVs := (support_VW w t0 hb hL r hr es).1
  have sVt := (support_VW w t0 hb hL r hr et).1
  have sWs := (support_VW w t0 hb hL r hr es).2
  have sWt := (support_VW w t0 hb hL r hr et).2
  have hP : P1 w Complex.I (j.val + 1) = evMat (1 : ℂ) Complex.I (1 : Fin k → ℂ) (Ev.host s t a b : Ev n k) * P1 w Complex.I j.val := by
    unfold P1; rw [pre_succ, evAt_get w _ 1 1 j.val j.isLt, hj]
  have e1 := congrFun (congrFun hP s) r
  have e2 := congrFun (congrFun hP t) r
  simp only [evMat, Matrix.add_mul, Matrix.one_mul, Matrix.add_apply, E1_mul_apply, hst, hst.symm,
    if_true, if_false, add_zero, mul_one, one_pow, map_mul] at e1 e2
  rw [hWs, sWs] at e1
  rw [hWt, sWt] at e2
  have z1 : P1 w Complex.I j.val t r = 0 := by linear_combination -e2 + algebraMap ℚ ℂ b * e1
  have z0 : P1 w Complex.I j.val s r = 0 := by
    linear_combination -e1 - algebraMap ℚ ℂ a * (-e2 + algebraMap ℚ ℂ b * e1)
  obtain ⟨⟨j', c⟩, hc⟩ := p
  simp only at hp
  subst hp
  have htm : tm w (j', c) = terms (Ev.host s t a b : Ev n k) c := by unfold tm; rw [hj]
  fin_cases c
  · simp only [Aw, Bw, Matrix.of_apply, htm, terms]
    show (P1 w Complex.I (j'.val + 1))⁻¹ r s * algebraMap ℚ ℂ (-2 * a) = 0 ∧ P1 w Complex.I j'.val t r = 0
    rw [hVs, sVs]; simp [z1]
  · simp only [Aw, Bw, Matrix.of_apply, htm, terms]
    show (P1 w Complex.I (j'.val + 1))⁻¹ r t * algebraMap ℚ ℂ (-2 * b) = 0 ∧ P1 w Complex.I j'.val s r = 0
    rw [hVt, sVt]; simp [z0]

/-- the J record of type B: HOST(s,t,a,b) then IDLE s {t0}, IDLE t {t0}.  Every frame column of that HOST is
    supported on E_t0 (A and B rows vanish on roles whose D-mask misses t0). -/
theorem jB_cols (j : ℕ) (hj2 : j + 2 < w.evs.length) (s t : Fin n) (a b : ℚ) (hst : s ≠ t)
    (h0 : w.evs.get ⟨j, by omega⟩ = Ev.host s t a b)
    (h1 : w.evs.get ⟨j + 1, by omega⟩ = Ev.idle s {t0} 0)
    (h2 : w.evs.get ⟨j + 2, hj2⟩ = Ev.idle t {t0} 0)
    (r : Fin n) (hr : t0 ∉ w.mask r) (p : Iota w) (hp : p.1.1.val = j) :
    Aw w Complex.I r p = 0 ∧ Bw w Complex.I r p = 0 := by
  have hi1 : inc t0 (w.evs.get ⟨j + 1, by omega⟩) = true := by rw [h1]; simp [inc]
  have hi2 : inc t0 (w.evs.get ⟨j + 2, hj2⟩) = true := by rw [h2]; simp [inc]
  have h1' : w.evs[j + 1]'(by omega) = Ev.idle s {t0} 0 := by simpa using h1
  have h2' : w.evs[j + 2]'hj2 = Ev.idle t {t0} 0 := by simpa using h2
  have hP2 : P1 w Complex.I (j + 2) = P1 w Complex.I (j + 1) := by
    unfold P1; rw [pre_succ, evAt_get w _ 1 1 (j + 1) (by omega), h1, idle_base, Matrix.one_mul]
  refine host_cols w t0 hb hL ⟨j, by omega⟩ s t a b h0 hst ⟨_, hi1⟩ ⟨_, hi2⟩ ?_ ?_ ?_ ?_ r hr p
    (Fin.ext hp)
  · intro r'; simp [incV, h1', reg]
  · intro r'; simp [incV, h2', reg, hP2]
  · intro r'; simp [incW, h1', reg]
  · intro r'; simp [incW, h2', reg, hP2]

end supp

/-- headline (support, from SPEC legality): for every legal word, every J record of type B at stage t0 gives
    frame columns supported on E_t0. -/
theorem legal_jB_support {n k : ℕ} (w : CWord n k) (hL : Legal w) (t0 : Fin k) (j : ℕ)
    (hj2 : j + 2 < w.evs.length) (s t : Fin n) (a b : ℚ) (hst : s ≠ t)
    (h0 : w.evs.get ⟨j, by omega⟩ = Ev.host s t a b)
    (h1 : w.evs.get ⟨j + 1, by omega⟩ = Ev.idle s {t0} 0)
    (h2 : w.evs.get ⟨j + 2, hj2⟩ = Ev.idle t {t0} 0)
    (r : Fin n) (hr : t0 ∉ w.mask r) (p : Iota w) (hp : p.1.1.val = j) :
    Aw w Complex.I r p = 0 ∧ Bw w Complex.I r p = 0 := by
  obtain ⟨hL', hb⟩ := legal_dn w hL t0
  exact jB_cols w t0 hb hL' j hj2 s t a b hst h0 h1 h2 r hr p hp

/-! non-vacuity: 3 roles, role 2 outside stage 0 (mask ∅, only IDLE_ODD); the J record of type B at j = 0. -/
def toy3 : CWord 3 1 where
  evs := [.host 0 1 0 1, .idle 0 {0} 0, .idle 1 {0} 0, .scale 1 (-1), .query 1 0 (-1), .scale 1 (-1),
          .idle 0 ∅ (-1), .idle 1 ∅ (-1), .idle 2 ∅ (-1)]
  ex := fun _ => -1
  mask := fun r => if r = 2 then ∅ else {0}

set_option maxHeartbeats 4000000 in
theorem toy3_legal : Legal toy3 := by
  refine ⟨?_, ?_⟩
  · intro e he s t a b h
    subst h
    simp [toy3] at he
    rcases he with ⟨rfl, rfl, -, -⟩
    decide
  · intro S _ _ q i D hq hi
    unfold LegalAt replay pre target toy3
    ext r r'
    fin_cases r <;> fin_cases r' <;>
      simp [evMat, E1, qp, Matrix.mul_apply, Fin.sum_univ_three, Matrix.diagonal] <;> ring

/-- role 2 (D-mask ∅) has zero A and B rows on every column of the stage-0 HOST. -/
theorem toy3_support (p : Iota toy3) (hp : p.1.1.val = 0) :
    Aw toy3 Complex.I 2 p = 0 ∧ Bw toy3 Complex.I 2 p = 0 :=
  legal_jB_support toy3 toy3_legal 0 0 (by decide) 0 1 0 1 (by decide) rfl rfl rfl 2 (by decide) p hp

end CallerWord

#print axioms CallerWord.toy3_support
#print axioms CallerWord.host_cols
#print axioms CallerWord.jB_cols
#print axioms CallerWord.legal_jB_support
