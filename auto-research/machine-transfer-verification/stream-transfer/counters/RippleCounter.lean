import TapeStack

/-! Head-local fixed-width binary ripple counting. Both delimiters and all cells
outside the counter are preserved. Lists describe configurations only; the
transition table sees one mode and one head symbol. -/
namespace RippleCounter
open Turing TapeStack

inductive Mode where
  | carry (direction : Bool)
  | rewind (overflow : Bool)
  | done (overflow : Bool)
  deriving DecidableEq, Fintype

structure Config where
  mode : Mode
  tape : Tape Symbol

structure Instruction where
  next : Mode
  action : Action
  deriving Fintype

/-- `true` increments; `false` decrements. The terminal flag reports carry
out, respectively borrow out (which is an exact input-zero test). -/
def instruction (mode : Mode) (head : Symbol) : Instruction :=
  match mode with
  | .carry d => match head with
    | .bit b => if b = d then ⟨.carry d, ⟨some (.bit (!b)), .right⟩⟩
                else ⟨.rewind false, ⟨some (.bit (!b)), .left⟩⟩
    | .separator => ⟨.rewind true, ⟨none, .left⟩⟩
    | .blank => ⟨.done false, {}⟩
  | .rewind flag => match head with
    | .bit _ => ⟨.rewind flag, ⟨none, .left⟩⟩
    | .separator => ⟨.done flag, ⟨none, .right⟩⟩
    | .blank => ⟨.done flag, {}⟩
  | .done flag => ⟨.done flag, {}⟩

def step (c : Config) : Config :=
  let i := instruction c.mode c.tape.head
  ⟨i.next, perform i.action c.tape⟩

def run : ℕ → Config → Config
  | 0, c => c
  | n+1, c => run n (step c)

theorem state_card : Fintype.card Mode = 6 := by decide

theorem run_add (n k : ℕ) (c : Config) : run (n+k) c = run k (run n c) := by
  induction n generalizing c with
  | zero => simp [run]
  | succ n ih => simpa only [Nat.succ_add, run] using ih (step c)

/-- Processed prefix is stored nearest-first, as required by `Tape.mk₂`. -/
def position (left bits : List Bool) (ancestor suffix : List Symbol) : Tape Symbol :=
  Tape.mk₂ (left.map .bit ++ .separator :: ancestor) (bits.map .bit ++ .separator :: suffix)

def ready (bits : List Bool) (ancestor suffix : List Symbol) : Tape Symbol :=
  position [] bits ancestor suffix

def rewinding (left right : List Bool) (ancestor suffix : List Symbol) : Tape Symbol :=
  match left with
  | [] => ⟨.separator, ListBlank.mk ancestor, ListBlank.mk (right.map .bit ++ .separator :: suffix)⟩
  | b::rest => ⟨.bit b, ListBlank.mk (rest.map .bit ++ .separator :: ancestor),
      ListBlank.mk (right.map .bit ++ .separator :: suffix)⟩

def carryLength (d : Bool) : List Bool → ℕ
  | [] => 0
  | b::rest => if b = d then carryLength d rest + 1 else 0

def stopTail (d : Bool) : List Bool → List Bool
  | [] => []
  | b::rest => if b = d then stopTail d rest else (!b) :: rest

def overflow (d : Bool) : List Bool → Bool
  | [] => true
  | b::rest => if b = d then overflow d rest else false

def updated (d : Bool) (bits : List Bool) : List Bool :=
  List.replicate (carryLength d bits) (!d) ++ stopTail d bits

def steps (d : Bool) (bits : List Bool) : ℕ := 2 * carryLength d bits + 2

theorem write_right (b : Bool) (left rest : List Bool) (ancestor suffix : List Symbol) :
    ((position left (b::rest) ancestor suffix).write (.bit (!b))).move .right =
      position ((!b)::left) rest ancestor suffix := by
  simp [position, Tape.mk₂, Tape.mk', Tape.write, Tape.move, ListBlank.head_mk,
    ListBlank.tail_mk, ListBlank.cons_mk]

