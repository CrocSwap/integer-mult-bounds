import MarkedBitXorScan

/-!
Actual marked-XOR execution in arbitrary finite ambient contexts. The left
context is supplied in the zipper's stored reverse order. A derived confined
state invariant prevents the prepared run from crossing either marker. Each
actual transition therefore commutes with adding the two spectator contexts;
this is proved before lifting to every run prefix and the accepted first halt.
All represented ambient cells are counted, including both local markers.

The context lists may contain arbitrary symbols, including other markers.
This does not allocate or construct the supplied segment, choose its width,
or implement a Nat-address metadata-slot codec. No strict local decoder is
silently applied to the whole ambient tape. Compound arithmetic workspace,
physical encoding/installation and selected runtime remain separate.
James Chang with OpenAI assistance; Apache-2.0. Reuses machine's accepted
MarkedBitXorScan and PairedBitXorScan unchanged. Pinned conditional context:
kappa=836330098538459/500000000000000000. Uncompiled candidate.
-/
set_option Elab.async false
set_option autoImplicit false
namespace CurrentMain.MarkedXorFraming
open PairedBitXorScan (Tape Pair xorPair)
open MarkedBitXorScan

/-- Arbitrary contexts are appended beyond each end of the local zipper. -/
def embed (left right : List Symbol) (s : State) : State :=
  ⟨⟨s.tape.left ++ left, s.tape.right ++ right⟩, s.scratch, s.phase⟩

/-- The actual run has its head at L, a data pair, or R. The move-right phase
is possible only at a data pair. This is established from the supplied input. -/
inductive Confined : State → Prop where
  | home (rows : List Pair) (b : Bool) (phase : Phase) (h : phase ≠ .advance) :
      Confined ⟨⟨[], marked rows⟩, b, phase⟩
  | body (ls : List Pair) (a b : Bool) (rs : List Pair) (scratch : Bool) (phase : Phase) :
      Confined ⟨⟨ls.map dataSymbol ++ [.leftMarker],
        .data a b :: (rs.map dataSymbol ++ [.rightMarker])⟩, scratch, phase⟩
  | rightEnd (ls : List Pair) (b : Bool) (phase : Phase) (h : phase ≠ .advance) :
      Confined ⟨⟨ls.map dataSymbol ++ [.leftMarker], [.rightMarker]⟩, b, phase⟩

private theorem confined_inside (ls rs : List Pair) (b : Bool) (phase : Phase)
    (h : phase ≠ .advance) :
    Confined ⟨⟨ls.map dataSymbol ++ [.leftMarker], rs.map dataSymbol ++ [.rightMarker]⟩,
      b, phase⟩ := by
  cases rs with
  | nil => exact Confined.rightEnd ls b phase h
  | cons row rs =>
      rcases row with ⟨a, c⟩
      exact Confined.body ls a c rs b phase

/-- Closure is proved by the real finite-alphabet transition, not an assumed
endpoint or a storage-count surrogate for boundary safety. -/
theorem confined_step {s : State} (h : Confined s) : Confined (step s) := by
  cases h with
  | home rows b phase h =>
      cases phase with
      | enter =>
          simpa [step, marked, Tape.readHead, Tape.moveRight] using
            confined_inside [] rows b .load (by intro h; cases h)
      | load => simpa [step, marked, Tape.readHead] using Confined.home rows b .halt (by intro h; cases h)
      | write => simpa [step, marked, Tape.readHead] using Confined.home rows b .halt (by intro h; cases h)
      | clear => simpa [step, marked, Tape.readHead] using Confined.home rows b .halt (by intro h; cases h)
      | advance => exact False.elim (h rfl)
      | rewind => simpa [step, marked, Tape.readHead] using Confined.home rows b .halt (by intro h; cases h)
      | halt => exact Confined.home rows b .halt (by intro h; cases h)
  | body ls a b rs scratch phase =>
      cases phase with
      | enter => simpa [step, Tape.readHead] using Confined.body ls a b rs scratch .halt
      | load => simpa [step, Tape.readHead] using Confined.body ls a b rs (scratch ^^ b) .write
      | write => simpa [step, Tape.readHead, Tape.writeHead] using Confined.body ls (a ^^ scratch) b rs scratch .clear
      | clear => simpa [step, Tape.readHead] using Confined.body ls a b rs (scratch ^^ b) .advance
      | advance =>
          simpa [step, Tape.moveRight, dataSymbol] using
            confined_inside ((a,b) :: ls) rs scratch .load (by intro h; cases h)
      | rewind =>
          cases ls with
          | nil =>
              simpa [step, Tape.readHead, Tape.moveLeft, marked, dataSymbol] using
                Confined.home ((a,b) :: rs) scratch .rewind (by intro h; cases h)
          | cons row ls =>
              rcases row with ⟨x,y⟩
              simpa [step, Tape.readHead, Tape.moveLeft, dataSymbol] using
                Confined.body ls x y ((a,b) :: rs) scratch .rewind
      | halt => exact Confined.body ls a b rs scratch .halt
  | rightEnd ls b phase h =>
      cases phase with
      | enter => simpa [step, Tape.readHead] using Confined.rightEnd ls b .halt (by intro h; cases h)
      | load => simpa [step, Tape.readHead] using Confined.rightEnd ls b .rewind (by intro h; cases h)
      | write => simpa [step, Tape.readHead] using Confined.rightEnd ls b .halt (by intro h; cases h)
      | clear => simpa [step, Tape.readHead] using Confined.rightEnd ls b .halt (by intro h; cases h)
      | advance => exact False.elim (h rfl)
      | rewind =>
          cases ls with
          | nil =>
              simpa [step, Tape.readHead, Tape.moveLeft, marked] using
                Confined.home [] b .rewind (by intro h; cases h)
          | cons row ls =>
              rcases row with ⟨x,y⟩
              simpa [step, Tape.readHead, Tape.moveLeft, dataSymbol] using
                Confined.body ls x y [] b .rewind
      | halt => exact Confined.rightEnd ls b .halt (by intro h; cases h)

