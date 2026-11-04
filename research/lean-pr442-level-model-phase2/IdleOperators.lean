import RouteTransport
import PendingDerivation

/-!
Ambient interpretation of Phase 1's independently reconstructed descriptors.
The pending axes are read only by the comparison operator. The input operators
come from the literal endpoint frames, local orientation, routes and exterior
axes, whose provenance is joined in the unchanged Phase 1 dependency.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
-/
namespace PR442LevelModel.Phase2
open scoped Matrix BigOperators

/-- Interpret the reconstructed source-before descriptor; the zero fallback
is irrelevant for children 1 and 2, whose existence is proved in Phase 1. -/
def sourceBeforeOperator (K : Type*) [Field K] (child : Nat)
    (port : Fin 120) (side : Bool) : (Fin 64 → K) → (Fin 64 → K) :=
  ((sourceBefore child port side).map (endpointOperator K port)).getD 0

/-- Interpret the independently reconstructed source-after descriptor. -/
def sourceAfterOperator (K : Type*) [Field K] (child : Nat)
    (port : Fin 120) (side : Bool) : (Fin 64 → K) → (Fin 64 → K) :=
  ((sourceAfter child port side).map (endpointOperator K port)).getD 0

/-- The physical pending operator is the difference of actual endpoint
projectors. Its definition does not use the coordinate level model. -/
def idlePendingOperator (K : Type*) [Field K] (child : Nat)
    (port : Fin 120) (side : Bool) : (Fin 64 → K) → (Fin 64 → K) :=
  sourceAfterOperator K child port side - sourceBeforeOperator K child port side

