/-
HPDual (lane LEANHP, Nov 20).  The KASYM chord dual (cards/WILD/NOVEL/kasym/KA.md sec 1-2), abstract algebra part.
  v2p = 17^s - 16^s, hh x = v2p - (8x+1)^s + 8^s x, qq = hh/x, chord slope sl through (2,qq 2),(k,qq k),
  Tt = (k-1) sl, wm = qq 2 - sl, Sf D = (k-1) G(D)/(k-D) (2<D<k), Sf k = Tt, Sf D = 0 (D<=2), wt l = Sf l - Sf (l-1).
Hypothesis package `QF s`: qq concave and monotone on [2,oo), and qq 3 <= 2 qq 2 (all discharged in CallerHP.lean).
Proved here (kernel only): key identity (E), wt_l >= 0, wm >= 0, telescoping, per-role dual feasibility
  roleVal + (sum_l wt_l row_l)/(k-1) + wm * #mains <= v2p   (stage-level form of rc2_avg's right-hand side),
and weak duality over all roles.
-/
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Analysis.Convex.Function
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Nov15.HPCalc

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace CallerHP
open Finset Set

section dual
variable (σ : ℝ)

noncomputable def v2p : ℝ := (17 : ℝ) ^ σ - (16 : ℝ) ^ σ
noncomputable def hh (x : ℝ) : ℝ := v2p σ - (8 * x + 1) ^ σ + (8 : ℝ) ^ σ * x
noncomputable def qq (x : ℝ) : ℝ := hh σ x / x

structure QF : Prop where
  conc : ConcaveOn ℝ (Ici 2) (qq σ)
  mono : MonotoneOn (qq σ) (Ici 2)
  q3 : qq σ 3 ≤ 2 * qq σ 2

variable (k : ℕ)

noncomputable def sl : ℝ := (qq σ k - qq σ 2) / ((k : ℝ) - 2)
noncomputable def Tt : ℝ := ((k : ℝ) - 1) * sl σ k
noncomputable def wm : ℝ := qq σ 2 - sl σ k
noncomputable def Gf (D : ℝ) : ℝ := qq σ D - qq σ 2 - sl σ k * (D - 2)
noncomputable def Sf (D : ℕ) : ℝ :=
  if D ≤ 2 then 0 else if D = k then Tt σ k else ((k : ℝ) - 1) * Gf σ k D / ((k : ℝ) - D)
noncomputable def wt (l : ℕ) : ℝ := Sf σ k l - Sf σ k (l - 1)

variable {σ k}

theorem hk_real (hk : 3 ≤ k) : (3 : ℝ) ≤ k := by exact_mod_cast hk

theorem hh_eq (x : ℝ) (hx : x ≠ 0) : hh σ x = x * qq σ x := by
  unfold qq; field_simp

theorem sl_mul (hk : 3 ≤ k) : sl σ k * ((k : ℝ) - 2) = qq σ k - qq σ 2 := by
  have : (k : ℝ) - 2 ≠ 0 := by have := hk_real hk; linarith
  unfold sl; field_simp

theorem Sf_mid (hk : 3 ≤ k) {D : ℕ} (h2 : 2 ≤ D) (hD : D < k) :
    Sf σ k D = ((k : ℝ) - 1) * Gf σ k D / ((k : ℝ) - D) := by
  unfold Sf
  by_cases h : D ≤ 2
  · have : D = 2 := by omega
    subst this
    simp only [if_pos h]
    unfold Gf; push_cast; simp
  · rw [if_neg h, if_neg (by omega)]

theorem Sf_k (hk : 3 ≤ k) : Sf σ k k = Tt σ k := by
  unfold Sf; rw [if_neg (by omega), if_pos rfl]

theorem Sf_small {D : ℕ} (h : D ≤ 2) : Sf σ k D = 0 := by
  unfold Sf; rw [if_pos h]

