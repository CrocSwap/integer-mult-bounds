/-
DesignLaws .  See DesignLaws.md.  Structural laws of internal notes section 2 / 4:
 (1) PCL port content law   (2) ONE-READ   (3) HYPERPLANE   (4) RANK-FEED   (5) XCLOSE exactness.
Event model = TokenCancel.St / Ev / step / run / LegalEv (charts := any type, `Submodule K E` for the geometry),
nesting = Annihilator / WholeFloorNest (cited, not needed here).  Kernel only: no sorry, no native_decide.
-/
import Nov15.TokenCancel
import Nov15.Annihilator
import Mathlib.LinearAlgebra.Span.Basic
import Mathlib.LinearAlgebra.Dimension.Finrank
import Mathlib.LinearAlgebra.Dimension.Constructions
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.RingTheory.SimpleModule.Basic
import Mathlib.Tactic.LinearCombination

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace DesignLaws
open TokenCancel Module
open scoped Classical

/-! ## Run bookkeeping -/
section Run
variable {K Reg C : Type*} [Field K] [DecidableEq Reg]

theorem run_append (s : St K Reg C) (l1 l2 : List (Ev K Reg C)) :
    run s (l1 ++ l2) = run (run s l1) l2 := by
  induction l1 generalizing s with
  | nil => rfl
  | cons e es ih => simp [run, ih]

theorem legal_append (z V : C) (s : St K Reg C) (l1 l2 : List (Ev K Reg C)) :
    Legal z V s (l1 ++ l2) ↔ Legal z V s l1 ∧ Legal z V (run s l1) l2 := by
  induction l1 generalizing s with
  | nil => simp [Legal, run]
  | cons e es ih => simp [Legal, run, ih, and_assoc]

/-- every MOVE of register `i` satisfies the relation `R old new`. -/
def MoveRel (R : C → C → Prop) (i : Reg) : St K Reg C → List (Ev K Reg C) → Prop
  | _, [] => True
  | s, e :: es => (match e with
      | .move j c => j = i → ∀ c0, s.loc i = some c0 → R c0 c
      | _ => True) ∧ MoveRel R i (step s e) es

theorem moveRel_append (R : C → C → Prop) (i : Reg) (s : St K Reg C) (l1 l2 : List (Ev K Reg C)) :
    MoveRel R i s (l1 ++ l2) ↔ MoveRel R i s l1 ∧ MoveRel R i (run s l1) l2 := by
  induction l1 generalizing s with
  | nil => simp [MoveRel, run]
  | cons e es ih => simp [MoveRel, run, ih, and_assoc]

/-- a register that is present keeps moving along `R` (reflexive, transitive). -/
theorem loc_rel (z V : C) (R : C → C → Prop) (hrefl : ∀ a, R a a) (htr : ∀ a b c, R a b → R b c → R a c)
    (i : Reg) : ∀ (es : List (Ev K Reg C)) (s : St K Reg C) (a b : C), Legal z V s es → MoveRel R i s es →
      s.loc i = some a → (run s es).loc i = some b → R a b := by
  intro es
  induction es with
  | nil => intro s a b _ _ ha hb; simp [run] at hb; rw [ha] at hb; cases hb; exact hrefl _
  | cons e es ih =>
    intro s a b hL hM ha hb
    simp only [Legal] at hL
    simp only [MoveRel] at hM
    simp only [run] at hb
    have hstep : ∃ a', (step s e).loc i = some a' ∧ R a a' := by
      cases e with
      | born j c =>
        simp only [LegalEv] at hL
        have hne : j ≠ i := by rintro rfl; rw [hL.1] at ha; cases ha
        exact ⟨a, by simp [step, Function.update, hne.symm, ha], hrefl _⟩
      | init j c =>
        simp only [LegalEv] at hL
        have hne : j ≠ i := by rintro rfl; rw [hL.1] at ha; cases ha
        exact ⟨a, by simp [step, Function.update, hne.symm, ha], hrefl _⟩
      | move j c =>
        by_cases hji : j = i
        · subst hji
          exact ⟨c, by simp [step], hM.1 rfl a ha⟩
        · exact ⟨a, by simp [step, Function.update, Ne.symm hji, ha], hrefl _⟩
      | add j k x c => exact ⟨a, by simpa [step] using ha, hrefl _⟩
      | scale j x c => exact ⟨a, by simpa [step] using ha, hrefl _⟩
      | clear j c => exact ⟨a, by simpa [step] using ha, hrefl _⟩
      | copy j k c => exact ⟨a, by simpa [step] using ha, hrefl _⟩
    obtain ⟨a', ha', hr⟩ := hstep
    exact htr _ _ _ hr (ih (step s e) a' b hL.2 hM.2 ha' hb)

