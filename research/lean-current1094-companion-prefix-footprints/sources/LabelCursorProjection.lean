import FreshScalarSupportStream

/-!
UNCOMPILED generic label-cursor projection, reusing the exact LemmaG Event.lab
semantics. Filtering a typed word to label writes on selected registers
preserves those label coordinates, for arbitrary incoming maps. This derives
the projection law and assumes neither operator equality nor WellLabelled.

COPY's label is its explicit stored F; its physical effect still reads another
register. Thus this result concerns labels only and does not justify dropping
COPY, ADD, SCALE or another event from physical/scalar execution.

Attribution: DreamingOfClouds' Apache-2.0 LemmaG stream/event semantics, preserved
in FreshScalarSupportStream. New proof prepared with OpenAI assistance.
This source does not parse JSON or assume a whole-word lowering exists.
-/
set_option Elab.async false

namespace CurrentMain.LabelCursorProjection

variable {ι Λ K : Type*} [DecidableEq ι]

/-- The exact target of an event's label write; arithmetic events write no label. -/
def writesIn (keep : ι → Bool) : LemmaG.Event ι Λ K → Bool
  | .relabel r _ _ => keep r
  | .copy r _ _ => keep r
  | .clear r _ => keep r
  | .add .. => false
  | .scale .. => false

/-- Each label coordinate depends only on its previous value and the stored
new label in a write to that same register. It never reads another label. -/
theorem event_lab_congr_at (e : LemmaG.Event ι Λ K) (r : ι)
    (l l' : ι → Λ) (h : l r = l' r) : e.lab l r = e.lab l' r := by
  cases e <;> simp [LemmaG.Event.lab, Function.update, h]

theorem labRun_congr_at (es : List (LemmaG.Event ι Λ K)) (r : ι)
    (l l' : ι → Λ) (h : l r = l' r) :
    LemmaG.Stream.labRun es l r = LemmaG.Stream.labRun es l' r := by
  induction es generalizing l l' with
  | nil => exact h
  | cons e es ih =>
      exact ih (e.lab l) (e.lab l') (event_lab_congr_at e r l l' h)

/-- A discarded event fixes every retained label coordinate, including COPY
and CLEAR whose destinations fail the selected-register test. -/
theorem discarded_fixes (keep : ι → Bool) (e : LemmaG.Event ι Λ K)
    (r : ι) (hr : keep r = true) (he : writesIn keep e = false)
    (l : ι → Λ) : e.lab l r = l r := by
  cases e with
  | relabel a A B =>
      by_cases h : r = a
      · subst r
        simp [writesIn, hr] at he
      · simp [LemmaG.Event.lab, Function.update, h]
  | copy a b F =>
      by_cases h : r = a
      · subst r
        simp [writesIn, hr] at he
      · simp [LemmaG.Event.lab, Function.update, h]
  | clear a F =>
      by_cases h : r = a
      · subst r
        simp [writesIn, hr] at he
      · simp [LemmaG.Event.lab, Function.update, h]
  | add t s q => rfl
  | scale t q => rfl

/-- A genuine cursor-transport law for every typed word and incoming map.
It is not a claim about the physical action of the filtered word. -/
theorem projection_preserves_label (keep : ι → Bool)
    (es : List (LemmaG.Event ι Λ K)) (r : ι) (hr : keep r = true)
    (l : ι → Λ) :
    LemmaG.Stream.labRun (es.filter (writesIn keep)) l r =
      LemmaG.Stream.labRun es l r := by
  induction es generalizing l with
  | nil => rfl
  | cons e es ih =>
      cases he : writesIn keep e with
      | true =>
          simpa [List.filter_cons, he, LemmaG.Stream.labRun] using ih (e.lab l)
      | false =>
          have hcoord : l r = e.lab l r := (discarded_fixes keep e r hr he l).symm
          calc
            LemmaG.Stream.labRun ((e :: es).filter (writesIn keep)) l r =
                LemmaG.Stream.labRun (es.filter (writesIn keep)) l r := by
                  simp [List.filter_cons, he]
            _ = LemmaG.Stream.labRun es l r := ih l
            _ = LemmaG.Stream.labRun es (e.lab l) r := labRun_congr_at es r l (e.lab l) hcoord
            _ = LemmaG.Stream.labRun (e :: es) l r := rfl

end CurrentMain.LabelCursorProjection

#print axioms CurrentMain.LabelCursorProjection.event_lab_congr_at
#print axioms CurrentMain.LabelCursorProjection.labRun_congr_at
#print axioms CurrentMain.LabelCursorProjection.discarded_fixes
#print axioms CurrentMain.LabelCursorProjection.projection_preserves_label
