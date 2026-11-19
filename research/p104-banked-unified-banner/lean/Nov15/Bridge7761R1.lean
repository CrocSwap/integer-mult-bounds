/-
Bridge7761R1 .  O(1) chart tables for #7761 (packed in Bridge7761R1D: basis 16-bit slots, pivots 4-bit slots,
9 slots per chart) tied to chBasis / chPiv by one decide, and the chart comparison `leP s t` used for the bank nest / climb / hcov checks.
  ubL / upL     : unpack chart c
  ub_ok         : ubL c = chBasis.getD c [] and upL c = chPiv.getD c []  for all c < 1099
  leP_le        : leP s t = true -> chartOf s <= chartOf t
  pack_bS/bT    : pkw 11 bS = BSK, pkw 11 bT = BTK  (bank src/dst chart ids, O(1) lookups `sl BSK 11 k`)
Kernel only.
-/
import Nov15.Bridge7761R1D
import Nov15.Bridge7761G3

namespace Bridge7761
open Finset Module BankWireC BankFlagB BankNC0

def ubL (c : ℕ) : List ℕ := ((List.range 9).map (fun i => sl BASK 16 (9 * c + i))).takeWhile (· != 0)
def upL (c : ℕ) : List ℕ := (List.range (ubL c).length).map (fun i => sl PVK 4 (9 * c + i))

def ubChk : Bool := ((chBasis.zip chPiv).zip (List.range 1099)).all (fun x => ubL x.2 == x.1.1 && upL x.2 == x.1.2)
theorem ub_chk : ubChk = true := by decide +kernel

theorem ub_ok (c : ℕ) (hc : c < 1099) : ubL c = chBasis.getD c [] ∧ upL c = chPiv.getD c [] := by
  have h1 : c < chBasis.length := by rw [len_chBasis]; exact hc
  have h2 : c < chPiv.length := by rw [len_chPiv]; exact hc
  have h3 : c < ((chBasis.zip chPiv).zip (List.range 1099)).length := by
    simp [List.length_zip, len_chBasis, len_chPiv]; omega
  have := List.all_eq_true.1 ub_chk _ (List.getElem_mem h3)
  simp only [List.getElem_zip, List.getElem_range, Bool.and_eq_true, beq_iff_eq] at this
  rw [List.getD_eq_getElem _ _ h1, List.getD_eq_getElem _ _ h2]; exact this

def leP (s t : ℕ) : Bool := (ubL s).all (inSpanB (ubL t) (upL t))

theorem leP_le (s t : ℕ) (hs : s < 1099) (ht : t < 1099) (h : leP s t = true) : chartOf s ≤ chartOf t := by
  unfold chartOf
  rw [← (ub_ok s hs).1]
  refine cht_le (B' := chBasis.getD t []) (P' := chPiv.getD t []) ?_
  intro b hb
  have := List.all_eq_true.1 h b hb
  rwa [(ub_ok t ht).1, (ub_ok t ht).2] at this

theorem pack_bS : pkw 11 bS = BSK := by decide +kernel
theorem pack_bT : pkw 11 bT = BTK := by decide +kernel

end Bridge7761
#print axioms Bridge7761.ub_ok
#print axioms Bridge7761.leP_le
#print axioms Bridge7761.pack_bT
