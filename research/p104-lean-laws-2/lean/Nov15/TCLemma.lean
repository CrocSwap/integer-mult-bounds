/-
LEMMA TC (CANCELBUS/R1.md) in the TokenCancel op model, lane LEAN-NEXT22, Nov 16.
Charts carry a `Preorder` (chart containment `c ≤ R` = "c ⊆ R"). Public moves ascend.
See TCLemma.md.
-/
import Nov15.TokenCancel

set_option linter.unusedSectionVars false

namespace TCLemma
open TokenCancel

variable {K Reg C : Type*} [Field K] [DecidableEq Reg] [DecidableEq C] [Preorder C]

/-- Ascending legality (all registers public): co-presence, births/INITs of absent registers,
every MOVE goes to a chart containing the old one, SCALE by a nonzero scalar. -/
def LegalEvA (s : St K Reg C) : Ev K Reg C → Prop
  | .born i _ => s.loc i = none
  | .init i _ => s.loc i = none
  | .move i c => ∃ c0, s.loc i = some c0 ∧ c0 ≤ c
  | .add i j _ c => i ≠ j ∧ s.loc i = some c ∧ s.loc j = some c
  | .scale i u c => u ≠ 0 ∧ s.loc i = some c
  | .clear i c => s.loc i = some c
  | .copy i j c => s.loc i = some c ∧ s.loc j = some c

def LegalA : St K Reg C → List (Ev K Reg C) → Prop
  | _, [] => True
  | s, e :: es => LegalEvA s e ∧ LegalA (step s e) es

/-- "No destruction": an event that overwrites register `i ≠ h` (birth, INIT, CLEAR, COPY into i)
only does so when `i` carries no e_h content. This is the paper's "no CLEAR escape" clause. -/
def NDEv (h : Reg) (s : St K Reg C) : Ev K Reg C → Prop
  | .born i _ => i ≠ h → s.row i h = 0
  | .init i _ => i ≠ h → s.row i h = 0
  | .clear i _ => i ≠ h → s.row i h = 0
  | .copy i _ _ => i ≠ h → s.row i h = 0
  | _ => True

def ND (h : Reg) : St K Reg C → List (Ev K Reg C) → Prop
  | _, [] => True
  | s, e :: es => NDEv h s e ∧ ND h (step s e) es

/-- Every register other than `h` with e_h content sits at a chart inside `R`. -/
def Held (h : Reg) (R : C) (s : St K Reg C) : Prop :=
  ∀ r, r ≠ h → s.row r h ≠ 0 → ∃ c, s.loc r = some c ∧ c ≤ R

