/-
Bridge7761O2 (lane BRIDGE-OUT, Nov 18).  hcov for #7761: every descent bank (src not <= dst) is one of the 23 chain positions chPos.flatten.
covB k := (height of dst < height of src) -> k in chPos.flatten, checked for the 5746 banks in 9 chunks of 650 (decide +kernel on the O(1) tables).
hcov7761 : descent in the chart order (not src <= dst) -> k in chPos.flatten   (nest7761 + finrank_chartOf turn the chart descent into a height drop).
Kernel only.
-/
import Nov15.Bridge7761R2
import Nov15.Bridge7761F3
import Nov15.Bridge7761G2

namespace Bridge7761
open Finset Module

def covB (k : ℕ) : Bool := !(decide (hp (dstId k) < hp (srcId k))) || chPos.flatten.contains k
theorem cv0 : (List.range' 0 650).all covB = true := by decide +kernel
theorem cv1 : (List.range' 650 650).all covB = true := by decide +kernel
theorem cv2 : (List.range' 1300 650).all covB = true := by decide +kernel
theorem cv3 : (List.range' 1950 650).all covB = true := by decide +kernel
theorem cv4 : (List.range' 2600 650).all covB = true := by decide +kernel
theorem cv5 : (List.range' 3250 650).all covB = true := by decide +kernel
theorem cv6 : (List.range' 3900 650).all covB = true := by decide +kernel
theorem cv7 : (List.range' 4550 650).all covB = true := by decide +kernel
theorem cv8 : (List.range' 5200 650).all covB = true := by decide +kernel

theorem cov_chk (k : ℕ) (hk : k < 5746) : covB k = true := by
  have h : ∀ i, i < 9 → (List.range' (650 * i) 650).all covB = true := by
    intro i hi; interval_cases i
    exacts [cv0, cv1, cv2, cv3, cv4, cv5, cv6, cv7, cv8]
  exact List.all_eq_true.1 (h (k / 650) (by omega)) k (by simp only [List.mem_range']; exact ⟨k % 650, by omega, by omega⟩)

theorem hcov7761 (k : ℕ) (hk : k < 5746) (h : ¬ chartOf (srcId k) ≤ chartOf (dstId k)) : k ∈ chPos.flatten := by
  have hs := srcId_lt k hk
  have hd := dstId_lt k hk
  have hlt : hp (dstId k) < hp (srcId k) := by
    rcases nest7761 k hk with h1 | h1
    · exact absurd h1 h
    · have h2 := Submodule.finrank_mono h1
      have e1 := finrank_chartOf _ hs
      have e2 := finrank_chartOf _ hd
      rcases lt_or_eq_of_le h2 with h3 | h3
      · have : (finrank (ZMod 2) (chartOf (dstId k)) : ℤ) < finrank (ZMod 2) (chartOf (srcId k)) := by exact_mod_cast h3
        rw [e1, e2] at this; exact this
      · exact absurd (Submodule.eq_of_le_of_finrank_eq h1 h3 ▸ le_refl _) h
  have hc := cov_chk k hk
  simp only [covB, Bool.or_eq_true, Bool.not_eq_true', decide_eq_false_iff_not, List.contains_iff_mem] at hc
  rcases hc with hc | hc
  · exact absurd hlt hc
  · exact hc

theorem hcov7761' (k : Fin 5746) (h : ¬ chartOf (srcId k) ≤ chartOf (dstId k)) : (k : ℕ) ∈ chPos.flatten :=
  hcov7761 k k.2 h

end Bridge7761
#print axioms Bridge7761.hcov7761
