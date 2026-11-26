import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity

/-! A direct cubic proof of the adaptive binary Walsh potential decrement. -/
namespace Moonshot.AlignedWalsh.Clock

noncomputable def logTwo (x : ℝ) : ℝ := Real.log (x+2)/Real.log 2
noncomputable def phi (x : ℝ) : ℝ := (x^2*logTwo x)^(1/3:ℝ)
noncomputable def psi (y : ℝ) : ℝ := Real.sqrt (y*logTwo y)

private lemma logTwo_nonneg {x : ℝ} (hx : 0≤x) : 0≤logTwo x :=
  div_nonneg (Real.log_nonneg (by linarith)) (Real.log_pos (by norm_num)).le

private lemma logTwo_mono {x y : ℝ} (hx : 0≤x) (hxy : x≤y) : logTwo x ≤ logTwo y :=
  div_le_div_of_nonneg_right (Real.log_le_log (by linarith) (by linarith)) (Real.log_pos (by norm_num)).le

private lemma phi_nonneg {x : ℝ} (hx : 0≤x) : 0≤phi x :=
  Real.rpow_nonneg (mul_nonneg (sq_nonneg x) (logTwo_nonneg hx)) _

private lemma phi_cube {x : ℝ} (hx : 0≤x) : (phi x)^3 = x^2*logTwo x := by
  unfold phi
  have hn := mul_nonneg (sq_nonneg x) (logTwo_nonneg hx)
  rw [← Real.rpow_natCast, ← Real.rpow_mul hn]
  norm_num

/-- Rounded child widths decremented by y/2 lose at least one third of the local
square-root/log charge in the *actual* base-two cube-root potential. -/
theorem numerical_decrement {x xp y : ℝ} (hx : 0<x) (hxp : 0≤xp) (hy : 0≤y)
    (hyx : y≤x) (hstep : xp≤x-y/2) (harity : phi x≤y) :
    psi y/3 ≤ phi x-phi xp := by
  have hx0 := hx.le
  have hp := phi_nonneg hx0
  have hpp := phi_nonneg hxp
  have hL := logTwo_nonneg hx0
  have hs := Real.sqrt_nonneg (y*logTwo y)
  have hmid : 0 ≤ x-y/2 := by linarith
  have hsub : xp^2*logTwo xp ≤ (x-y/2)^2*logTwo x :=
    mul_le_mul (pow_le_pow_left₀ hxp hstep 2) (logTwo_mono hxp (by linarith))
      (logTwo_nonneg hxp) (sq_nonneg _)
  have hpoly : (3*x)^3*(x-y/2)^2 ≤ (3*x-y)^3*x^2 := by
    have hlast : 0≤9*x/4-y := by linarith
    have hprod := mul_nonneg (mul_nonneg (sq_nonneg x) (sq_nonneg y)) hlast
    nlinarith only [hprod]
  have hcube : (3*x*phi xp)^3 ≤ ((3*x-y)*phi x)^3 := calc
    _ = (3*x)^3*(xp^2*logTwo xp) := by rw [mul_pow,phi_cube hxp]
    _ ≤ (3*x)^3*((x-y/2)^2*logTwo x) := mul_le_mul_of_nonneg_left hsub (by positivity)
    _ = ((3*x)^3*(x-y/2)^2)*logTwo x := by ring
    _ ≤ ((3*x-y)^3*x^2)*logTwo x := mul_le_mul_of_nonneg_right hpoly hL
    _ = _ := by rw [mul_pow,phi_cube hx0]; ring
  have hcoeff : 0≤3*x-y := by linarith
  have hdec := (pow_le_pow_iff_left₀ (mul_nonneg (by positivity) hpp)
    (mul_nonneg hcoeff hp) (by decide : (3:ℕ)≠0)).mp hcube
  have hsqs : (x*psi y)^2 ≤ (y*phi x)^2 := calc
    _ = x^2*y*logTwo y := by
      rw [psi,mul_pow,Real.sq_sqrt (mul_nonneg hy (logTwo_nonneg hy))]
      ring
    _ ≤ x^2*y*logTwo x := mul_le_mul_of_nonneg_left (logTwo_mono hy hyx)
      (mul_nonneg (sq_nonneg _) hy)
    _ = y*(phi x)^3 := by rw [phi_cube hx0]; ring
    _ ≤ y*(y*(phi x)^2) := by
      apply mul_le_mul_of_nonneg_left _ hy
      rw [show (phi x)^3=phi x*(phi x)^2 by ring]
      exact mul_le_mul_of_nonneg_right harity (sq_nonneg _)
    _ = _ := by ring
  have hps := (pow_le_pow_iff_left₀ (mul_nonneg hx0 hs)
    (mul_nonneg hy hp) (by decide : (2:ℕ)≠0)).mp hsqs
  change x*psi y ≤ y*phi x at hps
  have hfinal : x*psi y ≤ x*(3*(phi x-phi xp)) := by nlinarith only [hdec,hps]
  have := le_of_mul_le_mul_left hfinal hx
  linarith

