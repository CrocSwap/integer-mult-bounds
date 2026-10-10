import Work.Carrier.Pack
import Work.Carrier.Ring

/-!
# (key: carrier-thm) The live roles of an invocation, and the four dirt gates as matrices

`L3 T Sl = (T ⊕ T) ⊕ Sl`: the bank roles `x` (`lX`), `y` (`lY`) and the helper slots (`lS`), all
on the same footing (no scratch copies).  `PX`, `PY`: the coordinate projectors.

For the matrix `M` of all gates of the main phase and its inverse `Mi`:

    g1 M  = 1 - PY * M * PS      `y -= K s`            g1i M = 1 + PY * M * PS   (its inverse)
    g8 Mi = PX + PY + PS * Mi    slot rows of `M⁻¹`    h8 M  = PX + PY + PS * M  (its inverse)

(`PS = 1 - PX - PY`).  This file: unit rows / columns of these gates (hence between which roles
their entries can be nonzero), the scatter with the copies eliminated (`scatM`), and the scalar
maps of `1 + PY * M * PX` and of the transpose of `1 - PY * M * PX`.

No `sorry`.
-/

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace OAI
namespace PowerSaving
namespace CR
open Binary Matrix Finset RAM SS CB BR
noncomputable section

section Diag
variable {ρ : Type*} [Fintype ρ] [DecidableEq ρ]

lemma col_zero_of {d : ρ → ℚ} {G : Matrix ρ ρ ℚ}
    (h : G * Matrix.diagonal d = Matrix.diagonal d) {i j : ρ} (hj : d j = 1) (hij : i ≠ j) :
    G i j = 0 := by
  have e := congrFun (congrFun h i) j
  rw [Matrix.mul_diagonal, Matrix.diagonal_apply_ne _ hij, hj, mul_one] at e
  exact e

lemma row_zero_of {d : ρ → ℚ} {G : Matrix ρ ρ ℚ}
    (h : Matrix.diagonal d * G = Matrix.diagonal d) {i j : ρ} (hi : d i = 1) (hij : i ≠ j) :
    G i j = 0 := by
  have e := congrFun (congrFun h i) j
  rw [Matrix.diagonal_mul, Matrix.diagonal_apply_ne _ hij, hi, one_mul] at e
  exact e

lemma diag_mul_of_rows {d : ρ → ℚ} {G : Matrix ρ ρ ℚ}
    (h : ∀ i j, d i ≠ 0 → G i j = if i = j then 1 else 0) :
    Matrix.diagonal d * G = Matrix.diagonal d := by
  ext i j
  rw [Matrix.diagonal_mul]
  by_cases hd : d i = 0
  · rw [hd, zero_mul]
    by_cases hij : i = j
    · subst hij; rw [Matrix.diagonal_apply_eq, hd]
    · rw [Matrix.diagonal_apply_ne _ hij]
  · rw [h i j hd]
    by_cases hij : i = j
    · subst hij; rw [if_pos rfl, mul_one, Matrix.diagonal_apply_eq]
    · rw [if_neg hij, mul_zero, Matrix.diagonal_apply_ne _ hij]

lemma mul_diag_of_cols {d : ρ → ℚ} {G : Matrix ρ ρ ℚ}
    (h : ∀ i j, d j ≠ 0 → G i j = if i = j then 1 else 0) :
    G * Matrix.diagonal d = Matrix.diagonal d := by
  ext i j
  rw [Matrix.mul_diagonal]
  by_cases hd : d j = 0
  · rw [hd, mul_zero]
    by_cases hij : i = j
    · subst hij; rw [Matrix.diagonal_apply_eq, hd]
    · rw [Matrix.diagonal_apply_ne _ hij]
  · rw [h i j hd]
    by_cases hij : i = j
    · subst hij; rw [if_pos rfl, one_mul, Matrix.diagonal_apply_eq]
    · rw [if_neg hij, zero_mul, Matrix.diagonal_apply_ne _ hij]

