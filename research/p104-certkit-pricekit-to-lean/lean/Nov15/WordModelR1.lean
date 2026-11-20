/-
WordModelR1 (lane WM-R1, Nov 18): R1 on the shared word model.  `R1 : Word cl s → 8 ≤ nR1 s`.
Region-span invariant for the down-set D_q = {charts c ⊆ q^⊥} (the only new invariant), then the x_Q-projection
count.  Uses: public ascent (Step.movePub, VERIFIER l.51), owned INIT row 0, Word endpoint fields, Q clique.
Kernel only: no sorry, no native_decide, no axioms.
-/
import Mathlib.LinearAlgebra.Dimension.Constructions
import Nov15.WordModelDefs

set_option linter.unusedSectionVars false

namespace WordModel

open Finset SafeRungsClique Module Submodule

section Gen
variable {R : Type} [Fintype R] [DecidableEq R] {pb : R → Bool}

/-- generators of the region span of D_q. -/
def Gq (q : ℕ) (s : St R) : Set (R → ℚ) :=
  {v | ∃ r c, c ⊆ Hq q ∧ r ∈ s.B c ∧ v = Pi.single r 1} ∪
  {v | ∃ a c, c ⊆ Hq q ∧ (a, c, v) ∈ s.olog}

/-- the region invariant. -/
def SInv (q : ℕ) (s : St R) : Prop :=
  ∀ r c, s.loc r = .sit c → c ⊆ Hq q → s.row r ∈ Submodule.span ℚ (Gq q s)

