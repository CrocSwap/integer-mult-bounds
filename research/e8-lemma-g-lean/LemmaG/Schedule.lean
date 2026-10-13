/-
Lemma G, schedule part: the compensation segment and the centre scatter are well labelled,
their moves are strict nested monotone chains, and the paid ranks telescope.
Apache-2.0.  Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

Frames are elements of an arbitrary partial order `Λ` with a strictly monotone rank
`rk : Λ → ℕ` (for subspaces of `F₂⁹`: inclusion and dimension, see `LemmaG.Frames`).
-/
import LemmaG.Stream

namespace LemmaG

open Stream Event

/-! ### Chains ordered by rank -/

section Rank

variable {Λ : Type*} [PartialOrder Λ] {rk : Λ → ℕ}

/-- In a chain, a rank comparison is an inclusion (PROOF.md, Claim 2). -/
theorem le_of_rk_le (hrk : StrictMono rk) {a b : Λ} (hc : a ≤ b ∨ b ≤ a) (h : rk a ≤ rk b) :
    a ≤ b := by
  rcases hc with hab | hba
  · exact hab
  · rcases hba.lt_or_eq with hlt | heq
    · exact absurd (hrk hlt) (not_lt.2 h)
    · exact heq ▸ le_rfl

/-- In a chain, equal rank is equality. -/
theorem eq_of_rk_eq (hrk : StrictMono rk) {a b : Λ} (hc : a ≤ b ∨ b ≤ a) (h : rk a = rk b) :
    a = b :=
  le_antisymm (le_of_rk_le hrk hc h.le) (le_of_rk_le hrk hc.symm h.ge)

end Rank

/-! ### The mover emitter

A schedule is a list of gates.  Each gate names a *mover* (the register that changes frame:
a target in the compensation segment, the private copy in the centre phase), a static
*partner* (the entering helper, resp. the served target or the centre register), the gate's
frame, a coefficient and a direction.  The emitter moves the mover to the gate's frame when
it is not already there and then emits the gate (PROOF.md §2.4, emission steps 3 and 6). -/

/-- One gate of a schedule. -/
structure Item (ι Λ K : Type*) where
  mv : ι
  pt : ι
  F : Λ
  q : K
  into : Bool

variable {ι Λ K : Type*} [DecidableEq ι] [DecidableEq Λ]

/-- The gate: `mv += q·pt` when `into`, otherwise `pt += q·mv`. -/
def Item.gate (it : Item ι Λ K) : Event ι Λ K :=
  if it.into then .add it.mv it.pt it.q else .add it.pt it.mv it.q

/-- The move before a gate: nothing if the mover is already at the gate's frame. -/
def Item.move (l : ι → Λ) (it : Item ι Λ K) : List (Event ι Λ K) :=
  if l it.mv = it.F then [] else [Event.relabel it.mv (l it.mv) it.F]

/-- The emitted events. -/
def emit : (ι → Λ) → List (Item ι Λ K) → List (Event ι Λ K)
  | _, [] => []
  | l, it :: its => it.move l ++ (it.gate :: emit (Function.update l it.mv it.F) its)

/-- The labels after the schedule. -/
def moveLab : (ι → Λ) → List (Item ι Λ K) → (ι → Λ)
  | l, [] => l
  | l, it :: its => moveLab (Function.update l it.mv it.F) its

omit [DecidableEq Λ] in
theorem moveLab_untouched : ∀ (its : List (Item ι Λ K)) (l : ι → Λ) (m : ι),
    (∀ a ∈ its, a.mv ≠ m) → moveLab l its m = l m
  | [], _, _, _ => rfl
  | it :: its, l, m, h => by
    simp only [moveLab]
    rw [moveLab_untouched its _ m (fun a ha => h a (List.mem_cons_of_mem _ ha))]
    exact Function.update_of_ne (Ne.symm (h it List.mem_cons_self)) _ _

