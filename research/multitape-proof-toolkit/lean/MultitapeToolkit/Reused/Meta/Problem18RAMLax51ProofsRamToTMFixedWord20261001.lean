import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsRamToTMPolynomialBounds20261001
import Mathlib.Data.Nat.Bitwise
import Mathlib.Data.Nat.ModEq

set_option backward.isDefEq.respectTransparency false


set_option autoImplicit false

namespace Lax51Proofs.RamToTM

/-- Decode a least-significant-bit-first Boolean word.  Unlike
`Computability.decodeNat`, trailing zeroes are significant syntactically but
do not change the represented value. -/
def bitsValue : List Bool → ℕ
  | [] => 0
  | b :: bs => Nat.bit b (bitsValue bs)

/-- The low `w` bits of `n`, padded to exactly `w` bits. -/
def fixedBits : ℕ → ℕ → List Bool
  | 0, _ => []
  | w + 1, n => n.bodd :: fixedBits w n.div2

@[simp] theorem fixedBits_length (w n : ℕ) : (fixedBits w n).length = w := by
  induction w generalizing n <;> simp [fixedBits, *]

@[simp] theorem bitsValue_replicate_false (w : ℕ) :
    bitsValue (List.replicate w false) = 0 := by
  induction w with
  | zero => rfl
  | succ w ih => simpa [List.replicate_succ, bitsValue] using ih

