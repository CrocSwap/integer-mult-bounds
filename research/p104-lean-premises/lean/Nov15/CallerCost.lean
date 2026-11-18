/-
CALLER-COST .  Closed form of the CALLERCO caller invoice (internal notes `caller`, ck.py),
histograms as lists of (rank, count) terms, S = sum r*(T-P), D0 = sum (T-P)*f(r), f r = r ln r (FloorD0 convention),
invoice = caller + calls * native, reproduction of the #7113 caller at 8|9, S(k) = 3408 k - 208, single-crossing in the native
D0 per call, and the abstract composition lemma.  Kernel only, no sorry / native_decide.
-/
import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Tactic

namespace CallerCost
open Real

/-- a histogram: list of (rank, count) terms -/
abbrev Hist := List (ℕ × ℕ)

def cnt (l : Hist) (r : ℕ) : ℕ := (l.map fun p => if p.1 = r then p.2 else 0).sum
def Sh (l : Hist) : ℤ := (l.map fun p => (p.1 : ℤ) * p.2).sum
noncomputable def fL (r : ℕ) : ℝ := (r : ℝ) * Real.log r
noncomputable def Dh (l : Hist) : ℝ := (l.map fun p => (p.2 : ℝ) * fL p.1).sum
def scale (L : ℕ) (l : Hist) : Hist := l.map fun p => (p.1, L * p.2)

structure Inv where
  T : Hist
  P : Hist

def Sinv (i : Inv) : ℤ := Sh i.T - Sh i.P
noncomputable def Dinv (i : Inv) : ℝ := Dh i.T - Dh i.P
/-- invoice = caller + L * native (pricekit.invoice, counts scaled by L) -/
def invoice (c n : Inv) (L : ℕ) : Inv := ⟨c.T ++ scale L n.T, c.P ++ scale L n.P⟩

theorem Sh_append (l m : Hist) : Sh (l ++ m) = Sh l + Sh m := by simp [Sh]
theorem Dh_append (l m : Hist) : Dh (l ++ m) = Dh l + Dh m := by simp [Dh]
theorem Sh_scale (L : ℕ) (l : Hist) : Sh (scale L l) = L * Sh l := by
  induction l with
  | nil => simp [Sh, scale]
  | cons p l ih =>
    simp only [Sh, scale, List.map_cons, List.sum_cons] at ih ⊢
    rw [ih]; push_cast; ring
theorem Dh_scale (L : ℕ) (l : Hist) : Dh (scale L l) = L * Dh l := by
  induction l with
  | nil => simp [Dh, scale]
  | cons p l ih =>
    simp only [Dh, scale, List.map_cons, List.sum_cons] at ih ⊢
    rw [ih]; push_cast; ring

theorem invoice_S (c n : Inv) (L : ℕ) : Sinv (invoice c n L) = Sinv c + L * Sinv n := by
  simp only [Sinv, invoice, Sh_append, Sh_scale]; ring
theorem invoice_D0 (c n : Inv) (L : ℕ) : Dinv (invoice c n L) = Dinv c + L * Dinv n := by
  simp only [Dinv, invoice, Dh_append, Dh_scale]; ring

/-! ### the caller family C(a|b): g = 8, 96 A ports x 4 thin queries, 8 B ports (s1.py) -/
def armT (n c : ℕ) : Hist := (List.range n).map fun i => (8 * i + 9, c)
def armP (m c : ℕ) : Hist := (List.range m).map fun i => (8 * i + 16, c)
/-- C(a'+2 | b'+2); stage count k = a'+b'+4.  208 = 2 * 104 ports. -/
def callerT (a b : ℕ) : Hist := armT (a + 2) 208 ++ armT (b + 2) 208 ++ [(8 * (a + b + 4) + 1, 208)]
def callerP (a b : ℕ) : Hist :=
  armP a 208 ++ armP b 208 ++ [(8, 384), (1, 384), (8, 16 * (a + b + 4)), (9, 32)]
