import SelectedMomentUpperAggregate
import SelectedMomentLogUnitEnclosure

/-!
Source-bound binary reduction and outward-grid rounding for the nine selected
logarithm arguments in PR531's pinned base_two_moment.py. The exact rational
source_domains identities and the five accepted real unit bounds are reused.
The ceiling adapter concerns the executable Batteries Rat.ceil used by the
source transcription; it does not assume identity with abstract Int.ceil.

Conditional source context: kappa = 1517760977820331/1000000000000000000
= 0.001517760977820331. This module supplies rounded logarithm upper bounds.
Positive weighted moment aggregation, operator/profile realization, initial
saving validity and all-size multiplier transfer remain separate obligations.
Attribution: inherited PR361 engine through PR531 and installed Mathlib
logarithm/floor identities. Prepared with OpenAI assistance.
-/
namespace CurrentMain.SelectedRoundedLogEnclosure

open SelectedMomentLogCheckpoints SelectedMomentUpperAggregate
open SelectedMomentLogUnitEnclosure
set_option Elab.async false

/-- Outwardness of the actual executable ceiling, by its two denominator cases. -/
private theorem executable_ceil_outward (q : Rat) : q ≤ Rat.ofInt (Rat.ceil q) := by
  unfold Rat.ceil
  split_ifs with h
  · change q ≤ (q.num : Rat)
    have he := q.num_div_den
    rw [h, Nat.cast_one, div_one] at he
    exact le_of_eq he.symm
  · change q ≤ ((q.num / (q.den : Int) + 1 : Int) : Rat)
    have hl := Int.lt_floor_add_one q
    rw [Rat.floor_def] at hl
    simpa only [Int.cast_add, Int.cast_one] using (le_of_lt hl)

/-- The source's exact10^30-grid operation rounds every rational input outward. -/
theorem ceilGrid_outward (q : Rat) : q ≤ ceilGrid q := by
  have hg : (0 : Rat) < gridScale := by norm_num [gridScale]
  unfold ceilGrid
  exact (le_div_iff₀ hg).2 (executable_ceil_outward (q * gridScale))

/-- Source binary factorization, positive logarithm algebra and outward ceiling. -/
private theorem rounded_from_domain (rank count k n d : Nat)
    (hd : sourceLogDomain rank count k n d)
    (hu : Real.log (((d+n : Nat) : ℝ) / ((d-n : Nat) : ℝ)) ≤
      (unitUpper n d : ℝ)) :
    Real.log ((73 : ℝ)/(rank : ℝ)) ≤ (roundedLog k n d : ℝ) := by
  rcases hd with ⟨hr, _, _, he, hlo, _⟩
  have hp : (0 : ℝ) < ((2^k : Nat) : ℝ) := by
    exact_mod_cast Nat.two_pow_pos k
  have hq : (0 : ℝ) < ((d+n : Nat) : ℝ) / ((d-n : Nat) : ℝ) := by
    have hh : (1 : ℝ) < ((d+n : Nat) : ℝ) / ((d-n : Nat) : ℝ) := by
      have hc : ((1 : Rat) : ℝ) <
          ((((d+n : Nat) : Rat) / ((d-n : Nat) : Rat)) : ℝ) := by
        exact_mod_cast hlo
      simpa only [Rat.cast_one, Rat.cast_div, Rat.cast_natCast] using hc
    linarith
  have heR : (73 : ℝ)/(rank : ℝ)/((2^k : Nat) : ℝ) =
      ((d+n : Nat) : ℝ)/((d-n : Nat) : ℝ) := by
    have hc := congrArg (fun q : Rat => (q : ℝ)) he
    simpa only [Rat.cast_div, Rat.cast_ofNat, Rat.cast_natCast] using hc
  have hx := (div_eq_iff (ne_of_gt hp)).mp heR
  have htw := mul_le_mul_of_nonneg_left log_two_upper
    (Nat.cast_nonneg k : (0 : ℝ) ≤ (k : ℝ))
  have hout := ceilGrid_outward (unitUpper n d + (k : Rat) * unitUpper 1 3)
  have hcast : ((unitUpper n d + (k : Rat) * unitUpper 1 3 : Rat) : ℝ) ≤
      (ceilGrid (unitUpper n d + (k : Rat) * unitUpper 1 3) : ℝ) := by
    exact_mod_cast hout
  have hrounded : (unitUpper n d : ℝ) + (k : ℝ) * (unitUpper 1 3 : ℝ) ≤
      (roundedLog k n d : ℝ) := by
    simpa only [roundedLog, Rat.cast_add, Rat.cast_mul, Rat.cast_natCast] using hcast
  calc
    Real.log ((73 : ℝ)/(rank : ℝ)) =
        Real.log (((d+n : Nat) : ℝ)/((d-n : Nat) : ℝ)) +
          (k : ℝ) * Real.log 2 := by
      rw [hx, Real.log_mul (ne_of_gt hq) (ne_of_gt hp)]
      norm_num only [Nat.cast_pow, Nat.cast_ofNat, Real.log_pow]
    _ ≤ (unitUpper n d : ℝ) + (k : ℝ) * (unitUpper 1 3 : ℝ) :=
      add_le_add hu htw
    _ ≤ (roundedLog k n d : ℝ) := hrounded

