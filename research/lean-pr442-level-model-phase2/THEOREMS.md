# Exact Phase 2 theorem statements

AI-assisted inventory extracted from the Lean sources. All declarations are in `PR442LevelModel.Phase2`. This document does not establish compilation; the validation receipt records measured results.


`FieldEntrance.lean:25`

```lean
theorem projector_entry (K : Type*) [Field K] (frame : Fin 944)
    (i j : Fin 8) :
    FrameGeometry.projector K frame i j =
      (FrameGeometry.scaled frame i j : K) / 4
```


`FieldEntrance.lean:34`

```lean
theorem source_entrance_projector_entry (K : Type*) [Field K]
    (port : Fin 120) (i j : Fin 8) :
    FrameGeometry.projector K (sourceEntrance port) i j =
      q K port i * q K port j / 4
```


`FieldEntrance.lean:43`

```lean
theorem source_entrance_projector (K : Type*) [Field K] (port : Fin 120) :
    FrameGeometry.projector K (sourceEntrance port) = rootProjector K port
```


`FieldEntrance.lean:48`

```lean
theorem target_entrance_projector (K : Type*) [Field K] (port : Fin 120) :
    FrameGeometry.projector K (targetEntrance port) = 0
```


`FieldEntrance.lean:53`

```lean
theorem source_exit_projector (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) :
    FrameGeometry.projector K (sourceExit port) = 1
```


`FieldEntrance.lean:59`

```lean
theorem target_exit_projector (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) :
    FrameGeometry.projector K (targetExit port) = 1 - rootProjector K port
```


`FieldEntrance.lean:75`

```lean
theorem old_source_entrance_projector (K : Type*) [Field K]
    (port : Fin 120) :
    FrameGeometry.projector K (oldSourceEntrance port) =
      (fun i j => (oldRootVector port i : K) *
        (oldRootVector port j : K) / 4 : Matrix (Fin 8) (Fin 8) K)
```


`FieldEntrance.lean:86`

```lean
theorem old_target_exit_projector (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) :
    FrameGeometry.projector K (oldTargetExit port) =
      1 - Matrix.of (fun i j : Fin 8 => (oldRootVector port i : K) *
        (oldRootVector port j : K) / 4)
```


`FieldEntrance.lean:97`

```lean
theorem root_square_sum (K : Type*) [Field K] (port : Fin 120) :
    (∑ i : Fin 8, q K port i * q K port i) = 4
```


`FieldEntrance.lean:105`

```lean
theorem source_entrance_mulVec (K : Type*) [Field K] (port : Fin 120)
    (v : Fin 8 → K) :
    FrameGeometry.projector K (sourceEntrance port) *ᵥ v =
      ((q K port ⬝ᵥ v) / 4) • q K port
```


`FieldEntrance.lean:126`

```lean
theorem source_entrance_fixes_root (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) :
    FrameGeometry.projector K (sourceEntrance port) *ᵥ q K port = q K port
```


`FieldEntrance.lean:134`

```lean
theorem root_ne_zero (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) : q K port ≠ 0
```


`FieldEntrance.lean:142`

```lean
theorem rootProjector_ne_zero (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) : rootProjector K port ≠ 0
```


`FieldEntrance.lean:149`

```lean
theorem entrance_projectors_differ (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) :
    FrameGeometry.projector K (sourceEntrance port) ≠
      FrameGeometry.projector K (targetEntrance port)
```


`FieldEntrance.lean:156`

```lean
theorem exit_projectors_differ (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) :
    FrameGeometry.projector K (sourceExit port) ≠
      FrameGeometry.projector K (targetExit port)
```


`FieldEntrance.lean:167`

```lean
theorem source_entrance_range (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) :
    Set.range (fun v : Fin 8 → K =>
      FrameGeometry.projector K (sourceEntrance port) *ᵥ v) =
    (Submodule.span K ({q K port} : Set (Fin 8 → K)) : Set (Fin 8 → K))
```


`FieldEntrance.lean:184`

```lean
theorem rootProjector_idempotent (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) :
    rootProjector K port * rootProjector K port = rootProjector K port
```


`FieldEntrance.lean:191`

