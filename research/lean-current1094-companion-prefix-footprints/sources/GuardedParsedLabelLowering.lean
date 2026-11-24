import SelectedSourceSyntax
import Current1094Helper450RelabelSlice

/-!
UNCOMPILED. Strict already-parsed row lowering for the selected 704+8 register
and1004 frame vocabulary. JSON byte parsing, duplicate keys and integer-token versus decimal-number
recognition precede Value; no parser correctness is assumed here.

COPY takes its entire stored label from the current source register. Every
emitted relabel and ADD is checked against Event.Admissible before the map is
advanced. The terminal cursor and WellLabelled conclusion are derived by list
induction. Serialized recipe references remain explicit data obligations; no
RecipesExact, payload, physical deletion, executor or cost theorem is supplied.

Selected emitter: icekylinx/PR425 and PR433, DreamingOfClouds' modifications,
Jeremy Kothe's hyperplane-ended convention, and Hanson Sun's PR1611 source lead.
LemmaG and HyperplaneEnd retain their Apache-2.0 attribution. New source prepared
with OpenAI assistance. Phase names are recognized individually; their complete
selected ordering and raw-to-typed cut map remain separate literal obligations.
-/
set_option Elab.async false

namespace CurrentMain.GuardedParsedLabelLowering

open CurrentMain.Current1094Helper450RelabelSlice
open CurrentMain.SelectedSourceSyntax (Value natValue bounded register)

deriving instance DecidableEq for HyperplaneEnd.XLab

structure Context where
  start : Fin 704 → Frame
  terminal : Fin 704 → Frame

inductive Reference where
  | identity
  | source (i : Fin 112) (f : Frame)
  | inverseTarget (i : Fin 112) (f : Frame)
  | inverseRight (r : Fin 704) (e u : Frame) (fullKey : Bool)
  | inverseLeft (r : Fin 704) (e u : Frame) (fullKey : Bool)
  | child (part : String) (r : Fin 704) (a b : Frame) (rank : Nat)
  | center (r : Fin 8) (a b : Frame) (rank : Nat)

/-- The annotation is retained even where it does not affect Event.lab.
Checking its association to a noncanonical tag is a separate source obligation. -/
inductive Action where
  | relabel (r : Register) (old new : Label) (recipe : Reference)
  | add (t s : Register) (q : Rat) (annotation : Frame)
  | scale (t : Register) (q : Rat) (annotation : Frame)
  | copy (t s : Register) (annotation : Frame)
  | clear (t : Register) (annotation : Frame)

inductive Instruction where
  | phase (name : String)
  | action (a : Action)

private def rational : Value → Value → Option Rat
  | .integer a, .integer b => if b = 0 then none else some ((a : Rat) / (b : Rat))
  | _, _ => none

private def positiveRank (v : Value) : Option Nat := do
  let k ← natValue v
  if 0 < k ∧ k < 10 then some k else none

private def phaseName (s : String) : Bool :=
  decide (s ∈ ["zero_frame_precondition", "entry_adapters", "A", "centers", "B",
    "cleanup_tail", "final", "exit_adapters", "full_frame_cleanup", "done"])

private def climbPart (s : String) : Bool :=
  decide (s ∈ ["A", "B", "cleanup_tail", "final"])

private def canonical (f : Frame) : Label := .frame (.canonical f)

private def residual (ctx : Context) (side : String) (rv ev uv : Value)
    (fullKey : Bool) : Option Instruction := do
  let r ← bounded 704 rv
  let e ← bounded 1004 ev
  let u ← bounded 1004 uv
  if 224 ≤ r.val ∧ (ctx.start r ≠ 0 ∨ ctx.terminal r ≠ 1) ∧
      e = ctx.start r ∧ u = ctx.terminal r ∧
      (if fullKey then u = 1 else u ≠ 1) then
    if side = "pre" then
      some (.action (.relabel (.inl r) (.prew (.inl r)) (canonical e)
        (.inverseRight r e u fullKey)))
    else if side = "post" then
      some (.action (.relabel (.inl r) (canonical u) (.done (.inl r))
        (.inverseLeft r e u fullKey)))
    else none
  else none

/-- Exact arities and disjoint parsed-value constructors reject malformed rows.
Recipe catalog membership, matrix validity and phase-sequence correctness are
not replaced by this syntax/reference decoding. -/
def decode (ctx : Context) : Value → Option Instruction
  | .array [.text "phase", .text s] =>
      if phaseName s then some (.phase s) else none
  | .array [.text "scalar", .array [.text "add", t, s, a, b], f] => do
      let t ← register t
      let s ← register s
      let q ← rational a b
      let f ← bounded 1004 f
      return .action (.add t s q f)
  | .array [.text "scalar", .array [.text "scale", t, a, b], f] => do
      let t ← register t
      let q ← rational a b
      let f ← bounded 1004 f
      return .action (.scale t q f)
  | .array [.text "scalar", .array [.text "copy", t, s], f] => do
      let t ← register t
      let s ← register s
      let f ← bounded 1004 f
      return .action (.copy t s f)
  | .array [.text "scalar", .array [.text "clear", t], f] => do
      let t ← register t
      let f ← bounded 1004 f
      return .action (.clear t f)
  | .array [.text "climb", .text part, rv, av, bv, kv] => do
      let r ← bounded 704 rv
      let a ← bounded 1004 av
      let b ← bounded 1004 bv
      let k ← positiveRank kv
      if climbPart part then
        some (.action (.relabel (.inl r) (canonical a) (canonical b)
          (.child part r a b k)))
      else none
  | .array [.text "center", rv, av, bv, kv] => do
      let r ← bounded 8 rv
      let a ← bounded 1004 av
      let b ← bounded 1004 bv
      let k ← positiveRank kv
      return .action (.relabel (.inr r) (canonical a) (canonical b)
        (.center r a b k))
  | .array [.text "adapter", .text way, rv, fv] => do
      let r ← bounded 704 rv
      let f ← bounded 1004 fv
      if way = "old_to_new" then
        if h : r.val < 112 then
          if f = ctx.start r then
            some (.action (.relabel (.inl r) (.frame (.dataPre ⟨r.val,h⟩))
              (canonical f) (.source ⟨r.val,h⟩ f)))
          else none
        else if f = 0 then
          some (.action (.relabel (.inl r) (canonical 0) (canonical 0) .identity))
        else none
      else if way = "new_to_old" then
        if h : 112 ≤ r.val ∧ r.val < 224 then
          if hi : r.val - 112 < 112 then
            let i : Fin 112 := ⟨r.val - 112, hi⟩
            if f = ctx.terminal r then
              some (.action (.relabel (.inl r) (canonical f)
                (.frame (.dataPost i)) (.inverseTarget i f)))
            else none
          else none
        else if f = 1 then
          some (.action (.relabel (.inl r) (canonical 1) (canonical 1) .identity))
        else none
      else none
  | .array [.text "residual_adapter", .text side, r, e] =>
      residual ctx side r e (.integer 1) true
  | .array [.text "residual_adapter", .text side, r, e, u] =>
      residual ctx side r e u false
  | _ => none

