/-
CALLER BORROWING, second pass (lane LEAN-NEXT36, Nov 17): the AUDITED closures of cards/WILD/BORROW/R7.md + AUDIT-R7.md
and R4.md section O + AUDIT-O.md, in the abstract caller model of CallerBorrow.lean.  See CallerBorrow2.md.
 1. D-isolation, 2. Lemma I, 3. Lemma L (audit-corrected form), 4. Theorem O (first/last-piece form).
-/
import Nov15.CallerBorrow

open Matrix CallerBorrow

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false
set_option linter.unusedSimpArgs false
set_option linter.unusedTactic false

namespace CallerBorrow2

variable {ι : Type*} [Fintype ι] [DecidableEq ι] {K : Type*} [Field K]

/-! ## §1. D-isolation (AUDIT-R7 (1): SOUND) -/

theorem commute_pm_iff (m : ι → Prop) [DecidablePred m] (F : Matrix ι ι K) :
    Commute F (pm m) ↔ ∀ i j, F i j ≠ 0 → (m i ↔ m j) := by
  constructor
  · intro h i j hij
    have h1 := congrFun (congrFun h.eq i) j
    rw [pm, Matrix.mul_diagonal, Matrix.diagonal_mul] at h1
    by_cases hi : m i <;> by_cases hj : m j <;> simp [hi, hj] at h1 ⊢
    · exact hij h1.symm
    · exact hij h1
  · intro h
    refine Matrix.ext fun i j => ?_
    rw [pm, Matrix.mul_diagonal, Matrix.diagonal_mul]
    by_cases hF : F i j = 0
    · simp [hF]
    · have := h i j hF
      by_cases hi : m i <;> by_cases hj : m j <;> simp_all

theorem pm_and (p q : ι → Prop) [DecidablePred p] [DecidablePred q] :
    (pm (fun i => p i ∧ q i) : Matrix ι ι K) = pm p * pm q := by
  rw [pm, pm, pm, Matrix.diagonal_mul_diagonal]
  congr 1; ext i; by_cases hp : p i <;> by_cases hq : q i <;> simp [hp, hq]

theorem pm_not (p : ι → Prop) [DecidablePred p] :
    (pm (fun i => ¬ p i) : Matrix ι ι K) = 1 - pm p := by
  ext i j
  by_cases hij : i = j
  · subst hij; by_cases hp : p i <;> simp [pm, hp]
  · simp [pm, Matrix.diagonal_apply, hij, Matrix.one_apply]

/-- **D-isolation.**  If `F` commutes with the two boundary projectors `π_m1`, `π_m2`, then `F` is block-diagonal on
`C | J1 | J2 | B` (`C = m1 ∩ m2`, `J1 = m1 \ m2`, `J2 = m2 \ m1`, `B` = rest): it commutes with all four block
projectors, and entrywise `F i j ≠ 0` forces `i` and `j` into the same block. -/
theorem d_isolation (m1 m2 : ι → Prop) [DecidablePred m1] [DecidablePred m2] {F : Matrix ι ι K}
    (h1 : Commute F (pm m1)) (h2 : Commute F (pm m2)) :
    Commute F (pm fun i => m1 i ∧ m2 i) ∧ Commute F (pm fun i => m1 i ∧ ¬ m2 i) ∧
    Commute F (pm fun i => m2 i ∧ ¬ m1 i) ∧ Commute F (pm fun i => ¬ m1 i ∧ ¬ m2 i) ∧
    ∀ i j, F i j ≠ 0 → ((m1 i ↔ m1 j) ∧ (m2 i ↔ m2 j)) := by
  have n1 : Commute F (pm fun i => ¬ m1 i) := by rw [pm_not]; exact (Commute.one_right F).sub_right h1
  have n2 : Commute F (pm fun i => ¬ m2 i) := by rw [pm_not]; exact (Commute.one_right F).sub_right h2
  refine ⟨?_, ?_, ?_, ?_, ?_⟩
  · rw [pm_and]; exact h1.mul_right h2
  · rw [pm_and]; exact h1.mul_right n2
  · rw [pm_and]; exact h2.mul_right n1
  · rw [pm_and]; exact n1.mul_right n2
  · intro i j hij
    exact ⟨(commute_pm_iff m1 F).1 h1 i j hij, (commute_pm_iff m2 F).1 h2 i j hij⟩

/-- The suffix product `G = -F⁻¹` is block-diagonal too. -/
theorem commute_neg_inv (m : ι → Prop) [DecidablePred m] {F G : Matrix ι ι K}
    (hFG : F * G = -1) (hGF : G * F = -1) (h : Commute F (pm m)) : Commute G (pm m) := by
  have e : G * (F * pm m) * G = G * (pm m * F) * G := by rw [h.eq]
  have l : G * (F * pm m) * G = - (pm m * G) := by
    calc G * (F * pm m) * G = (G * F) * pm m * G := by simp only [mul_assoc]
      _ = _ := by rw [hGF]; simp
  have r : G * (pm m * F) * G = - (G * pm m) := by
    calc G * (pm m * F) * G = G * pm m * (F * G) := by simp only [mul_assoc]
      _ = _ := by rw [hFG]; simp
  have : pm m * G = G * pm m := by
    have := e; rw [l, r] at this; exact neg_injective this
  exact this.symm

/-- A unit lying in the mask commutes after the stage. -/
theorem commute_after_stage {x y : ℕ → ι → K} (m : ι → Prop) [DecidablePred m] (s : ℕ)
    (hx : InMask m (x s)) (hy : InMask m (y s)) (hc : Commute (pm m) (pp x y s)) :
    Commute (pm m) (pp x y (s + 1)) :=
  (commute_pm_unit m hx hy).mul_right hc

