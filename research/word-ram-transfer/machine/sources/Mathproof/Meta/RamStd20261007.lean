import Mathproof.Meta.Problem18RAMLax51RamPolytime20261001
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith

/-!
# `RamStd`: the house-standard word RAM

One machine for every formalization, so that no problem needs its own RAM.  It is `Lax13.Ram`
(same states, same memory update `setCell`, same conventions: every value produced is reduced
modulo `2 ^ w` and every address used is reduced modulo `2 ^ w`) with the standard word
operations that `Lax13.Ram` derives by macros made primitive:

| instruction | effect on cell `a` |
|---|---|
| `set a n` | `n` |
| `load a b`, `store a b` | indirect read and write |
| `add`, `sub` (truncated at `0`), `subw` (wrapping) | `m[b] ± m[c]` |
| `mul`, `mulhi` | low and high word of `m[b] * m[c]` |
| `div`, `mod` | `m[b] / m[c]`, `m[b] % m[c]` (`x / 0 = 0`, `x % 0 = x`) |
| `and`, `or`, `xor`, `not` | bitwise |
| `shiftl`, `shiftr` | `m[b] * 2 ^ m[c]`, `m[b] / 2 ^ m[c]` |
| `jump l`, `jzero a l`, `jlt a b l` | control: unconditional, if zero, if `m[a] < m[b]` |
| `halt`, `read a`, `write a` | halting and the input and output tapes |

Each operation costs `poly(w)` bit operations (`bitCost`), so unused operations are free in
every proof about a specific program; only the generic theorems below case-split over them.

**The kit.**
* Semantics `step`, `run`, `RunsTo`, with determinism (`runsTo_out_unique`, `runsTo_time_unique`).
* `ofLax13`: every `Lax13.Ram` program is a `RamStd` program with identical runs
  (`runsTo_ofLax13`), so every existing `Lax13` result transfers (`ramPolytime_of_lax13`).
* Bit cost: `runCost w p t s ≤ t * (w + 1) ^ 2` (`runCost_le`).
* What varies between problems is a statement parameter, never the machine:
  - `ComputesIn f p W T`: on every input `x`, at every word length `w ≥ W(n)`, the program
    halts within `T(n)` steps with output `f x` (`n` the bit size, input tape length-prefixed);
  - `RamPolytime`: `W`, `T` polynomial (the P regime);
  - `LogWordTime f T`: `W(n) = c (log₂ n + 1)`, the regime of fine-grained bounds, in which a
    program cannot pack the input into a few huge words;
  - `UsesOnly S p`: the program uses only instructions satisfying `S` (`basicOps`: no division,
    bitwise or shift instructions; `noMulOps`: additionally no multiplication), for results
    stated on a restricted machine.
-/

set_option autoImplicit false

namespace RamStd

open Lax13.Ram (State setCell initState)
open Lax51.BinaryWordEncoding

/-! ## The machine -/

inductive Instr
  | set (a n : ℕ)
  | load (a b : ℕ)
  | store (a b : ℕ)
  | add (a b c : ℕ)
  | sub (a b c : ℕ)
  | subw (a b c : ℕ)
  | mul (a b c : ℕ)
  | mulhi (a b c : ℕ)
  | div (a b c : ℕ)
  | mod (a b c : ℕ)
  | and (a b c : ℕ)
  | or (a b c : ℕ)
  | xor (a b c : ℕ)
  | not (a b : ℕ)
  | shiftl (a b c : ℕ)
  | shiftr (a b c : ℕ)
  | jump (l : ℕ)
  | jzero (a l : ℕ)
  | jlt (a b l : ℕ)
  | halt
  | read (a : ℕ)
  | write (a : ℕ)
  deriving DecidableEq

abbrev Program : Type := List Instr

/-- Write `v` to cell `a` and fall through. -/
def wr (w : ℕ) (s : State) (a v : ℕ) : Option State :=
  some ⟨s.pc + 1, setCell w s.mem a v, s.inp, s.out⟩

