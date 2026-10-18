import Mathlib.Analysis.Convex.SpecificFunctions.Pow
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum

/-! Sufficient certificate transfer for finite paid-rank profiles.
The analytic cost is an arbitrary real weight until the concentration section,
where it is proved for real powers with exponent in [0,1]. -/

namespace IntegerMultBounds.MomentTransfer

open scoped BigOperators

variable {ι : Type*}

noncomputable def weighted (s : Finset ι) (c w : ι → ℝ) : ℝ :=
  ∑ i ∈ s, c i * w i

theorem weighted_zero (s : Finset ι) (w : ι → ℝ) : weighted s (fun _ => 0) w = 0 := by
  simp [weighted]

theorem weighted_add (s : Finset ι) (a b w : ι → ℝ) :
    weighted s (fun i => a i + b i) w = weighted s a w + weighted s b w := by
  simp [weighted, add_mul, Finset.sum_add_distrib]

theorem weighted_sub (s : Finset ι) (a b w : ι → ℝ) :
    weighted s (fun i => a i - b i) w = weighted s a w - weighted s b w := by
  simp [weighted, sub_mul, Finset.sum_sub_distrib]

theorem weighted_scale (s : Finset ι) (a w : ι → ℝ) (k : ℝ) :
    weighted s (fun i => k * a i) w = k * weighted s a w := by
  simp [weighted, mul_assoc, Finset.mul_sum]

theorem weighted_nonneg (s : Finset ι) (c w : ι → ℝ)
    (hc : ∀ i ∈ s, 0 ≤ c i) (hw : ∀ i ∈ s, 0 ≤ w i) :
    0 ≤ weighted s c w := by
  exact Finset.sum_nonneg fun i hi => mul_nonneg (hc i hi) (hw i hi)

theorem weighted_mono_counts (s : Finset ι) (a b w : ι → ℝ)
    (hab : ∀ i ∈ s, a i ≤ b i) (hw : ∀ i ∈ s, 0 ≤ w i) :
    weighted s a w ≤ weighted s b w := by
  exact Finset.sum_le_sum fun i hi => mul_le_mul_of_nonneg_right (hab i hi) (hw i hi)

theorem weighted_mono_weights (s : Finset ι) (c u v : ι → ℝ)
    (hc : ∀ i ∈ s, 0 ≤ c i) (huv : ∀ i ∈ s, u i ≤ v i) :
    weighted s c u ≤ weighted s c v := by
  exact Finset.sum_le_sum fun i hi => mul_le_mul_of_nonneg_left (huv i hi) (hc i hi)

/-- Remove a paid subprofile and insert another; the identity is exact. -/
theorem replacement_identity (s : Finset ι) (old removed added w : ι → ℝ) :
    weighted s (fun i => old i - removed i + added i) w =
      weighted s old w - weighted s removed w + weighted s added w := by
  rw [weighted_add, weighted_sub]

theorem replacement_nonneg (s : Finset ι) (old removed added : ι → ℝ)
    (hremove : ∀ i ∈ s, removed i ≤ old i) (hadd : ∀ i ∈ s, 0 ≤ added i) :
    ∀ i ∈ s, 0 ≤ old i - removed i + added i := by
  intro i hi
  exact add_nonneg (sub_nonneg.mpr (hremove i hi)) (hadd i hi)

theorem admission_of_replacement (s : Finset ι) (old removed added w : ι → ℝ)
    (budget : ℝ) (hold : weighted s old w < budget)
    (hmove : weighted s added w ≤ weighted s removed w) :
    weighted s (fun i => old i - removed i + added i) w < budget := by
  rw [replacement_identity]
  linarith

/-- A move's saving may pay a genuinely positive new reserve. -/
theorem admission_with_reserve (s : Finset ι) (old removed added w : ι → ℝ)
    (budget reserve margin saving : ℝ)
    (hold : weighted s old w ≤ budget - margin)
    (hmove : weighted s added w ≤ weighted s removed w - saving)
    (hreserve : reserve < margin + saving) :
    weighted s (fun i => old i - removed i + added i) w + reserve < budget := by
  rw [replacement_identity]
  linarith

/-- Equal removed/added stock or mass is inherited by the new profile. -/
theorem conserved_weight_of_replacement (s : Finset ι) (old removed added w : ι → ℝ)
    (hmove : weighted s added w = weighted s removed w) :
    weighted s (fun i => old i - removed i + added i) w = weighted s old w := by
  rw [replacement_identity, hmove]
  ring

