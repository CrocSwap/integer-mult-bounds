import Mathlib.Analysis.Complex.ExponentialBounds
import Mathlib.Tactic
set_option autoImplicit false
namespace MultitapeToolkit.ReplicaTailGain

lemma rpow_one_sub (r t : ℝ) (hr : 0 < r) :
    r ^ (1-t) = r * Real.exp (-t * Real.log r) := by
  rw [Real.rpow_def_of_pos hr]
  rw [show Real.log r * (1-t) = Real.log r + (-t * Real.log r) by ring,
    Real.exp_add,Real.exp_log hr]

lemma rpow_one_sub_lower (r t : ℝ) (hr : 0 < r) :
    r * (1-t*Real.log r) ≤ r ^ (1-t) := by
  rw [rpow_one_sub r t hr]
  apply mul_le_mul_of_nonneg_left _ hr.le
  linarith [Real.add_one_le_exp (-t*Real.log r)]

lemma rpow_one_sub_upper (r t : ℝ) (hr : 0 < r)
    (ht : 0 ≤ t) (htop : t ≤ 1/100) (hl : 0 ≤ Real.log r) (hu : Real.log r ≤ 4) :
    r ^ (1-t) ≤ r*(1-t*Real.log r+t^2*(Real.log r)^2) := by
  rw [rpow_one_sub r t hr]
  apply mul_le_mul_of_nonneg_left _ hr.le
  have hx : |-t*Real.log r| ≤ 1 := by
    rw [abs_of_nonpos (by nlinarith : -t*Real.log r ≤ 0)]
    nlinarith
  have h := (abs_le.mp (Real.abs_exp_sub_one_sub_id_le hx)).2
  nlinarith

lemma log_32 : Real.log 32 = 5*Real.log 2 := by
  rw [show (32:ℝ) = 2^5 by norm_num,Real.log_pow]
  norm_num

lemma log_48 : Real.log 48 = 4*Real.log 2+Real.log 3 := by
  rw [show (48:ℝ) = 2^4*3 by norm_num,
    Real.log_mul (by norm_num : (2:ℝ)^4 ≠ 0) (by norm_num : (3:ℝ) ≠ 0),Real.log_pow]
  norm_num

/-- Strictly positive paid cost of the single residue tail in the actual
74-replica allocation, throughout the exponent interval used by the frontier.
This proves a power-cost fact; physical realization of a new allocation remains
an independent literal certificate obligation. -/
theorem tail_power_positive (p : ℝ) (hp : 99/100 ≤ p) (hp1 : p < 1) :
    0 < 3*(3:ℝ)^p - 5*(5:ℝ)^p + 5*(32:ℝ)^p - 3*(48:ℝ)^p := by
  let t := 1-p
  have ht : 0 < t := by dsimp [t]; linarith
  have htt : t ≤ 1/100 := by dsimp [t]; linarith
  have hpt : p=1-t := by dsimp [t]; ring
  have l2 : Real.log 2 ≤ 7/10 := by linarith [Real.log_two_lt_d9]
  have l3 : 109/100 ≤ Real.log 3 := by linarith [Real.log_three_gt_d9]
  have l3u : Real.log 3 ≤ 11/10 := by linarith [Real.log_three_lt_d9]
  have l5 : 8/5 ≤ Real.log 5 := by linarith [Real.log_five_gt_d9]
  have l5u : Real.log 5 ≤ 2 := by linarith [Real.log_five_lt_d9]
  have l5z : 0 ≤ Real.log 5 := Real.log_nonneg (by norm_num)
  have l48z : 0 ≤ Real.log 48 := Real.log_nonneg (by norm_num)
  have l48u : Real.log 48 ≤ 4 := by rw [log_48]; linarith
  have h3 := rpow_one_sub_lower 3 t (by norm_num)
  have h32 := rpow_one_sub_lower 32 t (by norm_num)
  have h5 := rpow_one_sub_upper 5 t (by norm_num) ht.le htt l5z (by linarith)
  have h48 := rpow_one_sub_upper 48 t (by norm_num) ht.le htt l48z l48u
  rw [←hpt] at h3 h32 h5 h48
  have s5 : (Real.log 5)^2 ≤ 4 := by nlinarith
  have s48 : (Real.log 48)^2 ≤ 16 := by nlinarith
  have e5 : t^2*(Real.log 5)^2 ≤ 4*t^2 := by nlinarith [mul_le_mul_of_nonneg_left s5 (sq_nonneg t)]
  have e48 : t^2*(Real.log 48)^2 ≤ 16*t^2 := by nlinarith [mul_le_mul_of_nonneg_left s48 (sq_nonneg t)]
  have ha : 30 ≤ 25*Real.log 5+144*Real.log 48-9*Real.log 3-160*Real.log 32 := by
    rw [log_48,log_32]
    linarith
  have hat := mul_nonneg ht.le (sub_nonneg.mpr ha)
  have hpos : 0 < 30*t-2404*t^2 := by
    nlinarith [mul_nonneg ht.le (sub_nonneg.mpr htt)]
  nlinarith


