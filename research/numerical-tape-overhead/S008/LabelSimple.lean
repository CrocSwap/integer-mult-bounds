import S008.PiecewiseDensity

namespace S008.Piecewise.LabelSimple
open S008.NumericalCutoff S008.WholeProfile S008.Piecewise

abbrev a0 : ℝ := 169049912771040
noncomputable abbrev h0 : ℝ := 1752712649713152816/3855005
noncomputable def l0 (w : ℝ) : ℝ := 3719981558627835295593/20231066240+(269/167936)*w
abbrev a1 : ℝ := 338099825541600
noncomputable abbrev h1 : ℝ := 2796587349989684016/3855005
noncomputable def l1 (w : ℝ) : ℝ := 8376764989540855006311/40462132480+(515/335872)*w
abbrev a2 : ℝ := 725677674332640
noncomputable abbrev h2 : ℝ := 208589401498995028656/158055205
noncomputable def l2 (w : ℝ) : ℝ := 13991522341751541275193/20231066240+(39/45056)*w
abbrev a3 : ℝ := 1451355348664800
noncomputable abbrev h3 : ℝ := 307870034702990471856/158055205
noncomputable def l3 (w : ℝ) : ℝ := 3986646779673101455767/5057766560+(9/11264)*w
abbrev a4 : ℝ := 2902710697329120
noncomputable abbrev h4 : ℝ := 491157357541135905456/158055205
noncomputable def l4 (w : ℝ) : ℝ := 35803303791265894152411/40462132480+(69/90112)*w
abbrev a5 : ℝ := 6201245580657120
noncomputable abbrev h5 : ℝ := 890362700843914785456/158055205
noncomputable def l5 (w : ℝ) : ℝ := 2814186109995531152000271/950860113280+(83/192512)*w

noncomputable def upper (w : ℝ) : ℝ := min (l0 w) <| min (l1 w) <| min (l2 w) <| min (l3 w) <| min (l4 w) (l5 w)

private theorem min_density {z t fz ft gz gt : ℝ} (hz : 0≤z)
    (hf : z*ft≤t*fz) (hg : z*gt≤t*gz) : z*min ft gt ≤ t*min fz gz := by
  rcases le_total fz gz with h | h
  · rw [min_eq_left h]
    exact (mul_le_mul_of_nonneg_left (min_le_left _ _) hz).trans hf
  · rw [min_eq_right h]
    exact (mul_le_mul_of_nonneg_left (min_le_right _ _) hz).trans hg

theorem upper_density {z t : ℝ} (hz : 0 ≤ z) (ht : z ≤ t) : z*upper t ≤ t*upper z := by
  unfold upper
  repeat' apply min_density hz
  all_goals dsimp only [l0,l1,l2,l3,l4,l5]; nlinarith only [ht]

theorem ln_floor (x k : ℕ) (h : 2^k ≤ x+2) : (k:ℝ) ≤ logTwo ((x:ℝ)+2) := by
  have hr : (2:ℝ)^k ≤ (x:ℝ)+2 := by exact_mod_cast h
  have hh := logTwo_mono (by positivity) hr
  rw [← Real.rpow_natCast,logTwo_two_rpow] at hh
  exact hh

theorem upper0 (x : ℝ) : upper x ≤ l0 x := by simp [upper,min_le_iff]

theorem upper1 (x : ℝ) : upper x ≤ l1 x := by simp [upper,min_le_iff]

theorem upper2 (x : ℝ) : upper x ≤ l2 x := by simp [upper,min_le_iff]

theorem upper3 (x : ℝ) : upper x ≤ l3 x := by simp [upper,min_le_iff]

theorem upper4 (x : ℝ) : upper x ≤ l4 x := by simp [upper,min_le_iff]

theorem upper5 (x : ℝ) : upper x ≤ l5 x := by simp [upper,min_le_iff]

theorem general_later {z t d L : ℝ} (hz : 2≤z) (ht : z≤t) (hd : 0≤d)
    (hl0 : logTwo (z+2)≤L) (hs : ∀ v, 0≤v → v≤z+2 → upper v-(159/4:ℝ)*phi v≤d)
    (endpoint0 : 183+4*L+d+48*phi (z+2)≤z/1000) (x : ℕ) (hx : (x:ℝ)≤t+2) :
    182+4*logTwo (t+2)+envelope (fun j=>upper (j:ℝ)) x+1 ≤ t/1000 := by
  let B := d+48*phi (z+2)
  have hB0 : 0≤B := add_nonneg hd (mul_nonneg (by norm_num) (phi_nonneg (by linarith)))
  have hb : prefixBound phi upper (z+2) B := by
    refine ⟨by dsimp [B]; linarith only [hd],?_⟩
    intro v hv hvt
    dsimp [B]
    linarith only [hs v hv hvt]
  have hP := shifted_prefix_density phi upper (by linarith : 0<z) ht hB0
    (fun u v hu hv => phi_density (by linarith) hv)
    (fun v hv => upper_density (by linarith) hv) hb
  have hh : history (fun j => upper (j:ℝ)) x ≤ t*B/z-48*phi (t+2) := by
    apply history_upper _ (by linarith only [hP.1])
    intro j hj
    have hr : (j:ℝ) ≤ t+2 := (show (j:ℝ)≤(x:ℝ) by exact_mod_cast hj).trans hx
    linarith only [hP.2 (j:ℝ) (by positivity) hr]
  have hp := phi_mono_nonneg (by positivity : (0:ℝ)≤(x:ℝ)) hx
  have hE : z*envelope (fun j=>upper (j:ℝ)) x ≤ t*B := by
    have hc : envelope (fun j=>upper (j:ℝ)) x ≤ t*B/z := by unfold envelope; linarith only [hh,hp]
    rw [le_div_iff₀ (by linarith : 0<z)] at hc
    linarith only [hc]
  have hl := (log_density hz ht).trans
    (mul_le_mul_of_nonneg_left hl0 (by linarith : 0≤t))
  have hend : 183+4*L+B≤z/1000 := by dsimp [B]; linarith only [endpoint0]
  have hscale := mul_le_mul_of_nonneg_left hend (by linarith : 0≤t)
  by_contra! hn
  nlinarith only [hl,hscale,hE,ht,mul_pos (by linarith : 0<z) (sub_pos.mpr hn)]