end Run

/-! ## (1) PCL: port content law -/
section PCL
variable {K E Reg : Type*} [Field K] [AddCommGroup E] [Module K E] [DecidableEq Reg]

/-- support invariant: a token `b` occurs in a row only at a chart containing its anchor `u b`. -/
def Supp (u : Reg → E) (s : St K Reg (Submodule K E)) : Prop :=
  ∀ j b, s.row j b ≠ 0 → ∃ c, s.loc j = some c ∧ u b ∈ c

/-- Discipline: public births sit at a chart containing their anchor; every MOVE of a PUBLIC register
(`¬ own i`) ascends. -/
def DiscEv (own : Reg → Prop) (u : Reg → E) (s : St K Reg (Submodule K E)) : Ev K Reg (Submodule K E) → Prop
  | .born i c => u i ∈ c
  | .move i c => ¬ own i → ∀ c0, s.loc i = some c0 → c0 ≤ c
  | _ => True

def Disc (own : Reg → Prop) (u : Reg → E) : St K Reg (Submodule K E) → List (Ev K Reg (Submodule K E)) → Prop
  | _, [] => True
  | s, e :: es => DiscEv own u s e ∧ Disc own u (step s e) es

/-- An OWNED descent: some owned register makes a non-ascending MOVE. -/
def DescEv (own : Reg → Prop) (s : St K Reg (Submodule K E)) : Ev K Reg (Submodule K E) → Prop
  | .move i c => own i ∧ ∃ c0, s.loc i = some c0 ∧ ¬ c0 ≤ c
  | _ => False

def Desc (own : Reg → Prop) : St K Reg (Submodule K E) → List (Ev K Reg (Submodule K E)) → Prop
  | _, [] => False
  | s, e :: es => DescEv own s e ∨ Desc own (step s e) es