/-- Only COPY reads a label in this operation. Its complete tag is stored in F,
including prew/done/dataPre/dataPost; the annotation is never substituted for it. -/
def Action.event (a : Action) (l : Register → Label) : LemmaG.Event Register Label Rat :=
  match a with
  | .relabel r A B _ => .relabel r A B
  | .add t s q _ => .add t s q
  | .scale t q _ => .scale t q
  | .copy t s _ => .copy t s (l s)
  | .clear t f => .clear t (canonical f)

private instance admissibleDecidable (e : LemmaG.Event Register Label Rat)
    (l : Register → Label) : Decidable (e.Admissible l) := by
  cases e <;> unfold LemmaG.Event.Admissible <;> infer_instance

/-- The decoded instructions are retained outside this evaluator so their
recipe references and numeric metadata are not lost by Event projection. -/
def lower : List Instruction → (Register → Label) →
    Option (List (LemmaG.Event Register Label Rat) × (Register → Label))
  | [], l => some ([], l)
  | .phase _ :: rest, l => lower rest l
  | .action a :: rest, l =>
      let e := a.event l
      if e.Admissible l then
        match lower rest (e.lab l) with
        | none => none
        | some (es, finish) => some (e :: es, finish)
      else none

/-- A successful run derives the cursor and every full-label guard. -/
theorem lower_sound (rows : List Instruction) (l finish : Register → Label)
    (es : List (LemmaG.Event Register Label Rat))
    (h : lower rows l = some (es, finish)) :
    LemmaG.Stream.WellLabelled es l ∧ LemmaG.Stream.labRun es l = finish := by
  induction rows generalizing l es finish with
  | nil =>
      have hp : ([], l) = (es, finish) := Option.some.inj h
      cases hp
      exact ⟨True.intro, rfl⟩
  | cons row rows ih =>
      cases row with
      | phase name => exact ih l finish es h
      | action a =>
          by_cases ha : (a.event l).Admissible l
          · cases ht : lower rows ((a.event l).lab l) with
            | none => simp [lower, ha, ht] at h
            | some result =>
                rcases result with ⟨tail, last⟩
                have hp : (a.event l :: tail, last) = (es, finish) :=
                  Option.some.inj (by simpa [lower, ha, ht] using h)
                obtain ⟨hw, hc⟩ := ih ((a.event l).lab l) last tail ht
                cases hp
                exact ⟨⟨ha, hw⟩, hc⟩
          · simp [lower, ha] at h

/-- Parsed input is decoded entirely before label execution; the retained
instruction list is exactly that successful decoding, not an assumed list. -/
def lowerParsed (ctx : Context) (rows : List Value) (l : Register → Label) :
    Option (List Instruction × List (LemmaG.Event Register Label Rat) × (Register → Label)) := do
  let instructions ← rows.mapM (decode ctx)
  let (es, finish) ← lower instructions l
  return (instructions, es, finish)

theorem lowerParsed_sound (ctx : Context) (rows : List Value)
    (l finish : Register → Label) (instructions : List Instruction)
    (es : List (LemmaG.Event Register Label Rat))
    (h : lowerParsed ctx rows l = some (instructions, es, finish)) :
    rows.mapM (decode ctx) = some instructions ∧
      LemmaG.Stream.WellLabelled es l ∧ LemmaG.Stream.labRun es l = finish := by
  cases hd : rows.mapM (decode ctx) with
  | none => simp [lowerParsed, hd] at h
  | some decoded =>
      cases hl : lower decoded l with
      | none => simp [lowerParsed, hd, hl] at h
      | some result =>
          rcases result with ⟨out, last⟩
          have hp : (decoded, out, last) = (instructions, es, finish) :=
            Option.some.inj (by simpa [lowerParsed, hd, hl] using h)
          have hs := lower_sound decoded l last out hl
          cases hp
          exact ⟨rfl, hs⟩

theorem copy_stores_full_tag (t s : Register) (f : Frame) (l : Register → Label) :
    (Action.copy t s f).event l = LemmaG.Event.copy t s (l s) := rfl

end CurrentMain.GuardedParsedLabelLowering

#print axioms CurrentMain.GuardedParsedLabelLowering.lower_sound
#print axioms CurrentMain.GuardedParsedLabelLowering.lowerParsed_sound
#print axioms CurrentMain.GuardedParsedLabelLowering.copy_stores_full_tag
