import Mathlib.Tactic
import Mathlib.Analysis.Convex.SpecificFunctions.Pow

/-!
Discrete concavity and capped-mass comparison of finite child profiles.
The expansion is proved here, not assumed. Actual finite profile cap checks
and strict concavity of any chosen analytic function are separate premises.
-/

namespace CappedMass
open scoped BigOperators

def slope (f : ℕ → ℝ) (k : ℕ) : ℝ := f (k + 1) - f k
def curvature (f : ℕ → ℝ) (k : ℕ) : ℝ := slope f k - slope f (k + 1)
def expansion (f : ℕ → ℝ) (T t : ℕ) : ℝ :=
  slope f T * t + ∑ k ∈ Finset.range T, curvature f k * (min t (k + 1) : ℕ)

theorem expansion_step_low (f : ℕ → ℝ) (T t : ℕ) (ht : t ≤ T + 1) :
    expansion f (T + 1) t = expansion f T t := by
  unfold expansion
  rw [Finset.sum_range_succ, Nat.min_eq_left ht]
  unfold curvature
  ring

theorem expansion_step_top (f : ℕ → ℝ) (T : ℕ) :
    expansion f T (T + 1) = expansion f T T + slope f T := by
  have hsum : (∑ k ∈ Finset.range T, curvature f k * (min (T + 1) (k + 1) : ℕ)) =
      ∑ k ∈ Finset.range T, curvature f k * (min T (k + 1) : ℕ) := by
    apply Finset.sum_congr rfl
    intro k hk
    have hkT : k < T := Finset.mem_range.mp hk
    rw [Nat.min_eq_right (by omega), Nat.min_eq_right (by omega)]
  unfold expansion
  rw [hsum]
  push_cast
  ring

/-- Every function vanishing at zero has the finite slope/curvature/min
expansion at each index up to T+1. Concavity is not needed for this identity. -/
theorem discrete_expansion (f : ℕ → ℝ) (hzero : f 0 = 0) :
    ∀ T t : ℕ, t ≤ T + 1 → f t = expansion f T t := by
  intro T
  induction T with
  | zero =>
    intro t ht
    have ht' : t = 0 ∨ t = 1 := by omega
    rcases ht' with rfl | rfl <;> simp [expansion, slope, hzero]
  | succ T ih =>
    intro t ht
    by_cases hlow : t ≤ T + 1
    · rw [expansion_step_low f T t hlow]
      exact ih t hlow
    · have heq : t = (T + 1) + 1 := by omega
      subst t
      rw [expansion_step_top, expansion_step_low f T (T + 1) (by omega)]
      rw [← ih (T + 1) (by omega)]
      unfold slope
      ring

def mass (T : ℕ) (d : ℕ → ℝ) : ℝ :=
  ∑ t ∈ Finset.range (T + 2), d t * t
def cap (T : ℕ) (d : ℕ → ℝ) (k : ℕ) : ℝ :=
  ∑ t ∈ Finset.range (T + 2), d t * (min t (k + 1) : ℕ)

/-- Exact summation-by-parts form of the discrete capped-mass expansion. -/
theorem profile_identity (f d : ℕ → ℝ) (T : ℕ) (hzero : f 0 = 0) :
    (∑ t ∈ Finset.range (T + 2), d t * f t) =
      slope f T * mass T d + ∑ k ∈ Finset.range T, curvature f k * cap T d k := by
  have hexp : (∑ t ∈ Finset.range (T + 2), d t * f t) =
      ∑ t ∈ Finset.range (T + 2), d t * expansion f T t := by
    apply Finset.sum_congr rfl
    intro t ht
    rw [discrete_expansion f hzero T t (by have := Finset.mem_range.mp ht; omega)]
  rw [hexp]
  unfold expansion mass cap
  simp_rw [mul_add, Finset.mul_sum]
  rw [Finset.sum_add_distrib]
  congr 1
  · apply Finset.sum_congr rfl
    intro t ht
    ring
  · rw [Finset.sum_comm]
    apply Finset.sum_congr rfl
    intro k hk
    apply Finset.sum_congr rfl
    intro t ht
    ring

/-- If the new-minus-old profile has zero rank mass and nonpositive capped
mass, every discretely concave function vanishing at zero has nonpositive
weighted difference. Signed profile differences are allowed. -/
theorem profile_le (f d : ℕ → ℝ) (T : ℕ) (hzero : f 0 = 0)
    (hmass : mass T d = 0)
    (hcap : ∀ k ∈ Finset.range T, cap T d k ≤ 0)
    (hconcave : ∀ k ∈ Finset.range T, 0 ≤ curvature f k) :
    (∑ t ∈ Finset.range (T + 2), d t * f t) ≤ 0 := by
  rw [profile_identity f d T hzero, hmass, mul_zero, zero_add]
  apply Finset.sum_nonpos
  intro k hk
  exact mul_nonpos_of_nonneg_of_nonpos (hconcave k hk) (hcap k hk)

