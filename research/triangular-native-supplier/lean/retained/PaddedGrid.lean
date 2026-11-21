import TraceProduct

namespace CirculantTraceProduct

open Finset
open scoped BigOperators
open CirculantGridBridge MixedRankPublicGrid MixedRankRecovery

theorem snap_subword {D : ℕ} (hD : 0 < D) (z : ℂ) (hz : ‖z‖ < (D:ℝ)⁻¹) :
    snap D z = 0 := by
  have hd : 0 < (D:ℝ) := by exact_mod_cast hD
  have one (x : ℝ) (hx : |x| < (D:ℝ)⁻¹) : snapReal D x = 0 := by
    have ha : |(D:ℝ)*x| < 1 := by
      rw [abs_mul, abs_of_pos hd, mul_comm]
      exact (lt_div_iff₀ hd).mp (by simpa [one_div] using hx)
    have hlow := (abs_lt.mp ha).1
    have hhigh := (abs_lt.mp ha).2
    unfold snapReal towardZero
    split_ifs with h
    · rw [Int.floor_eq_zero_iff.mpr ⟨h,hhigh⟩]
      simp
    · rw [Int.floor_eq_zero_iff.mpr ⟨by linarith,by linarith⟩]
      simp
  apply Complex.ext
  · exact one z.re ((Complex.abs_re_le_norm z).trans_lt hz)
  · exact one z.im ((Complex.abs_im_le_norm z).trans_lt hz)

variable {d : ℕ} (s t : Fin d → ℕ) (hs : Pairwise fun i j ↦ Nat.Coprime (s i) (s j))
  [∀ i, NeZero (s i)] (ht : ∀ i, s i ≤ t i)

noncomputable def zeroFill (x : Signal (∏ i, s i)) : Field t := by
  classical
  exact fun u ↦ if h : ∃ k, paddedAddress s t hs ht k = u then x h.choose else 0

theorem zeroFill_true (x : Signal (∏ i, s i)) (k : ZMod (∏ i, s i)) :
    zeroFill s t hs ht x (paddedAddress s t hs ht k) = x k := by
  classical
  have h : ∃ j, paddedAddress s t hs ht j = paddedAddress s t hs ht k := ⟨k,rfl⟩
  simp only [zeroFill, h, ↓reduceDIte]
  exact congrArg x (paddedAddress_injective s t hs ht h.choose_spec)

theorem zeroFill_hole (x : Signal (∏ i,s i)) (u : Carrier t)
    (hu : ¬ ∃ k, paddedAddress s t hs ht k = u) : zeroFill s t hs ht x u = 0 := by
  classical
  simp [zeroFill, hu]

/-- Two coordinate truncations and the signed pointwise product produce
the physical zero-fill of the represented valid packet. One forward
word of absolute size below one grid unit at a hole suffices. -/
theorem physical_packet {D : ℕ} (hD : 0 < D) (f g : Field t)
    (hf : ∀ u, (¬ ∃ k, paddedAddress s t hs ht k = u) → ‖f u‖ < (D:ℝ)⁻¹) :
    (fun u ↦ snap D (snap D (f u) * snap D (g u))) =
      zeroFill s t hs ht (fun k ↦ snap D (snap D (f (paddedAddress s t hs ht k)) *
        snap D (g (paddedAddress s t hs ht k)))) := by
  classical
  funext u
  by_cases h : ∃ k, paddedAddress s t hs ht k = u
  · obtain ⟨k,rfl⟩ := h
    rw [zeroFill_true]
  · rw [zeroFill_hole _ _ _ _ _ _ h, snap_subword hD (f u) (hf u h), zero_mul]
    exact snap_subword hD 0 (by simp [show (0:ℝ) < D by exact_mod_cast hD])

theorem packet_from_raw_residual {D : ℕ} (hD : 2 ≤ D) (f g : Field t)
    (v : Signal (∏ i, s i)) (hf : ∀ u, ‖f u - zeroFill s t hs ht v u‖ ≤ 1/(D:ℝ)^4) :
    (fun u ↦ snap D (snap D (f u) * snap D (g u))) =
      zeroFill s t hs ht (fun k ↦ snap D (snap D (f (paddedAddress s t hs ht k)) *
        snap D (g (paddedAddress s t hs ht k)))) := by
  apply physical_packet s t hs ht (by omega)
  intro u hu
  have h := hf u
  rw [zeroFill_hole _ _ _ _ _ _ hu, sub_zero] at h
  have hd : (0:ℝ) < D := by exact_mod_cast (show 0 < D by omega)
  have hr : (1/7:ℝ)/D < (D:ℝ)⁻¹ := by
    rw [inv_eq_one_div]
    exact div_lt_div_of_pos_right (by norm_num) hd
  exact h.trans_lt ((residual_room hD).trans_lt hr)

