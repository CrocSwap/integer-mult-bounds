import AccretiveFactors
import Mathlib.Algebra.Ring.Int.Parity
import Mathlib.Data.ZMod.ValMinAbs

/-!
The quadratic label in ZMod (2*N) works for every positive transform
length. The integer midpoint table gives two identical circulants and one
known scalar. The full Gaussian sum determines the mean normalization.
-/

namespace CirculantRoot

open Finset AddChar
open scoped BigOperators ComplexConjugate Real

variable {N : ℕ} [NeZero N]

/-- The exponent in the positive chirp. Its value is independent of the
integer lift of the index, including when N is even. -/
def quadLabel (j : ZMod N) : ZMod (2*N) :=
  ((j.valMinAbs * (j.valMinAbs + (N : ℤ)) : ℤ) : ZMod (2*N))

omit [NeZero N] in
theorem label_congr {x y : ℤ} (h : (x : ZMod N) = (y : ZMod N)) :
    (((x*(x+N)) : ℤ) : ZMod (2*N)) = (((y*(y+N)) : ℤ) : ZMod (2*N)) := by
  obtain ⟨k, hk⟩ := (ZMod.intCast_eq_intCast_iff_dvd_sub x y N).mp h
  obtain ⟨z, hz⟩ := Int.even_mul_succ_self k
  apply (ZMod.intCast_eq_intCast_iff_dvd_sub ..).mpr
  refine ⟨x*k + N*z, ?_⟩
  have he : y = x + N*k := by linarith
  rw [he]
  push_cast
  linear_combination (N : ℤ)^2 * hz

omit [NeZero N] in
theorem label_lift (z : ℤ) :
    quadLabel (z : ZMod N) = ((z*(z+N) : ℤ) : ZMod (2*N)) :=
  label_congr (ZMod.coe_valMinAbs (z : ZMod N))

noncomputable def quadChirp (j : ZMod N) : ℂ := ZMod.stdAddChar (quadLabel j)

theorem double_character (z : ℤ) :
    ZMod.stdAddChar ((2*z : ℤ) : ZMod (2*N)) = ZMod.stdAddChar (z : ZMod N) := by
  rw [ZMod.stdAddChar_coe, ZMod.stdAddChar_coe]
  congr 1
  push_cast
  field_simp

theorem quad_unit (j : ZMod N) : ‖quadChirp j‖ = 1 := by
  simp [quadChirp, ZMod.stdAddChar_apply]

theorem quad_neg (j : ZMod N) : quadChirp (-j) = quadChirp j := by
  obtain ⟨x, rfl⟩ := ZMod.intCast_surjective j
  rw [← Int.cast_neg]
  simp only [quadChirp, label_lift]
  congr 1
  apply (ZMod.intCast_eq_intCast_iff_dvd_sub ..).mpr
  refine ⟨x, ?_⟩
  push_cast
  ring

theorem quad_sub (j k : ZMod N) :
    quadChirp (j-k) = quadChirp j * quadChirp k * ZMod.stdAddChar (-(j*k)) := by
  obtain ⟨x, rfl⟩ := ZMod.intCast_surjective j
  obtain ⟨y, rfl⟩ := ZMod.intCast_surjective k
  rw [← Int.cast_sub, ← Int.cast_mul, ← Int.cast_neg, ← double_character]
  simp only [quadChirp, label_lift, ← AddChar.map_add_eq_mul, ← Int.cast_add]
  congr 1
  apply (ZMod.intCast_eq_intCast_iff_dvd_sub ..).mpr
  refine ⟨y, ?_⟩
  push_cast
  ring

noncomputable def quadDiag (j : ZMod N) : ℂ := conj (quadChirp j)

theorem qd_mul (j : ZMod N) : quadDiag j * quadChirp j = 1 := by
  rw [quadDiag, mul_comm, Complex.mul_conj, ← Complex.sq_norm, quad_unit]
  norm_num