theorem step_supp (z V : Submodule K E) (own : Reg → Prop) (u : Reg → E) (s : St K Reg (Submodule K E))
    (e : Ev K Reg (Submodule K E)) (hS : Supp u s) (hL : LegalEv z V s e)
    (hD : DiscEv own u s e) (hN : ¬ DescEv own s e) : Supp u (step s e) := by
  intro j b hb
  simp only [DiscEv] at hD
  simp only [DescEv] at hN
  cases e with
  | born i c =>
    simp only [DiscEv] at hD
    by_cases hji : j = i
    · subst hji
      simp only [step, Function.update_self] at hb
      have : b = j := by
        by_contra h; apply hb; simp [Pi.single_apply, h]
      subst this
      exact ⟨c, by simp [step], hD⟩
    · simp only [step, Function.update_of_ne hji] at hb ⊢
      exact hS j b hb
  | init i c =>
    by_cases hji : j = i
    · subst hji; simp [step] at hb
    · simp only [step, Function.update_of_ne hji] at hb ⊢
      exact hS j b hb
  | move i c =>
    obtain ⟨c', hc', hu⟩ := hS j b hb
    by_cases hji : j = i
    · subst hji
      have hle : c' ≤ c := by
        by_cases ho : own j
        · by_contra hn; exact hN ⟨ho, c', hc', hn⟩
        · exact hD ho c' hc'
      exact ⟨c, by simp [step], hle hu⟩
    · exact ⟨c', by simpa [step, Function.update_of_ne hji] using hc', hu⟩
  | add i k x c =>
    simp only [LegalEv] at hL
    by_cases hji : j = i
    · subst hji
      simp only [step, Function.update_self, Pi.add_apply, Pi.smul_apply, smul_eq_mul] at hb
      refine ⟨c, by simp [step, hL.2.1], ?_⟩
      by_cases h1 : s.row j b = 0
      · have h2 : s.row k b ≠ 0 := by
          intro h2; apply hb; simp [h1, h2]
        obtain ⟨c2, hc2, hu2⟩ := hS k b h2
        rw [hL.2.2] at hc2; cases hc2; exact hu2
      · obtain ⟨c1, hc1, hu1⟩ := hS j b h1
        rw [hL.2.1] at hc1; cases hc1; exact hu1
    · simp only [step, Function.update_of_ne hji] at hb ⊢
      exact hS j b hb
  | scale i x c =>
    by_cases hji : j = i
    · subst hji
      simp only [step, Function.update_self, Pi.smul_apply, smul_eq_mul] at hb
      have h1 : s.row j b ≠ 0 := fun h => hb (by simp [h])
      obtain ⟨c1, hc1, hu1⟩ := hS j b h1
      exact ⟨c1, by simpa [step] using hc1, hu1⟩
    · simp only [step, Function.update_of_ne hji] at hb ⊢
      exact hS j b hb
  | clear i c =>
    by_cases hji : j = i
    · subst hji; simp [step] at hb
    · simp only [step, Function.update_of_ne hji] at hb ⊢
      exact hS j b hb
  | copy i k c =>
    simp only [LegalEv] at hL
    by_cases hji : j = i
    · subst hji
      simp only [step, Function.update_self] at hb
      obtain ⟨c1, hc1, hu1⟩ := hS k b hb
      refine ⟨c, by simp [step, hL.1], ?_⟩
      rw [hL.2] at hc1; cases hc1; exact hu1
    · simp only [step, Function.update_of_ne hji] at hb ⊢
      exact hS j b hb

theorem supp_run (z V : Submodule K E) (own : Reg → Prop) (u : Reg → E) :
    ∀ (es : List (Ev K Reg (Submodule K E))) (s : St K Reg (Submodule K E)),
      Supp u s → Legal z V s es → Disc own u s es → ¬ Desc own s es → Supp u (run s es) := by
  intro es
  induction es with
  | nil => intro s hS _ _ _; exact hS
  | cons e es ih =>
    intro s hS hL hD hN
    simp only [Legal] at hL
    simp only [Disc] at hD
    simp only [Desc, not_or] at hN
    exact ih (step s e) (step_supp z V own u s e hS hL.1 hD.1 hN.1) hL.2 hD.2 hN.2

/-- **PCL (port content law).**  Ports `t` carry functionals `φ t` (Φ_t = ker φ t), tokens `b` have anchors `u b`.
If a register `j` ends at a chart inside Φ_t and holds a nonzero coefficient of a token `b` NOT orthogonal to `t`
(`φ t (u b) ≠ 0`; this includes `b = t` when `u t` is non-isotropic), then an OWNED MOVE descended somewhere. -/
theorem pcl (z V : Submodule K E) (own : Reg → Prop) (u : Reg → E) (φ : Reg → Dual K E)
    (es : List (Ev K Reg (Submodule K E))) (s : St K Reg (Submodule K E))
    (h0 : ∀ j b, s.row j b = 0) (hL : Legal z V s es) (hD : Disc own u s es)
    (t j b : Reg) (c : Submodule K E) (hc : (run s es).loc j = some c) (hcΦ : c ≤ LinearMap.ker (φ t))
    (hnon : φ t (u b) ≠ 0) (hrow : (run s es).row j b ≠ 0) : Desc own s es := by
  by_contra hN
  have hS0 : Supp u s := fun j b hb => absurd (h0 j b) hb
  obtain ⟨c', hc', hu⟩ := supp_run z V own u es s hS0 hL hD hN j b hrow
  rw [hc] at hc'; cases hc'
  exact hnon (hcΦ hu)

