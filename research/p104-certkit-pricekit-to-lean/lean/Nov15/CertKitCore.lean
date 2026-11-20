/-
CertKitCore (lane CERTKIT, Nov 19).  Generic kernel machinery for "PRICEKIT true value -> Lean cert".
An invoice is a list cs of (coefficient c : ℤ, rank r : ℕ, r ≥ 1); its form is F cs t = Σ c · r^(1-t)  (PRICEKIT's F).
* certified rational enclosures of log m (series of Real.abs_log_sub_add_sum_range_le, telescoped m -> m+1) and of
  exp x for x ≤ 0 (Real.exp_bound with argument halving), dyadic rounding to 2^-PB;  phiLo ≤ r^(1-t) ≤ phiHi.
* a piece check: on [a,b] (0 ≤ a), F t ≤ Σ_{c>0} c·phiHi(r,a) + Σ_{c<0} c·phiLo(r,b)  (each r^(1-t) is antitone in t),
  the mirror lower bound, and a tail bound on [a,∞) (Σ_{c>0} c·phiHi(r,a) + the rank-1 coefficient).
* `loOK` / `upOK` chains (computable Bool, checked by `decide +kernel`), with soundness:
  loOK ⇒ F > 0 on the chain's span, upOK ⇒ F < 0 on [start, ∞).
* `kroot cs := sSup {t | 0 ≤ t ∧ 0 ≤ F cs t}` and `kroot_bracket`: positivity on [0,lo] and negativity on [hi,∞)
  give lo ≤ kroot ≤ hi, F (kroot) = 0, and every root of F on [0,∞) lies in (lo, hi).
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Mathlib.Analysis.SpecialFunctions.Log.Deriv
import Mathlib.Analysis.SpecialFunctions.Pow.Continuity
import Mathlib.Analysis.Complex.Exponential
import Mathlib.Data.Rat.Floor
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Positivity

namespace CertKit
open Finset

/-! ## dyadic rounding -/

def PB : ℕ := 128

def rdn (q : ℚ) : ℚ := (⌊q * 2 ^ PB⌋ : ℚ) / 2 ^ PB
def rup (q : ℚ) : ℚ := (⌈q * 2 ^ PB⌉ : ℚ) / 2 ^ PB

theorem rdn_le (q : ℚ) : rdn q ≤ q := by
  unfold rdn
  rw [div_le_iff₀ (by positivity)]
  exact Int.floor_le _

theorem le_rup (q : ℚ) : q ≤ rup q := by
  unfold rup
  rw [le_div_iff₀ (by positivity)]
  exact Int.le_ceil _

theorem rdn_nonneg {q : ℚ} (h : 0 ≤ q) : 0 ≤ rdn q := by
  unfold rdn
  apply div_nonneg _ (by positivity)
  exact_mod_cast Int.floor_nonneg.2 (mul_nonneg h (by positivity))

theorem rdn_le_r (q : ℚ) : ((rdn q : ℚ) : ℝ) ≤ (q : ℝ) := by exact_mod_cast rdn_le q
theorem le_rup_r (q : ℚ) : ((q : ℚ) : ℝ) ≤ (rup q : ℝ) := by exact_mod_cast le_rup q

/-! ## exp enclosures -/

def expSum (x : ℚ) : ℕ → ℚ
  | 0 => 0
  | n + 1 => expSum x n + x ^ n / (n.factorial : ℚ)

def expErr (x : ℚ) (n : ℕ) : ℚ := |x| ^ n * ((n + 1 : ℚ) / ((n.factorial : ℚ) * n))

theorem expSum_cast (x : ℚ) (n : ℕ) : ((expSum x n : ℚ) : ℝ) = ∑ m ∈ range n, (x : ℝ) ^ m / m.factorial := by
  induction n with
  | zero => simp [expSum]
  | succ n ih => rw [expSum, sum_range_succ, ← ih]; push_cast; ring

theorem expErr_cast (x : ℚ) (n : ℕ) :
    ((expErr x n : ℚ) : ℝ) = |(x : ℝ)| ^ n * ((n.succ : ℝ) / (n.factorial * n)) := by
  unfold expErr; push_cast; ring

def NE : ℕ := 24

def eLo0 (x : ℚ) : ℚ := max 0 (rdn (expSum x NE - expErr x NE))
def eHi0 (x : ℚ) : ℚ := rup (expSum x NE + expErr x NE)

theorem eLo0_sound (x : ℚ) (hx : |(x : ℝ)| ≤ 1) : ((eLo0 x : ℚ) : ℝ) ≤ Real.exp x := by
  have hb := Real.exp_bound hx (n := NE) (by norm_num [NE])
  rw [← expSum_cast, ← expErr_cast] at hb
  have h1 := (abs_sub_le_iff.1 hb).2
  unfold eLo0
  push_cast
  apply max_le (Real.exp_pos _).le
  have := rdn_le_r (expSum x NE - expErr x NE)
  push_cast at this
  linarith

theorem eHi0_sound (x : ℚ) (hx : |(x : ℝ)| ≤ 1) : Real.exp x ≤ ((eHi0 x : ℚ) : ℝ) := by
  have hb := Real.exp_bound hx (n := NE) (by norm_num [NE])
  rw [← expSum_cast, ← expErr_cast] at hb
  have h1 := (abs_sub_le_iff.1 hb).1
  unfold eHi0
  have := le_rup_r (expSum x NE + expErr x NE)
  push_cast at this
  linarith

def sqLo (a : ℚ) : ℚ := rdn (a * a)
def sqHi (a : ℚ) : ℚ := rup (a * a)

def eLo : ℕ → ℚ → ℚ
  | 0, x => eLo0 x
  | j + 1, x => sqLo (eLo j (x / 2))

def eHi : ℕ → ℚ → ℚ
  | 0, x => eHi0 x
  | j + 1, x => sqHi (eHi j (x / 2))

theorem eLo_nonneg (j : ℕ) (x : ℚ) : 0 ≤ eLo j x := by
  cases j with
  | zero => exact le_max_left _ _
  | succ j => exact rdn_nonneg (mul_self_nonneg _)

theorem exp_halves (x : ℝ) : Real.exp x = Real.exp (x / 2) * Real.exp (x / 2) := by
  rw [← Real.exp_add]; ring_nf

theorem eLo_sound (j : ℕ) : ∀ x : ℚ, |(x : ℝ)| ≤ 2 ^ j → ((eLo j x : ℚ) : ℝ) ≤ Real.exp x := by
  induction j with
  | zero => intro x hx; show ((eLo0 x : ℚ) : ℝ) ≤ _; exact eLo0_sound x (by simpa using hx)
  | succ j ih =>
    intro x hx
    have h2 : |((x / 2 : ℚ) : ℝ)| ≤ 2 ^ j := by
      push_cast; rw [abs_div, abs_two, div_le_iff₀ (by norm_num)]; rw [pow_succ] at hx; linarith
    have ha := ih (x / 2) h2
    have hn : (0 : ℝ) ≤ (eLo j (x / 2) : ℝ) := by exact_mod_cast eLo_nonneg j (x / 2)
    show ((sqLo (eLo j (x / 2)) : ℚ) : ℝ) ≤ _
    unfold sqLo
    have := rdn_le_r (eLo j (x / 2) * eLo j (x / 2))
    push_cast at this ha
    rw [exp_halves]
    calc _ ≤ _ := this
      _ ≤ _ := mul_le_mul ha ha hn (Real.exp_pos _).le

theorem eHi_sound (j : ℕ) : ∀ x : ℚ, |(x : ℝ)| ≤ 2 ^ j → Real.exp x ≤ ((eHi j x : ℚ) : ℝ) := by
  induction j with
  | zero => intro x hx; show _ ≤ ((eHi0 x : ℚ) : ℝ); exact eHi0_sound x (by simpa using hx)
  | succ j ih =>
    intro x hx
    have h2 : |((x / 2 : ℚ) : ℝ)| ≤ 2 ^ j := by
      push_cast; rw [abs_div, abs_two, div_le_iff₀ (by norm_num)]; rw [pow_succ] at hx; linarith
    have ha := ih (x / 2) h2
    show _ ≤ ((sqHi (eHi j (x / 2)) : ℚ) : ℝ)
    unfold sqHi
    have := le_rup_r (eHi j (x / 2) * eHi j (x / 2))
    push_cast at this ha
    rw [exp_halves]
    calc _ ≤ _ := mul_le_mul ha ha (Real.exp_pos _).le ((Real.exp_pos _).le.trans ha)
      _ ≤ _ := this

/-- the halving depth: smallest j ≤ 12 with |x| ≤ 2^j / 4 (any value is sound; this one is fast). -/
def jFind (x : ℚ) : ℕ → ℕ → ℕ
  | j, 0 => j
  | j, f + 1 => if |x| ≤ 2 ^ j / 4 then j else jFind x (j + 1) f

def jOf (x : ℚ) : ℕ := jFind x 0 12

def expLo (x : ℚ) : ℚ := if |x| ≤ 2 ^ jOf x then eLo (jOf x) x else 0
def expHi (x : ℚ) : ℚ := if |x| ≤ 2 ^ jOf x then eHi (jOf x) x else 1

theorem expLo_sound (x : ℚ) : ((expLo x : ℚ) : ℝ) ≤ Real.exp x := by
  unfold expLo
  split_ifs with h
  · exact eLo_sound _ x (by exact_mod_cast h)
  · simpa using (Real.exp_pos _).le

theorem expHi_sound (x : ℚ) (hx : x ≤ 0) : Real.exp x ≤ ((expHi x : ℚ) : ℝ) := by
  unfold expHi
  split_ifs with h
  · exact eHi_sound _ x (by exact_mod_cast h)
  · push_cast; exact Real.exp_le_one_iff.2 (by exact_mod_cast hx)

/-! ## log enclosures: log (m+1) = log m - log (1 - 1/(m+1)) -/

def lnSum (x : ℚ) : ℕ → ℚ
  | 0 => 0
  | n + 1 => lnSum x n + x ^ (n + 1) / (n + 1)

def lnErr (x : ℚ) (n : ℕ) : ℚ := x ^ (n + 1) / (1 - x)

theorem lnSum_cast (x : ℚ) (n : ℕ) : ((lnSum x n : ℚ) : ℝ) = ∑ i ∈ range n, (x : ℝ) ^ (i + 1) / (i + 1) := by
  induction n with
  | zero => simp [lnSum]
  | succ n ih => rw [lnSum, sum_range_succ, ← ih]; push_cast; ring

/-- one telescoping step m → m+1 (m ≥ 1): new bounds (l', h') from old (l, h) with n series terms. -/
def logStep (m : ℕ) (l h l' h' : ℚ) (n : ℕ) : Bool :=
  decide (l' ≤ l + (lnSum (1 / (m + 1)) n - lnErr (1 / (m + 1)) n)) &&
  decide (h + (lnSum (1 / (m + 1)) n + lnErr (1 / (m + 1)) n) ≤ h')

theorem logStep_sound (m : ℕ) (hm : 1 ≤ m) (l h l' h' : ℚ) (n : ℕ) (hs : logStep m l h l' h' n = true)
    (hl : (l : ℝ) ≤ Real.log m) (hh : Real.log m ≤ h) :
    (l' : ℝ) ≤ Real.log ((m + 1 : ℕ) : ℝ) ∧ Real.log ((m + 1 : ℕ) : ℝ) ≤ h' := by
  simp only [logStep, Bool.and_eq_true, decide_eq_true_eq] at hs
  obtain ⟨h1, h2⟩ := hs
  have hm' : (1 : ℝ) ≤ m := by exact_mod_cast hm
  set x : ℝ := 1 / ((m : ℝ) + 1) with hx
  have hx0 : 0 < x := by rw [hx]; positivity
  have hx1 : x < 1 := by rw [hx, div_lt_one (by linarith)]; linarith
  have hax : |x| < 1 := by rw [abs_of_pos hx0]; exact hx1
  have hb := Real.abs_log_sub_add_sum_range_le hax n
  rw [abs_of_pos hx0] at hb
  have hlog : Real.log ((m + 1 : ℕ) : ℝ) = Real.log m - Real.log (1 - x) := by
    have e : 1 - x = (m : ℝ) / ((m : ℝ) + 1) := by rw [hx]; field_simp; ring
    rw [e, Real.log_div (by positivity) (by positivity)]; push_cast; ring
  have cS : ((lnSum (1 / (m + 1)) n : ℚ) : ℝ) = ∑ i ∈ range n, x ^ (i + 1) / (i + 1) := by
    rw [lnSum_cast]; push_cast; rfl
  have cE : ((lnErr (1 / (m + 1)) n : ℚ) : ℝ) = x ^ (n + 1) / (1 - x) := by
    unfold lnErr; push_cast; rfl
  have r1 : (l' : ℝ) ≤ l + ((lnSum (1 / (m + 1)) n : ℝ) - (lnErr (1 / (m + 1)) n : ℝ)) := by exact_mod_cast h1
  have r2 : (h : ℝ) + ((lnSum (1 / (m + 1)) n : ℝ) + (lnErr (1 / (m + 1)) n : ℝ)) ≤ h' := by exact_mod_cast h2
  rw [cS, cE] at r1 r2
  have hb' := abs_le.1 hb
  constructor <;> rw [hlog] <;> linarith [hb'.1, hb'.2]

/-- a log table: entry k = (lo, hi, n) bounds log (k+1); n = series terms for the step k+1 → k+2. -/
def logsOK : ℕ → List (ℚ × ℚ × ℕ) → Bool
  | _, [] => true
  | _, [_] => true
  | m, a :: b :: rest => logStep m a.1 a.2.1 b.1 b.2.1 a.2.2 && logsOK (m + 1) (b :: rest)

def LogTab (tb : List (ℚ × ℚ × ℕ)) : Prop :=
  ∀ k (hk : k < tb.length), ((tb[k]).1 : ℝ) ≤ Real.log ((k + 1 : ℕ) : ℝ) ∧ Real.log ((k + 1 : ℕ) : ℝ) ≤ (tb[k]).2.1

theorem logsOK_sound_aux : ∀ (L : List (ℚ × ℚ × ℕ)) (m : ℕ) (a : ℚ × ℚ × ℕ), 1 ≤ m → logsOK m (a :: L) = true →
    (a.1 : ℝ) ≤ Real.log m → Real.log m ≤ a.2.1 →
    ∀ k (hk : k < (a :: L).length), (((a :: L)[k]).1 : ℝ) ≤ Real.log ((m + k : ℕ) : ℝ) ∧
      Real.log ((m + k : ℕ) : ℝ) ≤ ((a :: L)[k]).2.1 := by
  intro L
  induction L with
  | nil =>
    intro m a _ _ hl hh k hk
    simp at hk; subst hk; simpa using ⟨hl, hh⟩
  | cons b rest ih =>
    intro m a hm hok hl hh k hk
    simp only [logsOK, Bool.and_eq_true] at hok
    obtain ⟨hs, hr⟩ := hok
    have hb := logStep_sound m hm a.1 a.2.1 b.1 b.2.1 a.2.2 hs hl hh
    cases k with
    | zero => simpa using ⟨hl, hh⟩
    | succ k =>
      have := ih (m + 1) b (by omega) hr hb.1 hb.2 k (by simpa using hk)
      simp only [List.getElem_cons_succ]
      rw [show m + (k + 1) = m + 1 + k by omega]
      exact this

theorem logsOK_sound (tb : List (ℚ × ℚ × ℕ)) (hok : logsOK 1 tb = true)
    (h0 : ∀ a ∈ tb.head?, a.1 ≤ 0 ∧ 0 ≤ a.2.1) : LogTab tb := by
  intro k hk
  cases tb with
  | nil => simp at hk
  | cons a L =>
    have ha := h0 a (by simp)
    have := logsOK_sound_aux L 1 a le_rfl hok (by simpa using (show (a.1 : ℝ) ≤ 0 by exact_mod_cast ha.1))
      (by simpa using (show (0 : ℝ) ≤ a.2.1 by exact_mod_cast ha.2)) k hk
    rw [show 1 + k = k + 1 by omega] at this
    exact this

/-! ## r^(1-t) enclosures -/

def lgLo (tb : List (ℚ × ℚ × ℕ)) (r : ℕ) : ℚ := (tb.getD (r - 1) (0, 0, 0)).1
def lgHi (tb : List (ℚ × ℚ × ℕ)) (r : ℕ) : ℚ := (tb.getD (r - 1) (0, 0, 0)).2.1

theorem lg_sound (tb : List (ℚ × ℚ × ℕ)) (ht : LogTab tb) (r : ℕ) (h1 : 1 ≤ r) (h2 : r ≤ tb.length) :
    (lgLo tb r : ℝ) ≤ Real.log r ∧ Real.log r ≤ lgHi tb r := by
  have hk : r - 1 < tb.length := by omega
  have := ht (r - 1) hk
  rw [show r - 1 + 1 = r by omega] at this
  unfold lgLo lgHi
  rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hk, Option.getD_some]
  exact this

def phiLo (tb : List (ℚ × ℚ × ℕ)) (r : ℕ) (t : ℚ) : ℚ := rdn (r * expLo (rdn (-(t * lgHi tb r))))
def phiHi (tb : List (ℚ × ℚ × ℕ)) (r : ℕ) (t : ℚ) : ℚ := rup (r * expHi (min 0 (rup (-(t * lgLo tb r)))))

theorem rpow_eq (r : ℕ) (hr : 1 ≤ r) (t : ℝ) : (r : ℝ) ^ (1 - t) = r * Real.exp (-(t * Real.log r)) := by
  have hp : (0 : ℝ) < r := by exact_mod_cast hr
  rw [Real.rpow_def_of_pos hp, show Real.log r * (1 - t) = Real.log r + -(t * Real.log r) by ring, Real.exp_add,
    Real.exp_log hp]

theorem phiLo_sound (tb : List (ℚ × ℚ × ℕ)) (ht : LogTab tb) (r : ℕ) (h1 : 1 ≤ r) (h2 : r ≤ tb.length)
    (t : ℚ) (h0 : 0 ≤ t) : ((phiLo tb r t : ℚ) : ℝ) ≤ (r : ℝ) ^ (1 - (t : ℝ)) := by
  have hl := lg_sound tb ht r h1 h2
  have ht0 : (0 : ℝ) ≤ t := by exact_mod_cast h0
  rw [rpow_eq r h1]
  unfold phiLo
  have e1 := rdn_le_r (-(t * lgHi tb r))
  have e2 := expLo_sound (rdn (-(t * lgHi tb r)))
  have e3 := rdn_le_r (r * expLo (rdn (-(t * lgHi tb r))))
  push_cast at e1 e3
  have hx : ((rdn (-(t * lgHi tb r)) : ℚ) : ℝ) ≤ -((t : ℝ) * Real.log r) := by
    have := mul_le_mul_of_nonneg_left hl.2 ht0; linarith
  have e4 := Real.exp_le_exp.2 hx
  have hr0 : (0 : ℝ) ≤ r := by positivity
  calc _ ≤ _ := e3
    _ ≤ _ := mul_le_mul_of_nonneg_left (e2.trans e4) hr0

theorem phiHi_sound (tb : List (ℚ × ℚ × ℕ)) (ht : LogTab tb) (r : ℕ) (h1 : 1 ≤ r) (h2 : r ≤ tb.length)
    (t : ℚ) (h0 : 0 ≤ t) : (r : ℝ) ^ (1 - (t : ℝ)) ≤ ((phiHi tb r t : ℚ) : ℝ) := by
  have hl := lg_sound tb ht r h1 h2
  have ht0 : (0 : ℝ) ≤ t := by exact_mod_cast h0
  have hlog0 : (0 : ℝ) ≤ Real.log r := Real.log_nonneg (by exact_mod_cast h1)
  rw [rpow_eq r h1]
  unfold phiHi
  set y : ℚ := min 0 (rup (-(t * lgLo tb r)))
  have e1 := le_rup_r (-(t * lgLo tb r))
  push_cast at e1
  have hx : -((t : ℝ) * Real.log r) ≤ (y : ℝ) := by
    show _ ≤ ((min 0 (rup (-(t * lgLo tb r))) : ℚ) : ℝ)
    push_cast
    apply le_min
    · have := mul_nonneg ht0 hlog0; linarith
    · have := mul_le_mul_of_nonneg_left hl.1 ht0; linarith
  have e2 := expHi_sound y (min_le_left _ _)
  have e3 := le_rup_r (r * expHi y)
  push_cast at e3
  have e4 := Real.exp_le_exp.2 hx
  have hr0 : (0 : ℝ) ≤ r := by positivity
  calc _ ≤ (r : ℝ) * (expHi y : ℝ) := mul_le_mul_of_nonneg_left (e4.trans e2) hr0
    _ ≤ _ := e3

/-! ## the invoice form and piece bounds -/

noncomputable def F (cs : List (ℤ × ℕ)) (t : ℝ) : ℝ := (cs.map fun p => (p.1 : ℝ) * (p.2 : ℝ) ^ (1 - t)).sum

def csOK (tb : List (ℚ × ℚ × ℕ)) (cs : List (ℤ × ℕ)) : Bool := cs.all fun p => decide (1 ≤ p.2 ∧ p.2 ≤ tb.length)

def ubP (tb : List (ℚ × ℚ × ℕ)) (cs : List (ℤ × ℕ)) (a b : ℚ) : ℚ :=
  (cs.map fun p => if 0 < p.1 then (p.1 : ℚ) * phiHi tb p.2 a else (p.1 : ℚ) * phiLo tb p.2 b).sum
def lbP (tb : List (ℚ × ℚ × ℕ)) (cs : List (ℤ × ℕ)) (a b : ℚ) : ℚ :=
  (cs.map fun p => if 0 < p.1 then (p.1 : ℚ) * phiLo tb p.2 b else (p.1 : ℚ) * phiHi tb p.2 a).sum
def tailP (tb : List (ℚ × ℚ × ℕ)) (cs : List (ℤ × ℕ)) (a : ℚ) : ℚ :=
  (cs.map fun p => if 0 < p.1 then (p.1 : ℚ) * phiHi tb p.2 a else if p.2 = 1 then (p.1 : ℚ) else 0).sum

theorem rpow_anti (r : ℕ) (hr : 1 ≤ r) {s t : ℝ} (h : s ≤ t) : (r : ℝ) ^ (1 - t) ≤ (r : ℝ) ^ (1 - s) :=
  Real.rpow_le_rpow_of_exponent_le (by exact_mod_cast hr) (by linarith)

theorem F_le_ub (tb : List (ℚ × ℚ × ℕ)) (ht : LogTab tb) (a b : ℚ) (ha : 0 ≤ a) (t : ℝ) (h1 : (a : ℝ) ≤ t)
    (h2 : t ≤ b) : ∀ cs : List (ℤ × ℕ), csOK tb cs = true → F cs t ≤ ubP tb cs a b := by
  have ha' : (0 : ℝ) ≤ a := by exact_mod_cast ha
  have hb' : (0 : ℝ) ≤ b := by linarith
  have hb : 0 ≤ b := by exact_mod_cast hb'
  intro cs
  induction cs with
  | nil => intro _; simp [F, ubP]
  | cons p rest ih =>
    intro hc
    simp only [csOK, List.all_cons, Bool.and_eq_true, decide_eq_true_eq] at hc
    have ih' := ih (by simpa [csOK] using hc.2)
    obtain ⟨hr1, hr2⟩ := hc.1
    simp only [F, ubP, List.map_cons, List.sum_cons] at ih' ⊢
    have hc' : ((if 0 < p.1 then (p.1 : ℚ) * phiHi tb p.2 a else (p.1 : ℚ) * phiLo tb p.2 b : ℚ) : ℝ) ≥
        (p.1 : ℝ) * (p.2 : ℝ) ^ (1 - t) := by
      split_ifs with hp
      · push_cast
        have hp' : (0 : ℝ) ≤ p.1 := by exact_mod_cast hp.le
        exact mul_le_mul_of_nonneg_left ((rpow_anti p.2 hr1 h1).trans (phiHi_sound tb ht p.2 hr1 hr2 a ha)) hp'
      · push_cast
        have hp' : (p.1 : ℝ) ≤ 0 := by exact_mod_cast not_lt.1 hp
        exact mul_le_mul_of_nonpos_left ((phiLo_sound tb ht p.2 hr1 hr2 b hb).trans (rpow_anti p.2 hr1 h2)) hp'
    rw [Rat.cast_add]
    linarith

theorem lb_le_F (tb : List (ℚ × ℚ × ℕ)) (ht : LogTab tb) (a b : ℚ) (ha : 0 ≤ a) (t : ℝ) (h1 : (a : ℝ) ≤ t)
    (h2 : t ≤ b) : ∀ cs : List (ℤ × ℕ), csOK tb cs = true → (lbP tb cs a b : ℝ) ≤ F cs t := by
  have ha' : (0 : ℝ) ≤ a := by exact_mod_cast ha
  have hb' : (0 : ℝ) ≤ b := by linarith
  have hb : 0 ≤ b := by exact_mod_cast hb'
  intro cs
  induction cs with
  | nil => intro _; simp [F, lbP]
  | cons p rest ih =>
    intro hc
    simp only [csOK, List.all_cons, Bool.and_eq_true, decide_eq_true_eq] at hc
    have ih' := ih (by simpa [csOK] using hc.2)
    obtain ⟨hr1, hr2⟩ := hc.1
    simp only [F, lbP, List.map_cons, List.sum_cons] at ih' ⊢
    have hc' : ((if 0 < p.1 then (p.1 : ℚ) * phiLo tb p.2 b else (p.1 : ℚ) * phiHi tb p.2 a : ℚ) : ℝ) ≤
        (p.1 : ℝ) * (p.2 : ℝ) ^ (1 - t) := by
      split_ifs with hp
      · push_cast
        have hp' : (0 : ℝ) ≤ p.1 := by exact_mod_cast hp.le
        exact mul_le_mul_of_nonneg_left ((phiLo_sound tb ht p.2 hr1 hr2 b hb).trans (rpow_anti p.2 hr1 h2)) hp'
      · push_cast
        have hp' : (p.1 : ℝ) ≤ 0 := by exact_mod_cast not_lt.1 hp
        exact mul_le_mul_of_nonpos_left ((rpow_anti p.2 hr1 h1).trans (phiHi_sound tb ht p.2 hr1 hr2 a ha)) hp'
    rw [Rat.cast_add]
    linarith

theorem F_le_tail (tb : List (ℚ × ℚ × ℕ)) (ht : LogTab tb) (a : ℚ) (ha : 0 ≤ a) (t : ℝ) (h1 : (a : ℝ) ≤ t) :
    ∀ cs : List (ℤ × ℕ), csOK tb cs = true → F cs t ≤ tailP tb cs a := by
  intro cs
  induction cs with
  | nil => intro _; simp [F, tailP]
  | cons p rest ih =>
    intro hc
    simp only [csOK, List.all_cons, Bool.and_eq_true, decide_eq_true_eq] at hc
    have ih' := ih (by simpa [csOK] using hc.2)
    obtain ⟨hr1, hr2⟩ := hc.1
    simp only [F, tailP, List.map_cons, List.sum_cons] at ih' ⊢
    have hc' : (p.1 : ℝ) * (p.2 : ℝ) ^ (1 - t) ≤
        ((if 0 < p.1 then (p.1 : ℚ) * phiHi tb p.2 a else if p.2 = 1 then (p.1 : ℚ) else 0 : ℚ) : ℝ) := by
      split_ifs with hp hr
      · push_cast
        have hp' : (0 : ℝ) ≤ p.1 := by exact_mod_cast hp.le
        exact mul_le_mul_of_nonneg_left ((rpow_anti p.2 hr1 h1).trans (phiHi_sound tb ht p.2 hr1 hr2 a ha)) hp'
      · push_cast; rw [hr]; simp
      · push_cast
        have hp' : (p.1 : ℝ) ≤ 0 := by exact_mod_cast not_lt.1 hp
        exact mul_nonpos_of_nonpos_of_nonneg hp' (Real.rpow_nonneg (by positivity) _)
    rw [Rat.cast_add]
    linarith

/-! ## chains -/

/-- lower chain from a: consecutive pieces [a,b] with lbP > 0. -/
def loOK (tb : List (ℚ × ℚ × ℕ)) (cs : List (ℤ × ℕ)) : ℚ → List ℚ → Bool
  | _, [] => true
  | a, b :: rest => decide (a ≤ b) && decide (0 < lbP tb cs a b) && loOK tb cs b rest

/-- upper chain from a: consecutive pieces [a,b] with ubP < 0, then the tail [last, ∞). -/
def upOK (tb : List (ℚ × ℚ × ℕ)) (cs : List (ℤ × ℕ)) : ℚ → List ℚ → Bool
  | a, [] => decide (tailP tb cs a < 0)
  | a, b :: rest => decide (a ≤ b) && decide (ubP tb cs a b < 0) && upOK tb cs b rest

theorem loOK_sound (tb : List (ℚ × ℚ × ℕ)) (ht : LogTab tb) (cs : List (ℤ × ℕ)) (hc : csOK tb cs = true) :
    ∀ (l : List ℚ) (a : ℚ), 0 ≤ a → loOK tb cs a l = true →
      ∀ t : ℝ, (a : ℝ) ≤ t → t ≤ (l.getLastD a : ℝ) → (l ≠ [] ∨ True) → 0 < F cs t ∨ l = [] := by
  intro l
  induction l with
  | nil => intros; right; rfl
  | cons b rest ih =>
    intro a ha hok t h1 h2 _
    left
    simp only [loOK, Bool.and_eq_true, decide_eq_true_eq] at hok
    obtain ⟨⟨hab, hpos⟩, hr⟩ := hok
    have hb0 : 0 ≤ b := ha.trans hab
    by_cases htb : t ≤ b
    · have := lb_le_F tb ht a b ha t h1 htb cs hc
      have hp : (0 : ℝ) < lbP tb cs a b := by exact_mod_cast hpos
      linarith
    · push Not at htb
      cases rest with
      | nil => simp at h2; linarith
      | cons c rest' =>
        rcases ih b hb0 hr t htb.le (by simpa [List.getLastD] using h2) (Or.inr trivial) with h | h
        · exact h
        · simp at h

theorem upOK_sound (tb : List (ℚ × ℚ × ℕ)) (ht : LogTab tb) (cs : List (ℤ × ℕ)) (hc : csOK tb cs = true) :
    ∀ (l : List ℚ) (a : ℚ), 0 ≤ a → upOK tb cs a l = true → ∀ t : ℝ, (a : ℝ) ≤ t → F cs t < 0 := by
  intro l
  induction l with
  | nil =>
    intro a ha hok t h1
    simp only [upOK, decide_eq_true_eq] at hok
    have := F_le_tail tb ht a ha t h1 cs hc
    have hn : (tailP tb cs a : ℝ) < 0 := by exact_mod_cast hok
    linarith
  | cons b rest ih =>
    intro a ha hok t h1
    simp only [upOK, Bool.and_eq_true, decide_eq_true_eq] at hok
    obtain ⟨⟨hab, hneg⟩, hr⟩ := hok
    by_cases htb : t ≤ b
    · have := F_le_ub tb ht a b ha t h1 htb cs hc
      have hn : (ubP tb cs a b : ℝ) < 0 := by exact_mod_cast hneg
      linarith
    · push Not at htb
      exact ih b (ha.trans hab) hr t htb.le

/-- positivity on one chunk [a, last]. -/
theorem pos_chunk (tb : List (ℚ × ℚ × ℕ)) (ht : LogTab tb) (cs : List (ℤ × ℕ)) (hc : csOK tb cs = true)
    (a : ℚ) (b : ℚ) (l : List ℚ) (ha : 0 ≤ a) (hok : loOK tb cs a (l ++ [b]) = true) :
    ∀ t : ℝ, (a : ℝ) ≤ t → t ≤ (b : ℝ) → 0 < F cs t := by
  intro t h1 h2
  rcases loOK_sound tb ht cs hc (l ++ [b]) a ha hok t h1 (by simpa using h2) (Or.inr trivial) with h | h
  · exact h
  · simp at h

/-- a middle upper chunk [a, last]: pieces with ubP < 0 (no tail). -/
def upC (tb : List (ℚ × ℚ × ℕ)) (cs : List (ℤ × ℕ)) : ℚ → List ℚ → Bool
  | _, [] => true
  | a, b :: rest => decide (a ≤ b) && decide (ubP tb cs a b < 0) && upC tb cs b rest

theorem upC_sound (tb : List (ℚ × ℚ × ℕ)) (ht : LogTab tb) (cs : List (ℤ × ℕ)) (hc : csOK tb cs = true) :
    ∀ (l : List ℚ) (a : ℚ), 0 ≤ a → upC tb cs a l = true →
      ∀ t : ℝ, (a : ℝ) ≤ t → t ≤ (l.getLastD a : ℝ) → l ≠ [] → F cs t < 0 := by
  intro l
  induction l with
  | nil => intros; contradiction
  | cons b rest ih =>
    intro a ha hok t h1 h2 _
    simp only [upC, Bool.and_eq_true, decide_eq_true_eq] at hok
    obtain ⟨⟨hab, hneg⟩, hr⟩ := hok
    by_cases htb : t ≤ b
    · have := F_le_ub tb ht a b ha t h1 htb cs hc
      have hn : (ubP tb cs a b : ℝ) < 0 := by exact_mod_cast hneg
      linarith
    · push Not at htb
      cases rest with
      | nil => simp at h2; linarith
      | cons c rest' => exact ih b (ha.trans hab) hr t htb.le (by simpa [List.getLastD] using h2) (by simp)

theorem neg_chunk (tb : List (ℚ × ℚ × ℕ)) (ht : LogTab tb) (cs : List (ℤ × ℕ)) (hc : csOK tb cs = true)
    (a : ℚ) (b : ℚ) (l : List ℚ) (ha : 0 ≤ a) (hok : upC tb cs a (l ++ [b]) = true) :
    ∀ t : ℝ, (a : ℝ) ≤ t → t ≤ (b : ℝ) → F cs t < 0 :=
  fun t h1 h2 => upC_sound tb ht cs hc (l ++ [b]) a ha hok t h1 (by simpa using h2) (by simp)

theorem neg_tail (tb : List (ℚ × ℚ × ℕ)) (ht : LogTab tb) (cs : List (ℤ × ℕ)) (hc : csOK tb cs = true)
    (a : ℚ) (ha : 0 ≤ a) (hok : decide (tailP tb cs a < 0) = true) : ∀ t : ℝ, (a : ℝ) ≤ t → F cs t < 0 :=
  upOK_sound tb ht cs hc [] a ha hok

theorem join {P : ℝ → Prop} {a b c : ℝ} (h1 : ∀ t, a ≤ t → t ≤ b → P t) (h2 : ∀ t, b ≤ t → t ≤ c → P t) :
    ∀ t, a ≤ t → t ≤ c → P t := by
  intro t ha hc
  rcases le_total t b with h | h
  · exact h1 t ha h
  · exact h2 t h hc

theorem join_tail {P : ℝ → Prop} {a b : ℝ} (h1 : ∀ t, a ≤ t → t ≤ b → P t) (h2 : ∀ t, b ≤ t → P t) :
    ∀ t, a ≤ t → P t := by
  intro t ha
  rcases le_total t b with h | h
  · exact h1 t ha h
  · exact h2 t h

theorem logsOK_sound0 (n0 : ℕ) (L : List (ℚ × ℚ × ℕ)) (hok : logsOK 1 ((0, 0, n0) :: L) = true) :
    LogTab ((0, 0, n0) :: L) :=
  logsOK_sound _ hok (by intro a ha; simp at ha; subst ha; simp)

/-! ## the root -/

theorem F_cont (cs : List (ℤ × ℕ)) (hc : ∀ p ∈ cs, 1 ≤ p.2) : Continuous (F cs) := by
  induction cs with
  | nil =>
    have e : F [] = fun _ => 0 := by funext t; simp [F]
    rw [e]; exact continuous_const
  | cons p rest ih =>
    have ih' := ih (fun q hq => hc q (by simp [hq]))
    have hp : (0 : ℝ) < p.2 := by exact_mod_cast hc p (by simp)
    have e : F (p :: rest) = fun t => (p.1 : ℝ) * (p.2 : ℝ) ^ (1 - t) + F rest t := by
      funext t; simp [F]
    rw [e]
    exact (continuous_const.mul (continuous_const.rpow (continuous_const.sub continuous_id)
      (fun _ => Or.inl hp.ne'))).add ih'

theorem csOK_ge (tb : List (ℚ × ℚ × ℕ)) (cs : List (ℤ × ℕ)) (hc : csOK tb cs = true) : ∀ p ∈ cs, 1 ≤ p.2 := by
  intro p hp
  have := List.all_eq_true.1 hc p hp
  simp only [decide_eq_true_eq] at this
  exact this.1

/-- PRICEKIT's κ: the last crossing of the invoice form on [0, ∞). -/
noncomputable def kroot (cs : List (ℤ × ℕ)) : ℝ := sSup {t : ℝ | 0 ≤ t ∧ 0 ≤ F cs t}

theorem kroot_bracket (cs : List (ℤ × ℕ)) (hc : ∀ p ∈ cs, 1 ≤ p.2) (lo hi : ℝ) (h0 : 0 ≤ lo)
    (hpos : ∀ t, 0 ≤ t → t ≤ lo → 0 < F cs t) (hneg : ∀ t, hi ≤ t → F cs t < 0) :
    lo ≤ kroot cs ∧ kroot cs ≤ hi ∧ F cs (kroot cs) = 0 ∧ (∀ t, 0 ≤ t → F cs t = 0 → lo < t ∧ t < hi) := by
  set S := {t : ℝ | 0 ≤ t ∧ 0 ≤ F cs t}
  have hloS : lo ∈ S := ⟨h0, (hpos lo h0 le_rfl).le⟩
  have hlt : ∀ t ∈ S, t < hi := by
    intro t ht; by_contra h; push Not at h; have := hneg t h; linarith [ht.2]
  have hbdd : BddAbove S := ⟨hi, fun t ht => (hlt t ht).le⟩
  have hne : S.Nonempty := ⟨lo, hloS⟩
  have h1 : lo ≤ kroot cs := le_csSup hbdd hloS
  have h2 : kroot cs ≤ hi := csSup_le hne (fun t ht => (hlt t ht).le)
  have hcont := (F_cont cs hc).continuousAt (x := kroot cs)
  rw [Metric.continuousAt_iff] at hcont
  have hs0 : 0 ≤ kroot cs := h0.trans h1
  have h3 : F cs (kroot cs) = 0 := by
    rcases lt_trichotomy (F cs (kroot cs)) 0 with hF | hF | hF
    · exfalso
      obtain ⟨δ, hδ, hδF⟩ := hcont (-(F cs (kroot cs))) (by linarith)
      obtain ⟨t, htS, ht⟩ := exists_lt_of_lt_csSup hne (show kroot cs - δ < kroot cs by linarith)
      have hts : t ≤ kroot cs := le_csSup hbdd htS
      have := hδF (x := t) (by rw [Real.dist_eq, abs_lt]; constructor <;> linarith)
      rw [Real.dist_eq, abs_lt] at this
      linarith [htS.2, this.2]
    · exact hF
    · exfalso
      obtain ⟨δ, hδ, hδF⟩ := hcont (F cs (kroot cs)) hF
      have hin : kroot cs + δ / 2 ∈ S := by
        refine ⟨by linarith, ?_⟩
        have := hδF (x := kroot cs + δ / 2) (by rw [Real.dist_eq, abs_lt]; constructor <;> linarith)
        rw [Real.dist_eq, abs_lt] at this
        linarith [this.1]
      have : kroot cs + δ / 2 ≤ kroot cs := le_csSup hbdd hin
      linarith
  refine ⟨h1, h2, h3, fun t ht hF => ⟨?_, ?_⟩⟩
  · by_contra h; push Not at h; have := hpos t ht h; linarith
  · by_contra h; push Not at h; have := hneg t h; linarith

end CertKit

#print axioms CertKit.kroot_bracket
#print axioms CertKit.upOK_sound
#print axioms CertKit.pos_chunk
#print axioms CertKit.logsOK_sound
