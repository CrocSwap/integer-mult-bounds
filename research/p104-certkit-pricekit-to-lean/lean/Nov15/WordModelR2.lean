/-
WordModelR2 (lane WORDMODEL, coordinator, Nov 18).  R2 (UE on U_Q, WHOLEFLOOR R2 §1 + MINPREM P2a) on the
shared word model WordModelDefs:  every legal Word has >= 8 owned MOVEs whose target meets Q.
Proof: region chart-span on the up-set U_Q (run invariant `InvU`), a dimension upper bound
(births in U + crossing entries + owned entries into U) and a lower bound via the dual functionals ψ of the
target (ψ r (tgt r') = δ), with φ_q = ψ (z q), z q = Y2_q (D port) / Y_q (B port).
Kernel only: no sorry, no native_decide, no axioms.
-/
import Nov15.WordModelDefs
import Mathlib.LinearAlgebra.Dimension.Constructions
import Mathlib.LinearAlgebra.StdBasis
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas

set_option linter.unusedSectionVars false

namespace WordModel

open Finset SafeRungsClique Module

theorem inUp_mono {c d : Ch} (h : c ≤ d) (hc : InUp c) : InUp d := by
  obtain ⟨p, hp, hpc⟩ := hc; exact ⟨p, hp, h hpc⟩

section Gen
variable {R : Type} [Fintype R] [DecidableEq R] (pb : R → Bool)

/-- a public MOVE crossing into U_Q. -/
def Cross (s : St R) (r : R) (c d : Ch) : Prop := (r, c, d) ∈ s.plog ∧ ¬ InUp c ∧ InUp d

/-- generators of the region span on U_Q. -/
def GUset (s : St R) : Set (R → ℚ) :=
  {v | ∃ r c, InUp c ∧ r ∈ s.B c ∧ v = Pi.single r 1} ∪ {v | ∃ r c d, Cross s r c d ∧ v = s.eRow r d}
    ∪ {v | ∃ a d, InUp d ∧ (a, d, v) ∈ s.olog}

def GU (s : St R) : Submodule ℚ (R → ℚ) := Submodule.span ℚ (GUset s)

structure InvU (s : St R) : Prop where
  ascA : ∀ r d, r ∈ s.A d → ∃ d', d ≤ d' ∧ s.loc r = .sit d'
  ascB : ∀ r c, r ∈ s.B c → ∃ d', c ≤ d' ∧ s.loc r = .sit d'
  pubA : ∀ r d, r ∈ s.A d → pb r = true
  pubB : ∀ r c, r ∈ s.B c → pb r = true
  plogA : ∀ r c d, (r, c, d) ∈ s.plog → r ∈ s.A d
  csU : ∀ r c, s.loc r = .sit c → InUp c → s.row r ∈ GU s
  uniq : ∀ r c d c' d', Cross s r c d → Cross s r c' d' → c = c' ∧ d = d'
  excl : ∀ r c0 c d, r ∈ s.B c0 → InUp c0 → Cross s r c d → False

theorem invU_init : InvU pb (init : St R) where
  ascA := by intro r d h; simp [init] at h
  ascB := by intro r d h; simp [init] at h
  pubA := by intro r d h; simp [init] at h
  pubB := by intro r d h; simp [init] at h
  plogA := by intro r c d h; simp [init] at h
  csU := by intro r c h; simp [init] at h
  uniq := by intro r c d c' d' h; simp [init, Cross] at h
  excl := by intro r c0 c d h; simp [init] at h

theorem GU_mono {s s' : St R} (h : GUset s ⊆ GUset s') : GU s ≤ GU s' := Submodule.span_mono h

theorem step_invU {s s' : St R} (hs : InvU pb s) (h : Step pb s s') : InvU pb s' := by
  cases h with
  | birthPub r c hu hp =>
    have hnA : ∀ d, r ∉ s.A d := by
      intro d hm; obtain ⟨_, _, h'⟩ := hs.ascA r d hm; rw [hu] at h'; cases h'
    have hnB : ∀ d, r ∉ s.B d := by
      intro d hm; obtain ⟨_, _, h'⟩ := hs.ascB r d hm; rw [hu] at h'; cases h'
    have hBsub : ∀ c' x, x ∈ s.B c' → x ∈ Function.update s.B c (insert r (s.B c)) c' := by
      intro c' x hx
      by_cases hc : c' = c
      · subst hc; simp [hx]
      · simp [Function.update_of_ne hc, hx]
    have hsub : GUset s ⊆ GUset ({ s with loc := Function.update s.loc r (.sit c), row := Function.update s.row r (Pi.single r 1), B := Function.update s.B c (insert r (s.B c)) } : St R) := by
      intro v hv
      simp only [GUset, Cross, Set.mem_union, Set.mem_setOf_eq] at hv ⊢
      rcases hv with (⟨x, c', h1, h2, rfl⟩ | h) | h
      · exact Or.inl (Or.inl ⟨x, c', h1, hBsub c' x h2, rfl⟩)
      · exact Or.inl (Or.inr h)
      · exact Or.inr h
    refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
    · intro r' d h'
      have hr : r' ≠ r := by rintro rfl; exact hnA d h'
      obtain ⟨d', h1, h2⟩ := hs.ascA r' d h'
      exact ⟨d', h1, by simpa [Function.update_of_ne hr] using h2⟩
    · intro r' c' h'
      by_cases hr : r' = r
      · subst hr
        by_cases hc : c' = c
        · subst hc; exact ⟨c', le_rfl, by simp⟩
        · simp only [Function.update_of_ne hc] at h'; exact (hnB c' h').elim
      · have h'' : r' ∈ s.B c' := by
          by_cases hc : c' = c
          · subst hc; simpa [hr] using h'
          · simpa [Function.update_of_ne hc] using h'
        obtain ⟨d', h1, h2⟩ := hs.ascB r' c' h''
        exact ⟨d', h1, by simpa [Function.update_of_ne hr] using h2⟩
    · exact hs.pubA
    · intro r' c' h'
      by_cases hr : r' = r
      · subst hr; exact hp
      · have h'' : r' ∈ s.B c' := by
          by_cases hc : c' = c
          · subst hc; simpa [hr] using h'
          · simpa [Function.update_of_ne hc] using h'
        exact hs.pubB r' c' h''
    · exact hs.plogA
    · intro r' c' hl hU
      by_cases hr : r' = r
      · subst hr
        simp only [Function.update_self, Loc.sit.injEq] at hl
        subst hl
        simp only [Function.update_self]
        refine Submodule.subset_span (Or.inl (Or.inl ⟨r', _, hU, by simp, rfl⟩))
      · simp only [Function.update_of_ne hr] at hl ⊢
        exact GU_mono hsub (hs.csU r' c' hl hU)
    · exact hs.uniq
    · intro r' c0 c1 d h1 h2 h3
      by_cases hr : r' = r
      · subst hr; exact hnA d (hs.plogA _ _ _ h3.1)
      · have h'' : r' ∈ s.B c0 := by
          by_cases hc : c0 = c
          · subst hc; simpa [hr] using h1
          · simpa [Function.update_of_ne hc] using h1
        exact hs.excl r' c0 c1 d h'' h2 h3
  | birthOwn r c hu hp =>
    refine ⟨?_, ?_, hs.pubA, hs.pubB, hs.plogA, ?_, hs.uniq, hs.excl⟩
    · intro r' d h'
      have hr : r' ≠ r := by rintro rfl; rw [hs.pubA r' d h'] at hp; cases hp
      obtain ⟨d', h1, h2⟩ := hs.ascA r' d h'
      exact ⟨d', h1, by simpa [Function.update_of_ne hr] using h2⟩
    · intro r' d h'
      have hr : r' ≠ r := by rintro rfl; rw [hs.pubB r' d h'] at hp; cases hp
      obtain ⟨d', h1, h2⟩ := hs.ascB r' d h'
      exact ⟨d', h1, by simpa [Function.update_of_ne hr] using h2⟩
    · intro r' c' hl hU
      by_cases hr : r' = r
      · subst hr; simp only [Function.update_self]; exact Submodule.zero_mem _
      · simp only [Function.update_of_ne hr] at hl ⊢
        exact hs.csU r' c' hl hU
  | gate r c coef hl =>
    refine ⟨hs.ascA, hs.ascB, hs.pubA, hs.pubB, hs.plogA, ?_, hs.uniq, hs.excl⟩
    intro r' c' hl' hU
    by_cases hr : r' = r
    · subst hr
      have hc : c' = c := by have := hl'.symm.trans hl; simpa using this
      subst hc
      simp only [Function.update_self]
      refine Submodule.sum_mem _ fun t ht => Submodule.smul_mem _ _ ?_
      exact hs.csU t c' (by simpa using ht) hU
    · simp only [Function.update_of_ne hr] at hl' ⊢
      exact hs.csU r' c' hl' hU
  | movePub r c d hl hp hlt =>
    -- r never re-enters a chart it entered
    have hnot : ∀ d', r ∈ s.A d' → d' ≤ c := by
      intro d' hm; obtain ⟨d'', h1, h2⟩ := hs.ascA r d' hm; rw [hl] at h2; cases h2; exact h1
    have hnAd : r ∉ s.A d := fun hm => absurd (lt_of_lt_of_le hlt (hnot d hm)) (lt_irrefl _)
    have hcross : ∀ r' c' d', Cross ({ s with loc := Function.update s.loc r (.sit d), A := Function.update s.A d (insert r (s.A d)), eRow := fun r' c' => if r' = r ∧ c' = d then s.row r else s.eRow r' c', slog := if r ∈ s.A c then (r, c) :: s.slog else s.slog, plog := (r, c, d) :: s.plog } : St R) r' c' d' ↔
        (Cross s r' c' d' ∨ ((r', c', d') = (r, c, d) ∧ ¬ InUp c ∧ InUp d)) := by
      intro r' c' d'
      simp only [Cross, List.mem_cons]
      constructor
      · rintro ⟨h1 | h1, h2, h3⟩
        · right; refine ⟨h1, ?_, ?_⟩ <;> simp_all
        · left; exact ⟨h1, h2, h3⟩
      · rintro (⟨h1, h2, h3⟩ | ⟨h1, h2, h3⟩)
        · exact ⟨Or.inr h1, h2, h3⟩
        · simp only [Prod.mk.injEq] at h1; obtain ⟨rfl, rfl, rfl⟩ := h1
          exact ⟨Or.inl rfl, h2, h3⟩
    have hAsub : ∀ d' x, x ∈ s.A d' → x ∈ Function.update s.A d (insert r (s.A d)) d' := by
      intro d' x hx
      by_cases hc : d' = d
      · subst hc; simp [hx]
      · simp [Function.update_of_ne hc, hx]
    have hsub : GUset s ⊆ GUset ({ s with loc := Function.update s.loc r (.sit d), A := Function.update s.A d (insert r (s.A d)), eRow := fun r' c' => if r' = r ∧ c' = d then s.row r else s.eRow r' c', slog := if r ∈ s.A c then (r, c) :: s.slog else s.slog, plog := (r, c, d) :: s.plog } : St R) := by
      intro v hv
      simp only [GUset, Set.mem_union, Set.mem_setOf_eq] at hv ⊢
      rcases hv with (h | ⟨x, c', d', h1, rfl⟩) | h
      · exact Or.inl (Or.inl h)
      · refine Or.inl (Or.inr ⟨x, c', d', (hcross x c' d').2 (Or.inl h1), ?_⟩)
        have : ¬ (x = r ∧ d' = d) := by
          rintro ⟨rfl, rfl⟩; exact hnAd (hs.plogA _ _ _ h1.1)
        simp [this]
      · exact Or.inr h
    refine ⟨?_, ?_, ?_, hs.pubB, ?_, ?_, ?_, ?_⟩
    · intro r' d' h'
      by_cases hr : r' = r
      · subst hr
        refine ⟨d, ?_, by simp⟩
        by_cases hc : d' = d
        · subst hc; exact le_rfl
        · have h'' : r' ∈ s.A d' := by simpa [Function.update_of_ne hc] using h'
          exact le_of_lt (lt_of_le_of_lt (hnot d' h'') hlt)
      · have h'' : r' ∈ s.A d' := by
          by_cases hc : d' = d
          · subst hc; simpa [hr] using h'
          · simpa [Function.update_of_ne hc] using h'
        obtain ⟨d'', h1, h2⟩ := hs.ascA r' d' h''
        exact ⟨d'', h1, by simpa [Function.update_of_ne hr] using h2⟩
    · intro r' c' h'
      obtain ⟨d'', h1, h2⟩ := hs.ascB r' c' h'
      by_cases hr : r' = r
      · subst hr; rw [hl] at h2; cases h2
        exact ⟨d, le_of_lt (lt_of_le_of_lt h1 hlt), by simp⟩
      · exact ⟨d'', h1, by simpa [Function.update_of_ne hr] using h2⟩
    · intro r' d' h'
      by_cases hr : r' = r
      · subst hr; exact hp
      · have h'' : r' ∈ s.A d' := by
          by_cases hc : d' = d
          · subst hc; simpa [hr] using h'
          · simpa [Function.update_of_ne hc] using h'
        exact hs.pubA r' d' h''
    · intro r' c' d' h'
      simp only [List.mem_cons, Prod.mk.injEq] at h'
      rcases h' with ⟨rfl, rfl, rfl⟩ | h'
      · simp
      · exact hAsub _ _ (hs.plogA _ _ _ h')
    · intro r' c' hl' hU
      by_cases hr : r' = r
      · subst hr
        simp only [Function.update_self, Loc.sit.injEq] at hl'
        subst hl'
        by_cases hUc : InUp c
        · exact GU_mono hsub (hs.csU r' c hl hUc)
        · refine Submodule.subset_span (Or.inl (Or.inr ⟨r', c, d, (hcross r' c d).2
            (Or.inr ⟨rfl, hUc, hU⟩), ?_⟩))
          simp
      · simp only [Function.update_of_ne hr] at hl' ⊢
        exact GU_mono hsub (hs.csU r' c' hl' hU)
    · -- a register that crossed before already sits inside U, so it cannot cross again
      have hold : ∀ c' d', Cross s r c' d' → ¬ InUp c → False := by
        intro c' d' h1 hUc
        obtain ⟨d'', h2, h3⟩ := hs.ascA r d' (hs.plogA _ _ _ h1.1)
        rw [hl] at h3; cases h3
        exact hUc (inUp_mono h2 h1.2.2)
      intro r' c1 d1 c2 d2 h1 h2
      rcases (hcross r' c1 d1).1 h1 with o1 | ⟨e1, n1, _⟩ <;>
        rcases (hcross r' c2 d2).1 h2 with o2 | ⟨e2, n2, _⟩
      · exact hs.uniq r' c1 d1 c2 d2 o1 o2
      · simp only [Prod.mk.injEq] at e2; obtain ⟨rfl, rfl, rfl⟩ := e2
        exact (hold c1 d1 o1 n2).elim
      · simp only [Prod.mk.injEq] at e1; obtain ⟨rfl, rfl, rfl⟩ := e1
        exact (hold c2 d2 o2 n1).elim
      · simp only [Prod.mk.injEq] at e1 e2
        obtain ⟨_, rfl, rfl⟩ := e1; obtain ⟨_, rfl, rfl⟩ := e2; exact ⟨rfl, rfl⟩
    · intro r' c0 c1 d1 h1 h2 h3
      rcases (hcross r' c1 d1).1 h3 with h3 | ⟨e3, n3, _⟩
      · exact hs.excl r' c0 c1 d1 h1 h2 h3
      · simp only [Prod.mk.injEq] at e3; obtain ⟨rfl, rfl, rfl⟩ := e3
        obtain ⟨d'', h4, h5⟩ := hs.ascB r' c0 h1
        rw [hl] at h5; cases h5
        exact n3 (inUp_mono h4 h2)
  | moveOwn r c d hl hp =>
    have hnA : ∀ d', r ∉ s.A d' := by
      intro d' hm; rw [hs.pubA r d' hm] at hp; cases hp
    have hnB : ∀ d', r ∉ s.B d' := by
      intro d' hm; rw [hs.pubB r d' hm] at hp; cases hp
    have hsub : GUset s ⊆ GUset ({ s with loc := Function.update s.loc r (.sit d), olog := (c, d, s.row r) :: s.olog } : St R) := by
      intro v hv
      simp only [GUset, Cross, Set.mem_union, Set.mem_setOf_eq, List.mem_cons] at hv ⊢
      rcases hv with (h | h) | ⟨a, d', h1, h2⟩
      · exact Or.inl (Or.inl h)
      · exact Or.inl (Or.inr h)
      · exact Or.inr ⟨a, d', h1, Or.inr h2⟩
    refine ⟨?_, ?_, hs.pubA, hs.pubB, hs.plogA, ?_, hs.uniq, hs.excl⟩
    · intro r' d' h'
      have hr : r' ≠ r := by rintro rfl; exact hnA d' h'
      obtain ⟨d'', h1, h2⟩ := hs.ascA r' d' h'
      exact ⟨d'', h1, by simpa [Function.update_of_ne hr] using h2⟩
    · intro r' d' h'
      have hr : r' ≠ r := by rintro rfl; exact hnB d' h'
      obtain ⟨d'', h1, h2⟩ := hs.ascB r' d' h'
      exact ⟨d'', h1, by simpa [Function.update_of_ne hr] using h2⟩
    · intro r' c' hl' hU
      by_cases hr : r' = r
      · subst hr
        simp only [Function.update_self, Loc.sit.injEq] at hl'
        subst hl'
        exact Submodule.subset_span (Or.inr ⟨c, _, hU, by simp⟩)
      · simp only [Function.update_of_ne hr] at hl' ⊢
        exact GU_mono hsub (hs.csU r' c' hl' hU)
  | clearOwn r c hl hp =>
    have hnA : ∀ d', r ∉ s.A d' := by
      intro d' hm; rw [hs.pubA r d' hm] at hp; cases hp
    have hnB : ∀ d', r ∉ s.B d' := by
      intro d' hm; rw [hs.pubB r d' hm] at hp; cases hp
    refine ⟨?_, ?_, hs.pubA, hs.pubB, hs.plogA, ?_, hs.uniq, hs.excl⟩
    · intro r' d' h'
      have hr : r' ≠ r := by rintro rfl; exact hnA d' h'
      obtain ⟨d'', h1, h2⟩ := hs.ascA r' d' h'
      exact ⟨d'', h1, by simpa [Function.update_of_ne hr] using h2⟩
    · intro r' d' h'
      have hr : r' ≠ r := by rintro rfl; exact hnB d' h'
      obtain ⟨d'', h1, h2⟩ := hs.ascB r' d' h'
      exact ⟨d'', h1, by simpa [Function.update_of_ne hr] using h2⟩
    · intro r' c' hl' hU
      by_cases hr : r' = r
      · subst hr; simp at hl'
      · simp only [Function.update_of_ne hr] at hl' ⊢
        exact hs.csU r' c' hl' hU

theorem reach_invU {s : St R} (h : Reach pb s) : InvU pb s := by
  induction h with
  | refl => exact invU_init pb
  | tail _ hst ih => exact step_invU pb ih hst

end Gen

section Caller
variable {Pt Hl Ow : Type} [Fintype Pt] [Fintype Hl] [Fintype Ow]
  [DecidableEq Pt] [DecidableEq Hl] [DecidableEq Ow] (cl : Caller Pt)

/-- coordinate functional. -/
noncomputable def pr (r : Reg Pt Hl Ow) : (Reg Pt Hl Ow → ℚ) →ₗ[ℚ] ℚ := LinearMap.proj r

/-- dual functionals of the target: ψ r (tgt r') = δ_{r r'} on public registers. -/
noncomputable def ψ : Reg Pt Hl Ow → (Reg Pt Hl Ow → ℚ) →ₗ[ℚ] ℚ
  | .x p => if cl.isD p then pr (.x p) - pr (.y p) else (1/2 : ℚ) • pr (.x p) - (1/2 : ℚ) • pr (.y p)
  | .y p => if cl.isD p then pr (.y p) else pr (.x p) + pr (.y p)
  | .x2 p => pr (.x2 p)
  | .y2 p => pr (.x2 p) + pr (.y2 p)
  | .h i => pr (.h i)
  | .o _ => 0

theorem e_app (r r' : Reg Pt Hl Ow) : (Pi.single r (1 : ℚ) : Reg Pt Hl Ow → ℚ) r' = if r' = r then 1 else 0 := by
  rw [Pi.single_apply]

theorem dual_tgt (r r' : Reg Pt Hl Ow) (hr : pub cl r = true) (hr' : pub cl r' = true) :
    ψ cl r (tgt cl r') = if r = r' then 1 else 0 := by
  rcases r with p|p|p|p|i|i <;> rcases r' with p'|p'|p'|p'|i'|i' <;>
    simp only [pub] at hr hr' <;>
    simp [ψ, tgt, pr, e, e_app] <;>
    (try split_ifs) <;> (try simp_all [e_app]) <;> (try norm_num) <;> (rintro rfl; simp_all)

/-- z p: φ_p = ψ (z p);  w p: the hosted/live X born at ⟨p⟩ that φ_p detects. -/
def zr (p : Pt) : Reg Pt Hl Ow := if cl.isD p then .y2 p else .y p
def wr (p : Pt) : Reg Pt Hl Ow := if cl.isD p then .x2 p else .x p

theorem pub_zr (p : Pt) : pub cl (zr (Hl := Hl) (Ow := Ow) cl p) = true := by
  unfold zr; cases h : cl.isD p <;> simp [pub, h]

theorem psi_z_w (p p' : Pt) :
    ψ cl (zr (Hl := Hl) (Ow := Ow) cl p') (e (wr cl p)) = if p' = p then 1 else 0 := by
  unfold zr wr
  cases h : cl.isD p <;> cases h' : cl.isD p' <;>
    simp [ψ, pr, e, e_app, h'] <;> (try split_ifs) <;> (try simp_all) <;> (rintro rfl; simp_all)

theorem not_inUp_Hq (q : ℕ) (hq : q ∈ Q) : ¬ InUp (Hq q) := by
  rintro ⟨p, hp, hpH⟩
  simp only [Hq, Finset.mem_filter] at hpH
  have := Q_dot_one p hp q hq
  omega

open Classical in
/-- **R2**: every legal word has >= 8 owned MOVEs entering U_Q. -/
theorem R2 {s : St (Reg Pt Hl Ow)} (hw : Word cl s) : 8 ≤ nR2 s := by
  have inv := reach_invU (pub cl) hw.reach
  set Res : Finset (Reg Pt Hl Ow) := univ.filter (fun r => ∃ c, InUp c ∧ s.loc r = .sit c) with hRes
  set Qp : Finset Pt := univ.filter (fun p => cl.lab p ∈ Q) with hQp
  have hQp8 : Qp.card = 8 := by
    have himg : Qp.image cl.lab = Q.toFinset := by
      ext q
      simp only [hQp, Finset.mem_image, Finset.mem_filter, Finset.mem_univ, true_and, List.mem_toFinset]
      constructor
      · rintro ⟨p, hp, rfl⟩; exact hp
      · intro hq; obtain ⟨p, rfl⟩ := cl.Q_sub q hq; exact ⟨p, hq, rfl⟩
    rw [← Finset.card_image_of_injective Qp cl.lab_inj, himg]; rfl
  have hpubRes : ∀ r ∈ Res, pub cl r = true := by
    intro r hr
    obtain ⟨c, _, hc⟩ := (Finset.mem_filter.1 hr).2
    cases h : pub cl r
    · exact absurd hc (hw.own_off r c h)
    · rfl
  have hzRes : ∀ p ∈ Qp, zr (Hl := Hl) (Ow := Ow) cl p ∉ Res := by
    intro p hp hz
    obtain ⟨c, hU, hc⟩ := (Finset.mem_filter.1 hz).2
    have hq : cl.lab p ∈ Q := (Finset.mem_filter.1 hp).2
    have hfin : s.loc (zr cl p) = .sit (Hq (cl.lab p)) := by
      unfold zr; cases h : cl.isD p
      · simpa [h] using hw.y_final p
      · simpa [h] using hw.y2_final p h
    rw [hfin] at hc; cases hc
    exact not_inUp_Hq _ hq hU
  -- upper bound: births in U + crossings + owned entries into U
  have hup : finrank ℚ (GU s) ≤ Res.card + nR2 s := by
    set BU : Finset (Reg Pt Hl Ow) := univ.filter (fun r => ∃ c, InUp c ∧ r ∈ s.B c) with hBU
    set XU : Finset (Reg Pt Hl Ow) := univ.filter (fun r => ∃ c d, Cross s r c d) with hXU
    let dp : Reg Pt Hl Ow → Ch := fun r =>
      if h : ∃ q : Ch × Ch, Cross s r q.1 q.2 then (Classical.choose h).2 else ∅
    have hdp : ∀ r c d, Cross s r c d → dp r = d := by
      intro r c d hC
      have h : ∃ q : Ch × Ch, Cross s r q.1 q.2 := ⟨(c, d), hC⟩
      simp only [dp, dif_pos h]
      exact (inv.uniq _ _ _ _ _ (Classical.choose_spec h) hC).2
    set OL := (s.olog.filter (fun m => decide (InUp m.2.1))).toFinset with hOL
    set T := BU.image (fun r => (Pi.single r (1 : ℚ) : Reg Pt Hl Ow → ℚ)) ∪
      XU.image (fun r => s.eRow r (dp r)) ∪ OL.image (fun m => m.2.2) with hT
    have hsub : GUset s ⊆ ↑T := by
      intro v hv
      simp only [GUset, Set.mem_union, Set.mem_setOf_eq] at hv
      simp only [hT, Finset.coe_union, Finset.coe_image, Set.mem_union, Set.mem_image, Finset.mem_coe]
      rcases hv with (⟨r, c, hU, hB, rfl⟩ | ⟨r, c, d, hC, rfl⟩) | ⟨a, d, hU, hm⟩
      · exact Or.inl (Or.inl ⟨r, by simp [hBU]; exact ⟨c, hU, hB⟩, rfl⟩)
      · exact Or.inl (Or.inr ⟨r, by simp [hXU]; exact ⟨c, d, hC⟩, by rw [hdp r c d hC]⟩)
      · exact Or.inr ⟨(a, d, v), by simp [hOL, hm, hU], rfl⟩
    have h1 : finrank ℚ (GU s) ≤ T.card :=
      (Submodule.finrank_mono (Submodule.span_mono hsub)).trans (finrank_span_finset_le_card T)
    have h2 : T.card ≤ BU.card + XU.card + OL.card :=
      (Finset.card_union_le _ _).trans (add_le_add ((Finset.card_union_le _ _).trans
        (add_le_add Finset.card_image_le Finset.card_image_le)) Finset.card_image_le)
    have h3 : OL.card ≤ nR2 s := by
      refine (List.toFinset_card_le _).trans ?_
      simp [nR2, List.countP_eq_length_filter]
    have hdisj : Disjoint BU XU := by
      rw [Finset.disjoint_left]
      intro r hb hx
      obtain ⟨c0, hU, hB⟩ := (Finset.mem_filter.1 hb).2
      obtain ⟨c, d, hC⟩ := (Finset.mem_filter.1 hx).2
      exact inv.excl r c0 c d hB hU hC
    have hsubR : BU ∪ XU ⊆ Res := by
      intro r hr
      simp only [hRes, Finset.mem_filter, Finset.mem_univ, true_and]
      rcases Finset.mem_union.1 hr with hb | hx
      · obtain ⟨c0, hU, hB⟩ := (Finset.mem_filter.1 hb).2
        obtain ⟨d', h1, h2⟩ := inv.ascB r c0 hB
        exact ⟨d', inUp_mono h1 hU, h2⟩
      · obtain ⟨c, d, hC⟩ := (Finset.mem_filter.1 hx).2
        obtain ⟨d', h1, h2⟩ := inv.ascA r d (inv.plogA _ _ _ hC.1)
        exact ⟨d', inUp_mono h1 hC.2.2, h2⟩
    have h4 : BU.card + XU.card ≤ Res.card := by
      rw [← Finset.card_union_of_disjoint hdisj]; exact Finset.card_le_card hsubR
    omega
  -- lower bound: the dual map is onto (ℚ^Res × ℚ^Qp)
  have hlo : Res.card + 8 ≤ finrank ℚ (GU s) := by
    let ι := {r // r ∈ Res} ⊕ {p // p ∈ Qp}
    let L : (Reg Pt Hl Ow → ℚ) →ₗ[ℚ] (ι → ℚ) :=
      LinearMap.pi (fun i => Sum.elim (fun r => ψ cl r.1) (fun p => ψ cl (zr cl p.1)) i)
    have hLapp : ∀ v i, L v i = Sum.elim (fun r => ψ cl r.1) (fun p => ψ cl (zr cl p.1)) i v := by
      intro v i; rfl
    have htgtGU : ∀ r ∈ Res, tgt cl r ∈ GU s := by
      intro r hr
      obtain ⟨c, hU, hc⟩ := (Finset.mem_filter.1 hr).2
      rw [← hw.final_row r (hpubRes r hr)]; exact inv.csU r c hc hU
    have hwGU : ∀ p ∈ Qp, e (wr (Hl := Hl) (Ow := Ow) cl p) ∈ GU s := by
      intro p hp
      have hq : cl.lab p ∈ Q := (Finset.mem_filter.1 hp).2
      have hU : InUp (line (cl.lab p)) := ⟨cl.lab p, hq, by simp [line]⟩
      have hB : wr (Hl := Hl) (Ow := Ow) cl p ∈ s.B (line (cl.lab p)) := by
        unfold wr; cases h : cl.isD p
        · simpa [h] using hw.x_birth p
        · simpa [h] using hw.x2_birth p h
      exact Submodule.subset_span (Or.inl (Or.inl ⟨_, _, hU, hB, rfl⟩))
    have hLt : ∀ r (hr : r ∈ Res), L (tgt cl r) = Pi.single (Sum.inl ⟨r, hr⟩) 1 := by
      intro r hr; funext i; rw [hLapp]
      rcases i with ⟨r', hr'⟩ | ⟨p, hp⟩
      · simp only [Sum.elim_inl]
        rw [dual_tgt cl r' r (hpubRes r' hr') (hpubRes r hr)]
        by_cases h : r' = r
        · subst h; simp
        · rw [if_neg h, Pi.single_apply, if_neg]; intro h'; exact h (by simpa using h')
      · simp only [Sum.elim_inr]
        rw [dual_tgt cl _ r (pub_zr cl p) (hpubRes r hr), if_neg, Pi.single_apply, if_neg]
        · simp
        · rintro rfl; exact hzRes p hp hr
    have hsurj : ∀ i, (Pi.single i (1 : ℚ) : ι → ℚ) ∈ (GU s).map L := by
      rintro (⟨r, hr⟩ | ⟨p, hp⟩)
      · exact ⟨tgt cl r, htgtGU r hr, hLt r hr⟩
      · refine ⟨e (wr cl p) - ∑ r ∈ Res.attach, ψ cl r.1 (e (wr cl p)) • tgt cl r.1, ?_, ?_⟩
        · exact Submodule.sub_mem _ (hwGU p hp)
            (Submodule.sum_mem _ fun r _ => Submodule.smul_mem _ _ (htgtGU r.1 r.2))
        · rw [map_sub, map_sum]
          simp only [map_smul]
          rw [Finset.sum_congr rfl (fun r _ => by rw [hLt r.1 r.2])]
          funext i
          rw [Pi.sub_apply, Finset.sum_apply, hLapp]
          rcases i with ⟨r', hr'⟩ | ⟨p', hp'⟩
          · simp only [Sum.elim_inl, Pi.smul_apply, Pi.single_apply, smul_eq_mul, mul_ite, mul_one,
              mul_zero, Sum.inl.injEq, reduceCtorEq, if_false]
            rw [Finset.sum_eq_single ⟨r', hr'⟩
              (fun b _ hb => if_neg (fun h => hb (Subtype.ext (congrArg Subtype.val h).symm)))
              (fun h => absurd (Finset.mem_attach _ _) h)]
            simp
          · simp only [Sum.elim_inr, Pi.smul_apply, Pi.single_apply, smul_eq_mul, reduceCtorEq,
              if_false, mul_zero, Finset.sum_const_zero, sub_zero, Sum.inr.injEq]
            rw [psi_z_w cl p p']
            by_cases h : p' = p
            · subst h; simp
            · rw [if_neg h, if_neg]; intro h'; exact h (congrArg Subtype.val (Sum.inr_injective h'))
    have htop : (GU s).map L = ⊤ := by
      rw [eq_top_iff, ← (Pi.basisFun ℚ ι).span_eq, Submodule.span_le]
      rintro _ ⟨i, rfl⟩
      rw [Pi.basisFun_apply]; exact hsurj i
    have hcard : finrank ℚ ((GU s).map L) = Res.card + 8 := by
      rw [htop, finrank_top, Module.finrank_fintype_fun_eq_card, Fintype.card_sum,
        Fintype.card_coe, Fintype.card_coe, hQp8]
    rw [← hcard]; exact Submodule.finrank_map_le L (GU s)
  omega

end Caller

end WordModel

#print axioms WordModel.reach_invU
#print axioms WordModel.R2
