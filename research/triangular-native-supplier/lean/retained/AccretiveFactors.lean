import CirculantOperators
import Mathlib.Algebra.BigOperators.Intervals

/-!
Each nonzero symbol of a cyclic convolution has two identical factors after
one common scalar rotation. The same finite rotation list applies to every
spectrum of a given size. A positive real-part bound controls the gain of
every principal section after entrywise changes to its first column.
-/

namespace CirculantRoot

open Finset AddChar
open scoped BigOperators ComplexConjugate Real

variable {N : ℕ} [NeZero N]

noncomputable def realPair (x y : Signal N) : ℝ := (∑ j, conj (x j) * y j).re

theorem spectral_realPair (s x : Signal N) :
    (N : ℝ) * realPair x (multiplier s x) =
      ∑ j, ‖ZMod.dft x j‖ ^ 2 * (s j).re := by
  have h := (pair_fourier x (fun j ↦ s j * ZMod.dft x j)).symm
  have ht (v u : ℂ) : (conj v * (u*v)).re = ‖v‖^2 * u.re := by
    rw [show conj v * (u*v) = (v*conj v)*u by ring, Complex.mul_conj,
      ← Complex.sq_norm]
    rw [Complex.mul_re, Complex.ofReal_re, Complex.ofReal_im, zero_mul, sub_zero]
  simpa [realPair, multiplier, ht] using congrArg Complex.re h

theorem accretive (s x : Signal N) {c : ℝ} (hs : ∀ j, c ≤ (s j).re) :
    c * energy x ≤ realPair x (multiplier s x) := by
  have h : c * energy (ZMod.dft x) ≤ ∑ j, ‖ZMod.dft x j‖^2 * (s j).re := by
    unfold energy
    rw [Finset.mul_sum]
    apply Finset.sum_le_sum
    intro j _
    rw [mul_comm c]
    exact mul_le_mul_of_nonneg_left (hs j) (sq_nonneg _)
  rw [fourier_energy, ← spectral_realPair, mul_left_comm] at h
  exact le_of_mul_le_mul_left h (show (0 : ℝ) < N by exact_mod_cast Nat.pos_of_ne_zero (NeZero.ne N))

omit [NeZero N] in
theorem pair_cs (L : Finset (ZMod N)) (x y : Signal N) :
    ((∑ j ∈ L, conj (x j) * y j).re) ^ 2 ≤ (∑ j ∈ L, ‖x j‖ ^ 2) * ∑ j ∈ L, ‖y j‖^2 := by
  have ht : |(∑ j ∈ L, conj (x j) * y j).re| ≤ ∑ j ∈ L, ‖x j‖ * ‖y j‖ := by
    apply (Complex.abs_re_le_norm _).trans
    simpa only [norm_mul, Complex.norm_conj] using norm_sum_le L (fun j ↦ conj (x j) * y j)
  calc
    ((∑ j ∈ L, conj (x j) * y j).re)^2 = |(∑ j ∈ L, conj (x j) * y j).re|^2 := (sq_abs _).symm
    _ ≤ (∑ j ∈ L, ‖x j‖ * ‖y j‖)^2 := pow_le_pow_left₀ (abs_nonneg _) ht 2
    _ ≤ _ := Finset.sum_mul_sq_le_sq_mul_sq L (fun j ↦ ‖x j‖) (fun j ↦ ‖y j‖)

