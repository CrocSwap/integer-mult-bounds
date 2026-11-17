/-
WHOLEFLOOR R3: PORT LEMMA and Y-side theorem (sum of slack >= #ports), plus the count identity
`#gens = dim F + dim E + sigma` (hcount of `slack_rank_model`) DISCHARGED.
Lane LEAN-NEXT25, Nov 17. See WFPort.md.
-/
import Nov15.WFSlack
import Nov15.WFUp

set_option linter.unusedSectionVars false

namespace WFPort
open TokenCancel WFCount WFSlack Submodule Module

/-! ## 0. Elementary list/count lemmas -/

theorem cp_split {α : Type*} (L : List α) (p q : α → Prop) [DecidablePred p] [DecidablePred q] :
    L.countP (fun a => decide (p a)) =
      L.countP (fun a => decide (p a ∧ q a)) + L.countP (fun a => decide (p a ∧ ¬ q a)) := by
  induction L with
  | nil => simp
  | cons a L ih =>
    by_cases hp : p a <;> by_cases hq : q a <;> simp [List.countP_cons, hp, hq] at ih ⊢ <;> omega

section Comb
variable {ι D : Type*} [Fintype ι] [DecidableEq ι] [DecidableEq D]

/-- Pure combinatorics of the Y-side sum, with the antichain hypothesis made explicit. -/
theorem y_side_sum (Hc : ι → D) (hinj : Function.Injective Hc) (sl : D → ℕ) (T : Finset D)
    (ch : ι → D) (hH : ∀ q, Hc q ∈ T)
    (hch : ∀ q, sl (Hc q) = 0 → ch q ∈ T ∧ ∀ q', ch q ≠ Hc q')
    (hfeed : ∀ C, (Finset.univ.filter (fun q => sl (Hc q) = 0 ∧ ch q = C)).card ≤ sl C) :
    Fintype.card ι ≤ ∑ C ∈ T, sl C := by
  classical
  set A : Finset ι := Finset.univ.filter (fun q => sl (Hc q) ≠ 0) with hA
  set B : Finset ι := Finset.univ.filter (fun q => sl (Hc q) = 0) with hB
  have hcard : Fintype.card ι = A.card + B.card := by
    have := Finset.card_filter_add_card_filter_not (s := (Finset.univ : Finset ι))
      (fun q => sl (Hc q) ≠ 0)
    simpa [hA, hB, Finset.card_univ] using this.symm
  set SA : Finset D := A.image Hc with hSA
  set SB : Finset D := B.image ch with hSB
  have hdisj : Disjoint SA SB := by
    rw [Finset.disjoint_left]
    intro C hCA hCB
    obtain ⟨q, hq, h1⟩ := Finset.mem_image.1 hCA
    obtain ⟨q', hq', h2⟩ := Finset.mem_image.1 hCB
    have := (hch q' (by simpa [hB] using hq')).2 q
    exact this (h2.trans h1.symm)
  have hsub : SA ∪ SB ⊆ T := by
    intro C hC
    rcases Finset.mem_union.1 hC with h | h
    · obtain ⟨q, _, rfl⟩ := Finset.mem_image.1 h; exact hH q
    · obtain ⟨q, hq, rfl⟩ := Finset.mem_image.1 h
      exact (hch q (by simpa [hB] using hq)).1
  have h1 : ∑ C ∈ SA ∪ SB, sl C ≤ ∑ C ∈ T, sl C :=
    Finset.sum_le_sum_of_subset hsub
  rw [Finset.sum_union hdisj] at h1
  have h2 : A.card ≤ ∑ C ∈ SA, sl C := by
    rw [hSA, Finset.sum_image (fun x _ y _ h => hinj h)]
    calc A.card = ∑ q ∈ A, 1 := by simp
      _ ≤ ∑ q ∈ A, sl (Hc q) := Finset.sum_le_sum (fun q hq => by
          have : sl (Hc q) ≠ 0 := by simpa [hA] using hq
          omega)
  have h3 : B.card ≤ ∑ C ∈ SB, sl C := by
    rw [Finset.card_eq_sum_card_image ch B]
    apply Finset.sum_le_sum
    intro C _
    refine le_trans (le_of_eq ?_) (hfeed C)
    congr 1
    ext q
    simp [hB]
  omega

end Comb

/-! ## 1. Generators: prefix, birth registers, entry source -/

section Gens
variable {K Reg C : Type*} [Field K] [DecidableEq Reg] [DecidableEq C] [Preorder C]

theorem legalW_append (Own : Reg → Prop) (s : St K Reg C) (l1 l2 : List (Ev K Reg C)) :
    LegalW Own s (l1 ++ l2) ↔ LegalW Own s l1 ∧ LegalW Own (run s l1) l2 := by
  induction l1 generalizing s with
  | nil => simp [LegalW, run]
  | cons e es ih => simp [LegalW, run, ih, and_assoc]

theorem gens_append (P : C → C → Prop) (B : C → Prop) (s : St K Reg C)
    (l1 l2 : List (Ev K Reg C)) :
    gens P B s (l1 ++ l2) = gens P B s l1 ++ gens P B (run s l1) l2 := by
  induction l1 generalizing s with
  | nil => simp [gens, run]
  | cons e es ih => simp [gens, run, ih, List.append_assoc]

/-- Birth generators carry the register that was born. -/
theorem gens_birth' (P : C → C → Prop) (B : C → Prop) :
    ∀ (evs : List (Ev K Reg C)) (s : St K Reg C) (g : Gen K Reg), g ∈ gens P B s evs →
    g.entry = false → ∃ c, Ev.born g.reg c ∈ evs ∧ B c ∧ g.row = Pi.single g.reg 1
  | [], s, g, hg, _ => by simp [gens] at hg
  | e :: es, s, g, hg, he => by
    simp only [gens, List.mem_append] at hg
    rcases hg with hg | hg
    · cases e with
      | born i c =>
        by_cases hb : B c
        · simp [genEv, hb] at hg; subst hg
          exact ⟨c, by simp, hb, rfl⟩
        · simp [genEv, hb] at hg
      | move i c =>
        simp only [genEv] at hg
        split_ifs at hg with hm
        · simp at hg; subst hg; simp at he
        · simp at hg
      | _ => simp [genEv] at hg
    · obtain ⟨c, hm, hb, hr⟩ := gens_birth' P B es (step s e) g hg he
      exact ⟨c, List.mem_cons_of_mem _ hm, hb, hr⟩

