import RowEvaluation

/-!
Sound symbolic execution of the normalized bit word. The same total gate
semantics runs on coefficient rows and Boolean values. A separate checker
verifies register ranges and the copy/erase clean-temporary preconditions.
Frame operations (opcode 0) act trivially in these normalized coordinates;
identifying those coordinates with physical streams requires a separate
frame invariant, not this linear replay theorem.
-/
namespace LinearReplay

structure Event where
  op : Nat
  x : Nat
  y : Nat
  odd : Bool
  deriving DecidableEq

def step (zero : α) (xor : α → α → α) (s : Array α) (e : Event) : Array α :=
  match e.op with
  | 0 => s
  | 1 => if e.odd then s.setIfInBounds e.x (xor (s.getD e.x zero) (s.getD e.y zero)) else s
  | 2 => s.setIfInBounds e.y (s.getD e.x zero)
  | _ => s.setIfInBounds e.y zero

def run (zero : α) (xor : α → α → α) (es : List Event) (s : Array α) : Array α :=
  es.foldl (step zero xor) s

def rowStep := step (0 : Nat) (· ^^^ ·)
def boolStep := step false (· ^^ ·)
def runRows := run (0 : Nat) (· ^^^ ·)
def runBools := run false (· ^^ ·)

def rowChecks (s : Array Nat) (e : Event) : Bool :=
  match e.op with
  | 0 => e.x < 987
  | 1 => e.x < 987 && e.y <= 987 && e.x != e.y
  | 2 => e.x < 987 && e.y == 987 && s.getD e.y 0 == 0
  | 3 => e.x < 987 && e.y == 987 && s.getD e.x 0 == s.getD e.y 0
  | _ => false

def checkedRowStep (s : Array Nat × Bool) (e : Event) : Array Nat × Bool :=
  (rowStep s.1 e, s.2 && rowChecks s.1 e)

def runCheckedRows (es : List Event) (s : Array Nat × Bool) : Array Nat × Bool :=
  es.foldl checkedRowStep s

def evalRows (n : Nat) (u : Nat → Bool) (s : Array Nat) : Array Bool :=
  s.map (evalRow n u)

theorem map_getD (f : α → β) (s : Array α) (i : Nat) (zero : α) :
    (s.map f).getD i (f zero) = f (s.getD i zero) := by
  simp only [Array.getD_eq_getD_getElem?, Array.getElem?_map]
  cases s[i]? <;> rfl