theorem rounded_accretive (s h x : Signal N) {c η : ℝ} (hη : 0 ≤ η)
    (hs : ∀ j, c ≤ (s j).re)
    (hh : ∀ j, ‖h j - (ZMod.dft (N := N)).symm s j‖ ≤ η) :
    (c - (N:ℝ)*η) * energy x ≤ realPair x (convolution h x) := by
  let err : Signal N := h - (ZMod.dft (N := N)).symm s
  have hnorm := convolution_energy err x hh
  have hc := pair_cs Finset.univ x (convolution err x)
  change (realPair x (convolution err x))^2 ≤ energy x * energy (convolution err x) at hc
  have bound : -(N:ℝ)*η*energy x ≤ realPair x (convolution err x) := by
    have this := hc.trans (mul_le_mul_of_nonneg_left hnorm (energy_nonneg x))
    have hn : 0 ≤ (N:ℝ)*η*energy x := by positivity [energy_nonneg x]
    nlinarith [sq_nonneg (realPair x (convolution err x) + (N:ℝ)*η*energy x)]
  have eq : realPair x (convolution h x) = realPair x (convolution err x) + realPair x (multiplier s x) := by
    have split : convolution h x = convolution err x + multiplier s x := by
      rw [multiplier_is_circulant]
      ext i
      simp [err, convolution, sub_mul, Finset.sum_sub_distrib]
    rw [split]
    simp [realPair, mul_add, Finset.sum_add_distrib]
  rw [eq]
  linarith [accretive s x hs]

/-- The section can be any subset of the physical index set. -/
theorem accretive_section (L : Finset (ZMod N)) (s h x : Signal N) {c η : ℝ}
    (hη : 0 ≤ η) (hmargin : (N:ℝ)*η ≤ c) (hs : ∀ j, c ≤ (s j).re)
    (hh : ∀ j, ‖h j - (ZMod.dft (N := N)).symm s j‖ ≤ η)
    (hx : ∀ j ∉ L, x j = 0) :
    (c - (N:ℝ)*η)^2 * energy x ≤ ∑ j ∈ L, ‖convolution h x j‖ ^ 2 := by
  let y := convolution h x
  have hpair : (∑ j ∈ L, conj (x j) * y j) = ∑ j, conj (x j) * y j := by
    apply Finset.sum_subset (Finset.subset_univ L)
    intro j _ hj
    simp [hx j hj]
  have hen : (∑ j ∈ L, ‖x j‖ ^ 2) = energy x := by
    apply Finset.sum_subset (Finset.subset_univ L)
    intro j _ hj
    simp [hx j hj]
  have hcs := pair_cs L x y
  rw [hpair, hen] at hcs
  have hlow := rounded_accretive s h x hη hs hh
  change (c-(N:ℝ)*η)*energy x ≤ realPair x y at hlow
  change (realPair x y)^2 ≤ energy x * _ at hcs
  have hg : 0 ≤ (c-(N:ℝ)*η)*energy x := mul_nonneg (sub_nonneg.mpr hmargin) (energy_nonneg x)
  have hmain := (pow_le_pow_left₀ hg hlow 2).trans hcs
  by_cases hpos : 0 < energy x
  · apply le_of_mul_le_mul_left (a := energy x) _ hpos
    simpa [mul_pow, pow_two, mul_assoc, mul_left_comm, mul_comm] using hmain
  · have he : energy x = 0 := by linarith [energy_nonneg x]
    rw [he, mul_zero]
    exact Finset.sum_nonneg fun _ _ ↦ sq_nonneg _

theorem pow_chord (w : ℂ) (hu : ‖w‖ = 1) (k : ℕ) :
    ‖w^k-1‖ ≤ k * ‖w-1‖ := by
  induction k with
  | zero => simp
  | succ k ih =>
    rw [pow_succ, show w^k*w - 1 = (w^k-1)*w + (w-1) by ring]
    refine (norm_add_le ..).trans ?_
    rw [norm_mul, hu, mul_one, Nat.cast_succ, add_mul, one_mul]
    linarith