```lean
theorem rootProjector_chart (K : Type*) [Field K] (port : Fin 120) :
    rootProjector K port =
      PortGeometry.basis K port *
        Matrix.diagonal (fun i : Fin 8 => if i = 0 then (1 : K) else 0) *
        (PortGeometry.basis K port).transpose
```


`FieldEntrance.lean:206`

```lean
theorem root_chart_mulVec (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) (v : Fin 8 → K) :
    rootProjector K port *ᵥ (PortGeometry.basis K port *ᵥ v) =
      PortGeometry.basis K port *ᵥ
        (fun i : Fin 8 => if i = 0 then v i else 0)
```


`FieldEntrance.lean:221`

```lean
theorem source_projector_difference (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) :
    FrameGeometry.projector K (sourceExit port) -
      FrameGeometry.projector K (sourceEntrance port) = 1 - rootProjector K port
```


`FieldEntrance.lean:229`

```lean
theorem target_projector_difference (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) :
    FrameGeometry.projector K (targetExit port) -
      FrameGeometry.projector K (targetEntrance port) = 1 - rootProjector K port
```


`FieldEntrance.lean:235`

```lean
theorem endpoint_difference_cancels (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) :
    (FrameGeometry.projector K (sourceExit port) -
      FrameGeometry.projector K (sourceEntrance port)) -
    (FrameGeometry.projector K (targetExit port) -
      FrameGeometry.projector K (targetEntrance port)) = 0
```


`FieldEntrance.lean:244`

```lean
theorem root_complement_left (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) :
    rootProjector K port * (1 - rootProjector K port) = 0
```


`FieldEntrance.lean:249`

```lean
theorem root_complement_right (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) :
    (1 - rootProjector K port) * rootProjector K port = 0
```


`RouteTransport.lean:46`

```lean
theorem localEndpoint_axes (p : Port) (stage : Nat) (reverse after side : Bool) :
    (localEndpoint p stage reverse after side).axes = routeAxes p stage
```


`RouteTransport.lean:50`

```lean
theorem localEndpoint_exterior (p : Port) (stage : Nat) (reverse after side : Bool) :
    (localEndpoint p stage reverse after side).exterior = exteriorAxes p stage
```


`RouteTransport.lean:53`

```lean
theorem entranceEndpoint_axes (p : Port) (side : Bool) :
    (entranceEndpoint p side).axes = routeAxes p 0
```


`RouteTransport.lean:69`

```lean
theorem relocationIndex_involutive (s : Fin 3) : Function.Involutive (relocationIndex s)
```


`RouteTransport.lean:77`

```lean
theorem relocate_involutive {K : Type*} (s : Fin 3) (v : Fin 64 → K) :
    relocate s (relocate s v) = v
```


`RouteTransport.lean:82`

```lean
theorem relocation_local (s : Fin 3) (j : Fin 8) :
    relocationIndex s (Fin.castAdd 56 j) = Fin.castAdd 56 j
```


`RouteTransport.lean:87`

```lean
theorem relocation_gather_index (s : Fin 3) (j : Fin 15) :
    (⟨(blockAxes s).getD j.val 0 % 64, Nat.mod_lt _ (by decide)⟩ : Fin 64) =
      relocationIndex s (if h : j.val < 8 then ⟨j.val, by omega⟩
        else ⟨j.val + 7, by omega⟩)
```


`RouteTransport.lean:94`

```lean
theorem gather_blockAxes {K : Type*} (s : Fin 3) (v : Fin 64 → K) :
    gatherAxes (blockAxes s) v = PortGeometry.gatherStage2 (relocate s v)
```


`RouteTransport.lean:101`

```lean
theorem blockAxes_length (s : Fin 3) : (blockAxes s).length = 15
```


`RouteTransport.lean:104`

```lean
theorem blockAxes_index (s : Fin 3) (i : Fin 64) :
    (blockAxes s).idxOf i.val =
      if i.val < 8 then i.val
      else if blockStart s ≤ i.val ∧ i.val < blockStart s + 7 then
        i.val - blockStart s + 8 else 15
```


`RouteTransport.lean:112`

