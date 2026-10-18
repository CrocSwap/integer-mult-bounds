import Mathlib.Tactic

/-!
An arithmetic refinement of PR2250 `monomial.py`'s LSB-first emit loop.
The list model follows its bit/carry recurrence and four output branches.
It does not formalize Python, tape allocation, or the whole monomial executor.
The emit algorithm and modular-versus-signed boundary are due to Jose Manuel,
PR2250 `research/selected-complex-compact-adapters/PROOF.md` section 5,
frozen at `d404b48a1e7b147556b309497d55089c837dddb2`.
Prepared for AAAmirinu with substantial OpenAI Codex assistance. Apache-2.0.
-/

namespace SelectedPhaseWords

def bit (b : Bool) : ℤ := if b then 1 else 0

def unsigned : List Bool → ℤ
  | [] => 0
  | b :: bs => bit b + 2 * unsigned bs

/-- `(1-input)+carry`, split into the emitted bit and the next carry. -/
def carryStep : Bool → Bool → Bool × Bool
  | false, false => (true, false)
  | false, true => (false, true)
  | true, false => (false, false)
  | true, true => (true, false)

def carryLoop : List Bool → Bool → List Bool × Bool
  | [], c => ([], c)
  | b :: bs, c =>
      ((carryStep b c).1 :: (carryLoop bs (carryStep b c).2).1,
        (carryLoop bs (carryStep b c).2).2)

def negate (bs : List Bool) : List Bool := (carryLoop bs true).1

theorem carryStep_balance (b c : Bool) :
    bit (carryStep b c).1 + 2 * bit (carryStep b c).2 = 1 - bit b + bit c := by
  cases b <;> cases c <;> decide

theorem carryLoop_length (bs : List Bool) (c : Bool) :
    (carryLoop bs c).1.length = bs.length := by
  induction bs generalizing c with
  | nil => rfl
  | cons b bs ih => simp only [carryLoop, List.length_cons, ih]

theorem negate_length (bs : List Bool) : (negate bs).length = bs.length :=
  carryLoop_length bs true

/-- Exact carry accounting, including the discarded final carry. -/
theorem carryLoop_conservation (bs : List Bool) (c : Bool) :
    unsigned (carryLoop bs c).1 + unsigned bs +
      (2 : ℤ) ^ bs.length * bit (carryLoop bs c).2 + 1 =
      (2 : ℤ) ^ bs.length + bit c := by
  induction bs generalizing c with
  | nil => simp [carryLoop, unsigned, add_comm]
  | cons b bs ih =>
      have tail := ih (carryStep b c).2
      have head := carryStep_balance b c
      simp only [carryLoop, unsigned, List.length_cons, pow_succ]
      linear_combination 2 * tail + head

theorem unsigned_bounds (bs : List Bool) :
    0 ≤ unsigned bs ∧ unsigned bs < (2 : ℤ) ^ bs.length := by
  induction bs with
  | nil => simp [unsigned]
  | cons b bs ih =>
      cases b <;> simp only [unsigned, bit, Bool.false_eq_true, if_false, if_true,
        List.length_cons, pow_succ] <;> omega

theorem negate_conservation (bs : List Bool) :
    unsigned (negate bs) + unsigned bs +
      (2 : ℤ) ^ bs.length * bit (carryLoop bs true).2 = (2 : ℤ) ^ bs.length := by
  exact add_right_cancel (carryLoop_conservation bs true)

theorem negate_sum (bs : List Bool) :
    unsigned (negate bs) + unsigned bs = 0 ∨
      unsigned (negate bs) + unsigned bs = (2 : ℤ) ^ bs.length := by
  have h := negate_conservation bs
  cases hc : (carryLoop bs true).2 <;> simp [hc, bit] at h
  · exact Or.inr h
  · left; omega

/-- Every width, without a signed-headroom premise: modular negation is exact. -/
theorem negate_unsigned_mod (bs : List Bool) :
    unsigned (negate bs) = ((2 : ℤ) ^ bs.length - unsigned bs) % (2 : ℤ) ^ bs.length := by
  have hu := unsigned_bounds bs
  have hv := unsigned_bounds (negate bs)
  rw [negate_length] at hv
  rcases negate_sum bs with hzero | hsum
  · have ha : unsigned bs = 0 := by omega
    have hb : unsigned (negate bs) = 0 := by omega
    simp [ha, hb]
  · have heq : (2 : ℤ) ^ bs.length - unsigned bs = unsigned (negate bs) := by omega
    rw [heq]
    exact (Int.emod_eq_of_lt hv.1 hv.2).symm

def signedAt (half value : ℤ) : ℤ := if value < half then value else value - 2 * half

def signed (bs : List Bool) : ℤ := signedAt ((2 : ℤ) ^ (bs.length - 1)) (unsigned bs)

theorem signedAt_negation (half a b : ℤ) (hh : 0 < half)
    (ha : 0 ≤ a ∧ a < 2 * half) (hb : 0 ≤ b ∧ b < 2 * half)
    (hs : b + a = 0 ∨ b + a = 2 * half) (hmin : a ≠ half) :
    signedAt half b = -signedAt half a := by
  unfold signedAt
  rcases hs with hz | hs <;> split_ifs <;> omega

/-- All positive widths; only the most-negative bit pattern must be excluded. -/
theorem negate_signed (w : ℕ) (bs : List Bool) (hlen : bs.length = w + 1)
    (hmin : unsigned bs ≠ (2 : ℤ) ^ w) :
    signed (negate bs) = -signed bs := by
  have hu := unsigned_bounds bs
  have hv := unsigned_bounds (negate bs)
  have hs := negate_sum bs
  rw [negate_length] at hv
  rw [hlen, pow_succ] at hu hv hs
  have hh : (0 : ℤ) < 2 ^ w := pow_pos (by omega) _
  unfold signed
  rw [negate_length, hlen]
  simp only [Nat.add_sub_cancel]
  apply signedAt_negation _ _ _ hh
  · constructor <;> omega
  · constructor <;> omega
  · rcases hs with h | h
    · exact Or.inl h
    · right; omega
  · exact hmin

