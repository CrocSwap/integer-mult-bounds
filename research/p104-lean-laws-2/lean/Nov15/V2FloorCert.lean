/-
V2FloorCert: the V2-FLOOR level-cut dual bound, Lean part (lane LEAN-NEXT20, Nov 16). See V2FloorCert.md.

Model (REBUILDKIT/v2/floor/FLOOR.md). Nodes: subspaces of F₂⁹ (any partial order with a monotone `dim` works here). A plan is a
finite edge set E of strict containments X < Y (shared stops, any Steiner nodes), each edge priced w(dim X, dim Y). A plan
REALISES pair p = (L_p, U_p) if U_p is reachable from L_p along edges of E (start-anywhere relay; open-ended chains excluded).
Dual: y p k ≥ 0 per pair and level, gain p X Y = Σ_{dim X ≤ k < dim Y} y p k. Feasibility (check.c's constraint, unrelaxed):
for every X < Y, Σ_{p : L_p ≤ X, Y ≤ U_p} gain p X Y ≤ w(dim X, dim Y).

`weak_duality`: every plan realising all pairs costs ≥ Σ_p gain p L_p U_p. No LP solver, no certificate data: this is the
generic half. The certificate half (feasibility of the exported y on F₂⁹, and the log arithmetic in w) is stated as the
hypothesis `Feasible` here; see V2FloorCert.md for what is and is not yet kernel-checked.
-/
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Algebra.Order.Field.Basic
import Mathlib.Data.Real.Basic
import Mathlib.Order.Interval.Finset.Nat
import Mathlib.Algebra.BigOperators.Intervals

namespace V2Floor
open Finset

variable {V P : Type*} [PartialOrder V] [Fintype P] [DecidableEq V] [DecidableLE V]

/-- reachability along plan edges. -/
inductive Reach (E : Finset (V × V)) : V → V → Prop
  | refl (X : V) : Reach E X X
  | step {X Y Z : V} : (X, Y) ∈ E → Reach E Y Z → Reach E X Z

variable (dim : V → ℕ) (y : P → ℕ → ℝ)

/-- the level gain of pair p on X → Y. -/
def gain (p : P) (X Y : V) : ℝ := ∑ k ∈ Ico (dim X) (dim Y), y p k

theorem Reach.le {E : Finset (V × V)} (hE : ∀ e ∈ E, e.1 < e.2) {X Z : V} (h : Reach E X Z) : X ≤ Z := by
  induction h with
  | refl X => exact le_rfl
  | step hXY _ ih => exact le_trans (le_of_lt (hE _ hXY)) ih

theorem gain_nonneg (hy : ∀ p k, 0 ≤ y p k) (p : P) (X Y : V) : 0 ≤ gain dim y p X Y :=
  sum_nonneg fun k _ => hy p k

/-- along a path X ⇝ Z, the gain telescopes and is paid by the path's edges, all of which lie in [X, Z]. -/
theorem gain_le_path (E : Finset (V × V)) (hE : ∀ e ∈ E, e.1 < e.2) (hmono : Monotone dim)
    (hy : ∀ p k, 0 ≤ y p k) (p : P) {X Z : V} (h : Reach E X Z) :
    gain dim y p X Z ≤ ∑ e ∈ E.filter (fun e => X ≤ e.1 ∧ e.2 ≤ Z), gain dim y p e.1 e.2 := by
  classical
  induction h with
  | refl X =>
    simp only [gain, Ico_self, sum_empty]
    exact sum_nonneg fun e _ => gain_nonneg dim y hy p _ _
  | @step X Y Z hXY hYZ ih =>
    have hlt : X < Y := hE _ hXY
    have hYZle : Y ≤ Z := hYZ.le hE
    have hsplit : gain dim y p X Z = gain dim y p X Y + gain dim y p Y Z := by
      unfold gain
      rw [sum_Ico_consecutive _ (hmono hlt.le) (hmono hYZle)]
    rw [hsplit]
    -- the IH edges and the edge (X, Y) are disjoint parts of the X-filter
    have hsub : E.filter (fun e => Y ≤ e.1 ∧ e.2 ≤ Z) ⊆ (E.filter (fun e => X ≤ e.1 ∧ e.2 ≤ Z)).erase (X, Y) := by
      intro e he
      simp only [mem_filter] at he
      simp only [mem_erase, mem_filter, ne_eq]
      refine ⟨?_, he.1, le_trans hlt.le he.2.1, he.2.2⟩
      rintro rfl
      exact absurd he.2.1 (not_le_of_gt hlt)
    have hmem : (X, Y) ∈ E.filter (fun e => X ≤ e.1 ∧ e.2 ≤ Z) := by
      simp only [mem_filter]; exact ⟨hXY, le_rfl, hYZle⟩
    rw [← add_sum_erase _ _ hmem]
    refine add_le_add le_rfl (le_trans ih ?_)
    exact sum_le_sum_of_subset_of_nonneg hsub fun e _ _ => gain_nonneg dim y hy p _ _

/-- **Weak duality.** If y ≥ 0 is feasible on every strict containment, every plan E (edges strictly increasing) that
realises every pair costs at least Σ_p gain p L_p U_p. -/
theorem weak_duality (L U : P → V) (w : ℕ → ℕ → ℝ) (hmono : Monotone dim) (hy : ∀ p k, 0 ≤ y p k)
    (hfeas : ∀ X Y : V, X < Y →
      ∑ p ∈ univ.filter (fun p => L p ≤ X ∧ Y ≤ U p), gain dim y p X Y ≤ w (dim X) (dim Y))
    (E : Finset (V × V)) (hE : ∀ e ∈ E, e.1 < e.2) (hreal : ∀ p, Reach E (L p) (U p)) :
    ∑ p, gain dim y p (L p) (U p) ≤ ∑ e ∈ E, w (dim e.1) (dim e.2) := by
  classical
  calc ∑ p, gain dim y p (L p) (U p)
      ≤ ∑ p, ∑ e ∈ E.filter (fun e => L p ≤ e.1 ∧ e.2 ≤ U p), gain dim y p e.1 e.2 :=
        sum_le_sum fun p _ => gain_le_path dim y E hE hmono hy p (hreal p)
    _ = ∑ p, ∑ e ∈ E, if L p ≤ e.1 ∧ e.2 ≤ U p then gain dim y p e.1 e.2 else 0 := by
        refine sum_congr rfl fun p _ => ?_
        rw [sum_filter]
    _ = ∑ e ∈ E, ∑ p, if L p ≤ e.1 ∧ e.2 ≤ U p then gain dim y p e.1 e.2 else 0 := sum_comm
    _ = ∑ e ∈ E, ∑ p ∈ univ.filter (fun p => L p ≤ e.1 ∧ e.2 ≤ U p), gain dim y p e.1 e.2 := by
        refine sum_congr rfl fun e _ => ?_
        rw [sum_filter]
    _ ≤ ∑ e ∈ E, w (dim e.1) (dim e.2) := sum_le_sum fun e he => hfeas e.1 e.2 (hE e he)

/-- **Class reduction.** The constraint of an edge X < Y only sees its served pair set. If S ⊇ served(X, Y) and the
class inequality Σ_{p ∈ S} gain ≤ w holds (gains depend only on the levels dim X, dim Y), the edge is feasible. This is
the step that lets a finite list of closed pair-classes (r2/classes.c) stand for all 6.9M subspaces. -/
theorem feasible_of_class (L U : P → V) (w : ℕ → ℕ → ℝ) (hy : ∀ p k, 0 ≤ y p k) (X Y : V) (S : Finset P)
    (hS : univ.filter (fun p => L p ≤ X ∧ Y ≤ U p) ⊆ S)
    (hcl : ∑ p ∈ S, gain dim y p X Y ≤ w (dim X) (dim Y)) :
    ∑ p ∈ univ.filter (fun p => L p ≤ X ∧ Y ≤ U p), gain dim y p X Y ≤ w (dim X) (dim Y) :=
  le_trans (sum_le_sum_of_subset_of_nonneg hS fun p _ _ => gain_nonneg dim y hy p X Y) hcl

end V2Floor