/-- Coordinate comparison target from PR1231; no endpoint is defined from it. -/
def pendingOperator (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (child : Nat) (port : Fin 120) (v : Fin 64 → K) : Fin 64 → K :=
  PortGeometry.chart64 K h2 port
    (fun i => if (PendingDerivation.pendingAxes child).contains i.val then
      (PortGeometry.chart64 K h2 port).symm v i else 0)

theorem chart64_sub (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) (v w : Fin 64 → K) :
    PortGeometry.chart64 K h2 port (v - w) =
      PortGeometry.chart64 K h2 port v - PortGeometry.chart64 K h2 port w := by
  have hn : PortGeometry.chart64 K h2 port (-w) =
      -PortGeometry.chart64 K h2 port w := by
    simpa only [neg_one_smul] using PortGeometry.chart64_smul K h2 port (-1) w
  rw [sub_eq_add_neg, PortGeometry.chart64_add, hn, ← sub_eq_add_neg]

/-- The operator interpretation retains the two literal child-1 endpoint
provenances checked in Phase 1. -/
theorem child1_source_operators (K : Type*) [Field K]
    (port : Fin 120) (side : Bool) :
    sourceBeforeOperator K 1 port side =
      endpointOperator K port (localEndpoint port 1 true true side) ∧
    sourceAfterOperator K 1 port side =
      endpointOperator K port (localEndpoint port 2 false true side) := by
  constructor <;> simp only [sourceBeforeOperator, sourceAfterOperator,
    (child1_endpoints port side).1, (child1_endpoints port side).2,
    Option.map_some, Option.getD_some]

theorem child2_source_operators (K : Type*) [Field K]
    (port : Fin 120) (side : Bool) :
    sourceBeforeOperator K 2 port side =
      endpointOperator K port (entranceEndpoint port side) ∧
    sourceAfterOperator K 2 port side =
      endpointOperator K port (localEndpoint port 3 true true side) := by
  constructor <;> simp only [sourceBeforeOperator, sourceAfterOperator,
    (child2_endpoints port side).1, (child2_endpoints port side).2,
    Option.map_some, Option.getD_some]

/-- The target-side root correction cancels between the two child-1
endpoint projectors; the source side is checked by the same entry identity. -/
theorem child1_mask_difference (K : Type*) [Field K] (side : Bool)
    (v : Fin 64 → K) :
    afterMask 2 side v - afterMask 1 side v =
      coordinateMask (List.range' 15 7) v := by
  funext i
  have hc : afterMask 2 side v i - afterMask 1 side v i =
      coordinateMask (List.range 22) v i - coordinateMask (List.range 15) v i := by
    cases side <;> simp [afterMask]
  change afterMask 2 side v i - afterMask 1 side v i = _
  rw [hc]
  by_cases h15 : i.val < 15
  · have h22 : i.val < 22 := by omega
    have hn15 : ¬15 ≤ i.val := by omega
    simp [coordinateMask, List.contains_iff_mem, List.mem_range, List.mem_range'_1,
      h15, h22, hn15]
  · have hge15 : 15 ≤ i.val := by omega
    by_cases h22 : i.val < 22 <;>
      simp [coordinateMask, List.contains_iff_mem, List.mem_range, List.mem_range'_1,
        h15, h22, hge15]

/-- For child 2, subtracting the sided literal entrance yields the same
root-complement plus exterior projector on both sides. -/
theorem child2_mask_difference (K : Type*) [Field K] (side : Bool)
    (v : Fin 64 → K) :
    afterMask 3 side v - (if side then 0 else coordinateMask [0] v) =
      coordinateMask (List.range' 1 28) v := by
  funext i
  have hc : (afterMask 3 side v -
      (if side then 0 else coordinateMask [0] v)) i =
      coordinateMask (List.range 29) v i - coordinateMask [0] v i := by
    cases side <;> simp [afterMask]
  rw [hc]
  by_cases h0 : i.val = 0
  · simp [coordinateMask, List.contains_iff_mem, List.mem_range, List.mem_range'_1, h0]
  · have hge1 : 1 ≤ i.val := by omega
    by_cases h29 : i.val < 29 <;>
      simp [coordinateMask, List.contains_iff_mem, List.mem_range, List.mem_range'_1,
        h0, h29, hge1]

theorem child1_pending_chart (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) (side : Bool) (v : Fin 64 → K) :
    idlePendingOperator K 1 port side (PortGeometry.chart64 K h2 port v) =
      PortGeometry.chart64 K h2 port (coordinateMask (List.range' 15 7) v) := by
  change sourceAfterOperator K 1 port side (PortGeometry.chart64 K h2 port v) -
    sourceBeforeOperator K 1 port side (PortGeometry.chart64 K h2 port v) = _
  rw [(child1_source_operators K port side).2,
    (child1_source_operators K port side).1,
    local_endpoint_after K h2 port (⟨2, by decide⟩ : Fin 4) false side v,
    local_endpoint_after K h2 port (⟨1, by decide⟩ : Fin 4) true side v]
  rw [← chart64_sub, child1_mask_difference]

theorem child2_pending_chart (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) (side : Bool) (v : Fin 64 → K) :
    idlePendingOperator K 2 port side (PortGeometry.chart64 K h2 port v) =
      PortGeometry.chart64 K h2 port (coordinateMask (List.range' 1 28) v) := by
  change sourceAfterOperator K 2 port side (PortGeometry.chart64 K h2 port v) -
    sourceBeforeOperator K 2 port side (PortGeometry.chart64 K h2 port v) = _
  rw [(child2_source_operators K port side).2,
    (child2_source_operators K port side).1,
    local_endpoint_after K h2 port (⟨3, by decide⟩ : Fin 4) true side v,
    entrance_endpoint K h2 port side v]
  rw [← chart64_sub]
  simp only [entranceMask]
  rw [child2_mask_difference]

theorem idle_pending_child1 (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) (side : Bool) :
    idlePendingOperator K 1 port side = pendingOperator K h2 1 port := by
  funext v
  obtain ⟨w, rfl⟩ := (PortGeometry.chart64 K h2 port).surjective v
  rw [child1_pending_chart]
  simp only [pendingOperator, PendingDerivation.pending_child1, Equiv.symm_apply_apply]
  rfl

theorem idle_pending_child2 (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) (side : Bool) :
    idlePendingOperator K 2 port side = pendingOperator K h2 2 port := by
  funext v
  obtain ⟨w, rfl⟩ := (PortGeometry.chart64 K h2 port).surjective v
  rw [child2_pending_chart]
  simp only [pendingOperator, PendingDerivation.pending_child2, Equiv.symm_apply_apply]
  rfl

/-- For exactly the two children used by PR540, the independently recovered
physical projector difference equals the PR1231 pending-coordinate operator,
on every input vector, in every field where two is nonzero. -/
theorem idle_pending_operator (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (child : Nat) (hchild : child = 1 ∨ child = 2)
    (port : Fin 120) (side : Bool) :
    idlePendingOperator K child port side = pendingOperator K h2 child port := by
  rcases hchild with rfl | rfl
  · exact idle_pending_child1 K h2 port side
  · exact idle_pending_child2 K h2 port side

/-- The source and target projectors retain their common literal-root
separation at each reconstructed before endpoint. -/
theorem source_before_sided_difference (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (child : Nat) (hchild : child = 1 ∨ child = 2) (port : Fin 120) :
    sourceBeforeOperator K child port false - sourceBeforeOperator K child port true =
      endpointOperator K port (entranceEndpoint port false) := by
  funext v
  obtain ⟨w, rfl⟩ := (PortGeometry.chart64 K h2 port).surjective v
  rcases hchild with rfl | rfl
  · change sourceBeforeOperator K 1 port false (PortGeometry.chart64 K h2 port w) -
      sourceBeforeOperator K 1 port true (PortGeometry.chart64 K h2 port w) = _
    rw [(child1_source_operators K port false).1,
      (child1_source_operators K port true).1,
      local_endpoint_after K h2 port (⟨1, by decide⟩ : Fin 4) true false w,
      local_endpoint_after K h2 port (⟨1, by decide⟩ : Fin 4) true true w,
      entrance_endpoint K h2 port false w, ← chart64_sub]
    congr 1
    funext i
    simp [afterMask, entranceMask]
  · change sourceBeforeOperator K 2 port false (PortGeometry.chart64 K h2 port w) -
      sourceBeforeOperator K 2 port true (PortGeometry.chart64 K h2 port w) = _
    rw [(child2_source_operators K port false).1,
      (child2_source_operators K port true).1,
      entrance_endpoint K h2 port false w,
      entrance_endpoint K h2 port true w, ← chart64_sub]
    simp [entranceMask]

/-- The same literal-root difference remains at each after endpoint; the
pending equality therefore uses cancellation, never equality of the levels. -/
theorem source_after_sided_difference (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (child : Nat) (hchild : child = 1 ∨ child = 2) (port : Fin 120) :
    sourceAfterOperator K child port false - sourceAfterOperator K child port true =
      endpointOperator K port (entranceEndpoint port false) := by
  funext v
  obtain ⟨w, rfl⟩ := (PortGeometry.chart64 K h2 port).surjective v
  rcases hchild with rfl | rfl
  · change sourceAfterOperator K 1 port false (PortGeometry.chart64 K h2 port w) -
      sourceAfterOperator K 1 port true (PortGeometry.chart64 K h2 port w) = _
    rw [(child1_source_operators K port false).2,
      (child1_source_operators K port true).2,
      local_endpoint_after K h2 port (⟨2, by decide⟩ : Fin 4) false false w,
      local_endpoint_after K h2 port (⟨2, by decide⟩ : Fin 4) false true w,
      entrance_endpoint K h2 port false w, ← chart64_sub]
    congr 1
    funext i
    simp [afterMask, entranceMask]
  · change sourceAfterOperator K 2 port false (PortGeometry.chart64 K h2 port w) -
      sourceAfterOperator K 2 port true (PortGeometry.chart64 K h2 port w) = _
    rw [(child2_source_operators K port false).2,
      (child2_source_operators K port true).2,
      local_endpoint_after K h2 port (⟨3, by decide⟩ : Fin 4) true false w,
      local_endpoint_after K h2 port (⟨3, by decide⟩ : Fin 4) true true w,
      entrance_endpoint K h2 port false w, ← chart64_sub]
    congr 1
    funext i
    simp [afterMask, entranceMask]

/-- Source and target endpoint projectors differ, but their pending
increments agree by the two separately proved operator comparisons. -/
theorem idle_source_target_cancellation (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (child : Nat) (hchild : child = 1 ∨ child = 2) (port : Fin 120) :
    idlePendingOperator K child port false = idlePendingOperator K child port true := by
  rw [idle_pending_operator K h2 child hchild port false,
    idle_pending_operator K h2 child hchild port true]

end PR442LevelModel.Phase2
