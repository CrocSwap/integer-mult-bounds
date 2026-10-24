import Mathlib.Data.List.Basic

set_option backward.isDefEq.respectTransparency false


/-!
---
title: The word RAM
type: definition
---
A word RAM is a random access machine whose cells hold *words*: natural
numbers below `2 ^ w`, for a word length `w` that is a parameter of the
model. It has a memory of `2 ^ w` cells, addressed by number, and no
other storage. Input arrives on a read-only input tape and output is
written on a write-only output tape. A program is a finite sequence of
instructions, executed in order unless a jump instruction changes the
program counter. Every instruction names the cells it works on: it sets
a cell to a literal; it reads or writes a cell through the address held
in another cell; it sets a cell to the sum, the difference, the product,
the quotient, the bitwise conjunction or the left shift of two cells, or
to the bitwise complement of one; it jumps unconditionally or if a cell
is zero; it halts; or it reads the next input number into a cell or
writes a cell to the output tape.

All arithmetic is arithmetic on words: every value the machine produces
is taken modulo `2 ^ w`, and every address is taken modulo `2 ^ w`.
Subtraction is truncated at zero rather than wrapping. Division is
integer division, with `x / 0 = 0`.

The machine starts with all memory cells zero, the whole input word on
the input tape and the output tape empty; it halts having written the
output word. The running time is the number of instructions executed,
each costing one time unit.

# Formalization notes

This is the machine the modern analysis of algorithms is stated on. Its
format is that of Cook and Reckhow (*Time bounded random access
machines*, JCSS 7, 1973): memory cells are the only storage, an
instruction is `cell ← f(cells)`, literals enter through one instruction
and indirection through two. Its numbers are bounded rather than its
instruction set, which is the discipline of Fredman and Willard
(*Surpassing the information theoretic bound with fusion trees*, JCSS
47, 1993) and of Hagerup (*Sorting and searching on the word RAM*,
STACS 1998): cells hold `w`-bit words, `w` is large enough to address
the input — `w ≥ log n`, here always written as an explicit inequality
against `2 ^ w` at the point of use — and a word operation costs one
time unit because on words it is one instruction of a real machine.
Multiplication, division, bitwise operations and shifts are then
unproblematic, and this is what makes the model the one in which the
results of the algorithms literature are actually stated. The formats
in which those results are written down simulate one another with
constant overhead (van Emde Boas, *Machine models and simulations*,
Handbook of Theoretical Computer Science A, 1990, §2).

Truncation is definitional and follows a single rule, applied
everywhere and with no exceptions: **every value the machine produces
is reduced modulo `2 ^ w` at the point of production, and every address
is reduced modulo `2 ^ w` at the point of use.** Values are produced
into memory, where `setCell` carries the reduction, and onto the output
tape, where `Instr.effect` writes it out; addresses are used by every
operand of every instruction, by the address `load` and `store` fetch
out of a cell, and by `setCell` when it writes. A literal is not
reduced where it is written down — that would be a second rule — but
the value it produces is, so an oversized literal is never observable
except through a word, and only a program's own literals can be
oversized in the first place, since every value it can read out of
memory is a word. Two consequences make the rule worth its uniformity:
every cell the machine can reach holds a word, by construction rather
than by an invariant to be proved; and the memory, although indexed by
all of `ℕ`, is touched only at the residues below `2 ^ w`, so it is
exactly the canonical `2 ^ w`-cell store. For the instructions whose
results cannot leave the words — truncated subtraction, division,
conjunction, complement — the reduction does nothing; it is written
anyway, because a rule without exceptions is easier to review than a
case distinction.

Subtraction is natural-number monus, truncated at zero, so that a
comparison is `sub` followed by `jzero`. The complement is
`2 ^ w - 1 - m[b]`, the one value that depends on the word length other
than through truncation; with `and` and `shiftl` beside it, every
bitwise operation and both shifts take a number of instructions
independent of `w`. A program measures `w` itself, by counting the
doublings of a cell from `1` until it wraps to zero, so the model needs
no instruction reporting the word length and one program serves every
word length. The remaining standard operations are derived at constant
cost; with `t` and `u` cells the program spares:

