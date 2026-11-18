import Nov15.CongestionI3DualConst
import Nov15.CongestionI3NumC1
import Nov15.CongestionNativeTab

/-! CONGESTION-C56 certificates: the three own56 t-pieces on [tK0, tC0] for the junk count N = 4166.
Numbers come from a script (Decimal, 80 digits, +-1e-70 brackets; spF DAG weights rounded DOWN, cst rounded UP,
unit_lo = 9^s lower - 8^s upper; all rounded outward to 14 / 6 / 7 digits).  Kernel-checked here: sigma certificates (`sigOK`), F_base point
enclosures (`Fup`), the derivative bound of F_base on [.93, 1 - tK0], the rational table arithmetic, and all unit lower bounds. -/
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual

def tK0 : ℚ := 122445 / 10 ^ 7
def tK1 : ℚ := 122455 / 10 ^ 7
def tK2 : ℚ := 123455 / 10 ^ 7
def sgK0 : ℚ := 25179 / 500000
def sgK1 : ℚ := 51679 / 1000000
def sgK2 : ℚ := 68163 / 1000000
def cHK0 : ℚ := 302469 / 10 ^ 7
def cHK1 : ℚ := 304907 / 10 ^ 7
def cHK2 : ℚ := 336819 / 10 ^ 7
def lcpK0 : ℚ := 1516551 / 62500
def lcpK1 : ℚ := 1516553 / 62500
def lcpK2 : ℚ := 24437489 / 10 ^ 6
def LK0 : ℚ := lcpK0 - 5 * sgK0
def LK1 : ℚ := lcpK1 - 5 * sgK1
def LK2 : ℚ := lcpK2 - 5 * sgK2
/-- lower bounds of spF(tK_j) -/
def spFloK0 : ℚ := 588257123193 / 100000000000000
def spFloK1 : ℚ := 588304695709 / 100000000000000
def spFloK2 : ℚ := 593061562153 / 100000000000000
/-- lower bounds of 9^(1-t_{j+1}) - 8^(1-t_{j+1}) (t_{j+1} = tK1, tK2, tC0) -/
def unitLoK0 : ℚ := 48110617331067 / 50000000000000
def unitLoK1 : ℚ := 4809545562343 / 5000000000000
def unitLoK2 : ℚ := 95794193417421 / 100000000000000

theorem tabK0 : lcpK0 + 8 * cHK0 ≤ 4166 * spFloK0 ∧ lcpK0 + 8 * cHK0 ≤ 4166 * (unitLoK0 / 48) := by
  unfold lcpK0 cHK0 spFloK0 unitLoK0; constructor <;> norm_num
theorem tabK1 : lcpK1 + 8 * cHK1 ≤ 4166 * spFloK1 ∧ lcpK1 + 8 * cHK1 ≤ 4166 * (unitLoK1 / 48) := by
  unfold lcpK1 cHK1 spFloK1 unitLoK1; constructor <;> norm_num
theorem tabK2 : lcpK2 + 8 * cHK2 ≤ 4166 * spFloK2 ∧ lcpK2 + 8 * cHK2 ≤ 4166 * (unitLoK2 / 48) := by
  unfold lcpK2 cHK2 spFloK2 unitLoK2; constructor <;> norm_num

end CongestionNative