/-- One instruction at word length `w`; `none` iff the machine halts. -/
def Instr.effect (w : ℕ) : Instr → State → Option State
  | .set a n, s => wr w s a n
  | .load a b, s => wr w s a (s.mem (s.mem (b % 2 ^ w) % 2 ^ w))
  | .store a b, s =>
      some ⟨s.pc + 1, setCell w s.mem (s.mem (a % 2 ^ w)) (s.mem (b % 2 ^ w)), s.inp, s.out⟩
  | .add a b c, s => wr w s a (s.mem (b % 2 ^ w) + s.mem (c % 2 ^ w))
  | .sub a b c, s => wr w s a (s.mem (b % 2 ^ w) - s.mem (c % 2 ^ w))
  | .subw a b c, s => wr w s a (s.mem (b % 2 ^ w) + (2 ^ w - s.mem (c % 2 ^ w) % 2 ^ w))
  | .mul a b c, s => wr w s a (s.mem (b % 2 ^ w) * s.mem (c % 2 ^ w))
  | .mulhi a b c, s => wr w s a (s.mem (b % 2 ^ w) * s.mem (c % 2 ^ w) / 2 ^ w)
  | .div a b c, s => wr w s a (s.mem (b % 2 ^ w) / s.mem (c % 2 ^ w))
  | .mod a b c, s => wr w s a (s.mem (b % 2 ^ w) % s.mem (c % 2 ^ w))
  | .and a b c, s => wr w s a (Nat.land (s.mem (b % 2 ^ w)) (s.mem (c % 2 ^ w)))
  | .or a b c, s => wr w s a (Nat.lor (s.mem (b % 2 ^ w)) (s.mem (c % 2 ^ w)))
  | .xor a b c, s => wr w s a (Nat.xor (s.mem (b % 2 ^ w)) (s.mem (c % 2 ^ w)))
  | .not a b, s => wr w s a (2 ^ w - 1 - s.mem (b % 2 ^ w))
  | .shiftl a b c, s => wr w s a (s.mem (b % 2 ^ w) * 2 ^ s.mem (c % 2 ^ w))
  | .shiftr a b c, s => wr w s a (s.mem (b % 2 ^ w) / 2 ^ s.mem (c % 2 ^ w))
  | .jump l, s => some ⟨l, s.mem, s.inp, s.out⟩
  | .jzero a l, s => some ⟨if s.mem (a % 2 ^ w) = 0 then l else s.pc + 1, s.mem, s.inp, s.out⟩
  | .jlt a b l, s =>
      some ⟨if s.mem (a % 2 ^ w) < s.mem (b % 2 ^ w) then l else s.pc + 1, s.mem, s.inp, s.out⟩
  | .halt, _ => none
  | .read a, s => s.inp.head?.map fun v => ⟨s.pc + 1, setCell w s.mem a v, s.inp.tail, s.out⟩
  | .write a, s => some ⟨s.pc + 1, s.mem, s.inp, s.out ++ [s.mem (a % 2 ^ w) % 2 ^ w]⟩

def step (w : ℕ) (p : Program) (s : State) : Option State :=
  p[s.pc]?.bind fun i => i.effect w s

def run (w : ℕ) (p : Program) : ℕ → State → Option State
  | 0, s => some s
  | t + 1, s => (step w p s).bind (run w p t)

/-- Started on `x` at word length `w`, the program executes exactly `t` instructions and halts
with output `y`. -/
def RunsTo (w : ℕ) (p : Program) (x y : List ℕ) (t : ℕ) : Prop :=
  ∃ s : State, run w p t (initState x) = some s ∧ step w p s = none ∧ s.out = y

/-! ## Determinism -/

theorem run_add (w : ℕ) (p : Program) :
    ∀ (a b : ℕ) (s : State), run w p (a + b) s = (run w p a s).bind (run w p b)
  | 0, b, s => by simp [run]
  | a + 1, b, s => by
    rw [show a + 1 + b = (a + b) + 1 by omega]
    simp only [run]
    cases step w p s with
    | none => rfl
    | some s' => exact run_add w p a b s'

theorem run_succ_of_halt {w : ℕ} {p : Program} {s : State} (h : step w p s = none) (k : ℕ) :
    run w p (k + 1) s = none := by
  simp [run, h]

theorem runsTo_out_unique {w : ℕ} {p : Program} {x y₁ y₂ : List ℕ} {t₁ t₂ : ℕ}
    (h₁ : RunsTo w p x y₁ t₁) (h₂ : RunsTo w p x y₂ t₂) : y₁ = y₂ ∧ t₁ = t₂ := by
  obtain ⟨s₁, hr₁, hs₁, ho₁⟩ := h₁
  obtain ⟨s₂, hr₂, hs₂, ho₂⟩ := h₂
  rcases lt_trichotomy t₁ t₂ with hlt | heq | hgt
  · obtain ⟨k, rfl⟩ : ∃ k, t₂ = t₁ + (k + 1) := ⟨t₂ - t₁ - 1, by omega⟩
    rw [run_add, hr₁, Option.bind_some, run_succ_of_halt hs₁] at hr₂
    cases hr₂
  · subst heq
    rw [hr₁] at hr₂
    cases hr₂
    exact ⟨by rw [← ho₁, ← ho₂], rfl⟩
  · obtain ⟨k, rfl⟩ : ∃ k, t₁ = t₂ + (k + 1) := ⟨t₁ - t₂ - 1, by omega⟩
    rw [run_add, hr₂, Option.bind_some, run_succ_of_halt hs₂] at hr₁
    cases hr₁

