import RouteTransport

/-!
Literal local entrance projectors agree with the preceding physical
endpoints, including the reflected calls. These identities complement
local frames before exterior extension and retain both physical sides.
No pending-coordinate definition supplies an entrance or prior endpoint.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
-/
namespace PR442LevelModel.Phase2
open scoped Matrix BigOperators

/-- A derived formula for a lifted local entrance: cumulative exterior
coordinates, plus the root coordinate on the physical source side. -/
def beforeMask {K : Type*} [Add K] [Zero K] (stage : Nat) (side : Bool)
    (v : Fin 64 → K) : Fin 64 → K :=
  coordinateMask (List.range' 8 (7 * stage)) v + entranceMask side v

/-- The reflected local roles are swapped and complemented in eight
dimensions. Both orientations therefore have the same sided entrance. -/
theorem local_before_projector (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (stage : Nat) (reverse side : Bool) :
    localProjector K (localEndpoint p stage reverse false side) =
      if side then 0 else rootProjector K p := by
  cases reverse <;> cases side <;>
    simp [localProjector, localEndpoint, source_entrance_projector,
      target_entrance_projector, source_exit_projector K h2,
      target_exit_projector K h2]

theorem local_before_mulVec (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (stage : Nat) (reverse side : Bool) (v : Fin 8 → K) :
    localProjector K (localEndpoint p stage reverse false side) *ᵥ
        (PortGeometry.basis K p *ᵥ v) =
      PortGeometry.basis K p *ᵥ (if side then 0 else rootMask8 v) := by
  rw [local_before_projector K h2]
  cases side
  · simp only [Bool.false_eq_true, if_false]
    exact root_chart_mulVec K h2 p v
  · simp

theorem beforeMask_firstEight (K : Type*) [Field K] (stage : Nat)
    (side : Bool) (v : Fin 64 → K) :
    PortGeometry.firstEight (beforeMask stage side v) =
      if side then 0 else rootMask8 (PortGeometry.firstEight v) := by
  funext j
  have hn8 : ¬8 ≤ j.val := by omega
  have hz : j.val = 0 ↔ j = 0 := by
    constructor
    · intro h
      apply Fin.ext
      exact h
    · intro h
      exact congrArg Fin.val h
  cases side <;>
    simp [PortGeometry.firstEight, beforeMask, coordinateMask, entranceMask,
      rootMask8, List.contains_iff_mem, List.mem_range'_1, hn8, hz]

theorem beforeMask_outside (K : Type*) [Field K] (p : Port)
    (stage : Fin 4) (side : Bool) (v : Fin 64 → K) (i : Fin 64) (hi : 8 ≤ i.val) :
    beforeMask stage.val side v i =
      if (exteriorAxes p stage.val).contains i.val then v i else 0 := by
  have hz : i.val ≠ 0 := by omega
  rw [exterior_axes_contains]
  cases side <;>
    simp [beforeMask, coordinateMask, entranceMask, List.contains_iff_mem,
      List.mem_range'_1, hz, hi]

theorem lifted_local_before_chart (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (stage : Fin 4) (reverse side : Bool) (v : Fin 64 → K) :
    liftedOperator K (localEndpoint p stage.val reverse false side)
        (PortGeometry.chart64 K h2 p v) =
      PortGeometry.chart64 K h2 p (beforeMask stage.val side v) := by
  funext i
  by_cases hi : i.val < 8
  · rw [chart64_inside K h2 p (beforeMask stage.val side v) i hi]
    simp only [liftedOperator, hi, dif_pos, PortGeometry.chart64_firstEight,
      local_before_mulVec K h2, beforeMask_firstEight]
  · rw [PortGeometry.chart64_outside K h2 p _ i (Nat.le_of_not_lt hi)]
    rw [beforeMask_outside K p stage side v i (Nat.le_of_not_lt hi)]
    simp only [liftedOperator, dif_neg hi, localEndpoint_exterior]
    rw [PortGeometry.chart64_outside K h2 p _ i (Nat.le_of_not_lt hi)]

/-- Routing the cumulative entrance exterior includes the local
root-complement and removes the current exterior block. -/
theorem stageIndex_before_exterior (s : Fin 3) (i : Fin 64) :
    (8 ≤ (stageIndex s i).val ∧
      (stageIndex s i).val < 8 + 7 * (s.val + 1)) ↔
      (1 ≤ i.val ∧ i.val < 8 + 7 * s.val) := by
  revert s i
  decide +kernel

theorem stageCoordinates_beforeMask (K : Type*) [Field K] (s : Fin 3)
    (side : Bool) (v : Fin 64 → K) :
    stageCoordinates s (beforeMask (s.val + 1) side v) =
      afterMask s.val side (stageCoordinates s v) := by
  funext i
  have hh := stageIndex_before_exterior s i
  have hz : stageIndex s i = 0 ↔ i.val = 0 := by
    constructor
    · intro h
      exact (stageIndex_root s i).mp (congrArg Fin.val h)
    · intro h
      exact Fin.ext ((stageIndex_root s i).mpr h)
  have hbound : 0 < 8 + 7 * s.val := by omega
  by_cases h0 : i.val = 0
  · have hn : ¬1 ≤ i.val := by omega
    have hi : i.val < 8 + 7 * s.val := by omega
    cases side <;>
      simp [stageCoordinates, Function.comp_apply, beforeMask, entranceMask,
        afterMask, coordinateMask, List.contains_iff_mem, List.mem_range'_1,
        List.mem_range, hh, hz, h0, hn, hi, hbound]
  · have hge1 : 1 ≤ i.val := by omega
    by_cases hi : i.val < 8 + 7 * s.val
    · cases side <;>
        simp [stageCoordinates, Function.comp_apply, beforeMask, entranceMask,
          afterMask, coordinateMask, List.contains_iff_mem, List.mem_range'_1,
          List.mem_range, hh, hz, h0, hge1, hi, hbound]
    · cases side <;>
        simp [stageCoordinates, Function.comp_apply, beforeMask, entranceMask,
          afterMask, coordinateMask, List.contains_iff_mem, List.mem_range'_1,
          List.mem_range, hh, hz, h0, hge1, hi, hbound]

/-- Every stage-1 through stage-3 local entrance is the preceding physical
level, for both orientations and both physical sides. -/
theorem local_endpoint_before_positive (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (s : Fin 3) (reverse side : Bool) (v : Fin 64 → K) :
    endpointOperator K p (localEndpoint p (s.val + 1) reverse false side)
        (PortGeometry.chart64 K h2 p v) =
      PortGeometry.chart64 K h2 p (afterMask s.val side v) := by
  simp only [endpointOperator, localEndpoint_axes]
  have hl := lifted_local_before_chart K h2 p s.succ reverse side
    (stageCoordinates s v)
  simp only [Fin.val_succ] at hl
  rw [route_axes_positive, axisRoute_blockAxes_chart K h2,
    hl,
    axisRoute_blockAxes_chart K h2, stageCoordinates_beforeMask,
    stageCoordinates_involutive]

/-- The stage-zero entrance is the literal root entrance on the source
side and zero on the target side, including reflected local orientation. -/
theorem local_endpoint_before_zero (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (reverse side : Bool) (v : Fin 64 → K) :
    endpointOperator K p (localEndpoint p 0 reverse false side)
        (PortGeometry.chart64 K h2 p v) =
      PortGeometry.chart64 K h2 p (entranceMask side v) := by
  simp only [endpointOperator, localEndpoint_axes]
  simp only [route_axes_zero, axisRoute_zero]
  have hl := lifted_local_before_chart K h2 p 0 reverse side v
  simp only [Fin.val_zero] at hl
  rw [hl]
  congr 1
  funext i
  simp [beforeMask, coordinateMask]

/-- Continuity is equality of ambient operators on every vector, with no
assumption that the source and target endpoint projectors coincide. -/
theorem local_entrance_previous_exit (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (s : Fin 3) (reverse previousReverse side : Bool) (v : Fin 64 → K) :
    endpointOperator K p (localEndpoint p (s.val + 1) reverse false side) v =
      endpointOperator K p (localEndpoint p s.val previousReverse true side) v := by
  have hb := local_endpoint_before_positive K h2 p s reverse side
    ((PortGeometry.chart64 K h2 p).symm v)
  have ha := local_endpoint_after K h2 p s.castSucc previousReverse side
    ((PortGeometry.chart64 K h2 p).symm v)
  rw [Equiv.apply_symm_apply] at hb ha
  exact hb.trans ha.symm

theorem local_initial_entrance (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (reverse side : Bool) (v : Fin 64 → K) :
    endpointOperator K p (localEndpoint p 0 reverse false side) v =
      endpointOperator K p (entranceEndpoint p side) v := by
  have hb := local_endpoint_before_zero K h2 p reverse side
    ((PortGeometry.chart64 K h2 p).symm v)
  have he := entrance_endpoint K h2 p side ((PortGeometry.chart64 K h2 p).symm v)
  rw [Equiv.apply_symm_apply] at hb he
  exact hb.trans he.symm

/-- The previous endpoint origin is read from schedule state just before
the literal call. Its pair, orientation and position come from source data. -/
def callEntranceOrigin (c : Fin 4) : Option Origin :=
  let sourceCall := call c
  let position := schedulePrefix.findIdx (fun event =>
    event == .local sourceCall.stage sourceCall.pair sourceCall.reverse)
  (replay (schedulePrefix.take position) initialOrigins []).bind
    (fun result => result.1[sourceCall.pair]?)

theorem call_stage (c : Fin 4) : (call c).stage = c.val := by
  revert c
  decide +kernel

/-- These origins are reconstructed from the schedule, including the
bridge-aligned idle transfer to pair 1 before its stage-3 call. -/
theorem call_entrance_origin (c : Fin 4) : callEntranceOrigin c = some
    (if c.val = 0 then .entrance else .localExit (c.val - 1) (c.val == 2)) := by
  revert c
  decide +kernel

/-- Connect every selected literal call's input to its independently
replayed prior endpoint, for every port, physical side and input vector. -/
theorem selected_call_entrance_continuity (K : Type*) [Field K]
    (h2 : (2 : K) ≠ 0) (c : Fin 4) (p : Port) (side : Bool) (v : Fin 64 → K) :
    (callEntranceOrigin c).map (fun origin => endpointOperator K p (endpoint p side origin) v) =
      some (endpointOperator K p
        (localEndpoint p (call c).stage (call c).reverse false side) v) := by
  rw [call_entrance_origin, call_stage]
  by_cases hc : c.val = 0
  · simp only [hc, if_pos, Option.map_some, endpoint]
    exact congrArg some (local_initial_entrance K h2 p (call c).reverse side v).symm
  · simp only [hc, if_neg, Option.map_some, endpoint]
    have hs : c.val - 1 + 1 = c.val := by omega
    have h := local_entrance_previous_exit K h2 p
      ⟨c.val - 1, by omega⟩ (call c).reverse (c.val == 2) side v
    apply congrArg some
    simpa only [hs] using h.symm

end PR442LevelModel.Phase2
