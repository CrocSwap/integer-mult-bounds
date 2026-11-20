/-
ChainRowB (lane LEAN-CHAINROW, Nov 18).  Live P104 pattern (labels DF.lq : Fin 104 → Fin 9 → 𝔽₂, charts in
Submodule (ZMod 2) (Fin 9 → ZMod 2) = BankFit chart type).  Kernel only.
 * `lq_odd`             : every live label has odd weight (dot (lq p) (lq p) = 1).
 * `chains_ge_8`        : a layout of pure relay chains realising the pattern has ≥ 8 chains (clique8).
 * `chain_mass_ge_56`   : ≤ 8 pure relay chains realising the pattern ⇒ descent mass ≥ 56.
 * `chain_mass_ge_56_rank8` : any number of chains, stacked φ/c ranks ≤ 8 ⇒ descent mass ≥ 56.
-/
import Nov15.ChainRowA
import Nov15.DecoderWall7

namespace ChainRow
open DecoderWall

theorem lq_odd : ∀ p : Fin 104, dot (DF.lq p) (DF.lq p) = 1 := by
  have : ∀ p : Fin 104, DW4.dotb (DW4.lab p.val) (DW4.lab p.val) = true := by decide +kernel
  intro p
  exact (DF.dotb_iff _ _).1 (this p)

variable {T : Type} [Fintype T]

/-- a layout realising the live pattern needs at least 8 chains. -/
theorem chains_ge_8 (L : ChainLayout ℚ DF.lq T) (hR : L.Realises) : 8 ≤ Fintype.card T :=
  DF.decoder_rows_ge_eight L.W L.U (L.isDecoder lq_odd hR)

/-- **≤ 8 pure relay chains realising the live pattern have descent mass ≥ 56.** -/
theorem chain_mass_ge_56 (L : ChainLayout ℚ DF.lq T) (hR : L.Realises) (h8 : Fintype.card T ≤ 8) :
    56 ≤ L.descentMass := by
  have hd := L.isDecoder lq_odd hR
  have hW : (DW7.Wm L.W).rank ≤ 8 := (Matrix.rank_le_card_width _).trans h8
  have hU : (DW7.Wm L.U).rank ≤ 8 := (Matrix.rank_le_card_width _).trans h8
  exact (DW7.D56_rank8_anyk L.W L.U hd hW hU).trans L.mass_le

/-- same with exactly 8 chains via the 8-row floor (cross-check route). -/
theorem chain_mass_ge_56' (L : ChainLayout ℚ DF.lq T) (hR : L.Realises) (h8 : Fintype.card T ≤ 8) :
    56 ≤ L.descentMass :=
  (DFR.D56_8rows_unc L.W L.U (L.isDecoder lq_odd hR)
    (le_antisymm h8 (chains_ge_8 L hR))).trans L.mass_le

/-- any number of chains whose stacked deposit/gather factors have rank ≤ 8. -/
theorem chain_mass_ge_56_rank8 (L : ChainLayout ℚ DF.lq T) (hR : L.Realises)
    (hW : (DW7.Wm L.W).rank ≤ 8) (hU : (DW7.Wm L.U).rank ≤ 8) : 56 ≤ L.descentMass :=
  (DW7.D56_rank8_anyk L.W L.U (L.isDecoder lq_odd hR) hW hU).trans L.mass_le

end ChainRow

#print axioms ChainRow.lq_odd
#print axioms ChainRow.chains_ge_8
#print axioms ChainRow.chain_mass_ge_56
#print axioms ChainRow.chain_mass_ge_56'
#print axioms ChainRow.chain_mass_ge_56_rank8