/-- A geometric sum bounds the distance between any two distinct grid rotations. -/
theorem root_separation {w : ℂ} (hn : w^(N+1) = 1) (h1 : w ≠ 1) :
    2/(N:ℝ) ≤ ‖w-1‖ := by
  have hnpos : (0:ℝ) < N := by exact_mod_cast Nat.pos_of_ne_zero (NeZero.ne N)
  have hu := Complex.norm_eq_one_of_pow_eq_one hn (by omega)
  have hz : (∑ i ∈ Finset.range (N+1), w^i) = 0 := by
    have h := geom_sum_mul w (N+1)
    rw [hn, sub_self] at h
    exact (mul_eq_zero.mp h).resolve_right (sub_ne_zero.mpr h1)
  have hs : (∑ i ∈ Finset.range (N+1), (w^i-1)) = -((N:ℂ)+1) := by
    simp [Finset.sum_sub_distrib, hz]
  have hsum : ((∑ i ∈ Finset.range (N+1), (i:ℝ)) * 2) = ((N:ℝ)+1)*N := by
    rw [← Nat.cast_sum]
    exact_mod_cast (show (∑ i ∈ Finset.range (N+1), i)*2 = (N+1)*N by
      simpa only [Nat.add_sub_cancel] using Finset.sum_range_id_mul_two (N+1))
  have he := norm_sum_le (Finset.range (N+1)) (fun i ↦ w^i-1)
  rw [hs, norm_neg, show ‖(N:ℂ)+1‖ = (N:ℝ)+1 by
    rw [← Complex.ofReal_natCast, ← Complex.ofReal_one, ← Complex.ofReal_add, Complex.norm_real,
      Real.norm_eq_abs, abs_of_nonneg (show 0 ≤ (N:ℝ)+1 by positivity)]] at he
  have hp := Finset.sum_le_sum (s := Finset.range (N+1)) (fun i _ ↦ pow_chord w hu i)
  rw [← Finset.sum_mul] at hp
  apply (div_le_iff₀ hnpos).mpr
  have h : ((N:ℝ)+1)*2 ≤ ((N:ℝ)+1) * (‖w-1‖ * N) := by
    calc
      ((N:ℝ)+1)*2 ≤ ((∑ i ∈ Finset.range (N+1), (i:ℝ)) * ‖w-1‖) * 2 := by linarith
      _ = ((N:ℝ)+1) * (‖w-1‖ * N) := by linear_combination ‖w-1‖ * hsum
  exact le_of_mul_le_mul_left h (by positivity)

theorem grid_separation {a b : ZMod (N+1)} (hab : a ≠ b) :
    2/(N:ℝ) ≤ ‖ZMod.stdAddChar a - ZMod.stdAddChar b‖ := by
  let w := ZMod.stdAddChar (a-b)
  have hw : w^(N+1) = 1 := by
    rw [show w^(N+1) = ZMod.stdAddChar ((N+1) • (a-b)) by rw [AddChar.map_nsmul_eq_pow]]
    simp only [nsmul_eq_mul, ZMod.natCast_self, zero_mul, AddChar.map_zero_eq_one]
  have h1 : w ≠ 1 := by
    rw [show (1:ℂ) = ZMod.stdAddChar (0 : ZMod (N+1)) by simp, Ne, ZMod.injective_stdAddChar.eq_iff]
    exact sub_ne_zero.mpr hab
  have hc : w * ZMod.stdAddChar b = ZMod.stdAddChar a := by
    rw [show w = ZMod.stdAddChar (a-b) by rfl, ← AddChar.map_add_eq_mul, sub_add_cancel]
  have hu : ‖ZMod.stdAddChar b‖ = 1 := by simp [ZMod.stdAddChar_apply]
  calc
    _ ≤ ‖w-1‖ := root_separation hw h1
    _ = ‖(w-1)*ZMod.stdAddChar b‖ := by rw [norm_mul, hu, mul_one]
    _ = _ := by rw [sub_mul, hc, one_mul]

/-- Each data point excludes at most one grid rotation. -/
theorem finite_rotation (t : Signal N) :
    ∃ a : ZMod (N+1), ∀ j, (N:ℝ)⁻¹ ≤ ‖ZMod.stdAddChar a + t j‖ := by
  classical
  by_contra! hn
  choose f hf using hn
  have hi : Function.Injective f := by
    intro a b hab
    by_contra hne
    have hs := grid_separation hne
    have hb := hf b
    rw [← hab] at hb
    have ht := norm_sub_le (ZMod.stdAddChar a + t (f a)) (ZMod.stdAddChar b + t (f a))
    rw [show (ZMod.stdAddChar a + t (f a)) - (ZMod.stdAddChar b + t (f a)) =
        ZMod.stdAddChar a - ZMod.stdAddChar b by abel] at ht
    rw [div_eq_mul_inv] at hs
    linarith [hf a]
  have hc := Fintype.card_le_of_injective f hi
  simp [ZMod.card] at hc