/-- The lower strict signed bound is enough; the upper bound comes from the word. -/
theorem negate_signed_headroom (w : ℕ) (bs : List Bool) (hlen : bs.length = w + 1)
    (hroom : -((2 : ℤ) ^ w) < signed bs) :
    signed (negate bs) = -signed bs := by
  apply negate_signed w bs hlen
  intro hm
  have hdecode : signed bs = -((2 : ℤ) ^ w) := by
    simp [signed, hlen, hm, signedAt]
    ring
  omega

inductive Phase where
  | one | imag | minusOne | minusImag
  deriving DecidableEq

def phaseOfNat (k : ℕ) : Phase :=
  match k % 4 with
  | 0 => .one
  | 1 => .imag
  | 2 => .minusOne
  | _ => .minusImag

def inversePhase : Phase → Phase
  | .one => .one
  | .imag => .minusImag
  | .minusOne => .minusOne
  | .minusImag => .imag

def rotateWords (p : Phase) (r i : List Bool) : List Bool × List Bool :=
  match p with
  | .one => (r, i)
  | .imag => (negate i, r)
  | .minusOne => (negate r, negate i)
  | .minusImag => (i, negate r)

def rotateIntegers (p : Phase) (r i : ℤ) : ℤ × ℤ :=
  match p with
  | .one => (r, i)
  | .imag => (-i, r)
  | .minusOne => (-r, -i)
  | .minusImag => (i, -r)

def decodePair (z : List Bool × List Bool) : ℤ × ℤ := (signed z.1, signed z.2)

def phaseHeadroom (p : Phase) (half r i : ℤ) : Prop :=
  match p with
  | .one => True
  | .imag => i ≠ half
  | .minusOne => r ≠ half ∧ i ≠ half
  | .minusImag => r ≠ half

/-- The exact sign-dependent guard: an untouched most-negative component is allowed. -/
theorem rotateWords_refines (w : ℕ) (p : Phase) (r i : List Bool)
    (hr : r.length = w + 1) (hi : i.length = w + 1)
    (h : phaseHeadroom p ((2 : ℤ) ^ w) (unsigned r) (unsigned i)) :
    decodePair (rotateWords p r i) = rotateIntegers p (signed r) (signed i) := by
  cases p with
  | one => rfl
  | imag =>
      simp only [phaseHeadroom] at h
      simp [decodePair, rotateWords, rotateIntegers, negate_signed w i hi h]
  | minusOne =>
      simp only [phaseHeadroom] at h
      simp [decodePair, rotateWords, rotateIntegers,
        negate_signed w r hr h.1, negate_signed w i hi h.2]
  | minusImag =>
      simp only [phaseHeadroom] at h
      simp [decodePair, rotateWords, rotateIntegers, negate_signed w r hr h]

def gaussianMul (a b : ℤ × ℤ) : ℤ × ℤ :=
  (a.1 * b.1 - a.2 * b.2, a.1 * b.2 + a.2 * b.1)

def phaseUnit : Phase → ℤ × ℤ
  | .one => (1, 0)
  | .imag => (0, 1)
  | .minusOne => (-1, 0)
  | .minusImag => (0, -1)

theorem rotateIntegers_is_gaussian_unit (p : Phase) (r i : ℤ) :
    rotateIntegers p r i = gaussianMul (phaseUnit p) (r, i) := by
  cases p <;> simp [rotateIntegers, gaussianMul, phaseUnit]

theorem phase_pass_coefficient (w : ℕ) (p : Phase) (r i : List Bool)
    (hr : r.length = w + 1) (hi : i.length = w + 1)
    (h : phaseHeadroom p ((2 : ℤ) ^ w) (unsigned r) (unsigned i)) :
    decodePair (rotateWords p r i) = gaussianMul (phaseUnit p) (signed r, signed i) := by
  rw [rotateWords_refines w p r i hr hi h, rotateIntegers_is_gaussian_unit]

def mostNegative (w : ℕ) : List Bool := List.replicate w false ++ [true]

theorem mostNegative_negate (w : ℕ) : negate (mostNegative w) = mostNegative w := by
  induction w with
  | zero => rfl
  | succ w ih =>
      simpa [mostNegative, List.replicate_succ, negate, carryLoop, carryStep] using
        congrArg (List.cons false) ih

theorem mostNegative_unsigned (w : ℕ) : unsigned (mostNegative w) = (2 : ℤ) ^ w := by
  induction w with
  | zero => decide
  | succ w ih =>
      simp only [mostNegative, List.replicate_succ, List.cons_append, unsigned, bit,
        Bool.false_eq_true, if_false, zero_add] at *
      rw [ih, pow_succ]
      ring

theorem mostNegative_signed (w : ℕ) : signed (mostNegative w) = -((2 : ℤ) ^ w) := by
  have hl : (mostNegative w).length = w + 1 := by simp [mostNegative]
  simp [signed, hl, mostNegative_unsigned, signedAt]
  ring

/-- Bytewise inversion may restore this word while signed negation is wrong. -/
theorem mostNegative_not_signed_negation (w : ℕ) :
    signed (negate (mostNegative w)) ≠ -signed (mostNegative w) := by
  rw [mostNegative_negate, mostNegative_signed]
  have hp : (0 : ℤ) < 2 ^ w := pow_pos (by omega) _
  omega

end SelectedPhaseWords
