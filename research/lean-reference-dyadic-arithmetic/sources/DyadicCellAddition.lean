import Current1094Row1DyadicReference
import Mathlib.Tactic.FieldSimp

/-!
Concrete exact exponent alignment and integer addition for the already checked
per-cell dyadic representation. The common exponent is the actual maximum of
the two cell exponents; inputs are shifted by explicit nonnegative differences.
No same-grid assumption or floating/fixed-precision rounding map is introduced.

The magnitude theorem counts binary numerator budget after alignment plus one
carry bit. It does not count sign/exponent/address metadata or bit-operation
time, and does not choose a selected precision schedule. Int/Nat operations are
unbounded reference operations. The program-level join is a separate module
using the source-bound raw2 instruction stream rather than assuming its result.
Attribution: selected PR1094 row2 ADD(+1/2), accepted per-cell dyadic SCALE core,
machine's explicit real reference. Apache-2.0; OpenAI-assisted. Selected
kappa836330098538459/500000000000000000 is unchanged.
-/
set_option Elab.async false
set_option autoImplicit false
namespace CurrentMain.DyadicCellAddition
open Current1094Row1DyadicReference

def commonExponent (a b : Cell) : ℕ := max a.fractionalBits b.fractionalBits

def alignedNumerator (q : ℕ) (c : Cell) : ℤ :=
  c.numerator * (2 : ℤ) ^ (q - c.fractionalBits)

/-- Explicit shifted integer addition; the inputs are not modified. -/
def addCell (a b : Cell) : Cell :=
  let q := commonExponent a b
  ⟨alignedNumerator q a + alignedNumerator q b, q⟩

/-- Raising an exponent by an exact integer shift preserves decoded value.
The ordering hypothesis is essential because Nat subtraction is truncated. -/
theorem aligned_value (q : ℕ) (c : Cell) (h : c.fractionalBits ≤ q) :
    (alignedNumerator q c : ℝ) / (2 : ℝ) ^ q = value c := by
  have hp : (2 : ℝ) ^ q =
      (2 : ℝ) ^ (q - c.fractionalBits) * (2 : ℝ) ^ c.fractionalBits := by
    rw [← pow_add, Nat.sub_add_cancel h]
  simp only [alignedNumerator, Int.cast_mul, Int.cast_pow, Int.cast_ofNat, value]
  apply (div_eq_div_iff (pow_ne_zero q (by norm_num))
    (pow_ne_zero c.fractionalBits (by norm_num))).2
  rw [hp]
  ring

/-- Exact addition with arbitrary, independently chosen input exponents. -/
theorem addCell_value (a b : Cell) : value (addCell a b) = value a + value b := by
  change ((alignedNumerator (commonExponent a b) a +
      alignedNumerator (commonExponent a b) b : ℤ) : ℝ) /
      (2 : ℝ) ^ commonExponent a b = value a + value b
  rw [Int.cast_add, add_div,
    aligned_value (commonExponent a b) a (le_max_left _ _),
    aligned_value (commonExponent a b) b (le_max_right _ _)]

theorem addCell_exponent (a b : Cell) :
    (addCell a b).fractionalBits = max a.fractionalBits b.fractionalBits := rfl

/-- The exact integer numerator budget includes both alignment shifts. -/
theorem addCell_numerator_bound (a b : Cell) :
    (addCell a b).numerator.natAbs ≤
      a.numerator.natAbs * 2 ^ (commonExponent a b - a.fractionalBits) +
      b.numerator.natAbs * 2 ^ (commonExponent a b - b.fractionalBits) := by
  have h := Int.natAbs_add_le (alignedNumerator (commonExponent a b) a)
    (alignedNumerator (commonExponent a b) b)
  simpa only [addCell, alignedNumerator, Int.natAbs_mul, Int.natAbs_pow,
    Int.natAbs_natCast] using h

/-- If both magnitudes fit their stated binary budgets, the aligned sum fits
one additional carry bit beyond the larger shifted budget. This says nothing
about the storage or time cost of the exponent itself. -/
theorem addCell_bit_budget (a b : Cell) (ba bb : ℕ)
    (ha : a.numerator.natAbs < 2 ^ ba) (hb : b.numerator.natAbs < 2 ^ bb) :
    (addCell a b).numerator.natAbs <
      2 ^ (max (ba + (commonExponent a b - a.fractionalBits))
        (bb + (commonExponent a b - b.fractionalBits)) + 1) := by
  let da := commonExponent a b - a.fractionalBits
  let db := commonExponent a b - b.fractionalBits
  let B := max (ba + da) (bb + db)
  have ha' : a.numerator.natAbs * 2 ^ da < 2 ^ (ba + da) := by
    rw [pow_add]
    exact Nat.mul_lt_mul_of_pos_right ha (pow_pos (by norm_num) _)
  have hb' : b.numerator.natAbs * 2 ^ db < 2 ^ (bb + db) := by
    rw [pow_add]
    exact Nat.mul_lt_mul_of_pos_right hb (pow_pos (by norm_num) _)
  have hba : (2 : ℕ) ^ (ba + da) ≤ 2 ^ B :=
    pow_le_pow_right₀ (by norm_num) (le_max_left _ _)
  have hbb : (2 : ℕ) ^ (bb + db) ≤ 2 ^ B :=
    pow_le_pow_right₀ (by norm_num) (le_max_right _ _)
  calc
    (addCell a b).numerator.natAbs ≤
        a.numerator.natAbs * 2 ^ da + b.numerator.natAbs * 2 ^ db :=
      addCell_numerator_bound a b
    _ < 2 ^ B + 2 ^ B := Nat.add_lt_add (ha'.trans_le hba) (hb'.trans_le hbb)
    _ = 2 ^ (B + 1) := by rw [pow_succ]; omega

/-- The concrete selected ADD component receives the source AFTER exact halving.
Thus its output grid is max(target.p,source.p+1), rather than a global grid. -/
theorem selected_half_add_value (target source : Cell) :
    value (addCell target (halfCell source)) = value target + value source / 2 ∧
    (addCell target (halfCell source)).fractionalBits =
      max target.fractionalBits (source.fractionalBits + 1) := by
  refine ⟨?_, rfl⟩
  rw [addCell_value]
  change value target + (source.numerator : ℝ) /
      (2 : ℝ) ^ (source.fractionalBits + 1) = value target + value source / 2
  rw [pow_succ, div_mul_eq_div_div]
  rfl

end CurrentMain.DyadicCellAddition

#print axioms CurrentMain.DyadicCellAddition.aligned_value
#print axioms CurrentMain.DyadicCellAddition.addCell_value
#print axioms CurrentMain.DyadicCellAddition.addCell_exponent
#print axioms CurrentMain.DyadicCellAddition.addCell_numerator_bound
#print axioms CurrentMain.DyadicCellAddition.addCell_bit_budget
#print axioms CurrentMain.DyadicCellAddition.selected_half_add_value
