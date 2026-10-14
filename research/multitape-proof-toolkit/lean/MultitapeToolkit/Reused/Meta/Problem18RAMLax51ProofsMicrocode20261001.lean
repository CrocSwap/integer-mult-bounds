import MultitapeToolkit.Reused.Meta.Problem18RAMLax13Ram20261001

set_option backward.isDefEq.respectTransparency false


/-!
Proof-internal accumulator microcode for the Turing simulator. Based on the
Lax13 accumulator semantics at d35ba57ad420ce6a6d3c763aa7f6a4a8be1d406d,
with a word-complement operation added for the cell-to-cell translation.

This is NOT the public RAM model. Public programs and executions use
`Lax13.Ram`; a separate checked translation must connect them to this
intermediate language. The accumulator is represented by a Turing work tape.
-/

set_option autoImplicit false

namespace Lax51Proofs.Microcode

/-- An operand: a literal, the contents of a memory cell, or the
contents of the cell addressed by a memory cell. -/
inductive Op
  /-- The literal number `n`. -/
  | lit (n : ℕ)
  /-- The contents of cell `a`. -/
  | mem (a : ℕ)
  /-- The contents of the cell whose address is the contents of cell
  `a`. -/
  | ind (a : ℕ)

/-- An instruction: tape transfers, accumulator transfers, arithmetic,
bitwise operations, jumps, and halting. -/
inductive Instr
  /-- Read the next number of the input tape into cell `a`. -/
  | read (a : ℕ)
  /-- Append the value of the operand to the output tape. -/
  | write (o : Op)
  /-- Load the operand into the accumulator. -/
  | load (o : Op)
  /-- Store the accumulator into cell `a`. -/
  | store (a : ℕ)
  /-- Store the accumulator into the cell addressed by cell `a`. -/
  | storeInd (a : ℕ)
  /-- Add the operand to the accumulator, wrapping around modulo
  `2 ^ w`. -/
  | add (o : Op)
  /-- Subtract the operand from the accumulator, truncated at zero
  rather than wrapping around. -/
  | sub (o : Op)
  /-- Multiply the accumulator by the operand, wrapping around modulo
  `2 ^ w`. -/
  | mul (o : Op)
  /-- Divide the accumulator by the operand, rounding towards zero;
  division by zero yields zero. -/
  | div (o : Op)
  /-- Replace the accumulator by its bitwise conjunction with the
  operand. -/
  | and (o : Op)
  /-- Replace the accumulator by its bitwise disjunction with the
  operand. -/
  | or (o : Op)
  /-- Replace the accumulator by its bitwise exclusive or with the
  operand. -/
  | xor (o : Op)
  /-- Complement the accumulator's low word; the operand is ignored. -/
  | compl (o : Op)
  /-- Shift the accumulator left by the operand many bits, wrapping
  around modulo `2 ^ w`; a shift by `w` or more yields zero. -/
  | shiftl (o : Op)
  /-- Shift the accumulator right by the operand many bits, discarding
  the bits shifted out. -/
  | shiftr (o : Op)
  /-- Continue at instruction `l`. -/
  | jump (l : ℕ)
  /-- Continue at instruction `l` if the accumulator is zero. -/
  | jzero (l : ℕ)
  /-- Continue at instruction `l` if the accumulator is positive. -/
  | jgtz (l : ℕ)
  /-- Halt. -/
  | halt

/-- A program: a finite sequence of instructions, numbered from `0`. -/
abbrev Program : Type := List Instr

/-- A machine state: the program counter, the accumulator, the contents
of every memory cell, the part of the input tape not yet read, and the
output tape written so far. -/
structure State where
  /-- The number of the instruction to be executed next. -/
  pc : ℕ
  /-- The accumulator. -/
  acc : ℕ
  /-- The contents of the memory cells; only the cells with number below
  `2 ^ w` are ever addressed. -/
  mem : ℕ → ℕ
  /-- The numbers still to be read from the input tape. -/
  inp : List ℕ
  /-- The numbers written to the output tape so far. -/
  out : List ℕ

/-- The value of an operand in a memory, at word length `w`: every
address is taken modulo `2 ^ w` before the cell it names is read. -/
def Op.value (w : ℕ) : Op → (ℕ → ℕ) → ℕ
  | lit n, _ => n
  | mem a, m => m (a % 2 ^ w)
  | ind a, m => m (m (a % 2 ^ w) % 2 ^ w)

