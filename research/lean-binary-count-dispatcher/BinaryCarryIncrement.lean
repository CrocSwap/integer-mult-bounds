import FixedTapeMachine
import CarryTapePass

/-! A five-state, one-tape implementation of the existing fixed-width carry
incrementer in the explicit three-symbol tape model. Home and end markers both
encode as blank; a dedicated end-return state distinguishes their reachable
uses. Only the well-formed marked interval is simulated. No input-driven count,
width allocation, compact-record conversion, source caller or Budget is claimed. -/
namespace CurrentMain.BinaryCarryIncrement
open FixedTapeMachine

private abbrev CT := CarryTape.Tape

def symbol : CarryTape.Symbol → Symbol
  | .home | .stop => .blank
  | .zero => .zero
  | .one => .one

def tape (s : CT) : Tape :=
  ⟨s.left.map symbol, symbol (CarryTape.read s), s.right.tail.map symbol⟩

def phase (s : CT) : Fin 5 :=
  match s.phase with
  | .enter => 0
  | .carry => 1
  | .rewind => if CarryTape.read s = .stop then 2 else 3
  | .halt => 4

def action (next : Fin 5) (write : Symbol) (move : Move) : Action 1 5 :=
  ⟨next, fun _ => write, fun _ => move⟩

/-- States: enter, carry, return from end, rewind, halt. -/
def machine : Machine where
  tapes := 1
  states := 5
  initial := 0
  transition := fun s read =>
    match s.val with
    | 0 => if read (0 : Fin 1) = .blank then
        some (action 1 .blank .right) else none
    | 1 => match read (0 : Fin 1) with
      | .zero => some (action 3 .one .stay)
      | .one => some (action 1 .zero .right)
      | .blank => some (action 2 .blank .stay)
    | 2 => some (action 3 (read (0 : Fin 1)) .left)
    | 3 => if read (0 : Fin 1) = .blank then
        some (action 4 .blank .stay)
      else some (action 3 (read (0 : Fin 1)) .left)
    | _ => none

def configuration (state : Fin 5) (contents : Tape) : Configuration machine :=
  ⟨state, fun _ => contents⟩

def encode (s : CT) : Configuration machine := configuration (phase s) (tape s)

/-- Exactly the reachable phase forms of a marker-bounded increment call. The
public theorem below constructs its initial witness for every Boolean word. -/
private inductive WellFormed : CT → Prop
  | enter (bits : List Bool) : WellFormed (CarryTape.homeTape bits .enter)
  | carry (pref bits : List Bool) : WellFormed (CarryTape.carryTape pref bits)
  | rewind (pref bits : List Bool) : WellFormed (CarryTape.rewindTape pref bits)
  | home (bits : List Bool) : WellFormed (CarryTape.homeTape bits .rewind)
  | halt (bits : List Bool) : WellFormed (CarryTape.homeTape bits .halt)

private theorem wellFormed_step (s : CT) (h : WellFormed s) :
    WellFormed (CarryTape.step s).1 := by
  cases h with
  | enter bits =>
    simpa [CarryTape.step, CarryTape.homeTape, CarryTape.read, CarryTape.right,
      CarryTape.carryTape] using WellFormed.carry [] bits
  | carry pref bits =>
    cases bits with
    | nil =>
      simpa [CarryTape.step, CarryTape.carryTape, CarryTape.rewindTape,
        CarryTape.read, CarryTape.cells] using WellFormed.rewind pref []
    | cons b bits =>
      cases b with
      | false =>
        simpa [CarryTape.step, CarryTape.carryTape, CarryTape.rewindTape,
          CarryTape.read, CarryTape.cells, CarryTape.encode, CarryTape.write]
          using WellFormed.rewind pref (true :: bits)
      | true =>
        simpa [CarryTape.step, CarryTape.carryTape, CarryTape.read,
          CarryTape.cells, CarryTape.encode, CarryTape.write, CarryTape.right]
          using WellFormed.carry (false :: pref) bits
  | rewind pref bits =>
    cases pref with
    | nil =>
      cases bits with
      | nil =>
        simpa [CarryTape.step, CarryTape.rewindTape, CarryTape.homeTape,
          CarryTape.read, CarryTape.cells, CarryTape.left]
          using WellFormed.home []
      | cons b bits =>
        have h := WellFormed.home (b :: bits)
        cases b <;>
          simpa [CarryTape.step, CarryTape.rewindTape, CarryTape.homeTape,
            CarryTape.read, CarryTape.cells, CarryTape.encode, CarryTape.left] using h
    | cons b pref =>
      cases bits with
      | nil =>
        simpa [CarryTape.step, CarryTape.rewindTape, CarryTape.read,
          CarryTape.cells, CarryTape.left] using WellFormed.rewind pref [b]
      | cons c bits =>
        have h := WellFormed.rewind pref (b :: c :: bits)
        cases c <;>
          simpa [CarryTape.step, CarryTape.rewindTape, CarryTape.read,
            CarryTape.cells, CarryTape.encode, CarryTape.left] using h
  | home bits =>
    simpa [CarryTape.step, CarryTape.homeTape, CarryTape.read]
      using WellFormed.halt bits
  | halt bits =>
    simpa [CarryTape.step, CarryTape.homeTape] using WellFormed.halt bits

