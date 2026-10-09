import Mathlib.Analysis.MeanInequalitiesPow
import Mathlib.Tactic

/-!
Rounded-width scalar recurrence transfer.

The physical recurrence is an explicit hypothesis. From finite contraction,
a finite rounding/overhead budget, and finitely many initial bounds, the main
theorem proves the bound for every positive integer width. No tape-machine,
compiler, movement-cost or logarithmic-overhead assumptions are hidden here.
-/

namespace RoundedRecurrence

open scoped BigOperators

/-- For 0 ≤ p ≤ 1, upward rounding loses at most one unit of p-power. -/
theorem ceil_power_bound (r : ℝ) (n : ℕ) (p : ℝ)
    (hr : 0 ≤ r) (hp : 0 ≤ p) (hp1 : p ≤ 1) :
    (⌈r * n⌉₊ : ℝ) ^ p ≤ r ^ p * (n : ℝ) ^ p + 1 := by
  have hx : 0 ≤ r * n := mul_nonneg hr (Nat.cast_nonneg n)
  calc
    (⌈r * n⌉₊ : ℝ) ^ p ≤ (r * n + 1) ^ p :=
      Real.rpow_le_rpow (Nat.cast_nonneg _) (Nat.ceil_lt_add_one hx).le hp
    _ ≤ (r * n) ^ p + (1 : ℝ) ^ p :=
      Real.rpow_add_le_add_rpow hx (by norm_num) hp hp1
    _ = r ^ p * (n : ℝ) ^ p + 1 := by rw [Real.mul_rpow hr (Nat.cast_nonneg n), Real.one_rpow]

/-- A finite threshold makes every rounded child positive and strictly smaller. -/
theorem rounded_child_lt (r : ℝ) (N n : ℕ) (hr : 0 < r) (_hr1 : r < 1)
    (hthreshold : r * N + 1 < N) (hn : N < n) :
    0 < ⌈r * n⌉₊ ∧ ⌈r * n⌉₊ < n := by
  have hn0 : 0 < n := Nat.zero_lt_of_lt hn
  have hnreal : (N : ℝ) < n := by exact_mod_cast hn
  have hnpos : (0 : ℝ) < n := by exact_mod_cast hn0
  constructor
  · exact Nat.ceil_pos.mpr (mul_pos hr hnpos)
  · have hx : 0 ≤ r * n := (mul_pos hr hnpos).le
    have hceil := Nat.ceil_lt_add_one hx
    have hdrop : r * n + 1 < n := by nlinarith
    have : (⌈r * n⌉₊ : ℝ) < n := lt_trans hceil hdrop
    exact_mod_cast this

/-- Two separate half-budget conditions suffice for the finite rounding and
overhead budget in the all-width theorem. Here P is the threshold's p-power. -/
theorem finite_budget_of_halves (A C γ M P : ℝ) (hA : 0 ≤ A) (hγ : γ < 1)
    (hP : 1 ≤ P) (hround : 2 * M ≤ (1 - γ) * P)
    (hoverhead : 2 * C ≤ A * (1 - γ)) :
    C + A * M ≤ A * (1 - γ) * P := by
  have hgap : 0 ≤ A * (1 - γ) := mul_nonneg hA (by linarith)
  have hlarge := mul_le_mul_of_nonneg_left hP hgap
  have hpaid := mul_le_mul_of_nonneg_left hround hA
  nlinarith

/-- An actual rounded recurrence has a uniform A*n^p bound.

