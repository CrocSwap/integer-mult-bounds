import Mathlib.Data.Fin.Basic
import Mathlib.Data.List.Basic

/-!
Literal finite part of PR2250's selected residual `0:1000.right`.
The data are source-bound separately.  All finite claims here are reduced by
Lean's kernel from the listed bits and gates; no computed image table is a
proof input.  This is a model of the source's bit operations, not a formal
verification of Python execution.  Predecessor: Jose Manuel, PR2250.
Prepared with substantial OpenAI Codex assistance. Apache-2.0.
-/

namespace SelectedMonomial

abbrev Address := Fin 512
abbrev Digit := Fin 9

inductive Gate where
  | add (target source : Digit)
  | flip (target : Digit)
  deriving DecidableEq, Repr

def bit (x : Address) (i : Nat) : Bool := x.val.testBit i

def bitNat (x : Address) (i : Nat) : Nat := if bit x i then 1 else 0

def toggle (x : Address) (i : Digit) : Address :=
  ⟨(x.val ^^^ 2 ^ i.val) % 512, Nat.mod_lt _ (by decide)⟩

def gate (g : Gate) (x : Address) : Address :=
  match g with
  | .add target source => if bit x source.val then toggle x target else x
  | .flip target => toggle x target

def runAddress : List Gate → Address → Address
  | [], x => x
  | g :: gs, x => runAddress gs (gate g x)

/-- The 22 operations emitted by the pinned source's binary elimination. -/
def word : List Gate :=
  [.add 7 8, .add 8 7, .add 7 8, .add 3 6, .add 1 6,
   .add 6 8, .add 8 6, .add 6 8, .add 8 3, .add 8 1,
   .add 1 3, .add 3 1, .add 1 3, .add 8 0, .add 3 0,
   .add 1 0, .flip 0, .flip 2, .flip 4, .flip 5, .flip 6, .flip 7]

def matrixRows : List Nat := [1, 73, 4, 67, 16, 32, 128, 256, 75]
def alpha : List Nat := [1, 3, 2, 3, 2, 2, 0, 2, 2]
def quadraticRows : List Nat := [65, 10, 0, 10, 0, 0, 1, 0, 0]
def offset : Nat := 245
def constantPhase : Nat := 2

def parity (row : Nat) (x : Address) : Nat :=
  ((List.range 9).map (fun i => if row.testBit i then bitNat x i else 0)).sum % 2

def affine (x : Address) : Address :=
  ⟨(((List.range 9).map (fun i => parity (matrixRows.getD i 0) x * 2 ^ i)).sum
       ^^^ offset) % 512, Nat.mod_lt _ (by decide)⟩

/-- The source reads only strict upper quadratic entries; alpha holds diagonals. -/
def rawQ (x : Address) : Nat :=
  (((List.range 9).map (fun i => alpha.getD i 0 * bitNat x i)).sum +
    2 * ((List.range 9).map (fun i =>
      ((List.range 9).map (fun j =>
        if i < j then
          if (quadraticRows.getD i 0).testBit j then bitNat x i * bitNat x j else 0
        else 0)).sum)).sum) % 4

/-- Expanded strict-upper phase of this particular selected recipe. -/
def q (x : Address) : Nat :=
  (bitNat x 0 + 3 * bitNat x 1 + 2 * bitNat x 2 + 3 * bitNat x 3 +
   2 * bitNat x 4 + 2 * bitNat x 5 + 2 * bitNat x 7 + 2 * bitNat x 8 +
   2 * bitNat x 0 * bitNat x 6 + 2 * bitNat x 1 * bitNat x 3) % 4

set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
theorem word_affine : ∀ x : Address, runAddress word x = affine x := by decide

set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
theorem reverse_forward : ∀ x : Address,
    runAddress word.reverse (runAddress word x) = x := by decide

set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
theorem forward_reverse : ∀ x : Address,
    runAddress word (runAddress word.reverse x) = x := by decide

set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
theorem strict_upper_phase : ∀ x : Address, rawQ x = q x := by decide

def sigma : Address ≃ Address where
  toFun := runAddress word
  invFun := runAddress word.reverse
  left_inv := reverse_forward
  right_inv := forward_reverse

theorem sigma_affine (x : Address) : sigma x = affine x := word_affine x

set_option maxRecDepth 100000 in
theorem zero_offset : sigma 0 = 245 := by decide
set_option maxRecDepth 100000 in
theorem phase_must_use_recovered_input : q (sigma 0) ≠ q 0 := by decide
theorem two_zero_columns_phase : (2 * 2 + q 0 + q 0) % 4 = 0 := by decide
theorem single_constant_is_wrong : (2 + q 0 + q 0) % 4 = 2 := by decide

end SelectedMonomial
