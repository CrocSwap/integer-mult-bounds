/-
WHOLEFLOOR R2: up-set entry lemma (UE), lane LEAN-NEXT22, Nov 16. See WFCount.md.
-/
import Nov15.WFCount

set_option linter.unusedSectionVars false

namespace WFCount
open TokenCancel Submodule

variable {K Reg C : Type*} [Field K] [DecidableEq Reg] [DecidableEq C] [Preorder C]

/-- Register `r` sits at a chart of `U`. -/
def inU (U : Set C) (s : St K Reg C) (r : Reg) : Prop := ∃ c ∈ U, s.loc r = some c

theorem stay_step (Own : Reg → Prop) (U : Set C) (hU : ∀ a b, a ≤ b → a ∈ U → b ∈ U)
    (s : St K Reg C) (e : Ev K Reg C) (hL : LegalEvW Own s e) (r : Reg) (hr : ¬ Own r)
    (h : inU U s r) : inU U (step s e) r := by
  obtain ⟨c, hc, hl⟩ := h
  cases e with
  | born i c' =>
    have : s.loc i = none := hL
    by_cases hri : r = i
    · subst hri; rw [this] at hl; cases hl
    · exact ⟨c, hc, by simpa [step, Function.update_of_ne hri] using hl⟩
  | init i c' =>
    have : s.loc i = none := hL
    by_cases hri : r = i
    · subst hri; rw [this] at hl; cases hl
    · exact ⟨c, hc, by simpa [step, Function.update_of_ne hri] using hl⟩
  | move i c' =>
    obtain ⟨c0, hc0, hle⟩ := hL
    by_cases hri : r = i
    · subst hri
      rw [hc0] at hl; cases hl
      exact ⟨c', hU _ _ (hle hr) hc, by simp [step]⟩
    · exact ⟨c, hc, by simpa [step, Function.update_of_ne hri] using hl⟩
  | add i j a c' => exact ⟨c, hc, by simpa [step] using hl⟩
  | scale i u c' => exact ⟨c, hc, by simpa [step] using hl⟩
  | clear i c' => exact ⟨c, hc, by simpa [step] using hl⟩
  | copy i j c' => exact ⟨c, hc, by simpa [step] using hl⟩

theorem stay_run (Own : Reg → Prop) (U : Set C) (hU : ∀ a b, a ≤ b → a ∈ U → b ∈ U) :
    ∀ (evs : List (Ev K Reg C)) (s : St K Reg C), LegalW Own s evs → ∀ r, ¬ Own r →
    inU U s r → inU U (run s evs) r
  | [], s, _, r, _, h => h
  | e :: es, s, ⟨hL, hLs⟩, r, hr, h =>
    stay_run Own U hU es (step s e) hLs r hr (stay_step Own U hU s e hL r hr h)

open Classical in
/-- Public registers carrying a generator. -/
noncomputable def pubRegs (Own : Reg → Prop) (L : List (Gen K Reg)) : List Reg :=
  L.filterMap (fun g => if ¬ Own g.reg then some g.reg else none)

theorem mem_pubRegs (Own : Reg → Prop) (L : List (Gen K Reg)) (r : Reg) :
    r ∈ pubRegs Own L ↔ ∃ g ∈ L, g.reg = r ∧ ¬ Own r := by
  classical
  simp only [pubRegs, List.mem_filterMap]
  constructor
  · rintro ⟨g, hg, h⟩
    by_cases ho : Own g.reg
    · simp [ho] at h
    · simp [ho] at h; exact ⟨g, hg, h, h ▸ ho⟩
  · rintro ⟨g, hg, rfl, ho⟩
    exact ⟨g, hg, by simp [ho]⟩

theorem pubRegs_append (Own : Reg → Prop) (L1 L2 : List (Gen K Reg)) :
    pubRegs Own (L1 ++ L2) = pubRegs Own L1 ++ pubRegs Own L2 := by
  simp [pubRegs, List.filterMap_append]

theorem genEv_len (P : C → C → Prop) (B : C → Prop) (s : St K Reg C) (e : Ev K Reg C) :
    (genEv P B s e).length ≤ 1 := by
  cases e <;> simp only [genEv] <;> (try split_ifs) <;> simp

