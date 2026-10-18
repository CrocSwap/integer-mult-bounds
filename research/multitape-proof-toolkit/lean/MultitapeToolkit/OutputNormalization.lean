import MultitapeToolkit.BinaryCanonicalOutput
import MultitapeToolkit.TM2Compiler

/-!
# A charged canonical-output adapter for the finite multitape toolkit

This is a toolkit interoperability component, not new normalization mathematics:
platypii master `ba92ef280de31a45a2e1ba8271ac309684c7c799` already supplies
`BinaryCanonicalTrim.normalize_exists`, and PR2 `Fast.Output.carryOut_exec`
already charges canonical emission. No upstream implementation is copied here.
The mathematical fixed-width specification is narrowed from Problem1.8 (see the
pure imported module). The actual machine has two Bool stacks, one label, and six
register values. One source macrostep consumes one input bit, with one final EOF
macrostep. Compilation supplies genuine tape-local read/write/move transitions.
-/

set_option autoImplicit false
namespace MultitapeToolkit.OutputNormalization

open Turing MultitapeToolkit.TM2Compiler

inductive Stack
  | source | output
  deriving DecidableEq

instance : Fintype Stack :=
  ⟨{.source, .output}, by intro k; cases k <;> simp⟩

/-- A seen-one bit and the most recent optional input bit: six finite values. -/
abbrev Register := Bool × Option Bool

/-- No input width, integer value, or unbounded accumulator is stored in control. -/
def program (_ : Unit) : TM2.Stmt (fun _ : Stack => Bool) Unit Register :=
  .pop .source (fun v b => (v.1 || b.getD false, b))
    (.branch (fun v => v.2.isSome)
      (.branch (fun v => v.1)
        (.push .output (fun v => v.2.getD false) (.goto fun _ => ()))
        (.goto fun _ => ()))
      .halt)

def stores (input output : List Bool) : Stack → List Bool
  | .source => input
  | .output => output

def startCfg (seen : Bool) (held : Option Bool) (input output : List Bool) :
    TM2.Cfg (fun _ : Stack => Bool) Unit Register :=
  ⟨some (), (seen, held), stores input output⟩

/-- Bits emitted onto the output stack, least significant bit first. -/
def emitted : Bool → List Bool → List Bool
  | _, [] => []
  | seen, b :: bs => emitted (seen || b) bs ++ if seen || b then [b] else []

def finalSeen : Bool → List Bool → Bool
  | seen, [] => seen
  | seen, b :: bs => finalSeen (seen || b) bs

def finishCfg (seen : Bool) (input output : List Bool) :
    TM2.Cfg (fun _ : Stack => Bool) Unit Register :=
  ⟨none, (finalSeen seen input, none), stores [] (emitted seen input ++ output)⟩

/-- Existing output data is retained as a suffix, including on all-zero input. -/
theorem emitted_seen (input : List Bool) : emitted true input = input.reverse := by
  induction input with
  | nil => rfl
  | cons b bs ih => simp [emitted, ih]

theorem emitted_unseen (input : List Bool) : emitted false input = trimHighZeros input := by
  induction input with
  | nil => rfl
  | cons b bs ih =>
    cases b
    · simpa [emitted, trimHighZeros] using ih
    · simp [emitted, trimHighZeros, emitted_seen]

abbrev sourceStep (c : Option (TM2.Cfg (fun _ : Stack => Bool) Unit Register)) :=
  c.bind (TM2.step program)

@[simp] theorem step_eof (seen : Bool) (held : Option Bool) (output : List Bool) :
    TM2.step program (startCfg seen held [] output) =
      some (finishCfg seen [] output) := by
  simp [TM2.step, TM2.stepAux, program, startCfg, finishCfg, finalSeen, emitted,
    stores, Function.update]

@[simp] theorem step_bit (seen b : Bool) (held : Option Bool)
    (input output : List Bool) :
    TM2.step program (startCfg seen held (b :: input) output) =
      some (startCfg (seen || b) (some b) input
        (if seen || b then b :: output else output)) := by
  cases seen <;> cases b <;>
    simp [TM2.step, TM2.stepAux, program, startCfg, stores, Function.update] <;>
    funext k <;> cases k <;> rfl

/-- Every actual input word is completely consumed in exactly length+1 macrosteps.
No width oracle or semantic transition oracle is assumed. -/
theorem source_run (input output : List Bool) (seen : Bool) (held : Option Bool) :
    (sourceStep^[input.length + 1]) (some (startCfg seen held input output)) =
      some (finishCfg seen input output) := by
  induction input generalizing output seen held with
  | nil => simp [sourceStep]
  | cons b bs ih =>
    rw [List.length_cons, Nat.succ_add, Function.iterate_succ_apply]
    simp only [sourceStep, Option.bind_some, step_bit]
    have hr := ih (if seen || b then b :: output else output) (seen || b) (some b)
    cases h : seen || b <;>
      simpa [finishCfg, finalSeen, emitted, h, List.append_assoc] using hr

theorem source_halts (input output : List Bool) (seen : Bool) :
    TM2.step program (finishCfg seen input output) = none := rfl

/-- The finite compiler charge is explicit and independent of the word. -/
theorem overhead_eq : MultitapeToolkit.TM2Compiler.overhead program = 10 := by
  simp [MultitapeToolkit.TM2Compiler.overhead, MultitapeToolkit.TM2Compiler.depth, program]

/-- A genuine finite-control two-tape machine reaches and halts at the encoded
clean-source/output configuration within ten times length+1 physical transitions. -/
theorem compiled_normalize (input output : List Bool) :
    ComputesWithin (compile program) (10 * (input.length + 1))
      (encode program (startCfg false none input output))
      (encode program (finishCfg false input output)) := by
  constructor
  · simpa [overhead_eq] using compile_run program (input.length + 1)
      (startCfg false none input output) (finishCfg false input output)
      (source_run input output false none)
  · exact encode_halts program _ _

/-- The designated output is the real tape contents, not an assumed decoder. -/
theorem compiled_output (input output : List Bool) :
    readStack (trimHighZeros input ++ output).length
      ((encode program (finishCfg false input output)).tapes .output) =
      trimHighZeros input ++ output := by
  simpa [finishCfg, stores, emitted_unseen] using
    read_output program (finishCfg false input output) Stack.output

theorem compiled_source_empty (input output : List Bool) :
    (encode program (finishCfg false input output)).tapes .source = stackTape [] := rfl

/-- Concrete fixed-width interoperability: padded MSB-first n becomes Mathlib's
canonical LSB-first Nat.bits, retaining any pre-existing output suffix. -/
theorem compiled_fixedWidth {w n : Nat} (h : n < 2 ^ w) (output : List Bool) :
    ComputesWithin (compile program) (10 * (w + 1))
      (encode program (startCfg false none (fixedBits w n).reverse output))
      (encode program (finishCfg false (fixedBits w n).reverse output)) ∧
    readStack (n.bits ++ output).length
      ((encode program (finishCfg false (fixedBits w n).reverse output)).tapes .output) =
      n.bits ++ output := by
  constructor
  · simpa using compiled_normalize (fixedBits w n).reverse output
  · simpa [trimHighZeros_fixedBits_reverse h] using
      compiled_output (fixedBits w n).reverse output

end MultitapeToolkit.OutputNormalization