/-- scalar map of a diagonal gate matrix. -/
lemma act_diag (d : ρ → ℚ) (u : ρ → ℂ) :
    actPoint (Matrix.diagonal d) u = fun i => ((d i : ℚ) : ℂ) * u i := by
  funext i
  show ∑ j, ((Matrix.diagonal d i j : ℚ) : ℂ) * u j = ((d i : ℚ) : ℂ) * u i
  rw [Finset.sum_eq_single i]
  · rw [Matrix.diagonal_apply_eq]
  · intro j _ hj
    rw [Matrix.diagonal_apply_ne _ (Ne.symm hj), Rat.cast_zero, zero_mul]
  · intro h
    exact absurd (Finset.mem_univ i) h

lemma actPoint_mul (A B : Matrix ρ ρ ℚ) (u : ρ → ℂ) :
    actPoint (A * B) u = actPoint A (actPoint B u) :=
  ap_mul A B u

end Diag

section Live
variable {T Sl : Type} [Fintype T] [DecidableEq T] [Fintype Sl] [DecidableEq Sl]

/-- live roles of one invocation: `x`, `y`, helper slots. -/
abbrev L3 (T Sl : Type) := (T ⊕ T) ⊕ Sl
abbrev lX (t : T) : L3 T Sl := Sum.inl (Sum.inl t)
abbrev lY (t : T) : L3 T Sl := Sum.inl (Sum.inr t)
abbrev lS (q : Sl) : L3 T Sl := Sum.inr q

/-- indicator of the x roles. -/
def iX : L3 T Sl → ℚ := Sum.elim (Sum.elim (fun _ => 1) (fun _ => 0)) (fun _ => 0)
/-- indicator of the y roles. -/
def iY : L3 T Sl → ℚ := Sum.elim (Sum.elim (fun _ => 0) (fun _ => 1)) (fun _ => 0)

def PX : Matrix (L3 T Sl) (L3 T Sl) ℚ := Matrix.diagonal iX
def PY : Matrix (L3 T Sl) (L3 T Sl) ℚ := Matrix.diagonal iY

lemma iX_cases (i : L3 T Sl) : iX i = 0 ∨ iX i = 1 := by
  rcases i with ((t|t)|q)
  · exact Or.inr rfl
  · exact Or.inl rfl
  · exact Or.inl rfl

lemma iY_cases (i : L3 T Sl) : iY i = 0 ∨ iY i = 1 := by
  rcases i with ((t|t)|q)
  · exact Or.inl rfl
  · exact Or.inr rfl
  · exact Or.inl rfl

lemma PX_sq : (PX : Matrix (L3 T Sl) (L3 T Sl) ℚ) * PX = PX := by
  unfold PX
  have e : (fun i : L3 T Sl => iX i * iX i) = iX := by
    funext i
    rcases i with ((t|t)|q) <;> simp [iX]
  rw [Matrix.diagonal_mul_diagonal, e]

lemma PY_sq : (PY : Matrix (L3 T Sl) (L3 T Sl) ℚ) * PY = PY := by
  unfold PY
  have e : (fun i : L3 T Sl => iY i * iY i) = iY := by
    funext i
    rcases i with ((t|t)|q) <;> simp [iY]
  rw [Matrix.diagonal_mul_diagonal, e]

lemma PX_PY : (PX : Matrix (L3 T Sl) (L3 T Sl) ℚ) * PY = 0 := by
  unfold PX PY
  rw [Matrix.diagonal_mul_diagonal]
  have e : (fun i : L3 T Sl => iX i * iY i) = fun _ => 0 := by
    funext i
    rcases i with ((t|t)|q) <;> simp [iX, iY]
  rw [e]
  exact Matrix.diagonal_zero

lemma PY_PX : (PY : Matrix (L3 T Sl) (L3 T Sl) ℚ) * PX = 0 := by
  unfold PX PY
  rw [Matrix.diagonal_mul_diagonal]
  have e : (fun i : L3 T Sl => iY i * iX i) = fun _ => 0 := by
    funext i
    rcases i with ((t|t)|q) <;> simp [iX, iY]
  rw [e]
  exact Matrix.diagonal_zero

lemma PX_T : (PX : Matrix (L3 T Sl) (L3 T Sl) ℚ)ᵀ = PX := Matrix.diagonal_transpose _
lemma PY_T : (PY : Matrix (L3 T Sl) (L3 T Sl) ℚ)ᵀ = PY := Matrix.diagonal_transpose _

