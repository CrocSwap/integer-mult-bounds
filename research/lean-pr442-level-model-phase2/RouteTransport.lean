import FieldEntrance
import LevelSchedule

/-!
Literal local frame operators are complemented in eight dimensions before
extension by their source-listed exterior axes. Routes use the source rho15
certificate on the source-listed fifteen axes. No pending mask defines an
endpoint in this module.

Apache-2.0. Prepared with substantial AI assistance.
-/
namespace PR442LevelModel.Phase2
open scoped Matrix BigOperators

def coordinateMask {K : Type*} [Zero K] (axes : List Nat) (v : Fin 64 → K) : Fin 64 → K :=
  fun i => if axes.contains i.val then v i else 0

/-- Local reflection is performed before exterior extension. -/
def localProjector (K : Type*) [Field K] (e : Endpoint) : Matrix (Fin 8) (Fin 8) K :=
  if e.complemented then 1 - FrameGeometry.projector K e.frame
  else FrameGeometry.projector K e.frame

/-- The source frame plus its literal exterior axes, with zero elsewhere. -/
def liftedOperator (K : Type*) [Field K] (e : Endpoint) (v : Fin 64 → K) : Fin 64 → K :=
  fun i => if hi : i.val < 8 then
    (localProjector K e *ᵥ PortGeometry.firstEight v) ⟨i.val, hi⟩
  else if e.exterior.contains i.val then v i else 0

def gatherAxes {K : Type*} (axes : List Nat) (v : Fin 64 → K) (j : Fin 15) : K :=
  v ⟨axes.getD j.val 0 % 64, Nat.mod_lt _ (by decide)⟩

/-- Interpret the literal rho15 on the literal route axes. The stage-zero
source route has only the eight local axes and is the identity. -/
def axisRoute (K : Type*) [Field K] (p : Port) (axes : List Nat)
    (v : Fin 64 → K) (i : Fin 64) : K :=
  if axes.length = 8 then v i
  else if h : axes.idxOf i.val < 15 then
    (PortGeometry.route15 K p *ᵥ gatherAxes axes v) ⟨axes.idxOf i.val, h⟩
  else v i

/-- Ambient interpretation of an independently reconstructed endpoint. -/
def endpointOperator (K : Type*) [Field K] (p : Port) (e : Endpoint)
    (v : Fin 64 → K) : Fin 64 → K :=
  axisRoute K p e.axes (liftedOperator K e (axisRoute K p e.axes v))

theorem localEndpoint_axes (p : Port) (stage : Nat) (reverse after side : Bool) :
    (localEndpoint p stage reverse after side).axes = routeAxes p stage := by
  simp only [localEndpoint]

theorem localEndpoint_exterior (p : Port) (stage : Nat) (reverse after side : Bool) :
    (localEndpoint p stage reverse after side).exterior = exteriorAxes p stage := rfl

theorem entranceEndpoint_axes (p : Port) (side : Bool) :
    (entranceEndpoint p side).axes = routeAxes p 0 := by
  simp only [entranceEndpoint]

def blockStart (s : Fin 3) : Nat := 8 + 7 * s.val

def blockAxes (s : Fin 3) : List Nat := List.range 8 ++ List.range' (blockStart s) 7

def relocationIndex (s : Fin 3) (i : Fin 64) : Fin 64 :=
  if blockStart s = 15 then i
  else if h : blockStart s ≤ i.val ∧ i.val < blockStart s + 7 then
    ⟨i.val + 15 - blockStart s, by unfold blockStart at *; omega⟩
  else if h : 15 ≤ i.val ∧ i.val < 22 then
    ⟨i.val + blockStart s - 15, by unfold blockStart at *; omega⟩
  else i

theorem relocationIndex_involutive (s : Fin 3) : Function.Involutive (relocationIndex s) := by
  change ∀ i : Fin 64, relocationIndex s (relocationIndex s i) = i
  revert s
  decide +kernel

def relocate {K : Type*} (s : Fin 3) (v : Fin 64 → K) : Fin 64 → K :=
  v ∘ relocationIndex s

theorem relocate_involutive {K : Type*} (s : Fin 3) (v : Fin 64 → K) :
    relocate s (relocate s v) = v := by
  funext i
  exact congrArg v (relocationIndex_involutive s i)

