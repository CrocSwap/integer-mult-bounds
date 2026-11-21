/-
EasyWireK (lane EASYWIRE, Nov 20).  The stage K-block of a type-B J record is determined by its two HOST coefficients:
  (sgK ...).submatrix (J.col s) (J.col s)  =  [[2+2ab, -2b], [-2a(1+ab), 2+2ab]],   det = 4 (1 + a b).
Hence `hlam` (every stage K-block invertible; "lambda /= -1") is equivalent to  a_s b_s /= -1  for every stage, for ANY legal
type-B word (only `LegalAt 1` is used).  Proof: G_ss(c,c') = coef_c' * (P1(j) P1(j+1)^-1)(y_c, x_c'), and host_rows
turns the rows of P1(j) into rows of P1(j+1).
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Nov15.CallerAsm
import Nov15.CallerWordK

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace EasyWire
open Matrix Finset CallerSign CallerWord CallerAsm

variable {n k : ℕ} {w : CWord n k}

theorem hostsum (hb : replay (1 : ℂ) Complex.I 1 w.evs = 1) (j : Fin w.evs.length) (s t : Fin n) (a b : ℚ)
    (hj : w.evs.get j = Ev.host s t a b) (hst : s ≠ t) (x : Fin n) :
    (∑ r, P1 w Complex.I j.val t r * (P1 w Complex.I (j.val + 1))⁻¹ r x
        = (if t = x then 1 else 0) - algebraMap ℚ ℂ b * (if s = x then 1 else 0)) ∧
    (∑ r, P1 w Complex.I j.val s r * (P1 w Complex.I (j.val + 1))⁻¹ r x
        = (1 + algebraMap ℚ ℂ a * algebraMap ℚ ℂ b) * (if s = x then 1 else 0)
          - algebraMap ℚ ℂ a * (if t = x then 1 else 0)) := by
  have hX : IsUnit (P1 w Complex.I (j.val + 1)).det :=
    isUnit_iff_ne_zero.mpr (det_P1_ne w Complex.I hb _ (by have := j.isLt; omega))
  have hI := Matrix.mul_nonsing_inv _ hX
  have e : ∀ y, ∑ r, P1 w Complex.I (j.val + 1) y r * (P1 w Complex.I (j.val + 1))⁻¹ r x
      = if y = x then 1 else 0 := by
    intro y
    have := congrFun (congrFun hI y) x
    simpa [Matrix.mul_apply, Matrix.one_apply] using this
  constructor
  · calc _ = ∑ r, (P1 w Complex.I (j.val + 1) t r * (P1 w Complex.I (j.val + 1))⁻¹ r x
          - algebraMap ℚ ℂ b * (P1 w Complex.I (j.val + 1) s r * (P1 w Complex.I (j.val + 1))⁻¹ r x)) := by
          refine Finset.sum_congr rfl fun r _ => ?_
          rw [(host_rows w j s t a b hj hst r).1]; ring
      _ = _ := by rw [Finset.sum_sub_distrib, ← Finset.mul_sum, e t, e s]
  · calc _ = ∑ r, ((1 + algebraMap ℚ ℂ a * algebraMap ℚ ℂ b) *
            (P1 w Complex.I (j.val + 1) s r * (P1 w Complex.I (j.val + 1))⁻¹ r x)
          - algebraMap ℚ ℂ a * (P1 w Complex.I (j.val + 1) t r * (P1 w Complex.I (j.val + 1))⁻¹ r x)) := by
          refine Finset.sum_congr rfl fun r _ => ?_
          rw [(host_rows w j s t a b hj hst r).2]; ring
      _ = _ := by rw [Finset.sum_sub_distrib, ← Finset.mul_sum, ← Finset.mul_sum, e t, e s]

theorem G_gen (J : JB w) (s : Fin k) (c c' : Fin 2) :
    sgG (Aw w Complex.I) (Bw w Complex.I) (J.col s c) (J.col s c') =
      algebraMap ℚ ℂ (terms (w.evs.get ⟨J.pos s, by have := J.lt s; omega⟩) c').2.2 *
      ∑ r, P1 w Complex.I (J.pos s) (terms (w.evs.get ⟨J.pos s, by have := J.lt s; omega⟩) c).2.1 r *
        (P1 w Complex.I (J.pos s + 1))⁻¹ r (terms (w.evs.get ⟨J.pos s, by have := J.lt s; omega⟩) c').1 := by
  unfold sgG
  rw [Matrix.mul_apply, Finset.mul_sum]
  refine Finset.sum_congr rfl fun r _ => ?_
  show P1 w Complex.I (J.pos s) (terms (w.evs.get ⟨J.pos s, by have := J.lt s; omega⟩) c).2.1 r *
      ((P1 w Complex.I (J.pos s + 1))⁻¹ r (terms (w.evs.get ⟨J.pos s, by have := J.lt s; omega⟩) c').1 *
        algebraMap ℚ ℂ (terms (w.evs.get ⟨J.pos s, by have := J.lt s; omega⟩) c').2.2) = _
  ring

theorem sgK_same {ι : Type*} [Fintype ι] [DecidableEq ι] (β : ι → ℕ) (G : Matrix ι ι ℂ) (i j : ι)
    (h : β i = β j) : sgK β G i j = (if i = j then 2 else 0) + G i j := by
  unfold sgK sgDiag sgUp sgLow
  simp only [Matrix.add_apply, Matrix.sub_apply, Matrix.smul_apply, Matrix.one_apply, Matrix.of_apply, h,
    lt_irrefl, if_false, if_true]
  by_cases hij : i = j <;> simp [hij]

theorem col_ne (J : JB w) (s : Fin k) : J.col s 0 ≠ J.col s 1 := by
  intro h
  have := congrArg (fun p : Iota w => p.1.2) h
  simp [JB.col] at this

/-- the K-block of a type-B record: determinant `4 (1 + a b)`. -/
theorem kblock_det (hb : replay (1 : ℂ) Complex.I 1 w.evs = 1) (J : JB w) (s : Fin k) :
    ((sgK (βw w) (sgG (Aw w Complex.I) (Bw w Complex.I))).submatrix (J.col s) (J.col s)).det
      = 4 * (1 + algebraMap ℚ ℂ (J.a s) * algebraMap ℚ ℂ (J.b s)) := by
  have hj := J.h0 s
  have hst := J.uv s
  have hsum := hostsum hb ⟨J.pos s, by have := J.lt s; omega⟩ (J.u s) (J.v s) (J.a s) (J.b s) hj hst
  have hβ : ∀ c c', βw w (J.col s c) = βw w (J.col s c') := fun c c' => rfl
  have e00 : sgG (Aw w Complex.I) (Bw w Complex.I) (J.col s 0) (J.col s 0)
      = 2 * (algebraMap ℚ ℂ (J.a s) * algebraMap ℚ ℂ (J.b s)) := by
    rw [G_gen, hj]
    simp only [terms, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons]
    rw [(hsum (J.u s)).1]
    simp [hst, hst.symm]; ring
  have e01 : sgG (Aw w Complex.I) (Bw w Complex.I) (J.col s 0) (J.col s 1)
      = -2 * algebraMap ℚ ℂ (J.b s) := by
    rw [G_gen, hj]
    simp only [terms, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons]
    rw [(hsum (J.v s)).1]
    simp [hst, hst.symm]
  have e10 : sgG (Aw w Complex.I) (Bw w Complex.I) (J.col s 1) (J.col s 0)
      = -2 * algebraMap ℚ ℂ (J.a s) * (1 + algebraMap ℚ ℂ (J.a s) * algebraMap ℚ ℂ (J.b s)) := by
    rw [G_gen, hj]
    simp only [terms, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons]
    rw [(hsum (J.u s)).2]
    simp [hst, hst.symm]
  have e11 : sgG (Aw w Complex.I) (Bw w Complex.I) (J.col s 1) (J.col s 1)
      = 2 * (algebraMap ℚ ℂ (J.a s) * algebraMap ℚ ℂ (J.b s)) := by
    rw [G_gen, hj]
    simp only [terms, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons]
    rw [(hsum (J.v s)).2]
    simp [hst, hst.symm]; ring
  rw [Matrix.det_fin_two]
  simp only [Matrix.submatrix_apply]
  rw [sgK_same _ _ _ _ (hβ _ _), sgK_same _ _ _ _ (hβ _ _), sgK_same _ _ _ _ (hβ _ _), sgK_same _ _ _ _ (hβ _ _),
    e00, e01, e10, e11]
  have n01 : J.col s 0 ≠ J.col s 1 := col_ne J s
  simp [n01, n01.symm]
  ring

/-- `hlam` for every type-B word: it is exactly `a_s b_s /= -1`. -/
theorem hlam_of_ab (hL : Legal w) (J : JB w) (hab : ∀ s, J.a s * J.b s ≠ -1) :
    ∀ s, IsUnit ((sgK (βw w) (sgG (Aw w Complex.I) (Bw w Complex.I))).submatrix (J.col s) (J.col s)).det := by
  intro s
  have hb : replay (1 : ℂ) Complex.I 1 w.evs = 1 := by
    have h1 := (legal_pm w hL).1
    unfold LegalAt at h1
    rw [h1]; unfold target; simp [one_qp]
  rw [kblock_det hb J s]
  have h1 : (1 + algebraMap ℚ ℂ (J.a s) * algebraMap ℚ ℂ (J.b s) : ℂ) ≠ 0 := by
    intro h
    apply hab s
    have : algebraMap ℚ ℂ (J.a s * J.b s + 1) = 0 := by simp only [map_add, map_mul, map_one]; linear_combination h
    have h2 := (map_eq_zero_iff (algebraMap ℚ ℂ) (algebraMap ℚ ℂ).injective).1 this
    linarith
  exact isUnit_iff_ne_zero.mpr (mul_ne_zero (by norm_num) h1)

theorem hlam_iff_ab (hL : Legal w) (J : JB w) (s : Fin k) :
    IsUnit ((sgK (βw w) (sgG (Aw w Complex.I) (Bw w Complex.I))).submatrix (J.col s) (J.col s)).det
      ↔ J.a s * J.b s ≠ -1 := by
  have hb : replay (1 : ℂ) Complex.I 1 w.evs = 1 := by
    have h1 := (legal_pm w hL).1
    unfold LegalAt at h1
    rw [h1]; unfold target; simp [one_qp]
  rw [kblock_det hb J s, isUnit_iff_ne_zero]
  constructor
  · intro h hab
    apply h
    have : (algebraMap ℚ ℂ (J.a s * J.b s + 1)) = 0 := by rw [hab]; simp
    simp only [map_add, map_mul, map_one] at this
    linear_combination 4 * this
  · intro h h0
    apply h
    have h1 : (1 + algebraMap ℚ ℂ (J.a s) * algebraMap ℚ ℂ (J.b s) : ℂ) = 0 := by
      rcases mul_eq_zero.1 h0 with h4 | h4
      · exact absurd h4 (by norm_num)
      · exact h4
    have : algebraMap ℚ ℂ (J.a s * J.b s + 1) = 0 := by simp only [map_add, map_mul, map_one]; linear_combination h1
    have h2 := (map_eq_zero_iff (algebraMap ℚ ℂ) (algebraMap ℚ ℂ).injective).1 this
    linarith

end EasyWire

#print axioms EasyWire.hostsum
#print axioms EasyWire.kblock_det
#print axioms EasyWire.hlam_of_ab
#print axioms EasyWire.hlam_iff_ab