/-- One strictly negative cap paired with strictly positive curvature gives
strict improvement of the whole weighted characteristic. -/
theorem profile_lt (f d : ℕ → ℝ) (T : ℕ) (hzero : f 0 = 0)
    (hmass : mass T d = 0)
    (hcap : ∀ k ∈ Finset.range T, cap T d k ≤ 0)
    (hconcave : ∀ k ∈ Finset.range T, 0 ≤ curvature f k)
    (hstrict : ∃ k ∈ Finset.range T, 0 < curvature f k ∧ cap T d k < 0) :
    (∑ t ∈ Finset.range (T + 2), d t * f t) < 0 := by
  rw [profile_identity f d T hzero, hmass, mul_zero, zero_add]
  have hlt : (∑ k ∈ Finset.range T, curvature f k * cap T d k) <
      ∑ _k ∈ Finset.range T, (0 : ℝ) := by
    apply Finset.sum_lt_sum
    · intro k hk
      exact mul_nonpos_of_nonneg_of_nonpos (hconcave k hk) (hcap k hk)
    · rcases hstrict with ⟨k, hk, hc, hd⟩
      exact ⟨k, hk, mul_neg_of_pos_of_neg hc hd⟩
  simpa using hlt

/-- The actual analytic power n^p has strictly positive discrete curvature
at every index, including zero, whenever 0<p<1. -/
theorem power_curvature_pos (p : ℝ) (hp : 0 < p) (hp1 : p < 1) (k : ℕ) :
    0 < curvature (fun n : ℕ => (n : ℝ) ^ p) k := by
  have hconc := (Real.strictConcaveOn_rpow hp hp1).2
  have h := hconc
    (x := (k : ℝ)) (y := (k : ℝ) + 2)
    (a := (1 / 2 : ℝ)) (b := (1 / 2 : ℝ))
    (by change (0 : ℝ) ≤ k; positivity)
    (by change (0 : ℝ) ≤ (k : ℝ) + 2; positivity)
    (by linarith) (by norm_num) (by norm_num) (by norm_num)
  have hmid : (1 / 2 : ℝ) * (k : ℝ) + (1 / 2 : ℝ) * ((k : ℝ) + 2) = (k : ℝ) + 1 := by ring
  simp only [smul_eq_mul] at h
  rw [hmid] at h
  unfold curvature slope
  push_cast
  have htwo : (k : ℝ) + 1 + 1 = (k : ℝ) + 2 := by ring
  rw [htwo]
  nlinarith

