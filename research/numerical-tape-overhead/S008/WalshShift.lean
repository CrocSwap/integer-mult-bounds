import S008.WalshInterpolation
import Mathlib.Algebra.BigOperators.Ring.Finset

/-! Orthogonality of the actual binary mask signs and a uniform one-sixteenth repair width. -/
namespace Moonshot.AlignedWalsh.ShiftGeometry

open Finset
abbrev Mask (y : ℕ) := Fin y → Bool

def bitSign (b : Bool) : ℤ := if b then -1 else 1

def localFactor (a t : Bool) : ℤ := if a then bitSign t else 1

def character {y : ℕ} (a t : Mask y) : ℤ := ∏ i, localFactor (a i) (t i)

def signedCharacter {y : ℕ} (key : Mask y → Bool) (a t : Mask y) : ℤ :=
  bitSign (key a) * character a t

def imbalance {y : ℕ} (I : Finset (Mask y)) (key : Mask y → Bool) (t : Mask y) : ℤ :=
  ∑ a ∈ I, signedCharacter key a t

def shiftedCount {y : ℕ} (I : Finset (Mask y)) (key : Mask y → Bool) (t : Mask y) : ℕ :=
  (I.filter (fun a ↦ signedCharacter key a t = -1)).card

private lemma bitSign_sq (b : Bool) : bitSign b * bitSign b = 1 := by
  cases b <;> decide

private lemma factor_inner (a b : Bool) :
    (∑ t : Bool, localFactor a t * localFactor b t) = if a=b then 2 else 0 := by
  cases a <;> cases b <;> rw [Fintype.sum_bool] <;> decide

theorem character_orthogonal {y : ℕ} (a b : Mask y) :
    (∑ t : Mask y, character a t * character b t) = if a=b then (2:ℤ)^y else 0 := by
  classical
  simp_rw [character, ← prod_mul_distrib]
  rw [← Fintype.prod_sum (fun i v ↦ localFactor (a i) v * localFactor (b i) v)]
  simp_rw [factor_inner]
  by_cases h : a=b
  · subst b
    simp
  · have ht : ∃ i, a i ≠ b i := by by_contra! hh; exact h (funext hh)
    obtain ⟨i,hi⟩ := ht
    rw [ite_eq_right h]
    exact prod_eq_zero (mem_univ i) (by simp [hi])

private lemma signed_orthogonal {y : ℕ} (key : Mask y → Bool) (a b : Mask y) :
    (∑ t : Mask y, signedCharacter key a t * signedCharacter key b t) =
      if a=b then (2:ℤ)^y else 0 := by
  classical
  calc
    _ = (bitSign (key a) * bitSign (key b)) * (∑ t : Mask y, character a t * character b t) := by
      rw [mul_sum]
      exact sum_congr rfl (fun t ht ↦ by simp only [signedCharacter]; ring)
    _ = _ := by
      rw [character_orthogonal]
      by_cases h : a=b <;> simp [h, bitSign_sq]

private lemma signed_square {y : ℕ} (key : Mask y → Bool) (a t : Mask y) :
    signedCharacter key a t * signedCharacter key a t = 1 := by
  unfold signedCharacter character
  rw [mul_mul_mul_comm, bitSign_sq, one_mul, ← prod_mul_distrib]
  apply prod_eq_one
  intro i hi
  cases a i <;> simp [localFactor, bitSign_sq]

theorem shifted_count_identity {y : ℕ} (I : Finset (Mask y)) (key : Mask y → Bool) (t : Mask y) :
    imbalance I key t = (I.card : ℤ) - 2 * shiftedCount I key t := by
  classical
  unfold imbalance
  calc
    _ = ∑ a ∈ I, (1-2*(if signedCharacter key a t = -1 then (1:ℤ) else 0)) := by
      apply sum_congr rfl
      intro a ha
      have h := (mul_self_eq_one_iff.mp (signed_square key a t))
      rcases h with h|h <;> simp [h]
    _ = _ := by rw [sum_sub_distrib, ← mul_sum]; simp [shiftedCount]

