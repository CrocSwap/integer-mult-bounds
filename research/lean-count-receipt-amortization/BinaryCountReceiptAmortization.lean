import CounterArithmeticPure
import BinaryAutomaticWidthCount

/-! Arithmetic transport from the existing PR64 fixed-direction counter bound.
The published TapeStack, RippleCounter and CounterArithmetic source files are
unchanged. Only the literal prefix/update/iteration interfaces are identified.
The marked-home increment receipt costs two more transitions than PR64's
restored-digit receipt, so current pass reads equal published totalSteps+2N.
The published4N+2w theorem then gives6N+2w and the accepted automatic-width
machine obtains the loose linear bound12n+4. No new potential argument, generic
counter algorithm or full tape-model simulation is asserted. Compact output,
source caller/Plan and selected asymptotic/kappa instantiation remain separate. -/
namespace CurrentMain.BinaryCountReceiptAmortization
open FixedTapeMachine

/-- The two literal prefix functions select exactly the same true-bit run. -/
theorem prefix_binding (bits : List Bool) :
    CarryTape.trailingOnes bits=RippleCounter.carryLength true bits := by
  induction bits with
  | nil => rfl
  | cons b bits ih =>
    cases b <;> simp [CarryTape.trailingOnes,RippleCounter.carryLength,ih]

/-- Reuse the published update equations, rather than prove increment
correctness or potential accounting again. -/
theorem increment_binding (bits : List Bool) :
    CarryTape.increment bits=RippleCounter.updated true bits := by
  induction bits with
  | nil => rfl
  | cons b bits ih =>
    cases b with
    | false =>
      rw [CounterArithmetic.updated_stop true false bits (by decide)]
      rfl
    | true =>
      rw [CounterArithmetic.updated_carry true bits]
      change false::CarryTape.increment bits=false::RippleCounter.updated true bits
      exact congrArg (List.cons false) ih

theorem increment_reads_binding (bits : List Bool) :
    (CarryTape.incrementReceipt bits).reads=RippleCounter.steps true bits+2 := by
  simp only [CarryTape.incrementReceipt,RippleCounter.steps,prefix_binding]

private theorem pass_binding (n : Nat) (bits : List Bool) :
    (CarryTape.pass n bits).1=CounterArithmetic.iterate true n bits ∧
      (CarryTape.pass n bits).2.reads=CounterArithmetic.totalSteps true n bits+2*n := by
  induction n generalizing bits with
  | zero =>
    simp [CarryTape.pass,CarryTape.Receipt.zero,CounterArithmetic.iterate,CounterArithmetic.totalSteps]
  | succ n ih =>
    obtain ⟨hv,hr⟩ := ih (CarryTape.increment bits)
    constructor
    · simp only [CarryTape.pass,CounterArithmetic.iterate]
      rw [← increment_binding bits]
      exact hv
    · simp only [CarryTape.pass,CarryTape.Receipt.add,CounterArithmetic.totalSteps]
      rw [hr,increment_reads_binding,increment_binding bits]
      omega

theorem pass_result_binding (n : Nat) (bits : List Bool) :
    (CarryTape.pass n bits).1=CounterArithmetic.iterate true n bits :=
  (pass_binding n bits).1

theorem pass_reads_binding (n : Nat) (bits : List Bool) :
    (CarryTape.pass n bits).2.reads=CounterArithmetic.totalSteps true n bits+2*n :=
  (pass_binding n bits).2

/-- The existing PR64 theorem applies in the fixed increment direction and
charges the width of an arbitrary initial word. Width0 and wraparound remain
included, with no uncharged initial-potential premise. -/
theorem pass_reads_le (n : Nat) (bits : List Bool) :
    (CarryTape.pass n bits).2.reads≤6*n+2*bits.length := by
  have h := CounterArithmetic.total_steps_bound true n bits
  rw [pass_reads_binding]
  omega

/-- A concrete linear bound for the already accepted ten-state machine, from
the same right-blank/pristine-counter entry and with the same full endpoint.
It does not supply compact output or an asymptotic multiplication theorem. -/
theorem count_run_linear (word : List Bool) :
    ∃ t≤12*word.length+4,
      run BinaryAutomaticWidthCount.machine t (BinaryAutomaticWidthCount.initialConfiguration word)=
        BinaryAutomaticWidthCount.finalConfiguration word := by
  obtain ⟨t,ht,hr⟩ := BinaryAutomaticWidthCount.count_run word
  have hp := pass_reads_le word.length (BinaryAutomaticWidthCount.zeroBits word)
  simp only [BinaryAutomaticWidthCount.zeroBits,List.length_replicate] at hp ht
  exact ⟨t,by omega,hr⟩

end CurrentMain.BinaryCountReceiptAmortization
#print axioms CurrentMain.BinaryCountReceiptAmortization.prefix_binding
#print axioms CurrentMain.BinaryCountReceiptAmortization.increment_binding
#print axioms CurrentMain.BinaryCountReceiptAmortization.increment_reads_binding
#print axioms CurrentMain.BinaryCountReceiptAmortization.pass_result_binding
#print axioms CurrentMain.BinaryCountReceiptAmortization.pass_reads_binding
#print axioms CurrentMain.BinaryCountReceiptAmortization.pass_reads_le
#print axioms CurrentMain.BinaryCountReceiptAmortization.count_run_linear