/-- Backward step of the TC invariant. -/
theorem held_back (h : Reg) (R : C) (s : St K Reg C) (e : Ev K Reg C)
    (hL : LegalEvA s e) (hN : NDEv h s e)
    (hr : ∀ i a c, e = .add i h a c → c ≤ R)
    (H : Held h R (step s e)) : Held h R s := by
  intro r hrh hrow
  cases e with
  | born i c =>
    by_cases hri : r = i
    · subst hri; exact absurd (hN hrh) hrow
    · have := H r hrh (by simpa [step, Function.update_of_ne hri] using hrow)
      simpa [step, Function.update_of_ne hri] using this
  | init i c =>
    by_cases hri : r = i
    · subst hri; exact absurd (hN hrh) hrow
    · have := H r hrh (by simpa [step, Function.update_of_ne hri] using hrow)
      simpa [step, Function.update_of_ne hri] using this
  | clear i c =>
    by_cases hri : r = i
    · subst hri; exact absurd (hN hrh) hrow
    · have := H r hrh (by simpa [step, Function.update_of_ne hri] using hrow)
      simpa [step, Function.update_of_ne hri] using this
  | copy i j c =>
    by_cases hri : r = i
    · subst hri; exact absurd (hN hrh) hrow
    · have := H r hrh (by simpa [step, Function.update_of_ne hri] using hrow)
      simpa [step, Function.update_of_ne hri] using this
  | move i c =>
    obtain ⟨c0, hc0, hle⟩ := hL
    by_cases hri : r = i
    · subst hri
      obtain ⟨c', hc', hcR⟩ := H r hrh (by simpa [step] using hrow)
      simp [step] at hc'
      subst hc'
      exact ⟨c0, hc0, le_trans hle hcR⟩
    · obtain ⟨c', hc', hcR⟩ := H r hrh (by simpa [step] using hrow)
      exact ⟨c', by simpa [step, Function.update_of_ne hri] using hc', hcR⟩
  | scale i u c =>
    obtain ⟨hu, hlc⟩ := hL
    by_cases hri : r = i
    · subst hri
      have h1 : (step s (Ev.scale r u c)).row r h ≠ 0 := by
        simp [step]; exact ⟨hu, hrow⟩
      obtain ⟨c', hc', hcR⟩ := H r hrh h1
      exact ⟨c', by simpa [step] using hc', hcR⟩
    · obtain ⟨c', hc', hcR⟩ := H r hrh (by simpa [step, Function.update_of_ne hri] using hrow)
      exact ⟨c', by simpa [step] using hc', hcR⟩
  | add i j a c =>
    obtain ⟨hij, hli, hlj⟩ := hL
    by_cases hri : r = i
    · subst hri
      by_cases hjh : j = h
      · subst hjh
        exact ⟨c, hli, hr r a c rfl⟩
      · by_cases h1 : (step s (Ev.add r j a c)).row r h = 0
        · have h2 : s.row r h + a * s.row j h = 0 := by simpa [step] using h1
          have hj0 : s.row j h ≠ 0 := by
            intro h0; rw [h0] at h2; simp at h2; exact hrow h2
          obtain ⟨c', hc', hcR⟩ := H j hjh (by simpa [step, Function.update_of_ne (Ne.symm hij)] using hj0)
          have hc'' : s.loc j = some c' := by simpa [step] using hc'
          rw [hlj] at hc''
          have hcc : c = c' := Option.some.inj hc''
          exact ⟨c, hli, hcc ▸ hcR⟩
        · obtain ⟨c', hc', hcR⟩ := H r hrh h1
          exact ⟨c', by simpa [step] using hc', hcR⟩
    · obtain ⟨c', hc', hcR⟩ := H r hrh (by simpa [step, Function.update_of_ne hri] using hrow)
      exact ⟨c', by simpa [step] using hc', hcR⟩


/-- **Lemma TC (run form).** If a run is ascending-legal, never destroys e_h content, reads `h`
only at charts inside `R`, and ends with every register `≠ h` free of e_h, then at the START every
register holding e_h sits inside `R` (hence at every prefix, see `TC_prefix`). -/
theorem held_run : ∀ (evs : List (Ev K Reg C)) (s : St K Reg C) (h : Reg) (R : C),
    LegalA s evs → ND h s evs → (∀ i a c, Ev.add i h a c ∈ evs → c ≤ R) →
    (∀ r, r ≠ h → (run s evs).row r h = 0) → Held h R s
  | [], s, h, R, _, _, _, hf => fun r hrh hr => absurd (hf r hrh) hr
  | e :: es, s, h, R, ⟨hL, hLs⟩, ⟨hN, hNs⟩, hr, hf =>
    held_back h R s e hL hN (fun i a c he => hr i a c (by simp [he]))
      (held_run es (step s e) h R hLs hNs
        (fun i a c hm => hr i a c (List.mem_cons_of_mem _ hm)) hf)

theorem run_append (s : St K Reg C) (l1 l2 : List (Ev K Reg C)) :
    run s (l1 ++ l2) = run (run s l1) l2 := by
  induction l1 generalizing s with
  | nil => rfl
  | cons e es ih => simp [run, ih]

theorem legalA_append (s : St K Reg C) (l1 l2 : List (Ev K Reg C)) :
    LegalA s (l1 ++ l2) ↔ LegalA s l1 ∧ LegalA (run s l1) l2 := by
  induction l1 generalizing s with
  | nil => simp [LegalA, run]
  | cons e es ih => simp [LegalA, run, ih, and_assoc]

theorem nd_append (h : Reg) (s : St K Reg C) (l1 l2 : List (Ev K Reg C)) :
    ND h s (l1 ++ l2) ↔ ND h s l1 ∧ ND h (run s l1) l2 := by
  induction l1 generalizing s with
  | nil => simp [ND, run]
  | cons e es ih => simp [ND, run, ih, and_assoc]