| operation | instructions | count |
|---|---|---|
| copy `a ← b` | `set t b; load a t` | 2 |
| `a ← b ∨ c` | `and t b c; sub t c t; add a b t` | 3 |
| `a ← b ⊕ c` | `and t b c; sub u c t; add u b u; sub a u t` | 4 |
| `a ← b ≫ c` | `set t 1; shiftl t t c; div a b t` | 3 |
| `a ← b mod c` | `div t b c; mul t t c; sub a b t` | 3 |
| if `b ≤ c` goto `l` | `sub t b c; jzero t l` | 2 |
| if `b < c` goto `l` | `sub t c b; jzero t l'; jump l; l':` | 3 |
| if `b = c` goto `l` | `sub t b c; sub u c b; add t t u; jzero t l` | 4 |

`read` reduces the number it takes off the input tape modulo `2 ^ w`,
like every other value, so the machine is total in its input and
honesty about inputs whose entries do not fit into a word lives on the
statement side, in the set of admissible inputs a claim quantifies
over.

Reading and writing are total: a `halt` instruction halts the machine,
an out-of-range program counter halts it, a read from an exhausted
input tape halts it, and every memory cell holds a number, so no error
states are needed. `Instr.effect` is the whole of the instruction
semantics and `step` adds only the fetch, returning `none` exactly when
the machine has halted, so the semantics is deterministic and total by
construction. `run w p t` is `t`-fold application of `step`, and it is
`none` as soon as the machine halts, which is what makes "halts after
exactly `t` steps" in `RunsTo` a statement about the *number of
instructions executed*: the time measure is intrinsic to the machine
and is not an annotation carried alongside the program. `RunsTo`
constrains the output tape and nothing else: memory is scratch space
and is left unconstrained on halting.

The input and output tapes are what makes the machine's memory start
out empty, and hence what lets a program address it by fixed cell
numbers; an input laid out in memory instead would begin at a cell
number depending on the input length. A program that wants random
access to its input copies it into memory first, at a cost of one
instruction per number.

Time is the machine's own step count, one unit per instruction, and it
is honest for multiplication precisely because the factors are words.
There is no space measure: it would be a further definition over `run`,
and space is in any case bounded by the `2 ^ w` cells the machine can
address. Randomness is absent as well; a randomized program is a
deterministic program that consumes a word list of random numbers,
which is definable downstream over this same machine, with no change to
the model.
-/

set_option autoImplicit false

namespace Lax13.Ram

/-- An instruction. The first cell named is the one written, and every
other number naming a cell is read; `set` is the only instruction
carrying a literal, and `jump`, `jzero` carry a program address. -/
inductive Instr
  /-- Set cell `a` to the literal `n`. -/
  | set (a n : ℕ)
  /-- Set cell `a` to the contents of the cell whose address cell `b`
  holds. -/
  | load (a b : ℕ)
  /-- Set the cell whose address cell `a` holds to the contents of cell
  `b`. -/
  | store (a b : ℕ)
  /-- Set cell `a` to the sum of cells `b` and `c`, wrapping around
  modulo `2 ^ w`. -/
  | add (a b c : ℕ)
  /-- Set cell `a` to the difference of cells `b` and `c`, truncated at
  zero rather than wrapping around. -/
  | sub (a b c : ℕ)
  /-- Set cell `a` to the product of cells `b` and `c`, wrapping around
  modulo `2 ^ w`. -/
  | mul (a b c : ℕ)
  /-- Set cell `a` to the quotient of cells `b` and `c`, rounding
  towards zero; division by zero yields zero. -/
  | div (a b c : ℕ)
  /-- Set cell `a` to the bitwise conjunction of cells `b` and `c`. -/
  | and (a b c : ℕ)
  /-- Set cell `a` to cell `b` shifted left by the number of bits cell
  `c` holds, wrapping around modulo `2 ^ w`; a shift by `w` or more
  yields zero. -/
  | shiftl (a b c : ℕ)
  /-- Set cell `a` to the bitwise complement `2 ^ w - 1 - m[b]` of cell
  `b` within the word length. -/
  | not (a b : ℕ)
  /-- Continue at instruction `l`. -/
  | jump (l : ℕ)
  /-- Continue at instruction `l` if cell `a` is zero. -/
  | jzero (a l : ℕ)
  /-- Halt. -/
  | halt
  /-- Read the next number of the input tape into cell `a`, or halt if
  the tape is exhausted. -/
  | read (a : ℕ)
  /-- Append the contents of cell `a` to the output tape. -/
  | write (a : ℕ)

