import Current1094Helper450TouchLabels

/-!
UNCOMPILED. Exact selected PR1094 companion-label projection for L450's seven
ADDs. The 23 literal label-changing rows for L157, L219, L230 and L508 through
raw16507 agree in both orientations. The serialized row scan records no other
label write to these four registers in those prefixes. It preserves full prew
and canonical tags, including L508's residual pre wrapper.

The theorems concern this finite projected Event list and arbitrary incoming
label maps. They do not identify it with a lowered whole JSON word. Exact
source-to-Event lowering and omitted-event label preservation are the remaining
transport obligations. No ADD payload is treated as zero or erased physically;
ADDs are omitted only from a label calculation because Event.lab preserves them.
RecipesExact, operator/Hosting/executor and cost/precision remain separate.

Attribution: DreamingOfClouds' Apache-2.0 LemmaG label semantics, Jeremy Kothe's
HyperplaneEnd labels and Hanson Sun (@bbMisk)'s PR1611 source-bound helper450
lead. Exact selected emitter and prior source provenance are retained.
Prepared with OpenAI assistance. No new compiler or supplier execution.
-/
set_option Elab.async false

namespace CurrentMain.Current1094Helper450CompanionLabels

open CurrentMain.Current1094Helper450RelabelSlice
open CurrentMain.Current1094Helper450TouchLabels

structure Move where
  rawIndex : Nat
  eventIndex : Nat
  register : Fin 704
  oldLabel : Label
  newLabel : Label

def Move.event (m : Move) : LemmaG.Event Register Label Rat :=
  .relabel (.inl m.register) m.oldLabel m.newLabel

/-- Every label-writing source row for the four companions before the last query. -/
def moves : List Move := [
  ⟨7559, 7557, 157, .frame (.canonical 0), .frame (.canonical 0)⟩,
  ⟨7621, 7619, 219, .frame (.canonical 0), .frame (.canonical 0)⟩,
  ⟨7632, 7630, 230, .frame (.canonical 0), .frame (.canonical 0)⟩,
  ⟨7910, 7908, 508, .prew (.inl 508), .frame (.canonical 2)⟩,
  ⟨9406, 9403, 230, .frame (.canonical 0), .frame (.canonical 12)⟩,
  ⟨9474, 9471, 230, .frame (.canonical 12), .frame (.canonical 25)⟩,
  ⟨9496, 9493, 230, .frame (.canonical 25), .frame (.canonical 31)⟩,
  ⟨12768, 12763, 157, .frame (.canonical 0), .frame (.canonical 2)⟩,
  ⟨12770, 12765, 219, .frame (.canonical 0), .frame (.canonical 2)⟩,
  ⟨13428, 13423, 157, .frame (.canonical 2), .frame (.canonical 173)⟩,
  ⟨13430, 13425, 219, .frame (.canonical 2), .frame (.canonical 172)⟩,
  ⟨14097, 14092, 230, .frame (.canonical 31), .frame (.canonical 550)⟩,
  ⟨14140, 14135, 508, .frame (.canonical 2), .frame (.canonical 552)⟩,
  ⟨14142, 14137, 508, .frame (.canonical 552), .frame (.canonical 556)⟩,
  ⟨14444, 14439, 219, .frame (.canonical 172), .frame (.canonical 600)⟩,
  ⟨15142, 15137, 157, .frame (.canonical 173), .frame (.canonical 750)⟩,
  ⟨15143, 15138, 508, .frame (.canonical 556), .frame (.canonical 750)⟩,
  ⟨15145, 15140, 219, .frame (.canonical 600), .frame (.canonical 751)⟩,
  ⟨15170, 15165, 230, .frame (.canonical 550), .frame (.canonical 755)⟩,
  ⟨15831, 15826, 219, .frame (.canonical 751), .frame (.canonical 859)⟩,
  ⟨15867, 15862, 157, .frame (.canonical 750), .frame (.canonical 867)⟩,
  ⟨16493, 16487, 508, .frame (.canonical 750), .frame (.canonical 999)⟩,
  ⟨16506, 16500, 230, .frame (.canonical 755), .frame (.canonical 999)⟩]

def movePrefix (n : Nat) : List (LemmaG.Event Register Label Rat) :=
  (moves.take n).map Move.event

/-- Existing append/untouched laws isolate the last write. The absent full-word
lowering must supply such an actual suffix and its no-move proof before reuse. -/
theorem label_after_last_relabel (before after : List (LemmaG.Event Register Label Rat))
    (l : Register → Label) (r : Register) (old new : Label)
    (hafter : ∀ e ∈ after, ¬ e.moves r) :
    LemmaG.Stream.labRun (before ++ .relabel r old new :: after) l r = new := by
  rw [LemmaG.Stream.labRun_append]
  change LemmaG.Stream.labRun after
    ((LemmaG.Event.relabel r old new : LemmaG.Event Register Label Rat).lab
      (LemmaG.Stream.labRun before l)) r = new
  rw [LemmaG.Stream.labRun_untouched after _ r hafter]
  simp [LemmaG.Event.lab]

