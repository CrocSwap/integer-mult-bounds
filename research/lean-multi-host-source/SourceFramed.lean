import FrameTraceData
import FrameTraceRefinement
import SourceEndpoint

/-!
The actual 19,002-event frame trace, executed on arbitrary dirty physical
payloads in all 987 original roles and one blank temporary. Its projection
is exactly the word checked by the whole symbolic matrix certificate.
The other 36 tree leaves are representation padding; the checked finite-role
projection proves that the word never accesses them as registers.

This discharges every chronological frame-label and COPY/ERASE cleanliness
guard, for a supplied family of genuine address gauges. It does not assert
that a nominal register is a distinct owned physical stream, or that those
gauges are the actual source projectors; those concrete geometry and ownership
certificates are separate. Rows here use a common invocation address chart.
-/
namespace SourceFramed
open TreeReplay (Tree)
set_option maxRecDepth 100000
set_option maxHeartbeats 0

def normalizedInput {X : Type} (gauges : Nat → FramedReplay.Gauge X)
    (input : Nat → X → Bool) (i : Nat) : X → Bool :=
  fun a => input i ((gauges (SourceFrameTrace.state0.frames.get i)).forward a)

def initial {X : Type} (gauges : Nat → FramedReplay.Gauge X)
    (input : Nat → X → Bool) : FramedReplay.Store X :=
  Tree.tabulate 10 (fun i => (gauges (SourceFrameTrace.state0.frames.get i),
    if i < 987 then input i else fun _ => false))

def final {X : Type} (gauges : Nat → FramedReplay.Gauge X)
    (input : Nat → X → Bool) : FramedReplay.Store X :=
  FramedReplay.runPhysical
    (SourceFrameTrace.forward.map (FrameTrace.toPhysical gauges)) (initial gauges input)

theorem initial_matches {X : Type} (gauges : Nat → FramedReplay.Gauge X)
    (input : Nat → X → Bool) :
    FrameTrace.Matches gauges SourceFrameTrace.state0 (initial gauges input) := by
  unfold FrameTrace.Matches initial
  rw [Tree.map_tabulate]
  change Tree.tabulate 10 (fun i => gauges (SourceFrameTrace.state0.frames.get i)) = _
  simpa only [Tree.map_tabulate, Function.comp_def] using
    congrArg (Tree.map gauges) SourceFrameTrace.initial_tabulate

theorem initial_decoded {X : Type} (gauges : Nat → FramedReplay.Gauge X)
    (input : Nat → X → Bool) :
    FramedReplay.decode (initial gauges input) =
      Tree.tabulate 10 (fun i => if i < 987 then normalizedInput gauges input i
        else fun _ => false) := by
  unfold FramedReplay.decode initial
  rw [Tree.map_tabulate]
  apply congrArg (Tree.tabulate 10)
  funext i
  change FramedReplay.decodeRow
    (gauges (SourceFrameTrace.state0.frames.get i),
      if i < 987 then input i else fun _ => false) =
    (if i < 987 then normalizedInput gauges input i else fun _ => false)
  by_cases hi : i < 987
  · simp only [if_pos hi]
    rfl
  · simp only [if_neg hi]
    rfl

theorem actual_valid {X : Type} (gauges : Nat → FramedReplay.Gauge X)
    (input : Nat → X → Bool) :
    FramedReplay.ValidTrace
      (SourceFrameTrace.forward.map (FrameTrace.toPhysical gauges)) (initial gauges input) := by
  apply FrameTrace.valid_trace gauges SourceFrameTrace.forward SourceFrameTrace.state0
    (initial gauges input) (initial_matches gauges input) SourceFrameTrace.forward_valid
  rw [SourceFrameTrace.scalar_word, initial_decoded]
  exact SourceMatrix.actual_payload_clean _

theorem final_matches {X : Type} (gauges : Nat → FramedReplay.Gauge X)
    (input : Nat → X → Bool) :
    FrameTrace.Matches gauges SourceFrameTrace.state96 (final gauges input) := by
  have h := FrameTrace.matches_run gauges SourceFrameTrace.forward SourceFrameTrace.state0
    (initial gauges input) (initial_matches gauges input) true
  rw [SourceFrameTrace.forward_checked] at h
  exact h

/-- Whole-store endpoint for arbitrary and correlated physical dirty payloads. -/
theorem actual_decoded_endpoint {X : Type} (gauges : Nat → FramedReplay.Gauge X)
    (input : Nat → X → Bool) :
    FramedReplay.decode (final gauges input) =
      Tree.tabulate 10 (SourceMatrix.endpointPayload (normalizedInput gauges input)) := by
  unfold final
  rw [FramedReplay.decode_run _ _ (actual_valid gauges input),
    FrameTrace.scalar_projection, SourceFrameTrace.scalar_word, initial_decoded,
    SourceMatrix.arbitrary_dirty_payloads]

/-- Physical endpoint in each final row's own chart, including all original
roles and the blank temporary. No arbitrary dirty input was specialized. -/
theorem actual_physical_endpoint {X : Type} (gauges : Nat → FramedReplay.Gauge X)
    (input : Nat → X → Bool) (i : Nat) (hi : i < 1024) (a : X) :
    ((final gauges input).get i).2 a =
      SourceMatrix.endpointPayload (normalizedInput gauges input) i
        ((gauges (SourceFrameTrace.state96.frames.get i)).inverse a) := by
  -- Keep the literal execution abstract while deriving the row-level identity.
  have physical_of_decode (s : FramedReplay.Store X) (f : Nat → X → Bool)
      (g : FramedReplay.Gauge X)
      (hd : FramedReplay.decode s = Tree.tabulate 10 f)
      (hg : (s.get i).1 = g) : (s.get i).2 a = f i (g.inverse a) := by
    have h := congrArg (fun t => Tree.get t i) hd
    dsimp only at h
    rw [FramedReplay.decode, Tree.map_get, Tree.get_tabulate 10 _ i hi] at h
    have ha := congrFun h (g.inverse a)
    simp only [FramedReplay.decodeRow, hg, FramedReplay.Gauge.forward_inverse] at ha
    exact ha
  exact physical_of_decode (final gauges input)
    (SourceMatrix.endpointPayload (normalizedInput gauges input))
    (gauges (SourceFrameTrace.state96.frames.get i))
    (actual_decoded_endpoint gauges input)
    (FrameTrace.matches_get gauges SourceFrameTrace.state96
      (final gauges input) (final_matches gauges input) i)

theorem actual_temporary_restored {X : Type} (gauges : Nat → FramedReplay.Gauge X)
    (input : Nat → X → Bool) :
    ((final gauges input).get 987).2 = fun _ => false := by
  funext a
  rw [actual_physical_endpoint gauges input 987 (by decide) a]
  rfl

/-- A function-level endpoint avoids reducing the literal interpreter when
later proofs select several physical outputs at once. -/
theorem all_physical_endpoints {X : Type} (gauges : Nat → FramedReplay.Gauge X)
    (input : Nat → X → Bool) :
    (fun r : Fin 1024 => ((final gauges input).get r.val).2) =
      (fun r a => SourceMatrix.endpointPayload (normalizedInput gauges input) r.val
        ((gauges (SourceFrameTrace.state96.frames.get r.val)).inverse a)) := by
  funext r a
  exact actual_physical_endpoint gauges input r.val r.isLt a

#print axioms initial_matches
#print axioms initial_decoded
#print axioms actual_valid
#print axioms final_matches
#print axioms actual_decoded_endpoint
#print axioms actual_physical_endpoint
#print axioms actual_temporary_restored
#print axioms all_physical_endpoints
end SourceFramed
