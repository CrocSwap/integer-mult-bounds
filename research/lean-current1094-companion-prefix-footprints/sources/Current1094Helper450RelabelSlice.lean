import FreshScalarSupportStream
import HyperplaneEnd.Labels

/-!
Source-only guarded relabel slice for selected current1094 ordinary L450
(borrowed helper226), over 704 ordinary plus 8 private registers and 1004 frames.
The six actual rows and their phase-erased indices occur in both orientations.
This file does not parse arbitrary JSON, execute a full word, establish its
WellLabelled/RecipesExact predicates, or interpret a physical chart/executor.

The parsed-input boundary must reject bools, nonintegral numbers, malformed
arrays, unknown tags and duplicate keys before constructing ParsedRow. The
decoder below independently rejects the wrong register, invalid pair key,
out-of-range frames, and zero/out-of-range climb rank. It preserves recipe
references rather than defining a recipe to be the desired transition.

Reuses DreamingOfClouds' Apache-2.0 LemmaG event semantics and Jeremy Kothe's
Apache-2.0 HyperplaneEnd extended labels. PR1611 by Hanson Sun (@bbMisk), with
OpenAI Codex assistance, supplies the source lead, not a kernel result here.
New preparation with OpenAI assistance. UNCOMPILED.
-/
set_option Elab.async false

namespace CurrentMain.Current1094Helper450RelabelSlice

abbrev Register := Fin 704 ⊕ Fin 8
abbrev Frame := Fin 1004

inductive BaseLabel where
  | canonical (f : Frame)
  | dataPre (i : Fin 112)
  | dataPost (i : Fin 112)
  deriving DecidableEq

abbrev Label := HyperplaneEnd.XLab Register BaseLabel

def helper : Register := .inl 450

/-- Only the labels reached by the selected helper; not the full label type. -/
inductive Cursor where
  | pre
  | frame (f : Frame)
  | done
  deriving DecidableEq

def Cursor.toLabel : Cursor → Label
  | .pre => .prew helper
  | .frame f => .frame (.canonical f)
  | .done => .done helper

inductive Part where
  | B
  | cleanupTail
  deriving DecidableEq

/-- References to independently interpreted serialized records. -/
inductive RecipeRef where
  | inverseRight (entrance terminal : Frame)
  | directedChild (old new : Frame) (rank : Nat) (part : Part)
  | inverseLeft (entrance terminal : Frame)
  deriving DecidableEq

structure Step where
  rawIndex : Nat
  eventIndex : Nat
  old : Cursor
  new : Cursor
  recipe : RecipeRef

/-- Already parsed JSON values; raw syntax validation is a separate boundary. -/
inductive ParsedRelabel where
  | pre (register entrance terminal : Nat)
  | climb (part : Part) (register old new rank : Nat)
  | post (register entrance terminal : Nat)

structure ParsedRow where
  rawIndex : Nat
  eventIndex : Nat
  body : ParsedRelabel

/-- A small strict decoder for this one helper's relabel vocabulary. -/
def decode (row : ParsedRow) : Option Step :=
  match row.body with
  | .pre r e u =>
      if r = 450 ∧ e = 2 ∧ u = 999 then
        some ⟨row.rawIndex, row.eventIndex, .pre, .frame 2, .inverseRight 2 999⟩
      else none
  | .post r e u =>
      if r = 450 ∧ e = 2 ∧ u = 999 then
        some ⟨row.rawIndex, row.eventIndex, .frame 999, .done, .inverseLeft 2 999⟩
      else none
  | .climb part r a b k =>
      if r = 450 then
        if ha : a < 1004 then
          if hb : b < 1004 then
            if 0 < k ∧ k < 10 then
              some ⟨row.rawIndex, row.eventIndex, .frame ⟨a, ha⟩,
                .frame ⟨b, hb⟩, .directedChild ⟨a, ha⟩ ⟨b, hb⟩ k part⟩
            else none
          else none
        else none
      else none

def Step.event (K : Type*) (s : Step) : LemmaG.Event Register Label K :=
  .relabel helper s.old.toLabel s.new.toLabel

/-- Every step checks the actual cursor against its emitted source label. -/
def guardedRun : List Step → Cursor → Option Cursor
  | [], c => some c
  | s :: ss, c => if c = s.old then guardedRun ss s.new else none

theorem guardedRun_reject (s : Step) (ss : List Step) (c : Cursor)
    (h : c ≠ s.old) : guardedRun (s :: ss) c = none := by
  simp [guardedRun, h]

