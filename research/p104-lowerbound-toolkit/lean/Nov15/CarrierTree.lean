import Nov15.FutureAttr

/-!
CARRIERTREE (lane LEANCT).  Kernel-only: no sorry / native_decide / new axioms.

Formalises SEPPAYS's THEOREM CT (carrier-tree separation).
* `ARun0` : FutureAttr's `ARun` WITHOUT `hcold`.  Every owned lifetime is GTD with respect to ALL
  its read-outs (a read of owned `e` by anything, public or owned, sets `B e` and `dep e`).
* `InvS`  : the invariant without the cold-content field (identity, charts, GTD cost bound).
* `Fo`    : forests (= acyclic parent maps) over lifetimes; `wf` is `A_{p(k)} ⊆ B_k`.
* `carrier_tree_decoder`: if non-roots have zero weight and every root's effective final content is
  cold at its subtree meet, the root rows form a decoder with total price ≤ cost.
* `mass_le_R_ct`, `R_ge_of_wall_ct`; non-vacuity `Toy2` (FLUSHROW's pinned hot-carry witness).
-/

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace CarrierTree
open Module Submodule Finset Function PriceLemma FutureAttr

/-! ## Run model: ARun0 -/
section Model
variable {K : Type*} [Field K] {τ ι ω : Type*} {n : ℕ} [Fintype τ] [DecidableEq ι]

/-- `ARun` without `hcold`; `dep`/`B` are updated by every read of an owned register. -/
inductive ARun0 (P : Finset ι) (X : τ → ι) (s0 : St K n ι ω) :
    St K n ι ω → Bk K τ ω ι n → ℕ → Prop
  | refl : ARun0 P X s0 s0 Bk.init 0
  | add {s bk cost} (d e : ι) (l : K) (hne : d ≠ e) (hch : s.ch d ≤ s.ch e)
      (hgtd : d ∉ P → bk.dep d = false) :
      ARun0 P X s0 s bk cost →
      ARun0 P X s0
        { s with v := fun r j => s.v r j + if r = d then l * s.v e j else 0 }
        { bk with
          W := fun r t => bk.W r t + if r = e then l * (tv X d t - bk.W d t) else 0
          A := fun r => if r = d ∧ d ∉ P then bk.A d ⊓ s.ch d else bk.A r
          B := fun r => if r = e ∧ e ∉ P then bk.B e ⊔ s.ch e else bk.B r
          dep := fun r => if r = e ∧ e ∉ P then true else bk.dep r } cost
  | init {s bk cost} (r : ι) (hr : r ∉ P) :
      ARun0 P X s0 s bk cost →
      ARun0 P X s0
        { s with v := fun r' j => if r' = r then 0 else s.v r' j }
        { W := fun r' t => if r' = r then 0 else bk.W r' t
          A := fun r' => if r' = r then ⊤ else bk.A r'
          B := fun r' => if r' = r then ⊥ else bk.B r'
          dep := fun r' => if r' = r then false else bk.dep r'
          lc := fun r' => if r' = r then 0 else bk.lc r'
          closed := ⟨bk.W r, s.v r, bk.A r, bk.B r, bk.lc r⟩ :: bk.closed } cost
  | down {s bk cost} (r : ι) (D : Chart n) (hr : r ∉ P) (h : D ≤ s.ch r) :
      ARun0 P X s0 s bk cost →
      ARun0 P X s0 { s with ch := fun r' => if r' = r then D else s.ch r' } bk cost
  | upOwn {s bk cost} (r : ι) (D : Chart n) (hr : r ∉ P) (h : s.ch r ≤ D) :
      ARun0 P X s0 s bk cost →
      ARun0 P X s0 { s with ch := fun r' => if r' = r then D else s.ch r' }
        { bk with lc := fun r' =>
            if r' = r then bk.lc r + (finrank (ZMod 2) D - finrank (ZMod 2) (s.ch r)) else bk.lc r' }
        (cost + (finrank (ZMod 2) D - finrank (ZMod 2) (s.ch r)))
  | upPub {s bk cost} (r : ι) (D : Chart n) (hr : r ∈ P) (h : s.ch r ≤ D) :
      ARun0 P X s0 s bk cost →
      ARun0 P X s0 { s with ch := fun r' => if r' = r then D else s.ch r' } bk cost

/-- a lifetime row is priced-valid: weights on labels of `B`, and `dim (A ⊔ B) ≤ dim A + lc`. -/
def Ok0 (q : τ → Fin n → ZMod 2) (ρ : Row K τ ω n) : Prop :=
  (∀ t, ρ.w t ≠ 0 → q t ∈ ρ.B) ∧
  finrank (ZMod 2) (ρ.A ⊔ ρ.B : Chart n) ≤ finrank (ZMod 2) ρ.A + ρ.lc

end Model

/-! ## The invariant without cold content -/
section Inv
variable {K : Type*} [Field K] {τ ι ω : Type*} {n : ℕ} [Fintype τ] [DecidableEq ι] [Fintype ι]
variable (P : Finset ι) (X : τ → ι) (q : τ → Fin n → ZMod 2) (s0 : St K n ι ω)

structure InvS (s : St K n ι ω) (bk : Bk K τ ω ι n) (cost : ℕ) : Prop where
  i1 : ∀ t j, s.v (X t) j - s0.v (X t) j =
    ∑ r, bk.W r t * s.v r j + (bk.closed.map fun ρ => ρ.w t * ρ.val j).sum
  i2 : ∀ r ∈ P, ∀ t, bk.W r t ≠ 0 → q t ∈ s.ch r
  i2' : ∀ t, q t ∈ s.ch (X t)
  i3 : ∀ r ∉ P, bk.dep r = false → bk.W r = 0
  i3b : ∀ r ∉ P, bk.dep r = false → bk.B r = ⊥
  i4 : ∀ r ∉ P, ∀ t, bk.W r t ≠ 0 → q t ∈ bk.B r
  i6 : ∀ r ∉ P, finrank (ZMod 2) (bk.A r ⊔ bk.B r ⊔ s.ch r : Chart n) ≤
      finrank (ZMod 2) (bk.A r) + bk.lc r
  i7 : ∀ ρ ∈ bk.closed, Ok0 q ρ
  i8 : cost = ∑ r ∈ univ.filter (· ∉ P), bk.lc r + (bk.closed.map fun ρ => ρ.lc).sum

theorem InvS.refl (hq : ∀ t, q t ∈ s0.ch (X t)) :
    InvS P X q s0 s0 Bk.init 0 where
  i1 := by intro t j; simp [Bk.init]
  i2 := by intro r _ t h; simp [Bk.init] at h
  i2' := hq
  i3 := by intro r _ _; rfl
  i3b := by intro r _ _; rfl
  i4 := by intro r _ t h; simp [Bk.init] at h
  i6 := by
    intro r _
    have : (⊤ ⊔ ⊥ ⊔ s0.ch r : Chart n) = ⊤ := by simp
    show finrank (ZMod 2) ↥((⊤ : Chart n) ⊔ ⊥ ⊔ s0.ch r) ≤ finrank (ZMod 2) ↥(⊤ : Chart n) + 0
    rw [this]; omega
  i7 := by intro ρ h; simp [Bk.init] at h
  i8 := by simp [Bk.init]

theorem InvS.add (hXP : ∀ t, X t ∈ P) {s : St K n ι ω} {bk : Bk K τ ω ι n} {cost : ℕ}
    (h : InvS P X q s0 s bk cost)
    (d e : ι) (l : K) (hne : d ≠ e) (hch : s.ch d ≤ s.ch e)
    (hgtd : d ∉ P → bk.dep d = false) :
    InvS P X q s0
        { s with v := fun r j => s.v r j + if r = d then l * s.v e j else 0 }
        { bk with
          W := fun r t => bk.W r t + if r = e then l * (tv X d t - bk.W d t) else 0
          A := fun r => if r = d ∧ d ∉ P then bk.A d ⊓ s.ch d else bk.A r
          B := fun r => if r = e ∧ e ∉ P then bk.B e ⊔ s.ch e else bk.B r
          dep := fun r => if r = e ∧ e ∉ P then true else bk.dep r } cost := by
  have hω0 : d ∉ P → ∀ t, tv X d t - bk.W d t = 0 := by
    intro hd t
    have h1 : tv (K := K) X d t = 0 := by
      simp only [tv]; rw [if_neg]; intro hh; exact hd (hh ▸ hXP t)
    have h2 : bk.W d t = 0 := congrFun (h.i3 d hd (hgtd hd)) t
    rw [h1, h2]; ring
  have hωq : d ∈ P → ∀ t, l * (tv X d t - bk.W d t) ≠ 0 → q t ∈ s.ch e := by
    intro hd t hne0
    have hne1 : tv X d t - bk.W d t ≠ 0 := right_ne_zero_of_mul hne0
    by_cases hdt : d = X t
    · subst hdt; exact hch (h.i2' t)
    · have h1 : tv (K := K) X d t = 0 := by simp [tv, hdt]
      rw [h1] at hne1
      have : bk.W d t ≠ 0 := fun hh => hne1 (by rw [hh]; ring)
      exact hch (h.i2 d hd t this)
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · intro t j
    have hsum : ∑ r, (bk.W r t + if r = e then l * (tv X d t - bk.W d t) else 0) *
          (s.v r j + if r = d then l * s.v e j else 0) =
        ∑ r, bk.W r t * s.v r j + l * (tv X d t - bk.W d t) * s.v e j
          + bk.W d t * (l * s.v e j) := by
      simp only [add_mul, mul_add, Finset.sum_add_distrib]
      have e1 : ∑ r, (if r = e then l * (tv X d t - bk.W d t) else 0) * s.v r j =
          l * (tv X d t - bk.W d t) * s.v e j := by simp [ite_mul]
      have e2 : ∑ r, bk.W r t * (if r = d then l * s.v e j else 0) =
          bk.W d t * (l * s.v e j) := by simp [mul_ite]
      have e3 : ∑ r, (if r = e then l * (tv X d t - bk.W d t) else 0) *
          (if r = d then l * s.v e j else 0) = 0 := by
        apply Finset.sum_eq_zero; intro r _
        by_cases hr : r = e
        · have : r ≠ d := fun h' => hne (h'.symm.trans hr)
          simp [this]
        · simp [hr]
      rw [e1, e2, e3]; ring
    dsimp only
    rw [hsum]
    have h1 := h.i1 t j
    by_cases hXt : X t = d
    · have : tv (K := K) X d t = 1 := by simp [tv, hXt.symm]
      simp only [hXt, if_true, this]
      rw [hXt] at h1
      linear_combination h1
    · have : tv (K := K) X d t = 0 := by
        simp only [tv]; rw [if_neg]; intro hh; exact hXt hh.symm
      simp only [hXt, if_false, this]
      linear_combination h1
  · intro r hr t hW
    dsimp only at hW ⊢
    by_cases hre : r = e
    · subst hre
      simp only [if_true] at hW
      by_cases hw0 : bk.W r t = 0
      · rw [hw0, zero_add] at hW
        by_cases hdP : d ∈ P
        · exact hωq hdP t hW
        · exact absurd (by rw [hω0 hdP t, mul_zero]) hW
      · exact h.i2 r hr t hw0
    · simp only [hre, if_false, add_zero] at hW; exact h.i2 r hr t hW
  · exact h.i2'
  · intro r hr hdep
    dsimp only at hdep ⊢
    have hnc : ¬(r = e ∧ e ∉ P) := fun hc => by simp [hc] at hdep
    rw [if_neg hnc] at hdep
    have hre : r ≠ e := fun hh => hnc ⟨hh, hh ▸ hr⟩
    funext t
    have hW := congrFun (h.i3 r hr hdep) t
    simp [hre, hW]
  · intro r hr hdep
    dsimp only at hdep ⊢
    have hnc : ¬(r = e ∧ e ∉ P) := fun hc => by simp [hc] at hdep
    rw [if_neg hnc] at hdep ⊢
    exact h.i3b r hr hdep
  · intro r hr t hW
    dsimp only at hW ⊢
    by_cases hc : r = e ∧ e ∉ P
    · rw [if_pos hc]
      obtain ⟨hr1, heP⟩ := hc
      subst hr1
      simp only [if_true] at hW
      by_cases hw0 : bk.W r t = 0
      · rw [hw0, zero_add] at hW
        by_cases hdP : d ∈ P
        · exact Submodule.mem_sup_right (hωq hdP t hW)
        · exact absurd (by rw [hω0 hdP t, mul_zero]) hW
      · exact Submodule.mem_sup_left (h.i4 r hr t hw0)
    · rw [if_neg hc]
      have hre : r ≠ e := fun hh => hc ⟨hh, hh ▸ hr⟩
      exact h.i4 r hr t (by simpa [hre] using hW)
  · intro r hr
    dsimp only
    by_cases hrd : r = d ∧ d ∉ P
    · obtain ⟨hr1, hdP⟩ := hrd
      subst hr1
      have hBe : ¬ (r = e ∧ e ∉ P) := fun hc => hne hc.1
      have hA : (if r = r ∧ r ∉ P then bk.A r ⊓ s.ch r else bk.A r) = bk.A r ⊓ s.ch r :=
        if_pos ⟨rfl, hdP⟩
      have hB := h.i3b r hr (hgtd hdP)
      have key := life_intake (bk.A r) (s.ch r) (bk.lc r) (by have := h.i6 r hr; rwa [hB] at this)
      refine fin_le_of_eq _ _ _ _ _ ?_ hA key
      rw [hA, if_neg hBe, hB]
    · by_cases hc : r = e ∧ e ∉ P
      · obtain ⟨hr1, heP⟩ := hc
        subst hr1
        refine fin_le_of_eq _ _ _ _ _ ?_ (if_neg hrd) (h.i6 r hr)
        rw [if_neg hrd, if_pos (And.intro rfl heP), life_output]
      · refine fin_le_of_eq _ _ _ _ _ ?_ (if_neg hrd) (h.i6 r hr)
        rw [if_neg hrd, if_neg hc]
  · exact h.i7
  · exact h.i8

theorem InvS.init' (hXP : ∀ t, X t ∈ P) {s : St K n ι ω} {bk : Bk K τ ω ι n} {cost : ℕ}
    (h : InvS P X q s0 s bk cost) (r : ι) (hr : r ∉ P) :
    InvS P X q s0
        { s with v := fun r' j => if r' = r then 0 else s.v r' j }
        { W := fun r' t => if r' = r then 0 else bk.W r' t
          A := fun r' => if r' = r then ⊤ else bk.A r'
          B := fun r' => if r' = r then ⊥ else bk.B r'
          dep := fun r' => if r' = r then false else bk.dep r'
          lc := fun r' => if r' = r then 0 else bk.lc r'
          closed := ⟨bk.W r, s.v r, bk.A r, bk.B r, bk.lc r⟩ :: bk.closed } cost := by
  have hXr : ∀ t, X t ≠ r := fun t hh => hr (hh ▸ hXP t)
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · intro t j
    have h1 := h.i1 t j
    have hterm : ∀ r' : ι, (if r' = r then (0 : K) else bk.W r' t) * (if r' = r then 0 else s.v r' j) =
        bk.W r' t * s.v r' j - (if r' = r then bk.W r' t * s.v r' j else 0) := by
      intro r'; by_cases hh : r' = r <;> simp [hh]
    simp only [hXr t, if_false, List.map_cons, List.sum_cons, hterm, Finset.sum_sub_distrib,
      Finset.sum_ite_eq', Finset.mem_univ, if_true]
    linear_combination h1
  · intro r' hr' t hW
    by_cases hh : r' = r
    · simp [hh] at hW
    · exact h.i2 r' hr' t (by simpa [hh] using hW)
  · exact h.i2'
  · intro r' hr' hdep
    by_cases hh : r' = r
    · funext t; simp [hh]
    · funext t
      have := congrFun (h.i3 r' hr' (by simpa [hh] using hdep)) t
      simp [hh, this]
  · intro r' hr' hdep
    by_cases hh : r' = r
    · simp [hh]
    · simpa [hh] using h.i3b r' hr' (by simpa [hh] using hdep)
  · intro r' hr' t hW
    by_cases hh : r' = r
    · simp [hh] at hW
    · simpa [hh] using h.i4 r' hr' t (by simpa [hh] using hW)
  · intro r' hr'
    by_cases hh : r' = r
    · subst hh
      have e1 : (if r' = r' then (⊤ : Chart n) else bk.A r') ⊔ (if r' = r' then (⊥ : Chart n) else bk.B r') ⊔
          s.ch r' = ⊤ := by simp
      refine fin_le_of_eq' _ _ _ _ _ 0 e1 (if_pos rfl) (by simp) ?_
      simp
    · refine fin_le_of_eq' _ _ _ _ _ _ ?_ (if_neg hh) (by simp [hh]) (h.i6 r' hr')
      dsimp only
      rw [if_neg hh, if_neg hh]
  · intro ρ hρ
    rcases List.mem_cons.1 hρ with rfl | hρ
    · exact ⟨h.i4 r hr, le_trans (Submodule.finrank_mono le_sup_left) (h.i6 r hr)⟩
    · exact h.i7 ρ hρ
  · have h8 := h.i8
    simp only [List.map_cons, List.sum_cons]
    have hsum := sum_ite_zero_add (univ.filter (· ∉ P)) bk.lc r (by simpa using hr)
    omega

theorem InvS.down (hXP : ∀ t, X t ∈ P) {s : St K n ι ω} {bk : Bk K τ ω ι n} {cost : ℕ}
    (h : InvS P X q s0 s bk cost) (r : ι) (D : Chart n) (hr : r ∉ P) (hD : D ≤ s.ch r) :
    InvS P X q s0 { s with ch := fun r' => if r' = r then D else s.ch r' } bk cost := by
  have hXr : ∀ t, X t ≠ r := fun t hh => hr (hh ▸ hXP t)
  refine ⟨h.i1, ?_, ?_, h.i3, h.i3b, h.i4, ?_, h.i7, h.i8⟩
  · intro r' hr' t hW
    have hh : r' ≠ r := fun e => hr (e ▸ hr')
    simpa [hh] using h.i2 r' hr' t hW
  · intro t; simpa [hXr t] using h.i2' t
  · intro r' hr'
    by_cases hh : r' = r
    · subst hh
      refine le_trans (Submodule.finrank_mono ?_) (h.i6 r' hr')
      exact sup_le_sup_left (by show (if r' = r' then D else s.ch r') ≤ s.ch r'; simpa using hD) _
    · refine fin_le_of_eq _ _ _ _ _ ?_ (rfl) (h.i6 r' hr')
      dsimp only
      rw [if_neg hh]

theorem InvS.upOwn (hXP : ∀ t, X t ∈ P) {s : St K n ι ω} {bk : Bk K τ ω ι n} {cost : ℕ}
    (h : InvS P X q s0 s bk cost) (r : ι) (D : Chart n) (hr : r ∉ P) (hD : s.ch r ≤ D) :
    InvS P X q s0 { s with ch := fun r' => if r' = r then D else s.ch r' }
      { bk with lc := fun r' =>
          if r' = r then bk.lc r + (finrank (ZMod 2) D - finrank (ZMod 2) (s.ch r)) else bk.lc r' }
      (cost + (finrank (ZMod 2) D - finrank (ZMod 2) (s.ch r))) := by
  have hXr : ∀ t, X t ≠ r := fun t hh => hr (hh ▸ hXP t)
  refine ⟨h.i1, ?_, ?_, h.i3, h.i3b, h.i4, ?_, h.i7, ?_⟩
  · intro r' hr' t hW
    have hh : r' ≠ r := fun e => hr (e ▸ hr')
    simpa [hh] using h.i2 r' hr' t hW
  · intro t; simpa [hXr t] using h.i2' t
  · intro r' hr'
    by_cases hh : r' = r
    · subst hh
      have h1 := life_up (bk.A r') (bk.B r') (s.ch r') D hD
      have h2 := h.i6 r' hr'
      have h3 : finrank (ZMod 2) (s.ch r') ≤ finrank (ZMod 2) D := Submodule.finrank_mono hD
      refine fin_le_of_eq' _ (bk.A r' ⊔ bk.B r' ⊔ D) _ (bk.A r') _
        (bk.lc r' + (finrank (ZMod 2) D - finrank (ZMod 2) (s.ch r'))) (by simp) rfl (by simp) ?_
      omega
    · refine fin_le_of_eq' _ _ _ _ _ _ ?_ rfl (by dsimp only; rw [if_neg hh]) (h.i6 r' hr')
      dsimp only
      rw [if_neg hh]
  · have h8 := h.i8
    have hterm : ∀ x : ι, (if x = r then bk.lc r + (finrank (ZMod 2) D - finrank (ZMod 2) (s.ch r))
        else bk.lc x) = bk.lc x + (if x = r then (finrank (ZMod 2) D - finrank (ZMod 2) (s.ch r)) else 0) := by
      intro x; by_cases hh : x = r
      · subst hh; simp
      · simp [hh]
    dsimp only
    have e : ∑ x ∈ univ.filter (· ∉ P), (if x = r then bk.lc r + (finrank (ZMod 2) D - finrank (ZMod 2) (s.ch r))
        else bk.lc x) = ∑ x ∈ univ.filter (· ∉ P), bk.lc x +
          (finrank (ZMod 2) D - finrank (ZMod 2) (s.ch r)) := by
      simp only [hterm, Finset.sum_add_distrib, Finset.sum_ite_eq', Finset.mem_filter, Finset.mem_univ,
        true_and, if_pos hr]
    simp only [e]
    omega

theorem InvS.upPub (hXP : ∀ t, X t ∈ P) {s : St K n ι ω} {bk : Bk K τ ω ι n} {cost : ℕ}
    (h : InvS P X q s0 s bk cost) (r : ι) (D : Chart n) (hr : r ∈ P) (hD : s.ch r ≤ D) :
    InvS P X q s0 { s with ch := fun r' => if r' = r then D else s.ch r' } bk cost := by
  refine ⟨h.i1, ?_, ?_, h.i3, h.i3b, h.i4, ?_, h.i7, h.i8⟩
  · intro r' hr' t hW
    by_cases hh : r' = r
    · subst hh; simpa using hD (h.i2 r' hr' t hW)
    · simpa [hh] using h.i2 r' hr' t hW
  · intro t
    by_cases hh : X t = r
    · have h1 : q t ∈ s.ch r := hh ▸ h.i2' t
      simpa [hh] using hD h1
    · simpa [hh] using h.i2' t
  · intro r' hr'
    have hh : r' ≠ r := fun e => hr' (e ▸ hr)
    refine fin_le_of_eq _ _ _ _ _ ?_ (rfl) (h.i6 r' hr')
    dsimp only
    rw [if_neg hh]

theorem invS_of_run (hXP : ∀ t, X t ∈ P) (hq : ∀ t, q t ∈ s0.ch (X t))
    {s : St K n ι ω} {bk : Bk K τ ω ι n} {cost : ℕ}
    (hrun : ARun0 P X s0 s bk cost) : InvS P X q s0 s bk cost := by
  induction hrun with
  | refl => exact InvS.refl P X q s0 hq
  | add d e l hne hch hgtd _ ih => exact InvS.add P X q s0 hXP ih d e l hne hch hgtd
  | init r hr _ ih => exact InvS.init' P X q s0 hXP ih r hr
  | down r D hr hD _ ih => exact InvS.down P X q s0 hXP ih r D hr hD
  | upOwn r D hr hD _ ih => exact InvS.upOwn P X q s0 hXP ih r D hr hD
  | upPub r D hr hD _ ih => exact InvS.upPub P X q s0 hXP ih r D hr hD

lemma finalRows_ok0 {s : St K n ι ω} {bk : Bk K τ ω ι n} {cost : ℕ}
    (h : InvS P X q s0 s bk cost) : ∀ ρ ∈ finalRows P s bk, Ok0 q ρ := by
  intro ρ hρ
  rcases List.mem_append.1 hρ with hρ | hρ
  · exact h.i7 ρ hρ
  · obtain ⟨r, hr, rfl⟩ := List.mem_map.1 hρ
    have hr' : r ∉ P := by simpa using (Finset.mem_toList.1 hr)
    exact ⟨h.i4 r hr', le_trans (Submodule.finrank_mono le_sup_left) (h.i6 r hr')⟩

lemma finalRows_cost0 {s : St K n ι ω} {bk : Bk K τ ω ι n} {cost : ℕ}
    (h : InvS P X q s0 s bk cost) : ((finalRows P s bk).map fun ρ => ρ.lc).sum = cost := by
  rw [h.i8]
  simp only [finalRows, List.map_append, List.sum_append, List.map_map, Function.comp_def,
    Finset.sum_map_toList]
  ring

end Inv

/-! ## Forests (= acyclic parent maps) -/

/-- A forest: `node k ch rest` is the tree with root `k` and child forest `ch`, followed by the
sibling forest `rest`.  (A parent map without cycles is exactly such a forest.) -/
inductive Fo (α : Type*) : Type _
  | leaf : Fo α
  | node : α → Fo α → Fo α → Fo α

namespace Fo
variable {α : Type*}

def labels : Fo α → List α
  | leaf => []
  | node k ch rest => k :: (labels ch ++ labels rest)

def roots : Fo α → List α
  | leaf => []
  | node k _ rest => k :: roots rest

def nonroots : Fo α → List α
  | leaf => []
  | node _ ch rest => labels ch ++ nonroots rest

lemma labels_sum {M : Type*} [AddCommMonoid M] (g : α → M) (f : Fo α) :
    ((labels f).map g).sum = ((roots f).map g).sum + ((nonroots f).map g).sum := by
  induction f with
  | leaf => simp [labels, roots, nonroots]
  | node k ch rest ihch ihrest =>
    simp only [labels, roots, nonroots, List.map_cons, List.map_append, List.sum_cons,
      List.sum_append] at ihrest ⊢
    rw [ihrest]
    abel

end Fo

section Forest
variable {K : Type*} [Field K] {τ ω : Type*} {n : ℕ}
open Fo

/-- meet of the intake charts `A_k` over a forest -/
def asub : Fo (Row K τ ω n) → Chart n
  | leaf => ⊤
  | node k ch rest => (k.A ⊓ asub ch) ⊓ asub rest

/-- the attachment condition `A_{p(k)} ⊆ B_k`: the parent's intake meet lies in the child's output join -/
def wf : Fo (Row K τ ω n) → Prop
  | leaf => True
  | node k ch rest => (∀ c ∈ roots ch, k.A ≤ c.B) ∧ wf ch ∧ wf rest

def lcSum (f : Fo (Row K τ ω n)) : ℕ := ((labels f).map Row.lc).sum

lemma lcSum_cons (k : Row K τ ω n) (ch rest : Fo (Row K τ ω n)) :
    lcSum (node k ch rest) = k.lc + (lcSum ch + lcSum rest) := by
  simp [lcSum, labels, List.sum_append]

lemma row_step (A B Z : Chart n) (lc : ℕ) (h : finrank (ZMod 2) (A ⊔ B : Chart n) ≤ finrank (ZMod 2) A + lc)
    (hZ : Z ≤ B) : finrank (ZMod 2) Z ≤ finrank (ZMod 2) (Z ⊓ A : Chart n) + lc := by
  have e1 := Submodule.finrank_sup_add_finrank_inf_eq A B
  have e2 := Submodule.finrank_sup_add_finrank_inf_eq Z (A ⊓ B)
  have e3 : (Z ⊓ (A ⊓ B) : Chart n) = Z ⊓ A := by
    ext x; simp only [Submodule.mem_inf]
    constructor
    · rintro ⟨a, c, _⟩; exact ⟨a, c⟩
    · rintro ⟨a, c⟩; exact ⟨a, c, hZ a⟩
  have e4 : finrank (ZMod 2) (Z ⊔ (A ⊓ B) : Chart n) ≤ finrank (ZMod 2) B :=
    Submodule.finrank_mono (sup_le hZ inf_le_right)
  rw [e3] at e2
  omega

/-- the forest bound: `Z` inside every root's output join costs at most the forest's lifetime cost -/
theorem forest_bound (f : Fo (Row K τ ω n))
    (hwf : wf f) (hc : ∀ ρ ∈ labels f, finrank (ZMod 2) (ρ.A ⊔ ρ.B : Chart n) ≤ finrank (ZMod 2) ρ.A + ρ.lc) :
    ∀ Z : Chart n, (∀ c ∈ roots f, Z ≤ c.B) →
      finrank (ZMod 2) Z ≤ finrank (ZMod 2) (Z ⊓ asub f : Chart n) + lcSum f := by
  induction f with
  | leaf =>
    intro Z _
    have h1 : (Z ⊓ asub (leaf : Fo (Row K τ ω n)) : Chart n) = Z := by
      show Z ⊓ ⊤ = Z
      exact inf_top_eq Z
    rw [h1]; omega
  | node k ch rest ihch ihrest =>
    obtain ⟨hA, hwch, hwrest⟩ := hwf
    intro Z hZ
    have hZk : Z ≤ k.B := hZ k (by simp [roots])
    have hZrest : ∀ c ∈ roots rest, Z ≤ c.B := fun c hc' => hZ c (by simp [roots, hc'])
    have hck := hc k (by simp [labels])
    have hcch : ∀ ρ ∈ labels ch, _ := fun ρ hρ => hc ρ (by simp [labels, hρ])
    have hcrest : ∀ ρ ∈ labels rest, _ := fun ρ hρ => hc ρ (by simp [labels, hρ])
    have s1 := row_step k.A k.B Z k.lc hck hZk
    have s2 := ihch hwch hcch (Z ⊓ k.A) (fun c hc' => le_trans inf_le_right (hA c hc'))
    have s3 := ihrest hwrest hcrest ((Z ⊓ k.A) ⊓ asub ch)
      (fun c hc' => le_trans (le_trans inf_le_left inf_le_left) (hZrest c hc'))
    have e : (Z ⊓ k.A) ⊓ asub ch ⊓ asub rest = Z ⊓ (k.A ⊓ asub ch ⊓ asub rest) := by
      simp only [inf_assoc]
    rw [e] at s3
    rw [lcSum_cons]
    have g : (Z ⊓ asub (node k ch rest) : Chart n) = Z ⊓ (k.A ⊓ asub ch ⊓ asub rest) := rfl
    rw [g]
    omega

variable [Fintype τ]

/-- price of a row with weights on `B` and effective content cold at `Ast` -/
theorem price_le_star (q : τ → Fin n → ZMod 2) (w e : τ → K) (B Ast : Chart n)
    (h1 : ∀ t, w t ≠ 0 → q t ∈ B) (h2 : ∀ u, e u ≠ 0 → ∀ a ∈ Ast, a ⬝ᵥ q u = 0) :
    price q ⟨w, e⟩ ≤ finrank (ZMod 2) B - finrank (ZMod 2) (B ⊓ Ast : Chart n) := by
  classical
  unfold price
  set lD : {t // w t ≠ 0} → Fin n → ZMod 2 := fun t => q t.1 with hlD
  set lS : {s // e s ≠ 0} → Fin n → ZMod 2 := fun s => q s.1 with hlS
  have hM : Submodule.span (ZMod 2) (Set.range lD) ≤ B := by
    apply Submodule.span_le.2
    rintro _ ⟨t, rfl⟩; exact h1 t.1 t.2
  have hL : B ⊓ Ast ≤ perp (Submodule.span (ZMod 2) (Set.range lS)) := by
    rw [le_perp_iff]
    apply Submodule.span_le.2
    rintro _ ⟨s, rfl⟩
    show q s.1 ∈ perp (B ⊓ Ast)
    rw [mem_perp]
    intro y hy
    exact h2 s.1 s.2 y (Submodule.mem_inf.1 hy).2
  exact (exact_price lD lS).2
    (show finrank (ZMod 2) B - finrank (ZMod 2) (B ⊓ Ast : Chart n) ∈ PriceSet lD lS from
      ⟨B, B ⊓ Ast, hM, inf_le_left, hL, rfl⟩)

/-- roots are cold at their subtree meet `A_k ⊓ asub ch` -/
def cold (xs ys : τ → ω) (Fy : τ → τ → K) (q : τ → Fin n → ZMod 2) : Fo (Row K τ ω n) → Prop
  | leaf => True
  | node k ch rest => (∀ u, eff xs ys Fy k.val u ≠ 0 → ∀ a ∈ (k.A ⊓ asub ch : Chart n),
        a ⬝ᵥ q u = 0) ∧ cold xs ys Fy q rest

/-- root prices sum to at most the total lifetime cost -/
theorem price_sum_le (xs ys : τ → ω) (Fy : τ → τ → K) (q : τ → Fin n → ZMod 2)
    (f : Fo (Row K τ ω n)) (hwf : wf f) (hok : ∀ ρ ∈ labels f, Ok0 q ρ)
    (hcold : cold xs ys Fy q f) :
    (((roots f).map fun ρ => price q ⟨ρ.w, eff xs ys Fy ρ.val⟩)).sum ≤ lcSum f := by
  induction f with
  | leaf => simp [roots, lcSum, labels]
  | node k ch rest ihch ihrest =>
    obtain ⟨hA, hwch, hwrest⟩ := hwf
    obtain ⟨hck, hcrest⟩ := hcold
    have hokrest : ∀ ρ ∈ labels rest, Ok0 q ρ := fun ρ hρ => hok ρ (by simp [labels, hρ])
    have ih := ihrest hwrest hokrest hcrest
    have hk := hok k (by simp [labels])
    -- the tree bound for the root `k`
    have hwt : wf (node k ch (leaf : Fo (Row K τ ω n))) := ⟨hA, hwch, trivial⟩
    have hct : ∀ ρ ∈ labels (node k ch (leaf : Fo (Row K τ ω n))),
        finrank (ZMod 2) (ρ.A ⊔ ρ.B : Chart n) ≤ finrank (ZMod 2) ρ.A + ρ.lc := by
      intro ρ hρ
      have h1 : ρ ∈ k :: labels ch := by simpa [labels] using hρ
      refine (hok ρ ?_).2
      rcases List.mem_cons.1 h1 with h | h
      · simp [labels, h]
      · simp [labels, h]
    have tb := forest_bound _ hwt hct k.B (by simp [roots])
    have g : (k.B ⊓ asub (node k ch (leaf : Fo (Row K τ ω n))) : Chart n) = k.B ⊓ (k.A ⊓ asub ch) := by
      show k.B ⊓ (k.A ⊓ asub ch ⊓ ⊤) = _
      rw [inf_top_eq]
    have hg : finrank (ZMod 2) (k.B ⊓ asub (node k ch (leaf : Fo (Row K τ ω n))) : Chart n) =
        finrank (ZMod 2) (k.B ⊓ (k.A ⊓ asub ch) : Chart n) :=
      congrArg (fun m : Chart n => finrank (ZMod 2) m) g
    have hlc0 : lcSum (leaf : Fo (Row K τ ω n)) = 0 := by simp [lcSum, labels]
    have hlc := lcSum_cons k ch (leaf : Fo (Row K τ ω n))
    have pk := price_le_star q k.w (eff xs ys Fy k.val) k.B (k.A ⊓ asub ch) hk.1 hck
    simp only [roots, List.map_cons, List.sum_cons]
    rw [lcSum_cons]
    omega

end Forest

/-! ## The decoder identity (no cold content needed) and THEOREM CT -/
section Main
variable {K : Type*} [Field K] {τ ι ω : Type*} {n : ℕ} [Fintype τ] [DecidableEq ι] [Fintype ι]
variable (xs ys : τ → ω) (Fy : τ → τ → K) (q : τ → Fin n → ZMod 2)
variable (P : Finset ι) (X : τ → ι) (s0 : St K n ι ω)

/-- the FA rows of ALL lifetimes decode the odd receipts (the identity does not use coldness). -/
theorem ident0 (hXP : ∀ t, X t ∈ P) (hXinj : Function.Injective X)
    {s : St K n ι ω} {bk : Bk K τ ω ι n} {cost : ℕ}
    (h : InvS P X q s0 s bk cost)
    (hfx : ∀ r ∈ P, ∀ u, s.v r (xs u) = if r = X u then 1 else 0)
    (hfy : ∀ r ∈ P, (∀ u, r ≠ X u) → ∀ u, s.v r (ys u) ≠ 0 → ∀ a ∈ s.ch r, a ⬝ᵥ q u = 0)
    (hfyX : ∀ u u', s.v (X u) (ys u') = Fy u u')
    (hbal : ∀ t u, s.v (X t) (xs u) = s0.v (X t) (xs u)) :
    IsDec q (fun t u => s.v (X t) (ys u) - s0.v (X t) (ys u))
      ((finalRows P s bk).map fun ρ => (⟨ρ.w, eff xs ys Fy ρ.val⟩ : DRow K τ)) := by
  classical
  intro t u' hQ
  have hx : ∀ u, bk.W (X u) t = -(((finalRows P s bk).map fun ρ => ρ.w t * ρ.val (xs u)).sum) := by
    intro u
    have h1 := h.i1 t (xs u)
    rw [hbal t u, sub_self, finalRows_sum P t (xs u)] at h1
    have h2 : ∑ r ∈ P, bk.W r t * s.v r (xs u) = bk.W (X u) t := by
      rw [Finset.sum_congr rfl (fun r hr => by rw [hfx r hr u])]
      simp [hXP u]
    rw [h2] at h1
    exact eq_neg_of_add_eq_zero_left h1.symm
  have hy : ∑ r ∈ P, bk.W r t * s.v r (ys u') = ∑ u, bk.W (X u) t * Fy u u' := by
    have hsub : (univ.image X) ⊆ P := by
      intro r hr; obtain ⟨u, -, rfl⟩ := Finset.mem_image.1 hr; exact hXP u
    rw [← Finset.sum_subset hsub, Finset.sum_image (fun a _ b _ hab => hXinj hab)]
    · exact Finset.sum_congr rfl (fun u _ => by rw [hfyX])
    · intro r hrP hrn
      have hrX : ∀ u, r ≠ X u := fun u hu => hrn (Finset.mem_image.2 ⟨u, mem_univ _, hu.symm⟩)
      by_contra hne
      have hW : bk.W r t ≠ 0 := fun hh => hne (by rw [hh, zero_mul])
      have hv : s.v r (ys u') ≠ 0 := fun hh => hne (by rw [hh, mul_zero])
      have := hfy r hrP hrX u' hv (q t) (h.i2 r hrP t hW)
      rw [this] at hQ
      exact zero_ne_one hQ
  have h2 := h.i1 t (ys u')
  rw [finalRows_sum P t (ys u'), hy] at h2
  have e3 : ∑ u, bk.W (X u) t * Fy u u' =
      -∑ u, ((finalRows P s bk).map fun ρ => ρ.w t * ρ.val (xs u)).sum * Fy u u' := by
    rw [← Finset.sum_neg_distrib]
    apply Finset.sum_congr rfl; intro u _; rw [hx u]; ring
  simp only [List.map_map, Function.comp_def]
  have := list_sum_eff xs ys Fy (finalRows P s bk) t u'
  rw [this, h2, e3]; ring

/-- THEOREM CT (carrier-tree separation).  `ARun0` (no `hcold`; every owned lifetime GTD).  A forest
`f` whose labels are the lifetimes (`hperm`), with `A_{p(k)} ⊆ B_k` (`wf`), zero weight on every
non-root (`hz`), and every root's effective final content cold at its subtree meet (`cold`):
the root rows form a decoder of the odd receipts with total price ≤ cost. -/
theorem carrier_tree_decoder (hXP : ∀ t, X t ∈ P) (hXinj : Function.Injective X)
    (hq : ∀ t, q t ∈ s0.ch (X t))
    {s : St K n ι ω} {bk : Bk K τ ω ι n} {cost : ℕ}
    (hrun : ARun0 P X s0 s bk cost)
    (hfx : ∀ r ∈ P, ∀ u, s.v r (xs u) = if r = X u then 1 else 0)
    (hfy : ∀ r ∈ P, (∀ u, r ≠ X u) → ∀ u, s.v r (ys u) ≠ 0 → ∀ a ∈ s.ch r, a ⬝ᵥ q u = 0)
    (hfyX : ∀ u u', s.v (X u) (ys u') = Fy u u')
    (hbal : ∀ t u, s.v (X t) (xs u) = s0.v (X t) (xs u))
    (f : Fo (Row K τ ω n)) (hperm : (Fo.labels f).Perm (finalRows P s bk))
    (hwf : wf f) (hz : ∀ ρ ∈ Fo.nonroots f, ρ.w = 0) (hcold : cold xs ys Fy q f) :
    ∃ rows : List (DRow K τ),
      IsDec q (fun t u => s.v (X t) (ys u) - s0.v (X t) (ys u)) rows ∧
      (rows.map (price q)).sum ≤ cost := by
  classical
  have h := invS_of_run P X q s0 hXP hq hrun
  have hok0 := finalRows_ok0 P X q s0 h
  have hcost := finalRows_cost0 P X q s0 h
  have hok : ∀ ρ ∈ Fo.labels f, Ok0 q ρ := fun ρ hρ => hok0 ρ (hperm.mem_iff.1 hρ)
  have ident := ident0 xs ys Fy q P X s0 hXP hXinj h hfx hfy hfyX hbal
  refine ⟨(Fo.roots f).map fun ρ => (⟨ρ.w, eff xs ys Fy ρ.val⟩ : DRow K τ), ?_, ?_⟩
  · intro t u hQ
    have e1 := ident t u hQ
    rw [← e1]
    simp only [List.map_map, Function.comp_def]
    have hs := (hperm.symm.map fun ρ : Row K τ ω n => ρ.w t * eff xs ys Fy ρ.val u).sum_eq
    have hl := Fo.labels_sum (fun ρ : Row K τ ω n => ρ.w t * eff xs ys Fy ρ.val u) f
    have hnr : ((Fo.nonroots f).map fun ρ : Row K τ ω n => ρ.w t * eff xs ys Fy ρ.val u).sum = 0 := by
      apply List.sum_eq_zero
      intro a ha
      obtain ⟨ρ, hρ, rfl⟩ := List.mem_map.1 ha
      simp [hz ρ hρ]
    rw [hnr, add_zero] at hl
    rw [← hl]
    exact hs.symm
  · simp only [List.map_map, Function.comp_def]
    have h1 := price_sum_le xs ys Fy q f hwf hok hcold
    have h2 : lcSum f = cost := by
      unfold lcSum
      rw [← hcost]
      exact (hperm.map Row.lc).sum_eq
    exact h2 ▸ h1

/-- R ≥ m(Q) on carrier-tree runs. -/
theorem mass_le_R_ct (hXP : ∀ t, X t ∈ P) (hXinj : Function.Injective X)
    (hq : ∀ t, q t ∈ s0.ch (X t))
    {s : St K n ι ω} {bk : Bk K τ ω ι n} {cost : ℕ}
    (hrun : ARun0 P X s0 s bk cost)
    (hfx : ∀ r ∈ P, ∀ u, s.v r (xs u) = if r = X u then 1 else 0)
    (hfy : ∀ r ∈ P, (∀ u, r ≠ X u) → ∀ u, s.v r (ys u) ≠ 0 → ∀ a ∈ s.ch r, a ⬝ᵥ q u = 0)
    (hfyX : ∀ u u', s.v (X u) (ys u') = Fy u u')
    (hbal : ∀ t u, s.v (X t) (xs u) = s0.v (X t) (xs u))
    (f : Fo (Row K τ ω n)) (hperm : (Fo.labels f).Perm (finalRows P s bk))
    (hwf : wf f) (hz : ∀ ρ ∈ Fo.nonroots f, ρ.w = 0) (hcold : cold xs ys Fy q f) :
    mass q (fun t u => s.v (X t) (ys u) - s0.v (X t) (ys u)) ≤ cost := by
  obtain ⟨rows, hd, hle⟩ := carrier_tree_decoder xs ys Fy q P X s0 hXP hXinj hq hrun hfx hfy hfyX
    hbal f hperm hwf hz hcold
  exact le_trans (mass_le hd) hle

/-- COROLLARY: `Wall N` (explicit hypothesis, e.g. `N = 56` at Q96) gives `R ≥ N` on carrier-tree runs. -/
theorem R_ge_of_wall_ct (N : ℕ) (hXP : ∀ t, X t ∈ P) (hXinj : Function.Injective X)
    (hq : ∀ t, q t ∈ s0.ch (X t))
    {s : St K n ι ω} {bk : Bk K τ ω ι n} {cost : ℕ}
    (hrun : ARun0 P X s0 s bk cost)
    (hfx : ∀ r ∈ P, ∀ u, s.v r (xs u) = if r = X u then 1 else 0)
    (hfy : ∀ r ∈ P, (∀ u, r ≠ X u) → ∀ u, s.v r (ys u) ≠ 0 → ∀ a ∈ s.ch r, a ⬝ᵥ q u = 0)
    (hfyX : ∀ u u', s.v (X u) (ys u') = Fy u u')
    (hbal : ∀ t u, s.v (X t) (xs u) = s0.v (X t) (xs u))
    (f : Fo (Row K τ ω n)) (hperm : (Fo.labels f).Perm (finalRows P s bk))
    (hwf : wf f) (hz : ∀ ρ ∈ Fo.nonroots f, ρ.w = 0) (hcold : cold xs ys Fy q f)
    (hwall : Wall q (fun t u => s.v (X t) (ys u) - s0.v (X t) (ys u)) N) : N ≤ cost := by
  obtain ⟨rows, hd, hle⟩ := carrier_tree_decoder xs ys Fy q P X s0 hXP hXinj hq hrun hfx hfy hfyX
    hbal f hperm hwf hz hcold
  exact le_trans (hwall rows hd) hle

end Main

/-! ## Non-vacuity: FLUSHROW's pinned hot-carry witness (one port, `q = 1`, N = 1).
Registers: `0 = X`, `1 = Y`, `2 = H` public (`H` the helper with token `h`); `3 = O`, `4 = O'` owned.
Symbols: `x = 0`, `y = 1`, `h = 2`.  `O'` copies `h` at chart `⊥` and climbs to `⟨q⟩ = ⊤` (cost 1);
`H` absorbs `y` at `⊥` and climbs free; `O` (born at `⊤`) takes `h + y` from `H` (HOT intake),
subtracts `O'` (→ `y`), delivers `−y` into `X` and restores `H := h`.
`O` is a nonzero-weight lifetime with a hot intake (outside class F, so outside `FutureAttr`);
`O'` is the zero-weight carrier: forest `node O (node O' leaf leaf) leaf`, `A* = ⊥`, price 1 = cost 1. -/
namespace Toy2

def Pub : Finset (Fin 5) := {0, 1, 2}
def Xr : Unit → Fin 5 := fun _ => 0
def xsym : Unit → Fin 3 := fun _ => 0
def ysym : Unit → Fin 3 := fun _ => 1
def Fy1 : Unit → Unit → ℚ := fun _ _ => -1
def q1 : Unit → Fin 1 → ZMod 2 := fun _ _ => 1
def st0 : St ℚ 1 (Fin 5) (Fin 3) where
  ch := fun r => if r = 0 ∨ r = 3 then ⊤ else ⊥
  v := fun r j => if r = 0 then (if j = 0 then 1 else 0)
    else if r = 1 then (if j = 1 then 1 else 0)
    else if r = 2 then (if j = 2 then 1 else 0) else 0

/-- the abstract part: from a few evaluated facts about the final state, all CT hypotheses hold
(with a genuine two-node tree), the root's own intake is hot, and `mass ≤ 1`. -/
theorem toy_of_facts (s : St ℚ 1 (Fin 5) (Fin 3)) (bk : Bk ℚ Unit (Fin 3) (Fin 5) 1) (cost : ℕ)
    (hrun : ARun0 Pub Xr st0 s bk cost) (hcost : cost = 1)
    (h1 : s.v 0 0 = 1) (h2 : s.v 1 0 = 0) (h3 : s.v 2 0 = 0) (h4 : s.v 0 1 = -1)
    (h5 : s.v 2 1 = 0) (h6 : s.ch 1 = ⊥) (h7 : bk.closed = []) (h8 : ∀ t, bk.W 4 t = 0)
    (h9 : bk.A 3 = ⊤) (h10 : bk.B 4 = ⊤) (h11 : bk.A 4 = ⊥) (h12 : s.v 3 1 = 1) (h13 : s.v 3 0 = 0) :
    ∃ f : Fo (Row ℚ Unit (Fin 3) 1),
      (Fo.labels f).Perm (finalRows Pub s bk) ∧ wf f ∧ (∀ ρ ∈ Fo.nonroots f, ρ.w = 0) ∧
      cold xsym ysym Fy1 q1 f ∧
      (∃ ρ ∈ Fo.roots f, ¬ ∀ u, eff xsym ysym Fy1 ρ.val u ≠ 0 → ∀ a ∈ ρ.A, a ⬝ᵥ q1 u = 0) ∧
      mass q1 (fun t u => s.v (Xr t) (ysym u) - st0.v (Xr t) (ysym u)) ≤ 1 := by
  classical
  let ρ3 : Row ℚ Unit (Fin 3) 1 := ⟨bk.W 3, s.v 3, bk.A 3, bk.B 3, bk.lc 3⟩
  let ρ4 : Row ℚ Unit (Fin 3) 1 := ⟨bk.W 4, s.v 4, bk.A 4, bk.B 4, bk.lc 4⟩
  let f : Fo (Row ℚ Unit (Fin 3) 1) := Fo.node ρ3 (Fo.node ρ4 Fo.leaf Fo.leaf) Fo.leaf
  have hperm : (Fo.labels f).Perm (finalRows Pub s bk) := by
    have hS : ((univ.filter (· ∉ Pub)).toList).Perm [3, 4] := by
      rw [List.perm_ext_iff_of_nodup (Finset.nodup_toList _) (by decide)]
      intro a
      simp only [Finset.mem_toList, Finset.mem_filter, Finset.mem_univ, true_and]
      fin_cases a <;> simp [Pub]
    have := (hS.map fun r => (⟨bk.W r, s.v r, bk.A r, bk.B r, bk.lc r⟩ : Row ℚ Unit (Fin 3) 1)).symm
    simp only [finalRows, h7, List.nil_append]
    simpa [f, Fo.labels, ρ3, ρ4] using this
  have hz : ∀ ρ ∈ Fo.nonroots f, ρ.w = 0 := by
    intro ρ hρ
    have hρ' : ρ = ρ4 := by simpa [f, Fo.nonroots, Fo.labels] using hρ
    rw [hρ']
    funext t; exact h8 t
  have hwf : wf f := by
    have hw1 : ∀ c ∈ Fo.roots (Fo.node ρ4 Fo.leaf Fo.leaf), ρ3.A ≤ c.B := by
      intro c hc
      have hc' : c = ρ4 := by simpa [Fo.roots] using hc
      rw [hc']
      show bk.A 3 ≤ bk.B 4
      rw [h9, h10]
    have hw2 : ∀ c ∈ Fo.roots (Fo.leaf : Fo (Row ℚ Unit (Fin 3) 1)), ρ4.A ≤ c.B := by
      intro c hc; simp [Fo.roots] at hc
    exact And.intro hw1 (And.intro (And.intro hw2 (And.intro trivial trivial)) trivial)
  have hcold : cold xsym ysym Fy1 q1 f := by
    have hc1 : ∀ u, eff xsym ysym Fy1 ρ3.val u ≠ 0 → ∀ a ∈ (ρ3.A ⊓ asub (Fo.node ρ4 Fo.leaf Fo.leaf) : Chart 1),
        a ⬝ᵥ q1 u = 0 := by
      intro u _ a ha
      have e : (ρ3.A ⊓ asub (Fo.node ρ4 Fo.leaf Fo.leaf) : Chart 1) = ⊥ := by
        show bk.A 3 ⊓ ((bk.A 4 ⊓ ⊤) ⊓ ⊤) = ⊥
        rw [h11]; simp
      rw [e] at ha
      have : a = 0 := by simpa using ha
      simp [this]
    exact And.intro hc1 trivial
  have hhot : ∃ ρ ∈ Fo.roots f, ¬ ∀ u, eff xsym ysym Fy1 ρ.val u ≠ 0 → ∀ a ∈ ρ.A, a ⬝ᵥ q1 u = 0 := by
    refine ⟨ρ3, by simp [f, Fo.roots], ?_⟩
    intro hh
    have he : eff xsym ysym Fy1 ρ3.val () ≠ 0 := by
      simp [eff, ρ3, xsym, ysym, Fy1, h12, h13]
    have := hh () he (fun _ => 1) (by show (fun _ => (1 : ZMod 2)) ∈ bk.A 3; rw [h9]; trivial)
    simp [q1, dotProduct] at this
  refine ⟨f, hperm, hwf, hz, hcold, hhot, ?_⟩
  refine le_trans (mass_le_R_ct xsym ysym Fy1 q1 Pub Xr st0 ?_ ?_ ?_ hrun ?_ ?_ ?_ ?_ f hperm hwf hz hcold) ?_
  · intro t; simp [Pub, Xr]
  · intro a b _; exact Subsingleton.elim a b
  · intro t; simp [st0, Xr]
  · intro r hr u
    simp only [Pub, Finset.mem_insert, Finset.mem_singleton] at hr
    rcases hr with rfl | rfl | rfl
    · simp [Xr, xsym, h1]
    · simp [Xr, xsym, h2]
    · simp [Xr, xsym, h3]
  · intro r hr hne u hv a ha
    simp only [Pub, Finset.mem_insert, Finset.mem_singleton] at hr
    rcases hr with rfl | rfl | rfl
    · exact absurd rfl (hne ())
    · rw [h6] at ha
      have : a = 0 := by simpa using ha
      simp [this]
    · exact absurd h5 hv
  · intro u u'; simp [Xr, ysym, Fy1, h4]
  · intro t u; simp [st0, Xr, xsym, h1]
  · omega

theorem toy_witness :
    ∃ (s : St ℚ 1 (Fin 5) (Fin 3)) (bk : Bk ℚ Unit (Fin 3) (Fin 5) 1) (cost : ℕ),
      ARun0 Pub Xr st0 s bk cost ∧ cost = 1 ∧
      ∃ f : Fo (Row ℚ Unit (Fin 3) 1),
        (Fo.labels f).Perm (finalRows Pub s bk) ∧ wf f ∧ (∀ ρ ∈ Fo.nonroots f, ρ.w = 0) ∧
        cold xsym ysym Fy1 q1 f ∧
        (∃ ρ ∈ Fo.roots f, ¬ ∀ u, eff xsym ysym Fy1 ρ.val u ≠ 0 → ∀ a ∈ ρ.A, a ⬝ᵥ q1 u = 0) ∧
        mass q1 (fun t u => s.v (Xr t) (ysym u) - st0.v (Xr t) (ysym u)) ≤ 1 := by
  have a1 := ARun0.add (P := Pub) (X := Xr) (s0 := st0) (s := st0) (bk := Bk.init) (cost := 0)
    4 2 (1 : ℚ) (by decide) (by simp [st0]) (fun _ => rfl) ARun0.refl
  have a2 := ARun0.add (P := Pub) (X := Xr) (s0 := st0) 2 1 (1 : ℚ) (by decide) (by simp [st0])
    (fun h => absurd (by decide) h) a1
  have a3 := ARun0.upPub (P := Pub) (X := Xr) (s0 := st0) 2 (⊤ : Chart 1) (by decide) le_top a2
  have a4 := ARun0.upOwn (P := Pub) (X := Xr) (s0 := st0) 4 (⊤ : Chart 1) (by decide) le_top a3
  have a5 := ARun0.add (P := Pub) (X := Xr) (s0 := st0) 3 2 (1 : ℚ) (by decide) (by simp [st0])
    (fun _ => by first | rfl | decide) a4
  have a6 := ARun0.add (P := Pub) (X := Xr) (s0 := st0) 3 4 (-1 : ℚ) (by decide) (by simp [st0])
    (fun _ => by first | rfl | decide) a5
  have a7 := ARun0.add (P := Pub) (X := Xr) (s0 := st0) 0 3 (-1 : ℚ) (by decide) (by simp [st0])
    (fun h => absurd (by decide) h) a6
  have a8 := ARun0.add (P := Pub) (X := Xr) (s0 := st0) 2 3 (-1 : ℚ) (by decide) (by simp [st0])
    (fun h => absurd (by decide) h) a7
  refine ⟨_, _, _, a8, ?hc, toy_of_facts _ _ _ a8 ?hc ?h1 ?h2 ?h3 ?h4 ?h5 ?h6 ?h7 ?h8 ?h9 ?h10 ?h11
    ?h12 ?h13⟩
  case hc =>
    have hb : finrank (ZMod 2) (⊥ : Chart 1) = 0 := finrank_bot (ZMod 2) _
    simp [st0, finrank_top]
    exact (congrArg (fun m => 1 - m) hb).trans rfl
  case h1 => simp [st0]
  case h2 => simp [st0]
  case h3 => simp [st0]
  case h4 => simp [st0]
  case h5 => simp [st0]
  case h6 => simp [st0]
  case h7 => rfl
  case h8 => intro t; simp [st0, tv, Xr, Bk.init]
  case h9 => simp [st0, Pub, Bk.init]
  case h10 => simp [st0, Pub, Bk.init]
  case h11 => simp [st0, Pub, Bk.init]
  case h12 => simp [st0]
  case h13 => simp [st0]

end Toy2

#print axioms invS_of_run
#print axioms forest_bound
#print axioms price_sum_le
#print axioms carrier_tree_decoder
#print axioms mass_le_R_ct
#print axioms R_ge_of_wall_ct
#print axioms Toy2.toy_of_facts
#print axioms Toy2.toy_witness

end CarrierTree
