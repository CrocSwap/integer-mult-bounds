import S008.Piecewise

/-! The continuous numerical native profile: actual-slot domination, concavity
    of Φ, and reduction of the entire prefix to two endpoint envelopes. -/
namespace S008.Piecewise

open S008.NumericalCutoff

theorem phi_nonneg {x : ℝ} (hx : 0 ≤ x) : 0 ≤ phi x := by
  unfold phi logTwo
  exact Real.rpow_nonneg (mul_nonneg (sq_nonneg _)
    (div_nonneg (Real.log_nonneg (by linarith)) (Real.log_nonneg (by norm_num)))) _

theorem phi_mono_nonneg {v x : ℝ} (hv : 0 ≤ v) (hx : v ≤ x) : phi v ≤ phi x := by
  have hvlog : 0 ≤ logTwo (v+2) := by
    unfold logTwo
    exact div_nonneg (Real.log_nonneg (by linarith)) (Real.log_nonneg (by norm_num))
  apply le_of_pow_le_pow_left₀ (by norm_num : (3:ℕ) ≠ 0) (phi_nonneg (hv.trans hx))
  rw [phi_cube hv, phi_cube (hv.trans hx)]
  have hs : v^2 ≤ x^2 := by
    nlinarith only [mul_nonneg (sub_nonneg.mpr hx) (show 0 ≤ x+v by linarith)]
  exact mul_le_mul hs (logTwo_mono (by linarith) (by linarith)) hvlog (sq_nonneg x)

theorem rounded_log {f : ℕ} : logTwo ((f:ℝ)+2) ≤ (activeLog f:ℝ) := by
  have hi : (f:ℝ)+2 ≤ (2:ℝ)^(activeLog f) := by
    exact_mod_cast Nat.le_pow_clog (by norm_num : 1 < 2) (f+2)
  have h := logTwo_mono (by positivity) hi
  rw [← Real.rpow_natCast, logTwo_two_rpow] at h
  exact h

/-- The literal native width f can be passed to a monotone real shape before
    the rounded parent exponent is applied. -/
theorem native_slot_covered (H : ℝ → ℝ) (hH : Monotone H) {f a : ℕ} (hf : f ≤ a) :
    H (logTwo ((f:ℝ)+2))+(33/4:ℝ)*phi (activeLog a:ℝ) ≤
      envelope (fun j => H (j:ℝ)) (activeLog a) := by
  have hlog := activeLog_mono hf
  have hφ := phi_mono_nonneg (by positivity : (0:ℝ)≤(activeLog f:ℝ))
    (show (activeLog f:ℝ) ≤ (activeLog a:ℝ) by exact_mod_cast hlog)
  have h := covers_earlier (fun j => H (j:ℝ)) hlog hφ
  linarith only [h,hH (rounded_log (f:=f))]

private theorem blend_pos {p q x y : ℝ} (hp : 0 ≤ p) (hq : 0 ≤ q)
    (hpq : p+q=1) (hx : 0 < x) (hy : 0 < y) : 0 < p*x+q*y := by
  rcases eq_or_lt_of_le hp with h | h
  · have hq1 : q=1 := by linarith
    simpa [← h,hq1] using hy
  · exact add_pos_of_pos_of_nonneg (mul_pos h hx) (mul_nonneg hq hy.le)

