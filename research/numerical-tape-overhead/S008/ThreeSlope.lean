import S008.WholeProfile
import S008.PiecewiseHistory

/-! Actual binary arity eligibility, an infinite normalized-height induction,
    the continuum interpolation and the global 63 arithmetic. -/
namespace S008.ThreeSlope

open S008.NumericalCutoff S008.WholeProfile

def scale (j : ℕ) := 3*j+Nat.clog 2 (3*j+3)+2

theorem scale_mono (j : ℕ) : scale j ≤ scale (j+1) := by
  have h := Nat.clog_mono_right 2 (show 3*j+3 ≤ 3*(j+1)+3 by omega)
  unfold scale
  omega

private theorem scale_cap (j b : ℕ) (hb : scale j ≤ b) :
    (b+3)*2^(3*j) ≤ 2^b := by
  have hL : Nat.clog 2 (3*j+3) ≤ 3*j+3 := Nat.clog_le_of_le_pow
    (Nat.lt_pow_self (n:=3*j+3) (by norm_num : 1 < 2)).le
  have hP := Nat.le_pow_clog (by norm_num : 1 < 2) (3*j+3)
  have hbase : scale j+3 ≤ 4*2^Nat.clog 2 (3*j+3) := by unfold scale; omega
  induction b, hb using Nat.le_induction with
  | base =>
    calc
      (scale j+3)*2^(3*j) ≤ (4*2^Nat.clog 2 (3*j+3))*2^(3*j) :=
        Nat.mul_le_mul_right _ hbase
      _ = 2^(scale j) := by simp [scale,pow_add]; ring
  | succ b h ih =>
    rw [pow_succ]
    nlinarith only [ih,Nat.mul_le_mul_right (2^(3*j)) (show b+1+3 ≤ 2*(b+3) by omega)]

/-- At the declared real-window switch the integer arity d=2^j is actually legal. -/
theorem legal_degree {u j : ℕ} (hu : scale j*2^(3*j) ≤ u) :
    2^(3*j)*Nat.clog 2 (u+2) ≤ u := by
  let D := 2^(3*j)
  let b := u/D
  have hpos : 0 < D := by dsimp [D]; positivity
  have hb : scale j ≤ b := (Nat.le_div_iff_mul_le hpos).mpr hu
  have hc : (b+3)*D ≤ 2^b := scale_cap j b hb
  have hl : b*D ≤ u := Nat.div_mul_le_self u D
  have hh : u < D*(b+1) := Nat.lt_mul_div_succ u hpos
  have hv : u+2 ≤ 2^b := by nlinarith only [hc,hh,hpos]
  have hclog := Nat.clog_le_of_le_pow hv
  calc
    2^(3*j)*Nat.clog 2 (u+2) ≤ D*b := Nat.mul_le_mul_left D hclog
    _ = b*D := Nat.mul_comm _ _
    _ ≤ u := hl

def height : ℕ → ℚ
  | 0 => 577283/67584
  | i+1 => 20/3 + (scale (5+i):ℚ)/(4*(scale (6+i):ℚ)) * (height i-7/4)

/-- The actual infinite sequence from band j=5 has the declared uniform cap. -/
theorem height_cap (i : ℕ) : height i ≤ 43/5 := by
  induction i with
  | zero => norm_num [height]
  | succ i ih =>
    have hQ : (0:ℚ) < (scale (6+i):ℕ) := by unfold scale; positivity
    have hm : (scale (5+i):ℚ) ≤ (scale (6+i):ℚ) := by
      exact_mod_cast (show scale (5+i) ≤ scale (6+i) by
        simpa only [show 5+i+1=6+i by omega] using scale_mono (5+i))
    let r := (scale (5+i):ℚ)/(4*(scale (6+i):ℚ))
    have hr : 0 ≤ r := by dsimp [r]; positivity
    have hmax : r ≤ 1/4 := by
      dsimp [r]
      rw [div_le_iff₀ (by positivity)]
      linarith only [hm]
    have h1 := mul_le_mul_of_nonneg_left (sub_le_sub_right ih (7/4:ℚ)) hr
    have h2 := mul_le_mul_of_nonneg_right hmax (show (0:ℚ)≤43/5-7/4 by norm_num)
    change 20/3 + r*(height i-7/4) ≤ 43/5
    linarith only [h1,h2]

