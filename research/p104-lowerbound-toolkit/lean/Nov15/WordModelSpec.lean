/-
WARNING (WM-AUDIT item 7): `FWword` charges stops twice (full paths AND −nStops·cstop), so it is NOT the word's
real invoice; P0_word/U0_word/P0_spec/U0_spec say nothing about the real κ. Use WordModelInvoice.P0_real /
U0_real (FWreal = real invoice, proved ≤ endpoint-collapsed invoice by the stop-excess lemma).
WordModelSpec (lane WORDMODEL, coordinator, Nov 18).  The SPEC price instantiated: charts ↦ subspaces of F2^9
(label n ↦ its bit vector), price = Lagrangian/lattice distance  d(U,V) = dim U + dim V − 2 dim(U ∩ V)
(SPEC general-clifford-frames "Preimage frames" lemma, LEANSWARM/RRHO.md: Fourier rank of the transition).
Proved here: d is a pseudometric (PriceMetric), integer-valued, ≥ |Δdim| on subspace charts (dim = log2 |frame|
= finrank), and ≥ 1 on a strictly nested pair of subspace charts.  Hence P0 / U0 hold for every model word priced
by the SPEC price, with clause `FramesSubsp` (every frame is a span, independent.py l.26-31) and, for U0,
`OwnedNested` (l.51 owned clause).  Only hF (κ a crossing of the word's invoice) is left.
Kernel only: no sorry, no native_decide, no axioms.
-/
import Nov15.WordModelPrice
import Mathlib.FieldTheory.Finiteness
import Mathlib.Data.ZMod.Basic
import Mathlib.Algebra.Field.ZMod

set_option linter.unusedSectionVars false

namespace WordModel

open Finset SafeRungsClique SafeRungsPrice Module

/-! ## Lattice distance on submodules -/

section Lat
variable {K E : Type*} [Field K] [AddCommGroup E] [Module K E] [FiniteDimensional K E]

noncomputable def latD (U V : Submodule K E) : ℝ :=
  (finrank K U : ℝ) + finrank K V - 2 * finrank K (U ⊓ V : Submodule K E)

theorem latD_metric : PriceMetric (latD (K := K) (E := E)) where
  nonneg := by
    intro U V
    have h1 := Submodule.finrank_mono (inf_le_left : U ⊓ V ≤ U)
    have h2 := Submodule.finrank_mono (inf_le_right : U ⊓ V ≤ V)
    have h1' : (finrank K (U ⊓ V : Submodule K E) : ℝ) ≤ finrank K U := by exact_mod_cast h1
    have h2' : (finrank K (U ⊓ V : Submodule K E) : ℝ) ≤ finrank K V := by exact_mod_cast h2
    unfold latD; linarith
  refl := by intro U; unfold latD; rw [inf_idem]; ring
  tri := by
    intro U V W
    have hs := Submodule.finrank_sup_add_finrank_inf_eq (U ⊓ V) (V ⊓ W)
    have h1 : finrank K ((U ⊓ V) ⊔ (V ⊓ W) : Submodule K E) ≤ finrank K V :=
      Submodule.finrank_mono (sup_le inf_le_right inf_le_left)
    have h2 : finrank K ((U ⊓ V) ⊓ (V ⊓ W) : Submodule K E) ≤ finrank K (U ⊓ W : Submodule K E) :=
      Submodule.finrank_mono (le_inf (inf_le_left.trans inf_le_left) (inf_le_right.trans inf_le_right))
    have : (finrank K (U ⊓ V : Submodule K E) : ℝ) + finrank K (V ⊓ W : Submodule K E) ≤
        finrank K V + finrank K (U ⊓ W : Submodule K E) := by exact_mod_cast (by omega)
    unfold latD; linarith

theorem latD_nat (U V : Submodule K E) : ∃ n : ℕ, latD U V = n := by
  have h1 := Submodule.finrank_mono (inf_le_left : U ⊓ V ≤ U)
  have h2 := Submodule.finrank_mono (inf_le_right : U ⊓ V ≤ V)
  refine ⟨finrank K U + finrank K V - 2 * finrank K (U ⊓ V : Submodule K E), ?_⟩
  unfold latD; push_cast [show 2 * finrank K (U ⊓ V : Submodule K E) ≤ finrank K U + finrank K V by omega]
  ring

theorem latD_ge_abs (U V : Submodule K E) :
    |(finrank K V : ℝ) - finrank K U| ≤ latD U V := by
  have h1 := Submodule.finrank_mono (inf_le_left : U ⊓ V ≤ U)
  have h2 := Submodule.finrank_mono (inf_le_right : U ⊓ V ≤ V)
  have h1' : (finrank K (U ⊓ V : Submodule K E) : ℝ) ≤ finrank K U := by exact_mod_cast h1
  have h2' : (finrank K (U ⊓ V : Submodule K E) : ℝ) ≤ finrank K V := by exact_mod_cast h2
  unfold latD; rw [abs_le]; constructor <;> linarith

theorem latD_lt {U V : Submodule K E} (h : U < V) : 1 ≤ latD U V := by
  have hl := Submodule.finrank_lt_finrank_of_lt h
  have hi : U ⊓ V = U := inf_eq_left.2 h.le
  unfold latD; rw [hi]
  have : (finrank K U : ℝ) + 1 ≤ finrank K V := by exact_mod_cast hl
  linarith

theorem latD_symm (U V : Submodule K E) : latD U V = latD V U := by
  unfold latD; rw [inf_comm]; ring

end Lat

/-! ## Charts as subspaces of F2^9 -/

abbrev V9 := Fin 9 → ZMod 2

/-- the bit vector of label n. -/
def vec (n : ℕ) : V9 := fun i => if n.testBit i then 1 else 0

theorem vec_xor (a b : ℕ) : vec (a ^^^ b) = vec a + vec b := by
  funext i
  simp only [vec, Nat.testBit_xor, Pi.add_apply]
  cases a.testBit i <;> cases b.testBit i <;> decide

theorem vec_zero : vec 0 = 0 := by funext i; simp [vec]

theorem vec_inj {a b : ℕ} (ha : a < 512) (hb : b < 512) (h : vec a = vec b) : a = b := by
  apply Nat.eq_of_testBit_eq
  intro i
  by_cases hi : i < 9
  · have := congrFun h ⟨i, hi⟩
    simp only [vec] at this
    cases ha' : a.testBit i <;> cases hb' : b.testBit i <;> simp_all
  · have h9 : (512 : ℕ) ≤ 2 ^ i := by
      calc (512 : ℕ) = 2 ^ 9 := by norm_num
        _ ≤ 2 ^ i := Nat.pow_le_pow_right (by norm_num) (by omega)
    rw [Nat.testBit_lt_two_pow (lt_of_lt_of_le ha h9), Nat.testBit_lt_two_pow (lt_of_lt_of_le hb h9)]

/-- span of a chart's label vectors. -/
noncomputable def toSub (c : Ch) : Submodule (ZMod 2) V9 := Submodule.span (ZMod 2) (vec '' ↑c)

/-- a subspace chart IS a submodule (no span needed). -/
def subOf (c : Ch) (hc : IsSubsp c) : Submodule (ZMod 2) V9 where
  carrier := vec '' ↑c
  add_mem' := by
    rintro _ _ ⟨a, ha, rfl⟩ ⟨b, hb, rfl⟩
    exact ⟨a ^^^ b, hc.2.2 a ha b hb, vec_xor a b⟩
  zero_mem' := ⟨0, hc.1, vec_zero⟩
  smul_mem' := by
    rintro r _ ⟨a, ha, rfl⟩
    have hr : r = 0 ∨ r = 1 := by
      fin_cases r
      · exact Or.inl rfl
      · exact Or.inr rfl
    rcases hr with rfl | rfl
    · exact ⟨0, hc.1, by rw [vec_zero, zero_smul]⟩
    · exact ⟨a, ha, by rw [one_smul]⟩

theorem toSub_eq (c : Ch) (hc : IsSubsp c) : toSub c = subOf c hc := by
  unfold toSub
  have : vec '' (↑c : Set ℕ) = ((subOf c hc : Submodule (ZMod 2) V9) : Set V9) := rfl
  rw [this, Submodule.span_eq]

/-- dim (log2 |frame|) = finrank of the span, for subspace charts. -/
theorem dim_eq_finrank (c : Ch) (hc : IsSubsp c) : dim c = finrank (ZMod 2) (toSub c) := by
  classical
  have hinj : Set.InjOn vec (↑c : Set ℕ) := fun a ha b hb h => vec_inj (hc.2.1 a ha) (hc.2.1 b hb) h
  have hcard : Nat.card (toSub c) = c.card := by
    rw [toSub_eq c hc]
    change Nat.card (vec '' (↑c : Set ℕ)) = c.card
    rw [Nat.card_image_of_injOn hinj, Nat.card_coe_set_eq, Set.ncard_coe_finset]
  have hpow : Nat.card (toSub c) = 2 ^ finrank (ZMod 2) (toSub c) := by
    rw [Nat.card_eq_fintype_card, Module.card_eq_pow_finrank (K := ZMod 2), ZMod.card]
  unfold dim
  rw [← hcard, hpow, Nat.log_pow (by norm_num)]

/-- the SPEC price on charts. -/
noncomputable def specPrice (a b : Ch) : ℝ := latD (toSub a) (toSub b)

theorem specPrice_metric : PriceMetric specPrice where
  nonneg := fun a b => (latD_metric).nonneg _ _
  refl := fun a => (latD_metric).refl _
  tri := fun a b c => (latD_metric).tri _ _ _

theorem specPrice_dim {a b : Ch} (ha : IsSubsp a) (hb : IsSubsp b) :
    |(dim b : ℝ) - dim a| ≤ specPrice a b := by
  rw [dim_eq_finrank a ha, dim_eq_finrank b hb]; exact latD_ge_abs _ _

theorem toSub_lt {a b : Ch} (ha : IsSubsp a) (hb : IsSubsp b) (h : a < b) : toSub a < toSub b := by
  rw [toSub_eq a ha, toSub_eq b hb]
  refine lt_of_le_of_ne ?_ ?_
  · rintro _ ⟨x, hx, rfl⟩; exact ⟨x, h.le hx, rfl⟩
  · intro he
    obtain ⟨x, hxb, hxa⟩ := Finset.exists_of_ssubset h
    have : vec x ∈ (subOf b hb : Set V9) := ⟨x, hxb, rfl⟩
    rw [← he] at this
    obtain ⟨y, hy, hxy⟩ := this
    exact hxa (vec_inj (hb.2.1 x hxb) (ha.2.1 y hy) hxy.symm ▸ hy)

theorem specPrice_nested {a b : Ch} (ha : IsSubsp a) (hb : IsSubsp b) (h : a < b ∨ b < a) :
    1 ≤ specPrice a b := by
  unfold specPrice
  rcases h with h | h
  · exact latD_lt (toSub_lt ha hb h)
  · rw [latD_symm]; exact latD_lt (toSub_lt hb ha h)

/-! ## The rungs under the SPEC price -/

/-- every frame used by the run is a span (independent.py l.26-31): birth charts, current charts,
owned MOVE charts. -/
def FramesSubsp {R : Type} (s : St R) : Prop :=
  (∀ r c, r ∈ s.B c → IsSubsp c) ∧ (∀ r c, s.loc r = .sit c → IsSubsp c) ∧
    ∀ m ∈ s.olog, IsSubsp m.1 ∧ IsSubsp m.2.1

variable {Pt Hl Ow : Type} [Fintype Pt] [Fintype Hl] [Fintype Ow]
  [DecidableEq Pt] [DecidableEq Hl] [DecidableEq Ow]

theorem ends_subsp {cl : Caller Pt} {s : St (Reg Pt Hl Ow)} (hw : Word cl s) (hfr : FramesSubsp s)
    (r : Reg Pt Hl Ow) (hp : pub cl r = true) :
    IsSubsp (path s r 0) ∧ IsSubsp (path s r (plen s r)) := by
  have hs := reach_pinv (pub cl) hw.reach
  obtain ⟨c, hc⟩ := hw.pub_sit r hp
  obtain ⟨c0, h0⟩ := hs.born r c hp hc
  obtain ⟨e0, e1⟩ := path_ends (pub cl) hs h0
  rw [e0]; refine ⟨hfr.1 r c0 h0, hfr.2.1 r _ e1⟩

theorem hH_spec {cl : Caller Pt} {s : St (Reg Pt Hl Ow)} (hw : Word cl s) (hfr : FramesSubsp s) :
    ∀ i ∈ (helpers : Finset (Reg Pt Hl Ow)), hcred s i ≤ specPrice (path s i 0) (path s i (plen s i)) := by
  intro i hi
  obtain ⟨j, -, rfl⟩ := Finset.mem_image.1 hi
  obtain ⟨h0, h1⟩ := ends_subsp hw hfr (Reg.h j) rfl
  exact (le_abs_self _).trans (specPrice_dim h0 h1)

theorem hM_spec {cl : Caller Pt} {s : St (Reg Pt Hl Ow)} (hw : Word cl s) (hfr : FramesSubsp s) :
    ∀ j ∈ mains cl, 1 ≤ plen s j ∧ 8 ≤ specPrice (path s j 0) (path s j (plen s j)) := by
  -- price restricted to the (subspace) endpoints satisfies DimLower there; reuse hM_word with a
  -- modified price that agrees with specPrice on subspace pairs and is |Δdim| elsewhere.
  classical
  let dc : Ch → Ch → ℝ := fun a b => if IsSubsp a ∧ IsSubsp b then specPrice a b else |(dim b : ℝ) - dim a|
  have hdl : DimLower dc := by
    intro a b; simp only [dc]; split_ifs with h
    · exact specPrice_dim h.1 h.2
    · exact le_rfl
  intro j hj
  obtain ⟨h1, h2⟩ := hM_word hw hdl j hj
  refine ⟨h1, ?_⟩
  have hp : pub cl j = true := by
    simp only [mains, Dset, Finset.mem_union, Finset.mem_image, Finset.mem_univ, true_and,
      Finset.mem_filter] at hj
    rcases hj with ((⟨p, rfl⟩ | ⟨p, rfl⟩) | ⟨p, hD, rfl⟩) | ⟨p, hD, rfl⟩ <;> simp [pub, *]
  obtain ⟨e0, e1⟩ := ends_subsp hw hfr j hp
  simpa [dc, e0, e1] using h2

theorem hO1_spec {s : St (Reg Pt Hl Ow)} (hfr : FramesSubsp s) (hn : OwnedNested s) :
    ∀ k < nOwned s, 1 ≤ specPrice (oSrc s k) (oTgt s k) := by
  intro k hk
  have hmem : s.olog.getD k (∅, ∅, 0) ∈ s.olog := by
    rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hk, Option.getD_some]; exact List.getElem_mem hk
  exact specPrice_nested (hfr.2.2 _ hmem).1 (hfr.2.2 _ hmem).2 (hn _ hmem)