/-- Contrapositive form: without an owned descent, every token in a register at a Φ_t chart is orthogonal to `t`. -/
theorem pcl_orth (z V : Submodule K E) (own : Reg → Prop) (u : Reg → E) (φ : Reg → Dual K E)
    (es : List (Ev K Reg (Submodule K E))) (s : St K Reg (Submodule K E))
    (h0 : ∀ j b, s.row j b = 0) (hL : Legal z V s es) (hD : Disc own u s es) (hN : ¬ Desc own s es)
    (t j b : Reg) (c : Submodule K E) (hc : (run s es).loc j = some c) (hcΦ : c ≤ LinearMap.ker (φ t))
    (hrow : (run s es).row j b ≠ 0) : φ t (u b) = 0 := by
  by_contra h; exact hN (pcl z V own u φ es s h0 hL hD t j b c hc hcΦ h hrow)

/-- an anchor line can sit inside Φ_t exactly when the token is orthogonal to `t`. -/
theorem line_le_ker_iff (φt : Dual K E) (x : E) : (K ∙ x) ≤ LinearMap.ker φt ↔ φt x = 0 := by
  rw [Submodule.span_singleton_le_iff_mem]; simp

end PCL

/-! ## (2) ONE-READ -/
section OneRead
variable {K Reg C : Type*} [Field K] [DecidableEq Reg] [PartialOrder C]

/-- ONE-READ.  A public register `r` (ascending) and an owned register `o` (DESCENDING lineage) are co-present at the
two read times (after the prefixes `l1` and `l1 ++ l2`).  Then the two reads happen at the SAME chart. -/
theorem one_read (z V : C) (r o : Reg) (s : St K Reg C) (l1 l2 : List (Ev K Reg C))
    (hL : Legal z V s (l1 ++ l2))
    (hr : MoveRel (· ≤ ·) r s (l1 ++ l2)) (ho : MoveRel (fun a b => b ≤ a) o s (l1 ++ l2))
    (c1 c2 : C)
    (h1r : (run s l1).loc r = some c1) (h1o : (run s l1).loc o = some c1)
    (h2r : (run s (l1 ++ l2)).loc r = some c2) (h2o : (run s (l1 ++ l2)).loc o = some c2) : c1 = c2 := by
  rw [legal_append] at hL
  rw [moveRel_append] at hr ho
  have a1 : c1 ≤ c2 := loc_rel z V (· ≤ ·) (fun a => le_refl a) (fun a b c => le_trans) r l2 _ c1 c2 hL.2 hr.2 h1r
    (by rw [← run_append]; exact h2r)
  have a2 : c2 ≤ c1 := loc_rel z V (fun a b => b ≤ a) (fun a => le_refl a) (fun a b c h1 h2 => le_trans h2 h1) o l2 _ c1 c2
    hL.2 ho.2 h1o (by rw [← run_append]; exact h2o)
  exact le_antisymm a1 a2

/-- The DESCENT hypothesis on the owned lineage is necessary: if the owned register may also ASCEND, a public reader
reads it at two different charts (charts := ℕ, ℚ coefficients; legal run, both lineages ascending). -/
theorem one_read_needs_descent :
    ∃ (l1 l2 : List (Ev ℚ (Fin 2) ℕ)),
      Legal (K := ℚ) 5 6 (⟨fun _ _ => 0, fun _ => none⟩ : St ℚ (Fin 2) ℕ) (l1 ++ l2) ∧
      MoveRel (· ≤ ·) (0 : Fin 2) (⟨fun _ _ => 0, fun _ => none⟩ : St ℚ (Fin 2) ℕ) (l1 ++ l2) ∧
      MoveRel (· ≤ ·) (1 : Fin 2) (⟨fun _ _ => 0, fun _ => none⟩ : St ℚ (Fin 2) ℕ) (l1 ++ l2) ∧
      (run (⟨fun _ _ => 0, fun _ => none⟩ : St ℚ (Fin 2) ℕ) l1).loc 0 = some 0 ∧
      (run (⟨fun _ _ => 0, fun _ => none⟩ : St ℚ (Fin 2) ℕ) l1).loc 1 = some 0 ∧
      (run (⟨fun _ _ => 0, fun _ => none⟩ : St ℚ (Fin 2) ℕ) (l1 ++ l2)).loc 0 = some 1 ∧
      (run (⟨fun _ _ => 0, fun _ => none⟩ : St ℚ (Fin 2) ℕ) (l1 ++ l2)).loc 1 = some 1 := by
  refine ⟨[.born 0 0, .init 1 0, .add 0 1 1 0], [.move 0 1, .move 1 1, .add 0 1 1 1], ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
  all_goals simp [Legal, LegalEv, MoveRel, run, step, Function.update]