/-- Cumulative unnormalized native proof charge at the actual start of band 5+i. -/
def fullHeight : ℕ → ℚ
  | 0 => 46182640
  | i+1 => fullHeight i +
      240*((2:ℚ)^(5+i))^2 * ((17/4)*(scale (5+i):ℚ)+
        2*(11/3)*(scale (5+i):ℚ)+(10/3)*(8*(scale (6+i):ℚ)-4*(scale (5+i):ℚ)))

theorem fullHeight_normalized (i : ℕ) :
    fullHeight i = 240*((2:ℚ)^(5+i))^2*(scale (5+i):ℚ)*height i := by
  induction i with
  | zero => decide +kernel
  | succ i ih =>
    have hq : (scale (6+i):ℚ) ≠ 0 := by unfold scale; positivity
    simp only [fullHeight,height,show 5+(i+1)=6+i by omega]
    rw [ih,show (2:ℚ)^(6+i)=2*2^(5+i) by
      rw [show 6+i=5+i+1 by omega,pow_succ,mul_comm]]
    field_simp
    ring

/-- The logarithm at a knot dominates its scale by an exact integer power comparison. -/
theorem scale_power (j a : ℕ) (ha : 1≤a) :
    2^(scale j) ≤ 240*(a*scale j*2^(3*j)+2)+2 := by
  let L := Nat.clog 2 (3*j+3)
  have hp := Nat.le_pow_clog (by norm_num : 1 < 2) (3*j+3)
  have hL : 0<L := by
    by_contra! hh
    have hz : L=0 := by omega
    change 3*j+3 ≤ 2^L at hp
    rw [hz] at hp
    omega
  have hpre := Nat.pow_pred_clog_lt_self (by norm_num : 1 < 2) (show 1 < 3*j+3 by omega)
  change 2^(L-1)<3*j+3 at hpre
  have hpL : 2^L ≤ 2*(3*j+3) := by
    rw [show L=L-1+1 by omega,pow_succ]
    omega
  have he : 2^(scale j) = 2^(3*j)*2^L*4 := by simp [scale,L,pow_add]
  have hQ : 3*j+3 ≤ scale j := by change 3*j+3≤3*j+L+2; omega
  have hc : 2^L*4 ≤ 240*(a*scale j) := by
    have hm := Nat.mul_le_mul_right (scale j) ha
    nlinarith only [hpL,hQ,hm]
  rw [he]
  nlinarith only [Nat.mul_le_mul_right (2^(3*j)) hc]

theorem normalized_cubes :
    240*(43/5:ℚ)^3 < (433/8:ℚ)^3 ∧
    240*(43/5+17/4:ℚ)^3 < (433/8:ℚ)^3*2^2 ∧
    240*(43/5+17/4+2*(11/3):ℚ)^3 < (433/8:ℚ)^3*4^2 := by norm_num

private theorem lower_log {a : ℝ} (p q : ℕ) (_ha : 0 < a)
    (h : (2:ℝ)^p ≤ a^q) : (p:ℝ) ≤ q*logTwo a := by
  have h2 := Real.log_pos (show (1:ℝ)<2 by norm_num)
  have hlog := Real.log_le_log (pow_pos (show (0:ℝ)<2 by norm_num) p) h
  rw [Real.log_pow,Real.log_pow] at hlog
  unfold logTwo
  rw [← mul_div_assoc, le_div_iff₀ h2]
  exact hlog

private theorem upper_log {a : ℝ} (p q : ℕ) (ha : 0 < a)
    (h : a^q ≤ (2:ℝ)^p) : (q:ℝ)*logTwo a ≤ p := by
  have h2 := Real.log_pos (show (1:ℝ)<2 by norm_num)
  have hlog := Real.log_le_log (pow_pos ha q) h
  rw [Real.log_pow,Real.log_pow] at hlog
  unfold logTwo
  rw [← mul_div_assoc, div_le_iff₀ h2]
  exact hlog

private theorem native_gate {v y lower : ℝ} (hy : 0 ≤ y)
    (hl : lower ≤ logTwo (y+2)) (hc : v^3 ≤ (433/8:ℝ)^3*y^2*lower) :
    v ≤ (433/8:ℝ)*phi y := by
  have h := mul_le_mul_of_nonneg_left hl
    (mul_nonneg (by norm_num : (0:ℝ)≤(433/8:ℝ)^3) (sq_nonneg y))
  apply le_of_pow_le_pow_left₀ (by norm_num : (3:ℕ)≠0)
    (mul_nonneg (by norm_num) (S008.Piecewise.phi_nonneg hy))
  rw [mul_pow,phi_cube hy]
  linarith only [hc,h]

