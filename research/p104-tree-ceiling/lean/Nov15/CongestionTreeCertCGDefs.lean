import Nov15.NumCertK
import Nov15.CongestionI3NumC1
namespace CongestionNative
open NumCertK CongestionI3
def tTJ0 : ℚ := 118103 / 10 ^ 7
def a0CG : ℚ := (58847 : ℚ) / 5000000
def tCG0 : ℚ := (58847 : ℚ) / 5000000
def tCG1 : ℚ := (7359 : ℚ) / 625000
def sgCG0 : ℚ := (48493 : ℚ) / 1000000
def cHCG0 : ℚ := (9093 : ℚ) / 312500
def lcpCG0 : ℚ := (28276807 : ℚ) / 1000000
def unLoCG0 : ℚ := (96364203646413 : ℚ) / 100000000000000
def capICG0 : ℕ := 2007587575966
def lamCG0 : ℕ := 574558412032
def gACG0 : ℕ := 36
def gBCG0 : ℕ := 36
def tCG2 : ℚ := (118103 : ℚ) / 10000000
def sgCG1 : ℚ := (12231 : ℚ) / 250000
def cHCG1 : ℚ := (72963 : ℚ) / 2500000
def lcpCG1 : ℚ := (14138053 : ℚ) / 500000
def unLoCG1 : ℚ := (12044162755641 : ℚ) / 12500000000000
def capICG1 : ℕ := 2007360459273
def lamCG1 : ℕ := 574558412032
def gACG1 : ℕ := 36
def gBCG1 : ℕ := 36
theorem tCGend : tCG2 = tTJ0 := by unfold tCG2 tTJ0; norm_num
theorem tCGstart : tCG0 = a0CG := by unfold tCG0 a0CG; norm_num
end CongestionNative