omit [DecidableEq Λ] in
/-- A mover ends at the frame of one of its gates. -/
theorem moveLab_mem : ∀ (its : List (Item ι Λ K)) (l : ι → Λ) (m : ι),
    (∃ a ∈ its, a.mv = m) → ∃ a ∈ its, a.mv = m ∧ moveLab l its m = a.F
  | [], _, _, ⟨_, ha, _⟩ => absurd ha List.not_mem_nil
  | it :: its, l, m, _ => by
    simp only [moveLab]
    by_cases hlater : ∃ a ∈ its, a.mv = m
    · obtain ⟨a, ha, ham, hfin⟩ := moveLab_mem its _ m hlater
      exact ⟨a, List.mem_cons_of_mem _ ha, ham, hfin⟩
    · push_neg at hlater
      rw [moveLab_untouched its _ m hlater]
      by_cases him : it.mv = m
      · subst him; exact ⟨it, List.mem_cons_self, rfl, by simp⟩
      · obtain ⟨a, ha, ham⟩ := ‹∃ a ∈ it :: its, a.mv = m›
        rcases List.mem_cons.1 ha with rfl | ha'
        · exact absurd ham him
        · exact absurd ham (hlater a ha')

omit [DecidableEq Λ] in
/-- If the frames of each mover are `R`-sorted (`R` transitive and reflexive), the mover ends
`R`-above every frame of its gates: with `R = (≤)` the target ends at `L_t = max ℰ_t`. -/
theorem moveLab_top (R : Λ → Λ → Prop) (hrefl : ∀ a, R a a)
    (htrans : ∀ a b c, R a b → R b c → R a c) :
    ∀ (its : List (Item ι Λ K)) (l : ι → Λ),
      its.Pairwise (fun a b => a.mv = b.mv → R a.F b.F) →
      ∀ a ∈ its, R a.F (moveLab l its a.mv)
  | [], _, _, a, ha => absurd ha List.not_mem_nil
  | it :: its, l, hs, a, ha => by
    simp only [moveLab]
    rw [List.pairwise_cons] at hs
    by_cases hlater : ∃ b ∈ its, b.mv = a.mv
    · obtain ⟨b, hb, hbm⟩ := hlater
      have hb' := moveLab_top R hrefl htrans its (Function.update l it.mv it.F) hs.2 b hb
      rw [hbm] at hb'
      rcases List.mem_cons.1 ha with rfl | ha'
      · exact htrans _ _ _ (hs.1 b hb hbm.symm) hb'
      · exact moveLab_top R hrefl htrans its _ hs.2 a ha'
    · push_neg at hlater
      rw [moveLab_untouched its _ a.mv hlater]
      rcases List.mem_cons.1 ha with rfl | ha'
      · simp [hrefl]
      · exact absurd rfl (hlater a ha')

/-- **Emitter lemma.**  Hypotheses: partners never move; each partner sits at its gate's frame;
each mover starts `R`-below each of its frames; along the list, the frames of each mover are
`R`-sorted.  Conclusions: the emitted stream is well labelled, its labels end at `moveLab`, and
every relabel it emits is a proper `R`-step. -/
theorem emit_spec (R : Λ → Λ → Prop) : ∀ (its : List (Item ι Λ K)) (l : ι → Λ),
    (∀ a ∈ its, ∀ b ∈ its, b.mv ≠ a.pt) →
    (∀ a ∈ its, l a.pt = a.F) →
    (∀ a ∈ its, R (l a.mv) a.F) →
    its.Pairwise (fun a b => a.mv = b.mv → R a.F b.F) →
    WellLabelled (emit l its) l ∧ labRun (emit l its) l = moveLab l its ∧
      (∀ r A B, Event.relabel r A B ∈ emit l its → R A B ∧ A ≠ B)
  | [], _, _, _, _, _ => ⟨trivial, rfl, fun _ _ _ h => absurd h List.not_mem_nil⟩
  | it :: its, l, hpt, hptl, hinit, hsort => by
    rw [List.pairwise_cons] at hsort
    set l1 := Function.update l it.mv it.F with hl1
    have hne : it.mv ≠ it.pt := hpt it List.mem_cons_self it List.mem_cons_self
    -- the move (possibly empty) brings the mover to the gate's frame
    have hpre : labRun (it.move l) l = l1 := by
      unfold Item.move; split_ifs with h
      · rw [hl1]; show l = _; rw [← h]; exact (Function.update_eq_self _ _).symm
      · rfl
    have hwpre : WellLabelled (it.move l) l := by
      unfold Item.move; split_ifs
      · trivial
      · exact ⟨rfl, trivial⟩
    -- the gate is admissible: both operands at the gate's frame
    have hgate : it.gate.Admissible l1 := by
      have h1 : l1 it.mv = it.F := by simp [hl1]
      have h2 : l1 it.pt = it.F := by
        rw [hl1, Function.update_of_ne (Ne.symm hne)]; exact hptl it List.mem_cons_self
      unfold Item.gate; split_ifs <;> simp [Admissible, h1, h2]
    have hglab : it.gate.lab l1 = l1 := by unfold Item.gate; split_ifs <;> rfl
    -- the induction hypothesis for the remaining gates
    have ih := emit_spec R its l1
      (fun a ha b hb => hpt a (List.mem_cons_of_mem _ ha) b (List.mem_cons_of_mem _ hb))
      (fun a ha => by
        have : a.pt ≠ it.mv := fun h =>
          hpt a (List.mem_cons_of_mem _ ha) it List.mem_cons_self h.symm
        rw [hl1, Function.update_of_ne this]; exact hptl a (List.mem_cons_of_mem _ ha))
      (fun a ha => by
        by_cases ham : a.mv = it.mv
        · rw [ham, hl1, Function.update_self]; exact hsort.1 a ha ham.symm
        · rw [hl1, Function.update_of_ne ham]; exact hinit a (List.mem_cons_of_mem _ ha))
      hsort.2
    refine ⟨?_, ?_, ?_⟩
    · simp only [emit]
      rw [wellLabelled_append, hpre]
      exact ⟨hwpre, hgate, by rw [hglab]; exact ih.1⟩
    · simp only [emit, moveLab]
      rw [labRun_append, hpre]
      show labRun (emit l1 its) (it.gate.lab l1) = moveLab l1 its
      rw [hglab]; exact ih.2.1
    · intro r A B hmem
      simp only [emit, List.mem_append, List.mem_cons] at hmem
      rcases hmem with hm | hm | hm
      · unfold Item.move at hm
        split_ifs at hm with h
        · exact absurd hm List.not_mem_nil
        · rw [List.mem_singleton] at hm
          cases hm
          exact ⟨hinit it List.mem_cons_self, h⟩
      · unfold Item.gate at hm; split_ifs at hm
      · exact ih.2.2 r A B hm

/-- **Exactness needs no order condition.**  The emitted stream is well labelled as soon as the
partners never move and each partner sits at its gate's frame: (a)–(d) are not used. -/
theorem emit_wellLabelled (its : List (Item ι Λ K)) (l : ι → Λ)
    (hpt : ∀ a ∈ its, ∀ b ∈ its, b.mv ≠ a.pt) (hptl : ∀ a ∈ its, l a.pt = a.F) :
    WellLabelled (emit l its) l :=
  (emit_spec (fun _ _ => True) its l hpt hptl (fun _ _ => trivial)
    (List.pairwise_of_forall (fun _ _ _ => trivial))).1

/-! ### Clause (b): the compensation segment (Claims 1 and 2) -/

/-- **Compensation segment.**  The gates `y_t += c·x_j` (mover = target `t`, partner = gauge
helper `j`, frame `E_j`), emitted in order of rank.  Hypotheses: helpers are not targets;
each helper is at its entrance label (virtual entrance, untouched before); each target starts
below each of its entrances (at `0`); (b) the entrances of each target form a chain.  Then the
segment is well labelled, every climb it emits is a strict nested ascent, and each target ends
at the largest of its entrances `L_t` (above all, and attained). -/
theorem comp_segment [PartialOrder Λ] (rk : Λ → ℕ) (hrk : StrictMono rk)
    (its : List (Item ι Λ K)) (l : ι → Λ)
    (hdisj : ∀ a ∈ its, ∀ b ∈ its, b.mv ≠ a.pt)
    (hentr : ∀ a ∈ its, l a.pt = a.F)
    (hbot : ∀ a ∈ its, l a.mv ≤ a.F)
    (hchain : ∀ a ∈ its, ∀ b ∈ its, a.mv = b.mv → a.F ≤ b.F ∨ b.F ≤ a.F)
    (hsorted : its.Pairwise (fun a b => rk a.F ≤ rk b.F)) :
    WellLabelled (emit l its) l ∧
      (∀ r A B, Event.relabel r A B ∈ emit l its → A < B) ∧
      (∀ a ∈ its, a.F ≤ labRun (emit l its) l a.mv ∧
        ∃ b ∈ its, b.mv = a.mv ∧ labRun (emit l its) l a.mv = b.F) ∧
      (∀ m, (∀ a ∈ its, a.mv ≠ m) → labRun (emit l its) l m = l m) := by
  have hle : its.Pairwise (fun a b => a.mv = b.mv → a.F ≤ b.F) :=
    hsorted.imp_of_mem (fun ha hb hr hm => le_of_rk_le hrk (hchain _ ha _ hb hm) hr)
  obtain ⟨hw, hlab, hrel⟩ := emit_spec (· ≤ ·) its l hdisj hentr hbot hle
  refine ⟨hw, fun r A B h => lt_of_le_of_ne (hrel r A B h).1 (hrel r A B h).2, ?_, ?_⟩
  · intro a ha
    rw [hlab]
    exact ⟨moveLab_top (· ≤ ·) (fun _ => le_rfl) (fun _ _ _ => le_trans) its l hle a ha,
      moveLab_mem its l a.mv ⟨a, ha, rfl⟩⟩
  · intro m hm; rw [hlab]; exact moveLab_untouched its l m hm

/-! ### Clause (c): the centre phase (Claim 4) -/

/-- **Centre phase, forward orientation.**  Copy the centre register `r` (label `c`) into the
private register `C`, then descend through the levels of the served targets in order of
decreasing rank, scattering `y_t += q·C` at each level, then clear `C`.  Hypotheses: the copy
register is neither the centre register nor a served target; the centre register is at `c`;
each served target is at its level; (c) the levels form a chain inside `c`.  Then the phase is
well labelled and every centre step is a strict nested descent. -/
theorem centre_forward [PartialOrder Λ] (rk : Λ → ℕ) (hrk : StrictMono rk)
    (C r : ι) (c : Λ) (its : List (Item ι Λ K)) (l : ι → Λ) (Fend : Λ)
    (hmv : ∀ a ∈ its, a.mv = C) (hCpt : ∀ a ∈ its, a.pt ≠ C)
    (hr : l r = c) (hlev : ∀ a ∈ its, l a.pt = a.F)
    (hin : ∀ a ∈ its, a.F ≤ c)
    (hchain : ∀ a ∈ its, ∀ b ∈ its, a.F ≤ b.F ∨ b.F ≤ a.F)
    (hsorted : its.Pairwise (fun a b => rk b.F ≤ rk a.F)) :
    WellLabelled ([Event.copy C r c] ++ emit (Function.update l C c) its ++ [Event.clear C Fend]) l ∧
      (∀ r' A B, Event.relabel r' A B ∈ emit (Function.update l C c) its → B < A) := by
  have hge : its.Pairwise (fun a b => a.mv = b.mv → b.F ≤ a.F) :=
    hsorted.imp_of_mem (fun ha hb hr' _ => le_of_rk_le hrk (hchain _ hb _ ha) hr')
  have hspec := emit_spec (fun a b => b ≤ a) its (Function.update l C c)
    (fun a _ b hb => by rw [hmv b hb]; exact (hCpt a ‹_›).symm)
    (fun a ha => by rw [Function.update_of_ne (hCpt a ha)]; exact hlev a ha)
    (fun a ha => by rw [hmv a ha, Function.update_self]; exact hin a ha)
    hge
  refine ⟨?_, fun r' A B h => lt_of_le_of_ne (hspec.2.2 r' A B h).1 (Ne.symm (hspec.2.2 r' A B h).2)⟩
  rw [wellLabelled_append, wellLabelled_append]
  refine ⟨⟨⟨hr, trivial⟩, ?_⟩, ?_⟩
  · exact hspec.1
  · exact ⟨trivial, trivial⟩

/-- **Centre phase, backward orientation.**  Clear `C` at the bottom level, ascend through the
levels in order of increasing rank gathering `C += q·y_t`, finally `r += -C` at `c` (the last
gate, partner `r` at frame `c`).  Hypotheses as in the forward orientation, with the gates now
sorted by increasing rank and the final gate at `c`.  Then the phase is well labelled and every
centre step is a strict nested ascent. -/
theorem centre_backward [PartialOrder Λ] (rk : Λ → ℕ) (hrk : StrictMono rk)
    (C : ι) (bottom : Λ) (its : List (Item ι Λ K)) (l : ι → Λ)
    (hmv : ∀ a ∈ its, a.mv = C) (hCpt : ∀ a ∈ its, a.pt ≠ C)
    (hlev : ∀ a ∈ its, l a.pt = a.F)
    (hbot : ∀ a ∈ its, bottom ≤ a.F)
    (hchain : ∀ a ∈ its, ∀ b ∈ its, a.F ≤ b.F ∨ b.F ≤ a.F)
    (hsorted : its.Pairwise (fun a b => rk a.F ≤ rk b.F)) :
    WellLabelled ([Event.clear C bottom] ++ emit (Function.update l C bottom) its) l ∧
      (∀ r' A B, Event.relabel r' A B ∈ emit (Function.update l C bottom) its → A < B) := by
  have hle : its.Pairwise (fun a b => a.mv = b.mv → a.F ≤ b.F) :=
    hsorted.imp_of_mem (fun ha hb hr' _ => le_of_rk_le hrk (hchain _ ha _ hb) hr')
  have hspec := emit_spec (· ≤ ·) its (Function.update l C bottom)
    (fun a _ b hb => by rw [hmv b hb]; exact (hCpt a ‹_›).symm)
    (fun a ha => by rw [Function.update_of_ne (hCpt a ha)]; exact hlev a ha)
    (fun a ha => by rw [hmv a ha, Function.update_self]; exact hbot a ha)
    hle
  refine ⟨?_, fun r' A B h => lt_of_le_of_ne (hspec.2.2 r' A B h).1 (hspec.2.2 r' A B h).2⟩
  rw [wellLabelled_append]
  exact ⟨⟨trivial, trivial⟩, hspec.1⟩

/-! ### Accounting: paid ranks telescope -/

/-- The paid rank of the relabels of register `m` in a stream: `|rk B - rk A|` per relabel. -/
def paid (rk : Λ → ℕ) (m : ι) : List (Event ι Λ K) → ℕ
  | [] => 0
  | Event.relabel r A B :: es => (if r = m then ((rk B : ℤ) - rk A).natAbs else 0) + paid rk m es
  | _ :: es => paid rk m es

omit [DecidableEq Λ] in
/-- **Telescoping.**  If every relabel of `m` in a well-labelled stream is rank-ascending and
nothing copies into or clears `m`, the paid rank of `m` is `rk λ¹(m) - rk λ⁰(m)`.  Nested
ascents (clause G2) are rank-ascending. -/
theorem paid_telescopes (rk : Λ → ℕ) (m : ι) :
    ∀ (es : List (Event ι Λ K)) (l : ι → Λ), WellLabelled es l →
      (∀ A B, Event.relabel m A B ∈ es → rk A ≤ rk B) →
      (∀ e ∈ es, ∀ F, (∀ r, e ≠ Event.copy m r F) ∧ e ≠ Event.clear m F) →
      (paid rk m es : ℤ) = rk (labRun es l m) - rk (l m)
  | [], _, _, _, _ => by simp [paid, labRun]
  | e :: es, l, hw, hasc, hcc => by
    have ih := paid_telescopes rk m es (e.lab l) hw.2
      (fun A B h => hasc A B (List.mem_cons_of_mem _ h))
      (fun e' he' => hcc e' (List.mem_cons_of_mem _ he'))
    have hcc0 := hcc e List.mem_cons_self
    simp only [labRun]
    cases e with
    | relabel r A B =>
      have hA : l r = A := hw.1
      simp only [paid, Nat.cast_add, ih]
      by_cases hrm : r = m
      · subst hrm
        have hab := hasc A B List.mem_cons_self
        simp only [Event.lab, Function.update_self, if_true]
        rw [Int.natAbs_of_nonneg (by omega), hA]
        omega
      · have h1 : (Event.relabel r A B : Event ι Λ K).lab l m = l m :=
          Function.update_of_ne (Ne.symm hrm) _ _
        rw [h1]; simp [hrm]
    | add t s q => simpa [paid, Event.lab] using ih
    | scale t q => simpa [paid, Event.lab] using ih
    | copy c r F =>
      have hc : c ≠ m := fun h => (hcc0 F).1 r (by rw [h])
      simp only [paid]
      rw [ih]; simp [Event.lab, Function.update_of_ne (Ne.symm hc)]
    | clear c F =>
      have hc : c ≠ m := fun h => (hcc0 F).2 (by rw [h])
      simp only [paid]
      rw [ih]; simp [Event.lab, Function.update_of_ne (Ne.symm hc)]

end LemmaG
