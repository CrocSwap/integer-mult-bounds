import Nov15.CongestionI3NumC2

/-! CONGESTION-I3 numeric part C3 : kernel interval pieces for the own56 ceiling; see CongestionI3NumC1 and CongestionI3.md. -/
namespace CongestionI3
open NumCertK

def sC : ℚ := 1 - 134769139 / 10 ^ 10
def LcC : ℚ := 1364105 / 10 ^ 5
def liftC : ℚ := 17 * LcC

theorem cfC88_p11 : Fup cfC88 (83/100) (86/100) < 0 := by decide +kernel
theorem cfC88_p12 : Fup cfC88 (86/100) (88/100) < 0 := by decide +kernel
theorem cfC88_p13 : Fup cfC88 (88/100) (9/10) < 0 := by decide +kernel
theorem cfC_q1 : Fup cfC (90 / 100) (915 / 1000) < liftC := by decide +kernel
theorem cfC_q2 : Fup cfC (915 / 1000) (93 / 100) < liftC := by decide +kernel

end CongestionI3