theorem bit_mod_two_pow (b : Bool) (n w : ℕ) :
    Nat.bit b (n % 2 ^ w) = Nat.bit b n % 2 ^ (w + 1) := by
  simp only [Nat.bit_val, pow_succ]
  let M := 2 ^ w
  have hM : 0 < M := by simp [M]
  have hn : n % M < M := Nat.mod_lt _ hM
  have hb : b.toNat ≤ 1 := by cases b <;> simp
  have hsmall : 2 * (n % M) + b.toNat < M * 2 := by omega
  rw [← Nat.mod_eq_of_lt hsmall]
  simpa [M, Nat.mul_comm, Nat.ModEq] using
    (Nat.ModEq.mul_left' 2 (Nat.mod_modEq n M)).add
      (Nat.ModEq.rfl : b.toNat ≡ b.toNat [MOD 2 * M])

@[simp] theorem bitsValue_fixedBits (w n : ℕ) :
    bitsValue (fixedBits w n) = n % 2 ^ w := by
  induction w generalizing n with
  | zero => simp [fixedBits, bitsValue, Nat.mod_one]
  | succ w ih =>
      simp only [fixedBits, bitsValue, ih]
      rw [bit_mod_two_pow, Nat.bit_bodd_div2]

theorem bitsValue_fixedBits_of_lt {w n : ℕ} (h : n < 2 ^ w) :
    bitsValue (fixedBits w n) = n := by
  simp [bitsValue_fixedBits, Nat.mod_eq_of_lt h]

theorem bitsValue_injective_of_length : ∀ {xs ys : List Bool},
    xs.length = ys.length → bitsValue xs = bitsValue ys → xs = ys
  | [], [], _, _ => rfl
  | [], _ :: _, hlen, _ => by simp at hlen
  | _ :: _, [], hlen, _ => by simp at hlen
  | x :: xs, y :: ys, hlen, hval => by
      have hxy : x = y := by
        have := congrArg Nat.bodd hval
        simpa [bitsValue, Nat.bodd_bit] using this
      have htail : bitsValue xs = bitsValue ys := by
        have := congrArg Nat.div2 hval
        simpa [bitsValue, Nat.div2_bit] using this
      subst y
      have hlen' : xs.length = ys.length := by simpa using hlen
      exact congrArg (x :: ·) (bitsValue_injective_of_length hlen' htail)

@[simp] theorem fixedBits_mod_word (w n : ℕ) :
    fixedBits w (n % 2 ^ w) = fixedBits w n := by
  apply bitsValue_injective_of_length
  · simp
  · simp [Nat.mod_eq_of_lt (Nat.mod_lt n (Nat.two_pow_pos w))]

/-- Bitwise Boolean mapping has the expected natural-number semantics on
fixed-width words. -/
def zipBits (f : Bool → Bool → Bool) : List Bool → List Bool → List Bool
  | a :: as, b :: bs => f a b :: zipBits f as bs
  | _, _ => []

@[simp] theorem zipBits_length_fixed (f : Bool → Bool → Bool) (w a b : ℕ) :
    (zipBits f (fixedBits w a) (fixedBits w b)).length = w := by
  induction w generalizing a b <;> simp [fixedBits, zipBits, *]

theorem fixedBits_land (w a b : ℕ) :
    fixedBits w (Nat.land a b) = zipBits (· && ·) (fixedBits w a) (fixedBits w b) := by
  induction w generalizing a b with
  | zero => rfl
  | succ w ih =>
      rw [← Nat.bit_bodd_div2 a, ← Nat.bit_bodd_div2 b]
      change fixedBits (w + 1)
          (Nat.bit a.bodd a.div2 &&& Nat.bit b.bodd b.div2) = _
      rw [Nat.land_bit]
      simp only [fixedBits, Nat.bodd_bit, Nat.div2_bit, zipBits]
      exact congrArg ((a.bodd && b.bodd) :: ·) (ih a.div2 b.div2)

theorem fixedBits_lor (w a b : ℕ) :
    fixedBits w (Nat.lor a b) = zipBits (· || ·) (fixedBits w a) (fixedBits w b) := by
  induction w generalizing a b with
  | zero => rfl
  | succ w ih =>
      rw [← Nat.bit_bodd_div2 a, ← Nat.bit_bodd_div2 b]
      change fixedBits (w + 1)
          (Nat.bit a.bodd a.div2 ||| Nat.bit b.bodd b.div2) = _
      rw [Nat.lor_bit]
      simp only [fixedBits, Nat.bodd_bit, Nat.div2_bit, zipBits]
      exact congrArg ((a.bodd || b.bodd) :: ·) (ih a.div2 b.div2)

theorem fixedBits_xor (w a b : ℕ) :
    fixedBits w (Nat.xor a b) = zipBits xor (fixedBits w a) (fixedBits w b) := by
  induction w generalizing a b with
  | zero => rfl
  | succ w ih =>
      rw [← Nat.bit_bodd_div2 a, ← Nat.bit_bodd_div2 b]
      change fixedBits (w + 1)
          (Nat.bit a.bodd a.div2 ^^^ Nat.bit b.bodd b.div2) = _
      rw [Nat.xor_bit]
      simp only [fixedBits, Nat.bodd_bit, Nat.div2_bit, zipBits]
      exact congrArg ((xor a.bodd b.bodd) :: ·) (ih a.div2 b.div2)

/-- Complementing a fixed-width bit list flips every bit within its width. -/
theorem bitsValue_complement_add (bs : List Bool) :
    bitsValue (bs.map Bool.not) + bitsValue bs + 1 = 2 ^ bs.length := by
  induction bs with
  | nil => simp [bitsValue]
  | cons b bs ih =>
      cases b <;> simp [bitsValue, Nat.bit_val, pow_succ] at * <;> omega

theorem zipBits_complement (as bs : List Bool) (h : as.length = bs.length) :
    zipBits (fun a _ => !a) as bs = as.map Bool.not := by
  induction as generalizing bs with
  | nil => simp [zipBits]
  | cons a as ih =>
      cases bs with
      | nil => simp at h
      | cons b bs => simp [zipBits, ih bs (by simpa using h)]

theorem fixedBits_complement (w a b : Nat) :
    fixedBits w (2 ^ w - 1 - a % 2 ^ w) =
      zipBits (fun a _ => !a) (fixedBits w a) (fixedBits w b) := by
  rw [zipBits_complement _ _ (by simp)]
  apply bitsValue_injective_of_length
  · simp
  · have h := bitsValue_complement_add (fixedBits w a)
    simp only [bitsValue_fixedBits, fixedBits_length] at h ⊢
    have hpos := Nat.two_pow_pos w
    have hlt : 2 ^ w - 1 - a % 2 ^ w < 2 ^ w := by omega
    rw [Nat.mod_eq_of_lt hlt]
    omega

/-- One-bit full adder, returning `(sum, carry)`. -/
def fullAdder (a b carry : Bool) : Bool × Bool :=
  (xor (xor a b) carry, (a && b) || (carry && xor a b))

theorem fullAdder_value (a b carry : Bool) :
    (fullAdder a b carry).1.toNat + 2 * (fullAdder a b carry).2.toNat =
      a.toNat + b.toNat + carry.toNat := by
  cases a <;> cases b <;> cases carry <;> decide

/-- Ripple-carry addition. It deliberately discards the final carry, so on
two `w`-bit inputs it computes addition modulo `2^w`. -/
def addBits : List Bool → List Bool → Bool → List Bool
  | a :: as, b :: bs, carry =>
      let q := fullAdder a b carry
      q.1 :: addBits as bs q.2
  | _, _, _ => []

theorem addBits_length_of_eq {as bs : List Bool} (carry : Bool)
    (h : as.length = bs.length) : (addBits as bs carry).length = as.length := by
  induction as generalizing bs carry with
  | nil => simp [addBits]
  | cons a as ih =>
      cases bs with
      | nil => simp at h
      | cons b bs =>
        simp at h
        simp [addBits, ih _ h]

@[simp] theorem addBits_length_fixed (w a b : ℕ) (carry : Bool) :
    (addBits (fixedBits w a) (fixedBits w b) carry).length = w := by
  induction w generalizing a b carry <;> simp [fixedBits, addBits, *]

theorem div2_add_carry (a b : ℕ) (carry : Bool) :
    (a + b + carry.toNat).div2 =
      a.div2 + b.div2 + (fullAdder a.bodd b.bodd carry).2.toNat := by
  have ha := Nat.bodd_add_div2 a
  have hb := Nat.bodd_add_div2 b
  have hf := fullAdder_value a.bodd b.bodd carry
  cases hca : a.bodd <;> cases hcb : b.bodd <;> cases carry <;>
    simp_all [Nat.div2_val, fullAdder] <;> omega

theorem bodd_add_carry (a b : ℕ) (carry : Bool) :
    (a + b + carry.toNat).bodd = (fullAdder a.bodd b.bodd carry).1 := by
  cases carry <;> simp [fullAdder, Nat.bodd_add, Bool.xor_assoc]

theorem fixedBits_add_carry (w a b : ℕ) (carry : Bool) :
    fixedBits w (a + b + carry.toNat) =
      addBits (fixedBits w a) (fixedBits w b) carry := by
  induction w generalizing a b carry with
  | zero => rfl
  | succ w ih =>
      simp only [fixedBits, addBits]
      rw [bodd_add_carry, div2_add_carry, ih]

theorem fixedBits_add (w a b : ℕ) :
    fixedBits w (a + b) = addBits (fixedBits w a) (fixedBits w b) false := by
  simpa using fixedBits_add_carry w a b false

theorem bitsValue_addBits_fixed (w a b : ℕ) :
    bitsValue (addBits (fixedBits w a) (fixedBits w b) false) =
      (a + b) % 2 ^ w := by
  rw [← fixedBits_add, bitsValue_fixedBits]

/-- One-bit full subtractor, returning `(difference, borrow)`. -/
def fullSubtractor (a b borrow : Bool) : Bool × Bool :=
  (xor (xor a b) borrow,
    ((!a) && (b || borrow)) || (b && borrow))

theorem fullSubtractor_value (a b borrow : Bool) :
    a.toNat + 2 * (fullSubtractor a b borrow).2.toNat =
      b.toNat + borrow.toNat + (fullSubtractor a b borrow).1.toNat := by
  cases a <;> cases b <;> cases borrow <;> decide

def subBits : List Bool → List Bool → Bool → List Bool
  | a :: as, b :: bs, borrow =>
      let q := fullSubtractor a b borrow
      q.1 :: subBits as bs q.2
  | _, _, _ => []

def subBorrowOut : List Bool → List Bool → Bool → Bool
  | a :: as, b :: bs, borrow =>
      subBorrowOut as bs (fullSubtractor a b borrow).2
  | _, _, borrow => borrow

theorem subBits_length_of_eq {as bs : List Bool} (borrow : Bool)
    (h : as.length = bs.length) : (subBits as bs borrow).length = as.length := by
  induction as generalizing bs borrow with
  | nil =>
      cases bs <;> simp [subBits] at h ⊢
  | cons a as ih =>
      cases bs with
      | nil => simp at h
      | cons b bs =>
          simp at h
          simp [subBits, ih _ h]

theorem subBits_value_identity {as bs : List Bool} (borrow : Bool)
    (h : as.length = bs.length) :
    bitsValue as + 2 ^ as.length * (subBorrowOut as bs borrow).toNat =
      bitsValue bs + borrow.toNat + bitsValue (subBits as bs borrow) := by
  induction as generalizing bs borrow with
  | nil =>
      cases bs with
      | nil => simp [bitsValue, subBits, subBorrowOut]
      | cons _ _ => simp at h
  | cons a as ih =>
      cases bs with
      | nil => simp at h
      | cons b bs =>
          simp at h
          have ht := ih (borrow := (fullSubtractor a b borrow).2)
            (bs := bs) h
          have hf := fullSubtractor_value a b borrow
          simp only [bitsValue, subBits, subBorrowOut, List.length_cons, pow_succ]
          simp only [bitsValue, Nat.bit_val] at ht ⊢
          nlinarith

@[simp] theorem subBits_length_fixed (w a b : ℕ) (borrow : Bool) :
    (subBits (fixedBits w a) (fixedBits w b) borrow).length = w := by
  induction w generalizing a b borrow <;> simp [fixedBits, subBits, *]

theorem sub_borrow_head_tail (a b : ℕ) (borrow : Bool)
    (h : b + borrow.toNat ≤ a) :
    let d := a - (b + borrow.toNat)
    d.bodd = (fullSubtractor a.bodd b.bodd borrow).1 ∧
      d.div2 = a.div2 -
        (b.div2 + (fullSubtractor a.bodd b.bodd borrow).2.toNat) ∧
      b.div2 + (fullSubtractor a.bodd b.bodd borrow).2.toNat ≤ a.div2 := by
  let d := a - (b + borrow.toNat)
  have hd : b + borrow.toNat + d = a := by
    dsimp [d]
    omega
  have ha := Nat.bodd_add_div2 a
  have hb := Nat.bodd_add_div2 b
  have hd' := Nat.bodd_add_div2 d
  have hf := fullSubtractor_value a.bodd b.bodd borrow
  have hhead : d.bodd = (fullSubtractor a.bodd b.bodd borrow).1 := by
    cases hba : a.bodd <;> cases hbb : b.bodd <;> cases hbd : d.bodd <;>
      cases borrow <;> simp_all [fullSubtractor] <;> omega
  have hquot :
      a.div2 = b.div2 +
        (fullSubtractor a.bodd b.bodd borrow).2.toNat + d.div2 := by
    cases hba : a.bodd <;> cases hbb : b.bodd <;> cases hbd : d.bodd <;>
      cases borrow <;> simp_all [fullSubtractor] <;> omega
  refine ⟨hhead, ?_, ?_⟩
  · rw [hquot, Nat.add_sub_cancel_left]
  · rw [hquot]
    omega

theorem fixedBits_sub_borrow (w a b : ℕ) (borrow : Bool)
    (h : b + borrow.toNat ≤ a) :
    fixedBits w (a - (b + borrow.toNat)) =
      subBits (fixedBits w a) (fixedBits w b) borrow := by
  induction w generalizing a b borrow with
  | zero => rfl
  | succ w ih =>
      obtain ⟨hhead, htail, hnext⟩ := sub_borrow_head_tail a b borrow h
      simp only [fixedBits, subBits]
      rw [hhead, htail]
      apply congrArg ((fullSubtractor a.bodd b.bodd borrow).1 :: ·)
      exact ih _ _ _ hnext

theorem fixedBits_sub_of_le (w : ℕ) {a b : ℕ} (h : b ≤ a) :
    fixedBits w (a - b) = subBits (fixedBits w a) (fixedBits w b) false := by
  simpa using fixedBits_sub_borrow w a b false (by simpa using h)

theorem bitsValue_subBits_fixed_of_le (w : ℕ) {a b : ℕ} (h : b ≤ a) :
    bitsValue (subBits (fixedBits w a) (fixedBits w b) false) =
      (a - b) % 2 ^ w := by
  rw [← fixedBits_sub_of_le w h, bitsValue_fixedBits]

theorem subBorrowOut_fixed_false (w : ℕ) {a b : ℕ} (borrow : Bool)
    (ha : a < 2 ^ w) (hb : b < 2 ^ w) (hba : b + borrow.toNat ≤ a) :
    subBorrowOut (fixedBits w a) (fixedBits w b) borrow = false := by
  induction w generalizing a b borrow with
  | zero =>
      simp at ha hb
      subst a
      subst b
      cases borrow <;> simp_all [subBorrowOut, fixedBits]
  | succ w ih =>
      obtain ⟨_, _, hnext⟩ := sub_borrow_head_tail a b borrow hba
      have ha' : a.div2 < 2 ^ w := by
        change a / 2 < 2 ^ w
        rw [pow_succ] at ha
        omega
      have hb' : b.div2 < 2 ^ w := by
        change b / 2 < 2 ^ w
        rw [pow_succ] at hb
        omega
      simp only [fixedBits, subBorrowOut]
      exact ih _ ha' hb' hnext

theorem subBorrowOut_fixed_false_of_le (w : ℕ) {a b : ℕ}
    (ha : a < 2 ^ w) (hb : b < 2 ^ w) (hba : b ≤ a) :
    subBorrowOut (fixedBits w a) (fixedBits w b) false = false := by
  exact subBorrowOut_fixed_false w false ha hb (by simpa using hba)

theorem subBorrowOut_fixed_eq_decide_lt (w a b : ℕ)
    (ha : a < 2 ^ w) (hb : b < 2 ^ w) :
    subBorrowOut (fixedBits w a) (fixedBits w b) false = decide (a < b) := by
  by_cases hlt : a < b
  · have hi := subBits_value_identity false
      (show (fixedBits w a).length = (fixedBits w b).length by simp)
    rw [bitsValue_fixedBits_of_lt ha, bitsValue_fixedBits_of_lt hb] at hi
    cases hout : subBorrowOut (fixedBits w a) (fixedBits w b) false
    · simp [hout] at hi
      omega
    · simp [hlt]
  · have hout := subBorrowOut_fixed_false_of_le w ha hb (Nat.le_of_not_gt hlt)
    simp [hlt, hout]

/-- Scan little-endian words while retaining the comparison at the most
significant position seen so far. -/
def lessBits : List Bool → List Bool → Bool → Bool
  | a :: as, b :: bs, previous =>
      lessBits as bs (if a = b then previous else (!a && b))
  | _, _, previous => previous

theorem lessBits_fixed_aux (w : ℕ) (a b : ℕ) (previous : Bool)
    (ha : a < 2 ^ w) (hb : b < 2 ^ w) :
    lessBits (fixedBits w a) (fixedBits w b) previous =
      if a = b then previous else decide (a < b) := by
  induction w generalizing a b previous with
  | zero =>
      simp at ha hb
      subst a
      subst b
      simp [lessBits, fixedBits]
  | succ w ih =>
      have ha' : a.div2 < 2 ^ w := by
        change a / 2 < 2 ^ w
        rw [pow_succ] at ha
        omega
      have hb' : b.div2 < 2 ^ w := by
        change b / 2 < 2 ^ w
        rw [pow_succ] at hb
        omega
      simp only [fixedBits, lessBits]
      rw [ih _ _ _ ha' hb']
      have hea := Nat.bodd_add_div2 a
      have heb := Nat.bodd_add_div2 b
      by_cases hq : a.div2 = b.div2
      · cases hba : a.bodd <;> cases hbb : b.bodd <;>
          by_cases hab : a = b <;> by_cases hlt : a < b <;>
            simp_all <;> omega
      · cases hba : a.bodd <;> cases hbb : b.bodd <;>
          by_cases hab : a = b <;> by_cases hlt : a < b <;>
            by_cases hqt : a.div2 < b.div2 <;> simp_all <;> omega

theorem lessBits_fixed (w : ℕ) (a b : ℕ)
    (ha : a < 2 ^ w) (hb : b < 2 ^ w) :
    lessBits (fixedBits w a) (fixedBits w b) false = decide (a < b) := by
  rw [lessBits_fixed_aux w a b false ha hb]
  split <;> simp_all

theorem bitsValue_lt_two_pow_length (xs : List Bool) :
    bitsValue xs < 2 ^ xs.length := by
  induction xs with
  | nil => simp [bitsValue]
  | cons b bs ih =>
      simp only [bitsValue, List.length_cons, pow_succ, Nat.bit_val]
      have hb : b.toNat ≤ 1 := by cases b <;> simp
      omega

theorem fixedBits_bitsValue (xs : List Bool) :
    fixedBits xs.length (bitsValue xs) = xs := by
  induction xs with
  | nil => rfl
  | cons b bs ih =>
      simp [fixedBits, bitsValue, ih]

theorem fixedBits_take (k w n : ℕ) :
    (fixedBits w n).take k = fixedBits (min k w) n := by
  induction k generalizing w n with
  | zero => simp [fixedBits]
  | succ k ih =>
      cases w with
      | zero => simp [fixedBits]
      | succ w => simp [fixedBits, ih, Nat.succ_min_succ]

/-- Fixed-width left shift by one bit. -/
def shiftLeftBits : List Bool → List Bool
  | [] => []
  | x :: xs => false :: (x :: xs).take xs.length

/-- Shift a fixed-width word left and install a new least-significant bit.
This is the arithmetic update used by one round of restoring division. -/
def shiftInBit (bit : Bool) : List Bool → List Bool
  | [] => []
  | x :: xs => bit :: (x :: xs).take xs.length

@[simp] theorem shiftInBit_length (bit : Bool) (bits : List Bool) :
    (shiftInBit bit bits).length = bits.length := by
  cases bits <;> simp [shiftInBit]

@[simp] theorem shiftLeftBits_length (xs : List Bool) :
    (shiftLeftBits xs).length = xs.length := by
  cases xs <;> simp [shiftLeftBits]

theorem shiftLeftBits_fixed (w n : ℕ) :
    shiftLeftBits (fixedBits w n) = fixedBits w (2 * n) := by
  cases w with
  | zero => rfl
  | succ w =>
      simp only [fixedBits]
      rw [shiftLeftBits]
      simp only [fixedBits_length]
      change false :: (n.bodd :: fixedBits w n.div2).take w =
        (2 * n).bodd :: fixedBits w (2 * n).div2
      rw [show n.bodd :: fixedBits w n.div2 = fixedBits (w + 1) n by rfl,
        fixedBits_take]
      simp [Nat.div2_val]

theorem shiftInBit_fixed (w r : ℕ) (bit : Bool) :
    shiftInBit bit (fixedBits (w + 1) r) =
      fixedBits (w + 1) (2 * r + bit.toNat) := by
  simp only [fixedBits, shiftInBit, fixedBits_length]
  rw [show r.bodd :: fixedBits w r.div2 = fixedBits (w + 1) r by rfl,
    fixedBits_take]
  cases bit <;> simp [Nat.div2_val]

@[simp] theorem fixedBits_zero (w : ℕ) :
    fixedBits w 0 = List.replicate w false := by
  induction w <;> simp [fixedBits, List.replicate_succ, *]

/-- Grade-school multiplication modulo the width of the first operand.
The recursive result is doubled and the multiplicand is conditionally added
for each little-endian multiplier bit. -/
def mulBits (multiplicand : List Bool) : List Bool → List Bool
  | [] => List.replicate multiplicand.length false
  | b :: bs =>
      let doubled := shiftLeftBits (mulBits multiplicand bs)
      if b then addBits multiplicand doubled false else doubled

@[simp] theorem mulBits_length (multiplicand multiplier : List Bool) :
    (mulBits multiplicand multiplier).length = multiplicand.length := by
  induction multiplier with
  | nil => simp [mulBits]
  | cons b bs ih =>
      cases b
      · simp [mulBits, ih]
      · simp only [mulBits, if_true]
        apply addBits_length_of_eq
        simpa [ih]

theorem mulBits_fixed (w k a b : ℕ) (hb : b < 2 ^ k) :
    mulBits (fixedBits w a) (fixedBits k b) = fixedBits w (a * b) := by
  induction k generalizing b with
  | zero =>
      simp at hb
      subst b
      simp [mulBits, fixedBits]
  | succ k ih =>
      have hb' : b.div2 < 2 ^ k := by
        change b / 2 < 2 ^ k
        rw [pow_succ] at hb
        omega
      simp only [fixedBits, mulBits]
      rw [ih b.div2 hb', shiftLeftBits_fixed]
      cases hbit : b.bodd with
      | false =>
          simp [hbit]
          have heq : b = 2 * b.div2 := by
            have := Nat.bodd_add_div2 b
            simp [hbit] at this
            omega
          rw [heq]
          congr 1
          simp [Nat.div2_val]
          ring
      | true =>
          simp [hbit, ← fixedBits_add]
          have heq : b = 2 * b.div2 + 1 := by
            have := Nat.bodd_add_div2 b
            simp [hbit] at this
            omega
          rw [heq]
          congr 1
          have hdiv : (2 * b.div2 + 1).div2 = b.div2 := by
            simp [Nat.div2_val]
          rw [hdiv]
          ring

theorem bitsValue_mulBits_fixed (w a b : ℕ) (hb : b < 2 ^ w) :
    bitsValue (mulBits (fixedBits w a) (fixedBits w b)) =
      (a * b) % 2 ^ w := by
  rw [mulBits_fixed w w a b hb, bitsValue_fixedBits]

/-- Interpret a bit list in most-significant-bit-first order, starting with
an existing prefix accumulator. -/
def msbValueFrom : ℕ → List Bool → ℕ
  | acc, [] => acc
  | acc, b :: bs => msbValueFrom (2 * acc + b.toNat) bs

def msbValue (bits : List Bool) : ℕ := msbValueFrom 0 bits

theorem msbValueFrom_append (acc : ℕ) (xs ys : List Bool) :
    msbValueFrom acc (xs ++ ys) = msbValueFrom (msbValueFrom acc xs) ys := by
  induction xs generalizing acc <;> simp [msbValueFrom, *]

@[simp] theorem msbValue_reverse (xs : List Bool) :
    msbValue xs.reverse = bitsValue xs := by
  induction xs with
  | nil => rfl
  | cons b bs ih =>
      change msbValueFrom 0 bs.reverse = bitsValue bs at ih
      simp [msbValue, msbValueFrom_append, msbValueFrom, bitsValue, ih,
        Nat.bit_val]

structure DivisionScan where
  quotient : List Bool
  remainder : ℕ

def divisionScanStep (divisor : ℕ) (s : DivisionScan) (bit : Bool) :
    DivisionScan :=
  let candidate := 2 * s.remainder + bit.toNat
  let quotientBit := decide (divisor ≤ candidate)
  { quotient := quotientBit :: s.quotient,
    remainder := if quotientBit then candidate - divisor else candidate }

def divisionScan (divisor : ℕ) : DivisionScan → List Bool → DivisionScan
  | s, [] => s
  | s, b :: bs => divisionScan divisor (divisionScanStep divisor s b) bs

theorem divisionScanStep_invariant {d : ℕ} (hd : 0 < d)
    (s : DivisionScan) (b : Bool) (hr : s.remainder < d) :
    let s' := divisionScanStep d s b
    bitsValue s'.quotient * d + s'.remainder =
      2 * (bitsValue s.quotient * d + s.remainder) + b.toNat ∧
    s'.remainder < d := by
  simp only [divisionScanStep]
  have hb : b.toNat ≤ 1 := by cases b <;> simp
  have hcand : 2 * s.remainder + b.toNat < 2 * d := by omega
  by_cases hle : d ≤ 2 * s.remainder + b.toNat
  · simp [hle, bitsValue, Nat.bit_val]
    constructor
    · have hsub := Nat.sub_add_cancel hle
      ring_nf at hsub ⊢
      omega
    · omega
  · simp [hle, bitsValue, Nat.bit_val]
    constructor
    · ring
    · omega

/-- The trial remainder of restoring division fits in one extra bit. -/
theorem divisionScan_candidate_lt_extra_bit {w d r : ℕ} (b : Bool)
    (hd : d < 2 ^ w) (hr : r < d) :
    2 * r + b.toNat < 2 ^ (w + 1) := by
  have hb : b.toNat ≤ 1 := by cases b <;> simp
  rw [pow_succ]
  omega

/-- Bit-level contract for one nonzero-divisor round.  Both the trial
remainder and the divisor use the extra remainder bit. -/
theorem divisionScanStep_fixed {w d : ℕ} (hd0 : 0 < d) (hd : d < 2 ^ w)
    (s : DivisionScan) (b : Bool) (hr : s.remainder < d) :
    let candidate := 2 * s.remainder + b.toNat
    let s' := divisionScanStep d s b
    fixedBits (w + 1) s'.remainder =
        if d ≤ candidate then
          subBits (fixedBits (w + 1) candidate) (fixedBits (w + 1) d) false
        else fixedBits (w + 1) candidate := by
  let candidate := 2 * s.remainder + b.toNat
  have hc : candidate < 2 ^ (w + 1) :=
    divisionScan_candidate_lt_extra_bit b hd hr
  have hdextra : d < 2 ^ (w + 1) := by
    rw [pow_succ]
    omega
  by_cases hle : d ≤ candidate
  · simp [divisionScanStep, candidate, hle]
    exact fixedBits_sub_of_le (w + 1) hle
  · simp [divisionScanStep, candidate, hle]

theorem divisionScan_invariant {d : ℕ} (hd : 0 < d)
    (bits : List Bool) (s : DivisionScan) (hr : s.remainder < d) :
    let s' := divisionScan d s bits
    bitsValue s'.quotient * d + s'.remainder =
      msbValueFrom (bitsValue s.quotient * d + s.remainder) bits ∧
    s'.remainder < d := by
  induction bits generalizing s with
  | nil => simp [divisionScan, msbValueFrom, hr]
  | cons b bits ih =>
      obtain ⟨hstep, hr'⟩ := divisionScanStep_invariant hd s b hr
      obtain ⟨htail, hr''⟩ := ih (divisionScanStep d s b) hr'
      simp only [divisionScan, msbValueFrom]
      rw [hstep] at htail
      exact ⟨htail, hr''⟩

theorem divisionScan_zero_correct {d : ℕ} (hd : 0 < d) (bits : List Bool) :
    let s := divisionScan d ⟨[], 0⟩ bits
    bitsValue s.quotient = msbValue bits / d ∧
      s.remainder = msbValue bits % d := by
  have hi :
      bitsValue (divisionScan d ⟨[], 0⟩ bits).quotient * d +
          (divisionScan d ⟨[], 0⟩ bits).remainder = msbValue bits ∧
        (divisionScan d ⟨[], 0⟩ bits).remainder < d := by
    simpa [msbValue, bitsValue] using
      (divisionScan_invariant hd bits (⟨[], 0⟩ : DivisionScan) hd)
  let s := divisionScan d ⟨[], 0⟩ bits
  have hdiv : msbValue bits / d = bitsValue s.quotient := by
    apply Nat.div_eq_of_lt_le
    · dsimp [s] at hi ⊢
      nlinarith [hi.1, hi.2]
    · dsimp [s] at hi ⊢
      nlinarith [hi.1, hi.2]
  have hmod : s.remainder = msbValue bits % d := by
    have hcanonical := Nat.div_add_mod (msbValue bits) d
    dsimp [s] at hi ⊢
    rw [hdiv] at hcanonical
    nlinarith [hi.1, hcanonical]
  exact ⟨hdiv.symm, hmod⟩

theorem divisionScan_fixed_correct (w n d : ℕ)
    (hn : n < 2 ^ w) (hd : 0 < d) :
    let s := divisionScan d ⟨[], 0⟩ (fixedBits w n).reverse
    bitsValue s.quotient = n / d ∧ s.remainder = n % d := by
  simpa [bitsValue_fixedBits_of_lt hn] using
    divisionScan_zero_correct hd (fixedBits w n).reverse

end Lax51Proofs.RamToTM