/-- Every entry generator is a MOVE of its register across `P`, with the row at that moment. -/
theorem entry_source (P : C → C → Prop) (B : C → Prop) :
    ∀ (evs : List (Ev K Reg C)) (s : St K Reg C) (g : Gen K Reg), g ∈ gens P B s evs →
    g.entry = true → ∃ pre post c0 c, evs = pre ++ Ev.move g.reg c :: post ∧
      (run s pre).loc g.reg = some c0 ∧ P c0 c ∧ (run s pre).row g.reg = g.row
  | [], s, g, hg, _ => by simp [gens] at hg
  | e :: es, s, g, hg, he => by
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
          obtain ⟨c0, hc0, hP⟩ := hm
          exact ⟨[], es, c0, c, rfl, hc0, hP, rfl⟩
        · simp at hg
      | _ => simp [genEv] at hg
    · obtain ⟨pre, post, c0, c, h1, h2, h3, h4⟩ := entry_source P B es (step s e) g hg he
      exact ⟨e :: pre, post, c0, c, by simp [h1], h2, h3, h4⟩

end Gens

/-! ## 2. Public generators are at distinct registers (convex regions) -/

section Pub
variable {K Reg C : Type*} [Field K] [DecidableEq Reg] [DecidableEq C] [Preorder C]

theorem genEv_info'' (Own : Reg → Prop) (D U : Set C) (hDU : D ⊆ U)
    (hUD : ∀ c0 c, c0 ≤ c → c0 ∉ D → c ∈ D → c0 ∉ U)
    (s : St K Reg C) (e : Ev K Reg C) (hL : LegalEvW Own s e) (g : Gen K Reg)
    (hg : g ∈ genEv (fun c0 c => c0 ∉ D ∧ c ∈ D) (fun c => c ∈ D) s e) (hpub : ¬ Own g.reg) :
    ¬ inU U s g.reg ∧ inU U (step s e) g.reg := by
  cases e with
  | born i c =>
    have hn : s.loc i = none := hL
    simp only [genEv] at hg
    split_ifs at hg with hb
    · simp at hg; subst hg
      refine ⟨?_, c, hDU hb, by simp [step]⟩
      rintro ⟨c1, _, hl⟩; simp [hn] at hl
    · simp at hg
  | move i c =>
    simp only [genEv] at hg
    split_ifs at hg with hm
    · simp at hg; subst hg
      obtain ⟨c0, hc0, h0, hc⟩ := hm
      obtain ⟨c0', hc0', hle⟩ := hL
      refine ⟨?_, c, hDU hc, by simp [step]⟩
      rintro ⟨c1, hc1, hl⟩
      rw [hc0] at hl; cases hl
      rw [hc0] at hc0'; cases hc0'
      exact hUD _ _ (hle hpub) h0 hc hc1
    · simp at hg
  | _ => simp [genEv] at hg

theorem pub_gens_D (Own : Reg → Prop) (D U : Set C) (hU : ∀ a b, a ≤ b → a ∈ U → b ∈ U)
    (hDU : D ⊆ U) (hUD : ∀ c0 c, c0 ≤ c → c0 ∉ D → c ∈ D → c0 ∉ U) :
    ∀ (evs : List (Ev K Reg C)) (s : St K Reg C), LegalW Own s evs →
    (pubRegs Own (gens (fun c0 c => c0 ∉ D ∧ c ∈ D) (fun c => c ∈ D) s evs)).Nodup ∧
    ∀ r ∈ pubRegs Own (gens (fun c0 c => c0 ∉ D ∧ c ∈ D) (fun c => c ∈ D) s evs),
      ¬ inU U s r ∧ inU U (run s evs) r
  | [], s, _ => by simp [gens, pubRegs]
  | e :: es, s, ⟨hL, hLs⟩ => by
    obtain ⟨hnd, hall⟩ := pub_gens_D Own D U hU hDU hUD es (step s e) hLs
    have hlen := genEv_len (fun c0 c => c0 ∉ D ∧ c ∈ D) (fun c => c ∈ D) s e
    have hfirst : ∀ r ∈ pubRegs Own (genEv (fun c0 c => c0 ∉ D ∧ c ∈ D) (fun c => c ∈ D) s e),
        ¬ inU U s r ∧ inU U (step s e) r ∧ ¬ Own r := by
      intro r hr
      obtain ⟨g, hg, rfl, ho⟩ := (mem_pubRegs _ _ _).1 hr
      obtain ⟨a, b⟩ := genEv_info'' Own D U hDU hUD s e hL g hg ho
      exact ⟨a, b, ho⟩
    have hfn : (pubRegs Own (genEv (fun c0 c => c0 ∉ D ∧ c ∈ D) (fun c => c ∈ D) s e)).Nodup := by
      have : (pubRegs Own (genEv (fun c0 c => c0 ∉ D ∧ c ∈ D) (fun c => c ∈ D) s e)).length ≤ 1 := by
        classical
        exact (List.length_filterMap_le _ _).trans hlen
      match h : pubRegs Own (genEv (fun c0 c => c0 ∉ D ∧ c ∈ D) (fun c => c ∈ D) s e), this with
      | [], _ => simp
      | [a], _ => simp
      | a :: b :: l, hh => simp at hh
    have hres : ∀ r ∈ pubRegs Own (gens (fun c0 c => c0 ∉ D ∧ c ∈ D) (fun c => c ∈ D) (step s e) es),
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