```lean
theorem relocation_cases (s : Fin 3) (i : Fin 64) :
    (relocationIndex s i).val =
      if i.val < 8 then i.val
      else if blockStart s ≤ i.val ∧ i.val < blockStart s + 7 then
        i.val - blockStart s + 15
      else if 15 ≤ i.val ∧ i.val < 22 then i.val - 15 + blockStart s
      else i.val
```


`RouteTransport.lean:123`

```lean
theorem axisRoute_blockAxes (K : Type*) [Field K] (p : Port) (s : Fin 3)
    (v : Fin 64 → K) :
    axisRoute K p (blockAxes s) v =
      relocate s (PortGeometry.sourceRoute64 K p (relocate s v))
```


`RouteTransport.lean:162`

```lean
theorem stageIndex_involutive (s : Fin 3) : Function.Involutive (stageIndex s)
```


`RouteTransport.lean:167`

```lean
theorem stageCoordinates_involutive {K : Type*} (s : Fin 3) (v : Fin 64 → K) :
    stageCoordinates s (stageCoordinates s v) = v
```


`RouteTransport.lean:172`

```lean
theorem relocation_region (s : Fin 3) (i : Fin 64) :
    (relocationIndex s i).val < 8 ↔ i.val < 8
```


`RouteTransport.lean:177`

```lean
theorem relocate_firstEight {K : Type*} (s : Fin 3) (v : Fin 64 → K) :
    PortGeometry.firstEight (relocate s v) = PortGeometry.firstEight v
```


`RouteTransport.lean:182`

```lean
theorem relocate_chart (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (s : Fin 3) (v : Fin 64 → K) :
    relocate s (PortGeometry.chart64 K h2 p v) =
      PortGeometry.chart64 K h2 p (relocate s v)
```


`RouteTransport.lean:202`

```lean
theorem axisRoute_blockAxes_chart (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (s : Fin 3) (v : Fin 64 → K) :
    axisRoute K p (blockAxes s) (PortGeometry.chart64 K h2 p v) =
      PortGeometry.chart64 K h2 p (stageCoordinates s v)
```


`RouteTransport.lean:213`

```lean
theorem exterior_block_shapes (s : Fin 3) :
    PendingSchedule.exteriorBlocks[s.val]! = List.range' (blockStart s) 7
```


`RouteTransport.lean:218`

```lean
theorem route_axes_zero (p : Port) : routeAxes p 0 = List.range 8
```


`RouteTransport.lean:221`

```lean
theorem route_axes_positive (p : Port) (s : Fin 3) :
    routeAxes p (s.val + 1) = blockAxes s
```


`RouteTransport.lean:229`

```lean
theorem exterior_axes_contains (p : Port) (stage : Fin 4) (i : Fin 64) :
    (exteriorAxes p stage.val).contains i.val =
      decide (8 ≤ i.val ∧ i.val < 8 + 7 * stage.val)
```


`RouteTransport.lean:267`

```lean
theorem local_after_projector (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (stage : Nat) (reverse side : Bool) :
    localProjector K (localEndpoint p stage reverse true side) =
      if side then 1 - rootProjector K p else 1
```


`RouteTransport.lean:276`

```lean
theorem local_after_mulVec (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (stage : Nat) (reverse side : Bool) (v : Fin 8 → K) :
    localProjector K (localEndpoint p stage reverse true side) *ᵥ
        (PortGeometry.basis K p *ᵥ v) =
      PortGeometry.basis K p *ᵥ (v - if side then rootMask8 v else 0)
```


`RouteTransport.lean:288`

```lean
theorem afterMask_firstEight (K : Type*) [Field K] (stage : Nat)
    (side : Bool) (v : Fin 64 → K) :
    PortGeometry.firstEight (afterMask stage side v) =
      PortGeometry.firstEight v -
        if side then rootMask8 (PortGeometry.firstEight v) else 0
```


`RouteTransport.lean:303`

```lean
theorem afterMask_outside (K : Type*) [Field K] (p : Port)
    (stage : Fin 4) (side : Bool) (v : Fin 64 → K) (i : Fin 64) (hi : 8 ≤ i.val) :
    afterMask stage.val side v i =
      if (exteriorAxes p stage.val).contains i.val then v i else 0
```


`RouteTransport.lean:313`