theorem exact_second_moment {y : ℕ} (I : Finset (Mask y)) (key : Mask y → Bool) :
    (∑ t : Mask y, ((I.card : ℤ)-2*shiftedCount I key t)^2) = (2:ℤ)^y * I.card := by
  classical
  simp_rw [← shifted_count_identity, imbalance, pow_two, sum_mul, mul_sum]
  rw [sum_comm]
  calc
    _ = ∑ a ∈ I, ∑ b ∈ I, (∑ t : Mask y, signedCharacter key a t * signedCharacter key b t) := by
      exact sum_congr rfl (fun a ha ↦ sum_comm)
    _ = _ := by
      simp_rw [signed_orthogonal]
      simp [mul_comm]

/-- The product character is the exact binary dot-mask sign across its digit positions. -/
def maskDotCount {y : ℕ} (a t : Mask y) : ℕ :=
  (univ.filter (fun i ↦ a i = true ∧ t i = true)).card

theorem character_is_dot {y : ℕ} (a t : Mask y) : character a t = (-1:ℤ)^(maskDotCount a t) := by
  classical
  unfold character maskDotCount
  calc
    _ = ∏ i, (if a i = true ∧ t i = true then (-1:ℤ) else 1) := by
      apply prod_congr rfl
      intro i hi
      cases h : a i <;> cases ht : t i <;> simp [localFactor,bitSign]
    _ = _ := by rw [prod_ite]; simp

theorem signed_is_shifted_bit {y : ℕ} (key : Mask y → Bool) (a t : Mask y) :
    signedCharacter key a t =
      (-1:ℤ)^((if key a then 1 else 0) + maskDotCount a t) := by
  rw [signedCharacter,character_is_dot,pow_add]
  cases ha : key a <;> simp [bitSign]