/-! ## Every `Lax13.Ram` program is a `RamStd` program -/

def ofLax13 : Lax13.Ram.Instr → Instr
  | .set a n => .set a n
  | .load a b => .load a b
  | .store a b => .store a b
  | .add a b c => .add a b c
  | .sub a b c => .sub a b c
  | .mul a b c => .mul a b c
  | .div a b c => .div a b c
  | .and a b c => .and a b c
  | .shiftl a b c => .shiftl a b c
  | .not a b => .not a b
  | .jump l => .jump l
  | .jzero a l => .jzero a l
  | .halt => .halt
  | .read a => .read a
  | .write a => .write a

theorem effect_ofLax13 (w : ℕ) (i : Lax13.Ram.Instr) (s : State) :
    (ofLax13 i).effect w s = i.effect w s := by
  cases i <;> rfl

theorem step_ofLax13 (w : ℕ) (p : Lax13.Ram.Program) (s : State) :
    step w (p.map ofLax13) s = Lax13.Ram.step w p s := by
  unfold step Lax13.Ram.step
  rw [List.getElem?_map]
  cases p[s.pc]? with
  | none => rfl
  | some i => exact effect_ofLax13 w i s

theorem run_ofLax13 (w : ℕ) (p : Lax13.Ram.Program) :
    ∀ (t : ℕ) (s : State), run w (p.map ofLax13) t s = Lax13.Ram.run w p t s
  | 0, _ => rfl
  | t + 1, s => by
    simp only [run, Lax13.Ram.run, step_ofLax13]
    cases Lax13.Ram.step w p s with
    | none => rfl
    | some s' => exact run_ofLax13 w p t s'

theorem runsTo_ofLax13 {w : ℕ} {p : Lax13.Ram.Program} {x y : List ℕ} {t : ℕ} :
    RunsTo w (p.map ofLax13) x y t ↔ Lax13.Ram.RunsTo w p x y t := by
  unfold RunsTo Lax13.Ram.RunsTo
  simp only [run_ofLax13, step_ofLax13]

/-! ## Bit cost -/

/-- Bit operations of one instruction on `w`-bit words (schoolbook multiplication and division;
a shift moves at most `w` bits at most `w` places). -/
def Instr.bitCost (w : ℕ) : Instr → ℕ
  | .mul .. | .mulhi .. | .div .. | .mod .. | .shiftl .. | .shiftr .. => w * w
  | .jump _ | .halt => 1
  | _ => w

def stepCost (w : ℕ) (p : Program) (s : State) : ℕ := (p[s.pc]?.map (Instr.bitCost w)).getD 1

/-- Bit cost of the first `t` steps from `s`; the halting step is charged. -/
def runCost (w : ℕ) (p : Program) : ℕ → State → ℕ
  | 0, _ => 0
  | t + 1, s => stepCost w p s + match step w p s with
    | none => 0
    | some s' => runCost w p t s'

theorem bitCost_le (w : ℕ) (i : Instr) : Instr.bitCost w i ≤ (w + 1) ^ 2 := by
  have := Nat.one_le_pow 2 (w + 1) (by omega)
  cases i <;> simp only [Instr.bitCost] <;> nlinarith

theorem stepCost_le (w : ℕ) (p : Program) (s : State) : stepCost w p s ≤ (w + 1) ^ 2 := by
  unfold stepCost
  cases h : p[s.pc]? with
  | none => simp; exact Nat.one_le_pow 2 (w + 1) (by omega)
  | some i => simpa using bitCost_le w i

theorem runCost_le (w : ℕ) (p : Program) : ∀ (t : ℕ) (s : State),
    runCost w p t s ≤ t * (w + 1) ^ 2
  | 0, _ => by simp [runCost]
  | t + 1, s => by
    have h1 := stepCost_le w p s
    simp only [runCost]
    cases step w p s with
    | none => simp only [Nat.add_zero]; nlinarith
    | some s' =>
      have h2 := runCost_le w p t s'
      simp only; nlinarith

/-! ## The regimes: statement parameters, not machines -/

/-- On every input, at every word length `w ≥ W(n)`, the program halts within `T(n)` steps with
output `f x`; `n` is the bit size of `x`, the input tape is length-prefixed, and the input, its
length and the output fit in words of `W(n)` bits. -/
def ComputesIn (f : List ℕ → List ℕ) (p : Program) (W T : ℕ → ℕ) : Prop :=
  ∀ x : List ℕ,
    (∀ a ∈ (x.length :: x) ++ f x, a < 2 ^ W (bitSize x)) ∧
      ∀ w, W (bitSize x) ≤ w → ∃ t ≤ T (bitSize x), RunsTo w p (x.length :: x) (f x) t

