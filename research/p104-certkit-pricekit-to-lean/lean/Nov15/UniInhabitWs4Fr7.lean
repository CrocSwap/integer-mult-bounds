/- UniInhabitWs4Fr7 (lane UNI-INHABIT): frame closure certificates, chunks 63..64 (decide +kernel). -/
import Nov15.UniInhabitWs4Frames

namespace UniInhabitWs4

theorem frames_63 : ∀ i < 1086, 1072 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel
theorem frames_64 : ∀ i < 1096, 1086 ≤ i → frameOK (gt 11 Tabs.maskT i) (Tabs.basesL.getD i []) = true := by decide +kernel

end UniInhabitWs4
