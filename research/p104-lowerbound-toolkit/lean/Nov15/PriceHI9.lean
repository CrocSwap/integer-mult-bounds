/-
PriceHI9 (lane PRICEH, Nov 20).  Molecule certificates (cards/WILD/NOVEL/priceh/mol_h*.json, gen.py; Fractions-verified by verify.py)
as MolData h for label ranks h in [9], each field checked by decide+kernel; `md<h>` : MolData h (instances of PriceHRung.rung_port_h).
Kernel only.
-/
import Nov15.PriceH
import Mathlib.Tactic.IntervalCases

set_option maxRecDepth 100000
set_option linter.unusedVariables false

namespace PriceH
open BankNC0

def molD9 : ℕ → ℕ := fun L => ([0, 4293256, 12, 168, 2, 12, 16, 12, 2]:List ℕ).getD L 0
def molE9 : ℕ → ℕ := fun L => ([0, 0, 0, 56, 0, 12, 16, 12, 0]:List ℕ).getD L 0
def molW9 : ℕ → List (ℕ × ℕ) := fun L => ([[], [(28, 177064), (52, 132680), (56, 51355), (84, 279774), (104, 240080), (112, 179121), (148, 228897), (160, 239602), (172, 230476), (200, 349916), (220, 24423), (258, 309085), (282, 211565), (302, 234087), (350, 39008), (374, 279569), (394, 28996), (446, 289581), (454, 231069), (466, 253591), (490, 270077), (522, 95515), (538, 251294), (550, 121307), (562, 109548), (590, 411010), (610, 84640), (646, 315495), (702, 180155), (750, 45347), (754, 442324), (762, 89993), (800, 439888), (836, 197776), (856, 161297), (892, 274353), (900, 118937), (920, 396540), (948, 117949), (960, 75589), (980, 123175), (1004, 241124)], [(24, 3), (60, 4), (96, 3), (192, 2), (204, 2), (240, 2), (390, 3), (510, 3), (518, 3), (638, 3), (768, 2), (780, 2), (816, 2), (920, 3), (972, 2), (992, 3), (1008, 2), (1020, 2)], [(56, 42), (68, 8), (112, 41), (116, 2), (120, 44), (140, 1), (184, 10), (196, 2), (252, 85), (382, 14), (398, 14), (454, 14), (478, 28), (494, 28), (506, 14), (514, 14), (526, 42), (574, 42), (766, 14), (772, 2), (780, 1), (796, 84), (824, 8), (888, 2), (892, 1), (896, 51), (904, 26), (956, 10), (960, 60), (992, 84), (1008, 69), (1016, 50)], [(60, 1), (120, 1), (240, 1), (510, 1), (542, 1), (768, 1), (896, 1), (960, 1), (992, 1), (1008, 1), (1016, 1), (1020, 1)], [(52, 1), (60, 1), (120, 2), (124, 6), (184, 2), (216, 1), (232, 1), (240, 3), (248, 1), (252, 1), (318, 3), (498, 3), (510, 6), (514, 3), (526, 3), (574, 3), (766, 3), (772, 1), (784, 2), (800, 2), (832, 4), (896, 10), (960, 4), (976, 1), (988, 2), (992, 13), (1004, 2), (1008, 4), (1012, 4), (1016, 11)], [(8, 5), (60, 1), (116, 2), (120, 2), (204, 1), (240, 3), (244, 1), (252, 7), (382, 4), (506, 4), (510, 8), (514, 4), (518, 4), (638, 4), (766, 4), (768, 7), (772, 1), (832, 1), (880, 3), (896, 7), (908, 2), (944, 7), (960, 14), (976, 8), (992, 24), (1016, 13), (1020, 9)], [(76, 1), (112, 1), (140, 1), (176, 1), (252, 4), (510, 12), (514, 6), (766, 6), (780, 4), (816, 4), (832, 3), (892, 1), (896, 15), (956, 1), (960, 8), (976, 6), (992, 18), (1012, 6), (1016, 18)], [(1, 1), (512, 1), (513, 1), (768, 2), (896, 2), (960, 2), (992, 2), (1008, 2), (1016, 2), (1020, 2)]] : List (List (ℕ × ℕ))).getD L []
theorem hdec9_1 : ∀ i, i ≤ 9 → ∀ j, j ≤ 9 →
    decVal (molW9 1) i j = molD9 1 * min 1 (dh i j) + molE9 1 * min 1 (dh i j) := by decide +kernel
theorem hdec9_2 : ∀ i, i ≤ 9 → ∀ j, j ≤ 9 →
    decVal (molW9 2) i j = molD9 2 * min 2 (dh i j) + molE9 2 * min 1 (dh i j) := by decide +kernel
theorem hdec9_3 : ∀ i, i ≤ 9 → ∀ j, j ≤ 9 →
    decVal (molW9 3) i j = molD9 3 * min 3 (dh i j) + molE9 3 * min 1 (dh i j) := by decide +kernel
theorem hdec9_4 : ∀ i, i ≤ 9 → ∀ j, j ≤ 9 →
    decVal (molW9 4) i j = molD9 4 * min 4 (dh i j) + molE9 4 * min 1 (dh i j) := by decide +kernel
theorem hdec9_5 : ∀ i, i ≤ 9 → ∀ j, j ≤ 9 →
    decVal (molW9 5) i j = molD9 5 * min 5 (dh i j) + molE9 5 * min 1 (dh i j) := by decide +kernel
theorem hdec9_6 : ∀ i, i ≤ 9 → ∀ j, j ≤ 9 →
    decVal (molW9 6) i j = molD9 6 * min 6 (dh i j) + molE9 6 * min 1 (dh i j) := by decide +kernel
theorem hdec9_7 : ∀ i, i ≤ 9 → ∀ j, j ≤ 9 →
    decVal (molW9 7) i j = molD9 7 * min 7 (dh i j) + molE9 7 * min 1 (dh i j) := by decide +kernel
theorem hdec9_8 : ∀ i, i ≤ 9 → ∀ j, j ≤ 9 →
    decVal (molW9 8) i j = molD9 8 * min 8 (dh i j) + molE9 8 * min 1 (dh i j) := by decide +kernel
theorem hD9 : ∀ L, L ≤ 9 - 1 → 1 ≤ L → 0 < molD9 L := by decide +kernel
theorem hdec9 : ∀ L, L ≤ 9 - 1 → 1 ≤ L → ∀ i, i ≤ 9 → ∀ j, j ≤ 9 →
    decVal (molW9 L) i j = molD9 L * min L (dh i j) + molE9 L * min 1 (dh i j) := by
  intro L h2 h1
  have h2' : L ≤ 8 := h2
  interval_cases L
  exacts [hdec9_1, hdec9_2, hdec9_3, hdec9_4, hdec9_5, hdec9_6, hdec9_7, hdec9_8]
theorem hsep9 : ∀ L, L ≤ 9 - 2 → 1 ≤ L → molD9 L + molE9 L ≤ 2 * sepValH 9 (molW9 L) := by decide +kernel
/-- the molecule certificate at label rank 9 -/
def md9 : MolData 9 :=
  ⟨molD9, molE9, molW9, hD9, hdec9, hsep9, by decide +kernel, by decide +kernel⟩

end PriceH
