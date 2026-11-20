/-
PriceHI6 (lane PRICEH, Nov 20).  Molecule certificates (cards/WILD/NOVEL/priceh/mol_h*.json, gen.py; Fractions-verified by verify.py)
as MolData h for label ranks h in [6], each field checked by decide+kernel; `md<h>` : MolData h (instances of PriceHRung.rung_port_h).
Kernel only.
-/
import Nov15.PriceH
import Mathlib.Tactic.IntervalCases

set_option maxRecDepth 100000
set_option linter.unusedVariables false

namespace PriceH
open BankNC0

def molD6 : ℕ → ℕ := fun L => ([0, 4, 12, 4, 2, 2]:List ℕ).getD L 0
def molE6 : ℕ → ℕ := fun L => ([0, 0, 4, 4, 2, 0]:List ℕ).getD L 0
def molW6 : ℕ → List (ℕ × ℕ) := fun L => ([[], [(28, 1), (42, 1), (54, 1), (70, 1), (90, 1), (108, 1), (112, 1)], [(12, 5), (16, 2), (24, 3), (28, 2), (38, 1), (50, 1), (54, 2), (62, 4), (66, 1), (70, 3), (78, 3), (94, 1), (96, 5), (100, 2), (112, 3), (120, 5), (124, 5)], [(12, 1), (24, 1), (28, 2), (46, 1), (58, 1), (62, 2), (66, 1), (70, 1), (78, 1), (94, 1), (96, 2), (104, 1), (112, 3), (116, 1), (120, 3), (124, 2)], [(28, 1), (62, 2), (66, 1), (94, 1), (96, 1), (108, 1), (112, 2), (116, 1), (120, 3)], [(1, 1), (64, 1), (65, 1), (96, 2), (112, 2), (120, 2), (124, 2)]] : List (List (ℕ × ℕ))).getD L []
theorem hdec6_1 : ∀ i, i ≤ 6 → ∀ j, j ≤ 6 →
    decVal (molW6 1) i j = molD6 1 * min 1 (dh i j) + molE6 1 * min 1 (dh i j) := by decide +kernel
theorem hdec6_2 : ∀ i, i ≤ 6 → ∀ j, j ≤ 6 →
    decVal (molW6 2) i j = molD6 2 * min 2 (dh i j) + molE6 2 * min 1 (dh i j) := by decide +kernel
theorem hdec6_3 : ∀ i, i ≤ 6 → ∀ j, j ≤ 6 →
    decVal (molW6 3) i j = molD6 3 * min 3 (dh i j) + molE6 3 * min 1 (dh i j) := by decide +kernel
theorem hdec6_4 : ∀ i, i ≤ 6 → ∀ j, j ≤ 6 →
    decVal (molW6 4) i j = molD6 4 * min 4 (dh i j) + molE6 4 * min 1 (dh i j) := by decide +kernel
theorem hdec6_5 : ∀ i, i ≤ 6 → ∀ j, j ≤ 6 →
    decVal (molW6 5) i j = molD6 5 * min 5 (dh i j) + molE6 5 * min 1 (dh i j) := by decide +kernel
theorem hD6 : ∀ L, L ≤ 6 - 1 → 1 ≤ L → 0 < molD6 L := by decide +kernel
theorem hdec6 : ∀ L, L ≤ 6 - 1 → 1 ≤ L → ∀ i, i ≤ 6 → ∀ j, j ≤ 6 →
    decVal (molW6 L) i j = molD6 L * min L (dh i j) + molE6 L * min 1 (dh i j) := by
  intro L h2 h1
  have h2' : L ≤ 5 := h2
  interval_cases L
  exacts [hdec6_1, hdec6_2, hdec6_3, hdec6_4, hdec6_5]
theorem hsep6 : ∀ L, L ≤ 6 - 2 → 1 ≤ L → molD6 L + molE6 L ≤ 2 * sepValH 6 (molW6 L) := by decide +kernel
/-- the molecule certificate at label rank 6 -/
def md6 : MolData 6 :=
  ⟨molD6, molE6, molW6, hD6, hdec6, hsep6, by decide +kernel, by decide +kernel⟩

end PriceH
