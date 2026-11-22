import TierCost

namespace WeightedNumerical

/-- A grade share is distributed in proportion to each owner's positive frequency. -/
theorem rowLift {K : Type*} [Fintype K] (I : K → Type*) [∀ k, Fintype (I k)]
    (p : K → ℚ) (w : ∀ k, I k → ℚ) (row : (∑ k, p k) = 1)
    (mass : ∀ k, 0 < ∑ i, w k i) :
    (∑ k, ∑ i, p k * w k i / (∑ j, w k j)) = 1 := by
  calc
    _ = ∑ k, p k := by
      apply Finset.sum_congr rfl
      intro k _
      calc
        _ = ∑ i, (p k / (∑ j, w k j)) * w k i := by
          apply Finset.sum_congr rfl
          intro i _
          ring
        _ = (p k / (∑ j, w k j)) * (∑ i, w k i) := by rw [Finset.mul_sum]
        _ = p k := by field_simp [ne_of_gt (mass k)]
    _ = 1 := row

/-- The aggregate grade bound implies the service capacity of each physical owner. -/
theorem columnLift {R : Type*} [Fintype R] (source share : R → ℚ)
    (w n k : ℚ) (owner : 0 ≤ w) (mass : 0 < n)
    (available : (∑ j, source j * share j) ≤ n * k) :
    (∑ j, source j * (share j * w / n)) ≤ w * k := by
  calc
    _ = ∑ j, (w / n) * (source j * share j) := by
      apply Finset.sum_congr rfl
      intro j _
      ring
    _ = (w / n) * ∑ j, source j * share j := by rw [Finset.mul_sum]
    _ ≤ (w / n) * (n * k) := mul_le_mul_of_nonneg_left available (div_nonneg owner mass.le)
    _ = w * k := by field_simp [ne_of_gt mass]

def upper (M : ℕ) := 2*(M/(2048*306))
def band (M : ℕ) := 2*((3*upper M)/8)
def actualSize (M : ℕ) := 258*(band M-8)

/-- The external parent interval and the integral period satisfy the physical size bounds. -/
theorem placement (M : ℕ) (large : 10^13 ≤ M) :
    (32768 < band M) ∧ (112 * upper M < 258 * band M) ∧
    ((band M+2)*258 < 112*M) ∧ (1616 * actualSize M < M) ∧
    (M+6000 < 1620*actualSize M) := by
  simp only [upper, band, actualSize]
  omega

theorem tickets (M : ℕ) (large : 10^13 ≤ M) :
    3240 < 5 * ((1620*actualSize M - M)/4) ∧ 1620/5 = 324 ∧ 3240/5 = 648 := by
  have h := (placement M large).2.2.2.2
  omega

/-- The complete controller pays for all low-tier inputs at the high-tier rate. -/
theorem prefixInvoice (x : ℝ) (hx : 0 < x) (bound : x ≤ (2:ℝ)^(1146239:ℝ)) :
    x^(1-(345:ℝ)/100000) ≤ x^(1-(389821:ℝ)/100000000) * (2:ℝ)^(514:ℝ) := by
  apply (TierCost.finitePrefix x 1146239 (345/100000) (389821/100000000) hx bound (by norm_num)).trans
  apply mul_le_mul_of_nonneg_left _ (Real.rpow_nonneg hx.le _)
  exact Real.rpow_le_rpow_of_exponent_le (by norm_num) (by norm_num)

theorem strictIncrease :
    (389821:ℚ)/100000000 - 38982016137/10000000000000 = 83863/10000000000000 := by norm_num

/-- Adding ordinary stages cannot exceed the maximum funded local price. -/
theorem boundedStages (b price : ℕ → ℚ) (cap : ℚ) (start : b 0 ≤ cap)
    (localBound : ∀ i, price i ≤ cap)
    (funded : ∀ i, b (i+1) ≤ (249 * price i + b i) / 250) : ∀ i, b i ≤ cap := by
  intro i
  induction i with
  | zero => exact start
  | succ i ih => linarith [localBound i, funded i]

/-- Both thresholds use the same ordinary and numerical costs as the signed caller. -/
theorem priceFloors :
    ((4391986206293:ℚ)/2^50 - 11/(8*517429) <
       389821/100000000 + 5/(10^18)) ∧
    ((17145637167:ℚ)/2^42 - 65081/(2^19*483869) <
       389821/100000000 + 5/(10^18)) := by norm_num

#print axioms boundedStages
#print axioms priceFloors
#print axioms prefixInvoice
#print axioms strictIncrease
#print axioms rowLift
#print axioms columnLift
#print axioms placement
#print axioms tickets
end WeightedNumerical
