/-
STAY-REMOVABILITY RULE (CONTACTARCH/R1.md §4, WHOLEFLOOR R3 §4), lane LEAN-NEXT25, Nov 17.
TokenCancel op model. See StayRemove.md.
-/
import Nov15.TCLemma
import Nov15.WFCount

set_option linter.unusedSectionVars false

namespace StayRemove
open TokenCancel TCLemma

variable {K Reg C : Type*} [Field K] [DecidableEq Reg] [DecidableEq C] [Preorder C]

/-- **Stay-removability rule (necessary condition).** Split helper `h` at its stay at chart `c`,
at the moment whose state is `st` (h resident at `c`): `h` keeps the part up to the moment and dies at
`c`; `post` is ANY continuation of the new word (relabelled later events plus whatever conversion
ops are added). If `post` is ascending-legal, destroys no e_h content, reads `h` only at charts
inside `c`, and ends with every other register e_h-free, then at the split moment EVERY holder of
e_h (`r ≠ h` with `row r h ≠ 0`) sits at a chart inside `c`.
This is `held_run` (the engine of `TC_last_read`) applied to the continuation only. -/
theorem stay_removable_necessary (h : Reg) (c : C) (st : St K Reg C) (post : List (Ev K Reg C))
    (hL : LegalA st post) (hN : ND h st post)
    (hreads : ∀ i a c', Ev.add i h a c' ∈ post → c' ≤ c)
    (hf : ∀ r, r ≠ h → (run st post).row r h = 0) : Held h c st :=
  held_run post st h c hL hN hreads hf

/-- A register that is never MOVEd stays put (ascending legal run). -/
theorem loc_stationary : ∀ (post : List (Ev K Reg C)) (s : St K Reg C) (h : Reg) (c : C),
    LegalA s post → (∀ c', Ev.move h c' ∉ post) → s.loc h = some c →
    (run s post).loc h = some c ∧ ∀ i a c', Ev.add i h a c' ∈ post → c' = c
  | [], s, h, c, _, _, hl => ⟨hl, by simp⟩
  | e :: es, s, h, c, ⟨hL, hLs⟩, hm, hl => by
    have hm' : ∀ c', Ev.move h c' ∉ es := fun c' hc => hm c' (List.mem_cons_of_mem _ hc)
    have hstep : (step s e).loc h = some c := by
      cases e with
      | born i c1 =>
        have hn : s.loc i = none := hL
        have : h ≠ i := by rintro rfl; rw [hn] at hl; cases hl
        simpa [step, Function.update_of_ne this] using hl
      | init i c1 =>
        have hn : s.loc i = none := hL
        have : h ≠ i := by rintro rfl; rw [hn] at hl; cases hl
        simpa [step, Function.update_of_ne this] using hl
      | move i c1 =>
        have : h ≠ i := by
          rintro rfl; exact hm c1 (by simp)
        simpa [step, Function.update_of_ne this] using hl
      | add i j a c1 => simpa [step] using hl
      | scale i u c1 => simpa [step] using hl
      | clear i c1 => simpa [step] using hl
      | copy i j c1 => simpa [step] using hl
    obtain ⟨h1, h2⟩ := loc_stationary es (step s e) h c hLs hm' hstep
    refine ⟨h1, ?_⟩
    intro i a c' hmem
    rcases List.mem_cons.1 hmem with he | hmem'
    · subst he
      have : s.loc h = some c' := hL.2.2
      rw [hl] at this
      exact (Option.some.inj this).symm
    · exact h2 i a c' hmem'

/-- **Stay-removability rule, stationary form.** If `h` dies at `c` (never moves again), the read
condition is automatic: every read of `h` after the split is at `c`. So splitting `h` at a moment
of its stay at `c` is possible only if every e_h holder sits at a chart inside `c` at that moment. -/
theorem stay_removable (h : Reg) (c : C) (st : St K Reg C) (post : List (Ev K Reg C))
    (hloc : st.loc h = some c) (hL : LegalA st post) (hN : ND h st post)
    (hstat : ∀ c', Ev.move h c' ∉ post)
    (hf : ∀ r, r ≠ h → (run st post).row r h = 0) : Held h c st :=
  stay_removable_necessary h c st post hL hN
    (fun i a c' hm => ((loc_stationary post st h c hL hstat hloc).2 i a c' hm).le) hf

