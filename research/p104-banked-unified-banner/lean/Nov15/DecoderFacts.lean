/-
DecoderFacts .  
Decoder facts for P104 labels (DW4.lab, 104 ports, F2^9).  Kernel only; named hypotheses, never axioms.
 * `lq p`, bridge dotb <-> DecoderWall.dot, `codeOf` (vector <-> code < 512).
 * `RigidSet D` : the ports outside D have real Gram rank <= 7  (consequence of DYADICPORTS rigidity:
   a rank-8 fit is D1 G D2, so a column vanishing on S forces rank G_SS <= 7).
 * `row_span_ge_eight` : RigidSet D  +  DW4.codim2_rank (kernel-checked flats)  =>  dim span labels(D) >= 8.
 * `rank8spans_of_rigid` : RigidCols W U  =>  DecoderWall.Rank8Spans lq W U.
 * `D56_decoder_8rows` : IsDecoder lq W U, |T| = 8, RigidCols  =>  mass >= 56   (via DecoderWall.rank8_floor).
Named hypotheses: `DyadicRigidity8` (DEC6 target), `Wall56` (the open >= 9 rows wall).
-/
import Nov15.DecoderWall4
import Nov15.DecoderWall2
import Mathlib.LinearAlgebra.Dimension.Finrank

open DecoderWall Matrix
set_option maxHeartbeats 0
namespace DF

def vecOf (a : ℕ) : Fin 9 → ZMod 2 := fun i => if a.testBit i then 1 else 0
def lq (p : Fin 104) : Fin 9 → ZMod 2 := vecOf (DW4.lab p)
def codeOf (v : Fin 9 → ZMod 2) : ℕ := ∑ i : Fin 9, (v i).val * 2 ^ (i : ℕ)

theorem vecOf_codeOf : ∀ v : Fin 9 → ZMod 2, vecOf (codeOf v) = v := by decide +kernel
theorem codeOf_lt : ∀ v : Fin 9 → ZMod 2, codeOf v < 512 := by decide +kernel

theorem lf_card (p : ℕ → Bool) : ∀ n, ((List.range n).filter p).length = ((Finset.range n).filter (fun k => p k = true)).card := by
  intro n
  induction n with
  | zero => simp
  | succ n ih =>
    rw [List.range_succ, List.filter_append, List.length_append, ih, Finset.range_add_one, Finset.filter_insert]
    by_cases h : p n = true
    · simp [h, Finset.card_insert_of_notMem]
    · simp [h]

theorem dot_comm' (x y : Fin 9 → ZMod 2) : DecoderWall.dot x y = DecoderWall.dot y x := dotProduct_comm _ _

theorem dot_vecOf (a b : ℕ) : DecoderWall.dot (vecOf a) (vecOf b) =
    (((Finset.range 9).filter fun k => a.testBit k && b.testBit k).card : ZMod 2) := by
  unfold DecoderWall.dot vecOf
  rw [dotProduct, Fin.sum_univ_eq_sum_range
    (fun i => (if a.testBit i then (1:ZMod 2) else 0) * (if b.testBit i then 1 else 0)) 9]
  rw [Finset.card_filter]; push_cast
  refine Finset.sum_congr rfl fun k _ => ?_
  by_cases ha : a.testBit k <;> by_cases hb : b.testBit k <;> simp [ha, hb]

theorem dotb_iff (a b : ℕ) : DW4.dotb a b = true ↔ DecoderWall.dot (vecOf a) (vecOf b) = 1 := by
  rw [dot_vecOf]
  have e := lf_card (fun k => a.testBit k && b.testBit k) 9
  unfold DW4.dotb
  rw [e, ZMod.natCast_eq_one_iff_odd, Nat.odd_iff]
  simp

/-- `S`-ports all vanish: the real Gram rank of `S` is at most 7 (rigid-row consequence). -/
def RigidSet (D : Finset (Fin 104)) : Prop :=
  ∀ S : Finset (Fin 104), (∀ p ∈ S, p ∉ D) → (DW4.blk S).rank ≤ 7

