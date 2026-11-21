import Mathlib.Analysis.Fourier.ZMod
import Mathlib.Analysis.SpecialFunctions.Complex.Arg
import Mathlib.Tactic.Ring
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.GCongr

/-!
The forward transform uses the negative character and the counting measure.
The inverse transform uses the positive character and divides by the axis size.
A multiplier acts by circular convolution with its inverse-transform column.
-/

namespace CirculantRoot

open Finset AddChar
open scoped BigOperators ComplexConjugate Real

variable {N : ℕ} [NeZero N]

abbrev Signal (N : ℕ) := ZMod N → ℂ

noncomputable def convolution (h x : Signal N) (k : ZMod N) : ℂ :=
  ∑ j, h (k - j) * x j

noncomputable def multiplier (s x : Signal N) : Signal N :=
  (ZMod.dft (N := N)).symm (fun j ↦ s j * ZMod.dft x j)

theorem char_neg (x : ZMod N) :
    ZMod.stdAddChar (-x) = conj (ZMod.stdAddChar x) := by
  rw [AddChar.map_neg_eq_inv, ZMod.stdAddChar_apply]
  exact Circle.coe_inv_eq_conj _

theorem fourier_convolution (h x : Signal N) (k : ZMod N) :
    ZMod.dft (convolution h x) k = ZMod.dft h k * ZMod.dft x k := by
  simp only [ZMod.dft_apply, convolution, smul_eq_mul, Finset.mul_sum]
  rw [sum_comm]
  apply Finset.sum_congr rfl
  intro j _
  rw [Finset.sum_mul]
  refine Fintype.sum_equiv (Equiv.subRight j) _ _ ?_
  intro t
  change ZMod.stdAddChar (-(t*k)) * (h (t-j) * x j) =
    ZMod.stdAddChar (-((t-j)*k)) * h (t-j) * (ZMod.stdAddChar (-(j*k)) * x j)
  have he : -(t*k) = -((t-j)*k) + -(j*k) := by ring
  rw [he, AddChar.map_add_eq_mul]
  ring

theorem multiplier_is_circulant (s x : Signal N) :
    multiplier s x = convolution ((ZMod.dft (N := N)).symm s) x := by
  apply ZMod.dft.injective
  ext k
  simp [multiplier, fourier_convolution]

