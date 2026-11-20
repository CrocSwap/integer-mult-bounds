/- UniInhabitFr5 (lane UNI-INHABIT): frame closure certificates, chunks 45..53 (decide +kernel). -/
import Nov15.UniInhabitFrames

namespace UniInhabit

theorem frames_45 : ∀ i < 839, 820 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_46 : ∀ i < 858, 839 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_47 : ∀ i < 877, 858 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_48 : ∀ i < 897, 877 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_49 : ∀ i < 910, 897 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_50 : ∀ i < 920, 910 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_51 : ∀ i < 930, 920 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_52 : ∀ i < 942, 930 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_53 : ∀ i < 952, 942 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel

end UniInhabit