end OneRead

/-! ## (3) HYPERPLANE -/
section Hyper
variable {K E Reg : Type*} [Field K] [AddCommGroup E] [Module K E] [DecidableEq Reg]

/-- a nonzero functional has a kernel of codimension 1: Φ_t is a hyperplane (dim 8 when dim E = 9). -/
theorem finrank_ker_add_one [FiniteDimensional K E] (φ : Dual K E) (hφ : φ ≠ 0) :
    finrank K (LinearMap.ker φ) + 1 = finrank K E := by
  have hs : Function.Surjective φ := LinearMap.surjective_of_ne_zero hφ
  have := LinearMap.finrank_range_add_finrank_ker φ
  rw [LinearMap.range_eq_top.mpr hs, finrank_top, Module.finrank_self] at this
  omega

/-- HYPERPLANE (general form): a register whose MOVEs ascend visits at most ONE chart of each dimension `d`. -/
theorem one_stop_per_dim [FiniteDimensional K E] (z V : Submodule K E) (r : Reg)
    (s : St K Reg (Submodule K E)) (l1 l2 : List (Ev K Reg (Submodule K E)))
    (hL : Legal z V s (l1 ++ l2)) (hr : MoveRel (· ≤ ·) r s (l1 ++ l2))
    (a b : Submodule K E) (ha : (run s l1).loc r = some a) (hb : (run s (l1 ++ l2)).loc r = some b)
    (hd : finrank K a = finrank K b) : a = b := by
  rw [legal_append] at hL
  rw [moveRel_append] at hr
  have hab : a ≤ b := loc_rel z V (· ≤ ·) (fun a => le_refl a) (fun a b c => le_trans) r l2 _ a b hL.2 hr.2 ha
    (by rw [← run_append]; exact hb)
  exact Submodule.eq_of_le_of_finrank_eq hab hd

