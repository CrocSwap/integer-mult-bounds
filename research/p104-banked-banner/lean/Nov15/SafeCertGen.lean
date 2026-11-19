/-
SafeCertGen .  Generic machinery to discharge CertP0 / CertU0 EXACTLY (no hypothesis).
phi r t = r^(1-t) is convex in t (weighted AM-GM).  For an exponential sum F(t) = sum q_j r_j^(1-t):
 on a piece [a,b] with a previous point x < a:  F t <= (b-t)/(b-a) * F a + (t-a)/(b-a) * G,
 G = sum_{q>0} q phi(b) + sum_{q<=0} q (phi a + (phi a - phi x)(b-a)/(a-x))      (chord above, secant extension below).
 So negativity of F a and of G gives negativity on the whole piece.  Rational enclosures a/d <= r^(1-k/Q) <= b/d
 are certified by the integer inequalities a^Q <= r^(Q-k) d^Q (kernel Nat arithmetic).
Kernel only: no sorry, no native_decide, no axioms.
-/
import Mathlib.Analysis.MeanInequalities
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.FieldSimp

namespace SafeCertGen

noncomputable def phi (r t : ℝ) : ℝ := r ^ (1 - t)

theorem phi_pos {r : ℝ} (hr : 0 < r) (t : ℝ) : 0 < phi r t := Real.rpow_pos_of_pos hr _

theorem chord_le {r : ℝ} (hr : 0 < r) {a b t : ℝ} (hab : a < b) (h1 : a ≤ t) (h2 : t ≤ b) :
    phi r t ≤ ((b - t) * phi r a + (t - a) * phi r b) / (b - a) := by
  have hba : 0 < b - a := by linarith
  have hw1 : 0 ≤ (b - t) / (b - a) := div_nonneg (by linarith) hba.le
  have hw2 : 0 ≤ (t - a) / (b - a) := div_nonneg (by linarith) hba.le
  have hsum : (b - t) / (b - a) + (t - a) / (b - a) = 1 := by field_simp; ring
  have h := Real.geom_mean_le_arith_mean2_weighted hw1 hw2 (phi_pos hr a).le (phi_pos hr b).le hsum
  have e : phi r a ^ ((b - t) / (b - a)) * phi r b ^ ((t - a) / (b - a)) = phi r t := by
    unfold phi
    rw [← Real.rpow_mul hr.le, ← Real.rpow_mul hr.le, ← Real.rpow_add hr]
    congr 1
    field_simp; ring
  rw [e] at h
  have e2 : ((b - t) * phi r a + (t - a) * phi r b) / (b - a)
      = (b - t) / (b - a) * phi r a + (t - a) / (b - a) * phi r b := by ring
  rw [e2]; exact h

theorem sec_ge {r : ℝ} (hr : 0 < r) {x a t : ℝ} (hxa : x < a) (h1 : a ≤ t) :
    phi r a + (phi r a - phi r x) * (t - a) / (a - x) ≤ phi r t := by
  have hax : 0 < a - x := by linarith
  rcases h1.eq_or_lt with h | h
  · subst h; simp
  · have hc := chord_le hr (show x < t by linarith) (le_of_lt hxa) h1
    have htx : 0 < t - x := by linarith
    rw [le_div_iff₀ htx] at hc
    have key : (phi r a - phi r x) * (t - a) / (a - x) ≤ phi r t - phi r a := by
      rw [div_le_iff₀ hax]; nlinarith [hc]
    linarith

/-- an exponential sum, terms (coefficient q, rank r), F t = sum q * r^(1-t). -/
noncomputable def Fl (cs : List (ℝ × ℝ)) (t : ℝ) : ℝ := (cs.map fun p => p.1 * phi p.2 t).sum

/-- the piece upper envelope value at b. -/
noncomputable def Gl (cs : List (ℝ × ℝ)) (x a b : ℝ) : ℝ :=
  (cs.map fun p => if 0 < p.1 then p.1 * phi p.2 b
    else p.1 * (phi p.2 a + (phi p.2 a - phi p.2 x) * (b - a) / (a - x))).sum