theorem multiplier_iterate (s x : Signal N) (b : ℕ) :
    (multiplier s)^[b] x = multiplier (fun j ↦ s j ^ b) x := by
  induction b with
  | zero => simp [multiplier]
  | succ b ih =>
    rw [Function.iterate_succ_apply', ih]
    apply ZMod.dft.injective
    ext j
    simp [multiplier, pow_succ, mul_comm, mul_assoc]

theorem opposite_mean (x : Signal N) (k : ZMod N) :
    (ZMod.dft (N := N)).symm x k = conj (ZMod.dft (fun j ↦ conj (x j)) k / (N : ℂ)) := by
  rw [ZMod.invDFT_apply, ZMod.dft_apply, map_div₀]
  simp only [smul_eq_mul, map_sum, map_mul, starRingEnd_self_apply, ← char_neg, neg_neg,
    map_natCast, div_eq_inv_mul]

theorem pair_fourier (x y : Signal N) :
    (∑ k, conj (ZMod.dft x k) * y k) =
      (N : ℂ) * ∑ j, conj (x j) * (ZMod.dft (N := N)).symm y j := by
  simp only [ZMod.dft_apply, ZMod.invDFT_apply, smul_eq_mul, map_sum, map_mul, ← char_neg, neg_neg]
  simp_rw [Finset.sum_mul]
  rw [Finset.sum_comm, Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro j _
  have hn : (N : ℂ) ≠ 0 := NeZero.ne _
  rw [show (N : ℂ) * (conj (x j) * ((N : ℂ)⁻¹ * ∑ k, ZMod.stdAddChar (k*j) * y k)) =
      conj (x j) * ∑ k, ZMod.stdAddChar (k*j) * y k by field_simp]
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro k _
  rw [mul_comm k j]
  ring

noncomputable def energy (x : Signal N) : ℝ := ∑ j, ‖x j‖ ^ 2

theorem fourier_energy (x : Signal N) : energy (ZMod.dft x) = N * energy x := by
  have h := pair_fourier x (ZMod.dft x)
  rw [LinearEquiv.symm_apply_apply] at h
  simp_rw [mul_comm (conj _), Complex.mul_conj, ← Complex.sq_norm] at h
  have hre (z : ℂ) : ((‖z‖ : ℂ)^2).re = ‖z‖^2 := by
    rw [← Complex.ofReal_pow, Complex.ofReal_re]
  simpa [energy, hre] using congrArg Complex.re h

theorem energy_nonneg (x : Signal N) : 0 ≤ energy x := Finset.sum_nonneg (fun _ _ ↦ sq_nonneg _)

/-- One uniformly bounded first-column error is repeated on each circular
diagonal. This bound charges all N nonzero potential contributions. -/
theorem convolution_energy (h x : Signal N) {η : ℝ} (hk : ∀ j, ‖h j‖ ≤ η) :
    energy (convolution h x) ≤ (N*η)^2 * energy x := by
  have each (k : ZMod N) : ‖convolution h x k‖^2 ≤ (N : ℝ) * η^2 * energy x := by
    have hnorm : ‖convolution h x k‖ ≤ ∑ j, η * ‖x j‖ := by
      apply (norm_sum_le _ _).trans
      apply Finset.sum_le_sum
      intro j _
      simpa [norm_mul] using mul_le_mul_of_nonneg_right (hk (k-j)) (norm_nonneg (x j))
    have hc := Finset.sum_mul_sq_le_sq_mul_sq (Finset.univ : Finset (ZMod N)) (fun _ ↦ η) (fun j ↦ ‖x j‖)
    calc
      ‖convolution h x k‖ ^ 2 ≤ (∑ j, η * ‖x j‖) ^ 2 :=
        pow_le_pow_left₀ (norm_nonneg _) hnorm 2
      _ ≤ _ := by simpa [energy, ZMod.card, nsmul_eq_mul] using hc
  calc
    energy (convolution h x) ≤ ∑ _ : ZMod N, ((N : ℝ)*η^2*energy x) :=
      Finset.sum_le_sum (fun k _ ↦ each k)
    _ = _ := by simp [ZMod.card, nsmul_eq_mul]; ring

theorem multiplier_scalar (c : ℂ) (s x : Signal N) :
    multiplier (fun j ↦ c * s j) x = fun j ↦ c * multiplier s x j := by
  apply ZMod.dft.injective
  ext k
  simp [ZMod.dft_const_mul, multiplier, mul_assoc]

theorem multiplier_energy (s x : Signal N) {b : ℝ} (hs : ∀ j, ‖s j‖ ≤ b) :
    energy (multiplier s x) ≤ b^2 * energy x := by
  have he : energy (ZMod.dft (multiplier s x)) ≤ b^2 * energy (ZMod.dft x) := by
    simp only [energy, multiplier, LinearEquiv.apply_symm_apply, Finset.mul_sum]
    apply Finset.sum_le_sum
    intro j _
    rw [norm_mul, mul_pow]
    exact mul_le_mul_of_nonneg_right (pow_le_pow_left₀ (norm_nonneg _) (hs j) 2) (sq_nonneg _)
  rw [fourier_energy, fourier_energy, mul_left_comm] at he
  exact le_of_mul_le_mul_left he (show (0:ℝ) < N by exact_mod_cast Nat.pos_of_ne_zero (NeZero.ne N))

theorem energy_add_with_bounds (u v : Signal N) {a b e : ℝ} (ha : 0 ≤ a) (hb : 0 ≤ b)
    (he : 0 ≤ e) (hu : energy u ≤ a^2 * e) (hv : energy v ≤ b^2 * e) :
    energy (u+v) ≤ (a+b)^2 * e := by
  have hc := Finset.sum_mul_sq_le_sq_mul_sq Finset.univ (fun j ↦ ‖u j‖) (fun j ↦ ‖v j‖)
  change (∑ j, ‖u j‖*‖v j‖)^2 ≤ energy u * energy v at hc
  have hprod := mul_le_mul hu hv (energy_nonneg v) (mul_nonneg (sq_nonneg a) he)
  have hs : (∑ j, ‖u j‖*‖v j‖) ≤ a*b*e := by
    have h := hc.trans hprod
    have hz : 0 ≤ a*b*e := by positivity
    nlinarith [sq_nonneg ((∑ j, ‖u j‖*‖v j‖) - a*b*e)]
  have htriangle : energy (u+v) ≤ ∑ j, (‖u j‖+‖v j‖)^2 := by
    apply Finset.sum_le_sum
    intro j _
    exact pow_le_pow_left₀ (norm_nonneg _) (norm_add_le ..) 2
  have hexpand : (∑ j, (‖u j‖+‖v j‖)^2) =
      energy u + 2*(∑ j, ‖u j‖*‖v j‖) + energy v := by
    simp only [add_sq, Finset.sum_add_distrib, mul_assoc, ← Finset.mul_sum, energy]
  linarith [show (a+b)^2*e = a^2*e + 2*(a*b*e) + b^2*e by ring]

theorem rounded_upper (s h x : Signal N) {b η : ℝ} (hb : 0 ≤ b) (hη : 0 ≤ η)
    (hs : ∀ j, ‖s j‖ ≤ b) (hh : ∀ j, ‖h j - (ZMod.dft (N := N)).symm s j‖ ≤ η) :
    energy (convolution h x) ≤ (b+(N:ℝ)*η)^2 * energy x := by
  let e : Signal N := h - (ZMod.dft (N := N)).symm s
  have hid : convolution h x = multiplier s x + convolution e x := by
    rw [multiplier_is_circulant]
    ext i
    simp [e, convolution, sub_mul, Finset.sum_sub_distrib]
  rw [hid]
  exact energy_add_with_bounds _ _ hb (by positivity) (energy_nonneg x)
    (multiplier_energy s x hs) (convolution_energy e x hh)

end CirculantRoot

#print axioms CirculantRoot.multiplier_is_circulant
#print axioms CirculantRoot.opposite_mean
#print axioms CirculantRoot.fourier_energy
#print axioms CirculantRoot.convolution_energy
#print axioms CirculantRoot.rounded_upper
