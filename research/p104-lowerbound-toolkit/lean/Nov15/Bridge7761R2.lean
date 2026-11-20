/-
Bridge7761R2 (lane LEAN-BRIDGE6, Nov 18).  BankedGraph.nest for #7761: for every bank position k < 5746 the source and destination charts
(chartOf (bS k), chartOf (bT k)) are comparable; all bank chart ids < 1099.  Chunks R2a-R2e (15 x 400 banks) on the O(1) packed chart tables of R1.
Kernel only.
-/
import Nov15.Bridge7761R2e
namespace Bridge7761
open Finset Module

theorem nest_chk (k : ℕ) (hk : k < 5746) : nestB k = true := by
  have h : ∀ i, i < 15 → (List.range' (400 * i) 400).all nestB = true := by
    intro i hi; interval_cases i
    exacts [nc0, nc1, nc2, nc3, nc4, nc5, nc6, nc7, nc8, nc9, nc10, nc11, nc12, nc13, nc14]
  have := List.all_eq_true.1 (h (k / 400) (by omega)) k (by simp only [List.mem_range']; exact ⟨k % 400, by omega, by omega⟩)
  exact this

theorem srcId_lt (k : ℕ) (hk : k < 5746) : srcId k < 1099 := by
  have := nest_chk k hk; simp only [nestB, Bool.and_eq_true, decide_eq_true_eq] at this; exact this.1.1
theorem dstId_lt (k : ℕ) (hk : k < 5746) : dstId k < 1099 := by
  have := nest_chk k hk; simp only [nestB, Bool.and_eq_true, decide_eq_true_eq] at this; exact this.1.2

theorem nest7761 (k : ℕ) (hk : k < 5746) : chartOf (srcId k) ≤ chartOf (dstId k) ∨ chartOf (dstId k) ≤ chartOf (srcId k) := by
  have := nest_chk k hk
  simp only [nestB, Bool.and_eq_true, Bool.or_eq_true, decide_eq_true_eq] at this
  rcases this.2 with h | h
  · exact Or.inl (leP_le _ _ (srcId_lt k hk) (dstId_lt k hk) h)
  · exact Or.inr (leP_le _ _ (dstId_lt k hk) (srcId_lt k hk) h)

end Bridge7761
#print axioms Bridge7761.nest7761
