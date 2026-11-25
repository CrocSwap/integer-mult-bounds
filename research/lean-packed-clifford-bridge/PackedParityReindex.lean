import Current535PackedCoordinates
import PR593Clifford

/-!
The exact packed parity primitive used by PR593 matrix and quadratic reads.
Bits have their source little-endian order. The proof is symbolic in the packed
address and the row mask; no address enumeration is introduced.
Apache-2.0; prepared with OpenAI assistance. See NOTICE.md.
-/
set_option Elab.async false
namespace CurrentMain.PackedParityReindex
open Current535PackedCoordinates
open CliffordNineBitDecoder (Bit Address mask)
open scoped BigOperators

def boolBit (b : Bool) : Bit := if b then 1 else 0

private theorem boolBit_xor (a b : Bool) :
    boolBit (a ^^ b) = boolBit a + boolBit b := by
  cases a <;> cases b <;> decide +kernel

private theorem boolBit_and (a b : Bool) :
    boolBit (a && b) = boolBit a * boolBit b := by
  cases a <;> cases b <;> decide +kernel

/-- The source's recursive parity is the sum of its input bits in ZMod2. -/
theorem parity_sum (n x : Nat) :
    boolBit (HyperplaneEnd.Clifford.par n x) =
      ∑ i : Fin n, boolBit (x.testBit i.val) := by
  induction n generalizing x with
  | zero => simp [HyperplaneEnd.Clifford.par, boolBit]
  | succ n ih =>
    rw [HyperplaneEnd.Clifford.par, boolBit_xor, ih, Fin.sum_univ_succ]
    apply congrArg₂ (· + ·)
    · simp [boolBit, Nat.testBit_zero]
    · apply Finset.sum_congr rfl
      intro i _
      rw [Nat.testBit_div_two]
      rfl

/-- AND with a nine-bit address bounds the parity input even when the stored
row has unused high bits. PR593's already checked par9_spec is reused. -/
theorem packed_parity_dot (row : Nat) (x : Packed) :
    boolBit (HyperplaneEnd.Clifford.par9 (row &&& x.val)) =
      dotProduct (mask row) (unpack x) := by
  have hb : row &&& x.val < 512 :=
    lt_of_le_of_lt Nat.and_le_right x.isLt
  rw [HyperplaneEnd.Clifford.par9_spec ⟨row &&& x.val, hb⟩, parity_sum]
  unfold dotProduct
  apply Finset.sum_congr rfl
  intro i _
  rw [Nat.testBit_and, boolBit_and]
  rfl

/-- Natural0/1 parity values agree as well; Z4 phase arithmetic remains Nat. -/
theorem packed_parity_value (row : Nat) (x : Packed) :
    (if HyperplaneEnd.Clifford.par9 (row &&& x.val) then 1 else 0) =
      (dotProduct (mask row) (unpack x)).val := by
  rw [← packed_parity_dot]
  cases h : HyperplaneEnd.Clifford.par9 (row &&& x.val) <;>
    simp [boolBit, h, ZMod.val_one_eq_one_mod]

end CurrentMain.PackedParityReindex

#print axioms CurrentMain.PackedParityReindex.parity_sum
#print axioms CurrentMain.PackedParityReindex.packed_parity_dot
#print axioms CurrentMain.PackedParityReindex.packed_parity_value
