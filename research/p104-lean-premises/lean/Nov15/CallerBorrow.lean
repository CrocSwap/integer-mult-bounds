/-
CALLER BORROWING lemmas : formalisation of the audited lemmas of internal notes R1-R6
(AUDIT-ER, AUDIT-X, AUDIT-R5 fixes) in an abstract caller model.  See CallerBorrow.md.
Model: units T_s = 1 - 2 x_s y_s^T on coordinates `ι` over a field; partial product pp s = T_{s-1} ... T_0;
masks = coordinate sets (`pm m` = diagonal projector); a stage unit lies in a mask when x,y vanish off it;
prefix commutation at a stage = `Commute (pm m) (pp s)`; product -I = `pp n = -1`.
-/
import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.Matrix.SchurComplement
import Mathlib.Tactic.NoncommRing
import Mathlib.Tactic.Abel
import Nov15.SpecTSUR

open Matrix

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false
set_option linter.unusedSimpArgs false
set_option linter.unusedTactic false

namespace CallerBorrow

variable {ι : Type*} [Fintype ι] [DecidableEq ι] {K : Type*} [Field K]

/-! ## §0. model -/

/-- diagonal projector onto a coordinate set (a mask) -/
def pm (m : ι → Prop) [DecidablePred m] : Matrix ι ι K := diagonal fun i => if m i then 1 else 0

/-- unit `1 - 2 x y^T` -/
def unitM (x y : ι → K) : Matrix ι ι K := 1 - (2 : K) • vecMulVec x y

/-- partial product `T_{s-1} ... T_0` -/
def pp (x y : ℕ → ι → K) : ℕ → Matrix ι ι K
  | 0 => 1
  | s + 1 => unitM (x s) (y s) * pp x y s

/-- window product `T_{a+j-1} ... T_a` -/
def seg (x y : ℕ → ι → K) (a : ℕ) : ℕ → Matrix ι ι K
  | 0 => 1
  | j + 1 => unitM (x (a + j)) (y (a + j)) * seg x y a j

theorem pp_add (x y : ℕ → ι → K) (a j : ℕ) : pp x y (a + j) = seg x y a j * pp x y a := by
  induction j with
  | zero => simp [seg]
  | succ j ih =>
    rw [← add_assoc, pp, ih, seg, mul_assoc]

/-- a vector lies in the mask -/
def InMask (m : ι → Prop) (v : ι → K) : Prop := ∀ i, ¬ m i → v i = 0

variable (m : ι → Prop) [DecidablePred m]

theorem pm_mulVec {v : ι → K} (h : InMask m v) : pm m *ᵥ v = v := by
  funext i
  simp only [pm, mulVec_diagonal]
  by_cases hi : m i
  · simp [hi]
  · simp [hi, h i hi]

theorem vecMul_pm {v : ι → K} (h : InMask m v) : v ᵥ* pm m = v := by
  funext i
  simp only [pm, vecMul_diagonal]
  by_cases hi : m i
  · simp [hi]
  · simp [hi, h i hi]

theorem commute_pm_unit {x y : ι → K} (hx : InMask m x) (hy : InMask m y) :
    Commute (pm m) (unitM x y) := by
  unfold unitM
  refine (Commute.one_right _).sub_right (Commute.smul_right ?_ _)
  show pm m * vecMulVec x y = vecMulVec x y * pm m
  have h1 : pm m * vecMulVec x y = vecMulVec x y := by
    rw [Matrix.mul_vecMulVec, pm_mulVec m hx]
  have h2 : vecMulVec x y * pm m = vecMulVec x y := by
    rw [Matrix.vecMulVec_mul, vecMul_pm m hy]
  rw [h1, h2]

/-- isotropy `y . x = 0` makes the unit invertible (inverse `1 + 2 x y^T`). -/
theorem unitM_isUnit {x y : ι → K} (h : y ⬝ᵥ x = 0) : IsUnit (unitM x y) := by
  have hA : vecMulVec x y * vecMulVec x y = 0 := by
    rw [Matrix.vecMulVec_mul_vecMulVec, h]; simp
  refine ⟨⟨unitM x y, 1 + (2 : K) • vecMulVec x y, ?_, ?_⟩, rfl⟩
  · unfold unitM
    simp [sub_mul, mul_add, smul_mul_assoc, mul_smul_comm, hA]
  · unfold unitM
    simp [sub_mul, mul_sub, add_mul, smul_mul_assoc, mul_smul_comm, hA]

theorem pm_mulVec_apply (v : ι → K) (i : ι) :
    (pm m *ᵥ v) i = if m i then v i else 0 := by
  simp [pm, mulVec_diagonal]

theorem vecMul_pm_apply (v : ι → K) (i : ι) :
    (v ᵥ* pm m) i = if m i then v i else 0 := by
  simp [pm, vecMul_diagonal, mul_comm]

theorem pm_mulVec_self (v : ι → K) :
    pm m *ᵥ (pm m *ᵥ v) = pm m *ᵥ v := by
  apply pm_mulVec; intro i hi; rw [pm_mulVec_apply]; simp [hi]

theorem vecMul_pm_self (v : ι → K) :
    (v ᵥ* pm m) ᵥ* pm m = v ᵥ* pm m := by
  apply vecMul_pm; intro i hi; rw [vecMul_pm_apply]; simp [hi]

/-! ## §1. Lemma E (AUDIT-ER: SOUND) -/

theorem commute_seg {x y : ℕ → ι → K} (a : ℕ) (d : ℕ)
    (hd : ∀ j, j < d → InMask m (x (a + j)) ∧ InMask m (y (a + j))) :
    Commute (pm m) (seg x y a d) := by
  induction d with
  | zero => simp [seg]
  | succ d ih =>
    rw [seg]
    exact (commute_pm_unit m (hd d (by omega)).1 (hd d (by omega)).2).mul_right
      (ih fun j hj => hd j (by omega))

theorem isUnit_seg {x y : ℕ → ι → K} (hu : ∀ s, IsUnit (unitM (x s) (y s))) (a d : ℕ) :
    IsUnit (seg x y a d) := by
  induction d with
  | zero => simp [seg]
  | succ d ih => rw [seg]; exact (hu _).mul ih

/-- **Lemma E.**  If every earlier-window unit `a ≤ j < s` (thins included) lies in `mask(s)` and the
prefix before the stage `s` commutes with `mask(s)`, the cut prefix `pp a` is block-diagonal for `mask(s)`. -/
theorem lemmaE {x y : ℕ → ι → K} (hu : ∀ s, IsUnit (unitM (x s) (y s))) (a s : ℕ) (has : a ≤ s)
    (hwin : ∀ j, a ≤ j → j < s → InMask m (x j) ∧ InMask m (y j))
    (hcomm : Commute (pm m) (pp x y s)) : Commute (pm m) (pp x y a) := by
  obtain ⟨d, rfl⟩ := Nat.exists_eq_add_of_le has
  have hseg : Commute (pm m) (seg x y a d) :=
    commute_seg m a d fun j hj => hwin (a + j) (by omega) (by omega)
  have hU := isUnit_seg hu a d
  rw [pp_add] at hcomm
  have h1 : seg x y a d * (pm m * pp x y a) = seg x y a d * (pp x y a * pm m) := by
    calc seg x y a d * (pm m * pp x y a) = pm m * (seg x y a d * pp x y a) := by
          rw [← mul_assoc, ← hseg.eq, mul_assoc]
      _ = (seg x y a d * pp x y a) * pm m := hcomm.eq
      _ = _ := by rw [mul_assoc]
  exact (hU.mul_right_inj).1 h1

/-- **Lemma E, dual.**  If every later unit `s ≤ j < a` of the window (stage `s` included) lies in `mask(s)`
and the prefix before `s` commutes with `mask(s)`, then `pp a` commutes with `mask(s)`. -/
theorem lemmaE_dual {x y : ℕ → ι → K} (s a : ℕ) (has : s ≤ a)
    (hwin : ∀ j, s ≤ j → j < a → InMask m (x j) ∧ InMask m (y j))
    (hcomm : Commute (pm m) (pp x y s)) : Commute (pm m) (pp x y a) := by
  obtain ⟨d, rfl⟩ := Nat.exists_eq_add_of_le has
  rw [pp_add]
  exact (commute_seg m s d fun j hj => hwin (s + j) (by omega) (by omega)).mul_right hcomm

/-! ## §2. Lemma R (re-basing at a cut; AUDIT-ER: SOUND-WITH-FIXES) -/

section Rebase
variable (Λ A : ι → Prop) [DecidablePred Λ] [DecidablePred A]

theorem pm_mul_pm_of_imp (h : ∀ i, A i → Λ i) : pm A * pm Λ = (pm A : Matrix ι ι K) := by
  unfold pm
  rw [diagonal_mul_diagonal]
  congr 1; funext i
  by_cases hA : A i
  · simp [hA, h i hA]
  · simp [hA]

theorem pm_comm (m : ι → Prop) [DecidablePred m] : Commute (pm m : Matrix ι ι K) (pm Λ) := by
  show _ * _ = _ * _
  unfold pm
  rw [diagonal_mul_diagonal, diagonal_mul_diagonal]
  congr 1; funext i; ring

/-- TS(5) memberships of a prefix unit: `x[Λ] ∈ V_-`, `y[Λ] ∈ ann V_+`. -/
def PreUnit (D : Matrix ι ι K) (Λ : ι → Prop) [DecidablePred Λ] (x y : ι → K) : Prop :=
  D *ᵥ (pm Λ *ᵥ x) = -(pm Λ *ᵥ x) ∧ (y ᵥ* pm Λ) ᵥ* D = -(y ᵥ* pm Λ)