def caller (a b : ℕ) : Inv := ⟨callerT a b, callerP a b⟩

/-- #7113 caller invoice (PRICEKIT caller_invoice of MONOCALLER/7113_CALLER.json), data; nJ = 17 -/
def dataT : Hist := [(9,416),(17,416),(25,416),(33,416),(41,416),(49,416),(57,416),(65,416),(73,208),(137,208)]
def dataP : Hist := [(1,384),(8,656),(9,32),(16,416),(24,416),(32,416),(40,416),(48,416),(56,416),(64,208)]

theorem cnt_zero {l : Hist} {r : ℕ} (h : ∀ p ∈ l, p.1 ≠ r) : cnt l r = 0 := by
  unfold cnt
  apply List.sum_eq_zero
  intro x hx
  obtain ⟨p, hp, rfl⟩ := List.mem_map.mp hx
  simp [h p hp]

theorem keys_T : ∀ p ∈ callerT 6 7, p.1 < 200 := by decide
theorem keys_P : ∀ p ∈ callerP 6 7, p.1 < 200 := by decide
theorem keys_dT : ∀ p ∈ dataT, p.1 < 200 := by decide
theorem keys_dP : ∀ p ∈ dataP, p.1 < 200 := by decide

theorem cnt_big {l : Hist} (hl : ∀ p ∈ l, p.1 < 200) {r : ℕ} (hr : 200 ≤ r) : cnt l r = 0 :=
  cnt_zero fun p hp => by have := hl p hp; omega

theorem repro_T : ∀ r, cnt (callerT 6 7) r = cnt dataT r := by
  intro r
  by_cases hr : r < 200
  · interval_cases r <;> decide
  · rw [cnt_big keys_T (by omega), cnt_big keys_dT (by omega)]
theorem repro_P : ∀ r, cnt (callerP 6 7) r = cnt dataP r := by
  intro r
  by_cases hr : r < 200
  · interval_cases r <;> decide
  · rw [cnt_big keys_P (by omega), cnt_big keys_dP (by omega)]

