import Nov15.CongestionI3
import Nov15.CongestionI3DualAlg
import Nov15.CongestionI3DualSig
import Nov15.CongestionI3DualConst
import Nov15.CongestionI3DualData
import Nov15.CongestionI3DualNumC
import Nov15.CongestionI3DualCertC0
import Nov15.CongestionI3DualCertC1
import Nov15.CongestionI3DualCertC2
import Nov15.CongestionI3DualCertC3
import Nov15.CongestionNativeTab

/-!
CONGESTION-NATIVE: the native-covering ceiling kappa <= .0136564 (own56, 8|9, m <= 5), the corrected form of
`CongestionI3Dual.ceiling_C2` (a COPY; the shipped files are unchanged).  See CongestionNative.md for the hypothesis ledger.
Changes against ceiling_C2 (HC1-HC4, AUD, AUD2 FIX A-C):
* hcong* carries the owned surplus `Omega = dprice ks s + mr - (6 * 9^s + 10)` on the right (ks = descents + non-unit rises, mr = unit rises: FIX-1) and is
  stated only for s in [.9, 1 - tC0]; `hE` is generalised to `Lj <= E + Omega` (`branchC_om`, `E_lower_cap_om`).
* ONE J throughout (J = J^arr, the arrival residual): hcong*, hdist and hJ all use the same variable `J`.
* The placeholder Props (Rank8C56, Prov) are gone; `ell`, `corr`, `cap` are concrete (`ellC`, `corrC`, `capC`); `LcTabC` is DERIVED from
  rational tables (CongestionNativeTab) and the hypotheses hspMono/hcstMono/hspTab/hcstTab/hunitTab.
* `hcong_of_capclass` (+ PathCut.lean) formalises the accounting that proves hcong* from the Cap class.
-/
namespace CongestionNative
open NumCertK JointCeiling CallerCost CongestionI3 CongestionI3Dual Finset

