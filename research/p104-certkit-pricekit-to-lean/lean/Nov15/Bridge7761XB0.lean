/-
Bridge7761XBal (lane LEAN-BRIDGE2, Nov 18).  #7761's moves as an `XBal.Model` (charts = its 1099 frames, 5746 banks, 1262 public fields
born at fA, finishing at fB, NO owned registers) with `Flow` (per-chart conservation) and W = 0 decide-checked:
  flow7761 : Flow, W7761 : W = 0, D7761 : D = 56, A7761 : A = 9721, climb7761 : Σc = 9665, X7761 : X = 112 = 2·D.
Kernel only (decide +kernel on data; no sorry/native_decide/axioms).
-/
import Nov15.XBalA
import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Algebra.BigOperators.Intervals
import Nov15.Bridge7761D1
import Nov15.Bridge7761D2
import Nov15.Bridge7761D3

namespace Bridge7761
open Finset

abbrev CF := Fin 1099

def fin1099 (x : ℕ) : CF := ⟨x % 1099, Nat.mod_lt _ (by norm_num)⟩

def hgt (c : ℕ) : ℤ := ((chBasis.getD c []).length : ℤ)

/-- the #7761 event-list model: charts 1099, banks 5746 (schedule order), fields 1262, no owned registers. -/
def model : XBal.Model CF (Fin 5746) (Fin 1262) Empty where
  h c := hgt c.val
  src m := fin1099 (bS.getD m 0)
  dst m := fin1099 (bT.getD m 0)
  ini f := fin1099 (fA.getD f 0)
  fin f := fin1099 (fB.getD f 0)
  oinit e := e.elim
  oclear e := e.elim

theorem sum_cnt_list (l : List ℕ) (c : ℕ) :
    ∑ i ∈ range l.length, (if l.getD i 0 = c then 1 else 0) = l.count c := by
  induction l with
  | nil => simp
  | cons a l ih =>
    rw [List.length_cons, Finset.sum_range_succ' _ l.length]
    simp only [List.getD_cons_succ, List.getD_cons_zero, ih, List.count_cons]
    by_cases h : a = c
    · subst h; simp
    · have : ¬ (a == c) = true := by simpa using h
      simp [h, this]

theorem cnt_list {n : ℕ} (l : List ℕ) (hl : l.length = n) (hlt : ∀ x ∈ l, x < 1099) (c : CF) :
    XBal.Model.cnt (fun m : Fin n => fin1099 (l.getD m 0)) c = (l.count c.val : ℤ) := by
  unfold XBal.Model.cnt
  have key : (univ.filter (fun m : Fin n => fin1099 (l.getD m 0) = c)).card = l.count c.val := by
    rw [Finset.card_eq_sum_ones, Finset.sum_filter]
    rw [Fin.sum_univ_eq_sum_range (fun i => if fin1099 (l.getD i 0) = c then 1 else 0) n]
    subst hl
    have : ∀ i ∈ range l.length, (if fin1099 (l.getD i 0) = c then 1 else 0)
        = if l.getD i 0 = c.val then 1 else 0 := by
      intro i hi
      have hi' := Finset.mem_range.mp hi
      have hm : l.getD i 0 ∈ l := by
        simp only [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hi', Option.getD_some]
        exact List.getElem_mem _
      have hv := hlt _ hm
      have : (fin1099 (l.getD i 0) = c) ↔ l.getD i 0 = c.val := by
        generalize l.getD i 0 = x at hv ⊢
        unfold fin1099
        rw [Fin.ext_iff]; simp only [Nat.mod_eq_of_lt hv]
      simp only [this]
    rw [Finset.sum_congr rfl this]
    exact sum_cnt_list l c.val
  exact_mod_cast key

end Bridge7761
