/-
WordModelR3 (lane WM-R3, Nov 18).  R3 slack-rank machinery on top of WordModelDefs:
  cs_final, cs_entry, born_unique, slack_rank  (the four stubs of WordModelDefs for WM-R3).
Kernel only.  Where the paper's step rests on a verifier-only line it is flagged `[L51]` below:
public strict ascent (l.51) enters through `Step.movePub` (c < d) and is used in
  - Inv.apos / csent (an entrant never re-enters a chart it already entered: eRow not overwritten),
  - Inv.disj (born at c  =>  never entrant at c)  -> |B_c| + |A_c| counts distinct registers.
Without it slack_rank (and so R3) has no proof here.  See cards/WILD/LEANSWARM/WM-R3.md.
-/
import Nov15.WordModelDefs
import Mathlib.LinearAlgebra.Basis.VectorSpace
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.LinearAlgebra.Dimension.Constructions

set_option linter.unusedSectionVars false

namespace WordModel

open Finset SafeRungsClique Module

section Inv

theorem updB_iff {R : Type} [DecidableEq R] (f : Ch → Finset R) (c0 c' : Ch) (r r' : R) :
    r' ∈ Function.update f c0 (insert r (f c0)) c' ↔ (c' = c0 ∧ r' = r) ∨ r' ∈ f c' := by
  by_cases h : c' = c0
  · subst h; simp [Function.update_self]
  · simp [Function.update_apply, h]

variable {R : Type} [Fintype R] [DecidableEq R] {pb : R → Bool}

/-- the run invariant. -/
structure Inv (pb : R → Bool) (s : St R) : Prop where
  bpub : ∀ r c, r ∈ s.B c → pb r = true
  apub : ∀ r c, r ∈ s.A c → pb r = true
  bornU : ∀ r c c', r ∈ s.B c → r ∈ s.B c' → c = c'
  bpos : ∀ r c, r ∈ s.B c → ∃ c', s.loc r = .sit c' ∧ c ⊆ c'
  apos : ∀ r d, r ∈ s.A d → ∃ c', s.loc r = .sit c' ∧ d ⊆ c'
  disj : ∀ r c, r ∈ s.B c → r ∉ s.A c
  sitBA : ∀ r c, pb r = true → s.loc r = .sit c → r ∈ s.B c ∨ r ∈ s.A c
  csrow : ∀ r c, s.loc r = .sit c → s.row r ∈ I s c
  csent : ∀ r d, r ∈ s.A d → ∃ c, c < d ∧ s.eRow r d ∈ I s c
  stops : ∀ r c, r ∈ s.A c → s.loc r ≠ .sit c → (r, c) ∈ s.slog

theorem Inv.init : Inv pb (init : St R) := by
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;> intro r c <;> simp [WordModel.init]
  all_goals intros; simp_all