/-- TS(5) memberships of a suffix unit: `x[Λ] ∈ V_+`, `y[Λ] ∈ ann V_-`. -/
def SufUnit (D : Matrix ι ι K) (Λ : ι → Prop) [DecidablePred Λ] (x y : ι → K) : Prop :=
  D *ᵥ (pm Λ *ᵥ x) = pm Λ *ᵥ x ∧ (y ᵥ* pm Λ) ᵥ* D = y ᵥ* pm Λ

/-! ### conjugation invariants -/

theorem inMask_iff (m : ι → Prop) [DecidablePred m] {v : ι → K} : InMask m v ↔ pm m *ᵥ v = v := by
  refine ⟨pm_mulVec m, fun h i hi => ?_⟩
  have := congrFun h i
  rw [pm_mulVec_apply] at this
  simpa [hi] using this.symm

theorem inMask_iff_vec (m : ι → Prop) [DecidablePred m] {v : ι → K} : InMask m v ↔ v ᵥ* pm m = v := by
  refine ⟨vecMul_pm m, fun h i hi => ?_⟩
  have := congrFun h i
  rw [vecMul_pm_apply] at this
  simpa [hi] using this.symm

theorem conj_vecMulVec (g G : Matrix ι ι K) (x y : ι → K) :
    g * vecMulVec x y * G = vecMulVec (g *ᵥ x) (y ᵥ* G) := by
  rw [Matrix.mul_vecMulVec, Matrix.vecMulVec_mul]

theorem conj_unit {g G : Matrix ι ι K} (hgG : g * G = 1) (x y : ι → K) :
    unitM (g *ᵥ x) (y ᵥ* G) = g * unitM x y * G := by
  unfold unitM
  rw [← conj_vecMulVec]
  simp only [mul_sub, sub_mul, mul_one, hgG, mul_smul_comm, smul_mul_assoc]

theorem conj_pp {g G : Matrix ι ι K} (hgG : g * G = 1) (hGg : G * g = 1) (x y : ℕ → ι → K) (s : ℕ) :
    pp (fun t => g *ᵥ x t) (fun t => y t ᵥ* G) s = g * pp x y s * G := by
  induction s with
  | zero => simp [pp, hgG]
  | succ s ih =>
    rw [pp, ih, pp, conj_unit hgG]
    calc g * unitM (x s) (y s) * G * (g * pp x y s * G)
        = g * unitM (x s) (y s) * (G * g) * pp x y s * G := by simp only [mul_assoc]
      _ = g * (unitM (x s) (y s) * pp x y s) * G := by rw [hGg]; simp only [mul_assoc, mul_one]

theorem conj_dot {g G : Matrix ι ι K} (hGg : G * g = 1) (y x : ι → K) :
    (y ᵥ* G) ⬝ᵥ (g *ᵥ x) = y ⬝ᵥ x := by
  rw [dotProduct_mulVec, vecMul_vecMul, hGg, vecMul_one]

/-- A matrix equal to the identity off `Λ` and commuting with `π_Λ` commutes with every mask that
contains `Λ` or misses it (a line class). -/
theorem commute_of_line (Λ m : ι → Prop) [DecidablePred Λ] [DecidablePred m] (M : Matrix ι ι K)
    (h1 : M * pm Λ = pm Λ * M) (h2 : M * (1 - pm Λ) = 1 - pm Λ)
    (hm : (pm m : Matrix ι ι K) * pm Λ = pm Λ ∨ (pm m : Matrix ι ι K) * pm Λ = 0) : Commute (pm m) M := by
  have hc : pm m * pm Λ = (pm Λ : Matrix ι ι K) * pm m := (pm_comm Λ m).eq
  have e1 : M = M * pm Λ + (1 - pm Λ) := by
    rw [← h2]; noncomm_ring
  show pm m * M = M * pm m
  rcases hm with h | h
  · have h' : (pm Λ : Matrix ι ι K) * pm m = pm Λ := by rw [← hc, h]
    calc pm m * M = pm m * (M * pm Λ + (1 - pm Λ)) := by rw [← e1]
      _ = pm m * (pm Λ * M) + (pm m - pm m * pm Λ) := by rw [← h1]; noncomm_ring
      _ = pm Λ * M + (pm m - pm Λ) := by rw [← mul_assoc, h]
      _ = M * pm Λ + (pm m - pm Λ) := by rw [h1]
      _ = (M * pm Λ + (1 - pm Λ)) * pm m := by
          rw [add_mul, mul_assoc, h', sub_mul, one_mul, h']
      _ = M * pm m := by rw [← e1]
  · have h' : (pm Λ : Matrix ι ι K) * pm m = 0 := by rw [← hc, h]
    calc pm m * M = pm m * (M * pm Λ + (1 - pm Λ)) := by rw [← e1]
      _ = pm m * (pm Λ * M) + (pm m - pm m * pm Λ) := by rw [← h1]; noncomm_ring
      _ = pm m := by rw [← mul_assoc, h]; simp
      _ = (M * pm Λ + (1 - pm Λ)) * pm m := by
          rw [add_mul, mul_assoc, h', sub_mul, one_mul, h']; simp
      _ = M * pm m := by rw [← e1]

/-- Data of a re-basing `g = G⁻¹` at a cut: `Λ` is the coordinate set of the E-atom/line class, `D` the
involution `D_Λ` of TS(5), `G` has columns `(basis V_-, basis V_+)` indexed by `(A, Λ \ A)`, `G = 1` off `Λ`. -/
structure RebaseData (D G g : Matrix ι ι K) : Prop where
  hA : ∀ i, A i → Λ i
  hgG : g * G = 1
  hGg : G * g = 1
  hGπ : G * pm Λ = pm Λ * G
  hGoff : G * (1 - pm Λ) = 1 - pm Λ
  hDa : D * G * pm A = -(G * pm A)
  hDb : D * G * (pm Λ - pm A) = G * (pm Λ - pm A)

theorem half_eq {a : ι → K} (h2 : (2 : K) ≠ 0) (h : a + a = 0) : a = 0 := by
  have : (2 : K) • a = 0 := by rw [two_smul, h]
  rcases smul_eq_zero.1 this with h | h
  · exact absurd h h2
  · exact h

variable {Λ A} {D G g : Matrix ι ι K} (R : RebaseData Λ A D G g)
include R

theorem RebaseData.hgG' (X : Matrix ι ι K) : g * (G * X) = X := by rw [← mul_assoc, R.hgG, one_mul]
theorem RebaseData.hGg' (X : Matrix ι ι K) : G * (g * X) = X := by rw [← mul_assoc, R.hGg, one_mul]

theorem RebaseData.hgπ : g * pm Λ = pm Λ * g := by
  calc g * pm Λ = g * pm Λ * (G * g) := by rw [R.hGg, mul_one]
    _ = g * (pm Λ * G) * g := by simp only [mul_assoc]
    _ = g * (G * pm Λ) * g := by rw [R.hGπ]
    _ = pm Λ * g := by simp only [mul_assoc]; exact R.hgG' _

/-- shared core of the vector statements: `w = G c`, `c = a c + b c`. -/
theorem RebaseData.vec_split {w : ι → K} (hw : pm Λ *ᵥ w = w) :
    G *ᵥ (g *ᵥ w) = w ∧ pm Λ *ᵥ (g *ᵥ w) = g *ᵥ w ∧
    g *ᵥ w = pm A *ᵥ (g *ᵥ w) + (pm Λ - pm A) *ᵥ (g *ᵥ w) := by
  set c := g *ᵥ w with hc
  have hGc : G *ᵥ c = w := by rw [hc, mulVec_mulVec, R.hGg, one_mulVec]
  have hπc : pm Λ *ᵥ c = c := by
    rw [hc, mulVec_mulVec, ← R.hgπ, ← mulVec_mulVec, hw]
  refine ⟨hGc, hπc, ?_⟩
  rw [sub_mulVec, add_sub_cancel, hπc]

theorem RebaseData.vec_D {w : ι → K} (hw : pm Λ *ᵥ w = w) :
    D *ᵥ w = -(G *ᵥ (pm A *ᵥ (g *ᵥ w))) + G *ᵥ ((pm Λ - pm A) *ᵥ (g *ᵥ w)) := by
  obtain ⟨hGc, -, hsplit⟩ := R.vec_split (A := A) hw
  set c := g *ᵥ w with hc
  have h1 := congrArg (fun M : Matrix ι ι K => M *ᵥ c) R.hDa
  have h2 := congrArg (fun M : Matrix ι ι K => M *ᵥ c) R.hDb
  simp only [neg_mulVec, ← mulVec_mulVec] at h1 h2
  conv_lhs => rw [← hGc, hsplit, mulVec_add, mulVec_add]
  rw [h1, h2]

/-- vectors in `V_-` (`D w = -w`, supported in Λ) are sent by `g` into the A-coordinates. -/
theorem RebaseData.vec_pre (h2 : (2 : K) ≠ 0) {w : ι → K} (hw : pm Λ *ᵥ w = w) (hD : D *ᵥ w = -w) :
    pm A *ᵥ (g *ᵥ w) = g *ᵥ w := by
  obtain ⟨hGc, -, hsplit⟩ := R.vec_split (A := A) hw
  have h1 := R.vec_D (A := A) hw
  set c := g *ᵥ w with hc
  clear_value c
  have h3 : G *ᵥ (pm A *ᵥ c) + G *ᵥ ((pm Λ - pm A) *ᵥ c) = w := by
    rw [← mulVec_add, ← hsplit, hGc]
  rw [hD, ← h3, neg_add] at h1
  have h5 := add_left_cancel h1
  have h6 : G *ᵥ ((pm Λ - pm A) *ᵥ c) = 0 := half_eq h2 (neg_eq_iff_add_eq_zero.1 h5)
  have h7 : (pm Λ - pm A) *ᵥ c = 0 := by
    calc (pm Λ - pm A) *ᵥ c = g *ᵥ (G *ᵥ ((pm Λ - pm A) *ᵥ c)) := by
          rw [mulVec_mulVec, R.hgG, one_mulVec]
      _ = 0 := by rw [h6, mulVec_zero]
  rw [h7, add_zero] at hsplit
  exact hsplit.symm

