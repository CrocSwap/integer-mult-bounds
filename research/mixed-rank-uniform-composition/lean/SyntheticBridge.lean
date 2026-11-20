import Std

namespace SyntheticBridge

structure Gaussian where
  re : Int
  im : Int
  deriving DecidableEq, Repr

inductive Step where
  | ident | quarter | plusI | minusI | twice | negTwice
  deriving DecidableEq, Repr

def act (s : Step) (v : Gaussian) : Gaussian :=
  match s with
  | .ident => v
  | .quarter => ⟨-v.im, v.re⟩
  | .plusI => ⟨v.re - v.im, v.re + v.im⟩
  | .minusI => ⟨v.re + v.im, v.im - v.re⟩
  | .twice => ⟨2 * v.re, 2 * v.im⟩
  | .negTwice => ⟨-2 * v.re, -2 * v.im⟩

theorem commute (s t : Step) (v : Gaussian) : act s (act t v) = act t (act s v) := by
  cases s <;> cases t <;> cases v <;> simp [act, Gaussian.mk.injEq] <;> omega

def run : List Step → Gaussian → Gaussian
  | [], v => v
  | s :: rest, v => act s (run rest v)

theorem pull (xs : List Step) (s : Step) (v : Gaussian) :
    run xs (act s v) = act s (run xs v) := by
  induction xs with
  | nil => rfl
  | cons t ts ih =>
    simp only [run, ih]
    exact commute t s _

abbrev Slot := Bool × Bool

def phase (b : Bool) : Step := if b then .quarter else .ident

def native (x : Slot) : Step := if x.1 == x.2 then .plusI else .minusI

def halfNumerator (x : Slot) : Step := if x.1 && x.2 then .negTwice else .twice

theorem oneSlot (x : Slot) (v : Gaussian) :
    act .minusI (act (phase x.1) (act (native x) (act (phase x.2) v))) =
      act (halfNumerator x) v := by
  obtain ⟨r, c⟩ := x
  cases r <;> cases c <;> cases v <;>
    simp [phase, native, halfNumerator, act, Gaussian.mk.injEq] <;> omega

/-- Matrix coefficient of b^h D C^tensor(h) D, applied to the given Gaussian
numerator after clearing the common denominator 4^h. A slot is (row bit, column bit). -/
def completed (xs : List Slot) (v : Gaussian) : Gaussian :=
  run (xs.map fun _ => Step.minusI)
    (run (xs.map fun x => phase x.1)
      (run (xs.map native) (run (xs.map fun x => phase x.2) v)))

theorem completed_cons (x : Slot) (xs : List Slot) (v : Gaussian) :
    completed (x :: xs) v = act (halfNumerator x) (completed xs v) := by
  simp only [completed, List.map_cons, run, pull]
  rw [commute (phase x.2) .minusI, commute (phase x.2) (phase x.1),
    commute (phase x.2) (native x), oneSlot]

/-- Every coefficient of the completed native layer equals the corresponding
coefficient of H0^tensor(h) at that same cleared denominator. -/
theorem allWidths (xs : List Slot) (v : Gaussian) :
    completed xs v = run (xs.map halfNumerator) v := by
  induction xs with
  | nil => rfl
  | cons x xs ih => simp only [completed_cons, ih, List.map_cons, run]

def sign (x : Slot) : Int := if x.1 && x.2 then -1 else 1

def scale (a : Int) (v : Gaussian) : Gaussian := ⟨a * v.re, a * v.im⟩

theorem scales (a b : Int) (v : Gaussian) : scale a (scale b v) = scale (a * b) v := by
  simp [scale, Int.mul_assoc]

theorem oneSign (x : Slot) (v : Gaussian) :
    act (halfNumerator x) v = scale (2 * sign x) v := by
  obtain ⟨r, c⟩ := x
  cases r <;> cases c <;> simp [sign, halfNumerator, scale, act]

/-- At denominator 4^h, the unabsorbed scalar is 2^h times the signed
row/column Hadamard character. Dividing gives the normalization 1/2^h. -/
theorem clearedCharacter (xs : List Slot) (v : Gaussian) :
    completed xs v = scale (2 ^ xs.length * (xs.map sign).prod) v := by
  induction xs with
  | nil => cases v <;> simp [completed, run, scale]
  | cons x xs ih =>
    rw [completed_cons, ih, oneSign, scales]
    congr 1
    simp [Int.pow_succ, Int.mul_assoc, Int.mul_left_comm, Int.mul_comm]

def sum : List Gaussian → Gaussian
  | [] => ⟨0, 0⟩
  | v :: vs => ⟨v.re + (sum vs).re, v.im + (sum vs).im⟩

/-- The source coordinates and their signed dyadic numerators may be arbitrary.
Use all columns of any fixed row to obtain the complete operator equality. -/
theorem anyInputs (inputs : List (List Slot × Gaussian)) :
    sum (inputs.map fun it => completed it.1 it.2) =
    sum (inputs.map fun it => run (it.1.map halfNumerator) it.2) := by
  simp only [allWidths]

#print axioms allWidths
#print axioms anyInputs
#print axioms clearedCharacter

end SyntheticBridge