/-- The exact Chebyshev certificate for any designated subset of distinct binary masks. -/
theorem exceptional_card {y : ℕ} (I : Finset (Mask y)) (hI : 0 < I.card)
    (key : Mask y → Bool) (bad : Finset (Mask y))
    (hbad : ∀ t ∈ bad, 16*(I.card : ℤ) ≤ ((I.card : ℤ)-2*shiftedCount I key t)^2) :
    16*bad.card ≤ 2^y := by
  classical
  have h0 : (bad.card : ℤ)*(16*(I.card : ℤ)) ≤ (2:ℤ)^y * I.card := calc
    _ = ∑ _t ∈ bad, (16*I.card : ℤ) := by simp
    _ ≤ ∑ t ∈ bad, ((I.card : ℤ)-2*shiftedCount I key t)^2 := sum_le_sum hbad
    _ ≤ ∑ t : Mask y, ((I.card : ℤ)-2*shiftedCount I key t)^2 :=
      sum_le_sum_of_subset_of_nonneg (subset_univ _) (fun i hi hi' => sq_nonneg _)
    _ = _ := exact_second_moment I key
  have hp : 0 < (I.card : ℤ) := by exact_mod_cast hI
  have hv : (16*(bad.card : ℤ))*(I.card : ℤ) ≤ (2:ℤ)^y * I.card := by
    simpa only [mul_comm 16 (bad.card : ℤ), mul_assoc] using h0
  exact_mod_cast le_of_mul_le_mul_right hv hp

private lemma outside_deviation {m B c : ℕ} (hB : 4*m ≤ B^2)
    (hout : c < m/2-B ∨ (m+1)/2+B<c) : 16*(m : ℤ) ≤ ((m : ℤ)-2*c)^2 := by
  have hB' : 4*(m : ℤ) ≤ (B : ℤ)^2 := by exact_mod_cast hB
  rcases hout with h|h
  · have hd : 2*(B : ℤ) ≤ (m : ℤ)-2*c := by omega
    have hs := pow_le_pow_left₀ (by positivity : 0 ≤ 2*(B:ℤ)) hd 2
    nlinarith
  · have hd : 2*(B : ℤ) ≤ 2*(c : ℤ)-m := by omega
    have hs := pow_le_pow_left₀ (by positivity : 0 ≤ 2*(B:ℤ)) hd 2
    nlinarith

theorem window_card {y : ℕ} (I : Finset (Mask y)) (hI : 0 < I.card)
    (key : Mask y → Bool) {B : ℕ} (hB : 4*I.card ≤ B^2) :
    let bad := univ.filter (fun t ↦ let c := shiftedCount I key t
      c < I.card/2-B ∨ (I.card+1)/2+B<c)
    bad.card ≤ 2^y/16 := by
  classical
  dsimp only
  apply (Nat.le_div_iff_mul_le (by decide)).mpr
  rw [mul_comm]
  apply exceptional_card I hI key
  intro t ht
  exact outside_deviation hB (mem_filter.mp ht).2


/-- Generalized integer binomial coefficient at c-u, including negative c-u. -/
def countChoose (c low h : ℕ) : ℤ :=
  if low ≤ c then ((c-low).choose h : ℤ)
  else (-1:ℤ)^h * (((low-c+h-1).choose h : ℕ) : ℤ)

def newtonSum (low d c : ℕ) : ℤ :=
  ∑ h ∈ range (d+1), (-2:ℤ)^h * countChoose c low h

theorem newton_in_window {low d c : ℕ} (hc : low ≤ c) (hd : c-low ≤ d) :
    newtonSum low d c = (-1:ℤ)^(c-low) := by
  classical
  rw [newtonSum]
  simp only [countChoose, ite_eq_left hc]
  let n := c-low
  change (∑ h ∈ range (d+1), (-2:ℤ)^h * ↑(n.choose h)) = (-1:ℤ)^n
  have hs : range (n+1) ⊆ range (d+1) := by
    intro i hi
    apply mem_range.mpr
    have hi := mem_range.mp hi
    dsimp [n] at hi
    omega
  rw [← sum_subset hs (fun h hh h' ↦ by
    have hn : n < h := by have hk : h ∉ range (n+1) := h'; simpa using hk
    simp [Nat.choose_eq_zero_of_lt hn])]
  simpa using (add_pow (-2:ℤ) 1 n).symm

def targetSign {y : ℕ} (I : Finset (Mask y)) (key : Mask y → Bool) : ℤ :=
  ∏ a ∈ I, bitSign (key a)

def shiftSign {y : ℕ} (I : Finset (Mask y)) (t : Mask y) : ℤ :=
  ∏ a ∈ I, character a t

def predictor {y : ℕ} (I : Finset (Mask y)) (key : Mask y → Bool) (low d : ℕ)
    (t : Mask y) : ℤ :=
  ((-1:ℤ)^low * shiftSign I t) * newtonSum low d (shiftedCount I key t)

private lemma shiftSign_square {y : ℕ} (I : Finset (Mask y)) (t : Mask y) :
    shiftSign I t * shiftSign I t = 1 := by
  rw [shiftSign, ← prod_mul_distrib]
  apply prod_eq_one
  intro a ha
  simpa [signedCharacter, bitSign] using signed_square (fun _ : Mask y ↦ false) a t

private lemma product_shifted {y : ℕ} (I : Finset (Mask y)) (key : Mask y → Bool) (t : Mask y) :
    (∏ a ∈ I, signedCharacter key a t) = (-1:ℤ)^(shiftedCount I key t) := by
  classical
  calc
    _ = ∏ a ∈ I, (if signedCharacter key a t = -1 then (-1:ℤ) else 1) := by
      apply prod_congr rfl
      intro a ha
      rcases mul_self_eq_one_iff.mp (signed_square key a t) with h|h <;> simp [h]
    _ = _ := by rw [prod_ite]; simp [shiftedCount]

theorem predictor_in_window {y : ℕ} (I : Finset (Mask y)) (key : Mask y → Bool) (t : Mask y)
    {low d : ℕ} (hlo : low ≤ shiftedCount I key t) (hhi : shiftedCount I key t-low ≤ d) :
    predictor I key low d t = targetSign I key := by
  rw [predictor, newton_in_window hlo hhi]
  calc
    _ = ((-1:ℤ)^low*(-1)^(shiftedCount I key t-low))*shiftSign I t := by ring
    _ = (-1:ℤ)^(shiftedCount I key t)*shiftSign I t := by
      rw [← pow_add, Nat.add_sub_of_le hlo]
    _ = (targetSign I key*shiftSign I t)*shiftSign I t := by
      rw [← product_shifted I key t]
      simp only [signedCharacter, prod_mul_distrib, targetSign, shiftSign]
    _ = _ := by rw [mul_assoc, shiftSign_square, mul_one]

theorem actual_defect_capacity {y : ℕ} (I : Finset (Mask y)) (hI : 0 < I.card)
    (key : Mask y → Bool) {B : ℕ} (hB : 4*I.card ≤ B^2) :
    let low := I.card/2-B
    let high := (I.card+1)/2+B
    let bad := univ.filter (fun t ↦ predictor I key low (high-low) t ≠ targetSign I key)
    bad.card ≤ 2^y/16 := by
  classical
  dsimp only
  apply (Finset.card_le_card ?_).trans (window_card I hI key hB)
  intro t ht
  have hn := (mem_filter.mp ht).2
  apply mem_filter.mpr
  refine ⟨mem_univ _, ?_⟩
  change shiftedCount I key t < I.card/2-B ∨ (I.card+1)/2+B < shiftedCount I key t
  by_contra! hg
  exact hn (predictor_in_window I key t hg.1 (by omega))


/-- Little-endian binary digits of the actual numbered seed or label. -/
def binaryMask (y t : ℕ) : Mask y := fun i ↦ t.testBit i.val

private theorem binaryMask_inj {y i j : ℕ} (hi : i < 2^y) (hj : j < 2^y)
    (he : binaryMask y i = binaryMask y j) : i=j := by
  apply Nat.eq_of_testBit_eq
  intro p
  by_cases hp : p < y
  · exact congrFun he ⟨p,hp⟩
  · have le2 : 2^y ≤ 2^p := Nat.pow_le_pow_right (by decide) (Nat.le_of_not_gt hp)
    rw [Nat.testBit_lt_two_pow (hi.trans_le le2), Nat.testBit_lt_two_pow (hj.trans_le le2)]

/-- Every nonzero label from 1 through 2^y−1, with its actual binary-AND coordinates. -/
def canonicalMasks (y : ℕ) : Finset (Mask y) := ((range (2^y)).erase 0).image (binaryMask y)

theorem canonical_mask_count (y : ℕ) : (canonicalMasks y).card = 2^y-1 := by
  classical
  rw [canonicalMasks, card_image_of_injOn]
  · rw [card_erase_of_mem (mem_range.mpr (by positivity)), card_range]
  · exact fun i hi j hj he ↦ binaryMask_inj (mem_range.mp (mem_erase.mp hi).2)
      (mem_range.mp (mem_erase.mp hj).2) he

def radius (m : ℕ) : ℕ := (4*m-1).sqrt+1

theorem radius_square (m : ℕ) : 4*m ≤ (radius m)^2 := by
  have ht := Nat.lt_succ_sqrt' (4*m-1)
  change 4*m-1 < ((4*m-1).sqrt+1)^2 at ht
  change 4*m ≤ ((4*m-1).sqrt+1)^2
  omega

def actualBad (y : ℕ) (key : Mask y → Bool) : Finset ℕ :=
  let I := canonicalMasks y
  let m := I.card
  let B := radius m
  let low := m/2-B
  let d := (m+1)/2+B-low
  (range (2^y)).filter (fun i ↦ predictor I key low d (binaryMask y i) ≠ targetSign I key)

theorem numbered_defect_capacity {y : ℕ} (hy : 0 < y) (key : Mask y → Bool) :
    (actualBad y key).card ≤ 2^y/16 := by
  classical
  let I := canonicalMasks y
  let B := radius I.card
  have hm : 0 < I.card := by
    dsimp [I]
    rw [canonical_mask_count]
    have hp := Nat.one_lt_two_pow (Nat.ne_of_gt hy)
    omega
  have hc := actual_defect_capacity I hm key (radius_square I.card)
  dsimp only at hc
  apply (card_le_card_of_injOn (binaryMask y) ?_ ?_).trans hc
  · intro i hi
    exact mem_filter.mpr ⟨mem_univ _, (mem_filter.mp hi).2⟩
  · intro i hi j hj he
    exact binaryMask_inj (mem_range.mp (mem_filter.mp hi).1)
      (mem_range.mp (mem_filter.mp hj).1) he


def safeGap (g : ℤ) : ℕ := if g=0 then 1 else g.natAbs

/-- Product of all nonzero gap magnitudes on every count and both independent signs. -/
def gapProduct (m low d : ℕ) : ℕ :=
  ∏ c ∈ range (m+1), ∏ gamma : Bool, ∏ z : Bool,
    safeGap (bitSign gamma * newtonSum low d c - bitSign z)

theorem gapProduct_pos (m low d : ℕ) : 0 < gapProduct m low d := by
  unfold gapProduct
  apply prod_pos
  intro c hc
  apply prod_pos
  intro ga hga
  apply prod_pos
  intro z hz
  unfold safeGap
  split_ifs with hg
  · decide
  · exact Int.natAbs_pos.mpr hg

private theorem is_bitSign {z : ℤ} (hz : z*z=1) : ∃ b : Bool, bitSign b=z := by
  rcases mul_self_eq_one_iff.mp hz with h|h
  · exact ⟨false,by simp [bitSign,h]⟩
  · exact ⟨true,by simp [bitSign,h]⟩

private theorem target_square {y : ℕ} (I : Finset (Mask y)) (key : Mask y → Bool) :
    targetSign I key * targetSign I key = 1 := by
  rw [targetSign, ← prod_mul_distrib]
  exact prod_eq_one (fun a ha ↦ bitSign_sq _)

theorem actual_gap_dvd {y : ℕ} (I : Finset (Mask y)) (key : Mask y → Bool) (t : Mask y)
    (low d : ℕ) (he : predictor I key low d t ≠ targetSign I key) :
    (predictor I key low d t-targetSign I key).natAbs ∣ gapProduct I.card low d := by
  classical
  let c := shiftedCount I key t
  have hc : c ∈ range (I.card+1) := mem_range.mpr
    (Nat.lt_succ_of_le (card_filter_le _ _))
  have hp : (-1:ℤ)^low * (-1)^low = 1 := by rw [← mul_pow]; simp
  have hg : (((-1:ℤ)^low)*shiftSign I t)*(((-1:ℤ)^low)*shiftSign I t)=1 := by
    rw [mul_mul_mul_comm, hp, shiftSign_square, mul_one]
  obtain ⟨gam,hgam⟩ := is_bitSign hg
  obtain ⟨z,hz⟩ := is_bitSign (target_square I key)
  let factor (c : ℕ) (a b : Bool) := safeGap (bitSign a*newtonSum low d c-bitSign b)
  have hv : (predictor I key low d t-targetSign I key).natAbs = factor c gam z := by
    dsimp [factor,c]
    rw [hgam,hz,← predictor, safeGap, ite_eq_right (sub_ne_zero.mpr he)]
  rw [hv]
  exact (dvd_prod_of_mem (fun b : Bool ↦ factor c gam b) (mem_univ z)).trans
    ((dvd_prod_of_mem (fun a : Bool ↦ ∏ b : Bool, factor c a b) (mem_univ gam)).trans
      (dvd_prod_of_mem (fun cc : ℕ ↦ ∏ a : Bool, ∏ b : Bool, factor cc a b) hc))

def lowEndpoint (m : ℕ) : ℕ := m/2-radius m

def newtonDegree (m : ℕ) : ℕ := (m+1)/2+radius m-lowEndpoint m

def numberedPredictor (y : ℕ) (key : Mask y → Bool) (i : ℕ) : ℤ :=
  let I := canonicalMasks y
  predictor I key (lowEndpoint I.card) (newtonDegree I.card) (binaryMask y i)

def numberedGap (y : ℕ) (key : Mask y → Bool) (i : ℕ) : ℤ :=
  numberedPredictor y key i - targetSign (canonicalMasks y) key

def numberedGapProduct (y : ℕ) : ℕ :=
  let m := (canonicalMasks y).card
  gapProduct m (lowEndpoint m) (newtonDegree m)

theorem actual_numbered_gap_dvd {y : ℕ} (key : Mask y → Bool) {i : ℕ} (hi : i ∈ actualBad y key) :
    (numberedGap y key i).natAbs ∣ numberedGapProduct y := by
  apply actual_gap_dvd (canonicalMasks y) key (binaryMask y i)
  exact (mem_filter.mp hi).2

open Moonshot.CompactSpecialization

/-- Complete exact-source certificate on the real numbered labels and the generated G.
It needs only the global modulus alignment from the common width-chain setup. -/
theorem numbered_repair_token {U e y : ℕ} (key : Mask y → Bool)
    (hU : (2^y-1).factorial^2 * numberedGapProduct y ∣ U) (r s x : ℕ) :
    let W := 2^y
    let J := actualBad y key
    let g := numberedGap y key
    let G := numberedGapProduct y
    let C := (W-1).factorial^2 * G
    let M := modulus U e
    let N := scaledRepairNum W G J g r s
    let z := (((N : ZMod M)*x).val)
    let Y := (z+shortCorrection C z*M)/C
    Y<M ∧ SourceTicket M (repairEntry W J g r s*x) (Y : ZMod M) := by
  apply actual_repair_token (actualBad y key) (fun i hi ↦ (mem_filter.mp hi).1) (numberedGap y key)
  · exact fun i hi ↦ actual_numbered_gap_dvd key hi
  · exact fun i hi ↦ sub_ne_zero.mpr (mem_filter.mp hi).2
  · apply gapProduct_pos
  · exact hU


theorem canonical_degree {y : ℕ} (hy : 6 ≤ y) :
    newtonDegree (2^y-1) = 2*radius (2^y-1)+1 := by
  let m := 2^y-1
  change newtonDegree m = 2*radius m+1
  have hm : 63 ≤ m := by
    have h := Nat.pow_le_pow_right (by decide : 0 < 2) hy
    norm_num at h
    omega
  have hhalf : 16 ≤ m/2 := by omega
  have hs : 16*(m/2) ≤ (m/2)*(m/2) := Nat.mul_le_mul_right _ hhalf
  have hs' : 4*m-1 < (m/2)*(m/2) := by omega
  have hb : radius m ≤ m/2 := Nat.sqrt_lt.mpr hs'
  have hm' : (m+1)/2=m/2+1 := by
    obtain ⟨z,rfl⟩ := Nat.exists_eq_succ_of_ne_zero (by omega : y ≠ 0)
    dsimp [m]
    rw [pow_succ]
    have hz : 0 < 2^z := by positivity
    omega
  unfold newtonDegree lowEndpoint
  omega

theorem shiftSign_is_parity {y : ℕ} (I : Finset (Mask y)) (t : Mask y) :
    shiftSign I t = (-1:ℤ)^((I.filter (fun a ↦ character a t = -1)).card) := by
  simpa [shiftSign, signedCharacter, bitSign, shiftedCount] using
    product_shifted I (fun _ ↦ false) t

/-- All actual numbered seed rows, both agreeing and disagreeing, return the exact
target sign after their two predictor applications and the computed check table. -/
theorem numbered_repair_all_rows {y i : ℕ} (key : Mask y → Bool) (x : ℕ → ℚ) (hi : i < 2^y) :
    let W := 2^y
    let J := actualBad y key
    let g := numberedGap y key
    let p := numberedPredictor y key
    let z := targetSign (canonicalMasks y) key
    let Z := ∑ r ∈ range J.card, (node W i)^r *
      (∑ s ∈ range J.card, repairEntry W J g r s *
        (∑ j ∈ J, (node W j)^s * ((g j : ℚ) * x j)))
    (p i : ℚ) * x i - (p i : ℚ) * Z + (z : ℚ) * Z = (z : ℚ) * x i := by
  exact corrected_predictor_all_seeds (by positivity) (numberedPredictor y key)
    (targetSign (canonicalMasks y) key) x hi

end Moonshot.AlignedWalsh.ShiftGeometry