theorem write_left (b : Bool) (left rest : List Bool) (ancestor suffix : List Symbol) :
    ((position left (b::rest) ancestor suffix).write (.bit (!b))).move .left =
      rewinding left ((!b)::rest) ancestor suffix := by
  cases left <;> simp [position, rewinding, Tape.mk₂, Tape.mk', Tape.write, Tape.move,
    ListBlank.head_mk, ListBlank.tail_mk, ListBlank.cons_mk]

theorem delimiter_left (left : List Bool) (ancestor suffix : List Symbol) :
    (position left [] ancestor suffix).move .left = rewinding left [] ancestor suffix := by
  cases left <;> simp [position, rewinding, Tape.mk₂, Tape.mk', Tape.move,
    ListBlank.head_mk, ListBlank.tail_mk, ListBlank.cons_mk]

theorem rewind_left (b : Bool) (left right : List Bool) (ancestor suffix : List Symbol) :
    (rewinding (b::left) right ancestor suffix).move .left =
      rewinding left (b::right) ancestor suffix := by
  cases left <;> simp [rewinding, Tape.move, ListBlank.head_mk,
    ListBlank.tail_mk, ListBlank.cons_mk]

theorem rewind_origin (right : List Bool) (ancestor suffix : List Symbol) :
    (rewinding [] right ancestor suffix).move .right = ready right ancestor suffix := by
  simp [rewinding, ready, position, Tape.mk₂, Tape.mk', Tape.move,
    ListBlank.head_mk, ListBlank.tail_mk, ListBlank.cons_mk]

theorem rewind_correct (left right : List Bool) (ancestor suffix : List Symbol) (flag : Bool) :
    run (left.length + 1) ⟨.rewind flag, rewinding left right ancestor suffix⟩ =
      ⟨.done flag, ready (left.reverse ++ right) ancestor suffix⟩ := by
  induction left generalizing right with
  | nil =>
    change Config.mk (.done flag) ((rewinding [] right ancestor suffix).move .right) = _
    rw [rewind_origin]
    rfl
  | cons b rest ih =>
    rw [List.length_cons, Nat.succ_add, run]
    change run (rest.length + 1) ⟨.rewind flag,
      (rewinding (b::rest) right ancestor suffix).move .left⟩ = _
    rw [rewind_left, ih]
    simp [List.reverse_cons, List.append_assoc]