theorem step_map (zero : α) (zero' : β) (xor : α → α → α) (xor' : β → β → β)
    (f : α → β) (hzero : f zero = zero')
    (hxor : ∀ a b, f (xor a b) = xor' (f a) (f b)) (s : Array α) (e : Event) :
    (step zero xor s e).map f = step zero' xor' (s.map f) e := by
  obtain ⟨op, x, y, odd⟩ := e
  cases op with
  | zero => rfl
  | succ op =>
      cases op with
      | zero =>
          cases odd <;> simp [step, hxor, ← hzero]
      | succ op =>
          cases op with
          | zero => simp [step, ← hzero]
          | succ op => simp [step, hzero]

theorem run_map (zero : α) (zero' : β) (xor : α → α → α) (xor' : β → β → β)
    (f : α → β) (hzero : f zero = zero')
    (hxor : ∀ a b, f (xor a b) = xor' (f a) (f b)) (es : List Event) (s : Array α) :
    (run zero xor es s).map f = run zero' xor' es (s.map f) := by
  induction es generalizing s with
  | nil => rfl
  | cons e es ih =>
      change (run zero xor es (step zero xor s e)).map f =
        run zero' xor' es (step zero' xor' (s.map f) e)
      rw [ih, step_map zero zero' xor xor' f hzero hxor]

theorem evalRows_step (n : Nat) (u : Nat → Bool) (s : Array Nat) (e : Event) :
    evalRows n u (rowStep s e) = boolStep (evalRows n u s) e := by
  exact step_map 0 false (· ^^^ ·) (· ^^ ·) (evalRow n u)
    (evalRow_zero n u) (evalRow_xor n u) s e

theorem evalRows_run (n : Nat) (u : Nat → Bool) (es : List Event) (s : Array Nat) :
    evalRows n u (runRows es s) = runBools es (evalRows n u s) := by
  exact run_map 0 false (· ^^^ ·) (· ^^ ·) (evalRow n u)
    (evalRow_zero n u) (evalRow_xor n u) es s

theorem checked_projection (es : List Event) (s : Array Nat × Bool) :
    (runCheckedRows es s).1 = runRows es s.1 := by
  induction es generalizing s with
  | nil => rfl
  | cons e es ih =>
      exact ih (checkedRowStep s e)

def basisRows (n : Nat) : Array Nat :=
  (Array.range (n + 1)).map fun i => if i < n then 1 <<< i else 0

def dirtyInput (n : Nat) (u : Nat → Bool) : Array Bool :=
  (Array.range (n + 1)).map fun i => if i < n then u i else false

theorem evalRows_basisRows (n : Nat) (u : Nat → Bool) :
    evalRows n u (basisRows n) = dirtyInput n u := by
  simp only [evalRows, basisRows, dirtyInput, Array.map_map]
  congr 1
  funext i
  by_cases h : i < n <;> simp [h, evalRow_shift_basis]

def boolChecks (s : Array Bool) (e : Event) : Bool :=
  match e.op with
  | 0 => e.x < 987
  | 1 => e.x < 987 && e.y <= 987 && e.x != e.y
  | 2 => e.x < 987 && e.y == 987 && !(s.getD e.y false)
  | 3 => e.x < 987 && e.y == 987 && s.getD e.x false == s.getD e.y false
  | _ => false

def checkedBoolStep (s : Array Bool × Bool) (e : Event) : Array Bool × Bool :=
  (boolStep s.1 e, s.2 && boolChecks s.1 e)

def runCheckedBools (es : List Event) (s : Array Bool × Bool) : Array Bool × Bool :=
  es.foldl checkedBoolStep s

theorem evalRows_getD (n : Nat) (u : Nat → Bool) (s : Array Nat) (i : Nat) :
    (evalRows n u s).getD i false = evalRow n u (s.getD i 0) := by
  simpa [evalRows] using map_getD (evalRow n u) s i 0

theorem checks_sound (n : Nat) (u : Nat → Bool) (s : Array Nat) (e : Event)
    (h : rowChecks s e = true) : boolChecks (evalRows n u s) e = true := by
  obtain ⟨op, x, y, odd⟩ := e
  cases op with
  | zero => exact h
  | succ op =>
      cases op with
      | zero => exact h
      | succ op =>
          cases op with
          | zero =>
              simp only [rowChecks, Bool.and_eq_true, beq_iff_eq] at h
              simp only [boolChecks, Bool.and_eq_true, beq_iff_eq, evalRows_getD]
              exact ⟨h.1, by simp [h.2]⟩
          | succ op =>
              cases op with
              | zero =>
                  simp only [rowChecks, Bool.and_eq_true, beq_iff_eq] at h
                  simp only [boolChecks, Bool.and_eq_true, beq_iff_eq, evalRows_getD]
                  exact ⟨h.1, congrArg (evalRow n u) h.2⟩
              | succ op => cases h

theorem checked_flag_mono (es : List Event) (s : Array Nat × Bool)
    (h : (runCheckedRows es s).2 = true) : s.2 = true := by
  induction es generalizing s with
  | nil => exact h
  | cons e es ih =>
      have h' := ih (checkedRowStep s e) h
      exact (Bool.and_eq_true_iff.mp h').1

theorem checked_guards_sound (n : Nat) (u : Nat → Bool) (es : List Event)
    (s : Array Nat × Bool) (h : (runCheckedRows es s).2 = true) :
    (runCheckedBools es (evalRows n u s.1, s.2)).2 = true := by
  induction es generalizing s with
  | nil => exact h
  | cons e es ih =>
      have hfirst := checked_flag_mono es (checkedRowStep s e) h
      have hparts : s.2 = true ∧ rowChecks s.1 e = true := by
        simpa only [checkedRowStep, Bool.and_eq_true] using hfirst
      have hb := checks_sound n u s.1 e hparts.2
      have hi := ih (checkedRowStep s e) h
      simpa only [runCheckedBools, List.foldl_cons, checkedBoolStep,
        evalRows_step, checkedRowStep, hparts.1, hparts.2, hb] using hi

end LinearReplay
