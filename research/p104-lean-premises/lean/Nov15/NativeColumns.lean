/-
LEAN-PREM3, Nov 17. #7620 premise `native_all_columns`: what "exact final rows" buys.
See NativeColumns.md.
Part A: data-level execution of a TokenCancel word over ANY K-module equals the row matrix
applied to the data (all columns, all tensor widths); exact rows <-> correct on every column.
Part B: column-test logic (basis columns determine a map; fewer do not; adjoint adds no
coverage; global phase is invisible to Pauli action but not to columns; census coverage).
-/
import Nov15.TokenCancel
import Mathlib.LinearAlgebra.Matrix.ToLin
import Mathlib.Data.Matrix.Basic
import Mathlib.Data.Complex.Basic

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace NativeColumns
open TokenCancel

section PartA
variable {K Reg C M : Type*} [Field K] [DecidableEq Reg] [DecidableEq C] [Fintype Reg]
  [AddCommGroup M] [Module K M]

/-- Data-level step: run the same event on actual data `v` (born reads the input `x`). -/
def dstep (x v : Reg → M) : Ev K Reg C → (Reg → M)
  | .born i _ => Function.update v i (x i)
  | .init i _ => Function.update v i 0
  | .move _ _ => v
  | .add i j a _ => Function.update v i (v i + a • v j)
  | .scale i u _ => Function.update v i (u • v i)
  | .clear i _ => Function.update v i 0
  | .copy i j _ => Function.update v i (v j)

def drun (x : Reg → M) : (Reg → M) → List (Ev K Reg C) → (Reg → M)
  | v, [] => v
  | v, e :: es => drun x (dstep x v e) es

/-- A row matrix applied to data. -/
def evalRows (row : Reg → Reg → K) (x : Reg → M) : Reg → M := fun i => ∑ j, row i j • x j

theorem evalRows_one (x : Reg → M) : evalRows (fun i j => (Pi.single i (1:K) : Reg → K) j) x = x := by
  funext i
  simp [evalRows, Pi.single_apply]

theorem dstep_eval (x : Reg → M) (s : St K Reg C) (e : Ev K Reg C) :
    dstep x (evalRows s.row x) e = evalRows (step s e).row x := by
  cases e with
  | born i c =>
    funext k
    by_cases hk : k = i
    · subst hk; simp [dstep, step, evalRows, Pi.single_apply]
    · simp [dstep, step, evalRows, hk]
  | init i c =>
    funext k
    by_cases hk : k = i
    · subst hk; simp [dstep, step, evalRows]
    · simp [dstep, step, evalRows, hk]
  | move i c => rfl
  | add i j a c =>
    funext k
    by_cases hk : k = i
    · subst hk; simp [dstep, step, evalRows, add_smul, Finset.sum_add_distrib, Finset.smul_sum, smul_smul]
    · simp [dstep, step, evalRows, hk]
  | scale i u c =>
    funext k
    by_cases hk : k = i
    · subst hk; simp [dstep, step, evalRows, Finset.smul_sum, smul_smul]
    · simp [dstep, step, evalRows, hk]
  | clear i c =>
    funext k
    by_cases hk : k = i
    · subst hk; simp [dstep, step, evalRows]
    · simp [dstep, step, evalRows, hk]
  | copy i j c =>
    funext k
    by_cases hk : k = i
    · subst hk; simp [dstep, step, evalRows]
    · simp [dstep, step, evalRows, hk]

/-- Simulation: executing the word on data = (final rows) applied to the initial data. -/
theorem drun_eval (x : Reg → M) (es : List (Ev K Reg C)) (s : St K Reg C) :
    drun x (evalRows s.row x) es = evalRows (run s es).row x := by
  induction es generalizing s with
  | nil => rfl
  | cons e es ih => simp only [drun, run]; rw [dstep_eval]; exact ih _

/-- Item 1: exact final rows = target rows  =>  the word is correct on EVERY input, in EVERY
K-module (every column count, every tensor power `V^n`, any coefficient module). -/
theorem all_columns_of_exact_rows (x : Reg → M) (es : List (Ev K Reg C)) (s : St K Reg C)
    (T : Reg → Reg → K) (h : (run s es).row = T) :
    drun x (evalRows s.row x) es = evalRows T x := by
  rw [drun_eval, h]

/-- Starting from the identity rows with data `x`, the word computes `T x`. -/
theorem word_computes (x : Reg → M) (es : List (Ev K Reg C)) (s : St K Reg C)
    (hs : s.row = fun i j => (Pi.single i (1:K) : Reg → K) j) (T : Reg → Reg → K)
    (h : (run s es).row = T) : drun x x es = evalRows T x := by
  have := all_columns_of_exact_rows x es s T h
  rwa [hs, evalRows_one] at this

