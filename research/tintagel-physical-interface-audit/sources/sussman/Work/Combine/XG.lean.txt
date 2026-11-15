import Work.BlockApply.Exact
import Work.SharedSumStructured.Labels

/-!
# (key: combine) Whole blocks on arbitrary frame matrices

`Work.SharedSumStructured.GPath` moves a role one unit direction at a time (`Reach`), because the
labels of a shared-sum helper circuit do not live in one fixed orthonormal basis.  Here the same
calculus is redone with WHOLE BLOCKS and an exact block count, on top of the block engine
(`Work.Block.*`) and the exact block routes of `Work.BlockApply.Exact` (`XStep`, `XRoute`):

* `bcost φ q`       price of one block of rank `q` (nothing if `q = 0`);
* `rcost φ l`       price of a list of block ranks;
* `XReach A B c`    on ANY role, the frame matrix `A` is carried to `B` by a block word whose
                    price is `c φ` for every price list `φ`;
* `XReach.of_subset`, `XReach.down_subset`
                    inside ONE orthonormal basis, a bigger index set is reached with ONE block
                    of rank `|t \ s|` (two blocks `(m-1)+1` if the rank is the whole space);
* `XRoute.reach_all` every role moves by its own block word; prices add;
* `XMap H α`        block frame map: projectors of `H` to frame matrices on `α`, a climb inside
                    one orthonormal basis of `H` costs ONE block of the rank of the climb;
* `xmap1`, `xmap2`  the two frame maps of the two-stage network (same matrices as
                    `SS.fmap1`, `SS.fmap2`);
* `xreach_X .. xreach_end`
                    the exterior climbs between the two stages, each ONE block.

No `sorry`.
-/

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace OAI
namespace PowerSaving
namespace CB
open Binary Matrix Finset RAM SS
noncomputable section

/-- price of one block of rank `q`; no block if `q = 0`. -/
def bcost (φ : ℕ → ℝ) (q : ℕ) : ℝ := if q = 0 then 0 else φ q

/-- price of a list of block ranks (zeros are free). -/
def rcost (φ : ℕ → ℝ) (l : List ℕ) : ℝ := (l.map (bcost φ)).sum

lemma bcost_zero (φ : ℕ → ℝ) : bcost φ 0 = 0 := by simp [bcost]
lemma bcost_pos (φ : ℕ → ℝ) {q : ℕ} (h : q ≠ 0) : bcost φ q = φ q := by simp [bcost, h]
lemma rcost_nil (φ : ℕ → ℝ) : rcost φ [] = 0 := rfl
lemma rcost_cons (φ : ℕ → ℝ) (a : ℕ) (l : List ℕ) : rcost φ (a :: l) = bcost φ a + rcost φ l := by
  simp [rcost]
lemma rcost_append (φ : ℕ → ℝ) (l l' : List ℕ) : rcost φ (l ++ l') = rcost φ l + rcost φ l' := by
  simp [rcost]
lemma rcost_single (φ : ℕ → ℝ) (a : ℕ) : rcost φ [a] = bcost φ a := by simp [rcost]

lemma split_bcost (φ : ℕ → ℝ) {m q : ℕ} (h : q < m) : splitCost φ m q = bcost φ q := by
  unfold splitCost bcost
  by_cases h0 : q = 0
  · simp [h0]
  · simp [h0, h]

lemma split_full (φ : ℕ → ℝ) {m : ℕ} (hm : m ≠ 0) : splitCost φ m m = φ (m-1) + φ 1 := by
  simp [splitCost, hm]

section
variable {α : Type*} [Fintype α] [DecidableEq α]

/-- On any role, the frame matrix `A` is carried to `B` by a block word of price `c`. -/
def XReach (A B : CMat α) (c : (ℕ → ℝ) → ℝ) : Prop :=
  ∀ (ρ : Type) [Fintype ρ] [DecidableEq ρ] (l : ρ), XStep l A B c