/-- key identity (E), cleared of denominators -/
theorem key_E (hk : 3 ≤ k) {D : ℕ} (h2 : 2 ≤ D) (hD : D ≤ k) :
    (D : ℝ) * ((k : ℝ) - 1) * Sf σ k D + (D : ℝ) * ((D : ℝ) - 1) * (Tt σ k - Sf σ k D)
      + (D : ℝ) * ((k : ℝ) - 1) * wm σ k = ((k : ℝ) - 1) * hh σ D := by
  have hk3 := hk_real hk
  have hk1 : (k : ℝ) - 1 ≠ 0 := by linarith
  have hk2 : (k : ℝ) - 2 ≠ 0 := by linarith
  have hDr : (2 : ℝ) ≤ D := by exact_mod_cast h2
  have hslm := sl_mul (σ := σ) hk
  have hq2 : hh σ 2 = 2 * qq σ 2 := hh_eq 2 (by norm_num)
  rcases Nat.lt_or_ge D k with hlt | hge
  · have hDk : (D : ℝ) < k := by exact_mod_cast hlt
    have hkD : (k : ℝ) - D ≠ 0 := by linarith
    rw [Sf_mid hk h2 hlt]
    have hqD : hh σ D = D * qq σ D := hh_eq _ (by positivity)
    rw [hqD]
    unfold Tt wm Gf
    field_simp
    ring
  · have hDk : D = k := le_antisymm hD hge
    subst hDk
    rw [Sf_k hk]
    have hqD : hh σ D = D * qq σ D := hh_eq _ (by positivity)
    rw [hqD]
    unfold Tt wm
    have : qq σ D = qq σ 2 + sl σ D * ((D : ℝ) - 2) := by linarith
    rw [this]
    ring

theorem chord_ineq {f : ℝ → ℝ} (hf : ConcaveOn ℝ (Ici 2) f) {x y z : ℝ} (hx : 2 ≤ x) (hxz : x ≤ z)
    (hzy : z ≤ y) (hxy : x < y) : (y - z) * f x + (z - x) * f y ≤ (y - x) * f z := by
  have hyx : 0 < y - x := by linarith
  have hne : y - x ≠ 0 := hyx.ne'
  have h := hf.2 (show x ∈ Ici (2:ℝ) from hx) (show y ∈ Ici (2:ℝ) from by simp; linarith)
    (show 0 ≤ (y - z) / (y - x) from div_nonneg (by linarith) hyx.le)
    (show 0 ≤ (z - x) / (y - x) from div_nonneg (by linarith) hyx.le)
    (by field_simp; ring)
  simp only [smul_eq_mul] at h
  have e : (y - z) / (y - x) * x + (z - x) / (y - x) * y = z := by
    field_simp; ring
  rw [e] at h
  have := mul_le_mul_of_nonneg_left h hyx.le
  have e2 : (y - x) * ((y - z) / (y - x) * f x + (z - x) / (y - x) * f y)
      = (y - z) * f x + (z - x) * f y := by field_simp
  linarith

theorem Gf_nonneg (hq : QF σ) (hk : 3 ≤ k) {D : ℕ} (h2 : 2 ≤ D) (hD : D ≤ k) : 0 ≤ Gf σ k D := by
  have hk3 := hk_real hk
  have hDr : (2 : ℝ) ≤ D := by exact_mod_cast h2
  have hDk : (D : ℝ) ≤ k := by exact_mod_cast hD
  have hslm := sl_mul (σ := σ) hk
  have hc := chord_ineq hq.conc (x := 2) (y := k) (z := D) le_rfl hDr hDk (by linarith)
  unfold Gf
  have : 0 ≤ ((k : ℝ) - 2) * (qq σ D - qq σ 2 - sl σ k * ((D : ℝ) - 2)) := by nlinarith
  by_contra hneg
  push Not at hneg
  have : ((k : ℝ) - 2) * (qq σ D - qq σ 2 - sl σ k * ((D : ℝ) - 2)) < 0 :=
    mul_neg_of_pos_of_neg (by linarith) hneg
  linarith

theorem sl_nonneg (hq : QF σ) (hk : 3 ≤ k) : 0 ≤ sl σ k := by
  have hk3 := hk_real hk
  have hm := hq.mono (show (2:ℝ) ∈ Ici (2:ℝ) from Set.mem_Ici.mpr le_rfl) (show (k:ℝ) ∈ Ici (2:ℝ) from by simp; linarith)
    (by linarith)
  unfold sl
  exact div_nonneg (by linarith) (by linarith)

