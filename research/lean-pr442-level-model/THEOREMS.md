# Exact Phase 1 theorem statements

AI-written inventory extracted from the Lean sources. All declarations are in `PR442LevelModel`. This file is documentation; `Audit.lean` is the permanent axiom inventory.


`LevelSourceData.lean:34`

```lean
theorem sourceEntrance_bound : ∀ p : Port, sourceEntranceIds.getD p.val 0 < 944
```


`LevelSourceData.lean:40`

```lean
theorem targetEntrance_bound : ∀ p : Port, targetEntranceIds.getD p.val 0 < 944
```


`LevelSourceData.lean:46`

```lean
theorem sourceExit_bound : ∀ p : Port, sourceExitIds.getD p.val 0 < 944
```


`LevelSourceData.lean:52`

```lean
theorem targetExit_bound : ∀ p : Port, targetExitIds.getD p.val 0 < 944
```


`LevelSourceData.lean:58`

```lean
theorem oldSourceEntrance_bound : ∀ p : Port, oldSourceEntranceIds.getD p.val 0 < 944
```


`LevelSourceData.lean:64`

```lean
theorem oldTargetEntrance_bound : ∀ p : Port, oldTargetEntranceIds.getD p.val 0 < 944
```


`LevelSourceData.lean:70`

```lean
theorem oldSourceExit_bound : ∀ p : Port, oldSourceExitIds.getD p.val 0 < 944
```


`LevelSourceData.lean:76`

```lean
theorem oldTargetExit_bound : ∀ p : Port, oldTargetExitIds.getD p.val 0 < 944
```


`LevelFrameJoins.lean:19`

```lean
theorem old_roots_join : ∀ (p : Port) (i : LocalAxis),
    oldRootVector p i = rootVector p i
```


`LevelFrameJoins.lean:24`

```lean
theorem old_endpoint_labels_join : ∀ p : Port,
    oldSourceEntrance p = sourceEntrance p ∧
    oldTargetEntrance p = targetEntrance p ∧
    oldSourceExit p = sourceExit p ∧
    oldTargetExit p = targetExit p
```


`LevelFrameJoins.lean:31`

```lean
theorem invocation_endpoint_labels : ∀ p : Port,
    SourceFrameTrace.state0.frames.get p.val = (sourceEntrance p).val ∧
    SourceFrameTrace.state0.frames.get (120 + p.val) = (targetEntrance p).val ∧
    SourceFrameTrace.state96.frames.get p.val = (sourceExit p).val ∧
    SourceFrameTrace.state96.frames.get (120 + p.val) = (targetExit p).val
```


`LevelFrameJoins.lean:39`

```lean
theorem ownership_entrance_labels : ∀ p : Port,
    SourceOwnership.lookup SourceOwnership.initialFrameTable p.val =
      (sourceEntrance p).val ∧
    SourceOwnership.lookup SourceOwnership.initialFrameTable (120 + p.val) =
      (targetEntrance p).val
```


`LevelFrameJoins.lean:45`

```lean
theorem endpoint_label_values : ∀ p : Port,
    (sourceEntrance p).val = p.val + 2 ∧ targetEntrance p = 0 ∧
    sourceExit p = 1 ∧ (targetExit p).val = 824 + p.val
```


`LevelFrameJoins.lean:52`

```lean
theorem old_entrance_singleton : ∀ p : Port,
    oldEntranceLineLabels.getD p.val [] = [p.val]
```


`LevelFrameJoins.lean:55`

```lean
theorem entrance_basis_join : ∀ (p : Port) (i : LocalAxis),
    FrameGeometry.stack (sourceEntrance p) 0 i =
      ((oldEntranceBasisRows.getD p.val #[]).getD 0 #[]).getD i.val 0 ∧
    FrameGeometry.stack (sourceEntrance p) 0 i = rootVector p i
```


`LevelFrameJoins.lean:61`

```lean
theorem target_exit_basis_join : ∀ (p : Port) (r : Fin 7) (i : LocalAxis),
    FrameGeometry.stack (targetExit p) ⟨r.val, by omega⟩ i =
      ((oldTargetExitBasisRows.getD p.val #[]).getD r.val #[]).getD i.val 0
```


`LevelFrameJoins.lean:66`

```lean
theorem endpoint_dimensions : ∀ p : Port,
    (FrameGeometry.frame (sourceEntrance p)).dimension = 1 ∧
    (FrameGeometry.frame (targetEntrance p)).dimension = 0 ∧
    (FrameGeometry.frame (sourceExit p)).dimension = 8 ∧
    (FrameGeometry.frame (targetExit p)).dimension = 7
```


`LevelFrameJoins.lean:73`

```lean
theorem root_eq_basis : ∀ (p : Port) (i : LocalAxis),
    rootVector p i = PortGeometry.doubledBasis p i 0
```


`LevelFrameJoins.lean:77`

```lean
theorem entrance_scaled : ∀ (p : Port) (i j : LocalAxis),
    FrameGeometry.scaled (sourceEntrance p) i j = rootVector p i * rootVector p j
```


`LevelFrameJoins.lean:82`

```lean
theorem target_exit_scaled : ∀ (p : Port) (i j : LocalAxis),
    FrameGeometry.scaled (targetExit p) i j =
      (if i = j then 4 else 0) - rootVector p i * rootVector p j
```