/-- weighted sums depend only on the histogram (keys below N) -/
theorem wsum_cnt (w : ℕ → ℝ) (N : ℕ) : ∀ l : Hist, (∀ p ∈ l, p.1 < N) →
    (l.map fun p => (p.2 : ℝ) * w p.1).sum = ∑ r ∈ Finset.range N, (cnt l r : ℝ) * w r := by
  intro l
  induction l with
  | nil => intro _; simp [cnt]
  | cons p l ih =>
    intro h
    have hp : p.1 < N := h p (by simp)
    have ih' := ih (fun q hq => h q (by simp [hq]))
    have hc : ∀ r, (cnt (p :: l) r : ℝ) = (if p.1 = r then (p.2 : ℝ) else 0) + cnt l r := by
      intro r; simp only [cnt, List.map_cons, List.sum_cons]; split_ifs <;> simp
    simp only [List.map_cons, List.sum_cons]
    rw [ih']
    simp only [hc, add_mul, Finset.sum_add_distrib]
    congr 1
    rw [Finset.sum_eq_single p.1]
    · simp
    · intro b _ hb; simp [Ne.symm hb]
    · intro h'; exact absurd (Finset.mem_range.mpr hp) h'

theorem Dh_congr (l m : Hist) (hl : ∀ p ∈ l, p.1 < 200) (hm : ∀ p ∈ m, p.1 < 200)
    (h : ∀ r, cnt l r = cnt m r) : Dh l = Dh m := by
  unfold Dh; rw [wsum_cnt fL 200 l hl, wsum_cnt fL 200 m hm]
  exact Finset.sum_congr rfl fun r _ => by rw [h r]

theorem caller89_D0 :
    Dh (callerT 6 7) = Dh dataT ∧ Dh (callerP 6 7) = Dh dataP :=
  ⟨Dh_congr _ _ keys_T keys_dT repro_T, Dh_congr _ _ keys_P keys_dP repro_P⟩

theorem caller89_S : Sh (callerT 6 7) = Sh dataT ∧ Sh (callerP 6 7) = Sh dataP := by
  constructor <;> decide

/-- REPRODUCTION: C(8|9) equals the #7113 caller invoice (histograms term for term; hence S and D0). -/
theorem reproduction :
    (∀ r, cnt (caller 6 7).T r = cnt dataT r) ∧ (∀ r, cnt (caller 6 7).P r = cnt dataP r) ∧
    Sinv (caller 6 7) = Sh dataT - Sh dataP ∧ Dinv (caller 6 7) = Dh dataT - Dh dataP := by
  refine ⟨repro_T, repro_P, ?_, ?_⟩
  · simp only [Sinv, caller, caller89_S.1, caller89_S.2]
  · simp only [Dinv, caller, caller89_D0.1, caller89_D0.2]

theorem S_data : Sh dataT - Sh dataP = 57728 := by decide

/-! ### closed forms -/
theorem Sh_armT (n c : ℕ) : Sh (armT n c) = c * (4 * n * n + 5 * n) := by
  induction n with
  | zero => simp [armT, Sh]
  | succ n ih =>
    have : armT (n + 1) c = armT n c ++ [(8 * n + 9, c)] := by simp [armT, List.range_succ]
    rw [this, Sh_append, ih]; simp [Sh]; push_cast; ring
theorem Sh_armP (m c : ℕ) : Sh (armP m c) = c * (4 * m * m + 12 * m) := by
  induction m with
  | zero => simp [armP, Sh]
  | succ n ih =>
    have : armP (n + 1) c = armP n c ++ [(8 * n + 16, c)] := by simp [armP, List.range_succ]
    rw [this, Sh_append, ih]; simp [Sh]; push_cast; ring

/-- caller S is affine in the stage count k = a+b+4: S = 3408 k - 208 (96 A + 8 B ports; both arms >= 2) -/
theorem S_caller (a b : ℕ) : Sinv (caller a b) = 3408 * ((a : ℤ) + b + 4) - 208 := by
  simp only [Sinv, caller, callerT, callerP, Sh_append, Sh_armT, Sh_armP]
  simp [Sh]; push_cast; ring

/-- S of the whole invoice with calls = k: (3408 + Sn) k - 208 -/
theorem S_invoice (a b : ℕ) (n : Inv) :
    Sinv (invoice (caller a b) n (a + b + 4)) = (3408 + Sinv n) * ((a : ℤ) + b + 4) - 208 := by
  rw [invoice_S, S_caller]; push_cast; ring

/-- with the #7630 native (S per call = -3312, from S = 1424 at k = 17): S(k) = 96 k - 208 -/
theorem S_7630 (a b : ℕ) (n : Inv) (hn : Sinv n = -3312) :
    Sinv (invoice (caller a b) n (a + b + 4)) = 96 * ((a : ℤ) + b + 4) - 208 := by
  rw [S_invoice, hn]; ring

theorem S_7630_k17 (n : Inv) (hn : Sinv n = -3312) :
    Sinv (invoice (caller 6 7) n 17) = 1424 := by
  have := S_7630 6 7 n hn; simpa using this

theorem Dh_armT (n c : ℕ) : Dh (armT n c) = c * ∑ i ∈ Finset.range n, fL (8 * i + 9) := by
  induction n with
  | zero => simp [armT, Dh]
  | succ n ih =>
    have : armT (n + 1) c = armT n c ++ [(8 * n + 9, c)] := by simp [armT, List.range_succ]
    rw [this, Dh_append, ih, Finset.sum_range_succ]; simp [Dh]; ring
theorem Dh_armP (n c : ℕ) : Dh (armP n c) = c * ∑ i ∈ Finset.range n, fL (8 * i + 16) := by
  induction n with
  | zero => simp [armP, Dh]
  | succ n ih =>
    have : armP (n + 1) c = armP n c ++ [(8 * n + 16, c)] := by simp [armP, List.range_succ]
    rw [this, Dh_append, ih, Finset.sum_range_succ]; simp [Dh]; ring

theorem fL_one : fL 1 = 0 := by simp [fL]

/-- caller D0 (the stage-count cost C(k), exact): the sums are over the ranks 8j+1 (T) and 8j (P) -/
theorem D0_caller (a b : ℕ) : Dinv (caller a b) =
    208 * (∑ i ∈ Finset.range (a + 2), fL (8 * i + 9) + ∑ i ∈ Finset.range (b + 2), fL (8 * i + 9)
      + fL (8 * (a + b + 4) + 1)
      - ∑ i ∈ Finset.range a, fL (8 * i + 16) - ∑ i ∈ Finset.range b, fL (8 * i + 16))
    - (384 + 16 * ((a : ℝ) + b + 4)) * fL 8 - 32 * fL 9 := by
  simp only [Dinv, caller, callerT, callerP, Dh_append, Dh_armT, Dh_armP]
  simp [Dh, fL_one]; ring

/-! ### single crossing: a cheaper native can only lower the best stage count (first-order proxy K = S/D0) -/
section crossing
variable {s ρ Dc1 Dc2 k1 k2 d d' : ℝ}

/-- proxy objective K_d(k) = S(k) / (Dc(k) + k d), S(k) = s k - ρ, d = native D0 per call, calls = k -/
theorem single_crossing (hρ : 0 < ρ) (hk : k1 ≤ k2) (hd : d ≤ d')
    (hD1 : 0 < Dc1 + k1 * d) (hD2 : 0 < Dc2 + k2 * d)
    (hD1' : 0 < Dc1 + k1 * d') (hD2' : 0 < Dc2 + k2 * d')
    (h : (s * k1 - ρ) / (Dc1 + k1 * d) ≤ (s * k2 - ρ) / (Dc2 + k2 * d)) :
    (s * k1 - ρ) / (Dc1 + k1 * d') ≤ (s * k2 - ρ) / (Dc2 + k2 * d') := by
  rw [div_le_div_iff₀ hD1 hD2] at h
  rw [div_le_div_iff₀ hD1' hD2']
  have : 0 ≤ (d' - d) * (ρ * (k2 - k1)) := mul_nonneg (by linarith) (mul_nonneg hρ.le (by linarith))
  nlinarith

/-- contrapositive form: if at the costlier native the smaller k is (weakly) preferred, it is at the cheaper native too;
    equivalently the best k never goes up when D0 per call goes down -/
theorem cheaper_native_lowers_k (hρ : 0 < ρ) (hk : k1 ≤ k2) (hd : d ≤ d')
    (hD1 : 0 < Dc1 + k1 * d) (hD2 : 0 < Dc2 + k2 * d)
    (hD1' : 0 < Dc1 + k1 * d') (hD2' : 0 < Dc2 + k2 * d')
    (h : (s * k2 - ρ) / (Dc2 + k2 * d') < (s * k1 - ρ) / (Dc1 + k1 * d')) :
    (s * k2 - ρ) / (Dc2 + k2 * d) < (s * k1 - ρ) / (Dc1 + k1 * d) := by
  by_contra hn
  exact absurd (single_crossing hρ hk hd hD1 hD2 hD1' hD2' (not_lt.mp hn)) (not_le.mpr h)

/-- the crossing native D0 per call at which k1 and k2 tie (proxy): d* = (S1 Dc2 - S2 Dc1) / (ρ (k2 - k1)) -/
theorem crossing_value (hρ : 0 < ρ) (hk : k1 < k2) :
    (s * k1 - ρ) * (Dc2 + k2 * d) = (s * k2 - ρ) * (Dc1 + k1 * d) ↔
      d = ((s * k1 - ρ) * Dc2 - (s * k2 - ρ) * Dc1) / (ρ * (k2 - k1)) := by
  have hne : ρ * (k2 - k1) ≠ 0 := (mul_pos hρ (by linarith)).ne'
  rw [eq_div_iff hne]
  constructor <;> intro h <;> nlinarith

/-- sensitivity: d/dd of the stationarity numerator N = S'D - SD' (D = Dc + k d) is k S' - S = rho > 0.
    (CALLERCO R1 sec 3 writes -(kS'-S); the sign convention there is reversed, the conclusion "cheaper native -> smaller k" is the same.) -/
theorem stationarity_slope (s ρ Dc Dc' k d : ℝ) :
    (s * (Dc + k * d) - (s * k - ρ) * (Dc' + d)) = (s * Dc - (s * k - ρ) * Dc') + ρ * d := by ring
end crossing

/-! ### composition: invoice D0 >= caller floor + calls * native floor -/
section composition
variable {Cl : Type}

/-- Abstract composition.  A caller class Cl with D0 cost Dc and call count `calls`; native per-call D0 Dn.
    hc: caller floor as a function of the number of calls it makes; hn: a floor on the TOTAL native D0 per call. -/
theorem composition (Dc : Cl → ℝ) (calls : Cl → ℕ) (Fc : ℕ → ℝ) (Dn Fn : ℝ)
    (hc : ∀ c, Fc (calls c) ≤ Dc c) (hn : Fn ≤ Dn) (c : Cl) :
    Fc (calls c) + calls c * Fn ≤ Dc c + calls c * Dn := by
  have := hc c
  have : (calls c : ℝ) * Fn ≤ calls c * Dn := mul_le_mul_of_nonneg_left hn (Nat.cast_nonneg _)
  linarith

/-- the native's D0 per call splits as helperD0 + rest (mains and owned MOVEs; these are CREDITS, rest <= 0 on #7630).
    The helper-only floor therefore needs a cap R on the credits: rest >= -R. -/
theorem composition_helper (Dc : Cl → ℝ) (calls : Cl → ℕ) (Fc : ℕ → ℝ) (H rest Hf R : ℝ)
    (hc : ∀ c, Fc (calls c) ≤ Dc c) (hH : Hf ≤ H) (hR : -R ≤ rest) (c : Cl) :
    Fc (calls c) + calls c * (Hf - R) ≤ Dc c + calls c * (H + rest) :=
  composition Dc calls Fc (H + rest) (Hf - R) hc (by linarith) c

/-- the proxy kappa is bounded by S / (floor) when the floor is positive -/
theorem kappa_proxy_le {S D F : ℝ} (hS : 0 ≤ S) (hF : 0 < F) (hFD : F ≤ D) : S / D ≤ S / F :=
  div_le_div_of_nonneg_left hS hF hFD

/-- FALSE AS WRITTEN: "invoice D0 >= caller D0 + calls * helperD0-floor" (helper floor 9,928.76 per call on #7630,
    caller D0 270,813, calls 17, invoice D0 391,295.63 (R1 sec 2; numbers are hypotheses/data)).  The missing term is the
    mains/owned MOVE credits (negative D0).  Counterexample: -/
theorem naive_composition_false :
    ¬ ((270813 : ℝ) + 17 * 9928.76 ≤ 391295.63) := by norm_num

/-- the credits implied by the data: rest per call = (391295.63 - 270813)/17 - 9928.76 < 0 -/
theorem rest_negative : (391295.63 - 270813 : ℝ) / 17 - 9928.76 < 0 := by norm_num

end composition

#print axioms reproduction
#print axioms S_caller
#print axioms S_7630_k17
#print axioms D0_caller
#print axioms invoice_S
#print axioms invoice_D0
#print axioms single_crossing
#print axioms cheaper_native_lowers_k
#print axioms crossing_value
#print axioms composition
#print axioms composition_helper
#print axioms naive_composition_false

end CallerCost