theorem wm_nonneg (hq : QF σ) (hk : 3 ≤ k) : 0 ≤ wm σ k := by
  have hk3 := hk_real hk
  have hslm := sl_mul (σ := σ) hk
  have hc := chord_ineq hq.conc (x := 2) (y := k) (z := 3) le_rfl (by norm_num) hk3 (by linarith)
  have h3 := hq.q3
  unfold wm
  by_contra hneg
  push Not at hneg
  -- sl > qq 2 >= qq 3 - qq 2, but (k-2)(qq3 - qq2) >= qk - q2 = sl (k-2)
  have h1 : sl σ k * ((k : ℝ) - 2) ≤ ((k : ℝ) - 2) * (qq σ 3 - qq σ 2) := by linarith
  have h2 : ((k : ℝ) - 2) * (qq σ 3 - qq σ 2) ≤ ((k : ℝ) - 2) * qq σ 2 :=
    mul_le_mul_of_nonneg_left (by linarith) (by linarith)
  have h3' : ((k : ℝ) - 2) * qq σ 2 < sl σ k * ((k : ℝ) - 2) := by
    have := mul_lt_mul_of_pos_right (show qq σ 2 < sl σ k by linarith) (show (0:ℝ) < (k:ℝ) - 2 by linarith)
    linarith
  linarith

theorem wt_nonneg (hq : QF σ) (hk : 3 ≤ k) {l : ℕ} (h3 : 3 ≤ l) (hl : l ≤ k) : 0 ≤ wt σ k l := by
  have hk3 := hk_real hk
  have hslm := sl_mul (σ := σ) hk
  unfold wt
  have hl1 : l - 1 + 1 = l := by omega
  have hlr : ((l : ℕ) : ℝ) = ((l - 1 : ℕ) : ℝ) + 1 := by
    have : ((l - 1 + 1 : ℕ) : ℝ) = ((l:ℕ):ℝ) := by rw [hl1]
    push_cast at this; linarith
  have har : (2 : ℝ) ≤ ((l - 1 : ℕ) : ℝ) := by
    have : 2 ≤ l - 1 := by omega
    exact_mod_cast this
  rcases Nat.lt_or_ge l k with hlt | hge
  · rw [Sf_mid hk (by omega) hlt, Sf_mid hk (by omega) (by omega)]
    have hlk : (l : ℝ) < k := by exact_mod_cast hlt
    have hCh := chord_ineq hq.conc (x := ((l - 1 : ℕ) : ℝ)) (y := k) (z := l) har (by linarith)
      hlk.le (by linarith)
    set a : ℝ := ((l - 1 : ℕ) : ℝ) with ha
    unfold Gf
    have hka : (0:ℝ) < (k : ℝ) - a := by linarith
    have hkl : (0:ℝ) < (k : ℝ) - l := by linarith
    rw [hlr]
    rw [hlr] at hkl hCh
    rw [sub_nonneg, div_le_div_iff₀ hka (by linarith)]
    have key : 0 ≤ ((k:ℝ) - a) * (qq σ (a+1) - qq σ 2 - sl σ k * (a + 1 - 2))
        - ((k:ℝ) - (a+1)) * (qq σ a - qq σ 2 - sl σ k * (a - 2)) := by nlinarith
    nlinarith
  · have hlk : l = k := le_antisymm hl hge
    subst hlk
    rw [Sf_k hk, Sf_mid hk (by omega) (by omega)]
    have hmono := hq.mono (show ((l - 1 : ℕ) : ℝ) ∈ Ici (2:ℝ) from Set.mem_Ici.mpr har)
      (show (l : ℝ) ∈ Ici (2:ℝ) from by simp; linarith) (by rw [hlr]; linarith)
    unfold Tt Gf
    have e : ((l : ℝ) - ((l - 1 : ℕ) : ℝ)) = 1 := by rw [hlr]; ring
    rw [e, div_one]
    have e2 : ((l - 1 : ℕ) : ℝ) = (l : ℝ) - 1 := by rw [hlr]; ring
    rw [e2]
    have : 0 ≤ ((l : ℝ) - 1) * (sl σ l - (qq σ ((l:ℝ) - 1) - qq σ 2 - sl σ l * ((l:ℝ) - 1 - 2))) := by
      apply mul_nonneg (by linarith)
      rw [e2] at hmono
      nlinarith
    nlinarith

/-! ## telescoping and the stage-row identity -/

theorem tele (S : ℕ → ℝ) (m : ℕ) : ∀ q, m ≤ q → ∑ l ∈ Finset.Ioc m q, (S l - S (l - 1)) = S q - S m := by
  intro q hq
  induction q, hq using Nat.le_induction with
  | base => simp
  | succ n hn ih =>
    rw [Finset.sum_Ioc_succ_top hn, ih]
    simp only [Nat.add_sub_cancel]
    ring