theorem padded_range (u : Carrier t) :
    (∃ k, paddedAddress s t hs ht k = u) ↔ ∀ i, (u i).val < s i := by
  constructor
  · rintro ⟨k,rfl⟩ i
    exact ZMod.val_lt _
  · intro h
    let v : Profile s := fun i ↦ ((u i).val : ZMod (s i))
    refine ⟨(addresses s hs).symm v, ?_⟩
    funext i
    apply Fin.ext
    change (addresses s hs ((addresses s hs).symm v) i).val = _
    rw [Equiv.apply_symm_apply]
    exact ZMod.val_natCast_of_lt (h i)

/-- A true wire sees the local character on the true input. A hole sees
only the diagonal identity entry. -/
noncomputable def paddedEntry {r t : ℕ} [NeZero r] (p : Bool) (j k : Fin t) : ℂ :=
  if j.val < r ∧ k.val < r then entry p (j.val : ZMod r) (k.val : ZMod r)
  else if j = k then 1 else 0

noncomputable def paddedMean (p : Bool) (x : Field t) (k : Carrier t) : ℂ :=
  ∑ j : Carrier t, (∏ i, paddedEntry (r := s i) p (j i) (k i)) * x j

theorem sum_zeroFill [NeZero (∏ i, s i)] (g : Field t) (x : Signal (∏ i,s i)) :
    ∑ u, g u * zeroFill s t hs ht x u = ∑ j, g (paddedAddress s t hs ht j) * x j := by
  classical
  let p := paddedAddress s t hs ht
  let L := Finset.univ.image p
  have en : (∑ u ∈ L, g u * zeroFill s t hs ht x u) = ∑ u, g u * zeroFill s t hs ht x u := by
    apply Finset.sum_subset (Finset.subset_univ L)
    intro u _ hu
    have h : ¬ ∃ k, p k = u := by simpa [L] using hu
    simp [zeroFill_hole _ _ _ _ _ _ h]
  rw [← en]
  dsimp only [L]
  rw [Finset.sum_image (fun a _ b _ h ↦ paddedAddress_injective s t hs ht h)]
  simp [zeroFill_true]

/-- The tensor of the actual local mean-with-identity matrices agrees
on every physical record with the zero-filled original-coordinate result. -/
theorem physical_zero_fill [NeZero (∏ i, s i)] (p : Bool) (x : Signal (∏ i,s i)) :
    paddedMean s t p (zeroFill s t hs ht x) = zeroFill s t hs ht (fromAxes s hs p x) := by
  classical
  funext u
  rw [paddedMean, sum_zeroFill]
  by_cases h : ∃ k, paddedAddress s t hs ht k = u
  · obtain ⟨k,rfl⟩ := h
    rw [zeroFill_true, fromAxes, tensor_kernel, ← (addresses s hs).sum_comp]
    simp only [Equiv.symm_apply_apply]
    apply Finset.sum_congr rfl
    intro j _
    congr 1
    apply Finset.prod_congr rfl
    intro i _
    simp [paddedEntry, paddedAddress, ZMod.val_lt]
  · rw [zeroFill_hole _ _ _ _ _ _ h]
    have hn := (padded_range s t hs ht u).not.mp h
    push Not at hn
    obtain ⟨i,hi⟩ := hn
    apply Finset.sum_eq_zero
    intro j _
    have hz : paddedEntry (r := s i) p (paddedAddress s t hs ht j i) (u i) = 0 := by
      have hneq : paddedAddress s t hs ht j i ≠ u i := by
        intro he
        have hv := congrArg Fin.val he
        have hj := ((padded_range s t hs ht _).mp ⟨j,rfl⟩) i
        omega
      simp [paddedEntry, not_lt.mpr hi, hneq]
    rw [Finset.prod_eq_zero (Finset.mem_univ i) hz, zero_mul]

#print axioms physical_zero_fill
#print axioms packet_from_raw_residual
#print axioms snap_subword
#print axioms physical_packet

end CirculantTraceProduct