theorem genEv_info' (Own : Reg → Prop) (U : Set C) (s : St K Reg C) (e : Ev K Reg C)
    (hL : LegalEvW Own s e) (g : Gen K Reg)
    (hg : g ∈ genEv (fun c0 c => c0 ∉ U ∧ c ∈ U) (fun c => c ∈ U) s e) :
    ¬ inU U s g.reg ∧ inU U (step s e) g.reg := by
  cases e with
  | born i c =>
    have hn : s.loc i = none := hL
    simp only [genEv] at hg
    split_ifs at hg with hb
    · simp at hg; subst hg
      refine ⟨?_, c, hb, by simp [step]⟩
      rintro ⟨c1, _, hl⟩; simp [hn] at hl
    · simp at hg
  | move i c =>
    simp only [genEv] at hg
    split_ifs at hg with hm
    · simp at hg; subst hg
      obtain ⟨c0, hc0, h0, hc⟩ := hm
      refine ⟨?_, c, hc, by simp [step]⟩
      rintro ⟨c1, hc1, hl⟩; rw [hc0] at hl; cases hl; exact h0 hc1
    · simp at hg
  | _ => simp [genEv] at hg

/-- Public generators: distinct registers, absent from `U` before, in `U` at the end. -/
theorem pub_gens (Own : Reg → Prop) (U : Set C) (hU : ∀ a b, a ≤ b → a ∈ U → b ∈ U) :
    ∀ (evs : List (Ev K Reg C)) (s : St K Reg C), LegalW Own s evs →
    (pubRegs Own (gens (fun c0 c => c0 ∉ U ∧ c ∈ U) (fun c => c ∈ U) s evs)).Nodup ∧
    ∀ r ∈ pubRegs Own (gens (fun c0 c => c0 ∉ U ∧ c ∈ U) (fun c => c ∈ U) s evs),
      ¬ inU U s r ∧ inU U (run s evs) r
  | [], s, _ => by simp [gens, pubRegs]
  | e :: es, s, ⟨hL, hLs⟩ => by
    obtain ⟨hnd, hall⟩ := pub_gens Own U hU es (step s e) hLs
    have hlen := genEv_len (fun c0 c => c0 ∉ U ∧ c ∈ U) (fun c => c ∈ U) s e
    have hfirst : ∀ r ∈ pubRegs Own (genEv (fun c0 c => c0 ∉ U ∧ c ∈ U) (fun c => c ∈ U) s e),
        ¬ inU U s r ∧ inU U (step s e) r ∧ ¬ Own r := by
      intro r hr
      obtain ⟨g, hg, rfl, ho⟩ := (mem_pubRegs _ _ _).1 hr
      obtain ⟨a, b⟩ := genEv_info' Own U s e hL g hg
      exact ⟨a, b, ho⟩
    have hfn : (pubRegs Own (genEv (fun c0 c => c0 ∉ U ∧ c ∈ U) (fun c => c ∈ U) s e)).Nodup := by
      have : (pubRegs Own (genEv (fun c0 c => c0 ∉ U ∧ c ∈ U) (fun c => c ∈ U) s e)).length ≤ 1 := by
        classical
        exact (List.length_filterMap_le _ _).trans hlen
      match h : pubRegs Own (genEv (fun c0 c => c0 ∉ U ∧ c ∈ U) (fun c => c ∈ U) s e), this with
      | [], _ => simp
      | [a], _ => simp
      | a :: b :: l, hh => simp at hh
    have hres : ∀ r ∈ pubRegs Own (gens (fun c0 c => c0 ∉ U ∧ c ∈ U) (fun c => c ∈ U) (step s e) es),
        ¬ inU U s r := by
      intro r hr hin
      have hro : ¬ Own r := ((mem_pubRegs _ _ _).1 hr).choose_spec.2.2
      exact (hall r hr).1 (stay_step Own U hU s e hL r hro hin)
    simp only [gens, pubRegs_append]
    refine ⟨List.nodup_append.2 ⟨hfn, hnd, ?_⟩, ?_⟩
    · intro a ha b hb hab
      subst hab
      exact (hall a hb).1 (hfirst a ha).2.1
    · intro r hr
      rcases List.mem_append.1 hr with hr | hr
      · obtain ⟨a, b, c⟩ := hfirst r hr
        exact ⟨a, stay_run Own U hU es (step s e) hLs r c b⟩
      · exact ⟨hres r hr, (hall r hr).2⟩


