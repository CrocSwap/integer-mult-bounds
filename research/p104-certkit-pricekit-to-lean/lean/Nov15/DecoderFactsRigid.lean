/-
DecoderFactsRigid (lane LEAN-WIRE, Nov 18).  Wires DW6.rigid_gram (DYADICPORTS rigidity, kernel-checked) into DecoderFacts:
 * `oddb_iff` : DW6.oddb p r = true <-> dot (lq p) (lq r) = 1   (the one-line bridge)
 * `hyp_of_decoder` : IsDecoder lq W U + |T| = 8  =>  DW6.Hyp W U
 * `rigidCols_of_decoder` : ... => RigidCols W U   (rigid_gram: M = L G L^-1 / 2; a column vanishing on S gives
    rank G_SS <= rank (W_S U_S^T) <= 7)
 * `dyadicRigidity8` : DF.DyadicRigidity8 PROVED (no hypothesis).
 * `D56_8rows_unc` : every 8-row decoder of the live pattern has mass >= 56, no rigidity hypothesis.
Kernel only.
-/
import Nov15.DecoderFacts
import Nov15.DecoderWall6G

open Matrix
set_option maxHeartbeats 0
namespace DFR

theorem oddb_iff (p r : Fin 104) :
    DW6.oddb p r = true ↔ DecoderWall.dot (DF.lq p) (DF.lq r) = 1 := by
  have : DW6.oddb p r = DW4.dotb (DW4.lab p.val) (DW4.lab r.val) := rfl
  rw [this, DF.dotb_iff]
  rfl

theorem hyp_of_decoder {T : Type} [Fintype T] [DecidableEq T] (W U : Fin 104 → T → ℚ)
    (hd : DecoderWall.IsDecoder DF.lq W U) (h8 : Fintype.card T = 8) : DW6.Hyp W U where
  card := h8
  diag := fun p => hd.diag p
  odd := fun p q hpq ho => hd.odd p q hpq ((oddb_iff p q).1 ho)

