/-
BridgeGNet (lane BRIDGE, Nov 20).  The word -> network bridge, read in NetContract's GNet convention (field ℚ, labels
q = DF.lq in F2^9, DAG order <, b_k ≤ a_k, N = Nmat H with N = 1 + H N), so the tight-chain contraction results
(NetContract) and the bowtie theorem (NetBowtie) apply to EVERY legal word's network.  What stays a premise:
the bowtie data BData of some iterated contraction (a genuine restriction on the network shape) and the decoder wall.
Kernel only.
-/
import Nov15.BridgeNet
import Nov15.NetContract

set_option linter.unusedSectionVars false

namespace BridgeNet
open WordModel Matrix

variable {Pt Hl Ow : Type} [Fintype Pt] [Fintype Hl] [Fintype Ow]
  [DecidableEq Pt] [DecidableEq Hl] [DecidableEq Ow]

/-- the target pattern of the caller on odd cells: c_s δ_sp with c_s = 1 (D port) or 1/2 (B port). -/
noncomputable def recOf (cl : Caller Pt) (σ : Fin 104 ≃ Pt) : Fin 104 → Fin 104 → ℚ :=
  fun s p => if s = p then (if cl.isD (σ s) then 1 else 1 / 2) else 0

theorem word_gnet (cl : Caller Pt) {s : St (Reg Pt Hl Ow)} (hw : Word cl s) (hcs : ChartsSubsp s)
    (hn : OwnedNested s) (σ : Fin 104 ≃ Pt) (hlab : ∀ i, cl.lab (σ i) = DW4.lab i) :
    ∃ (n : ℕ) (Nt : NetContract.GNet ℚ (Fin 104) (Fin n) 9), Nt.q = DF.lq ∧ Nt.D = ownDrop s ∧
      ∀ t p, Nt.q t ⬝ᵥ Nt.q p = 1 → (Nt.G * Nt.N * Nt.F) t p = recOf cl σ t p := by
  obtain ⟨n, N, hd, hba, hc⟩ := word_netW cl hw hcs hn σ hlab
  have hN1 : N8.Nmat N.H = 1 + N.H * N8.Nmat N.H := by
    have e := N8.mul_Nmat N.H N.hHlt
    rw [Matrix.sub_mul, Matrix.one_mul] at e
    exact eq_add_of_sub_eq e
  refine ⟨n,
    { q := DF.lq
      lt := fun a b => a < b
      ltrans := fun a b c h1 h2 => lt_trans h1 h2
      lirr := fun a => lt_irrefl a
      a := N.a
      b := N.b
      hba := hba
      F := N.F
      G := N.G
      H := N.H
      N := N8.Nmat N.H
      hF := N.hF
      hG := N.hG
      hHlt := N.hHlt
      hH := N.hH
      hN1 := hN1 }, rfl, hd, ?_⟩
  intro t p h
  have := N.hM t p h
  rw [this, hc]
  rfl

/-- **bowtie corollary, Wall56 the only premise beyond the shape**: if some iterated tight-chain contraction of the
word's network carries bowtie data, then Wall56 (in FutureAttr.Wall form, for the caller's odd-cell pattern) gives
owned descent >= 56. -/
theorem word_bowtie_wall (cl : Caller Pt) {s : St (Reg Pt Hl Ow)} (hw : Word cl s) (hcs : ChartsSubsp s)
    (hn : OwnedNested s) (σ : Fin 104 ≃ Pt) (hlab : ∀ i, cl.lab (σ i) = DW4.lab i) :
    ∃ (n : ℕ) (Nt : NetContract.GNet ℚ (Fin 104) (Fin n) 9), Nt.D = ownDrop s ∧
      ∀ (γ : Type) [Fintype γ] [DecidableEq γ] (Nt' : NetContract.GNet ℚ (Fin 104) (Fin n) 9),
        NetContract.Reach Nt Nt' → NetContract.BData Nt' γ →
        FutureAttr.Wall DF.lq (recOf cl σ) 56 → 56 ≤ ownDrop s := by
  obtain ⟨n, Nt, hq, hd, hM⟩ := word_gnet cl hw hcs hn σ hlab
  refine ⟨n, Nt, hd, fun γ _ _ Nt' hR B hwall => ?_⟩
  rw [← hd]
  exact NetContract.contract_D_ge_of_wall hR B 56 (recOf cl σ) hM (by rw [hq]; exact hwall)

end BridgeNet

#print axioms BridgeNet.word_gnet
#print axioms BridgeNet.word_bowtie_wall