```lean
theorem chart64_inside (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (v : Fin 64 → K) (i : Fin 64) (hi : i.val < 8) :
    PortGeometry.chart64 K h2 p v i =
      (PortGeometry.basis K p *ᵥ PortGeometry.firstEight v) ⟨i.val, hi⟩
```


`RouteTransport.lean:325`

```lean
theorem lifted_local_after_chart (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (stage : Fin 4) (reverse side : Bool) (v : Fin 64 → K) :
    liftedOperator K (localEndpoint p stage.val reverse true side)
        (PortGeometry.chart64 K h2 p v) =
      PortGeometry.chart64 K h2 p (afterMask stage.val side v)
```


`RouteTransport.lean:340`

```lean
theorem stageIndex_after_region (s : Fin 3) (i : Fin 64) :
    (stageIndex s i).val < 8 + 7 * (s.val + 1) ↔
      i.val < 8 + 7 * (s.val + 1)
```


`RouteTransport.lean:346`

```lean
theorem stageIndex_root (s : Fin 3) (i : Fin 64) :
    (stageIndex s i).val = 0 ↔ i.val = 0
```


`RouteTransport.lean:351`

```lean
theorem stageIndex_zero (s : Fin 3) (i : Fin 64) :
    stageIndex s i = 0 ↔ i = 0
```


`RouteTransport.lean:356`

```lean
theorem stageCoordinates_afterMask (K : Type*) [Field K] (s : Fin 3)
    (side : Bool) (v : Fin 64 → K) :
    stageCoordinates s (afterMask (s.val + 1) side v) =
      afterMask (s.val + 1) side (stageCoordinates s v)
```


`RouteTransport.lean:365`

```lean
theorem axisRoute_zero (K : Type*) [Field K] (p : Port) (v : Fin 64 → K) :
    axisRoute K p (List.range 8) v = v
```


`RouteTransport.lean:372`

```lean
theorem local_endpoint_after (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (stage : Fin 4) (reverse side : Bool) (v : Fin 64 → K) :
    endpointOperator K p (localEndpoint p stage.val reverse true side)
        (PortGeometry.chart64 K h2 p v) =
      PortGeometry.chart64 K h2 p (afterMask stage.val side v)
```


`RouteTransport.lean:397`

```lean
theorem entranceMask_firstEight (K : Type*) [Field K] (side : Bool) (v : Fin 64 → K) :
    PortGeometry.firstEight (entranceMask side v) =
      if side then 0 else rootMask8 (PortGeometry.firstEight v)
```


`RouteTransport.lean:409`

```lean
theorem entrance_endpoint (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (side : Bool) (v : Fin 64 → K) :
    endpointOperator K p (entranceEndpoint p side) (PortGeometry.chart64 K h2 p v) =
      PortGeometry.chart64 K h2 p (entranceMask side v)
```


`RouteTransport.lean:435`

```lean
theorem stage2_literal_route (K : Type*) [Field K] (p : Port) (v : Fin 64 → K) :
    axisRoute K p (routeAxes p 2) v = PortGeometry.sourceRoute64 K p v
```


`RouteTransport.lean:447`

```lean
theorem axisRoute_blockAxes_involutive (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (s : Fin 3) : Function.Involutive (axisRoute K p (blockAxes s))
```


`RouteTransport.lean:463`

```lean
theorem stageCoordinates_dot (K : Type*) [Field K] (s : Fin 3)
    (v w : Fin 64 → K) :
    (∑ i, stageCoordinates s v i * stageCoordinates s w i) = ∑ i, v i * w i
```


`RouteTransport.lean:470`

```lean
theorem axisRoute_blockAxes_dot (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (s : Fin 3) (v w : Fin 64 → K) :
    (∑ i, axisRoute K p (blockAxes s) v i * axisRoute K p (blockAxes s) w i) =
      ∑ i, v i * w i
```


`RouteTransport.lean:484`

```lean
theorem route15_entrance_block (K : Type*) [Field K] (p : Port) (i j : Fin 8) :
    PortGeometry.route15 K p ⟨i.val, by omega⟩ ⟨j.val, by omega⟩ =
      FrameGeometry.projector K (sourceEntrance p) i j
```


