/-
BridgeNetInst (lane BRIDGE, Nov 20).  The word -> NetW bridge for the concrete #7113 caller (UniFold7113Inst.caller7113,
the caller of t7669 / w_s4): its 104 port labels ARE the P104 labels DW4.labs up to the explicit permutation σ7113
(decide), so the label premise of BridgeNet.word_netW is discharged.  The 8 non-D ports 15,17,27,34,35,42,47,55 are
exactly the images of P104 indices 96..103.  Kernel only.
-/
import Nov15.BridgeNet
import Nov15.UniFold7113Inst

namespace BridgeNet
open WordModel UniFold7113

def sigL : List ℕ := [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 18, 19, 20, 21, 22, 23, 24, 25, 26, 28, 29, 30, 31, 32, 33, 36, 37, 38, 39, 40, 41, 43, 44, 45, 46, 48, 49, 50, 51, 52, 53, 54, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 15, 34, 47, 27, 42, 17, 55, 35]
def invL : List ℕ := [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 96, 15, 101, 16, 17, 18, 19, 20, 21, 22, 23, 24, 99, 25, 26, 27, 28, 29, 30, 97, 103, 31, 32, 33, 34, 35, 36, 100, 37, 38, 39, 40, 98, 41, 42, 43, 44, 45, 46, 47, 102, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95]

def sigF (i : Fin 104) : Fin 104 := ⟨sigL.getD i 0 % 104, Nat.mod_lt _ (by norm_num)⟩
def invF (i : Fin 104) : Fin 104 := ⟨invL.getD i 0 % 104, Nat.mod_lt _ (by norm_num)⟩

theorem sig_left : ∀ i, invF (sigF i) = i := by decide
theorem sig_right : ∀ i, sigF (invF i) = i := by decide

/-- the port permutation: P104 index i ↦ #7113 port index. -/
def σ7113 : Fin 104 ≃ Fin 104 := ⟨sigF, invF, sig_left, sig_right⟩

theorem hlab7113 : ∀ i : Fin 104, caller7113.lab (σ7113 i) = DW4.lab i := by
  show ∀ i : Fin 104, lab7113 (sigF i) = DW4.lab i
  decide +kernel

theorem nonD_images : ∀ i : Fin 104, caller7113.isD (σ7113 i) = decide (i.1 < 96) := by
  show ∀ i : Fin 104, isD7113 (sigF i) = decide (i.1 < 96)
  decide +kernel

/-- **BRIDGE at the #7113 caller**: every legal word of the #7113 caller (any helper / owned register types) with the
verifier clauses ChartsSubsp and OwnedNested is a P104 NetW whose total drop is its owned descent, with >= 8 gathering
and >= 8 depositing nodes, the DX level cut, and the NET8 node corollary. -/
theorem word7113_net_laws {Hl Ow : Type} [Fintype Hl] [Fintype Ow] [DecidableEq Hl] [DecidableEq Ow]
    {s : St (Reg (Fin 104) Hl Ow)} (hw : Word caller7113 s) (hcs : ChartsSubsp s) (hn : OwnedNested s) :
    ∃ (n : ℕ) (N : N8.NetW n), (∑ k, N.drop k = ownDrop s) ∧ (∀ k, N.b k ≤ N.a k) ∧
      8 ≤ (N8.gatS N).card ∧ 8 ≤ (N8.depS N).card ∧
      (∀ L : Finset ℕ, ∑ l ∈ L, (N8.Mstar N.G N.H N.F N.da N.db l).rank ≤ ownDrop s) ∧
      ((N8.gatS N).card ≤ 8 → (N8.depS N).card ≤ 8 → 56 ≤ ownDrop s) :=
  word_net_laws caller7113 hw hcs hn σ7113 hlab7113

end BridgeNet

#print axioms BridgeNet.hlab7113
#print axioms BridgeNet.word7113_net_laws