`LevelFrameJoins.lean:89`

```lean
theorem route_root_block (p : Port) (i j : LocalAxis) :
    PortGeometry.quarteredRoute p ⟨i.val, by omega⟩ ⟨j.val, by omega⟩ =
      FrameGeometry.scaled (sourceEntrance p) i j
```


`LevelSchedule.lean:120`

```lean
theorem schedule_prefix_join : schedulePrefix.map eraseOrientation =
    PendingSchedule.schedule.take 10
```


`LevelSchedule.lean:125`

```lean
theorem route_axes_join : ∀ (p : Port) (stage : Fin 4),
    routeAxes p stage.val = List.range 8 ++
      (if stage.val = 0 then []
       else PendingSchedule.exteriorBlocks[stage.val - 1]!)
```


`LevelSchedule.lean:132`

```lean
theorem stage2_axis_positions : ∀ (p : Port) (i : Fin 15),
    (routeAxes p 2).getD i.val 64 =
      if i.val < 8 then i.val else i.val + 7
```


`LevelSchedule.lean:136`

```lean
theorem calls_match_schedule : ∀ c : Fin 4,
    Event.local (call c).stage (call c).pair (call c).reverse ∈ schedulePrefix
```


`LevelSchedule.lean:141`

```lean
theorem call_owner_alignment : ∀ (c : Fin 4) (side : Bool) (p : Port),
    let localSide := if (call c).reverse then !side else side
    let role := (if localSide then 120 else 0) + p.val
    (call c).ownerFamilies.getD role 0 =
      (2 * (call c).pair + if side then 1 else 0) * 120 + p.val ∧
    (call c).ownerRouteStages.getD role 0 = (call c).stage ∧
    (call c).ownerRoutePorts.getD role 0 = p.val
```


`LevelSchedule.lean:150`

```lean
theorem child1_provenance : observation 1 = some
    ⟨1, 1, 7, 2, 3, .localExit 1 true, .localExit 2 false⟩
```


`LevelSchedule.lean:153`

```lean
theorem child2_provenance : observation 2 = some
    ⟨2, 2, 28, 0, 4, .entrance, .localExit 3 true⟩
```


`LevelSchedule.lean:158`

```lean
theorem recorded_levels_and_ranks : ∀ (idx : Fin 3) (p : Port) (side : Bool),
    match observation idx.val with
    | none => False
    | some o => o.recordedSource = levelTag o.before ∧
        o.recordedTarget = levelTag o.after ∧
        descriptorDimension (endpoint p side o.before) + o.rank =
          descriptorDimension (endpoint p side o.after)
```


`LevelSchedule.lean:179`

```lean
theorem child1_endpoints (p : Port) (side : Bool) :
    sourceBefore 1 p side = some (localEndpoint p 1 true true side) ∧
    sourceAfter 1 p side = some (localEndpoint p 2 false true side)
```


`LevelSchedule.lean:184`

```lean
theorem child2_endpoints (p : Port) (side : Bool) :
    sourceBefore 2 p side = some (entranceEndpoint p side) ∧
    sourceAfter 2 p side = some (localEndpoint p 3 true true side)
```


`LevelSchedule.lean:191`

```lean
theorem selected_invocation_inside_windows :
    PendingSchedule.selectedStage = 2 ∧
    (replay (schedulePrefix.take 4) initialOrigins []).map (fun s => s.1[1]?) =
      some (some (.localExit 1 true)) ∧
    (replay (schedulePrefix.take 5) initialOrigins []).map (fun s => s.1[1]?) =
      some (some (.localExit 1 true)) ∧
    (replay (schedulePrefix.take 4) initialOrigins []).map (fun s => s.1[2]?) =
      some (some .entrance) ∧
    (replay (schedulePrefix.take 5) initialOrigins []).map (fun s => s.1[2]?) =
      some (some .entrance)
```


`BaseLevel.lean:30`

```lean
theorem source_entrance_projector_entry (port : Fin 120) (i j : Fin 8) :
    FrameGeometry.projector ℚ (sourceEntrance port) i j =
      q port i * q port j / 4
```


`BaseLevel.lean:40`

```lean
theorem source_entrance_projector (port : Fin 120) :
    FrameGeometry.projector ℚ (sourceEntrance port) = rootProjector port
```


`BaseLevel.lean:47`

```lean
theorem root_square_sum (port : Fin 120) :
    (∑ i : Fin 8, q port i * q port i) = 4
```


`BaseLevel.lean:56`

```lean
theorem source_entrance_mulVec (port : Fin 120) (v : Fin 8 → ℚ) :
    FrameGeometry.projector ℚ (sourceEntrance port) *ᵥ v =
      ((q port ⬝ᵥ v) / 4) • q port
```


`BaseLevel.lean:77`

```lean
theorem source_entrance_fixes_root (port : Fin 120) :
    FrameGeometry.projector ℚ (sourceEntrance port) *ᵥ q port = q port
```


`BaseLevel.lean:86`

```lean
theorem source_entrance_range (port : Fin 120) :
    Set.range (fun v : Fin 8 → ℚ =>
      FrameGeometry.projector ℚ (sourceEntrance port) *ᵥ v) =
    (Submodule.span ℚ ({q port} : Set (Fin 8 → ℚ)) : Set (Fin 8 → ℚ))
```
