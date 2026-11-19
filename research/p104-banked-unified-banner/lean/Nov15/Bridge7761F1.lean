/-
Bridge7761F1 .  O(n) packed-histogram encoding: hist l = foldl (acc + 65536^x) 0 l (one GMP add per list step),
generic lemma `count_eq_of_hist` (equal histograms => equal per-chart counts when counts < 65536), then
  flow7761 : model.Flow   (all 1099 charts at once; a single Nat equality checked by decide +kernel).
Kernel only.
-/
import Nov15.Bridge7761XBal
namespace Bridge7761
open Finset

def histF (l : List ℕ) : ℕ := l.foldl (fun acc x => acc + 65536 ^ x) 0

theorem foldl_hist (l : List ℕ) (a : ℕ) :
    l.foldl (fun acc x => acc + 65536 ^ x) a = a + (l.map (fun x => 65536 ^ x)).sum := by
  induction l generalizing a with
  | nil => simp
  | cons x l ih => simp only [List.foldl_cons, List.map_cons, List.sum_cons, ih]; ring

theorem hist_count (n : ℕ) (l : List ℕ) (hl : ∀ x ∈ l, x < n) :
    histF l = ∑ c ∈ range n, l.count c * 65536 ^ c := by
  unfold histF; rw [foldl_hist, zero_add]
  induction l with
  | nil => simp
  | cons a l ih =>
    have ha : a < n := hl a List.mem_cons_self
    have ih' := ih (fun x hx => hl x (List.mem_cons_of_mem _ hx))
    simp only [List.map_cons, List.sum_cons, ih', List.count_cons, add_mul, Finset.sum_add_distrib]
    have : ∑ c ∈ range n, (if (a == c) = true then 1 else 0) * 65536 ^ c = 65536 ^ a := by
      have h1 : ∀ c ∈ range n, (if (a == c) = true then 1 else 0) * 65536 ^ c
          = if a = c then 65536 ^ a else 0 := by
        intro c _
        by_cases h : a = c
        · subst h; simp
        · have : ¬ (a == c) = true := by simpa using h
          simp [h, this]
      rw [Finset.sum_congr rfl h1, Finset.sum_ite_eq]; simp [ha]
    rw [this]; ring

theorem digits_inj : ∀ (n : ℕ) (f g : ℕ → ℕ), (∀ c, c < n → f c < 65536) → (∀ c, c < n → g c < 65536) →
    ∑ c ∈ range n, f c * 65536 ^ c = ∑ c ∈ range n, g c * 65536 ^ c → ∀ c, c < n → f c = g c := by
  intro n
  induction n with
  | zero => intro f g _ _ _ c hc; omega
  | succ n ih =>
    intro f g hf hg h c hc
    rw [Finset.sum_range_succ', Finset.sum_range_succ'] at h
    have e1 : ∀ (u : ℕ → ℕ), ∑ i ∈ range n, u (i + 1) * 65536 ^ (i + 1) = 65536 * ∑ i ∈ range n, u (i + 1) * 65536 ^ i := by
      intro u; rw [Finset.mul_sum]; refine Finset.sum_congr rfl fun i _ => by ring
    rw [e1, e1] at h
    simp only [pow_zero, mul_one] at h
    have f0 := hf 0 (by omega); have g0 := hg 0 (by omega)
    have h0 : f 0 = g 0 := by
      have := congrArg (· % 65536) h
      simp only [Nat.mul_add_mod, Nat.mod_eq_of_lt f0, Nat.mod_eq_of_lt g0] at this
      exact this
    have h1 : ∑ i ∈ range n, f (i + 1) * 65536 ^ i = ∑ i ∈ range n, g (i + 1) * 65536 ^ i := by
      rw [h0] at h; omega
    cases c with
    | zero => exact h0
    | succ c =>
      exact ih (fun i => f (i + 1)) (fun i => g (i + 1)) (fun i hi => hf _ (by omega)) (fun i hi => hg _ (by omega)) h1 c (by omega)

theorem count_eq_of_hist (n : ℕ) (a b c d : List ℕ)
    (ha : ∀ x ∈ a, x < n) (hb : ∀ x ∈ b, x < n) (hc : ∀ x ∈ c, x < n) (hd : ∀ x ∈ d, x < n)
    (hlt : ∀ x, x < n → a.count x + b.count x < 65536 ∧ c.count x + d.count x < 65536)
    (h : histF a + histF b = histF c + histF d) :
    ∀ x, x < n → a.count x + b.count x = c.count x + d.count x := by
  rw [hist_count n a ha, hist_count n b hb, hist_count n c hc, hist_count n d hd,
    ← Finset.sum_add_distrib, ← Finset.sum_add_distrib] at h
  refine digits_inj n (fun x => a.count x + b.count x) (fun x => c.count x + d.count x)
    (fun x hx => (hlt x hx).1) (fun x hx => (hlt x hx).2) ?_
  simpa only [add_mul] using h

theorem hist_flow : histF bT + histF fA = histF bS + histF fB := by decide +kernel


theorem count_le_bound : ∀ x, x < 1099 → bT.count x + fA.count x < 65536 ∧ bS.count x + fB.count x < 65536 := by
  intro x _
  have h1 := List.count_le_length (a := x) (l := bT)
  have h2 := List.count_le_length (a := x) (l := fA)
  have h3 := List.count_le_length (a := x) (l := bS)
  have h4 := List.count_le_length (a := x) (l := fB)
  rw [len_bT] at h1; rw [len_fA] at h2; rw [len_bS] at h3; rw [len_fB] at h4
  omega

theorem counts7761 : ∀ x, x < 1099 → bT.count x + fA.count x = bS.count x + fB.count x :=
  count_eq_of_hist 1099 bT fA bS fB lt_bT lt_fA lt_bS lt_fB count_le_bound hist_flow

theorem flow7761 : model.Flow := by
  intro c
  have e : ∀ {α : Type} [Fintype α] (f : α → CF), XBal.Model.cnt f c = XBal.Model.cnt f c := fun _ => rfl
  have h1 : XBal.Model.cnt model.dst c = (bT.count c.val : ℤ) := cnt_list bT len_bT lt_bT c
  have h2 : XBal.Model.cnt model.src c = (bS.count c.val : ℤ) := cnt_list bS len_bS lt_bS c
  have h3 : XBal.Model.cnt model.ini c = (fA.count c.val : ℤ) := cnt_list fA len_fA lt_fA c
  have h4 : XBal.Model.cnt model.fin c = (fB.count c.val : ℤ) := cnt_list fB len_fB lt_fB c
  have h5 : XBal.Model.cnt model.oinit c = 0 := by simp [XBal.Model.cnt]
  have h6 : XBal.Model.cnt model.oclear c = 0 := by simp [XBal.Model.cnt]
  rw [h1, h2, h3, h4, h5, h6]
  have := counts7761 c.val (by have := c.2; omega)
  omega

end Bridge7761