/-- Polynomial time at polynomial word length (the P regime). -/
def RamPolytime (f : List ℕ → List ℕ) : Prop :=
  ∃ (p : Program) (W T : Polynomial ℕ), ComputesIn f p W.eval T.eval

/-- Time `T` at logarithmic word length `c (⌊log₂ n⌋ + 1)` (`Nat.log2`): the regime of fine-grained bounds. -/
def LogWordTime (f : List ℕ → List ℕ) (T : ℕ → ℕ) : Prop :=
  ∃ (p : Program) (c : ℕ), ComputesIn f p (fun n => c * (Nat.log2 n + 1)) T

/-- The program uses only instructions satisfying `S`. -/
def UsesOnly (S : Instr → Prop) (p : Program) : Prop := ∀ i ∈ p, S i

/-- No division, modulus, bitwise or shift instructions, and no high-word multiplication. -/
def basicOps : Instr → Prop
  | .div .. | .mod .. | .and .. | .or .. | .xor .. | .not .. | .shiftl .. | .shiftr ..
  | .mulhi .. => False
  | _ => True

/-- `basicOps` without multiplication. -/
def noMulOps : Instr → Prop
  | .mul .. => False
  | i => basicOps i

theorem usesOnly_mono {S S' : Instr → Prop} (h : ∀ i, S i → S' i) {p : Program}
    (hp : UsesOnly S p) : UsesOnly S' p := fun i hi => h i (hp i hi)

/-- Programs from `Lax13.Ram` avoid every instruction `Lax13.Ram` lacks. -/
def lax13Ops : Instr → Prop
  | .subw .. | .mulhi .. | .mod .. | .or .. | .xor .. | .shiftr .. | .jlt .. => False
  | _ => True

theorem usesOnly_ofLax13 (p : Lax13.Ram.Program) : UsesOnly lax13Ops (p.map ofLax13) := by
  intro i hi
  obtain ⟨j, -, rfl⟩ := List.mem_map.mp hi
  cases j <;> trivial

/-! ## Transfer -/

theorem computesIn_ofLax13 {f : List ℕ → List ℕ} {p : Lax13.Ram.Program} {W T : ℕ → ℕ}
    (h : ∀ x : List ℕ,
      (∀ a ∈ (x.length :: x) ++ f x, a < 2 ^ W (bitSize x)) ∧
      ∀ w, W (bitSize x) ≤ w → ∃ t ≤ T (bitSize x), Lax13.Ram.RunsTo w p (x.length :: x) (f x) t) :
    ComputesIn f (p.map ofLax13) W T := fun x =>
  ⟨(h x).1, fun w hw => by
    obtain ⟨t, ht, hr⟩ := (h x).2 w hw
    exact ⟨t, ht, runsTo_ofLax13.mpr hr⟩⟩

/-- Every `Lax13` polynomial-time result is a `RamStd` polynomial-time result. -/
theorem ramPolytime_of_lax13 {f : List ℕ → List ℕ} (h : Lax51.RamPolytime.RamPolytime f) :
    RamPolytime f := by
  obtain ⟨p, W, T, hp⟩ := h
  exact ⟨p.map ofLax13, W, T, computesIn_ofLax13 hp⟩

/-- A run within `T` steps at word length `w` costs at most `(T + 1) (w + 1) ^ 2` bit operations,
halting step included. -/
theorem runsTo_bitCost {w : ℕ} {p : Program} {x y : List ℕ} {t T : ℕ} (h : RunsTo w p x y t)
    (hT : t ≤ T) : runCost w p (t + 1) (initState x) ≤ (T + 1) * (w + 1) ^ 2 := by
  have := runCost_le w p (t + 1) (initState x)
  have : (t + 1) * (w + 1) ^ 2 ≤ (T + 1) * (w + 1) ^ 2 := Nat.mul_le_mul_right _ (by omega)
  omega

/-- Polynomial time at polynomial word length is polynomial bit cost. -/
theorem ramPolytime_bitCost {f : List ℕ → List ℕ} (h : RamPolytime f) :
    ∃ (p : Program) (W B : Polynomial ℕ), ∀ x : List ℕ, ∃ t,
      RunsTo (W.eval (bitSize x)) p (x.length :: x) (f x) t ∧
      runCost (W.eval (bitSize x)) p (t + 1) (initState (x.length :: x)) ≤ B.eval (bitSize x) := by
  obtain ⟨p, W, T, hp⟩ := h
  refine ⟨p, W, (T + 1) * (W + 1) ^ 2, fun x => ?_⟩
  obtain ⟨t, ht, hr⟩ := (hp x).2 _ le_rfl
  refine ⟨t, hr, ?_⟩
  have := runsTo_bitCost hr ht
  simpa [Polynomial.eval_mul, Polynomial.eval_add, Polynomial.eval_pow, Polynomial.eval_one]
    using this

end RamStd
