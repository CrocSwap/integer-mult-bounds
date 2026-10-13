import FloorRecurrence

/-! Exact outer row supply from existing address digits. This proves arithmetic
contracts, not physical gathering, padding, or fixed-tape implementation. -/
namespace OuterRows

theorem child_gap (m t e : ℕ) (ht : t < m) (he : m ≤ e) :
    (m - t) + FloorDepth.child m t e ≤ e := by
  have hm : 0 < m := Nat.zero_lt_of_lt ht
  have hf : 1 ≤ e / m := Nat.div_pos he hm
  have hgap : m - t + t = m := Nat.sub_add_cancel ht.le
  have hmul := Nat.mul_div_le e m
  have hd := Nat.mul_le_mul_left (m - t) hf
  unfold FloorDepth.child
  nlinarith

/-- An additive decrease gives a useful all-width bound in addition to the
sharper logarithmic depth estimate. -/
theorem depth_gap_bound (m t : ℕ) (ht : t < m) (e : ℕ) :
    (m - t) * FloorDepth.depth m t ht e ≤ e := by
  induction e using Nat.strong_induction_on with
  | h e ih =>
    by_cases hb : e < m
    · rw [FloorDepth.depth_base m t ht e hb]; simp
    · have he : m ≤ e := Nat.le_of_not_gt hb
      have hc := FloorDepth.child_lt m t e ht he
      have hi := ih (FloorDepth.child m t e) hc
      have hg := child_gap m t e ht he
      rw [FloorDepth.depth_step m t ht e he]
      nlinarith

def rho (m t : ℕ) (ht : t < m) (c e : ℕ) : ℕ :=
  c * FloorDepth.depth m t ht e

theorem twice_rho_lt_width (m t c e : ℕ) (ht : t < m)
    (hc : 2 * c < m - t) (he : 0 < e) : 2 * rho m t ht c e < e := by
  have hd := depth_gap_bound m t ht e
  by_cases hz : FloorDepth.depth m t ht e = 0
  · simp [rho, hz, he]
  · have hp : 0 < FloorDepth.depth m t ht e := Nat.pos_of_ne_zero hz
    have hmul := Nat.mul_lt_mul_of_pos_right hc hp
    unfold rho
    nlinarith

theorem row_range_covers_stock (m t c e q W : ℕ) (ht : t < m)
    (hbase : W ≤ q ^ (2 * c)) :
    W ^ FloorDepth.depth m t ht e ≤ q ^ (2 * rho m t ht c e) := by
  have h := Nat.pow_le_pow_left hbase (FloorDepth.depth m t ht e)
  rw [← pow_mul] at h
  simpa [rho, Nat.mul_assoc] using h

/-- Positive N rounded up to the least multiple of P. -/
def roundedRows (N P : ℕ) : ℕ := ((N - 1) / P + 1) * P

theorem rounding_bounds (N P : ℕ) (hN : 0 < N) (hP : 0 < P) :
    N ≤ roundedRows N P ∧ roundedRows N P < N + P := by
  have hdiv := Nat.mod_add_div (N - 1) P
  have hmod := Nat.mod_lt (N - 1) hP
  have hn : N - 1 + 1 = N := Nat.sub_add_cancel hN
  unfold roundedRows
  constructor <;> nlinarith [Nat.zero_le ((N - 1) % P)]

theorem rounding_dvd (N P : ℕ) : P ∣ roundedRows N P := by
  unfold roundedRows
  exact dvd_mul_left _ _

theorem rounding_less_than_twice (N P : ℕ) (hN : 0 < N)
    (hP : 0 < P) (hPN : P ≤ N) : roundedRows N P < 2 * N := by
  have h := (rounding_bounds N P hN hP).2
  omega

theorem remaining_width_positive (m t c e : ℕ) (ht : t < m)
    (hc : 2 * c < m - t) (he : 0 < e) : 0 < e - rho m t ht c e := by
  have h := twice_rho_lt_width m t c e ht hc he
  omega

theorem reduced_width_stock (m t c e q W : ℕ) (ht : t < m) :
    W ^ FloorDepth.depth m t ht (e - rho m t ht c e) ∣
      roundedRows (q ^ (2 * rho m t ht c e)) (W ^ FloorDepth.depth m t ht e) := by
  have hd := FloorDepth.depth_mono m t ht (Nat.sub_le e (rho m t ht c e))
  exact dvd_trans (pow_dvd_pow W hd) (rounding_dvd _ _)

theorem existing_digit_volume (q e r : ℕ) (hr : r ≤ e) :
    q ^ (2 * r) * q ^ (2 * (e - r)) = q ^ (2 * e) := by
  rw [← pow_add]
  congr 1
  omega

