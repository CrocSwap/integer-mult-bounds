import FrameData
import OwnershipData

/-! Kernel joins between the actual helper slot descriptors and the actual
frame matrix table. All displayed coordinate claims are finite checks of
those literal tables, not premises of the physical source theorem. -/
namespace SelectedGeometry
set_option maxRecDepth 100000
set_option maxHeartbeats 0

theorem tag_frame_bound : ∀ t : SourceOwnership.Tag,
    SourceOwnership.lookup SourceOwnership.tagInitialFrame t.val < 944 := by decide

def tagFrame (t : SourceOwnership.Tag) : Fin 944 :=
  ⟨SourceOwnership.lookup SourceOwnership.tagInitialFrame t.val, tag_frame_bound t⟩

theorem tag_residual_diagonal : ∀ (t : SourceOwnership.Tag) (i j : Fin 8),
    FrameGeometry.scaled 1 i j - FrameGeometry.scaled (tagFrame t) i j =
      if i = j ∧ SourceOwnership.sourceMask t ⟨i.val, Nat.lt_trans i.isLt (by decide)⟩ = true
      then 4 else 0 := by decide

theorem source_mask_outside : ∀ (t : SourceOwnership.Tag) (i : SourceOwnership.Axis),
    8 ≤ i.val → SourceOwnership.sourceMask t i = false := by decide

end SelectedGeometry
