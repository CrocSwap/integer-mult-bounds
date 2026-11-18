/-
WholeFloorPrice : the pricing step of WHOLEFLOOR R3 §3, in D0 and F currency,
with the owned-LATERAL correction.
Inputs (named hypotheses, each proved or quoted elsewhere):
  h_Y    : 104 <= (#helper stops) + (#main stops) + (#owned MOVEs)      [slack-rank + port lemma, R3 Thm Y]
  h_help : 2 ln 2 * sH <= helper D0                                     [FloorD0.helperD0_ge_fL]
  h_main : -400 f(8) + 2 ln 2 * sM <= main D0                           [R1 superadditivity + R3 stop price]
  owned  : D0 = -sum f(k_i), k_i in 1..9 paid; mass sum k_i <= 112 (S >= 1424); >= 16 paid moves (R1+R2).
R3 counts m = ALL owned MOVEs in h_Y but prices them with k_i >= 1 only: a LATERAL owned MOVE
(|dim b - dim a| = 0, pricekit rk = 0, cost f(0) = 0, mass 0) satisfies h_Y for free. `lat` below.
-/
import Nov15.JointCeiling
import Nov15.JunkLB2

set_option linter.unusedSectionVars false

namespace WholeFloorPrice
open JunkLB2 Real

noncomputable abbrev f (x : ℝ) : ℝ := fL x

lemma f1 : f 1 = 0 := by simp [f, fL]
lemma f8 : f 8 = 24 * Real.log 2 := by
  have : Real.log 8 = 3 * Real.log 2 := by
    rw [show (8 : ℝ) = 2 ^ 3 by norm_num, Real.log_pow]; norm_num
  simp [f, fL, this]; ring
lemma f9 : f 9 = 18 * Real.log 3 := by
  have : Real.log 9 = 2 * Real.log 3 := by
    rw [show (9 : ℝ) = 3 ^ 2 by norm_num, Real.log_pow]; norm_num
  simp [f, fL, this]; ring

/-- chord bound: f(k) <= (f 9 / 8) (k - 1) on [1, 9]. -/
lemma chord {k : ℝ} (h1 : 1 ≤ k) (h9 : k ≤ 9) : f k ≤ f 9 / 8 * (k - 1) := by
  have cvx := fL_convex
  have ha : (0 : ℝ) ≤ (9 - k) / 8 := by linarith
  have hb : (0 : ℝ) ≤ (k - 1) / 8 := by linarith
  have hab : (9 - k) / 8 + (k - 1) / 8 = (1 : ℝ) := by ring
  have := cvx.2 (show (1 : ℝ) ∈ Set.Ici (0 : ℝ) by norm_num) (show (9 : ℝ) ∈ Set.Ici (0 : ℝ) by norm_num)
    ha hb hab
  have e : ((9 - k) / 8) • (1 : ℝ) + ((k - 1) / 8) • (9 : ℝ) = k := by simp only [smul_eq_mul]; ring
  rw [e] at this
  simp only [smul_eq_mul] at this
  have h0 : fL 1 = 0 := f1
  show fL k ≤ fL 9 / 8 * (k - 1)
  rw [h0] at this; linarith

lemma two_ln2_le : 2 * Real.log 2 ≤ f 9 / 8 := by
  have h : Real.log 256 ≤ Real.log 19683 := Real.log_le_log (by norm_num) (by norm_num)
  have h1 : Real.log 256 = 8 * Real.log 2 := by
    rw [show (256 : ℝ) = 2 ^ 8 by norm_num, Real.log_pow]; norm_num
  have h2 : Real.log 19683 = 9 * Real.log 3 := by
    rw [show (19683 : ℝ) = 3 ^ 9 by norm_num, Real.log_pow]; norm_num
  rw [f9]; linarith

/-- a word's pricing summary: stops, paid owned moves, lateral owned moves, D0 parts. -/
structure Word where
  sH : ℕ
  sM : ℕ
  ow : List ℕ
  lat : ℕ
  hD0 : ℝ
  mD0 : ℝ
  oD0 : ℝ

/-- the named upstream facts. -/
structure Priced (w : Word) : Prop where
  h_help : 2 * Real.log 2 * w.sH ≤ w.hD0
  h_main : -400 * f 8 + 2 * Real.log 2 * w.sM ≤ w.mD0
  h_own : w.oD0 = -(w.ow.map fun k : ℕ => f k).sum
  h_rng : ∀ k ∈ w.ow, 1 ≤ k ∧ k ≤ 9
  h_mass : w.ow.sum ≤ 112
  h_m16 : 16 ≤ w.ow.length
  h_Y : 104 ≤ w.sH + w.sM + w.ow.length + w.lat

lemma owned_le (w : Word) (h : Priced w) :
    (w.ow.map fun k : ℕ => f k).sum ≤ f 9 / 8 * (112 - w.ow.length) := by
  have key : ∀ l : List ℕ, (∀ k ∈ l, 1 ≤ k ∧ k ≤ 9) →
      (l.map fun k : ℕ => f k).sum ≤ f 9 / 8 * ((l.sum : ℝ) - l.length) := by
    intro l
    induction l with
    | nil => intro _; simp
    | cons a l ih =>
      intro hl
      have ha := hl a List.mem_cons_self
      have := ih fun k hk => hl k (List.mem_cons_of_mem _ hk)
      have hc := chord (k := (a : ℝ)) (by exact_mod_cast ha.1) (by exact_mod_cast ha.2)
      simp only [List.map_cons, List.sum_cons, List.length_cons, Nat.cast_add, Nat.cast_one]
      nlinarith
  have := key w.ow h.h_rng
  have hm : (w.ow.sum : ℝ) ≤ 112 := by exact_mod_cast h.h_mass
  have hf9 : 0 ≤ f 9 / 8 := by rw [f9]; have := Real.log_pos (by norm_num : (1 : ℝ) < 3); positivity
  nlinarith

/-- **R3 pricing step with the lateral correction**: D0 of the native >= -400 f 8 - 12 f 9 +
2 ln 2 * max 0 (88 - lat). With `lat = 0` this is R3's -115.31 per word (+ mains). -/
theorem d0_floor (w : Word) (h : Priced w) :
    -400 * f 8 - 12 * f 9 + 2 * Real.log 2 * max 0 (88 - (w.lat : ℝ)) ≤ w.hD0 + w.mD0 + w.oD0 := by
  have ho := owned_le w h
  have hb := two_ln2_le
  have hl2 : 0 < Real.log 2 := Real.log_pos (by norm_num)
  have hm : (16 : ℝ) ≤ w.ow.length := by exact_mod_cast h.h_m16
  have hY : (104 : ℝ) ≤ w.sH + w.sM + w.ow.length + w.lat := by exact_mod_cast h.h_Y
  have hH := h.h_help
  have hM := h.h_main
  have hown := h.h_own
  set m : ℝ := (w.ow.length : ℝ)
  set a := f 9 / 8
  set b := 2 * Real.log 2
  have hb0 : 0 ≤ b := by show 0 ≤ 2 * Real.log 2; linarith
  have hsH : (0 : ℝ) ≤ w.sH := Nat.cast_nonneg _
  have hsM : (0 : ℝ) ≤ w.sM := Nat.cast_nonneg _
  have e96 : 12 * f 9 = 96 * a := by simp only [a]; ring
  rw [e96]
  have hbm : 0 ≤ (a - b) * (m - 16) := mul_nonneg (by linarith) (by linarith)
  rcases le_or_gt 0 (104 - m - w.lat) with hc | hc
  · have : max 0 (88 - (w.lat : ℝ)) = 88 - w.lat := max_eq_right (by linarith)
    rw [this]
    have hst : b * ((w.sH : ℝ) + w.sM) ≥ b * (104 - m - w.lat) :=
      mul_le_mul_of_nonneg_left (by linarith) (by linarith)
    nlinarith
  · have hmx : max 0 (88 - (w.lat : ℝ)) ≤ m - 16 := max_le (by linarith) (by linarith)
    have h1 : b * max 0 (88 - (w.lat : ℝ)) ≤ b * (m - 16) := mul_le_mul_of_nonneg_left hmx hb0
    have : 0 ≤ b * ((w.sH : ℝ) + w.sM) := by positivity
    nlinarith

/-! ### the lateral counterexample to R3's reading -/

/-- 12 owned MOVEs of rank 9 and 4 of rank 1 (mass 112), no stops, and 88 LATERAL owned MOVEs. -/
noncomputable def cex : Word where
  sH := 0
  sM := 0
  ow := List.replicate 12 9 ++ List.replicate 4 1
  lat := 88
  hD0 := 0
  mD0 := -400 * f 8
  oD0 := -(12 * f 9)

theorem cex_priced : Priced cex := by
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · simp [cex]
  · simp [cex]
  · simp [cex, f1, List.sum_replicate]; ring
  · intro k hk
    simp only [cex, List.mem_append, List.mem_replicate] at hk
    omega
  · simp [cex]
  · simp [cex]
  · simp [cex]

/-- R3's claimed per-word value (-115.31 = -12 f 9 + 88 * 2 ln 2) is NOT a floor for admissible
words once lateral owned MOVEs are allowed. -/
theorem r3_stops_not_forced :
    ¬ (-400 * f 8 - 12 * f 9 + 2 * Real.log 2 * 88 ≤ cex.hD0 + cex.mD0 + cex.oD0) := by
  have hl2 : 0 < Real.log 2 := Real.log_pos (by norm_num)
  simp only [cex]
  intro h; linarith

/-- and the corrected floor (lat = 88) is exactly the R2 value -400 f 8 - 12 f 9, attained. -/
theorem cex_attains : cex.hD0 + cex.mD0 + cex.oD0 = -400 * f 8 - 12 * f 9 := by
  simp [cex]; ring

/-! ### F currency: the native floor Nfl of JointCeiling, derived, with the lateral correction -/

open JointCeiling CallerCost in
/-- corrected native floor: `lat` lateral owned MOVEs remove `lat` forced stops. `lat = 0` is JointCeiling.Nfl. -/
noncomputable def NflL (lat : ℕ) (s : ℝ) : ℝ :=
  400 * (8 : ℝ) ^ s + 16 + max 0 (88 - (lat : ℝ)) * (2 - (2 : ℝ) ^ s)

open JointCeiling in
theorem NflL_zero (s : ℝ) : NflL 0 s = Nfl s := by
  simp [NflL, Nfl]

/-- **F-currency pricing**: for s in [0,1], if the native's F obeys
`F <= -400 8^s - (2 - 2^s)(stops) - (#paid owned)` (mains subadditivity, owned rank >= 1, stop price
2^s - 2 = F-charge of a convex-gap stop) and R1/R2 (>= 16 paid) and Thm Y, then F <= -NflL lat s. -/
theorem F_floor (s : ℝ) (hs0 : 0 ≤ s) (hs1 : s ≤ 1) (st mp lat : ℕ) (Fn : ℝ)
    (hF : Fn ≤ -400 * (8 : ℝ) ^ s - (2 - (2 : ℝ) ^ s) * st - mp)
    (hm : 16 ≤ mp) (hY : 104 ≤ st + mp + lat) : Fn ≤ -NflL lat s := by
  have hu1 : (1 : ℝ) ≤ (2 : ℝ) ^ s := Real.one_le_rpow (by norm_num) hs0
  have hu2 : (2 : ℝ) ^ s ≤ 2 := by
    have := Real.rpow_le_rpow_of_exponent_le (show (1 : ℝ) ≤ 2 by norm_num) hs1
    simpa using this
  set c : ℝ := 2 - (2 : ℝ) ^ s with hc
  have hc0 : 0 ≤ c := by linarith
  have hc1 : c ≤ 1 := by linarith
  have hm' : (16 : ℝ) ≤ mp := by exact_mod_cast hm
  have hY' : (104 : ℝ) ≤ st + mp + lat := by exact_mod_cast hY
  have hst : (0 : ℝ) ≤ st := Nat.cast_nonneg _
  simp only [NflL]
  rw [← hc]
  rcases le_or_gt 0 (104 - (mp : ℝ) - lat) with h | h
  · have hmx : max 0 (88 - (lat : ℝ)) = 88 - lat := max_eq_right (by linarith)
    rw [hmx]
    have h1 : c * (104 - mp - lat) ≤ c * st := mul_le_mul_of_nonneg_left (by linarith) hc0
    have h2 : (1 - c) * (mp - 16) ≥ 0 := mul_nonneg (by linarith) (by linarith)
    nlinarith
  · have hmx : max 0 (88 - (lat : ℝ)) ≤ mp - 16 := max_le (by linarith) (by linarith)
    have hM0 : 0 ≤ max 0 (88 - (lat : ℝ)) := le_max_left _ _
    have h1 : c * max 0 (88 - (lat : ℝ)) ≤ 1 * max 0 (88 - (lat : ℝ)) :=
      mul_le_mul_of_nonneg_right hc1 hM0
    have : 0 ≤ c * st := mul_nonneg hc0 hst
    nlinarith

open JointCeiling CallerCost in
/-- the fixed #7113 caller C(8|9) at 17 calls: any native meeting the (lateral-free) floor has F < 0
at t = .0205, i.e. the `control_neg` bracket of JointCeiling transfers to every priced native. -/
theorem fixed_caller_point (n : Inv) (hN : ∀ s : ℝ, 0 ≤ s → s ≤ 1 → Finv s n ≤ -Nfl s) :
    Finv (1 - (205 : ℝ) / 10000) (invoice (caller 6 7) n 17) < 0 := by
  have hs0 : (0 : ℝ) ≤ 1 - 205 / 10000 := by norm_num
  have hs1 : (1 : ℝ) - 205 / 10000 ≤ 1 := by norm_num
  have h1 := hN _ hs0 hs1
  have h2 := invoice_F (1 - 205 / 10000) (caller 6 7) n 17
  have h3 := invoice_F (1 - 205 / 10000) (caller 6 7) natFloor 17
  have h4 := natFloor_F (1 - 205 / 10000)
  have h5 := control_bracket.2
  have h6 : Finv (1 - (205 : ℝ) / 10000) I89 = Finv (1 - 205 / 10000) (invoice (caller 6 7) natFloor 17) := rfl
  push_cast at h2 h3
  nlinarith

end WholeFloorPrice

#print axioms WholeFloorPrice.d0_floor
#print axioms WholeFloorPrice.cex_priced
#print axioms WholeFloorPrice.r3_stops_not_forced
#print axioms WholeFloorPrice.F_floor
#print axioms WholeFloorPrice.fixed_caller_point
