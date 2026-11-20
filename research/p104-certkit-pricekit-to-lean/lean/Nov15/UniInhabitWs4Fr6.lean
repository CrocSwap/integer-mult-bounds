/- UniInhabitWs4Fr6 (lane UNI-INHABIT): frame closure certificates, chunks 54..62 (decide +kernel). -/
import Nov15.UniInhabitWs4Frames

namespace UniInhabitWs4

theorem frames_54 : ∀ i < 962, 952 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_55 : ∀ i < 972, 962 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_56 : ∀ i < 982, 972 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_57 : ∀ i < 992, 982 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_58 : ∀ i < 1002, 992 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_59 : ∀ i < 1012, 1002 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_60 : ∀ i < 1024, 1012 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_61 : ∀ i < 1046, 1024 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_62 : ∀ i < 1072, 1046 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel

end UniInhabitWs4