theorem relocation_local (s : Fin 3) (j : Fin 8) :
    relocationIndex s (Fin.castAdd 56 j) = Fin.castAdd 56 j := by
  revert s j
  decide +kernel

theorem relocation_gather_index (s : Fin 3) (j : Fin 15) :
    (⟨(blockAxes s).getD j.val 0 % 64, Nat.mod_lt _ (by decide)⟩ : Fin 64) =
      relocationIndex s (if h : j.val < 8 then ⟨j.val, by omega⟩
        else ⟨j.val + 7, by omega⟩) := by
  revert s j
  decide +kernel

theorem gather_blockAxes {K : Type*} (s : Fin 3) (v : Fin 64 → K) :
    gatherAxes (blockAxes s) v = PortGeometry.gatherStage2 (relocate s v) := by
  funext j
  unfold gatherAxes PortGeometry.gatherStage2 relocate
  rw [relocation_gather_index]
  by_cases hj : j.val < 8 <;> simp [hj]

theorem blockAxes_length (s : Fin 3) : (blockAxes s).length = 15 := by
  simp [blockAxes]

theorem blockAxes_index (s : Fin 3) (i : Fin 64) :
    (blockAxes s).idxOf i.val =
      if i.val < 8 then i.val
      else if blockStart s ≤ i.val ∧ i.val < blockStart s + 7 then
        i.val - blockStart s + 8 else 15 := by
  revert s i
  decide +kernel

theorem relocation_cases (s : Fin 3) (i : Fin 64) :
    (relocationIndex s i).val =
      if i.val < 8 then i.val
      else if blockStart s ≤ i.val ∧ i.val < blockStart s + 7 then
        i.val - blockStart s + 15
      else if 15 ≤ i.val ∧ i.val < 22 then i.val - 15 + blockStart s
      else i.val := by
  revert s i
  decide +kernel

/-- Reuse the proved literal source route by relocation. -/
theorem axisRoute_blockAxes (K : Type*) [Field K] (p : Port) (s : Fin 3)
    (v : Fin 64 → K) :
    axisRoute K p (blockAxes s) v =
      relocate s (PortGeometry.sourceRoute64 K p (relocate s v)) := by
  funext i
  simp only [axisRoute, blockAxes_length, show ¬(15 = 8) by decide, if_false,
    blockAxes_index, gather_blockAxes, relocate, Function.comp_apply]
  by_cases hi : i.val < 8
  · have hr : (relocationIndex s i).val = i.val := by simp [relocation_cases, hi]
    have ha : i.val < 15 := by omega
    simp [hi, ha, PortGeometry.sourceRoute64, hr]
  · by_cases hb : blockStart s ≤ i.val ∧ i.val < blockStart s + 7
    · have hr : (relocationIndex s i).val = i.val - blockStart s + 15 := by
        simp [relocation_cases, hi, hb]
      have ha : i.val - blockStart s + 8 < 15 := by omega
      have hri : ¬ (relocationIndex s i).val < 8 := by rw [hr]; omega
      have hrb : 15 ≤ (relocationIndex s i).val ∧ (relocationIndex s i).val < 22 := by
        rw [hr]; omega
      have heq : (relocationIndex s i).val - 7 = i.val - blockStart s + 8 := by
        rw [hr]; omega
      simp [hi, hb, ha, PortGeometry.sourceRoute64, hri, hrb, heq]
    · have hri : ¬ (relocationIndex s i).val < 8 := by
        rw [relocation_cases]
        split_ifs <;> unfold blockStart at * <;> omega
      have hrb : ¬(15 ≤ (relocationIndex s i).val ∧ (relocationIndex s i).val < 22) := by
        rw [relocation_cases]
        split_ifs <;> unfold blockStart at * <;> omega
      simp [hi, hb, PortGeometry.sourceRoute64, hri, hrb,
        relocationIndex_involutive s i]



/-- The source route's coordinate permutation, after relocation. -/
def stageIndex (s : Fin 3) (i : Fin 64) : Fin 64 :=
  relocationIndex s (PortGeometry.stage2Index (relocationIndex s i))

def stageCoordinates {K : Type*} (s : Fin 3) (v : Fin 64 → K) : Fin 64 → K :=
  v ∘ stageIndex s

