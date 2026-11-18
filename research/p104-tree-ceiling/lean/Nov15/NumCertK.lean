import Mathlib.Analysis.SpecialFunctions.Log.Deriv
import Mathlib.Analysis.SpecialFunctions.Pow.Deriv
import Mathlib.Analysis.Complex.ExponentialBounds
import Mathlib.Analysis.Calculus.Deriv.MeanValue

/-!
NUMCERT-K .  Kernel-checked interval arithmetic for the numeric crossing hypotheses of the kappa ceilings.
Section 1: rational enclosures of ln r (chain ln(c+2) = ln(c+1) + 2 atanh(1/(2c+3)) with an explicit geometric tail) and of exp (Taylor of x/8, explicit
remainder `Real.exp_bound'`, eighth power), packaged as `pow_lo`/`pow_hi`: r^s in [pLo r a, pHi r b] for s in [a,b].  Kernel only; no native_decide.
-/

namespace NumCertK
open Finset

def SC : ℚ := 10 ^ 30
def rdn (q : ℚ) : ℚ := ((⌊q * SC⌋ : ℤ) : ℚ) / SC
def rup (q : ℚ) : ℚ := ((⌈q * SC⌉ : ℤ) : ℚ) / SC
theorem SC_pos : (0 : ℚ) < SC := by unfold SC; positivity
theorem rdn_le (q : ℚ) : rdn q ≤ q := by
  unfold rdn; rw [div_le_iff₀ SC_pos]; exact Int.floor_le _
theorem le_rup (q : ℚ) : q ≤ rup q := by
  unfold rup; rw [le_div_iff₀ SC_pos]; exact Int.le_ceil _
theorem rdn_nonneg {q : ℚ} (h : 0 ≤ q) : 0 ≤ rdn q := by
  unfold rdn
  have : (0 : ℤ) ≤ ⌊q * SC⌋ := Int.floor_nonneg.mpr (mul_nonneg h SC_pos.le)
  have h2 : (0 : ℚ) ≤ ((⌊q * SC⌋ : ℤ) : ℚ) := by exact_mod_cast this
  exact div_nonneg h2 SC_pos.le
theorem rup_nonneg {q : ℚ} (h : 0 ≤ q) : 0 ≤ rup q := le_trans h (le_rup q)
theorem rdn_mono {p q : ℚ} (h : p ≤ q) : rdn p ≤ rdn q := by
  unfold rdn
  apply div_le_div_of_nonneg_right _ SC_pos.le
  exact_mod_cast Int.floor_mono (mul_le_mul_of_nonneg_right h SC_pos.le)
theorem rup_mono {p q : ℚ} (h : p ≤ q) : rup p ≤ rup q := by
  unfold rup
  apply div_le_div_of_nonneg_right _ SC_pos.le
  exact_mod_cast Int.ceil_mono (mul_le_mul_of_nonneg_right h SC_pos.le)

/-! ### 1. ln -/
def aS (a n : ℕ) : ℚ :=
  ∑ k ∈ range n, 2 * (1 / (2 * (k : ℚ) + 1)) * (1 / (2 * (a : ℚ) + 1)) ^ (2 * k + 1)
def aTail (a n : ℕ) : ℚ :=
  2 * (1 / (2 * (a : ℚ) + 1)) ^ (2 * n + 1) / ((2 * (n : ℚ) + 1) * (1 - (1 / (2 * (a : ℚ) + 1)) ^ 2))