/-- One-step refinement on the derived confined domain, even when spectators
contain markers. No context symbol can become the observed local head. -/
theorem step_embed (left right : List Symbol) {s : State} (h : Confined s) :
    step (embed left right s) = embed left right (step s) := by
  cases h with
  | home rows b phase h =>
      cases phase <;> simp_all [embed, step, marked, Tape.readHead, Tape.writeHead, Tape.moveRight, Tape.moveLeft]
  | body ls a b rs scratch phase =>
      cases phase <;> cases ls <;>
        simp [embed, step, Tape.readHead, Tape.writeHead, Tape.moveRight, Tape.moveLeft, dataSymbol, List.append_assoc]
  | rightEnd ls b phase h =>
      cases phase <;> cases ls <;>
        simp_all [embed, step, Tape.readHead, Tape.writeHead, Tape.moveRight, Tape.moveLeft, dataSymbol, List.append_assoc]

/-- Every actual prefix, including times after halt, preserves the same two
spectator lists and the local head/scratch/control through this embedding. -/
theorem run_embed (left right : List Symbol) (k : Nat) (s : State) (h : Confined s) :
    run k (embed left right s) = embed left right (run k s) := by
  induction k generalizing s with
  | zero => rfl
  | succ k ih =>
      simp only [run]
      rw [step_embed left right h]
      exact ih (step s) (confined_step h)

theorem cells_embed (left right : List Symbol) (s : State) :
    cells (embed left right s) = left.length + cells s + right.length := by
  simp only [cells, embed, List.length_append]
  omega

private theorem runs_embed (left right : List Symbol) {n : Nat} {s t : State}
    (h : RunsToHalt n s t) : Confined s → RunsToHalt n (embed left right s) (embed left right t) := by
  induction h with
  | done s hh => intro _; exact RunsToHalt.done _ hh
  | @next n s t hh hsize tail ih =>
      intro hs
      apply RunsToHalt.next (s := embed left right s) hh
      · rw [step_embed left right hs, cells_embed, cells_embed, hsize]
      · rw [step_embed left right hs]
        exact ih (confined_step hs)

private theorem initial_confined (rows : List Pair) : Confined (initial rows) :=
  Confined.home rows false .enter (by intro h; cases h)

/-- The inherited exact first halt is preserved, including the returned L-head,
false scratch, target XOR, unchanged source track and both ambient contexts. -/
theorem framed_scan_exact (left right : List Symbol) (rows : List Pair) :
    RunsToHalt (5 * rows.length + 4) (embed left right (initial rows))
      (embed left right (final (rows.map xorPair))) :=
  runs_embed left right (marked_scan_exact rows) (initial_confined rows)

theorem framed_scan_result (left right : List Symbol) (rows : List Pair) :
    run (5 * rows.length + 4) (embed left right (initial rows)) =
      embed left right (final (rows.map xorPair)) := by
  rw [run_embed left right _ _ (initial_confined rows), marked_scan_result]

/-- The entire represented tape is charged. Zero or arbitrary ambient context
is supplied input, not free storage. Both local markers are counted. -/
theorem framed_scan_storage (left right : List Symbol) (rows : List Pair) (k : Nat) :
    cells (run k (embed left right (initial rows))) =
      left.length + (rows.length + 2) + right.length := by
  rw [run_embed left right k _ (initial_confined rows), cells_embed, marked_scan_storage]

end CurrentMain.MarkedXorFraming
#print axioms CurrentMain.MarkedXorFraming.confined_step
#print axioms CurrentMain.MarkedXorFraming.step_embed
#print axioms CurrentMain.MarkedXorFraming.run_embed
#print axioms CurrentMain.MarkedXorFraming.cells_embed
#print axioms CurrentMain.MarkedXorFraming.framed_scan_exact
#print axioms CurrentMain.MarkedXorFraming.framed_scan_result
#print axioms CurrentMain.MarkedXorFraming.framed_scan_storage
#check @CurrentMain.MarkedXorFraming.run_embed