`gamma = sum c_i*r_i^p < 1` is the characteristic condition. The finite budget
`C + A*sum c_i ≤ A*(1-gamma)*N^p` pays for all upward-rounding and fixed overhead.
The recurrence and base cases are named hypotheses, not invented axioms.
-/
theorem all_width_bound {ι : Type} (s : Finset ι) (c r : ι → ℝ)
    (f : ℕ → ℝ) (p A C γ : ℝ) (N : ℕ)
    (hp : 0 ≤ p) (hp1 : p ≤ 1) (hA : 0 ≤ A)
    (hc : ∀ i ∈ s, 0 ≤ c i)
    (hr : ∀ i ∈ s, 0 < r i) (hr1 : ∀ i ∈ s, r i < 1)
    (hγ : γ = ∑ i ∈ s, c i * (r i) ^ p) (hγ1 : γ < 1)
    (hthreshold : ∀ i ∈ s, r i * N + 1 < N)
    (hbudget : C + A * (∑ i ∈ s, c i) ≤ A * (1 - γ) * (N : ℝ) ^ p)
    (base : ∀ n, 0 < n → n ≤ N → f n ≤ A * (n : ℝ) ^ p)
    (recurrence : ∀ n, N < n → f n ≤ C + ∑ i ∈ s, c i * f ⌈r i * n⌉₊) :
    ∀ n, 0 < n → f n ≤ A * (n : ℝ) ^ p := by
  intro n
  induction n using Nat.strong_induction_on with
  | h n ih =>
    intro hn
    by_cases hsmall : n ≤ N
    · exact base n hn hsmall
    · have hlarge : N < n := Nat.lt_of_not_ge hsmall
      have hrec :
          (∑ i ∈ s, c i * f ⌈r i * n⌉₊) ≤
          ∑ i ∈ s, c i * (A * ((r i) ^ p * (n : ℝ) ^ p + 1)) := by
        apply Finset.sum_le_sum
        intro i hi
        have hchild := rounded_child_lt (r i) N n (hr i hi) (hr1 i hi) (hthreshold i hi) hlarge
        have hbound := ih _ hchild.2 hchild.1
        have hround := ceil_power_bound (r i) n p (hr i hi).le hp hp1
        exact mul_le_mul_of_nonneg_left
          (le_trans hbound (mul_le_mul_of_nonneg_left hround hA)) (hc i hi)
      have hsum : (∑ i ∈ s, c i * (A * ((r i) ^ p * (n : ℝ) ^ p + 1))) =
          A * γ * (n : ℝ) ^ p + A * (∑ i ∈ s, c i) := by
        rw [hγ]
        simp only [Finset.mul_sum, Finset.sum_mul, ← Finset.sum_add_distrib]
        apply Finset.sum_congr rfl
        intro i hi
        ring
      have hmono : (N : ℝ) ^ p ≤ (n : ℝ) ^ p :=
        Real.rpow_le_rpow (Nat.cast_nonneg N) (by exact_mod_cast hlarge.le) hp
      have hgap : 0 ≤ A * (1 - γ) := mul_nonneg hA (by linarith)
      have hbudgetn : C + A * (∑ i ∈ s, c i) ≤ A * (1 - γ) * (n : ℝ) ^ p :=
        le_trans hbudget (mul_le_mul_of_nonneg_left hmono hgap)
      calc
        f n ≤ C + ∑ i ∈ s, c i * f ⌈r i * n⌉₊ := recurrence n hlarge
        _ ≤ C + ∑ i ∈ s, c i * (A * ((r i) ^ p * (n : ℝ) ^ p + 1)) :=
          add_le_add_left hrec C
        _ = C + (A * γ * (n : ℝ) ^ p + A * (∑ i ∈ s, c i)) := by rw [hsum]
        _ ≤ A * (n : ℝ) ^ p := by nlinarith [hbudgetn]

/-- The real-exponential characteristic used by the exact finite certificates. -/
noncomputable def expCharacteristic {ι : Type} (s : Finset ι) (multiplicity width : ι → ℝ)
    (m W a : ℝ) : ℝ :=
  ∑ i ∈ s, (multiplicity i * width i / (m * W)) *
    Real.exp (a * Real.log (m / width i))

