/-
PriceHI7 (lane PRICEH, Nov 20).  Molecule certificates (cards/WILD/NOVEL/priceh/mol_h*.json, gen.py; Fractions-verified by verify.py)
as MolData h for label ranks h in [7], each field checked by decide+kernel; `md<h>` : MolData h (instances of PriceHRung.rung_port_h).
Kernel only.
-/
import Nov15.PriceH
import Mathlib.Tactic.IntervalCases

set_option maxRecDepth 100000
set_option linter.unusedVariables false

namespace PriceH
open BankNC0

def molD7 : ℕ → ℕ := fun L => ([0, 192, 4, 2, 4, 2, 2]:List ℕ).getD L 0
def molE7 : ℕ → ℕ := fun L => ([0, 0, 0, 0, 4, 2, 0]:List ℕ).getD L 0
def molW7 : ℕ → List (ℕ × ℕ) := fun L => ([[], [(28, 18), (36, 6), (44, 12), (52, 12), (56, 18), (78, 24), (82, 24), (102, 24), (122, 24), (134, 7), (138, 22), (158, 19), (162, 19), (182, 22), (186, 7), (204, 13), (208, 20), (212, 15), (228, 10), (232, 25), (240, 3), (252, 10)], [(24, 1), (60, 2), (102, 1), (126, 1), (134, 1), (158, 1), (204, 2), (224, 1), (240, 2), (248, 1)], [(28, 1), (56, 1), (126, 1), (142, 1), (192, 1), (224, 1), (240, 1), (248, 1), (252, 1)], [(8, 1), (12, 1), (16, 1), (48, 1), (60, 2), (94, 1), (122, 1), (126, 2), (130, 1), (134, 1), (158, 1), (190, 1), (192, 2), (208, 1), (224, 4), (240, 2), (244, 1), (248, 4), (252, 2)], [(60, 1), (126, 2), (130, 1), (190, 1), (204, 1), (208, 1), (224, 3), (240, 1), (244, 1), (248, 3)], [(1, 1), (128, 1), (129, 1), (192, 2), (224, 2), (240, 2), (248, 2), (252, 2)]] : List (List (ℕ × ℕ))).getD L []
theorem hdec7_1 : ∀ i, i ≤ 7 → ∀ j, j ≤ 7 →
    decVal (molW7 1) i j = molD7 1 * min 1 (dh i j) + molE7 1 * min 1 (dh i j) := by decide +kernel
theorem hdec7_2 : ∀ i, i ≤ 7 → ∀ j, j ≤ 7 →
    decVal (molW7 2) i j = molD7 2 * min 2 (dh i j) + molE7 2 * min 1 (dh i j) := by decide +kernel
theorem hdec7_3 : ∀ i, i ≤ 7 → ∀ j, j ≤ 7 →
    decVal (molW7 3) i j = molD7 3 * min 3 (dh i j) + molE7 3 * min 1 (dh i j) := by decide +kernel
theorem hdec7_4 : ∀ i, i ≤ 7 → ∀ j, j ≤ 7 →
    decVal (molW7 4) i j = molD7 4 * min 4 (dh i j) + molE7 4 * min 1 (dh i j) := by decide +kernel
theorem hdec7_5 : ∀ i, i ≤ 7 → ∀ j, j ≤ 7 →
    decVal (molW7 5) i j = molD7 5 * min 5 (dh i j) + molE7 5 * min 1 (dh i j) := by decide +kernel
theorem hdec7_6 : ∀ i, i ≤ 7 → ∀ j, j ≤ 7 →
    decVal (molW7 6) i j = molD7 6 * min 6 (dh i j) + molE7 6 * min 1 (dh i j) := by decide +kernel
theorem hD7 : ∀ L, L ≤ 7 - 1 → 1 ≤ L → 0 < molD7 L := by decide +kernel
theorem hdec7 : ∀ L, L ≤ 7 - 1 → 1 ≤ L → ∀ i, i ≤ 7 → ∀ j, j ≤ 7 →
    decVal (molW7 L) i j = molD7 L * min L (dh i j) + molE7 L * min 1 (dh i j) := by
  intro L h2 h1
  have h2' : L ≤ 6 := h2
  interval_cases L
  exacts [hdec7_1, hdec7_2, hdec7_3, hdec7_4, hdec7_5, hdec7_6]
theorem hsep7 : ∀ L, L ≤ 7 - 2 → 1 ≤ L → molD7 L + molE7 L ≤ 2 * sepValH 7 (molW7 L) := by decide +kernel
/-- the molecule certificate at label rank 7 -/
def md7 : MolData 7 :=
  ⟨molD7, molE7, molW7, hD7, hdec7, hsep7, by decide +kernel, by decide +kernel⟩

end PriceH
