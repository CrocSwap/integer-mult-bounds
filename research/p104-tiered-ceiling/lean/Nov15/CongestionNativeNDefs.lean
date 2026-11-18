import Mathlib.Data.Rat.Defs
import Mathlib.Tactic.NormNum

/-! CONGESTION-NATIVE-N96 tables. Source: internal table generators (N = 96;
spF_lo / unit_lo rounded DOWN to 14 digits, cst rounded UP, outward Decimal 80 digits). -/
namespace CongestionNative

def tN0 : ℚ := 151027 / 10 ^ 7
def tN1 : ℚ := 151077 / 10 ^ 7
def tN2 : ℚ := 153077 / 10 ^ 7
def tN3 : ℚ := 253077 / 10 ^ 7
def tN4 : ℚ := 7 / 100
def tN5 : ℚ := 1 / 10
def sgN0 : ℚ := 61897 / 1000000
def cHN0 : ℚ := 23253 / 625000
def lcpN0 : ℚ := 198661 / 500000
def LN0 : ℚ := lcpN0 - 5 * sgN0
def spFloN0 : ℚ := 723917880571 / 100000000000000
def unitLoN0 : ℚ := 47678349095889 / 50000000000000
def sgN1 : ℚ := 4031 / 62500
def cHN1 : ℚ := 188447 / 5000000
def lcpN1 : ℚ := 393673 / 1000000
def LN1 : ℚ := lcpN1 - 5 * sgN1
def spFloN1 : ℚ := 362077327347 / 50000000000000
def unitLoN1 : ℚ := 23824137184247 / 25000000000000
def sgN2 : ℚ := 40937 / 200000
def cHN2 : ℚ := 77077 / 1250000
def lcpN2 : ℚ := 105493 / 500000
def LN2 : ℚ := lcpN2 - 5 * sgN2
def spFloN2 : ℚ := 45851503937 / 6250000000000
def unitLoN2 : ℚ := 23083018215939 / 25000000000000
def sgN3 : ℚ := 747329 / 1000000
def cHN3 : ℚ := 1628077 / 10000000
def lcpN3 : ℚ := -147349 / 1000000
def LN3 : ℚ := lcpN3 - 5 * sgN3
def spFloN3 : ℚ := 1203242422603 / 100000000000000
def unitLoN3 : ℚ := 5004058989633 / 6250000000000
def sgN4 : ℚ := 24423 / 40000
def cHN4 : ℚ := 2255027 / 10000000
def lcpN4 : ℚ := -43839 / 125000
def LN4 : ℚ := lcpN4 - 5 * sgN4
def spFloN4 : ℚ := 3212352863571 / 100000000000000
def unitLoN4 : ℚ := 72665488499219 / 100000000000000
theorem tabN0 : lcpN0 + 8 * cHN0 ≤ 96 * spFloN0 ∧ lcpN0 + 8 * cHN0 ≤ 96 * (unitLoN0 / 48) := by
  unfold lcpN0 cHN0 spFloN0 unitLoN0; constructor <;> norm_num
theorem tabN1 : lcpN1 + 8 * cHN1 ≤ 96 * spFloN1 ∧ lcpN1 + 8 * cHN1 ≤ 96 * (unitLoN1 / 48) := by
  unfold lcpN1 cHN1 spFloN1 unitLoN1; constructor <;> norm_num
theorem tabN2 : lcpN2 + 8 * cHN2 ≤ 96 * spFloN2 ∧ lcpN2 + 8 * cHN2 ≤ 96 * (unitLoN2 / 48) := by
  unfold lcpN2 cHN2 spFloN2 unitLoN2; constructor <;> norm_num
theorem tabN3 : lcpN3 + 8 * cHN3 ≤ 96 * spFloN3 ∧ lcpN3 + 8 * cHN3 ≤ 96 * (unitLoN3 / 48) := by
  unfold lcpN3 cHN3 spFloN3 unitLoN3; constructor <;> norm_num
theorem tabN4 : lcpN4 + 8 * cHN4 ≤ 96 * spFloN4 ∧ lcpN4 + 8 * cHN4 ≤ 96 * (unitLoN4 / 48) := by
  unfold lcpN4 cHN4 spFloN4 unitLoN4; constructor <;> norm_num

end CongestionNative