/-- A program: a finite sequence of instructions, numbered from `0`. -/
abbrev Program : Type := List Instr

/-- A machine state: the program counter, the contents of every memory
cell, the part of the input tape not yet read, and the output tape
written so far. Memory is the only storage there is. -/
structure State where
  /-- The number of the instruction to be executed next. -/
  pc : ℕ
  /-- The contents of the memory cells; only the cells with number below
  `2 ^ w` are ever addressed. -/
  mem : ℕ → ℕ
  /-- The numbers still to be read from the input tape. -/
  inp : List ℕ
  /-- The numbers written to the output tape so far. -/
  out : List ℕ

/-- The memory `m` with cell `a` set to `v`, at word length `w`: the
address and the value written are both taken modulo `2 ^ w`. -/
def setCell (w : ℕ) (m : ℕ → ℕ) (a v : ℕ) : ℕ → ℕ :=
  fun b => if b = a % 2 ^ w then v % 2 ^ w else m b

/-- The effect of one instruction on the state at word length `w`, or
`none` if it halts the machine, which a `halt` instruction and a read
from an exhausted input tape do. Every value produced is reduced modulo
`2 ^ w` and every address used is reduced modulo `2 ^ w`. -/
def Instr.effect (w : ℕ) : Instr → State → Option State
  | set a n, s => some { s with pc := s.pc + 1, mem := setCell w s.mem a n }
  | load a b, s =>
      some
        { s with
          pc := s.pc + 1
          mem := setCell w s.mem a (s.mem (s.mem (b % 2 ^ w) % 2 ^ w)) }
  | store a b, s =>
      some
        { s with
          pc := s.pc + 1
          mem := setCell w s.mem (s.mem (a % 2 ^ w)) (s.mem (b % 2 ^ w)) }
  | add a b c, s =>
      some
        { s with
          pc := s.pc + 1
          mem := setCell w s.mem a (s.mem (b % 2 ^ w) + s.mem (c % 2 ^ w)) }
  | sub a b c, s =>
      some
        { s with
          pc := s.pc + 1
          mem := setCell w s.mem a (s.mem (b % 2 ^ w) - s.mem (c % 2 ^ w)) }
  | mul a b c, s =>
      some
        { s with
          pc := s.pc + 1
          mem := setCell w s.mem a (s.mem (b % 2 ^ w) * s.mem (c % 2 ^ w)) }
  | div a b c, s =>
      some
        { s with
          pc := s.pc + 1
          mem := setCell w s.mem a (s.mem (b % 2 ^ w) / s.mem (c % 2 ^ w)) }
  | and a b c, s =>
      some
        { s with
          pc := s.pc + 1
          mem := setCell w s.mem a (Nat.land (s.mem (b % 2 ^ w)) (s.mem (c % 2 ^ w))) }
  | shiftl a b c, s =>
      some
        { s with
          pc := s.pc + 1
          mem := setCell w s.mem a (s.mem (b % 2 ^ w) * 2 ^ s.mem (c % 2 ^ w)) }
  | not a b, s =>
      some
        { s with
          pc := s.pc + 1
          mem := setCell w s.mem a (2 ^ w - 1 - s.mem (b % 2 ^ w)) }
  | jump l, s => some { s with pc := l }
  | jzero a l, s => some { s with pc := if s.mem (a % 2 ^ w) = 0 then l else s.pc + 1 }
  | halt, _ => none
  | read a, s =>
      s.inp.head?.map fun v =>
        { s with pc := s.pc + 1, mem := setCell w s.mem a v, inp := s.inp.tail }
  | write a, s =>
      some { s with pc := s.pc + 1, out := s.out ++ [s.mem (a % 2 ^ w) % 2 ^ w] }

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

/-- The initial state on input `x`: program counter zero, all memory
cells zero, the input word on the input tape, the output tape empty. -/
def initState (x : List ℕ) : State where
  pc := 0
  mem := fun _ => 0
  inp := x
  out := []

/-- Started on input `x` at word length `w`, the machine executes
exactly `t` instructions and then halts, having written the word `y` to
its output tape. -/
def RunsTo (w : ℕ) (p : Program) (x y : List ℕ) (t : ℕ) : Prop :=
  ∃ s : State, run w p t (initState x) = some s ∧ step w p s = none ∧ s.out = y

end Lax13.Ram