/-- A product `A Bᵀ` on `S` whose `k`-th column term vanishes has rank <= 7 (|T| = 8). -/
theorem rank_le_seven {T : Type} [Fintype T] [DecidableEq T] (h8 : Fintype.card T = 8)
    (S : Finset (Fin 104)) (A B : Fin 104 → T → ℚ) (k : T)
    (hk : ∀ p ∈ S, ∀ r ∈ S, A p k * B r k = 0) :
    (Matrix.of fun p r : S => ∑ t, A p t * B r t).rank ≤ 7 := by
  let A' : Matrix S {t // t ≠ k} ℚ := Matrix.of fun p t => A p t.1
  let B' : Matrix S {t // t ≠ k} ℚ := Matrix.of fun p t => B p t.1
  have e : (Matrix.of fun p r : S => ∑ t, A p t * B r t) = A' * B'ᵀ := by
    ext p r
    simp only [Matrix.of_apply, Matrix.mul_apply, Matrix.transpose_apply, A', B']
    rw [← Finset.sum_erase Finset.univ (f := fun t => A p.1 t * B r.1 t) (hk p.1 p.2 r.1 r.2),
      Finset.sum_subtype (Finset.univ.erase k) (p := fun t => t ≠ k) (by intro x; simp)]
  have hc : Fintype.card {t // t ≠ k} = 7 := by
    rw [Fintype.card_subtype_compl, Fintype.card_subtype_eq, h8]
  rw [e]
  exact (Matrix.rank_mul_le_left _ _).trans ((Matrix.rank_le_card_width A').trans hc.le)

theorem rank_blk_le_of_rigid {T : Type} [Fintype T] [DecidableEq T] (W U : Fin 104 → T → ℚ)
    (h : DW6.Hyp W U) (S : Finset (Fin 104)) (A B : Fin 104 → T → ℚ)
    (hAB : ∀ p r, DW6.Mx W U p r = ∑ t, A p t * B r t) (k : T)
    (hk : ∀ p ∈ S, ∀ r ∈ S, A p k * B r k = 0) : (DW4.blk S).rank ≤ 7 := by
  obtain ⟨lam, hl, hM⟩ := DW6.rigid_gram h
  let N : Matrix S S ℚ := Matrix.of fun p r : S => ∑ t, A p t * B r t
  have e : DW4.blk S = Matrix.diagonal (fun p : S => 2 / lam p.1) * N * Matrix.diagonal (fun r : S => lam r.1) := by
    ext p r
    have hm := hM p.1 r.1
    rw [hAB] at hm
    simp only [DW4.blk, DW4.Gq, Matrix.submatrix_apply, Matrix.of_apply, N, Matrix.mul_apply,
      Matrix.diagonal_apply, mul_ite, ite_mul, mul_zero, zero_mul, Finset.sum_ite_eq, Finset.mem_univ, if_true,
      Finset.sum_ite_eq']
    have h1 := hl p.1
    have h2 := hl r.1
    rw [hm]
    field_simp
  have := rank_le_seven h.card S A B k hk
  rw [e]
  exact ((Matrix.rank_mul_le_left _ _).trans (Matrix.rank_mul_le_right _ _)).trans this

theorem rigidCols_of_decoder {T : Type} [Fintype T] [DecidableEq T] (W U : Fin 104 → T → ℚ)
    (hd : DecoderWall.IsDecoder DF.lq W U) (h8 : Fintype.card T = 8) : DF.RigidCols W U := by
  have h := hyp_of_decoder W U hd h8
  intro k
  constructor
  · intro S hS
    refine rank_blk_le_of_rigid W U h S W U (fun p r => rfl) k ?_
    intro p hp r hr
    have : W p k = 0 := by
      by_contra hne
      exact hS p hp (by simp [DecoderWall.dep, hne])
    simp [this]
  · intro S hS
    refine rank_blk_le_of_rigid W U h S W U (fun p r => rfl) k ?_
    intro p hp r hr
    have : U r k = 0 := by
      by_contra hne
      exact hS r hr (by simp [DecoderWall.gat, hne])
    simp [this]

/-- DF.DyadicRigidity8 is a theorem. -/
theorem dyadicRigidity8 : DF.DyadicRigidity8 := by
  intro T _ W U hd h8
  classical
  exact rigidCols_of_decoder W U hd h8

theorem rank8spans_of_decoder {T : Type} [Fintype T] (W U : Fin 104 → T → ℚ)
    (hd : DecoderWall.IsDecoder DF.lq W U) (h8 : Fintype.card T = 8) : DecoderWall.Rank8Spans DF.lq W U := by
  classical
  exact DF.rank8spans_of_rigid W U (rigidCols_of_decoder W U hd h8)

/-- **Every 8-row decoder of the live P104 pattern has mass >= 56.  No rigidity hypothesis.** -/
theorem D56_8rows_unc {T : Type} [Fintype T] (W U : Fin 104 → T → ℚ)
    (hd : DecoderWall.IsDecoder DF.lq W U) (h8 : Fintype.card T = 8) : 56 ≤ DecoderWall.mass DF.lq W U :=
  DF.D56_8rows dyadicRigidity8 W U hd h8

theorem rank8_floor_unc {T : Type} [Fintype T] (W U : Fin 104 → T → ℚ)
    (hd : DecoderWall.IsDecoder DF.lq W U) (h8 : Fintype.card T = 8) : 56 ≤ DecoderWall.mass DF.lq W U :=
  D56_8rows_unc W U hd h8

/-- Pure networks with <= 8 rows (NetToDec8), unconditionally on rigidity. -/
theorem D56_pure_le8_unc (Net : ℕ → Prop) (hN : DF.NetToDec8 Net) : ∀ n, Net n → 56 ≤ n :=
  DF.D56_pure_le8 Net hN dyadicRigidity8

end DFR

#print axioms DFR.dyadicRigidity8
#print axioms DFR.D56_8rows_unc
#print axioms DFR.D56_pure_le8_unc
