/-
WholeFloorModel : WHOLEFLOOR R3 §1-2 in Lean.
The time-ordered model M, CS (chart span), and the SLACK-RANK lemma. See WholeFloor.md.

Model (R3 §1, R2 §1): registers `Reg` with rows in `W = Reg → K` (initial-row coordinates), charts `C`
(partial order = proper inclusion of spans). Public registers are born with the unit row e_r; owned
registers are INITed with row 0 (R5 "owned INIT rows are 0"). Public MOVEs strictly ascend, owned
MOVEs go anywhere; an owned register may be CLEARed, a public one never is. Gates (ADD / SCALE / COPY
are all special cases) set a register's row to a linear combination of rows of registers at the SAME
chart. Ghost data record the generators of I_C: B C = public registers born at C, A C = public
entrants (with eRow = row at entry), O C = rows of owned MOVEs into C.
-/
import Mathlib.LinearAlgebra.Span.Basic
import Mathlib.LinearAlgebra.Dimension.Finrank
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.LinearAlgebra.LinearIndependent.Lemmas
import Mathlib.LinearAlgebra.Pi
import Mathlib.Algebra.BigOperators.Fin

set_option linter.unusedSectionVars false

namespace WholeFloor

open Module Finset

inductive Loc (C : Type*)
  | unborn
  | sit (c : C)
  | cleared

variable {K Reg C : Type*}

/-- the ghosted run state. -/
structure St (K Reg C : Type*) where
  loc : Reg → Loc C
  row : Reg → Reg → K
  B : C → Finset Reg
  A : C → Finset Reg
  eRow : Reg → C → Reg → K
  O : C → List (Reg → K)

section Model
variable [Field K] [Fintype Reg] [DecidableEq Reg] [DecidableEq C] [PartialOrder C]
  (pub : Reg → Prop)

open Classical in
/-- the initial state: nothing born. -/
def init : St K Reg C := ⟨fun _ => .unborn, fun _ => 0, fun _ => ∅, fun _ => ∅, fun _ _ => 0, fun _ => []⟩

open Classical in
/-- one event of the model. -/
inductive Step : St K Reg C → St K Reg C → Prop
  | birthPub (s : St K Reg C) (r : Reg) (c : C) : s.loc r = .unborn → pub r →
      Step s { s with loc := Function.update s.loc r (.sit c),
                      row := Function.update s.row r (Pi.single r 1),
                      B := Function.update s.B c (insert r (s.B c)) }
  | birthOwn (s : St K Reg C) (r : Reg) (c : C) : s.loc r = .unborn → ¬ pub r →
      Step s { s with loc := Function.update s.loc r (.sit c),
                      row := Function.update s.row r 0 }
  | gate (s : St K Reg C) (r : Reg) (c : C) (coef : Reg → K) : s.loc r = .sit c →
      Step s { s with row := Function.update s.row r (∑ t ∈ univ.filter (fun t => s.loc t = .sit c), coef t • s.row t) }
  | movePub (s : St K Reg C) (r : Reg) (c d : C) : s.loc r = .sit c → pub r → c < d →
      Step s { s with loc := Function.update s.loc r (.sit d),
                      A := Function.update s.A d (insert r (s.A d)),
                      eRow := fun r' c' => if r' = r ∧ c' = d then s.row r else s.eRow r' c' }
  | moveOwn (s : St K Reg C) (r : Reg) (c d : C) : s.loc r = .sit c → ¬ pub r →
      Step s { s with loc := Function.update s.loc r (.sit d),
                      O := Function.update s.O d (s.row r :: s.O d) }
  | clearOwn (s : St K Reg C) (r : Reg) (c : C) : s.loc r = .sit c → ¬ pub r →
      Step s { s with loc := Function.update s.loc r .cleared,
                      row := Function.update s.row r 0 }

/-- reachable states. -/
def Reach (s : St K Reg C) : Prop := Relation.ReflTransGen (Step pub) init s

/-- generators of I_C: unit rows of public births at C, rows of public entrants at their entry,
rows of owned MOVEs into C. -/
def gens (s : St K Reg C) (c : C) : Set (Reg → K) :=
  (fun r => (Pi.single r (1 : K) : Reg → K)) '' ↑(s.B c) ∪ (fun r => s.eRow r c) '' ↑(s.A c)
    ∪ {v | v ∈ s.O c}