theorem deficit_preserved (s : Finset ι) (old removed added rank : ι → ℝ)
    (capacity : ℝ) (hmass : weighted s added rank = weighted s removed rank) :
    capacity - weighted s (fun i => old i - removed i + added i) rank =
      capacity - weighted s old rank := by
  rw [conserved_weight_of_replacement s old removed added rank hmass]

/-- Soundness of finite rational upper bounds for arbitrary real costs. -/
theorem rational_upper_certificate (s : Finset ι) (c upper : ι → ℚ) (w : ι → ℝ)
    (budget : ℚ) (hc : ∀ i ∈ s, 0 ≤ c i)
    (hupper : ∀ i ∈ s, w i ≤ (upper i : ℝ))
    (hcertificate : (∑ i ∈ s, c i * upper i) < budget) :
    weighted s (fun i => (c i : ℝ)) w < (budget : ℝ) := by
  have h := weighted_mono_weights s (fun i => (c i : ℝ)) w (fun i => (upper i : ℝ))
    (fun i hi => by exact_mod_cast hc i hi) hupper
  have hcast : weighted s (fun i => (c i : ℝ)) (fun i => (upper i : ℝ)) < (budget : ℝ) := by
    change (∑ i ∈ s, (c i : ℝ) * (upper i : ℝ)) < (budget : ℝ)
    exact_mod_cast hcertificate
  exact h.trans_lt hcast

/-- Dividing by a positive budget connects paid sums to moment < 1. -/
theorem normalized_admission (cost budget : ℝ) (hbudget : 0 < budget) :
    cost / budget < 1 ↔ cost < budget := by
  rw [div_lt_one hbudget]

/-- A concave cost decreases when two bins are mixed towards the endpoints. -/
theorem concave_pair_mix (f : ℝ → ℝ) (hf : ConcaveOn ℝ (Set.Ici 0) f)
    (x y a b : ℝ) (hx : 0 ≤ x) (hy : 0 ≤ y)
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hab : a + b = 1) :
    f x + f y ≤ f (a*x + b*y) + f (b*x + a*y) := by
  have h₁ := hf.2 hx hy ha hb hab
  have h₂ := hf.2 hx hy hb ha (by linarith : b + a = 1)
  simp only [smul_eq_mul] at h₁ h₂
  have heq : (a*f x+b*f y)+(b*f x+a*f y)=f x+f y := by
    calc
      _ = (a+b)*(f x+f y) := by ring
      _ = _ := by rw [hab]; ring
  linarith

/-- Reverse Robin Hood exchange: move rank from the smaller bin to the larger. -/
theorem concave_concentration (f : ℝ → ℝ) (hf : ConcaveOn ℝ (Set.Ici 0) f)
    (x y d : ℝ) (hd : 0 ≤ d) (hdx : d ≤ x) (hxy : x ≤ y) :
    f (x-d) + f (y+d) ≤ f x + f y := by
  by_cases hzero : d = 0
  · simp [hzero]
  have hdpos : 0 < d := lt_of_le_of_ne hd (Ne.symm hzero)
  have hden : 0 < y-x+2*d := by linarith
  let a := (y-x+d)/(y-x+2*d)
  let b := d/(y-x+2*d)
  have ha : 0 ≤ a := div_nonneg (by linarith) hden.le
  have hb : 0 ≤ b := div_nonneg hd hden.le
  have hab : a+b=1 := by
    dsimp [a,b]
    rw [← add_div]
    rw [show (y-x+d)+d=y-x+2*d by ring]
    exact div_self (ne_of_gt hden)
  have hx : 0 ≤ x-d := by linarith
  have hy : 0 ≤ y+d := by linarith
  have h := concave_pair_mix f hf (x-d) (y+d) a b hx hy ha hb hab
  have e₁ : a*(x-d)+b*(y+d)=x := by
    dsimp [a,b]
    calc
      _ = ((y-x+d)*(x-d)+d*(y+d))/(y-x+2*d) := by ring
      _ = x := (div_eq_iff (ne_of_gt hden)).2 (by ring)
  have e₂ : b*(x-d)+a*(y+d)=y := by
    dsimp [a,b]
    calc
      _ = (d*(x-d)+(y-x+d)*(y+d))/(y-x+2*d) := by ring
      _ = y := (div_eq_iff (ne_of_gt hden)).2 (by ring)
  simpa only [e₁,e₂] using h

