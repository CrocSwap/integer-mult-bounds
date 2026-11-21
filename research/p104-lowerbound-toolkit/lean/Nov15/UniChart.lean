/-
UniChart (lane UNI-L0L1, stage L0 CHARTBRIDGE, Nov 19).  cards/WILD/UNIMODEL/ARCH.md.
ONE chart type and ONE lattice distance for the word model (charts = Finset ℕ labels, WordModelDefs) and the banked
model (charts = Submodule (ZMod 2) (Fin 9 → ZMod 2), BankFitA.BankedGraph).
* `Uni.Chart` := Submodule (ZMod 2) V9;  `Uni.latD` := WordModel.latD on it;  BankPrem.latD = Uni.latD (rfl).
* `chartOf U` (labels of U's vectors) and `toSub c` (WordModelSpec) are inverse on subspace charts:
  `chartEquiv : {c // IsSubsp c} ≃o Chart` (order isomorphism; ⊆ ↔ ≤).
* dim = finrank through the bridge (`dim_chartOf`, WordModelSpec.dim_eq_finrank), mvPrice = BankNC0.dh of finranks.
* `specPrice_dim'`: |Δdim| ≤ specPrice re-derived THROUGH the bridge (BankPrem.dh_le_latD + dim = finrank);
  `specPrice_eq_mvPrice`: on nested subspace charts the SPEC price IS the native |Δdim| (pricekit rule).
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Nov15.WordModelSpec
import Nov15.BankPrem

set_option linter.unusedSectionVars false

namespace Uni

open Finset Module WordModel

/-- THE chart type: subspaces of F₂⁹. -/
abbrev Chart := Submodule (ZMod 2) V9

/-- THE lattice distance: dim U + dim W − 2 dim (U ⊓ W) = rank(M_W − M_U) (SPEC "Preimage frames"). -/
noncomputable def latD (U W : Chart) : ℝ := WordModel.latD U W

theorem latD_eq_bankPrem (U W : Chart) : BankPrem.latD U W = latD U W := rfl
theorem latD_eq_word (U W : Chart) : WordModel.latD U W = latD U W := rfl
theorem specPrice_eq (a b : Ch) : specPrice a b = latD (toSub a) (toSub b) := rfl

/-! ## Labels ↔ vectors -/

theorem card_V9 : Fintype.card V9 = 512 := by
  simp [V9, Fintype.card_fun, ZMod.card]

/-- every vector of F₂⁹ is the bit vector of a label < 512. -/
theorem vec_surj (v : V9) : ∃ n < 512, vec n = v := by
  classical
  have hinj : Set.InjOn vec (↑(range 512) : Set ℕ) := fun a ha b hb h =>
    vec_inj (mem_range.1 ha) (mem_range.1 hb) h
  have hc : ((range 512).image vec).card = Fintype.card V9 := by
    rw [card_image_of_injOn hinj, card_range, card_V9]
  have hu := (Finset.eq_univ_of_card _ hc)
  have : v ∈ (range 512).image vec := by rw [hu]; exact mem_univ v
  obtain ⟨n, hn, rfl⟩ := mem_image.1 this
  exact ⟨n, mem_range.1 hn, rfl⟩

theorem xor_lt_512 {a b : ℕ} (ha : a < 512) (hb : b < 512) : a ^^^ b < 512 := by
  have := Nat.xor_lt_two_pow (n := 9) (by simpa using ha) (by simpa using hb)
  simpa using this

/-- the label chart of a subspace. -/
noncomputable def chartOf (U : Chart) : Ch := by
  classical exact (range 512).filter (fun n => vec n ∈ U)

theorem mem_chartOf {U : Chart} {n : ℕ} : n ∈ chartOf U ↔ n < 512 ∧ vec n ∈ U := by
  classical
  unfold chartOf; simp [mem_filter, mem_range]

theorem chartOf_subsp (U : Chart) : IsSubsp (chartOf U) := by
  refine ⟨mem_chartOf.2 ⟨by norm_num, by rw [vec_zero]; exact U.zero_mem⟩,
    fun a ha => (mem_chartOf.1 ha).1, fun a ha b hb => ?_⟩
  obtain ⟨ha1, ha2⟩ := mem_chartOf.1 ha
  obtain ⟨hb1, hb2⟩ := mem_chartOf.1 hb
  exact mem_chartOf.2 ⟨xor_lt_512 ha1 hb1, by rw [vec_xor]; exact U.add_mem ha2 hb2⟩

theorem toSub_chartOf (U : Chart) : toSub (chartOf U) = U := by
  rw [toSub_eq _ (chartOf_subsp U)]
  ext v
  change v ∈ vec '' (↑(chartOf U) : Set ℕ) ↔ v ∈ U
  constructor
  · rintro ⟨n, hn, rfl⟩; exact (mem_chartOf.1 hn).2
  · intro hv
    obtain ⟨n, hn, rfl⟩ := vec_surj v
    exact ⟨n, mem_chartOf.2 ⟨hn, hv⟩, rfl⟩

theorem mem_toSub {c : Ch} (hc : IsSubsp c) {n : ℕ} (hn : n < 512) : vec n ∈ toSub c ↔ n ∈ c := by
  rw [toSub_eq c hc]
  change vec n ∈ vec '' (↑c : Set ℕ) ↔ n ∈ c
  constructor
  · rintro ⟨m, hm, he⟩
    rwa [← vec_inj (hc.2.1 m hm) hn he]
  · intro h; exact ⟨n, h, rfl⟩

theorem chartOf_toSub {c : Ch} (hc : IsSubsp c) : chartOf (toSub c) = c := by
  ext n
  rw [mem_chartOf]
  constructor
  · rintro ⟨hn, hv⟩; exact (mem_toSub hc hn).1 hv
  · intro h; have hn := hc.2.1 n h; exact ⟨hn, (mem_toSub hc hn).2 h⟩

theorem toSub_le_iff {a b : Ch} (ha : IsSubsp a) (hb : IsSubsp b) : toSub a ≤ toSub b ↔ a ⊆ b := by
  constructor
  · intro h n hn
    have hn5 := ha.2.1 n hn
    exact (mem_toSub hb hn5).1 (h ((mem_toSub ha hn5).2 hn))
  · intro h
    rw [toSub_eq a ha, toSub_eq b hb]
    rintro _ ⟨x, hx, rfl⟩; exact ⟨x, h hx, rfl⟩

theorem toSub_inj {a b : Ch} (ha : IsSubsp a) (hb : IsSubsp b) (h : toSub a = toSub b) : a = b := by
  rw [← chartOf_toSub ha, ← chartOf_toSub hb, h]

/-- **CHARTBRIDGE**: subspace label charts ≃o subspaces of F₂⁹ (inclusion ↔ ≤). -/
noncomputable def chartEquiv : {c : Ch // IsSubsp c} ≃o Chart where
  toFun c := toSub c.1
  invFun U := ⟨chartOf U, chartOf_subsp U⟩
  left_inv c := Subtype.ext (chartOf_toSub c.2)
  right_inv U := toSub_chartOf U
  map_rel_iff' := by
    intro a b
    change toSub a.1 ≤ toSub b.1 ↔ a.1 ⊆ b.1
    exact toSub_le_iff a.2 b.2

/-! ## dim = finrank, one price -/

theorem dim_chartOf (U : Chart) : dim (chartOf U) = finrank (ZMod 2) U := by
  rw [dim_eq_finrank _ (chartOf_subsp U), toSub_chartOf]

theorem natAbs_sub_comm' (x y : ℤ) : (x - y).natAbs = (y - x).natAbs := by
  rw [← Int.natAbs_neg, neg_sub]

/-- the native price |Δdim| IS BankNC0.dh of the finranks (bankPrice's base) on subspace charts. -/
theorem mvPrice_eq_dh {a b : Ch} (ha : IsSubsp a) (hb : IsSubsp b) :
    mvPrice a b = BankNC0.dh (finrank (ZMod 2) (toSub a)) (finrank (ZMod 2) (toSub b)) := by
  unfold mvPrice BankNC0.dh
  rw [dim_eq_finrank a ha, dim_eq_finrank b hb, natAbs_sub_comm']

/-- **specPrice_dim re-derived through the bridge**: |Δdim| ≤ specPrice on subspace charts. -/
theorem specPrice_dim' {a b : Ch} (ha : IsSubsp a) (hb : IsSubsp b) :
    |(dim b : ℝ) - dim a| ≤ specPrice a b := by
  have h := BankPrem.dh_le_latD (toSub a) (toSub b)
  rw [latD_eq_bankPrem, ← specPrice_eq, ← mvPrice_eq_dh ha hb] at h
  refine le_trans (le_of_eq ?_) h
  unfold mvPrice
  rw [Nat.cast_natAbs, Int.cast_abs]; push_cast; rfl

/-- on nested subspace charts the SPEC price IS the native |Δdim| (the pricekit / bank.py rule). -/
theorem specPrice_eq_mvPrice {a b : Ch} (ha : IsSubsp a) (hb : IsSubsp b) (h : a ⊆ b ∨ b ⊆ a) :
    specPrice a b = mvPrice a b := by
  rcases h with h | h
  · rw [specPrice_eq, ← latD_eq_bankPrem, BankPrem.latD_eq_dh_of_le ((toSub_le_iff ha hb).2 h),
      mvPrice_eq_dh ha hb]
  · rw [specPrice_eq, ← latD_eq_bankPrem]
    have e : BankPrem.latD (toSub a) (toSub b) = BankPrem.latD (toSub b) (toSub a) := by
      unfold BankPrem.latD; rw [inf_comm]; ring
    rw [e, BankPrem.latD_eq_dh_of_le ((toSub_le_iff hb ha).2 h), mvPrice_eq_dh ha hb]
    unfold BankNC0.dh; rw [natAbs_sub_comm']

end Uni

#print axioms Uni.chartEquiv
#print axioms Uni.dim_chartOf
#print axioms Uni.specPrice_dim'
#print axioms Uni.specPrice_eq_mvPrice
