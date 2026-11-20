/- UniInhabitFr1 (lane UNI-INHABIT): frame closure certificates, chunks 9..17 (decide +kernel). -/
import Nov15.UniInhabitFrames

namespace UniInhabit

theorem frames_9 : ∀ i < 161, 156 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_10 : ∀ i < 166, 161 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_11 : ∀ i < 171, 166 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_12 : ∀ i < 176, 171 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_13 : ∀ i < 181, 176 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_14 : ∀ i < 186, 181 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_15 : ∀ i < 191, 186 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_16 : ∀ i < 196, 191 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_17 : ∀ i < 201, 196 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel

end UniInhabit
