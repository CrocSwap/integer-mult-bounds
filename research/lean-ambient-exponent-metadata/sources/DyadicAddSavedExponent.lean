import DyadicCellAddition

/-!
A small reversible-encoding step for the checked aligned dyadic ADD. The forward
operation can increase the target exponent, so ordinary opposite addition does
not in general restore its original Cell representation. This reference undo
retains the original target exponent, subtracts the unchanged source at the
stored output exponent, and divides by the exact alignment factor. No original
target numerator, endpoint equality, same-grid hypothesis or divisibility
assumption is supplied: exact divisibility follows from the forward definition.

The selected specialization uses the source after halfCell, matching raw2
L119 += (1/2)*L169. This is a new local reference implementation, not an assertion
about the selected physical instruction tape. Retained exponent metadata and
the unchanged source are required; allocation, metadata cleanup, dirty scratch,
rounding and bit-operation cost remain separate.

Reuses the accepted analytic Cell and DyadicCellAddition definitions unchanged.
Attribution: selected PR1094 raw2; analytic exact per-cell exponent alignment;
machine reference ADD. Apache-2.0; prepared with OpenAI assistance. Selected
kappa836330098538459/500000000000000000 is unchanged. Uncompiled source candidate.
-/
set_option Elab.async false
set_option autoImplicit false
namespace CurrentMain.DyadicAddSavedExponent
open Current1094Row1DyadicReference DyadicCellAddition

/-- Restore the old target representation using its saved exponent. This function
uses only the updated target, unchanged source, and that exponent. On unrelated
inputs it is a total reference function; the correctness claim below concerns
actual outputs of addCell. -/
def restoreCell (updated source : Cell) (originalExponent : ℕ) : Cell :=
  ⟨(updated.numerator - alignedNumerator updated.fractionalBits source) /
      (2 : ℤ) ^ (updated.fractionalBits - originalExponent),
    originalExponent⟩

/-- Exact raw-Cell restoration is derived from the shifted-add definition. -/
theorem restore_addCell (target source : Cell) :
    restoreCell (addCell target source) source target.fractionalBits = target := by
  cases target with
  | mk z p =>
    change Cell.mk
      ((z * (2 : ℤ) ^ (max p source.fractionalBits - p) +
        alignedNumerator (max p source.fractionalBits) source -
        alignedNumerator (max p source.fractionalBits) source) /
        (2 : ℤ) ^ (max p source.fractionalBits - p)) p = Cell.mk z p
    rw [add_sub_cancel_right,
      Int.mul_ediv_cancel z (pow_ne_zero _ (by norm_num))]

/-- Retain only the old exponent alongside the actual new target Cell. -/
def rememberedHalfAdd (target source : Cell) : Cell × ℕ :=
  (addCell target (halfCell source), target.fractionalBits)

/-- This selected +1/2 specialization does not require equal input exponents. -/
theorem restore_rememberedHalfAdd (target source : Cell) :
    restoreCell (rememberedHalfAdd target source).1 (halfCell source)
      (rememberedHalfAdd target source).2 = target :=
  restore_addCell target (halfCell source)

/-- The retained metadata is exactly one original exponent, not an old payload. -/
theorem rememberedHalfAdd_exponent (target source : Cell) :
    (rememberedHalfAdd target source).2 = target.fractionalBits := rfl

end CurrentMain.DyadicAddSavedExponent

#print axioms CurrentMain.DyadicAddSavedExponent.restore_addCell
#print axioms CurrentMain.DyadicAddSavedExponent.restore_rememberedHalfAdd
#print axioms CurrentMain.DyadicAddSavedExponent.rememberedHalfAdd_exponent
#check @CurrentMain.DyadicAddSavedExponent.restore_rememberedHalfAdd
