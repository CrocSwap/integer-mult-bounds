/-
PriceHI4 (lane PRICEH, Nov 20).  Molecule certificates (cards/WILD/NOVEL/priceh/mol_h*.json, gen.py; Fractions-verified by verify.py)
as MolData h for label ranks h in [4], each field checked by decide+kernel; `md<h>` : MolData h (instances of PriceHRung.rung_port_h).
Kernel only.
-/
import Nov15.PriceH
import Mathlib.Tactic.IntervalCases

set_option maxRecDepth 100000
set_option linter.unusedVariables false

namespace PriceH
open BankNC0

def molD4 : ℕ → ℕ := fun L => ([0, 4, 2, 2]:List ℕ).getD L 0
def molE4 : ℕ → ℕ := fun L => ([0, 0, 2, 0]:List ℕ).getD L 0
def molW4 : ℕ → List (ℕ × ℕ) := fun L => ([[], [(4, 1), (10, 1), (14, 1), (18, 1), (22, 1), (24, 1), (28, 1)], [(4, 1), (14, 2), (18, 1), (22, 1), (24, 2), (28, 2)], [(1, 1), (16, 1), (17, 1), (24, 2), (28, 2)]] : List (List (ℕ × ℕ))).getD L []
theorem hdec4_1 : ∀ i, i ≤ 4 → ∀ j, j ≤ 4 →
    decVal (molW4 1) i j = molD4 1 * min 1 (dh i j) + molE4 1 * min 1 (dh i j) := by decide +kernel
theorem hdec4_2 : ∀ i, i ≤ 4 → ∀ j, j ≤ 4 →
    decVal (molW4 2) i j = molD4 2 * min 2 (dh i j) + molE4 2 * min 1 (dh i j) := by decide +kernel
theorem hdec4_3 : ∀ i, i ≤ 4 → ∀ j, j ≤ 4 →
    decVal (molW4 3) i j = molD4 3 * min 3 (dh i j) + molE4 3 * min 1 (dh i j) := by decide +kernel
theorem hD4 : ∀ L, L ≤ 4 - 1 → 1 ≤ L → 0 < molD4 L := by decide +kernel
theorem hdec4 : ∀ L, L ≤ 4 - 1 → 1 ≤ L → ∀ i, i ≤ 4 → ∀ j, j ≤ 4 →
    decVal (molW4 L) i j = molD4 L * min L (dh i j) + molE4 L * min 1 (dh i j) := by
  intro L h2 h1
  have h2' : L ≤ 3 := h2
  interval_cases L
  exacts [hdec4_1, hdec4_2, hdec4_3]
theorem hsep4 : ∀ L, L ≤ 4 - 2 → 1 ≤ L → molD4 L + molE4 L ≤ 2 * sepValH 4 (molW4 L) := by decide +kernel
/-- the molecule certificate at label rank 4 -/
def md4 : MolData 4 :=
  ⟨molD4, molE4, molW4, hD4, hdec4, hsep4, by decide +kernel, by decide +kernel⟩

end PriceH