/-- Public generators of a convex region sit at distinct registers. -/
theorem pub_nodup (Own : Reg → Prop) (D : Set C)
    (hconv : ∀ a b c, a ∈ D → a ≤ b → b ≤ c → c ∈ D → b ∈ D)
    (evs : List (Ev K Reg C)) (hL : LegalW Own start evs) :
    (pubRegs Own (gens (fun c0 c => c0 ∉ D ∧ c ∈ D) (fun c => c ∈ D) start evs)).Nodup := by
  refine (pub_gens_D Own D {c | ∃ a ∈ D, a ≤ c} ?_ ?_ ?_ evs start hL).1
  · rintro a b hab ⟨x, hx, hxa⟩; exact ⟨x, hx, hxa.trans hab⟩
  · intro c hc; exact ⟨c, hc, le_rfl⟩
  · rintro c0 c hle h0 hc ⟨x, hx, hxc0⟩
    exact h0 (hconv x c0 c hx hxc0 hle hc)

end Pub

/-! ## 3. The slack count `#gens = dim F + dim E + sigma` (hcount discharged) -/

section Slack
variable {K Reg C : Type*} [Field K] [DecidableEq Reg] [DecidableEq C] [Preorder C]

open Classical in
/-- `o_D`: owned generators of `D` (owned births in `D` AND owned entries into `D`). -/
noncomputable def slackO (Own : Reg → Prop) (D : Set C) (evs : List (Ev K Reg C)) : ℕ :=
  (gens (fun c0 c => c0 ∉ D ∧ c ∈ D) (fun c => c ∈ D) (start : St K Reg C) evs).countP
    (fun g => decide (Own g.reg))

open Classical in
/-- `s_D`: passers = public entrants into `D` that do not end in `D`. -/
noncomputable def slackS (Own : Reg → Prop) (D : Set C) (evs : List (Ev K Reg C)) : ℕ :=
  (gens (fun c0 c => c0 ∉ D ∧ c ∈ D) (fun c => c ∈ D) (start : St K Reg C) evs).countP
    (fun g => decide (¬ Own g.reg ∧ ¬ inU D (run (start : St K Reg C) evs) g.reg ∧ g.entry = true))