theorem rpow_concentration (p x y d : ℝ) (hp : 0 ≤ p) (hp1 : p ≤ 1)
    (hd : 0 ≤ d) (hdx : d ≤ x) (hxy : x ≤ y) :
    (x-d)^p + (y+d)^p ≤ x^p + y^p :=
  concave_concentration (fun t : ℝ => t^p) (Real.concaveOn_rpow hp hp1) x y d hd hdx hxy

/-- The physical rank mass of this two-bin move is unchanged. -/
theorem concentration_rank_mass (x y d : ℝ) : (x-d)+(y+d)=x+y := by ring

/-- The same move preserves unused rank capacity, for any fixed stock. -/
theorem concentration_rank_deficit (capacity x y d : ℝ) :
    capacity-((x-d)+(y+d))=capacity-(x+y) := by ring

/-- Pair concentration is already a sufficient admission-preserving compiler rule. -/
theorem admission_of_concentration (p x y d rest budget : ℝ)
    (hp : 0 ≤ p) (hp1 : p ≤ 1) (hd : 0 ≤ d) (hdx : d ≤ x) (hxy : x ≤ y)
    (hold : rest+x^p+y^p < budget) :
    rest+(x-d)^p+(y+d)^p < budget := by
  have h := rpow_concentration p x y d hp hp1 hd hdx hxy
  linarith

/-- Uniform scaling preserves a profitable exchange, including cover normalizers. -/
theorem scaled_rpow_concentration (p x y d factor : ℝ)
    (hp : 0 ≤ p) (hp1 : p ≤ 1) (hd : 0 ≤ d) (hdx : d ≤ x) (hxy : x ≤ y)
    (hfactor : 0 ≤ factor) :
    factor*((x-d)^p+(y+d)^p) ≤ factor*(x^p+y^p) :=
  mul_le_mul_of_nonneg_left (rpow_concentration p x y d hp hp1 hd hdx hxy) hfactor

/-- The cost comparison in the project's normalized rank coordinates. -/
theorem normalized_rpow_concentration (p x y d dimension : ℝ)
    (hp : 0 ≤ p) (hp1 : p ≤ 1) (hd : 0 ≤ d) (hdx : d ≤ x) (hxy : x ≤ y)
    (hm : 0 < dimension) :
    ((x-d)/dimension)^p+((y+d)/dimension)^p ≤
      (x/dimension)^p+(y/dimension)^p := by
  have h := rpow_concentration p (x/dimension) (y/dimension) (d/dimension)
    hp hp1 (div_nonneg hd hm.le) (div_le_div_of_nonneg_right hdx hm.le)
    (div_le_div_of_nonneg_right hxy hm.le)
  simpa only [sub_div,add_div] using h

/-- Any finite batch is sound from the individually checkable move contracts. -/
theorem batch_rpow_concentration (s : Finset ι) (p : ℝ) (a b d : ι → ℝ)
    (hp : 0 ≤ p) (hp1 : p ≤ 1) (hd : ∀ i ∈ s, 0 ≤ d i)
    (hda : ∀ i ∈ s, d i ≤ a i) (hab : ∀ i ∈ s, a i ≤ b i) :
    (∑ i ∈ s, ((a i-d i)^p+(b i+d i)^p)) ≤
      ∑ i ∈ s, ((a i)^p+(b i)^p) := by
  exact Finset.sum_le_sum fun i hi =>
    rpow_concentration p (a i) (b i) (d i) hp hp1 (hd i hi) (hda i hi) (hab i hi)

theorem admission_of_batch_concentration (s : Finset ι) (p : ℝ) (a b d : ι → ℝ)
    (rest budget : ℝ) (hp : 0 ≤ p) (hp1 : p ≤ 1)
    (hd : ∀ i ∈ s, 0 ≤ d i) (hda : ∀ i ∈ s, d i ≤ a i)
    (hab : ∀ i ∈ s, a i ≤ b i)
    (hold : rest+(∑ i ∈ s, ((a i)^p+(b i)^p)) < budget) :
    rest+(∑ i ∈ s, ((a i-d i)^p+(b i+d i)^p)) < budget := by
  have h := batch_rpow_concentration s p a b d hp hp1 hd hda hab
  linarith

end IntegerMultBounds.MomentTransfer