theorem sum_wt (hk : 3 ≤ k) {p q : ℕ} (hpq : p ≤ q) (hq2 : 2 ≤ q) (hqk : q ≤ k) :
    ∑ l ∈ Finset.Icc 3 k, (if p < l ∧ l ≤ q then wt σ k l else 0) = Sf σ k q - Sf σ k p := by
  rw [← Finset.sum_filter]
  have hf : (Finset.Icc 3 k).filter (fun l => p < l ∧ l ≤ q) = Finset.Ioc (max p 2) q := by
    ext l; simp only [Finset.mem_filter, Finset.mem_Icc, Finset.mem_Ioc]; omega
  rw [hf]
  have h := tele (Sf σ k) (max p 2) q (by omega)
  have hS : Sf σ k (max p 2) = Sf σ k p := by
    rcases le_total p 2 with h | h
    · rw [max_eq_right h, Sf_small h, Sf_small (le_refl 2)]
    · rw [max_eq_left h]
  simp only [wt]
  rw [h, hS]

theorem stage_row (hk : 3 ≤ k) {D a : ℕ} (hD2 : 2 ≤ D) (hDk : D ≤ k) (haD : a ≤ D) :
    ∑ l ∈ Finset.Icc 3 k, wt σ k l * (if l ≤ D then (if a < l then ((k : ℝ) - a) else 0) else ((D : ℝ) - a))
      = ((k : ℝ) - a) * (Sf σ k D - Sf σ k a) + ((D : ℝ) - a) * (Tt σ k - Sf σ k D) := by
  have h1 := sum_wt (σ := σ) hk haD hD2 hDk
  have h2 := sum_wt (σ := σ) hk (p := D) (q := k) hDk (by omega) le_rfl
  have hpt : ∀ l ∈ Finset.Icc 3 k, wt σ k l * (if l ≤ D then (if a < l then ((k : ℝ) - a) else 0) else ((D : ℝ) - a))
      = ((k : ℝ) - a) * (if a < l ∧ l ≤ D then wt σ k l else 0)
        + ((D : ℝ) - a) * (if D < l ∧ l ≤ k then wt σ k l else 0) := by
    intro l hl
    rw [Finset.mem_Icc] at hl
    split_ifs <;> first | (exfalso; omega) | ring
  rw [Finset.sum_congr rfl hpt, Finset.sum_add_distrib, ← Finset.mul_sum, ← Finset.mul_sum, h1, h2,
    Sf_k hk]

/-! ## stage-level data -/

variable {τ : Type*}

noncomputable def rowS (k : ℕ) (st : Finset τ) (a : τ → ℕ) (l : ℕ) : ℝ :=
  ∑ s ∈ st, (if l ≤ st.card then (if a s < l then ((k : ℝ) - a s) else 0) else ((st.card : ℝ) - a s))

noncomputable def roleVal (σ : ℝ) (st : Finset τ) (a : τ → ℕ) : ℝ :=
  (8 * (st.card : ℝ) + 1) ^ σ - ∑ s ∈ st, (8 * (a s : ℝ)) ^ σ / (a s : ℝ)

noncomputable def mainCnt (st : Finset τ) (mn : τ → Bool) : ℝ :=
  ∑ s ∈ st, (if mn s = true then (1 : ℝ) else 0)

/-- (F1) -/
theorem f1 (h0 : 0 < σ) (h1 : σ < 1) {a : ℕ} (ha : 2 ≤ a) :
    (8 * (a : ℝ) + 1) ^ σ - (8 * (a : ℝ)) ^ σ ≤ v2p σ := by
  have h := diff_anti h0 h1 (show (0:ℝ) ∈ Ici (0:ℝ) from Set.mem_Ici.mpr le_rfl)
    (show (8 * (a:ℝ)) ∈ Ici (0:ℝ) from Set.mem_Ici.mpr (by positivity))
    (show (0:ℝ) ≤ 8 * (a:ℝ) by positivity)
  have h16 := diff_anti h0 h1 (show (16:ℝ) ∈ Ici (0:ℝ) from Set.mem_Ici.mpr (by norm_num))
    (show (8 * (a:ℝ)) ∈ Ici (0:ℝ) from Set.mem_Ici.mpr (by positivity))
    (by have : (2:ℝ) ≤ a := by exact_mod_cast ha
        linarith)
  simp only at h16
  unfold v2p
  have e : (16 : ℝ) + 1 = 17 := by norm_num
  rw [e] at h16
  exact h16

