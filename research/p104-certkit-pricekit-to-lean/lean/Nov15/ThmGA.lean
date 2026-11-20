/-
ThmGA (lane LEAN-THMG, Nov 19).  GENDAG Theorem G, pattern-level core (cards/WILD/UCEIL/bankd56/gendag/GD.md).
Kernel only.  Charts are `Submodule (ZMod 2) (Fin 9 → ZMod 2)` (= BankFit chart type).
 * `hullW / OrdW / fold_W`  : W-side FOLD.  Trunks t₁,…,tₙ listed outward from a head chart X with each
     dst tᵢ ≤ (X ⊔ src t₁ ⊔ … ⊔ src tᵢ₋₁) (in-trees, nested trunks, any DAG order) ⟹
     dim (X ⊔ ⨆ src tᵢ) ≤ dim X + Σ (dim src tᵢ − dim dst tᵢ).
 * `hullU / OrdU / fold_U`  : U-side FOLD (transpose).  Tails listed outward from an end chart X with
     (X ⊓ dst t₁ ⊓ … ⊓ dst tᵢ₋₁) ≤ src tᵢ ⟹ dim X ≤ dim (X ⊓ ⨅ dst tᵢ) + Σ drops.
 * `dep_hull_ge_8 / gat_hull_le_1` : an 8-row decoder of the live pattern (DFR.rank8spans_of_decoder): a chart
     containing every deposit label of a row has dim ≥ 8; a chart ⊥ every gather label of a row has dim ≤ 1.
 * `decouple`               : D_r ≥ dim a_r − dim b_r for 8 groups ⟹ Σ D_r + Σ d_T + Σ d_U ≥ 56 + E_W + E_U,
     E_W = Σ d_T − Σ δ_r (δ_r = 8 − dim a_r),  E_U = Σ d_U − Σ δ'_r (δ'_r = dim b_r − 1).
 * `oti_of_comp`, `otiComp_disjoint`, `otiComp_hall` : OTI (Σ δ ≤ Σ d) assembled per component; components with
     pairwise-disjoint FOLD ancestor sets (single head = FOLD; nested in-trees) and Hall components
     (all heads δ ≤ 1, every trunk d ≥ 1, #small heads ≤ #trunks) are discharged; any other component's OTI is the
     named hypothesis `OTIComp`.
-/
import Nov15.ChainRowB

open Module Submodule

namespace ThmG
open DecoderWall ChainRow

abbrev Ch := Submodule (ZMod 2) (Fin 9 → ZMod 2)
noncomputable abbrev dm (c : Ch) : ℕ := finrank (ZMod 2) c

/-! ## FOLD, W side -/
section FoldW
variable {τ : Type} (src dst : τ → Ch)

def hullW : Ch → List τ → Ch
  | X, [] => X
  | X, t :: L => hullW (X ⊔ src t) L

def OrdW : Ch → List τ → Prop
  | _, [] => True
  | X, t :: L => dst t ≤ X ∧ OrdW (X ⊔ src t) L

noncomputable def dropL (L : List τ) : ℕ := (L.map fun t => dm (src t) - dm (dst t)).sum

theorem le_hullW : ∀ (L : List τ) (X : Ch), X ≤ hullW src X L
  | [], X => le_refl X
  | t :: L, X => le_trans le_sup_left (le_hullW L (X ⊔ src t))

theorem fold_W (hle : ∀ t, dst t ≤ src t) :
    ∀ (L : List τ) (X : Ch), OrdW src dst X L → dm (hullW src X L) ≤ dm X + dropL src dst L
  | [], X, _ => by simp [hullW, dropL]
  | t :: L, X, h => by
    have ih := fold_W hle L (X ⊔ src t) h.2
    have h1 := Submodule.finrank_sup_add_finrank_inf_eq X (src t)
    have h2 : dm (dst t) ≤ dm (X ⊓ src t) := Submodule.finrank_mono (le_inf h.1 (hle t))
    have h3 : dm (dst t) ≤ dm (src t) := Submodule.finrank_mono (hle t)
    have e : dropL src dst (t :: L) = (dm (src t) - dm (dst t)) + dropL src dst L := by
      simp [dropL]
    show dm (hullW src (X ⊔ src t) L) ≤ _
    rw [e]
    have : dm (X ⊔ src t) + dm (X ⊓ src t) = dm X + dm (src t) := h1
    omega

end FoldW

/-! ## FOLD, U side -/
section FoldU
variable {τ : Type} (src dst : τ → Ch)

def hullU : Ch → List τ → Ch
  | X, [] => X
  | X, t :: L => hullU (X ⊓ dst t) L

def OrdU : Ch → List τ → Prop
  | _, [] => True
  | X, t :: L => X ≤ src t ∧ OrdU (X ⊓ dst t) L

theorem hullU_le : ∀ (L : List τ) (X : Ch), hullU dst X L ≤ X
  | [], X => le_refl X
  | t :: L, X => le_trans (hullU_le L (X ⊓ dst t)) inf_le_left

theorem hullU_le_mem : ∀ (L : List τ) (X : Ch) (t : τ), t ∈ L → hullU dst X L ≤ dst t
  | [], _, _, h => absurd h (List.not_mem_nil)
  | u :: L, X, t, h => by
    rcases List.mem_cons.1 h with rfl | h
    · exact le_trans (hullU_le dst L _) inf_le_right
    · exact hullU_le_mem L (X ⊓ dst u) t h

theorem fold_U (hle : ∀ t, dst t ≤ src t) :
    ∀ (L : List τ) (X : Ch), OrdU src dst X L → dm X ≤ dm (hullU dst X L) + dropL src dst L
  | [], X, _ => by simp [hullU, dropL]
  | t :: L, X, h => by
    have ih := fold_U hle L (X ⊓ dst t) h.2
    have h1 := Submodule.finrank_sup_add_finrank_inf_eq X (dst t)
    have h2 : dm (X ⊔ dst t) ≤ dm (src t) := Submodule.finrank_mono (sup_le h.1 (hle t))
    have e : dropL src dst (t :: L) = (dm (src t) - dm (dst t)) + dropL src dst L := by
      simp [dropL]
    show _ ≤ dm (hullU dst (X ⊓ dst t) L) + _
    rw [e]
    have : dm (X ⊔ dst t) + dm (X ⊓ dst t) = dm X + dm (dst t) := h1
    omega

end FoldU

/-! ## rank-8 consequences for the folded 8-row decoder -/
section Rank8
variable {T : Type} [Fintype T]

theorem dep_hull_ge_8 (W U : Fin 104 → T → ℚ) (hd : IsDecoder DF.lq W U) (h8 : Fintype.card T = 8)
    (k : T) (H : Ch) (hH : ∀ p, W p k ≠ 0 → DF.lq p ∈ H) : 8 ≤ dm H := by
  classical
  have hs := (DFR.rank8spans_of_decoder W U hd h8 k).1
  refine hs.trans (Submodule.finrank_mono ?_)
  rw [Submodule.span_le]
  rintro _ ⟨t, rfl⟩
  have ht := t.2
  simp only [dep, Finset.mem_filter, Finset.mem_univ, true_and] at ht
  exact hH t ht

theorem gat_hull_le_1 (W U : Fin 104 → T → ℚ) (hd : IsDecoder DF.lq W U) (h8 : Fintype.card T = 8)
    (k : T) (H : Ch) (hH : ∀ s, U s k ≠ 0 → ∀ y ∈ H, dot (DF.lq s) y = 0) : dm H ≤ 1 := by
  classical
  have hs := (DFR.rank8spans_of_decoder W U hd h8 k).2
  have ha := finrank_annS_add (fun s : gat U k => DF.lq s)
  have hle : H ≤ annS (fun s : gat U k => DF.lq s) := by
    intro y hy
    show Phi _ y = 0
    funext s
    rw [Phi_apply]
    have hsk := s.2
    simp only [gat, Finset.mem_filter, Finset.mem_univ, true_and] at hsk
    have := hH s hsk y hy
    rw [show dot y (DF.lq s) = dot (DF.lq s) y from dotProduct_comm _ _, this]
    rfl
  have h1 := Submodule.finrank_mono hle
  simp only [Fintype.card_fin] at ha
  show finrank (ZMod 2) H ≤ 1
  omega

end Rank8

/-! ## the decoupling lemma (Theorem G arithmetic) -/

/-- head deficit δ_r = 8 − dim a_r and end excess δ'_r = dim b_r − 1. -/
noncomputable def dW (a : Ch) : ℤ := 8 - (dm a : ℤ)
noncomputable def dU (b : Ch) : ℤ := (dm b : ℤ) - 1

/-- **DECOUPLING.**  8 groups with D_r ≥ dim a_r − dim b_r, any trunk drops dT and tail drops dT':
Σ D_r + Σ dT + Σ dT' ≥ 56 + E_W + E_U. -/
theorem decouple {R Tr Tu : Type} [Fintype R] [Fintype Tr] [Fintype Tu] (h8 : Fintype.card R = 8)
    (a b : R → Ch) (D : R → ℕ) (hD : ∀ r, dm (a r) - dm (b r) ≤ D r) (dT : Tr → ℕ) (dT' : Tu → ℕ) :
    56 + ((∑ t, (dT t : ℤ)) - ∑ r, dW (a r)) + ((∑ u, (dT' u : ℤ)) - ∑ r, dU (b r)) ≤
      ∑ r, (D r : ℤ) + ∑ t, (dT t : ℤ) + ∑ u, (dT' u : ℤ) := by
  have hr : ∀ r, (7 : ℤ) - dW (a r) - dU (b r) ≤ D r := by
    intro r; have := hD r; simp only [dW, dU]; omega
  have hs := Finset.sum_le_sum fun r (_ : r ∈ Finset.univ) => hr r
  simp only [Finset.sum_sub_distrib, Finset.sum_const, Finset.card_univ, h8] at hs
  norm_num at hs
  linarith

/-! ## OTI assembled per component -/
section OTI
variable {R Tr C : Type} [Fintype R] [Fintype Tr] [DecidableEq C]

/-- OTI of one component `c`: Σ_{r ∈ c} δ_r ≤ Σ_{t ∈ c} d_t. -/
def OTIComp (δ : R → ℤ) (d : Tr → ℕ) (cr : R → C) (ct : Tr → C) (c : C) : Prop :=
  ∑ r ∈ Finset.univ.filter (fun r => cr r = c), δ r ≤ ∑ t ∈ Finset.univ.filter (fun t => ct t = c), (d t : ℤ)

theorem oti_of_comp [Fintype C] (δ : R → ℤ) (d : Tr → ℕ) (cr : R → C) (ct : Tr → C)
    (h : ∀ c, OTIComp δ d cr ct c) : ∑ r, δ r ≤ ∑ t, (d t : ℤ) := by
  rw [← Finset.sum_fiberwise Finset.univ cr δ, ← Finset.sum_fiberwise Finset.univ ct (fun t => (d t : ℤ))]
  exact Finset.sum_le_sum fun c _ => h c

/-- FOLD components: the groups of `c` have pairwise-disjoint ancestor sets inside `c`, and FOLD bounds
each δ_r by its ancestors' drops (covers single-head components and nested in-trees). -/
theorem otiComp_disjoint (δ : R → ℤ) (d : Tr → ℕ) (cr : R → C) (ct : Tr → C) (c : C)
    (anc : R → Finset Tr) (hfold : ∀ r, cr r = c → δ r ≤ ∑ t ∈ anc r, (d t : ℤ))
    (hin : ∀ r, cr r = c → ∀ t ∈ anc r, ct t = c)
    (hdis : ∀ r r', cr r = c → cr r' = c → r ≠ r' → Disjoint (anc r) (anc r')) : OTIComp δ d cr ct c := by
  classical
  unfold OTIComp
  calc ∑ r ∈ Finset.univ.filter (fun r => cr r = c), δ r
      ≤ ∑ r ∈ Finset.univ.filter (fun r => cr r = c), ∑ t ∈ anc r, (d t : ℤ) :=
        Finset.sum_le_sum fun r hr => hfold r (Finset.mem_filter.1 hr).2
    _ = ∑ t ∈ (Finset.univ.filter (fun r => cr r = c)).biUnion anc, (d t : ℤ) := by
        rw [Finset.sum_biUnion]
        intro r hr r' hr' hne
        exact hdis r r' (Finset.mem_filter.1 hr).2 (Finset.mem_filter.1 hr').2 hne
    _ ≤ ∑ t ∈ Finset.univ.filter (fun t => ct t = c), (d t : ℤ) := by
        refine Finset.sum_le_sum_of_subset_of_nonneg ?_ fun _ _ _ => Int.natCast_nonneg _
        intro t ht
        obtain ⟨r, hr, htr⟩ := Finset.mem_biUnion.1 ht
        exact Finset.mem_filter.2 ⟨Finset.mem_univ _, hin r (Finset.mem_filter.1 hr).2 t htr⟩

/-- HALL components: every head of `c` has δ ≤ 1 (7-dim or larger), every trunk of `c` drops ≥ 1, and
#{small heads of c} ≤ #{trunks of c}. -/
theorem otiComp_hall (δ : R → ℤ) (d : Tr → ℕ) (cr : R → C) (ct : Tr → C) (c : C)
    (hδ : ∀ r, cr r = c → δ r ≤ 1) (hd : ∀ t, ct t = c → 1 ≤ d t)
    (hcard : (Finset.univ.filter (fun r => cr r = c ∧ 1 ≤ δ r)).card ≤
      (Finset.univ.filter (fun t => ct t = c)).card) : OTIComp δ d cr ct c := by
  classical
  unfold OTIComp
  have h1 : ∑ r ∈ Finset.univ.filter (fun r => cr r = c), δ r ≤
      ∑ r ∈ Finset.univ.filter (fun r => cr r = c), (if 1 ≤ δ r then (1 : ℤ) else 0) := by
    refine Finset.sum_le_sum fun r hr => ?_
    have := hδ r (Finset.mem_filter.1 hr).2
    split_ifs with h <;> omega
  have h2 : ∑ r ∈ Finset.univ.filter (fun r => cr r = c), (if 1 ≤ δ r then (1 : ℤ) else 0) =
      ((Finset.univ.filter (fun r => cr r = c ∧ 1 ≤ δ r)).card : ℤ) := by
    rw [Finset.sum_ite, Finset.sum_const_zero, add_zero, Finset.sum_const, Finset.filter_filter]
    simp
  have h3 : ((Finset.univ.filter (fun t => ct t = c)).card : ℤ) ≤
      ∑ t ∈ Finset.univ.filter (fun t => ct t = c), (d t : ℤ) := by
    rw [Finset.card_eq_sum_ones, Nat.cast_sum]
    exact Finset.sum_le_sum fun t ht => by exact_mod_cast hd t (Finset.mem_filter.1 ht).2
  have h4 : ((Finset.univ.filter (fun r => cr r = c ∧ 1 ≤ δ r)).card : ℤ) ≤
      ((Finset.univ.filter (fun t => ct t = c)).card : ℤ) := by exact_mod_cast hcard
  linarith

end OTI
end ThmG

#print axioms ThmG.fold_W
#print axioms ThmG.fold_U
#print axioms ThmG.dep_hull_ge_8
#print axioms ThmG.gat_hull_le_1
#print axioms ThmG.decouple
#print axioms ThmG.oti_of_comp
#print axioms ThmG.otiComp_disjoint
#print axioms ThmG.otiComp_hall
