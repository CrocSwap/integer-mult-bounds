import Mathlib.Data.Rat.Defs
import Mathlib.Tactic.NormNum

/-! CONGESTION-NATIVE-Z0 tables. Source: internal table generators (N = 0;
spF_lo / unit_lo rounded DOWN to 14 digits, cst rounded UP, outward Decimal 80 digits). -/
namespace CongestionNative

def tZ0 : ℚ := 151869 / 10 ^ 7
def tZ1 : ℚ := 151889 / 10 ^ 7
def tZ2 : ℚ := 152889 / 10 ^ 7
def tZ3 : ℚ := 202889 / 10 ^ 7
def tZ4 : ℚ := 7 / 100
def tZ5 : ℚ := 1 / 10
def sgZ0 : ℚ := 31097 / 500000
def cHZ0 : ℚ := 74803 / 2000000
def lcpZ0 : ℚ := -74803 / 250000
def LZ0 : ℚ := lcpZ0 - 5 * sgZ0
def spFloZ0 : ℚ := 363952451801 / 50000000000000
def unitLoZ0 : ℚ := 1906645468203 / 2000000000000
def sgZ1 : ℚ := 31749 / 500000
def cHZ1 : ℚ := 188219 / 5000000
def lcpZ1 : ℚ := -301151 / 1000000
def LZ1 : ℚ := lcpZ1 - 5 * sgZ1
def spFloZ1 : ℚ := 727999600691 / 100000000000000
def unitLoZ1 : ℚ := 95302201336951 / 100000000000000
def sgZ2 : ℚ := 25673 / 200000
def cHZ2 : ℚ := 496937 / 10000000
def lcpZ2 : ℚ := -7951 / 20000
def LZ2 : ℚ := lcpZ2 - 5 * sgZ2
def spFloZ2 : ℚ := 366367033967 / 50000000000000
def unitLoZ2 : ℚ := 23452348528969 / 25000000000000
def sgZ3 : ℚ := 32509 / 40000
def cHZ3 : ℚ := 1628077 / 10000000
def lcpZ3 : ℚ := -651231 / 500000
def LZ3 : ℚ := lcpZ3 - 5 * sgZ3
def spFloZ3 : ℚ := 968491930913 / 100000000000000
def unitLoZ3 : ℚ := 5004058989633 / 6250000000000
def sgZ4 : ℚ := 24423 / 40000
def cHZ4 : ℚ := 2255027 / 10000000
def lcpZ4 : ℚ := -902011 / 500000
def LZ4 : ℚ := lcpZ4 - 5 * sgZ4
def spFloZ4 : ℚ := 3212352863571 / 100000000000000
def unitLoZ4 : ℚ := 72665488499219 / 100000000000000
theorem tabZ0 : lcpZ0 + 8 * cHZ0 ≤ 0 * spFloZ0 ∧ lcpZ0 + 8 * cHZ0 ≤ 0 * (unitLoZ0 / 48) := by
  unfold lcpZ0 cHZ0 spFloZ0 unitLoZ0; constructor <;> norm_num
theorem tabZ1 : lcpZ1 + 8 * cHZ1 ≤ 0 * spFloZ1 ∧ lcpZ1 + 8 * cHZ1 ≤ 0 * (unitLoZ1 / 48) := by
  unfold lcpZ1 cHZ1 spFloZ1 unitLoZ1; constructor <;> norm_num
theorem tabZ2 : lcpZ2 + 8 * cHZ2 ≤ 0 * spFloZ2 ∧ lcpZ2 + 8 * cHZ2 ≤ 0 * (unitLoZ2 / 48) := by
  unfold lcpZ2 cHZ2 spFloZ2 unitLoZ2; constructor <;> norm_num
theorem tabZ3 : lcpZ3 + 8 * cHZ3 ≤ 0 * spFloZ3 ∧ lcpZ3 + 8 * cHZ3 ≤ 0 * (unitLoZ3 / 48) := by
  unfold lcpZ3 cHZ3 spFloZ3 unitLoZ3; constructor <;> norm_num
theorem tabZ4 : lcpZ4 + 8 * cHZ4 ≤ 0 * spFloZ4 ∧ lcpZ4 + 8 * cHZ4 ≤ 0 * (unitLoZ4 / 48) := by
  unfold lcpZ4 cHZ4 spFloZ4 unitLoZ4; constructor <;> norm_num

end CongestionNative