noncomputable def midpointUnit (w : ℂ) : ℂ := (1+w) / ↑‖1+w‖

theorem unit_midpoint_square (w : ℂ) (hu : ‖w‖ = 1) (hp : 0 < ‖1+w‖) :
    midpointUnit w ^ 2 = w := by
  have hc : w*conj w = 1 := by rw [Complex.mul_conj, ← Complex.sq_norm, hu]; norm_num
  have ha : (↑‖1+w‖ : ℂ) ^ 2 = (1+w) * (1+conj w) := by
    rw [← Complex.ofReal_pow, Complex.sq_norm, ← Complex.mul_conj, map_add, map_one]
  unfold midpointUnit
  rw [div_pow, div_eq_iff (pow_ne_zero _ (Complex.ofReal_ne_zero.mpr hp.ne'))]
  rw [ha]
  linear_combination -(1+w) * hc

theorem unit_midpoint_real (w : ℂ) (hu : ‖w‖ = 1) (hp : 0 < ‖1+w‖) :
    (midpointUnit w).re = ‖1+w‖ / 2 := by
  have hw : w.re*w.re + w.im*w.im = 1 := by rw [← Complex.normSq_apply, ← Complex.sq_norm, hu]; norm_num
  have hd : ‖1+w‖^2 = (1+w).re*2 := by
    rw [Complex.sq_norm, Complex.normSq_apply]
    simp only [Complex.add_re, Complex.one_re, Complex.add_im, Complex.one_im, zero_add]
    nlinarith
  rw [midpointUnit, Complex.div_ofReal_re, div_eq_iff hp.ne']
  linarith

theorem unit_midpoint_norm (w : ℂ) (hp : 0 < ‖1+w‖) : ‖midpointUnit w‖ = 1 := by
  simp [midpointUnit, hp.ne']

noncomputable def unitPart (z : ℂ) : ℂ := z / ↑‖z‖

theorem unitPart_norm (z : ℂ) (h : z ≠ 0) : ‖unitPart z‖ = 1 := by
  simp [unitPart, h]

noncomputable def generalRoot (τ z : ℂ) : ℂ :=
  ↑(√‖z‖) * midpointUnit (τ * unitPart z)

/-- One finite search selects a common rotation. The identical two
circulants have a positive real-part margin on the full frequency list. -/
theorem two_factor_symbol (s : Signal N) (hs : ∀ j, s j ≠ 0) :
    ∃ a : ZMod (N+1), let τ := ZMod.stdAddChar a
      ∀ j, (generalRoot τ (s j))^2 = τ * s j ∧
        √‖s j‖ / (2*(N:ℝ)) ≤ (generalRoot τ (s j)).re ∧
        ‖generalRoot τ (s j)‖ = √‖s j‖ := by
  obtain ⟨a, ha⟩ := finite_rotation (fun j ↦ conj (unitPart (s j)))
  refine ⟨a, ?_⟩
  dsimp only
  intro j
  let τ := ZMod.stdAddChar a
  let u := unitPart (s j)
  have hu : ‖u‖ = 1 := unitPart_norm _ (hs j)
  have ht : ‖τ‖ = 1 := by simp [τ, ZMod.stdAddChar_apply]
  have hr : ‖τ*u‖ = 1 := by rw [norm_mul, ht, hu, mul_one]
  have huid : conj u*u = 1 := by rw [mul_comm, Complex.mul_conj, ← Complex.sq_norm, hu]; norm_num
  have hgap : (N:ℝ)⁻¹ ≤ ‖1+τ*u‖ := by
    calc
      _ ≤ ‖τ+conj u‖ := ha j
      _ = ‖(τ+conj u)*u‖ := by rw [norm_mul, hu, mul_one]
      _ = _ := by rw [add_mul, huid, add_comm]
  have hnpos : (0:ℝ) < N := by exact_mod_cast Nat.pos_of_ne_zero (NeZero.ne N)
  have hd : 0 < ‖1+τ*u‖ := lt_of_lt_of_le (inv_pos.mpr hnpos) hgap
  have hz : ‖s j‖ ≠ 0 := norm_ne_zero_iff.mpr (hs j)
  change (↑√‖s j‖ * midpointUnit (τ*u))^2 = τ * s j ∧
    _ ≤ (↑√‖s j‖ * midpointUnit (τ*u)).re ∧ ‖↑√‖s j‖ * midpointUnit (τ*u)‖ = _
  refine ⟨?_, ?_, ?_⟩
  · rw [mul_pow, unit_midpoint_square _ hr hd, ← Complex.ofReal_pow, Real.sq_sqrt (norm_nonneg _)]
    change ↑‖s j‖ * (τ * (s j / ↑‖s j‖)) = _
    field_simp [Complex.ofReal_ne_zero.mpr hz]
  · rw [Complex.mul_re, Complex.ofReal_im, Complex.ofReal_re, zero_mul, sub_zero, unit_midpoint_real _ hr hd]
    have hg := mul_le_mul_of_nonneg_left hgap (Real.sqrt_nonneg ‖s j‖)
    rw [div_eq_mul_inv, mul_inv, mul_comm (2:ℝ)⁻¹]
    linarith
  · rw [norm_mul, unit_midpoint_norm _ hd, mul_one, Complex.norm_real, Real.norm_eq_abs,
      abs_of_nonneg (Real.sqrt_nonneg _)]

theorem two_circulants (s : Signal N) (hs : ∀ j, s j ≠ 0) :
    ∃ a : ZMod (N+1), let τ := ZMod.stdAddChar a
      let t : Signal N := fun j ↦ generalRoot τ (s j)
      (∀ x : Signal N, (multiplier t)^[2] x = fun k ↦ τ * multiplier s x k) ∧
      (∀ j, √‖s j‖ / (2*(N:ℝ)) ≤ (t j).re ∧ ‖t j‖ = √‖s j‖) := by
  obtain ⟨a, ha⟩ := two_factor_symbol s hs
  refine ⟨a, ?_, fun j ↦ (ha j).2⟩
  intro x
  rw [multiplier_iterate]
  simp_rw [(ha _).1]
  exact multiplier_scalar _ _ _

/-- The live entries occupy the first N positions. All trailing entries have
the identity action, including entries whose initial values are nonzero. -/
def padEntry (h : Signal N) (i j : ℕ) : ℂ :=
  if i < N ∧ j < N then h ((i : ZMod N)-(j : ZMod N)) else if i = j then 1 else 0

def lowerShift (A : ℕ → ℕ → ℂ) : ℕ → ℕ → ℂ
  | i+1, j+1 => A i j
  | _, _ => 0

def stein (A : ℕ → ℕ → ℂ) (i j : ℕ) : ℂ := A i j - lowerShift A i j

omit [NeZero N] in
theorem stein_interior (h : Signal N) {i j : ℕ}
    (hi : i ≠ 0) (hj : j ≠ 0) (hiN : i ≠ N) (hjN : j ≠ N) :
    stein (padEntry h) i j = 0 := by
  obtain ⟨k, rfl⟩ := Nat.exists_eq_succ_of_ne_zero hi
  obtain ⟨m, rfl⟩ := Nat.exists_eq_succ_of_ne_zero hj
  have hk : k+1 < N ↔ k < N := by omega
  have hm : m+1 < N ↔ m < N := by omega
  simp [stein, lowerShift, padEntry, hk, hm]

def impulse (a i : ℕ) : ℂ := if i = a then 1 else 0

/-- This is a factorization into four outer products. It holds after
truncation to any physical square that contains the N live positions. -/
theorem padded_four_generators (h : Signal N) (i j : ℕ) :
    let Δ := stein (padEntry h)
    let row (a : ℕ) := fun j ↦ Δ a j
    let col (a : ℕ) := fun i ↦ if i = 0 ∨ i = N then 0 else Δ i a
    Δ i j = impulse 0 i * row 0 j + impulse N i * row N j +
      col 0 i * impulse 0 j + col N i * impulse N j := by
  dsimp only
  have hn : N ≠ 0 := NeZero.ne N
  rcases eq_or_ne i 0 with rfl | hi
  · simp [impulse, Ne.symm hn]
  rcases eq_or_ne i N with rfl | hiN
  · simp [impulse, hn]
  rcases eq_or_ne j 0 with rfl | hj
  · simp [impulse, hi, hiN, Ne.symm hn]
  rcases eq_or_ne j N with rfl | hjN
  · simp [impulse, hi, hiN, hn]
  simp [impulse, hi, hiN, hj, hjN, stein_interior h hi hj hiN hjN]

variable {ι : Type*} [Fintype ι] [DecidableEq ι]

noncomputable def paddedApply (h : Signal N) (x : ZMod N ⊕ ι → ℂ) : ZMod N ⊕ ι → ℂ :=
  Sum.elim (convolution h (fun j ↦ x (.inl j))) (fun t ↦ x (.inr t))

theorem padded_accretive_section (L : Finset (ZMod N ⊕ ι)) (s h : Signal N)
    (x : ZMod N ⊕ ι → ℂ) {c η : ℝ} (hη : 0 ≤ η) (hmargin : (N:ℝ)*η ≤ c)
    (hcap : c - (N:ℝ)*η ≤ 1) (hs : ∀ j, c ≤ (s j).re)
    (hh : ∀ j, ‖h j - (ZMod.dft (N := N)).symm s j‖ ≤ η) (hx : ∀ j ∉ L, x j = 0) :
    (c-(N:ℝ)*η)^2 * (∑ j, ‖x j‖^2) ≤ ∑ j ∈ L, ‖paddedApply h x j‖^2 := by
  classical
  let K : Finset (ZMod N) := Finset.univ.filter fun j ↦ Sum.inl j ∈ L
  have hl := accretive_section K s h (fun j ↦ x (.inl j)) hη hmargin hs hh
    (fun j hj ↦ hx _ (by simpa [K] using hj))
  change (c-(N:ℝ)*η)^2 * (∑ j, ‖x (.inl j)‖^2) ≤ _ at hl
  have hg : (c-(N:ℝ)*η)^2 ≤ 1 := by nlinarith [sub_nonneg.mpr hmargin, sq_nonneg (c-(N:ℝ)*η-1)]
  have hr : (c-(N:ℝ)*η)^2 * (∑ t : ι, ‖x (.inr t)‖^2) ≤
      ∑ t : ι, if Sum.inr t ∈ L then ‖x (.inr t)‖^2 else 0 := by
    rw [Finset.mul_sum]
    apply Finset.sum_le_sum
    intro t _
    split_ifs with ht
    · simpa only [one_mul] using mul_le_mul_of_nonneg_right hg (sq_nonneg ‖x (.inr t)‖)
    · simp [hx _ ht]
  have hrewrite : (∑ j ∈ L, ‖paddedApply h x j‖^2) =
      ∑ j, if j ∈ L then ‖paddedApply h x j‖^2 else 0 := by simp
  rw [hrewrite, Fintype.sum_sum_type, Fintype.sum_sum_type, mul_add]
  apply add_le_add _ hr
  simpa only [K, Finset.sum_filter, paddedApply, Sum.elim_inl] using hl

end CirculantRoot

#print axioms CirculantRoot.two_factor_symbol
#print axioms CirculantRoot.two_circulants
#print axioms CirculantRoot.accretive_section
#print axioms CirculantRoot.padded_four_generators
#print axioms CirculantRoot.padded_accretive_section