/-! ### 0. copied from CongestionI3Dual (F_base monotonicity and point enclosures, own56 side) -/
theorem Fc_monoOn (cf : CF) (hok : okR cf) (a b : ℚ) (ha : 0 ≤ a) (hb1 : b ≤ 1) (hd : 0 < dLo cf a b)
    (s s' : ℝ) (h1 : (a : ℝ) ≤ s) (hss : s ≤ s') (h2 : s' ≤ (b : ℝ)) : Fc cf s ≤ Fc cf s' := by
  have hab : (a : ℝ) ≤ b := le_trans h1 (le_trans hss h2)
  have hcont : ContinuousOn (Fc cf) (Set.Icc (a : ℝ) b) :=
    fun x _ => (Fc_hasDerivAt cf hok x).continuousAt.continuousWithinAt
  have hm : StrictMonoOn (Fc cf) (Set.Icc (a : ℝ) b) := by
    apply strictMonoOn_of_deriv_pos (convex_Icc _ _) hcont
    intro x hx
    rw [interior_Icc] at hx
    rw [(Fc_hasDerivAt cf hok x).deriv]
    have := dFc_ge cf hok a b ha hb1 x hx.1.le hx.2.le
    have hd' : (0:ℝ) < ((dLo cf a b : ℚ) : ℝ) := by exact_mod_cast hd
    linarith
  exact hm.monotoneOn ⟨h1, le_trans hss h2⟩ ⟨le_trans h1 hss, h2⟩ hss

theorem cfC_monoOn (s s' : ℝ) (h1 : (93 / 100 : ℝ) ≤ s) (hss : s ≤ s') (h2 : s' ≤ ((sC : ℚ) : ℝ)) : Fc cfC s ≤ Fc cfC s' :=
  Fc_monoOn cfC cfC_ok (93 / 100) sC (by norm_num) (by unfold sC; norm_num) cfC_d s s'
    (by rw [show (((93 / 100 : ℚ)) : ℝ) = 93 / 100 by norm_num]; exact h1) hss h2

theorem pt_of_Fup (cf : CF) (hok : okR cf) (q L : ℚ) (hq0 : 0 ≤ q) (hq1 : q ≤ 1) (h : Fup cf q q < 17 * L) :
    Fc cf (q : ℝ) < 17 * (L : ℝ) := by
  have h1 := Fc_le cf hok q q hq0 hq1 (q : ℝ) (le_refl _) (le_refl _)
  have h2 : ((Fup cf q q : ℚ) : ℝ) < ((17 * L : ℚ) : ℝ) := by exact_mod_cast h
  push_cast at h2
  linarith

theorem hFbC_of (a b L : ℚ) (hb93 : 93 / 100 ≤ 1 - b) (hab : a ≤ b) (haA : 1 - a ≤ sC) (ha0 : 0 ≤ a)
    (hpt : Fup cfC (1 - a) (1 - a) < 17 * L) :
    ∀ s : ℝ, ((1 - b : ℚ) : ℝ) ≤ s → s ≤ ((1 - a : ℚ) : ℝ) → Fc cfC s < 17 * (L : ℝ) := by
  intro s h1 h2
  have hb : (((93 / 100 : ℚ)) : ℝ) ≤ s := le_trans (by exact_mod_cast hb93) h1
  have hb' : (93 / 100 : ℝ) ≤ s := by rwa [show (((93 / 100 : ℚ)) : ℝ) = 93 / 100 by norm_num] at hb
  have hm := cfC_monoOn s ((1 - a : ℚ) : ℝ) hb' h2 (by exact_mod_cast haA)
  exact lt_of_le_of_lt hm (pt_of_Fup cfC cfC_ok (1 - a) L (by linarith [(by exact_mod_cast hab : (a : ℚ) ≤ b)]) (by linarith) hpt)

/-! ### 1. concrete definitions -/

/-- owned surplus: all owned moves `|k|^s` (ks = descents + non-unit rises, mr = unit rises, price 1 each) minus what `own56_floor` charges (6 * 9^s + 10). -/
noncomputable def Omega (ks : List ℕ) (mr : ℕ) (s : ℝ) : ℝ := dprice ks s + mr - (6 * (9 : ℝ) ^ s + 10)
/-- per-cell cap `(9^s - 8^s) / 48` -/
noncomputable def capC (s : ℝ) : ℝ := ((9 : ℝ) ^ s - (8 : ℝ) ^ s) / 48
/-- lower bound of the capped per-cell distance: `min (spF (1 - s)) (cap s)` -/
noncomputable def ellC (spF : ℝ → ℝ) (s : ℝ) : ℝ := min (spF (1 - s)) (capC s)
/-- LIFT1 rise correction `8 * cst(1 - s)` -/
noncomputable def corrC (cstF : ℝ → ℝ) (s : ℝ) : ℝ := 8 * cstF (1 - s)

/-! ### 2. two-sided I3 with the owned surplus on the right -/
section Elower
variable {ι : Type*} [DecidableEq ι]

/-- two-sided I3, cap/correction form with surplus: `sum min (dist, cap) - corr <= charges + Om` gives `E + Om >= 1936 ell - corr - m sigma`. -/
theorem E_lower_cap_om (R : Finset ι) (n : ι → ℕ) (d : ι → ℕ → ℕ) (J : Finset (ℕ × ℕ)) (dist : ℕ × ℕ → ℝ)
    (E s cap corr ell σ Om : ℝ) (m : ℕ)
    (hmono : ∀ r ∈ R, ∀ i < n r, d r i ≤ d r (i + 1)) (hd9 : ∀ r ∈ R, d r (n r) ≤ 9)
    (hm : (R.filter fun r => Mixed d n r).card ≤ m) (hσ0 : 0 ≤ σ)
    (hσ : ∀ a b : ℕ, 1 ≤ a → a ≤ b → b ≤ 8 → c2 (gs s) (a : ℝ) (b : ℝ) ≤ σ)
    (hcong : ∑ p ∈ J, min (dist p) cap - corr ≤ ∑ r ∈ R, ∑ i ∈ range (n r), c2 (gs s) (lev d r i) (lev d r (i + 1)) + Om)
    (hEex : ∑ r ∈ R, ex (gs s) (lev d r) (n r) ≤ E) (hdist : ∀ p ∈ J, ell ≤ min (dist p) cap) (hJ : 1936 ≤ J.card) (hell : 0 ≤ ell) :
    1936 * ell - corr - m * σ ≤ E + Om := by
  have h1 := sum_all_c2_le (gs s) (gs_zero s) R n d hmono hd9 m hm σ hσ0 hσ
  have h2 := Finset.card_nsmul_le_sum J (fun p => min (dist p) cap) ell hdist
  rw [nsmul_eq_mul] at h2
  have hj : (1936 : ℝ) ≤ J.card := by exact_mod_cast hJ
  nlinarith

end Elower

/-! ### 3. the branch with the surplus (the 88c branch is only needed for t >= .1) -/

theorem branchC_om (n : Inv) (ks : List ℕ) (mr : ℕ) (E Lj s : ℝ)
    (hF : Finv s n ≤ -400 * (8 : ℝ) ^ s - dprice ks s - mr - E)
    (hE : Lj ≤ E + Omega ks mr s) (hFb : Fc cfC s < 17 * Lj) :
    Finv s (invoice (caller 6 7) n 17) < 0 := by
  have h1' : Finv s n ≤ -400 * (8 : ℝ) ^ s - (6 * (9 : ℝ) ^ s + 10) - Lj := by
    unfold Omega at hE; linarith
  have h2 := invoice_F s (caller 6 7) n 17
  have h3 := invoice_F s (caller 6 7) natBaseC 17
  have h4 := natBaseC_F s
  have h6 := baseC_eq s
  push_cast at h2 h3
  nlinarith

/-! ### 4. the Cap-class accounting (HC1 sec. 2): hcong* from legal + transported cells -/

/-- `J` splits into LEGAL cells (a descent-free D_t-confined path: I3 charge + rise saving `cst * Rm`) and TRANSPORTED cells (cut at an owned descent, `<= 48 * Nf` of them, each at most `cap = U/48`).
Then `sum min - 8 cst <= Pub + Om` as soon as the Cap class inequality `cst (Rm - 8) + U Nf <= Om` holds. -/
theorem hcong_of_capclass (J : Finset (ℕ × ℕ)) (leg : ℕ × ℕ → Prop) [DecidablePred leg] (dist : ℕ × ℕ → ℝ)
    (cap U Pub cst Rm Nf Om : ℝ) (hcap : cap = U / 48) (hU : 0 ≤ U)
    (hleg : ∑ p ∈ J.filter leg, dist p ≤ Pub + cst * Rm)
    (hT : ((J.filter fun p => ¬ leg p).card : ℝ) ≤ 48 * Nf)
    (hclass : cst * (Rm - 8) + U * Nf ≤ Om) :
    ∑ p ∈ J, min (dist p) cap - 8 * cst ≤ Pub + Om := by
  have hsplit := Finset.sum_filter_add_sum_filter_not J leg (fun p => min (dist p) cap)
  have h1 : ∑ p ∈ J.filter leg, min (dist p) cap ≤ ∑ p ∈ J.filter leg, dist p :=
    Finset.sum_le_sum fun p _ => min_le_left _ _
  have h2 : ∑ p ∈ J.filter (fun p => ¬ leg p), min (dist p) cap ≤ ∑ _p ∈ J.filter (fun p => ¬ leg p), cap :=
    Finset.sum_le_sum fun p _ => min_le_right _ _
  rw [Finset.sum_const, nsmul_eq_mul] at h2
  have hc0 : 0 ≤ cap := by rw [hcap]; positivity
  have h3 : ((J.filter fun p => ¬ leg p).card : ℝ) * cap ≤ 48 * Nf * cap := mul_le_mul_of_nonneg_right hT hc0
  have h4 : 48 * Nf * cap = U * Nf := by rw [hcap]; ring
  nlinarith

/-! ### 5. the derived table `LcTabC` -/

theorem unit_mono (s s' : ℝ) (hs : 0 ≤ s) (h : s ≤ s') : (9 : ℝ) ^ s - (8 : ℝ) ^ s ≤ (9 : ℝ) ^ s' - (8 : ℝ) ^ s' := by
  have e : ∀ x : ℝ, (9 : ℝ) ^ x - (8 : ℝ) ^ x = (8 : ℝ) ^ x * (((9 : ℝ) / 8) ^ x - 1) := by
    intro x
    have h9 : (9 : ℝ) ^ x = (8 : ℝ) ^ x * ((9 : ℝ) / 8) ^ x := by
      rw [← Real.mul_rpow (by norm_num) (by norm_num)]; norm_num
    rw [h9]; ring
  rw [e, e]
  have h1 : (8 : ℝ) ^ s ≤ (8 : ℝ) ^ s' := Real.rpow_le_rpow_of_exponent_le (by norm_num) h
  have h2 : ((9 : ℝ) / 8) ^ s ≤ ((9 : ℝ) / 8) ^ s' := Real.rpow_le_rpow_of_exponent_le (by norm_num) h
  have h3 : (1 : ℝ) ≤ ((9 : ℝ) / 8) ^ s := Real.one_le_rpow (by norm_num) hs
  exact mul_le_mul h1 (by linarith) (by linarith) (by positivity)

/-- one t-piece `[a, b]` of the own56 table: `lcp <= 1936 ell - corr` follows from the rational table and endpoint hypotheses (monotonicity of spF and cst in t). -/
theorem tab_piece (spF cstF : ℝ → ℝ) (a b : ℚ) (lcp cH spLo unLo : ℚ) (hlcp : 0 ≤ lcp) (hcH : 0 ≤ cH) (ha0 : tC0 ≤ a) (hab : a ≤ b) (hb : b ≤ 1 / 10)
    (hmS : MonotoneOn spF (Set.Icc ((tC0 : ℚ) : ℝ) (1 / 10))) (hmC : MonotoneOn cstF (Set.Icc ((tC0 : ℚ) : ℝ) (1 / 10)))
    (hsp : (spLo : ℝ) ≤ spF (a : ℝ)) (hcs : cstF (b : ℝ) ≤ cH)
    (hun : (unLo : ℝ) ≤ (9 : ℝ) ^ (1 - (b : ℝ)) - (8 : ℝ) ^ (1 - (b : ℝ)))
    (hn1 : lcp + 8 * cH ≤ 1936 * spLo) (hn2 : lcp + 8 * cH ≤ 1936 * (unLo / 48)) :
    ∀ s : ℝ, ((1 - b : ℚ) : ℝ) ≤ s → s ≤ ((1 - a : ℚ) : ℝ) → (lcp : ℝ) ≤ 1936 * ellC spF s - corrC cstF s ∧ 0 ≤ ellC spF s := by
  intro s h1 h2
  push_cast at h1 h2
  have ha' : ((tC0 : ℚ) : ℝ) ≤ a := by exact_mod_cast ha0
  have hab' : (a : ℝ) ≤ b := by exact_mod_cast hab
  have hb' : (b : ℝ) ≤ 1 / 10 := by
    have := (Rat.cast_le (K := ℝ)).mpr hb
    push_cast at this; exact this
  have htl : (a : ℝ) ≤ 1 - s := by linarith
  have htu : 1 - s ≤ (b : ℝ) := by linarith
  have hspt : spF a ≤ spF (1 - s) := hmS ⟨ha', by linarith⟩ ⟨by linarith, by linarith⟩ htl
  have hcst : cstF (1 - s) ≤ cstF b := hmC ⟨by linarith, by linarith⟩ ⟨by linarith, hb'⟩ htu
  have hcap : (unLo : ℝ) / 48 ≤ capC s := by
    have := unit_mono (1 - b) s (by linarith) h1
    unfold capC; linarith
  have hell : min (spLo : ℝ) ((unLo : ℝ) / 48) ≤ ellC spF s := by
    unfold ellC
    exact le_min (le_trans (min_le_left _ _) (by linarith)) (le_trans (min_le_right _ _) hcap)
  have hcorr : corrC cstF s ≤ 8 * (cH : ℝ) := by unfold corrC; linarith
  have hn1' : (lcp : ℝ) + 8 * cH ≤ 1936 * spLo := by exact_mod_cast hn1
  have hn2' : (lcp : ℝ) + 8 * cH ≤ 1936 * ((unLo : ℝ) / 48) := by exact_mod_cast hn2
  have hl0 : (0 : ℝ) ≤ lcp := by exact_mod_cast hlcp
  have hc0 : (0 : ℝ) ≤ cH := by exact_mod_cast hcH
  rcases le_total (spLo : ℝ) ((unLo : ℝ) / 48) with hh | hh
  · rw [min_eq_left hh] at hell; exact ⟨by linarith, by linarith⟩
  · rw [min_eq_right hh] at hell; exact ⟨by linarith, by linarith⟩

/-! ### 6. the native-covering ceiling -/

/-- **native-covering ceiling.**  For a word whose public registers have at most 5 mixed registers (`hmix`) and whose owned layer splits as `ks` (descents + non-unit rises) and `mr` (unit rises),
if the congestion step `hcong` (with the owned surplus), the distance floor `hdist`, `hJ` (|J| >= 1936) hold for ONE set `J` (= J^arr), together with the accounting identities and the
certified tables, then `F(1 - t, invoice (caller 6 7) n 17) < 0` for all t in [tC0, 1], i.e. kappa <= tC0 = .0136564 (8|9). Every hypothesis is listed in CongestionNative.md. -/
theorem ceiling_native {ι : Type*} [DecidableEq ι]
    (R : Finset ι) (nR : ι → ℕ) (dR : ι → ℕ → ℕ)
    (hmono : ∀ r ∈ R, ∀ i < nR r, dR r i ≤ dR r (i + 1)) (hd9 : ∀ r ∈ R, dR r (nR r) ≤ 9)
    (hmix : (R.filter fun r => Mixed dR nR r).card ≤ 5)
    (n : Inv) (ks : List ℕ) (mr st : ℕ) (E : ℝ → ℝ) (J : Finset (ℕ × ℕ)) (distF : ℝ → ℕ × ℕ → ℝ) (spF cstF : ℝ → ℝ)
    (hk : ∀ k ∈ ks, 1 ≤ k ∧ k ≤ 9) (hmass : 56 ≤ ks.sum) (hmd : 8 ≤ ks.length) (hmr : 8 ≤ mr)
    (hF : ∀ s, 0 ≤ s → s ≤ 1 → Finv s n ≤ -400 * (8 : ℝ) ^ s - dprice ks s - mr - E s)
    (hY : 104 ≤ st + (ks.length + mr))
    (hst : ∀ s, 0 ≤ s → s ≤ 1 → (2 - (2 : ℝ) ^ s) * st ≤ E s)
    (hEex : ∀ s, 0 ≤ s → s ≤ 1 → ∑ r ∈ R, ex (gs s) (lev dR r) (nR r) ≤ E s)
    (hcong : ∀ s, 9 / 10 ≤ s → s ≤ 1 - ((tC0 : ℚ) : ℝ) →
      ∑ p ∈ J, min (distF s p) (capC s) - corrC cstF s ≤
        ∑ r ∈ R, ∑ i ∈ range (nR r), c2 (gs s) (lev dR r i) (lev dR r (i + 1)) + Omega ks mr s)
    (hdist : ∀ s, 9 / 10 ≤ s → s ≤ 1 - ((tC0 : ℚ) : ℝ) → ∀ p ∈ J, spF (1 - s) ≤ distF s p)
    (hJ : 1936 ≤ J.card)
    (hspMono : MonotoneOn spF (Set.Icc ((tC0 : ℚ) : ℝ) (1 / 10)))
    (hcstMono : MonotoneOn cstF (Set.Icc ((tC0 : ℚ) : ℝ) (1 / 10)))
    (hspTab : ((spFloC0 : ℚ) : ℝ) ≤ spF ((tC0 : ℚ) : ℝ) ∧ ((spFloC1 : ℚ) : ℝ) ≤ spF ((tC1 : ℚ) : ℝ) ∧
      ((spFloC2 : ℚ) : ℝ) ≤ spF ((tC2 : ℚ) : ℝ) ∧ ((spFloC3 : ℚ) : ℝ) ≤ spF ((tC3 : ℚ) : ℝ))
    (hcstTab : cstF ((tC1 : ℚ) : ℝ) ≤ ((cHC0 : ℚ) : ℝ) ∧ cstF ((tC2 : ℚ) : ℝ) ≤ ((cHC1 : ℚ) : ℝ) ∧
      cstF ((tC3 : ℚ) : ℝ) ≤ ((cHC2 : ℚ) : ℝ) ∧ cstF (1 / 10) ≤ ((cHC3 : ℚ) : ℝ))
    (hunitTab : ((unitLoC0 : ℚ) : ℝ) ≤ (9 : ℝ) ^ (1 - ((tC1 : ℚ) : ℝ)) - (8 : ℝ) ^ (1 - ((tC1 : ℚ) : ℝ)) ∧
      ((unitLoC1 : ℚ) : ℝ) ≤ (9 : ℝ) ^ (1 - ((tC2 : ℚ) : ℝ)) - (8 : ℝ) ^ (1 - ((tC2 : ℚ) : ℝ)) ∧
      ((unitLoC2 : ℚ) : ℝ) ≤ (9 : ℝ) ^ (1 - ((tC3 : ℚ) : ℝ)) - (8 : ℝ) ^ (1 - ((tC3 : ℚ) : ℝ)) ∧
      ((unitLoC3 : ℚ) : ℝ) ≤ (9 : ℝ) ^ (1 - (1 / 10 : ℝ)) - (8 : ℝ) ^ (1 - (1 / 10 : ℝ))) :
    ∀ t : ℝ, ((tC0 : ℚ) : ℝ) ≤ t → t ≤ 1 → Finv (1 - t) (invoice (caller 6 7) n 17) < 0 := by
  have piece : ∀ (a b lcp σ : ℚ), sigOK (1 - b) (1 - a) σ = true → 0 ≤ σ → tC0 ≤ a → a ≤ b → b ≤ 1 / 10 → 0 ≤ lcp →
      (∀ s : ℝ, ((1 - b : ℚ) : ℝ) ≤ s → s ≤ ((1 - a : ℚ) : ℝ) → (lcp : ℝ) ≤ 1936 * ellC spF s - corrC cstF s ∧ 0 ≤ ellC spF s) →
      (∀ s : ℝ, ((1 - b : ℚ) : ℝ) ≤ s → s ≤ ((1 - a : ℚ) : ℝ) → Fc cfC s < 17 * (((lcp - 5 * σ : ℚ)) : ℝ)) →
      ∀ t : ℝ, (a : ℝ) ≤ t → t ≤ (b : ℝ) → Finv (1 - t) (invoice (caller 6 7) n 17) < 0 := by
    intro a b lcp σ hσc hσ0 ha0 hab hb hl0 hLcp hFb t h1 h2
    have ha0q : (0 : ℚ) ≤ a := le_trans (by unfold tC0; norm_num) ha0
    have ha0' : ((tC0 : ℚ) : ℝ) ≤ a := by exact_mod_cast ha0
    have hb' : (b : ℝ) ≤ 1 / 10 := by
      have := (Rat.cast_le (K := ℝ)).mpr hb
      push_cast at this; exact this
    have hab' : (a : ℝ) ≤ b := by exact_mod_cast hab
    have hA0 : (0 : ℝ) ≤ a := by exact_mod_cast ha0q
    have hs0 : 0 ≤ 1 - t := by linarith
    have hs1 : 1 - t ≤ 1 := by linarith
    have hσ : ∀ a' b' : ℕ, 1 ≤ a' → a' ≤ b' → b' ≤ 8 → c2 (gs (1 - t)) (a' : ℝ) (b' : ℝ) ≤ (σ : ℝ) := by
      intro a' b' h1' h2' h3'
      exact sig_of_ok (1 - b) (1 - a) σ hσc (by linarith) (by linarith) hσ0 (1 - t)
        (by push_cast; linarith) (by push_cast; linarith) a' b' h1' h2' h3'
    have hl0' : (0 : ℝ) ≤ lcp := by exact_mod_cast hl0
    have hLcp' := hLcp (1 - t) (by push_cast; linarith) (by push_cast; linarith)
    have hslo : (9 / 10 : ℝ) ≤ 1 - t := by linarith
    have hshi : 1 - t ≤ 1 - ((tC0 : ℚ) : ℝ) := by linarith
    have hell : 0 ≤ ellC spF (1 - t) := hLcp'.2
    have hE := E_lower_cap_om R nR dR J (distF (1 - t)) (E (1 - t)) (1 - t) (capC (1 - t)) (corrC cstF (1 - t)) (ellC spF (1 - t))
      (σ : ℝ) (Omega ks mr (1 - t)) 5 hmono hd9 hmix (by exact_mod_cast hσ0) hσ (hcong (1 - t) hslo hshi) (hEex _ hs0 hs1)
      (fun p hp => le_min (le_trans (min_le_left _ _) (hdist (1 - t) hslo hshi p hp)) (min_le_right _ _)) hJ hell
    have hE' : (((lcp - 5 * σ : ℚ)) : ℝ) ≤ E (1 - t) + Omega ks mr (1 - t) := by push_cast; push_cast at hE; linarith [hLcp'.1]
    exact branchC_om n ks mr (E (1 - t)) _ (1 - t) (hF _ hs0 hs1) hE'
      (hFb (1 - t) (by push_cast; linarith) (by push_cast; linarith))
  intro t ht ht1
  have htC0 : (0 : ℝ) ≤ ((tC0 : ℚ) : ℝ) := by unfold tC0; norm_num
  have hs0 : (0 : ℝ) ≤ 1 - t := by linarith
  have hs1 : 1 - t ≤ 1 := by linarith
  have hu1 : (1 : ℝ) ≤ (2 : ℝ) ^ (1 - t) := Real.one_le_rpow (by norm_num) hs0
  have hu2 : (2 : ℝ) ^ (1 - t) ≤ 2 := by
    have := Real.rpow_le_rpow_of_exponent_le (show (1 : ℝ) ≤ 2 by norm_num) hs1; simpa using this
  have hE0 : 0 ≤ E (1 - t) :=
    le_trans (mul_nonneg (by linarith) (Nat.cast_nonneg st)) (hst _ hs0 hs1)
  rcases le_or_gt (1 / 10 : ℝ) t with h10 | h10
  · have h2 := invoice_F (1 - t) (caller 6 7) n 17
    have h3 := invoice_F (1 - t) (caller 6 7) natBaseC 17
    have h4 := natBaseC_F (1 - t)
    push_cast at h2 h3
    have h1 := own56_floor (1 - t) hs0 hs1 ks hk hmass hmd mr st hmr (Finv (1 - t) n) (E (1 - t)) 0 (hF _ hs0 hs1) hY
      (hst _ hs0 hs1) hE0
    have hc0 : (0 : ℝ) ≤ 88 * (2 - (2 : ℝ) ^ (1 - t)) := by linarith
    rw [max_eq_left hc0] at h1
    have h5 := cfC88_neg (1 - t) hs0 (by linarith)
    have h6 := base88_eq (1 - t)
    nlinarith
  · obtain ⟨sp0, sp1, sp2, sp3⟩ := hspTab
    obtain ⟨cs0, cs1, cs2, cs3⟩ := hcstTab
    obtain ⟨un0, un1, un2, un3⟩ := hunitTab
    have q01 : tC0 ≤ tC1 := by unfold tC0 tC1; norm_num
    have q12 : tC1 ≤ tC2 := by unfold tC1 tC2; norm_num
    have q23 : tC2 ≤ tC3 := by unfold tC2 tC3; norm_num
    have q3 : tC3 ≤ 1 / 10 := by unfold tC3; norm_num
    have lcp0 : ∀ q : ℚ, q = lcpC0 ∨ q = lcpC1 ∨ q = lcpC2 ∨ q = lcpC3 → 0 ≤ q := by
      intro q h; unfold lcpC0 lcpC1 lcpC2 lcpC3 at h; rcases h with h | h | h | h <;> rw [h] <;> norm_num
    have cH0 : ∀ q : ℚ, q = cHC0 ∨ q = cHC1 ∨ q = cHC2 ∨ q = cHC3 → 0 ≤ q := by
      intro q h; unfold cHC0 cHC1 cHC2 cHC3 at h; rcases h with h | h | h | h <;> rw [h] <;> norm_num
    have e1 : ((tC0 : ℚ) : ℝ) ≤ ((tC1 : ℚ) : ℝ) := by exact_mod_cast q01
    have e2 : ((tC1 : ℚ) : ℝ) ≤ ((tC2 : ℚ) : ℝ) := by exact_mod_cast q12
    have e3 : ((tC2 : ℚ) : ℝ) ≤ ((tC3 : ℚ) : ℝ) := by exact_mod_cast q23
    by_cases k1 : t ≤ ((tC1 : ℚ) : ℝ)
    · exact piece tC0 tC1 lcpC0 sgC0 sigC0 (by unfold sgC0; norm_num) (le_refl _) q01 (by linarith) (lcp0 _ (Or.inl rfl))
        (tab_piece spF cstF tC0 tC1 lcpC0 cHC0 spFloC0 unitLoC0 (lcp0 _ (Or.inl rfl)) (cH0 _ (Or.inl rfl)) (le_refl _) q01 (by linarith)
          hspMono hcstMono sp0 cs0 un0 tabC0.1 tabC0.2)
        (hFbC_of tC0 tC1 LC0 (by unfold tC1; norm_num) q01 (by unfold tC0 sC; norm_num) (by unfold tC0; norm_num) ptC0) t ht k1
    by_cases k2 : t ≤ ((tC2 : ℚ) : ℝ)
    · exact piece tC1 tC2 lcpC1 sgC1 sigC1 (by unfold sgC1; norm_num) q01 q12 (by linarith) (lcp0 _ (Or.inr (Or.inl rfl)))
        (tab_piece spF cstF tC1 tC2 lcpC1 cHC1 spFloC1 unitLoC1 (lcp0 _ (Or.inr (Or.inl rfl))) (cH0 _ (Or.inr (Or.inl rfl))) q01 q12 (by linarith)
          hspMono hcstMono sp1 cs1 un1 tabC1.1 tabC1.2)
        (hFbC_of tC1 tC2 LC1 (by unfold tC2; norm_num) q12 (by unfold tC1 sC; norm_num) (by unfold tC1; norm_num) ptC1) t
        (by push Not at k1; exact k1.le) k2
    by_cases k3 : t ≤ ((tC3 : ℚ) : ℝ)
    · exact piece tC2 tC3 lcpC2 sgC2 sigC2 (by unfold sgC2; norm_num) (le_trans q01 q12) q23 (by linarith) (lcp0 _ (Or.inr (Or.inr (Or.inl rfl))))
        (tab_piece spF cstF tC2 tC3 lcpC2 cHC2 spFloC2 unitLoC2 (lcp0 _ (Or.inr (Or.inr (Or.inl rfl)))) (cH0 _ (Or.inr (Or.inr (Or.inl rfl))))
          (le_trans q01 q12) q23 (by linarith) hspMono hcstMono sp2 cs2 un2 tabC2.1 tabC2.2)
        (hFbC_of tC2 tC3 LC2 (by unfold tC3; norm_num) q23 (by unfold tC2 sC; norm_num) (by unfold tC2; norm_num) ptC2) t
        (by push Not at k2; exact k2.le) k3
    · have h110 : (((1 / 10 : ℚ)) : ℝ) = 1 / 10 := by norm_num
      refine piece tC3 (1 / 10) lcpC3 sgC3 ?_ (by unfold sgC3; norm_num) (le_trans q01 (le_trans q12 q23)) q3 (le_refl _)
        (lcp0 _ (Or.inr (Or.inr (Or.inr rfl)))) ?_ ?_ t (by push Not at k3; exact k3.le) (by push_cast; exact h10.le)
      · rw [show (1 - 1 / 10 : ℚ) = 9 / 10 by norm_num]; exact sigC3
      · refine tab_piece spF cstF tC3 (1 / 10) lcpC3 cHC3 spFloC3 unitLoC3 (lcp0 _ (Or.inr (Or.inr (Or.inr rfl)))) (cH0 _ (Or.inr (Or.inr (Or.inr rfl))))
          (le_trans q01 (le_trans q12 q23)) q3 (le_refl _) hspMono hcstMono sp3 ?_ ?_ tabC3.1 tabC3.2
        · rw [h110]; exact cs3
        · rw [h110]; exact un3
      · intro s hs1' hs2'
        have hsC' : s ≤ ((sC : ℚ) : ℝ) := by
          have : (1 : ℚ) - tC3 ≤ sC := by unfold tC3 sC; norm_num
          have h' : (((1 - tC3 : ℚ)) : ℝ) ≤ ((sC : ℚ) : ℝ) := by exact_mod_cast this
          linarith
        have h9 : (9 / 10 : ℝ) ≤ s := by
          have : ((((1 - 1 / 10 : ℚ)) : ℚ) : ℝ) = 9 / 10 := by norm_num
          linarith
        have := cfC_neg s h9 hsC'
        have h7 : ((liftC : ℚ) : ℝ) ≤ 17 * (((lcpC3 - 5 * sgC3 : ℚ)) : ℝ) := by
          have : liftC ≤ 17 * LC3 := LC3_ge
          exact_mod_cast this
        linarith

end CongestionNative

#print axioms CongestionNative.E_lower_cap_om
#print axioms CongestionNative.branchC_om
#print axioms CongestionNative.hcong_of_capclass
#print axioms CongestionNative.unit_mono
#print axioms CongestionNative.tab_piece
#print axioms CongestionNative.ceiling_native
