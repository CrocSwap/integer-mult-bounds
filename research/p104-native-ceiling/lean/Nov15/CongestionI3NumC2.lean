import Nov15.CongestionI3NumC1

/-! CONGESTION-I3 numeric part C2 : kernel interval pieces for the own56 ceiling; see CongestionI3NumC1 and CongestionI3.md. -/
namespace CongestionI3
open NumCertK

theorem cfC88_p6 : Fup cfC88 (67/100) (72/100) < 0 := by decide +kernel
theorem cfC88_p7 : Fup cfC88 (72/100) (76/100) < 0 := by decide +kernel
theorem cfC88_p8 : Fup cfC88 (76/100) (79/100) < 0 := by decide +kernel
theorem cfC88_p9 : Fup cfC88 (79/100) (81/100) < 0 := by decide +kernel
theorem cfC88_p10 : Fup cfC88 (81/100) (83/100) < 0 := by decide +kernel

end CongestionI3