namespace XReach
variable {A B C : CMat α} {c c' : (ℕ → ℝ) → ℝ}

theorem refl (A : CMat α) : XReach A A (fun _ => 0) := fun ρ _ _ l => XStep.refl l A

theorem cast (h : XReach A B c) (hc : ∀ φ, c φ = c' φ) : XReach A B c' :=
  fun ρ _ _ l => (h ρ l).cast hc

theorem trans (h : XReach A B c) (g : XReach B C c') : XReach A C (fun φ => c φ + c' φ) :=
  fun ρ _ _ l => (h ρ l).trans (g ρ l)

/-- Inside one orthonormal basis: ONE block for all the new indices. -/
theorem of_subset (hm : 2 ≤ Fintype.card α) (A : OBase α) {s t : Finset α} (h : s ⊆ t) :
    XReach (frame A s) (frame A t)
      (fun φ => splitCost φ (Fintype.card α) (t \ s).card) := by
  intro ρ _ _ l
  have e := A.xup_step (ρ := ρ) hm l s (t \ s) disjoint_sdiff
  rwa [union_sdiff_of_subset h] at e

/-- Inside one orthonormal basis, downwards: ONE block for all the removed indices. -/
theorem down_subset (hm : 2 ≤ Fintype.card α) (A : OBase α) {s t : Finset α} (h : s ⊆ t) :
    XReach (frame A t) (frame A s)
      (fun φ => splitCost φ (Fintype.card α) (t \ s).card) := by
  intro ρ _ _ l
  have e := A.xdown_step (ρ := ρ) hm l s (t \ s) disjoint_sdiff
  rwa [union_sdiff_of_subset h] at e

end XReach
end

section
variable {α : Type*} [Fintype α] [DecidableEq α] {ρ : Type} [Fintype ρ] [DecidableEq ρ]

/-- rewrite the scalar map of an exact route. -/
theorem _root_.OAI.PowerSaving.RAM.XRoute.castg {S T : ρ → CMat α} {g g' : (ρ→ℂ) → (ρ→ℂ)} {c : (ℕ → ℝ) → ℝ}
    (h : XRoute S T g c) (hg : g = g') : XRoute S T g' c := hg ▸ h

/-- Every role moves by its own block word; prices add. -/
theorem _root_.OAI.PowerSaving.RAM.XRoute.reach_all (S T : ρ → CMat α) (c : ρ → (ℕ → ℝ) → ℝ)
    (h : ∀ r, XReach (S r) (T r) (c r)) :
    XRoute S T id (fun φ => ∑ r, c r φ) := by
  have hh (J : Finset ρ) :
      XRoute S (fun r => if r ∈ J then T r else S r) id (fun φ => ∑ r ∈ J, c r φ) := by
    induction J using Finset.induction_on with
    | empty =>
      have e0 : (fun r => if r ∈ (∅ : Finset ρ) then T r else S r) = S := by
        funext r; simp
      rw [e0]
      exact XRoute.refl.cast (fun φ => by simp)
    | insert l J hl ih =>
      have hsl : (if l ∈ J then T l else S l) = S l := by simp [hl]
      have step : XStep l (if l ∈ J then T l else S l) (T l) (c l) := by
        rw [hsl]; exact h l ρ l
      have b := XRoute.on_role (fun r => if r ∈ J then T r else S r) l (T l) step
      have hupd : Function.update (fun r => if r ∈ J then T r else S r) l (T l) =
          fun r => if r ∈ insert l J then T r else S r := by
        funext r
        by_cases hr : r = l
        · subst hr; simp
        · simp [Function.update_of_ne hr, Finset.mem_insert, hr]
      rw [hupd] at b
      exact (ih.trans b).cast (fun φ => by rw [Finset.sum_insert hl, add_comm])
  have H := hh Finset.univ
  have e1 : (fun r => if r ∈ (Finset.univ : Finset ρ) then T r else S r) = T := by
    funext r; simp
  rw [e1] at H
  exact H

end

/-! ## block frame maps -/

/-- A block frame map: projectors of `H` to frame matrices on `α`; a climb (or a descent)
inside one orthonormal basis of `H` is ONE block whose rank is the number of new indices. -/
structure XMap (H α : Type) [Fintype H] [DecidableEq H] [Fintype α] [DecidableEq α] where
  Φ : Matrix H H F → CMat α
  up : ∀ (A : OBase H) (s t : Finset H), s ⊆ t →
    XReach (Φ (A.mat s)) (Φ (A.mat t)) (fun φ => bcost φ (t \ s).card)
  down : ∀ (A : OBase H) (s t : Finset H), s ⊆ t →
    XReach (Φ (A.mat t)) (Φ (A.mat s)) (fun φ => bcost φ (t \ s).card)

section XMapLemmas
variable {H α : Type} [Fintype H] [DecidableEq H] [Fintype α] [DecidableEq α]

/-- one `Climb` of single-factor labels is ONE block of rank `V.d - U.d`. -/
lemma XMap.climb (Xm : XMap H α) {U V : Lbl H} (h : Climb U V) :
    XReach (Xm.Φ U.P) (Xm.Φ V.P) (fun φ => bcost φ (V.d - U.d)) := by
  obtain ⟨A, s, t, hst, hU, hV, hd⟩ := h
  have e : V.d - U.d = (t \ s).card := by omega
  rw [hU, hV, e]
  exact Xm.up A s t hst

/-- the same climb, backwards: ONE block of rank `V.d - U.d`. -/
lemma XMap.descend (Xm : XMap H α) {U V : Lbl H} (h : Climb U V) :
    XReach (Xm.Φ V.P) (Xm.Φ U.P) (fun φ => bcost φ (V.d - U.d)) := by
  obtain ⟨A, s, t, hst, hU, hV, hd⟩ := h
  have e : V.d - U.d = (t \ s).card := by omega
  rw [hU, hV, e]
  exact Xm.down A s t hst

end XMapLemmas

section Two
variable {H : Type} [Fintype H] [DecidableEq H]

lemma card_lt_sq (hH : 2 ≤ Fintype.card H) (s : Finset H) :
    s.card < Fintype.card (H × H) := by
  rw [Fintype.card_prod]
  have h1 := card_le_univ s
  nlinarith

lemma two_le_sq (hH : 2 ≤ Fintype.card H) : 2 ≤ Fintype.card (H × H) := by
  rw [Fintype.card_prod]; nlinarith

/-- stage 1 block frame map (second factor fixed to the basis vector `B.v k`). -/
def xmap1 (hH : 2 ≤ Fintype.card H) (B : OBase H) (k : H) : XMap H (H × H) where
  Φ := Phi1 (B.v k)
  up := fun A s t hst => by
    rw [Phi1_eq, Phi1_eq]
    have hsub : s ×ˢ ({k} : Finset H) ⊆ t ×ˢ {k} := product_subset_product hst (Subset.refl _)
    refine (XReach.of_subset (two_le_sq hH) _ hsub).cast (fun φ => ?_)
    have e : ((t ×ˢ ({k} : Finset H)) \ (s ×ˢ {k})).card = (t \ s).card := by
      rw [card_sdiff_of_subset hsub, card_product, card_product, card_singleton, mul_one, mul_one,
        card_sdiff_of_subset hst]
    rw [e]
    exact split_bcost φ (card_lt_sq hH _)
  down := fun A s t hst => by
    rw [Phi1_eq, Phi1_eq]
    have hsub : s ×ˢ ({k} : Finset H) ⊆ t ×ˢ {k} := product_subset_product hst (Subset.refl _)
    refine (XReach.down_subset (two_le_sq hH) _ hsub).cast (fun φ => ?_)
    have e : ((t ×ˢ ({k} : Finset H)) \ (s ×ˢ {k})).card = (t \ s).card := by
      rw [card_sdiff_of_subset hsub, card_product, card_product, card_singleton, mul_one, mul_one,
        card_sdiff_of_subset hst]
    rw [e]
    exact split_bcost φ (card_lt_sq hH _)

lemma sdiff_stage2 (k : H) {s t : Finset H} (hst : s ⊆ t) :
    ((({k} : Finset H) ×ˢ t) ∪ ((univ \ {k}) ×ˢ univ)) \ ((({k} : Finset H) ×ˢ s) ∪ ((univ \ {k}) ×ˢ univ))
      = ({k} : Finset H) ×ˢ (t \ s) := by
  ext ⟨i, j⟩
  simp only [mem_sdiff, mem_union, mem_product, mem_singleton, mem_univ, true_and, and_true]
  tauto

lemma sub_stage2 (k : H) {s t : Finset H} (hst : s ⊆ t) :
    ((({k} : Finset H) ×ˢ s) ∪ ((univ \ {k}) ×ˢ univ)) ⊆ ((({k} : Finset H) ×ˢ t) ∪ ((univ \ {k}) ×ˢ univ)) :=
  union_subset_union (product_subset_product (Subset.refl _) hst) (Subset.refl _)

/-- stage 2 block frame map (first factor fixed to the basis vector `B.v k`). -/
def xmap2 (hH : 2 ≤ Fintype.card H) (B : OBase H) (k : H) : XMap H (H × H) where
  Φ := Phi2 (B.v k)
  up := fun A s t hst => by
    rw [Phi2_eq' A B k s, Phi2_eq' A B k t]
    refine (XReach.of_subset (two_le_sq hH) _ (sub_stage2 k hst)).cast (fun φ => ?_)
    have e : (((({k} : Finset H) ×ˢ t) ∪ ((univ \ {k}) ×ˢ univ))
        \ ((({k} : Finset H) ×ˢ s) ∪ ((univ \ {k}) ×ˢ univ))).card = (t \ s).card := by
      rw [sdiff_stage2 k hst, card_product, card_singleton, one_mul]
    rw [e]
    exact split_bcost φ (card_lt_sq hH _)
  down := fun A s t hst => by
    rw [Phi2_eq' A B k s, Phi2_eq' A B k t]
    refine (XReach.down_subset (two_le_sq hH) _ (sub_stage2 k hst)).cast (fun φ => ?_)
    have e : (((({k} : Finset H) ×ˢ t) ∪ ((univ \ {k}) ×ˢ univ))
        \ ((({k} : Finset H) ×ˢ s) ∪ ((univ \ {k}) ×ˢ univ))).card = (t \ s).card := by
      rw [sdiff_stage2 k hst, card_product, card_singleton, one_mul]
    rw [e]
    exact split_bcost φ (card_lt_sq hH _)

/-! ### the exterior climbs, each ONE block -/

variable (hH : 2 ≤ Fintype.card H) (A B : OBase H) (ka kb : H)
include hH

/-- rank of the exterior climb of a bank role: `(h-1)^2`. -/
def rkBank (H : Type) [Fintype H] : ℕ := (Fintype.card H - 1) * (Fintype.card H - 1)
/-- rank of the exterior climb of a helper slot: `(h-1) h`. -/
def rkSlot (H : Type) [Fintype H] : ℕ := (Fintype.card H - 1) * Fintype.card H

lemma rkBank_lt : rkBank H < Fintype.card (H × H) := by
  rw [Fintype.card_prod]; unfold rkBank
  obtain ⟨k, hk⟩ : ∃ k, Fintype.card H = k + 1 := ⟨Fintype.card H - 1, by omega⟩
  rw [hk, Nat.add_sub_cancel]; nlinarith

lemma rkSlot_lt : rkSlot H < Fintype.card (H × H) := by
  rw [Fintype.card_prod]; unfold rkSlot
  obtain ⟨k, hk⟩ : ∃ k, Fintype.card H = k + 1 := ⟨Fintype.card H - 1, by omega⟩
  rw [hk, Nat.add_sub_cancel]; nlinarith

/-- `X(a,b)` between the stages: ONE block of rank `(h-1)^2`. -/
lemma xreach_X : XReach (Phi1 (B.v kb) 1) (Phi2 (A.v ka) (tt (B.v kb)))
    (fun φ => bcost φ (rkBank H)) := by
  rw [Phi1_full A B kb, ← mat_single, Phi2_eq' B A ka]
  have hsub : (univ : Finset H) ×ˢ ({kb} : Finset H)
      ⊆ (({ka} : Finset H) ×ˢ {kb}) ∪ ((univ \ {ka}) ×ˢ univ) := by
    rintro ⟨i,j⟩ h
    simp only [mem_union, mem_product, mem_singleton, mem_sdiff, mem_univ, true_and,
      and_true] at h ⊢
    by_cases hi : i = ka
    · exact Or.inl ⟨hi, h⟩
    · exact Or.inr hi
  refine (XReach.of_subset (two_le_sq hH) _ hsub).cast (fun φ => ?_)
  have hdis : Disjoint (({ka} : Finset H) ×ˢ ({kb} : Finset H)) ((univ \ {ka}) ×ˢ univ) := by
    rw [disjoint_left]
    rintro ⟨i,j⟩ h1 h2
    simp only [mem_product, mem_singleton, mem_sdiff, mem_univ, true_and, and_true] at h1 h2
    exact h2 h1.1
  have h1 := Finset.card_sdiff_add_card_eq_card hsub
  rw [card_union_of_disjoint hdis, card_product, card_product, card_product, card_singleton,
    card_singleton, card_sdiff_of_subset (subset_univ _), card_univ, card_singleton] at h1
  have e : ((({ka} : Finset H) ×ˢ ({kb} : Finset H) ∪ (univ \ {ka}) ×ˢ univ)
      \ ((univ : Finset H) ×ˢ ({kb} : Finset H))).card = rkBank H := by
    unfold rkBank
    obtain ⟨k, hk⟩ : ∃ k, Fintype.card H = k + 1 := ⟨Fintype.card H - 1, by omega⟩
    rw [hk, Nat.add_sub_cancel] at h1 ⊢
    nlinarith
  rw [e]
  exact split_bcost φ (rkBank_lt hH)

/-- `Y(a,b)` between the stages: ONE block of rank `(h-1)^2`. -/
lemma xreach_Y : XReach (Phi1 (B.v kb) (1 + tt (A.v ka))) (Phi2 (A.v ka) 0)
    (fun φ => bcost φ (rkBank H)) := by
  rw [Phi1_perp A B ka kb, Phi2_zero' A B ka]
  have hsub : ((univ : Finset H) \ {ka}) ×ˢ ({kb} : Finset H) ⊆ (univ \ {ka}) ×ˢ univ :=
    product_subset_product (Subset.refl _) (subset_univ _)
  refine (XReach.of_subset (two_le_sq hH) _ hsub).cast (fun φ => ?_)
  have h1 := Finset.card_sdiff_add_card_eq_card hsub
  rw [card_product, card_product, card_singleton,
    card_sdiff_of_subset (subset_univ _), card_univ, card_singleton] at h1
  have e : ((((univ : Finset H) \ {ka}) ×ˢ (univ : Finset H))
      \ (((univ : Finset H) \ {ka}) ×ˢ ({kb} : Finset H))).card = rkBank H := by
    unfold rkBank
    obtain ⟨k, hk⟩ : ∃ k, Fintype.card H = k + 1 := ⟨Fintype.card H - 1, by omega⟩
    rw [hk, Nat.add_sub_cancel] at h1 ⊢
    nlinarith
  rw [e]
  exact split_bcost φ (rkBank_lt hH)

/-- a stage-1 helper slot after its invocation: ONE block of rank `(h-1) h`. -/
lemma xreach_S1 : XReach (Phi1 (B.v kb) 1) (kernel (H × H)) (fun φ => bcost φ (rkSlot H)) := by
  rw [Phi1_full (OBase.canonical H) B kb, ← frame_univ (pbase (OBase.canonical H) B)]
  have hsub : (univ : Finset H) ×ˢ ({kb} : Finset H) ⊆ univ := subset_univ _
  refine (XReach.of_subset (two_le_sq hH) _ hsub).cast (fun φ => ?_)
  have h1 := Finset.card_sdiff_add_card_eq_card hsub
  rw [card_product, card_singleton, card_univ, card_univ, Fintype.card_prod] at h1
  have e : ((univ : Finset (H × H)) \ ((univ : Finset H) ×ˢ ({kb} : Finset H))).card = rkSlot H := by
    unfold rkSlot
    obtain ⟨k, hk⟩ : ∃ k, Fintype.card H = k + 1 := ⟨Fintype.card H - 1, by omega⟩
    rw [hk] at h1 ⊢
    rw [Nat.add_sub_cancel]
    nlinarith
  rw [e]
  exact split_bcost φ (rkSlot_lt hH)

/-- a stage-2 helper slot before its invocation: ONE block of rank `(h-1) h`. -/
lemma xreach_S2 : XReach (1 : CMat (H × H)) (Phi2 (A.v ka) 0) (fun φ => bcost φ (rkSlot H)) := by
  rw [Phi2_zero' A (OBase.canonical H) ka, ← frame_zero (pbase A (OBase.canonical H))]
  refine (XReach.of_subset (two_le_sq hH) _ (empty_subset _)).cast (fun φ => ?_)
  have e : ((((univ : Finset H) \ {ka}) ×ˢ (univ : Finset H)) \ ∅).card = rkSlot H := by
    unfold rkSlot
    rw [sdiff_empty, card_product, card_sdiff_of_subset (subset_univ _), card_univ, card_singleton]
  rw [e]
  exact split_bcost φ (rkSlot_lt hH)

/-- an idle role: nothing up to everything, TWO blocks of ranks `m-1` and `1`. -/
lemma xreach_idle : XReach (1 : CMat (H × H)) (kernel (H × H))
    (fun φ => φ (Fintype.card (H × H) - 1) + φ 1) := by
  rw [← frame_zero (OBase.canonical (H × H)), ← frame_univ (OBase.canonical (H × H))]
  refine (XReach.of_subset (two_le_sq hH) _ (empty_subset _)).cast (fun φ => ?_)
  rw [sdiff_empty, card_univ]
  exact split_full φ (by have := two_le_sq hH; omega)

/-- the endpoint copy comes down one line: ONE block of rank `1`. -/
lemma xreach_end : XReach (kernel (H × H)) (Phi2 (A.v ka) (1 + tt (B.v kb))) (fun φ => φ 1) := by
  rw [Phi2_perp A B ka kb, ← frame_univ (pbase A B)]
  refine (XReach.down_subset (two_le_sq hH) _ (subset_univ _)).cast (fun φ => ?_)
  have e : (univ : Finset (H × H)) \ (univ \ {(ka,kb)}) = {(ka,kb)} := by ext x; simp
  rw [e, card_singleton, split_bcost φ (by have := two_le_sq hH; omega)]
  exact bcost_pos φ one_ne_zero

end Two
end
end CB
end PowerSaving
end OAI

#print axioms OAI.PowerSaving.RAM.XRoute.reach_all
#print axioms OAI.PowerSaving.CB.xmap1
#print axioms OAI.PowerSaving.CB.xmap2
#print axioms OAI.PowerSaving.CB.xreach_X
#print axioms OAI.PowerSaving.CB.xreach_idle
