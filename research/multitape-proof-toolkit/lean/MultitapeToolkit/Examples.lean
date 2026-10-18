import MultitapeToolkit.FrameRule

/-!
# A literal three-tape copy program using the verified toolkit

The examples quantify over arbitrary integer head positions and arbitrary entire
tape contents. There is no clean-scratch or bounded-data assumption. One actual
transition copies the scanned source symbol, then genuinely halts; all other
cells, including an entirely dirty parked tape, retain their initial contents.

Read and write frames serve different purposes: the source tape is unchanged,
but its scanned symbol determines the copied output. Being unchanged therefore
does not justify removing a tape from a read-agreement premise.
-/

namespace MultitapeToolkit.Examples

open Absolute Absolute.Trace Absolute.FrameRule Locality

abbrev TapeIndex := Fin 3
abbrev Symbol := Fin 4

/-- A literal fixed table: false copies one symbol and enters true; true halts. -/
def copyProgram : Program TapeIndex Symbol Bool where
  transition control scanned :=
    if control then none else
      some (true, fun i => ((if i = (1 : TapeIndex) then scanned 0 else scanned i), Move.stay))

/-- Entire input tapes and head locations are supplied unchanged. -/
def copyStart (heads : TapeIndex → ℤ) (cells : TapeIndex → ℤ → Symbol) :
    Absolute.Config TapeIndex Symbol Bool := ⟨false, heads, cells⟩

/-- The actual destination has one copied cell and otherwise retains all data. -/
def copyFinish (heads : TapeIndex → ℤ) (cells : TapeIndex → ℤ → Symbol) :
    Absolute.Config TapeIndex Symbol Bool where
  state := true
  head := heads
  cell i x := if i = (1 : TapeIndex) ∧ x = heads 1 then cells 0 (heads 0) else cells i x

/-- This concrete table executes the specified copy with precisely one transition. -/
theorem copy_step (heads : TapeIndex → ℤ) (cells : TapeIndex → ℤ → Symbol) :
    Absolute.step copyProgram (copyStart heads cells) = some (copyFinish heads cells) := by
  simp only [Absolute.step, copyProgram, copyStart, Bool.false_eq_true, ite_false,
    Option.map_some]
  congr 1
  apply Absolute.Config.ext
  · rfl
  · funext i; simp [moveOffset, copyFinish]
  · funext i x
    by_cases hi : i = (1 : TapeIndex)
    · subst i
      by_cases hx : x = heads 1
      · simp [copyFinish, hx]
      · simp [copyFinish, hx]
    · by_cases hx : x = heads i
      · simp [copyFinish, hi, hx]
      · simp [copyFinish, hi, hx]

/-- The terminal configuration genuinely has no successor. -/
theorem copy_halts (heads : TapeIndex → ℤ) (cells : TapeIndex → ℤ → Symbol) :
    Absolute.Halts copyProgram (copyFinish heads cells) := by
  simp [Absolute.Halts, Absolute.step, copyProgram, copyFinish]

/-- The certified literal copy is an exact one-step run. -/
theorem copy_run (heads : TapeIndex → ℤ) (cells : TapeIndex → ℤ → Symbol) :
    Absolute.Runs copyProgram 1 (copyStart heads cells) (copyFinish heads cells) :=
  .cons (copy_step heads cells) (.refl _)

/-- The real footprint is one initial scanned position on every tape. -/
theorem copy_footprint (heads : TapeIndex → ℤ) (cells : TapeIndex → ℤ → Symbol) :
    FootprintedRuns copyProgram 1 (copyStart heads cells) (copyFinish heads cells)
      (fun i => {heads i}) :=
  .cons (copy_step heads cells) (.refl _)

/-- Every tape except the destination is certified idle by the actual finite table. -/
theorem copy_tape_idle (tape : TapeIndex) (hnot : tape ≠ 1) : IdleOn copyProgram tape := by
  intro state scanned next actions ht
  cases state with
  | false =>
    have hp : (next, actions) =
        (true, fun i => ((if i = (1 : TapeIndex) then scanned 0 else scanned i), Move.stay)) := by
      exact Option.some.inj (by simpa [copyProgram] using ht.symm)
    have ha : actions = (fun i => ((if i = (1 : TapeIndex) then scanned 0 else scanned i), Move.stay)) :=
      congrArg Prod.snd hp
    constructor
    · rw [ha]
    · rw [ha]
      simp [hnot]
  | true => simp [copyProgram] at ht