/-- A normalized cubic bound transfers to the actual unnormalized real knot. -/
theorem later_knot {D Q a c h y : ℝ} (hD : 0≤D) (hQ : 0≤Q) (ha : 0≤a)
    (hh0 : 0≤h) (hh : h ≤ 240*D^2*Q*c) (hy : 240*a*Q*D^3 ≤ y)
    (hlog : Q ≤ logTwo (y+2)) (hc : 240*c^3 ≤ (433/8:ℝ)^3*a^2) :
    h ≤ (433/8:ℝ)*phi y := by
  have hb : 0≤240*a*Q*D^3 := by positivity
  have h1 := pow_le_pow_left₀ hh0 hh 3
  have h2 := mul_le_mul_of_nonneg_right hc (show 0≤240^2*D^6*Q^3 by positivity)
  have h3 := pow_le_pow_left₀ hb hy 2
  have h4 := mul_le_mul_of_nonneg_right h3
    (show (0:ℝ)≤(433/8:ℝ)^3*Q by positivity)
  apply native_gate (hb.trans hy) hlog
  calc
    h^3 ≤ (240*D^2*Q*c)^3 := h1
    _ = (240*c^3)*(240^2*D^6*Q^3) := by ring
    _ ≤ ((433/8:ℝ)^3*a^2)*(240^2*D^6*Q^3) := h2
    _ = (240*a*Q*D^3)^2*((433/8:ℝ)^3*Q) := by ring
    _ ≤ y^2*((433/8:ℝ)^3*Q) := h4
    _ = (433/8:ℝ)^3*y^2*Q := by ring

inductive Place where
  | first | second | fourth

def Place.factor : Place → ℕ
  | .first => 1 | .second => 2 | .fourth => 4

def Place.extra : Place → ℚ
  | .first => 0 | .second => 17/4 | .fourth => 17/4+2*(11/3)

def knotIndex (j : ℕ) (p : Place) : ℕ := 240*(p.factor*scale j*2^(3*j)+2)

noncomputable def knotHeight (i : ℕ) (p : Place) : ℝ :=
  (fullHeight i : ℝ) + 240*((2:ℝ)^(5+i))^2*(scale (5+i):ℝ)*(p.extra:ℝ)

private theorem height_positive (i : ℕ) : 7/4 ≤ height i := by
  induction i with
  | zero => norm_num [height]
  | succ i ih =>
    change 7/4 ≤ 20/3+(scale (5+i):ℚ)/(4*(scale (6+i):ℚ))*(height i-7/4)
    have h := mul_nonneg (by positivity : (0:ℚ)≤(scale (5+i):ℚ)/(4*(scale (6+i):ℚ)))
      (sub_nonneg.mpr ih)
    linarith only [h]

/-- Every one of the three actual endpoints in every subsequent band is below C_I Φ. -/
theorem all_later_knots (i : ℕ) (p : Place) :
    knotHeight i p ≤ (433/8:ℝ)*phi (knotIndex (5+i) p:ℝ) := by
  let j := 5+i
  let D := (2:ℝ)^j
  let Q := (scale j:ℝ)
  have hD : 0≤D := by dsimp [D]; positivity
  have hQ : 0≤Q := by dsimp [Q]; positivity
  have hp : 1≤p.factor := by cases p <;> decide
  have he : (0:ℝ)≤(p.extra:ℝ) := by cases p <;> norm_num [Place.extra]
  have hscale := scale_power j p.factor hp
  have hxpow : (2:ℝ)^(scale j) ≤ (knotIndex j p:ℝ)+2 := by exact_mod_cast hscale
  have hlog := lower_log (a:=(knotIndex j p:ℝ)+2) (scale j) 1 (by positivity) (by simpa using hxpow)
  norm_num only [Nat.cast_one,one_mul] at hlog
  have hfull : (fullHeight i:ℝ) = 240*D^2*Q*(height i:ℝ) := by
    dsimp [D,Q,j]
    exact_mod_cast fullHeight_normalized i
  have hpos : 0≤(height i:ℝ) := by
    exact_mod_cast (show (0:ℚ)≤height i by linarith [height_positive i])
  have hcap : (height i:ℝ)≤43/5 := by
    have hR : (height i:ℝ) ≤ ((43/5:ℚ):ℝ) := Rat.cast_le.mpr (height_cap i)
    norm_num at hR ⊢
    exact hR
  have hfac : 0≤240*D^2*Q := by positivity
  have hkn : knotHeight i p = 240*D^2*Q*((height i:ℝ)+(p.extra:ℝ)) := by
    unfold knotHeight
    rw [hfull]
    dsimp [D,Q,j]
    ring
  have hk0 : 0≤knotHeight i p := by rw [hkn]; exact mul_nonneg hfac (add_nonneg hpos he)
  have hku : knotHeight i p ≤ 240*D^2*Q*((43/5:ℝ)+(p.extra:ℝ)) := by
    rw [hkn]
    exact mul_le_mul_of_nonneg_left (by linarith only [hcap]) hfac
  have hpow : D^3=(2:ℝ)^(3*j) := by dsimp [D]; rw [← pow_mul, Nat.mul_comm]
  have hy : 240*(p.factor:ℝ)*Q*D^3 ≤ (knotIndex j p:ℝ) := by
    unfold knotIndex
    push_cast
    rw [hpow]
    dsimp [Q]
    nlinarith
  have hc : 240*((43/5:ℝ)+(p.extra:ℝ))^3 ≤ (433/8:ℝ)^3*(p.factor:ℝ)^2 := by
    cases p <;> norm_num [Place.factor,Place.extra]
  exact later_knot hD hQ (by positivity) hk0 hku hy hlog hc