/-- **Tight form via `TC_last_read`.** If the last read of `h` in the new word is at chart `R`
(it lies before the split moment or at `c`), then at EVERY moment of the new word, in particular
at the split moment, every e_h holder sits inside `R` (not just inside `c`). -/
theorem stay_removable_last_read (h : Reg) (R : C) (i0 : Reg) (a0 : K) (s0 : St K Reg C)
    (pre post : List (Ev K Reg C))
    (hpost : ∀ i a c, Ev.add i h a c ∉ post)
    (hL : LegalA s0 (pre ++ Ev.add i0 h a0 R :: post))
    (hN : ND h s0 (pre ++ Ev.add i0 h a0 R :: post))
    (hf : ∀ r, r ≠ h → (run s0 (pre ++ Ev.add i0 h a0 R :: post)).row r h = 0) (k : ℕ) :
    Held h R (run s0 ((pre ++ Ev.add i0 h a0 R :: post).take k)) :=
  TC_last_read h R i0 a0 s0 pre post hpost hL hN hf k

/-! ### The paper's "public holders" wording is false once an owned register may descend. -/

namespace CE
open WFCount
abbrev E := Ev ℚ (Fin 3) ℕ
def Own : Fin 3 → Prop := fun i => i = 2
/-- registers: `0` = helper h, `1` = public receiver r, `2` = owned j. -/
def pre : List E :=
  [.born 0 0, .born 1 0, .born 2 0, .add 1 0 1 0, .add 2 0 1 0,
   .move 1 2, .move 2 2, .move 0 1]
/-- the BASE word: everything ascends (all registers), h stays at chart 1 for one moment. -/
def base : List E := pre ++ [.move 0 3, .add 1 2 (-1) 2, .move 2 3, .add 2 0 (-1) 3]
/-- the SPLIT word: `h` dies at chart `1`; the owned `j` cleans r at 2, DESCENDS to 1, reads h. -/
def split : List E := pre ++ [.add 1 2 (-1) 2, .move 2 1, .add 2 0 (-1) 1]

theorem base_legalA : LegalA (start : St ℚ (Fin 3) ℕ) base := by
  simp [base, pre, start, LegalA, LegalEvA, step]

theorem base_nd : ND (0 : Fin 3) (start : St ℚ (Fin 3) ℕ) base := by
  simp [base, pre, start, ND, NDEv, step, Function.update, Pi.single]

theorem base_clean : ∀ r : Fin 3, r ≠ 0 → (run (start : St ℚ (Fin 3) ℕ) base).row r 0 = 0 := by
  intro r hr
  fin_cases r
  · exact absurd rfl hr
  · simp [base, pre, start, run, step, Function.update, Pi.single]
  · simp [base, pre, start, run, step, Function.update, Pi.single]

theorem split_legalW : LegalW Own (start : St ℚ (Fin 3) ℕ) split := by
  simp [split, pre, start, LegalW, LegalEvW, step, Own]

theorem split_nd : ND (0 : Fin 3) (start : St ℚ (Fin 3) ℕ) split := by
  simp [split, pre, start, ND, NDEv, step, Function.update, Pi.single]

theorem split_clean : ∀ r : Fin 3, r ≠ 0 → (run (start : St ℚ (Fin 3) ℕ) split).row r 0 = 0 := by
  intro r hr
  fin_cases r
  · exact absurd rfl hr
  · simp [split, pre, start, run, step, Function.update, Pi.single]
  · simp [split, pre, start, run, step, Function.update, Pi.single]

/-- all reads of `h = 0` in the split word are at charts `≤ 1` (h dies at chart 1). -/
theorem split_reads : ∀ i a c, Ev.add i (0 : Fin 3) a c ∈ split → c ≤ 1 := by
  intro i a c hm
  simp [split, pre] at hm
  rcases hm with ⟨_, _, h0⟩ | ⟨_, _, h0⟩ | ⟨_, _, h0⟩ <;> omega

/-- At the split moment (after `pre`: `h` has just arrived at chart `1`, and in the base word
leaves at once, so this is the only moment of the stay) the public receiver `1` holds e_h at
chart `2`, which is NOT inside chart `1`. -/
theorem not_held : ¬ Held (0 : Fin 3) (1 : ℕ) (run (start : St ℚ (Fin 3) ℕ) pre) := by
  intro H
  have := H 1 (by decide) (by simp [pre, start, run, step, Function.update, Pi.single])
  obtain ⟨c, hc, hle⟩ := this
  simp [pre, start, run, step, Function.update] at hc
  subst hc
  omega

end CE

end StayRemove

#print axioms StayRemove.stay_removable_necessary
#print axioms StayRemove.stay_removable
#print axioms StayRemove.stay_removable_last_read
#print axioms StayRemove.CE.not_held
#print axioms StayRemove.CE.split_legalW
