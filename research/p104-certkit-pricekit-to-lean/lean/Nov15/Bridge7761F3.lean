/-
Bridge7761F3 (lane LEAN-BRIDGE3, Nov 18).  The descents of #7761 are 8 pure chains (kernel-checked):
  chainOKb: step k sits at bank chPos_k with src = ids_k, dst = ids_(k+1) (so b_k = a_(k+1) by sharing), height strictly drops;
  chain lengths 3,3,3,3,4,2,3,2; positions distinct (23); source charts / target charts nodup (in/out <= 1); all betas nonzero;
  descent count over ALL 5746 banks = 23 (chunked), so the 23 chain steps are exactly the descents (and D = 56 from F2).
Kernel only.
-/
import Nov15.Bridge7761F2
import Nov15.Bridge7761D5
namespace Bridge7761
open Finset

def chainOKb : List ℕ → List ℕ → Bool
  | p :: ps, s :: t :: ids =>
      (bS.getD p 0 == s) && (bT.getD p 0 == t) && decide (hp t < hp s) && chainOKb ps (t :: ids)
  | [], [_] => true
  | _, _ => false

theorem chain0 : chainOKb (chPos.getD 0 []) (chIds.getD 0 []) = true := by decide +kernel
theorem chain1 : chainOKb (chPos.getD 1 []) (chIds.getD 1 []) = true := by decide +kernel
theorem chain2 : chainOKb (chPos.getD 2 []) (chIds.getD 2 []) = true := by decide +kernel
theorem chain3 : chainOKb (chPos.getD 3 []) (chIds.getD 3 []) = true := by decide +kernel
theorem chain4 : chainOKb (chPos.getD 4 []) (chIds.getD 4 []) = true := by decide +kernel
theorem chain5 : chainOKb (chPos.getD 5 []) (chIds.getD 5 []) = true := by decide +kernel
theorem chain6 : chainOKb (chPos.getD 6 []) (chIds.getD 6 []) = true := by decide +kernel
theorem chain7 : chainOKb (chPos.getD 7 []) (chIds.getD 7 []) = true := by decide +kernel

theorem chain_lens : chPos.map List.length = [3, 3, 3, 3, 4, 2, 3, 2] := by decide +kernel
theorem chain_count : chPos.length = 8 ∧ chIds.length = 8 := by decide +kernel
theorem pos_nodup : chPos.flatten.Nodup := by decide +kernel
theorem pos_card : chPos.flatten.length = 23 := by decide +kernel
/-- in/out degree ≤ 1: sources (resp. targets) of the 23 descents are pairwise distinct charts. -/
theorem src_nodup : (chIds.flatMap (fun l => l.dropLast)).Nodup := by decide +kernel
theorem dst_nodup : (chIds.flatMap (fun l => l.tail)).Nodup := by decide +kernel
theorem beta_ne : ∀ q ∈ chBeta.flatten, q ≠ 0 := by decide +kernel

def isDesc (s t : ℕ) : ℤ := if hp t < hp s then 1 else 0
theorem nD0 : zs isDesc 0 bS0 bT0 = 0 := by decide +kernel
theorem nD1 : zs isDesc 0 bS1 bT1 = 0 := by decide +kernel
theorem nD2 : zs isDesc 0 bS2 bT2 = 8 := by decide +kernel
theorem nD3 : zs isDesc 8 bS3 bT3 = 23 := by decide +kernel
theorem nDesc : zs isDesc 0 bS bT = 23 := by
  rw [zs_banks, nD0, nD1, nD2, nD3]

end Bridge7761
#print axioms Bridge7761.nDesc
#print axioms Bridge7761.X7761
#print axioms Bridge7761.flow7761
#print axioms Bridge7761.chain4
#print axioms Bridge7761.pos_nodup