theorem early_endpoints :
    (15728880:ℝ) ≤ (433/8:ℝ)*phi 31457760 ∧
    (16773360:ℝ) ≤ (433/8:ℝ)*phi 35389920 ∧
    (24883440:ℝ) ≤ (433/8:ℝ)*phi 70779360 := by
  refine ⟨native_gate (lower:=124/5) (by norm_num) ?_ (by norm_num),
    native_gate (lower:=25) (by norm_num) ?_ (by norm_num),
    native_gate (lower:=26) (by norm_num) ?_ (by norm_num)⟩
  · have h := lower_log (a:=31457760+2) 124 5 (by norm_num) (by norm_num)
    norm_num at h; linarith
  · have h := lower_log (a:=35389920+2) 25 1 (by norm_num) (by norm_num)
    norm_num at h ⊢; exact h
  · have h := lower_log (a:=70779360+2) 26 1 (by norm_num) (by norm_num)
    norm_num at h ⊢; exact h

/-- Jensen covers each positive-width affine segment from its endpoint checks. -/
theorem interpolate {p q a b ha hb : ℝ} (hp : 0 ≤ p) (hq : 0 ≤ q) (hpq : p+q=1)
    (ha0 : 0<a) (hb0 : 0<b) (h1 : ha ≤ (433/8:ℝ)*phi a)
    (h2 : hb ≤ (433/8:ℝ)*phi b) :
    p*ha+q*hb ≤ (433/8:ℝ)*phi (p*a+q*b) := by
  have h := S008.Piecewise.phi_blend hp hq hpq ha0 hb0
  have hpa := mul_le_mul_of_nonneg_left h1 hp
  have hqb := mul_le_mul_of_nonneg_left h2 hq
  nlinarith only [h,hpa,hqb]

theorem earlier_guard {X Y : ℝ} (hX : 896 ≤ X) (hY : Y ≤ X/64+1) :
    56*Y ≤ (15/16)*X ∧ 56*Y ≤ X-7 := by constructor <;> linarith

private theorem phipos {x : ℝ} (hx : 0 ≤ x) : 0 ≤ phi x := by
  unfold phi logTwo
  apply Real.rpow_nonneg
  exact mul_nonneg (sq_nonneg _) (div_nonneg (Real.log_nonneg (by linarith))
    (Real.log_nonneg (by norm_num)))

private theorem log_lower_nat {x : ℝ} (j : ℕ) (hx : (2:ℝ)^j ≤ x+2) :
    (j:ℝ) ≤ logTwo (x+2) := by
  have h := logTwo_mono (pow_pos (show (0:ℝ)<2 by norm_num) j) hx
  have he := logTwo_two_rpow (j:ℝ)
  rw [Real.rpow_natCast] at he
  rwa [he] at h

private theorem bounded_below (x a m : ℝ) (j : ℕ) (hx : a ≤ x) (ha : 0 ≤ a)
    (hlog : (2:ℝ)^j ≤ x+2) (hnum : m^3 ≤ a^2 * j) : m ≤ phi x := by
  have hy : 0 ≤ x := le_trans ha hx
  have hl := log_lower_nat j hlog
  have hs : a^2 ≤ x^2 := by
    nlinarith [mul_nonneg (sub_nonneg.mpr hx) (by linarith : 0 ≤ x+a)]
  have hj : (0:ℝ) ≤ (j:ℝ) := by positivity
  apply le_of_pow_le_pow_left₀ (by norm_num : (3:ℕ) ≠ 0) (phipos hy)
  rw [phi_cube hy]
  exact hnum.trans (mul_le_mul hs hl hj (sq_nonneg x))