theorem exists_pair_ann (D : Finset (Fin 104)) (hlt : Module.finrank (ZMod 2)
      (Submodule.span (ZMod 2) (Set.range fun t : D => lq t)) < 8) :
    ∃ a b : Fin 9 → ZMod 2, a ≠ 0 ∧ b ≠ 0 ∧ a ≠ b ∧
      (∀ p ∈ D, DecoderWall.dot a (lq p) = 0 ∧ DecoderWall.dot b (lq p) = 0) := by
  have h1 := finrank_annS_add (fun t : D => lq t)
  have h2 : 1 < Module.finrank (ZMod 2) (annS (fun t : D => lq t)) := by
    have : Fintype.card (Fin 9) = 9 := by simp
    omega
  obtain ⟨x, hx0⟩ := Module.finrank_pos_iff_exists_ne_zero.1 (by omega : 0 < Module.finrank (ZMod 2) (annS (fun t : D => lq t)))
  obtain ⟨y, hxy⟩ := exists_linearIndependent_pair_of_one_lt_finrank h2 hx0
  have hy0 : y ≠ 0 := by
    intro e
    have := LinearIndependent.pair_iff.1 hxy 0 1 (by simp [e])
    simp at this
  have hne : x ≠ y := by
    intro e
    have h2 : (2 : ZMod 2) = 0 := by decide
    have := LinearIndependent.pair_iff.1 hxy 1 1 (by rw [one_smul, one_smul, e, ← two_smul (ZMod 2), h2, zero_smul])
    exact absurd this.1 (by decide)
  refine ⟨x.1, y.1, fun e => hx0 (Subtype.ext e), fun e => hy0 (Subtype.ext e),
    fun e => hne (Subtype.ext e), fun p hp => ⟨?_, ?_⟩⟩
  · have := x.2
    simp only [annS, LinearMap.mem_ker] at this
    have := congrFun this ⟨p, hp⟩
    rwa [Phi_apply] at this
  · have := y.2
    simp only [annS, LinearMap.mem_ker] at this
    have := congrFun this ⟨p, hp⟩
    rwa [Phi_apply] at this