/-- Full paid child sum in the actual 74-replica predecessor. -/
noncomputable def predecessorPower (p : ℝ) : ℝ :=
  1591740 + 430902*(2:ℝ)^p + 204396*(3:ℝ)^p + 79920*(4:ℝ)^p +
  22532*(5:ℝ)^p + 5328*(8:ℝ)^p + (32:ℝ)^p + 26558*(48:ℝ)^p

/-- Proposed complete periodic profile, for ten replicas. Physical ownership
is checked independently; this definition does not assume its realizability. -/
noncomputable def tenReplicaPower (p : ℝ) : ℝ :=
  215100 + 58230*(2:ℝ)^p + 27621*(3:ℝ)^p + 10800*(4:ℝ)^p +
  3045*(5:ℝ)^p + 720*(8:ℝ)^p + 3589*(48:ℝ)^p

/-- Exact amortized invoice difference, including the predecessor's rank32 tail. -/
theorem profile_difference (p : ℝ) :
    predecessorPower p / 74 - tenReplicaPower p / 10 =
      (3*(3:ℝ)^p-5*(5:ℝ)^p+5*(32:ℝ)^p-3*(48:ℝ)^p) / 370 := by
  unfold predecessorPower tenReplicaPower
  ring

/-- The entire periodic paid profile strictly improves the normalized native
moment throughout the frontier exponent interval, for every positive number
of ten-replica blocks. No hosting or all-size implication is asserted here. -/
theorem periodic_moment_strict (p : ℝ) (hp : 99/100 ≤ p) (hp1 : p < 1)
    (k : ℕ) (hk : 0 < k) :
    ((k:ℝ)*tenReplicaPower p) / ((8960*(k:ℝ))*(73:ℝ)^p) <
      predecessorPower p / (66304*(73:ℝ)^p) := by
  have hkR : (0:ℝ)<k := by exact_mod_cast hk
  have h73 : (0:ℝ)<(73:ℝ)^p := Real.rpow_pos_of_pos (by norm_num) p
  have hunit : tenReplicaPower p / 10 < predecessorPower p / 74 := by
    have h := div_pos (tail_power_positive p hp hp1) (by norm_num : (0:ℝ)<370)
    rw [←profile_difference p] at h
    linarith
  have hdiv := (div_lt_div_iff_of_pos_right (show 0 < 896*(73:ℝ)^p by positivity)).mpr hunit
  have hleft : ((k:ℝ)*tenReplicaPower p) / ((8960*(k:ℝ))*(73:ℝ)^p) =
      (tenReplicaPower p / 10) / (896*(73:ℝ)^p) := by
    field_simp
    ring
  have hright : predecessorPower p / (66304*(73:ℝ)^p) =
      (predecessorPower p / 74) / (896*(73:ℝ)^p) := by
    ring
  rw [hleft,hright]
  exact hdiv

/-- The periodic count vector conserves the exact source-bound deficit. -/
theorem periodic_rank_mass (k : ℕ) :
    k*(215100+2*58230+3*27621+4*10800+5*3045+8*720+48*3589) + 3200*k =
      73*(8960*k) := by omega


/-- The exact positive finite residue charge, rather than a free leftover. -/
noncomputable def residuePower (p : ℝ) : ℝ :=
  (3*(3:ℝ)^p-5*(5:ℝ)^p+5*(32:ℝ)^p-3*(48:ℝ)^p)/5

/-- A scaled periodic profile retaining the very same finite charged residue. -/
noncomputable def replicaPower (T p : ℝ) : ℝ :=
  (T/10)*tenReplicaPower p + residuePower p

lemma predecessor_residue (p : ℝ) : replicaPower 74 p=predecessorPower p := by
  unfold replicaPower residuePower tenReplicaPower predecessorPower
  ring