/-- One term of the rank-profile characteristic equals the corresponding
coefficient times the child ratio raised to the recurrence exponent. -/
theorem characteristic_term (multiplicity t m W a : ℝ)
    (ht : 0 < t) (hm : 0 < m) (hW : 0 < W) :
    (multiplicity / W) * (t / m) ^ (1 - a) =
      (multiplicity * t / (m * W)) * Real.exp (a * Real.log (m / t)) := by
  have hratio : 0 < t / m := div_pos ht hm
  have hlog : Real.log (t / m) = -Real.log (m / t) := by
    rw [Real.log_div ht.ne' hm.ne', Real.log_div hm.ne' ht.ne']
    ring
  have hpow : (t / m) ^ (1 - a) = (t / m) * Real.exp (a * Real.log (m / t)) := by
    rw [Real.rpow_def_of_pos hratio]
    have he : Real.log (t / m) * (1 - a) =
        Real.log (t / m) + a * Real.log (m / t) := by rw [hlog]; ring
    rw [he, Real.exp_add, Real.exp_log hratio]
  rw [hpow]
  field_simp
  ring

/-- Exact equality of the recurrence characteristic and the certified profile
expression. This is a real identity, not a floating-point approximation. -/
theorem characteristic_identity {ι : Type} (s : Finset ι)
    (multiplicity width : ι → ℝ) (m W a : ℝ)
    (hm : 0 < m) (hW : 0 < W) (ht : ∀ i ∈ s, 0 < width i) :
    (∑ i ∈ s, (multiplicity i / W) * (width i / m) ^ (1 - a)) =
      expCharacteristic s multiplicity width m W a := by
  unfold expCharacteristic
  apply Finset.sum_congr rfl
  intro i hi
  exact characteristic_term (multiplicity i) (width i) m W a (ht i hi) hm hW

/-- Finite rank profiles transfer to a bound for every positive width, provided
the named physical recurrence and the REAL characteristic inequality hold.
Finite rational enclosure files are not silently promoted to this real premise.
-/
theorem network_all_width_bound {ι : Type} (s : Finset ι)
    (multiplicity width : ι → ℝ) (m W a A C : ℝ) (N : ℕ) (f : ℕ → ℝ)
    (hm : 0 < m) (hW : 0 < W) (ha : 0 ≤ a) (ha1 : a ≤ 1) (hA : 0 ≤ A)
    (hc : ∀ i ∈ s, 0 ≤ multiplicity i)
    (ht : ∀ i ∈ s, 0 < width i) (htm : ∀ i ∈ s, width i < m)
    (real_characteristic : expCharacteristic s multiplicity width m W a < 1)
    (hthreshold : ∀ i ∈ s, (width i / m) * N + 1 < N)
    (hbudget : C + A * (∑ i ∈ s, multiplicity i / W) ≤
      A * (1 - expCharacteristic s multiplicity width m W a) * (N : ℝ) ^ (1 - a))
    (base : ∀ n, 0 < n → n ≤ N → f n ≤ A * (n : ℝ) ^ (1 - a))
    (physical_recurrence : ∀ n, N < n → f n ≤ C +
      ∑ i ∈ s, (multiplicity i / W) * f ⌈(width i / m) * n⌉₊) :
    ∀ n, 0 < n → f n ≤ A * (n : ℝ) ^ (1 - a) := by
  apply all_width_bound s (fun i => multiplicity i / W) (fun i => width i / m)
    f (1 - a) A C (expCharacteristic s multiplicity width m W a) N
    (by linarith) (by linarith) hA
  · intro i hi; exact div_nonneg (hc i hi) hW.le
  · intro i hi; exact div_pos (ht i hi) hm
  · intro i hi; exact (div_lt_one hm).mpr (htm i hi)
  · exact (characteristic_identity s multiplicity width m W a hm hW ht).symm
  · exact real_characteristic
  · exact hthreshold
  · exact hbudget
  · exact base
  · exact physical_recurrence

#print axioms ceil_power_bound
#print axioms rounded_child_lt
#print axioms finite_budget_of_halves
#print axioms all_width_bound
#print axioms characteristic_term
#print axioms characteristic_identity
#print axioms network_all_width_bound

end RoundedRecurrence