/-- "no gate into an x role": the x rows are unit rows. -/
lemma PX_mul_of {M : Matrix (L3 T Sl) (L3 T Sl) ℚ}
    (hx : ∀ t j, M (lX t) j = if lX t = j then 1 else 0) : PX * M = PX := by
  unfold PX
  apply diag_mul_of_rows
  intro i j hi
  rcases i with ((t|t)|q)
  · exact hx t j
  · exact absurd rfl hi
  · exact absurd rfl hi

/-- "no gate reads a y role": the y columns are unit columns. -/
lemma mul_PY_of {M : Matrix (L3 T Sl) (L3 T Sl) ℚ}
    (hy : ∀ i t, M i (lY t) = if i = lY t then 1 else 0) : M * PY = PY := by
  unfold PY
  apply mul_diag_of_cols
  intro i j hj
  rcases j with ((t|t)|q)
  · exact absurd rfl hj
  · exact hy i t
  · exact absurd rfl hj

/-! ### the four dirt gates -/

def g1 (M : Matrix (L3 T Sl) (L3 T Sl) ℚ) : Matrix (L3 T Sl) (L3 T Sl) ℚ :=
  1 - PY * M * (1 - PX - PY)
def g1i (M : Matrix (L3 T Sl) (L3 T Sl) ℚ) : Matrix (L3 T Sl) (L3 T Sl) ℚ :=
  1 + PY * M * (1 - PX - PY)
def g8 (Mi : Matrix (L3 T Sl) (L3 T Sl) ℚ) : Matrix (L3 T Sl) (L3 T Sl) ℚ :=
  PX + PY + (1 - PX - PY) * Mi
def h8 (M : Matrix (L3 T Sl) (L3 T Sl) ℚ) : Matrix (L3 T Sl) (L3 T Sl) ℚ :=
  PX + PY + (1 - PX - PY) * M

/-- a gate with unit x rows and unit x columns joins two different roles only if neither is an
x role. -/
lemma offdiag_x {G : Matrix (L3 T Sl) (L3 T Sl) ℚ} (h1 : G * PX = PX) (h2 : PX * G = PX)
    {i j : L3 T Sl} (hij : G i j ≠ 0) (e : i ≠ j) : iX i = 0 ∧ iX j = 0 := by
  constructor
  · by_contra h
    exact hij (row_zero_of h2 ((iX_cases i).resolve_left h) e)
  · by_contra h
    exact hij (col_zero_of h1 ((iX_cases j).resolve_left h) e)

/-- a gate with unit x rows, unit y rows and unit y columns: a nonzero entry off the diagonal
is in a slot row and not in a y column. -/
lemma offdiag_s {G : Matrix (L3 T Sl) (L3 T Sl) ℚ} (hx : PX * G = PX) (hy : PY * G = PY)
    (hyc : G * PY = PY) {i j : L3 T Sl} (hij : G i j ≠ 0) (e : i ≠ j) :
    iX i = 0 ∧ iY i = 0 ∧ iY j = 0 := by
  refine ⟨?_, ?_, ?_⟩
  · by_contra h
    exact hij (row_zero_of hx ((iX_cases i).resolve_left h) e)
  · by_contra h
    exact hij (row_zero_of hy ((iY_cases i).resolve_left h) e)
  · by_contra h
    exact hij (col_zero_of hyc ((iY_cases j).resolve_left h) e)

lemma g1_x (M : Matrix (L3 T Sl) (L3 T Sl) ℚ) : g1 M * PX = PX ∧ PX * g1 M = PX := by
  unfold g1
  constructor
  · rw [sub_mul, one_mul, side_n_right (PX_sq (T := T) (Sl := Sl)) PY_PX, sub_zero]
  · rw [mul_sub, mul_one, side_n_left (PX_PY (T := T) (Sl := Sl)), sub_zero]

lemma g1i_x (M : Matrix (L3 T Sl) (L3 T Sl) ℚ) : g1i M * PX = PX ∧ PX * g1i M = PX := by
  unfold g1i
  constructor
  · rw [add_mul, one_mul, side_n_right (PX_sq (T := T) (Sl := Sl)) PY_PX, add_zero]
  · rw [mul_add, mul_one, side_n_left (PX_PY (T := T) (Sl := Sl)), add_zero]

end Live
end
end CR
end PowerSaving
end OAI