/-- Capped-mass dominance strictly improves the real power characteristic for
every exponent 0<p<1, without any numerical exponential evaluation. -/
theorem power_profile_lt (d : ℕ → ℝ) (T : ℕ) (p : ℝ)
    (hp : 0 < p) (hp1 : p < 1) (hmass : mass T d = 0)
    (hcap : ∀ k ∈ Finset.range T, cap T d k ≤ 0)
    (hstrict : ∃ k ∈ Finset.range T, cap T d k < 0) :
    (∑ t ∈ Finset.range (T + 2), d t * (t : ℝ) ^ p) < 0 := by
  apply profile_lt (fun n : ℕ => (n : ℝ) ^ p) d T
  · simp [Real.zero_rpow hp.ne']
  · exact hmass
  · exact hcap
  · intro k hk; exact (power_curvature_pos p hp hp1 k).le
  · rcases hstrict with ⟨k, hk, hd⟩
    exact ⟨k, hk, power_curvature_pos p hp hp1 k, hd⟩

/-- Literal new-minus-old local width multiplicities from the independently
reconstructed h=23 ranked pair profile; their construction provenance and
serialized-word SHA256 hashes are in outputs/concave-dominance.json. -/
def delta23Z : ℕ → ℤ
  | 1 => 79 | 2 => -95 | 3 => -22 | 4 => -140 | 5 => -91 | 6 => -3
  | 7 => -11 | 8 => -19 | 9 => 23 | 10 => 22 | 11 => 22 | 12 => 21
  | 13 => 14 | 14 => 24 | _ => 0

/-- Literal new-minus-old local width multiplicities for h=25. -/
def delta25Z : ℕ → ℤ
  | 1 => -75 | 2 => 39 | 3 => -135 | 4 => -119 | 5 => -106 | 6 => -58
  | 7 => -87 | 8 => -1 | 9 => 15 | 10 => -17 | 11 => 22 | 12 => 47
  | 13 => 19 | 14 => 8 | 15 => 49 | 17 => 10 | 18 => -5 | 19 => 12
  | 20 => 10 | _ => 0

def delta23 (t : ℕ) : ℝ := delta23Z t
def delta25 (t : ℕ) : ℝ := delta25Z t

set_option maxRecDepth 10000 in
theorem delta23_integer_certificate :
    (∑ t ∈ Finset.range 15, delta23Z t * (t : ℤ)) = 0 ∧
    (∀ k : Fin 13, (∑ t ∈ Finset.range 15, delta23Z t * (min t (k.val + 1) : ℕ)) ≤ 0) ∧
    (∑ t ∈ Finset.range 15, delta23Z t * (min t 1 : ℕ)) < 0 := by decide

set_option maxRecDepth 10000 in
theorem delta25_integer_certificate :
    (∑ t ∈ Finset.range 21, delta25Z t * (t : ℤ)) = 0 ∧
    (∀ k : Fin 19, (∑ t ∈ Finset.range 21, delta25Z t * (min t (k.val + 1) : ℕ)) ≤ 0) ∧
    (∑ t ∈ Finset.range 21, delta25Z t * (min t 1 : ℕ)) < 0 := by decide

theorem delta23_cap_certificate : mass 13 delta23 = 0 ∧
    (∀ k ∈ Finset.range 13, cap 13 delta23 k ≤ 0) ∧ cap 13 delta23 0 < 0 := by
  constructor
  · unfold mass delta23
    exact_mod_cast delta23_integer_certificate.1
  constructor
  · intro k hk
    have hc := delta23_integer_certificate.2.1 ⟨k, Finset.mem_range.mp hk⟩
    unfold cap delta23
    exact_mod_cast hc
  · unfold cap delta23
    exact_mod_cast delta23_integer_certificate.2.2

theorem delta25_cap_certificate : mass 19 delta25 = 0 ∧
    (∀ k ∈ Finset.range 19, cap 19 delta25 k ≤ 0) ∧ cap 19 delta25 0 < 0 := by
  constructor
  · unfold mass delta25
    exact_mod_cast delta25_integer_certificate.1
  constructor
  · intro k hk
    have hc := delta25_integer_certificate.2.1 ⟨k, Finset.mem_range.mp hk⟩
    unfold cap delta25
    exact_mod_cast hc
  · unfold cap delta25
    exact_mod_cast delta25_integer_certificate.2.2

/-- The concrete h=23 ranked profile strictly improves every power moment
0<p<1, not merely one target saving checked numerically. -/
theorem delta23_every_power (p : ℝ) (hp : 0 < p) (hp1 : p < 1) :
    (∑ t ∈ Finset.range 15, delta23 t * (t : ℝ) ^ p) < 0 := by
  apply power_profile_lt delta23 13 p hp hp1 delta23_cap_certificate.1
    delta23_cap_certificate.2.1
  exact ⟨0, by decide, delta23_cap_certificate.2.2⟩

/-- The concrete h=25 ranked profile strictly improves every power moment
0<p<1. No physical compiler or tape-cost conclusion is bundled into this. -/
theorem delta25_every_power (p : ℝ) (hp : 0 < p) (hp1 : p < 1) :
    (∑ t ∈ Finset.range 21, delta25 t * (t : ℝ) ^ p) < 0 := by
  apply power_profile_lt delta25 19 p hp hp1 delta25_cap_certificate.1
    delta25_cap_certificate.2.1
  exact ⟨0, by decide, delta25_cap_certificate.2.2⟩

/-- Positive replication and opposite-axis scaling preserve strict joint
improvement. The positive coefficients may include the corresponding h^p. -/
theorem weighted_axes_improve (p A B : ℝ) (hp : 0 < p) (hp1 : p < 1)
    (hA : 0 < A) (hB : 0 < B) :
    A * (∑ t ∈ Finset.range 15, delta23 t * (t : ℝ) ^ p) +
    B * (∑ t ∈ Finset.range 21, delta25 t * (t : ℝ) ^ p) < 0 := by
  exact add_neg (mul_neg_of_pos_of_neg hA (delta23_every_power p hp hp1))
    (mul_neg_of_pos_of_neg hB (delta25_every_power p hp hp1))

/-- The same strict comparison in the multiplication certificate's saving
coordinate a, where the recursive power is p=1-a. -/
theorem every_saving_improves (a A B : ℝ) (ha : 0 < a) (ha1 : a < 1)
    (hA : 0 < A) (hB : 0 < B) :
    A * (∑ t ∈ Finset.range 15, delta23 t * (t : ℝ) ^ (1 - a)) +
    B * (∑ t ∈ Finset.range 21, delta25 t * (t : ℝ) ^ (1 - a)) < 0 :=
  weighted_axes_improve (1 - a) A B (by linarith) (by linarith) hA hB

#print axioms expansion_step_low
#print axioms expansion_step_top
#print axioms discrete_expansion
#print axioms profile_identity
#print axioms profile_le
#print axioms profile_lt
#print axioms power_curvature_pos
#print axioms power_profile_lt
#print axioms delta23_integer_certificate
#print axioms delta25_integer_certificate
#print axioms delta23_cap_certificate
#print axioms delta25_cap_certificate
#print axioms delta23_every_power
#print axioms delta25_every_power
#print axioms weighted_axes_improve
#print axioms every_saving_improves

end CappedMass
