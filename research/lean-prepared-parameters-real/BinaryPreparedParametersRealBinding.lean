import BinaryPreparedParameters
import BinaryCeilLogRealBinding

/-! Identity-only attachment of the literal real ceiling to the accepted
forty-eight-state, eight-tape prelude. Both run statements use its original
initialConfiguration, finalConfiguration and machine without alteration.
Natural ceiling includes the existing zero extension; integer ceiling is
stated on the explicit positive-width branch. No selected one-string caller,
new parameter computation, first completion, Plan or Budget is supplied. -/
namespace CurrentMain.BinaryPreparedParametersRealBinding
open FixedTapeMachine
set_option Elab.async false

private theorem parameter_tokens (x y : List Bool) :
    wordValue (BinaryPreparedParameters.parameterBits x y)=
      BinaryCeilLogTokens.tokenCount
        (BinaryCounterCompactCopy.compact (BinaryPreparedParameters.widthBits x y)) := by
  rw [BinaryCeilLogTokens.token_count_ceil_log2,BinaryPreparedParameters.width_value]
  exact BinaryPreparedParameters.parameter_value x y

/-- The stored parameter equals the natural real-logarithm ceiling, including zero. -/
theorem parameter_nat_ceil (x y : List Bool) :
    wordValue (BinaryPreparedParameters.parameterBits x y)=
      ⌈Real.logb (2 : Nat) (BinaryPreparedParameters.width x y : Real)⌉₊ := by
  calc
    wordValue (BinaryPreparedParameters.parameterBits x y)=
        BinaryCeilLogTokens.tokenCount
          (BinaryCounterCompactCopy.compact (BinaryPreparedParameters.widthBits x y)) :=
      parameter_tokens x y
    _=⌈Real.logb (2 : Nat) (BinaryPreparedParameters.width x y : Real)⌉₊ := by
      simpa only [BinaryPreparedParameters.width_value] using
        BinaryCeilLogRealBinding.token_count_nat_ceil (BinaryPreparedParameters.widthBits x y)

/-- The positive-width branch matches the source's integer-ceiling convention. -/
theorem parameter_int_ceil (x y : List Bool) (hpos : 0<BinaryPreparedParameters.width x y) :
    (wordValue (BinaryPreparedParameters.parameterBits x y) : Int)=
      ⌈Real.logb (2 : Nat) (BinaryPreparedParameters.width x y : Real)⌉ := by
  have hp : 0<wordValue (BinaryPreparedParameters.widthBits x y) := by
    simpa only [BinaryPreparedParameters.width_value] using hpos
  calc
    (wordValue (BinaryPreparedParameters.parameterBits x y) : Int)=
        (BinaryCeilLogTokens.tokenCount
          (BinaryCounterCompactCopy.compact (BinaryPreparedParameters.widthBits x y)) : Int) :=
      congrArg (fun n : Nat => (n : Int)) (parameter_tokens x y)
    _=⌈Real.logb (2 : Nat) (BinaryPreparedParameters.width x y : Real)⌉ := by
      simpa only [BinaryPreparedParameters.width_value] using
        BinaryCeilLogRealBinding.token_count_int_ceil (BinaryPreparedParameters.widthBits x y) hp

theorem zero_parameter (x y : List Bool) (hzero : BinaryPreparedParameters.width x y=0) :
    wordValue (BinaryPreparedParameters.parameterBits x y)=0 := by
  have hz : wordValue (BinaryPreparedParameters.widthBits x y)=0 :=
    (BinaryPreparedParameters.width_value x y).trans hzero
  exact (parameter_tokens x y).trans
    (BinaryCeilLogRealBinding.zero_parameter (BinaryPreparedParameters.widthBits x y) hz)

theorem one_parameter (x y : List Bool) (hone : BinaryPreparedParameters.width x y=1) :
    wordValue (BinaryPreparedParameters.parameterBits x y)=0 := by
  have ho : wordValue (BinaryPreparedParameters.widthBits x y)=1 :=
    (BinaryPreparedParameters.width_value x y).trans hone
  exact (parameter_tokens x y).trans
    (BinaryCeilLogRealBinding.one_parameter (BinaryPreparedParameters.widthBits x y) ho)

/-- The same full physical endpoint and bound, with the literal natural ceiling attached. -/
theorem prepare_parameters_run_nat_ceil (x y : List Bool) :
    ∃ t≤35*BinaryPreparedParameters.width x y+24,
      run BinaryPreparedParameters.machine t (BinaryPreparedParameters.initialConfiguration x y)=
        BinaryPreparedParameters.finalConfiguration x y ∧
      wordValue (BinaryPreparedParameters.parameterBits x y)=
        ⌈Real.logb (2 : Nat) (BinaryPreparedParameters.width x y : Real)⌉₊ := by
  obtain ⟨t,ht,hr⟩ := BinaryPreparedParameters.prepare_parameters_run_linear x y
  exact ⟨t,ht,hr,parameter_nat_ceil x y⟩

/-- The positive-width run uses the same endpoint and integer-ceiling convention. -/
theorem prepare_parameters_run_int_ceil (x y : List Bool)
    (hpos : 0<BinaryPreparedParameters.width x y) :
    ∃ t≤35*BinaryPreparedParameters.width x y+24,
      run BinaryPreparedParameters.machine t (BinaryPreparedParameters.initialConfiguration x y)=
        BinaryPreparedParameters.finalConfiguration x y ∧
      (wordValue (BinaryPreparedParameters.parameterBits x y) : Int)=
        ⌈Real.logb (2 : Nat) (BinaryPreparedParameters.width x y : Real)⌉ := by
  obtain ⟨t,ht,hr⟩ := BinaryPreparedParameters.prepare_parameters_run_linear x y
  exact ⟨t,ht,hr,parameter_int_ceil x y hpos⟩

end CurrentMain.BinaryPreparedParametersRealBinding
#print axioms CurrentMain.BinaryPreparedParametersRealBinding.parameter_nat_ceil
#print axioms CurrentMain.BinaryPreparedParametersRealBinding.parameter_int_ceil
#print axioms CurrentMain.BinaryPreparedParametersRealBinding.zero_parameter
#print axioms CurrentMain.BinaryPreparedParametersRealBinding.one_parameter
#print axioms CurrentMain.BinaryPreparedParametersRealBinding.prepare_parameters_run_nat_ceil
#print axioms CurrentMain.BinaryPreparedParametersRealBinding.prepare_parameters_run_int_ceil
