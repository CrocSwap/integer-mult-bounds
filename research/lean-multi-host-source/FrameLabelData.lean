import FrameTraceLiterals

/-!
Literal label bounds and full-to-zero private COPY/ERASE identification.
The checker reads every event in the actual selected forward word.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
-/
namespace SourceFrameLabels
set_option maxRecDepth 100000
set_option maxHeartbeats 0

def labelCheck (e : FrameTrace.Entry) : Bool :=
  decide (e.oldFrame < 944 ∧ e.newFrame < 944 ∧
    ((e.scalar.op = 2 ∨ e.scalar.op = 3) → e.oldFrame = 1 ∧ e.newFrame = 0))

theorem labels_checked : SourceFrameTrace.forward.all labelCheck = true := by
  -- Check the existing chunks before flattening the 19,002-entry word.
  rw [SourceFrameTrace.forward, List.all_flatten]
  decide +kernel

theorem labels_valid (e : FrameTrace.Entry) (he : e ∈ SourceFrameTrace.forward) :
    e.oldFrame < 944 ∧ e.newFrame < 944 ∧
    ((e.scalar.op = 2 ∨ e.scalar.op = 3) → e.oldFrame = 1 ∧ e.newFrame = 0) := by
  exact of_decide_eq_true (List.all_eq_true.mp labels_checked e he)

theorem label_range (e : FrameTrace.Entry) (he : e ∈ SourceFrameTrace.forward) :
    e.oldFrame < 944 ∧ e.newFrame < 944 :=
  ⟨(labels_valid e he).1, (labels_valid e he).2.1⟩

theorem copy_frames (e : FrameTrace.Entry) (he : e ∈ SourceFrameTrace.forward)
    (hop : e.scalar.op = 2) : e.oldFrame = 1 ∧ e.newFrame = 0 :=
  (labels_valid e he).2.2 (Or.inl hop)

theorem erase_frames (e : FrameTrace.Entry) (he : e ∈ SourceFrameTrace.forward)
    (hop : e.scalar.op = 3) : e.oldFrame = 1 ∧ e.newFrame = 0 :=
  (labels_valid e he).2.2 (Or.inr hop)

end SourceFrameLabels
#print axioms SourceFrameLabels.labels_checked
#print axioms SourceFrameLabels.label_range
#print axioms SourceFrameLabels.copy_frames
#print axioms SourceFrameLabels.erase_frames
