import BinaryCeilLogNatBinding
import Mathlib.Analysis.SpecialFunctions.Log.Base

/-! Thin reuse of the installed real-logarithm ceiling theorem. The accepted
Nat.clog transport is retained as a dependency rather than reproved. Natural
ceiling includes the library's explicit zero extension. The integer-ceiling
source interface requires positive represented input; zero and one are
recorded separately. No physical machine, caller, precision or Budget premise
is changed, and no new analytic logarithm argument is introduced. -/
namespace CurrentMain.BinaryCeilLogRealBinding
open FixedTapeMachine
set_option Elab.async false

/-- Published natural ceiling interface, including the explicit zero extension. -/
theorem token_count_nat_ceil (bits : List Bool) :
    BinaryCeilLogTokens.tokenCount (BinaryCounterCompactCopy.compact bits)=
      ⌈Real.logb (2 : Nat) (wordValue bits : Real)⌉₊ :=
  (BinaryCeilLogNatBinding.token_count_nat_clog bits).trans
    (Real.natCeil_logb_natCast 2 (wordValue bits)).symm

/-- On the positive source branch, natural and integer ceiling agree. -/
theorem token_count_int_ceil (bits : List Bool) (hpos : 0<wordValue bits) :
    (BinaryCeilLogTokens.tokenCount (BinaryCounterCompactCopy.compact bits) : Int)=
      ⌈Real.logb (2 : Nat) (wordValue bits : Real)⌉ := by
  rw [token_count_nat_ceil]
  exact Int.natCast_ceil_eq_ceil
    (Real.logb_nonneg (show (1 : Real)<2 from one_lt_two) (Nat.one_le_cast.2 hpos))

theorem zero_parameter (bits : List Bool) (hzero : wordValue bits=0) :
    BinaryCeilLogTokens.tokenCount (BinaryCounterCompactCopy.compact bits)=0 := by
  rw [BinaryCeilLogNatBinding.token_count_nat_clog,hzero,Nat.clog_zero_right]

theorem one_parameter (bits : List Bool) (hone : wordValue bits=1) :
    BinaryCeilLogTokens.tokenCount (BinaryCounterCompactCopy.compact bits)=0 := by
  rw [BinaryCeilLogNatBinding.token_count_nat_clog,hone,Nat.clog_one_right]

end CurrentMain.BinaryCeilLogRealBinding
#print axioms CurrentMain.BinaryCeilLogRealBinding.token_count_nat_ceil
#print axioms CurrentMain.BinaryCeilLogRealBinding.token_count_int_ceil
#print axioms CurrentMain.BinaryCeilLogRealBinding.zero_parameter
#print axioms CurrentMain.BinaryCeilLogRealBinding.one_parameter
