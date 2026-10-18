import MultitapeToolkit.IntegerMultiplicationEngine
import Mathlib.Data.Nat.Size
import Mathlib.Data.ZMod.Basic
set_option autoImplicit false
/-! Applications of the actual clean six-tape multiplication run. Width selection
and residue labeling are external input conventions; no uncharged physical
conversion or output truncation is asserted. -/
namespace MultitapeToolkit.IntegerMultiplicationProductApplications
open Turing MultitapeToolkit MultitapeToolkit.Absolute
open MultitapeToolkit.BinaryMultiplication MultitapeToolkit.IntegerMultiplicationEngine
open Lax51Proofs.RamToTM
/-- Smallest common width admitting both natural operands; zero is allowed. -/
def commonWidth (a b : ℕ) : ℕ := max a.size b.size
theorem commonWidth_spec (a b n : ℕ) :
    commonWidth a b ≤ n ↔ a < 2^n ∧ b < 2^n := by
  simp [commonWidth, Nat.size_le]
theorem commonWidth_fits (a b : ℕ) :
    a < 2^(commonWidth a b) ∧ b < 2^(commonWidth a b) :=
  (commonWidth_spec a b _).mp le_rfl
theorem bitsValue_nat_bits (a : ℕ) : bitsValue a.bits = a := by
  induction a using Nat.binaryRec' with
  | zero => rfl
  | bit b a h ih =>
    rw [Nat.bits_append_bit a b h]
    simp only [bitsValue, ih]
/-- Literal list equality, including every zero padding symbol. -/
theorem fixedBits_eq_bits_padding (a n : ℕ) (h : a.size ≤ n) :
    fixedBits n a = a.bits ++ List.replicate (n-a.size) false := by
  apply bitsValue_injective_of_length
  · simp [Nat.size_eq_bits_len, Nat.add_sub_of_le h]
  · rw [bitsValue_append_zeros, bitsValue_nat_bits,
      bitsValue_fixedBits_of_lt (Nat.size_le.mp h)]
noncomputable def minimalInput (a b : ℕ) := cleanInput (commonWidth a b) a b
/-- Input tapes contain canonical bits followed by literal zero padding. -/
theorem minimalInput_literal_operands (a b : ℕ) :
    (minimalInput a b).cell .multiplier =
      StackOriginSerializer.sourceStack 0
        (b.bits ++ List.replicate (commonWidth a b-b.size) false) ∧
    (minimalInput a b).cell .multiplicand =
      StackOriginSerializer.sourceStack 0
        (a.bits ++ List.replicate (commonWidth a b-a.size) false) := by
  have h := clean_input_operands (commonWidth a b) a b
  rw [fixedBits_eq_bits_padding b (commonWidth a b) (le_max_right a.size b.size),
    fixedBits_eq_bits_padding a (commonWidth a b) (le_max_left a.size b.size)] at h
  exact h
/-- Arbitrary naturals run on one fixed machine at minimal common width. -/
theorem minimal_width_product (a b : ℕ) :
    ∃ t, t ≤ 280*(commonWidth a b)^2+322*(commonWidth a b)+122 ∧
      MultitapeToolkit.Absolute.Runs cleanMachine t (minimalInput a b) (cleanOutput (commonWidth a b) (a*b)) ∧
      MultitapeToolkit.Absolute.Halts cleanMachine (cleanOutput (commonWidth a b) (a*b)) ∧
      bitsValue ((fixedBits (2*commonWidth a b) (a*b)).reverse.reverse)=a*b := by
  exact clean_product _ a b (commonWidth_fits a b).1 (commonWidth_fits a b).2
/-- Physical output is the exact double-width product; its residue label is the
ring product. No physical output truncation operation is asserted. -/
theorem zmod_product (n : ℕ) (x y : ZMod (2^n)) :
    ∃ t, t ≤ 280*n^2+322*n+122 ∧
      MultitapeToolkit.Absolute.Runs cleanMachine t (cleanInput n x.val y.val) (cleanOutput n (x.val*y.val)) ∧
      MultitapeToolkit.Absolute.Halts cleanMachine (cleanOutput n (x.val*y.val)) ∧
      (bitsValue ((fixedBits (2*n) (x.val*y.val)).reverse.reverse) : ZMod (2^n))=x*y ∧
      bitsValue (fixedBits n (x.val*y.val))=(x*y).val := by
  let : NeZero (2^n) := ⟨pow_ne_zero _ (by decide)⟩
  rcases clean_product n x.val y.val x.val_lt y.val_lt with ⟨t,ht,hr,hh,hvalue⟩
  refine ⟨t,ht,hr,hh,?_,?_⟩
  · rw [hvalue, Nat.cast_mul, ZMod.natCast_zmod_val, ZMod.natCast_zmod_val]
  · rw [bitsValue_fixedBits, ZMod.val_mul]
/-- Canonical nonnegative residue labels include negative integer inputs. -/
theorem signed_residue_label (n : ℕ) (z : ℤ) :
    (((z : ZMod (2^n)).val : ℕ) : ℤ)=z % ((2^n : ℕ) : ℤ) := by
  let : NeZero (2^n) := ⟨pow_ne_zero _ (by decide)⟩
  exact ZMod.val_intCast z
/-- Signed labels use canonical-residue words, with no assumed signed parser. -/
theorem signed_residue_product (n : ℕ) (a b : ℤ) :
    ∃ t, t ≤ 280*n^2+322*n+122 ∧
      MultitapeToolkit.Absolute.Runs cleanMachine t
        (cleanInput n (a : ZMod (2^n)).val (b : ZMod (2^n)).val)
        (cleanOutput n ((a : ZMod (2^n)).val*(b : ZMod (2^n)).val)) ∧
      MultitapeToolkit.Absolute.Halts cleanMachine
        (cleanOutput n ((a : ZMod (2^n)).val*(b : ZMod (2^n)).val)) ∧
      (bitsValue ((fixedBits (2*n)
        ((a : ZMod (2^n)).val*(b : ZMod (2^n)).val)).reverse.reverse) : ZMod (2^n))=
        ((a*b : ℤ) : ZMod (2^n)) := by
  rcases zmod_product n (a : ZMod (2^n)) (b : ZMod (2^n)) with
    ⟨t,ht,hr,hh,hvalue,_⟩
  exact ⟨t,ht,hr,hh,by simpa only [Int.cast_mul] using hvalue⟩
end MultitapeToolkit.IntegerMultiplicationProductApplications
