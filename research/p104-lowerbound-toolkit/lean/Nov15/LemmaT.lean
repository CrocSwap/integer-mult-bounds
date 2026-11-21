import Mathlib.Data.ZMod.Basic
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Tactic.Ring
/-!
LEMMA T (VALCOUPLE2, VC.md VC2 item 1) and the ALL-OR-NOTHING law (VC.md item 2), abstract versions.
Kernel-only: no sorry / native_decide / new axioms.

Lemma T.  Ports ι, rows κ (finite), mod-4 rows w v : κ → ι → ZMod 4.  `Lam` is a port set.
 H_id   : on every cell (t,s) of Lam×Lam flagged `Odd t s` (odd label dot), sum_k w_k t * v_k s = 2*[t=s].
 H_unif : each row is uniform on Lam on both sides (all entries odd or all even).
 H_nb   : no row is odd on both sides at ports of Lam.
 Triangle-type configuration: distinct a b c ∈ Lam with odd cells (a,a),(a,c),(b,a),(b,c).
 (A triangle with all 9 cells odd gives it.)  Conclusion: False.
The mod-2 / frame / label data are NOT assumed beyond `Odd` being an arbitrary relation.
-/
open Finset

namespace LemmaT

/-- oddness of an element of Z/4 -/
def Od (z : ZMod 4) : Prop := z = 1 ∨ z = 3

instance (z : ZMod 4) : Decidable (Od z) := by unfold Od; infer_instance

/-- per-row "separability": uniform + not both odd ⇒ the 2×2 minor identity mod 4 -/
lemma row_minor (x x' y y' : ZMod 4)
    (hx : Od x ↔ Od x') (hy : Od y ↔ Od y')
    (h1 : ¬ (Od x ∧ Od y)) (h2 : ¬ (Od x ∧ Od y'))
    (h3 : ¬ (Od x' ∧ Od y)) (h4 : ¬ (Od x' ∧ Od y')) :
    x * y + x' * y' = x * y' + x' * y := by
  revert x x' y y'
  decide

variable {ι κ : Type*} [Fintype κ] [DecidableEq ι]

/-- hypotheses of Lemma T bundled as a structure (all named) -/
structure Hyp (w v : κ → ι → ZMod 4) (Lam : Set ι) (Odd : ι → ι → Prop) : Prop where
  H_id : ∀ t ∈ Lam, ∀ s ∈ Lam, Odd t s →
    ∑ k, w k t * v k s = if t = s then 2 else 0
  H_unif_w : ∀ k, ∀ t ∈ Lam, ∀ t' ∈ Lam, (Od (w k t) ↔ Od (w k t'))
  H_unif_v : ∀ k, ∀ s ∈ Lam, ∀ s' ∈ Lam, (Od (v k s) ↔ Od (v k s'))
  H_nb : ∀ k, ∀ t ∈ Lam, ∀ s ∈ Lam, ¬ (Od (w k t) ∧ Od (v k s))

/-- the minor identity summed over rows -/
lemma minor_sum {w v : κ → ι → ZMod 4} {Lam : Set ι} {Odd : ι → ι → Prop}
    (H : Hyp w v Lam Odd) {t t' s s' : ι}
    (ht : t ∈ Lam) (ht' : t' ∈ Lam) (hs : s ∈ Lam) (hs' : s' ∈ Lam) :
    ∑ k, w k t * v k s + ∑ k, w k t' * v k s' =
      ∑ k, w k t * v k s' + ∑ k, w k t' * v k s := by
  rw [← Finset.sum_add_distrib, ← Finset.sum_add_distrib]
  refine Finset.sum_congr rfl fun k _ => ?_
  exact row_minor _ _ _ _ (H.H_unif_w k t ht t' ht') (H.H_unif_v k s hs s' hs')
    (H.H_nb k t ht s hs) (H.H_nb k t ht s' hs') (H.H_nb k t' ht' s hs) (H.H_nb k t' ht' s' hs')

/-- LEMMA T. -/
theorem lemmaT {w v : κ → ι → ZMod 4} {Lam : Set ι} {Odd : ι → ι → Prop}
    (H : Hyp w v Lam Odd) {a b c : ι}
    (ha : a ∈ Lam) (hb : b ∈ Lam) (hc : c ∈ Lam)
    (hab : a ≠ b) (hac : a ≠ c) (hbc : b ≠ c)
    (oaa : Odd a a) (oac : Odd a c) (oba : Odd b a) (obc : Odd b c) : False := by
  have m := minor_sum H ha hb ha hc
  rw [H.H_id a ha a ha oaa, H.H_id a ha c hc oac, H.H_id b hb a ha oba,
    H.H_id b hb c hc obc] at m
  rw [if_pos rfl, if_neg hac, if_neg hab.symm, if_neg hbc] at m
  revert m; decide

/-- Triangle form: three distinct ports of Lam, all nine cells odd. -/
theorem lemmaT_triangle {w v : κ → ι → ZMod 4} {Lam : Set ι} {Odd : ι → ι → Prop}
    (H : Hyp w v Lam Odd) {a b c : ι}
    (ha : a ∈ Lam) (hb : b ∈ Lam) (hc : c ∈ Lam)
    (hab : a ≠ b) (hac : a ≠ c) (hbc : b ≠ c)
    (tri : ∀ x ∈ ({a, b, c} : Set ι), ∀ y ∈ ({a, b, c} : Set ι), Odd x y) : False :=
  lemmaT H ha hb hc hab hac hbc (tri a (by simp) a (by simp)) (tri a (by simp) c (by simp))
    (tri b (by simp) a (by simp)) (tri b (by simp) c (by simp))

/-! ### Non-vacuity: the hypotheses are satisfiable without the triangle (2 ports, 1 row w=1, v=2·..).
 One row, ports Fin 2, Lam = univ, Odd = fun s t => s = t.  w = (1,1), v = (2,0)?  need
 w_0 t v_0 s = 2[t=s] on diagonal cells: w=(1,1), v=(2,2): row sum = 2 on all cells; on odd cells (diagonal) = 2. -/
def exW : Fin 1 → Fin 2 → ZMod 4 := fun _ _ => 1
def exV : Fin 1 → Fin 2 → ZMod 4 := fun _ _ => 2

theorem nonvac : Hyp exW exV Set.univ (fun s t : Fin 2 => s = t) := by
  refine ⟨?_, ?_, ?_, ?_⟩
  · intro t _ s _ h; subst h; simp [exW, exV]
  · intro k t _ t' _; simp [exW]
  · intro k t _ t' _; simp [exV]
  · intro k t _ s _; simp [exW, exV, Od]; decide

/-- ... and the triangle hypothesis is what fails: 3 distinct ports with a triangle contradict any Hyp. -/
example : ¬ ∃ (w v : Fin 2 → Fin 3 → ZMod 4), Hyp w v Set.univ (fun _ _ => True) :=
  fun ⟨w, v, H⟩ => lemmaT H (a := 0) (b := 1) (c := 2) trivial trivial trivial (by decide)
    (by decide) (by decide) trivial trivial trivial trivial

#print axioms lemmaT
#print axioms lemmaT_triangle
#print axioms nonvac

end LemmaT