`EntranceContinuity.lean:21`

```lean
theorem local_before_projector (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (stage : Nat) (reverse side : Bool) :
    localProjector K (localEndpoint p stage reverse false side) =
      if side then 0 else rootProjector K p
```


`EntranceContinuity.lean:30`

```lean
theorem local_before_mulVec (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (stage : Nat) (reverse side : Bool) (v : Fin 8 → K) :
    localProjector K (localEndpoint p stage reverse false side) *ᵥ
        (PortGeometry.basis K p *ᵥ v) =
      PortGeometry.basis K p *ᵥ (if side then 0 else rootMask8 v)
```


`EntranceContinuity.lean:41`

```lean
theorem beforeMask_firstEight (K : Type*) [Field K] (stage : Nat)
    (side : Bool) (v : Fin 64 → K) :
    PortGeometry.firstEight (beforeMask stage side v) =
      if side then 0 else rootMask8 (PortGeometry.firstEight v)
```


`EntranceContinuity.lean:58`

```lean
theorem beforeMask_outside (K : Type*) [Field K] (p : Port)
    (stage : Fin 4) (side : Bool) (v : Fin 64 → K) (i : Fin 64) (hi : 8 ≤ i.val) :
    beforeMask stage.val side v i =
      if (exteriorAxes p stage.val).contains i.val then v i else 0
```


`EntranceContinuity.lean:68`

```lean
theorem lifted_local_before_chart (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (stage : Fin 4) (reverse side : Bool) (v : Fin 64 → K) :
    liftedOperator K (localEndpoint p stage.val reverse false side)
        (PortGeometry.chart64 K h2 p v) =
      PortGeometry.chart64 K h2 p (beforeMask stage.val side v)
```


`EntranceContinuity.lean:85`

```lean
theorem stageIndex_before_exterior (s : Fin 3) (i : Fin 64) :
    (8 ≤ (stageIndex s i).val ∧
      (stageIndex s i).val < 8 + 7 * (s.val + 1)) ↔
      (1 ≤ i.val ∧ i.val < 8 + 7 * s.val)
```


`EntranceContinuity.lean:92`

```lean
theorem stageCoordinates_beforeMask (K : Type*) [Field K] (s : Fin 3)
    (side : Bool) (v : Fin 64 → K) :
    stageCoordinates s (beforeMask (s.val + 1) side v) =
      afterMask s.val side (stageCoordinates s v)
```


`EntranceContinuity.lean:125`

```lean
theorem local_endpoint_before_positive (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (s : Fin 3) (reverse side : Bool) (v : Fin 64 → K) :
    endpointOperator K p (localEndpoint p (s.val + 1) reverse false side)
        (PortGeometry.chart64 K h2 p v) =
      PortGeometry.chart64 K h2 p (afterMask s.val side v)
```


`EntranceContinuity.lean:141`

```lean
theorem local_endpoint_before_zero (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (reverse side : Bool) (v : Fin 64 → K) :
    endpointOperator K p (localEndpoint p 0 reverse false side)
        (PortGeometry.chart64 K h2 p v) =
      PortGeometry.chart64 K h2 p (entranceMask side v)
```


`EntranceContinuity.lean:157`

```lean
theorem local_entrance_previous_exit (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (s : Fin 3) (reverse previousReverse side : Bool) (v : Fin 64 → K) :
    endpointOperator K p (localEndpoint p (s.val + 1) reverse false side) v =
      endpointOperator K p (localEndpoint p s.val previousReverse true side) v
```


`EntranceContinuity.lean:168`

```lean
theorem local_initial_entrance (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (reverse side : Bool) (v : Fin 64 → K) :
    endpointOperator K p (localEndpoint p 0 reverse false side) v =
      endpointOperator K p (entranceEndpoint p side) v
```


`EntranceContinuity.lean:187`

```lean
theorem call_stage (c : Fin 4) : (call c).stage = c.val
```


`EntranceContinuity.lean:193`

```lean
theorem call_entrance_origin (c : Fin 4) : callEntranceOrigin c = some
    (if c.val = 0 then .entrance else .localExit (c.val - 1) (c.val == 2))
```


`EntranceContinuity.lean:200`

