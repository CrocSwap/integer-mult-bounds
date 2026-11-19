/- Bridge7761R3 BankedGraph climb / cl / Mn / main8 / card for #7761 (fields Fin 1262, ChA7761/ChB7761):
 climbA7761, cl7761, Mn7761, card_Mn7761 : Mn7761.card = 400, main8_7761 : cl = 8 on Mn7761. Kernel only. -/
import Nov15.Bridge7761R3c
namespace Bridge7761
open Finset Module BankNC0
theorem climb_chk (f : ℕ) (hf : f < 1262) : climbB f = true := by
  have h : ∀ i, i < 3 → (List.range' (421 * i) 421).all climbB = true := by
    intro i hi; interval_cases i
    exacts [cb0, cb1, cb2]
  exact List.all_eq_true.1 (h (f / 421) (by omega)) f (by simp only [List.mem_range']; exact ⟨f % 421, by omega, by omega⟩)

def cl7761 (f : Fin 1262) : ℕ := clN f

theorem climbA7761 (f : Fin 1262) : ChA7761 f ≤ ChB7761 f ∧
    finrank (ZMod 2) (ChB7761 f) = finrank (ZMod 2) (ChA7761 f) + cl7761 f := by
  have h := climb_chk f f.2
  simp only [climbB, Bool.and_eq_true, decide_eq_true_eq] at h
  refine ⟨leP_le _ _ (fA_lt f f.2) (fB_lt f f.2) h.1, ?_⟩
  have a := finrank_A f; have b := finrank_B f
  unfold cl7761 clN
  have := h.2
  omega

theorem main8_7761 : ∀ f ∈ Mn7761, cl7761 f = 8 := by
  intro f hf
  have h1 : MB.testBit f = true := by unfold Mn7761 at hf; exact (Finset.mem_filter.1 hf).2
  have := main8_chk f h1
  unfold cl7761 clN; omega

end Bridge7761
#print axioms Bridge7761.climbA7761
#print axioms Bridge7761.card_Mn7761
#print axioms Bridge7761.main8_7761
