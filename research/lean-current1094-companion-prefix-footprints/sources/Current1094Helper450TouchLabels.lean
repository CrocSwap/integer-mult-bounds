import Current1094Helper450RelabelSlice

/-!
UNCOMPILED source-bound helper-side labels for all thirteen selected PR1094
L450 touches, in both orientations. L450 is borrowed helper226, not450.
The exact seven ADDs are retained with their operands, rational coefficients,
declared frames and raw/phase-erased indices. ADD preserves the label map,
but its payload effect is not deleted. The six relabels reuse the prior slice.

The derived helper guards do not assert that the companion registers carry
the required frames. Those remaining label equations and the source-to-typed
intervening-word join are explicit. There is no RecipesExact, physical chart,
executor, scalar unit-row, cost, precision or full-word theorem here.

Attribution: DreamingOfClouds' Apache-2.0 LemmaG event/label semantics;
Jeremy Kothe's HyperplaneEnd labels; Hanson Sun (@bbMisk), PR1611, supplied
the exact-source helper450 lead. The retained selected1094 emitter and
six-row slice provenance are preserved. New OpenAI-assisted source.
-/
set_option Elab.async false

namespace CurrentMain.Current1094Helper450TouchLabels

open CurrentMain.Current1094Helper450RelabelSlice

inductive HelperSide where
  | target
  | source
  deriving DecidableEq

/-- These are the actual helper-touching rows, not a whole-word decoder. -/
inductive Touch where
  | relabel (step : Step)
  | add (rawIndex eventIndex : Nat) (side : HelperSide) (other : Fin 704)
      (numerator : Int) (denominator : Nat) (frame : Frame)

def Touch.old : Touch → Cursor
  | .relabel s => s.old
  | .add _ _ _ _ _ _ f => .frame f

def Touch.next : Touch → Cursor
  | .relabel s => s.new
  | .add _ _ _ _ _ _ f => .frame f

def Touch.event : Touch → LemmaG.Event Register Label Rat
  | .relabel s => s.event Rat
  | .add _ _ .target r n d _ => .add helper (.inl r) ((n : Rat) / d)
  | .add _ _ .source r n d _ => .add (.inl r) helper ((n : Rat) / d)

def Touch.relabel? : Touch → Option Step
  | .relabel s => some s
  | .add .. => none

def guardedRun : List Touch → Cursor → Option Cursor
  | [], c => some c
  | t :: ts, c => if c = t.old then guardedRun ts t.next else none

/-- Checks the actual complete label map at each helper-touching event. -/
def HelperGuards : List Touch → (Register → Label) → Prop
  | [], _ => True
  | t :: ts, l => l helper = t.old.toLabel ∧ HelperGuards ts (t.event.lab l)

/-- The separate, unproved companion-register label obligation of each ADD. -/
def Touch.CompanionReady : Touch → (Register → Label) → Prop
  | .relabel _, _ => True
  | .add _ _ _ r _ _ f, l => l (.inl r) = (.frame f : Cursor).toLabel

theorem Touch.lab_helper (t : Touch) (l : Register → Label)
    (h : l helper = t.old.toLabel) :
    t.event.lab l helper = t.next.toLabel := by
  cases t with
  | relabel s => simp [Touch.event, Touch.next, Step.event, LemmaG.Event.lab]
  | add raw idx side r n d f =>
      cases side <;> simpa only [Touch.event, Touch.old, Touch.next, LemmaG.Event.lab] using h

/-- The independently supplied companion equation completes exactly the
original Event.Admissible condition; it is never inferred from helper data. -/
theorem Touch.admissible_of_companion (t : Touch) (l : Register → Label)
    (h : l helper = t.old.toLabel) (hother : t.CompanionReady l) :
    t.event.Admissible l := by
  cases t with
  | relabel s => exact h
  | add raw idx side r n d f =>
      cases side with
      | target => exact h.trans hother.symm
      | source => exact hother.trans h.symm

/-- Success derives each helper-side source-frame equation and the final
helper label while propagating the real, complete label map. -/
theorem guardedRun_sound (ts : List Touch) (c d : Cursor)
    (l : Register → Label) (hl : l helper = c.toLabel)
    (h : guardedRun ts c = some d) :
    HelperGuards ts l ∧
      LemmaG.Stream.labRun (ts.map Touch.event) l helper = d.toLabel := by
  induction ts generalizing c l with
  | nil =>
      have hcd : c = d := Option.some.inj h
      subst d
      exact ⟨True.intro, hl⟩
  | cons t ts ih =>
      by_cases hc : c = t.old
      · have ht : guardedRun ts t.next = some d := by
          simpa [guardedRun, hc] using h
        have hr : l helper = t.old.toLabel := by simpa [hc] using hl
        obtain ⟨hw, hd⟩ := ih t.next (t.event.lab l) (t.lab_helper l hr) ht
        exact ⟨⟨hr, hw⟩, by simpa only [List.map_cons, LemmaG.Stream.labRun] using hd⟩
      · simp [guardedRun, hc] at h