private theorem ln_two_lower : (1/2:ℝ) ≤ Real.log 2 := by
  have h := Real.log_le_sub_one_of_pos (show (0:ℝ) < 1/2 by norm_num)
  rw [Real.log_div (by norm_num) (by norm_num), Real.log_one] at h
  linarith

/-- Unit coefficient, natural logarithms, and all later input lengths. The
    caller supplies its actual rounded width and its physical raw time invoice. -/
theorem natural_from {w : ℝ} (hy : ∀ t, w≤t → ∀ x : ℕ, (x:ℝ)≤t+2 →
      182+4*logTwo (t+2)+envelope (fun j=>upper (j:ℝ)) x+1 ≤ t/1000)
    (n cost : ℝ) (a : ℕ) (hn : (2:ℝ)^((2:ℝ)^w) ≤ n)
    (ha : (activeLog a:ℝ) ≤ logTwo (logTwo n)+2)
    (hcost : cost ≤ n*Real.sqrt (logTwo n)*(2:ℝ)^(182+4*logTwo (logTwo (logTwo n)+2)+
        envelope (fun j => upper (j:ℝ)) (activeLog a))) : cost ≤ n*(Real.log n)^(501/1000:ℝ) := by
  have hnpos : 0<n := lt_of_lt_of_le (Real.rpow_pos_of_pos (by norm_num) _) hn
  have hlog := logTwo_mono (Real.rpow_pos_of_pos (show (0:ℝ)<2 by norm_num) _) hn
  rw [logTwo_two_rpow] at hlog
  have hL : 0 < logTwo n := lt_of_lt_of_le (Real.rpow_pos_of_pos (by norm_num) _) hlog
  have hl2 : 0 < Real.log 2 := Real.log_pos (by norm_num)
  have hln : 0 ≤ Real.log n := by
    unfold logTwo at hL
    exact le_of_lt ((div_pos_iff_of_pos_right hl2).mp hL)
  let exponent := 182+4*logTwo (logTwo (logTwo n)+2)+envelope (fun j => upper (j:ℝ)) (activeLog a)
  have hx : exponent+1 ≤ logTwo (logTwo n)/1000 := by
    unfold exponent
    exact hy _ (length_gate n _ hn) (activeLog a) ha
  have hpow := Real.rpow_le_rpow_of_exponent_le (show (1:ℝ) ≤ 2 by norm_num) hx
  rw [Real.rpow_add (by norm_num),Real.rpow_one] at hpow
  have hid : (2:ℝ)^(logTwo (logTwo n)/1000) = (logTwo n)^(1/1000:ℝ) := by
    rw [div_eq_mul_one_div,Real.rpow_mul (by norm_num : (0:ℝ)≤2),two_log_cancel hL]
  rw [hid] at hpow
  change cost ≤ n*Real.sqrt (logTwo n)*(2:ℝ)^exponent at hcost
  have hb : 2*cost ≤ n*(logTwo n)^(501/1000:ℝ) := by
    calc
      2*cost ≤ n*Real.sqrt (logTwo n)*(logTwo n)^(1/1000:ℝ) := by
        nlinarith only [hcost,mul_le_mul_of_nonneg_left hpow
          (mul_nonneg hnpos.le (Real.sqrt_nonneg (logTwo n)))]
      _ = _ := by rw [Real.sqrt_eq_rpow,mul_assoc,← Real.rpow_add hL]; norm_num
  have hupper : logTwo n ≤ 2*Real.log n := by
    unfold logTwo
    rw [div_le_iff₀ hl2]
    nlinarith only [mul_nonneg hln (sub_nonneg.mpr ln_two_lower)]
  have hmono := Real.rpow_le_rpow hL.le hupper (by norm_num : (0:ℝ) ≤ 501/1000)
  rw [Real.mul_rpow (by norm_num) hln] at hmono
  have hfactor := Real.rpow_le_rpow_of_exponent_le (show (1:ℝ) ≤ 2 by norm_num)
    (show (501/1000:ℝ) ≤ 1 by norm_num)
  rw [Real.rpow_one] at hfactor
  have hh := mul_le_mul_of_nonneg_right hfactor (Real.rpow_nonneg hln (501/1000:ℝ))
  nlinarith only [hb,mul_le_mul_of_nonneg_left (hmono.trans hh) hnpos.le]


end S008.Piecewise.LabelSimple
