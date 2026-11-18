import Nov15.NumCertK
import Nov15.CongestionI3NumC1
namespace CongestionNative
open NumCertK CongestionI3
def tTJ0RD : ℚ := 118103 / 10 ^ 7
def a0RD : ℚ := (57631 : ℚ) / 5000000
def dIRD : ℕ := 1829476964867
def tRD0 : ℚ := (57631 : ℚ) / 5000000
def tRD1 : ℚ := (14409 : ℚ) / 1250000
def sgRD0 : ℚ := (1483 : ℚ) / 31250
def cHRD0 : ℚ := (284941 : ℚ) / 10000000
def lcpRD0 : ℚ := (6066973 : ℚ) / 200000
def unLoRD0 : ℚ := (96439299869701 : ℚ) / 100000000000000
def capIRD0 : ℕ := 2009152080618
def lamRD0 : ℕ := 645764760052
def gARD0 : ℕ := 2152870912751
def gBRD0 : ℕ := 31
def tRD2 : ℚ := (7267 : ℚ) / 625000
def sgRD1 : ℚ := (48779 : ℚ) / 1000000
def cHRD1 : ℚ := (287383 : ℚ) / 10000000
def lcpRD1 : ℚ := (30332911 : ℚ) / 1000000
def unLoRD1 : ℚ := (96408914818159 : ℚ) / 100000000000000
def capIRD1 : ℕ := 2008519058711
def lamRD1 : ℕ := 645764760052
def gARD1 : ℕ := 2152870912751
def gBRD1 : ℕ := 31
def tRD3 : ℚ := (118103 : ℚ) / 10000000
def sgRD2 : ℚ := (50289 : ℚ) / 1000000
def cHRD2 : ℚ := (72963 : ℚ) / 2500000
def lcpRD2 : ℚ := (3791167 : ℚ) / 125000
def unLoRD2 : ℚ := (12044162755641 : ℚ) / 12500000000000
def capIRD2 : ℕ := 2007360459273
def lamRD2 : ℕ := 645764760052
def gARD2 : ℕ := 2152870912751
def gBRD2 : ℕ := 31
theorem tRDend : tRD3 = tTJ0RD := by unfold tRD3 tTJ0RD; norm_num
theorem tRDstart : tRD0 = a0RD := by unfold tRD0 a0RD; norm_num
end CongestionNative
