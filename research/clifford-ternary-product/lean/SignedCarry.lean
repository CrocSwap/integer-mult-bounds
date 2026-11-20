import Mathlib.Data.Int.Basic
import Mathlib.Tactic.Ring

namespace SignedCarry

def digit : Bool → ℕ | false => 0 | true => 1

def numeral : List Bool → ℕ
  | [] => 0
  | b :: rest => digit b + 2 * numeral rest

def ones : List Bool → ℕ
  | [] => 0
  | b :: rest => digit b + ones rest

/-- Extend the tape by zero cells when the requested position is beyond its end. -/
def deposit : ℕ → List Bool → List Bool
  | 0, [] => [true]
  | 0, false :: rest => true :: rest
  | 0, true :: rest => false :: deposit 0 rest
  | k+1, [] => false :: deposit k []
  | k+1, b :: rest => b :: deposit k rest
termination_by k xs => (k, xs.length)

def carries : ℕ → List Bool → ℕ
  | 0, true :: rest => 1 + carries 0 rest
  | 0, _ => 0
  | k+1, [] => carries k []
  | k+1, _ :: rest => carries k rest
termination_by k xs => (k, xs.length)

theorem deposit_value (k : ℕ) (xs : List Bool) :
    numeral (deposit k xs) = numeral xs + 2^k := by
  induction k, xs using deposit.induct with
  | case1 => simp [deposit, numeral, digit]
  | case2 rest => simp [deposit, numeral, digit, Nat.add_comm]
  | case3 rest ih => simp [deposit, numeral, digit, ih]; omega
  | case4 k ih => simp [deposit, numeral, digit, ih, pow_succ, Nat.mul_comm]
  | case5 k b rest ih => simp [deposit, numeral, ih, pow_succ]; ring

theorem deposit_weight (k : ℕ) (xs : List Bool) :
    ones (deposit k xs) + carries k xs = ones xs + 1 := by
  induction k, xs using deposit.induct with
  | case1 => simp [deposit, carries, ones, digit]
  | case2 rest => simp [deposit, carries, ones, digit, Nat.add_comm]
  | case3 rest ih => simp [deposit, carries, ones, digit] at *; omega
  | case4 k ih => simpa [deposit, carries, ones, digit] using ih
  | case5 k b rest ih => simp [deposit, carries, ones]; omega

structure Tracks where
  positive : List Bool
  negative : List Bool

def Tracks.weight (s : Tracks) : ℕ := ones s.positive + ones s.negative
def Tracks.value (s : Tracks) : ℤ := (numeral s.positive : ℤ) - (numeral s.negative : ℤ)

structure Event where
  plus : Bool
  address : ℕ

def Event.update (e : Event) (s : Tracks) : Tracks :=
  if e.plus then {s with positive := deposit e.address s.positive}
  else {s with negative := deposit e.address s.negative}

def Event.cost (e : Event) (s : Tracks) : ℕ :=
  carries e.address (if e.plus then s.positive else s.negative)

def Event.value (e : Event) : ℤ := if e.plus then (2:ℤ)^e.address else -(2:ℤ)^e.address

theorem event_weight (e : Event) (s : Tracks) :
    (e.update s).weight + e.cost s = s.weight + 1 := by
  rcases e with ⟨b,k⟩
  have hp := deposit_weight k s.positive
  have hn := deposit_weight k s.negative
  cases b <;> simp [Event.update, Event.cost, Tracks.weight] <;> omega

theorem event_value (e : Event) (s : Tracks) :
    (e.update s).value = s.value + e.value := by
  rcases e with ⟨b,k⟩
  cases b <;> simp [Event.update, Tracks.value, Event.value, deposit_value] <;> ring

def finish : List Event → Tracks → Tracks
  | [], s => s
  | e :: rest, s => finish rest (e.update s)

def totalCarry : List Event → Tracks → ℕ
  | [], _ => 0
  | e :: rest, s => e.cost s + totalCarry rest (e.update s)

theorem conservation (es : List Event) (s : Tracks) :
    (finish es s).weight + totalCarry es s = s.weight + es.length := by
  induction es generalizing s with
  | nil => simp [finish, totalCarry]
  | cons e rest ih =>
    simp only [finish, totalCarry, List.length_cons]
    have h := ih (e.update s)
    have j := event_weight e s
    omega

theorem linear_ripple (es : List Event) :
    totalCarry es ⟨[],[]⟩ ≤ es.length := by
  have h := conservation es ⟨[],[]⟩
  simp [Tracks.weight, ones] at h
  omega

theorem signed_numeral (es : List Event) (s : Tracks) :
    (finish es s).value = s.value + (es.map Event.value).sum := by
  induction es generalizing s with
  | nil => simp [finish]
  | cons e rest ih => simp [finish, ih, event_value, add_assoc]

#print axioms linear_ripple
#print axioms signed_numeral

end SignedCarry