/-- The nine source ranks in their original order, including the rank-one fallback input. -/
theorem selected_rounded_log_enclosures :
    Real.log (73 : ℝ) ≤ (roundedLog 6 9 137 : ℝ) ∧
    Real.log ((73 : ℝ)/2) ≤ (roundedLog 5 9 137 : ℝ) ∧
    Real.log ((73 : ℝ)/3) ≤ (roundedLog 4 25 121 : ℝ) ∧
    Real.log ((73 : ℝ)/4) ≤ (roundedLog 4 9 137 : ℝ) ∧
    Real.log ((73 : ℝ)/5) ≤ (roundedLog 3 33 113 : ℝ) ∧
    Real.log ((73 : ℝ)/6) ≤ (roundedLog 3 25 121 : ℝ) ∧
    Real.log ((73 : ℝ)/7) ≤ (roundedLog 3 17 129 : ℝ) ∧
    Real.log ((73 : ℝ)/32) ≤ (roundedLog 1 9 137 : ℝ) ∧
    Real.log ((73 : ℝ)/48) ≤ (roundedLog 0 25 121 : ℝ) := by
  have hu9 : Real.log (((137+9 : Nat) : ℝ)/((137-9 : Nat) : ℝ)) ≤
      (unitUpper 9 137 : ℝ) := by
    convert log_73_64_upper using 1 <;> norm_num
  have hu25 : Real.log (((121+25 : Nat) : ℝ)/((121-25 : Nat) : ℝ)) ≤
      (unitUpper 25 121 : ℝ) := by
    convert log_73_48_upper using 1 <;> norm_num
  have hu33 : Real.log (((113+33 : Nat) : ℝ)/((113-33 : Nat) : ℝ)) ≤
      (unitUpper 33 113 : ℝ) := by
    convert log_73_40_upper using 1 <;> norm_num
  have hu17 : Real.log (((129+17 : Nat) : ℝ)/((129-17 : Nat) : ℝ)) ≤
      (unitUpper 17 129 : ℝ) := by
    convert log_73_56_upper using 1 <;> norm_num
  rcases source_domains with ⟨h1, h2, h3, h4, h5, h6, h7, h32, h48, _⟩
  refine ⟨?_, rounded_from_domain 2 54144 5 9 137 h2 hu9,
    rounded_from_domain 3 13991 4 25 121 h3 hu25,
    rounded_from_domain 4 28224 4 9 137 h4 hu9,
    rounded_from_domain 5 7615 3 33 113 h5 hu33,
    rounded_from_domain 6 4032 3 25 121 h6 hu25,
    rounded_from_domain 7 1376 3 17 129 h7 hu17,
    rounded_from_domain 32 1 1 9 137 h32 hu9,
    rounded_from_domain 48 825 0 25 121 h48 hu25⟩
  simpa only [Nat.cast_one, div_one] using (rounded_from_domain 1 146016 6 9 137 h1 hu9)

#print axioms ceilGrid_outward
#print axioms selected_rounded_log_enclosures
end CurrentMain.SelectedRoundedLogEnclosure
