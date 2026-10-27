import FramedReplay

/-!
Executable frame-label and retained-center checker for the literal forward
record word. Frame zero represents the unallocated temporary's arbitrary
gauge; the separate `center` field records whether the temporary is live.
No projector equation, owner map, or address isometry follows from labels.
-/
namespace FrameTrace
open TreeReplay (Tree)

structure Entry where
  scalar : LinearReplay.Event
  oldFrame : Nat
  newFrame : Nat
  rank : Nat
  deriving DecidableEq

structure State where
  frames : Tree Nat
  center : Option Nat
  deriving DecidableEq

def next (s : State) (e : Entry) : State :=
  match e.scalar.op with
  | 0 => {s with frames := s.frames.put e.scalar.x e.newFrame}
  | 1 => s
  | 2 => ⟨s.frames.put e.scalar.y e.newFrame, some e.scalar.x⟩
  | _ => ⟨s.frames.put e.scalar.y 0, none⟩

def check (s : State) (e : Entry) : Bool :=
  match e.scalar.op with
  | 0 => e.scalar.x < 987 && s.frames.get e.scalar.x == e.oldFrame &&
      s.center != some e.scalar.x
  | 1 => e.scalar.x < 987 && e.scalar.y <= 987 && e.scalar.x != e.scalar.y &&
      s.frames.get e.scalar.x == e.oldFrame && s.frames.get e.scalar.y == e.oldFrame &&
      s.center != some e.scalar.x && (e.scalar.y != 987 || s.center.isSome)
  | 2 => e.scalar.x < 987 && e.scalar.y == 987 &&
      s.frames.get e.scalar.x == e.oldFrame && s.center.isNone && e.rank == 8
  | 3 => e.scalar.x < 987 && e.scalar.y == 987 &&
      s.frames.get e.scalar.x == e.oldFrame && s.frames.get e.scalar.y == e.newFrame &&
      s.center == some e.scalar.x && e.rank == 0
  | _ => false

def checkedStep (s : State × Bool) (e : Entry) : State × Bool :=
  (next s.1 e, s.2 && check s.1 e)

def runChecked (es : List Entry) (s : State × Bool) : State × Bool :=
  es.foldl checkedStep s

def Valid : List Entry → State → Prop
  | [], _ => True
  | e :: es, s => check s e = true ∧ Valid es (next s e)

theorem flag_mono (es : List Entry) (s : State × Bool)
    (h : (runChecked es s).2 = true) : s.2 = true := by
  induction es generalizing s with
  | nil => exact h
  | cons e es ih =>
      have h' := ih (checkedStep s e) h
      exact (Bool.and_eq_true_iff.mp h').1

theorem checked_valid (es : List Entry) (s : State × Bool)
    (h : (runChecked es s).2 = true) : Valid es s.1 := by
  induction es generalizing s with
  | nil => trivial
  | cons e es ih =>
      have h' := flag_mono es (checkedStep s e) h
      exact ⟨(Bool.and_eq_true_iff.mp h').2, ih (checkedStep s e) h⟩

def toPhysical {X : Type} (gauges : Nat → FramedReplay.Gauge X) (e : Entry) :
    FramedReplay.Event X :=
  ⟨e.scalar, gauges (if e.scalar.op < 3 then e.newFrame else 0)⟩

theorem scalar_projection {X : Type} (gauges : Nat → FramedReplay.Gauge X)
    (es : List Entry) :
    FramedReplay.scalarWord (es.map (toPhysical gauges)) = es.map Entry.scalar := by
  simp only [FramedReplay.scalarWord, List.map_map]
  rfl

end FrameTrace

#print axioms FrameTrace.flag_mono
#print axioms FrameTrace.checked_valid
#print axioms FrameTrace.scalar_projection
