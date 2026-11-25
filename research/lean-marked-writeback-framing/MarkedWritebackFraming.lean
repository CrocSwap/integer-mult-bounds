import MarkedTrackWriteback

/-!
Destination-segment framing of the accepted equal-width writeback machine.
The source remains the supplied standalone marked tape. Derived confinement
prevents the destination head from reaching either ambient context, including
when those contexts contain markers. This is an actual step/run refinement;
no bulk data movement or assumed framed endpoint is introduced.
James Chang with OpenAI assistance, Apache-2.0. Reuses MarkedTrackWriteback
unchanged and follows the accepted marked-XOR confinement method.
Author-checked pinned context kappa=836330098538459/500000000000000000.
Uncompiled candidate. Positioning, equal-width preparation and allocation are
caller obligations; all supplied ambient destination cells are charged.
-/
set_option Elab.async false
set_option autoImplicit false
namespace CurrentMain.MarkedWritebackFraming
open PairedBitXorScan (Tape Pair)
open MarkedBitXorScan (Symbol marked dataSymbol)
open MarkedTrackWriteback

def embed (left right : List Symbol) (s : State) : State :=
  { s with destination := ⟨s.destination.left ++ left, s.destination.right ++ right⟩ }

def BoundaryPhase (p : Phase) : Prop :=
  p ≠ .clear ∧ p ≠ .advanceSource ∧ p ≠ .advanceDestination

inductive Confined : State → Prop where
  | home (source : Tape Symbol) (rows : List Pair) (b : Bool) (phase : Phase)
      (safe : BoundaryPhase phase) : Confined ⟨source,⟨[],marked rows⟩,b,phase⟩
  | body (source : Tape Symbol) (ls : List Pair) (a b : Bool) (rs : List Pair)
      (scratch : Bool) (phase : Phase) :
      Confined ⟨source,⟨ls.map dataSymbol ++ [.leftMarker],
        .data a b :: (rs.map dataSymbol ++ [.rightMarker])⟩,scratch,phase⟩
  | rightEnd (source : Tape Symbol) (ls : List Pair) (b : Bool) (phase : Phase)
      (safe : BoundaryPhase phase) :
      Confined ⟨source,⟨ls.map dataSymbol ++ [.leftMarker],[.rightMarker]⟩,b,phase⟩

private theorem inside (source : Tape Symbol) (ls rs : List Pair) (b : Bool) (phase : Phase)
    (safe : BoundaryPhase phase) :
    Confined ⟨source,⟨ls.map dataSymbol ++ [.leftMarker],rs.map dataSymbol ++ [.rightMarker]⟩,b,phase⟩ := by
  cases rs with
  | nil => exact Confined.rightEnd source ls b phase safe
  | cons row rs => rcases row with ⟨a,c⟩; exact Confined.body source ls a c rs b phase

