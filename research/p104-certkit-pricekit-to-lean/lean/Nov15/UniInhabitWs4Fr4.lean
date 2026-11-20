/- UniInhabitWs4Fr4 (lane UNI-INHABIT): frame closure certificates, chunks 36..44 (decide +kernel). -/
import Nov15.UniInhabitWs4Frames

namespace UniInhabitWs4

theorem frames_36 : ∀ i < 630, 592 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_37 : ∀ i < 648, 630 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_38 : ∀ i < 664, 648 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_39 : ∀ i < 682, 664 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_40 : ∀ i < 707, 682 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_41 : ∀ i < 739, 707 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_42 : ∀ i < 769, 739 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_43 : ∀ i < 794, 769 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_44 : ∀ i < 820, 794 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel

end UniInhabitWs4
