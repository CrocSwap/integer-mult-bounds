import Nov15.NumCertK
import Nov15.CongestionI3NumC1
namespace CongestionNative
open NumCertK CongestionI3
def tTJ0RF : ℚ := 118103 / 10 ^ 7
def a0RF : ℚ := (28857 : ℚ) / 2500000
def dIRF : ℕ := 1832044939017
def tRF0 : ℚ := (28857 : ℚ) / 2500000
def tRF1 : ℚ := (14441 : ℚ) / 1250000
def sgRF0 : ℚ := (47643 : ℚ) / 1000000
def cHRF0 : ℚ := (142783 : ℚ) / 5000000
def lcpRF0 : ℚ := (15097357 : ℚ) / 500000
def unLoRF0 : ℚ := (12053940059817 : ℚ) / 12500000000000
def capIRF0 : ℕ := 2008990009969
def lamRF0 : ℕ := 646684787048
def gARF0 : ℕ := 2155930020953
def gBRF0 : ℕ := 3
def tRF2 : ℚ := (118103 : ℚ) / 10000000
def sgRF1 : ℚ := (50979 : ℚ) / 1000000
def cHRF1 : ℚ := (72963 : ℚ) / 2500000
def lcpRF1 : ℚ := (6037937 : ℚ) / 200000
def unLoRF1 : ℚ := (12044162755641 : ℚ) / 12500000000000
def capIRF1 : ℕ := 2007360459273
def lamRF1 : ℕ := 646684787048
def gARF1 : ℕ := 2155930020953
def gBRF1 : ℕ := 3
theorem tRFend : tRF2 = tTJ0RF := by unfold tRF2 tTJ0RF; norm_num
theorem tRFstart : tRF0 = a0RF := by unfold tRF0 a0RF; norm_num
end CongestionNative