/-- Success derives all relabel guards and the terminal label for this slice.
The initial label is related to an actual arbitrary register-label map l. -/
theorem guardedRun_sound (K : Type*) (ss : List Step) (c d : Cursor)
    (l : Register → Label) (hl : l helper = c.toLabel)
    (h : guardedRun ss c = some d) :
    LemmaG.Stream.WellLabelled (ss.map (Step.event K)) l ∧
      LemmaG.Stream.labRun (ss.map (Step.event K)) l helper = d.toLabel := by
  induction ss generalizing c l with
  | nil =>
      have hcd : c = d := Option.some.inj h
      subst d
      exact ⟨True.intro, hl⟩
  | cons s ss ih =>
      by_cases hc : c = s.old
      · have ht : guardedRun ss s.new = some d := by
          simpa [guardedRun, hc] using h
        have hr : l helper = s.old.toLabel := by simpa [hc] using hl
        have hn : (Step.event K s).lab l helper = s.new.toLabel := by
          simp [Step.event, LemmaG.Event.lab]
        obtain ⟨hw, hd⟩ := ih s.new ((Step.event K s).lab l) hn ht
        constructor
        · change (l helper = s.old.toLabel) ∧
            LemmaG.Stream.WellLabelled (ss.map (Step.event K)) ((Step.event K s).lab l)
          exact ⟨hr, hw⟩
        · simpa only [List.map_cons, LemmaG.Stream.labRun] using hd
      · simp [guardedRun, hc] at h

def selectedParsed : List ParsedRow := [
  ⟨7852, 7850, .pre 450 2 999⟩,
  ⟨13948, 13943, .climb .B 450 2 31 2⟩,
  ⟨14143, 14138, .climb .B 450 31 556 3⟩,
  ⟨15146, 15141, .climb .B 450 556 751 1⟩,
  ⟨16494, 16488, .climb .cleanupTail 450 751 999 1⟩,
  ⟨24562, 24553, .post 450 2 999⟩]

def selectedSteps : List Step := [
  ⟨7852, 7850, .pre, .frame 2, .inverseRight 2 999⟩,
  ⟨13948, 13943, .frame 2, .frame 31, .directedChild 2 31 2 .B⟩,
  ⟨14143, 14138, .frame 31, .frame 556, .directedChild 31 556 3 .B⟩,
  ⟨15146, 15141, .frame 556, .frame 751, .directedChild 556 751 1 .B⟩,
  ⟨16494, 16488, .frame 751, .frame 999, .directedChild 751 999 1 .cleanupTail⟩,
  ⟨24562, 24553, .frame 999, .done, .inverseLeft 2 999⟩]

theorem selected_decode : selectedParsed.map decode = selectedSteps.map some := by
  rfl

theorem selected_run : guardedRun selectedSteps .pre = some .done := by
  rfl

/-- Wrong starting chart is rejected even though its numeric frame is2. -/
theorem selected_wrong_start : guardedRun selectedSteps (.frame 2) = none := by
  rfl

/-- Only six metadata indices are compared; no register payload is evaluated. -/
theorem selected_chronology :
    (selectedSteps.map Step.rawIndex).Pairwise (· < ·) ∧
      (selectedSteps.map Step.eventIndex).Pairwise (· < ·) := by
  decide

theorem selected_slice_guards (K : Type*) (l : Register → Label)
    (hl : l helper = .prew helper) :
    LemmaG.Stream.WellLabelled (selectedSteps.map (Step.event K)) l ∧
      LemmaG.Stream.labRun (selectedSteps.map (Step.event K)) l helper = .done helper :=
  guardedRun_sound K selectedSteps .pre .done l hl selected_run

/-- Exact serialized monomial data; no interpretation or validity is inferred. -/
structure MonomialData where
  quadraticRows : List Nat
  linearZ4 : List Nat
  matrixRows : List Nat
  offset : Nat
  phase : Nat

def selectedLeft : MonomialData :=
  ⟨[0,6,6,0,0,0,0,0,0], [2,3,3,2,2,2,2,0,0],
    [1,128,262,2,4,8,16,32,64], 0, 0⟩

def selectedRight : MonomialData :=
  ⟨[0,12,2,26,24,0,0,0,0], [2,2,0,3,3,2,2,2,2],
    [1,28,4,32,64,128,256,14,16], 511, 1⟩

end CurrentMain.Current1094Helper450RelabelSlice

#print axioms CurrentMain.Current1094Helper450RelabelSlice.guardedRun_reject
#print axioms CurrentMain.Current1094Helper450RelabelSlice.guardedRun_sound
#print axioms CurrentMain.Current1094Helper450RelabelSlice.selected_decode
#print axioms CurrentMain.Current1094Helper450RelabelSlice.selected_run
#print axioms CurrentMain.Current1094Helper450RelabelSlice.selected_wrong_start
#print axioms CurrentMain.Current1094Helper450RelabelSlice.selected_chronology
#print axioms CurrentMain.Current1094Helper450RelabelSlice.selected_slice_guards
#check @CurrentMain.Current1094Helper450RelabelSlice.decode
