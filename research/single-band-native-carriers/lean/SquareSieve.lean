import Mathlib.Data.Nat.Choose.Sum
import Mathlib.Algebra.Order.Floor.Div
import Mathlib.Tactic

/-! Pointwise truncation of the coprime indicator in disjoint prime bands. -/

namespace SquareSieve

open Finset

/-- `hits` counts the primes of one band that divide the current integer. -/
structure Band where
  hits : ℕ
  halfOrder : ℕ

def Band.upper (b : Band) : ℤ :=
  ∑ i ∈ range (2 * b.halfOrder + 1), (-1 : ℤ) ^ i * (b.hits.choose i : ℤ)

def Band.good (b : Band) : ℤ := if b.hits = 0 then 1 else 0

def Band.omitted (b : Band) : ℤ := b.hits.choose (2 * b.halfOrder + 1)

theorem oneBand (b : Band) :
    0 ≤ b.good ∧ b.good ≤ b.upper ∧ b.upper - b.good ≤ b.omitted := by
  rcases b with ⟨m, k⟩
  cases m with
  | zero => simp [Band.good, Band.upper, Band.omitted, sum_range_succ']
  | succ m =>
    simp only [Band.good, Band.upper, Band.omitted, Nat.succ_ne_zero, ite_false,
      Int.alternating_sum_range_choose_eq_choose, Nat.choose_succ_succ', Nat.cast_add]
    simp [pow_mul]

def allUpper : List Band → ℤ
  | [] => 1
  | b :: bs => b.upper * allUpper bs

def allGood : List Band → ℤ
  | [] => 1
  | b :: bs => b.good * allGood bs

/-- Each summand uses the first omitted degree in one band and the upper sum in all other bands. -/
def correction : List Band → ℤ
  | [] => 0
  | b :: bs => b.omitted * allUpper bs + b.upper * correction bs

theorem joint (bs : List Band) :
    0 ≤ allGood bs ∧ allGood bs ≤ allUpper bs ∧ allUpper bs - allGood bs ≤ correction bs := by
  induction bs with
  | nil => norm_num [allGood, allUpper, correction]
  | cons b bs ih =>
    rcases ih with ⟨good, leUpper, leCorr⟩
    rcases oneBand b with ⟨bg, bu, bo⟩
    have upper := le_trans good leUpper
    have bUpper := le_trans bg bu
    refine ⟨mul_nonneg bg good, mul_le_mul bu leUpper good bUpper, ?_⟩
    calc
      allUpper (b :: bs) - allGood (b :: bs) =
          (b.upper - b.good) * allUpper bs + b.good * (allUpper bs - allGood bs) := by
            simp only [allUpper, allGood]
            ring
      _ ≤ b.omitted * allUpper bs + b.upper * (allUpper bs - allGood bs) :=
        add_le_add (mul_le_mul_of_nonneg_right bo upper)
          (mul_le_mul_of_nonneg_right bu (sub_nonneg.mpr leUpper))
      _ ≤ correction (b :: bs) :=
        add_le_add le_rfl (mul_le_mul_of_nonneg_left leCorr bUpper)

theorem lowerIndicator (bs : List Band) : allUpper bs - correction bs ≤ allGood bs :=
  by linarith only [(joint bs).2.2]

#print axioms lowerIndicator

end SquareSieve

namespace SquareGeometry

theorem postjumpRise (k : ℕ) (h : 7 ≤ 2 ^ k) :
    2 ^ k + 1 - 7 * (k + 1) ≤ 2 ^ (k + 1) + 1 - 7 * (k + 2) := by
  rw [pow_succ]
  omega

#print axioms postjumpRise

def compactNativeDepth (s : ℕ) : ℕ :=
  8 + (s + 609999) / 610000 + (s + 259999) / 260000 + (s + 1599999) / 1600000

/-- A complete stack at every compact input, including all suspended native levels. -/
theorem compactStripe {s handleBits : ℕ} (hs : 2471429 ≤ s)
    (handles : 64 * handleBits ≤ s) :
    1024 + ((2 * compactNativeDepth s + 4) * 16384 + 65584 + 2 * handleBits) < s / 2 - 2 := by
  unfold compactNativeDepth
  omega

#print axioms compactStripe

def higherNativeDepth (s : ℕ) : ℕ :=
  20 + (s + 1599999) / 1600000 + (s + 24999999) / 25000000 +
    (s + 159999999) / 160000000 + (s + 999999999) / 1000000000 +
    (s + 5999999999) / 6000000000 + (s + 35999999999) / 36000000000 +
    (s + 223999999999) / 224000000000

private theorem upperCeil (s d : ℕ) : ((s + d - 1) / d) * d ≤ s + d :=
  le_trans (Nat.div_mul_le_self _ _) (by omega)

private theorem highMargins {s bits pos a b c d e f : ℕ} (hs : 267186701154 ≤ s)
    (head : 64 * bits ≤ s) (p : pos * 1600000 ≤ s+1600000)
    (ha : a * 25000000 ≤ s+25000000) (hb : b * 160000000 ≤ s+160000000)
    (hc : c * 1000000000 ≤ s+1000000000) (hd : d * 6000000000 ≤ s+6000000000)
    (he : e * 36000000000 ≤ s+36000000000) (hf : f * 224000000000 ≤ s+224000000000) :
    2 * (1027 + (2 * (20+pos+a+b+c+d+e+f) + 4) * 32768 + 65584 + 2 * bits) < s := by
  linarith only [hs, head, p, ha, hb, hc, hd, he, hf]

/-- The separate high-rate stack includes all six ordinary services. -/
theorem higherStripe {s handleBits : ℕ} (hs : 267186701154 ≤ s)
    (handles : 64 * handleBits ≤ s) :
    1024 + ((2 * higherNativeDepth s + 4) * 32768 + 65584 + 2 * handleBits) < s / 2 - 2 := by
  have h := highMargins hs handles (upperCeil s 1600000) (upperCeil s 25000000)
    (upperCeil s 160000000) (upperCeil s 1000000000) (upperCeil s 6000000000)
    (upperCeil s 36000000000) (upperCeil s 224000000000)
  have eq (x : ℕ) : s + (x+1) - 1 = s + x := by omega
  simp only [eq] at h
  change 2 * (1027 + (2 * higherNativeDepth s + 4) * 32768 + 65584 + 2 * handleBits) < s at h
  generalize higherNativeDepth s = k at h ⊢
  omega

#print axioms higherStripe

private theorem fewerLevels (s d e : ℕ) (hd : 0 < d) (de : d ≤ e) :
    (s + (e - 1)) / e ≤ (s + (d - 1)) / d := by
  have he : 0 < e := by omega
  rw [← Nat.add_sub_assoc he, ← Nat.add_sub_assoc hd,
    ← Nat.ceilDiv_eq_add_pred_div, ← Nat.ceilDiv_eq_add_pred_div]
  apply (ceilDiv_le_iff_le_mul he).2
  exact le_trans ((ceilDiv_le_iff_le_mul hd).1 le_rfl) (Nat.mul_le_mul_right _ de)

def priceMatchDepth (s : ℕ) : ℕ :=
  20 + (s + 1599999) / 1600000 + (s + 174999999) / 175000000 +
    (s + 1119999999) / 1120000000 + (s + 6999999999) / 7000000000 +
    (s + 41999999999) / 42000000000 + (s + 251999999999) / 252000000000 +
    (s + 1567999999999) / 1568000000000

/-- Higher ranks reduce the depth at every public width. -/
theorem priceMatchStripe {s bits : ℕ} (hs : 1870297303585 ≤ s) (handles : 64 * bits ≤ s) :
    1024 + ((2 * priceMatchDepth s + 4) * 32768 + 65584 + 2 * bits) < s / 2 - 2 := by
  apply lt_of_le_of_lt _ (higherStripe (s := s) (by omega) handles)
  have depth : priceMatchDepth s ≤ higherNativeDepth s := by
    unfold priceMatchDepth higherNativeDepth
    have h₁ := fewerLevels s 25000000 175000000 (by decide) (by decide)
    have h₂ := fewerLevels s 160000000 1120000000 (by decide) (by decide)
    have h₃ := fewerLevels s 1000000000 7000000000 (by decide) (by decide)
    have h₄ := fewerLevels s 6000000000 42000000000 (by decide) (by decide)
    have h₅ := fewerLevels s 36000000000 252000000000 (by decide) (by decide)
    have h₆ := fewerLevels s 224000000000 1568000000000 (by decide) (by decide)
    exact Nat.add_le_add (Nat.add_le_add (Nat.add_le_add (Nat.add_le_add
      (Nat.add_le_add (Nat.add_le_add (Nat.le_refl _) h₁) h₂) h₃) h₄) h₅) h₆
  omega

#print axioms priceMatchStripe

end SquareGeometry
