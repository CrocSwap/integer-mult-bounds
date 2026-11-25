import TreeReplay

/-!
Literal framed MOVE / XOR / fresh COPY / checked ERASE simulation.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.

This uses the existing `FramedXor` gauge convention for the actual source
interpreter's copy/erase opcodes and tree register store. A MOVE reindexes
the named row by old.forward ∘ new.inverse. COPY performs the same transport
from the source gauge to the fresh destination gauge. ERASE may clear only
a temporary whose decoded contents equal the still-live source contents.

This is a generic refinement theorem, not an instantiated source provider.
An actual source certificate must supply the concrete frame gauges and new
frame for every event, prove the chronological admissibility predicate,
and identify distinct tree registers with their actual physical owners.
No source frame or ownership claim follows from the product/tree types.
-/
namespace FramedReplay

open TreeReplay (Tree)
/- The same four-field address-gauge interface as main's FramedXor.lean.
It is reproduced here as a local dependency without importing unrelated
fanout proofs. No conclusion about those proofs is used here. -/
structure Gauge (X : Type) where
  forward : X → X
  inverse : X → X
  inverse_forward : ∀ x, inverse (forward x) = x
  forward_inverse : ∀ x, forward (inverse x) = x

abbrev Row (X : Type) := Gauge X × (X → Bool)
abbrev Store (X : Type) := Tree (Row X)

def decodeRow {X : Type} (r : Row X) : X → Bool :=
  fun a => r.2 (r.1.forward a)

def decode {X : Type} (s : Store X) : Tree (X → Bool) := s.map decodeRow

def reframe {X : Type} (new : Gauge X) (r : Row X) : Row X :=
  (new, fun a => r.2 (r.1.forward (new.inverse a)))

theorem decode_reframe {X : Type} (new : Gauge X) (r : Row X) :
    decodeRow (reframe new r) = decodeRow r := by
  funext a
  simp only [decodeRow, reframe, new.inverse_forward]

structure Event (X : Type) where
  scalar : LinearReplay.Event
  /-- Used by MOVE and COPY. After ERASE this is only the gauge attached to
  an identically zero/unallocated row; changing it has no physical action. -/
  newFrame : Gauge X

def physicalStep {X : Type} (s : Store X) (e : Event X) : Store X :=
  match e.scalar.op with
  | 0 => s.put e.scalar.x (reframe e.newFrame (s.get e.scalar.x))
  | 1 => if e.scalar.odd then
      s.put e.scalar.x ((s.get e.scalar.x).1,
        fun a => (s.get e.scalar.x).2 a ^^ (s.get e.scalar.y).2 a)
    else s
  | 2 => s.put e.scalar.y (reframe e.newFrame (s.get e.scalar.x))
  | _ => s.put e.scalar.y (e.newFrame, fun _ => false)

/-- Source-specific range, owner and frame-label checks are additional.
Here the predicates express the semantic common-frame and clean-work rules. -/
def ValidStep {X : Type} (s : Store X) (e : Event X) : Prop :=
  match e.scalar.op with
  | 0 => True
  | 1 => (s.get e.scalar.x).1 = (s.get e.scalar.y).1
  | 2 => decodeRow (s.get e.scalar.y) = fun _ => false
  | 3 => decodeRow (s.get e.scalar.x) = decodeRow (s.get e.scalar.y)
  | _ => False

theorem put_get (s : Tree α) (i : Nat) : s.put i (s.get i) = s := by
  induction s generalizing i with
  | leaf a => rfl
  | node l r ihl ihr =>
      simp only [Tree.put, Tree.get]
      split <;> simp_all

theorem decode_xor {X : Type} (r t : Row X) (common : r.1 = t.1) :
    decodeRow (r.1, fun a => r.2 a ^^ t.2 a) =
      fun a => decodeRow r a ^^ decodeRow t a := by
  funext a
  simp only [decodeRow]
  rw [common]

theorem decode_step {X : Type} (s : Store X) (e : Event X)
    (valid : ValidStep s e) :
    decode (physicalStep s e) =
      TreeReplay.step (fun _ : X => false) (fun a b x => a x ^^ b x)
        (decode s) e.scalar := by
  obtain ⟨⟨op, x, y, odd⟩, newFrame⟩ := e
  cases op with
  | zero =>
      simp only [physicalStep, decode, Tree.map_put, decode_reframe, TreeReplay.step]
      rw [← Tree.map_get decodeRow s x]
      exact put_get _ _
  | succ op =>
      cases op with
      | zero =>
          change (s.get x).1 = (s.get y).1 at valid
          cases odd <;>
            simp [physicalStep, decode, TreeReplay.step, Tree.map_put,
              Tree.map_get, decode_xor _ _ valid]
      | succ op =>
          cases op with
          | zero =>
              simp [physicalStep, decode, TreeReplay.step, Tree.map_put,
                Tree.map_get, decode_reframe]
          | succ op =>
              simp only [physicalStep, decode, TreeReplay.step, Tree.map_put]
              rfl

/-- Decoded blankness is actual physical blankness, since the gauge is a
bijection. COPY therefore does not overwrite arbitrary dirty workspace. -/
theorem physical_blank_of_decoded_blank {X : Type} (r : Row X)
    (blank : decodeRow r = fun _ => false) (a : X) : r.2 a = false := by
  have h := congrFun blank (r.1.inverse a)
  simpa only [decodeRow, r.1.forward_inverse] using h

/-- Before ERASE the temporary really is the source transported to its
current frame. This is the physical content of the decoded equality guard. -/
theorem erase_guard_transport {X : Type} (source temporary : Row X)
    (equal : decodeRow source = decodeRow temporary) (a : X) :
    temporary.2 a =
      source.2 (source.1.forward (temporary.1.inverse a)) := by
  have h := congrFun equal (temporary.1.inverse a)
  simpa only [decodeRow, temporary.1.forward_inverse] using h.symm

def runPhysical {X : Type} (events : List (Event X)) (s : Store X) : Store X :=
  events.foldl physicalStep s

def scalarWord {X : Type} (events : List (Event X)) : List LinearReplay.Event :=
  events.map Event.scalar

def ValidTrace {X : Type} : List (Event X) → Store X → Prop
  | [], _ => True
  | e :: es, s => ValidStep s e ∧ ValidTrace es (physicalStep s e)

/-- Chronological simulation, including the actual temporary outputs from
each preceding event. The predicates must be proved on that same execution. -/
theorem decode_run {X : Type} (events : List (Event X)) (s : Store X)
    (valid : ValidTrace events s) :
    decode (runPhysical events s) = TreeReplay.runPayloads (scalarWord events) (decode s) := by
  induction events generalizing s with
  | nil => rfl
  | cons e es ih =>
      change decode (runPhysical es (physicalStep s e)) =
        TreeReplay.runPayloads (scalarWord es)
          (TreeReplay.step (fun _ : X => false) (fun a b x => a x ^^ b x)
            (decode s) e.scalar)
      rw [ih _ valid.2, decode_step _ _ valid.1]

end FramedReplay

#print axioms FramedReplay.decode_reframe
#print axioms FramedReplay.put_get
#print axioms FramedReplay.decode_xor
#print axioms FramedReplay.decode_step
#print axioms FramedReplay.physical_blank_of_decoded_blank
#print axioms FramedReplay.erase_guard_transport
#print axioms FramedReplay.decode_run
