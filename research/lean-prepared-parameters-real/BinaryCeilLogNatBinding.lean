import BinaryCeilLogTokens
import Mathlib.Data.Nat.Log

/-! A thin source-parameter interface to the installed natural ceiling logarithm.
The accepted physical token scan supplies the least-power certificate; the
published Nat.le_pow_iff_clog_le and Nat.le_pow_clog identify the same value.
No new logarithm, counter or potential argument is proved. Zero and one retain
the existing zero parameter convention. The wider Real.logb ceiling interface,
binary parameter machine and selected source caller remain separate. -/
namespace CurrentMain.BinaryCeilLogNatBinding
open FixedTapeMachine
set_option Elab.async false

/-- Exact transport of the normalized token count to the published Nat.clog. -/
theorem token_count_nat_clog (bits : List Bool) :
    BinaryCeilLogTokens.tokenCount (BinaryCounterCompactCopy.compact bits)=
      Nat.clog 2 (wordValue bits) := by
  apply Nat.le_antisymm
  · exact (BinaryCeilLogTokens.parameter_le_iff bits (Nat.clog 2 (wordValue bits))).2
      (Nat.le_pow_clog (b:=2) (by decide) (wordValue bits))
  · exact (Nat.le_pow_iff_clog_le (b:=2) (by decide)).1
      ((BinaryCeilLogTokens.parameter_le_iff bits
        (BinaryCeilLogTokens.tokenCount (BinaryCounterCompactCopy.compact bits))).1 (Nat.le_refl _))

end CurrentMain.BinaryCeilLogNatBinding
#print axioms CurrentMain.BinaryCeilLogNatBinding.token_count_nat_clog
