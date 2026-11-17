/-
WHOLEFLOOR counting lemmas (R1-R3), lane LEAN-NEXT22, Nov 16. See WFCount.md.
Part A: chart-span invariant (CS) with generators = births in D + rows at entries into D.
-/
import Nov15.TokenCancel
import Mathlib.LinearAlgebra.Dimension.Finite
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.LinearAlgebra.Dimension.Constructions

set_option linter.unusedSectionVars false

namespace WFCount
open TokenCancel Submodule

variable {K Reg C : Type*} [Field K] [DecidableEq Reg] [DecidableEq C] [Preorder C]

/-- Legality with an ownership predicate: public registers (`¬ Own i`) only MOVE up. -/
def LegalEvW (Own : Reg → Prop) (s : St K Reg C) : Ev K Reg C → Prop
  | .born i _ => s.loc i = none
  | .init i _ => s.loc i = none
  | .move i c => ∃ c0, s.loc i = some c0 ∧ (¬ Own i → c0 ≤ c)
  | .add i j _ c => i ≠ j ∧ s.loc i = some c ∧ s.loc j = some c
  | .scale i _ c => s.loc i = some c
  | .clear i c => s.loc i = some c
  | .copy i j c => s.loc i = some c ∧ s.loc j = some c

def LegalW (Own : Reg → Prop) : St K Reg C → List (Ev K Reg C) → Prop
  | _, [] => True
  | s, e :: es => LegalEvW Own s e ∧ LegalW Own (step s e) es

/-- A generator of the chart span: a birth in the region, or the row of a register at a MOVE
that enters the region. `entry` tells which. -/
structure Gen (K Reg : Type*) where
  reg : Reg
  row : Reg → K
  entry : Bool

open Classical in
noncomputable def genEv (P : C → C → Prop) (B : C → Prop) (s : St K Reg C) :
    Ev K Reg C → List (Gen K Reg)
  | .born i c => if B c then [⟨i, Pi.single i 1, false⟩] else []
  | .move i c => if (∃ c0, s.loc i = some c0 ∧ P c0 c) then [⟨i, s.row i, true⟩] else []
  | _ => []

noncomputable def gens (P : C → C → Prop) (B : C → Prop) :
    St K Reg C → List (Ev K Reg C) → List (Gen K Reg)
  | _, [] => []
  | s, e :: es => genEv P B s e ++ gens P B (step s e) es

/-- Rows covered by a list of generators. -/
def gspan (L : List (Gen K Reg)) : Submodule K (Reg → K) :=
  Submodule.span K {v | ∃ g ∈ L, g.row = v}

/-- Chart-span coverage: every row at a chart in `D` lies in `W`. -/
def Cov (D : Set C) (W : Submodule K (Reg → K)) (s : St K Reg C) : Prop :=
  ∀ r c, s.loc r = some c → c ∈ D → s.row r ∈ W

