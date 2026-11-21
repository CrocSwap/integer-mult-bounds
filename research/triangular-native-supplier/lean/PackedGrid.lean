import PaddedGrid

namespace PackedPublicGrid

open MixedRankPublicGrid MixedRankRecovery
open scoped BigOperators

/-- An eighth of one public grid step fits between the two signed truncations. -/
theorem run_eighth {S D : ℕ} (hD : 0 < D) (ideal : Signal S → Signal S)
    (nonexp : ∀ x y e, (∀ j, ‖x j - y j‖ ≤ e) → ∀ k, ‖ideal x k - ideal y k‖ ≤ e)
    (raw : GridSignal S D → Signal S)
    (hraw : ∀ u : GridSignal S D, disk u.val (1/2) → ∀ j,
      ‖raw u j - ideal u.val j‖ ≤ (1/8 : ℝ) / D)
    (x : Signal S) (hx : disk x (1/2)) (k : ZMod S) :
    ‖run raw x k - ideal x k‖ ≤ 3 / (D : ℝ) := by
  let y := enter D x
  have h₁ := hraw y (enter_disk hD hx) k
  have h₂ := nonexp y.val x ((10/7 : ℝ)/D) (fun j ↦ snap_error hD (x j)) k
  have h₃ := snap_error hD (raw y k)
  change ‖run raw x k - raw y k‖ ≤ _ at h₃
  have t₁ := dist_triangle (run raw x k) (raw y k) (ideal y.val k)
  have t₂ := dist_triangle (run raw x k) (ideal y.val k) (ideal x k)
  simp only [dist_eq_norm] at t₁ t₂
  have room : (10/7 : ℝ)/D + (1/8 : ℝ)/D + (10/7 : ℝ)/D ≤ 3/D := by
    rw [← add_div, ← add_div]
    exact div_le_div_of_nonneg_right (by norm_num) (by positivity)
  linarith only [t₁, t₂, h₁, h₂, h₃, room]

open CirculantGridBridge
open CirculantTraceProduct

/-- Truncating the two physical forward fields gives the zero-padded public product. -/
theorem physical_packet_eighth {d D : ℕ} (s t : Fin d → ℕ)
    (hs : Pairwise fun i j ↦ Nat.Coprime (s i) (s j)) [∀ i, NeZero (s i)]
    (ht : ∀ i, s i ≤ t i) (hD : 0 < D) (f g : Field t)
    (v : Signal (∏ i, s i))
    (hf : ∀ u, ‖f u - zeroFill s t hs ht v u‖ ≤ (1/8 : ℝ)/D) :
    (fun u ↦ snap D (snap D (f u) * snap D (g u))) =
      zeroFill s t hs ht (fun k ↦ snap D (snap D (f (paddedAddress s t hs ht k)) *
        snap D (g (paddedAddress s t hs ht k)))) := by
  apply physical_packet s t hs ht hD
  intro u hu
  have h := hf u
  rw [zeroFill_hole _ _ _ _ _ _ hu, sub_zero] at h
  apply h.trans_lt
  rw [inv_eq_one_div]
  exact div_lt_div_of_pos_right (by norm_num) (by exact_mod_cast hD)

/-- The new selector still forces a genuine branching gate on every true axis. -/
theorem mixing_margin (r ell P : ℕ) (hr : r ≤ 2^ell) (hP : 32768*(ell+6) ≤ P) :
    2*r*(64*2^ell)^400 < 2^P := by
  have he : 1+ell+(6+ell)*400 < P := by omega
  calc
    _ ≤ 2*(2^ell)*(64*2^ell)^400 :=
      Nat.mul_le_mul_right _ (Nat.mul_le_mul_left 2 hr)
    _ = 2^(1+ell+(6+ell)*400) := by simp only [pow_add, pow_mul]; norm_num
    _ < _ := Nat.pow_lt_pow_right (by decide) he

/-- The physical mean Fourier pair with an eighth-step raw budget recovers the same signed words. -/
theorem product_on_the_public_grid {d : ℕ} (s : Fin d → ℕ)
    (hs : Pairwise fun i j ↦ Nat.Coprime (s i) (s j)) [∀ i, NeZero (s i)]
    [NeZero (∏ i, s i)] (B : ℕ) (hB : 32 ≤ B) (hEven : Even B) (hsize : ∏ i, s i ≤ B)
    (W : Bool → GridSignal (∏ i, s i) (B^6) → Signal (∏ i, s i))
    (hW : ∀ p x, disk x.val (1/2) → ∀ k,
      ‖W p x k - fromAxes s hs p x.val k‖ ≤ (1/8 : ℝ) / ((B^6 : ℕ) : ℝ))
    (a b : ZMod (∏ i, s i) → ℕ) (ha : ∀ j, a j ≤ B) (hb : ∀ j, b j ≤ B)
    (hspan : ∀ i j, a i ≠ 0 → b j ≠ 0 → i.val+j.val < ∏ i, s i) :
    pack B (carry B 0 (ordered (wordDecode (by omega : 0 < B) hEven (W false) (W true) a b))) =
      radixValue B a * radixValue B b := by
  rw [← decode_on_words]
  have hd : 0 < B^6 := pow_pos (by omega) _
  have hacc (p : Bool) (x : GridSignal (∏ i, s i) (B^6)) (hx : disk x.val (1/2)) (k) :
      ‖W p x k - target s hs p x.val k‖ ≤ (1/8 : ℝ) / ((B^6 : ℕ) : ℝ) := by
    rw [← tensor_at_original_coordinates]
    exact hW p x hx k
  exact MixedRankIntegrated.product_at_physical_coordinates s oneWeight hs
    (oneWeight_coprime s) B hB hsize (run (W false)) (run (W true)) (roundedMul (B^6))
    (3 / ((B^6 : ℕ) : ℝ)) (by positivity) (by simp)
    (run_eighth hd _ (forward_error _) (W false) (hacc false))
    (run_eighth hd _ (opposite_error _) (W true) (hacc true))
    (roundedMul_accuracy hd) a b ha hb hspan

#print axioms run_eighth
#print axioms physical_packet_eighth
#print axioms mixing_margin
#print axioms product_on_the_public_grid

end PackedPublicGrid
