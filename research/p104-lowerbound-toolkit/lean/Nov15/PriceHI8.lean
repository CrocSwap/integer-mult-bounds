/-
PriceHI8 (lane PRICEH, Nov 20).  Molecule certificates (cards/WILD/NOVEL/priceh/mol_h*.json, gen.py; Fractions-verified by verify.py)
as MolData h for label ranks h in [8], each field checked by decide+kernel; `md<h>` : MolData h (instances of PriceHRung.rung_port_h).
Kernel only.
-/
import Nov15.PriceH
import Mathlib.Tactic.IntervalCases

set_option maxRecDepth 100000
set_option linter.unusedVariables false

namespace PriceH
open BankNC0

def molD8 : ℕ → ℕ := fun L => ([0, 400, 20, 24, 8, 4, 96, 2]:List ℕ).getD L 0
def molE8 : ℕ → ℕ := fun L => ([0, 0, 4, 8, 8, 4, 96, 0]:List ℕ).getD L 0
def molW8 : ℕ → List (ℕ × ℕ) := fun L => ([[], [(28, 37), (36, 27), (68, 5), (72, 22), (104, 10), (112, 32), (124, 31), (138, 9), (150, 31), (166, 30), (186, 30), (206, 30), (210, 30), (234, 31), (246, 9), (262, 19), (282, 40), (290, 13), (302, 10), (318, 18), (322, 23), (350, 18), (358, 35), (370, 10), (378, 14), (392, 28), (428, 28), (432, 44), (448, 12), (460, 16), (468, 44), (488, 16), (508, 12)], [(12, 5), (24, 1), (48, 5), (100, 1), (120, 5), (124, 5), (158, 1), (194, 1), (198, 2), (222, 2), (230, 3), (254, 3), (258, 1), (262, 5), (318, 5), (382, 1), (396, 1), (408, 4), (412, 4), (432, 1), (444, 1), (448, 3), (456, 2), (460, 2), (480, 5), (484, 1), (492, 2), (496, 6)], [(28, 6), (56, 12), (60, 1), (92, 1), (96, 1), (112, 6), (124, 6), (142, 2), (226, 2), (238, 4), (254, 8), (258, 2), (270, 6), (286, 6), (382, 2), (384, 7), (396, 4), (444, 3), (448, 12), (476, 3), (480, 9), (496, 6), (500, 4), (504, 16)], [(28, 1), (48, 1), (60, 4), (80, 1), (120, 4), (124, 1), (158, 1), (190, 1), (222, 1), (242, 2), (254, 3), (258, 2), (270, 2), (286, 2), (382, 2), (384, 3), (396, 1), (432, 2), (448, 4), (464, 2), (480, 7), (492, 1), (500, 4), (504, 8)], [(60, 1), (120, 1), (124, 2), (190, 1), (250, 1), (254, 2), (258, 1), (262, 1), (318, 1), (382, 1), (392, 1), (400, 1), (416, 1), (448, 3), (476, 1), (480, 4), (492, 1), (496, 4), (500, 1), (504, 3)], [(20, 2), (28, 4), (36, 4), (56, 4), (80, 8), (104, 2), (108, 8), (124, 30), (254, 96), (258, 48), (382, 48), (392, 2), (396, 31), (400, 23), (416, 25), (432, 8), (444, 7), (448, 125), (476, 11), (480, 100), (492, 5), (496, 61), (500, 42), (504, 136)], [(1, 1), (256, 1), (257, 1), (384, 2), (448, 2), (480, 2), (496, 2), (504, 2), (508, 2)]] : List (List (ℕ × ℕ))).getD L []
theorem hdec8_1 : ∀ i, i ≤ 8 → ∀ j, j ≤ 8 →
    decVal (molW8 1) i j = molD8 1 * min 1 (dh i j) + molE8 1 * min 1 (dh i j) := by decide +kernel
theorem hdec8_2 : ∀ i, i ≤ 8 → ∀ j, j ≤ 8 →
    decVal (molW8 2) i j = molD8 2 * min 2 (dh i j) + molE8 2 * min 1 (dh i j) := by decide +kernel
theorem hdec8_3 : ∀ i, i ≤ 8 → ∀ j, j ≤ 8 →
    decVal (molW8 3) i j = molD8 3 * min 3 (dh i j) + molE8 3 * min 1 (dh i j) := by decide +kernel
theorem hdec8_4 : ∀ i, i ≤ 8 → ∀ j, j ≤ 8 →
    decVal (molW8 4) i j = molD8 4 * min 4 (dh i j) + molE8 4 * min 1 (dh i j) := by decide +kernel
theorem hdec8_5 : ∀ i, i ≤ 8 → ∀ j, j ≤ 8 →
    decVal (molW8 5) i j = molD8 5 * min 5 (dh i j) + molE8 5 * min 1 (dh i j) := by decide +kernel
theorem hdec8_6 : ∀ i, i ≤ 8 → ∀ j, j ≤ 8 →
    decVal (molW8 6) i j = molD8 6 * min 6 (dh i j) + molE8 6 * min 1 (dh i j) := by decide +kernel
theorem hdec8_7 : ∀ i, i ≤ 8 → ∀ j, j ≤ 8 →
    decVal (molW8 7) i j = molD8 7 * min 7 (dh i j) + molE8 7 * min 1 (dh i j) := by decide +kernel
theorem hD8 : ∀ L, L ≤ 8 - 1 → 1 ≤ L → 0 < molD8 L := by decide +kernel
theorem hdec8 : ∀ L, L ≤ 8 - 1 → 1 ≤ L → ∀ i, i ≤ 8 → ∀ j, j ≤ 8 →
    decVal (molW8 L) i j = molD8 L * min L (dh i j) + molE8 L * min 1 (dh i j) := by
  intro L h2 h1
  have h2' : L ≤ 7 := h2
  interval_cases L
  exacts [hdec8_1, hdec8_2, hdec8_3, hdec8_4, hdec8_5, hdec8_6, hdec8_7]
theorem hsep8 : ∀ L, L ≤ 8 - 2 → 1 ≤ L → molD8 L + molE8 L ≤ 2 * sepValH 8 (molW8 L) := by decide +kernel
/-- the molecule certificate at label rank 8 -/
def md8 : MolData 8 :=
  ⟨molD8, molE8, molW8, hD8, hdec8, hsep8, by decide +kernel, by decide +kernel⟩

end PriceH