theorem gens_sub {s s' : St R}
    (hB : ∀ c, s.B c ⊆ s'.B c) (hA : ∀ c, s.A c ⊆ s'.A c)
    (hE : ∀ c r, r ∈ s.A c → s'.eRow r c = s.eRow r c)
    (hO : ∀ c a v, (a, c, v) ∈ s.olog → (a, c, v) ∈ s'.olog) (c : Ch) :
    gens s c ⊆ gens s' c := by
  intro v hv
  rcases hv with (⟨r, hr, rfl⟩ | ⟨r, hr, rfl⟩) | ⟨a, ha⟩
  · exact Or.inl (Or.inl ⟨r, hB c hr, rfl⟩)
  · exact Or.inl (Or.inr ⟨r, hA c hr, hE c r hr⟩)
  · exact Or.inr ⟨a, hO c a v ha⟩

theorem Step.gens_mono {s s' : St R} (hI : Inv pb s) (h : Step pb s s') (c : Ch) :
    gens s c ⊆ gens s' c := by
  cases h with
  | birthPub r c0 h1 h2 =>
    refine gens_sub ?_ ?_ ?_ ?_ c
    · intro c' x hx; rw [updB_iff]; exact Or.inr hx
    · exact fun _ _ hx => hx
    · exact fun _ _ _ => rfl
    · exact fun _ _ _ hx => hx
  | birthOwn r c0 h1 h2 =>
    refine gens_sub ?_ ?_ ?_ ?_ c
    · exact fun _ _ hx => hx
    · exact fun _ _ hx => hx
    · exact fun _ _ _ => rfl
    · exact fun _ _ _ hx => hx
  | gate r c0 coef h1 =>
    refine gens_sub ?_ ?_ ?_ ?_ c
    · exact fun _ _ hx => hx
    · exact fun _ _ hx => hx
    · exact fun _ _ _ => rfl
    · exact fun _ _ _ hx => hx
  | movePub r c0 d h1 h2 hcd =>
    refine gens_sub ?_ ?_ ?_ ?_ c
    · exact fun _ _ hx => hx
    · intro c' x hx; rw [updB_iff]; exact Or.inr hx
    · intro c' r' hx
      by_cases hc : r' = r ∧ c' = d
      · obtain ⟨rfl, rfl⟩ := hc
        obtain ⟨c2, hl, hsub⟩ := hI.apos _ _ hx
        rw [h1] at hl
        have := Loc.sit.inj hl
        subst this
        exact absurd hcd (not_lt_of_ge hsub)
      · simp [hc]
    · exact fun _ _ _ hx => hx
  | moveOwn r c0 d h1 h2 =>
    refine gens_sub ?_ ?_ ?_ ?_ c
    · exact fun _ _ hx => hx
    · exact fun _ _ hx => hx
    · exact fun _ _ _ => rfl
    · exact fun _ _ _ hx => List.mem_cons_of_mem _ hx
  | clearOwn r c0 h1 h2 =>
    refine gens_sub ?_ ?_ ?_ ?_ c
    · exact fun _ _ hx => hx
    · exact fun _ _ hx => hx
    · exact fun _ _ _ => rfl
    · exact fun _ _ _ hx => hx

theorem Inv.step {s s' : St R} (hI : Inv pb s) (h : Step pb s s') : Inv pb s' := by
  have hm : ∀ c, I s c ≤ I s' c := fun c => Submodule.span_mono (Step.gens_mono hI h c)
  cases h with
  | birthPub r c0 h1 h2 =>
    have hne : ∀ r' c', r' ∈ s.B c' → r' ≠ r := by
      intro r' c' hx hr
      subst hr
      obtain ⟨c3, hl, _⟩ := hI.bpos _ _ hx
      rw [h1] at hl; cases hl
    have hne' : ∀ r' c', r' ∈ s.A c' → r' ≠ r := by
      intro r' c' hx hr
      subst hr
      obtain ⟨c3, hl, _⟩ := hI.apos _ _ hx
      rw [h1] at hl; cases hl
    refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
    · intro r' c' hx
      rw [updB_iff] at hx
      rcases hx with ⟨_, rfl⟩ | hx
      · exact h2
      · exact hI.bpub _ _ hx
    · exact fun r' c' hx => hI.apub r' c' hx
    · intro r' c1 c2 hx1 hx2
      rw [updB_iff] at hx1 hx2
      rcases hx1 with ⟨ha, rfl⟩ | hx1
      · rcases hx2 with ⟨hb, _⟩ | hx2
        · exact ha.trans hb.symm
        · exact absurd rfl (hne _ _ hx2)
      · rcases hx2 with ⟨hb, rfl⟩ | hx2
        · exact absurd rfl (hne _ _ hx1)
        · exact hI.bornU _ _ _ hx1 hx2
    · intro r' c' hx
      rw [updB_iff] at hx
      rcases hx with ⟨hc, rfl⟩ | hx
      · refine ⟨c0, by simp, ?_⟩
        rw [hc]
      · obtain ⟨c3, hl, hs⟩ := hI.bpos _ _ hx
        exact ⟨c3, by simp [Function.update_apply, hne _ _ hx, hl], hs⟩
    · intro r' d hx
      obtain ⟨c3, hl, hs⟩ := hI.apos _ _ hx
      exact ⟨c3, by simp [Function.update_apply, hne' _ _ hx, hl], hs⟩
    · intro r' c' hx
      rw [updB_iff] at hx
      rcases hx with ⟨hc, rfl⟩ | hx
      · intro hA; exact hne' _ _ hA rfl
      · exact hI.disj _ _ hx
    · intro r' c' hp hl
      by_cases hr : r' = r
      · subst hr
        simp at hl
        subst hl
        left; rw [updB_iff]; exact Or.inl ⟨rfl, rfl⟩
      · simp only [Function.update_apply, hr, if_false] at hl
        rcases hI.sitBA _ _ hp hl with hb | ha
        · left; rw [updB_iff]; exact Or.inr hb
        · right; exact ha
    · intro r' c' hl
      by_cases hr : r' = r
      · subst hr
        simp at hl
        subst hl
        simp only [Function.update_self]
        refine Submodule.subset_span (Or.inl (Or.inl ⟨r', ?_, rfl⟩))
        simp [updB_iff]
      · simp only [Function.update_apply, hr, if_false] at hl ⊢
        exact hm _ (hI.csrow _ _ hl)
    · intro r' d hx
      obtain ⟨c3, hc, hmem⟩ := hI.csent _ _ hx
      exact ⟨c3, hc, hm _ hmem⟩
    · intro r' c' hx hl
      apply hI.stops _ _ hx
      intro hl'
      apply hl
      simp [Function.update_apply, hne' _ _ hx, hl']
  | birthOwn r c0 h1 h2 =>
    have hne : ∀ r' c', r' ∈ s.B c' → r' ≠ r := by
      intro r' c' hx hr
      subst hr
      obtain ⟨c3, hl, _⟩ := hI.bpos _ _ hx
      rw [h1] at hl; cases hl
    have hne' : ∀ r' c', r' ∈ s.A c' → r' ≠ r := by
      intro r' c' hx hr
      subst hr
      obtain ⟨c3, hl, _⟩ := hI.apos _ _ hx
      rw [h1] at hl; cases hl
    refine ⟨hI.bpub, hI.apub, hI.bornU, ?_, ?_, hI.disj, ?_, ?_, ?_, ?_⟩
    · intro r' c' hx
      obtain ⟨c3, hl, hs⟩ := hI.bpos _ _ hx
      exact ⟨c3, by simp [Function.update_apply, hne _ _ hx, hl], hs⟩
    · intro r' d hx
      obtain ⟨c3, hl, hs⟩ := hI.apos _ _ hx
      exact ⟨c3, by simp [Function.update_apply, hne' _ _ hx, hl], hs⟩
    · intro r' c' hp hl
      have hr : r' ≠ r := by
        rintro rfl; rw [h2] at hp; cases hp
      simp only [Function.update_apply, hr, if_false] at hl
      exact hI.sitBA _ _ hp hl
    · intro r' c' hl
      by_cases hr : r' = r
      · subst hr
        simp only [Function.update_self]
        exact Submodule.zero_mem _
      · simp only [Function.update_apply, hr, if_false] at hl ⊢
        exact hm _ (hI.csrow _ _ hl)
    · intro r' d hx
      obtain ⟨c3, hc, hmem⟩ := hI.csent _ _ hx
      exact ⟨c3, hc, hm _ hmem⟩
    · intro r' c' hx hl
      apply hI.stops _ _ hx
      intro hl'
      apply hl
      simp [Function.update_apply, hne' _ _ hx, hl']
  | gate r c0 coef h1 =>
    refine ⟨hI.bpub, hI.apub, hI.bornU, hI.bpos, hI.apos, hI.disj, hI.sitBA, ?_, ?_, hI.stops⟩
    · intro r' c' hl
      by_cases hr : r' = r
      · subst hr
        have hc : c' = c0 := by
          have := hl; simp at this; rw [h1] at this; exact (Loc.sit.inj this).symm
        subst hc
        simp only [Function.update_self]
        refine Submodule.sum_mem _ (fun t ht => Submodule.smul_mem _ _ ?_)
        exact hI.csrow _ _ (by simpa using ht)
      · simp only [Function.update_apply, hr, if_false] at hl ⊢
        exact hI.csrow _ _ hl
    · intro r' d hx
      exact hI.csent _ _ hx
  | movePub r c0 d h1 h2 hcd =>
    have hpos : ∀ {c2 : Ch}, s.loc r = .sit c2 → c2 = c0 := fun h => by
      rw [h1] at h; exact (Loc.sit.inj h).symm
    have hnotA : r ∉ s.A d := by
      intro hx
      obtain ⟨c2, hl, hsub⟩ := hI.apos _ _ hx
      have := hpos hl
      subst this
      exact absurd hcd (not_lt_of_ge hsub)
    have hnotB : r ∉ s.B d := by
      intro hx
      obtain ⟨c2, hl, hsub⟩ := hI.bpos _ _ hx
      have := hpos hl
      subst this
      exact absurd hcd (not_lt_of_ge hsub)
    refine ⟨hI.bpub, ?_, hI.bornU, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
    · intro r' c' hx
      rw [updB_iff] at hx
      rcases hx with ⟨_, rfl⟩ | hx
      · exact h2
      · exact hI.apub _ _ hx
    · intro r' c' hx
      obtain ⟨c3, hl, hs⟩ := hI.bpos _ _ hx
      by_cases hr : r' = r
      · subst hr
        have := hpos hl
        subst this
        exact ⟨d, by simp, hs.trans hcd.subset⟩
      · exact ⟨c3, by simp [Function.update_apply, hr, hl], hs⟩
    · intro r' d' hx
      rw [updB_iff] at hx
      rcases hx with ⟨hc, rfl⟩ | hx
      · exact ⟨d, by simp, hc ▸ subset_rfl⟩
      · obtain ⟨c3, hl, hs⟩ := hI.apos _ _ hx
        by_cases hr : r' = r
        · subst hr
          have := hpos hl
          subst this
          exact ⟨d, by simp, hs.trans hcd.subset⟩
        · exact ⟨c3, by simp [Function.update_apply, hr, hl], hs⟩
    · intro r' c' hx hh
      rw [updB_iff] at hh
      rcases hh with ⟨hc, rfl⟩ | hh
      · exact hnotB (hc ▸ hx)
      · exact hI.disj _ _ hx hh
    · intro r' c' hp hl
      by_cases hr : r' = r
      · subst hr
        simp at hl
        subst hl
        right; rw [updB_iff]; exact Or.inl ⟨rfl, rfl⟩
      · simp only [Function.update_apply, hr, if_false] at hl
        rcases hI.sitBA _ _ hp hl with hb | ha
        · left; exact hb
        · right; rw [updB_iff]; exact Or.inr ha
    · intro r' c' hl
      by_cases hr : r' = r
      · subst hr
        simp at hl
        subst hl
        refine Submodule.subset_span (Or.inl (Or.inr ⟨r', ?_, ?_⟩))
        · simp [updB_iff]
        · simp
      · simp only [Function.update_apply, hr, if_false] at hl
        exact hm _ (hI.csrow _ _ hl)
    · intro r' d' hx
      rw [updB_iff] at hx
      by_cases hc : r' = r ∧ d' = d
      · obtain ⟨rfl, rfl⟩ := hc
        refine ⟨c0, hcd, ?_⟩
        simp only [and_self, if_true]
        exact hm _ (hI.csrow _ _ h1)
      · have hx' : r' ∈ s.A d' := by
          rcases hx with ⟨hc', rfl⟩ | hx
          · exact absurd ⟨rfl, hc'⟩ hc
          · exact hx
        obtain ⟨c3, hlt, hmem⟩ := hI.csent _ _ hx'
        refine ⟨c3, hlt, ?_⟩
        simp only [hc, if_false]
        exact hm _ hmem
    · intro r' c' hx hl
      rw [updB_iff] at hx
      by_cases hr : r' = r
      · subst hr
        by_cases hcc : c' = c0
        · subst hcc
          have : r' ∈ s.A c' := by
            rcases hx with ⟨hc', _⟩ | hx
            · subst hc'; exact absurd hcd (lt_irrefl _)
            · exact hx
          simp [this]
        · have hx' : r' ∈ s.A c' := by
            rcases hx with ⟨hc', _⟩ | hx
            · subst hc'; simp at hl
            · exact hx
          have := hI.stops _ _ hx' (by rw [h1]; intro h; exact hcc (Loc.sit.inj h).symm)
          simp only
          split_ifs
          · exact List.mem_cons_of_mem _ this
          · exact this
      · have hx' : r' ∈ s.A c' := by
          rcases hx with ⟨_, rfl⟩ | hx
          · exact absurd rfl hr
          · exact hx
        have := hI.stops _ _ hx' (by simpa [Function.update_apply, hr] using hl)
        simp only
        split_ifs
        · exact List.mem_cons_of_mem _ this
        · exact this
  | moveOwn r c0 d h1 h2 =>
    have hne : ∀ r' c', r' ∈ s.B c' → r' ≠ r := by
      intro r' c' hx hr; subst hr; rw [hI.bpub _ _ hx] at h2; cases h2
    have hne' : ∀ r' c', r' ∈ s.A c' → r' ≠ r := by
      intro r' c' hx hr; subst hr; rw [hI.apub _ _ hx] at h2; cases h2
    refine ⟨hI.bpub, hI.apub, hI.bornU, ?_, ?_, hI.disj, ?_, ?_, ?_, ?_⟩
    · intro r' c' hx
      obtain ⟨c3, hl, hs⟩ := hI.bpos _ _ hx
      exact ⟨c3, by simp [Function.update_apply, hne _ _ hx, hl], hs⟩
    · intro r' d' hx
      obtain ⟨c3, hl, hs⟩ := hI.apos _ _ hx
      exact ⟨c3, by simp [Function.update_apply, hne' _ _ hx, hl], hs⟩
    · intro r' c' hp hl
      have hr : r' ≠ r := by
        rintro rfl; rw [h2] at hp; cases hp
      simp only [Function.update_apply, hr, if_false] at hl
      exact hI.sitBA _ _ hp hl
    · intro r' c' hl
      by_cases hr : r' = r
      · subst hr
        have hc : c' = d := by
          have := hl; simp at this; exact this.symm
        subst hc
        refine Submodule.subset_span (Or.inr ⟨c0, ?_⟩)
        simp
      · simp only [Function.update_apply, hr, if_false] at hl
        exact hm _ (hI.csrow _ _ hl)
    · intro r' d' hx
      obtain ⟨c3, hc, hmem⟩ := hI.csent _ _ hx
      exact ⟨c3, hc, hm _ hmem⟩
    · intro r' c' hx hl
      apply hI.stops _ _ hx
      intro hl'
      apply hl
      simp [Function.update_apply, hne' _ _ hx, hl']
  | clearOwn r c0 h1 h2 =>
    have hne : ∀ r' c', r' ∈ s.B c' → r' ≠ r := by
      intro r' c' hx hr; subst hr; rw [hI.bpub _ _ hx] at h2; cases h2
    have hne' : ∀ r' c', r' ∈ s.A c' → r' ≠ r := by
      intro r' c' hx hr; subst hr; rw [hI.apub _ _ hx] at h2; cases h2
    refine ⟨hI.bpub, hI.apub, hI.bornU, ?_, ?_, hI.disj, ?_, ?_, ?_, ?_⟩
    · intro r' c' hx
      obtain ⟨c3, hl, hs⟩ := hI.bpos _ _ hx
      exact ⟨c3, by simp [Function.update_apply, hne _ _ hx, hl], hs⟩
    · intro r' d' hx
      obtain ⟨c3, hl, hs⟩ := hI.apos _ _ hx
      exact ⟨c3, by simp [Function.update_apply, hne' _ _ hx, hl], hs⟩
    · intro r' c' hp hl
      have hr : r' ≠ r := by
        rintro rfl; rw [h2] at hp; cases hp
      simp only [Function.update_apply, hr, if_false] at hl
      exact hI.sitBA _ _ hp hl
    · intro r' c' hl
      by_cases hr : r' = r
      · subst hr
        simp at hl
      · simp only [Function.update_apply, hr, if_false] at hl ⊢
        exact hm _ (hI.csrow _ _ hl)
    · intro r' d' hx
      obtain ⟨c3, hc, hmem⟩ := hI.csent _ _ hx
      exact ⟨c3, hc, hm _ hmem⟩
    · intro r' c' hx hl
      apply hI.stops _ _ hx
      intro hl'
      apply hl
      simp [Function.update_apply, hne' _ _ hx, hl']

theorem Inv.of_reach {s : St R} (h : Reach pb s) : Inv pb s := by
  induction h with
  | refl => exact Inv.init
  | tail _ hs ih => exact ih.step hs

end Inv

/-! ## Linear independence from pivots -/

theorem linInd_of_pivot {ι R' : Type} [Fintype ι] [DecidableEq ι] (v : ι → R' → ℚ) (π : ι → R')
    (h1 : ∀ i, v i (π i) ≠ 0) (h2 : ∀ i j, i ≠ j → v i (π j) = 0) : LinearIndependent ℚ v := by
  rw [Fintype.linearIndependent_iff]
  intro g hg i
  have h := congrFun hg (π i)
  simp only [Finset.sum_apply, Pi.smul_apply, smul_eq_mul, Pi.zero_apply] at h
  rw [Finset.sum_eq_single i (fun j _ hj => by rw [h2 j i hj, mul_zero]) (fun h => absurd (mem_univ i) h)] at h
  exact (mul_eq_zero.1 h).resolve_right (h1 i)

/-- no q: q^⊥ is never the two-point line {0,q} (the odd-weight label q is not orthogonal to everything
else): decide-checked witness search. -/
theorem Hq_ne_line (q : ℕ) (hq : q < 512) (hodd : wt q % 2 = 1) : Hq q ≠ line q := by
  have key : ∀ q < 512, wt q % 2 = 1 → ∃ v < 16, 0 < v ∧ v ≠ q ∧ dot v q = 0 := by decide +kernel
  obtain ⟨v, hv16, hv0, hvq, hdot⟩ := key q hq hodd
  intro h
  have hv : v ∈ Hq q := by
    simp only [Hq, mem_filter, mem_range]; exact ⟨by omega, hdot⟩
  rw [h] at hv
  simp only [line, mem_insert, mem_singleton] at hv
  omega

section WordPart
variable {Pt Hl Ow : Type} [Fintype Pt] [Fintype Hl] [Fintype Ow]
  [DecidableEq Pt] [DecidableEq Hl] [DecidableEq Ow]
variable {cl : Caller Pt} {s : St (Reg Pt Hl Ow)}

theorem cs_final (hw : Word cl s) : CSFinal s := (Inv.of_reach hw.reach).csrow
theorem cs_entry (hw : Word cl s) : CSEntry s := (Inv.of_reach hw.reach).csent
theorem born_unique (hw : Word cl s) : BornUnique s := (Inv.of_reach hw.reach).bornU

open Classical in
/-- index set of the independent family F_stay + E_BL at chart c. -/
noncomputable def Sx (cl : Caller Pt) (s : St (Reg Pt Hl Ow)) (c : Ch) : Finset (Reg Pt Hl Ow) :=
  univ.filter (fun r => (pub cl r = true ∧ s.loc r = .sit c) ∨ (r ∈ s.B c ∧ s.loc r ≠ .sit c))

/-- the family: final row of a stayer, unit row of a born leaver. -/
noncomputable def vv (s : St (Reg Pt Hl Ow)) (c : Ch) (r : Reg Pt Hl Ow) : Reg Pt Hl Ow → ℚ :=
  if s.loc r = .sit c then s.row r else Pi.single r 1

theorem x_not_Sx (hw : Word cl s) {c : Ch} (hc : c ≠ Vc) (p : Pt) (hyp : c = Hq (cl.lab p)) :
    Reg.x p ∉ Sx cl s c := by
  have hI := Inv.of_reach hw.reach
  intro hm
  simp only [Sx, mem_filter, mem_univ, true_and] at hm
  rcases hm with ⟨_, hl⟩ | ⟨hb, _⟩
  · rw [hw.x_final p] at hl; exact hc (Loc.sit.inj hl).symm
  · have h := hI.bornU _ _ _ hb (hw.x_birth p)
    exact Hq_ne_line (cl.lab p) (cl.lab_lt p) (cl.lab_odd p) (hyp.symm.trans h)

theorem stayer_shape (hw : Word cl s) {c : Ch} (hc : c ≠ Vc) {r : Reg Pt Hl Ow}
    (hp : pub cl r = true) (hl : s.loc r = .sit c) :
    (∃ i, r = .h i) ∨ (∃ p, r = .y p ∧ c = Hq (cl.lab p)) ∨ (∃ p, r = .y2 p) := by
  cases r with
  | x p => rw [hw.x_final p] at hl; exact absurd (Loc.sit.inj hl).symm hc
  | y p =>
    right; left
    exact ⟨p, rfl, by rw [hw.y_final p] at hl; exact (Loc.sit.inj hl).symm⟩
  | x2 p =>
    have hD : cl.isD p = true := by simpa [pub] using hp
    rw [hw.x2_final p hD] at hl; exact absurd (Loc.sit.inj hl).symm hc
  | y2 p => right; right; exact ⟨p, rfl⟩
  | h i => left; exact ⟨i, rfl⟩
  | o i => simp [pub] at hp

theorem Sx_stay_pub {c : Ch} {r : Reg Pt Hl Ow} (hr : r ∈ Sx cl s c) (hl : s.loc r = .sit c) :
    pub cl r = true := by
  simp only [Sx, mem_filter, mem_univ, true_and] at hr
  rcases hr with ⟨hp, _⟩ | ⟨_, hh⟩
  · exact hp
  · exact absurd hl hh

theorem vv_off (hw : Word cl s) {c : Ch} (hc : c ≠ Vc) {r r' : Reg Pt Hl Ow}
    (hr : r ∈ Sx cl s c) (hr' : r' ∈ Sx cl s c) (hne : r ≠ r') : vv s c r r' = 0 := by
  unfold vv
  by_cases hl : s.loc r = .sit c
  · rw [if_pos hl]
    have hp := Sx_stay_pub hr hl
    rw [hw.final_row r hp]
    rcases stayer_shape hw hc hp hl with ⟨i, rfl⟩ | ⟨p, rfl, hcp⟩ | ⟨p, rfl⟩
    · simp [tgt, e, Pi.single_apply, hne.symm]
    · have hx : r' ≠ Reg.x p := fun h => x_not_Sx hw hc p hcp (h ▸ hr')
      cases hD : cl.isD p <;> simp [tgt, e, Pi.single_apply, hne.symm, hx, hD]
    · simp [tgt, e, Pi.single_apply, hne.symm]
  · rw [if_neg hl]; simp [Pi.single_apply, hne.symm]

theorem vv_diag (hw : Word cl s) {c : Ch} (hc : c ≠ Vc) {r : Reg Pt Hl Ow}
    (hr : r ∈ Sx cl s c) : vv s c r r ≠ 0 := by
  unfold vv
  by_cases hl : s.loc r = .sit c
  · rw [if_pos hl]
    have hp := Sx_stay_pub hr hl
    rw [hw.final_row r hp]
    rcases stayer_shape hw hc hp hl with ⟨i, rfl⟩ | ⟨p, rfl, hcp⟩ | ⟨p, rfl⟩
    · simp [tgt, e]
    · cases hD : cl.isD p <;> simp [tgt, e, Pi.single_apply, hD]
    · simp [tgt, e]
  · rw [if_neg hl]; simp

/-- **slack-rank lemma (R3 §2)** at every chart c ≠ V.  Uses l.51 through `Inv` (apos, disj, csent). -/
theorem slack_rank (hw : Word cl s) : SlackRank (pub cl) s := by
  classical
  have hI := Inv.of_reach hw.reach
  intro c hc
  have hli : LinearIndependent ℚ (fun r : {r // r ∈ Sx cl s c} => vv s c r.1) :=
    linInd_of_pivot _ (fun r => r.1) (fun r => vv_diag hw hc r.2)
      (fun r r' h => vv_off hw hc r.2 r'.2 (fun h' => h (Subtype.ext h')))
  set F : Submodule ℚ (Reg Pt Hl Ow → ℚ) := Submodule.span ℚ (Fstay (pub cl) s c ∪ EBL s c) with hF
  have hFI : F ≤ I s c := by
    refine Submodule.span_le.2 ?_
    rintro v (⟨r, hp, hl, rfl⟩ | ⟨r, ⟨hb, _⟩, rfl⟩)
    · exact hI.csrow r c hl
    · exact Submodule.subset_span (Or.inl (Or.inl ⟨r, hb, rfl⟩))
  have hcardF : (Sx cl s c).card ≤ finrank ℚ F := by
    have h1 := finrank_span_eq_card hli
    have hc' : Fintype.card {x // x ∈ Sx cl s c} = (Sx cl s c).card := Fintype.card_coe _
    rw [← hc', ← h1]
    apply Submodule.finrank_mono
    apply Submodule.span_le.2
    rintro _ ⟨r, rfl⟩
    have hr := r.2
    by_cases hl : s.loc r.1 = .sit c
    · have hp := Sx_stay_pub hr hl
      have : vv s c r.1 = s.row r.1 := by simp [vv, hl]
      show vv s c r.1 ∈ F
      rw [this]
      exact Submodule.subset_span (Or.inl ⟨r.1, hp, hl, rfl⟩)
    · have : vv s c r.1 = Pi.single r.1 1 := by simp [vv, hl]
      simp only [Sx, mem_filter, mem_univ, true_and] at hr
      rcases hr with ⟨_, h⟩ | ⟨hb, _⟩
      · exact absurd h hl
      · show vv s c r.1 ∈ F
        rw [this]
        exact Submodule.subset_span (Or.inr ⟨r.1, ⟨hb, hl⟩, rfl⟩)
  have hfin : finrank ℚ (I s c) ≤
      (s.B c).card + (s.A c).card + s.olog.countP (fun m => decide (m.2.1 = c)) := by
    let T : Finset (Reg Pt Hl Ow → ℚ) :=
      ((s.B c).image (fun r => (Pi.single r (1:ℚ) : Reg Pt Hl Ow → ℚ))) ∪
      ((s.A c).image (fun r => s.eRow r c)) ∪
      ((s.olog.filter (fun m => decide (m.2.1 = c))).map (fun m => m.2.2)).toFinset
    have hsub : I s c ≤ Submodule.span ℚ (T : Set (Reg Pt Hl Ow → ℚ)) := by
      apply Submodule.span_mono
      rintro v ((⟨r, hr, rfl⟩ | ⟨r, hr, rfl⟩) | ⟨a, ha⟩)
      · exact mem_coe.2 (mem_union_left _ (mem_union_left _ (mem_image_of_mem _ hr)))
      · exact mem_coe.2 (mem_union_left _ (mem_union_right _ (mem_image_of_mem _ hr)))
      · refine mem_coe.2 (mem_union_right _ (List.mem_toFinset.2 (List.mem_map.2 ⟨(a, c, v), ?_, rfl⟩)))
        exact List.mem_filter.2 ⟨ha, by simp⟩
    refine (Submodule.finrank_mono hsub).trans ((by simpa [Set.finrank] using finrank_span_finset_le_card (R := ℚ) T : finrank ℚ (Submodule.span ℚ (T : Set (Reg Pt Hl Ow → ℚ))) ≤ T.card).trans ?_)
    refine (card_union_le _ _).trans ?_
    refine Nat.add_le_add ((card_union_le _ _).trans (Nat.add_le_add card_image_le card_image_le)) ?_
    refine (List.toFinset_card_le _).trans ?_
    rw [List.length_map, List.countP_eq_length_filter]
  have hcount : (s.B c).card + (s.A c).card ≤
      (Sx cl s c).card + s.slog.countP (fun t => decide (t.2 = c)) := by
    have hd : Disjoint (s.B c) (s.A c) := Finset.disjoint_left.2 (fun r hb ha => hI.disj r c hb ha)
    rw [← card_union_of_disjoint hd]
    let Lv := (s.A c).filter (fun r => s.loc r ≠ .sit c)
    have h1 : s.B c ∪ s.A c ⊆ Sx cl s c ∪ Lv := by
      intro r hr
      rcases mem_union.1 hr with hb | ha
      · apply mem_union_left
        by_cases hl : s.loc r = .sit c
        · simp only [Sx, mem_filter, mem_univ, true_and]
          exact Or.inl ⟨hI.bpub _ _ hb, hl⟩
        · simp only [Sx, mem_filter, mem_univ, true_and]
          exact Or.inr ⟨hb, hl⟩
      · by_cases hl : s.loc r = .sit c
        · apply mem_union_left
          simp only [Sx, mem_filter, mem_univ, true_and]
          exact Or.inl ⟨hI.apub _ _ ha, hl⟩
        · exact mem_union_right _ (mem_filter.2 ⟨ha, hl⟩)
    have h2 : Lv.card ≤ s.slog.countP (fun t => decide (t.2 = c)) := by
      have hsub : Lv.image (fun r => (r, c)) ⊆
          (s.slog.filter (fun t => decide (t.2 = c))).toFinset := by
        intro x hx
        obtain ⟨r, hr, rfl⟩ := mem_image.1 hx
        obtain ⟨ha, hl⟩ := mem_filter.1 hr
        exact List.mem_toFinset.2 (List.mem_filter.2 ⟨hI.stops r c ha hl, by simp⟩)
      calc Lv.card = (Lv.image (fun r => (r, c))).card :=
            (card_image_of_injective _ (fun a b h => by simpa using h)).symm
        _ ≤ (s.slog.filter (fun t => decide (t.2 = c))).toFinset.card := card_le_card hsub
        _ ≤ (s.slog.filter (fun t => decide (t.2 = c))).length := List.toFinset_card_le _
        _ = _ := List.countP_eq_length_filter.symm
    calc (s.B c ∪ s.A c).card ≤ (Sx cl s c ∪ Lv).card := card_le_card h1
      _ ≤ (Sx cl s c).card + Lv.card := card_union_le _ _
      _ ≤ _ := by omega
  obtain ⟨K0, hK0⟩ := Submodule.exists_isCompl F
  have e : F ⊔ K0 ⊓ I s c = I s c := by
    have := (sup_inf_assoc_of_le K0 hFI).symm
    rwa [hK0.sup_eq_top, top_inf_eq] at this
  refine ⟨K0 ⊓ I s c, ?_, le_of_eq e.symm⟩
  have hdis : F ⊓ (K0 ⊓ I s c) = ⊥ :=
    eq_bot_iff.2 (le_trans (inf_le_inf_left F inf_le_left) hK0.inf_eq_bot.le)
  have hdim := Submodule.finrank_sup_add_finrank_inf_eq F (K0 ⊓ I s c)
  rw [e, hdis, finrank_bot] at hdim
  unfold sigma
  omega

end WordPart

end WordModel