theorem carry_correct (d : Bool) (bits left : List Bool) (ancestor suffix : List Symbol) :
    run (carryLength d bits + 1) ⟨.carry d, position left bits ancestor suffix⟩ =
      ⟨.rewind (overflow d bits),
        rewinding (List.replicate (carryLength d bits) (!d) ++ left)
          (stopTail d bits) ancestor suffix⟩ := by
  induction bits generalizing left with
  | nil =>
    change Config.mk (.rewind true) ((position left [] ancestor suffix).move .left) = _
    rw [delimiter_left]
    rfl
  | cons b rest ih =>
    by_cases h : b = d
    · subst b
      simp only [carryLength, stopTail, overflow, if_pos]
      rw [run]
      simp only [step, show (position left (d::rest) ancestor suffix).head = .bit d from rfl,
        instruction, if_pos, perform]
      rw [write_right, ih]
      simp [List.replicate_succ', List.append_assoc]
    · simp only [carryLength, stopTail, overflow, if_neg h]
      simp only [run, step, show (position left (b::rest) ancestor suffix).head = .bit b from rfl,
        instruction, if_neg h, perform]
      rw [write_left]
      rfl

/-- Actual finite-table execution, including return of the tape head, with an
exact number of steps uniform in arbitrary untouched exterior tape contents. -/
theorem counter_correct (d : Bool) (bits : List Bool) (ancestor suffix : List Symbol) :
    run (steps d bits) ⟨.carry d, ready bits ancestor suffix⟩ =
      ⟨.done (overflow d bits), ready (updated d bits) ancestor suffix⟩ := by
  have count : steps d bits = (carryLength d bits + 1) + (carryLength d bits + 1) := by
    simp [steps]; omega
  rw [count, run_add]
  change run (carryLength d bits + 1)
    (run (carryLength d bits + 1) ⟨.carry d, position [] bits ancestor suffix⟩) = _
  rw [carry_correct]
  simp only [List.append_nil]
  have h := rewind_correct (List.replicate (carryLength d bits) (!d))
    (stopTail d bits) ancestor suffix (overflow d bits)
  simpa [updated] using h

def active : Mode → Bool
  | .carry _ => true
  | .rewind _ => true
  | .done _ => false

theorem rewind_running (left right : List Bool) (ancestor suffix : List Symbol)
    (flag : Bool) (n : ℕ) (hn : n < left.length + 1) :
    active (run n ⟨.rewind flag, rewinding left right ancestor suffix⟩).mode = true := by
  induction left generalizing right n with
  | nil =>
    have : n = 0 := by simpa using hn
    subst n
    rfl
  | cons b rest ih =>
    cases n with
    | zero => rfl
    | succ n =>
      rw [run]
      change active (run n ⟨.rewind flag,
        (rewinding (b::rest) right ancestor suffix).move .left⟩).mode = true
      rw [rewind_left]
      apply ih (b::right) n
      simpa using hn

theorem carry_running (d : Bool) (bits left : List Bool) (ancestor suffix : List Symbol)
    (n : ℕ) (hn : n < carryLength d bits + 1) :
    active (run n ⟨.carry d, position left bits ancestor suffix⟩).mode = true := by
  induction bits generalizing left n with
  | nil =>
    have : n = 0 := by simpa [carryLength] using hn
    subst n
    rfl
  | cons b rest ih =>
    by_cases h : b = d
    · subst b
      cases n with
      | zero => rfl
      | succ n =>
        rw [run]
        simp only [step, show (position left (d::rest) ancestor suffix).head = .bit d from rfl,
          instruction, if_pos, perform]
        rw [write_right]
        apply ih ((!d)::left) n
        simpa [carryLength] using hn
    · have : n = 0 := by simpa [carryLength, h] using hn
      subst n
      rfl

/-- The reported transition count is the FIRST completed state. This supports
composition with a surrounding finite controller that acts immediately on done. -/
theorem counter_running (d : Bool) (bits : List Bool) (ancestor suffix : List Symbol)
    (n : ℕ) (hn : n < steps d bits) :
    active (run n ⟨.carry d, ready bits ancestor suffix⟩).mode = true := by
  by_cases he : n < carryLength d bits + 1
  · exact carry_running d bits [] ancestor suffix n he
  · have hle : carryLength d bits + 1 ≤ n := by omega
    have heq : n = (carryLength d bits + 1) + (n - (carryLength d bits + 1)) := by omega
    rw [heq, run_add]
    change active (run (n - (carryLength d bits + 1))
      (run (carryLength d bits + 1) ⟨.carry d, position [] bits ancestor suffix⟩)).mode = true
    rw [carry_correct]
    simp only [List.append_nil]
    apply rewind_running
    simp only [List.length_replicate]
    unfold steps at hn
    omega

end RippleCounter

#print axioms RippleCounter.state_card
#print axioms RippleCounter.run_add
#print axioms RippleCounter.write_right
#print axioms RippleCounter.write_left
#print axioms RippleCounter.delimiter_left
#print axioms RippleCounter.rewind_left
#print axioms RippleCounter.rewind_origin
#print axioms RippleCounter.rewind_correct
#print axioms RippleCounter.carry_correct
#print axioms RippleCounter.counter_correct
#print axioms RippleCounter.rewind_running
#print axioms RippleCounter.carry_running
#print axioms RippleCounter.counter_running
