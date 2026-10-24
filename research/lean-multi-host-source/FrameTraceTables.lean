import FrameTraceLiterals
import OwnershipData

/-! Small concrete joins between the independently extracted frame trajectory
and the ownership tables. These are finite equalities, not assumptions about
an unexecuted source word. The source-binding replay reproduces both tables. -/
namespace SourceFrameTrace
set_option maxRecDepth 100000
set_option maxHeartbeats 0

theorem initial_owner_frames : ∀ r : SourceOwnership.Role,
    state0.frames.get r.val = SourceOwnership.lookup SourceOwnership.initialFrameTable r.val := by
  decide

theorem helper_final_frames : ∀ h : Fin 747,
    state96.frames.get (240 + h.val) = 1 := by
  decide

theorem initial_frame_range : ∀ r : SourceOwnership.Role,
    state0.frames.get r.val < 944 := by
  decide

theorem final_frame_range : ∀ r : SourceOwnership.Role,
    state96.frames.get r.val < 944 := by
  decide

#print axioms initial_owner_frames
#print axioms helper_final_frames
#print axioms initial_frame_range
#print axioms final_frame_range
end SourceFrameTrace