theorem piece_le (cs : List (ℝ × ℝ)) (hr : ∀ p ∈ cs, 0 < p.2) {x a b t : ℝ}
    (hxa : x < a) (hab : a < b) (h1 : a ≤ t) (h2 : t ≤ b) :
    Fl cs t ≤ (b - t) / (b - a) * Fl cs a + (t - a) / (b - a) * Gl cs x a b := by
  have hba : 0 < b - a := by linarith
  induction cs with
  | nil => simp [Fl, Gl]
  | cons p rest ih =>
    have ih' := ih (fun q hq => hr q (by simp [hq]))
    have hp := hr p (by simp)
    simp only [Fl, Gl, List.map_cons, List.sum_cons] at ih' ⊢
    have hch := chord_le hp hab h1 h2
    have hsc := sec_ge hp hxa h1 (t := t)
    by_cases hq : 0 < p.1
    · simp only [hq, if_true]
      have : p.1 * phi p.2 t ≤ p.1 * (((b - t) * phi p.2 a + (t - a) * phi p.2 b) / (b - a)) :=
        mul_le_mul_of_nonneg_left hch hq.le
      have e : p.1 * (((b - t) * phi p.2 a + (t - a) * phi p.2 b) / (b - a))
          = (b - t) / (b - a) * (p.1 * phi p.2 a) + (t - a) / (b - a) * (p.1 * phi p.2 b) := by ring
      rw [e] at this
      nlinarith [ih', this]
    · simp only [hq, if_false]
      push_neg at hq
      have h3 : p.1 * phi p.2 t ≤ p.1 * (phi p.2 a + (phi p.2 a - phi p.2 x) * (t - a) / (a - x)) :=
        mul_le_mul_of_nonpos_left hsc hq
      have hax : a - x ≠ 0 := by linarith
      have e : p.1 * (phi p.2 a + (phi p.2 a - phi p.2 x) * (t - a) / (a - x))
          = (b - t) / (b - a) * (p.1 * phi p.2 a) + (t - a) / (b - a) *
            (p.1 * (phi p.2 a + (phi p.2 a - phi p.2 x) * (b - a) / (a - x))) := by
        field_simp; ring
      rw [e] at h3
      nlinarith [ih', h3]

end SafeCertGen

namespace SafeCertGen

theorem enc_lo (rn kn Qn An Dn : ℕ) (r t A D : ℝ) (hr : r = rn) (ht : t = kn / Qn) (hA : A = An)
    (hD : D = Dn) (hQ : 0 < Qn) (hk : kn ≤ Qn) (hDp : 0 < Dn)
    (h : An ^ Qn ≤ rn ^ (Qn - kn) * Dn ^ Qn) (hrp : 0 < rn) : A / D ≤ phi r t := by
  subst hr ht hA hD
  have hQr : (0:ℝ) < Qn := by exact_mod_cast hQ
  have hDr : (0:ℝ) < Dn := by exact_mod_cast hDp
  have hrr : (0:ℝ) < rn := by exact_mod_cast hrp
  have e : phi (rn:ℝ) ((kn:ℝ) / Qn) = (rn:ℝ) ^ (((Qn - kn : ℕ) : ℝ) / Qn) := by
    unfold phi; congr 1
    rw [Nat.cast_sub hk]; field_simp
  rw [e]
  have h1 : ((An:ℝ) / Dn) ^ Qn ≤ ((rn:ℝ) ^ (((Qn - kn : ℕ) : ℝ) / Qn)) ^ Qn := by
    rw [← Real.rpow_natCast ((rn:ℝ) ^ _) Qn, ← Real.rpow_mul hrr.le]
    have : ((Qn - kn : ℕ) : ℝ) / Qn * (Qn:ℝ) = ((Qn - kn : ℕ) : ℝ) := by field_simp
    rw [this, Real.rpow_natCast, div_pow, div_le_iff₀ (by positivity)]
    exact_mod_cast h
  exact (pow_le_pow_iff_left₀ (by positivity) (by positivity) (by omega)).1 h1

theorem enc_hi (rn kn Qn Bn Dn : ℕ) (r t B D : ℝ) (hr : r = rn) (ht : t = kn / Qn) (hB : B = Bn)
    (hD : D = Dn) (hQ : 0 < Qn) (hk : kn ≤ Qn) (hDp : 0 < Dn)
    (h : rn ^ (Qn - kn) * Dn ^ Qn ≤ Bn ^ Qn) (hrp : 0 < rn) : phi r t ≤ B / D := by
  subst hr ht hB hD
  have hQr : (0:ℝ) < Qn := by exact_mod_cast hQ
  have hDr : (0:ℝ) < Dn := by exact_mod_cast hDp
  have hrr : (0:ℝ) < rn := by exact_mod_cast hrp
  have e : phi (rn:ℝ) ((kn:ℝ) / Qn) = (rn:ℝ) ^ (((Qn - kn : ℕ) : ℝ) / Qn) := by
    unfold phi; congr 1
    rw [Nat.cast_sub hk]; field_simp
  rw [e]
  have h1 : ((rn:ℝ) ^ (((Qn - kn : ℕ) : ℝ) / Qn)) ^ Qn ≤ ((Bn:ℝ) / Dn) ^ Qn := by
    rw [← Real.rpow_natCast ((rn:ℝ) ^ _) Qn, ← Real.rpow_mul hrr.le]
    have : ((Qn - kn : ℕ) : ℝ) / Qn * (Qn:ℝ) = ((Qn - kn : ℕ) : ℝ) := by field_simp
    rw [this, Real.rpow_natCast, div_pow, le_div_iff₀ (by positivity)]
    exact_mod_cast h
  exact (pow_le_pow_iff_left₀ (by positivity) (by positivity) (by omega)).1 h1

theorem phi_one (t : ℝ) : phi 1 t = 1 := by simp [phi]

theorem conv_neg (w1 w2 u v : ℝ) (h1 : 0 ≤ w1) (h2 : 0 ≤ w2) (hs : w1 + w2 = 1) (hu : u < 0)
    (hv : v < 0) : w1 * u + w2 * v < 0 := by
  rcases le_total u v with h | h
  · have := mul_le_mul_of_nonneg_left h h1
    nlinarith
  · have := mul_le_mul_of_nonneg_left h h2
    nlinarith

end SafeCertGen
