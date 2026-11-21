import PowerInterpretation

namespace CarrierTrial

private theorem census_nonneg (xs : List Row) (w : Row→ℕ) : 0 ≤ actual xs w := by
  induction xs with
  | nil => simp [actual]
  | cons r rs ih =>
    simp only [actual,List.map_cons,List.sum_cons] at *
    exact add_nonneg (mul_nonneg (Nat.cast_nonneg _) (Real.rpow_nonneg (Nat.cast_nonneg _) _)) ih

/-- The complete debit of the 264-factor split and pruned word, including
both tails, is strictly below its productive price at the trial exponent. -/
theorem tensor_surplus :
    (actual main Row.paid / actual main Row.target)^264 +
    2*(actual split Row.paid / (realPower splitScale * actual main Row.target))^264 +
    (actual prune Row.target * realPower floorScale / actual main Row.target)^264 <
      1-1/(10^7:ℝ) := by
  obtain ⟨h0,h1,h2,ht,hs⟩ := actual_margins
  have p0 := pow_le_pow_left₀ (div_nonneg (census_nonneg _ _) ht.le) ((div_lt_iff₀ ht).mpr h0).le 264
  have h1' : actual split Row.paid < (947/1000:ℝ)*(realPower splitScale*actual main Row.target) := by
    simpa only [mul_assoc] using h1
  have p1 := pow_le_pow_left₀ (div_nonneg (census_nonneg _ _) (mul_pos hs ht).le)
    ((div_lt_iff₀ (mul_pos hs ht)).mpr h1').le 264
  have p2 := pow_le_pow_left₀ (div_nonneg (mul_nonneg (census_nonneg _ _)
    (Real.rpow_nonneg (Nat.cast_nonneg _) _)) ht.le) ((div_lt_iff₀ ht).mpr h2).le 264
  have rat : (1-88/(10^10:Rat))^264 + 2*(947/1000:Rat)^264 + (949/1000:Rat)^264 <
      1-1/(10^7:Rat) := by decide +kernel
  have exactPrice : (1-88/(10^10:ℝ))^264 + 2*(947/1000:ℝ)^264 + (949/1000:ℝ)^264 <
      1-1/(10^7:ℝ) := by
    have lift : (((1-88/(10^10:Rat))^264 + 2*(947/1000:Rat)^264 + (949/1000:Rat)^264 : Rat):ℝ) <
        ((1-1/(10^7:Rat):Rat):ℝ) := Rat.cast_lt.mpr rat
    push_cast at lift
    exact lift
  exact (add_le_add (add_le_add p0 (mul_le_mul_of_nonneg_left p1 (by norm_num))) p2).trans_lt exactPrice

#print axioms tensor_surplus
end CarrierTrial