theorem dyadic_middle {x : ℝ} (hx : 5 ≤ x) (hmax : x ≤ 4097) :
    61+(3/2)*x ≤ 63*phi x := by
  by_cases h8 : x ≤ 8
  · have h := bounded_below x 5 3 2 hx (by norm_num) (by linarith) (by norm_num)
    linarith
  by_cases h32 : x ≤ 32
  · have h := bounded_below x 8 5 3 (by linarith) (by norm_num) (by linarith) (by norm_num)
    linarith
  by_cases h64 : x ≤ 64
  · have h := bounded_below x 32 8 5 (by linarith) (by norm_num) (by linarith) (by norm_num)
    linarith
  have hden : x ≤ 512*logTwo (x+2) := by
    by_cases h2 : x ≤ 2048
    · have h := log_lower_nat 6 (by norm_num; linarith : (2:ℝ)^6 ≤ x+2)
      norm_num at h
      linarith only [h,h2]
    · have h := log_lower_nat 11 (by norm_num; linarith : (2:ℝ)^11 ≤ x+2)
      norm_num at h
      linarith only [h,hmax]
  have hs : x/8 ≤ phi x := by
    have hxx : 0 ≤ x := by linarith
    apply le_of_pow_le_pow_left₀ (by norm_num : (3:ℕ) ≠ 0) (phipos hxx)
    rw [phi_cube hxx]
    nlinarith only [mul_le_mul_of_nonneg_left hden (sq_nonneg x)]
  linarith


theorem small_excess {x : ℝ} (hx : 1 ≤ x) : 60 ≤ 63*phi x := by
  have hlog := lower_log (a:=x+2) 1 1 (by linarith) (by norm_num; linarith)
  norm_num at hlog
  have hp : 0 ≤ x := by linarith
  have h : 1 ≤ phi x := by
    apply le_of_pow_le_pow_left₀ (by norm_num : (3:ℕ)≠0) (S008.Piecewise.phi_nonneg hp)
    rw [phi_cube hp]
    nlinarith [mul_nonneg (sq_nonneg x) (sub_nonneg.mpr hlog),sq_nonneg (x-1)]
  linarith

theorem coprime_excess {x : ℝ} (hx : 4096 ≤ x) :
    182+4*logTwo (x+2)+(499/8)*phi (x+2)+1 ≤ 63*phi x := by
  have hp : 0≤x := by linarith
  have hlog := lower_log (a:=x+2) 12 1 (by linarith) (by norm_num; linarith)
  norm_num at hlog
  have htop := upper_log (a:=(4096:ℝ)+2) 97 8 (by norm_num) (by norm_num)
  have hr := log_density (x:=(4096:ℝ)) (y:=x) (by norm_num) hx
  have hfix : 336*logTwo (4096+2) ≤ (4096:ℝ) := by norm_num at htop ⊢; linarith only [htop]
  have hg : 336*logTwo (x+2) ≤ x := by
    nlinarith only [hr,mul_le_mul_of_nonneg_left hfix hp]
  have hs := shifted_phi (show 2≤x by linarith)
  have hx2 : 4096^2 ≤ x^2 := by
    nlinarith only [mul_nonneg (sub_nonneg.mpr hx) (show 0≤x+4096 by linarith)]
  have hbig : 576 ≤ phi x := by
    apply le_of_pow_le_pow_left₀ (by norm_num : (3:ℕ)≠0) (S008.Piecewise.phi_nonneg hp)
    rw [phi_cube hp]
    nlinarith only [hx2,mul_le_mul_of_nonneg_left hlog (sq_nonneg x)]
  have hg2 : (336*logTwo (x+2))^2 ≤ x^2 := by
    nlinarith only [mul_nonneg (sub_nonneg.mpr hg)
      (show 0≤x+336*logTwo (x+2) by linarith)]
  have hb : 48*logTwo (x+2) ≤ phi x := by
    apply le_of_pow_le_pow_left₀ (by norm_num : (3:ℕ)≠0) (S008.Piecewise.phi_nonneg hp)
    rw [phi_cube hp]
    nlinarith only [mul_le_mul_of_nonneg_right hg2 (show 0≤logTwo (x+2) by linarith),
      mul_nonneg (sq_nonneg (logTwo (x+2))) (show 0≤logTwo (x+2) by linarith)]
  linarith only [hs,hbig,hb]

end S008.ThreeSlope