```lean
theorem selected_call_entrance_continuity (K : Type*) [Field K]
    (h2 : (2 : K) ≠ 0) (c : Fin 4) (p : Port) (side : Bool) (v : Fin 64 → K) :
    (callEntranceOrigin c).map (fun origin => endpointOperator K p (endpoint p side origin) v) =
      some (endpointOperator K p
        (localEndpoint p (call c).stage (call c).reverse false side) v)
```


`IdleOperators.lean:38`

```lean
theorem chart64_sub (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) (v w : Fin 64 → K) :
    PortGeometry.chart64 K h2 port (v - w) =
      PortGeometry.chart64 K h2 port v - PortGeometry.chart64 K h2 port w
```


`IdleOperators.lean:49`

```lean
theorem child1_source_operators (K : Type*) [Field K]
    (port : Fin 120) (side : Bool) :
    sourceBeforeOperator K 1 port side =
      endpointOperator K port (localEndpoint port 1 true true side) ∧
    sourceAfterOperator K 1 port side =
      endpointOperator K port (localEndpoint port 2 false true side)
```


`IdleOperators.lean:59`

```lean
theorem child2_source_operators (K : Type*) [Field K]
    (port : Fin 120) (side : Bool) :
    sourceBeforeOperator K 2 port side =
      endpointOperator K port (entranceEndpoint port side) ∧
    sourceAfterOperator K 2 port side =
      endpointOperator K port (localEndpoint port 3 true true side)
```


`IdleOperators.lean:71`

```lean
theorem child1_mask_difference (K : Type*) [Field K] (side : Bool)
    (v : Fin 64 → K) :
    afterMask 2 side v - afterMask 1 side v =
      coordinateMask (List.range' 15 7) v
```


`IdleOperators.lean:93`

```lean
theorem child2_mask_difference (K : Type*) [Field K] (side : Bool)
    (v : Fin 64 → K) :
    afterMask 3 side v - (if side then 0 else coordinateMask [0] v) =
      coordinateMask (List.range' 1 28) v
```


`IdleOperators.lean:110`

```lean
theorem child1_pending_chart (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) (side : Bool) (v : Fin 64 → K) :
    idlePendingOperator K 1 port side (PortGeometry.chart64 K h2 port v) =
      PortGeometry.chart64 K h2 port (coordinateMask (List.range' 15 7) v)
```


`IdleOperators.lean:122`

```lean
theorem child2_pending_chart (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) (side : Bool) (v : Fin 64 → K) :
    idlePendingOperator K 2 port side (PortGeometry.chart64 K h2 port v) =
      PortGeometry.chart64 K h2 port (coordinateMask (List.range' 1 28) v)
```


`IdleOperators.lean:136`

```lean
theorem idle_pending_child1 (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) (side : Bool) :
    idlePendingOperator K 1 port side = pendingOperator K h2 1 port
```


`IdleOperators.lean:145`

```lean
theorem idle_pending_child2 (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) (side : Bool) :
    idlePendingOperator K 2 port side = pendingOperator K h2 2 port
```


`IdleOperators.lean:157`

```lean
theorem idle_pending_operator (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (child : Nat) (hchild : child = 1 ∨ child = 2)
    (port : Fin 120) (side : Bool) :
    idlePendingOperator K child port side = pendingOperator K h2 child port
```


`IdleOperators.lean:167`

```lean
theorem source_before_sided_difference (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (child : Nat) (hchild : child = 1 ∨ child = 2) (port : Fin 120) :
    sourceBeforeOperator K child port false - sourceBeforeOperator K child port true =
      endpointOperator K port (entranceEndpoint port false)
```


`IdleOperators.lean:194`

```lean
theorem source_after_sided_difference (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (child : Nat) (hchild : child = 1 ∨ child = 2) (port : Fin 120) :
    sourceAfterOperator K child port false - sourceAfterOperator K child port true =
      endpointOperator K port (entranceEndpoint port false)
```


`IdleOperators.lean:224`

```lean
theorem idle_source_target_cancellation (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (child : Nat) (hchild : child = 1 ∨ child = 2) (port : Fin 120) :
    idlePendingOperator K child port false = idlePendingOperator K child port true
```