def BInv (s : St R) : Prop :=
  (∀ r c, r ∈ s.B c → s.loc r ≠ .unborn) ∧ (∀ r c c', r ∈ s.B c → r ∈ s.B c' → c = c')

theorem Gq_mono {s s' : St R} (hB : ∀ c r, r ∈ s.B c → r ∈ s'.B c)
    (hO : ∀ m ∈ s.olog, m ∈ s'.olog) (q : ℕ) : Gq q s ⊆ Gq q s' := by
  rintro v (⟨r, c, hc, hr, rfl⟩ | ⟨a, c, hc, hm⟩)
  · exact Or.inl ⟨r, c, hc, hB c r hr, rfl⟩
  · exact Or.inr ⟨a, c, hc, hO _ hm⟩

theorem loc_mono {s s' : St R} (h : Step pb s s') (r : R) (h0 : s.loc r ≠ .unborn) :
    s'.loc r ≠ .unborn := by
  cases h <;> first | exact h0 | (simp only [Function.update_apply]; split_ifs <;> first | exact h0 | simp | simp_all)

theorem step_inv {s s' : St R} (h : Step pb s s') (hb : BInv s) (hs : ∀ q, SInv q s) :
    BInv s' ∧ ∀ q, SInv q s' := by
  have hmono : ∀ q, ∀ {t t' : St R}, (∀ c r, r ∈ t.B c → r ∈ t'.B c) →
      (∀ m ∈ t.olog, m ∈ t'.olog) → ∀ v, v ∈ Submodule.span ℚ (Gq q t) →
      v ∈ Submodule.span ℚ (Gq q t') :=
    fun q t t' hB hO v hv => Submodule.span_mono (Gq_mono hB hO q) hv
  cases h with
  | birthPub r c hu hp =>
    refine ⟨⟨?_, ?_⟩, ?_⟩
    · intro r' c' hr'
      by_cases hrr : r' = r
      · subst hrr; simp [Function.update_apply]
      · have : r' ∈ s.B c' := by
          by_cases hc : c' = c
          · subst hc; simpa [Function.update_apply, hrr] using hr'
          · simpa [Function.update_apply, hc] using hr'
        simpa [Function.update_apply, hrr] using hb.1 r' c' this
    · intro r' c1 c2 h1 h2
      have key : ∀ c', r' ∈ (Function.update s.B c (insert r (s.B c))) c' →
          (r' = r ∧ c' = c) ∨ r' ∈ s.B c' := by
        intro c' hh
        by_cases hc : c' = c
        · subst hc
          simp only [Function.update_self, Finset.mem_insert] at hh
          rcases hh with hh | hh
          · exact Or.inl ⟨hh, rfl⟩
          · exact Or.inr hh
        · simp only [Function.update_of_ne hc] at hh; exact Or.inr hh
      rcases key _ h1 with ⟨e1, e2⟩ | h1' <;> rcases key _ h2 with ⟨f1, f2⟩ | h2'
      · rw [e2, f2]
      · exact absurd hu (by subst e1; exact hb.1 _ _ h2')
      · exact absurd hu (by subst f1; exact hb.1 _ _ h1')
      · exact hb.2 _ _ _ h1' h2'
    · intro q r' c' hl hc'
      by_cases hrr : r' = r
      · subst hrr
        have hl2 : Loc.sit c = Loc.sit c' := by simpa [Function.update_apply] using hl
        have hc : c = c' := Loc.sit.inj hl2
        subst hc
        simp only [Function.update_self]
        apply Submodule.subset_span
        exact Or.inl ⟨r', c, hc', by simp, rfl⟩
      · have hl' : s.loc r' = Loc.sit c' := by simpa [Function.update_apply, hrr] using hl
        simp only [Function.update_apply, hrr, if_false]
        refine hmono q (t := s) ?_ ?_ _ (hs q r' c' hl' hc')
        swap
        · intro m hm; exact hm
        intro c1 r1 hr1
        by_cases hc : c1 = c
        · subst hc; simp [hr1]
        · simp [Function.update_of_ne hc, hr1]
  | birthOwn r c hu hp =>
    refine ⟨⟨?_, hb.2⟩, ?_⟩
    · intro r' c' hr'
      have h0 := hb.1 r' c' hr'
      simp only [Function.update_apply]; split_ifs <;> simp_all
    · intro q r' c' hl hc'
      by_cases hrr : r' = r
      · subst hrr; simp [Function.update_apply]
      · have hl' : s.loc r' = Loc.sit c' := by simpa [Function.update_apply, hrr] using hl
        simp only [Function.update_apply, hrr, if_false]
        exact hs q r' c' hl' hc'
  | gate r c coef hl =>
    refine ⟨⟨hb.1, hb.2⟩, ?_⟩
    intro q r' c' hl' hc'
    by_cases hrr : r' = r
    · subst hrr
      have hc : c' = c := by
        have : Loc.sit c' = Loc.sit c := hl'.symm.trans hl
        simpa using this
      subst hc
      simp only [Function.update_self]
      refine Submodule.sum_mem _ (fun t ht => Submodule.smul_mem _ _ ?_)
      have ht' : s.loc t = .sit c' := by simpa using ht
      exact hs q t c' ht' hc'
    · simp only [Function.update_apply, hrr, if_false]
      exact hs q r' c' hl' hc'
  | movePub r c d hl hp hlt =>
    refine ⟨⟨?_, hb.2⟩, ?_⟩
    · intro r' c' hr'
      have h0 := hb.1 r' c' hr'
      simp only [Function.update_apply]; split_ifs <;> simp_all
    · intro q r' c' hl' hc'
      by_cases hrr : r' = r
      · subst hrr
        have hc : d = c' := by
          have : Loc.sit d = Loc.sit c' := by simpa [Function.update_apply] using hl'
          simpa using this
        subst hc
        have hcd : c ⊆ d := hlt.subset
        exact hmono q (t := s) (fun c1 r1 h1 => h1) (fun m hm => hm) _ (hs q r' c hl (hcd.trans hc'))
      · have hl2 : s.loc r' = Loc.sit c' := by simpa [Function.update_apply, hrr] using hl'
        exact hmono q (t := s) (fun c1 r1 h1 => h1) (fun m hm => hm) _ (hs q r' c' hl2 hc')
  | moveOwn r c d hl hp =>
    refine ⟨⟨?_, hb.2⟩, ?_⟩
    · intro r' c' hr'
      have h0 := hb.1 r' c' hr'
      simp only [Function.update_apply]; split_ifs <;> simp_all
    · intro q r' c' hl' hc'
      by_cases hrr : r' = r
      · subst hrr
        have hc : d = c' := by
          have : Loc.sit d = Loc.sit c' := by simpa [Function.update_apply] using hl'
          simpa using this
        subst hc
        apply Submodule.subset_span
        exact Or.inr ⟨c, d, hc', by simp⟩
      · have hl2 : s.loc r' = Loc.sit c' := by simpa [Function.update_apply, hrr] using hl'
        simp only [Function.update_apply, hrr, if_false]
        refine hmono q (t := s) ?_ ?_ _ (hs q r' c' hl2 hc')
        · intro c1 r1 hr1; exact hr1
        intro m hm
        simp [hm]
  | clearOwn r c hl hp =>
    refine ⟨⟨?_, hb.2⟩, ?_⟩
    · intro r' c' hr'
      have h0 := hb.1 r' c' hr'
      simp only [Function.update_apply]; split_ifs <;> simp_all
    · intro q r' c' hl' hc'
      by_cases hrr : r' = r
      · subst hrr; simp [Function.update_apply] at hl'
      · have hl2 : s.loc r' = Loc.sit c' := by simpa [Function.update_apply, hrr] using hl'
        simp only [Function.update_apply, hrr, if_false]
        exact hs q r' c' hl2 hc'

theorem reach_inv {s : St R} (h : Reach pb s) : BInv s ∧ ∀ q, SInv q s := by
  induction h with
  | refl =>
    refine ⟨⟨?_, ?_⟩, ?_⟩
    · intro r c hr; simp [init] at hr
    · intro r c c' hr; simp [init] at hr
    · intro q r c hl; simp [init] at hl
  | tail _ hstep ih => exact step_inv hstep ih.1 ih.2

end Gen

section Main
variable {Pt Hl Ow : Type} [Fintype Pt] [Fintype Hl] [Fintype Ow]
  [DecidableEq Pt] [DecidableEq Hl] [DecidableEq Ow]

/-- R1: at least 8 owned MOVEs enter a down-set q^perp (q in Q). -/
theorem R1 {cl : Caller Pt} {s : St (Reg Pt Hl Ow)} (h : Word cl s) : 8 ≤ nR1 s := by
  classical
  obtain ⟨hb, hs⟩ := reach_inv h.reach
  let ι := ↥(Q.toFinset)
  have hQmem : ∀ q : ι, q.1 ∈ Q := fun q => List.mem_toFinset.1 q.2
  let pt : ι → Pt := fun q => Classical.choose (cl.Q_sub q.1 (hQmem q))
  have hpt : ∀ q : ι, cl.lab (pt q) = q.1 := fun q => Classical.choose_spec (cl.Q_sub q.1 (hQmem q))
  have hptinj : ∀ q q' : ι, pt q' = pt q ↔ q' = q := by
    intro q q'
    constructor
    · intro he
      apply Subtype.ext
      rw [← hpt q', ← hpt q, he]
    · intro he; rw [he]
  let π : (Reg Pt Hl Ow → ℚ) →ₗ[ℚ] (ι → ℚ) :=
    LinearMap.funLeft ℚ ℚ (fun q : ι => (Reg.x (pt q) : Reg Pt Hl Ow))
  let L : List (Reg Pt Hl Ow → ℚ) :=
    (s.olog.filter (fun m => decide (InDown m.2.1))).map (fun m => m.2.2)
  have hL : L.length = nR1 s := by
    simp [L, nR1, List.countP_eq_length_filter]
  let W : Submodule ℚ (ι → ℚ) := (Submodule.span ℚ {v | v ∈ L}).map π
  have hWdim : finrank ℚ W ≤ L.length := by
    calc finrank ℚ W ≤ finrank ℚ (Submodule.span ℚ {v | v ∈ L}) := Submodule.finrank_map_le _ _
      _ ≤ L.toFinset.card := by
          have := finrank_span_finset_le_card (R := ℚ) L.toFinset
          rw [Set.finrank, List.coe_toFinset] at this
          exact this
      _ ≤ L.length := List.toFinset_card_le L
  have hsingle : ∀ q : ι, (Pi.single q (1 : ℚ) : ι → ℚ) ∈ W := by
    intro q
    have hyl := h.y_final (pt q)
    have hrow := h.final_row (Reg.y (pt q)) (by simp [pub])
    rw [hpt q] at hyl
    have hspan := hs q.1 (Reg.y (pt q)) (Hq q.1) hyl (subset_refl _)
    have hG : Gq q.1 s ⊆ (Submodule.span ℚ {v | v ∈ L} ⊔ LinearMap.ker π : Submodule ℚ _) := by
      intro g hg
      rcases hg with ⟨r, c, hc, hr, rfl⟩ | ⟨a, c, hc, hm⟩
      · apply Submodule.mem_sup_right
        rw [LinearMap.mem_ker]
        ext q'
        simp only [π, LinearMap.funLeft_apply, Pi.single_apply, Pi.zero_apply]
        by_contra hne
        have hxr : (Reg.x (pt q') : Reg Pt Hl Ow) = r := by
          by_contra hx; exact hne (if_neg hx)
        subst hxr
        have hbirth := h.x_birth (pt q')
        rw [hpt q'] at hbirth
        have hce : c = line q'.1 := hb.2 _ _ _ hr hbirth
        have hmem : q'.1 ∈ Hq q.1 := hc (by rw [hce]; simp [line])
        have h0 : dot q'.1 q.1 = 0 := by simp [Hq] at hmem; exact hmem.2
        have h1 := Q_dot_one q'.1 (hQmem q') q.1 (hQmem q)
        omega
      · apply Submodule.mem_sup_left
        apply Submodule.subset_span
        simp only [Set.mem_setOf_eq, L, List.mem_map, List.mem_filter]
        refine ⟨(a, c, g), ⟨hm, ?_⟩, rfl⟩
        have hid : InDown c := ⟨q.1, hQmem q, fun x hx => by
          have := hc hx; simp [Hq] at this; exact this.2⟩
        simpa using hid
    have hZ := Submodule.span_le.2 hG hspan
    obtain ⟨a, ha, b, hb', hab⟩ := Submodule.mem_sup.1 hZ
    have hπ : π (s.row (Reg.y (pt q))) ∈ W := by
      have : π (s.row (Reg.y (pt q))) = π a := by
        rw [← hab, map_add, LinearMap.mem_ker.1 hb', add_zero]
      rw [this]; exact Submodule.mem_map_of_mem ha
    have hcoord : ∀ c : ℚ, c ≠ 0 → π (s.row (Reg.y (pt q))) = c • (Pi.single q (1 : ℚ) : ι → ℚ) →
        (Pi.single q (1 : ℚ) : ι → ℚ) ∈ W := by
      intro c hc he
      rw [he] at hπ
      have := W.smul_mem c⁻¹ hπ
      rwa [smul_smul, inv_mul_cancel₀ hc, one_smul] at this
    by_cases hD : cl.isD (pt q) = true
    · refine hcoord 1 one_ne_zero ?_
      ext q'
      simp [π, hrow, tgt, hD, e, Pi.single_apply, hptinj]
    · refine hcoord (1/2) (by norm_num) ?_
      ext q'
      simp [π, hrow, tgt, hD, e, Pi.single_apply, hptinj]
  have hle : span ℚ (Set.range (Pi.basisFun ℚ ι)) ≤ W := by
    refine Submodule.span_le.2 ?_
    rintro _ ⟨i, rfl⟩
    simpa using hsingle i
  have h1 : finrank ℚ (span ℚ (Set.range (Pi.basisFun ℚ ι))) = Fintype.card ι :=
    finrank_span_eq_card (Pi.basisFun ℚ ι).linearIndependent
  have hcard : Fintype.card ι = 8 := by
    simp only [ι, Fintype.card_coe]; decide
  have h2 := Submodule.finrank_mono hle
  omega

end Main
end WordModel

#print axioms WordModel.R1