/-- Converse (so exactness of rows is exactly the all-column statement): if the word agrees
with `T` on every unit column `e_c` over `K`, the final rows equal `T`. -/
theorem exact_rows_of_columns (es : List (Ev K Reg C)) (s : St K Reg C) (T : Reg → Reg → K)
    (h : ∀ c : Reg, drun (Pi.single c (1:K)) (evalRows s.row (Pi.single c (1:K))) es
        = evalRows T (Pi.single c (1:K))) : (run s es).row = T := by
  funext i c
  have := congrFun (h c) i
  rw [drun_eval] at this
  simpa [evalRows, Pi.single_apply] using this

theorem exact_rows_iff_columns (es : List (Ev K Reg C)) (s : St K Reg C) (T : Reg → Reg → K) :
    (run s es).row = T ↔ ∀ c : Reg, drun (Pi.single c (1:K)) (evalRows s.row (Pi.single c (1:K))) es
        = evalRows T (Pi.single c (1:K)) :=
  ⟨fun h c => all_columns_of_exact_rows _ es s T h, exact_rows_of_columns es s T⟩

end PartA

section PartB

/-- Basis columns determine a matrix. -/
theorem matrix_ext_cols {R : Type*} [Semiring R] {m n : Type*} [Fintype n] [DecidableEq n]
    (A B : Matrix m n R) (h : ∀ c, A.mulVec (Pi.single c 1) = B.mulVec (Pi.single c 1)) : A = B := by
  ext i c
  have := congrFun (h c) i
  simpa using this

/-- Agreement on a spanning set of columns suffices (not only the unit vectors). -/
theorem linear_ext_span {K V W : Type*} [Field K] [AddCommGroup V] [Module K V]
    [AddCommGroup W] [Module K W] (f g : V →ₗ[K] W) (S : Set V)
    (hS : Submodule.span K S = ⊤) (h : ∀ v ∈ S, f v = g v) : f = g :=
  LinearMap.ext_on hS h

/-- Fewer than all columns do not suffice: a 2x2 witness over `ℚ` agreeing on column 0. -/
theorem partial_columns_insufficient :
    ∃ A B : Matrix (Fin 2) (Fin 2) ℚ,
      A.mulVec (Pi.single 0 1) = B.mulVec (Pi.single 0 1) ∧ A ≠ B := by
  refine ⟨!![1, 0; 0, 1], !![1, 0; 0, 2], ?_, ?_⟩
  · funext i; fin_cases i <;> simp [Matrix.mulVec, dotProduct, Fin.sum_univ_two]
  · intro h
    have := congrFun (congrFun h 1) 1
    simp at this

/-- The adjoint column test adds no coverage: forward exactness <-> adjoint exactness. -/
theorem adjoint_iff_forward {m n : Type*} (A B : Matrix m n ℂ) : Matrix.conjTranspose A = Matrix.conjTranspose B ↔ A = B :=
  Matrix.conjTranspose_inj

/-- Global phase is invisible to a Pauli-conjugation action but visible on every column:
`c • A` and `A` differ whenever `c ≠ 1` and `A ≠ 0` (here: `A` has a nonzero entry). -/
theorem phase_visible {m n : Type*} (A : Matrix m n ℂ) (i : m) (j : n) (hA : A i j ≠ 0)
    (c : ℂ) (hc : c ≠ 1) : c • A ≠ A := by
  intro h
  have := congrFun (congrFun h i) j
  simp only [Matrix.smul_apply, smul_eq_mul] at this
  have : (c - 1) * A i j = 0 := by rw [sub_mul, this]; ring
  rcases mul_eq_zero.mp this with h1 | h1
  · exact hc (sub_eq_zero.mp h1)
  · exact hA h1

/-- Census coverage: columns correct on every census pair + used pairs inside the census
=> every used pair correct.  (`used ⊆ census` is the finite-set check in `affected_pairs`.) -/
theorem census_coverage {P : Type*} (used census : Set P) (Correct : P → Prop)
    (hsub : used ⊆ census) (hall : ∀ p ∈ census, Correct p) : ∀ p ∈ used, Correct p :=
  fun p hp => hall p (hsub hp)

end PartB
end NativeColumns

#print axioms NativeColumns.all_columns_of_exact_rows
#print axioms NativeColumns.exact_rows_iff_columns
#print axioms NativeColumns.partial_columns_insufficient
#print axioms NativeColumns.adjoint_iff_forward
#print axioms NativeColumns.phase_visible