theorem atanh_bounds (a n : ℕ) (ha : 0 < a) :
    ((aS a n : ℚ) : ℝ) ≤ Real.log (1 + (a : ℝ)⁻¹) ∧
    Real.log (1 + (a : ℝ)⁻¹) ≤ ((aS a n : ℚ) : ℝ) + ((aTail a n : ℚ) : ℝ) := by
  have haR : (0 : ℝ) < a := by exact_mod_cast ha
  have hs := Real.hasSum_log_one_add_inv haR
  set y : ℝ := 1 / (2 * (a : ℝ) + 1) with hy
  have hy0 : 0 < y := by rw [hy]; positivity
  have hy1 : y < 1 := by
    rw [hy, div_lt_one (by positivity)]; have : (1:ℝ) ≤ a := by exact_mod_cast ha
    linarith
  set f : ℕ → ℝ := fun k => 2 * (1 / (2 * (k : ℝ) + 1)) * y ^ (2 * k + 1) with hf
  have hS : ((aS a n : ℚ) : ℝ) = ∑ k ∈ range n, f k := by
    simp only [aS, hf, hy]; push_cast; rfl
  have ht := (hasSum_nat_add_iff' n).mpr hs
  rw [hS]
  have hfpos : ∀ k, 0 ≤ f k := fun k => by simp only [hf]; positivity
  constructor
  · have := ht.nonneg (fun k => hfpos (k + n))
    linarith
  · set c : ℝ := 2 * (1 / (2 * (n : ℝ) + 1)) * y ^ (2 * n + 1) with hc
    have hy2 : y ^ 2 < 1 := by nlinarith
    have hg : HasSum (fun k : ℕ => c * (y ^ 2) ^ k) (c * (1 - y ^ 2)⁻¹) :=
      (hasSum_geometric_of_lt_one (by positivity) hy2).mul_left c
    have hle : ∀ k : ℕ, f (k + n) ≤ c * (y ^ 2) ^ k := by
      intro k
      simp only [hf, hc]
      have e : y ^ (2 * (k + n) + 1) = y ^ (2 * n + 1) * (y ^ 2) ^ k := by
        rw [← pow_mul]; rw [← pow_add]; congr 1; ring
      push_cast
      rw [e]
      have h1 : 1 / (2 * ((k : ℝ) + n) + 1) ≤ 1 / (2 * (n : ℝ) + 1) := by
        apply one_div_le_one_div_of_le (by positivity); nlinarith [(Nat.cast_nonneg k : (0:ℝ) ≤ k)]
      have h2 : 0 ≤ y ^ (2 * n + 1) * (y ^ 2) ^ k := by positivity
      nlinarith [mul_le_mul_of_nonneg_right h1 h2]
    have := hasSum_le hle ht hg
    have hT : ((aTail a n : ℚ) : ℝ) = c * (1 - y ^ 2)⁻¹ := by
      simp only [aTail, hc, hy]; push_cast
      have : (1 - (1 / (2 * (a : ℝ) + 1)) ^ 2) ≠ 0 := by
        have := hy2; rw [hy] at this; intro h; linarith
      field_simp
    rw [hT]; linarith

def N : ℕ := 36
def lnLoC : ℕ → ℚ
  | 0 => 0
  | c + 1 => lnLoC c + rdn (aS (c + 1) N)
def lnHiC : ℕ → ℚ
  | 0 => 0
  | c + 1 => lnHiC c + rup (aS (c + 1) N + aTail (c + 1) N)
/-- bounds for ln r (r >= 1) -/
def lnLo (r : ℕ) : ℚ := lnLoC (r - 1)
def lnHi (r : ℕ) : ℚ := lnHiC (r - 1)

theorem aS_nonneg (a n : ℕ) : 0 ≤ aS a n := by
  unfold aS; apply Finset.sum_nonneg; intro k _; positivity
theorem aTail_nonneg (a n : ℕ) : 0 ≤ aTail a n := by
  unfold aTail
  apply div_nonneg (by positivity)
  apply mul_nonneg (by positivity)
  by_cases h : a = 0
  · subst h; simp
  · have : (1:ℚ) ≤ a := by exact_mod_cast Nat.pos_of_ne_zero h
    have h1 : 1 / (2 * (a : ℚ) + 1) ≤ 1 := by rw [div_le_one (by positivity)]; linarith
    have h0 : 0 ≤ 1 / (2 * (a : ℚ) + 1) := by positivity
    nlinarith

theorem ln_chain (c : ℕ) :
    ((lnLoC c : ℚ) : ℝ) ≤ Real.log ((c : ℝ) + 1) ∧ Real.log ((c : ℝ) + 1) ≤ ((lnHiC c : ℚ) : ℝ) := by
  induction c with
  | zero => simp [lnLoC, lnHiC]
  | succ c ih =>
    obtain ⟨h1, h2⟩ := ih
    have hc : (0 : ℝ) < (c : ℝ) + 1 := by positivity
    have e : Real.log (((c + 1 : ℕ) : ℝ) + 1) = Real.log ((c : ℝ) + 1) + Real.log (1 + (((c + 1 : ℕ) : ℝ))⁻¹) := by
      rw [← Real.log_mul hc.ne' (by positivity)]
      congr 1; push_cast; field_simp
    obtain ⟨b1, b2⟩ := atanh_bounds (c + 1) N (Nat.succ_pos c)
    rw [e]
    constructor
    · have : ((rdn (aS (c + 1) N) : ℚ) : ℝ) ≤ ((aS (c + 1) N : ℚ) : ℝ) := by exact_mod_cast rdn_le _
      simp only [lnLoC]; push_cast at *; linarith
    · have : ((aS (c + 1) N + aTail (c + 1) N : ℚ) : ℝ) ≤ ((rup (aS (c + 1) N + aTail (c + 1) N) : ℚ) : ℝ) :=
        by exact_mod_cast le_rup _
      simp only [lnHiC]; push_cast at *; linarith

theorem lnLo_le (r : ℕ) (hr : 1 ≤ r) : ((lnLo r : ℚ) : ℝ) ≤ Real.log r := by
  have h := (ln_chain (r - 1)).1
  unfold lnLo
  have : ((r - 1 : ℕ) : ℝ) + 1 = r := by rw [Nat.cast_sub hr]; simp
  rwa [this] at h
theorem le_lnHi (r : ℕ) (hr : 1 ≤ r) : Real.log r ≤ ((lnHi r : ℚ) : ℝ) := by
  have h := (ln_chain (r - 1)).2
  unfold lnHi
  have : ((r - 1 : ℕ) : ℝ) + 1 = r := by rw [Nat.cast_sub hr]; simp
  rwa [this] at h

theorem lnLoC_nonneg (c : ℕ) : 0 ≤ lnLoC c := by
  induction c with
  | zero => simp [lnLoC]
  | succ c ih => simp only [lnLoC]; exact add_nonneg ih (rdn_nonneg (aS_nonneg _ _))
theorem lnHiC_mono : Monotone lnHiC := by
  apply monotone_nat_of_le_succ; intro c
  simp only [lnHiC]
  have := rup_nonneg (add_nonneg (aS_nonneg (c + 1) N) (aTail_nonneg (c + 1) N))
  linarith
theorem lnLo_nonneg (r : ℕ) : 0 ≤ lnLo r := lnLoC_nonneg _
theorem lnHi_nonneg (r : ℕ) : 0 ≤ lnHi r := by
  have : (0:ℚ) ≤ lnHiC 0 := by simp [lnHiC]
  exact le_trans this (lnHiC_mono (Nat.zero_le _))

theorem lnHi_145 : lnHi 145 ≤ 5 := by unfold lnHi; decide +kernel
theorem lnHi_le_5 (r : ℕ) (hr : r ≤ 145) : lnHi r ≤ 5 := by
  refine le_trans ?_ lnHi_145
  exact lnHiC_mono (by omega)

/-! ### 2. exp -/
def NE : ℕ := 24
def eS (y : ℚ) : ℚ := ∑ m ∈ range NE, y ^ m / (Nat.factorial m : ℚ)
def eR (y : ℚ) : ℚ := y ^ NE * ((NE : ℚ) + 1) / ((Nat.factorial NE : ℚ) * NE)
/-- lower / upper enclosure of exp x: (Taylor of x/8)^8 with outward fixed-point rounding -/
def eLo (x : ℚ) : ℚ := rdn ((rdn (eS (x / 8))) ^ 8)
def eHi (x : ℚ) : ℚ := rup ((rup (eS (x / 8) + eR (x / 8))) ^ 8)

theorem eLo_le (x : ℚ) (hx : 0 ≤ x) : ((eLo x : ℚ) : ℝ) ≤ Real.exp x := by
  have hx0 : (0:ℝ) ≤ x := by exact_mod_cast hx
  have hy : (0 : ℝ) ≤ (x : ℝ) / 8 := by positivity
  have h1 := Real.sum_le_exp_of_nonneg hy NE
  have hS : ((eS (x / 8) : ℚ) : ℝ) = ∑ m ∈ range NE, ((x : ℝ) / 8) ^ m / (Nat.factorial m : ℝ) := by
    simp only [eS]; push_cast; rfl
  have h0 : 0 ≤ eS (x / 8) := by
    unfold eS; apply Finset.sum_nonneg; intro m _; have : 0 ≤ x / 8 := by positivity
    positivity
  have h2 : ((rdn (eS (x / 8)) : ℚ) : ℝ) ≤ Real.exp ((x : ℝ) / 8) := by
    have : ((rdn (eS (x / 8)) : ℚ) : ℝ) ≤ ((eS (x / 8) : ℚ) : ℝ) := by exact_mod_cast rdn_le _
    linarith
  have h3 : (0 : ℝ) ≤ ((rdn (eS (x / 8)) : ℚ) : ℝ) := by exact_mod_cast rdn_nonneg h0
  have h4 : (((rdn (eS (x / 8))) ^ 8 : ℚ) : ℝ) ≤ Real.exp x := by
    push_cast
    calc ((rdn (eS (x / 8)) : ℚ) : ℝ) ^ 8 ≤ (Real.exp ((x : ℝ) / 8)) ^ 8 := pow_le_pow_left₀ h3 h2 8
      _ = Real.exp x := by rw [← Real.exp_nat_mul]; congr 1; push_cast; ring
  have h5 : ((rdn ((rdn (eS (x / 8))) ^ 8) : ℚ) : ℝ) ≤ (((rdn (eS (x / 8))) ^ 8 : ℚ) : ℝ) := by
    exact_mod_cast rdn_le _
  unfold eLo; linarith

theorem le_eHi (x : ℚ) (hx : 0 ≤ x) (hx8 : x ≤ 8) : Real.exp x ≤ ((eHi x : ℚ) : ℝ) := by
  have hx0 : (0:ℝ) ≤ x := by exact_mod_cast hx
  have hx8' : (x:ℝ) ≤ 8 := by exact_mod_cast hx8
  have hy : (0 : ℝ) ≤ (x : ℝ) / 8 := by positivity
  have hy1 : (x : ℝ) / 8 ≤ 1 := by linarith
  have h1 := Real.exp_bound' hy hy1 (n := NE) (by unfold NE; norm_num)
  have hS : ((eS (x / 8) + eR (x / 8) : ℚ) : ℝ) =
      (∑ m ∈ range NE, ((x : ℝ) / 8) ^ m / (Nat.factorial m : ℝ)) +
        ((x : ℝ) / 8) ^ NE * ((NE : ℝ) + 1) / ((Nat.factorial NE : ℝ) * NE) := by
    simp only [eS, eR]; push_cast; rfl
  have h2 : Real.exp ((x : ℝ) / 8) ≤ ((rup (eS (x / 8) + eR (x / 8)) : ℚ) : ℝ) := by
    have : ((eS (x / 8) + eR (x / 8) : ℚ) : ℝ) ≤ ((rup (eS (x / 8) + eR (x / 8)) : ℚ) : ℝ) := by
      exact_mod_cast le_rup _
    linarith
  have h3 : Real.exp x ≤ (((rup (eS (x / 8) + eR (x / 8))) ^ 8 : ℚ) : ℝ) := by
    push_cast
    calc Real.exp x = (Real.exp ((x : ℝ) / 8)) ^ 8 := by rw [← Real.exp_nat_mul]; congr 1; push_cast; ring
      _ ≤ _ := pow_le_pow_left₀ (Real.exp_pos _).le h2 8
  have h5 : (((rup (eS (x / 8) + eR (x / 8))) ^ 8 : ℚ) : ℝ) ≤ ((rup ((rup (eS (x / 8) + eR (x / 8))) ^ 8) : ℚ) : ℝ) := by
    exact_mod_cast le_rup _
  unfold eHi; linarith

/-! ### 3. r^s on an interval of exponents -/
def pLo (r : ℕ) (a : ℚ) : ℚ := eLo (rdn (a * lnLo r))
def pHi (r : ℕ) (b : ℚ) : ℚ := eHi (rup (b * lnHi r))

/-- **rpow bound (lower)**: for 1 <= r, 0 <= a <= s: pLo r a <= r^s. -/
theorem pow_lo (r : ℕ) (hr : 1 ≤ r) (a : ℚ) (ha : 0 ≤ a) (s : ℝ) (hs : (a : ℝ) ≤ s) :
    ((pLo r a : ℚ) : ℝ) ≤ (r : ℝ) ^ s := by
  have hr1 : (1 : ℝ) ≤ r := by exact_mod_cast hr
  have hrp : (0 : ℝ) < r := by linarith
  have ha0 : (0:ℝ) ≤ a := by exact_mod_cast ha
  have h1 : (r : ℝ) ^ (a : ℝ) ≤ (r : ℝ) ^ s := Real.rpow_le_rpow_of_exponent_le hr1 hs
  have hx0 : 0 ≤ rdn (a * lnLo r) := rdn_nonneg (mul_nonneg ha (lnLo_nonneg r))
  have h2 := eLo_le _ hx0
  have h3 : ((rdn (a * lnLo r) : ℚ) : ℝ) ≤ Real.log r * a := by
    have a1 : ((rdn (a * lnLo r) : ℚ) : ℝ) ≤ ((a * lnLo r : ℚ) : ℝ) := by exact_mod_cast rdn_le _
    have a2 := lnLo_le r hr
    push_cast at a1
    nlinarith
  have e := Real.rpow_def_of_pos hrp (a : ℝ)
  unfold pLo
  have := Real.exp_le_exp.mpr h3
  linarith

/-- **rpow bound (upper)**: for 1 <= r <= 145, 0 <= s <= b <= 1: r^s <= pHi r b. -/
theorem pow_hi (r : ℕ) (hr : 1 ≤ r) (hr2 : r ≤ 145) (b : ℚ) (hb0 : 0 ≤ b) (hb1 : b ≤ 1) (s : ℝ)
    (hs : s ≤ (b : ℝ)) :
    (r : ℝ) ^ s ≤ ((pHi r b : ℚ) : ℝ) := by
  have hr1 : (1 : ℝ) ≤ r := by exact_mod_cast hr
  have hrp : (0 : ℝ) < r := by linarith
  have h1 : (r : ℝ) ^ s ≤ (r : ℝ) ^ (b : ℝ) := Real.rpow_le_rpow_of_exponent_le hr1 hs
  have hx0 : 0 ≤ rup (b * lnHi r) := rup_nonneg (mul_nonneg hb0 (lnHi_nonneg r))
  have h5 := lnHi_le_5 r hr2
  have hx8 : rup (b * lnHi r) ≤ 8 := by
    have : b * lnHi r ≤ 5 := by nlinarith [lnHi_nonneg r]
    have h6 := rup_mono this
    have h7 : rup 5 = 5 := by unfold rup SC; norm_num
    linarith
  have h2 := le_eHi _ hx0 hx8
  have h3 : Real.log r * b ≤ ((rup (b * lnHi r) : ℚ) : ℝ) := by
    have a1 : ((b * lnHi r : ℚ) : ℝ) ≤ ((rup (b * lnHi r) : ℚ) : ℝ) := by exact_mod_cast le_rup _
    have a2 := le_lnHi r hr
    have hb : (0:ℝ) ≤ b := by exact_mod_cast hb0
    push_cast at a1
    nlinarith
  have e := Real.rpow_def_of_pos hrp (b : ℝ)
  unfold pHi
  have := Real.exp_le_exp.mpr h3
  linarith

/-! ### 4. F(s) = sum c_r r^s: enclosures of F and F', monotonicity -/
abbrev CF := List (ℕ × ℤ)
noncomputable def Fc (cf : CF) (s : ℝ) : ℝ := (cf.map fun p => (p.2 : ℝ) * (p.1 : ℝ) ^ s).sum
noncomputable def dFc (cf : CF) (s : ℝ) : ℝ := (cf.map fun p => (p.2 : ℝ) * (Real.log p.1 * (p.1 : ℝ) ^ s)).sum
def okR (cf : CF) : Prop := ∀ p ∈ cf, 1 ≤ p.1 ∧ p.1 ≤ 145
instance (cf : CF) : Decidable (okR cf) := by unfold okR; infer_instance
/-- upper bound of F on s in [a,b] -/
def Fup (cf : CF) (a b : ℚ) : ℚ :=
  (cf.map fun p => if 0 ≤ p.2 then (p.2 : ℚ) * pHi p.1 b else (p.2 : ℚ) * pLo p.1 a).sum
/-- lower bound of F' on s in [a,b] -/
def dLo (cf : CF) (a b : ℚ) : ℚ :=
  (cf.map fun p => if 0 ≤ p.2 then (p.2 : ℚ) * (lnLo p.1 * pLo p.1 a)
    else (p.2 : ℚ) * (lnHi p.1 * pHi p.1 b)).sum

theorem Fc_le (cf : CF) (hok : okR cf) (a b : ℚ) (ha : 0 ≤ a) (hb1 : b ≤ 1) (s : ℝ)
    (h1 : (a : ℝ) ≤ s) (h2 : s ≤ (b : ℝ)) : Fc cf s ≤ ((Fup cf a b : ℚ) : ℝ) := by
  have ha0 : (0:ℝ) ≤ a := by exact_mod_cast ha
  have hb0 : 0 ≤ b := by
    have : (0:ℝ) ≤ b := by linarith
    exact_mod_cast this
  induction cf with
  | nil => simp [Fc, Fup]
  | cons p l ih =>
    have hp := hok p (by simp)
    have hl : okR l := fun q hq => hok q (by simp [hq])
    have ih := ih hl
    simp only [Fc, Fup, List.map_cons, List.sum_cons] at ih ⊢
    rw [Rat.cast_add]
    have hlo := pow_lo p.1 hp.1 a ha s h1
    have hhi := pow_hi p.1 hp.1 hp.2 b hb0 hb1 s h2
    split_ifs with hc
    · have hc' : (0:ℝ) ≤ p.2 := by exact_mod_cast hc
      simp only [Rat.cast_mul, Rat.cast_intCast]
      nlinarith [mul_le_mul_of_nonneg_left hhi hc']
    · have hc' : (p.2:ℝ) ≤ 0 := by exact_mod_cast (show p.2 ≤ 0 by omega)
      simp only [Rat.cast_mul, Rat.cast_intCast]
      nlinarith [mul_le_mul_of_nonpos_left hlo hc']

theorem dFc_ge (cf : CF) (hok : okR cf) (a b : ℚ) (ha : 0 ≤ a) (hb1 : b ≤ 1) (s : ℝ)
    (h1 : (a : ℝ) ≤ s) (h2 : s ≤ (b : ℝ)) : ((dLo cf a b : ℚ) : ℝ) ≤ dFc cf s := by
  have ha0 : (0:ℝ) ≤ a := by exact_mod_cast ha
  have hb0 : 0 ≤ b := by
    have : (0:ℝ) ≤ b := by linarith
    exact_mod_cast this
  induction cf with
  | nil => simp [dFc, dLo]
  | cons p l ih =>
    have hp := hok p (by simp)
    have hl : okR l := fun q hq => hok q (by simp [hq])
    have ih := ih hl
    simp only [dFc, dLo, List.map_cons, List.sum_cons] at ih ⊢
    rw [Rat.cast_add]
    have hlo := pow_lo p.1 hp.1 a ha s h1
    have hhi := pow_hi p.1 hp.1 hp.2 b hb0 hb1 s h2
    have hr1 : (1:ℝ) ≤ p.1 := by exact_mod_cast hp.1
    have hL0 : 0 ≤ Real.log p.1 := Real.log_nonneg hr1
    have hl1 := lnLo_le p.1 hp.1
    have hl2 := le_lnHi p.1 hp.1
    have hn0 : (0:ℝ) ≤ ((lnLo p.1 : ℚ) : ℝ) := by exact_mod_cast lnLo_nonneg p.1
    have hn1 : (0:ℝ) ≤ ((lnHi p.1 : ℚ) : ℝ) := by exact_mod_cast lnHi_nonneg p.1
    have hq0 : (0:ℝ) ≤ ((pLo p.1 a : ℚ) : ℝ) := by
      have : 0 ≤ pLo p.1 a := by
        unfold pLo eLo
        apply rdn_nonneg; apply pow_nonneg; apply rdn_nonneg
        unfold eS; apply Finset.sum_nonneg; intro m _
        have : 0 ≤ rdn (a * lnLo p.1) / 8 := div_nonneg (rdn_nonneg (mul_nonneg ha (lnLo_nonneg _))) (by norm_num)
        positivity
      exact_mod_cast this
    have hrs : (0:ℝ) ≤ (p.1 : ℝ) ^ s := by positivity
    split_ifs with hc
    · have hc' : (0:ℝ) ≤ p.2 := by exact_mod_cast hc
      simp only [Rat.cast_mul, Rat.cast_intCast]
      have m1 : ((lnLo p.1 : ℚ) : ℝ) * ((pLo p.1 a : ℚ) : ℝ) ≤ Real.log p.1 * (p.1 : ℝ) ^ s :=
        mul_le_mul hl1 hlo hq0 hL0
      nlinarith [mul_le_mul_of_nonneg_left m1 hc']
    · have hc' : (p.2:ℝ) ≤ 0 := by exact_mod_cast (show p.2 ≤ 0 by omega)
      simp only [Rat.cast_mul, Rat.cast_intCast]
      have m1 : Real.log p.1 * (p.1 : ℝ) ^ s ≤ ((lnHi p.1 : ℚ) : ℝ) * ((pHi p.1 b : ℚ) : ℝ) :=
        mul_le_mul hl2 hhi hrs hn1
      nlinarith [mul_le_mul_of_nonpos_left m1 hc']

theorem Fc_hasDerivAt (cf : CF) (hok : okR cf) (s : ℝ) : HasDerivAt (Fc cf) (dFc cf s) s := by
  induction cf with
  | nil => simp only [Fc, dFc, List.map_nil, List.sum_nil]; exact hasDerivAt_const s (0 : ℝ)
  | cons p l ih =>
    have hp := hok p (by simp)
    have hl : okR l := fun q hq => hok q (by simp [hq])
    have ih := ih hl
    have hrp : (0:ℝ) < p.1 := by have : (1:ℝ) ≤ p.1 := by exact_mod_cast hp.1
                                 linarith
    have h1 := ((Real.hasStrictDerivAt_const_rpow hrp s).hasDerivAt.const_mul (p.2 : ℝ)).add ih
    have e : Fc (p :: l) = fun s => (p.2 : ℝ) * (p.1 : ℝ) ^ s + Fc l s := by
      funext s; simp [Fc]
    have e2 : dFc (p :: l) s = (p.2 : ℝ) * ((p.1 : ℝ) ^ s * Real.log p.1) + dFc l s := by
      simp only [dFc, List.map_cons, List.sum_cons]; ring
    rw [e, e2]; exact h1

/-- if F' >= dLo > 0 on [a,b] then F(s) <= F(b) on [a,b] -/
theorem Fc_mono (cf : CF) (hok : okR cf) (a b : ℚ) (ha : 0 ≤ a) (hb1 : b ≤ 1) (hd : 0 < dLo cf a b)
    (s : ℝ) (h1 : (a : ℝ) ≤ s) (h2 : s ≤ (b : ℝ)) : Fc cf s ≤ Fc cf b := by
  have hab : (a : ℝ) ≤ b := le_trans h1 h2
  have hcont : ContinuousOn (Fc cf) (Set.Icc (a : ℝ) b) :=
    fun x _ => (Fc_hasDerivAt cf hok x).continuousAt.continuousWithinAt
  have hm : StrictMonoOn (Fc cf) (Set.Icc (a : ℝ) b) := by
    apply strictMonoOn_of_deriv_pos (convex_Icc _ _) hcont
    intro x hx
    rw [interior_Icc] at hx
    rw [(Fc_hasDerivAt cf hok x).deriv]
    have := dFc_ge cf hok a b ha hb1 x hx.1.le hx.2.le
    have hd' : (0:ℝ) < ((dLo cf a b : ℚ) : ℝ) := by exact_mod_cast hd
    linarith
  exact hm.monotoneOn ⟨h1, h2⟩ ⟨hab, le_refl _⟩ h2

theorem Fc_neg_piece (cf : CF) (hok : okR cf) (a b : ℚ) (ha : 0 ≤ a) (hb1 : b ≤ 1) (h : Fup cf a b < 0)
    (s : ℝ) (h1 : (a : ℝ) ≤ s) (h2 : s ≤ (b : ℝ)) : Fc cf s < 0 := by
  have := Fc_le cf hok a b ha hb1 s h1 h2
  have h' : ((Fup cf a b : ℚ) : ℝ) < 0 := by exact_mod_cast h
  linarith

end NumCertK

#print axioms NumCertK.pow_lo
#print axioms NumCertK.pow_hi
#print axioms NumCertK.Fc_mono