theorem quad_zero : quadChirp (0 : ZMod N) = 1 := by
  have h := label_lift (N := N) 0
  simp only [Int.cast_zero, zero_add, zero_mul] at h
  simp [quadChirp, h]

theorem quad_dft (x : Signal N) (k : ZMod N) :
    ZMod.dft x k = quadDiag k * convolution quadChirp (fun j ↦ quadDiag j * x j) k := by
  rw [ZMod.dft_apply, convolution, Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro j _
  rw [quad_sub, smul_eq_mul, mul_comm j k]
  linear_combination -(quadDiag j * quadChirp j * ZMod.stdAddChar (-(k*j)) * x j) * qd_mul k
    - (ZMod.stdAddChar (-(k*j)) * x j) * qd_mul j

theorem quad_spectrum (k : ZMod N) :
    ZMod.dft quadChirp k = quadDiag k * ∑ j : ZMod N, quadChirp j := by
  rw [ZMod.dft_apply, Finset.mul_sum]
  refine Fintype.sum_equiv (Equiv.subRight k) _ _ ?_
  intro j
  change ZMod.stdAddChar (-(j*k)) • quadChirp j = quadDiag k * quadChirp (j-k)
  rw [quad_sub, smul_eq_mul]
  linear_combination -(ZMod.stdAddChar (-(j*k)) * quadChirp j) * qd_mul k

theorem all_gauss_norm_sq : ‖∑ j : ZMod N, quadChirp j‖ ^ 2 = (N : ℝ) := by
  let G := ∑ j : ZMod N, quadChirp j
  have h := congrFun (ZMod.dft_dft (N := N) quadChirp) 0
  rw [ZMod.dft_apply_zero] at h
  simp_rw [quad_spectrum, quadDiag] at h
  rw [← Finset.sum_mul, ← map_sum] at h
  change conj G * G = _ at h
  have hh : (‖G‖^2 : ℂ) = (N : ℂ) := by
    rw [← Complex.ofReal_pow, Complex.sq_norm, ← Complex.mul_conj, mul_comm, h]
    simp [quad_zero]
  exact_mod_cast hh

theorem quad_multiplier (x : Signal N) :
    convolution quadChirp x = fun k ↦ (∑ j : ZMod N, quadChirp j) * multiplier quadDiag x k := by
  apply ZMod.dft.injective
  ext k
  rw [fourier_convolution, quad_spectrum]
  simp [ZMod.dft_const_mul, multiplier, mul_assoc, mul_left_comm]

theorem all_mean (x : Signal N) (k : ZMod N) :
    ZMod.dft x k / N = ((∑ j : ZMod N, quadChirp j) / (N : ℂ)) * quadDiag k *
      multiplier quadDiag (fun j ↦ quadDiag j * x j) k := by
  rw [quad_dft, quad_multiplier]
  ring

end CirculantRoot

namespace CirculantRoot

open Finset AddChar
open scoped BigOperators ComplexConjugate Real

variable {D : ℕ} [NeZero D]

/-- Assign the midpoint of a frequency-grid cell before taking a square root. -/
def midIndex (z : ZMod D) : ZMod (2*D) :=
  ((2*z.valMinAbs + 1 : ℤ) : ZMod (2*D))

noncomputable def midAngle (z : ZMod D) : ℝ :=
  π * (midIndex z).valMinAbs / (2*(D:ℝ))

noncomputable def midRoot (z : ZMod D) : ℂ :=
  Complex.exp (↑(midAngle z) * Complex.I)

noncomputable def midScalar (D : ℕ) [NeZero D] : ℂ :=
  ZMod.stdAddChar (1 : ZMod (2*D))

theorem mid_square (z : ZMod D) : midRoot z ^ 2 = midScalar D * ZMod.stdAddChar z := by
  have hc := ZMod.stdAddChar_coe (N := 2*D) (midIndex z).valMinAbs
  rw [ZMod.coe_valMinAbs] at hc
  have he : midRoot z ^ 2 = ZMod.stdAddChar (midIndex z) := by
    rw [midRoot, ← Complex.exp_nat_mul, hc]
    congr 1
    unfold midAngle
    push_cast
    ring
  rw [he, midIndex, Int.cast_add, AddChar.map_add_eq_mul, double_character, ZMod.coe_valMinAbs]
  simp [midScalar, mul_comm]

omit [NeZero D] in
theorem mid_unit (z : ZMod D) : ‖midRoot z‖ = 1 :=
  Complex.norm_exp_ofReal_mul_I _

theorem scalar_unit : ‖midScalar D‖ = 1 := by simp [midScalar, ZMod.stdAddChar_apply]

theorem index_gap (hD : Even D) (z : ZMod D) :
    -(D : ℤ)+1 ≤ (midIndex z).valMinAbs ∧ (midIndex z).valMinAbs ≤ (D : ℤ)-1 := by
  let m := (midIndex z).valMinAbs
  have hc : (m : ZMod (2*D)) = ((2*z.valMinAbs+1 : ℤ) : ZMod (2*D)) :=
    ZMod.coe_valMinAbs _
  obtain ⟨k, hk⟩ := (ZMod.intCast_eq_intCast_iff_dvd_sub ..).mp hc
  push_cast at hk
  obtain ⟨v, hv⟩ := hD
  have hv' : (D : ℤ) = v + (v : ℤ) := by exact_mod_cast hv
  obtain ⟨hl, hu⟩ := (midIndex z).valMinAbs_mem_Ioc
  change -(↑(2*D) : ℤ) < m * 2 at hl
  change m * 2 ≤ (↑(2*D) : ℤ) at hu
  push_cast at hl hu
  have hodd : m = 2*(z.valMinAbs - (D:ℤ)*k)+1 := by linarith [hk]
  change - (D : ℤ)+1 ≤ m ∧ m ≤ (D : ℤ)-1
  omega

theorem abs_sin_nat_mul (u : ℝ) (n : ℕ) :
    |Real.sin (n*u)| ≤ n*|Real.sin u| := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [Nat.cast_succ, add_mul, one_mul, Real.sin_add]
    apply (abs_add_le ..).trans
    rw [abs_mul, abs_mul]
    have h₁ := mul_le_mul_of_nonneg_left (Real.abs_cos_le_one u) (abs_nonneg (Real.sin (n*u)))
    have h₂ := mul_le_mul_of_nonneg_right (Real.abs_cos_le_one (n*u)) (abs_nonneg (Real.sin u))
    linarith

theorem sine_gap : (D : ℝ)⁻¹ ≤ Real.sin (π/(2*(D:ℝ))) := by
  have hd : (0 : ℝ) < D := by exact_mod_cast Nat.pos_of_ne_zero (NeZero.ne D)
  have hd1 : (1 : ℝ) ≤ D := by exact_mod_cast Nat.pos_of_ne_zero (NeZero.ne D)
  have ha : 0 ≤ π/(2*(D:ℝ)) := by positivity
  have hp : π/(2*(D:ℝ)) ≤ π := by
    apply (div_le_iff₀ (by positivity)).2
    nlinarith [mul_le_mul_of_nonneg_left hd1 Real.pi_nonneg, Real.pi_pos]
  have h := abs_sin_nat_mul (π/(2*(D:ℝ))) D
  rw [show (D:ℝ)*(π/(2*D)) = π/2 by field_simp, Real.sin_pi_div_two, abs_one,
    abs_of_nonneg (Real.sin_nonneg_of_nonneg_of_le_pi ha hp)] at h
  rwa [inv_eq_one_div, div_le_iff₀ hd, mul_comm]

theorem mid_real (hD : Even D) (z : ZMod D) : (D : ℝ)⁻¹ ≤ (midRoot z).re := by
  have hd : (0 : ℝ) < D := by exact_mod_cast Nat.pos_of_ne_zero (NeZero.ne D)
  obtain ⟨hl,hu⟩ := index_gap hD z
  have hl' : -(D : ℝ)+1 ≤ (midIndex z).valMinAbs := by exact_mod_cast hl
  have hu' : ((midIndex z).valMinAbs:ℝ) ≤ (D:ℝ)-1 := by exact_mod_cast hu
  have hc : |midAngle z| ≤ π/2 - π/(2*(D:ℝ)) := by
    have e : π/2 - π/(2*(D:ℝ)) = π*((D:ℝ)-1)/(2*D) := by field_simp
    rw [e, midAngle, abs_div, abs_of_pos (show 0 < 2*(D:ℝ) by positivity)]
    apply div_le_div_of_nonneg_right _ (by positivity)
    rw [abs_mul, abs_of_pos Real.pi_pos]
    exact mul_le_mul_of_nonneg_left (abs_le.mpr ⟨by linarith, hu'⟩) Real.pi_nonneg
  have h := Real.cos_le_cos_of_nonneg_of_le_pi (abs_nonneg (midAngle z))
    (show π/2 - π/(2*(D:ℝ)) ≤ π by linarith [div_nonneg Real.pi_nonneg (show 0 ≤ 2*(D:ℝ) by positivity),Real.pi_pos]) hc
  rw [Real.cos_abs, Real.cos_pi_div_two_sub] at h
  exact sine_gap.trans (by simpa only [midRoot, Complex.exp_ofReal_mul_I_re] using h)

variable {N : ℕ} [NeZero N]

noncomputable def quadRoot (j : ZMod N) : ℂ := midRoot (-quadLabel j)

theorem quadRoot_square (j : ZMod N) :
    quadRoot j ^ 2 = midScalar (2*N) * quadDiag j := by
  rw [quadRoot, mid_square, char_neg]
  rfl

theorem quadRoot_real (j : ZMod N) : ((2:ℝ)*N)⁻¹ ≤ (quadRoot j).re := by
  have he : Even (2*N) := ⟨N, by omega⟩
  simpa only [Nat.cast_mul, Nat.cast_ofNat, quadRoot] using mid_real he (-quadLabel j)

theorem two_stage_mean (x : Signal N) (k : ZMod N) :
    ZMod.dft x k / (N : ℂ) =
      ((∑ j : ZMod N, quadChirp j) / ((N : ℂ) * midScalar (2*N))) * quadDiag k *
        (multiplier quadRoot)^[2] (fun j ↦ quadDiag j * x j) k := by
  rw [all_mean, multiplier_iterate]
  simp_rw [quadRoot_square]
  rw [multiplier_scalar]
  have h : midScalar (2*N) ≠ 0 := norm_ne_zero_iff.mp (by rw [scalar_unit]; norm_num)
  field_simp

/-- The gain bound uses the rounded column on every section and includes the
cost in accuracy of all entries of each row. -/
theorem two_stage_section (L : Finset (ZMod N)) (h x : Signal N)
    (hh : ∀ j, ‖h j - (ZMod.dft (N := N)).symm quadRoot j‖ ≤ (4*(N:ℝ)^2)⁻¹)
    (hx : ∀ j ∉ L, x j = 0) :
    ((4*(N:ℝ))⁻¹)^2 * energy x ≤ ∑ j ∈ L, ‖convolution h x j‖^2 := by
  have hz : (0:ℝ) < N := by exact_mod_cast Nat.pos_of_ne_zero (NeZero.ne N)
  have diff : ((2:ℝ)*N)⁻¹ - (N:ℝ)*(4*(N:ℝ)^2)⁻¹ = (4*(N:ℝ))⁻¹ := by
    field_simp
    ring
  rw [← diff]
  apply accretive_section L quadRoot h x (by positivity) _ quadRoot_real hh hx
  linarith [show (0:ℝ) ≤ (4*(N:ℝ))⁻¹ by positivity]

end CirculantRoot

#print axioms CirculantRoot.quad_dft
#print axioms CirculantRoot.all_gauss_norm_sq
#print axioms CirculantRoot.mid_square
#print axioms CirculantRoot.quadRoot_real
#print axioms CirculantRoot.two_stage_mean
#print axioms CirculantRoot.two_stage_section