/-- **P0 under the SPEC price**: every model word (96 D ports, frames = spans), every crossing κ ∈ (0,1] of
its own invoice priced by d(U,V) = dim U + dim V − 2 dim(U∩V) is < .0227043. -/
theorem P0_spec {cl : Caller Pt} {s : St (Reg Pt Hl Ow)} (hw : Word cl s) (hD : DCount cl)
    (hfr : FramesSubsp s) (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ ≤ 1)
    (hF : 0 ≤ FWword cl s specPrice (1 - κ)) : κ < 227043 / 10000000 :=
  SafeRungsExact.P0_kappa_exact specPrice_metric helpers (hcred s) (plen s) (path s) (mains cl) (plen s)
    (path s) (nOwned s) (oSrc s) (oTgt s) (nStops s) (hH_spec hw hfr) (hM_spec hw hfr) (mains_card cl hD)
    (Nat.cast_nonneg _) κ hκ0 hκ1 hF

/-- **U0 under the SPEC price**: adding owned nesting (l.51), κ < .0204111. -/
theorem U0_spec {cl : Caller Pt} {s : St (Reg Pt Hl Ow)} (hw : Word cl s) (hD : DCount cl)
    (hfr : FramesSubsp s) (hnest : OwnedNested s) (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ ≤ 1)
    (hF : 0 ≤ FWword cl s specPrice (1 - κ)) : κ < 204111 / 10000000 :=
  U0_kappa_word specPrice_metric helpers (hcred s) (plen s) (path s) (mains cl) (plen s) (path s)
    (oSrc s) (oTgt s) (hH_spec hw hfr) (hM_spec hw hfr) (mains_card cl hD) hw (hO1_spec hfr hnest)
    κ hκ0 hκ1 hF

end WordModel

#print axioms WordModel.P0_spec
#print axioms WordModel.U0_spec
