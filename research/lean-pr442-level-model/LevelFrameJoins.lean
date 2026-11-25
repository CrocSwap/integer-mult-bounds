import LevelSourceData
import FrameLookup
import FrameTraceLiterals
import OwnershipDatumCore
import PortData

/-!
Finite joins between separately extracted PR370/PR386 labels, the PR442
endpoint tables, and PR540's existing certified frames and port routes.
The two programs have different helper populations; only the stated data-role
and frame-table joins are asserted. No pending-coordinate definition is used.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
-/
namespace PR442LevelModel
set_option maxHeartbeats 0
set_option maxRecDepth 100000

/-- The old root labels and the actual PR442 geometry agree at every port. -/
theorem old_roots_join : ∀ (p : Port) (i : LocalAxis),
    oldRootVector p i = rootVector p i := by decide +kernel

/-- The old word and current invocation share these four data-role endpoints.
This does not assert equality of their entire initial/final role arrays. -/
theorem old_endpoint_labels_join : ∀ p : Port,
    oldSourceEntrance p = sourceEntrance p ∧
    oldTargetEntrance p = targetEntrance p ∧
    oldSourceExit p = sourceExit p ∧
    oldTargetExit p = targetExit p := by decide +kernel

/-- Bind the extracted endpoints to PR540's literal initial/final frame trace. -/
theorem invocation_endpoint_labels : ∀ p : Port,
    SourceFrameTrace.state0.frames.get p.val = (sourceEntrance p).val ∧
    SourceFrameTrace.state0.frames.get (120 + p.val) = (targetEntrance p).val ∧
    SourceFrameTrace.state96.frames.get p.val = (sourceExit p).val ∧
    SourceFrameTrace.state96.frames.get (120 + p.val) = (targetExit p).val := by
  decide +kernel

/-- The independently extracted ownership table selects the same entrances. -/
theorem ownership_entrance_labels : ∀ p : Port,
    SourceOwnership.lookup SourceOwnership.initialFrameTable p.val =
      (sourceEntrance p).val ∧
    SourceOwnership.lookup SourceOwnership.initialFrameTable (120 + p.val) =
      (targetEntrance p).val := by decide +kernel

theorem endpoint_label_values : ∀ p : Port,
    (sourceEntrance p).val = p.val + 2 ∧ targetEntrance p = 0 ∧
    sourceExit p = 1 ∧ (targetExit p).val = 824 + p.val := by
  decide +kernel

/-- The old entrance is literally the singleton root label, not a newly
chosen projector of the same rank. -/
theorem old_entrance_singleton : ∀ p : Port,
    oldEntranceLineLabels.getD p.val [] = [p.val] := by decide +kernel

theorem entrance_basis_join : ∀ (p : Port) (i : LocalAxis),
    FrameGeometry.stack (sourceEntrance p) 0 i =
      ((oldEntranceBasisRows.getD p.val #[]).getD 0 #[]).getD i.val 0 ∧
    FrameGeometry.stack (sourceEntrance p) 0 i = rootVector p i := by
  decide +kernel

theorem target_exit_basis_join : ∀ (p : Port) (r : Fin 7) (i : LocalAxis),
    FrameGeometry.stack (targetExit p) ⟨r.val, by omega⟩ i =
      ((oldTargetExitBasisRows.getD p.val #[]).getD r.val #[]).getD i.val 0 := by
  decide +kernel

theorem endpoint_dimensions : ∀ p : Port,
    (FrameGeometry.frame (sourceEntrance p)).dimension = 1 ∧
    (FrameGeometry.frame (targetEntrance p)).dimension = 0 ∧
    (FrameGeometry.frame (sourceExit p)).dimension = 8 ∧
    (FrameGeometry.frame (targetExit p)).dimension = 7 := by decide +kernel

/-- This join ties the root read from JSON to the already certified port chart. -/
theorem root_eq_basis : ∀ (p : Port) (i : LocalAxis),
    rootVector p i = PortGeometry.doubledBasis p i 0 := by decide +kernel

/-- Four times the literal entrance projector is the root outer product. -/
theorem entrance_scaled : ∀ (p : Port) (i j : LocalAxis),
    FrameGeometry.scaled (sourceEntrance p) i j = rootVector p i * rootVector p j := by
  decide +kernel

/-- Both sides are retained: the target exits on the complementary projector. -/
theorem target_exit_scaled : ∀ (p : Port) (i j : LocalAxis),
    FrameGeometry.scaled (targetExit p) i j =
      (if i = j then 4 else 0) - rootVector p i * rootVector p j := by
  decide +kernel

/-- Reuse PR540's literal route certificate to identify its upper-left block
with the independently joined entrance frame. Stage transport is Phase 2. -/
theorem route_root_block (p : Port) (i j : LocalAxis) :
    PortGeometry.quarteredRoute p ⟨i.val, by omega⟩ ⟨j.val, by omega⟩ =
      FrameGeometry.scaled (sourceEntrance p) i j := by
  rw [PortGeometry.quarteredRoute_exact, entrance_scaled]
  simp [PortGeometry.expectedQuarteredRoute, PortGeometry.routeExpected,
    i.isLt, j.isLt, root_eq_basis]

end PR442LevelModel
