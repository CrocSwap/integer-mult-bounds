/-
Copyright (c) 2026 Andrey Mas and contributors.
SPDX-License-Identifier: Apache-2.0

P112 finite successor to PR1497/PR1610. SOURCE ONLY: NOT YET KERNEL CHECKED.
Formalization assistance: GPT-6 Pro through ChatGPT (operator-selected label).
Only the left sparse-row evaluation needed by this fixed certificate is added.
The imported bridge is preserved byte-for-byte at its supplied published pin.
-/
import PR1497Bridge

set_option autoImplicit false
set_option maxRecDepth 4096
set_option maxHeartbeats 1000000

namespace P112Cert.Sparse
open PR1497

/-- A literal integer linear combination of ordinary coordinate basis rows. -/
def row {n : Nat} : List (Fin n × Int) → Row n
  | [] => (rowGroup n).zero
  | (i, c) :: xs => (rowGroup n).add (scale c (basis n i)) (row xs)

/-- Evaluate only the listed left coefficients against the rows of B. -/
def eval {n d : Nat} : List (Fin n × Int) → Mat n d → Row d
  | [], _ => (rowGroup d).zero
  | (i, c) :: xs, B => (rowGroup d).add (scale c (B i)) (eval xs B)

/-- The sparse convention is the ordinary sum of coefficients at a column.
    The pinned source has no duplicate column entries; no deduplication is used. -/
theorem row_apply {n : Nat} (xs : List (Fin n × Int)) (j : Fin n) :
    row xs j = xs.foldr (fun e s => (if j = e.1 then e.2 else 0) + s) 0 := by
  induction xs with
  | nil => rfl
  | cons e xs ih =>
    cases e with
    | mk i c =>
      change c * (if j = i then 1 else 0) + row xs j =
        (if j = i then c else 0) +
          xs.foldr (fun e s => (if j = e.1 then e.2 else 0) + s) 0
      rw [ih]
      by_cases h : j = i
      · simp only [if_pos h, Int.mul_one]
      · simp only [if_neg h, Int.mul_zero]

/-- Scalar linearity is derived from the inherited, proved row homomorphism. -/
theorem rowMul_scale {n d : Nat} (c : Int) (v : Row n) (B : Mat n d) :
    rowMul (scale c v) B = scale c (rowMul v B) := by
  have h := (Rows.rowHom B).map_zsmul c v
  change rowMul ((rowGroup n).zsmul c v) B =
    (rowGroup d).zsmul c (rowMul v B) at h
  simpa only [Rows.row_zsmul] using h

/-- Sound connection to PR1497.rowMul and its actual recursive finite sum.
    No Boolean checker, matrix identity, or annihilation law is assumed. -/
theorem rowMul_row {n d : Nat} (xs : List (Fin n × Int)) (B : Mat n d) :
    rowMul (row xs) B = eval xs B := by
  induction xs with
  | nil => exact Rows.rowMul_zero_left B
  | cons e xs ih =>
    cases e with
    | mk i c =>
      change rowMul ((rowGroup n).add (scale c (basis n i)) (row xs)) B =
        (rowGroup d).add (scale c (B i)) (eval xs B)
      rw [Rows.rowMul_add, rowMul_scale, Rows.rowMul_basis, ih]

/-- Bounded-depth assembly of complete finite index families. This is only
    a wrapper around core Fin.addCases; both subranges are supplied as proofs. -/
theorem allFinAdd {a b : Nat} {R : Fin (a + b) → Prop}
    (hl : ∀ i : Fin a, R (Fin.castAdd b i))
    (hr : ∀ i : Fin b, R (Fin.natAdd a i)) :
    ∀ i : Fin (a + b), R i :=
  fun i => Fin.addCases (motive := R) hl hr i

end P112Cert.Sparse

set_option pp.fullNames true
#print axioms P112Cert.Sparse.row
#print axioms P112Cert.Sparse.eval
#print axioms P112Cert.Sparse.row_apply
#print axioms P112Cert.Sparse.rowMul_scale
#print axioms P112Cert.Sparse.rowMul_row
#print axioms P112Cert.Sparse.allFinAdd