open Classical in
theorem pub_count (Own : Reg → Prop) (L : List (Gen K Reg)) :
    (pubRegs Own L).length + L.countP (fun g => decide (Own g.reg)) = L.length := by
  induction L with
  | nil => simp [pubRegs]
  | cons g L ih =>
    by_cases ho : Own g.reg
    · simp [pubRegs, List.filterMap_cons, ho, List.countP_cons] at ih ⊢; omega
    · simp [pubRegs, List.filterMap_cons, ho, List.countP_cons] at ih ⊢; omega

open Classical in
/-- **Up-set entry lemma (WHOLEFLOOR R2, UE), count form.** `U` up-closed, public moves ascend.
`F` = span of the final rows of the public residents of `U` (assumed independent: the target is
invertible), `Bsp` = span of the unit rows of registers born in `U`. Then
`dim (F + Bsp) ≤ dim F + #(owned generators)`, i.e. `#owned (births + entries) ≥ def(U)`. -/
theorem up_entry [Fintype Reg] (Own : Reg → Prop) (U : Set C)
    (hU : ∀ a b, a ≤ b → a ∈ U → b ∈ U)
    (evs : List (Ev K Reg C)) (hL : LegalW Own start evs)
    (hind : LinearIndependent K
      (fun r : {r : Reg // ¬ Own r ∧ inU U (run start evs) r} => (run start evs).row r.1)) :
    Module.finrank K ↥(span K (Set.range
        (fun r : {r : Reg // ¬ Own r ∧ inU U (run start evs) r} => (run start evs).row r.1)) ⊔
        span K {v | ∃ i c, Ev.born i c ∈ evs ∧ c ∈ U ∧ v = Pi.single i 1})
      ≤ Module.finrank K ↥(span K (Set.range
        (fun r : {r : Reg // ¬ Own r ∧ inU U (run start evs) r} => (run start evs).row r.1)))
        + (gens (fun c0 c => c0 ∉ U ∧ c ∈ U) (fun c => c ∈ U) start evs).countP
            (fun g => decide (Own g.reg)) := by
  set P : C → C → Prop := fun c0 c => c0 ∉ U ∧ c ∈ U with hPdef
  set B : C → Prop := fun c => c ∈ U with hBdef
  set L := gens P B start evs with hLdef
  have hcov : Cov U (gspan L) (run start evs) :=
    CS_run Own U P B (fun c0 c h0 hc => ⟨h0, hc⟩) (fun c hc => hc) evs hL
  have hF : span K (Set.range
      (fun r : {r : Reg // ¬ Own r ∧ inU U (run start evs) r} => (run start evs).row r.1))
        ≤ gspan L := by
    rw [Submodule.span_le]
    rintro _ ⟨⟨r, ho, c, hc, hl⟩, rfl⟩
    exact hcov r c hl hc
  have hBs : span K {v | ∃ i c, Ev.born i c ∈ evs ∧ c ∈ U ∧ v = Pi.single i 1} ≤ gspan L := by
    rw [Submodule.span_le]
    rintro _ ⟨i, c, hm, hc, rfl⟩
    obtain ⟨g, hg, hr⟩ := born_mem_gens P B i c hc evs start hm
    exact Submodule.subset_span ⟨g, hg, hr⟩
  have h1 := Submodule.finrank_mono (sup_le hF hBs)
  have hsp : gspan L = span K {v | v ∈ L.map Gen.row} := by
    unfold gspan; congr 1; ext v; simp
  have h2 : Module.finrank K ↥(gspan L) ≤ L.length := by
    rw [hsp]; simpa using finrank_span_list_le (K := K) (L.map Gen.row)
  have h3 := pub_count Own L
  obtain ⟨hnd, hall⟩ := pub_gens Own U hU evs start hL
  have h4 : (pubRegs Own L).length ≤ Fintype.card
      {r : Reg // ¬ Own r ∧ inU U (run start evs) r} := by
    rw [← List.toFinset_card_of_nodup hnd, Fintype.card_subtype]
    apply Finset.card_le_card
    intro r hr
    have hr' := List.mem_toFinset.1 hr
    simp only [Finset.mem_filter, Finset.mem_univ, true_and]
    exact ⟨((mem_pubRegs _ _ _).1 hr').choose_spec.2.2, (hall r hr').2⟩
  rw [finrank_span_eq_card hind]
  omega

end WFCount

#print axioms WFCount.up_entry
