import Mathlib.Data.Rat.Defs

/-! CONGESTION-I3-DUAL constants: t-breakpoints of the pieces, certified sigma_j (Sig/Cert*), data lower bounds lcp_j
(python: internal notes; lcp_j = lower bound of 1936 spF(t_j) [8|9] resp. 1936 min(sp, cap) - 8 cst [own56], rounded down), L_j = lcp_j - 5 sigma_j. -/
namespace CongestionI3Dual
-- 8|9 plain, m = 5: t-breakpoints
def tA0 : ℚ := 186470 / 10 ^ 7
def tA1 : ℚ := 186490 / 10 ^ 7
def tA2 : ℚ := 187490 / 10 ^ 7
def tA3 : ℚ := 287490 / 10 ^ 7
-- own56, m = 5
def tC0 : ℚ := 136564 / 10 ^ 7
def tC1 : ℚ := 136584 / 10 ^ 7
def tC2 : ℚ := 137584 / 10 ^ 7
def tC3 : ℚ := 237584 / 10 ^ 7
def sgA0 : ℚ := 37981 / 500000
def sgA1 : ℚ := 77257 / 10 ^ 6
def sgA2 : ℚ := 213457 / 10 ^ 6
def sgA3 : ℚ := 560567 / 500000
def sgC0 : ℚ := 28029 / 500000
def sgC1 : ℚ := 28683 / 500000
def sgC2 : ℚ := 200709 / 10 ^ 6
def sgC3 : ℚ := 1185727 / 10 ^ 6


def lcpA0 : ℚ := 862761 / 50000
def lcpA1 : ℚ := 17257043 / 10 ^ 6
def lcpA2 : ℚ := 3469639 / 200000
def lcpA3 : ℚ := 6597489 / 250000
def LA0 : ℚ := lcpA0 - 5 * sgA0
def LA1 : ℚ := lcpA1 - 5 * sgA1
def LA2 : ℚ := lcpA2 - 5 * sgA2
def LA3 : ℚ := lcpA3 - 5 * sgA3
def lcpC0 : ℚ := 12418057 / 10 ^ 6
def lcpC1 : ℚ := 248359 / 20000
def lcpC2 : ℚ := 3079357 / 250000
def lcpC3 : ℚ := 5022921 / 250000
def LC0 : ℚ := lcpC0 - 5 * sgC0
def LC1 : ℚ := lcpC1 - 5 * sgC1
def LC2 : ℚ := lcpC2 - 5 * sgC2
def LC3 : ℚ := lcpC3 - 5 * sgC3

end CongestionI3Dual
