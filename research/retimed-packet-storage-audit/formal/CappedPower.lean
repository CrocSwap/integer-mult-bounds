import Lean

/-!
Correctness of the capped binary-power predicate resolved by Ali Romman's #8042.
See SOURCE-CORRESPONDENCE.md for the frozen Python sources and translation domain.
The theorem concerns the Boolean result; it does not formalize machine time.
Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
-/

namespace RetimedCappedPower

/-- Capping a positive factor at `h+1` preserves every threshold query. -/
theorem cap_threshold (h a b n : Nat) (ha : 1 ≤ a) :
    a * (min (h+1) b)^n ≤ h ↔ a*b^n ≤ h := by
  by_cases hb : b ≤ h+1
  · rw [Nat.min_eq_right hb]
  by_cases hn : n = 0
  · simp [hn]
  have hn' : 0 < n := by omega
  have hc : h+1 ≤ b := by omega
  have hm (x : Nat) : x ≤ a*x := by
    simpa only [Nat.one_mul] using Nat.mul_le_mul_right x ha
  have hl : h < a*(h+1)^n :=
    Nat.lt_of_lt_of_le (Nat.lt_succ_self h) (Nat.le_trans (Nat.le_pow hn') (hm _))
  have hr : h < a*b^n :=
    Nat.lt_of_lt_of_le (Nat.lt_succ_self h)
      (Nat.le_trans hc (Nat.le_trans (Nat.le_pow hn') (hm _)))
  rw [Nat.min_eq_left hc]
  exact iff_of_false (by omega) (by omega)

/-- The source's binary loop; the unneeded final square is denotational only. -/
def loop (h a b p : Nat) : Bool :=
  if hp : p = 0 then true
  else if p % 2 = 1 then
    if h < a*b then false
    else loop h (a*b) (min (h+1) (b*b)) (p/2)
  else loop h a (min (h+1) (b*b)) (p/2)
termination_by p

theorem exponent_even (b p : Nat) (hp : p % 2 = 0) :
    b^p = (b*b)^(p/2) := by
  have hx : p = 2*(p/2) := by omega
  conv => lhs; rw [hx, Nat.pow_mul]
  simp only [Nat.pow_two]

theorem exponent_odd (b p : Nat) (hp : p % 2 = 1) :
    b^p = b * (b*b)^(p/2) := by
  have hx : p = 2*(p/2)+1 := by omega
  conv => lhs; rw [hx, Nat.pow_add, Nat.pow_mul]
  simp only [Nat.pow_one, Nat.pow_two]
  exact Nat.mul_comm _ _

/-- Correctness of every reachable positive accumulator state. -/
theorem loop_correct (h a b p : Nat) (ha : 1 ≤ a) (hb : 1 ≤ b)
    (hah : a ≤ h) : loop h a b p = true ↔ a * b^p ≤ h := by
  induction p using Nat.strongRecOn generalizing a b with
  | ind p ih =>
    by_cases hp : p = 0
    · simp [loop, hp, hah]
    have hp0 : 0 < p := by omega
    have hdiv : p / 2 < p := Nat.div_lt_self hp0 (by omega)
    have hcap : 1 ≤ min (h+1) (b*b) := by
      apply Nat.le_min.mpr
      constructor
      · omega
      · exact Nat.mul_pos (by omega) (by omega)
    rw [loop]
    simp only [hp, ↓reduceDIte]
    by_cases hodd : p % 2 = 1
    · simp only [hodd, ↓reduceIte]
      rw [exponent_odd b p hodd, ← Nat.mul_assoc]
      by_cases hbig : h < a*b
      · simp only [hbig, ↓reduceIte, Bool.false_eq_true, false_iff]
        have hpow : 1 ≤ (b*b)^(p/2) :=
          Nat.one_le_pow _ _ (Nat.mul_pos (by omega) (by omega))
        have hprod := Nat.mul_le_mul_left (a*b) hpow
        simp only [Nat.mul_one] at hprod
        omega
      · simp only [hbig, ↓reduceIte]
        have hab : 1 ≤ a*b := by
          exact Nat.mul_pos (by omega) (by omega)
        rw [ih (p/2) hdiv (a*b) (min (h+1) (b*b)) hab hcap (by omega)]
        exact cap_threshold h (a*b) (b*b) (p/2) hab
    · simp only [hodd, ↓reduceIte]
      have heven : p % 2 = 0 := by omega
      rw [ih (p/2) hdiv a (min (h+1) (b*b)) ha hcap hah]
      rw [exponent_even b p heven]
      exact cap_threshold h a (b*b) (p/2) ha

/-- Python's nonzero low-bit test on natural exponents. -/
theorem low_bit_branch (p : Nat) : (p &&& 1 ≠ 0) ↔ p % 2 = 1 := by
  rw [Nat.and_one_is_mod]
  have := Nat.mod_two_eq_zero_or_one p
  omega

/-- The source chronology, including its low-bit guard and omitted final square. -/
def sourceLoop (h a b p : Nat) : Bool :=
  if hp : p = 0 then true
  else if p &&& 1 ≠ 0 then
    if h < a*b then false
    else if p/2 = 0 then true
    else sourceLoop h (a*b) (min (h+1) (b*b)) (p/2)
  else if p/2 = 0 then true
  else sourceLoop h a (min (h+1) (b*b)) (p/2)
termination_by p

/-- Omitting the square after the final bit does not affect the returned value. -/
theorem sourceLoop_eq_loop (h a b p : Nat) : sourceLoop h a b p = loop h a b p := by
  induction p using Nat.strongRecOn generalizing a b with
  | ind p ih =>
    by_cases hp : p = 0
    · simp [sourceLoop, loop, hp]
    have hdiv : p/2 < p := Nat.div_lt_self (by omega) (by omega)
    rw [sourceLoop, loop]
    simp only [hp, ↓reduceDIte, low_bit_branch]
    by_cases ho : p % 2 = 1
    · simp only [ho, ↓reduceIte]
      by_cases hg : h < a*b
      · simp [hg]
      · simp only [hg, ↓reduceIte]
        by_cases hq : p/2 = 0
        · simp [hq, loop]
        · simp only [hq, ↓reduceIte]
          exact ih (p/2) hdiv _ _
    · simp only [ho, ↓reduceIte]
      by_cases hq : p/2 = 0
      · simp [hq, loop]
      · simp only [hq, ↓reduceIte]
        exact ih (p/2) hdiv _ _

/-- The source's argument order is `(base, power, ceiling)`. -/
def power_le (base power ceiling : Nat) : Bool := sourceLoop ceiling 1 base power

theorem sourceLoop_correct (h a b p : Nat) (ha : 1 ≤ a) (hb : 1 ≤ b)
    (hah : a ≤ h) : sourceLoop h a b p = true ↔ a * b^p ≤ h := by
  rw [sourceLoop_eq_loop]
  exact loop_correct h a b p ha hb hah

theorem power_le_correct (base power ceiling : Nat) (hb : 1 ≤ base)
    (hh : 1 ≤ ceiling) : power_le base power ceiling = true ↔ base^power ≤ ceiling := by
  simpa [power_le] using sourceLoop_correct ceiling 1 base power (by decide) hb hh

theorem retimed_stop_correct (selected rootWidth : Nat)
    (he : 1 ≤ selected) (hh : 1 ≤ rootWidth) :
    power_le selected (10^21) rootWidth = true ↔ selected^(10^21) ≤ rootWidth := by
  exact power_le_correct selected (10^21) rootWidth he hh

/-- The actual caller first short-circuits at its carrier. -/
def callerStop (carrier selected rootWidth exponent : Nat) : Bool :=
  decide (selected ≤ carrier) || power_le selected exponent rootWidth

theorem callerStop_correct (carrier selected rootWidth exponent : Nat)
    (he : 1 ≤ selected) (hh : 1 ≤ rootWidth) :
    callerStop carrier selected rootWidth exponent = true ↔
      selected ≤ carrier ∨ selected^exponent ≤ rootWidth := by
  simp [callerStop, power_le_correct selected exponent rootWidth he hh]

/-- A failed source call supplies exactly the strict parent relation used downstream. -/
theorem callerContinue_correct (carrier selected rootWidth exponent : Nat)
    (he : 1 ≤ selected) (hh : 1 ≤ rootWidth) :
    callerStop carrier selected rootWidth exponent = false ↔
      carrier < selected ∧ rootWidth < selected^exponent := by
  rw [Bool.eq_false_iff]
  change (¬ callerStop carrier selected rootWidth exponent = true) ↔ _
  rw [callerStop_correct carrier selected rootWidth exponent he hh]
  simp [Nat.not_le]

/-- The zero-exponent return is meaningful only with a valid initial accumulator. -/
theorem exponent_zero (base ceiling : Nat) : power_le base 0 ceiling = true := by
  simp [power_le, sourceLoop]

theorem base_one (power ceiling : Nat) (hh : 1 ≤ ceiling) :
    power_le 1 power ceiling = true := by
  apply (power_le_correct 1 power ceiling (by decide) hh).mpr
  simpa using hh

/-- Semantic mutation used only as a negative control: cap at h, rather than h+1. -/
def badCapLoop (h a b p : Nat) : Bool :=
  if hp : p = 0 then true
  else if p % 2 = 1 then
    if h < a*b then false
    else badCapLoop h (a*b) (min h (b*b)) (p/2)
  else badCapLoop h a (min h (b*b)) (p/2)
termination_by p

theorem cap_mutation_rejected :
    badCapLoop 3 1 2 2 = true ∧ power_le 2 2 3 = false ∧ ¬ (2^2 ≤ 3) := by
  simp [badCapLoop, power_le, sourceLoop]

theorem equality_boundary_retained :
    power_le 2 3 8 = true ∧ ¬ (2^3 < 8) := by
  simp [power_le, sourceLoop]

theorem early_reject_retained : sourceLoop 3 2 2 3 = false := by
  simp [sourceLoop]

theorem accumulator_premise_needed :
    loop 0 1 2 0 = true ∧ ¬ (1 * 2^0 ≤ 0) := by
  simp [loop]

#print axioms cap_threshold
#print axioms loop_correct
#print axioms low_bit_branch
#print axioms sourceLoop_eq_loop
#print axioms sourceLoop_correct
#print axioms power_le_correct
#print axioms retimed_stop_correct
#print axioms callerStop_correct
#print axioms callerContinue_correct
#print axioms exponent_zero
#print axioms base_one
#print axioms cap_mutation_rejected
#print axioms equality_boundary_retained
#print axioms early_reject_retained
#print axioms accumulator_premise_needed
end RetimedCappedPower
