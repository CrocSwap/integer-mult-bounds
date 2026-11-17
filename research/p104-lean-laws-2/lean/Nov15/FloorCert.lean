/-
FloorCert (lane LEAN-NEXT14, Nov 16): the RANKSTEINER R4 dual certificate for the class-K junk floor
(780 paid stops = 1,081.31 D0/call), checked in Lean by kernel evaluation (`decide +kernel`, no
`native_decide`, so no `Lean.ofReduceBool`). See FloorCert.md.

The LP is the support sub-LP of rslp.py's LP (only rows with positive dual: 892 rows, 18,868
columns, 31,249 nonzeros), exported by Nov15/floorcert/export_cert.py into FloorCertData.lean.
All of A, b, c are integers; the dual is y = Y / 8 with Y integer.

Build (one at a time):
  lake env lean -o .lake/build/lib/lean/Nov15/FloorCertDefs.olean Nov15/FloorCertDefs.lean
  lake env lean -o .lake/build/lib/lean/Nov15/FloorCertData.olean Nov15/FloorCertData.lean  (90 s, 2.1 GB)
  lake env lean -o .lake/build/lib/lean/Nov15/FloorCertCheck.olean Nov15/FloorCertCheck.lean  (20 s, 2.3 GB)
  lake env lean -o .lake/build/lib/lean/Nov15/FloorCert.olean Nov15/FloorCert.lean
(needs the Floor / FloorGlue / ExportLaw oleans.)
-/
import Nov15.FloorCertCheck
import Nov15.FloorGlue
import Mathlib.Analysis.SpecialFunctions.Log.Basic

open Finset

set_option linter.unusedSectionVars false

namespace FloorCert

/-! ## 2. The LP over any ordered field -/

section Field
variable {𝕜 : Type*} [Field 𝕜] [LinearOrder 𝕜] [IsStrictOrderedRing 𝕜]

/-- column j of the exported LP -/
def col (j : Fin nCols) : Int × List (Nat × Int) := colList.getD j (0, [])

/-- A i j: the coefficient of column j in row i (sum of the sparse entries with row index i). -/
def A (i : Fin nRows) (j : Fin nCols) : 𝕜 :=
  ((col j).2.map fun p => if p.1 = i.val then (p.2 : 𝕜) else 0).sum

/-- right-hand sides -/
def b (i : Fin nRows) : 𝕜 := (bList.getD i 0 : 𝕜)

/-- costs (1 on fresh heads x_m and on y_c, 0 on z / a) -/
def c (j : Fin nCols) : 𝕜 := ((col j).1 : 𝕜)

/-- the dual vector y = Y / 8 -/
def y (i : Fin nRows) : 𝕜 := (Ytree.get i : 𝕜) / (den : 𝕜)

lemma den_pos : (0 : 𝕜) < (den : 𝕜) := by norm_num [den]

theorem y_nonneg (i : Fin nRows) : 0 ≤ (y i : 𝕜) :=
  div_nonneg (by exact_mod_cast Y_nonneg_ok i) den_pos.le