/-- The parked tape needs no clean-data invariant. -/
theorem copy_tape2_idle : IdleOn copyProgram (2 : TapeIndex) :=
  copy_tape_idle 2 (by decide)

/-- The read source is unchanged even though its scanned value determines the output. -/
theorem copy_preserves_source {n : ℕ}
    {c d : Absolute.Config TapeIndex Symbol Bool} (h : Absolute.Runs copyProgram n c d) :
    d.head 0 = c.head 0 ∧ ∀ x, d.cell 0 x = c.cell 0 x :=
  runs_idle_tape copyProgram 0 (copy_tape_idle 0 (by decide)) h

/-- Every actual run of this table preserves the entire parked tape and its head. -/
theorem copy_preserves_dirty_tape2 {n : ℕ}
    {c d : Absolute.Config TapeIndex Symbol Bool} (h : Absolute.Runs copyProgram n c d) :
    d.head 2 = c.head 2 ∧ ∀ x, d.cell 2 x = c.cell 2 x :=
  runs_idle_tape copyProgram 2 copy_tape2_idle h

/-- Universal correctness includes the charged transition, real halt, output,
unchanged heads, arbitrary dirty parked data, and every unscanned cell. -/
theorem literal_copy_correct (heads : TapeIndex → ℤ)
    (cells : TapeIndex → ℤ → Symbol) :
    ∃ final : Absolute.Config TapeIndex Symbol Bool,
      Absolute.Runs copyProgram 1 (copyStart heads cells) final ∧
      Absolute.Halts copyProgram final ∧ final.head = heads ∧
      final.cell 1 (heads 1) = cells 0 (heads 0) ∧
      (∀ x, final.cell 0 x = cells 0 x) ∧
      (∀ x, final.cell 2 x = cells 2 x) ∧
      ∀ i x, x ≠ heads i → final.cell i x = cells i x := by
  refine ⟨copyFinish heads cells, copy_run heads cells, copy_halts heads cells, rfl, ?_, ?_, ?_, ?_⟩
  · simp [copyFinish]
  · exact (copy_preserves_source (copy_run heads cells)).2
  · exact (copy_preserves_dirty_tape2 (copy_run heads cells)).2
  · exact (step_frame copyProgram (copy_step heads cells)).2

/-- The general completed-frame theorem applies to this actual finite copy table.
Other configurations may contain unrelated dirty data at every unscanned cell. -/
theorem completed_copy_frame (heads : TapeIndex → ℤ)
    (cells otherCells : TapeIndex → ℤ → Symbol)
    (hagrees : ∀ i, cells i (heads i) = otherCells i (heads i)) :
    ∃ otherFinal : Absolute.Config TapeIndex Symbol Bool,
      FootprintedRuns copyProgram 1 (copyStart heads otherCells) otherFinal
        (fun i => {heads i}) ∧
      Absolute.Halts copyProgram otherFinal ∧
      MatchesOn (fun i => ({heads i} : Set ℤ)) (copyFinish heads cells) otherFinal ∧
      ∀ i x, x ≠ heads i → otherFinal.cell i x = otherCells i x := by
  have hm : MatchesOn (fun i => ({heads i} : Set ℤ))
      (copyStart heads cells) (copyStart heads otherCells) := by
    refine ⟨rfl, rfl, ?_⟩
    intro i x hx
    have hx' : x = heads i := by simpa using hx
    subst x
    exact hagrees i
  rcases (copy_footprint heads cells).completed_lockstep
    (fun i => ({heads i} : Set ℤ)) (by intro i x hx; simpa using hx)
    (by intro i; simp [copyFinish]) (copy_halts heads cells)
    (copyStart heads otherCells) hm with ⟨otherFinal, hr, hh, hmFinal⟩
  refine ⟨otherFinal, hr, hh, hmFinal, ?_⟩
  intro i x hne
  exact hr.frame i x (by simpa using hne)

end MultitapeToolkit.Examples





