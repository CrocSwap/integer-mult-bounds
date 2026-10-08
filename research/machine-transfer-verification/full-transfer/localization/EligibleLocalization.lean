import Mathlib.RingTheory.Localization.Away.Basic
import Mathlib.Data.Rat.Cast.CharZero
import Mathlib.Data.Rat.Lemmas
import Mathlib.Data.ZMod.Basic
import Mathlib.Data.Nat.Prime.Infinite
import Mathlib.Data.Matrix.Basic
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.Data.Matrix.Kronecker
import Mathlib.Tactic

/-! Finite rational tables live in Z[1/D], not in a fictitious ring map from
Q to finite characteristic. The rational view is injective; reduction exists
only when D is a unit. A finite table can include inverses of selected nonzero
Gram determinants and pivots, thereby recording the numerator exceptions too.
-/
namespace EligibleLocalization
open scoped BigOperators

abbrev Coeff (D : ℕ) := Localization.Away (D : ℤ)

noncomputable def rationalView (D : ℕ) (hD : 0 < D) : Coeff D →+* ℚ :=
  IsLocalization.Away.lift (D : ℤ) (g := Int.castRingHom ℚ)
    (isUnit_iff_ne_zero.mpr (by change (D : ℚ) ≠ 0; exact_mod_cast hD.ne'))

@[simp] theorem rationalView_integer (D : ℕ) (hD : 0 < D) (a : ℤ) :
    rationalView D hD (algebraMap ℤ (Coeff D) a) = (a : ℚ) := by
  simp [rationalView]

theorem rationalView_injective (D : ℕ) (hD : 0 < D) :
    Function.Injective (rationalView D hD) := by
  apply IsLocalization.injective_of_map_algebraMap_zero (M := Submonoid.powers (D : ℤ))
    (Coeff D) (rationalView D hD)
  intro a ha
  have hz : a = 0 := by simpa using ha
  simp [hz]

noncomputable def reduction (D : ℕ) (K : Type) [CommRing K]
    (eligible : IsUnit (D : K)) : Coeff D →+* K :=
  IsLocalization.Away.lift (D : ℤ) (g := Int.castRingHom K) (by simpa using eligible)

@[simp] theorem reduction_integer (D : ℕ) (K : Type) [CommRing K]
    (eligible : IsUnit (D : K)) (a : ℤ) :
    reduction D K eligible (algebraMap ℤ (Coeff D) a) = (a : K) := by
  simp [reduction]

noncomputable def fraction (D : ℕ) (a : ℤ) (b : ℕ) (hb : b ∣ D) : Coeff D :=
  algebraMap ℤ (Coeff D) a *
    ↑((IsLocalization.Away.isUnit_of_dvd (S := Coeff D) (D : ℤ)
      (by exact_mod_cast hb : (b : ℤ) ∣ (D : ℤ))).unit⁻¹)

theorem fraction_mul_denominator (D : ℕ) (a : ℤ) (b : ℕ) (hb : b ∣ D) :
    fraction D a b hb * algebraMap ℤ (Coeff D) b = algebraMap ℤ (Coeff D) a := by
  let h := IsLocalization.Away.isUnit_of_dvd (S := Coeff D) (D : ℤ)
    (by exact_mod_cast hb : (b : ℤ) ∣ (D : ℤ))
  change algebraMap ℤ (Coeff D) a * ↑(h.unit⁻¹) * algebraMap ℤ (Coeff D) b = _
  have hcancel : ↑(h.unit⁻¹) * algebraMap ℤ (Coeff D) b = 1 := by
    simpa only [h.unit_spec] using Units.inv_mul h.unit
  rw [mul_assoc, hcancel, mul_one]

theorem rationalView_fraction (D : ℕ) (hD : 0 < D) (a : ℤ) (b : ℕ)
    (hb : b ∣ D) (hb0 : 0 < b) :
    rationalView D hD (fraction D a b hb) = (a : ℚ) / b := by
  apply (eq_div_iff (by exact_mod_cast hb0.ne' : (b : ℚ) ≠ 0)).mpr
  have h := congrArg (rationalView D hD) (fraction_mul_denominator D a b hb)
  simpa using h

def denominatorProduct {ι : Type} [Fintype ι] (values : ι → ℚ) : ℕ :=
  ∏ i, (values i).den

theorem denominatorProduct_positive {ι : Type} [Fintype ι] (values : ι → ℚ) :
    0 < denominatorProduct values := by
  exact Finset.prod_pos (fun i _ => (values i).den_pos)

theorem denominator_divides_product {ι : Type} [Fintype ι] (values : ι → ℚ) (i : ι) :
    (values i).den ∣ denominatorProduct values := by
  exact Finset.dvd_prod_of_mem (fun i => (values i).den) (Finset.mem_univ i)

noncomputable def liftTable {ι : Type} [Fintype ι] (values : ι → ℚ) (i : ι) :
    Coeff (denominatorProduct values) :=
  fraction _ (values i).num (values i).den (denominator_divides_product values i)

/-- Every finite rational table has a genuine common-denominator localized
representation. Inputs may include all matrix entries and reciprocal pivots. -/
theorem liftTable_exact {ι : Type} [Fintype ι] (values : ι → ℚ) (i : ι) :
    rationalView (denominatorProduct values) (denominatorProduct_positive values)
      (liftTable values i) = values i := by
  rw [liftTable, rationalView_fraction]
  · exact (values i).num_div_den
  · exact (values i).den_pos

/-- Storing a reciprocal adds the original numerator to the finite exception
product. This is the precise extra condition for nonzero pivots and minors. -/
theorem reciprocal_numerator_divides_product {ι : Type} [Fintype ι]
    (values : ι → ℚ) (i j : ι) (hi : values i ≠ 0)
    (reciprocal : values j = (values i)⁻¹) :
    (values i).num.natAbs ∣ denominatorProduct values := by
  have h := denominator_divides_product values j
  rwa [reciprocal, Rat.den_inv_of_ne_zero hi] at h

theorem eligible_prime_power (D p f : ℕ) (coprime : D.Coprime p) :
    IsUnit (D : ZMod (p ^ f)) :=
  (ZMod.isUnit_iff_coprime D (p ^ f)).mpr (coprime.pow_right f)

noncomputable def reducePrimePower (D p f : ℕ) (coprime : D.Coprime p) :
    Coeff D →+* ZMod (p ^ f) := reduction D _ (eligible_prime_power D p f coprime)

/-- There is an odd eligible prime after every fixed finite table is chosen.
The same prime works for every address-block exponent f. -/
theorem exists_eligible_odd_prime (D : ℕ) (hD : 0 < D) :
    ∃ p, p.Prime ∧ 2 < p ∧ D.Coprime p ∧ ∀ f, IsUnit (D : ZMod (p ^ f)) := by
  obtain ⟨p, hlarge, hp⟩ := Nat.exists_infinite_primes (D + 3)
  have hDp : D < p := by omega
  have hnot : ¬ p ∣ D := fun hd => (Nat.le_of_dvd hD hd).not_gt hDp
  have hc : D.Coprime p := (hp.coprime_iff_not_dvd.mpr hnot).symm
  exact ⟨p, hp, by omega, hc, fun f => eligible_prime_power D p f hc⟩

end EligibleLocalization

#print axioms EligibleLocalization.rationalView_integer
#print axioms EligibleLocalization.rationalView_injective
#print axioms EligibleLocalization.reduction_integer
#print axioms EligibleLocalization.fraction_mul_denominator
#print axioms EligibleLocalization.rationalView_fraction
#print axioms EligibleLocalization.denominatorProduct_positive
#print axioms EligibleLocalization.denominator_divides_product
#print axioms EligibleLocalization.liftTable_exact
#print axioms EligibleLocalization.reciprocal_numerator_divides_product
#print axioms EligibleLocalization.eligible_prime_power
#print axioms EligibleLocalization.exists_eligible_odd_prime