/-- The source halt step is inert, matching the target's saturated run. -/
private theorem step_simulation (s : CT) (h : WellFormed s) :
    run machine 1 (encode s) = encode (CarryTape.step s).1 := by
  cases h with
  | enter bits =>
    cases bits with
    | nil => rfl
    | cons b bits => cases b <;> rfl
  | carry pref bits =>
    cases bits with
    | nil => rfl
    | cons b bits =>
      cases b with
      | false => rfl
      | true =>
        cases bits with
        | nil => rfl
        | cons c bits => cases c <;> rfl
  | rewind pref bits =>
    cases pref with
    | nil =>
      cases bits with
      | nil => rfl
      | cons b bits => cases b <;> rfl
    | cons b pref =>
      cases bits with
      | nil => cases b <;> rfl
      | cons c bits => cases b <;> cases c <;> rfl
  | home bits => rfl
  | halt bits => rfl

private theorem run_simulation (n : Nat) (s : CT) (h : WellFormed s) :
    run machine n (encode s) = encode (CarryTape.run n s).1 := by
  induction n generalizing s with
  | zero => rfl
  | succ n ih =>
    have split : run machine (n + 1) (encode s) =
        run machine n (run machine 1 (encode s)) := by
      simpa only [Nat.one_add] using run_add machine 1 n (encode s)
    rw [split, step_simulation s h, ih _ (wellFormed_step s h)]
    rfl

/-- The home blank and end blank are two distinct represented cells, including
width zero. This is not the canonical Tape.ofWord representation. -/
def homeTape (bits : List Bool) : Tape :=
  ⟨[], .blank, bits.map bitSymbol ++ [.blank]⟩

def initialConfiguration (bits : List Bool) : Configuration machine :=
  configuration 0 (homeTape bits)

def finalConfiguration (bits : List Bool) : Configuration machine :=
  configuration 4 (homeTape (CarryTape.increment bits))

private theorem encode_home (bits : List Bool) (p : CarryTape.Phase) :
    tape (CarryTape.homeTape bits p) = homeTape bits := by
  change (Tape.mk [] .blank ((bits.map CarryTape.encode ++ [CarryTape.Symbol.stop]).map symbol)) =
    Tape.mk [] .blank (bits.map bitSymbol ++ [.blank])
  have maps : (bits.map CarryTape.encode).map symbol = bits.map bitSymbol := by
    rw [List.map_map]
    apply List.map_congr_left
    intro b _
    cases b <;> rfl
  simp only [List.map_append, maps, List.map_cons, List.map_nil, symbol]

/-- Exact target-table run for every width and bit pattern, including overflow.
The cost and logical update are transported from the existing carry proof. -/
theorem increment_run (bits : List Bool) :
    run machine (2 * CarryTape.trailingOnes bits + 4) (initialConfiguration bits) =
      finalConfiguration bits := by
  have h := run_simulation (2 * CarryTape.trailingOnes bits + 4)
    (CarryTape.homeTape bits .enter) (WellFormed.enter bits)
  rw [CarryTape.increment_execution] at h
  have start : encode (CarryTape.homeTape bits .enter) = initialConfiguration bits :=
    congrArg (configuration (0 : Fin 5)) (encode_home bits .enter)
  have finish : encode (CarryTape.homeTape (CarryTape.increment bits) .halt) =
      finalConfiguration bits :=
    congrArg (configuration (4 : Fin 5)) (encode_home (CarryTape.increment bits) .halt)
  exact (congrArg (run machine (2 * CarryTape.trailingOnes bits + 4)) start.symm).trans
    (h.trans finish)

theorem final_halted (bits : List Bool) : Halted machine (finalConfiguration bits) := by
  rfl

theorem increment_length (bits : List Bool) :
    (CarryTape.increment bits).length = bits.length := CarryTape.increment_length bits

/-- A representation identity only; no counter arithmetic is reproved. -/
theorem value_binding (bits : List Bool) : CarryTape.value bits = wordValue bits := by
  induction bits with
  | nil => rfl
  | cons b bits ih =>
    simpa only [CarryTape.value, wordValue, IntegerConvolution.binaryValue,
      List.map_cons, IntegerConvolution.value]
      using congrArg (fun v => (if b then 1 else 0) + 2 * v) ih

theorem increment_modular_value (bits : List Bool) :
    wordValue (CarryTape.increment bits) = (wordValue bits + 1) % 2 ^ bits.length := by
  rw [← value_binding, ← value_binding]
  exact CarryTape.increment_mod bits

end CurrentMain.BinaryCarryIncrement
#print axioms CurrentMain.BinaryCarryIncrement.increment_run
#print axioms CurrentMain.BinaryCarryIncrement.final_halted
#print axioms CurrentMain.BinaryCarryIncrement.increment_length
#print axioms CurrentMain.BinaryCarryIncrement.value_binding
#print axioms CurrentMain.BinaryCarryIncrement.increment_modular_value