def forward : List Touch := [
  .relabel ⟨7852, 7850, .pre, .frame 2, .inverseRight 2 999⟩,
  .add 12769 12764 .source 157 1 2 2,
  .add 12771 12766 .source 219 1 2 2,
  .relabel ⟨13948, 13943, .frame 2, .frame 31, .directedChild 2 31 2 .B⟩,
  .add 13949 13944 .target 230 1 1 31,
  .relabel ⟨14143, 14138, .frame 31, .frame 556, .directedChild 31 556 3 .B⟩,
  .add 14144 14139 .source 508 1 1 556,
  .relabel ⟨15146, 15141, .frame 556, .frame 751, .directedChild 556 751 1 .B⟩,
  .add 15147 15142 .source 219 (-1) 2 751,
  .relabel ⟨16494, 16488, .frame 751, .frame 999, .directedChild 751 999 1 .cleanupTail⟩,
  .add 16495 16489 .source 508 (-1) 1 999,
  .add 16507 16501 .target 230 (-1) 1 999,
  .relabel ⟨24562, 24553, .frame 999, .done, .inverseLeft 2 999⟩]

def backward : List Touch := [
  .relabel ⟨7852, 7850, .pre, .frame 2, .inverseRight 2 999⟩,
  .add 12769 12764 .target 157 (-1) 2 2,
  .add 12771 12766 .target 219 (-1) 2 2,
  .relabel ⟨13948, 13943, .frame 2, .frame 31, .directedChild 2 31 2 .B⟩,
  .add 13949 13944 .source 230 (-1) 1 31,
  .relabel ⟨14143, 14138, .frame 31, .frame 556, .directedChild 31 556 3 .B⟩,
  .add 14144 14139 .target 508 (-1) 1 556,
  .relabel ⟨15146, 15141, .frame 556, .frame 751, .directedChild 556 751 1 .B⟩,
  .add 15147 15142 .target 219 1 2 751,
  .relabel ⟨16494, 16488, .frame 751, .frame 999, .directedChild 751 999 1 .cleanupTail⟩,
  .add 16495 16489 .target 508 1 1 999,
  .add 16507 16501 .source 230 1 1 999,
  .relabel ⟨24562, 24553, .frame 999, .done, .inverseLeft 2 999⟩]

theorem relabel_slices :
    forward.filterMap Touch.relabel? = selectedSteps ∧
      backward.filterMap Touch.relabel? = selectedSteps := by
  exact ⟨rfl, rfl⟩

theorem forward_run : guardedRun forward .pre = some .done := by rfl

theorem backward_run : guardedRun backward .pre = some .done := by rfl

theorem forward_helper_guards (l : Register → Label)
    (hl : l helper = .prew helper) :
    HelperGuards forward l ∧
      LemmaG.Stream.labRun (forward.map Touch.event) l helper = .done helper :=
  guardedRun_sound forward .pre .done l hl forward_run

theorem backward_helper_guards (l : Register → Label)
    (hl : l helper = .prew helper) :
    HelperGuards backward l ∧
      LemmaG.Stream.labRun (backward.map Touch.event) l helper = .done helper :=
  guardedRun_sound backward .pre .done l hl backward_run

end CurrentMain.Current1094Helper450TouchLabels

#print axioms CurrentMain.Current1094Helper450TouchLabels.Touch.lab_helper
#print axioms CurrentMain.Current1094Helper450TouchLabels.Touch.admissible_of_companion
#print axioms CurrentMain.Current1094Helper450TouchLabels.guardedRun_sound
#print axioms CurrentMain.Current1094Helper450TouchLabels.relabel_slices
#print axioms CurrentMain.Current1094Helper450TouchLabels.forward_run
#print axioms CurrentMain.Current1094Helper450TouchLabels.backward_run
#print axioms CurrentMain.Current1094Helper450TouchLabels.forward_helper_guards
#print axioms CurrentMain.Current1094Helper450TouchLabels.backward_helper_guards
