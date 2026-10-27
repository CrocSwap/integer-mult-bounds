import HelperGeometryData
import FrameGeometry
import FrameTraceTables
import FrameLabelData
import PhysicalSourceConnection
import AddressPairs

/-!
Actual stage-2 address gauges, including the common exterior E₂ swap on
coordinates 8..21. The helper relative-frame premise is discharged from the
literal trace and frame tables. Modulo indexing only totalizes the public
Nat API: every source frame label has separately been checked below 944.
-/
namespace SelectedGeometry

def gauges (K : Type) [Field K] (h2 : (2 : K) ≠ 0) : PhysicalSourceConnection.Gauges K :=
  fun n => AddressPairs.gauge
    (FrameGeometry.gaugeStage2 K h2 ⟨n % 944, Nat.mod_lt _ (by decide)⟩)

theorem gauges_tag (K : Type) [Field K] (h2 : (2 : K) ≠ 0) (t : SourceOwnership.Tag) :
    gauges K h2 (SourceOwnership.lookup SourceOwnership.tagInitialFrame t.val) =
      AddressPairs.gauge (FrameGeometry.gaugeStage2 K h2 (tagFrame t)) := by
  have hf : (⟨SourceOwnership.lookup SourceOwnership.tagInitialFrame t.val % 944,
      Nat.mod_lt _ (by decide)⟩ : Fin 944) = tagFrame t := by
    apply Fin.ext
    exact Nat.mod_eq_of_lt (tag_frame_bound t)
  exact congrArg (fun f => AddressPairs.gauge (FrameGeometry.gaugeStage2 K h2 f)) hf

theorem helper_relative (K : Type) [Field K] (h2 : (2 : K) ≠ 0) :
    PhysicalSourceConnection.HelperRelative (gauges K h2) := by
  intro h a
  have hi := SourceFrameTrace.initial_owner_frames (SourceConnection.role h)
  have hr := SourceOwnership.helper_frame (SourceConnection.role h) (by
    change 240 ≤ 240 + h.val
    omega)
  have hf := SourceFrameTrace.helper_final_frames h
  have hi' : SourceFrameTrace.state0.frames.get (240 + h.val) =
      SourceOwnership.lookup SourceOwnership.tagInitialFrame
        (SourceOwnership.tag (SourceConnection.role h)).val := hi.trans hr
  unfold PhysicalSourceConnection.relative
  rw [hi', hf, gauges_tag]
  change (AddressPairs.gauge
      (FrameGeometry.gaugeStage2 K h2 (tagFrame (SourceOwnership.tag (SourceConnection.role h))))).forward
    ((AddressPairs.gauge (FrameGeometry.gaugeStage2 K h2 1)).inverse a) = _
  apply AddressPairs.relative_coordinate
  intro p
  exact FrameGeometry.stage2_helper_endpoint K h2 _ _
    (tag_residual_diagonal (SourceOwnership.tag (SourceConnection.role h)))
    (source_mask_outside (SourceOwnership.tag (SourceConnection.role h))) p

end SelectedGeometry
