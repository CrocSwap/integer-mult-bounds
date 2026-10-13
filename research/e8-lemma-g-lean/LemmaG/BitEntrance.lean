/-
Bit-side transfer of the entrance step: for the doubled-address frame operator
`D_P = [[1 - P, P], [P, 1 - P]]`, `D_1 · D_P = D_{1-P}` (the entrance `D_I D_E = D_{E⊥}`), and
`D_{gᵀ P g} = diag(g, g)ᵀ · D_P · diag(g, g)` for every `g` with `gᵀ g = 1`.  Both hold for every
square matrix `P` over every commutative ring; nothing about roots or the field is used.
Apache-2.0.  Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
-/
import Mathlib.Data.Matrix.Block

namespace LemmaG

open Matrix

variable {n R : Type*} [Fintype n] [DecidableEq n] [CommRing R]

/-- The bit-side frame operator on the doubled address space. -/
def Dbit (P : Matrix n n R) : Matrix (n ⊕ n) (n ⊕ n) R := fromBlocks (1 - P) P P (1 - P)

/-- `D_I · D_E = D_{E⊥}` with `P_{E⊥} = 1 - P_E`. -/
theorem Dbit_one_mul (P : Matrix n n R) : Dbit 1 * Dbit P = Dbit (1 - P) := by
  simp [Dbit, fromBlocks_multiply]

/-- Conjugation by `diag(g, g)` for `gᵀ g = 1`. -/
theorem Dbit_conj (g P : Matrix n n R) (hg : gᵀ * g = 1) :
    (fromBlocks g 0 0 g)ᵀ * Dbit P * fromBlocks g 0 0 g = Dbit (gᵀ * P * g) := by
  simp only [Dbit, fromBlocks_transpose, transpose_zero, fromBlocks_multiply, Matrix.mul_zero,
    Matrix.zero_mul, add_zero, zero_add, Matrix.mul_sub, Matrix.sub_mul, Matrix.mul_one,
    Matrix.mul_assoc, hg]
  simp only [← Matrix.mul_assoc, hg, sub_self, add_zero, zero_add]

end LemmaG