/-- Last actual writes determine the seven labels, independent of incoming
payloads and of all unmentioned incoming label coordinates. -/
theorem companion_labels (l : Register → Label) :
    LemmaG.Stream.labRun (movePrefix 8) l (.inl 157) =
      (.frame (.canonical 2) : Label) ∧
    LemmaG.Stream.labRun (movePrefix 9) l (.inl 219) =
      (.frame (.canonical 2) : Label) ∧
    LemmaG.Stream.labRun (movePrefix 11) l (.inl 230) =
      (.frame (.canonical 31) : Label) ∧
    LemmaG.Stream.labRun (movePrefix 14) l (.inl 508) =
      (.frame (.canonical 556) : Label) ∧
    LemmaG.Stream.labRun (movePrefix 18) l (.inl 219) =
      (.frame (.canonical 751) : Label) ∧
    LemmaG.Stream.labRun (movePrefix 22) l (.inl 508) =
      (.frame (.canonical 999) : Label) ∧
    LemmaG.Stream.labRun (movePrefix 23) l (.inl 230) =
      (.frame (.canonical 999) : Label) := by
  simp [movePrefix, moves, Move.event, LemmaG.Stream.labRun, LemmaG.Event.lab,
    Function.update]

structure Observation where
  rawIndex : Nat
  eventIndex : Nat
  prefixLength : Nat
  companion : Fin 704
  side : HelperSide
  numerator : Int
  denominator : Nat
  frame : Frame

def Observation.forwardTouch (q : Observation) : Touch :=
  .add q.rawIndex q.eventIndex q.side q.companion q.numerator q.denominator q.frame

def oppositeSide : HelperSide → HelperSide
  | .target => .source
  | .source => .target

def Observation.backwardTouch (q : Observation) : Touch :=
  .add q.rawIndex q.eventIndex (oppositeSide q.side) q.companion
    (-q.numerator) q.denominator q.frame

def observations : List Observation := [
  ⟨12769, 12764, 8, 157, .source, 1, 2, 2⟩,
  ⟨12771, 12766, 9, 219, .source, 1, 2, 2⟩,
  ⟨13949, 13944, 11, 230, .target, 1, 1, 31⟩,
  ⟨14144, 14139, 14, 508, .source, 1, 1, 556⟩,
  ⟨15147, 15142, 18, 219, .source, (-1), 2, 751⟩,
  ⟨16495, 16489, 22, 508, .source, (-1), 1, 999⟩,
  ⟨16507, 16501, 23, 230, .target, (-1), 1, 999⟩]

def isAdd : Touch → Bool
  | .add .. => true
  | .relabel _ => false

/-- Exact connection to the already checked full thirteen-touch forward data. -/
theorem forward_touches_exact :
    observations.map Observation.forwardTouch = forward.filter isAdd := by rfl

/-- Backward ADD sides and signed coefficients are preserved, not replayed forward. -/
theorem backward_touches_exact :
    observations.map Observation.backwardTouch = backward.filter isAdd := by rfl

/-- All seven previously supplied CompanionReady equations are now derived for
these source-bound projected prefixes, in both orientations. Whole-word prefix
transport is deliberately not inferred from this finite projection theorem. -/
theorem selected_companions (l : Register → Label) (q : Observation)
    (hq : q ∈ observations) :
    q.forwardTouch.CompanionReady (LemmaG.Stream.labRun (movePrefix q.prefixLength) l) ∧
    q.backwardTouch.CompanionReady (LemmaG.Stream.labRun (movePrefix q.prefixLength) l) := by
  obtain ⟨h1, h2, h3, h4, h5, h6, h7⟩ := companion_labels l
  simp only [observations, List.mem_cons, List.mem_nil_iff, or_false] at hq
  rcases hq with rfl | rfl | rfl | rfl | rfl | rfl | rfl
  · exact ⟨h1, h1⟩
  · exact ⟨h2, h2⟩
  · exact ⟨h3, h3⟩
  · exact ⟨h4, h4⟩
  · exact ⟨h5, h5⟩
  · exact ⟨h6, h6⟩
  · exact ⟨h7, h7⟩

end CurrentMain.Current1094Helper450CompanionLabels

#print axioms CurrentMain.Current1094Helper450CompanionLabels.label_after_last_relabel
#print axioms CurrentMain.Current1094Helper450CompanionLabels.companion_labels
#print axioms CurrentMain.Current1094Helper450CompanionLabels.forward_touches_exact
#print axioms CurrentMain.Current1094Helper450CompanionLabels.backward_touches_exact
#print axioms CurrentMain.Current1094Helper450CompanionLabels.selected_companions
