/-
UniInhabitWs4Hist (lane UNI-INHABIT, Nov 19).  Price / credit histograms of the tWs4 fold tables (decide +kernel):
bank prices |HD_k - HS_k| (6250 banks) and helper climbs FF - FI over the 1101 helpers (json index lk hI i).
Core Lean only.
-/
import Nov15.UniInhabitWs4Facts

namespace UniInhabitWs4

def dhN (a b : Nat) : Nat := if a ≤ b then b - a else a - b
def nb (X j : Nat) : Nat := X / 16 ^ j % 16
def prc (j : Nat) : Nat := dhN (nb TWs4Data.HS j) (nb TWs4Data.HD j)
def clm (i : Nat) : Nat := nb TWs4Data.FF (lk Tabs.hI i) - nb TWs4Data.FI (lk Tabs.hI i)

theorem prc_lt : (List.range 6250).all (fun j => Nat.blt (prc j) 10) = true := by decide +kernel
theorem clm_ok : ∀ i < 1101, nb TWs4Data.FI (lk Tabs.hI i) ≤ nb TWs4Data.FF (lk Tabs.hI i) ∧ clm i < 10 := by decide +kernel

theorem prc_0 : ((List.range 6250).filter (fun j => Nat.beq (prc j) 0)).length = 0 := by decide +kernel
theorem clm_0 : ((List.range 1101).filter (fun i => Nat.beq (clm i) 0)).length = 0 := by decide +kernel
theorem prc_1 : ((List.range 6250).filter (fun j => Nat.beq (prc j) 1)).length = 3983 := by decide +kernel
theorem clm_1 : ((List.range 1101).filter (fun i => Nat.beq (clm i) 1)).length = 18 := by decide +kernel
theorem prc_2 : ((List.range 6250).filter (fun j => Nat.beq (prc j) 2)).length = 935 := by decide +kernel
theorem clm_2 : ((List.range 1101).filter (fun i => Nat.beq (clm i) 2)).length = 21 := by decide +kernel
theorem prc_3 : ((List.range 6250).filter (fun j => Nat.beq (prc j) 3)).length = 644 := by decide +kernel
theorem clm_3 : ((List.range 1101).filter (fun i => Nat.beq (clm i) 3)).length = 47 := by decide +kernel
theorem prc_4 : ((List.range 6250).filter (fun j => Nat.beq (prc j) 4)).length = 292 := by decide +kernel
theorem clm_4 : ((List.range 1101).filter (fun i => Nat.beq (clm i) 4)).length = 225 := by decide +kernel
theorem prc_5 : ((List.range 6250).filter (fun j => Nat.beq (prc j) 5)).length = 354 := by decide +kernel
theorem clm_5 : ((List.range 1101).filter (fun i => Nat.beq (clm i) 5)).length = 80 := by decide +kernel
theorem prc_6 : ((List.range 6250).filter (fun j => Nat.beq (prc j) 6)).length = 25 := by decide +kernel
theorem clm_6 : ((List.range 1101).filter (fun i => Nat.beq (clm i) 6)).length = 45 := by decide +kernel
theorem prc_7 : ((List.range 6250).filter (fun j => Nat.beq (prc j) 7)).length = 11 := by decide +kernel
theorem clm_7 : ((List.range 1101).filter (fun i => Nat.beq (clm i) 7)).length = 19 := by decide +kernel
theorem prc_8 : ((List.range 6250).filter (fun j => Nat.beq (prc j) 8)).length = 6 := by decide +kernel
theorem clm_8 : ((List.range 1101).filter (fun i => Nat.beq (clm i) 8)).length = 32 := by decide +kernel
theorem prc_9 : ((List.range 6250).filter (fun j => Nat.beq (prc j) 9)).length = 0 := by decide +kernel
theorem clm_9 : ((List.range 1101).filter (fun i => Nat.beq (clm i) 9)).length = 614 := by decide +kernel

end UniInhabitWs4
