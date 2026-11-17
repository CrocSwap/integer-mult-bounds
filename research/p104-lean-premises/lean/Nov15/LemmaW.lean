/-
LEMMA W (BORROW R12 §2; ).  Caller stage model of CallerBorrow.lean:
units T_s = 1 - 2 x_s y_s^T, prefix `pp s = T_{s-1}...T_0`, mask projector `pm m`.
Thin units u_j = a+j (j<k) sit between the cut prefix A = pp a and the stage R at index a+k with mask m = m_R.
Q_{j-1} = pp (a+j), pulled-back covector w_j = y_{a+j}^T Q_{j-1} = `y (a+j) ᵥ* pp (a+j)`.
-/
import Nov15.CallerBorrow

open Matrix

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false
set_option linter.unusedSimpArgs false
set_option linter.unusedTactic false

namespace LemmaW
open CallerBorrow

variable {ι : Type*} [Fintype ι] [DecidableEq ι] {K : Type*} [Field K]
variable (m : ι → Prop) [DecidablePred m]

/-- entrywise unit step: `pp (s+1) r c = pp s r c - 2 x_s r (y_s^T pp s) c` -/
theorem pp_succ_entry (x y : ℕ → ι → K) (s : ℕ) (r c : ι) :
    pp x y (s + 1) r c = pp x y s r c - 2 * (x s r * (y s ᵥ* pp x y s) c) := by
  have : pp x y (s + 1) = pp x y s - (2 : K) • vecMulVec (x s) (y s ᵥ* pp x y s) := by
    rw [pp, unitM, sub_mul, one_mul, smul_mul_assoc, Matrix.vecMulVec_mul]
  rw [this]; simp [vecMulVec_apply]

/-- telescoped entry formula over the thin window `a ≤ s < a+k` -/
theorem pp_window_entry (x y : ℕ → ι → K) (a k : ℕ) (r c : ι) :
    pp x y (a + k) r c =
      pp x y a r c - 2 * ∑ j ∈ Finset.range k, x (a + j) r * (y (a + j) ᵥ* pp x y (a + j)) c := by
  induction k with
  | zero => simp
  | succ k ih =>
    rw [← add_assoc, pp_succ_entry, ih, Finset.sum_range_succ]; ring

/-- a matrix commuting with `pm m` has no entry from a masked-in column to a masked-out row. -/
theorem entry_zero_of_commute {M : Matrix ι ι K} (h : Commute (pm m) M) {r c : ι}
    (hr : ¬ m r) (hc : m c) : M r c = 0 := by
  have := congrFun (congrFun h.eq r) c
  simp only [pm, Matrix.diagonal_mul, Matrix.mul_diagonal, hr, hc, if_true, if_false] at this
  simpa using this.symm

/-- **Lemma W, exact form (no commutation of A needed).**  If the prefix before the stage commutes with
`pm m`, then for a role `r ∉ m` and `c ∈ m`:  `2 Σ_j x_{a+j}[r] (y_{a+j}^T Q_{j-1})[c] = A[r,c]`. -/
theorem lemmaW_defect (x y : ℕ → ι → K) (a k : ℕ)
    (hcomm : Commute (pm m) (pp x y (a + k))) {r c : ι} (hr : ¬ m r) (hc : m c) :
    2 * ∑ j ∈ Finset.range k, x (a + j) r * (y (a + j) ᵥ* pp x y (a + j)) c = pp x y a r c := by
  have h0 := entry_zero_of_commute m hcomm hr hc
  have h1 := pp_window_entry x y a k r c
  rw [h0] at h1
  linear_combination h1

/-- **LEMMA W (i).**  If moreover the cut prefix `A = pp a` commutes with `pm m` ("R untouched before"),
and `2 ≠ 0`: `Σ_j x_{a+j}[r] (y_{a+j}^T Q_{j-1})|_m = 0` for every borrowed role `r ∉ m`. -/
theorem lemmaW (x y : ℕ → ι → K) (a k : ℕ) (h2 : (2 : K) ≠ 0)
    (hA : Commute (pm m) (pp x y a)) (hcomm : Commute (pm m) (pp x y (a + k)))
    {r c : ι} (hr : ¬ m r) (hc : m c) :
    ∑ j ∈ Finset.range k, x (a + j) r * (y (a + j) ᵥ* pp x y (a + j)) c = 0 := by
  have h := lemmaW_defect m x y a k hcomm hr hc
  rw [entry_zero_of_commute m hA hr hc] at h
  exact (mul_eq_zero.1 h).resolve_left h2

/-- vector form: the row vector `Σ_j x_{a+j}[r] w_j`, restricted to the mask, vanishes. -/
theorem lemmaW_vec (x y : ℕ → ι → K) (a k : ℕ) (h2 : (2 : K) ≠ 0)
    (hA : Commute (pm m) (pp x y a)) (hcomm : Commute (pm m) (pp x y (a + k))) {r : ι} (hr : ¬ m r) :
    (∑ j ∈ Finset.range k, x (a + j) r • (y (a + j) ᵥ* pp x y (a + j))) ᵥ* pm m = 0 := by
  funext c
  rw [vecMul_pm_apply]
  by_cases hc : m c
  · simp only [hc, if_true, Finset.sum_apply, Pi.smul_apply, smul_eq_mul, Pi.zero_apply]
    exact lemmaW m x y a k h2 hA hcomm hr hc
  · simp [hc]