theorem padded_volume_lt_twice (q W m t c e : ℕ) (ht : t < m)
    (hq : 0 < q) (hW : 0 < W) (hbase : W ≤ q ^ (2 * c))
    (hr : rho m t ht c e ≤ e) :
    roundedRows (q ^ (2 * rho m t ht c e)) (W ^ FloorDepth.depth m t ht e) *
      q ^ (2 * (e - rho m t ht c e)) < 2 * q ^ (2 * e) := by
  have hR := rounding_less_than_twice
    (q ^ (2 * rho m t ht c e)) (W ^ FloorDepth.depth m t ht e)
    (pow_pos hq _) (pow_pos hW _) (row_range_covers_stock m t c e q W ht hbase)
  have h := Nat.mul_lt_mul_of_pos_right hR (pow_pos hq (2 * (e - rho m t ht c e)))
  simpa [Nat.mul_assoc, existing_digit_volume q e (rho m t ht c e) hr] using h

theorem padded_volume_with_spectators (q W m t c e S : ℕ) (ht : t < m)
    (hq : 0 < q) (hW : 0 < W) (hbase : W ≤ q ^ (2 * c))
    (hr : rho m t ht c e ≤ e) (hS : 0 < S) :
    S * (roundedRows (q ^ (2 * rho m t ht c e)) (W ^ FloorDepth.depth m t ht e) *
      q ^ (2 * (e - rho m t ht c e))) < 2 * (S * q ^ (2 * e)) := by
  have h := Nat.mul_lt_mul_of_pos_left
    (padded_volume_lt_twice q W m t c e ht hq hW hbase hr) hS
  simpa [Nat.mul_left_comm S 2] using h

theorem rho_log_bound (m t c e : ℕ) (ht : t < m) (ht0 : 0 < t) (he : 0 < e) :
    (rho m t ht c e : ℝ) ≤ (c : ℝ) *
      (1 + Real.log e / Real.log ((m : ℝ) / t)) := by
  have h := FloorRecurrence.depth_log_bound m t ht ht0 e he
  have hc : (0 : ℝ) ≤ c := Nat.cast_nonneg c
  simpa [rho] using mul_le_mul_of_nonneg_left h hc

/-- Gathering O(rho) high digits is absorbed into every positive power of e;
the physical cost of a single digit operation remains an external contract. -/
theorem rho_power_bound (m t c e : ℕ) (ht : t < m) (ht0 : 0 < t)
    (he : 0 < e) (p : ℝ) (hp : 0 < p) :
    (rho m t ht c e : ℝ) ≤
      (c : ℝ) * (1 + 1 / (p * Real.log ((m : ℝ) / t))) * (e : ℝ) ^ p := by
  have htR : (0 : ℝ) < t := by exact_mod_cast ht0
  have htm : (t : ℝ) < m := by exact_mod_cast ht
  have hlog : 0 < Real.log ((m : ℝ) / t) :=
    Real.log_pos ((one_lt_div htR).2 htm)
  have heR : (1 : ℝ) ≤ e := by exact_mod_cast he
  have hone : (1 : ℝ) ≤ (e : ℝ) ^ p := Real.one_le_rpow heR hp.le
  have hl := Real.log_natCast_le_rpow_div e hp
  have hd := div_le_div_of_nonneg_right hl hlog.le
  have hc : (0 : ℝ) ≤ c := Nat.cast_nonneg c
  calc
    (rho m t ht c e : ℝ) ≤ (c : ℝ) *
        (1 + Real.log e / Real.log ((m : ℝ) / t)) := rho_log_bound m t c e ht ht0 he
    _ ≤ (c : ℝ) * ((e : ℝ) ^ p + ((e : ℝ) ^ p / p) / Real.log ((m : ℝ) / t)) :=
      mul_le_mul_of_nonneg_left (add_le_add hone hd) hc
    _ = _ := by ring

