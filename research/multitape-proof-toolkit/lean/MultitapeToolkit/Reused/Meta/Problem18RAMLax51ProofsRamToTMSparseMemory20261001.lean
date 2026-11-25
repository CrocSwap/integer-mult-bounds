import MultitapeToolkit.Reused.Meta.Problem18RAMLax51RamPolytime20261001
import MultitapeToolkit.Reused.Meta.Problem18RAMLax51TuringPolytime20261001
import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsEncoding20261001
import Mathlib.Tactic.GCongr
import Mathlib.Tactic.Ring
import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsMicrocode20261001

set_option backward.isDefEq.respectTransparency false


set_option autoImplicit false

namespace Lax51Proofs.RamToTM

open Lax51Proofs.Microcode

/-- A finite association list representing the nonzero/touched fragment of
RAM memory. Missing cells read as zero. -/
def SparseMemory := List (ℕ × ℕ)

def SparseMemory.read : SparseMemory → ℕ → ℕ
  | [], _ => 0
  | (a, v) :: m, b => if b = a then v else SparseMemory.read m b

/-- Replace the first binding for an address, or insert a new binding. -/
def SparseMemory.put : SparseMemory → ℕ → ℕ → SparseMemory
  | [], a, v => [(a, v)]
  | (b, u) :: m, a, v =>
      if a = b then (a, v) :: m else (b, u) :: SparseMemory.put m a v

@[simp] theorem SparseMemory.read_nil (a : ℕ) : SparseMemory.read [] a = 0 := rfl

theorem SparseMemory.read_put_eq (m : SparseMemory) (a v : ℕ) :
    (m.put a v).read a = v := by
  induction m with
  | nil => simp [SparseMemory.put, SparseMemory.read]
  | cons bv m ih =>
      rcases bv with ⟨b, u⟩
      by_cases h : a = b
      · subst b
        simp [SparseMemory.put, SparseMemory.read]
      · simp [SparseMemory.put, SparseMemory.read, h, ih]

theorem SparseMemory.read_put_ne (m : SparseMemory) {a b v : ℕ} (h : b ≠ a) :
    (m.put a v).read b = m.read b := by
  induction m with
  | nil => simp [SparseMemory.put, SparseMemory.read, h]
  | cons cu m ih =>
      rcases cu with ⟨c, u⟩
      by_cases hac : a = c
      · subst c
        simp [SparseMemory.put, SparseMemory.read, h]
      · by_cases hbc : b = c
        · subst c
          simp [SparseMemory.put, SparseMemory.read, hac]
        · simp [SparseMemory.put, SparseMemory.read, hac, hbc, ih]

theorem SparseMemory.read_put (m : SparseMemory) (a v b : ℕ) :
    (m.put a v).read b = if b = a then v else m.read b := by
  by_cases h : b = a
  · subst b; simp [SparseMemory.read_put_eq]
  · simp [h, SparseMemory.read_put_ne m h]

/-- Word-normalized sparse write, matching the RAM's address and value
normalization.  The sparse representation is a write log: the newest binding
is prepended, and `read` selects the first matching address.  Keeping stale
bindings is extensionally harmless and makes a concrete TM write a constant
number of word transfers instead of a scan through memory. -/
def SparseMemory.write (w : ℕ) (m : SparseMemory) (a v : ℕ) : SparseMemory :=
  (a % 2 ^ w, v % 2 ^ w) :: m

theorem SparseMemory.read_write (w : ℕ) (m : SparseMemory) (a v b : ℕ) :
    (m.write w a v).read b =
      if b = a % 2 ^ w then v % 2 ^ w else m.read b := by
  simp [SparseMemory.write, SparseMemory.read]

theorem SparseMemory.write_toMem (w : ℕ) (m : SparseMemory) (a v : ℕ) :
    (m.write w a v).read = setCell w m.read a v := by
  funext b
  simp [SparseMemory.read_write, setCell]

theorem SparseMemory.put_length_le (m : SparseMemory) (a v : ℕ) :
    (m.put a v).length ≤ m.length + 1 := by
  induction m with
  | nil => simp [SparseMemory.put]
  | cons bu m ih =>
      rcases bu with ⟨b, u⟩
      by_cases h : a = b
      · simp [SparseMemory.put, h]
      · simp [SparseMemory.put, h]
        omega

theorem SparseMemory.write_length_le (w : ℕ) (m : SparseMemory) (a v : ℕ) :
    (m.write w a v).length ≤ m.length + 1 :=
  by simp [SparseMemory.write]

/-- A RAM state whose memory is represented sparsely. -/
structure SparseState where
  pc : ℕ
  acc : ℕ
  mem : SparseMemory
  inp : List ℕ
  out : List ℕ