/-- Closure accounts for all phases that can lead to a right move: clear,
advanceSource and advanceDestination cannot occur at either local boundary. -/
theorem confined_step {s : State} (h : Confined s) : Confined (step s) := by
  cases h with
  | home source rows b phase safe =>
      cases phase with
      | enterSource =>
          cases hh : source.readHead .blank <;> simp [step, hh]
          all_goals exact Confined.home _ _ _ _ (by simp [BoundaryPhase])
      | enterDestination =>
          simpa [step, marked, Tape.readHead, Tape.moveRight] using
            inside source [] rows b .load (by simp [BoundaryPhase])
      | load =>
          cases hh : source.readHead .blank <;> simp [step, hh]
          all_goals exact Confined.home _ _ _ _ (by simp [BoundaryPhase])
      | write => simpa [step, marked, Tape.readHead] using Confined.home source rows b .halt (by simp [BoundaryPhase])
      | clear => exact False.elim (safe.1 rfl)
      | advanceSource => exact False.elim (safe.2.1 rfl)
      | advanceDestination => exact False.elim (safe.2.2 rfl)
      | checkEnd => simpa [step, marked, Tape.readHead] using Confined.home source rows b .halt (by simp [BoundaryPhase])
      | rewindSource =>
          by_cases hh : source.readHead .blank = .leftMarker <;> simp [step, hh]
          all_goals exact Confined.home _ _ _ _ (by simp [BoundaryPhase])
      | rewindDestination => simpa [step, marked, Tape.readHead] using Confined.home source rows b .clearScratch (by simp [BoundaryPhase])
      | clearScratch => exact Confined.home source rows false .halt (by simp [BoundaryPhase])
      | halt => exact Confined.home source rows b .halt (by simp [BoundaryPhase])
  | body source ls a b rs scratch phase =>
      cases phase with
      | enterSource =>
          cases hh : source.readHead .blank <;> simp [step, hh]
          all_goals exact Confined.body _ _ _ _ _ _ _
      | enterDestination => simpa [step, Tape.readHead] using Confined.body source ls a b rs scratch .halt
      | load =>
          cases hh : source.readHead .blank <;> simp [step, hh]
          all_goals exact Confined.body _ _ _ _ _ _ _
      | write => simpa [step, Tape.readHead, Tape.writeHead] using Confined.body source ls scratch b rs scratch .clear
      | clear =>
          cases hh : source.readHead .blank <;> simp [step, hh]
          all_goals exact Confined.body _ _ _ _ _ _ _
      | advanceSource => exact Confined.body _ _ _ _ _ _ _
      | advanceDestination =>
          simpa [step, Tape.moveRight, dataSymbol] using
            inside source ((a,b)::ls) rs scratch .load (by simp [BoundaryPhase])
      | checkEnd => simpa [step, Tape.readHead] using Confined.body source ls a b rs scratch .halt
      | rewindSource =>
          by_cases hh : source.readHead .blank = .leftMarker <;> simp [step, hh]
          all_goals exact Confined.body _ _ _ _ _ _ _
      | rewindDestination =>
          cases ls with
          | nil => simpa [step, Tape.readHead, Tape.moveLeft, marked, dataSymbol] using
              Confined.home source ((a,b)::rs) scratch .rewindDestination (by simp [BoundaryPhase])
          | cons row ls => rcases row with ⟨x,y⟩; simpa [step, Tape.readHead, Tape.moveLeft, dataSymbol] using
              Confined.body source ls x y ((a,b)::rs) scratch .rewindDestination
      | clearScratch => exact Confined.body _ _ _ _ _ _ _
      | halt => exact Confined.body _ _ _ _ _ _ _
  | rightEnd source ls b phase safe =>
      cases phase with
      | enterSource =>
          cases hh : source.readHead .blank <;> simp [step, hh]
          all_goals exact Confined.rightEnd _ _ _ _ (by simp [BoundaryPhase])
      | enterDestination => simpa [step, Tape.readHead] using Confined.rightEnd source ls b .halt (by simp [BoundaryPhase])
      | load =>
          cases hh : source.readHead .blank <;> simp [step, hh]
          all_goals exact Confined.rightEnd _ _ _ _ (by simp [BoundaryPhase])
      | write => simpa [step, Tape.readHead] using Confined.rightEnd source ls b .halt (by simp [BoundaryPhase])
      | clear => exact False.elim (safe.1 rfl)
      | advanceSource => exact False.elim (safe.2.1 rfl)
      | advanceDestination => exact False.elim (safe.2.2 rfl)
      | checkEnd => exact Confined.rightEnd source ls b .rewindSource (by simp [BoundaryPhase])
      | rewindSource =>
          by_cases hh : source.readHead .blank = .leftMarker <;> simp [step, hh]
          all_goals exact Confined.rightEnd _ _ _ _ (by simp [BoundaryPhase])
      | rewindDestination =>
          cases ls with
          | nil => simpa [step, Tape.readHead, Tape.moveLeft, marked] using
              Confined.home source [] b .rewindDestination (by simp [BoundaryPhase])
          | cons row ls => rcases row with ⟨x,y⟩; simpa [step, Tape.readHead, Tape.moveLeft, dataSymbol] using
              Confined.body source ls x y [] b .rewindDestination
      | clearScratch => exact Confined.rightEnd source ls false .halt (by simp [BoundaryPhase])
      | halt => exact Confined.rightEnd source ls b .halt (by simp [BoundaryPhase])

