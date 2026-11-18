import Nov15.CongestionI3DualConst
import Nov15.CongestionI3NumC1
import Nov15.CongestionNativeTab

/-! CONGESTION-NATIVE-J certificates: the three own56 t-pieces on [tJ0, tC0] for the junk count N = 4962.
Source: internal table generators (Decimal 80 digits, +-1e-70 brackets; spF DAG weights rounded DOWN, cst rounded UP,
unit_lo = 9^s lower - 8^s upper; all rounded outward to 14 / 6 / 7 digits).  Kernel-checked here: sigma certificates (`sigOK`), F_base point
enclosures (`Fup`), the derivative bound of F_base on [.93, 1 - tJ0], the rational table arithmetic, and ALL unit lower bounds (old and new). -/
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual

def tJ0 : ℚ := 118103 / 10 ^ 7
def tJ1 : ℚ := 118123 / 10 ^ 7
def tJ2 : ℚ := 120123 / 10 ^ 7
def sgJ0 : ℚ := 24309 / 500000
def sgJ1 : ℚ := 25631 / 500000
def sgJ2 : ℚ := 57 / 800
def cHJ0 : ℚ := 291901 / 10 ^ 7
def cHJ1 : ℚ := 296781 / 10 ^ 7
def cHJ2 : ℚ := 336819 / 10 ^ 7
def lcpJ0 : ℚ := 27930489 / 10 ^ 6
def lcpJ1 : ℚ := 2793131 / 10 ^ 5
def lcpJ2 : ℚ := 28371641 / 10 ^ 6
def LJ0 : ℚ := lcpJ0 - 5 * sgJ0
def LJ1 : ℚ := lcpJ1 - 5 * sgJ1
def LJ2 : ℚ := lcpJ2 - 5 * sgJ2
/-- lower bounds of spF(tJ_j) -/
def spFloJ0 : ℚ := 113518785551 / 20000000000000
def spFloJ1 : ℚ := 17740285593 / 3125000000000
def spFloJ2 : ℚ := 577208719357 / 100000000000000
/-- lower bounds of 9^(1-t_{j+1}) - 8^(1-t_{j+1}) (t_{j+1} = tJ1, tJ2, tC0) -/
def unitLoJ0 : ℚ := 48176347373057 / 50000000000000
def unitLoJ1 : ℚ := 96291982180651 / 100000000000000
def unitLoJ2 : ℚ := 95794193417421 / 100000000000000

theorem tabJ0 : lcpJ0 + 8 * cHJ0 ≤ 4962 * spFloJ0 ∧ lcpJ0 + 8 * cHJ0 ≤ 4962 * (unitLoJ0 / 48) := by
  unfold lcpJ0 cHJ0 spFloJ0 unitLoJ0; constructor <;> norm_num
theorem tabJ1 : lcpJ1 + 8 * cHJ1 ≤ 4962 * spFloJ1 ∧ lcpJ1 + 8 * cHJ1 ≤ 4962 * (unitLoJ1 / 48) := by
  unfold lcpJ1 cHJ1 spFloJ1 unitLoJ1; constructor <;> norm_num
theorem tabJ2 : lcpJ2 + 8 * cHJ2 ≤ 4962 * spFloJ2 ∧ lcpJ2 + 8 * cHJ2 ≤ 4962 * (unitLoJ2 / 48) := by
  unfold lcpJ2 cHJ2 spFloJ2 unitLoJ2; constructor <;> norm_num

end CongestionNative