def SparseState.toState (s : SparseState) : State where
  pc := s.pc
  acc := s.acc
  mem := s.mem.read
  inp := s.inp
  out := s.out

@[simp] theorem SparseState.toState_pc (s : SparseState) : s.toState.pc = s.pc := rfl
@[simp] theorem SparseState.toState_acc (s : SparseState) : s.toState.acc = s.acc := rfl
@[simp] theorem SparseState.toState_mem (s : SparseState) : s.toState.mem = s.mem.read := rfl
@[simp] theorem SparseState.toState_inp (s : SparseState) : s.toState.inp = s.inp := rfl
@[simp] theorem SparseState.toState_out (s : SparseState) : s.toState.out = s.out := rfl

def sparseInitState (x : List ℕ) : SparseState where
  pc := 0
  acc := 0
  mem := []
  inp := x
  out := []

@[simp] theorem sparseInitState_toState (x : List ℕ) :
    (sparseInitState x).toState = initState x := by
  rfl

def sparseValue (w : ℕ) (o : Op) (m : SparseMemory) : ℕ :=
  o.value w m.read

def sparseEffect (w : ℕ) : Instr → SparseState → Option SparseState
  | .read a, s =>
      s.inp.head?.map fun v =>
        { s with pc := s.pc + 1, mem := s.mem.write w a v, inp := s.inp.tail }
  | .write o, s =>
      some { s with pc := s.pc + 1, out := s.out ++ [sparseValue w o s.mem % 2 ^ w] }
  | .load o, s =>
      some { s with pc := s.pc + 1, acc := sparseValue w o s.mem % 2 ^ w }
  | .store a, s =>
      some { s with pc := s.pc + 1, mem := s.mem.write w a s.acc }
  | .storeInd a, s =>
      some { s with pc := s.pc + 1, mem := s.mem.write w (s.mem.read (a % 2 ^ w)) s.acc }
  | .add o, s =>
      some { s with pc := s.pc + 1, acc := (s.acc + sparseValue w o s.mem) % 2 ^ w }
  | .sub o, s =>
      some { s with pc := s.pc + 1, acc := (s.acc - sparseValue w o s.mem) % 2 ^ w }
  | .mul o, s =>
      some { s with pc := s.pc + 1, acc := (s.acc * sparseValue w o s.mem) % 2 ^ w }
  | .div o, s =>
      some { s with pc := s.pc + 1, acc := (s.acc / sparseValue w o s.mem) % 2 ^ w }
  | .and o, s =>
      some { s with pc := s.pc + 1, acc := Nat.land s.acc (sparseValue w o s.mem) % 2 ^ w }
  | .or o, s =>
      some { s with pc := s.pc + 1, acc := Nat.lor s.acc (sparseValue w o s.mem) % 2 ^ w }
  | .xor o, s =>
      some { s with pc := s.pc + 1, acc := Nat.xor s.acc (sparseValue w o s.mem) % 2 ^ w }
  | .compl _, s =>
      some { s with pc := s.pc + 1, acc := (2 ^ w - 1 - s.acc % 2 ^ w) % 2 ^ w }
  | .shiftl o, s =>
      some { s with pc := s.pc + 1, acc := s.acc * 2 ^ sparseValue w o s.mem % 2 ^ w }
  | .shiftr o, s =>
      some { s with pc := s.pc + 1, acc := s.acc / 2 ^ sparseValue w o s.mem % 2 ^ w }
  | .jump l, s => some { s with pc := l }
  | .jzero l, s => some { s with pc := if s.acc = 0 then l else s.pc + 1 }
  | .jgtz l, s => some { s with pc := if 0 < s.acc then l else s.pc + 1 }
  | .halt, _ => none

theorem sparseEffect_toState (w : ℕ) (i : Instr) (s : SparseState) :
    Option.map SparseState.toState (sparseEffect w i s) = i.effect w s.toState := by
  cases i <;> simp [sparseEffect, Instr.effect, sparseValue, SparseState.toState,
    SparseMemory.write_toMem]
  case read a => cases s.inp <;> simp [sparseEffect, Instr.effect, SparseState.toState,
    SparseMemory.write_toMem]