theorem step_embed (left right : List Symbol) {s : State} (h : Confined s) :
    step (embed left right s) = embed left right (step s) := by
  cases h with
  | home source rows b phase safe =>
      by_cases hsource : source.readHead .blank = .leftMarker <;> cases phase <;> simp_all [BoundaryPhase, embed, step, marked, Tape.readHead,
        Tape.writeHead, Tape.moveRight, Tape.moveLeft] <;> (repeat first | split) <;> simp_all [List.append_assoc]
  | body source ls a b rs scratch phase =>
      by_cases hsource : source.readHead .blank = .leftMarker <;> cases phase <;> cases ls <;> simp_all [embed, step, Tape.readHead,
        Tape.writeHead, Tape.moveRight, Tape.moveLeft, dataSymbol, List.append_assoc] <;> (repeat first | split) <;> simp_all [List.append_assoc]
  | rightEnd source ls b phase safe =>
      by_cases hsource : source.readHead .blank = .leftMarker <;> cases phase <;> cases ls <;> simp_all [BoundaryPhase, embed, step, Tape.readHead,
        Tape.writeHead, Tape.moveRight, Tape.moveLeft, dataSymbol, List.append_assoc] <;> (repeat first | split) <;> simp_all [List.append_assoc]


theorem run_embed (left right : List Symbol) (s : State) (h : Confined s) (k : Nat) :
    run k (embed left right s) = embed left right (run k s) := by
  induction k generalizing s with
  | zero => rfl
  | succ k ih =>
      simp only [run]
      rw [step_embed left right h]
      exact ih (step s) (confined_step h)

theorem cells_embed (left right : List Symbol) (s : State) :
    cells (embed left right s) = left.length + cells s + right.length := by
  simp [embed, cells, tapeCells]
  omega

private theorem initial_confined (src dst : List Pair) (b : Bool) : Confined (initial src dst b) :=
  Confined.home _ _ _ _ (by simp [BoundaryPhase])

/-- Both supplied ambient contexts survive the actual equal-width writeback.
The source and local destination heads return; arbitrary input scratch clears. -/
theorem framed_result (left right : List Symbol) (src dst : List Pair)
    (h : src.length = dst.length) (b : Bool) :
    run (7*src.length+9) (embed left right (initial src dst b)) =
      embed left right (final src dst) ∧
    ∀ k, k < 7*src.length+9 →
      (run k (embed left right (initial src dst b))).phase ≠ .halt := by
  constructor
  · rw [run_embed left right _ (initial_confined src dst b), (writeback_result src dst h b).1]
  · intro k hk
    rw [run_embed left right _ (initial_confined src dst b)]
    exact (writeback_result src dst h b).2.2 k hk

theorem framed_storage (left right : List Symbol) (src dst : List Pair)
    (h : src.length = dst.length) (b : Bool) (k : Nat) :
    cells (run k (embed left right (initial src dst b))) ≤
      left.length + (2*src.length+4) + right.length := by
  rw [run_embed left right _ (initial_confined src dst b), cells_embed]
  have hbound := writeback_storage src dst h b k
  omega

end CurrentMain.MarkedWritebackFraming
#print axioms CurrentMain.MarkedWritebackFraming.confined_step
#print axioms CurrentMain.MarkedWritebackFraming.step_embed
#print axioms CurrentMain.MarkedWritebackFraming.run_embed
#print axioms CurrentMain.MarkedWritebackFraming.cells_embed
#print axioms CurrentMain.MarkedWritebackFraming.framed_result
#print axioms CurrentMain.MarkedWritebackFraming.framed_storage