/-- Full multiplicity up to 2^(10ψ), including the normalized square-root volume,
spends at most one quarter of the parent's clock at coefficient 36. -/
theorem quarter_clock {x xp y B M : ℝ} (hx : 0<x) (hxp : 0≤xp) (hy : 0≤y)
    (hyx : y≤x) (hstep : xp≤x-y/2) (harity : phi x≤y) (hpsi : 1≤psi y)
    (hB : 36≤B) (hM : M≤(2:ℝ)^(10*psi y)) :
    M*(2:ℝ)^(B*phi xp) ≤ (1/4)*(2:ℝ)^(B*phi x) := by
  have hd := numerical_decrement hx hxp hy hyx hstep harity
  have hpos : 0≤phi x-phi xp := by linarith
  have hm := mul_le_mul_of_nonneg_right hB hpos
  calc
    _ ≤ (2:ℝ)^(10*psi y)*(2:ℝ)^(B*phi xp) :=
      mul_le_mul_of_nonneg_right hM (Real.rpow_nonneg (by norm_num) _)
    _ = (2:ℝ)^(10*psi y+B*phi xp) := (Real.rpow_add (by norm_num) _ _).symm
    _ ≤ (2:ℝ)^(B*phi x-2) := Real.rpow_le_rpow_of_exponent_le (by norm_num)
      (by nlinarith only [hd,hm,hpsi])
    _ = _ := by rw [Real.rpow_sub (by norm_num)]; norm_num; ring

/-- Each of the two sequential outgoing finite jobs receives one eighth of the
current dense row population. The terminal dense transform calls one per axis. -/
theorem two_eighth_invoice {C : ℕ → ℝ} {d R A : ℝ} (hd : 0 ≤ d) (hR : 0 ≤ R)
    (hterminal : C 0 ≤ A) (hstep : ∀ h, C (h+1) ≤ 2*d*R+C h/4) (h : ℕ) :
    C h ≤ (8/3)*d*R+A*(1/4)^h := by
  induction h with
  | zero =>
    have hp : 0 ≤ (8/3)*d*R := mul_nonneg (mul_nonneg (by norm_num) hd) hR
    simpa using hterminal.trans (le_add_of_nonneg_left hp)
  | succ h ih =>
    calc
      C (h+1) ≤ 2*d*R + C h/4 := hstep h
      _ ≤ 2*d*R + ((8/3)*d*R+A*(1/4)^h)/4 := by
        apply add_le_add_right
        exact div_le_div_of_nonneg_right ih (by norm_num)
      _ = _ := by rw [pow_succ]; ring