/-- HYPERPLANE (dedicated register): if the hyperplanes Φ_t, Φ_t' are different and of equal dimension, an ascending
register cannot stop at Φ_t and later at Φ_t' (nor, by symmetry, the other order): a delivery at Φ_t uses a
register dedicated to `t`. -/
theorem hyperplane_dedicated [FiniteDimensional K E] (z V : Submodule K E) (r : Reg)
    (s : St K Reg (Submodule K E)) (l1 l2 : List (Ev K Reg (Submodule K E)))
    (hL : Legal z V s (l1 ++ l2)) (hr : MoveRel (· ≤ ·) r s (l1 ++ l2))
    (φ φ' : Dual K E) (hne : LinearMap.ker φ ≠ LinearMap.ker φ') (hd : finrank K (LinearMap.ker φ) = finrank K (LinearMap.ker φ'))
    (ha : (run s l1).loc r = some (LinearMap.ker φ)) (hb : (run s (l1 ++ l2)).loc r = some (LinearMap.ker φ')) : False :=
  hne (one_stop_per_dim z V r s l1 l2 hL hr _ _ ha hb hd)

end Hyper

/-! ## (4) RANK-FEED -/
section RankFeed
variable {K P : Type*} [Field K] [Fintype P] [DecidableEq P]

/-- RANK-FEED (general "≥ N − s").  `O t : P → K` = owned-routed content of port `t` (a vector over tokens), all in the
span `W` of the owned states ever read (`s = finrank W`).  Content is exact on `N_t = {t} ∪ non-orth(t)`:
`O t b = δ_{tb}` there (`Orth t b` = tokens `t`, `b` orthogonal).  Then at most `s` ports have an exact owned content
(no residue); the other ≥ N − s ports have an orthogonal residue `b ≠ t`, `Orth t b`, `O t b ≠ 0`, to be fed/cancelled. -/
theorem rank_feed (Orth : P → P → Prop) (W : Submodule K (P → K)) (O : P → P → K)
    (hW : ∀ t, O t ∈ W) (hNt : ∀ t b, (b = t ∨ ¬ Orth t b) → O t b = if b = t then 1 else 0) :
    Fintype.card P ≤ finrank K W + (Finset.univ.filter fun t => ∃ b, b ≠ t ∧ Orth t b ∧ O t b ≠ 0).card := by
  set F := Finset.univ.filter fun t => ∃ b, b ≠ t ∧ Orth t b ∧ O t b ≠ 0 with hF
  set Z := Finset.univ.filter fun t => ¬ ∃ b, b ≠ t ∧ Orth t b ∧ O t b ≠ 0 with hZ
  have hcard : Z.card + F.card = Fintype.card P := by
    rw [hZ, hF, add_comm, Finset.card_filter_add_card_filter_not]
    exact Finset.card_univ
  have hZO : ∀ t ∈ Z, O t = Pi.single t 1 := by
    intro t ht
    simp only [hZ, Finset.mem_filter, Finset.mem_univ, true_and, not_exists, not_and] at ht
    funext b
    by_cases hb : b = t
    · subst hb; rw [hNt b b (Or.inl rfl)]; simp
    · by_cases ho : Orth t b
      · have := ht b hb ho; push Not at this; simp [hb, this]
      · rw [hNt t b (Or.inr ho)]; simp [hb]
  have hli : LinearIndependent K (fun t : Z => (Pi.single (t : P) (1 : K) : P → K)) :=
    by
      have := (Pi.basisFun K P).linearIndependent.comp (fun t : Z => (t : P)) Subtype.val_injective
      convert this using 1
      funext t; simp [Pi.basisFun_apply]
  have hle : Submodule.span K (Set.range fun t : Z => (Pi.single (t : P) (1 : K) : P → K)) ≤ W := by
    apply Submodule.span_le.mpr
    rintro _ ⟨t, rfl⟩
    show (Pi.single (t : P) (1 : K) : P → K) ∈ W
    rw [← hZO t t.2]; exact hW t
  have := Submodule.finrank_mono hle
  rw [finrank_span_eq_card hli] at this
  simp only [Fintype.card_coe] at this
  omega

end RankFeed

section RankFeedExtra
variable {K P : Type*} [Field K] [Fintype P] [DecidableEq P]

/-- `rank_feed` with the residue set given as any finset `F` with the right membership. -/
theorem rank_feed' (Orth : P → P → Prop) (W : Submodule K (P → K)) (O : P → P → K)
    (hW : ∀ t, O t ∈ W) (hNt : ∀ t b, (b = t ∨ ¬ Orth t b) → O t b = if b = t then 1 else 0)
    (F : Finset P) (hF : ∀ t, t ∈ F ↔ ∃ b, b ≠ t ∧ Orth t b ∧ O t b ≠ 0) :
    Fintype.card P ≤ finrank K W + F.card := by
  have h := rank_feed Orth W O hW hNt
  have : (Finset.univ.filter fun t => ∃ b, b ≠ t ∧ Orth t b ∧ O t b ≠ 0) = F := by
    ext t; simp [hF]
  rwa [this] at h

/-- `rank (I + J) ≤ s` in matrix form: the matrix with columns `O t` has rank ≤ dim W. -/
theorem matrix_rank_le (W : Submodule K (P → K)) (O : P → P → K) (hW : ∀ t, O t ∈ W) :
    (Matrix.of fun b t => O t b).rank ≤ finrank K W := by
  rw [Matrix.rank_eq_finrank_span_cols]
  apply Submodule.finrank_mono
  apply Submodule.span_le.mpr
  rintro _ ⟨t, rfl⟩
  exact hW t

/-- st1 instance (REBUILDKIT/core/RC5.md gate 1): N = 104 ports, s = 96 read owned-state rank ⇒ ≥ 8 ports with residue. -/
theorem rank_feed_st1 (Orth : Fin 104 → Fin 104 → Prop) (W : Submodule K (Fin 104 → K)) (O : Fin 104 → Fin 104 → K)
    (hW : ∀ t, O t ∈ W) (hNt : ∀ t b, (b = t ∨ ¬ Orth t b) → O t b = if b = t then 1 else 0)
    (hs : finrank K W = 96) :
    8 ≤ (Finset.univ.filter fun t => ∃ b, b ≠ t ∧ Orth t b ∧ O t b ≠ 0).card := by
  have := rank_feed' Orth W O hW hNt (Finset.univ.filter fun t => ∃ b, b ≠ t ∧ Orth t b ∧ O t b ≠ 0)
    (by intro t; simp)
  simp only [Fintype.card_fin, hs] at this
  omega

end RankFeedExtra

/-! ## (5) XCLOSE exactness -/
section XClose
variable {K Reg C : Type*} [Field K] [DecidableEq Reg]

/-- **XCLOSE.**  Closer `x = X_σ(t)` and `y = Y_t` are both at the dim-8 stop `Φ_t` (legal co-presence).  X's row is
`λ e_σ + g` (λ ≠ 0: its own token plus the gathered correction `g`, σ-free).  One ADD `y += a x`: the σ-coefficient of Y
becomes `y_σ + aλ` (own token cancelled iff a = -y_σ/λ), every other coordinate receives exactly `a·g` (the delivered
correction), nothing else changes. -/
theorem xclose_add (s : St K Reg C) (y x σ : Reg) (c : C) (a lam : K) (g : Reg → K)
    (hx : s.row x = lam • Pi.single σ (1 : K) + g) (hg : g σ = 0) :
    (step s (.add y x a c)).row y σ = s.row y σ + a * lam ∧
    (∀ b, b ≠ σ → (step s (.add y x a c)).row y b = s.row y b + a * g b) ∧
    (∀ j, j ≠ y → (step s (.add y x a c)).row j = s.row j) ∧
    (step s (.add y x a c)).loc = s.loc := by
  refine ⟨?_, ?_, ?_, rfl⟩
  · simp [step, hx, hg]
  · intro b hb; simp [step, hx, Pi.single_apply, hb]
  · intro j hj; simp [step, Function.update_of_ne hj]

/-- Exactness: if Y's pre-close row is `τ + k · (X's row)` with τ σ-free (X's token is not part of the target), then the
single ADD with `a = -k` yields exactly τ, and `a = -k` is the only coefficient that does (legal when both sit at `c`). -/
theorem xclose_exact (z V : C) (s : St K Reg C) (y x σ : Reg) (c : C) (hyx : y ≠ x)
    (hy : s.loc y = some c) (hxl : s.loc x = some c) (lam : K) (hlam : lam ≠ 0) (g : Reg → K)
    (hx : s.row x = lam • Pi.single σ (1 : K) + g) (hg : g σ = 0)
    (τ : Reg → K) (hτ : τ σ = 0) (k : K) (hrow : s.row y = τ + k • s.row x) :
    LegalEv z V s (.add y x (-k) c) ∧ (step s (.add y x (-k) c)).row y = τ ∧
    ∀ a, (step s (.add y x a c)).row y = τ → a = -k := by
  refine ⟨⟨hyx, hy, hxl⟩, ?_, ?_⟩
  · simp [step, hrow]
  · intro a ha
    have h1 := (xclose_add s y x σ c a lam g hx hg).1
    have h2 : s.row y σ = τ σ + k * lam := by
      have := congrFun hrow σ
      simp [hx, hg] at this
      simpa using this
    have h3 : (step s (.add y x a c)).row y σ = τ σ := by rw [ha]
    have : (a + k) * lam = 0 := by
      rw [h3, h2] at h1
      linear_combination -h1
    rcases mul_eq_zero.mp this with h | h
    · linear_combination h
    · exact absurd h hlam

end XClose

end DesignLaws

#print axioms DesignLaws.pcl
#print axioms DesignLaws.supp_run
#print axioms DesignLaws.one_read
#print axioms DesignLaws.one_read_needs_descent
#print axioms DesignLaws.one_stop_per_dim
#print axioms DesignLaws.hyperplane_dedicated
#print axioms DesignLaws.finrank_ker_add_one
#print axioms DesignLaws.rank_feed
#print axioms DesignLaws.rank_feed_st1
#print axioms DesignLaws.matrix_rank_le
#print axioms DesignLaws.xclose_exact