theorem cov_mono {D : Set C} {W W' : Submodule K (Reg → K)} {s : St K Reg C}
    (h : Cov D W s) (hW : W ≤ W') : Cov D W' s :=
  fun r c hl hc => hW (h r c hl hc)

theorem cov_step (Own : Reg → Prop) (D : Set C) (P : C → C → Prop) (B : C → Prop)
    (hP : ∀ c0 c, c0 ∉ D → c ∈ D → P c0 c) (hB : ∀ c, c ∈ D → B c)
    (W : Submodule K (Reg → K)) (s : St K Reg C) (e : Ev K Reg C)
    (hL : LegalEvW Own s e) (H : Cov D W s) :
    Cov D (W ⊔ gspan (genEv P B s e)) (step s e) := by
  have hsub : W ≤ W ⊔ gspan (genEv P B s e) := le_sup_left
  intro r c' hloc hcD
  cases e with
  | born i c =>
    by_cases hri : r = i
    · subst hri
      simp only [step, Function.update_self, Option.some.injEq] at hloc
      subst hloc
      apply Submodule.mem_sup_right
      apply Submodule.subset_span
      refine ⟨⟨r, Pi.single r 1, false⟩, ?_, by simp [step]⟩
      simp [genEv, hB c hcD]
    · apply hsub
      apply H r c' (by simpa [step, Function.update_of_ne hri] using hloc) hcD |> fun x => ?_
      simpa [step, Function.update_of_ne hri] using x
  | init i c =>
    by_cases hri : r = i
    · subst hri; apply hsub; simp [step]
    · apply hsub
      have := H r c' (by simpa [step, Function.update_of_ne hri] using hloc) hcD
      simpa [step, Function.update_of_ne hri] using this
  | move i c =>
    obtain ⟨c0, hc0, _⟩ := hL
    by_cases hri : r = i
    · subst hri
      simp only [step, Function.update_self, Option.some.injEq] at hloc
      subst hloc
      by_cases h0 : c0 ∈ D
      · exact hsub (by simpa [step] using H r c0 hc0 h0)
      · apply Submodule.mem_sup_right
        apply Submodule.subset_span
        refine ⟨⟨r, s.row r, true⟩, ?_, by simp [step]⟩
        have : ∃ c1, s.loc r = some c1 ∧ P c1 c := ⟨c0, hc0, hP c0 c h0 hcD⟩
        simp [genEv, this]
    · apply hsub
      have := H r c' (by simpa [step, Function.update_of_ne hri] using hloc) hcD
      simpa [step] using this
  | add i j a c =>
    obtain ⟨hij, hli, hlj⟩ := hL
    by_cases hri : r = i
    · subst hri
      have hc : c' = c := by
        have := hloc; simp [step] at this; rw [hli] at this; exact (Option.some.inj this).symm
      subst hc
      apply hsub
      have h1 := H r c' hli hcD
      have h2 := H j c' hlj hcD
      simp only [step, Function.update_self]
      exact W.add_mem h1 (W.smul_mem a h2)
    · apply hsub
      have := H r c' (by simpa [step] using hloc) hcD
      simpa [step, Function.update_of_ne hri] using this
  | scale i u c =>
    by_cases hri : r = i
    · subst hri
      apply hsub
      have h1 := H r c' (by simpa [step] using hloc) hcD
      simpa [step] using W.smul_mem u h1
    · apply hsub
      have := H r c' (by simpa [step] using hloc) hcD
      simpa [step, Function.update_of_ne hri] using this
  | clear i c =>
    by_cases hri : r = i
    · subst hri; apply hsub; simp [step]
    · apply hsub
      have := H r c' (by simpa [step] using hloc) hcD
      simpa [step, Function.update_of_ne hri] using this
  | copy i j c =>
    obtain ⟨hli, hlj⟩ := hL
    by_cases hri : r = i
    · subst hri
      have hc : c' = c := by
        have := hloc; simp [step] at this; rw [hli] at this; exact (Option.some.inj this).symm
      subst hc
      apply hsub
      simpa [step] using H j c' hlj hcD
    · apply hsub
      have := H r c' (by simpa [step] using hloc) hcD
      simpa [step, Function.update_of_ne hri] using this


theorem gspan_nil : gspan ([] : List (Gen K Reg)) = ⊥ := by
  simp [gspan]

theorem gspan_append (L1 L2 : List (Gen K Reg)) : gspan (L1 ++ L2) = gspan L1 ⊔ gspan L2 := by
  unfold gspan
  rw [← Submodule.span_union]
  congr 1
  ext v; simp only [Set.mem_setOf_eq, List.mem_append, Set.mem_union]
  constructor
  · rintro ⟨g, hg | hg, rfl⟩
    · exact Or.inl ⟨g, hg, rfl⟩
    · exact Or.inr ⟨g, hg, rfl⟩
  · rintro (⟨g, hg, rfl⟩ | ⟨g, hg, rfl⟩)
    · exact ⟨g, Or.inl hg, rfl⟩
    · exact ⟨g, Or.inr hg, rfl⟩

/-- **Chart span (CS), run form.** -/
theorem cov_run (Own : Reg → Prop) (D : Set C) (P : C → C → Prop) (B : C → Prop)
    (hP : ∀ c0 c, c0 ∉ D → c ∈ D → P c0 c) (hB : ∀ c, c ∈ D → B c) :
    ∀ (evs : List (Ev K Reg C)) (s : St K Reg C) (W : Submodule K (Reg → K)),
    LegalW Own s evs → Cov D W s → Cov D (W ⊔ gspan (gens P B s evs)) (run s evs)
  | [], s, W, _, H => by
    simpa [gens, run, gspan_nil] using H
  | e :: es, s, W, ⟨hL, hLs⟩, H => by
    have H1 := cov_step Own D P B hP hB W s e hL H
    have H2 := cov_run Own D P B hP hB es (step s e) _ hLs H1
    refine cov_mono H2 ?_
    simp only [gens, gspan_append, run]
    rw [sup_assoc]

theorem cov_start (D : Set C) : Cov D (⊥ : Submodule K (Reg → K)) (start : St K Reg C) := by
  intro r c hl; simp [start] at hl

theorem CS_run (Own : Reg → Prop) (D : Set C) (P : C → C → Prop) (B : C → Prop)
    (hP : ∀ c0 c, c0 ∉ D → c ∈ D → P c0 c) (hB : ∀ c, c ∈ D → B c)
    (evs : List (Ev K Reg C)) (hL : LegalW Own start evs) :
    Cov D (gspan (gens P B start evs)) (run start evs) := by
  have := cov_run Own D P B hP hB evs start ⊥ hL (cov_start D)
  simpa using this

theorem born_mem_gens (P : C → C → Prop) (B : C → Prop) (i : Reg) (c : C) (hB : B c) :
    ∀ (evs : List (Ev K Reg C)) (s : St K Reg C), Ev.born i c ∈ evs →
    ∃ g ∈ gens P B s evs, g.row = Pi.single i 1
  | [], s, h => by simp at h
  | e :: es, s, h => by
    rcases List.mem_cons.1 h with he | he
    · subst he
      exact ⟨⟨i, Pi.single i 1, false⟩, by simp [gens, genEv, hB], rfl⟩
    · obtain ⟨g, hg, hr⟩ := born_mem_gens P B i c hB es (step s e) he
      exact ⟨g, by simp [gens, hg], hr⟩

theorem gens_birth (P : C → C → Prop) (B : C → Prop) :
    ∀ (evs : List (Ev K Reg C)) (s : St K Reg C) (g : Gen K Reg), g ∈ gens P B s evs →
    g.entry = false → ∃ i c, Ev.born i c ∈ evs ∧ B c ∧ g.row = Pi.single i 1
  | [], s, g, hg, _ => by simp [gens] at hg
  | e :: es, s, g, hg, he => by
    simp only [gens, List.mem_append] at hg
    rcases hg with hg | hg
    · cases e with
      | born i c =>
        by_cases hb : B c
        · simp [genEv, hb] at hg; subst hg
          exact ⟨i, c, by simp, hb, rfl⟩
        · simp [genEv, hb] at hg
      | move i c =>
        simp only [genEv] at hg
        split_ifs at hg with hm
        · simp at hg; subst hg; simp at he
        · simp at hg
      | _ => simp [genEv] at hg
    · obtain ⟨i, c, hm, hb, hr⟩ := gens_birth P B es (step s e) g hg he
      exact ⟨i, c, List.mem_cons_of_mem _ hm, hb, hr⟩

/-- Entry generators are owned when the entry relation excludes ascents. -/
theorem entry_gen_own (Own : Reg → Prop) (P : C → C → Prop) (B : C → Prop)
    (hPown : ∀ c0 c, P c0 c → ¬ c0 ≤ c) :
    ∀ (evs : List (Ev K Reg C)) (s : St K Reg C), LegalW Own s evs →
    ∀ g ∈ gens P B s evs, g.entry = true → Own g.reg
  | [], s, _, g, hg, _ => by simp [gens] at hg
  | e :: es, s, ⟨hL, hLs⟩, g, hg, he => by
    simp only [gens, List.mem_append] at hg
    rcases hg with hg | hg
    · cases e with
      | born i c =>
        simp only [genEv] at hg
        split_ifs at hg with hb
        · simp at hg; subst hg; simp at he
        · simp at hg
      | move i c =>
        simp only [genEv] at hg
        split_ifs at hg with hm
        · simp at hg; subst hg
          obtain ⟨c0, hc0, hle⟩ := hL
          obtain ⟨c1, hc1, hP⟩ := hm
          rw [hc0] at hc1; cases hc1
          by_contra hno
          exact hPown _ _ hP (hle hno)
        · simp at hg
      | _ => simp [genEv] at hg
    · exact entry_gen_own Own P B hPown es (step s e) hLs g hg he

theorem finrank_span_list_le {V : Type*} [AddCommGroup V] [Module K V] (E : List V) :
    Module.finrank K (span K {v | v ∈ E}) ≤ E.length := by
  classical
  have : {v | v ∈ E} = (E.toFinset : Set V) := by ext; simp
  rw [this]; exact (finrank_span_finset_le_card _).trans (List.toFinset_card_le E)

/-- **Down-set descent lemma (WHOLEFLOOR R1), abstract-count form.** Regions `D q` (`q ∈ ι`), a
linear map `π` killing every birth row inside any region; each region ends with a register whose
`π`-image is the unit vector `δ_q`. Then the number of entries (a MOVE from outside some `D q` into
it) is at least `|ι|`. -/
theorem descent_count {ι : Type*} [Fintype ι] [DecidableEq ι]
    (Own : Reg → Prop) (D : ι → Set C) (π : (Reg → K) →ₗ[K] (ι → K))
    (evs : List (Ev K Reg C)) (hL : LegalW Own start evs)
    (hb : ∀ q i c, Ev.born i c ∈ evs → c ∈ D q → π (Pi.single i 1) = 0)
    (hy : ∀ q, ∃ y c, (run start evs).loc y = some c ∧ c ∈ D q ∧
        π ((run start evs).row y) = Pi.single q 1) :
    Fintype.card ι ≤
      ((gens (fun c0 c => ∃ q, c0 ∉ D q ∧ c ∈ D q) (fun c => ∃ q, c ∈ D q) start evs).filter
        (fun g => g.entry)).length := by
  classical
  set P : C → C → Prop := fun c0 c => ∃ q, c0 ∉ D q ∧ c ∈ D q with hPdef
  set B : C → Prop := fun c => ∃ q, c ∈ D q with hBdef
  set L := gens P B start evs with hLdef
  set E : List (ι → K) := (L.filter (fun g => g.entry)).map (fun g => π g.row) with hE
  have hcov : ∀ q, Cov (D q) (gspan L) (run start evs) := fun q =>
    CS_run Own (D q) P B (fun c0 c h0 hc => ⟨q, h0, hc⟩) (fun c hc => ⟨q, hc⟩) evs hL
  have hrows : ∀ g ∈ L, π g.row ∈ span K {v | v ∈ E} := by
    intro g hg
    by_cases he : g.entry = true
    · apply Submodule.subset_span
      simp only [hE, List.mem_map, List.mem_filter, Set.mem_setOf_eq]
      exact ⟨g, ⟨hg, he⟩, rfl⟩
    · have he' : g.entry = false := by simpa using he
      obtain ⟨i, c, hm, ⟨q, hq⟩, hr⟩ := gens_birth P B evs start g hg he'
      rw [hr, hb q i c hm hq]; exact Submodule.zero_mem _
  have hmap : (gspan L).map π ≤ span K {v | v ∈ E} := by
    unfold gspan
    rw [Submodule.map_span, Submodule.span_le]
    rintro _ ⟨v, ⟨g, hg, rfl⟩, rfl⟩
    exact hrows g hg
  have hδ : ∀ q, (Pi.single q 1 : ι → K) ∈ span K {v | v ∈ E} := by
    intro q
    obtain ⟨y, c, hl, hc, hπ⟩ := hy q
    rw [← hπ]
    exact hmap ⟨_, hcov q y c hl hc, rfl⟩
  have htop : span K {v | v ∈ E} = ⊤ := by
    rw [eq_top_iff, ← (Pi.basisFun K ι).span_eq, Submodule.span_le]
    rintro _ ⟨q, rfl⟩
    simpa using hδ q
  have h1 : Module.finrank K (span K {v | v ∈ E}) = Fintype.card ι := by
    rw [htop, finrank_top]; simp
  have h2 := finrank_span_list_le (K := K) E
  rw [h1] at h2
  simpa [hE] using h2

/-- The entries counted by `descent_count` are OWNED MOVEs when every `D q` is down-closed and
public moves ascend: a public register cannot enter a down-set from outside. -/
theorem descent_entries_owned {ι : Type*} (Own : Reg → Prop) (D : ι → Set C)
    (hdown : ∀ q a b, a ≤ b → b ∈ D q → a ∈ D q)
    (evs : List (Ev K Reg C)) (hL : LegalW Own start evs) :
    ∀ g ∈ gens (fun c0 c => ∃ q, c0 ∉ D q ∧ c ∈ D q) (fun c => ∃ q, c ∈ D q) start evs,
      g.entry = true → Own g.reg :=
  entry_gen_own Own _ _ (fun c0 c ⟨q, h0, hc⟩ hle => h0 (hdown q c0 c hle hc)) evs start hL

end WFCount

#print axioms WFCount.cov_run
#print axioms WFCount.descent_count
#print axioms WFCount.descent_entries_owned