theorem stage_ineq (hq : QF σ) (h0 : 0 < σ) (h1 : σ < 1) (hk : 3 ≤ k) {D a : ℕ} (hD2 : 2 ≤ D)
    (hDk : D ≤ k) (ha1 : 1 ≤ a) (haD : a ≤ D) (m : ℝ) (hm0 : 0 ≤ m) (hm1 : m ≤ 1)
    (hmain : m ≠ 0 → a = 1) :
    -((k : ℝ) - 1) * ((8 * (a : ℝ)) ^ σ / (a : ℝ))
      + (((k : ℝ) - a) * (Sf σ k D - Sf σ k a) + ((D : ℝ) - a) * (Tt σ k - Sf σ k D))
      + wm σ k * ((k : ℝ) - 1) * m
    ≤ ((k : ℝ) - 1) * (wm σ k - (8 : ℝ) ^ σ) + (Sf σ k D * ((k : ℝ) - D) + ((D : ℝ) - 1) * Tt σ k) := by
  have hk3 := hk_real hk
  have hwm := wm_nonneg hq hk
  by_cases ha : a = 1
  · subst ha
    rw [Sf_small (σ := σ) (k := k) (D := 1) (by norm_num)]
    have : (8 * ((1:ℕ):ℝ)) ^ σ / ((1:ℕ):ℝ) = (8:ℝ) ^ σ := by norm_num
    rw [this]
    have hp : 0 ≤ wm σ k * ((k : ℝ) - 1) * (1 - m) :=
      mul_nonneg (mul_nonneg hwm (by linarith)) (by linarith)
    push_cast
    nlinarith
  · have ha2 : 2 ≤ a := by omega
    have hm : m = 0 := by
      by_contra hne; exact ha (hmain hne)
    subst hm
    have har : (2 : ℝ) ≤ a := by exact_mod_cast ha2
    have ha0 : (a : ℝ) ≠ 0 := by positivity
    have hE := key_E (σ := σ) hk ha2 (haD.trans hDk)
    have hX2 : (a : ℝ) * (((k : ℝ) - a) * Sf σ k a + ((a : ℝ) - 1) * Tt σ k)
        = ((k : ℝ) - 1) * (hh σ a - a * wm σ k) := by linear_combination hE
    have hz : (8 * (a : ℝ)) ^ σ / (a : ℝ) * (a : ℝ) = (8 * (a : ℝ)) ^ σ := div_mul_cancel₀ _ ha0
    have hF := f1 h0 h1 ha2
    have hF' : 0 ≤ (8 * (a : ℝ)) ^ σ + v2p σ - (8 * (a : ℝ) + 1) ^ σ := by linarith
    have hdiff : (((k : ℝ) - 1) * (wm σ k - (8 : ℝ) ^ σ) + (Sf σ k D * ((k : ℝ) - D) + ((D : ℝ) - 1) * Tt σ k))
        - (-((k : ℝ) - 1) * ((8 * (a : ℝ)) ^ σ / (a : ℝ))
          + (((k : ℝ) - a) * (Sf σ k D - Sf σ k a) + ((D : ℝ) - a) * (Tt σ k - Sf σ k D))
          + wm σ k * ((k : ℝ) - 1) * 0)
        = ((k : ℝ) - 1) * ((8 * (a : ℝ)) ^ σ + v2p σ - (8 * (a : ℝ) + 1) ^ σ) / (a : ℝ) := by
      rw [eq_div_iff ha0]
      unfold hh at hX2
      linear_combination ((k : ℝ) - 1) * hz + hX2
    have : 0 ≤ ((k : ℝ) - 1) * ((8 * (a : ℝ)) ^ σ + v2p σ - (8 * (a : ℝ) + 1) ^ σ) / (a : ℝ) :=
      div_nonneg (mul_nonneg (by linarith) hF') (by positivity)
    linarith

theorem role_le (hq : QF σ) (h0 : 0 < σ) (h1 : σ < 1) (hk : 3 ≤ k) (st : Finset τ) (a : τ → ℕ)
    (mn : τ → Bool) (hD2 : 2 ≤ st.card) (hDk : st.card ≤ k) (ha1 : ∀ s ∈ st, 1 ≤ a s)
    (haD : ∀ s ∈ st, a s ≤ st.card) (hmain : ∀ s ∈ st, mn s = true → a s = 1) :
    roleVal σ st a + (∑ l ∈ Finset.Icc 3 k, wt σ k l * rowS k st a l) / ((k : ℝ) - 1)
      + wm σ k * mainCnt st mn ≤ v2p σ := by
  have hk3 := hk_real hk
  have hk1 : (0 : ℝ) < (k : ℝ) - 1 := by linarith
  obtain ⟨D, hD⟩ : ∃ D, st.card = D := ⟨_, rfl⟩
  rw [hD] at hD2 hDk
  simp only [hD] at haD
  have hRV : roleVal σ st a = (8 * (D : ℝ) + 1) ^ σ - ∑ s ∈ st, (8 * (a s : ℝ)) ^ σ / (a s : ℝ) := by
    unfold roleVal; rw [hD]
  have hrow : ∑ l ∈ Finset.Icc 3 k, wt σ k l * rowS k st a l
      = ∑ s ∈ st, (((k : ℝ) - a s) * (Sf σ k D - Sf σ k (a s))
          + ((D : ℝ) - a s) * (Tt σ k - Sf σ k D)) := by
    unfold rowS
    simp_rw [Finset.mul_sum]
    rw [Finset.sum_comm]
    rw [hD]
    exact Finset.sum_congr rfl fun s hs => stage_row hk hD2 hDk (haD s hs)
  have hst : ∀ s ∈ st,
      -((k : ℝ) - 1) * ((8 * (a s : ℝ)) ^ σ / (a s : ℝ))
        + (((k : ℝ) - a s) * (Sf σ k D - Sf σ k (a s)) + ((D : ℝ) - a s) * (Tt σ k - Sf σ k D))
        + wm σ k * ((k : ℝ) - 1) * (if mn s = true then (1 : ℝ) else 0)
      ≤ ((k : ℝ) - 1) * (wm σ k - (8 : ℝ) ^ σ)
        + (Sf σ k D * ((k : ℝ) - D) + ((D : ℝ) - 1) * Tt σ k) := by
    intro s hs
    apply stage_ineq hq h0 h1 hk hD2 hDk (ha1 s hs) (haD s hs)
    · split_ifs <;> norm_num
    · split_ifs <;> norm_num
    · intro hne
      by_cases hm : mn s = true
      · exact hmain s hs hm
      · exfalso; apply hne; simp [hm]
  have hsum := Finset.sum_le_sum hst
  rw [Finset.sum_add_distrib, Finset.sum_add_distrib, ← Finset.mul_sum, ← Finset.mul_sum,
    Finset.sum_const, nsmul_eq_mul, ← hrow, hD] at hsum
  have hmc : ∑ s ∈ st, (if mn s = true then (1 : ℝ) else 0) = mainCnt st mn := rfl
  rw [hmc] at hsum
  have hE := key_E (σ := σ) hk hD2 hDk
  rw [hRV]
  have hX : ((k : ℝ) - 1) * ((∑ l ∈ Finset.Icc 3 k, wt σ k l * rowS k st a l) / ((k : ℝ) - 1))
      = ∑ l ∈ Finset.Icc 3 k, wt σ k l * rowS k st a l := by
    field_simp
  generalize (∑ l ∈ Finset.Icc 3 k, wt σ k l * rowS k st a l) = X at *
  generalize (∑ s ∈ st, (8 * (a s : ℝ)) ^ σ / (a s : ℝ)) = Ssum at *
  generalize mainCnt st mn = mc at *
  generalize (X / ((k : ℝ) - 1)) = Y at *
  unfold hh at hE
  have hmul : ((k : ℝ) - 1) * ((8 * (D : ℝ) + 1) ^ σ - Ssum + Y + wm σ k * mc)
      ≤ ((k : ℝ) - 1) * v2p σ := by
    nlinarith [hsum, hE, hX]
  exact le_of_mul_le_mul_left hmul hk1

theorem sum_wt_all (hk : 3 ≤ k) : ∑ l ∈ Finset.Icc 3 k, wt σ k l = Tt σ k := by
  have h := sum_wt (σ := σ) hk (p := 2) (q := k) (by omega) (by omega) le_rfl
  have e : ∀ l ∈ Finset.Icc 3 k, (if 2 < l ∧ l ≤ k then wt σ k l else 0) = wt σ k l := by
    intro l hl
    rw [Finset.mem_Icc] at hl
    rw [if_pos (by omega)]
  rw [Finset.sum_congr rfl e] at h
  rw [h, Sf_k hk, Sf_small (le_refl 2)]
  ring

/-- WEAK DUALITY for the reduced LP: any family of `n = 2k-2` roles (stage sets of size `D >= 2`, piece sizes
`a_s`, main flags on singletons) satisfying the MAINS count `>= 2k` and the averaged RC2 rows for `l = 3..k`
has total value `<= 2((k-2)(17^s-16^s) + (8k+1)^s - 8^s k) = (k/104) HP(k)`. -/
theorem total_le {R : Type*} [Fintype R] (hq : QF σ) (h0 : 0 < σ) (h1 : σ < 1) (hk : 3 ≤ k)
    (st : R → Finset τ) (a : R → τ → ℕ) (mn : R → τ → Bool)
    (hD2 : ∀ r, 2 ≤ (st r).card) (hDk : ∀ r, (st r).card ≤ k)
    (ha1 : ∀ r, ∀ s ∈ st r, 1 ≤ a r s) (haD : ∀ r, ∀ s ∈ st r, a r s ≤ (st r).card)
    (hmain : ∀ r, ∀ s ∈ st r, mn r s = true → a r s = 1)
    (hcard : (Fintype.card R : ℝ) = 2 * (k : ℝ) - 2)
    (hrc : ∀ l ∈ Finset.Icc 3 k, 2 * (k : ℝ) * ((k : ℝ) - 1) ≤ ∑ r, rowS k (st r) (a r) l)
    (hmains : 2 * (k : ℝ) ≤ ∑ r, mainCnt (st r) (mn r)) :
    ∑ r, roleVal σ (st r) (a r) ≤ 2 * (((k : ℝ) - 2) * v2p σ + (8 * (k : ℝ) + 1) ^ σ - (8 : ℝ) ^ σ * k) := by
  have hk3 := hk_real hk
  have hk1 : (0 : ℝ) < (k : ℝ) - 1 := by linarith
  have hwm := wm_nonneg hq hk
  have hs := Finset.sum_le_sum (fun r (_ : r ∈ (Finset.univ : Finset R)) =>
    role_le hq h0 h1 hk (st r) (a r) (mn r) (hD2 r) (hDk r) (ha1 r) (haD r) (hmain r))
  rw [Finset.sum_add_distrib, Finset.sum_add_distrib, ← Finset.mul_sum, Finset.sum_const,
    Finset.card_univ, nsmul_eq_mul, hcard] at hs
  simp only [div_eq_mul_inv, ← Finset.sum_mul] at hs
  have hswap : ∑ r, ∑ l ∈ Finset.Icc 3 k, wt σ k l * rowS k (st r) (a r) l
      = ∑ l ∈ Finset.Icc 3 k, wt σ k l * ∑ r, rowS k (st r) (a r) l := by
    simp_rw [Finset.mul_sum]
    exact Finset.sum_comm
  rw [hswap] at hs
  have hY : 2 * (k : ℝ) * ((k : ℝ) - 1) * Tt σ k
      ≤ ∑ l ∈ Finset.Icc 3 k, wt σ k l * ∑ r, rowS k (st r) (a r) l := by
    rw [← sum_wt_all hk, Finset.mul_sum]
    refine Finset.sum_le_sum fun l hl => ?_
    rw [Finset.mem_Icc] at hl
    have := wt_nonneg hq hk hl.1 hl.2
    have h2 := hrc l (Finset.mem_Icc.mpr hl)
    nlinarith
  generalize (∑ l ∈ Finset.Icc 3 k, wt σ k l * ∑ r, rowS k (st r) (a r) l) = Y at *
  generalize (∑ r, mainCnt (st r) (mn r)) = MC at *
  have hY2 : 2 * (k : ℝ) * Tt σ k ≤ Y * ((k : ℝ) - 1)⁻¹ := by
    rw [← div_eq_mul_inv, le_div_iff₀ hk1]; nlinarith
  have hMC : wm σ k * (2 * (k : ℝ)) ≤ wm σ k * MC := mul_le_mul_of_nonneg_left hmains hwm
  have hslm := sl_mul (σ := σ) hk
  have hhk : hh σ k = k * qq σ k := hh_eq _ (by positivity)
  unfold hh at hhk
  unfold Tt wm at *
  nlinarith [hs, hY2, hMC, hslm, hhk]

end dual
end CallerHP