/-- vectors in `V_+` (`D w = w`, supported in Λ) are sent by `g` into the complementary coordinates `Λ \ A`. -/
theorem RebaseData.vec_suf (h2 : (2 : K) ≠ 0) {w : ι → K} (hw : pm Λ *ᵥ w = w) (hD : D *ᵥ w = w) :
    pm A *ᵥ (g *ᵥ w) = 0 := by
  obtain ⟨hGc, -, hsplit⟩ := R.vec_split (A := A) hw
  have h1 := R.vec_D (A := A) hw
  set c := g *ᵥ w with hc
  clear_value c
  have h3 : G *ᵥ (pm A *ᵥ c) + G *ᵥ ((pm Λ - pm A) *ᵥ c) = w := by
    rw [← mulVec_add, ← hsplit, hGc]
  rw [hD, ← h3] at h1
  have h5 := add_right_cancel h1
  have h6 : G *ᵥ (pm A *ᵥ c) = 0 := half_eq h2 (eq_neg_iff_add_eq_zero.1 h5)
  calc pm A *ᵥ c = g *ᵥ (G *ᵥ (pm A *ᵥ c)) := by
        rw [mulVec_mulVec, R.hgG, one_mulVec]
    _ = 0 := by rw [h6, mulVec_zero]

theorem RebaseData.row_split {v : ι → K} (hv : v ᵥ* pm Λ = v) :
    (v ᵥ* G) ᵥ* pm Λ = v ᵥ* G ∧
    v ᵥ* G = (v ᵥ* G) ᵥ* pm A + (v ᵥ* G) ᵥ* (pm Λ - pm A) := by
  have hπ : (v ᵥ* G) ᵥ* pm Λ = v ᵥ* G := by
    rw [vecMul_vecMul, R.hGπ, ← vecMul_vecMul, hv]
  refine ⟨hπ, ?_⟩
  rw [← vecMul_add, add_sub_cancel, hπ]

/-- covectors in `ann V_+` (`v D = -v`, supported in Λ): `v G` lies in the A-coordinates. -/
theorem RebaseData.row_pre (h2 : (2 : K) ≠ 0) {v : ι → K} (hv : v ᵥ* pm Λ = v) (hD : v ᵥ* D = -v) :
    (v ᵥ* G) ᵥ* pm A = v ᵥ* G := by
  obtain ⟨-, hsplit⟩ := R.row_split (A := A) hv
  have e := congrArg (fun M : Matrix ι ι K => v ᵥ* M) R.hDb
  simp only [← vecMul_vecMul, hD, neg_vecMul] at e
  have h6 : (v ᵥ* G) ᵥ* (pm Λ - pm A) = 0 := half_eq h2 (neg_eq_iff_add_eq_zero.1 e)
  rw [h6, add_zero] at hsplit
  exact hsplit.symm

/-- covectors in `ann V_-` (`v D = v`, supported in Λ): `v G` lies in the complementary coordinates. -/
theorem RebaseData.row_suf (h2 : (2 : K) ≠ 0) {v : ι → K} (hv : v ᵥ* pm Λ = v) (hD : v ᵥ* D = v) :
    (v ᵥ* G) ᵥ* pm A = 0 := by
  have e := congrArg (fun M : Matrix ι ι K => v ᵥ* M) R.hDa
  simp only [← vecMul_vecMul, hD, vecMul_neg] at e
  exact half_eq h2 (eq_neg_iff_add_eq_zero.1 e)

theorem RebaseData.x_on_Λ (x : ι → K) {i : ι} (hΛ : Λ i) :
    (g *ᵥ x) i = (g *ᵥ (pm Λ *ᵥ x)) i := by
  have : pm Λ *ᵥ (g *ᵥ x) = g *ᵥ (pm Λ *ᵥ x) := by
    rw [mulVec_mulVec, mulVec_mulVec, ← R.hgπ]
  rw [← this, pm_mulVec_apply]; simp [hΛ]

theorem RebaseData.y_on_Λ (y : ι → K) {i : ι} (hΛ : Λ i) :
    (y ᵥ* G) i = ((y ᵥ* pm Λ) ᵥ* G) i := by
  have : (y ᵥ* G) ᵥ* pm Λ = (y ᵥ* pm Λ) ᵥ* G := by
    rw [vecMul_vecMul, vecMul_vecMul, R.hGπ]
  rw [← this, vecMul_pm_apply]; simp [hΛ]