/-- **Lemma TC at every time.** At any prefix `pre`, every register `≠ h` holding e_h sits at a
chart `⊆ R`. -/
theorem TC_prefix (h : Reg) (R : C) (s0 : St K Reg C) (pre post : List (Ev K Reg C))
    (hL : LegalA s0 (pre ++ post)) (hN : ND h s0 (pre ++ post))
    (hr : ∀ i a c, Ev.add i h a c ∈ pre ++ post → c ≤ R)
    (hf : ∀ r, r ≠ h → (run s0 (pre ++ post)).row r h = 0) :
    Held h R (run s0 pre) := by
  rw [legalA_append] at hL
  rw [nd_append] at hN
  rw [run_append] at hf
  exact held_run post _ h R hL.2 hN.2
    (fun i a c hm => hr i a c (List.mem_append_right _ hm)) hf

/-- One step moves `h` upward. -/
theorem loc_step (h : Reg) (s : St K Reg C) (e : Ev K Reg C) (hL : LegalEvA s e)
    (c0 : C) (hc0 : s.loc h = some c0) : ∃ c1, (step s e).loc h = some c1 ∧ c0 ≤ c1 := by
  cases e with
  | born i c =>
    have hL' : s.loc i = none := hL
    by_cases hi : h = i
    · subst hi; rw [hL'] at hc0; cases hc0
    · exact ⟨c0, by simpa [step, Function.update_of_ne hi] using hc0, le_rfl⟩
  | init i c =>
    have hL' : s.loc i = none := hL
    by_cases hi : h = i
    · subst hi; rw [hL'] at hc0; cases hc0
    · exact ⟨c0, by simpa [step, Function.update_of_ne hi] using hc0, le_rfl⟩
  | move i c =>
    obtain ⟨c', hc', hle⟩ := hL
    by_cases hi : h = i
    · subst hi; rw [hc0] at hc'; cases hc'; exact ⟨c, by simp [step], hle⟩
    · exact ⟨c0, by simpa [step, Function.update_of_ne hi] using hc0, le_rfl⟩
  | add i j a c => exact ⟨c0, by simpa [step] using hc0, le_rfl⟩
  | scale i u c => exact ⟨c0, by simpa [step] using hc0, le_rfl⟩
  | clear i c => exact ⟨c0, by simpa [step] using hc0, le_rfl⟩
  | copy i j c => exact ⟨c0, by simpa [step] using hc0, le_rfl⟩

theorem loc_mono (h : Reg) : ∀ (evs : List (Ev K Reg C)) (s : St K Reg C), LegalA s evs →
    ∀ c0, s.loc h = some c0 → ∃ c1, (run s evs).loc h = some c1 ∧ c0 ≤ c1
  | [], s, _, c0, hc0 => ⟨c0, hc0, le_rfl⟩
  | e :: es, s, ⟨hL, hLs⟩, c0, hc0 => by
    obtain ⟨c1, hc1, h01⟩ := loc_step h s e hL c0 hc0
    obtain ⟨c2, hc2, h12⟩ := loc_mono h es (step s e) hLs c1 hc1
    exact ⟨c2, hc2, le_trans h01 h12⟩

/-- Reads of `h` at charts inside the chart of a LATER read: with ascending moves, `R_h`, the chart
of the last read, bounds every read of `h`. -/
theorem reads_le_last (h : Reg) (R : C) (i0 : Reg) (a0 : K) :
    ∀ (pre post : List (Ev K Reg C)) (s : St K Reg C),
    LegalA s (pre ++ Ev.add i0 h a0 R :: post) →
    ∀ i a c, Ev.add i h a c ∈ pre → c ≤ R
  | [], post, s, _, i, a, c, hm => by simp at hm
  | e :: es, post, s, hL, i, a, c, hm => by
    have hL' : LegalA (step s e) (es ++ Ev.add i0 h a0 R :: post) := hL.2
    rcases List.mem_cons.1 hm with he | hm'
    · subst he
      -- the read at chart c: h is at c here
      have hlc : s.loc h = some c := hL.1.2.2
      have hh : s.loc h = some c := hlc
      rw [legalA_append] at hL'
      obtain ⟨c1, hc1, hle⟩ := loc_mono h es (step s (Ev.add i h a c)) hL'.1 c
        (by simpa [step] using hh)
      have hlast := hL'.2.1.2.2
      rw [hc1] at hlast
      cases hlast
      exact hle
    · exact reads_le_last h R i0 a0 es post (step s e) hL' i a c hm'

/-- **TC with R_h = chart of the last read.** Hypothesis-level order, ascending public moves. -/
theorem TC_last_read (h : Reg) (R : C) (i0 : Reg) (a0 : K) (s0 : St K Reg C)
    (pre post : List (Ev K Reg C))
    (hpost : ∀ i a c, Ev.add i h a c ∉ post)
    (hL : LegalA s0 (pre ++ Ev.add i0 h a0 R :: post))
    (hN : ND h s0 (pre ++ Ev.add i0 h a0 R :: post))
    (hf : ∀ r, r ≠ h → (run s0 (pre ++ Ev.add i0 h a0 R :: post)).row r h = 0)
    (k : ℕ) :
    Held h R (run s0 ((pre ++ Ev.add i0 h a0 R :: post).take k)) := by
  have hr : ∀ i a c, Ev.add i h a c ∈ pre ++ Ev.add i0 h a0 R :: post → c ≤ R := by
    intro i a c hm
    rcases List.mem_append.1 hm with hm | hm
    · exact reads_le_last h R i0 a0 pre post s0 hL i a c hm
    · rcases List.mem_cons.1 hm with he | hm
      · cases he; exact le_rfl
      · exact absurd hm (hpost i a c)
  have := TC_prefix h R s0 ((pre ++ Ev.add i0 h a0 R :: post).take k)
    ((pre ++ Ev.add i0 h a0 R :: post).drop k) (by rwa [List.take_append_drop])
    (by rwa [List.take_append_drop]) (by rwa [List.take_append_drop])
    (by rwa [List.take_append_drop])
  exact this

/-- **Cancellation needs a read** (TC corollary). If an event drives the e_h coefficient of a
register `r ≠ h` from nonzero to zero, it is an ADD into `r` whose source is `h` or itself carries
e_h content. -/
theorem cancel_only_by_read (h : Reg) (s : St K Reg C) (e : Ev K Reg C)
    (hL : LegalEvA s e) (hN : NDEv h s e) (r : Reg) (hrh : r ≠ h)
    (h1 : s.row r h ≠ 0) (h2 : (step s e).row r h = 0) :
    ∃ j a c, e = Ev.add r j a c ∧ (j = h ∨ s.row j h ≠ 0) := by
  cases e with
  | born i c =>
    by_cases hri : r = i
    · subst hri; exact absurd (hN hrh) h1
    · exact absurd (by simpa [step, Function.update_of_ne hri] using h2) h1
  | init i c =>
    by_cases hri : r = i
    · subst hri; exact absurd (hN hrh) h1
    · exact absurd (by simpa [step, Function.update_of_ne hri] using h2) h1
  | clear i c =>
    by_cases hri : r = i
    · subst hri; exact absurd (hN hrh) h1
    · exact absurd (by simpa [step, Function.update_of_ne hri] using h2) h1
  | copy i j c =>
    by_cases hri : r = i
    · subst hri; exact absurd (hN hrh) h1
    · exact absurd (by simpa [step, Function.update_of_ne hri] using h2) h1
  | move i c => exact absurd (by simpa [step] using h2) h1
  | scale i u c =>
    by_cases hri : r = i
    · subst hri
      have hu := hL.1
      simp [step] at h2
      rcases h2 with h2 | h2
      · exact absurd h2 hu
      · exact absurd h2 h1
    · exact absurd (by simpa [step, Function.update_of_ne hri] using h2) h1
  | add i j a c =>
    by_cases hri : r = i
    · subst hri
      refine ⟨j, a, c, rfl, ?_⟩
      by_cases hjh : j = h
      · exact Or.inl hjh
      · right
        intro h0
        have : s.row r h + a * s.row j h = 0 := by simpa [step] using h2
        rw [h0] at this; simp at this; exact h1 this
    · exact absurd (by simpa [step, Function.update_of_ne hri] using h2) h1

end TCLemma

#print axioms TCLemma.TC_prefix
#print axioms TCLemma.TC_last_read
#print axioms TCLemma.cancel_only_by_read
