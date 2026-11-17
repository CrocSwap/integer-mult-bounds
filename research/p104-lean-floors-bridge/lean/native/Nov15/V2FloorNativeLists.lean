/-
V2FloorNativeLists (lane LEAN-NEXT21, Nov 16): pure list lemmas for the native route: top-M sums, grouping sums by key.
-/
import Mathlib.Data.List.Sort
import Mathlib.Algebra.BigOperators.Group.List.Basic
import Mathlib.Data.List.Perm.Subperm

namespace V2Floor

/-- sum of the M largest entries. -/
def topsum (M : ℕ) (l : List ℕ) : ℕ := ((l.mergeSort (fun a b => decide (b ≤ a))).take M).sum

theorem take_succ_le (x : ℕ) : ∀ (m : List ℕ), (∀ y ∈ m, y ≤ x) → ∀ M, (m.take (M + 1)).sum ≤ x + (m.take M).sum := by
  intro m
  induction m with
  | nil => intro _ M; simp
  | cons y m ih =>
    intro h M
    have hy : y ≤ x := h y (by simp)
    cases M with
    | zero => simp; exact hy
    | succ k =>
      have := ih (fun z hz => h z (by simp [hz])) k
      simp only [List.take_succ_cons, List.sum_cons]
      omega

theorem sub_sorted : ∀ (m s : List ℕ) (M : ℕ), m.Pairwise (fun a b => b ≤ a) → s.Sublist m → s.length ≤ M →
    s.sum ≤ (m.take M).sum := by
  intro m
  induction m with
  | nil => intro s M _ hs _; simp [List.sublist_nil.1 hs]
  | cons x m ih =>
    intro s M hp hs hl
    cases M with
    | zero => simp at hl; subst hl; simp
    | succ M =>
      rw [List.pairwise_cons] at hp
      cases hs with
      | cons _ hs' =>
        have h1 := ih s (M + 1) hp.2 hs' hl
        have h2 := take_succ_le x m hp.1 M
        simp only [List.take_succ_cons, List.sum_cons]
        omega
      | cons_cons _ hs' =>
        simp only [List.length_cons] at hl
        have := ih _ M hp.2 hs' (by omega)
        simp only [List.take_succ_cons, List.sum_cons]
        omega

theorem top_le (M : ℕ) (l s : List ℕ) (hs : s.Sublist l) (hl : s.length ≤ M) : s.sum ≤ topsum M l := by
  unfold topsum
  have hperm := List.mergeSort_perm l (fun a b => decide (b ≤ a))
  have hsorted : (l.mergeSort (fun a b => decide (b ≤ a))).Pairwise (fun a b => b ≤ a) := by
    have := List.pairwise_mergeSort (le := fun a b => decide (b ≤ a))
      (by intro a b c h1 h2; simp at *; omega) (by intro a b; simp; omega) l
    simpa using this
  have hsub : s.Subperm (l.mergeSort (fun a b => decide (b ≤ a))) := hs.subperm.trans hperm.symm.subperm
  obtain ⟨s', hs'p, hs'⟩ := hsub
  have := sub_sorted _ s' M hsorted hs' (by rw [hs'p.length_eq]; exact hl)
  rw [hs'p.sum_eq] at this
  exact this

theorem sum_filter_map_ite {α : Type*} (l : List α) (P : α → Bool) (f : α → ℕ) :
    ((l.filter P).map f).sum = (l.map (fun x => if P x then f x else 0)).sum := by
  induction l with
  | nil => simp
  | cons a l ih =>
    by_cases h : P a = true <;> simp [List.filter_cons, h, ih]

theorem sum_filter_le {α : Type*} (l : List α) (P : α → Bool) (f : α → ℕ) :
    ((l.filter P).map f).sum ≤ (l.map f).sum := by
  induction l with
  | nil => simp
  | cons a l ih =>
    by_cases h : P a = true <;> simp [List.filter_cons, h] <;> omega

theorem sum_group {α κ : Type*} [DecidableEq κ] (key : α → κ) (f : α → ℕ) :
    ∀ (U : List κ) (R : List α), U.Nodup → (∀ r ∈ R, key r ∈ U) →
    (R.map f).sum = (U.map (fun u => ((R.filter (fun r => decide (key r = u))).map f).sum)).sum := by
  intro U
  induction U with
  | nil =>
    intro R _ hk
    cases R with
    | nil => simp
    | cons r R => exact absurd (hk r (by simp)) (by simp)
  | cons u U ih =>
    intro R hnd hk
    rw [List.nodup_cons] at hnd
    have hperm := List.filter_append_perm (fun r => decide (key r = u)) R
    have h1 : (R.map f).sum = ((R.filter (fun r => decide (key r = u))).map f).sum +
        ((R.filter (fun r => !decide (key r = u))).map f).sum := by
      rw [← List.sum_append, ← List.map_append]
      exact (hperm.map f).sum_eq.symm
    have hk' : ∀ r ∈ R.filter (fun r => !decide (key r = u)), key r ∈ U := by
      intro r hr
      rw [List.mem_filter] at hr
      have h2 := hk r hr.1
      have h3 : key r ≠ u := by simpa using hr.2
      rcases List.mem_cons.1 h2 with h | h
      · exact absurd h h3
      · exact h
    have h2 := ih _ hnd.2 hk'
    rw [h1, h2, List.map_cons, List.sum_cons]
    congr 1
    congr 1
    apply List.map_congr_left
    intro u' hu'
    have hne : u' ≠ u := fun h => hnd.1 (h ▸ hu')
    rw [List.filter_filter]
    congr 2
    apply List.filter_congr
    intro r _
    by_cases h : key r = u'
    · simp [h, hne]
    · simp [h]

end V2Floor
