import Nov15.NumCertK
import Nov15.CongestionI3NumC1
namespace CongestionNative
open NumCertK CongestionI3
def tTJ0RE : ℚ := 118103 / 10 ^ 7
def a0RE : ℚ := (14441 : ℚ) / 1250000
def dIRE : ℕ := 1833591819603
def tRE0 : ℚ := (14441 : ℚ) / 1250000
def tRE1 : ℚ := (28907 : ℚ) / 2500000
def sgRE0 : ℚ := (11921 : ℚ) / 250000
def cHRE0 : ℚ := (28581 : ℚ) / 1000000
def lcpRE0 : ℚ := (6022117 : ℚ) / 200000
def unLoRE0 : ℚ := (96428481806759 : ℚ) / 100000000000000
def capIRE0 : ℕ := 2008926704307
def lamRE0 : ℕ := 647239006391
def gARE0 : ℕ := 2157772800171
def gBRE0 : ℕ := 1
def tRE2 : ℚ := (118103 : ℚ) / 10000000
def sgRE1 : ℚ := (50887 : ℚ) / 1000000
def cHRE1 : ℚ := (72963 : ℚ) / 2500000
def lcpRE1 : ℚ := (30105751 : ℚ) / 1000000
def unLoRE1 : ℚ := (12044162755641 : ℚ) / 12500000000000
def capIRE1 : ℕ := 2007360459273
def lamRE1 : ℕ := 647239006391
def gARE1 : ℕ := 2157772800171
def gBRE1 : ℕ := 1
theorem tREend : tRE2 = tTJ0RE := by unfold tRE2 tTJ0RE; norm_num
theorem tREstart : tRE0 = a0RE := by unfold tRE0 a0RE; norm_num
end CongestionNative
