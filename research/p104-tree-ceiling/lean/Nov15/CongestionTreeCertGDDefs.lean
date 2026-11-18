import Nov15.NumCertK
import Nov15.CongestionI3NumC1
namespace CongestionNative
open NumCertK CongestionI3
def tTJ0GD : ℚ := 118103 / 10 ^ 7
def a0GD : ℚ := (467 : ℚ) / 40000
def tGD0 : ℚ := (467 : ℚ) / 40000
def tGD1 : ℚ := (73 : ℚ) / 6250
def sgGD0 : ℚ := (48111 : ℚ) / 1000000
def cHGD0 : ℚ := (9021 : ℚ) / 312500
def lcpGD0 : ℚ := (29075199 : ℚ) / 1000000
def unLoGD0 : ℚ := (19278574995077 : ℚ) / 20000000000000
def capIGD0 : ℕ := 2008184895320
def lamGD0 : ℕ := 648426768687
def gAGD0 : ℕ := 3764747108290
def gBGD0 : ℕ := 1584459010234
def tGD2 : ℚ := (118103 : ℚ) / 10000000
def sgGD1 : ℚ := (249 : ℚ) / 5000
def cHGD1 : ℚ := (72963 : ℚ) / 2500000
def lcpGD1 : ℚ := (5814531 : ℚ) / 200000
def unLoGD1 : ℚ := (12044162755641 : ℚ) / 12500000000000
def capIGD1 : ℕ := 2007360459273
def lamGD1 : ℕ := 648426768687
def gAGD1 : ℕ := 3764747108290
def gBGD1 : ℕ := 1584459010234
theorem tGDend : tGD2 = tTJ0GD := by unfold tGD2 tTJ0GD; norm_num
theorem tGDstart : tGD0 = a0GD := by unfold tGD0 a0GD; norm_num
end CongestionNative