/-- I_C of R3 §1. -/
def I (s : St K Reg C) (c : C) : Submodule K (Reg → K) := Submodule.span K (gens s c)

/-- the invariants carried along every run. -/
structure Inv (s : St K Reg C) : Prop where
  cs : ∀ r c, s.loc r = .sit c → s.row r ∈ I s c
  stay : ∀ r c, pub r → s.loc r = .sit c → r ∈ s.B c ∨ r ∈ s.A c
  disj : ∀ c, Disjoint (s.B c) (s.A c)
  asc : ∀ r c, (r ∈ s.B c ∨ r ∈ s.A c) → ∃ d, c ≤ d ∧ s.loc r = .sit d
  pubBA : ∀ r c, (r ∈ s.B c ∨ r ∈ s.A c) → pub r

omit [Fintype Reg] in
theorem inv_init : Inv pub (init : St K Reg C) where
  cs := by intro r c h; simp [init] at h
  stay := by intro r c _ h; simp [init] at h
  disj := by intro c; simp [init]
  asc := by intro r c h; simp [init] at h
  pubBA := by intro r c h; simp [init] at h

theorem I_mono {s s' : St K Reg C} (h : ∀ c, gens s c ⊆ gens s' c) (c : C) : I s c ≤ I s' c :=
  Submodule.span_mono (h c)