/-- confinement of the rebased vectors on Λ, prefix side: touches only the A-coordinates. -/
theorem RebaseData.pre_conf (h2 : (2 : K) ≠ 0) {x y : ι → K} (hu : PreUnit D Λ x y) :
    (∀ i, Λ i → ¬ A i → (g *ᵥ x) i = 0) ∧ (∀ i, Λ i → ¬ A i → (y ᵥ* G) i = 0) := by
  constructor
  · intro i hΛ hA
    have h' := congrFun (R.vec_pre (A := A) h2 (pm_mulVec_self Λ x) hu.1) i
    rw [pm_mulVec_apply] at h'
    rw [R.x_on_Λ x hΛ, ← h']; simp [hA]
  · intro i hΛ hA
    have h' := congrFun (R.row_pre (A := A) h2 (vecMul_pm_self Λ y) hu.2) i
    rw [vecMul_pm_apply] at h'
    rw [R.y_on_Λ y hΛ, ← h']; simp [hA]

/-- suffix side: touches only the coordinates of Λ outside A. -/
theorem RebaseData.suf_conf (h2 : (2 : K) ≠ 0) {x y : ι → K} (hu : SufUnit D Λ x y) :
    (∀ i, Λ i → A i → (g *ᵥ x) i = 0) ∧ (∀ i, Λ i → A i → (y ᵥ* G) i = 0) := by
  constructor
  · intro i hΛ hA
    have h' := congrFun (R.vec_suf (A := A) h2 (pm_mulVec_self Λ x) hu.1) i
    rw [pm_mulVec_apply] at h'
    rw [R.x_on_Λ x hΛ]; simpa [hA] using h'
  · intro i hΛ hA
    have h' := congrFun (R.row_suf (A := A) h2 (vecMul_pm_self Λ y) hu.2) i
    rw [vecMul_pm_apply] at h'
    rw [R.y_on_Λ y hΛ]; simpa [hA] using h'

/-- **Lemma R, conclusion.** After re-basing, no role of Λ is touched on both sides of the cut. -/
theorem RebaseData.not_both (h2 : (2 : K) ≠ 0) {x y x' y' : ι → K}
    (hp : PreUnit D Λ x y) (hs : SufUnit D Λ x' y') {i : ι} (hΛ : Λ i) :
    ¬ (((g *ᵥ x) i ≠ 0 ∨ (y ᵥ* G) i ≠ 0) ∧ ((g *ᵥ x') i ≠ 0 ∨ (y' ᵥ* G) i ≠ 0)) := by
  rintro ⟨h1, h3⟩
  by_cases hA : A i
  · have := R.suf_conf (A := A) h2 hs
    rcases h3 with h3 | h3
    · exact h3 (this.1 i hΛ hA)
    · exact h3 (this.2 i hΛ hA)
  · have := R.pre_conf (A := A) h2 hp
    rcases h1 with h1 | h1
    · exact h1 (this.1 i hΛ hA)
    · exact h1 (this.2 i hΛ hA)

theorem RebaseData.g_off : g * (1 - pm Λ) = 1 - pm Λ := by
  have := congrArg (fun X => g * X) R.hGoff
  simpa only [R.hgG'] using this.symm

theorem RebaseData.commute_g (m : ι → Prop) [DecidablePred m]
    (hm : (pm m : Matrix ι ι K) * pm Λ = pm Λ ∨ (pm m : Matrix ι ι K) * pm Λ = 0) :
    Commute (pm m) g ∧ Commute (pm m) G :=
  ⟨commute_of_line Λ m g R.hgπ R.g_off hm, commute_of_line Λ m G R.hGπ R.hGoff hm⟩

/-- **Lemma R (packaged).**  Conjugating every unit by `g` (`x ↦ g x`, `y ↦ y G`) gives a tuple with
the same unit products up to conjugation, product `-I`, all pairings `y_s . x_t` (isotropy and every `t`),
the same stage masks and prefix commutations (for masks that contain Λ or miss it), and
prefix/suffix units touching complementary coordinates of Λ. -/
theorem RebaseData.lemmaR (h2 : (2 : K) ≠ 0) (x y : ℕ → ι → K) (n : ℕ) (hprod : pp x y n = -1) :
    (∀ s, pp (fun t => g *ᵥ x t) (fun t => y t ᵥ* G) s = g * pp x y s * G) ∧
    pp (fun t => g *ᵥ x t) (fun t => y t ᵥ* G) n = -1 ∧
    (∀ s t, (y s ᵥ* G) ⬝ᵥ (g *ᵥ x t) = y s ⬝ᵥ x t) ∧
    (∀ (m : ι → Prop) [DecidablePred m], ((pm m : Matrix ι ι K) * pm Λ = pm Λ ∨ (pm m : Matrix ι ι K) * pm Λ = 0) →
      ∀ s, (InMask m (x s) → InMask m (g *ᵥ x s)) ∧ (InMask m (y s) → InMask m (y s ᵥ* G)) ∧
        (Commute (pm m) (pp x y s) ↔
          Commute (pm m) (pp (fun t => g *ᵥ x t) (fun t => y t ᵥ* G) s))) := by
  refine ⟨conj_pp R.hgG R.hGg x y, ?_, fun s t => conj_dot R.hGg _ _, ?_⟩
  · rw [conj_pp R.hgG R.hGg, hprod]
    calc g * -1 * G = -(g * G) := by noncomm_ring
      _ = -1 := by rw [R.hgG]
  · intro m _ hm s
    obtain ⟨hg, hG⟩ := R.commute_g m hm
    refine ⟨fun h => ?_, fun h => ?_, ?_⟩
    · rw [inMask_iff] at h ⊢
      rw [mulVec_mulVec, hg.eq, ← mulVec_mulVec, h]
    · rw [inMask_iff_vec] at h ⊢
      rw [vecMul_vecMul, ← hG.eq, ← vecMul_vecMul, h]
    · rw [conj_pp R.hgG R.hGg]
      constructor
      · intro h; exact (hg.mul_right h).mul_right hG
      · intro h
        have e : G * (g * pp x y s * G) * g = pp x y s := by
          calc G * (g * pp x y s * G) * g = (G * g) * pp x y s * (G * g) := by simp only [mul_assoc]
            _ = pp x y s := by rw [R.hGg]; simp
        rw [← e]
        exact (hG.mul_right h).mul_right hg

end Rebase

/-! ## §3. Lemma OS (one-sided shear; AUDIT-R5 hypotheses made explicit) -/

theorem half_zero {M : Type*} [AddCommGroup M] [Module K M] (h2 : (2 : K) ≠ 0) {a : M}
    (h : a + a = 0) : a = 0 := by
  have : (2 : K) • a = 0 := by rw [two_smul, h]
  rcases smul_eq_zero.1 this with h | h
  · exact absurd h h2
  · exact h

section OS

variable {ez ep es π F0 U Kq Lq G g : Matrix ι ι K}

/-- Block-coordinate data of the cut (z = off B, pre = B_pre, suf = B_suf): `ez,ep,es` orthogonal
idempotents summing to 1, `Kq : suf -> pre`, `Lq : pre -> suf` the off-diagonal parts of
`G = g⁻¹ = [[I,Kq],[Lq,I]]`, `F0` the part of `F_k` off B, `U` a product of units with no pre part,
`π` the projector onto the stage mask `N` (no pre part).  `D = G (es - ep) g` is the block `D_B` of
`F_k = F0 ⊕ D_B` (TS(5): `D_B = g⁻¹ J g`, `J = diag(-I_pre, I_suf)`). -/
structure OSData (ez ep es π F0 U Kq Lq G g : Matrix ι ι K) : Prop where
  zz : ez * ez = ez
  pp : ep * ep = ep
  ss : es * es = es
  zp : ez * ep = 0
  pz : ep * ez = 0
  zs : ez * es = 0
  sz : es * ez = 0
  ps : ep * es = 0
  sp : es * ep = 0
  sum : ez + ep + es = 1
  epK : ep * Kq = Kq
  Kes : Kq * es = Kq
  esL : es * Lq = Lq
  Lep : Lq * ep = Lq
  hG : G = 1 + Kq + Lq
  hgG : g * G = 1
  hGg : G * g = 1
  hF0 : F0 = ez * F0 * ez
  epU : ep * U = ep
  Uep : U * ep = ep
  epπ : ep * π = 0
  πep : π * ep = 0

variable (O : OSData ez ep es π F0 U Kq Lq G g)
include O

theorem OSData.hGg' (X : Matrix ι ι K) : G * (g * X) = X := by rw [← mul_assoc, O.hGg, one_mul]
theorem OSData.hgG' (X : Matrix ι ι K) : g * (G * X) = X := by rw [← mul_assoc, O.hgG, one_mul]

/-- the block `D_B = G (es - ep) g` -/
def OSD (es ep G g : Matrix ι ι K) : Matrix ι ι K := G * (es - ep) * g

/-! derived zero-products -/
theorem OSData.Kep : Kq * ep = 0 := by rw [← O.Kes, mul_assoc, O.sp, mul_zero]
theorem OSData.esK : es * Kq = 0 := by rw [← O.epK, ← mul_assoc, O.sp, zero_mul]
theorem OSData.Les : Lq * es = 0 := by rw [← O.Lep, mul_assoc, O.ps, mul_zero]
theorem OSData.epL : ep * Lq = 0 := by rw [← O.esL, ← mul_assoc, O.ps, zero_mul]
theorem OSData.Kez : Kq * ez = 0 := by rw [← O.Kes, mul_assoc, O.sz, mul_zero]
theorem OSData.ezK : ez * Kq = 0 := by rw [← O.epK, ← mul_assoc, O.zp, zero_mul]
theorem OSData.Lez : Lq * ez = 0 := by rw [← O.Lep, mul_assoc, O.pz, mul_zero]
theorem OSData.ezL : ez * Lq = 0 := by rw [← O.esL, ← mul_assoc, O.zs, zero_mul]
theorem OSData.LL : Lq * Lq = 0 := by
  calc Lq * Lq = Lq * (ep * (es * Lq)) := by rw [O.esL]; nth_rewrite 1 [← O.Lep]; simp only [mul_assoc]
    _ = 0 := by rw [← mul_assoc ep es, O.ps]; simp

theorem OSData.epG : ep * G = ep + Kq := by
  rw [O.hG]; simp only [mul_add, mul_one, O.epK, O.epL, add_zero]
theorem OSData.esG : es * G = es + Lq := by
  rw [O.hG]; simp only [mul_add, mul_one, O.esK, O.esL, add_zero]
theorem OSData.Gep : G * ep = ep + Lq := by
  rw [O.hG]; simp only [add_mul, one_mul, O.Kep, O.Lep, add_zero]
theorem OSData.Ges : G * es = es + Kq := by
  rw [O.hG]; simp only [add_mul, one_mul, O.Kes, O.Les, add_zero]
theorem OSData.ezG : ez * G = ez := by
  rw [O.hG]; simp only [mul_add, mul_one, O.ezK, O.ezL, add_zero]
theorem OSData.Gez : G * ez = ez := by
  rw [O.hG]; simp only [add_mul, one_mul, O.Kez, O.Lez, add_zero]
theorem OSData.gez : g * ez = ez := by
  calc g * ez = g * (G * ez) := by rw [O.Gez]
    _ = ez := O.hgG' ez
theorem OSData.ezg : ez * g = ez := by
  calc ez * g = (ez * G) * g := by rw [O.ezG]
    _ = ez := by rw [mul_assoc, O.hGg, mul_one]
theorem OSData.A1 : (ep + Kq) * g = ep := by
  rw [← O.epG, mul_assoc, O.hGg, mul_one]
theorem OSData.A2 : (es + Lq) * g = es := by
  rw [← O.esG, mul_assoc, O.hGg, mul_one]
theorem OSData.A3 : g * (ep + Lq) = ep := by
  rw [← O.Gep, O.hgG']
theorem OSData.A4 : g * (es + Kq) = es := by
  rw [← O.Ges, O.hgG']


theorem OSData.B1 : g * ep = ep * g * ep - Lq * (ep * g * ep) := by
  have hA2 : es * (g * ep) + Lq * (ep * g * ep) = 0 := by
    have h := congrArg (· * ep) O.A2
    simp only [add_mul, mul_assoc, O.sp] at h
    have e : Lq * (g * ep) = Lq * (ep * g * ep) := by
      conv_lhs => rw [← O.Lep]
      simp only [mul_assoc]
    rw [← e]; exact h
  have hes : es * (g * ep) = -(Lq * (ep * g * ep)) := eq_neg_of_add_eq_zero_left hA2
  calc g * ep = (ez + ep + es) * (g * ep) := by rw [O.sum, one_mul]
    _ = ez * (g * ep) + ep * (g * ep) + es * (g * ep) := by simp only [add_mul]
    _ = ep * g * ep - Lq * (ep * g * ep) := by
      rw [hes, ← mul_assoc ez g ep, O.ezg, O.zp, ← mul_assoc ep g ep]; abel

theorem OSData.C2 : (ep * g * ep) * (ep - Kq * Lq) = ep := by
  have h4 : ep * g * es + (ep * g * ep) * Kq = 0 := by
    have h := congrArg (ep * ·) O.A4
    simp only [mul_add, O.ps] at h
    have e : ep * (g * Kq) = (ep * g * ep) * Kq := by
      conv_lhs => rw [← O.epK]
      simp only [mul_assoc]
    rw [← e]; simpa only [mul_assoc] using h
  have h3 : ep * g * ep + (ep * g * es) * Lq = ep := by
    have h := congrArg (ep * ·) O.A3
    simp only [mul_add, O.pp] at h
    have e : ep * (g * Lq) = (ep * g * es) * Lq := by
      conv_lhs => rw [← O.esL]
      simp only [mul_assoc]
    rw [← e]; simpa only [mul_assoc] using h
  have h5 : ep * g * es = -((ep * g * ep) * Kq) := eq_neg_of_add_eq_zero_left h4
  have hpp : (ep * g * ep) * ep = ep * g * ep := by rw [mul_assoc, O.pp]
  calc (ep * g * ep) * (ep - Kq * Lq) = ep * g * ep + (ep * g * es) * Lq := by
        rw [mul_sub, hpp, h5]; simp only [neg_mul, mul_assoc]; abel
    _ = ep := h3


theorem OSData.epF0 : ep * F0 = 0 := by
  rw [O.hF0]; simp only [← mul_assoc, O.pz, zero_mul]
theorem OSData.F0ep : F0 * ep = 0 := by
  rw [O.hF0]; simp only [mul_assoc, O.zp, mul_zero]

theorem OSData.epD : ep * OSD es ep G g = (Kq - ep) * g := by
  have h : (ep + Kq) * (es - ep) = Kq - ep := by
    simp only [add_mul, mul_sub, O.ps, O.pp, O.Kes, O.Kep]; abel
  unfold OSD
  calc ep * (G * (es - ep) * g) = (ep * G) * (es - ep) * g := by simp only [mul_assoc]
    _ = (Kq - ep) * g := by rw [O.epG, h]

theorem OSData.Dep : OSD es ep G g * ep = -((ep + Lq + Lq + Kq * Lq) * (ep * g * ep)) := by
  have hg : g * ep = (ep - Lq) * (ep * g * ep) := by
    rw [O.B1, sub_mul]; congr 1; simp only [← mul_assoc, O.pp]
  have h1 : (es - ep) * (ep - Lq) = -Lq - ep := by
    simp only [mul_sub, sub_mul, O.sp, O.esL, O.pp, O.epL]; abel
  have h2 : G * (-Lq - ep) = -(ep + Lq + Lq + Kq * Lq) := by
    have hGL : G * Lq = Lq + Kq * Lq := by
      rw [O.hG]; simp only [add_mul, one_mul, O.LL, add_zero]
    rw [mul_sub, mul_neg, hGL, O.Gep]; abel
  unfold OSD
  calc G * (es - ep) * g * ep = G * ((es - ep) * (g * ep)) := by simp only [mul_assoc]
    _ = G * ((es - ep) * ((ep - Lq) * (ep * g * ep))) := by rw [hg]
    _ = (G * (-Lq - ep)) * (ep * g * ep) := by rw [← h1]; simp only [mul_assoc]
    _ = _ := by rw [h2, neg_mul]

theorem OSData.Dpi (hKπ : Kq * π = 0) (hgπ : g * π = π) : OSD es ep G g * π = es * π := by
  have h : G * es * π = es * π := by rw [O.Ges, add_mul, hKπ, add_zero]
  unfold OSD
  calc G * (es - ep) * g * π = G * ((es - ep) * π) := by rw [mul_assoc (G * (es - ep)), hgπ, mul_assoc]
    _ = G * es * π := by rw [sub_mul, O.epπ, sub_zero, mul_assoc]
    _ = es * π := h


theorem OSData.UK : U * Kq = Kq := by rw [← O.epK, ← mul_assoc, O.Uep]

theorem OSData.πK : π * Kq = 0 := by rw [← O.epK, ← mul_assoc, O.πep, zero_mul]

/-- commutation at the stage forces `K π = 0` (no unforced tilt reaches the stage mask) and `π U L = 0`. -/
theorem OSData.forced (h2 : (2 : K) ≠ 0)
    (H : π * (U * (F0 + OSD es ep G g)) = (U * (F0 + OSD es ep G g)) * π) :
    Kq * π = 0 ∧ π * U * Lq = 0 ∧ g * π = π := by
  have hE1 : (Kq - ep) * g * π = 0 := by
    have h := congrArg (ep * ·) H
    have l : ep * (π * (U * (F0 + OSD es ep G g))) = 0 := by rw [← mul_assoc, O.epπ, zero_mul]
    have r : ep * ((U * (F0 + OSD es ep G g)) * π) = (Kq - ep) * g * π := by
      calc ep * ((U * (F0 + OSD es ep G g)) * π) = (ep * U) * (F0 + OSD es ep G g) * π := by
            simp only [mul_assoc]
        _ = ep * (F0 + OSD es ep G g) * π := by rw [O.epU]
        _ = (Kq - ep) * g * π := by rw [mul_add, O.epF0, zero_add, O.epD]
    exact (l.symm.trans (h.trans r)).symm
  have hE2 : (ep + Kq) * g * π = 0 := by rw [O.A1, O.epπ]
  have e1 : Kq * g * π - ep * g * π = 0 := by
    calc Kq * g * π - ep * g * π = (Kq - ep) * g * π := by simp only [sub_mul]
      _ = 0 := hE1
  have e2 : ep * g * π + Kq * g * π = 0 := by
    calc ep * g * π + Kq * g * π = (ep + Kq) * g * π := by simp only [add_mul]
      _ = 0 := hE2
  have hE3 : Kq * g * π = 0 := half_zero h2 (by
    calc Kq * g * π + Kq * g * π = (Kq * g * π - ep * g * π) + (ep * g * π + Kq * g * π) := by abel
      _ = 0 := by rw [e1, e2, add_zero])
  have hE4 : ep * g * π = 0 := half_zero h2 (by
    calc ep * g * π + ep * g * π = (ep * g * π + Kq * g * π) - (Kq * g * π - ep * g * π) := by abel
      _ = 0 := by rw [e1, e2, sub_zero])
  have hE5 : g * π = π := by
    have hK : Kq * (g * π) = 0 := by rw [← mul_assoc, hE3]
    have hL : Lq * (g * π) = 0 := by
      calc Lq * (g * π) = Lq * (ep * (g * π)) := by
            conv_lhs => rw [← O.Lep]
            rw [mul_assoc]
        _ = 0 := by rw [← mul_assoc ep g π, hE4, mul_zero]
    calc g * π = G * (g * π) - Kq * (g * π) - Lq * (g * π) := by
          rw [O.hG]; simp only [add_mul, one_mul]; abel
      _ = π := by rw [O.hGg', hK, hL]; simp
  have hKπ : Kq * π = 0 := by rw [← hE5]; exact (by rw [← mul_assoc]; exact hE3)
  refine ⟨hKπ, ?_, hE5⟩
  -- the (suf, pre) block
  have hR0 : π * (U * (F0 + OSD es ep G g)) * ep = 0 := by
    calc π * (U * (F0 + OSD es ep G g)) * ep = ((U * (F0 + OSD es ep G g)) * π) * ep := by rw [H]
      _ = U * (F0 + OSD es ep G g) * (π * ep) := by simp only [mul_assoc]
      _ = 0 := by rw [O.πep, mul_zero]
  have hR1 : π * (U * (OSD es ep G g * ep)) = 0 := by
    have : π * (U * (F0 + OSD es ep G g)) * ep = π * (U * (OSD es ep G g * ep)) := by
      simp only [mul_add, add_mul, mul_assoc, O.F0ep, mul_zero, zero_add]
    rw [← this]; exact hR0
  rw [O.Dep] at hR1
  set Δ := ep * g * ep with hΔ
  have hR2 : (π * U * Lq * Δ) + (π * U * Lq * Δ) = 0 := by
    have e : π * (U * (-((ep + Lq + Lq + Kq * Lq) * Δ))) = -((π * U * Lq * Δ) + (π * U * Lq * Δ)) := by
      have a1 : π * U * ep = 0 := by rw [mul_assoc, O.Uep, O.πep]
      have a2 : π * U * (Kq * Lq) = 0 := by
        calc π * U * (Kq * Lq) = π * (U * Kq) * Lq := by simp only [mul_assoc]
          _ = 0 := by rw [O.UK, O.πK, zero_mul]
      calc π * (U * (-((ep + Lq + Lq + Kq * Lq) * Δ)))
          = -(π * U * ep * Δ + π * U * Lq * Δ + π * U * Lq * Δ + π * U * (Kq * Lq) * Δ) := by
            simp only [mul_neg, neg_inj, add_mul, mul_add, mul_assoc]
        _ = _ := by rw [a1, a2]; simp
    rw [e] at hR1
    have := neg_eq_zero.1 hR1
    exact this
  have hR3 : π * U * Lq * Δ = 0 := half_zero h2 hR2
  calc π * U * Lq = π * U * Lq * ep := by rw [mul_assoc (π * U), O.Lep]
    _ = (π * U * Lq * Δ) * (ep - Kq * Lq) := by rw [mul_assoc (π * U * Lq), hΔ, O.C2]
    _ = 0 := by rw [hR3, zero_mul]


theorem OSData.πD (hπUL : π * U * Lq = 0) : π * U * OSD es ep G g = π * U * (es - ep) := by
  have a1 : π * U * ep = 0 := by rw [mul_assoc, O.Uep, O.πep]
  have hUG : π * U * G = π * U := by
    have a2 : π * U * Kq = 0 := by rw [mul_assoc, O.UK, ← O.epK, ← mul_assoc, O.πep, zero_mul]
    rw [O.hG]; simp only [mul_add, mul_one, a2, hπUL, add_zero]
  have hX : π * U * es * g = π * U * es := by
    have hXG : π * U * es * G = π * U * es := by
      have b1 : π * U * es * Kq = 0 := by rw [mul_assoc (π * U), O.esK, mul_zero]
      have b2 : π * U * es * Lq = 0 := by rw [mul_assoc (π * U), O.esL, hπUL]
      rw [O.hG]; simp only [mul_add, mul_one, b1, b2, add_zero]
    calc π * U * es * g = π * U * es * G * g := by rw [hXG]
      _ = π * U * es := by rw [mul_assoc _ G, O.hGg, mul_one]
  unfold OSD
  calc π * U * (G * (es - ep) * g) = (π * U * G) * (es - ep) * g := by simp only [mul_assoc]
    _ = π * U * es * g - π * U * ep * g := by rw [hUG]; simp only [mul_sub, sub_mul]
    _ = π * U * (es - ep) := by rw [hX, a1, zero_mul, mul_sub, a1, sub_zero]

theorem OSData.conjF : g * (F0 + OSD es ep G g) * G = F0 + (es - ep) := by
  have h1 : g * F0 * G = F0 := by
    calc g * F0 * G = g * (ez * F0 * ez) * G := by rw [← O.hF0]
      _ = (g * ez) * F0 * (ez * G) := by simp only [mul_assoc]
      _ = F0 := by rw [O.gez, O.ezG, ← O.hF0]
  have h2 : g * OSD es ep G g * G = es - ep := by
    unfold OSD
    calc g * (G * (es - ep) * g) * G = (g * G) * (es - ep) * (g * G) := by simp only [mul_assoc]
      _ = es - ep := by rw [O.hgG]; simp
  rw [mul_add, add_mul, h1, h2]

/-- **Lemma OS.**  Hypotheses (AUDIT-R5): the cut block structure `OSData` (all units between the cut and the
stage `N` form `U`, a product of stage units with no pre part, `π` the mask of `N` with no pre part),
the sheared tuple fixes `U` (`g U g⁻¹ = U`, true when the stage vectors of `U` are fixed by `g`, see
`fixed_conj`), and the original commutation `π (U F) = (U F) π`.
Conclusions: the commutation FORCES `K π = 0` and `π U L = 0`, and the sheared partial product
`g (U F) g⁻¹ = U (F0 ⊕ J)` commutes with `π`. -/
theorem OSData.os (h2 : (2 : K) ≠ 0) (hU' : g * U * G = U)
    (H : π * (U * (F0 + OSD es ep G g)) = (U * (F0 + OSD es ep G g)) * π) :
    Kq * π = 0 ∧ π * U * Lq = 0 ∧
    g * (U * (F0 + OSD es ep G g)) * G = U * (F0 + (es - ep)) ∧
    π * (U * (F0 + (es - ep))) = (U * (F0 + (es - ep))) * π := by
  obtain ⟨hK, hL, hgπ⟩ := O.forced h2 H
  have hconj : g * (U * (F0 + OSD es ep G g)) * G = U * (F0 + (es - ep)) := by
    calc g * (U * (F0 + OSD es ep G g)) * G
        = (g * U * G) * (g * (F0 + OSD es ep G g) * G) := by
          have : g * U * (G * g) * (F0 + OSD es ep G g) * G = g * (U * (F0 + OSD es ep G g)) * G := by
            rw [O.hGg]; simp only [mul_assoc, mul_one]
          rw [← this]; simp only [mul_assoc]
      _ = U * (F0 + (es - ep)) := by rw [hU', O.conjF]
  refine ⟨hK, hL, hconj, ?_⟩
  have hπD := O.πD hL
  have hDπ := O.Dpi hK hgπ
  have hJπ : (es - ep) * π = es * π := by rw [sub_mul, O.epπ, sub_zero]
  have e1 : π * (U * (es - ep)) = π * (U * OSD es ep G g) := by
    rw [← mul_assoc, ← mul_assoc, hπD]
  calc π * (U * (F0 + (es - ep))) = π * (U * F0) + π * (U * (es - ep)) := by simp only [mul_add]
    _ = π * (U * F0) + π * (U * OSD es ep G g) := by rw [e1]
    _ = π * (U * (F0 + OSD es ep G g)) := by simp only [mul_add]
    _ = (U * (F0 + OSD es ep G g)) * π := H
    _ = U * F0 * π + U * (OSD es ep G g * π) := by simp only [mul_add, add_mul, mul_assoc]
    _ = U * F0 * π + U * ((es - ep) * π) := by rw [hDπ, hJπ]
    _ = (U * (F0 + (es - ep))) * π := by simp only [mul_add, add_mul, mul_assoc]


/-- A stage-unit vector with no pre part lying in `V_+` (`D x_B = x_B`) is fixed by the shear `g`
(R4 (ii)); hypotheses: `ep x = 0` and `D x = es x` (the B-part of `x` is `es x`, `D` kills `ez`). -/
theorem OSData.fixed_vec (h2 : (2 : K) ≠ 0) {x : ι → K} (hx : ep *ᵥ x = 0)
    (hD : OSD es ep G g *ᵥ x = es *ᵥ x) : g *ᵥ x = x := by
  have hGc : G *ᵥ (g *ᵥ x) = x := by rw [mulVec_mulVec, O.hGg, one_mulVec]
  set c := g *ᵥ x with hc
  clear_value c
  have hsplit : x = ez *ᵥ x + es *ᵥ x := by
    have : (ez + ep + es) *ᵥ x = x := by rw [O.sum, one_mulVec]
    rw [add_mulVec, add_mulVec, hx] at this
    simpa using this.symm
  have hDx : OSD es ep G g *ᵥ x = G *ᵥ ((es - ep) *ᵥ c) := by
    unfold OSD; rw [hc]; simp only [← mulVec_mulVec]
  have h1 : (es - ep) *ᵥ c = g *ᵥ (es *ᵥ x) := by
    have : G *ᵥ ((es - ep) *ᵥ c) = es *ᵥ x := by rw [← hDx, hD]
    calc (es - ep) *ᵥ c = g *ᵥ (G *ᵥ ((es - ep) *ᵥ c)) := by
          rw [mulVec_mulVec, O.hgG, one_mulVec]
      _ = _ := by rw [this]
  have e : g *ᵥ (ez *ᵥ x) = ez *ᵥ x := by rw [mulVec_mulVec, O.gez]
  have h2' : c = ez *ᵥ x + g *ᵥ (es *ᵥ x) := by
    calc c = g *ᵥ x := hc
      _ = g *ᵥ (ez *ᵥ x + es *ᵥ x) := by rw [← hsplit]
      _ = _ := by rw [mulVec_add, e]
  have h2'' : g *ᵥ (es *ᵥ x) = c - ez *ᵥ x := by rw [h2']; abel
  rw [h2''] at h1
  have h3 : ep *ᵥ c = 0 := by
    have a : ep *ᵥ ((es - ep) *ᵥ c) = -(ep *ᵥ c) := by
      rw [mulVec_mulVec, mul_sub, O.ps, O.pp, zero_sub, neg_mulVec]
    have b : ep *ᵥ (c - ez *ᵥ x) = ep *ᵥ c := by
      rw [mulVec_sub, mulVec_mulVec, O.pz, zero_mulVec, sub_zero]
    have := congrArg (fun v => ep *ᵥ v) h1
    simp only [a, b] at this
    exact half_zero h2 (neg_eq_iff_add_eq_zero.1 this)
  have hesc : es *ᵥ c = c - ez *ᵥ x := by
    rw [← h1, sub_mulVec, h3, sub_zero]
  have hx2 : x = es *ᵥ c + Kq *ᵥ c + ez *ᵥ x := by
    have : x = G *ᵥ (es *ᵥ c + ez *ᵥ x) := by
      rw [hesc]; simp only [sub_add_cancel]; exact hGc.symm
    rw [mulVec_add, mulVec_mulVec, mulVec_mulVec, O.Ges, O.Gez, add_mulVec] at this
    exact this
  have hKc : Kq *ᵥ c = 0 := by
    have := congrArg (fun v => ep *ᵥ v) hx2
    simp only [hx, mulVec_add, mulVec_mulVec, O.ps, O.epK, O.pz, zero_mulVec] at this
    simpa using this.symm
  have hfin : x = es *ᵥ c + ez *ᵥ x := by
    rw [hKc, add_zero] at hx2; exact hx2
  calc c = es *ᵥ c + ez *ᵥ x := by rw [hesc]; abel
    _ = x := hfin.symm


/-- covector version of `fixed_vec`: `y ep = 0` and `y D = y es` give `y G = y`. -/
theorem OSData.fixed_row (h2 : (2 : K) ≠ 0) {y : ι → K} (hy : y ᵥ* ep = 0)
    (hD : y ᵥ* OSD es ep G g = y ᵥ* es) : y ᵥ* G = y := by
  have hyK : y ᵥ* Kq = 0 := by
    have : y ᵥ* Kq = y ᵥ* (ep * Kq) := by rw [O.epK]
    rw [this, ← vecMul_vecMul, hy, zero_vecMul]
  have hr : y ᵥ* G = y + y ᵥ* Lq := by
    rw [O.hG, vecMul_add, vecMul_add, vecMul_one, hyK, add_zero]
  have key : y ᵥ* (G * (es - ep)) = y ᵥ* (es + Lq) := by
    have e1 : (y ᵥ* OSD es ep G g) ᵥ* G = y ᵥ* (G * (es - ep)) := by
      unfold OSD
      rw [vecMul_vecMul]; congr 1
      calc G * (es - ep) * g * G = G * (es - ep) * (g * G) := by simp only [mul_assoc]
        _ = G * (es - ep) := by rw [O.hgG, mul_one]
    rw [← e1, hD, vecMul_vecMul, O.esG]
  have hl : y ᵥ* (G * (es - ep)) = y ᵥ* es - y ᵥ* Lq := by
    rw [← vecMul_vecMul, hr, vecMul_sub, add_vecMul, add_vecMul, vecMul_vecMul, vecMul_vecMul, O.Les, O.Lep]
    simp [hy]
  rw [hl, vecMul_add] at key
  have h5 : y ᵥ* Lq + y ᵥ* Lq = 0 := by
    have h7 : -(y ᵥ* Lq + y ᵥ* Lq) = 0 := by
      have := sub_eq_zero.2 key
      rw [← this]; abel
    exact neg_eq_zero.1 h7
  rw [hr, half_zero h2 h5, add_zero]


end OS

section NearFar
variable {ez ep es π F0 Kq Lq G g : Matrix ι ι K}

theorem ep_unit {e : Matrix ι ι K} {x y : ι → K} (hx : e *ᵥ x = 0) : e * unitM x y = e := by
  unfold unitM
  rw [mul_sub, mul_one, mul_smul_comm, Matrix.mul_vecMulVec, hx]
  simp

theorem unit_ep {e : Matrix ι ι K} {x y : ι → K} (hy : y ᵥ* e = 0) : unitM x y * e = e := by
  unfold unitM
  rw [sub_mul, one_mul, smul_mul_assoc, Matrix.vecMulVec_mul, hy]
  simp

theorem seg_ep {x y : ℕ → ι → K} {e : Matrix ι ι K} (a d : ℕ)
    (h : ∀ j, j < d → e *ᵥ x (a + j) = 0 ∧ y (a + j) ᵥ* e = 0) :
    e * seg x y a d = e ∧ seg x y a d * e = e := by
  induction d with
  | zero => simp [seg]
  | succ d ih =>
    obtain ⟨h1, h2⟩ := ih fun j hj => h j (by omega)
    obtain ⟨hx, hy⟩ := h d (by omega)
    rw [seg]
    refine ⟨?_, ?_⟩
    · rw [← mul_assoc, ep_unit hx, h1]
    · rw [mul_assoc, h2, unit_ep hy]

theorem conj_fixed_unit {g G : Matrix ι ι K} (hgG : g * G = 1) {x y : ι → K}
    (hx : g *ᵥ x = x) (hy : y ᵥ* G = y) : g * unitM x y * G = unitM x y := by
  rw [← conj_unit hgG, hx, hy]

theorem conj_fixed_seg {g G : Matrix ι ι K} (hgG : g * G = 1) (hGg : G * g = 1) {x y : ℕ → ι → K}
    (a d : ℕ) (h : ∀ j, j < d → g *ᵥ x (a + j) = x (a + j) ∧ y (a + j) ᵥ* G = y (a + j)) :
    g * seg x y a d * G = seg x y a d := by
  induction d with
  | zero => simp [seg, hgG]
  | succ d ih =>
    have h1 := ih fun j hj => h j (by omega)
    obtain ⟨hx, hy⟩ := h d (by omega)
    rw [seg]
    calc g * (unitM (x (a + d)) (y (a + d)) * seg x y a d) * G
        = (g * unitM (x (a + d)) (y (a + d)) * G) * (g * seg x y a d * G) := by
          calc _ = g * unitM (x (a + d)) (y (a + d)) * (G * g) * seg x y a d * G := by
                rw [hGg]; simp only [mul_assoc, mul_one]
            _ = _ := by simp only [mul_assoc]
      _ = _ := by rw [conj_fixed_unit hgG hx hy, h1]

theorem OSData.withU {ez ep es π F0 U Kq Lq G g : Matrix ι ι K}
    (O : OSData ez ep es π F0 U Kq Lq G g) (U' : Matrix ι ι K) (h1 : ep * U' = ep) (h2 : U' * ep = ep) :
    OSData ez ep es π F0 U' Kq Lq G g := { O with epU := h1, Uep := h2 }

/-- **Lemma OS, near side, in the word.**  Hypotheses (AUDIT-R5 (2), explicit): the cut prefix is
`pp a = F0 ⊕ D_B`; every unit `a ≤ j < a+d` between the cut and the stage `N = a+d` is a stage with no pre part
(`ep x = 0`, `y ep = 0`) whose B-part lies in `V_+` (`D x = es x`, `y D = y es`); `π` = mask of `N` (no pre part);
and the ORIGINAL prefix commutation at `N`.  Conclusions: commutation forces `K π = 0` and `π U L = 0`, and the
sheared prefix `g pp(N) g⁻¹ = U (F0 ⊕ J)` still commutes with `π`. -/
theorem near_side {ez ep es π F0 U0 Kq Lq G g : Matrix ι ι K}
    (O : OSData ez ep es π F0 U0 Kq Lq G g) (h2 : (2 : K) ≠ 0) {x y : ℕ → ι → K} (a d : ℕ)
    (hunit : ∀ j, j < d → ep *ᵥ x (a + j) = 0 ∧ y (a + j) ᵥ* ep = 0 ∧
      OSD es ep G g *ᵥ x (a + j) = es *ᵥ x (a + j) ∧ y (a + j) ᵥ* OSD es ep G g = y (a + j) ᵥ* es)
    (hF : pp x y a = F0 + OSD es ep G g)
    (H : π * pp x y (a + d) = pp x y (a + d) * π) :
    Kq * π = 0 ∧ π * seg x y a d * Lq = 0 ∧
    g * pp x y (a + d) * G = seg x y a d * (F0 + (es - ep)) ∧
    π * (g * pp x y (a + d) * G) = (g * pp x y (a + d) * G) * π := by
  obtain ⟨h1, h1'⟩ := seg_ep (x := x) (y := y) (e := ep) a d fun j hj => ⟨(hunit j hj).1, (hunit j hj).2.1⟩
  have O' := O.withU (seg x y a d) h1 h1'
  have hfix : g * seg x y a d * G = seg x y a d :=
    conj_fixed_seg O.hgG O.hGg a d fun j hj =>
      ⟨O.fixed_vec h2 (hunit j hj).1 (hunit j hj).2.2.1, O.fixed_row h2 (hunit j hj).2.1 (hunit j hj).2.2.2⟩
  rw [pp_add, hF] at H
  obtain ⟨hK, hL, -, hcomm⟩ := O'.os h2 hfix H
  have hconj : g * pp x y (a + d) * G = seg x y a d * (F0 + (es - ep)) := by
    rw [pp_add, hF]; exact (O'.os h2 hfix H).2.2.1
  refine ⟨hK, hL, hconj, ?_⟩
  rw [hconj]; exact hcomm

/-- **Far side.**  If the product `Q` of the units from the stage to the word end (all stages, vectors fixed by
`g`) satisfies `Q P = -1`, then the sheared partial product equals the original one: `g P g⁻¹ = P`. -/
theorem far_side {P Q : Matrix ι ι K} (hgG : g * G = 1) (hGg : G * g = 1) (hQP : Q * P = -1)
    (hQ : g * Q * G = Q) (hQu : IsUnit Q) : g * P * G = P := by
  have h : Q * (g * P * G) = Q * P := by
    calc Q * (g * P * G) = (g * Q * G) * (g * P * G) := by rw [hQ]
      _ = g * (Q * P) * G := by
          calc (g * Q * G) * (g * P * G) = g * Q * (G * g) * P * G := by simp only [mul_assoc]
            _ = _ := by rw [hGg]; simp only [mul_assoc, mul_one]
      _ = Q * P := by
          rw [hQP]
          calc g * -1 * G = -(g * G) := by noncomm_ring
            _ = -1 := by rw [hgG]
  exact hQu.mul_right_inj.1 h

end NearFar

/-! ## §4. singleton atoms are dead (R1/AUDIT-ER: `D = ±1` on a one-role atom) -/

/-- On a one-role atom `D = κ` with `κ² = 1` (TS(5)).  If some prefix unit touches the role and some suffix
unit touches it, we get a contradiction: no singleton atom is genuinely shared across a cut. -/
theorem singleton_dead (h2 : (2 : K) ≠ 0) (κ : K) (hκ : κ * κ = 1) (xp yp xs ys : K)
    (hxp : κ * xp = -xp) (hyp : yp * κ = -yp) (hxs : κ * xs = xs) (hys : ys * κ = ys) :
    ¬ ((xp ≠ 0 ∨ yp ≠ 0) ∧ (xs ≠ 0 ∨ ys ≠ 0)) := by
  rintro ⟨hp, hs⟩
  rcases mul_self_eq_one_iff.1 hκ with h | h
  · subst h
    have a : xp = 0 := by
      have : (2 : K) * xp = 0 := by linear_combination hxp
      rcases mul_eq_zero.1 this with h | h
      · exact absurd h h2
      · exact h
    have b : yp = 0 := by
      have : (2 : K) * yp = 0 := by linear_combination hyp
      rcases mul_eq_zero.1 this with h | h
      · exact absurd h h2
      · exact h
    rcases hp with h | h <;> contradiction
  · subst h
    have a : xs = 0 := by
      have : (2 : K) * xs = 0 := by linear_combination -hxs
      rcases mul_eq_zero.1 this with h | h
      · exact absurd h h2
      · exact h
    have b : ys = 0 := by
      have : (2 : K) * ys = 0 := by linear_combination -hys
      rcases mul_eq_zero.1 this with h | h
      · exact absurd h h2
      · exact h
    rcases hs with h | h <;> contradiction

/-! ## §5. boundary addendum (BD): the rank-2 twist sits on the common roles, the rest are involutions -/

theorem rank_eq_zero_imp {n : Type*} [Fintype n] [DecidableEq n] {M : Matrix n n K} (h : M.rank = 0) :
    M = 0 := by
  have h0 : LinearMap.range M.mulVecLin = ⊥ := Submodule.finrank_eq_zero.1 h
  ext i j
  have hm : M *ᵥ Pi.single j 1 ∈ LinearMap.range M.mulVecLin := ⟨_, rfl⟩
  rw [h0, Submodule.mem_bot] at hm
  have := congrFun hm i
  simpa [Matrix.mulVec_single_one] using this

section BD
variable {a b : Type*} [Fintype a] [Fintype b] [DecidableEq a] [DecidableEq b]

/-- **BD, involution blocks.**  `D = D_C ⊕ D_R` with `rank(1 - D²) ≤ 2` (cut tightness B2) and the twist block
`rank(1 - D_C²) ≥ 2` forces `D_R² = 1` on the rest (m1\m2, m2\m1, EO). -/
theorem bd_involution (Dc : Matrix a a K) (Dr : Matrix b b K)
    (hB2 : (1 - fromBlocks Dc 0 0 Dr * fromBlocks Dc 0 0 Dr : Matrix (a ⊕ b) (a ⊕ b) K).rank ≤ 2)
    (hC : 2 ≤ (1 - Dc * Dc : Matrix a a K).rank) : Dr * Dr = 1 := by
  have e : (1 - fromBlocks Dc 0 0 Dr * fromBlocks Dc 0 0 Dr : Matrix (a ⊕ b) (a ⊕ b) K)
      = fromBlocks (1 - Dc * Dc) 0 0 (1 - Dr * Dr) := by
    rw [fromBlocks_multiply]
    ext (i | i) (j | j) <;> simp [Matrix.one_apply, Matrix.sub_apply]
  rw [e] at hB2
  have h := SpecTSUR.rank_fromBlocks_diag_ge (1 - Dc * Dc) (1 - Dr * Dr)
  have h0 : (1 - Dr * Dr : Matrix b b K).rank = 0 := by omega
  exact (sub_eq_zero.1 (rank_eq_zero_imp h0)).symm

end BD

/-- **TS(4) twist bound.**  If `(1+D)u, (1+D)v` are independent modulo `ker(1-D)` (no nontrivial combination
is killed by `1-D`), then `rank(1 - D²) ≥ 2` (the content of `rank(I+D_bd) - dim ker(I-D_bd) = rank(I-D_bd²) ≥ 2`
once Lemma S supplies the rank-2 block `X_s2[C]`). -/
theorem twist_rank_two {n : Type*} [Fintype n] [DecidableEq n] (D : Matrix n n K) (u v : n → K)
    (hind : ∀ s t : K, (1 - D) *ᵥ (s • ((1 + D) *ᵥ u) + t • ((1 + D) *ᵥ v)) = 0 → s = 0 ∧ t = 0) :
    2 ≤ (1 - D * D).rank := by
  have hM : ((1 - D) * (1 + D) : Matrix n n K) = 1 - D * D := by noncomm_ring
  have hp : (1 - D * D) *ᵥ u ∈ LinearMap.range (1 - D * D : Matrix n n K).mulVecLin := ⟨u, rfl⟩
  have hq : (1 - D * D) *ᵥ v ∈ LinearMap.range (1 - D * D : Matrix n n K).mulVecLin := ⟨v, rfl⟩
  have hli : LinearIndependent K ![(1 - D * D) *ᵥ u, (1 - D * D) *ᵥ v] := by
    rw [LinearIndependent.pair_iff]
    intro s t h
    apply hind
    rw [mulVec_add, mulVec_smul, mulVec_smul, mulVec_mulVec, mulVec_mulVec, hM]
    exact h
  let f : Fin 2 → LinearMap.range (1 - D * D : Matrix n n K).mulVecLin := ![⟨_, hp⟩, ⟨_, hq⟩]
  have hf : LinearIndependent K f := by
    have hc : ((LinearMap.range (1 - D * D : Matrix n n K).mulVecLin).subtype ∘ f) =
        ![(1 - D * D) *ᵥ u, (1 - D * D) *ᵥ v] := by
      funext i; fin_cases i <;> rfl
    apply LinearIndependent.of_comp (LinearMap.range (1 - D * D : Matrix n n K).mulVecLin).subtype
    rw [hc]; exact hli
  have := hf.fintype_card_le_finrank
  simpa [Matrix.rank] using this


/-! ## §6. shear lemma GS for blocks of any size (R4 §1): the algebra after the block extraction

Setting (prefix stage `π`, no suf part; `P' = g P g⁻¹ = 1 + N`, `N` supported on z ⊕ pre).  Writing the
commutation `[P', gπG] = 0` in blocks (z|pre|suf) gives (R4's "7 block identities")
  `N_zp X = π_z N_zp`, `N_zp X K = 0`, `N_pz π_z = X N_pz`, `L X N_pz = 0`,
  `N_pp X = X N_pp`, `N_pp X K = 0`, `L X N_pp = 0`,  with `X = Δ p`, `Δ = (1 - K L)⁻¹`.
The three lemmas below derive from them, under `[p, K L] = 0`, the conclusions `N_zp p = π_z N_zp`,
`p N_pz = N_pz π_z`, `N_pp p = p N_pp` (i.e. `[N, π] = 0`).  The extraction of the block identities themselves
is routine block multiplication (not formalised; checked numerically at (z,pre,suf) = (2,3,2), see the .md). -/

section GS
variable {ep Kq Lq Δ p : Matrix ι ι K}

/-- `Δ` commutes with `p` (from `[p, K L] = 0` and `Δ = (1 - K L)⁻¹` on the pre block). -/
theorem gs_comm (hΔ1 : Δ * (ep - Kq * Lq) = ep) (hΔ2 : (ep - Kq * Lq) * Δ = ep)
    (hepΔ : ep * Δ = Δ) (hΔep : Δ * ep = Δ) (hpep : p * ep = p) (hepp : ep * p = p)
    (hpT : p * (Kq * Lq) = (Kq * Lq) * p) : p * Δ = Δ * p := by
  have hM : p * (ep - Kq * Lq) = (ep - Kq * Lq) * p := by
    rw [mul_sub, sub_mul, hpep, hepp, hpT]
  calc p * Δ = ep * (p * Δ) := by rw [← mul_assoc, hepp]
    _ = (Δ * (ep - Kq * Lq)) * (p * Δ) := by rw [hΔ1]
    _ = Δ * ((ep - Kq * Lq) * p) * Δ := by simp only [mul_assoc]
    _ = Δ * (p * (ep - Kq * Lq)) * Δ := by rw [hM]
    _ = Δ * p * ((ep - Kq * Lq) * Δ) := by simp only [mul_assoc]
    _ = Δ * p := by rw [hΔ2, mul_assoc, hpep]

variable (hΔ1 : Δ * (ep - Kq * Lq) = ep) (hΔ2 : (ep - Kq * Lq) * Δ = ep)
  (hpΔ : p * Δ = Δ * p) (hpep : p * ep = p) (hepp : ep * p = p) (hpp : p * p = p)
include hΔ1 hΔ2 hpΔ hpep hepp hpp

/-- (z,pre) block. -/
theorem gs_zp {W πz : Matrix ι ι K} (hπz : πz * πz = πz) (hW : W * Δ * p = πz * W) :
    W * p = πz * W := by
  have h0 : (W - πz * W) * Δ * p = 0 := by
    calc (W - πz * W) * Δ * p = W * Δ * p - πz * (W * Δ * p) := by simp only [sub_mul, mul_assoc]
      _ = πz * W - πz * (πz * W) := by rw [hW]
      _ = 0 := by rw [← mul_assoc, hπz, sub_self]
  have h1 : (W - πz * W) * p = 0 := by
    calc (W - πz * W) * p = (W - πz * W) * p * ep := by rw [mul_assoc _ p ep, hpep]
      _ = (W - πz * W) * p * (Δ * (ep - Kq * Lq)) := by rw [hΔ1]
      _ = ((W - πz * W) * Δ * p) * (ep - Kq * Lq) := by
          have : p * Δ = Δ * p := hpΔ
          calc _ = (W - πz * W) * (p * Δ) * (ep - Kq * Lq) := by simp only [mul_assoc]
            _ = _ := by rw [this]; simp only [mul_assoc]
      _ = 0 := by rw [h0, zero_mul]
  have h2 : πz * W * p = πz * W := by
    rw [← hW]; simp only [mul_assoc, hpp]
  calc W * p = (W - πz * W) * p + πz * W * p := by noncomm_ring
    _ = πz * W := by rw [h1, h2, zero_add]

/-- (pre,z) block. -/
theorem gs_pz {V πz : Matrix ι ι K} (hepV : ep * V = V) (hV : V * πz = Δ * p * V)
    (hL : Lq * Δ * p * V = 0) : p * V = V * πz := by
  have h1 : Lq * (V * πz) = 0 := by rw [hV]; simpa only [mul_assoc] using hL
  calc p * V = (ep - Kq * Lq) * Δ * p * V := by rw [hΔ2, hepp]
    _ = (ep - Kq * Lq) * (Δ * p * V) := by simp only [mul_assoc]
    _ = (ep - Kq * Lq) * (V * πz) := by rw [hV]
    _ = V * πz := by rw [sub_mul, mul_assoc Kq Lq, h1, mul_zero, sub_zero, ← mul_assoc, hepV]

/-- (pre,pre) block. -/
theorem gs_pp {S : Matrix ι ι K} (hepS : ep * S = S) (hSep : S * ep = S)
    (hS : S * Δ * p = Δ * p * S) (hL : Lq * Δ * p * S = 0) (hK : S * Δ * p * Kq = 0) :
    S * p = p * S := by
  have h1 : S * Δ * p = p * S := by
    have hM : (ep - Kq * Lq) * (S * Δ * p) = p * S := by
      calc (ep - Kq * Lq) * (S * Δ * p) = (ep - Kq * Lq) * (Δ * p * S) := by rw [hS]
        _ = ((ep - Kq * Lq) * Δ) * p * S := by simp only [mul_assoc]
        _ = p * S := by rw [hΔ2, hepp]
    have hM2 : (ep - Kq * Lq) * (S * Δ * p) = S * Δ * p := by
      have : Lq * (S * Δ * p) = 0 := by
        calc Lq * (S * Δ * p) = Lq * (Δ * p * S) := by rw [hS]
          _ = 0 := by rw [← hL]; simp only [mul_assoc]
      rw [sub_mul, mul_assoc Kq Lq, this, mul_zero, sub_zero]; simp only [← mul_assoc, hepS]
    rw [← hM2, hM]
  have h2 : p * S * Kq = 0 := by rw [← h1]; exact hK
  calc S * p = S * p * ep := by rw [mul_assoc, hpep]
    _ = S * p * (Δ * (ep - Kq * Lq)) := by rw [hΔ1]
    _ = (S * (p * Δ)) * (ep - Kq * Lq) := by simp only [mul_assoc]
    _ = (S * Δ * p) * (ep - Kq * Lq) := by rw [hpΔ]; simp only [mul_assoc]
    _ = (p * S) * (ep - Kq * Lq) := by rw [h1]
    _ = p * S := by
        rw [mul_sub, mul_assoc p S ep, hSep, ← mul_assoc (p * S) Kq Lq, h2, zero_mul, sub_zero]

end GS

end CallerBorrow

#print axioms CallerBorrow.lemmaE
#print axioms CallerBorrow.lemmaE_dual
#print axioms CallerBorrow.RebaseData.lemmaR
#print axioms CallerBorrow.RebaseData.pre_conf
#print axioms CallerBorrow.RebaseData.suf_conf
#print axioms CallerBorrow.RebaseData.not_both
#print axioms CallerBorrow.singleton_dead
#print axioms CallerBorrow.bd_involution
#print axioms CallerBorrow.twist_rank_two
#print axioms CallerBorrow.OSData.forced
#print axioms CallerBorrow.OSData.os
#print axioms CallerBorrow.OSData.fixed_vec
#print axioms CallerBorrow.OSData.fixed_row
#print axioms CallerBorrow.near_side
#print axioms CallerBorrow.far_side
#print axioms CallerBorrow.gs_comm
#print axioms CallerBorrow.gs_zp
#print axioms CallerBorrow.gs_pz
#print axioms CallerBorrow.gs_pp
#print axioms CallerBorrow.unitM_isUnit
