import QuadraticProduct
import SignedCarry
import Mathlib.Tactic.LinearCombination

/-! The positive and negative streams hold ordinary binary digits.
One signed event adds a single power of two at the current head.
The final low-first sweep subtracts, then drops the two scale bits. -/
namespace BinaryDelivery
open TernaryCollect QuadraticProduct

def binary : List Bool → ℕ
  | [] => 0
  | b::bs => value b + 2*binary bs

theorem numeral_eq (bs : List Bool) : binary bs = SignedCarry.numeral bs := by
  induction bs with
  | nil => rfl
  | cons b bs ih => cases b <;> simp [binary,value,SignedCarry.numeral,SignedCarry.digit,ih]

def borrow (a b c : Bool) : Bool := decide (value a < value b + value c)
def digit (a b c : Bool) : Bool := a ^^ b ^^ c

def subtract : Bool → List (Bool × Bool) → List Bool × Bool
  | c, [] => ([],c)
  | c,(a,b)::bs =>
    let tail := subtract (borrow a b c) bs
    (digit a b c :: tail.1,tail.2)

theorem column (a b c : Bool) :
    (value a:ℤ) - value b - value c = value (digit a b c) - 2*(value (borrow a b c):ℤ) := by
  cases a <;> cases b <;> cases c <;> decide

theorem subtract_value (bs : List (Bool×Bool)) (c : Bool) :
    (binary (bs.map Prod.fst):ℤ) - binary (bs.map Prod.snd) - value c =
      binary (subtract c bs).1 - (2:ℤ)^bs.length * value (subtract c bs).2 := by
  induction bs generalizing c with
  | nil => simp [subtract,binary]
  | cons ab bs ih =>
    obtain ⟨a,b⟩ := ab
    simp only [List.map_cons, binary, subtract, List.length_cons, Nat.cast_add, Nat.cast_mul,
      Nat.cast_ofNat, pow_succ]
    linear_combination 2 * ih (borrow a b c) + column a b c

theorem subtract_length (bs : List (Bool×Bool)) (c : Bool) : (subtract c bs).1.length = bs.length := by
  induction bs generalizing c with
  | nil => rfl
  | cons ab bs ih => simp [subtract,ih]

theorem binary_lt (bs : List Bool) : binary bs < 2^bs.length := by
  induction bs with
  | nil => decide
  | cons b bs ih => cases b <;> simp [binary,value,pow_succ] <;> omega

theorem low_shift (bs : List Bool) : binary (bs.drop 1) = binary bs / 2 := by
  cases bs with
  | nil => rfl
  | cons b bs =>
    cases b <;> simp [binary,value]
    omega

theorem exact_finish (bs : List (Bool×Bool)) (c : ℕ)
    (h : (binary (bs.map Prod.fst):ℤ) - binary (bs.map Prod.snd) = 4*(c:ℤ)) :
    (subtract false bs).2 = false ∧ binary ((subtract false bs).1.drop 2) = c := by
  have hv := subtract_value bs false
  rw [h, show value false = 0 by rfl] at hv
  have hle := binary_lt (subtract false bs).1
  rw [subtract_length] at hle
  have hle' : (binary (subtract false bs).1:ℤ) < (2:ℤ)^bs.length := by exact_mod_cast hle
  have hneg : (subtract false bs).2 = false := by
    cases he : (subtract false bs).2 with
    | false => rfl
    | true => rw [he] at hv; simp [value] at hv; omega
  refine ⟨hneg,?_⟩
  rw [hneg] at hv
  simp [value] at hv
  have ha : 4*c = binary (subtract false bs).1 := by exact_mod_cast hv
  have htwo (u : List Bool) : (u.drop 2) = (u.drop 1).drop 1 := by simp
  rw [htwo,low_shift,low_shift,←ha]
  omega

/-- This consumes the four emitted sign passes once their streamed events
are at their computed exponents. Both sides are literal binary words. -/
theorem decoded_product {m} (a b : Bits m → Bool) (A B : BooleanGauss.Model (Fin m))
    (ha : ∀ x, a x = mask A x) (hb : ∀ y, b y = mask B y) (bs : List (Bool×Bool))
    (h : (binary (bs.map Prod.fst):ℤ) - binary (bs.map Prod.snd) =
      ∑ t : TritWord m, (2:ℤ)^(exponent t)*numerator t A B) :
    (subtract false bs).2 = false ∧ binary ((subtract false bs).1.drop 2) = operand a * operand b := by
  apply exact_finish
  rw [h, funext ha, funext hb]
  have e := four_product (BooleanGauss.support A.rows) A.phase.eval (BooleanGauss.support B.rows) B.phase.eval
  simp only [numerator, gauss_eq_mass, energy_leaf]
  exact e.symm

#print axioms numeral_eq
#print axioms subtract_value
#print axioms exact_finish
#print axioms decoded_product
end BinaryDelivery