/-- One RAM instruction can introduce at most one new sparse-memory binding. -/
theorem sparseEffect_mem_length_le {w : ℕ} {i : Instr} {s s' : SparseState}
    (h : sparseEffect w i s = some s') : s'.mem.length ≤ s.mem.length + 1 := by
  cases i <;> simp [sparseEffect] at h
  case read a =>
    cases hin : s.inp with
    | nil => simp [hin] at h
    | cons v xs =>
      simp [hin] at h
      subst s'
      exact SparseMemory.write_length_le w s.mem a v
  all_goals
    subst s'
    simp only [SparseState.mem]
    first
    | exact SparseMemory.write_length_le _ _ _ _
    | omega

def sparseStep (w : ℕ) (p : Program) (s : SparseState) : Option SparseState :=
  p[s.pc]?.bind fun i => sparseEffect w i s

theorem sparseStep_toState (w : ℕ) (p : Program) (s : SparseState) :
    Option.map SparseState.toState (sparseStep w p s) = step w p s.toState := by
  simp only [sparseStep, step, SparseState.toState_pc]
  cases hfetch : p[s.pc]? with
  | none => simp [hfetch]
  | some i => simp [hfetch, sparseEffect_toState]

theorem sparseStep_mem_length_le {w : ℕ} {p : Program} {s s' : SparseState}
    (h : sparseStep w p s = some s') : s'.mem.length ≤ s.mem.length + 1 := by
  unfold sparseStep at h
  cases hi : p[s.pc]? with
  | none => simp [hi] at h
  | some i =>
    simp [hi] at h
    exact sparseEffect_mem_length_le (w := w) (i := i) (s := s) h

def sparseRun (w : ℕ) (p : Program) : ℕ → SparseState → Option SparseState
  | 0, s => some s
  | t + 1, s => (sparseStep w p s).bind (sparseRun w p t)

theorem sparseRun_toState (w : ℕ) (p : Program) (t : ℕ) (s : SparseState) :
    Option.map SparseState.toState (sparseRun w p t s) = run w p t s.toState := by
  induction t generalizing s with
  | zero => rfl
  | succ t ih =>
      simp only [sparseRun, run]
      cases hs : sparseStep w p s with
      | none =>
        have hdense : step w p s.toState = none := by
          have h := sparseStep_toState w p s
          simpa [hs] using h.symm
        simp [hs, hdense]
      | some s' =>
        have hdense : step w p s.toState = some s'.toState := by
          have h := sparseStep_toState w p s
          simpa [hs] using h.symm
        simp [hs, hdense, ih]

/-- After `t` instructions, sparse memory has grown by at most `t` cells. -/
theorem sparseRun_mem_length_le {w : ℕ} {p : Program} {t : ℕ} {s s' : SparseState}
    (h : sparseRun w p t s = some s') : s'.mem.length ≤ s.mem.length + t := by
  induction t generalizing s with
  | zero =>
      simp [sparseRun] at h
      subst s'
      omega
  | succ t ih =>
      simp only [sparseRun] at h
      cases hs : sparseStep w p s with
      | none => simp [hs] at h
      | some s₁ =>
        simp [hs] at h
        have hone := sparseStep_mem_length_le hs
        have hrest := ih (s := s₁) h
        omega

theorem sparseRun_init_mem_length_le {w : ℕ} {p : Program} {x : List ℕ}
    {t : ℕ} {s : SparseState} (h : sparseRun w p t (sparseInitState x) = some s) :
    s.mem.length ≤ t := by
  simpa [sparseInitState] using sparseRun_mem_length_le h

/-- Every concrete RAM run has a finite sparse-memory execution with the same
control, tapes and extensional memory. -/
theorem sparseRun_exists_of_run {w : ℕ} {p : Program} {x : List ℕ} {t : ℕ}
    {s : State} (h : run w p t (initState x) = some s) :
    ∃ ss, sparseRun w p t (sparseInitState x) = some ss ∧ ss.toState = s := by
  have hm := sparseRun_toState w p t (sparseInitState x)
  rw [sparseInitState_toState, h] at hm
  cases hs : sparseRun w p t (sparseInitState x) with
  | none => simp [hs] at hm
  | some ss =>
      simp [hs] at hm
      exact ⟨ss, rfl, hm⟩

/-- A halting dense execution has an exactly corresponding halting sparse
execution, with the same output and at most one memory binding per step. -/
theorem sparse_halts_of_runsTo {w : ℕ} {p : Program} {x y : List ℕ} {t : ℕ}
    (h : RunsTo w p x y t) :
    ∃ ss, sparseRun w p t (sparseInitState x) = some ss ∧
      sparseStep w p ss = none ∧ ss.out = y ∧ ss.mem.length ≤ t := by
  rcases h with ⟨s, hrun, hhalt, hout⟩
  rcases sparseRun_exists_of_run hrun with ⟨ss, hsrun, hstate⟩
  have hstepMap := sparseStep_toState w p ss
  rw [hstate, hhalt] at hstepMap
  have hshalt : sparseStep w p ss = none := by
    cases hs : sparseStep w p ss with
    | none => rfl
    | some ss' => simp [hs] at hstepMap
  refine ⟨ss, hsrun, hshalt, ?_, sparseRun_init_mem_length_le hsrun⟩
  simpa [← hstate] using hout

end Lax51Proofs.RamToTM