/-- `sigma_D = s_D + o_D` (the paper's slack). -/
noncomputable def slack (Own : Reg → Prop) (D : Set C) (evs : List (Ev K Reg C)) : ℕ :=
  slackS Own D evs + slackO Own D evs

/-- `F`: span of the final rows of the public registers ending in `D`. -/
def Fc (Own : Reg → Prop) (D : Set C) (evs : List (Ev K Reg C)) : Submodule K (Reg → K) :=
  span K (Set.range (fun r : {r : Reg // ¬ Own r ∧ inU D (run (start : St K Reg C) evs) r} =>
    (run (start : St K Reg C) evs).row r.1))

/-- `E`: span of the unit rows of public registers born in `D` that do not end in `D`
(the paper's `E_BL`: born-and-leave). -/
def Ec (Own : Reg → Prop) (D : Set C) (evs : List (Ev K Reg C)) : Submodule K (Reg → K) :=
  span K {v | ∃ i c, Ev.born i c ∈ evs ∧ c ∈ D ∧ ¬ Own i ∧
    ¬ inU D (run (start : St K Reg C) evs) i ∧ v = Pi.single i 1}

open Classical in
theorem pubRegs_eq (Own : Reg → Prop) (L : List (Gen K Reg)) :
    pubRegs Own L = (L.filter (fun g => decide (¬ Own g.reg))).map Gen.reg := by
  induction L with
  | nil => simp [pubRegs]
  | cons g L ih =>
    by_cases ho : Own g.reg
    · simp [pubRegs, ho] at ih ⊢; exact ih
    · simp [pubRegs, ho] at ih ⊢; exact ih

open Classical in
theorem cp_le_card (Own : Reg → Prop) (L : List (Gen K Reg))
    (hnd : ((L.filter (fun g => decide (¬ Own g.reg))).map Gen.reg).Nodup)
    (r : Gen K Reg → Prop) [DecidablePred r] (T : Finset Reg)
    (hrown : ∀ g, r g → ¬ Own g.reg) (hT : ∀ g ∈ L, r g → g.reg ∈ T) :
    L.countP (fun g => decide (r g)) ≤ T.card := by
  rw [List.countP_eq_length_filter]
  have hsub : List.Sublist (L.filter (fun g => decide (r g)))
      (L.filter (fun g => decide (¬ Own g.reg))) :=
    List.monotone_filter_right L (fun g h => by simpa using hrown g (by simpa using h))
  have hnd' := List.Nodup.sublist (hsub.map Gen.reg) hnd
  calc (L.filter (fun g => decide (r g))).length
      = ((L.filter (fun g => decide (r g))).map Gen.reg).length := (List.length_map _).symm
    _ = ((L.filter (fun g => decide (r g))).map Gen.reg).toFinset.card :=
        (List.toFinset_card_of_nodup hnd').symm
    _ ≤ T.card := by
        apply Finset.card_le_card
        intro x hx
        simp only [List.mem_toFinset, List.mem_map, List.mem_filter, decide_eq_true_eq] at hx
        obtain ⟨g, ⟨hg, hrg⟩, rfl⟩ := hx
        exact hT g hg hrg

open Classical in
/-- **hcount discharged.** For a convex region `D`, with `F` (finals of public residents,
independent) and `E` (units of public born-and-leave registers),
`#gens <= dim F + dim E + (s_D + o_D)`. -/
theorem hcount_full [Fintype Reg] (Own : Reg → Prop) (D : Set C)
    (hconv : ∀ a b c, a ∈ D → a ≤ b → b ≤ c → c ∈ D → b ∈ D)
    (evs : List (Ev K Reg C)) (hL : LegalW Own (start : St K Reg C) evs)
    (hind : LinearIndependent K
      (fun r : {r : Reg // ¬ Own r ∧ inU D (run (start : St K Reg C) evs) r} =>
        (run (start : St K Reg C) evs).row r.1)) :
    (gens (fun c0 c => c0 ∉ D ∧ c ∈ D) (fun c => c ∈ D) (start : St K Reg C) evs).length ≤
      finrank K (Fc Own D evs) + finrank K (Ec Own D evs) + slack Own D evs := by
  set L := gens (fun c0 c => c0 ∉ D ∧ c ∈ D) (fun c => c ∈ D) (start : St K Reg C) evs with hLdef
  have hnd : ((L.filter (fun g => decide (¬ Own g.reg))).map Gen.reg).Nodup := by
    rw [← pubRegs_eq]; exact pub_nodup Own D hconv evs hL
  have h0 : L.length = L.countP (fun g => decide (Own g.reg)) +
      L.countP (fun g => decide (¬ Own g.reg)) := by
    have := cp_split L (fun _ => True) (fun g => Own g.reg)
    simpa using this
  have h1 := cp_split L (fun g => ¬ Own g.reg) (fun g => inU D (run (start : St K Reg C) evs) g.reg)
  have h2 := cp_split L (fun g => ¬ Own g.reg ∧ ¬ inU D (run (start : St K Reg C) evs) g.reg)
    (fun g => g.entry = true)
  simp only [and_assoc] at h2
  -- A: public gens ending in D
  have hA : L.countP (fun g => decide (¬ Own g.reg ∧ inU D (run (start : St K Reg C) evs) g.reg))
      ≤ finrank K (Fc Own D evs) := by
    have hF : finrank K (Fc Own D evs) = Fintype.card
        {r : Reg // ¬ Own r ∧ inU D (run (start : St K Reg C) evs) r} := finrank_span_eq_card hind
    rw [hF, Fintype.card_subtype]
    exact cp_le_card Own L hnd
      (fun g => ¬ Own g.reg ∧ inU D (run (start : St K Reg C) evs) g.reg)
      (Finset.univ.filter (fun r => ¬ Own r ∧ inU D (run (start : St K Reg C) evs) r))
      (fun g h => h.1) (fun g _ h => by simp [h.1, h.2])
  -- B: public births ending outside D
  have hB : L.countP (fun g => decide (¬ Own g.reg ∧ ¬ inU D (run (start : St K Reg C) evs) g.reg ∧
        ¬ g.entry = true)) ≤ finrank K (Ec Own D evs) := by
    have hli : LinearIndependent K (fun i : {i : Reg // ∃ c, Ev.born i c ∈ evs ∧ c ∈ D ∧ ¬ Own i ∧
        ¬ inU D (run (start : St K Reg C) evs) i} => (Pi.single i.1 1 : Reg → K)) := by
      have := (Pi.basisFun K Reg).linearIndependent.comp (fun i : {i : Reg // ∃ c, Ev.born i c ∈ evs ∧
        c ∈ D ∧ ¬ Own i ∧ ¬ inU D (run (start : St K Reg C) evs) i} => i.1) Subtype.val_injective
      simpa [Function.comp_def] using this
    have hE : Ec Own D evs = span K (Set.range (fun i : {i : Reg // ∃ c, Ev.born i c ∈ evs ∧ c ∈ D ∧
        ¬ Own i ∧ ¬ inU D (run (start : St K Reg C) evs) i} => (Pi.single i.1 1 : Reg → K))) := by
      unfold Ec
      congr 1
      ext v
      constructor
      · rintro ⟨i, c, hb, hc, ho, he, rfl⟩
        exact ⟨⟨i, c, hb, hc, ho, he⟩, rfl⟩
      · rintro ⟨⟨i, c, hb, hc, ho, he⟩, rfl⟩
        exact ⟨i, c, hb, hc, ho, he, rfl⟩
    have hF : finrank K (Ec Own D evs) = Fintype.card {i : Reg // ∃ c, Ev.born i c ∈ evs ∧ c ∈ D ∧
        ¬ Own i ∧ ¬ inU D (run (start : St K Reg C) evs) i} := by
      rw [hE]; exact finrank_span_eq_card hli
    rw [hF, Fintype.card_subtype]
    refine cp_le_card Own L hnd
      (fun g => ¬ Own g.reg ∧ ¬ inU D (run (start : St K Reg C) evs) g.reg ∧ ¬ g.entry = true)
      (Finset.univ.filter (fun i : Reg => ∃ c, Ev.born i c ∈ evs ∧ c ∈ D ∧ ¬ Own i ∧
        ¬ inU D (run (start : St K Reg C) evs) i))
      (fun g h => h.1) (fun g hg h => ?_)
    have hen : g.entry = false := by simpa using h.2.2
    obtain ⟨c, hbm, hbc, _⟩ := gens_birth' (fun c0 c => c0 ∉ D ∧ c ∈ D) (fun c => c ∈ D) evs
      (start : St K Reg C) g hg hen
    simp only [Finset.mem_filter, Finset.mem_univ, true_and]
    exact ⟨c, hbm, hbc, h.1, h.2.1⟩
  unfold slack slackS slackO
  have h2' : L.countP (fun g => decide (¬ Own g.reg ∧ ¬ inU D (run (start : St K Reg C) evs) g.reg)) =
      L.countP (fun g => decide (¬ Own g.reg ∧ ¬ inU D (run (start : St K Reg C) evs) g.reg ∧
        g.entry = true)) + L.countP (fun g => decide (¬ Own g.reg ∧
        ¬ inU D (run (start : St K Reg C) evs) g.reg ∧ ¬ g.entry = true)) := h2
  have h1' : L.countP (fun g => decide (¬ Own g.reg)) =
      L.countP (fun g => decide (¬ Own g.reg ∧ inU D (run (start : St K Reg C) evs) g.reg)) +
      L.countP (fun g => decide (¬ Own g.reg ∧ ¬ inU D (run (start : St K Reg C) evs) g.reg)) := h1
  rw [← hLdef]
  omega

/-- **Slack decomposition with the count discharged**: `I_D = F + E + K`, `dim K <= s_D + o_D`. -/
theorem slack_full [Fintype Reg] (Own : Reg → Prop) (D : Set C)
    (hconv : ∀ a b c, a ∈ D → a ≤ b → b ≤ c → c ∈ D → b ∈ D)
    (evs : List (Ev K Reg C)) (hL : LegalW Own (start : St K Reg C) evs)
    (hind : LinearIndependent K
      (fun r : {r : Reg // ¬ Own r ∧ inU D (run (start : St K Reg C) evs) r} =>
        (run (start : St K Reg C) evs).row r.1))
    (hFE : Disjoint (Fc Own D evs) (Ec Own D evs)) :
    ∃ Kc : Submodule K (Reg → K),
      Kc ≤ gspan (gens (fun c0 c => c0 ∉ D ∧ c ∈ D) (fun c => c ∈ D) (start : St K Reg C) evs) ∧
      Disjoint (Fc Own D evs ⊔ Ec Own D evs) Kc ∧
      Fc Own D evs ⊔ Ec Own D evs ⊔ Kc =
        gspan (gens (fun c0 c => c0 ∉ D ∧ c ∈ D) (fun c => c ∈ D) (start : St K Reg C) evs) ∧
      finrank K Kc ≤ slack Own D evs := by
  refine slack_rank_model Own D evs hL (Fc Own D evs) (Ec Own D evs) ?_ ?_ hFE (slack Own D evs)
    (hcount_full Own D hconv evs hL hind)
  · unfold Fc
    rw [Submodule.span_le]
    rintro _ ⟨⟨r, ho, c, hc, hl⟩, rfl⟩
    exact Submodule.subset_span ⟨r, c, hl, hc, rfl⟩
  · unfold Ec
    apply Submodule.span_mono
    rintro v ⟨i, c, hb, hc, _, _, rfl⟩
    exact ⟨i, c, hb, hc, rfl⟩

/-- **Charge lemma (one chart).** If `pi(F + E)` lies in the span of the units `delta_r`,
`r in Bs`, and every `q in Q` (disjoint from `Bs`) has `delta_q in pi(I_D)`, then the chart pays
`|Q|` units of slack. -/
theorem charge [Fintype Reg] {ι : Type*} [Fintype ι] [DecidableEq ι]
    (Own : Reg → Prop) (D : Set C)
    (hconv : ∀ a b c, a ∈ D → a ≤ b → b ≤ c → c ∈ D → b ∈ D)
    (evs : List (Ev K Reg C)) (hL : LegalW Own (start : St K Reg C) evs)
    (hind : LinearIndependent K
      (fun r : {r : Reg // ¬ Own r ∧ inU D (run (start : St K Reg C) evs) r} =>
        (run (start : St K Reg C) evs).row r.1))
    (hFE : Disjoint (Fc Own D evs) (Ec Own D evs))
    (π : (Reg → K) →ₗ[K] (ι → K)) (Bs : Finset ι)
    (hPFE : (Fc Own D evs ⊔ Ec Own D evs).map π ≤
      span K {v | ∃ r ∈ Bs, v = (Pi.single r 1 : ι → K)})
    (Q : Finset ι) (hQ : ∀ q ∈ Q, q ∉ Bs)
    (hmem : ∀ q ∈ Q, (Pi.single q 1 : ι → K) ∈
      (gspan (gens (fun c0 c => c0 ∉ D ∧ c ∈ D) (fun c => c ∈ D) (start : St K Reg C) evs)).map π) :
    Q.card ≤ slack Own D evs := by
  obtain ⟨Kc, hKI, hdis, hsup, hdim⟩ := slack_full Own D hconv evs hL hind hFE
  obtain ⟨pr, hpr⟩ : ∃ pr : (ι → K) →ₗ[K] (Q → K), ∀ f x, pr f x = f x.1 :=
    ⟨LinearMap.funLeft K K (Subtype.val : Q → ι), fun f x => rfl⟩
  set W : Submodule K (Q → K) := (Kc.map π).map pr with hW
  have hker : span K {v | ∃ r ∈ Bs, v = (Pi.single r 1 : ι → K)} ≤ LinearMap.ker pr := by
    rw [Submodule.span_le]
    rintro _ ⟨r, hr, rfl⟩
    rw [SetLike.mem_coe, LinearMap.mem_ker]
    funext x
    have : (x : ι) ≠ r := fun h => hQ x.1 x.2 (h ▸ hr)
    rw [hpr]
    simp [Pi.single_apply, this]
  have hpq : ∀ q : Q, (Pi.single q 1 : Q → K) ∈ W := by
    intro q
    have h1 := hmem q.1 q.2
    rw [← hsup, Submodule.map_sup] at h1
    obtain ⟨a, ha, b, hb, hab⟩ := Submodule.mem_sup.1 h1
    have ha0 : pr a = 0 := LinearMap.mem_ker.1 (hker (hPFE ha))
    have : pr (Pi.single q.1 1) = Pi.single q 1 := by
      funext y
      rw [hpr]
      by_cases hy : y = q
      · subst hy; simp
      · have hy' : y.1 ≠ q.1 := fun h => hy (Subtype.ext h)
        rw [Pi.single_eq_of_ne hy', Pi.single_eq_of_ne hy]
    rw [← this, ← hab, map_add, ha0, zero_add]
    exact ⟨b, hb, rfl⟩
  have htop : W = ⊤ := by
    rw [eq_top_iff, ← (Pi.basisFun K Q).span_eq, Submodule.span_le]
    rintro _ ⟨q, rfl⟩
    simpa using hpq q
  have h1 : finrank K W = Q.card := by
    rw [htop, finrank_top]; simp
  have h2 : finrank K W ≤ finrank K (Kc.map π) := Submodule.finrank_map_le _ _
  have h3 : finrank K (Kc.map π) ≤ finrank K Kc := Submodule.finrank_map_le _ _
  omega

end Slack

/-! ## 4. The port lemma -/

section Port
variable {K Reg C : Type*} [Field K] [DecidableEq Reg] [DecidableEq C] [Preorder C]

theorem gspan_mono_of_subset {L1 L2 : List (Gen K Reg)} (h : ∀ g ∈ L1, g ∈ L2) :
    gspan L1 ≤ gspan L2 := by
  unfold gspan
  apply Submodule.span_mono
  rintro v ⟨g, hg, rfl⟩
  exact ⟨g, h g hg, rfl⟩

/-- **Port lemma** (WHOLEFLOOR R3 §2). `D = {H}` is the port chart `q^⊥`. If it has NO slack
(`s_H = o_H = 0`), `pi(F + E)` lies in `span delta_q`, births in `H` have `pi = 0`, and some register
ends in `H` with `pi(row) = delta_q`, then some PUBLIC register enters `H` from a chart `c0 < H`
(strictly inside), carrying `pi(row) = lam * delta_q`, `lam != 0`, and that row lies in the chart
span `I_{c0}` (of the whole run). So the junk must be cleaned before entry (every entry row has `pi`
in `span delta_q`), and `delta_q in pi(I_{c0})`. -/
theorem port_entry [Fintype Reg] {ι : Type*} [Fintype ι] [DecidableEq ι]
    (Own : Reg → Prop) (H : C)
    (hconv : ∀ a b c, a ∈ ({H} : Set C) → a ≤ b → b ≤ c → c ∈ ({H} : Set C) → b ∈ ({H} : Set C))
    (evs : List (Ev K Reg C)) (hL : LegalW Own (start : St K Reg C) evs)
    (hind : LinearIndependent K
      (fun r : {r : Reg // ¬ Own r ∧ inU ({H} : Set C) (run (start : St K Reg C) evs) r} =>
        (run (start : St K Reg C) evs).row r.1))
    (hFE : Disjoint (Fc Own ({H} : Set C) evs) (Ec Own ({H} : Set C) evs))
    (π : (Reg → K) →ₗ[K] (ι → K)) (q : ι)
    (h0 : slack Own ({H} : Set C) evs = 0)
    (hPFE : (Fc Own ({H} : Set C) evs ⊔ Ec Own ({H} : Set C) evs).map π ≤
      span K {(Pi.single q 1 : ι → K)})
    (hb : ∀ i, Ev.born i H ∈ evs → π (Pi.single i 1) = 0)
    (hy : ∃ y, (run (start : St K Reg C) evs).loc y = some H ∧
      π ((run (start : St K Reg C) evs).row y) = Pi.single q 1) :
    ∃ (pre post : List (Ev K Reg C)) (r : Reg) (c0 : C) (lam : K),
      evs = pre ++ Ev.move r H :: post ∧ (run (start : St K Reg C) pre).loc r = some c0 ∧
      c0 ≤ H ∧ c0 ≠ H ∧ ¬ Own r ∧ lam ≠ 0 ∧
      π ((run (start : St K Reg C) pre).row r) = lam • (Pi.single q 1 : ι → K) ∧
      (run (start : St K Reg C) pre).row r ∈
        gspan (gens (fun c1 c => c1 ∉ ({c0} : Set C) ∧ c ∈ ({c0} : Set C))
          (fun c => c ∈ ({c0} : Set C)) (start : St K Reg C) evs) := by
  classical
  set L := gens (fun c0 c => c0 ∉ ({H} : Set C) ∧ c ∈ ({H} : Set C))
    (fun c => c ∈ ({H} : Set C)) (start : St K Reg C) evs with hLdef
  have hS : slackS Own ({H} : Set C) evs = 0 := by unfold slack at h0; omega
  have hO : slackO Own ({H} : Set C) evs = 0 := by unfold slack at h0; omega
  have hpub : ∀ g ∈ L, ¬ Own g.reg := by
    intro g hg
    have := (List.countP_eq_zero.1 hO) g hg
    simpa using this
  obtain ⟨Kc, hKI, hdis, hsup, hdim⟩ := slack_full Own {H} hconv evs hL hind hFE
  have h0' : finrank K Kc = 0 := by omega
  have hKc : Kc = ⊥ := Submodule.finrank_eq_zero.1 h0'
  rw [hKc, sup_bot_eq] at hsup
  have hπ : (gspan L).map π ≤ span K {(Pi.single q 1 : ι → K)} := by rw [← hsup]; exact hPFE
  have hcov : Cov ({H} : Set C) (gspan L) (run (start : St K Reg C) evs) :=
    CS_run Own {H} _ _ (fun c0 c h0 hc => ⟨h0, hc⟩) (fun c hc => hc) evs hL
  obtain ⟨y, hyl, hyπ⟩ := hy
  have hyin : π ((run (start : St K Reg C) evs).row y) ∈ (gspan L).map π :=
    ⟨_, hcov y H hyl rfl, rfl⟩
  rw [hyπ] at hyin
  have hne : (Pi.single q 1 : ι → K) ≠ 0 := by
    intro h; have := congrFun h q; simp at this
  -- some generator row has nonzero image
  have hex : ∃ g ∈ L, π g.row ≠ 0 := by
    by_contra hno
    simp only [not_exists, not_and, not_not] at hno
    have : (gspan L).map π ≤ ⊥ := by
      unfold gspan
      rw [Submodule.map_span, Submodule.span_le]
      rintro _ ⟨v, ⟨g, hg, rfl⟩, rfl⟩
      exact hno g hg
    exact hne (by simpa using (le_bot_iff.1 this ▸ hyin : (Pi.single q 1 : ι → K) ∈ (⊥ : Submodule K _)))
  obtain ⟨g, hg, hgπ⟩ := hex
  have hent : g.entry = true := by
    by_contra hen
    have hen' : g.entry = false := by simpa using hen
    obtain ⟨c, hbm, hbc, hrow⟩ := gens_birth' _ _ evs (start : St K Reg C) g hg hen'
    have hcH : c = H := hbc
    subst hcH
    apply hgπ
    rw [hrow]; exact hb _ hbm
  have hgin : π g.row ∈ (gspan L).map π := ⟨g.row, Submodule.subset_span ⟨g, hg, rfl⟩, rfl⟩
  obtain ⟨lam, hlam⟩ := Submodule.mem_span_singleton.1 (hπ hgin)
  have hlam0 : lam ≠ 0 := by
    rintro rfl; apply hgπ; rw [← hlam]; simp
  obtain ⟨pre, post, c0, c, hev, hloc, hP, hrow⟩ :=
    entry_source _ _ evs (start : St K Reg C) g hg hent
  have hcH : c = H := hP.2
  subst hcH
  have hL2 := (legalW_append Own (start : St K Reg C) pre (Ev.move g.reg c :: post)).1
    (hev ▸ hL)
  obtain ⟨c0', hc0', hle⟩ := hL2.2.1
  rw [hloc] at hc0'
  cases hc0'
  have hc0H : c0 ≠ c := fun h => hP.1 (by simp [h])
  have hcov0 : Cov ({c0} : Set C) (gspan (gens (fun c1 c => c1 ∉ ({c0} : Set C) ∧ c ∈ ({c0} : Set C))
      (fun c => c ∈ ({c0} : Set C)) (start : St K Reg C) pre)) (run (start : St K Reg C) pre) :=
    CS_run Own {c0} _ _ (fun a b h0 hc => ⟨h0, hc⟩) (fun c hc => hc) pre hL2.1
  have hin : (run (start : St K Reg C) pre).row g.reg ∈ gspan (gens
      (fun c1 c => c1 ∉ ({c0} : Set C) ∧ c ∈ ({c0} : Set C)) (fun c => c ∈ ({c0} : Set C))
      (start : St K Reg C) pre) := hcov0 g.reg c0 hloc rfl
  have hmono : gspan (gens (fun c1 c => c1 ∉ ({c0} : Set C) ∧ c ∈ ({c0} : Set C))
      (fun c => c ∈ ({c0} : Set C)) (start : St K Reg C) pre) ≤
      gspan (gens (fun c1 c => c1 ∉ ({c0} : Set C) ∧ c ∈ ({c0} : Set C))
        (fun c => c ∈ ({c0} : Set C)) (start : St K Reg C) evs) := by
    apply gspan_mono_of_subset
    intro x hx
    rw [hev, gens_append]
    exact List.mem_append_left _ hx
  refine ⟨pre, post, g.reg, c0, lam, hev, hloc, hle (hpub g hg), hc0H, hpub g hg, hlam0, ?_,
    hmono hin⟩
  rw [hrow]; exact hlam.symm

end Port

/-! ## 5. Y-side theorem: sum of slack >= number of ports -/

section YSide
variable {K Reg C : Type*} [Field K] [DecidableEq Reg] [DecidableEq C] [PartialOrder C]

theorem conv_singleton (x : C) :
    ∀ a b c, a ∈ ({x} : Set C) → a ≤ b → b ≤ c → c ∈ ({x} : Set C) → b ∈ ({x} : Set C) := by
  intro a b c ha hab hbc hc
  simp only [Set.mem_singleton_iff] at *
  subst ha; subst hc
  exact le_antisymm hbc hab

/-- **Y-side theorem (WHOLEFLOOR R3 §2, Theorem).** Ports `q : ι` with port charts `Hc q`
(injective, and an ANTICHAIN: no `Hc q' < Hc q`; true for distinct equal-dimension hyperplanes).
Per-chart data: finals independent, `F`/`E` disjoint, `pi(F + E) <= span{delta_r : r in Bs C}`,
with `Bs (Hc q) <= {q}` (at `q^perp` only `delta_q`) and `q not in Bs C` for `C < Hc q`
(the port `q` is not born strictly inside `q^perp`: `q` has odd weight). Births in `Hc q` have
`pi = 0`; each `q` has a register ending in `Hc q` with `pi(row) = delta_q`.
Then `#ports <= sum_{C in T} sigma_C` for any finset `T` containing every `Hc q` and every `C < Hc q`
(`V` is not below any `q^perp`, so `V` is excluded). -/
theorem y_side [Fintype Reg] {ι : Type*} [Fintype ι] [DecidableEq ι]
    (Own : Reg → Prop) (evs : List (Ev K Reg C)) (hL : LegalW Own (start : St K Reg C) evs)
    (Hc : ι → C) (hHinj : Function.Injective Hc) (hanti : ∀ q q', ¬ Hc q' < Hc q)
    (hind : ∀ C' : C, LinearIndependent K
      (fun r : {r : Reg // ¬ Own r ∧ inU ({C'} : Set C) (run (start : St K Reg C) evs) r} =>
        (run (start : St K Reg C) evs).row r.1))
    (hFE : ∀ C' : C, Disjoint (Fc Own ({C'} : Set C) evs) (Ec Own ({C'} : Set C) evs))
    (π : (Reg → K) →ₗ[K] (ι → K)) (Bs : C → Finset ι)
    (hPFE : ∀ C' : C, (Fc Own ({C'} : Set C) evs ⊔ Ec Own ({C'} : Set C) evs).map π ≤
      span K {v | ∃ r ∈ Bs C', v = (Pi.single r 1 : ι → K)})
    (hBH : ∀ q, Bs (Hc q) ⊆ {q}) (hBq : ∀ q C', C' < Hc q → q ∉ Bs C')
    (hb : ∀ q i, Ev.born i (Hc q) ∈ evs → π (Pi.single i 1) = 0)
    (hy : ∀ q, ∃ y, (run (start : St K Reg C) evs).loc y = some (Hc q) ∧
      π ((run (start : St K Reg C) evs).row y) = Pi.single q 1)
    (T : Finset C) (hT1 : ∀ q, Hc q ∈ T) (hT2 : ∀ q C', C' < Hc q → C' ∈ T) :
    Fintype.card ι ≤ ∑ C' ∈ T, slack Own ({C'} : Set C) evs := by
  classical
  have hport : ∀ q, slack Own ({Hc q} : Set C) evs = 0 → ∃ c0 : C, c0 < Hc q ∧
      (Pi.single q 1 : ι → K) ∈ (gspan (gens (fun c1 c => c1 ∉ ({c0} : Set C) ∧ c ∈ ({c0} : Set C))
        (fun c => c ∈ ({c0} : Set C)) (start : St K Reg C) evs)).map π := by
    intro q h0
    have hPq : (Fc Own ({Hc q} : Set C) evs ⊔ Ec Own ({Hc q} : Set C) evs).map π ≤
        span K {(Pi.single q 1 : ι → K)} := by
      refine (hPFE (Hc q)).trans ?_
      apply Submodule.span_mono
      rintro v ⟨r, hr, rfl⟩
      have := hBH q hr
      simp only [Finset.mem_singleton] at this
      subst this
      exact rfl
    obtain ⟨pre, post, r, c0, lam, hev, hloc, hle, hne, hpub, hlam, hπr, hin⟩ :=
      port_entry Own (Hc q) (conv_singleton _) evs hL (hind _) (hFE _) π q h0 hPq
        (fun i hi => hb q i hi) (hy q)
    refine ⟨c0, lt_of_le_of_ne hle hne, ?_⟩
    have : (Pi.single q 1 : ι → K) = lam⁻¹ • π ((run (start : St K Reg C) pre).row r) := by
      rw [hπr, smul_smul, inv_mul_cancel₀ hlam, one_smul]
    rw [this]
    exact Submodule.smul_mem _ _ ⟨_, hin, rfl⟩
  set sl : C → ℕ := fun C' => slack Own ({C'} : Set C) evs with hsl
  let ch : ι → C := fun q =>
    if h : sl (Hc q) = 0 then Classical.choose (hport q h) else Hc q
  have hchspec : ∀ q, sl (Hc q) = 0 → ch q < Hc q ∧ (Pi.single q 1 : ι → K) ∈
      (gspan (gens (fun c1 c => c1 ∉ ({ch q} : Set C) ∧ c ∈ ({ch q} : Set C))
        (fun c => c ∈ ({ch q} : Set C)) (start : St K Reg C) evs)).map π := by
    intro q h
    have := Classical.choose_spec (hport q h)
    simp only [ch, dif_pos h]
    exact this
  refine y_side_sum Hc hHinj sl T ch hT1 ?_ ?_
  · intro q h
    obtain ⟨hlt, _⟩ := hchspec q h
    exact ⟨hT2 q _ hlt, fun q' heq => hanti q q' (heq ▸ hlt)⟩
  · intro C'
    have := charge Own ({C'} : Set C) (conv_singleton C') evs hL (hind C') (hFE C') π (Bs C')
      (hPFE C') (Finset.univ.filter (fun q => sl (Hc q) = 0 ∧ ch q = C'))
      (by
        intro q hq
        simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hq
        obtain ⟨h0, hc⟩ := hq
        have := (hchspec q h0).1
        rw [hc] at this
        exact hBq q C' this)
      (by
        intro q hq
        simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hq
        obtain ⟨h0, hc⟩ := hq
        have := (hchspec q h0).2
        rw [hc] at this
        exact this)
    exact this

/-- **Forced stops** (arithmetic corollary). If `sigma_C = s_C + o_C`, `sum sigma >= n` and the owned
part is `sum o <= m`, then the passers number at least `n - m`. Here `m` must count owned
BIRTHS in the charts as well as owned entering MOVEs (both are generators of `I_C`). -/
theorem forced_stops {D : Type*} (T : Finset D) (s o : D → ℕ) (n m : ℕ)
    (hsum : n ≤ ∑ C ∈ T, (s C + o C)) (hm : ∑ C ∈ T, o C ≤ m) : n - m ≤ ∑ C ∈ T, s C := by
  rw [Finset.sum_add_distrib] at hsum
  omega

end YSide

/-! ## 6. Without the antichain hypothesis the counting step is false -/

/-- Two ports with `H q0 = 0 < H q1 = 1`, `sigma(0) = 1`, `sigma(1) = 0`, `q1` fed from chart `0`:
every hypothesis of `y_side_sum` except the `ch q != Hc q'` clause holds, but `2 > 1 = sum sigma`.
(One unit of slack at chart `0` would serve both as `q0`'s own slack and as `q1`'s feeding slack.) -/
theorem antichain_needed :
    ∃ (Hc : Fin 2 → ℕ) (sl : ℕ → ℕ) (ch : Fin 2 → ℕ),
    (∀ q, Hc q ∈ ({0, 1} : Finset ℕ)) ∧
    (∀ q, sl (Hc q) = 0 → ch q ∈ ({0, 1} : Finset ℕ)) ∧
    (∀ C, (Finset.univ.filter (fun q => sl (Hc q) = 0 ∧ ch q = C)).card ≤ sl C) ∧
    ¬ (Fintype.card (Fin 2) ≤ ∑ C ∈ ({0, 1} : Finset ℕ), sl C) := by
  refine ⟨fun q => q.1, fun C => if C = 0 then 1 else 0, fun _ => 0, by decide, by decide, ?_,
    by decide⟩
  intro C
  by_cases hC : C = 0
  · subst hC; decide
  · have : (Finset.univ.filter (fun q : Fin 2 =>
        (fun C : ℕ => if C = 0 then 1 else 0) ((fun q : Fin 2 => q.1) q) = 0 ∧ (fun _ : Fin 2 => 0) q = C)) = ∅ := by
      ext q; simp [Ne.symm hC]
    rw [this]; simp

end WFPort

#print axioms WFPort.hcount_full
#print axioms WFPort.slack_full
#print axioms WFPort.charge
#print axioms WFPort.port_entry
#print axioms WFPort.y_side_sum
#print axioms WFPort.y_side
#print axioms WFPort.forced_stops
#print axioms WFPort.antichain_needed