private theorem log_blend {p q x y : ℝ} (hp : 0 ≤ p) (hq : 0 ≤ q)
    (hpq : p+q=1) (hx : 0 < x) (hy : 0 < y) :
    p*Real.log x+q*Real.log y ≤ Real.log (p*x+q*y) := by
  set m := p*x+q*y with hm
  have hm0 : 0 < m := blend_pos hp hq hpq hx hy
  have h₁ := Real.log_le_sub_one_of_pos (div_pos hx hm0)
  have h₂ := Real.log_le_sub_one_of_pos (div_pos hy hm0)
  rw [Real.log_div hx.ne' hm0.ne'] at h₁
  rw [Real.log_div hy.ne' hm0.ne'] at h₂
  have hs := add_le_add (mul_le_mul_of_nonneg_left h₁ hp) (mul_le_mul_of_nonneg_left h₂ hq)
  have hr : p*(x/m-1)+q*(y/m-1)=0 := by
    calc
      _ = (p*x+q*y)/m-(p+q) := by ring
      _ = 0 := by rw [← hm,hpq,div_self hm0.ne']; ring
  have hl : p*(Real.log x-Real.log m)+q*(Real.log y-Real.log m) =
      p*Real.log x+q*Real.log y-Real.log m := by
    calc
      _ = p*Real.log x+q*Real.log y-(p+q)*Real.log m := by ring
      _ = _ := by rw [hpq,one_mul]
  linarith only [hs,hr,hl]

private theorem shifted_log_blend {p q x y : ℝ} (hp : 0 ≤ p) (hq : 0 ≤ q)
    (hpq : p+q=1) (hx : 0 < x) (hy : 0 < y) :
    p*logTwo (x+2)+q*logTwo (y+2) ≤ logTwo (p*x+q*y+2) := by
  have h := log_blend hp hq hpq (by linarith : 0 < x+2) (by linarith : 0 < y+2)
  have harg : p*(x+2)+q*(y+2)=p*x+q*y+2 := by nlinarith only [hpq]
  rw [harg] at h
  unfold logTwo
  rw [← mul_div_assoc,← mul_div_assoc,← add_div]
  exact div_le_div_of_nonneg_right h (Real.log_nonneg (by norm_num))

private theorem cube_blend {A B u v : ℝ} (hA : 0 ≤ A) (hB : 0 ≤ B)
    (hu : 0 ≤ u) (hv : 0 ≤ v) : (A*u+B*v)^3 ≤ (A+B)^2*(A*u^3+B*v^3) := by
  have h := mul_nonneg (mul_nonneg (mul_nonneg hA hB) (sq_nonneg (u-v)))
    (add_nonneg (mul_nonneg hA (by linarith : 0 ≤ 2*u+v))
       (mul_nonneg hB (by linarith : 0 ≤ u+2*v)))
  nlinarith only [h]

/-- Direct Jensen proof for the real function actually used in the clock.
    We use the cube identity and the supporting tangent of log. -/
theorem phi_blend {p q x y : ℝ} (hp : 0 ≤ p) (hq : 0 ≤ q)
    (hpq : p+q=1) (hx : 0 < x) (hy : 0 < y) :
    p*phi x+q*phi y ≤ phi (p*x+q*y) := by
  have hm := blend_pos hp hq hpq hx hy
  have hl := shifted_log_blend hp hq hpq hx hy
  have h₁ : x*(phi x/x)^3=logTwo (x+2) := by
    rw [div_pow, phi_cube hx.le]
    field_simp
  have h₂ : y*(phi y/y)^3=logTwo (y+2) := by
    rw [div_pow, phi_cube hy.le]
    field_simp
  have h₃ : p*x*(phi x/x) = p*phi x := by field_simp
  have h₄ : q*y*(phi y/y) = q*phi y := by field_simp
  have hbl := cube_blend (mul_nonneg hp hx.le) (mul_nonneg hq hy.le)
    (div_nonneg (phi_nonneg hx.le) hx.le) (div_nonneg (phi_nonneg hy.le) hy.le)
  rw [h₃,h₄,mul_assoc p x _,h₁,mul_assoc q y _,h₂] at hbl
  apply le_of_pow_le_pow_left₀ (by norm_num : (3:ℕ) ≠ 0) (phi_nonneg hm.le)
  rw [phi_cube hm.le]
  exact hbl.trans (mul_le_mul_of_nonneg_left hl (sq_nonneg _))

/-- A linear function minus a nonnegative multiple of the concave clock
    lies below a common endpoint bound throughout the intervening interval. -/
theorem affine_surplus {a b x u v D : ℝ} (ha : 0 < a) (hax : a ≤ x) (hxb : x ≤ b)
    (hl : u+v*a-(159/4:ℝ)*phi a ≤ D) (hr : u+v*b-(159/4:ℝ)*phi b ≤ D) :
    u+v*x-(159/4:ℝ)*phi x ≤ D := by
  by_cases hab : a=b
  · have he : x=a := le_antisymm (hxb.trans_eq hab.symm) hax
    rwa [he]
  have hba : 0 < b-a := by
    exact sub_pos.mpr (lt_of_le_of_ne (hax.trans hxb) hab)
  let p := (b-x)/(b-a)
  let q := (x-a)/(b-a)
  have hp : 0 ≤ p := div_nonneg (sub_nonneg.mpr hxb) hba.le
  have hq : 0 ≤ q := div_nonneg (sub_nonneg.mpr hax) hba.le
  have hpq : p+q=1 := by dsimp [p,q]; field_simp; ring
  have heq : p*a+q*b=x := by dsimp [p,q]; field_simp; ring
  have hφ := phi_blend hp hq hpq ha (ha.trans_le (hax.trans hxb))
  rw [heq] at hφ
  have hs := add_le_add (mul_le_mul_of_nonneg_left hl hp) (mul_le_mul_of_nonneg_left hr hq)
  have hid : p*(u+v*a-(159/4:ℝ)*phi a)+q*(u+v*b-(159/4:ℝ)*phi b) =
      u+v*x-(159/4:ℝ)*(p*phi a+q*phi b) := by
    calc
      _ = (p+q)*u+v*(p*a+q*b)-(159/4:ℝ)*(p*phi a+q*phi b) := by ring
      _ = _ := by rw [hpq,heq,one_mul]
  have hD : p*D+q*D=D := by rw [← add_mul,hpq,one_mul]
  linarith only [hφ,hs,hid,hD]

/-- The increasing eleven-facet R=240 native potential, represented by its
    supporting affine functions. All slopes and intercepts are exact. -/

private theorem arity_power {m Y : ℝ} (hm : 0 < m) (hY : logTwo m ≤ Y) (r : ℕ) :
    m^r ≤ (2:ℝ)^((r:ℝ)*Y) := by
  calc
    m^r = ((2:ℝ)^logTwo m)^r := by rw [two_log_cancel hm]
    _ = (2:ℝ)^(logTwo m*(r:ℝ)) := by rw [← Real.rpow_natCast,← Real.rpow_mul (by norm_num)]
    _ ≤ _ := Real.rpow_le_rpow_of_exponent_le (by norm_num)
      (by rw [mul_comm]; exact mul_le_mul_of_nonneg_left hY (by positivity))

/-- Exactly the square-root saving on the executed two-slot mutation f,
    followed by the genuine m^8 Walsh movement transfer. -/
theorem typed_data_gain (native : ℝ → ℝ) (native_mono : Monotone native) (m f a : ℕ) (hm : 0 < m) (hf : f ≤ a)
    (hfslot : 2*(m:ℝ)*(f:ℝ) ≤ (a:ℝ))
    (hy : logTwo ((m:ℝ)+1) ≤ (33/32:ℝ)*phi (activeLog a:ℝ)) :
    (m:ℝ)^(17/2:ℝ)*Real.sqrt (f:ℝ)*(2:ℝ)^(native (logTwo ((f:ℝ)+2))) ≤
      Real.sqrt (a:ℝ)*(2:ℝ)^(envelope (fun j => native (j:ℝ)) (activeLog a)) := by
  have hm0 : (0:ℝ) < (m:ℝ) := by exact_mod_cast hm
  have hf0 : (0:ℝ) ≤ (f:ℝ) := by positivity
  have hmf : (m:ℝ)*(f:ℝ) ≤ (a:ℝ) := by nlinarith only [hfslot,mul_nonneg hm0.le hf0]
  have hroot : Real.sqrt (m:ℝ)*Real.sqrt (f:ℝ) ≤ Real.sqrt (a:ℝ) := by
    rw [← Real.sqrt_mul hm0.le]
    exact Real.sqrt_le_sqrt hmf
  have hlog := (logTwo_mono hm0 (show (m:ℝ)≤(m:ℝ)+1 by linarith)).trans hy
  have hp := arity_power hm0 hlog 8
  norm_num at hp
  have he := native_slot_covered native native_mono hf
  have hi : (m:ℝ)^8*(2:ℝ)^(native (logTwo ((f:ℝ)+2))) ≤
      (2:ℝ)^(envelope (fun j => native (j:ℝ)) (activeLog a)) := by
    calc
      _ ≤ (2:ℝ)^((33/4:ℝ)*phi (activeLog a:ℝ))*(2:ℝ)^(native (logTwo ((f:ℝ)+2))) := by
        apply mul_le_mul_of_nonneg_right _ (Real.rpow_nonneg (by norm_num) _)
        convert hp using 2; ring
      _ = (2:ℝ)^(native (logTwo ((f:ℝ)+2))+(33/4:ℝ)*phi (activeLog a:ℝ)) := by
        rw [Real.rpow_add (by norm_num)]
        exact mul_comm _ _
      _ ≤ _ := Real.rpow_le_rpow_of_exponent_le (by norm_num) he
  have hmexp : (m:ℝ)^(17/2:ℝ) = (m:ℝ)^8*Real.sqrt (m:ℝ) := by
    rw [show (17/2:ℝ) = (8:ℕ)+(1/2:ℝ) by norm_num,Real.rpow_add hm0,
      Real.rpow_natCast,Real.sqrt_eq_rpow]
  rw [hmexp]
  calc
    _ = (Real.sqrt (m:ℝ)*Real.sqrt (f:ℝ))*((m:ℝ)^8*(2:ℝ)^(native (logTwo ((f:ℝ)+2)))) := by ring
    _ ≤ Real.sqrt (a:ℝ)*((m:ℝ)^8*(2:ℝ)^(native (logTwo ((f:ℝ)+2)))) :=
      mul_le_mul_of_nonneg_right hroot (mul_nonneg (by positivity) (Real.rpow_nonneg (by norm_num) _))
    _ ≤ _ := mul_le_mul_of_nonneg_left hi (Real.sqrt_nonneg _)

/-- The separate ordinary m^45 invoice uses the 48Φ portion at this parent. -/
theorem ordinary_45_gain (native : ℝ → ℝ) (m a : ℕ) (hm : 0 < m)
    (hy : logTwo ((m:ℝ)+1) ≤ (33/32:ℝ)*phi (activeLog a:ℝ)) :
    (m:ℝ)^45 ≤ (2:ℝ)^(envelope (fun j => native (j:ℝ)) (activeLog a)) := by
  have hm0 : (0:ℝ) < (m:ℝ) := by exact_mod_cast hm
  have hlog := (logTwo_mono hm0 (show (m:ℝ)≤(m:ℝ)+1 by linarith)).trans hy
  apply le_trans (arity_power hm0 hlog 45)
  apply Real.rpow_le_rpow_of_exponent_le (by norm_num)
  unfold envelope
  have hφ := phi_nonneg (by positivity : (0:ℝ) ≤ (activeLog a:ℝ))
  have hh := history_nonneg (fun j => native (j:ℝ)) (activeLog a)
  norm_num
  linarith

end S008.Piecewise