/-- sparse-column identity: Σ_{i<R} Y(i)·A(i) = Σ_{(i,a) ∈ l} Y(i)·a when every row index is < R. -/
lemma sum_sparse {R : Nat} (Y : Nat → Int) (l : List (Nat × Int)) (hl : ∀ p ∈ l, p.1 < R) :
    ∑ i : Fin R, (Y i : 𝕜) * (l.map fun p => if p.1 = i.val then (p.2 : 𝕜) else 0).sum
      = ((colDot Y l : Int) : 𝕜) := by
  induction l with
  | nil => simp [colDot]
  | cons p l ih =>
    have hp : p.1 < R := hl p (by simp)
    have ih' := ih fun q hq => hl q (by simp [hq])
    simp only [List.map_cons, List.sum_cons, mul_add, Finset.sum_add_distrib, ih']
    have h1 : ∑ i : Fin R, (Y i : 𝕜) * (if p.1 = i.val then (p.2 : 𝕜) else 0)
        = (Y p.1 : 𝕜) * p.2 := by
      rw [Finset.sum_eq_single ⟨p.1, hp⟩]
      · simp
      · intro i _ hi
        have : p.1 ≠ i.val := fun h => hi (Fin.ext h.symm)
        simp [this]
      · simp
    rw [h1]
    simp [colDot]

theorem yA_le (j : Fin nCols) : ∑ i, (y i : 𝕜) * A i j ≤ c j := by
  have hmem : col j ∈ colList := by
    have hj : (j : Nat) < colList.length := by rw [len_ok.1]; exact j.2
    simp only [col, List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hj, Option.getD_some]
    exact List.getElem_mem hj
  have hok := List.all_eq_true.1 cols_ok _ hmem
  simp only [colOK, Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at hok
  obtain ⟨hidx, hdot⟩ := hok
  have hs := sum_sparse (𝕜 := 𝕜) (R := nRows) Ytree.get (col j).2 hidx
  have : ∑ i, (y i : 𝕜) * A i j = ((colDot Ytree.get (col j).2 : Int) : 𝕜) / (den : 𝕜) := by
    rw [← hs, div_eq_mul_inv, Finset.sum_mul]
    refine Finset.sum_congr rfl fun i _ => ?_
    simp only [y, A]; ring
  rw [this, div_le_iff₀ den_pos, c]
  have : ((colDot Ytree.get (col j).2 : Int) : 𝕜) ≤ ((den * (col j).1 : Int) : 𝕜) := by
    exact_mod_cast hdot
  push_cast at this; linarith

lemma bDot_eq (Y : Nat → Int) (bs : List Int) (i0 : Nat) :
    ((bDot Y bs i0 : Int) : 𝕜) = ∑ k ∈ range bs.length, (Y (i0 + k) : 𝕜) * (bs.getD k 0 : 𝕜) := by
  induction bs generalizing i0 with
  | nil => simp [bDot]
  | cons b bs ih =>
    rw [List.length_cons, Finset.sum_range_succ', bDot]
    push_cast
    rw [ih (i0 + 1)]
    simp [add_comm, add_left_comm]

theorem yb_eq : ∑ i, (y i : 𝕜) * b i = 780 := by
  have h := bDot_eq (𝕜 := 𝕜) Ytree.get bList 0
  rw [bDot_ok, len_ok.2] at h
  simp only [zero_add] at h
  rw [← Fin.sum_univ_eq_sum_range (fun k => (Ytree.get k : 𝕜) * (bList.getD k 0 : 𝕜))] at h
  have : ∑ i, (y i : 𝕜) * b i = (∑ i : Fin nRows, (Ytree.get i : 𝕜) * (bList.getD i 0 : 𝕜)) / den := by
    rw [div_eq_mul_inv, Finset.sum_mul]; refine Finset.sum_congr rfl fun i _ => ?_; simp only [y, b]; ring
  rw [this, ← h]
  have := (den_pos (𝕜 := 𝕜)).ne'
  push_cast; field_simp

/-! ## 3. The class-K floor -/

/-- **Class-K floor, LP form.** Any x ≥ 0 satisfying the exported rows (the native-feasibility map
is the documented Python extraction) has objective ≥ 780. -/
theorem lp_floor (x : Fin nCols → 𝕜) (hx : ∀ j, 0 ≤ x j) (hAx : ∀ i, b i ≤ ∑ j, A i j * x j) :
    780 ≤ ∑ j, c j * x j := by
  have := Floor.weak_duality A b c x y hx hAx y_nonneg yA_le
  rwa [yb_eq] at this

/-- **Every class-K build has ≥ 780 paid stops**: a build whose native maps to a feasible x with
objective ≤ #paid stays. -/
theorem stops_ge_780 {σ : Type*} (x : Fin nCols → 𝕜) (hx : ∀ j, 0 ≤ x j)
    (hAx : ∀ i, b i ≤ ∑ j, A i j * x j) (stays : Finset σ) (hobj : ∑ j, c j * x j ≤ stays.card) :
    (780 : 𝕜) ≤ stays.card :=
  (lp_floor x hx hAx).trans hobj

/-- **Cost form** (FloorGlue.global_floor_of_certificate with the checked certificate): per-stop
cost ≥ κ gives total cost ≥ 780 κ. With 𝕜 = ℝ and κ = 2 ln 2 this is 1,081.31 D0/call. -/
theorem cost_ge_780 {σ : Type*} (x : Fin nCols → 𝕜) (hx : ∀ j, 0 ≤ x j)
    (hAx : ∀ i, b i ≤ ∑ j, A i j * x j) (stays : Finset σ) (cost : σ → 𝕜) (κ : 𝕜) (hκ0 : 0 ≤ κ)
    (hκ : ∀ s ∈ stays, κ ≤ cost s) (hobj : ∑ j, c j * x j ≤ stays.card) :
    κ * 780 ≤ ∑ s ∈ stays, cost s := by
  have := FloorGlue.global_floor_of_certificate A b c x y hx hAx y_nonneg yA_le stays cost κ hκ0 hκ hobj
  rwa [yb_eq] at this

end Field

/-- the real-valued instance: κ = 2 ln 2 per stop. -/
theorem cost_ge_real {σ : Type*} (x : Fin nCols → ℝ) (hx : ∀ j, 0 ≤ x j)
    (hAx : ∀ i, b i ≤ ∑ j, A i j * x j) (stays : Finset σ) (cost : σ → ℝ)
    (hκ : ∀ s ∈ stays, 2 * Real.log 2 ≤ cost s) (hobj : ∑ j, c j * x j ≤ stays.card) :
    2 * Real.log 2 * 780 ≤ ∑ s ∈ stays, cost s :=
  cost_ge_780 x hx hAx stays cost _ (by positivity) hκ hobj

end FloorCert

#print axioms FloorCert.yA_le
#print axioms FloorCert.yb_eq
#print axioms FloorCert.lp_floor
#print axioms FloorCert.stops_ge_780
#print axioms FloorCert.cost_ge_780
#print axioms FloorCert.cost_ge_real
