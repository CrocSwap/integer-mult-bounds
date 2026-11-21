/-
PriceHI5 (lane PRICEH, Nov 20).  Molecule certificates (cards/WILD/NOVEL/priceh/mol_h*.json, gen.py; Fractions-verified by verify.py)
as MolData h for label ranks h in [5], each field checked by decide+kernel; `md<h>` : MolData h (instances of PriceHRung.rung_port_h).
Kernel only.
-/
import Nov15.PriceH
import Mathlib.Tactic.IntervalCases

set_option maxRecDepth 100000
set_option linter.unusedVariables false

namespace PriceH
open BankNC0

def molD5 : ℕ → ℕ := fun L => ([0, 4, 2, 2, 2]:List ℕ).getD L 0
def molE5 : ℕ → ℕ := fun L => ([0, 0, 0, 2, 0]:List ℕ).getD L 0
def molW5 : ℕ → List (ℕ × ℕ) := fun L => ([[], [(12, 1), (22, 1), (26, 1), (34, 1), (46, 1), (52, 1), (56, 1)], [(12, 1), (30, 1), (38, 1), (48, 1), (56, 1), (60, 1)], [(4, 1), (8, 1), (30, 2), (34, 1), (46, 1), (48, 2), (56, 2), (60, 2)], [(1, 1), (32, 1), (33, 1), (48, 2), (56, 2), (60, 2)]] : List (List (ℕ × ℕ))).getD L []
theorem hdec5_1 : ∀ i, i ≤ 5 → ∀ j, j ≤ 5 →
    decVal (molW5 1) i j = molD5 1 * min 1 (dh i j) + molE5 1 * min 1 (dh i j) := by decide +kernel
theorem hdec5_2 : ∀ i, i ≤ 5 → ∀ j, j ≤ 5 →
    decVal (molW5 2) i j = molD5 2 * min 2 (dh i j) + molE5 2 * min 1 (dh i j) := by decide +kernel
theorem hdec5_3 : ∀ i, i ≤ 5 → ∀ j, j ≤ 5 →
    decVal (molW5 3) i j = molD5 3 * min 3 (dh i j) + molE5 3 * min 1 (dh i j) := by decide +kernel
theorem hdec5_4 : ∀ i, i ≤ 5 → ∀ j, j ≤ 5 →
    decVal (molW5 4) i j = molD5 4 * min 4 (dh i j) + molE5 4 * min 1 (dh i j) := by decide +kernel
theorem hD5 : ∀ L, L ≤ 5 - 1 → 1 ≤ L → 0 < molD5 L := by decide +kernel
theorem hdec5 : ∀ L, L ≤ 5 - 1 → 1 ≤ L → ∀ i, i ≤ 5 → ∀ j, j ≤ 5 →
    decVal (molW5 L) i j = molD5 L * min L (dh i j) + molE5 L * min 1 (dh i j) := by
  intro L h2 h1
  have h2' : L ≤ 4 := h2
  interval_cases L
  exacts [hdec5_1, hdec5_2, hdec5_3, hdec5_4]
theorem hsep5 : ∀ L, L ≤ 5 - 2 → 1 ≤ L → molD5 L + molE5 L ≤ 2 * sepValH 5 (molW5 L) := by decide +kernel
/-- the molecule certificate at label rank 5 -/
def md5 : MolData 5 :=
  ⟨molD5, molE5, molW5, hD5, hdec5, hsep5, by decide +kernel, by decide +kernel⟩

end PriceH