theorem stageIndex_involutive (s : Fin 3) : Function.Involutive (stageIndex s) := by
  change ∀ i : Fin 64, stageIndex s (stageIndex s i) = i
  revert s
  decide +kernel

theorem stageCoordinates_involutive {K : Type*} (s : Fin 3) (v : Fin 64 → K) :
    stageCoordinates s (stageCoordinates s v) = v := by
  funext i
  exact congrArg v (stageIndex_involutive s i)

theorem relocation_region (s : Fin 3) (i : Fin 64) :
    (relocationIndex s i).val < 8 ↔ i.val < 8 := by
  revert s i
  decide +kernel

theorem relocate_firstEight {K : Type*} (s : Fin 3) (v : Fin 64 → K) :
    PortGeometry.firstEight (relocate s v) = PortGeometry.firstEight v := by
  funext j
  exact congrArg v (relocation_local s j)

theorem relocate_chart (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (s : Fin 3) (v : Fin 64 → K) :
    relocate s (PortGeometry.chart64 K h2 p v) =
      PortGeometry.chart64 K h2 p (relocate s v) := by
  funext i
  by_cases hi : i.val < 8
  · have hr : (relocationIndex s i).val = i.val := by simp [relocation_cases, hi]
    have he : relocationIndex s i = i := Fin.ext hr
    change PortGeometry.chart64 K h2 p v (relocationIndex s i) =
      PortGeometry.chart64 K h2 p (relocate s v) i
    rw [he]
    change PortGeometry.extendEight (PortGeometry.chart8 K h2 p) v i =
      PortGeometry.extendEight (PortGeometry.chart8 K h2 p) (relocate s v) i
    simp only [PortGeometry.extendEight, hi, dif_pos]
    rw [relocate_firstEight]
  · have hr : 8 ≤ (relocationIndex s i).val := by
      exact Nat.le_of_not_lt (fun h => hi ((relocation_region s i).mp h))
    rw [PortGeometry.chart64_outside K h2 p _ i (Nat.le_of_not_lt hi)]
    exact PortGeometry.chart64_outside K h2 p v _ hr

theorem axisRoute_blockAxes_chart (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (s : Fin 3) (v : Fin 64 → K) :
    axisRoute K p (blockAxes s) (PortGeometry.chart64 K h2 p v) =
      PortGeometry.chart64 K h2 p (stageCoordinates s v) := by
  rw [axisRoute_blockAxes, relocate_chart, PortGeometry.sourceRoute64_eq K h2]
  change relocate s (PortGeometry.chart64 K h2 p
    (PortGeometry.stage2Coordinates ((PortGeometry.chart64 K h2 p).symm
      (PortGeometry.chart64 K h2 p (relocate s v))))) = _
  rw [Equiv.symm_apply_apply, relocate_chart]
  rfl

theorem exterior_block_shapes (s : Fin 3) :
    PendingSchedule.exteriorBlocks[s.val]! = List.range' (blockStart s) 7 := by
  revert s
  decide +kernel

theorem route_axes_zero (p : Port) : routeAxes p 0 = List.range 8 := by
  simpa using route_axes_join p 0

theorem route_axes_positive (p : Port) (s : Fin 3) :
    routeAxes p (s.val + 1) = blockAxes s := by
  have h := route_axes_join p s.succ
  simp only [Fin.val_succ, Nat.add_eq_zero_iff, Nat.one_ne_zero, and_false,
    if_false, Nat.add_sub_cancel] at h
  rw [exterior_block_shapes] at h
  exact h

theorem exterior_axes_contains (p : Port) (stage : Fin 4) (i : Fin 64) :
    (exteriorAxes p stage.val).contains i.val =
      decide (8 ≤ i.val ∧ i.val < 8 + 7 * stage.val) := by
  have hs : ∀ t : Fin 4, routeAxes p t.val =
      List.range 8 ++ if t.val = 0 then []
        else List.range' (8 + 7 * (t.val - 1)) 7 := by
    intro t
    refine Fin.cases ?_ ?_ t
    · simp [route_axes_zero]
    · intro t
      simp [route_axes_positive, blockAxes, blockStart]
  revert stage i
  intro stage i
  unfold exteriorAxes
  have hh : (List.range (stage.val + 1)).flatMap (fun t => (routeAxes p t).drop 8) =
      (List.range (stage.val + 1)).flatMap (fun t =>
        (List.range 8 ++ if t = 0 then [] else List.range' (8 + 7 * (t - 1)) 7).drop 8) := by
    apply List.flatMap_congr
    intro t ht
    have ht4 : t < 4 := by have := List.mem_range.mp ht; omega
    rw [hs ⟨t, ht4⟩]
  rw [hh]
  clear hh hs p
  revert stage i
  decide +kernel

/-- A comparison formula, derived from the literal descriptors rather than
used to define them. The physical target lacks the common root axis. -/
def afterMask {K : Type*} [Sub K] [Zero K] (stage : Nat) (side : Bool)
    (v : Fin 64 → K) : Fin 64 → K :=
  coordinateMask (List.range (8 + 7 * stage)) v -
    if side then coordinateMask [0] v else 0



def rootMask8 {K : Type*} [Zero K] (v : Fin 8 → K) : Fin 8 → K :=
  fun i => if i = 0 then v i else 0

theorem local_after_projector (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (stage : Nat) (reverse side : Bool) :
    localProjector K (localEndpoint p stage reverse true side) =
      if side then 1 - rootProjector K p else 1 := by
  cases reverse <;> cases side <;>
    simp [localProjector, localEndpoint, source_entrance_projector,
      target_entrance_projector, source_exit_projector K h2,
      target_exit_projector K h2]

theorem local_after_mulVec (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (stage : Nat) (reverse side : Bool) (v : Fin 8 → K) :
    localProjector K (localEndpoint p stage reverse true side) *ᵥ
        (PortGeometry.basis K p *ᵥ v) =
      PortGeometry.basis K p *ᵥ (v - if side then rootMask8 v else 0) := by
  rw [local_after_projector K h2]
  cases side
  · simp
  · simp only [Bool.true_eq, if_true, Matrix.sub_mulVec, Matrix.one_mulVec,
      root_chart_mulVec K h2, rootMask8, Matrix.mulVec_sub]
    rfl

theorem afterMask_firstEight (K : Type*) [Field K] (stage : Nat)
    (side : Bool) (v : Fin 64 → K) :
    PortGeometry.firstEight (afterMask stage side v) =
      PortGeometry.firstEight v -
        if side then rootMask8 (PortGeometry.firstEight v) else 0 := by
  funext j
  have hj : j.val < 8 + 7 * stage := by omega
  have hz : j.val = 0 ↔ j = 0 := by
    constructor
    · intro h; exact Fin.ext h
    · intro h; rw [h]; rfl
  cases side <;>
    simp [PortGeometry.firstEight, afterMask, coordinateMask, rootMask8,
      List.contains_iff_mem, List.mem_range, hj, hz]

theorem afterMask_outside (K : Type*) [Field K] (p : Port)
    (stage : Fin 4) (side : Bool) (v : Fin 64 → K) (i : Fin 64) (hi : 8 ≤ i.val) :
    afterMask stage.val side v i =
      if (exteriorAxes p stage.val).contains i.val then v i else 0 := by
  have hz : i.val ≠ 0 := by omega
  rw [exterior_axes_contains]
  cases side <;>
    simp [afterMask, coordinateMask, List.contains_iff_mem, List.mem_range,
      hz, hi]

theorem chart64_inside (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (v : Fin 64 → K) (i : Fin 64) (hi : i.val < 8) :
    PortGeometry.chart64 K h2 p v i =
      (PortGeometry.basis K p *ᵥ PortGeometry.firstEight v) ⟨i.val, hi⟩ := by
  have h := congrFun (PortGeometry.chart64_firstEight K h2 p v) ⟨i.val, hi⟩
  change PortGeometry.chart64 K h2 p v (Fin.castAdd 56 ⟨i.val, hi⟩) = _ at h
  have he : Fin.castAdd 56 ⟨i.val, hi⟩ = i := Fin.ext rfl
  rw [he] at h
  exact h

/-- Each side has its own projector. The common root discrepancy is
retained explicitly in the comparison formula. -/
theorem lifted_local_after_chart (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (stage : Fin 4) (reverse side : Bool) (v : Fin 64 → K) :
    liftedOperator K (localEndpoint p stage.val reverse true side)
        (PortGeometry.chart64 K h2 p v) =
      PortGeometry.chart64 K h2 p (afterMask stage.val side v) := by
  funext i
  by_cases hi : i.val < 8
  · rw [chart64_inside K h2 p (afterMask stage.val side v) i hi]
    simp only [liftedOperator, hi, dif_pos, PortGeometry.chart64_firstEight,
      local_after_mulVec K h2, afterMask_firstEight]
  · rw [PortGeometry.chart64_outside K h2 p _ i (Nat.le_of_not_lt hi)]
    rw [afterMask_outside K p stage side v i (Nat.le_of_not_lt hi)]
    simp only [liftedOperator, dif_neg hi, localEndpoint_exterior]
    rw [PortGeometry.chart64_outside K h2 p _ i (Nat.le_of_not_lt hi)]

theorem stageIndex_after_region (s : Fin 3) (i : Fin 64) :
    (stageIndex s i).val < 8 + 7 * (s.val + 1) ↔
      i.val < 8 + 7 * (s.val + 1) := by
  revert s i
  decide +kernel

theorem stageIndex_root (s : Fin 3) (i : Fin 64) :
    (stageIndex s i).val = 0 ↔ i.val = 0 := by
  revert s i
  decide +kernel

theorem stageIndex_zero (s : Fin 3) (i : Fin 64) :
    stageIndex s i = 0 ↔ i = 0 := by
  revert s i
  decide +kernel

theorem stageCoordinates_afterMask (K : Type*) [Field K] (s : Fin 3)
    (side : Bool) (v : Fin 64 → K) :
    stageCoordinates s (afterMask (s.val + 1) side v) =
      afterMask (s.val + 1) side (stageCoordinates s v) := by
  funext i
  cases side <;>
    simp [stageCoordinates, Function.comp_apply, afterMask, coordinateMask,
      List.contains_iff_mem, List.mem_range, stageIndex_after_region, stageIndex_root, stageIndex_zero]

theorem axisRoute_zero (K : Type*) [Field K] (p : Port) (v : Fin 64 → K) :
    axisRoute K p (List.range 8) v = v := by
  funext i
  simp [axisRoute]

/-- Exact ambient transport of every independently reconstructed local exit
through stages zero to three, for both call orientations and both sides. -/
theorem local_endpoint_after (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (stage : Fin 4) (reverse side : Bool) (v : Fin 64 → K) :
    endpointOperator K p (localEndpoint p stage.val reverse true side)
        (PortGeometry.chart64 K h2 p v) =
      PortGeometry.chart64 K h2 p (afterMask stage.val side v) := by
  simp only [endpointOperator, localEndpoint_axes]
  revert stage
  refine Fin.cases ?_ ?_
  · simp only [Fin.val_zero, route_axes_zero, axisRoute_zero]
    exact lifted_local_after_chart K h2 p 0 reverse side v
  · intro s
    simp only [Fin.val_succ]
    have hl := lifted_local_after_chart K h2 p s.succ reverse side
      (stageCoordinates s v)
    simp only [Fin.val_succ] at hl
    rw [route_axes_positive, axisRoute_blockAxes_chart K h2,
      hl,
      axisRoute_blockAxes_chart K h2,
      stageCoordinates_afterMask, stageCoordinates_involutive]

/-- The physical entrance source is the root line; the entrance target is
zero. This formula is proved from the literal entrance frame IDs. -/
def entranceMask {K : Type*} [Zero K] (side : Bool) (v : Fin 64 → K) : Fin 64 → K :=
  if side then 0 else coordinateMask [0] v

theorem entranceMask_firstEight (K : Type*) [Field K] (side : Bool) (v : Fin 64 → K) :
    PortGeometry.firstEight (entranceMask side v) =
      if side then 0 else rootMask8 (PortGeometry.firstEight v) := by
  funext j
  have hz : j.val = 0 ↔ j = 0 := by
    constructor
    · intro h; exact Fin.ext h
    · intro h; rw [h]; rfl
  cases side <;>
    simp [PortGeometry.firstEight, entranceMask, coordinateMask, rootMask8,
      List.contains_iff_mem, hz]

theorem entrance_endpoint (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (side : Bool) (v : Fin 64 → K) :
    endpointOperator K p (entranceEndpoint p side) (PortGeometry.chart64 K h2 p v) =
      PortGeometry.chart64 K h2 p (entranceMask side v) := by
  simp only [endpointOperator, entranceEndpoint_axes]
  simp only [route_axes_zero, axisRoute_zero]
  funext i
  by_cases hi : i.val < 8
  · rw [chart64_inside K h2 p (entranceMask side v) i hi]
    simp only [liftedOperator, hi, dif_pos, PortGeometry.chart64_firstEight]
    cases side <;>
      simp only [entranceEndpoint, localProjector, Bool.false_eq_true, Bool.true_eq,
        if_false, if_true,
        source_entrance_projector, target_entrance_projector, Matrix.zero_mulVec,
        root_chart_mulVec K h2]
    all_goals rw [entranceMask_firstEight]
    all_goals simp [rootMask8]
    all_goals rfl
  · have hz : i.val ≠ 0 := by omega
    rw [PortGeometry.chart64_outside K h2 p _ i (Nat.le_of_not_lt hi)]
    cases side <;>
      simp [liftedOperator, entranceEndpoint, hi, entranceMask, coordinateMask, hz]



/-- Stage two is exactly the existing source rho15 on axes 0..7,15..21. -/
theorem stage2_literal_route (K : Type*) [Field K] (p : Port) (v : Fin 64 → K) :
    axisRoute K p (routeAxes p 2) v = PortGeometry.sourceRoute64 K p v := by
  have h := route_axes_positive p (1 : Fin 3)
  change routeAxes p 2 = blockAxes 1 at h
  rw [h, axisRoute_blockAxes]
  have hr : relocationIndex (1 : Fin 3) = id := by
    funext i
    rfl
  simp [relocate, hr]

/-- The two uses of a route in an endpoint interpretation are forward and
inverse because the source-certified operator is involutive. -/
theorem axisRoute_blockAxes_involutive (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (s : Fin 3) : Function.Involutive (axisRoute K p (blockAxes s)) := by
  intro v
  have h := axisRoute_blockAxes_chart K h2 p s ((PortGeometry.chart64 K h2 p).symm v)
  rw [Equiv.apply_symm_apply] at h
  rw [h, axisRoute_blockAxes_chart K h2, stageCoordinates_involutive,
    Equiv.apply_symm_apply]



def stagePermutation (s : Fin 3) : Equiv.Perm (Fin 64) where
  toFun := stageIndex s
  invFun := stageIndex s
  left_inv := stageIndex_involutive s
  right_inv := stageIndex_involutive s

theorem stageCoordinates_dot (K : Type*) [Field K] (s : Fin 3)
    (v w : Fin 64 → K) :
    (∑ i, stageCoordinates s v i * stageCoordinates s w i) = ∑ i, v i * w i :=
  Fintype.sum_equiv (stagePermutation s) _ _ (fun _ => rfl)

/-- Every needed literal route preserves the ambient dot form over any
field in which two is nonzero. -/
theorem axisRoute_blockAxes_dot (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (p : Port) (s : Fin 3) (v w : Fin 64 → K) :
    (∑ i, axisRoute K p (blockAxes s) v i * axisRoute K p (blockAxes s) w i) =
      ∑ i, v i * w i := by
  have hv := axisRoute_blockAxes_chart K h2 p s ((PortGeometry.chart64 K h2 p).symm v)
  have hw := axisRoute_blockAxes_chart K h2 p s ((PortGeometry.chart64 K h2 p).symm w)
  rw [Equiv.apply_symm_apply] at hv hw
  rw [hv, hw, PortGeometry.chart64_dot, stageCoordinates_dot,
    PortGeometry.chart64_symm_dot]



/-- The literal rho15 upper-left block is the independently joined source
entrance projector, with the route's denominator four preserved exactly. -/
theorem route15_entrance_block (K : Type*) [Field K] (p : Port) (i j : Fin 8) :
    PortGeometry.route15 K p ⟨i.val, by omega⟩ ⟨j.val, by omega⟩ =
      FrameGeometry.projector K (sourceEntrance p) i j := by
  simp only [PortGeometry.route15, FrameGeometry.projector, Matrix.smul_apply,
    FrameGeometry.castMatrix, Matrix.map_apply, FrameGeometry.scaledMatrix,
    Matrix.of_apply, smul_eq_mul]
  rw [route_root_block]
  simp only [div_eq_mul_inv, mul_comm]
  rfl

end PR442LevelModel.Phase2
