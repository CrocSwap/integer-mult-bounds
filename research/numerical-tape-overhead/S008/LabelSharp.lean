import S008.LabelSimple
import S008.RecountTrueLabel

namespace S008.Piecewise.LabelSharp
open S008.NumericalCutoff S008.Piecewise
open S008.Piecewise.LabelSimple (upper upper0 upper1 upper2 upper3 upper4 upper5
  a0 a1 a2 a3 a4 a5 h0 h1 h2 h3 h4 h5 ln_floor general_later natural_from)
open S008.Recount.TrueLabel (Z B peak)

noncomputable def hot : ℝ := peak-(159/4)*phi (B:ℝ)
abbrev coarse : ℝ := 580000000000
abbrev a6 : ℝ := 7519517465920990
noncomputable abbrev h6 : ℝ := 94349681054883235844501761/15213761812480

private theorem hot_lower : coarse≤hot := by
  have hb : (B:ℝ)+2 ≤ (2:ℝ)^(53:ℕ) := by norm_num [B]
  have hl := logTwo_mono (by norm_num [B] : 0<(B:ℝ)+2) hb
  rw [←Real.rpow_natCast,logTwo_two_rpow] at hl
  have hp : phi (B:ℝ) ≤ 127000000000 := by
    apply le_of_pow_le_pow_left₀ (by decide : (3:ℕ)≠0) (by norm_num)
    rw [phi_cube (by positivity)]
    norm_num [B] at hl ⊢
    linarith only [hl]
  unfold hot
  norm_num [coarse,peak,B] at hp ⊢
  linarith only [hp]

private theorem guarded_corner {x v l : ℝ} (hx:0≤x) (hl:l≤logTwo (x+2))
    (hc:(4*(v-coarse))^3≤159^3*x^2*l) : v-(159/4:ℝ)*phi x ≤ hot := by
  apply le_trans _ hot_lower
  suffices 4*(v-coarse) ≤ 159*phi x by linarith
  apply le_of_pow_le_pow_left₀ (by decide : (3:ℕ)≠0)
    (mul_nonneg (by norm_num) (phi_nonneg hx))
  rw [show (159*phi x)^3=159^3*(phi x)^3 by ring,phi_cube hx]
  nlinarith only [hc,mul_nonneg (sq_nonneg x) (sub_nonneg.mpr hl)]

private theorem knot0 : h0-(159/4:ℝ)*phi a0 ≤ hot :=
  guarded_corner (by norm_num [a0]) (ln_floor 169049912771040 47 (by decide +kernel)) (by norm_num [a0,h0,coarse])

private theorem knot1 : h1-(159/4:ℝ)*phi a1 ≤ hot :=
  guarded_corner (by norm_num [a1]) (ln_floor 338099825541600 48 (by decide +kernel)) (by norm_num [a1,h1,coarse])

private theorem knot2 : h2-(159/4:ℝ)*phi a2 ≤ hot :=
  guarded_corner (by norm_num [a2]) (ln_floor 725677674332640 49 (by decide +kernel)) (by norm_num [a2,h2,coarse])

private theorem knot3 : h3-(159/4:ℝ)*phi a3 ≤ hot :=
  guarded_corner (by norm_num [a3]) (ln_floor 1451355348664800 50 (by decide +kernel)) (by norm_num [a3,h3,coarse])

private theorem knot4 : h4-(159/4:ℝ)*phi a4 ≤ hot :=
  guarded_corner (by norm_num [a4]) (ln_floor 2902710697329120 51 (by decide +kernel)) (by norm_num [a4,h4,coarse])

private theorem knot5 : h5-(159/4:ℝ)*phi a5 ≤ hot := by
  unfold hot
  norm_num [h5,a5,B,peak]

private theorem knot6 : h6-(159/4:ℝ)*phi a6 ≤ hot :=
  guarded_corner (by norm_num [a6]) (ln_floor 7519517465920990 52 (by decide +kernel)) (by norm_num [a6,h6,coarse])