/-- Increasing the number of replicas strictly improves the actual normalized
paid sum when the same residue charge is retained. Literal realizability of
that count vector must be independently checked for the chosen replica count. -/
theorem retained_tail_dilution (T p : ℝ) (hT : 74<T)
    (hp : 99/100 ≤ p) (hp1 : p<1) :
    replicaPower T p / (896*T*(73:ℝ)^p) <
      predecessorPower p / (66304*(73:ℝ)^p) := by
  have ht : 0<T := by linarith
  have hr : (0:ℝ)<(73:ℝ)^p := Real.rpow_pos_of_pos (by norm_num) p
  have hc : 0<residuePower p := div_pos (tail_power_positive p hp hp1) (by norm_num)
  have hsmall : 0<896*74*(73:ℝ)^p := by positivity
  have hden : 896*74*(73:ℝ)^p < 896*T*(73:ℝ)^p := by nlinarith
  have hd := div_lt_div_of_pos_left hc hsmall hden
  have hnew : replicaPower T p / (896*T*(73:ℝ)^p) =
      tenReplicaPower p/(8960*(73:ℝ)^p) + residuePower p/(896*T*(73:ℝ)^p) := by
    unfold replicaPower
    field_simp
    ring
  have hold : predecessorPower p / (66304*(73:ℝ)^p) =
      tenReplicaPower p/(8960*(73:ℝ)^p) + residuePower p/(896*74*(73:ℝ)^p) := by
    rw [←predecessor_residue p]
    unfold replicaPower
    field_simp
    ring
  rw [hnew,hold]
  linarith

/-- Complete periodic paid sum for the independently published PR2802 profile.
Seven width-five retired-lender helper deletions contribute seven paid rank-five
remainders per call. Literal owner realization remains independently checked. -/
noncomputable def frontierTenReplicaPower (p : ℝ) : ℝ :=
  216720 + 58320*(2:ℝ)^p + 25011*(3:ℝ)^p + 11520*(4:ℝ)^p +
  3675*(5:ℝ)^p + 720*(8:ℝ)^p + 3589*(48:ℝ)^p

/-- Complete actual 74-replica profile claimed by PR2802. -/
noncomputable def frontierPredecessorPower (p : ℝ) : ℝ :=
  1603728 + 431568*(2:ℝ)^p + 185082*(3:ℝ)^p + 85248*(4:ℝ)^p +
  27194*(5:ℝ)^p + 5328*(8:ℝ)^p + (32:ℝ)^p + 26558*(48:ℝ)^p

/-- Proposed changed-replica profile with the very same positive residue. -/
noncomputable def frontierReplicaPower (T p : ℝ) : ℝ :=
  (T/10)*frontierTenReplicaPower p + residuePower p

lemma frontier_predecessor_residue (p : ℝ) :
    frontierReplicaPower 74 p=frontierPredecessorPower p := by
  unfold frontierReplicaPower residuePower frontierTenReplicaPower frontierPredecessorPower
  ring

/-- The new native profile changes the periodic term but not the charged tail. -/
theorem frontier_profile_difference (p : ℝ) :
    frontierPredecessorPower p / 74 - frontierTenReplicaPower p / 10 =
      (3*(3:ℝ)^p-5*(5:ℝ)^p+5*(32:ℝ)^p-3*(48:ℝ)^p) / 370 := by
  unfold frontierPredecessorPower frontierTenReplicaPower
  ring

/-- Universal strict dilution for the PR2802 paid profile, conditional on
independent literal realization at the chosen integer replica count. -/
theorem frontier_retained_tail_dilution (T p : ℝ) (hT : 74<T)
    (hp : 99/100 ≤ p) (hp1 : p<1) :
    frontierReplicaPower T p / (896*T*(73:ℝ)^p) <
      frontierPredecessorPower p / (66304*(73:ℝ)^p) := by
  have ht : 0<T := by linarith
  have hr : (0:ℝ)<(73:ℝ)^p := Real.rpow_pos_of_pos (by norm_num) p
  have hc : 0<residuePower p := div_pos (tail_power_positive p hp hp1) (by norm_num)
  have hsmall : 0<896*74*(73:ℝ)^p := by positivity
  have hden : 896*74*(73:ℝ)^p < 896*T*(73:ℝ)^p := by nlinarith
  have hd := div_lt_div_of_pos_left hc hsmall hden
  have hnew : frontierReplicaPower T p / (896*T*(73:ℝ)^p) =
      frontierTenReplicaPower p/(8960*(73:ℝ)^p) + residuePower p/(896*T*(73:ℝ)^p) := by
    unfold frontierReplicaPower
    field_simp
    ring
  have hold : frontierPredecessorPower p / (66304*(73:ℝ)^p) =
      frontierTenReplicaPower p/(8960*(73:ℝ)^p) + residuePower p/(896*74*(73:ℝ)^p) := by
    rw [←frontier_predecessor_residue p]
    unfold frontierReplicaPower
    field_simp
    ring
  rw [hnew,hold]
  linarith

end MultitapeToolkit.ReplicaTailGain
