import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsRamToTMSparseEncoding20261001

set_option backward.isDefEq.respectTransparency false


set_option autoImplicit false

namespace Lax51Proofs.RamToTM

/-! Semantic contracts shared by the arithmetic branches of the RAM
interpreter.  Each operation consumes and produces a little-endian word of
the same width; the later control machine only has to realize these list
transformations. -/

/-- Repeated fixed-width left shift. -/
def shiftLeftMany : ℕ → List Bool → List Bool
  | 0, bits => bits
  | k + 1, bits => shiftLeftMany k (shiftLeftBits bits)

@[simp] theorem shiftLeftMany_length (k : ℕ) (bits : List Bool) :
    (shiftLeftMany k bits).length = bits.length := by
  induction k generalizing bits with
  | zero => rfl
  | succ k ih => simp [shiftLeftMany, ih]

theorem shiftLeftMany_fixed (k w a : ℕ) :
    shiftLeftMany k (fixedBits w a) = fixedBits w (a * 2 ^ k) := by
  induction k generalizing a with
  | zero => simp [shiftLeftMany]
  | succ k ih =>
      simp only [shiftLeftMany, shiftLeftBits_fixed, ih]
      congr 1
      rw [pow_succ]
      ring

/-- Fixed-width right shift.  Dropped low bits are replaced by zeroes at the
most-significant end. -/
def shiftRightBits : List Bool → List Bool
  | [] => []
  | _ :: bits => bits ++ [false]

@[simp] theorem bitsValue_append_false (bits : List Bool) :
    bitsValue (bits ++ [false]) = bitsValue bits := by
  induction bits with
  | nil => rfl
  | cons b bits ih => simp [bitsValue, ih]

@[simp] theorem shiftRightBits_length_of_ne_nil {bits : List Bool}
    (h : bits ≠ []) : (shiftRightBits bits).length = bits.length := by
  cases bits with
  | nil => contradiction
  | cons b bs => simp [shiftRightBits]

theorem shiftRightBits_fixed (w a : ℕ) (ha : a < 2 ^ w) :
    shiftRightBits (fixedBits w a) = fixedBits w (a / 2) := by
  cases w with
  | zero => simp [shiftRightBits, fixedBits]
  | succ w =>
      have hdiv : a / 2 < 2 ^ w := by
        rw [pow_succ'] at ha
        omega
      change fixedBits w (a / 2) ++ [false] = fixedBits (w + 1) (a / 2)
      rw [← fixedBits_bitsValue (fixedBits w (a / 2) ++ [false])]
      rw [bitsValue_append_false, bitsValue_fixedBits_of_lt hdiv]
      simp

/-- Repeated fixed-width right shift. -/
def shiftRightMany : ℕ → List Bool → List Bool
  | 0, bits => bits
  | k + 1, bits => shiftRightMany k (shiftRightBits bits)

theorem shiftRightMany_fixed (k w a : ℕ) (ha : a < 2 ^ w) :
    shiftRightMany k (fixedBits w a) = fixedBits w (a / 2 ^ k) := by
  induction k generalizing a with
  | zero => simp [shiftRightMany]
  | succ k ih =>
      rw [shiftRightMany, shiftRightBits_fixed w a ha, ih]
      · rw [pow_succ, Nat.div_div_eq_div_mul, Nat.mul_comm]
      · exact Nat.lt_of_le_of_lt (Nat.div_le_self _ _) ha

/-- Division on words, including the RAM convention that division by zero
returns zero. -/
def divBits (w : ℕ) (dividend divisor : List Bool) : List Bool :=
  if bitsValue divisor = 0 then fixedBits w 0
  else (divisionScan (bitsValue divisor) ⟨[], 0⟩ dividend.reverse).quotient

theorem divisionScan_quotient_length (d : ℕ) (s : DivisionScan)
    (bits : List Bool) :
    (divisionScan d s bits).quotient.length = s.quotient.length + bits.length := by
  induction bits generalizing s with
  | nil => simp [divisionScan]
  | cons b bits ih =>
      simp only [divisionScan]
      rw [ih]
      simp [divisionScanStep]
      omega

theorem divBits_fixed (w a d : ℕ) (ha : a < 2 ^ w) (hd : d < 2 ^ w) :
    divBits w (fixedBits w a) (fixedBits w d) = fixedBits w (a / d) := by
  by_cases hzero : d = 0
  · subst d
    simp [divBits]
  · have hdpos : 0 < d := Nat.pos_of_ne_zero hzero
    let s := divisionScan d ⟨[], 0⟩ (fixedBits w a).reverse
    have hscan : bitsValue s.quotient = a / d :=
      (divisionScan_fixed_correct w a d ha hdpos).1
    have hlen : s.quotient.length = w := by
      dsimp [s]
      rw [divisionScan_quotient_length]
      simp
    unfold divBits
    rw [bitsValue_fixedBits_of_lt hd]
    simp only [hzero, if_false]
    change s.quotient = fixedBits w (a / d)
    rw [← hscan, ← hlen]
    exact (fixedBits_bitsValue s.quotient).symm

end Lax51Proofs.RamToTM
