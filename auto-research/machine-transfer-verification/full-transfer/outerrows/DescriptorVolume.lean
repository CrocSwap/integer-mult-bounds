import OuterRows

/-! Quantitative uniformity of descriptor overhead. Complete retained main
address ranges are an explicit physical layout contract. No algorithm for
descriptor manipulation or streaming field interchange is asserted here. -/
namespace DescriptorVolume

theorem retained_range_covers_stock (m t c e q W : ℕ) (ht : t < m)
    (hq : 1 ≤ q) (hbase : W ≤ q ^ (2 * c))
    (hhalf : 2 * OuterRows.rho m t ht c e ≤ e) :
    W ^ FloorDepth.depth m t ht e ≤ q ^ (2 * (e - OuterRows.rho m t ht c e)) := by
  have hstock := OuterRows.row_range_covers_stock m t c e q W ht hbase
  apply hstock.trans
  apply Nat.pow_le_pow_right hq
  omega

/-- Every descendant has a complete address range of size X. Row division
alone therefore reduces volume, and the root volume is at most its square. -/
theorem row_division_volume_square (W D j R X S : ℕ) (hW : 0 < W)
    (hj : j ≤ D) (hR : 0 < R) (hS : 0 < S)
    (stock : W ^ D ∣ R) (retained : W ^ D ≤ X) :
    0 < (R / W ^ j) * X * S ∧
      R * X * S = W ^ j * ((R / W ^ j) * X * S) ∧
      R * X * S ≤ ((R / W ^ j) * X * S) ^ 2 := by
  have hp : 0 < W ^ j := pow_pos hW _
  have hdvd : W ^ j ∣ R := dvd_trans (pow_dvd_pow W hj) stock
  have hrows : 0 < R / W ^ j := Nat.div_pos (Nat.le_of_dvd hR hdvd) hp
  have hx : 0 < X := lt_of_lt_of_le (pow_pos hW _) retained
  have hpos : 0 < (R / W ^ j) * X * S := Nat.mul_pos (Nat.mul_pos hrows hx) hS
  have hpow : W ^ j ≤ X :=
    (Nat.pow_le_pow_right hW hj).trans retained
  have hscale : X ≤ (R / W ^ j) * X * S := by
    have h1 : X ≤ (R / W ^ j) * X := by nlinarith
    nlinarith
  have heq : R * X * S = W ^ j * ((R / W ^ j) * X * S) := by
    rw [← Nat.mul_assoc, ← Nat.mul_assoc, Nat.mul_div_cancel' hdvd]
  refine ⟨hpos, heq, ?_⟩
  rw [heq, pow_two]
  exact Nat.mul_le_mul_right _ (hpow.trans hscale)

theorem log_root_le_twice_log_current (root current : ℝ)
    (hroot : 0 < root) (hsq : root ≤ current ^ 2) :
    Real.log (2 * root) ≤ 2 * Real.log (2 * current) := by
  have hpos : 0 < 2 * root := by positivity
  have hle : 2 * root ≤ (2 * current) ^ 2 := by nlinarith
  have h := Real.log_le_log hpos hle
  simpa only [Real.log_pow, Nat.cast_ofNat] using h

/-- Explicit absorption constant for any fixed positive polynomial degree.
This is a real-number bound; implementation of descriptor arithmetic remains
external and may use any fixed degree k. -/
theorem descriptor_power_bound (root current : ℝ) (k : ℕ)
    (hroot : 1 ≤ root) (hcurrent : 1 ≤ current) (hsq : root ≤ current ^ 2)
    (hk : 0 < k) :
    (Real.log (2 * root)) ^ k ≤ 2 * (2 * (k : ℝ)) ^ k * current := by
  have hkR : (0 : ℝ) < k := by exact_mod_cast hk
  have hlog := log_root_le_twice_log_current root current (by linarith) hsq
  have hlog0 : 0 ≤ Real.log (2 * root) := Real.log_nonneg (by linarith)
  have hpow := Real.log_le_rpow_div (x := 2 * current) (ε := (k : ℝ)⁻¹)
    (by linarith) (inv_pos.mpr hkR)
  simp only [div_inv_eq_mul] at hpow
  have hsum : Real.log (2 * root) ≤
      (2 * (k : ℝ)) * (2 * current) ^ (k : ℝ)⁻¹ := by nlinarith
  have h := pow_le_pow_left₀ hlog0 hsum k
  rw [mul_pow, Real.rpow_inv_natCast_pow (by linarith) (by omega)] at h
  nlinarith

theorem selected_descendant_volume (q W e j S : ℕ) (hq : 2 ≤ q)
    (hW : 0 < W) (hWmax : W ≤ 137151806) (he : 0 < e) (hS : 0 < S)
    (hj : j ≤ FloorDepth.depth 575 529 (by decide) e) :
    let r := OuterRows.rho 575 529 (by decide) 14 e
    let R := OuterRows.roundedRows (q ^ (2 * r))
      (W ^ FloorDepth.depth 575 529 (by decide) e)
    let X := q ^ (2 * (e - r))
    0 < (R / W ^ j) * X * S ∧
      R * X * S = W ^ j * ((R / W ^ j) * X * S) ∧
      R * X * S ≤ ((R / W ^ j) * X * S) ^ 2 := by
  dsimp only
  have hq0 : 0 < q := by omega
  have hb := OuterRows.selected_base_range q W hq hWmax
  have hh := OuterRows.twice_rho_lt_width 575 529 14 e (by decide) (by decide) he
  have hN : 0 < q ^ (2 * OuterRows.rho 575 529 (by decide) 14 e) := pow_pos hq0 _
  have hP : 0 < W ^ FloorDepth.depth 575 529 (by decide) e := pow_pos hW _
  have hR := lt_of_lt_of_le hN (OuterRows.rounding_bounds _ _ hN hP).1
  exact row_division_volume_square W _ j _ _ S hW hj hR hS
    (OuterRows.rounding_dvd _ _) (retained_range_covers_stock 575 529 14 e q W
      (by decide) (by omega) hb hh.le)

end DescriptorVolume

#print axioms DescriptorVolume.retained_range_covers_stock
#print axioms DescriptorVolume.row_division_volume_square
#print axioms DescriptorVolume.log_root_le_twice_log_current
#print axioms DescriptorVolume.descriptor_power_bound
#print axioms DescriptorVolume.selected_descendant_volume