/-- The memory `m` with cell `a` set to `v`, at word length `w`: the
address and the value written are both taken modulo `2 ^ w`. -/
def setCell (w : ℕ) (m : ℕ → ℕ) (a v : ℕ) : ℕ → ℕ :=
  fun b => if b = a % 2 ^ w then v % 2 ^ w else m b

/-- The effect of one instruction on the state at word length `w`, or
`none` if it halts the machine, which a `halt` instruction and a read
from an exhausted input tape do. Every value produced is reduced modulo
`2 ^ w` and every address used is reduced modulo `2 ^ w`. -/
def Instr.effect (w : ℕ) : Instr → State → Option State
  | read a, s =>
      s.inp.head?.map fun v =>
        { s with pc := s.pc + 1, mem := setCell w s.mem a v, inp := s.inp.tail }
  | write o, s =>
      some { s with pc := s.pc + 1, out := s.out ++ [o.value w s.mem % 2 ^ w] }
  | load o, s => some { s with pc := s.pc + 1, acc := o.value w s.mem % 2 ^ w }
  | store a, s => some { s with pc := s.pc + 1, mem := setCell w s.mem a s.acc }
  | storeInd a, s =>
      some { s with pc := s.pc + 1, mem := setCell w s.mem (s.mem (a % 2 ^ w)) s.acc }
  | add o, s => some { s with pc := s.pc + 1, acc := (s.acc + o.value w s.mem) % 2 ^ w }
  | sub o, s => some { s with pc := s.pc + 1, acc := (s.acc - o.value w s.mem) % 2 ^ w }
  | mul o, s => some { s with pc := s.pc + 1, acc := (s.acc * o.value w s.mem) % 2 ^ w }
  | div o, s => some { s with pc := s.pc + 1, acc := (s.acc / o.value w s.mem) % 2 ^ w }
  | and o, s => some { s with pc := s.pc + 1, acc := Nat.land s.acc (o.value w s.mem) % 2 ^ w }
  | or o, s => some { s with pc := s.pc + 1, acc := Nat.lor s.acc (o.value w s.mem) % 2 ^ w }
  | xor o, s => some { s with pc := s.pc + 1, acc := Nat.xor s.acc (o.value w s.mem) % 2 ^ w }
  | compl _, s =>
      some { s with pc := s.pc + 1, acc := (2 ^ w - 1 - s.acc % 2 ^ w) % 2 ^ w }
  | shiftl o, s =>
      some { s with pc := s.pc + 1, acc := s.acc * 2 ^ o.value w s.mem % 2 ^ w }
  | shiftr o, s =>
      some { s with pc := s.pc + 1, acc := s.acc / 2 ^ o.value w s.mem % 2 ^ w }
  | jump l, s => some { s with pc := l }
  | jzero l, s => some { s with pc := if s.acc = 0 then l else s.pc + 1 }
  | jgtz l, s => some { s with pc := if 0 < s.acc then l else s.pc + 1 }
  | halt, _ => none

/-- One step of the machine at word length `w`: fetch the instruction
the program counter points at and execute it. The result is `none` if
the machine has halted, which also happens when the program counter has
run past the program. -/
def step (w : ℕ) (p : Program) (s : State) : Option State :=
  p[s.pc]?.bind fun i => i.effect w s

/-- The state after `t` steps at word length `w`, or `none` if the
machine halts before executing `t` instructions. -/
def run (w : ℕ) (p : Program) : ℕ → State → Option State
  | 0, s => some s
  | t + 1, s => (step w p s).bind (run w p t)

/-- The initial state on input `x`: program counter and accumulator
zero, all memory cells zero, the input word on the input tape, the
output tape empty. -/
def initState (x : List ℕ) : State where
  pc := 0
  acc := 0
  mem := fun _ => 0
  inp := x
  out := []

/-- Started on input `x` at word length `w`, the machine executes
exactly `t` instructions and then halts, having written the word `y` to
its output tape. -/
def RunsTo (w : ℕ) (p : Program) (x y : List ℕ) (t : ℕ) : Prop :=
  ∃ s : State, run w p t (initState x) = some s ∧ step w p s = none ∧ s.out = y

end Lax51Proofs.Microcode

