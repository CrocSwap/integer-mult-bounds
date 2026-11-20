import Integrated

/-! The public fixed-point boundary on both signs and on the pointwise product. -/
namespace MixedRankPublicGrid

open MixedRankRecovery

noncomputable def towardZero (x : ℝ) : ℤ :=
  if 0 ≤ x then ⌊x⌋ else -⌊-x⌋

theorem towardZero_int (k : ℤ) : towardZero (k : ℝ) = k := by
  unfold towardZero
  split
  · simp
  · rw [← Int.cast_neg, Int.floor_intCast, neg_neg]

theorem towardZero_division (k : ℤ) {c : ℕ} (hc : 0 < c) :
    towardZero ((k : ℝ)/c) = k.tdiv c := by
  have hc' : 0 < (c : ℝ) := by exact_mod_cast hc
  by_cases hk : 0 ≤ k
  · have hr : 0 ≤ (k : ℝ)/c := div_nonneg (by exact_mod_cast hk) hc'.le
    simp [towardZero, hr, Int.floor_div_natCast, Int.tdiv_eq_ediv_of_nonneg hk]
  · have hr : ¬ 0 ≤ (k : ℝ)/c := not_le.mpr (div_neg_of_neg_of_pos (by exact_mod_cast lt_of_not_ge hk) hc')
    simp only [towardZero, hr, ↓reduceIte]
    rw [← neg_div, ← Int.cast_neg, Int.floor_div_natCast, Int.floor_intCast,
      ← Int.tdiv_eq_ediv_of_nonneg (show 0 ≤ -k by omega), Int.neg_tdiv, neg_neg]

theorem towardZero_bounds (x : ℝ) :
    |(towardZero x : ℝ)| ≤ |x| ∧ |(towardZero x : ℝ) - x| ≤ 1 := by
  by_cases hx : 0 ≤ x
  · have hf := Int.floor_le x
    have hl := Int.lt_floor_add_one x
    have hpos : (0 : ℝ) ≤ (⌊x⌋ : ℤ) := by exact_mod_cast Int.floor_nonneg.mpr hx
    simp only [towardZero, hx, ↓reduceIte]
    rw [abs_of_nonneg hpos, abs_of_nonneg hx,
      abs_of_nonpos (sub_nonpos.mpr hf)]
    exact ⟨hf, by linarith⟩
  · have hneg : 0 ≤ -x := by linarith
    have hf := Int.floor_le (-x)
    have hl := Int.lt_floor_add_one (-x)
    have hpos : (0 : ℝ) ≤ (⌊-x⌋ : ℤ) := by exact_mod_cast Int.floor_nonneg.mpr hneg
    simp only [towardZero, hx, ↓reduceIte]
    rw [Int.cast_neg, abs_neg, abs_of_nonneg hpos,
      abs_of_nonpos (le_of_not_ge hx), abs_of_nonneg (by linarith : 0 ≤ -(⌊-x⌋ : ℝ) - x)]
    exact ⟨hf, by linarith⟩

noncomputable def snapReal (D : ℕ) (x : ℝ) : ℝ :=
  (towardZero ((D : ℝ) * x) : ℝ) / D

noncomputable def snap (D : ℕ) (z : ℂ) : ℂ :=
  ⟨snapReal D z.re, snapReal D z.im⟩

theorem snap_finer_word {D c : ℕ} (hD : 0 < D) (hc : 0 < c) (k : ℤ) :
    snapReal D ((k : ℝ)/((D:ℝ)*c)) = (k.tdiv c : ℝ)/D := by
  have hd : (D : ℝ) ≠ 0 := by exact_mod_cast hD.ne'
  have hc' : (c : ℝ) ≠ 0 := by exact_mod_cast hc.ne'
  rw [snapReal, show (D:ℝ)*((k:ℝ)/((D:ℝ)*c)) = (k:ℝ)/c by field_simp,
    towardZero_division k hc]

def Represented (D : ℕ) (z : ℂ) : Prop :=
  ∃ a b : ℤ, z.re = (a : ℝ)/D ∧ z.im = (b : ℝ)/D

theorem snap_represented (D : ℕ) (z : ℂ) : Represented D (snap D z) :=
  ⟨_, _, rfl, rfl⟩

theorem snapReal_word {D : ℕ} (hD : 0 < D) (k : ℤ) :
    snapReal D ((k : ℝ)/D) = (k : ℝ)/D := by
  have h : (D : ℝ) ≠ 0 := by exact_mod_cast hD.ne'
  rw [snapReal, show (D : ℝ) * ((k : ℝ) / D) = k by field_simp, towardZero_int]

theorem snap_word {D : ℕ} (hD : 0 < D) {z : ℂ} (hz : Represented D z) :
    snap D z = z := by
  obtain ⟨a, b, ha, hb⟩ := hz
  apply Complex.ext
  · change snapReal D z.re = z.re
    rw [ha, snapReal_word hD]
  · change snapReal D z.im = z.im
    rw [hb, snapReal_word hD]

theorem snapReal_bounds {D : ℕ} (hD : 0 < D) (x : ℝ) :
    |snapReal D x| ≤ |x| ∧ |snapReal D x - x| ≤ 1 / (D : ℝ) := by
  have hd : 0 < (D : ℝ) := by exact_mod_cast hD
  obtain ⟨hs, ht⟩ := towardZero_bounds ((D : ℝ)*x)
  rw [abs_mul, abs_of_pos hd] at hs
  constructor
  · rw [snapReal, abs_div, abs_of_pos hd, div_le_iff₀ hd]
    simpa [mul_comm] using hs
  · have hx : snapReal D x - x = ((towardZero ((D : ℝ) * x) : ℝ) - D*x) / D := by
      unfold snapReal
      field_simp
    rw [hx, abs_div, abs_of_pos hd]
    exact div_le_div_of_nonneg_right ht hd.le

theorem snap_radius {D : ℕ} (hD : 0 < D) (z : ℂ) : ‖snap D z‖ ≤ ‖z‖ := by
  rw [Complex.norm_def, Complex.norm_def]
  apply Real.sqrt_le_sqrt
  have hr := sq_le_sq.mpr (snapReal_bounds hD z.re).1
  have hi := sq_le_sq.mpr (snapReal_bounds hD z.im).1
  simpa [Complex.normSq_apply, snap, pow_two] using add_le_add hr hi

theorem snap_error {D : ℕ} (hD : 0 < D) (z : ℂ) :
    ‖snap D z - z‖ ≤ (10/7 : ℝ) / D := by
  have hd : 0 < (D : ℝ) := by exact_mod_cast hD
  have hinv : 0 ≤ 1 / (D : ℝ) := by positivity
  have hr := sq_le_sq.mpr ((snapReal_bounds hD z.re).2.trans_eq (abs_of_nonneg hinv).symm)
  have hi := sq_le_sq.mpr ((snapReal_bounds hD z.im).2.trans_eq (abs_of_nonneg hinv).symm)
  rw [Complex.norm_def, Real.sqrt_le_iff]
  refine ⟨by positivity, ?_⟩
  calc
    Complex.normSq (snap D z - z) ≤ (1 / (D : ℝ))^2 + (1 / (D : ℝ))^2 := by
      simpa [Complex.normSq_apply, snap, pow_two] using add_le_add hr hi
    _ ≤ ((10/7 : ℝ) / D)^2 := by
      field_simp
      norm_num

abbrev GridSignal (S D : ℕ) := {x : Signal S // ∀ k, Represented D (x k)}

noncomputable def enter {S : ℕ} (D : ℕ) (x : Signal S) : GridSignal S D :=
  ⟨fun k ↦ snap D (x k), fun k ↦ snap_represented D (x k)⟩

theorem enter_word {S D : ℕ} (hD : 0 < D) (x : GridSignal S D) :
    enter D x.val = x := by
  apply Subtype.ext
  funext k
  exact snap_word hD (x.property k)

theorem enter_disk {S D : ℕ} (hD : 0 < D) {x : Signal S} {r : ℝ} (hx : disk x r) :
    disk (enter D x).val r :=
  fun k ↦ (snap_radius hD _).trans (hx k)

noncomputable def run {S D : ℕ} (raw : GridSignal S D → Signal S) (x : Signal S) :
    Signal S := fun k ↦ snap D (raw (enter D x) k)

noncomputable def roundedMul (D : ℕ) (x y : ℂ) : ℂ :=
  snap D (snap D x * snap D y)

theorem run_on_words {S D : ℕ} (hD : 0 < D) (raw : GridSignal S D → Signal S)
    (x : GridSignal S D) (k : ZMod S) : run raw x.val k = snap D (raw x k) := by
  rw [run, enter_word hD]

theorem roundedMul_words {D : ℕ} (hD : 0 < D) {x y : ℂ}
    (hx : Represented D x) (hy : Represented D y) :
    roundedMul D x y = snap D (x * y) := by
  rw [roundedMul, snap_word hD hx, snap_word hD hy]

theorem residual_room {D : ℕ} (hD : 2 ≤ D) :
    1 / (D : ℝ)^4 ≤ (1/7 : ℝ) / D := by
  have h : (2 : ℝ) ≤ D := by exact_mod_cast hD
  have hd : 0 < (D : ℝ) := by linarith
  have hh : (2:ℝ)^3 ≤ (D : ℝ)^3 := by gcongr
  have hh' : (7:ℝ) ≤ (D:ℝ)^3 := by norm_num at hh; linarith
  calc
    1 / (D:ℝ)^4 = (1 / (D:ℝ)^3) / D := by field_simp
    _ ≤ (1/7 : ℝ) / D := by gcongr

variable {S : ℕ} [NeZero S]

theorem forward_error (u : (ZMod S)ˣ) (x y : Signal S) (e : ℝ)
    (h : ∀ j, ‖x j - y j‖ ≤ e) (k : ZMod S) :
    ‖forward u x k - forward u y k‖ ≤ e := by
  have he : forward u x k - forward u y k = forward u (x-y) k := by
    simp [forward, mul_sub]
  rw [he]
  exact forward_bound u (x-y) e h k

def RawAccuracy (D : ℕ) (ideal : Signal S → Signal S)
    (raw : GridSignal S D → Signal S) : Prop :=
  ∀ x : GridSignal S D, disk x.val (1/2) →
    ∀ k, ‖raw x k - ideal x.val k‖ ≤ 1 / (D : ℝ)^4

omit [NeZero S] in
theorem run_accuracy {D : ℕ} (hD : 2 ≤ D) (ideal : Signal S → Signal S)
    (nonexp : ∀ x y e, (∀ j, ‖x j - y j‖ ≤ e) → ∀ k, ‖ideal x k - ideal y k‖ ≤ e)
    (raw : GridSignal S D → Signal S) (hraw : RawAccuracy D ideal raw)
    (x : Signal S) (hx : disk x (1/2)) (k : ZMod S) :
    ‖run raw x k - ideal x k‖ ≤ 3 / (D : ℝ) := by
  have hpos : 0 < D := by omega
  let y := enter D x
  have hy : disk y.val (1/2) := enter_disk hpos hx
  have h1 := hraw y hy k
  have h2 := nonexp y.val x ((10/7 : ℝ)/D) (fun j ↦ snap_error hpos (x j)) k
  have h3 := snap_error hpos (raw y k)
  have hr := residual_room hD
  have a := dist_triangle (run raw x k) (raw y k) (ideal y.val k)
  have b := dist_triangle (run raw x k) (ideal y.val k) (ideal x k)
  simp only [dist_eq_norm] at a b
  change ‖run raw x k - raw y k‖ ≤ _ at h3
  have hsum : (10/7 : ℝ)/D + (1/7 : ℝ)/D + (10/7 : ℝ)/D = 3/D := by ring
  linarith only [a, b, h1, h2, h3, hr, hsum]

theorem roundedMul_accuracy {D : ℕ} (hD : 0 < D) (x y : ℂ)
    (hx : ‖x‖ ≤ 1/2) (hy : ‖y‖ ≤ 1/2) :
    ‖roundedMul D x y - x*y‖ ≤ 3/(D : ℝ) := by
  let a := snap D x
  let b := snap D y
  have ht := dist_triangle (roundedMul D x y) (a*b) (x*y)
  simp only [dist_eq_norm] at ht
  have hi : a*b - x*y = (a-x)*b + x*(b-y) := by ring
  have h1 := norm_add_le ((a-x)*b) (x*(b-y))
  rw [← hi] at h1
  simp only [norm_mul] at h1
  have hr : 0 ≤ (10/7 : ℝ)/D := by positivity
  have h2 := mul_le_mul (snap_error hD x) ((snap_radius hD y).trans hy) (norm_nonneg _) hr
  have h3 := mul_le_mul hx (snap_error hD y) (norm_nonneg _) (by norm_num : (0:ℝ) ≤ 1/2)
  have h4 : ‖roundedMul D x y - a*b‖ ≤ (10/7 : ℝ)/D := snap_error hD _
  change ‖a-x‖ * ‖b‖ ≤ _ at h2
  change ‖x‖ * ‖b-y‖ ≤ _ at h3
  have hsum : (10/7 : ℝ)/D + ((10/7 : ℝ)/D)*(1/2) + (1/2)*((10/7 : ℝ)/D) ≤ 3/D := by
    calc
      _ = (20/7 : ℝ)/D := by ring
      _ ≤ 3/D := div_le_div_of_nonneg_right (by norm_num) (by positivity)
  linarith only [ht, h1, h2, h3, h4, hsum]

theorem dyadic_denominator (b : ℕ) : ((2 : ℕ)^b)^6 = 2^(6*b) := by
  rw [← pow_mul, Nat.mul_comm b 6]

theorem dyadic_even {b : ℕ} (hb : 0 < b) : Even ((2 : ℕ)^b) := by
  cases b with
  | zero => omega
  | succ b => exact ⟨2^b, by rw [pow_succ]; omega⟩

theorem radix_input_divides {B : ℕ} (hB : Even B) : 4*B ∣ B^6 := by
  obtain ⟨k, hk⟩ := hB
  refine ⟨8*k^5, ?_⟩
  rw [hk]
  ring

omit [NeZero S] in
theorem digit_words {D K : ℕ} (hD : 0 < D) (hK : 0 < K) (hdiv : D ∣ K)
    (a : ZMod S → ℕ) (j : ZMod S) : Represented K (digitInput D a j) := by
  obtain ⟨c, rfl⟩ := hdiv
  have hdn : (D:ℝ) ≠ 0 := by exact_mod_cast hD.ne'
  have hc : c ≠ 0 := by intro h; simp [h] at hK
  have hcn : (c:ℝ) ≠ 0 := by exact_mod_cast hc
  have he : digitInput D a j = Complex.ofReal ((a j:ℝ) / (D:ℝ)) := by
    simp [digitInput, div_eq_inv_mul]
  rw [he]
  refine ⟨((a j*c : ℕ):ℤ), 0, ?_, ?_⟩
  · rw [Complex.ofReal_re]
    push_cast
    field_simp
  · simp

omit [NeZero S] in
theorem radix_digit_words {B : ℕ} (hB : 0 < B) (hEven : Even B)
    (a : ZMod S → ℕ) (j : ZMod S) : Represented (B^6) (digitInput (4*B) a j) :=
  digit_words (by positivity) (by positivity) (radix_input_divides hEven) a j

noncomputable def radixWords {B : ℕ} (hB : 0 < B) (hEven : Even B)
    (a : ZMod S → ℕ) : GridSignal S (B^6) :=
  ⟨digitInput (4*B) a, radix_digit_words hB hEven a⟩

noncomputable def wordPacket {D : ℕ} (fw : GridSignal S D → Signal S)
    (x y : GridSignal S D) : GridSignal S D :=
  ⟨fun k ↦ snap D (snap D (fw x k) * snap D (fw y k)), fun _ ↦ snap_represented D _⟩

omit [NeZero S] in
theorem packet_on_words {D : ℕ} (hD : 0 < D) (fw : GridSignal S D → Signal S)
    (x y : GridSignal S D) :
    packet (run fw) (roundedMul D) x.val y.val = (wordPacket fw x y).val := by
  funext k
  change roundedMul D (run fw x.val k) (run fw y.val k) = _
  rw [run_on_words hD, run_on_words hD, roundedMul_words hD (snap_represented _ _) (snap_represented _ _)]
  rfl

noncomputable def wordDecode {B : ℕ} (hB : 0 < B) (hEven : Even B)
    (fw bw : GridSignal S (B^6) → Signal S) (a b : ZMod S → ℕ) (k : ZMod S) : ℕ :=
  let z := wordPacket fw (radixWords hB hEven a) (radixWords hB hEven b)
  (round ((((S : ℂ) * ((4*B : ℕ):ℂ))^2 * snap (B^6) (bw z k)).re)).toNat

omit [NeZero S] in
theorem decode_on_words {B : ℕ} (hB : 0 < B) (hEven : Even B)
    (fw bw : GridSignal S (B^6) → Signal S) (a b : ZMod S → ℕ) :
    decode B (run fw) (run bw) (roundedMul (B^6)) a b = wordDecode hB hEven fw bw a b := by
  have hD : 0 < B^6 := by positivity
  let x := radixWords hB hEven a
  let y := radixWords hB hEven b
  funext k
  change (round ((((S : ℂ) * ((4*B : ℕ):ℂ))^2 *
    run bw (packet (run fw) (roundedMul (B^6)) x.val y.val) k).re)).toNat = _
  rw [packet_on_words hD, run_on_words hD]
  rfl

theorem grid_product_at_physical_coordinates {d : ℕ} (s t : Fin d → ℕ)
    (hs : Pairwise fun i j ↦ Nat.Coprime (s i) (s j))
    (ht : ∀ i, Nat.Coprime (t i) (s i)) [∀ i, NeZero (s i)] [NeZero (∏ i, s i)]
    (B : ℕ) (hB : 32 ≤ B) (hEven : Even B) (hsize : ∏ i, s i ≤ B)
    (fw bw : GridSignal (∏ i, s i) (B^6) → MixedRankIntegrated.SourceSignal s)
    (hfw : RawAccuracy (B^6) (forward (MixedRankIntegrated.sourceUnit s t hs ht)) fw)
    (hbw : RawAccuracy (B^6) (opposite (MixedRankIntegrated.sourceUnit s t hs ht)) bw)
    (a b : ZMod (∏ i, s i) → ℕ) (ha : ∀ j, a j ≤ B) (hb : ∀ j, b j ≤ B)
    (hspan : ∀ i j, a i ≠ 0 → b j ≠ 0 → i.val + j.val < ∏ i, s i) :
    pack B (carry B 0 (ordered (wordDecode (by omega : 0 < B) hEven fw bw a b))) =
      radixValue B a * radixValue B b := by
  rw [← decode_on_words]
  have low : 2 ≤ B^6 := by calc
    2 ≤ 32^6 := by decide
    _ ≤ B^6 := by gcongr
  refine MixedRankIntegrated.product_at_physical_coordinates s t hs ht B hB hsize
    (run fw) (run bw) (roundedMul (B^6)) (3 / ((B^6:ℕ):ℝ)) (by positivity) (by simp)
    (run_accuracy low _ (forward_error _) fw hfw)
    (run_accuracy low _ (opposite_error _) bw hbw)
    (roundedMul_accuracy (by omega)) a b ha hb hspan

#print axioms snap_radius
#print axioms snap_error
#print axioms snap_finer_word
#print axioms run_accuracy
#print axioms roundedMul_accuracy
#print axioms radix_digit_words
#print axioms grid_product_at_physical_coordinates

end MixedRankPublicGrid