theorem step_inv {s s' : St K Reg C} (hs : Inv pub s) (h : Step pub s s') : Inv pub s' := by
  cases h with
  | birthPub r c hu hp =>
    have hsub : ∀ c', gens s c' ⊆ gens
        ({ s with loc := Function.update s.loc r (.sit c),
                  row := Function.update s.row r (Pi.single r 1),
                  B := Function.update s.B c (insert r (s.B c)) } : St K Reg C) c' := by
      intro c' x hx
      simp only [gens, Set.mem_union, Set.mem_image, Finset.mem_coe, Set.mem_setOf_eq] at hx ⊢
      rcases hx with (⟨y, hy, rfl⟩ | ⟨y, hy, rfl⟩) | hx
      · left; left; refine ⟨y, ?_, rfl⟩
        by_cases hc : c' = c
        · subst hc; simp [hy]
        · simp [hc, hy]
      · left; right; exact ⟨y, hy, rfl⟩
      · right; exact hx
    have hnb : ∀ c', r ∉ s.B c' ∧ r ∉ s.A c' := by
      intro c'; constructor <;> intro hm
      · obtain ⟨d, _, hd⟩ := hs.asc r c' (Or.inl hm); rw [hu] at hd; cases hd
      · obtain ⟨d, _, hd⟩ := hs.asc r c' (Or.inr hm); rw [hu] at hd; cases hd
    refine ⟨?_, ?_, ?_, ?_, ?_⟩
    · intro r' c' hl
      by_cases hr : r' = r
      · subst hr
        simp only [Function.update_self, Loc.sit.injEq] at hl
        subst hl
        simp only [Function.update_self]
        exact Submodule.subset_span (Or.inl (Or.inl ⟨r', by simp, by simp⟩))
      · simp only [Function.update_of_ne hr] at hl ⊢
        exact I_mono hsub c' (hs.cs r' c' hl)
    · intro r' c' hp' hl
      by_cases hr : r' = r
      · subst hr
        simp only [Function.update_self, Loc.sit.injEq] at hl
        subst hl; left; simp
      · simp only [Function.update_of_ne hr] at hl
        rcases hs.stay r' c' hp' hl with h | h
        · left; by_cases hc : c' = c
          · subst hc; simp [h]
          · simp [Function.update_of_ne hc, h]
        · right; exact h
    · intro c'
      by_cases hc : c' = c
      · subst hc
        simp only [Function.update_self]
        rw [Finset.disjoint_insert_left]
        exact ⟨(hnb c').2, hs.disj c'⟩
      · simpa [Function.update_of_ne hc] using hs.disj c'
    · intro r' c' h
      by_cases hr : r' = r
      · subst hr
        by_cases hc : c' = c
        · subst hc; exact ⟨c', le_rfl, by simp⟩
        · simp only [Function.update_of_ne hc] at h
          rcases h with h | h
          · exact ((hnb c').1 h).elim
          · exact ((hnb c').2 h).elim
      · have h' : r' ∈ s.B c' ∨ r' ∈ s.A c' := by
          by_cases hc : c' = c
          · subst hc; simpa [hr] using h
          · simpa [Function.update_of_ne hc] using h
        obtain ⟨d, hd, hl⟩ := hs.asc r' c' h'
        exact ⟨d, hd, by simpa [Function.update_of_ne hr] using hl⟩
    · intro r' c' h
      by_cases hr : r' = r
      · subst hr; exact hp
      · have h' : r' ∈ s.B c' ∨ r' ∈ s.A c' := by
          by_cases hc : c' = c
          · subst hc; simpa [hr] using h
          · simpa [Function.update_of_ne hc] using h
        exact hs.pubBA r' c' h'
  | birthOwn r c hu hp =>
    refine ⟨?_, ?_, ?_, ?_, ?_⟩
    · intro r' c' hl
      by_cases hr : r' = r
      · subst hr; simp only [Function.update_self]; exact Submodule.zero_mem _
      · simp only [Function.update_of_ne hr] at hl ⊢
        exact hs.cs r' c' hl
    · intro r' c' hp' hl
      by_cases hr : r' = r
      · subst hr; exact (hp hp').elim
      · simp only [Function.update_of_ne hr] at hl
        exact hs.stay r' c' hp' hl
    · exact hs.disj
    · intro r' c' h
      obtain ⟨d, hd, hl⟩ := hs.asc r' c' h
      have hr : r' ≠ r := by rintro rfl; rw [hu] at hl; cases hl
      exact ⟨d, hd, by simpa [Function.update_of_ne hr] using hl⟩
    · exact hs.pubBA
  | gate r c coef hl =>
    refine ⟨?_, ?_, ?_, ?_, ?_⟩
    · intro r' c' hl'
      by_cases hr : r' = r
      · subst hr
        have hc : c' = c := by
          have := hl'.symm.trans hl; simpa using this
        subst hc
        simp only [Function.update_self]
        refine Submodule.sum_mem _ fun t ht => Submodule.smul_mem _ _ ?_
        exact hs.cs t c' (by simpa using ht)
      · simp only [Function.update_of_ne hr] at hl' ⊢
        exact hs.cs r' c' hl'
    · exact hs.stay
    · exact hs.disj
    · exact hs.asc
    · exact hs.pubBA
  | movePub r c d hl hp hlt =>
    have hnB : r ∉ s.B d := by
      intro hm
      obtain ⟨d', hd, hl'⟩ := hs.asc r d (Or.inl hm)
      rw [hl] at hl'; cases hl'; exact absurd hlt (not_lt_of_ge hd)
    have hnA : r ∉ s.A d := by
      intro hm
      obtain ⟨d', hd, hl'⟩ := hs.asc r d (Or.inr hm)
      rw [hl] at hl'; cases hl'; exact absurd hlt (not_lt_of_ge hd)
    have hsub : ∀ c', gens s c' ⊆ gens
        ({ s with loc := Function.update s.loc r (.sit d),
                  A := Function.update s.A d (insert r (s.A d)),
                  eRow := fun r' c' => if r' = r ∧ c' = d then s.row r else s.eRow r' c' } : St K Reg C) c' := by
      intro c' x hx
      simp only [gens, Set.mem_union, Set.mem_image, Finset.mem_coe, Set.mem_setOf_eq] at hx ⊢
      rcases hx with (⟨y, hy, rfl⟩ | ⟨y, hy, rfl⟩) | hx
      · left; left; exact ⟨y, hy, rfl⟩
      · left; right
        refine ⟨y, ?_, ?_⟩
        · by_cases hc : c' = d
          · subst hc; simp [hy]
          · simp [hc, hy]
        · have : ¬ (y = r ∧ c' = d) := by
            rintro ⟨rfl, rfl⟩; exact hnA hy
          simp [this]
      · right; exact hx
    refine ⟨?_, ?_, ?_, ?_, ?_⟩
    · intro r' c' hl'
      by_cases hr : r' = r
      · subst hr
        simp only [Function.update_self, Loc.sit.injEq] at hl'
        subst hl'
        refine Submodule.subset_span (Or.inl (Or.inr ⟨r', by simp, by simp⟩))
      · simp only [Function.update_of_ne hr] at hl' ⊢
        exact I_mono hsub c' (hs.cs r' c' hl')
    · intro r' c' hp' hl'
      by_cases hr : r' = r
      · subst hr
        simp only [Function.update_self, Loc.sit.injEq] at hl'
        subst hl'; right; simp
      · simp only [Function.update_of_ne hr] at hl'
        rcases hs.stay r' c' hp' hl' with h | h
        · left; exact h
        · right; by_cases hc : c' = d
          · subst hc; simp [h]
          · simp [Function.update_of_ne hc, h]
    · intro c'
      by_cases hc : c' = d
      · subst hc
        simp only [Function.update_self]
        rw [Finset.disjoint_insert_right]
        exact ⟨hnB, hs.disj c'⟩
      · simpa [Function.update_of_ne hc] using hs.disj c'
    · intro r' c' h
      by_cases hr : r' = r
      · subst hr
        refine ⟨d, ?_, by simp⟩
        by_cases hc : c' = d
        · subst hc; exact le_rfl
        · have h' : r' ∈ s.B c' ∨ r' ∈ s.A c' := by simpa [Function.update_of_ne hc] using h
          obtain ⟨d', hd', hl'⟩ := hs.asc r' c' h'
          rw [hl] at hl'; cases hl'; exact le_of_lt (lt_of_le_of_lt hd' hlt)
      · have h' : r' ∈ s.B c' ∨ r' ∈ s.A c' := by
          by_cases hc : c' = d
          · subst hc; simpa [hr] using h
          · simpa [Function.update_of_ne hc] using h
        obtain ⟨d', hd', hl'⟩ := hs.asc r' c' h'
        exact ⟨d', hd', by simpa [Function.update_of_ne hr] using hl'⟩
    · intro r' c' h
      by_cases hr : r' = r
      · subst hr; exact hp
      · have h' : r' ∈ s.B c' ∨ r' ∈ s.A c' := by
          by_cases hc : c' = d
          · subst hc; simpa [hr] using h
          · simpa [Function.update_of_ne hc] using h
        exact hs.pubBA r' c' h'
  | moveOwn r c d hl hp =>
    have hsub : ∀ c', gens s c' ⊆ gens
        ({ s with loc := Function.update s.loc r (.sit d),
                  O := Function.update s.O d (s.row r :: s.O d) } : St K Reg C) c' := by
      intro c' x hx
      simp only [gens, Set.mem_union, Set.mem_image, Finset.mem_coe, Set.mem_setOf_eq] at hx ⊢
      rcases hx with (⟨y, hy, rfl⟩ | ⟨y, hy, rfl⟩) | hx
      · left; left; exact ⟨y, hy, rfl⟩
      · left; right; exact ⟨y, hy, rfl⟩
      · right
        by_cases hc : c' = d
        · subst hc; simp [hx]
        · simp [hc, hx]
    refine ⟨?_, ?_, ?_, ?_, ?_⟩
    · intro r' c' hl'
      by_cases hr : r' = r
      · subst hr
        simp only [Function.update_self, Loc.sit.injEq] at hl'
        subst hl'
        exact Submodule.subset_span (Or.inr (by simp))
      · simp only [Function.update_of_ne hr] at hl' ⊢
        exact I_mono hsub c' (hs.cs r' c' hl')
    · intro r' c' hp' hl'
      by_cases hr : r' = r
      · subst hr; exact (hp hp').elim
      · simp only [Function.update_of_ne hr] at hl'
        exact hs.stay r' c' hp' hl'
    · exact hs.disj
    · intro r' c' h
      have hr : r' ≠ r := by rintro rfl; exact hp (hs.pubBA r' c' h)
      obtain ⟨d', hd', hl'⟩ := hs.asc r' c' h
      exact ⟨d', hd', by simpa [Function.update_of_ne hr] using hl'⟩
    · exact hs.pubBA
  | clearOwn r c hl hp =>
    refine ⟨?_, ?_, ?_, ?_, ?_⟩
    · intro r' c' hl'
      by_cases hr : r' = r
      · subst hr; simp at hl'
      · simp only [Function.update_of_ne hr] at hl' ⊢
        exact hs.cs r' c' hl'
    · intro r' c' hp' hl'
      by_cases hr : r' = r
      · subst hr; exact (hp hp').elim
      · simp only [Function.update_of_ne hr] at hl'
        exact hs.stay r' c' hp' hl'
    · exact hs.disj
    · intro r' c' h
      have hr : r' ≠ r := by rintro rfl; exact hp (hs.pubBA r' c' h)
      obtain ⟨d', hd', hl'⟩ := hs.asc r' c' h
      exact ⟨d', hd', by simpa [Function.update_of_ne hr] using hl'⟩
    · exact hs.pubBA

theorem reach_inv {s : St K Reg C} (h : Reach pub s) : Inv pub s := by
  induction h with
  | refl => exact inv_init pub
  | tail _ hst ih => exact step_inv pub ih hst

/-- generators only grow along a run (the overwritten `eRow r d` is a fresh entry, by `asc`). -/
theorem step_gens_mono {s s' : St K Reg C} (hs : Inv pub s) (h : Step pub s s') :
    ∀ c, gens s c ⊆ gens s' c := by
  intro c' x hx
  simp only [gens, Set.mem_union, Set.mem_image, Finset.mem_coe, Set.mem_ofPred_eq] at hx ⊢
  cases h with
  | birthPub r c hu hp =>
    rcases hx with (⟨y, hy, rfl⟩ | ⟨y, hy, rfl⟩) | hx
    · left; left; refine ⟨y, ?_, rfl⟩
      by_cases hc : c' = c
      · subst hc; simp [hy]
      · simp [hc, hy]
    · left; right; exact ⟨y, hy, rfl⟩
    · right; exact hx
  | birthOwn r c hu hp => exact hx
  | gate r c coef hl => exact hx
  | movePub r c d hl hp hlt =>
    have hnA : r ∉ s.A d := by
      intro hm
      obtain ⟨d', hd, hl'⟩ := hs.asc r d (Or.inr hm)
      rw [hl] at hl'; cases hl'; exact absurd hlt (not_lt_of_ge hd)
    rcases hx with (⟨y, hy, rfl⟩ | ⟨y, hy, rfl⟩) | hx
    · left; left; exact ⟨y, hy, rfl⟩
    · left; right
      refine ⟨y, ?_, ?_⟩
      · by_cases hc : c' = d
        · subst hc; simp [hy]
        · simp [hc, hy]
      · have : ¬ (y = r ∧ c' = d) := by
          rintro ⟨rfl, rfl⟩; exact hnA hy
        simp [this]
    · right; exact hx
  | moveOwn r c d hl hp =>
    rcases hx with (⟨y, hy, rfl⟩ | ⟨y, hy, rfl⟩) | hx
    · left; left; exact ⟨y, hy, rfl⟩
    · left; right; exact ⟨y, hy, rfl⟩
    · right
      by_cases hc : c' = d
      · subst hc; simp [hx]
      · simp [hc, hx]
  | clearOwn r c hl hp => exact hx

/-- along any run from an invariant state, invariants persist and every I_C grows. -/
theorem run_inv_mono {s sF : St K Reg C} (hs : Inv pub s)
    (h : Relation.ReflTransGen (Step pub) s sF) : Inv pub sF ∧ ∀ c, I s c ≤ I sF c := by
  induction h with
  | refl => exact ⟨hs, fun _ => le_rfl⟩
  | tail hab hbc ih =>
    exact ⟨step_inv pub ih.1 hbc, fun c => (ih.2 c).trans (I_mono (step_gens_mono pub ih.1 hbc) c)⟩

/-- **CS (chart span), timed form**: a row that sits at chart c at ANY moment of a run (in particular
every row leaving c, and every final row of a register ending at c) lies in I_c of the end state. -/
theorem cs_final {s sF : St K Reg C} (hr : Reach pub s)
    (h : Relation.ReflTransGen (Step pub) s sF) {r : Reg} {c : C} (hl : s.loc r = .sit c) :
    s.row r ∈ I sF c :=
  ((run_inv_mono pub (reach_inv pub hr) h).2 c) ((reach_inv pub hr).cs r c hl)

end Model

end WholeFloor

#print axioms WholeFloor.step_inv
#print axioms WholeFloor.reach_inv
#print axioms WholeFloor.cs_final
