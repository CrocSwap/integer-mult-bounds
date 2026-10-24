import LevelSourceData
import FrameLookup
import PendingScheduleData

/-!
Finite reconstruction of endpoint provenance through the first two hosted
idle children. No endpoint definition reads inLevel or pendingAxes.

An idle target is obtained from the current endpoint of the OTHER pair in
the immediately following literal bridge. Recorded source/target levels
are checked afterwards. These descriptors do not assert that local inputs
are equal to prior physical states: that geometric transport is Phase 2.
The reconstruction stops after the bridge following child 2.
Apache-2.0. Prepared with substantial AI assistance.
-/
namespace PR442LevelModel
set_option maxHeartbeats 0
set_option maxRecDepth 100000

/-- A literal frame, optional reflected complement, lift and routed axes.
Its interpretation is conjugation of the lifted frame projector by the
source route. No coordinate-mask level model appears in these fields. -/
structure Endpoint where
  frame : Fin 944
  complemented : Bool
  stage : Nat
  axes : List Nat
  exterior : List Nat
  deriving DecidableEq, Repr

/-- `side = false` is physical source; `true` is physical target. -/
def entranceEndpoint (p : Port) (side : Bool) : Endpoint :=
  ⟨if side then targetEntrance p else sourceEntrance p,
    false, 0, routeAxes p 0, []⟩

/-- Reflection reverses the word, complements frames and swaps the two
data roles, as recorded by the original local-call owner tables. -/
def localEndpoint (p : Port) (stage : Nat) (reverse after side : Bool) : Endpoint :=
  let localSide := if reverse then !side else side
  let useFinal := if reverse then !after else after
  let f := if useFinal then
      (if localSide then targetExit p else sourceExit p)
    else (if localSide then targetEntrance p else sourceEntrance p)
  ⟨f, reverse, stage, routeAxes p stage, exteriorAxes p stage⟩

inductive Origin where
  | entrance
  | localExit (stage : Nat) (reverse : Bool)
  deriving DecidableEq, Repr

def endpoint (p : Port) (side : Bool) : Origin → Endpoint
  | .entrance => entranceEndpoint p side
  | .localExit stage reverse => localEndpoint p stage reverse true side

/-- A bookkeeping tag read from provenance, not a geometric subspace. -/
def levelTag : Origin → Nat
  | .entrance => 0
  | .localExit stage _ => stage + 1

/-- Dimension of the literal local frame plus its literal exterior lift.
Preservation of this dimension under the route is a separate geometry fact. -/
def descriptorDimension (e : Endpoint) : Nat :=
  (if e.complemented then 8 - (FrameGeometry.frame e.frame).dimension
   else (FrameGeometry.frame e.frame).dimension) + e.exterior.length

structure IdleObservation where
  idx : Nat
  pair : Nat
  rank : Nat
  recordedSource : Nat
  recordedTarget : Nat
  before : Origin
  after : Origin
  deriving DecidableEq, Repr

/-- The partner is selected solely from the next source bridge. -/
def bridgePartner (pair : Nat) : List Event → Option Nat
  | .bridge dst src _ :: _ =>
      if pair = dst then some src else if pair = src then some dst else none
  | _ => none

/-- Replay endpoint provenance, checking local phase tags and bridge agreement.
Idle recorded levels/ranks do not determine state updates. -/
def replay : List Event → Array Origin → List IdleObservation →
    Option (Array Origin × List IdleObservation)
  | [], state, observations => some (state, observations.reverse)
  | .local stage pair reverse :: rest, state, observations => do
      let previous ← state[pair]?
      if levelTag previous != stage then none
      else replay rest (state.set! pair (.localExit stage reverse)) observations
  | .bridge dst src _ :: rest, state, observations => do
      let a ← state[dst]?
      let b ← state[src]?
      if a != b then none else replay rest state observations
  | .idle idx pair rank source target :: rest, state, observations => do
      let before ← state[pair]?
      let partner ← bridgePartner pair rest
      let after ← state[partner]?
      let observation := ⟨idx, pair, rank, source, target, before, after⟩
      replay rest (state.set! pair after) (observation :: observations)

def initialOrigins : Array Origin := #[.entrance, .entrance, .entrance, .entrance]
def reconstructed := replay schedulePrefix initialOrigins []

def observation (idx : Nat) : Option IdleObservation := do
  let (_, observations) ← reconstructed
  observations.find? (fun o => o.idx == idx)

def sourceBefore (idx : Nat) (p : Port) (side : Bool) : Option Endpoint :=
  (observation idx).map (fun o => endpoint p side o.before)

def sourceAfter (idx : Nat) (p : Port) (side : Bool) : Option Endpoint :=
  (observation idx).map (fun o => endpoint p side o.after)