/-- **D-isolation from the stage data.**  Adjacent units `s` (mask `m1`) and `s+1` (mask `m2`) with no thin between
them; the cut is `pp (s+1)`.  Commutation after `m1` (stage unit in the mask + prefix commutation at `s`) and
before `m2` (prefix commutation at `s+1`) give the commutation of the cut with both boundary projectors. -/
theorem d_isolation_stages {x y : ℕ → ι → K} (m1 m2 : ι → Prop) [DecidablePred m1] [DecidablePred m2] (s : ℕ)
    (hx : InMask m1 (x s)) (hy : InMask m1 (y s)) (hc1 : Commute (pm m1) (pp x y s))
    (hc2 : Commute (pm m2) (pp x y (s + 1))) :
    ∀ i j, pp x y (s + 1) i j ≠ 0 → ((m1 i ↔ m1 j) ∧ (m2 i ↔ m2 j)) := by
  have h1 := commute_after_stage m1 s hx hy hc1
  exact (d_isolation m1 m2 h1.symm hc2.symm).2.2.2.2

/-! ## §2. Lemma I (AUDIT-R7 (2): SOUND) -/

/-- `Q` fixes the `J` columns and the `J` rows of the identity. -/
def FixJ (J : ι → Prop) (Q : Matrix ι ι K) : Prop :=
  (∀ i z, J z → Q i z = (1 : Matrix ι ι K) i z) ∧ (∀ z j, J z → Q z j = (1 : Matrix ι ι K) z j)

theorem FixJ.one (J : ι → Prop) : FixJ J (1 : Matrix ι ι K) := ⟨fun _ _ _ => rfl, fun _ _ _ => rfl⟩

