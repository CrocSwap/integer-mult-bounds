/- UniInhabitWs4Fr0 (lane UNI-INHABIT): frame closure certificates, chunks 0..8 (decide +kernel). -/
import Nov15.UniInhabitWs4Frames

namespace UniInhabitWs4

theorem frames_0 : ∀ i < 50, 0 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_1 : ∀ i < 100, 50 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_2 : ∀ i < 127, 100 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_3 : ∀ i < 131, 127 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_4 : ∀ i < 136, 131 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_5 : ∀ i < 141, 136 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_6 : ∀ i < 146, 141 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_7 : ∀ i < 151, 146 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_8 : ∀ i < 156, 151 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel

end UniInhabitWs4
