import Mathlib.Tactic

namespace ScaledEntrance

def upper (M : ℕ) := 2*(M/(2048*12087))
def band (M : ℕ) := 2*((3*upper M)/8)
def actualSize (M : ℕ) := 10191*(band M-8)

/-- All integer rounding in the changed physical entrance, including the period fences. -/
theorem placement (M : ℕ) (large : 10^13 ≤ M) :
    (32768 < band M) ∧
    (4424 * upper M < 10191 * band M) ∧
    ((band M+2)*10191 < 4424*M) ∧
    (1616 * actualSize M < M) ∧
    (M+6000 < 1620*actualSize M) := by
  simp only [upper, band, actualSize]
  omega

/-- Both following tickets belong to the five-hit prefix and differ from slot one. -/
theorem tickets (M : ℕ) (large : 10^13 ≤ M) :
    3240 < 5 * ((1620*actualSize M - M)/4) ∧
    1620/5 = 324 ∧ 3240/5 = 648 := by
  have h := (placement M large).2.2.2.2
  omega

#print axioms placement
#print axioms tickets
end ScaledEntrance