private theorem surplus_at (v : ℝ) (hv : 0≤v) (hvt : v≤(Z:ℝ)+2) :
    upper v-(159/4:ℝ)*phi v ≤ hot := by
  by_cases hA : v≤a0
  · have h₀ := upper0 v
    have hp := phi_nonneg hv
    unfold S008.Piecewise.LabelSimple.l0 at h₀
    unfold a0 at hA
    apply le_trans _ hot_lower
    unfold coarse
    linarith only [h₀,hp,hA]
  by_cases h_1 : v≤a1
  · have h := affine_surplus (by norm_num [a0] : 0<a0) (le_of_not_ge hA) h_1 (u:=3719981558627835295593/20231066240) (v:=269/167936)
      (by have c := knot0; norm_num [a0,h0] at c ⊢; exact c)
      (by have c := knot1; norm_num [a1,h1] at c ⊢; exact c)
    exact (sub_le_sub_right (upper0 v) _).trans h
  by_cases h_2 : v≤a2
  · have h := affine_surplus (by norm_num [a1] : 0<a1) (le_of_not_ge h_1) h_2 (u:=8376764989540855006311/40462132480) (v:=515/335872)
      (by have c := knot1; norm_num [a1,h1] at c ⊢; exact c)
      (by have c := knot2; norm_num [a2,h2] at c ⊢; exact c)
    exact (sub_le_sub_right (upper1 v) _).trans h
  by_cases h_3 : v≤a3
  · have h := affine_surplus (by norm_num [a2] : 0<a2) (le_of_not_ge h_2) h_3 (u:=13991522341751541275193/20231066240) (v:=39/45056)
      (by have c := knot2; norm_num [a2,h2] at c ⊢; exact c)
      (by have c := knot3; norm_num [a3,h3] at c ⊢; exact c)
    exact (sub_le_sub_right (upper2 v) _).trans h
  by_cases h_4 : v≤a4
  · have h := affine_surplus (by norm_num [a3] : 0<a3) (le_of_not_ge h_3) h_4 (u:=3986646779673101455767/5057766560) (v:=9/11264)
      (by have c := knot3; norm_num [a3,h3] at c ⊢; exact c)
      (by have c := knot4; norm_num [a4,h4] at c ⊢; exact c)
    exact (sub_le_sub_right (upper3 v) _).trans h
  by_cases h_5 : v≤a5
  · have h := affine_surplus (by norm_num [a4] : 0<a4) (le_of_not_ge h_4) h_5 (u:=35803303791265894152411/40462132480) (v:=69/90112)
      (by have c := knot4; norm_num [a4,h4] at c ⊢; exact c)
      (by have c := knot5; norm_num [a5,h5] at c ⊢; exact c)
    exact (sub_le_sub_right (upper4 v) _).trans h
  have h := affine_surplus (by norm_num [a5] : 0<a5) (le_of_not_ge h_5) (show v≤a6 by norm_num [Z,a6] at hvt ⊢; exact hvt) (u:=2814186109995531152000271/950860113280) (v:=83/192512)
    (by have c := knot5; norm_num [a5,h5] at c ⊢; exact c)
    (by have c := knot6; norm_num [a6,h6] at c ⊢; exact c)
  exact (sub_le_sub_right (upper5 v) _).trans h

/-- The old native corner supplies the maximum even after passing to the
    continuous upper profile. All future widths are covered by density. -/
theorem all_later {t : ℝ} (ht : (Z:ℝ)≤t) (x : ℕ) (hx : (x:ℝ)≤t+2) :
    182+4*logTwo (t+2)+envelope (fun j=>upper (j:ℝ)) x+1 ≤ t/1000 := by
  have he := S008.Recount.TrueLabel.passing
  unfold S008.Recount.TrueLabel.invoice at he
  have hc : 0 ≤ hot := (by norm_num [coarse] : 0≤coarse).trans hot_lower
  apply general_later (L:=logTwo ((Z:ℝ)+2)) (by norm_num [Z]) ht hc (le_refl _) surplus_at _ x hx
  unfold hot
  linarith only [he]

theorem natural_clock (n cost : ℝ) (a : ℕ)
    (hn : (2:ℝ)^((2:ℝ)^(7519517465920988:ℝ)) ≤ n)
    (ha : (activeLog a:ℝ) ≤ logTwo (logTwo n)+2)
    (hcost : cost ≤ n*Real.sqrt (logTwo n)*(2:ℝ)^(182+4*logTwo (logTwo (logTwo n)+2)+
        envelope (fun j => upper (j:ℝ)) (activeLog a))) : cost ≤ n*(Real.log n)^(501/1000:ℝ) := by
  apply natural_from (w:=(Z:ℝ)) (fun _ ht x hx => all_later ht x hx) n cost a _ ha hcost
  convert hn using 3; norm_num [Z]

end S008.Piecewise.LabelSharp