/-- **LEMMA W (ii): unique toucher.**  If exactly one thin `a+j₀` has `x[r] ≠ 0` (every other thin has
`x[r] = 0`), its pulled-back covector vanishes on the whole mask. -/
theorem lemmaW_unique (x y : ℕ → ι → K) (a k : ℕ) (h2 : (2 : K) ≠ 0)
    (hA : Commute (pm m) (pp x y a)) (hcomm : Commute (pm m) (pp x y (a + k)))
    {r : ι} (hr : ¬ m r) {j₀ : ℕ} (hj₀ : j₀ < k) (hother : ∀ j, j < k → j ≠ j₀ → x (a + j) r = 0)
    (hx : x (a + j₀) r ≠ 0) {c : ι} (hc : m c) :
    (y (a + j₀) ᵥ* pp x y (a + j₀)) c = 0 := by
  have h := lemmaW m x y a k h2 hA hcomm hr hc
  rw [Finset.sum_eq_single j₀ (fun j hj hne => by rw [hother j (Finset.mem_range.1 hj) hne]; simp)
    (fun hn => absurd (Finset.mem_range.2 hj₀) hn)] at h
  exact (mul_eq_zero.1 h).resolve_left hx

theorem isUnit_pp {x y : ℕ → ι → K} (hu : ∀ s, IsUnit (unitM (x s) (y s))) (a : ℕ) :
    IsUnit (pp x y a) := by
  induction a with
  | zero => simp [pp]
  | succ a ih => rw [pp]; exact (hu _).mul ih

theorem vecMul_eq_zero_of_isUnit {A : Matrix ι ι K} (hA : IsUnit A) {v : ι → K}
    (h : v ᵥ* A = 0) : v = 0 := by
  obtain ⟨u, rfl⟩ := hA
  have : (v ᵥ* (u : Matrix ι ι K)) ᵥ* ((u⁻¹ : (Matrix ι ι K)ˣ) : Matrix ι ι K) = 0 := by
    rw [h]; simp
  rwa [Matrix.vecMul_vecMul, ← Units.val_mul, mul_inv_cancel, Units.val_one, vecMul_one] at this

/-- **LEMMA W (ii): single-thin impossibility.**  One thin (`k = 1`) touching a role `r ∉ m` (`x[r] ≠ 0`)
before a stage with mask `m`, cut prefix commuting with `m` and invertible units, forces `y` to vanish on
the whole mask `m = m_R`.  Hence if the thin has any support on `m_R` (`pm m y ≠ 0`) it cannot borrow. -/
theorem single_thin_forces (x y : ℕ → ι → K) (a : ℕ) (h2 : (2 : K) ≠ 0)
    (hu : ∀ s, IsUnit (unitM (x s) (y s)))
    (hA : Commute (pm m) (pp x y a)) (hcomm : Commute (pm m) (pp x y (a + 1)))
    {r : ι} (hr : ¬ m r) (hx : x a r ≠ 0) : InMask (fun i => ¬ m i) (y a) := by
  -- covector w = y_a^T A vanishes on m
  have hw : ∀ c, m c → (y a ᵥ* pp x y a) c = 0 := fun c hc => by
    have := lemmaW_unique m x y a 1 h2 hA hcomm hr (j₀ := 0) (by omega)
      (fun j hj hne => absurd (by omega) hne) (by simpa using hx) hc
    simpa using this
  have h1 : (y a ᵥ* pm m) ᵥ* pp x y a = 0 := by
    rw [Matrix.vecMul_vecMul, hA.eq, ← Matrix.vecMul_vecMul]
    funext c
    rw [vecMul_pm_apply]
    by_cases hc : m c
    · simpa [hc] using hw c hc
    · simp [hc]
  have h3 := vecMul_eq_zero_of_isUnit (isUnit_pp hu a) h1
  intro i hi
  have := congrFun h3 i
  rw [vecMul_pm_apply] at this
  have hmi : m i := by simpa using hi
  simpa [hmi] using this

/-- the identity cannot be strengthened: a thin with `y` off the mask may touch a borrowed role alone
(`ι = Fin 2`, `m = {0}`, `x = y = e_1`, `T = diag(1,-1)`; prefix before the stage commutes with `m`). -/
example : ∃ (x y : ℕ → Fin 2 → ℚ) (m : Fin 2 → Prop) (_ : DecidablePred m),
    Commute (pm m) (pp x y 0) ∧ Commute (pm m) (pp x y (0 + 1)) ∧ ¬ m 1 ∧ x 0 1 ≠ 0 ∧ y 0 0 = 0 := by
  refine ⟨fun _ => ![0, 1], fun _ => ![0, 1], fun i => i = 0, inferInstance, ?_, ?_, by simp, by simp, by simp⟩
  · simp [pp]
  · show pm _ * _ = _ * pm _
    ext i j
    fin_cases i <;> fin_cases j <;>
      simp [pm, pp, unitM, vecMulVec, Matrix.mul_apply, Fin.sum_univ_two, Matrix.one_apply]

end LemmaW

#print axioms LemmaW.pp_window_entry
#print axioms LemmaW.lemmaW_defect
#print axioms LemmaW.lemmaW
#print axioms LemmaW.lemmaW_vec
#print axioms LemmaW.lemmaW_unique
#print axioms LemmaW.single_thin_forces
