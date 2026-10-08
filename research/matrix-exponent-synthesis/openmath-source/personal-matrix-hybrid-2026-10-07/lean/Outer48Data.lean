import Mathlib.Data.Fin.VecNotation
import Mathlib.Data.Fintype.BigOperators
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Ring

/-!
Mathematical coefficient data for the publicly pinned48-product outer.
Source:spicylemonade/faster_16x16,commit7743ee6848ed876615012c4edb3bc46a1f870afd.
Source byteSHA256:a0dd1675fa9f8389230db4dc376639ee20b0f9786765b9e75abc60c14844f0ef.
Reconstructed from ordered leftA/rightB linear forms and output coefficients.
Input and output coordinates use row-major4*row+col. This is an integer tensor
certificate, not yet the generic coefficient-domain lifting or hybrid theorem.
Prepared source: actual Lean compilation/axiom inspection is a separate step.
-/
namespace PersonalMatrix.Outer48
open scoped BigOperators
set_option autoImplicit false
set_option maxHeartbeats 0

def alphaDenominator : ℤ := 1
def betaDenominator : ℤ := 1
def gammaDenominator : ℤ := 8
def commonDenominator : ℤ := 8

def alphaInteger : Fin 48 → Fin 16 → ℤ :=
![
  ![-1, 1, 1, 1, -1, 1, 1, 1, 1, -1, -1, -1, -1, 1, 1, 1],
  ![-1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, -1, 0, 0, 0],
  ![0, 0, -1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
  ![0, 0, -1, -1, 0, 0, -1, -1, 0, 0, 1, -1, 0, 0, 1, -1],
  ![1, 1, 1, -1, -1, -1, -1, 1, 1, 1, 1, -1, 1, 1, 1, -1],
  ![1, 1, -1, 1, -1, -1, 1, -1, -1, -1, 1, -1, 1, 1, -1, 1],
  ![0, 0, 0, -1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
  ![1, 1, 1, -1, -1, -1, -1, 1, 1, 1, 1, -1, -1, -1, -1, 1],
  ![0, 0, -1, -1, 0, 0, 1, 1, -1, 1, 0, 0, -1, 1, 0, 0],
  ![1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, -1, 0, 0, 0],
  ![-1, -1, -1, 1, 1, 1, 1, -1, 1, 1, 1, -1, -1, -1, -1, 1],
  ![0, 1, 0, 1, -1, 0, 1, 0, 0, 1, 0, 1, -1, 0, 1, 0],
  ![0, 0, 1, 0, 0, 0, -1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
  ![0, 0, 1, 0, 0, 0, 1, 0, 0, 0, -1, 0, 0, 0, -1, 0],
  ![1, 0, 1, 0, 1, 0, -1, 0, -1, 0, -1, 0, 1, 0, -1, 0],
  ![1, 1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, -1, -1, 1, -1],
  ![1, 1, 0, 0, 1, 1, 0, 0, -1, 1, 0, 0, -1, 1, 0, 0],
  ![-1, 1, 1, 1, -1, 1, 1, 1, 1, -1, -1, -1, 1, -1, -1, -1],
  ![0, 1, 0, 1, -1, 0, 1, 0, 0, -1, 0, -1, 1, 0, -1, 0],
  ![-1, 1, -1, -1, -1, 1, -1, -1, 1, -1, 1, 1, 1, -1, 1, 1],
  ![0, 0, 1, 0, 0, 0, -1, 0, 0, 0, -1, 0, 0, 0, 1, 0],
  ![1, 0, 1, 0, 0, -1, 0, 1, 1, 0, 1, 0, 0, -1, 0, 1],
  ![0, 0, 0, 1, 0, 0, 0, -1, 0, 0, 0, 1, 0, 0, 0, 1],
  ![1, -1, 1, 1, -1, 1, -1, -1, 1, -1, 1, 1, 1, -1, 1, 1],
  ![1, 1, 0, 0, -1, -1, 0, 0, 0, 0, 1, -1, 0, 0, 1, -1],
  ![1, -1, 1, 1, 1, -1, 1, 1, 1, -1, 1, 1, -1, 1, -1, -1],
  ![0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0],
  ![0, 0, 1, 1, 0, 0, 1, 1, 1, -1, 0, 0, -1, 1, 0, 0],
  ![1, -1, -1, -1, -1, 1, 1, 1, -1, 1, 1, 1, -1, 1, 1, 1],
  ![0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
  ![0, 1, 0, 0, 0, -1, 0, 0, 0, 1, 0, 0, 0, -1, 0, 0],
  ![1, 0, 1, 0, 0, -1, 0, 1, -1, 0, -1, 0, 0, 1, 0, -1],
  ![-1, -1, 1, -1, 1, 1, -1, 1, 1, 1, -1, 1, 1, 1, -1, 1],
  ![0, 0, -1, -1, 0, 0, 1, 1, 0, 0, 1, -1, 0, 0, -1, 1],
  ![1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, -1, 0, 0, -1, 1],
  ![1, -1, 1, 1, 1, -1, 1, 1, 1, -1, 1, 1, 1, -1, 1, 1],
  ![0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, -1, 0, 0],
  ![0, 1, 0, 1, 0, 1, 0, -1, 0, 1, 0, 1, 0, -1, 0, 1],
  ![0, 1, 0, 0, 0, 1, 0, 0, 0, -1, 0, 0, 0, 1, 0, 0],
  ![-1, -1, 0, 0, 1, 1, 0, 0, 1, -1, 0, 0, -1, 1, 0, 0],
  ![-1, 1, 1, 1, -1, 1, 1, 1, -1, 1, 1, 1, -1, 1, 1, 1],
  ![0, 0, 0, 1, 0, 0, 0, -1, 0, 0, 0, 1, 0, 0, 0, -1],
  ![1, 0, 0, 0, 1, 0, 0, 0, -1, 0, 0, 0, 1, 0, 0, 0],
  ![1, 0, 1, 0, 1, 0, -1, 0, 1, 0, 1, 0, -1, 0, 1, 0],
  ![1, 1, -1, 1, 1, 1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1],
  ![1, 1, 1, -1, 1, 1, 1, -1, 1, 1, 1, -1, -1, -1, -1, 1],
  ![-1, 0, 0, 0, -1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
  ![0, -1, 0, -1, 0, -1, 0, 1, 0, 1, 0, 1, 0, -1, 0, 1]
]

def betaInteger : Fin 48 → Fin 16 → ℤ :=
![
  ![0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
  ![0, 1, 0, 1, 0, -1, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0],
  ![0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
  ![0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, -1, 0],
  ![-1, 0, 1, 1, -1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
  ![0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
  ![0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0],
  ![1, 0, 0, -1, 0, 0, 0, 0, 1, 0, 0, -1, 0, 0, 0, 0],
  ![1, 1, -1, -1, -1, -1, 1, 1, -1, 1, 1, 1, -1, 1, 1, 1],
  ![0, 1, 1, 1, 0, 0, 0, 0, 0, -1, -1, -1, 0, 0, 0, 0],
  ![0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, -1, 0, -1],
  ![-1, -1, -1, 1, 1, -1, -1, -1, 1, 1, 1, -1, 1, -1, -1, -1],
  ![1, 0, -1, -1, 0, 0, 0, 0, -1, 0, 1, 1, 0, 0, 0, 0],
  ![0, 0, 0, 0, 0, 0, 0, 0, 1, 0, -1, 0, -1, 0, 1, 0],
  ![0, 1, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0],
  ![1, 0, 0, -1, 0, 0, 0, 0, -1, 0, 0, 1, 0, 0, 0, 0],
  ![0, -1, -1, 0, 1, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  ![0, 0, 0, 0, 1, 0, -1, 0, 0, 0, 0, 0, 1, 0, -1, 0],
  ![1, -1, -1, -1, 1, 1, -1, 1, -1, 1, 1, 1, 1, 1, -1, 1],
  ![0, 0, 0, 0, -1, 0, 1, 0, 0, 0, 0, 0, 1, 0, -1, 0],
  ![0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1],
  ![1, 1, 1, -1, -1, 1, 1, 1, 1, 1, 1, -1, 1, -1, -1, -1],
  ![0, 0, 0, 0, -1, 0, 1, 1, 0, 0, 0, 0, -1, 0, 1, 1],
  ![1, 0, -1, -1, -1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
  ![1, 1, -1, -1, 1, 1, -1, -1, -1, 1, 1, 1, 1, -1, -1, -1],
  ![0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1],
  ![0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  ![1, -1, -1, -1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
  ![0, -1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  ![0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, 0, 0, 1, 1, 0],
  ![1, 0, 0, -1, -1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
  ![1, -1, -1, -1, 1, 1, -1, 1, 1, -1, -1, -1, -1, -1, 1, -1],
  ![0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  ![0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 1, 0, 1, 0, 1],
  ![-1, 1, 1, 1, -1, 1, 1, 1, -1, -1, -1, -1, 1, 1, 1, 1],
  ![0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
  ![0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1],
  ![0, 0, 0, 0, -1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1],
  ![0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
  ![1, 0, 0, -1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
  ![0, 1, 1, 0, 0, 0, 0, 0, 0, -1, -1, 0, 0, 0, 0, 0],
  ![0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, -1, 1, 0, 0, -1],
  ![1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
  ![1, 0, -1, -1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
  ![0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 1, 0, 0, 0],
  ![0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, -1, -1, -1],
  ![1, 0, -1, 0, 1, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  ![0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
]

def gammaNumerator : Fin 48 → Fin 16 → ℤ :=
![
  ![0, 0, 0, 0, 0, 0, 0, 0, -2, 2, 0, -2, 2, -2, 0, 2],
  ![-4, 0, 0, -4, 4, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0],
  ![0, 0, 0, 0, 0, 4, -4, 0, 0, 0, 0, 0, 0, 4, -4, 0],
  ![0, -4, 2, 2, 0, -4, 2, 2, 0, 0, 2, -2, 0, 0, 2, -2],
  ![0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2],
  ![0, 0, 0, 0, 2, -2, 2, 0, 0, 0, 0, 0, -2, 2, -2, 0],
  ![0, 4, 0, -4, 0, 0, 0, 0, 0, -4, 0, 4, 0, 0, 0, 0],
  ![0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2],
  ![1, -1, -1, 1, -1, 1, 1, -1, 1, -1, 1, 1, 1, -1, 1, 1],
  ![4, 0, 0, 4, 0, 0, 0, 0, 4, 0, 0, 4, 0, 0, 0, 0],
  ![0, 0, 0, -2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0],
  ![2, -2, 1, 1, 0, 0, 1, -1, 2, -2, 1, 1, 0, 0, 1, -1],
  ![0, -4, 4, 0, 0, 0, 0, 0, 0, -4, 4, 0, 0, 0, 0, 0],
  ![0, 4, -4, 0, 0, 4, -4, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  ![-2, 2, -2, -2, 2, 2, -2, 2, 2, -2, 2, 2, 2, 2, -2, 2],
  ![2, -2, 2, 0, 0, 0, 0, 0, 2, -2, 2, 0, 0, 0, 0, 0],
  ![0, 0, -2, 2, 0, 0, -2, 2, 4, 0, 2, 2, 4, 0, 2, 2],
  ![0, 0, 0, 0, 2, -2, 0, 2, 0, 0, 0, 0, -2, 2, 0, -2],
  ![0, 0, -1, 1, -2, 2, -1, -1, 0, 0, 1, -1, 2, -2, 1, 1],
  ![0, 0, 2, 0, 0, 0, 0, 0, 0, 0, -2, 0, 0, 0, 0, 0],
  ![0, 0, 0, 0, 0, 0, 0, 0, 0, -4, 4, 0, 0, 4, -4, 0],
  ![0, 0, 1, -1, 0, 0, -1, -1, 0, 0, 1, -1, 0, 0, -1, -1],
  ![0, 0, 0, 0, 0, 4, 0, -4, 0, 0, 0, 0, 0, -4, 0, 4],
  ![0, 0, -2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  ![-1, 1, -1, -1, 1, -1, 1, 1, -1, 1, -1, 1, -1, 1, -1, 1],
  ![0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, -2, 0],
  ![0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 4, 0, 4, 0, 4, 0],
  ![1, -1, 1, 1, 1, -1, 1, 1, 1, -1, -1, 1, -1, 1, 1, -1],
  ![2, -2, 0, 2, -2, 2, 0, -2, 0, 0, 0, 0, 0, 0, 0, 0],
  ![0, 4, 0, -4, 0, 4, 0, -4, 0, 0, 0, 0, 0, 0, 0, 0],
  ![-4, 0, -4, 0, 4, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  ![0, 0, -1, -1, 0, 0, 1, -1, 0, 0, 1, 1, 0, 0, -1, 1],
  ![0, 0, 0, 0, 0, 0, 0, 0, -2, 2, -2, 0, -2, 2, -2, 0],
  ![0, 0, 2, -2, 0, 0, -2, 2, 0, -4, 2, 2, 0, 4, -2, -2],
  ![-1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, -1, 1, -1, 1, 1],
  ![0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0],
  ![0, 0, 0, 0, 4, 0, 4, 0, 0, 0, 0, 0, -4, 0, -4, 0],
  ![2, -2, 2, 2, -2, -2, -2, 2, 2, -2, 2, 2, 2, 2, 2, -2],
  ![-4, 0, -4, 0, 0, 0, 0, 0, 4, 0, 4, 0, 0, 0, 0, 0],
  ![-4, 0, -2, -2, 4, 0, 2, 2, 0, 0, 2, -2, 0, 0, -2, 2],
  ![2, -2, 0, 2, 0, 0, 0, 0, 2, -2, 0, 2, 0, 0, 0, 0],
  ![0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, -4, 0, -4, 0, 4],
  ![0, 0, 0, 0, 4, 0, 0, 4, 0, 0, 0, 0, 4, 0, 0, 4],
  ![2, 2, -2, 2, -2, 2, -2, -2, 2, 2, -2, 2, 2, -2, 2, 2],
  ![2, -2, 2, 0, 2, -2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  ![0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0],
  ![0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 4, 4, 0, 0, 4],
  ![-2, -2, -2, 2, 2, -2, 2, 2, 2, 2, 2, -2, 2, -2, 2, 2]
]

def target (i j o : Fin 16) : ℤ :=
  if i.val / 4 = o.val / 4 ∧ j.val % 4 = o.val % 4 ∧ i.val % 4 = j.val / 4
    then 1 else 0

def tensorNumerator (i j o : Fin 16) : ℤ :=
  ∑ t : Fin 48, alphaInteger t i * betaInteger t j * gammaNumerator t o

private theorem certificate_00 : ∀ i j : Fin 16,
    tensorNumerator i j (0 : Fin 16) = 8 * target i j (0 : Fin 16) := by
  decide +kernel

private theorem certificate_01 : ∀ i j : Fin 16,
    tensorNumerator i j (1 : Fin 16) = 8 * target i j (1 : Fin 16) := by
  decide +kernel

private theorem certificate_02 : ∀ i j : Fin 16,
    tensorNumerator i j (2 : Fin 16) = 8 * target i j (2 : Fin 16) := by
  decide +kernel

private theorem certificate_03 : ∀ i j : Fin 16,
    tensorNumerator i j (3 : Fin 16) = 8 * target i j (3 : Fin 16) := by
  decide +kernel

private theorem certificate_04 : ∀ i j : Fin 16,
    tensorNumerator i j (4 : Fin 16) = 8 * target i j (4 : Fin 16) := by
  decide +kernel

private theorem certificate_05 : ∀ i j : Fin 16,
    tensorNumerator i j (5 : Fin 16) = 8 * target i j (5 : Fin 16) := by
  decide +kernel

private theorem certificate_06 : ∀ i j : Fin 16,
    tensorNumerator i j (6 : Fin 16) = 8 * target i j (6 : Fin 16) := by
  decide +kernel

private theorem certificate_07 : ∀ i j : Fin 16,
    tensorNumerator i j (7 : Fin 16) = 8 * target i j (7 : Fin 16) := by
  decide +kernel

private theorem certificate_08 : ∀ i j : Fin 16,
    tensorNumerator i j (8 : Fin 16) = 8 * target i j (8 : Fin 16) := by
  decide +kernel

private theorem certificate_09 : ∀ i j : Fin 16,
    tensorNumerator i j (9 : Fin 16) = 8 * target i j (9 : Fin 16) := by
  decide +kernel

private theorem certificate_10 : ∀ i j : Fin 16,
    tensorNumerator i j (10 : Fin 16) = 8 * target i j (10 : Fin 16) := by
  decide +kernel

private theorem certificate_11 : ∀ i j : Fin 16,
    tensorNumerator i j (11 : Fin 16) = 8 * target i j (11 : Fin 16) := by
  decide +kernel

private theorem certificate_12 : ∀ i j : Fin 16,
    tensorNumerator i j (12 : Fin 16) = 8 * target i j (12 : Fin 16) := by
  decide +kernel

private theorem certificate_13 : ∀ i j : Fin 16,
    tensorNumerator i j (13 : Fin 16) = 8 * target i j (13 : Fin 16) := by
  decide +kernel

private theorem certificate_14 : ∀ i j : Fin 16,
    tensorNumerator i j (14 : Fin 16) = 8 * target i j (14 : Fin 16) := by
  decide +kernel

private theorem certificate_15 : ∀ i j : Fin 16,
    tensorNumerator i j (15 : Fin 16) = 8 * target i j (15 : Fin 16) := by
  decide +kernel

theorem brent_integer (i j o : Fin 16) :
    tensorNumerator i j o = 8 * target i j o := by
  fin_cases o
  · exact certificate_00 i j
  · exact certificate_01 i j
  · exact certificate_02 i j
  · exact certificate_03 i j
  · exact certificate_04 i j
  · exact certificate_05 i j
  · exact certificate_06 i j
  · exact certificate_07 i j
  · exact certificate_08 i j
  · exact certificate_09 i j
  · exact certificate_10 i j
  · exact certificate_11 i j
  · exact certificate_12 i j
  · exact certificate_13 i j
  · exact certificate_14 i j
  · exact certificate_15 i j

def alphaCommon (t : Fin 48) (i : Fin 16) : ℤ := commonDenominator * alphaInteger t i
def betaCommon (t : Fin 48) (j : Fin 16) : ℤ := commonDenominator * betaInteger t j
def gammaCommon (t : Fin 48) (o : Fin 16) : ℤ := gammaNumerator t o

/-- CommonD=8 for all three legs; their ordered coefficient contraction is D³T. -/
theorem brent_common_denominator (i j o : Fin 16) :
    (∑ t : Fin 48, alphaCommon t i * betaCommon t j * gammaCommon t o) =
      commonDenominator^3 * target i j o := by
  have term (t : Fin 48) :
      alphaCommon t i * betaCommon t j * gammaCommon t o =
      64 * (alphaInteger t i * betaInteger t j * gammaNumerator t o) := by
    dsimp [alphaCommon, betaCommon, gammaCommon, commonDenominator]
    ring
  calc
    (∑ t : Fin 48, alphaCommon t i * betaCommon t j * gammaCommon t o) =
        ∑ t : Fin 48, 64 * (alphaInteger t i * betaInteger t j * gammaNumerator t o) := by
      apply Finset.sum_congr rfl
      intro t _
      exact term t
    _ = 64 * tensorNumerator i j o := by
      unfold tensorNumerator
      rw [Finset.mul_sum]
    _ = commonDenominator^3 * target i j o := by
      rw [brent_integer]
      dsimp [commonDenominator]
      ring

/-- Every scheduled ordered product has a nonzero left coefficient vector. -/
theorem alpha_nonzero : ∀ t : Fin 48, ∃ i : Fin 16, alphaInteger t i ≠ 0 := by
  decide +kernel

theorem beta_nonzero : ∀ t : Fin 48, ∃ j : Fin 16, betaInteger t j ≠ 0 := by
  decide +kernel

theorem gamma_nonzero : ∀ t : Fin 48, ∃ o : Fin 16, gammaNumerator t o ≠ 0 := by
  decide +kernel

#print axioms brent_integer
#print axioms brent_common_denominator
#print axioms alpha_nonzero
#print axioms beta_nonzero
#print axioms gamma_nonzero
#check brent_common_denominator
end PersonalMatrix.Outer48