/-- Multiply the full row invoice by the precise offspring/parent square-root
ratio before accumulating it in the global potential. -/
theorem square_root_invoice {m A a f d R mass t : ℝ}
    (hm : 0 ≤ m) (hA : 0 < A) (ha : 0 < a) (hf : 0 ≤ f)
    (hR : 1 ≤ R) (ht : 0 ≤ t) (hAm : 2*m ≤ A) (hmA : A ≤ 4*m)
    (hslot : A*f ≤ a) (hdegree : d ≤ 7*Real.sqrt m) (hdepth : t*Real.sqrt m ≤ 1)
    (htotal : mass ≤ (8/3)*d*R+A*t) :
    mass*Real.sqrt (f/a) ≤ 16*R := by
  let S := Real.sqrt (f/a)
  have hS : 0 ≤ S := Real.sqrt_nonneg _
  have hAs := Real.sqrt_nonneg A
  have hms := Real.sqrt_nonneg m
  have hsquare : A*(f/a) ≤ 1 := by
    rw [←mul_div_assoc]
    exact (div_le_one ha).mpr hslot
  have hunit : Real.sqrt A*S ≤ 1 := by
    apply (pow_le_pow_iff_left₀ (mul_nonneg hAs hS) (by norm_num) (by decide : 2≠0)).mp
    change (Real.sqrt A*Real.sqrt (f/a))^2 ≤ 1^2
    rw [mul_pow, Real.sq_sqrt hA.le, Real.sq_sqrt (div_nonneg hf ha.le), one_pow]
    exact hsquare
  have hseven : 7*Real.sqrt m ≤ 5*Real.sqrt A := by
    apply (pow_le_pow_iff_left₀ (mul_nonneg (by norm_num) hms)
      (mul_nonneg (by norm_num) hAs) (by decide : 2≠0)).mp
    rw [mul_pow,mul_pow,Real.sq_sqrt hm,Real.sq_sqrt hA.le]
    nlinarith only [hAm,hm]
  have hdouble : Real.sqrt A ≤ 2*Real.sqrt m := by
    apply (pow_le_pow_iff_left₀ hAs (mul_nonneg (by norm_num) hms) (by decide : 2≠0)).mp
    rw [mul_pow,Real.sq_sqrt hm,Real.sq_sqrt hA.le]
    nlinarith only [hmA]
  have hpoly : d*S ≤ 5 := calc
    _ ≤ (5*Real.sqrt A)*S := mul_le_mul_of_nonneg_right (hdegree.trans hseven) hS
    _ = 5*(Real.sqrt A*S) := by ring
    _ ≤ 5 := by nlinarith only [hunit]
  have hsmall : Real.sqrt A*t ≤ 2 := by
    have := mul_le_mul_of_nonneg_right hdouble ht
    nlinarith only [this,hdepth]
  have hterm : A*t*S ≤ 2 := calc
    _ = (Real.sqrt A)^2*t*S := by rw [Real.sq_sqrt hA.le]
    _ = (Real.sqrt A*t)*(Real.sqrt A*S) := by ring
    _ ≤ 2*1 := mul_le_mul hsmall hunit (mul_nonneg hAs hS) (by norm_num)
    _ = 2 := by ring
  have hprod := mul_le_mul_of_nonneg_right hpoly (show 0≤R by linarith)
  have hvolume := mul_le_mul_of_nonneg_right htotal hS
  change mass*S ≤ 16*R
  nlinarith only [hprod,hvolume,hterm,hR]

/-- The implemented two-eighth finite conversions, their full terminal, and every
extracted dense spatial child use at most a quarter of the parent clock. -/
theorem finite_to_quarter {C : ℕ → ℝ} {m A a f d R x xp y B : ℝ} {h : ℕ}
    (hm : 0 ≤ m) (hA : 0 < A) (ha : 0 < a) (hf : 0 ≤ f) (hd : 0 ≤ d)
    (hR : 1 ≤ R) (hAm : 2*m ≤ A) (hmA : A ≤ 4*m) (hslot : A*f ≤ a)
    (hdegree : d ≤ 7*Real.sqrt m) (hdepth : (1/4)^h*Real.sqrt m ≤ 1)
    (hterminal : C 0 ≤ A) (hstep : ∀ n, C (n+1) ≤ 2*d*R+C n/4)
    (hx : 0 < x) (hxp : 0 ≤ xp) (hy : 0 ≤ y) (hyx : y ≤ x)
    (hwidth : xp ≤ x-y/2) (harity : phi x ≤ y) (hpsi : 1 ≤ psi y)
    (hB : 36 ≤ B) (hpencil : 16*R ≤ (2:ℝ)^(10*psi y)) :
    C h*Real.sqrt (f/a)*(2:ℝ)^(B*phi xp) ≤ (1/4)*(2:ℝ)^(B*phi x) := by
  have htotal := two_eighth_invoice hd (show 0≤R by linarith) hterminal hstep h
  have hvol := square_root_invoice hm hA ha hf hR (pow_nonneg (by norm_num) h)
    hAm hmA hslot hdegree hdepth htotal
  exact quarter_clock hx hxp hy hyx hwidth harity hpsi hB (hvol.trans hpencil)

end Moonshot.AlignedWalsh.Clock