theorem FixJ.mul {J : ι → Prop} {Q Q' : Matrix ι ι K} (h : FixJ J Q) (h' : FixJ J Q') : FixJ J (Q * Q') := by
  constructor
  · intro i z hz
    rw [Matrix.mul_apply, Finset.sum_congr rfl fun k _ => by rw [h'.1 k z hz], ← Matrix.mul_apply, mul_one,
      h.1 i z hz]
  · intro z j hz
    rw [Matrix.mul_apply, Finset.sum_congr rfl fun k _ => by rw [h.2 z k hz], ← Matrix.mul_apply, one_mul,
      h'.2 z j hz]

theorem FixJ.unit {J : ι → Prop} {x y : ι → K} (hx : ∀ i, J i → x i = 0) (hy : ∀ i, J i → y i = 0) :
    FixJ J (unitM x y) := by
  constructor
  · intro i z hz; simp [unitM, vecMulVec_apply, hy z hz]
  · intro z j hz; simp [unitM, vecMulVec_apply, hx z hz]

theorem FixJ.pp {J : ι → Prop} {x y : ℕ → ι → K} (n : ℕ) (hx : ∀ s, s < n → ∀ i, J i → x s i = 0)
    (hy : ∀ s, s < n → ∀ i, J i → y s i = 0) : FixJ J (pp x y n) := by
  induction n with
  | zero => exact FixJ.one J
  | succ n ih =>
    exact (FixJ.unit (hx n (by omega)) (hy n (by omega))).mul
      (ih (fun s hs => hx s (by omega)) fun s hs => hy s (by omega))

theorem FixJ.seg {J : ι → Prop} {x y : ℕ → ι → K} (a d : ℕ) (hx : ∀ s, a ≤ s → s < a + d → ∀ i, J i → x s i = 0)
    (hy : ∀ s, a ≤ s → s < a + d → ∀ i, J i → y s i = 0) : FixJ J (seg x y a d) := by
  induction d with
  | zero => exact FixJ.one J
  | succ d ih =>
    exact (FixJ.unit (hx (a + d) (by omega) (by omega)) (hy (a + d) (by omega) (by omega))).mul
      (ih (fun s h1 h2 => hx s h1 (by omega)) fun s h1 h2 => hy s h1 (by omega))

theorem mulVec_fix_of_col {S : ι → Prop} {Q : Matrix ι ι K} (hc : ∀ i k, S k → Q i k = (1 : Matrix ι ι K) i k)
    {v : ι → K} (hv : ∀ k, ¬ S k → v k = 0) : Q *ᵥ v = v := by
  ext i
  rw [Matrix.mulVec, dotProduct]
  have : ∀ k, Q i k * v k = (1 : Matrix ι ι K) i k * v k := by
    intro k; by_cases hk : S k
    · rw [hc i k hk]
    · rw [hv k hk]; simp
  rw [Finset.sum_congr rfl fun k _ => this k, ← dotProduct, ← Matrix.mulVec, Matrix.one_mulVec]

/-- Lemma I core (column form): if some `y z ≠ 0` with `z ∈ J`, the unit is the identity (`x = 0`). -/
theorem lemmaI_core (h2 : (2 : K) ≠ 0) (J : ι → Prop) {Q1 Q2 Q2' : Matrix ι ι K} {x y : ι → K}
    (hiso : y ⬝ᵥ x = 0)
    (hQ1c : ∀ i z, J z → Q1 i z = (1 : Matrix ι ι K) i z)
    (hQ2c : ∀ i z, J z → Q2 i z = (1 : Matrix ι ι K) i z) (hQ2inv : Q2' * Q2 = 1)
    (hbd : ∀ i j, (Q2 * unitM x y * Q1) i j ≠ 0 → (J i ↔ J j))
    (hD : ∀ i j, J i → J j → ((Q2 * unitM x y * Q1) * (Q2 * unitM x y * Q1)) i j = (1 : Matrix ι ι K) i j)
    (z : ι) (hz : J z) (hyz : y z ≠ 0) : x = 0 := by
  set w : ι → K := Q2 *ᵥ x with hw
  set F : Matrix ι ι K := Q2 * unitM x y * Q1 with hF
  -- F = (Q2 - 2 w y^T) Q1
  have hFeq : F = Q2 * Q1 - (2 : K) • (vecMulVec w y * Q1) := by
    rw [hF, unitM, Matrix.mul_sub, Matrix.mul_one, Matrix.mul_smul, Matrix.mul_vecMulVec, Matrix.sub_mul,
      Matrix.smul_mul]
  have hFcol : ∀ i j, J j → F i j = (1 : Matrix ι ι K) i j - 2 * w i * y j := by
    intro i j hj
    have e1 : (Q2 * Q1) i j = (1 : Matrix ι ι K) i j := by
      rw [Matrix.mul_apply, Finset.sum_congr rfl fun k _ => by rw [hQ1c k j hj], ← Matrix.mul_apply, mul_one,
        hQ2c i j hj]
    have e2 : (vecMulVec w y * Q1) i j = w i * y j := by
      rw [Matrix.mul_apply, Finset.sum_congr rfl fun k _ => by rw [hQ1c k j hj]]
      simp [vecMulVec_apply, Matrix.one_apply]
    rw [hFeq, Matrix.sub_apply, Matrix.smul_apply, e1, e2, smul_eq_mul]; ring
  -- step 1: w vanishes off J
  have hwJ : ∀ i, ¬ J i → w i = 0 := by
    intro i hi
    by_contra hwi
    have hne : i ≠ z := fun h => hi (h ▸ hz)
    have : F i z ≠ 0 := by
      rw [hFcol i z hz]; simp [Matrix.one_apply, hne, h2, hyz, hwi]
    exact hi ((hbd i z this).2 hz)
  -- step 2: x = w
  have hQ2w : Q2 *ᵥ w = w := mulVec_fix_of_col hQ2c fun k hk => hwJ k hk
  have hxw : x = w := by
    calc x = (Q2' * Q2) *ᵥ x := by rw [hQ2inv, Matrix.one_mulVec]
      _ = Q2' *ᵥ w := by rw [← Matrix.mulVec_mulVec]
      _ = Q2' *ᵥ (Q2 *ᵥ w) := by rw [hQ2w]
      _ = w := by rw [Matrix.mulVec_mulVec, hQ2inv, Matrix.one_mulVec]
  -- step 3: F w = w
  have hFw : F *ᵥ w = w := by
    have h1 : Q1 *ᵥ w = w := mulVec_fix_of_col hQ1c fun k hk => hwJ k hk
    have h3 : unitM x y *ᵥ w = w := by
      have hyw : y ⬝ᵥ w = 0 := hxw ▸ hiso
      rw [unitM, Matrix.sub_mulVec, Matrix.one_mulVec, Matrix.smul_mulVec, Matrix.vecMulVec_mulVec, hyw]
      simp
    rw [hF, ← Matrix.mulVec_mulVec, ← Matrix.mulVec_mulVec, h1, h3, hQ2w]
  -- step 4: D^2 = 1 on J forces w = 0
  have hFF : ∀ i, (F * F) i z = F i z - 2 * y z * w i := by
    intro i
    have hk : ∀ k, F i k * F k z = F i k * (1 : Matrix ι ι K) k z - 2 * y z * (F i k * w k) := by
      intro k; rw [hFcol k z hz]; ring
    rw [Matrix.mul_apply, Finset.sum_congr rfl fun k _ => hk k, Finset.sum_sub_distrib, ← Finset.mul_sum]
    have e1 : ∑ k, F i k * (1 : Matrix ι ι K) k z = F i z := by
      simp [Matrix.one_apply]
    have e2 : ∑ k, F i k * w k = w i := by
      have := congrFun hFw i
      simpa [Matrix.mulVec, dotProduct] using this
    rw [e1, e2]
  have hw0 : ∀ i, w i = 0 := by
    intro i
    by_cases hi : J i
    · have h1 := hD i z hi hz
      rw [hFF i, hFcol i z hz] at h1
      have h4 : (2 : K) * 2 * y z * w i = 0 := by linear_combination (-1 : K) * h1
      have h22 : (2 : K) * 2 ≠ 0 := mul_ne_zero h2 h2
      simpa [h22, hyz] using h4
    · exact hwJ i hi
  rw [hxw]; funext i; exact hw0 i

/-- transposition swaps the roles of `x`, `y` and of the two sides. -/
theorem lemmaI_row (h2 : (2 : K) ≠ 0) (J : ι → Prop) {Q1 Q2 Q1' : Matrix ι ι K} {x y : ι → K}
    (hiso : y ⬝ᵥ x = 0)
    (hQ1r : ∀ z j, J z → Q1 z j = (1 : Matrix ι ι K) z j)
    (hQ2r : ∀ z j, J z → Q2 z j = (1 : Matrix ι ι K) z j) (hQ1inv : Q1 * Q1' = 1)
    (hbd : ∀ i j, (Q2 * unitM x y * Q1) i j ≠ 0 → (J i ↔ J j))
    (hD : ∀ i j, J i → J j → ((Q2 * unitM x y * Q1) * (Q2 * unitM x y * Q1)) i j = (1 : Matrix ι ι K) i j)
    (z : ι) (hz : J z) (hxz : x z ≠ 0) : y = 0 := by
  have hT : (unitM x y)ᵀ = unitM y x := by
    unfold unitM; rw [Matrix.transpose_sub, Matrix.transpose_one, Matrix.transpose_smul, Matrix.transpose_vecMulVec]
  have hFT : (Q2 * unitM x y * Q1)ᵀ = Q1ᵀ * unitM y x * Q2ᵀ := by
    rw [Matrix.transpose_mul, Matrix.transpose_mul, hT]; simp only [mul_assoc]
  refine lemmaI_core h2 J (Q1 := Q2ᵀ) (Q2 := Q1ᵀ) (Q2' := Q1'ᵀ) (x := y) (y := x)
    (by rw [dotProduct_comm]; exact hiso) ?_ ?_ ?_ ?_ ?_ z hz hxz
  · intro i z' hz'; rw [Matrix.transpose_apply, hQ2r z' i hz']; simp [Matrix.one_apply, eq_comm]
  · intro i z' hz'; rw [Matrix.transpose_apply, hQ1r z' i hz']; simp [Matrix.one_apply, eq_comm]
  · rw [← Matrix.transpose_mul, hQ1inv, Matrix.transpose_one]
  · intro i j hij
    rw [← hFT, Matrix.transpose_apply] at hij
    exact (hbd j i hij).symm
  · intro i j hi hj
    rw [← hFT, ← Matrix.transpose_mul, Matrix.transpose_apply]
    have := hD j i hj hi
    rw [this]; simp [Matrix.one_apply, eq_comm]

/-- **Lemma I (single toucher).**  `F = Q2 · T · Q1` with `T = 1 - 2 x yᵀ` isotropic, `Q1`,`Q2` invertible and fixing
the `J` rows and columns, `F` block-diagonal for `J` and `F[J,J]² = 1` (char ≠ 2).  Then either `T` is the identity
(`x = 0` or `y = 0`) or `T` touches `J` in neither `x` nor `y`.  (`x ≠ 0 ≠ y` is exactly "T is a genuine unit":
a unit with `x = 0` and `y[J] ≠ 0` is the identity, so "touches" is vacuous there.) -/
theorem lemmaI (h2 : (2 : K) ≠ 0) (J : ι → Prop) {Q1 Q2 : Matrix ι ι K} {x y : ι → K}
    (hiso : y ⬝ᵥ x = 0) (hQ1 : FixJ J Q1) (hQ2 : FixJ J Q2) (hu1 : IsUnit Q1) (hu2 : IsUnit Q2)
    (hbd : ∀ i j, (Q2 * unitM x y * Q1) i j ≠ 0 → (J i ↔ J j))
    (hD : ∀ i j, J i → J j → ((Q2 * unitM x y * Q1) * (Q2 * unitM x y * Q1)) i j = (1 : Matrix ι ι K) i j) :
    x = 0 ∨ y = 0 ∨ ((∀ i, J i → x i = 0) ∧ (∀ i, J i → y i = 0)) := by
  obtain ⟨Q2', hQ2'⟩ := hu2.exists_left_inv
  obtain ⟨Q1', hQ1'⟩ := hu1.exists_right_inv
  by_cases hx : x = 0
  · exact Or.inl hx
  by_cases hy : y = 0
  · exact Or.inr (Or.inl hy)
  refine Or.inr (Or.inr ⟨fun i hi => ?_, fun i hi => ?_⟩)
  · by_contra hne
    exact hy (lemmaI_row h2 J hiso hQ1.2 hQ2.2 hQ1' hbd hD i hi hne)
  · by_contra hne
    exact hx (lemmaI_core h2 J hiso hQ1.1 hQ2.1 hQ2' hbd hD i hi hne)

theorem isUnit_pp {x y : ℕ → ι → K} (hu : ∀ s, IsUnit (unitM (x s) (y s))) (n : ℕ) : IsUnit (pp x y n) := by
  induction n with
  | zero => simp [pp]
  | succ n ih => rw [pp]; exact (hu _).mul ih

/-- Lemma I in the prefix-product model: `F = pp (s+1+d)` with one unit `s` and all other units (before `s`, after
`s`) not touching `J` (each `x j`, `y j` vanishes on `J`), all units isotropic. -/
theorem lemmaI_pp (h2 : (2 : K) ≠ 0) (J : ι → Prop) {x y : ℕ → ι → K}
    (hu : ∀ s, IsUnit (unitM (x s) (y s))) (hiso : ∀ s, y s ⬝ᵥ x s = 0) (s d : ℕ)
    (hx : ∀ j i, j ≠ s → J i → x j i = 0) (hy : ∀ j i, j ≠ s → J i → y j i = 0)
    (hbd : ∀ i j, pp x y (s + 1 + d) i j ≠ 0 → (J i ↔ J j))
    (hD : ∀ i j, J i → J j → (pp x y (s + 1 + d) * pp x y (s + 1 + d)) i j = (1 : Matrix ι ι K) i j) :
    x s = 0 ∨ y s = 0 ∨ ((∀ i, J i → x s i = 0) ∧ (∀ i, J i → y s i = 0)) := by
  have hQ1 : FixJ J (pp x y s) := FixJ.pp s (fun j hj i hi => hx j i (by omega) hi)
    fun j hj i hi => hy j i (by omega) hi
  have hQ2 : FixJ J (seg x y (s + 1) d) := FixJ.seg (s + 1) d (fun j h1 h2 i hi => hx j i (by omega) hi)
    fun j h1 h2 i hi => hy j i (by omega) hi
  have hF : pp x y (s + 1 + d) = seg x y (s + 1) d * unitM (x s) (y s) * pp x y s := by
    rw [pp_add, pp, mul_assoc]
  rw [hF] at hbd hD
  exact lemmaI h2 J (hiso s) hQ1 hQ2 ((isUnit_pp hu s)) (isUnit_seg hu _ _) hbd hD

/-! ## §3. Lemma L, audit-corrected (AUDIT-R7 (3): SOUND-WITH-FIXES)

Corrected argument: `L = 0` (a −1 eigenvector vanishes on untouched suffix rows) ⇒ `V_- = R^{B_pre}` ⇒ for
`(Kw, w) ∈ V_+` with `w` on untouched suffix columns, `F (Kw, w) = (−Kw, w)`, so `K = 0` and the shear
`g⁻¹ = 1 + K` is the identity.  No claim about `y_pre K` is used (the audit showed it unjustified). -/

theorem mulVec_row_fix {S : ι → Prop} {M : Matrix ι ι K} (hrow : ∀ s j, S s → M s j = (1 : Matrix ι ι K) s j)
    (v : ι → K) {s : ι} (hs : S s) : (M *ᵥ v) s = v s := by
  rw [Matrix.mulVec, dotProduct, Finset.sum_congr rfl fun j _ => by rw [hrow s j hs], ← dotProduct,
    ← Matrix.mulVec, Matrix.one_mulVec]

/-- **Lemma L, first step.**  A `−1` eigenvector vanishes on every untouched row. -/
theorem lemmaL_zero (h2 : (2 : K) ≠ 0) {M : Matrix ι ι K} (S : ι → Prop)
    (hrow : ∀ s j, S s → M s j = (1 : Matrix ι ι K) s j) {v : ι → K} (hv : M *ᵥ v = -v) {s : ι} (hs : S s) :
    v s = 0 := by
  have h := congrFun hv s
  rw [mulVec_row_fix hrow v hs] at h
  have : (2 : K) * v s = 0 := by simp only [Pi.neg_apply] at h; linear_combination h
  simpa [h2] using this

/-- **`L = 0`.**  `V_-` is a graph `a ↦ a + L a` over `B_pre`, `L` lands in `B_suf`; if every `B_suf` row of `F`
is an identity row (no prefix unit touches `B_suf`), then `L = 0`. -/
theorem L_eq_zero (h2 : (2 : K) ≠ 0) {F Lm : Matrix ι ι K} (Bpre Bsuf : ι → Prop)
    (hdisj : ∀ i, Bpre i → ¬ Bsuf i) (hLs : ∀ i j, Lm i j ≠ 0 → Bsuf i)
    (hrow : ∀ s j, Bsuf s → F s j = (1 : Matrix ι ι K) s j)
    (hgraph : ∀ a : ι → K, (∀ i, ¬ Bpre i → a i = 0) → F *ᵥ (a + Lm *ᵥ a) = -(a + Lm *ᵥ a))
    (a : ι → K) (ha : ∀ i, ¬ Bpre i → a i = 0) : Lm *ᵥ a = 0 := by
  ext s
  by_cases hs : Bsuf s
  · have h0 := lemmaL_zero h2 Bsuf hrow (hgraph a ha) hs
    have has : a s = 0 := ha s fun hp => hdisj s hp hs
    simpa [has] using h0
  · simp only [Matrix.mulVec, dotProduct, Pi.zero_apply]
    refine Finset.sum_eq_zero fun j _ => ?_
    by_cases hL : Lm s j = 0
    · simp [hL]
    · exact absurd (hLs s j hL) hs

/-- **Lemma L (shear is trivial).**  With `V_- = R^{B_pre}` (`L = 0`), `V_+ = {(Kw, w)}` over untouched suffix
columns `B_suf` (columns of `F` equal to the identity columns), `K = 0`, hence `g⁻¹ = 1 + K = 1`. -/
theorem lemmaL_K (h2 : (2 : K) ≠ 0) {F Km : Matrix ι ι K} (Bpre Bsuf : ι → Prop)
    (hVm : ∀ a : ι → K, (∀ i, ¬ Bpre i → a i = 0) → F *ᵥ a = -a)
    (hfix : ∀ i z, Bsuf z → F i z = (1 : Matrix ι ι K) i z)
    (hKs : ∀ i j, Km i j ≠ 0 → Bpre i ∧ Bsuf j)
    (hVp : ∀ w : ι → K, (∀ i, ¬ Bsuf i → w i = 0) → F *ᵥ (Km *ᵥ w + w) = Km *ᵥ w + w) :
    Km = 0 := by
  have hu : ∀ w : ι → K, (∀ i, ¬ Bsuf i → w i = 0) → Km *ᵥ w = 0 := by
    intro w hw
    have hKw : ∀ i, ¬ Bpre i → (Km *ᵥ w) i = 0 := by
      intro i hi
      simp only [Matrix.mulVec, dotProduct]
      refine Finset.sum_eq_zero fun j _ => ?_
      by_cases hk : Km i j = 0
      · simp [hk]
      · exact absurd (hKs i j hk).1 hi
    have h1 := hVp w hw
    rw [Matrix.mulVec_add, hVm _ hKw, mulVec_fix_of_col hfix hw] at h1
    ext i
    have := congrFun h1 i
    simp only [Pi.add_apply, Pi.neg_apply] at this
    have h22 : (2 : K) * (Km *ᵥ w) i = 0 := by linear_combination -this
    simpa [h2] using h22
  ext i j
  by_cases hj : Bsuf j
  · have := congrFun (hu (Pi.single j 1) fun k hk => by
      have : k ≠ j := fun h => hk (h ▸ hj)
      simp [Pi.single_apply, this]) i
    simpa [Matrix.mulVec, dotProduct, Pi.single_apply] using this
  · by_contra hne
    exact hj (hKs i j hne).2

theorem shear_id {Km : Matrix ι ι K} (h : Km = 0) : (1 : Matrix ι ι K) + Km = 1 := by rw [h, add_zero]

/-- Dual (suffix side): with `G = −F⁻¹`, a `+1` eigenvector of `F` is a `−1` eigenvector of `G` (and conversely). -/
theorem G_eigen_of_F_plus {F G : Matrix ι ι K} (hGF : G * F = -1) {v : ι → K} (hv : F *ᵥ v = v) :
    G *ᵥ v = -v := by
  have : G *ᵥ (F *ᵥ v) = -v := by rw [Matrix.mulVec_mulVec, hGF, Matrix.neg_mulVec, Matrix.one_mulVec]
  rwa [hv] at this

theorem G_eigen_of_F_minus {F G : Matrix ι ι K} (hGF : G * F = -1) {v : ι → K} (hv : F *ᵥ v = -v) :
    G *ᵥ v = v := by
  have : G *ᵥ (F *ᵥ v) = -v := by rw [Matrix.mulVec_mulVec, hGF, Matrix.neg_mulVec, Matrix.one_mulVec]
  rw [hv, Matrix.mulVec_neg] at this
  exact neg_injective this

/-- Dual of `lemmaL_zero`: if no suffix unit touches the rows `S` (rows of `G` are identity rows), every
`+1` eigenvector of `F` vanishes on `S`, i.e. `V_+ ⊆ R^{B_suf}` ("T_last avoids B_pre"). -/
theorem lemmaL_zero_dual (h2 : (2 : K) ≠ 0) {F G : Matrix ι ι K} (hGF : G * F = -1) (S : ι → Prop)
    (hrow : ∀ s j, S s → G s j = (1 : Matrix ι ι K) s j) {v : ι → K} (hv : F *ᵥ v = v) {s : ι} (hs : S s) :
    v s = 0 :=
  lemmaL_zero h2 S hrow (G_eigen_of_F_plus hGF hv) hs

/-- Untouched sets are monotone: this is the "masks are intervals" step, `B_suf(k') ⊆ B_suf(1)`. -/
theorem FixJ.mono {J J' : ι → Prop} {Q : Matrix ι ι K} (h : FixJ J Q) (hJ : ∀ i, J' i → J i) : FixJ J' Q :=
  ⟨fun i z hz => h.1 i z (hJ z hz), fun z j hz => h.2 z j (hJ z hz)⟩

/-! ## §4. Theorem O, first/last-piece form (AUDIT-O: SOUND-WITH-FIXES) -/

/-- `ker (X + 1)` = the `−1` eigenspace (used for `ker(M_w + I)`). -/
def kerm (X : Matrix ι ι K) : Submodule K (ι → K) := LinearMap.ker (X + 1).mulVecLin

theorem mem_kerm {X : Matrix ι ι K} {v : ι → K} : v ∈ kerm X ↔ X *ᵥ v = -v := by
  rw [kerm, LinearMap.mem_ker, Matrix.mulVecLin_apply, Matrix.add_mulVec, Matrix.one_mulVec,
    add_eq_zero_iff_eq_neg]

/-- rank-nullity split along a coordinate map -/
theorem finrank_le_inf_ker_add_map (P : Submodule K (ι → K)) (φ : (ι → K) →ₗ[K] (ι → K)) :
    Module.finrank K P ≤ Module.finrank K ↥(P ⊓ LinearMap.ker φ) + Module.finrank K ↥(P.map φ) := by
  have h := LinearMap.finrank_range_add_finrank_ker (φ.domRestrict P)
  rw [LinearMap.range_domRestrict, Module.finrank_eq_card_basis (Module.finBasis K P)] at h
  have h2 : Module.finrank K (LinearMap.ker (φ.domRestrict P)) ≤ Module.finrank K ↥(P ⊓ LinearMap.ker φ) := by
    rw [← Submodule.finrank_map_subtype_eq P (LinearMap.ker (φ.domRestrict P))]
    apply Submodule.finrank_mono
    rintro v ⟨u, hu, rfl⟩
    refine ⟨u.2, ?_⟩
    simpa using hu
  have h3 : Module.finrank K P = Fintype.card (Fin (Module.finrank K P)) := by simp
  omega

/-- a submodule of vectors supported on `PH` has dimension `≤ |PH|` -/
theorem finrank_le_card_supp (PH : ι → Prop) [DecidablePred PH] (T : Submodule K (ι → K))
    (hT : ∀ v ∈ T, ∀ i, ¬ PH i → v i = 0) : Module.finrank K T ≤ Fintype.card {i // PH i} := by
  let f : (ι → K) →ₗ[K] ({i // PH i} → K) := LinearMap.funLeft K K Subtype.val
  have hinj : Function.Injective (f.domRestrict T) := by
    intro u v huv
    apply Subtype.ext
    funext i
    by_cases hi : PH i
    · have := congrFun huv ⟨i, hi⟩
      simpa [f, LinearMap.funLeft] using this
    · rw [hT u.1 u.2 i hi, hT v.1 v.2 i hi]
  have := LinearMap.finrank_le_finrank_of_injective hinj
  simpa using this

/-- **Theorem O, step 1.**  Commutation of the prefix `P` with `π_m` (`m = mask(r_1)`), `L` missing `m` (h1),
`P e_l = A e_l` (h4, the audit's reading), and rows outside `L ∪ m` of `A` being identity rows (h2) give
`A[L^c, L] = 0`. -/
theorem thmO_step1 {A P : Matrix ι ι K} (m L : ι → Prop) [DecidablePred m]
    (hcomm : Commute P (pm m)) (hLm : ∀ l, L l → ¬ m l) (hPA : ∀ l, L l → ∀ i, P i l = A i l)
    (hrow : ∀ i, ¬ L i → ¬ m i → ∀ j, A i j = (1 : Matrix ι ι K) i j) :
    ∀ i l, ¬ L i → L l → A i l = 0 := by
  intro i l hi hl
  by_cases hmi : m i
  · rw [← hPA l hl i]
    by_contra hne
    exact hLm l hl (((commute_pm_iff m P).1 hcomm i l hne).1 hmi)
  · rw [hrow i hi hmi l]
    have : i ≠ l := fun h => hi (h ▸ hl)
    simp [Matrix.one_apply, this]

/-- **W as an equality** (AUDIT-O): `ker(F_w + I) ≅ ker H` for `H = (G_w − K_w)` (the audit's
`ker(F+I) = X ker(G−K)`).  `dim = N_w − rank H`, and `rank H = 2` needs the TWO explicit hypotheses: `rank ≤ 2`
(global `ρ = 2`) and `rank ≥ 2` (a stage with `t ≠ −1` in the window gives a `2×2` block of determinant `1 + t`). -/
theorem W_dim {n : Type*} [Fintype n] [DecidableEq n] (H : Matrix n n K)
    (hρ_le : H.rank ≤ 2) (ht_ge : 2 ≤ H.rank) {P : Submodule K (n → K)}
    (e : LinearMap.ker H.mulVecLin ≃ₗ[K] P) : Module.finrank K P + 2 = Fintype.card n := by
  have h := LinearMap.finrank_range_add_finrank_ker H.mulVecLin
  have hr : H.rank = 2 := le_antisymm hρ_le ht_ge
  rw [Matrix.rank] at hr
  rw [hr, e.finrank_eq] at h
  simp only [Module.finrank_fintype_fun_eq_card] at h
  omega

/-- **Theorem O (first/last-piece form): contradiction.**  `A` = left-stage product, `B` = right-stage product,
`M = B A` the piece, `L`, `R`, `PH` the left-only roles, right-only roles, and the phantom roles.
Hypotheses: `A[L^c,L] = 0` (step 1), the right stages fix `L` (rows and columns), the left stages fix `R`
columns, (h3) `ker(M+I)` lies in `R^{L ∪ R ∪ PH}`, and the three W-dimensions (`W` applied to the left arm, the right
arm and the piece window): `dim ker(A+I) + 1 ≤ cL`, `dim ker(B+I) + 1 ≤ cR`, `N ≤ dim ker(M+I) + 2`, with
`cL + cR + |PH| < N` (for `cL = 2s−1`, `cR = 2t−1`, `|PH| ≤ 1`, `N = N_i ≥ 2s+2t`, i.e. `N_i − 2 > 2s+2t−3`). -/
theorem thmO (L R PH : ι → Prop) [DecidablePred L] [DecidablePred R] [DecidablePred PH] {A B : Matrix ι ι K}
    (hAQL : ∀ i l, ¬ L i → L l → A i l = 0)
    (hBc : ∀ i k, L k → B i k = (1 : Matrix ι ι K) i k) (hBr : ∀ l j, L l → B l j = (1 : Matrix ι ι K) l j)
    (hAR : ∀ i r, R r → A i r = (1 : Matrix ι ι K) i r)
    (h3 : ∀ v, (B * A) *ᵥ v = -v → ∀ i, ¬ (L i ∨ R i ∨ PH i) → v i = 0)
    (cL cR N : ℕ) (hWA : Module.finrank K (kerm A) + 1 ≤ cL) (hWB : Module.finrank K (kerm B) + 1 ≤ cR)
    (hWM : N ≤ Module.finrank K (kerm (B * A)) + 2)
    (hN : cL + cR + Fintype.card {i // PH i} < N) : False := by
  classical
  let P := kerm (B * A)
  let φQ : (ι → K) →ₗ[K] (ι → K) := (pm (fun i => ¬ L i) : Matrix ι ι K).mulVecLin
  let φH : (ι → K) →ₗ[K] (ι → K) := (pm PH : Matrix ι ι K).mulVecLin
  have hφQ : ∀ v i, φQ v i = if L i then 0 else v i := by
    intro v i; simp only [φQ, Matrix.mulVecLin_apply, pm_mulVec_apply]; by_cases h : L i <;> simp [h]
  have hφH : ∀ v i, φH v i = if PH i then v i else 0 := by
    intro v i; simp only [φH, Matrix.mulVecLin_apply, pm_mulVec_apply]
  -- (a)
  have ha : P ⊓ LinearMap.ker φQ ≤ kerm A := by
    intro v hv
    obtain ⟨hvP, hvk⟩ := Submodule.mem_inf.1 hv
    have hvL : ∀ i, ¬ L i → v i = 0 := by
      intro i hi
      have := congrFun (LinearMap.mem_ker.1 hvk) i
      simpa [hφQ, hi] using this
    have hAv : ∀ i, ¬ L i → (A *ᵥ v) i = 0 := by
      intro i hi
      simp only [Matrix.mulVec, dotProduct]
      refine Finset.sum_eq_zero fun j _ => ?_
      by_cases hj : L j
      · simp [hAQL i j hi hj]
      · simp [hvL j hj]
    have hBA : B *ᵥ (A *ᵥ v) = A *ᵥ v := mulVec_fix_of_col hBc hAv
    have hM : (B * A) *ᵥ v = A *ᵥ v := by rw [← Matrix.mulVec_mulVec, hBA]
    exact mem_kerm.2 (by rw [← hM]; exact mem_kerm.1 hvP)
  -- (b)
  have hb : (P.map φQ) ⊓ LinearMap.ker φH ≤ kerm B := by
    intro u hu
    obtain ⟨hU, hk⟩ := Submodule.mem_inf.1 hu
    obtain ⟨v, hvP, rfl⟩ := Submodule.mem_map.1 hU
    have hvM := mem_kerm.1 hvP
    have hR : ∀ i, ¬ R i → φQ v i = 0 := by
      intro i hi
      by_cases hL : L i
      · simp [hφQ, hL]
      · by_cases hH : PH i
        · have := congrFun (LinearMap.mem_ker.1 hk) i
          simpa [hφH, hφQ, hH, hL] using this
        · have := h3 v hvM i (by tauto)
          simp [hφQ, hL, this]
    set u := φQ v with hu_def
    set vL : ι → K := v - u with hvL_def
    have hvLi : ∀ j, ¬ L j → vL j = 0 := by
      intro j hj; simp [hvL_def, hu_def, hφQ, hj]
    have hAvL : ∀ i, ¬ L i → (A *ᵥ vL) i = 0 := by
      intro i hi
      simp only [Matrix.mulVec, dotProduct]
      refine Finset.sum_eq_zero fun j _ => ?_
      by_cases hj : L j
      · simp [hAQL i j hi hj]
      · simp [hvLi j hj]
    have e1 : B *ᵥ (A *ᵥ vL) = A *ᵥ vL := mulVec_fix_of_col hBc hAvL
    have e2 : A *ᵥ u = u := mulVec_fix_of_col hAR hR
    have e3 : v = vL + u := by simp [hvL_def]
    have e4 : (B * A) *ᵥ v = A *ᵥ vL + B *ᵥ u := by
      rw [e3, Matrix.mulVec_add, ← Matrix.mulVec_mulVec, ← Matrix.mulVec_mulVec, e1, e2]
    apply mem_kerm.2
    ext i
    by_cases hi : L i
    · have a1 : (B *ᵥ u) i = u i := mulVec_row_fix hBr u hi
      have a2 : u i = 0 := by simp [hu_def, hφQ, hi]
      simp [a1, a2]
    · have h5 := congrFun (e4.symm.trans hvM) i
      have h6 := congrFun e3 i
      simp only [Pi.add_apply, Pi.neg_apply] at h5 h6
      rw [hAvL i hi] at h5
      rw [hvLi i hi] at h6
      simp only [Pi.neg_apply]
      linear_combination h5 - h6
  -- (c)
  have hc : Module.finrank K ↥(((P.map φQ).map φH)) ≤ Fintype.card {i // PH i} := by
    apply finrank_le_card_supp
    intro w hw i hi
    obtain ⟨u, -, rfl⟩ := Submodule.mem_map.1 hw
    simp [hφH, hi]
  have h1 := finrank_le_inf_ker_add_map P φQ
  have h2 := finrank_le_inf_ker_add_map (P.map φQ) φH
  have h3' := Submodule.finrank_mono ha
  have h4 := Submodule.finrank_mono hb
  have hP : Module.finrank K P = Module.finrank K (kerm (B * A)) := rfl
  omega

/-- AUDIT-O arithmetic: `cL = 2s−1`, `cR = 2t−1`, `|PH| ≤ 1`, `N ≥ 2s+2t` (i.e. `N_i − 2 > 2s+2t−3`) give
`cL + cR + |PH| < N`; `|PH| = 2` would NOT (ph ≤ 1 is essential, AUDIT-O). -/
theorem thmO_numbers (s t ph N : ℕ) (hs : 1 ≤ s) (ht : 1 ≤ t) (hph : ph ≤ 1) (hN : 2 * s + 2 * t ≤ N) :
    (2 * s - 1) + (2 * t - 1) + ph < N := by omega

theorem thmO_ph2_fails : ¬ ((2 * 1 - 1) + (2 * 1 - 1) + 2 < 2 * 1 + 2 * 1) := by omega

end CallerBorrow2

#print axioms CallerBorrow2.d_isolation
#print axioms CallerBorrow2.d_isolation_stages
#print axioms CallerBorrow2.commute_neg_inv
#print axioms CallerBorrow2.lemmaI_core
#print axioms CallerBorrow2.lemmaI
#print axioms CallerBorrow2.lemmaI_pp
#print axioms CallerBorrow2.lemmaL_zero
#print axioms CallerBorrow2.L_eq_zero
#print axioms CallerBorrow2.lemmaL_K
#print axioms CallerBorrow2.lemmaL_zero_dual
#print axioms CallerBorrow2.thmO_step1
#print axioms CallerBorrow2.W_dim
#print axioms CallerBorrow2.thmO
#print axioms CallerBorrow2.thmO_numbers