/-- One outer gathering/padding layer preserves the width exponent. Its
implementation costs are exposed in `outer_contract`, not inferred from
arithmetic volume or row counts. -/
theorem outer_cost_bound (m t c e : ℕ) (ht : t < m) (ht0 : 0 < t)
    (he : 0 < e) (p A C V paddedV cost : ℝ) (hp : 0 < p)
    (hA : 0 ≤ A) (hC : 0 ≤ C) (hV : 0 ≤ V)
    (volume_bound : paddedV ≤ 2 * V)
    (outer_contract : cost ≤ C * V * ((rho m t ht c e : ℝ) + 1) +
      A * paddedV * ((e - rho m t ht c e : ℕ) : ℝ) ^ p) :
    cost ≤ (C * ((c : ℝ) * (1 + 1 / (p * Real.log ((m : ℝ) / t))) + 1) +
      2 * A) * V * (e : ℝ) ^ p := by
  have heR : (1 : ℝ) ≤ e := by exact_mod_cast he
  have hone : (1 : ℝ) ≤ (e : ℝ) ^ p := Real.one_le_rpow heR hp.le
  have hr := rho_power_bound m t c e ht ht0 he p hp
  have hg : (rho m t ht c e : ℝ) + 1 ≤
      ((c : ℝ) * (1 + 1 / (p * Real.log ((m : ℝ) / t))) + 1) * (e : ℝ) ^ p := by
    nlinarith
  have hpw : ((e - rho m t ht c e : ℕ) : ℝ) ^ p ≤ (e : ℝ) ^ p := by
    apply Real.rpow_le_rpow (Nat.cast_nonneg _)
    · exact_mod_cast Nat.sub_le e (rho m t ht c e)
    · exact hp.le
  have overhead := mul_le_mul_of_nonneg_left hg (mul_nonneg hC hV)
  have child : A * paddedV * ((e - rho m t ht c e : ℕ) : ℝ) ^ p ≤
      A * (2 * V) * (e : ℝ) ^ p := by
    apply mul_le_mul
    · exact mul_le_mul_of_nonneg_left volume_bound hA
    · exact hpw
    · exact Real.rpow_nonneg (Nat.cast_nonneg _) _
    · positivity
  calc
    cost ≤ _ := outer_contract
    _ ≤ C * V * (((c : ℝ) * (1 + 1 / (p * Real.log ((m : ℝ) / t))) + 1) * (e : ℝ) ^ p) +
        A * (2 * V) * (e : ℝ) ^ p := add_le_add overhead child
    _ = _ := by ring

theorem selected_base_range (q W : ℕ) (hq : 2 ≤ q) (hW : W ≤ 137151806) :
    W ≤ q ^ (2 * 14) := by
  have h := Nat.pow_le_pow_left hq 28
  norm_num at h ⊢
  omega

theorem selected_outer_rows (q W e : ℕ) (hq : 2 ≤ q) (hW : 0 < W)
    (hWmax : W ≤ 137151806) (he : 0 < e) :
    let r := rho 575 529 (by decide) 14 e
    let N := q ^ (2 * r)
    let P := W ^ FloorDepth.depth 575 529 (by decide) e
    2 * r < e ∧ 0 < e - r ∧ P ≤ N ∧ N ≤ roundedRows N P ∧
      roundedRows N P < 2 * N ∧
      W ^ FloorDepth.depth 575 529 (by decide) (e - r) ∣ roundedRows N P ∧
      roundedRows N P * q ^ (2 * (e - r)) < 2 * q ^ (2 * e) := by
  dsimp only
  have hq0 : 0 < q := by omega
  have hb := selected_base_range q W hq hWmax
  have hr := twice_rho_lt_width 575 529 14 e (by decide) (by decide) he
  have hn : 0 < q ^ (2 * rho 575 529 (by decide) 14 e) := pow_pos hq0 _
  have hp : 0 < W ^ FloorDepth.depth 575 529 (by decide) e := pow_pos hW _
  have hcover := row_range_covers_stock 575 529 14 e q W (by decide) hb
  exact ⟨hr, remaining_width_positive 575 529 14 e (by decide) (by decide) he,
    hcover, (rounding_bounds _ _ hn hp).1, rounding_less_than_twice _ _ hn hp hcover,
    reduced_width_stock 575 529 14 e q W (by decide),
    padded_volume_lt_twice q W 575 529 14 e (by decide) hq0 hW hb (by omega)⟩

end OuterRows

#print axioms OuterRows.child_gap
#print axioms OuterRows.depth_gap_bound
#print axioms OuterRows.twice_rho_lt_width
#print axioms OuterRows.row_range_covers_stock
#print axioms OuterRows.rounding_bounds
#print axioms OuterRows.rounding_dvd
#print axioms OuterRows.rounding_less_than_twice
#print axioms OuterRows.remaining_width_positive
#print axioms OuterRows.reduced_width_stock
#print axioms OuterRows.existing_digit_volume
#print axioms OuterRows.padded_volume_lt_twice
#print axioms OuterRows.padded_volume_with_spectators
#print axioms OuterRows.rho_log_bound
#print axioms OuterRows.rho_power_bound
#print axioms OuterRows.outer_cost_bound
#print axioms OuterRows.selected_base_range
#print axioms OuterRows.selected_outer_rows