def eraseOrientation : Event → PendingSchedule.Event
  | .local stage pair _ => .local stage pair
  | .idle idx pair rank source target => .idle idx pair rank source target
  | .bridge dst src _ => .bridge dst src

theorem schedule_prefix_join : schedulePrefix.map eraseOrientation =
    PendingSchedule.schedule.take 10 := by decide +kernel

/-- Independently extracted route axes agree with the inherited stage blocks.
Only stages needed to reach the two selected idle children are included. -/
theorem route_axes_join : ∀ (p : Port) (stage : Fin 4),
    routeAxes p stage.val = List.range 8 ++
      (if stage.val = 0 then []
       else PendingSchedule.exteriorBlocks[stage.val - 1]!) := by
  decide +kernel

/-- Source-listed stage-2 positions agree with PR540's literal route embedding. -/
theorem stage2_axis_positions : ∀ (p : Port) (i : Fin 15),
    (routeAxes p 2).getD i.val 64 =
      if i.val < 8 then i.val else i.val + 7 := by decide +kernel

theorem calls_match_schedule : ∀ c : Fin 4,
    Event.local (call c).stage (call c).pair (call c).reverse ∈ schedulePrefix := by
  decide +kernel

/-- Finite source-owner join establishes the reflection's physical-side swap. -/
theorem call_owner_alignment : ∀ (c : Fin 4) (side : Bool) (p : Port),
    let localSide := if (call c).reverse then !side else side
    let role := (if localSide then 120 else 0) + p.val
    (call c).ownerFamilies.getD role 0 =
      (2 * (call c).pair + if side then 1 else 0) * 120 + p.val ∧
    (call c).ownerRouteStages.getD role 0 = (call c).stage ∧
    (call c).ownerRoutePorts.getD role 0 = p.val := by
  decide +kernel

theorem child1_provenance : observation 1 = some
    ⟨1, 1, 7, 2, 3, .localExit 1 true, .localExit 2 false⟩ := by decide +kernel

theorem child2_provenance : observation 2 = some
    ⟨2, 2, 28, 0, 4, .entrance, .localExit 3 true⟩ := by decide +kernel

/-- The ranks and level labels agree with independently reconstructed endpoints.
Child 0 is included only as a prerequisite of child 1, not as a new target. -/
theorem recorded_levels_and_ranks : ∀ (idx : Fin 3) (p : Port) (side : Bool),
    match observation idx.val with
    | none => False
    | some o => o.recordedSource = levelTag o.before ∧
        o.recordedTarget = levelTag o.after ∧
        descriptorDimension (endpoint p side o.before) + o.rank =
          descriptorDimension (endpoint p side o.after) := by
  have h0 : observation 0 = some
      ⟨0, 1, 14, 0, 2, .entrance, .localExit 1 true⟩ := by decide +kernel
  refine Fin.cases ?_ ?_
  · simp only [Fin.val_zero, h0]
    decide +kernel
  · refine Fin.cases ?_ ?_
    · simp only [Fin.val_zero, Fin.val_succ, Nat.reduceAdd, child1_provenance]
      decide +kernel
    · refine Fin.cases ?_ ?_
      · simp only [Fin.val_zero, Fin.val_succ, Nat.reduceAdd, child2_provenance]
        decide +kernel
      · intro i
        exact Fin.elim0 i

theorem child1_endpoints (p : Port) (side : Bool) :
    sourceBefore 1 p side = some (localEndpoint p 1 true true side) ∧
    sourceAfter 1 p side = some (localEndpoint p 2 false true side) := by
  simp [sourceBefore, sourceAfter, child1_provenance, endpoint]

theorem child2_endpoints (p : Port) (side : Bool) :
    sourceBefore 2 p side = some (entranceEndpoint p side) ∧
    sourceAfter 2 p side = some (localEndpoint p 3 true true side) := by
  simp [sourceBefore, sourceAfter, child2_provenance, endpoint]

/-- The stage-2 invocation is inside each child's untouched interval. This
is endpoint provenance only; execution/disjointness across calls is not proved. -/
theorem selected_invocation_inside_windows :
    PendingSchedule.selectedStage = 2 ∧
    (replay (schedulePrefix.take 4) initialOrigins []).map (fun s => s.1[1]?) =
      some (some (.localExit 1 true)) ∧
    (replay (schedulePrefix.take 5) initialOrigins []).map (fun s => s.1[1]?) =
      some (some (.localExit 1 true)) ∧
    (replay (schedulePrefix.take 4) initialOrigins []).map (fun s => s.1[2]?) =
      some (some .entrance) ∧
    (replay (schedulePrefix.take 5) initialOrigins []).map (fun s => s.1[2]?) =
      some (some .entrance) := by
  decide +kernel

end PR442LevelModel