/-- The kernel-checked flats (DW4) turn rigidity into a span bound: `D` rigid => labels of `D` span >= 8. -/
theorem row_span_ge_eight (D : Finset (Fin 104)) (hr : RigidSet D) :
    8 ≤ Module.finrank (ZMod 2) (Submodule.span (ZMod 2) (Set.range fun t : D => lq t)) := by
  by_contra hlt
  simp only [not_le] at hlt
  obtain ⟨a, b, ha, hb, hab, hD⟩ := exists_pair_ann D hlt
  have hca : codeOf a ≠ 0 := by
    intro e; apply ha; have := vecOf_codeOf a; rw [e] at this; rw [← this]; funext i; simp [vecOf]
  have hcb : codeOf b ≠ 0 := by
    intro e; apply hb; have := vecOf_codeOf b; rw [e] at this; rw [← this]; funext i; simp [vecOf]
  have hcab : codeOf a ≠ codeOf b := by
    intro e; apply hab; rw [← vecOf_codeOf a, ← vecOf_codeOf b, e]
  have key := DW4.codim2_rank (codeOf a) (codeOf b) (codeOf_lt a) (codeOf_lt b) hca hcb hcab
  have hsub : DW4.out2 (codeOf a) (codeOf b) ⊆ (Finset.univ.filter fun p => p ∉ D) := by
    intro p hp
    simp only [DW4.out2, Finset.mem_filter, Finset.mem_univ, true_and] at hp ⊢
    intro hpD
    obtain ⟨h1, h2⟩ := hD p hpD
    rcases Bool.or_eq_true_iff.1 hp with h | h
    · have this := (dotb_iff _ _).1 h
      rw [vecOf_codeOf a] at this
      have h1' : DecoderWall.dot (vecOf (DW4.lab p)) a = 0 := by rw [dot_comm']; exact h1
      rw [h1'] at this; exact absurd this (by decide)
    · have this := (dotb_iff _ _).1 h
      rw [vecOf_codeOf b] at this
      have h2' : DecoderWall.dot (vecOf (DW4.lab p)) b = 0 := by rw [dot_comm']; exact h2
      rw [h2'] at this; exact absurd this (by decide)
  have h8 := key
  have hmono : (DW4.blk (DW4.out2 (codeOf a) (codeOf b))).rank ≤ (DW4.blk (Finset.univ.filter fun p => p ∉ D)).rank :=
    DW4.rank_blk_mono hsub
  have := hr (Finset.univ.filter fun p => p ∉ D) (by intro p hp; simpa using hp)
  omega

/-! ### Rigid rows -> Rank8Spans -> floor 56 -/

/-- Rigid-row hypothesis for ONE decoder: every row's deposit/gather support is a rigid set.  Consequence of
`DyadicRigidity8` for 8-row decoders (columns of W, U lie in the 8-dim column space D1 A of the rank-8 fit,
so a column vanishing on S has real Gram rank <= 7 on S).  False for a zero row (reduced decoders only). -/
def RigidCols {T : Type} [Fintype T] (W U : Fin 104 → T → ℚ) : Prop :=
  ∀ k, RigidSet (dep W k) ∧ RigidSet (gat U k)

theorem rank8spans_of_rigid {T : Type} [Fintype T] (W U : Fin 104 → T → ℚ) (hr : RigidCols W U) :
    Rank8Spans lq W U :=
  fun k => ⟨row_span_ge_eight _ (hr k).1, row_span_ge_eight _ (hr k).2⟩

def clique8 : Fin 8 → Fin 104 := ![0, 6, 16, 22, 29, 36, 45, 95]

theorem clique8_inj : Function.Injective clique8 := by decide

theorem clique8_odd : ∀ i j, i ≠ j → DecoderWall.dot (lq (clique8 i)) (lq (clique8 j)) = 1 := by
  have : ∀ i j : Fin 8, i ≠ j → DW4.dotb (DW4.lab (clique8 i)) (DW4.lab (clique8 j)) = true := by
    decide +kernel
  intro i j hij
  exact (dotb_iff _ _).1 (this i j hij)

/-- **D56 for decoders (kernel-checked given rigid rows).**  Any rational decoder of P104's live pattern whose
rows are rigid has mass >= 56.  Uses DW4 flats (kernel) + DecoderWall.rank8_floor. -/
theorem D56_decoder {T : Type} [Fintype T] (W U : Fin 104 → T → ℚ) (hd : IsDecoder lq W U)
    (hr : RigidCols W U) : 56 ≤ mass lq W U :=
  rank8_floor lq W U hd (by simp) (rank8spans_of_rigid W U hr) clique8 clique8_inj clique8_odd

theorem decoder_rows_ge_eight {T : Type} [Fintype T] (W U : Fin 104 → T → ℚ) (hd : IsDecoder lq W U) :
    8 ≤ Fintype.card T :=
  rows_ge_eight lq W U hd clique8 clique8_inj clique8_odd

/-- NAMED HYPOTHESIS (DYADICPORTS rigidity; DEC6 target): every 8-row decoder of the live pattern has rigid
rows.  Numerical only today (DEC5/DEC6). -/
def DyadicRigidity8 : Prop :=
  ∀ (T : Type) [Fintype T] (W U : Fin 104 → T → ℚ), IsDecoder lq W U → Fintype.card T = 8 → RigidCols W U

/-- NAMED HYPOTHESIS (the open wall, >= 9 rows): every decoder has mass >= 56. -/
def Wall56 : Prop :=
  ∀ (T : Type) [Fintype T] (W U : Fin 104 → T → ℚ), IsDecoder lq W U → 56 ≤ mass lq W U

theorem D56_8rows (hR : DyadicRigidity8) {T : Type} [Fintype T] (W U : Fin 104 → T → ℚ)
    (hd : IsDecoder lq W U) (h8 : Fintype.card T = 8) : 56 ≤ mass lq W U :=
  D56_decoder W U hd (hR T W U hd h8)

/-! ### D56-pure and the hosted dual (network level, abstract) -/

/-- `Net n` : some pure-descent network realising P104's live pattern has descent mass `n`.
NAMED HYPOTHESIS `NetToDec8` (UC5 sec 1 normal form + stage law, paper): a network with <= 8 depositing
descents gives an 8-row decoder of mass <= its descent mass (pads/drops nothing: >= 8 rows are forced). -/
def NetToDec8 (Net : ℕ → Prop) : Prop :=
  ∀ n, Net n → ∃ (T : Type) (_ : Fintype T) (W U : Fin 104 → T → ℚ),
    IsDecoder lq W U ∧ Fintype.card T = 8 ∧ mass lq W U ≤ n

def NetToDec (Net : ℕ → Prop) : Prop :=
  ∀ n, Net n → ∃ (T : Type) (_ : Fintype T) (W U : Fin 104 → T → ℚ), IsDecoder lq W U ∧ mass lq W U ≤ n

/-- D56-pure, <= 8 rows: modulo `NetToDec8` and `DyadicRigidity8` only. -/
theorem D56_pure_le8 (Net : ℕ → Prop) (hN : NetToDec8 Net) (hR : DyadicRigidity8) :
    ∀ n, Net n → 56 ≤ n := by
  intro n hn
  obtain ⟨T, _, W, U, hd, h8, hm⟩ := hN n hn
  exact (D56_8rows hR W U hd h8).trans hm

/-- D56-pure, any rows: modulo `NetToDec` and the wall `Wall56`. -/
theorem D56_pure_wall (Net : ℕ → Prop) (hN : NetToDec Net) (hW : Wall56) : ∀ n, Net n → 56 ≤ n := by
  intro n hn
  obtain ⟨T, _, W, U, hd, hm⟩ := hN n hn
  exact (hW T W U hd).trans hm

/-- Hosted dual: `f ↦ f^⊥` sends hosted gathers/deposits to live ones and rises to descents of equal rank
(UC3 sec 1).  NAMED HYPOTHESIS `HostDual`.  Then every ceiling for live descents is one for hosted rises. -/
def HostDual (Net NetH : ℕ → Prop) : Prop := ∀ n, NetH n → Net n

theorem D56_hosted (Net NetH : ℕ → Prop) (hD : HostDual Net NetH) (h : ∀ n, Net n → 56 ≤ n) :
    ∀ n, NetH n → 56 ≤ n := fun n hn => h n (hD n hn)

end DF

#print axioms DF.row_span_ge_eight
#print axioms DF.D56_decoder
#print axioms DF.D56_pure_le8
#print axioms DF.clique8_odd
