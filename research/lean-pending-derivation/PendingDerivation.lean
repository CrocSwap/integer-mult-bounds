import PendingScheduleData
import OwnershipDatumCore

/-!
Pending coordinates of the selected invocation, derived from the literal PR442
schedule instead of supplied by hand.

Level model (PR386 bit geometry, chart `B_port ⊕ I₅₆`): level −1 is span(q),
which is axis 0; level `l ≥ 0` is the local block `[0,8)` together with the
exterior route blocks of stages `1..l`. An idle child advancing a pair from
level `a` to level `b` has pending set `L_b \ L_a`. Its window is the set of
local invocations strictly after the pair's last local/bridge touch.

What is checked here:
* every idle event's rank is the size of its derived pending set, and levels nest;
* the selected stage lies in the window of every hosted child, whose pair is idle;
* every hosted target mask is the `[offset, offset+width)` slice of its child's
  ascending derived pending axes.

What is not: the identification of level −1 with span(q) and of these levels
with the PR386 frames is the stated model, not a theorem here. The schedule and
blocks are extracted literals (`generate_pending_schedule.py`).

Apache-2.0. Douglas Colkitt, with Claude (Anthropic) assistance.
-/
namespace PendingDerivation
open PendingSchedule

/-- Membership of axis `i` in level `l - 1` (levels are shifted: `0` is level −1). -/
def inLevel (l i : Nat) : Bool :=
  if l = 0 then i == 0
  else i < 8 || (exteriorBlocks.take (l - 1)).any (fun b => b.contains i)

/-- `(pair, rank, source, target)` of the idle child with index `idx`. -/
def idleData (idx : Nat) : Option (Nat × Nat × Nat × Nat) :=
  schedule.findSome? fun
    | .idle j p r s t => if j = idx then some (p, r, s, t) else none
    | _ => none

/-- Ascending derived pending axes `L_target \ L_source` of an idle child. -/
def pendingAxes (idx : Nat) : List Nat :=
  match idleData idx with
  | some (_, _, s, t) => (List.range 64).filter fun i => inLevel t i && !inLevel s i
  | none => []

def windowGo (idx p : Nat) : List Event → List Nat → List Nat
  | [], _ => []
  | .local s q :: es, acc => if q = p then windowGo idx p es [] else windowGo idx p es (acc ++ [s])
  | .bridge d s :: es, acc =>
      if d = p ∨ s = p then windowGo idx p es [] else windowGo idx p es acc
  | .idle j _ _ _ _ :: es, acc => if j = idx then acc else windowGo idx p es acc
  | .exchange :: es, acc => windowGo idx p es acc

/-- Stages of the local invocations strictly between the last touch of the
child's pair and the child. Idle children are not touches. -/
def window (idx : Nat) : List Nat :=
  match idleData idx with
  | some (p, _, _, _) => windowGo idx p schedule []
  | none => []

def idleConsistent : List Event → Bool
  | [] => true
  | .idle idx _ r s t :: es =>
      s ≤ t && (List.range 64).all (fun i => !inLevel s i || inLevel t i) &&
        (pendingAxes idx).length == r && idleConsistent es
  | _ :: es => idleConsistent es

theorem idle_ranks_and_nesting : idleConsistent schedule = true := by decide

theorem top_level_is_ambient : (List.range 64).all (inLevel 9) = true := by decide

theorem pending_child1 : pendingAxes 1 = List.range' 15 7 := by decide
theorem pending_child2 : pendingAxes 2 = List.range' 1 28 := by decide

/-- Idle child hosting a role tag. -/
def child (t : SourceOwnership.Tag) : Nat := SourceOwnership.lookup SourceOwnership.tagChild t.val

def derivedPendingTag (t : SourceOwnership.Tag) (i : SourceOwnership.Axis) : Bool :=
  (pendingAxes (child t)).contains i.val

def derivedTarget (t : SourceOwnership.Tag) (i : SourceOwnership.Axis) : Bool :=
  (((pendingAxes (child t)).drop (SourceOwnership.lookup SourceOwnership.tagOffset t.val)).take
    (SourceOwnership.lookup SourceOwnership.tagWidth t.val)).contains i.val

theorem hosted_windows : ∀ t : SourceOwnership.Tag,
    selectedStage ∈ window (child t) ∧
      (idleData (child t)).map (·.1) ≠ some selectedPair ∧
      SourceOwnership.lookup SourceOwnership.tagOffset t.val +
          SourceOwnership.lookup SourceOwnership.tagWidth t.val ≤ (pendingAxes (child t)).length := by
  decide

/-- The extracted target masks are exactly slices of the derived pending axes. -/
theorem target_derived : ∀ (t : SourceOwnership.Tag) (i : SourceOwnership.Axis),
    SourceOwnership.targetMask t i = derivedTarget t i := by
  decide +kernel

theorem target_in_derived_pending : ∀ (t : SourceOwnership.Tag) (i : SourceOwnership.Axis),
    SourceOwnership.targetMask t i = true → derivedPendingTag t i = true := by
  decide +kernel

end PendingDerivation

#print axioms PendingDerivation.idle_ranks_and_nesting
#print axioms PendingDerivation.hosted_windows
#print axioms PendingDerivation.target_derived
#print axioms PendingDerivation.target_in_derived_pending
