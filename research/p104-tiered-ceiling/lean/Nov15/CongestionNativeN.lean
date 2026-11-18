import Nov15.CongestionNativeJ
import Nov15.CongestionNativeNDefs
import Nov15.CongestionNativeNSig0
import Nov15.CongestionNativeNSig1
import Nov15.CongestionNativeNSig2
import Nov15.CongestionNativeNSig3
import Nov15.CongestionNativeNSig4
import Nov15.CongestionNativeNPt
import Nov15.CongestionNativeNUnit

/-!
CONGESTION-NATIVE-N96: `ceiling_native` / `ceiling_native_J` with the junk count hypothesis lowered to `hJ : 96 <= |J|`,
the value of Law A (JunkLawA.lean) at descending mass 56: 96 = 2 (104 - 56).  Conclusion: F(1 - t, invoice (caller 6 7) n 17) < 0 for t in [tN0, 1],
tN0 = .0151027, i.e. kappa <= .0151027 (own56, m <= 5) for every word satisfying the hypotheses (float crossing .0151026, see JunkLawA.md).
Pieces: [tN0, tN1, tN2, tN3, .07, .1] (4 point-form pieces with F_base monotone on [.93, 1 - tN0], one box-form piece on s in [.9, .93]), then t >= .1 as in `ceiling_native`.
Hypotheses are those of `ceiling_native_J` with 4962 -> 96 and the new endpoint brackets (hspTabN, hcstTabN); all unit brackets, sigma certificates, F_base enclosures are kernel.
-/
namespace CongestionNative
open NumCertK JointCeiling CallerCost CongestionI3 CongestionI3Dual Finset

/-- one t-piece `[a, b]` with N = 96; `lcp` may be negative (only `0 <= spLo`, `0 <= unLo` are needed for `0 <= ell`). -/
theorem tab_pieceN (spF cstF : ℝ → ℝ) (a b : ℚ) (lcp cH spLo unLo : ℚ) (hcH : 0 ≤ cH) (hsp0 : 0 ≤ spLo) (hun0 : 0 ≤ unLo)
    (ha0 : tN0 ≤ a) (hab : a ≤ b) (hb : b ≤ 1 / 10)
    (hmS : MonotoneOn spF (Set.Icc ((tN0 : ℚ) : ℝ) (1 / 10))) (hmC : MonotoneOn cstF (Set.Icc ((tN0 : ℚ) : ℝ) (1 / 10)))
    (hsp : (spLo : ℝ) ≤ spF (a : ℝ)) (hcs : cstF (b : ℝ) ≤ cH)
    (hun : (unLo : ℝ) ≤ (9 : ℝ) ^ (1 - (b : ℝ)) - (8 : ℝ) ^ (1 - (b : ℝ)))
    (hn1 : lcp + 8 * cH ≤ 96 * spLo) (hn2 : lcp + 8 * cH ≤ 96 * (unLo / 48)) :
    ∀ s : ℝ, ((1 - b : ℚ) : ℝ) ≤ s → s ≤ ((1 - a : ℚ) : ℝ) → (lcp : ℝ) ≤ 96 * ellC spF s - corrC cstF s ∧ 0 ≤ ellC spF s := by
  intro s h1 h2
  push_cast at h1 h2
  have ha' : ((tN0 : ℚ) : ℝ) ≤ a := by exact_mod_cast ha0
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
  have hn1' : (lcp : ℝ) + 8 * cH ≤ 96 * spLo := by exact_mod_cast hn1
  have hn2' : (lcp : ℝ) + 8 * cH ≤ 96 * ((unLo : ℝ) / 48) := by exact_mod_cast hn2
  have hs0' : (0 : ℝ) ≤ spLo := by exact_mod_cast hsp0
  have hu0' : (0 : ℝ) ≤ (unLo : ℝ) / 48 := by
    have h : (0 : ℝ) ≤ unLo := by exact_mod_cast hun0
    linarith
  have hc0 : (0 : ℝ) ≤ cH := by exact_mod_cast hcH
  have hmin0 : (0 : ℝ) ≤ min (spLo : ℝ) ((unLo : ℝ) / 48) := le_min hs0' hu0'
  rcases le_total (spLo : ℝ) ((unLo : ℝ) / 48) with hh | hh
  · rw [min_eq_left hh] at hell hmin0; exact ⟨by linarith, by linarith⟩
  · rw [min_eq_right hh] at hell hmin0; exact ⟨by linarith, by linarith⟩

/-- **no-hJ ceiling, junk count 96.**  Same statement as `ceiling_native_J` with `hJ : 96 ≤ J.card`, hcong*/hdist on s in [.9, 1 - tN0], monotonicity on [tN0, 1/10], five spF and five cst endpoint brackets.
Conclusion on t in [tN0, 1]: kappa <= .0151027. -/
theorem ceiling_native_N96 {ι : Type*} [DecidableEq ι]
    (R : Finset ι) (nR : ι → ℕ) (dR : ι → ℕ → ℕ)
    (hmono : ∀ r ∈ R, ∀ i < nR r, dR r i ≤ dR r (i + 1)) (hd9 : ∀ r ∈ R, dR r (nR r) ≤ 9)
    (hmix : (R.filter fun r => Mixed dR nR r).card ≤ 5)
    (n : Inv) (ks : List ℕ) (mr st : ℕ) (E : ℝ → ℝ) (J : Finset (ℕ × ℕ)) (distF : ℝ → ℕ × ℕ → ℝ) (spF cstF : ℝ → ℝ)
    (hk : ∀ k ∈ ks, 1 ≤ k ∧ k ≤ 9) (hmass : 56 ≤ ks.sum) (hmd : 8 ≤ ks.length) (hmr : 8 ≤ mr)
    (hF : ∀ s, 0 ≤ s → s ≤ 1 → Finv s n ≤ -400 * (8 : ℝ) ^ s - dprice ks s - mr - E s)
    (hY : 104 ≤ st + (ks.length + mr))
    (hst : ∀ s, 0 ≤ s → s ≤ 1 → (2 - (2 : ℝ) ^ s) * st ≤ E s)
    (hEex : ∀ s, 0 ≤ s → s ≤ 1 → ∑ r ∈ R, ex (gs s) (lev dR r) (nR r) ≤ E s)
    (hcong : ∀ s, 9 / 10 ≤ s → s ≤ 1 - ((tN0 : ℚ) : ℝ) →
      ∑ p ∈ J, min (distF s p) (capC s) - corrC cstF s ≤
        ∑ r ∈ R, ∑ i ∈ range (nR r), c2 (gs s) (lev dR r i) (lev dR r (i + 1)) + Omega ks mr s)
    (hdist : ∀ s, 9 / 10 ≤ s → s ≤ 1 - ((tN0 : ℚ) : ℝ) → ∀ p ∈ J, spF (1 - s) ≤ distF s p)
    (hJ : 96 ≤ J.card)
    (hspMono : MonotoneOn spF (Set.Icc ((tN0 : ℚ) : ℝ) (1 / 10)))
    (hcstMono : MonotoneOn cstF (Set.Icc ((tN0 : ℚ) : ℝ) (1 / 10)))
    (hspTabN : ((spFloN0 : ℚ) : ℝ) ≤ spF ((tN0 : ℚ) : ℝ) ∧ ((spFloN1 : ℚ) : ℝ) ≤ spF ((tN1 : ℚ) : ℝ) ∧
      ((spFloN2 : ℚ) : ℝ) ≤ spF ((tN2 : ℚ) : ℝ) ∧ ((spFloN3 : ℚ) : ℝ) ≤ spF ((tN3 : ℚ) : ℝ) ∧
      ((spFloN4 : ℚ) : ℝ) ≤ spF ((tN4 : ℚ) : ℝ))
    (hcstTabN : cstF ((tN1 : ℚ) : ℝ) ≤ ((cHN0 : ℚ) : ℝ) ∧ cstF ((tN2 : ℚ) : ℝ) ≤ ((cHN1 : ℚ) : ℝ) ∧
      cstF ((tN3 : ℚ) : ℝ) ≤ ((cHN2 : ℚ) : ℝ) ∧ cstF ((tN4 : ℚ) : ℝ) ≤ ((cHN3 : ℚ) : ℝ) ∧
      cstF ((tN5 : ℚ) : ℝ) ≤ ((cHN4 : ℚ) : ℝ)) :
    ∀ t : ℝ, ((tN0 : ℚ) : ℝ) ≤ t → t ≤ 1 → Finv (1 - t) (invoice (caller 6 7) n 17) < 0 := by
  have piece : ∀ (a b lcp σ : ℚ), sigOK (1 - b) (1 - a) σ = true → 0 ≤ σ → tN0 ≤ a → a ≤ b → b ≤ 1 / 10 →
      (∀ s : ℝ, ((1 - b : ℚ) : ℝ) ≤ s → s ≤ ((1 - a : ℚ) : ℝ) → (lcp : ℝ) ≤ 96 * ellC spF s - corrC cstF s ∧ 0 ≤ ellC spF s) →
      (∀ s : ℝ, ((1 - b : ℚ) : ℝ) ≤ s → s ≤ ((1 - a : ℚ) : ℝ) → Fc cfC s < 17 * (((lcp - 5 * σ : ℚ)) : ℝ)) →
      ∀ t : ℝ, (a : ℝ) ≤ t → t ≤ (b : ℝ) → Finv (1 - t) (invoice (caller 6 7) n 17) < 0 := by
    intro a b lcp σ hσc hσ0 ha0 hab hb hLcp hFb t h1 h2
    have ha0q : (0 : ℚ) ≤ a := le_trans (by unfold tN0; norm_num) ha0
    have ha0' : ((tN0 : ℚ) : ℝ) ≤ a := by exact_mod_cast ha0
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
    have hLcp' := hLcp (1 - t) (by push_cast; linarith) (by push_cast; linarith)
    have hslo : (9 / 10 : ℝ) ≤ 1 - t := by linarith
    have hshi : 1 - t ≤ 1 - ((tN0 : ℚ) : ℝ) := by linarith
    have hell : 0 ≤ ellC spF (1 - t) := hLcp'.2
    have hE := E_lower_cap_omN R nR dR J (distF (1 - t)) (E (1 - t)) (1 - t) (capC (1 - t)) (corrC cstF (1 - t)) (ellC spF (1 - t))
      (σ : ℝ) (Omega ks mr (1 - t)) 5 96 hmono hd9 hmix (by exact_mod_cast hσ0) hσ (hcong (1 - t) hslo hshi) (hEex _ hs0 hs1)
      (fun p hp => le_min (le_trans (min_le_left _ _) (hdist (1 - t) hslo hshi p hp)) (min_le_right _ _)) hJ hell
    have hE' : (((lcp - 5 * σ : ℚ)) : ℝ) ≤ E (1 - t) + Omega ks mr (1 - t) := by
      push_cast; push_cast at hE; linarith [hLcp'.1]
    exact branchC_om n ks mr (E (1 - t)) _ (1 - t) (hF _ hs0 hs1) hE'
      (hFb (1 - t) (by push_cast; linarith) (by push_cast; linarith))
  intro t ht ht1
  have ht0 : (0 : ℝ) ≤ ((tN0 : ℚ) : ℝ) := by unfold tN0; norm_num
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
  · obtain ⟨sp0, sp1, sp2, sp3, sp4⟩ := hspTabN
    obtain ⟨cs0, cs1, cs2, cs3, cs4⟩ := hcstTabN
    have q01 : tN0 ≤ tN1 := by unfold tN0 tN1; norm_num
    have q12 : tN1 ≤ tN2 := by unfold tN1 tN2; norm_num
    have q23 : tN2 ≤ tN3 := by unfold tN2 tN3; norm_num
    have q34 : tN3 ≤ tN4 := by unfold tN3 tN4; norm_num
    have q45 : tN4 ≤ tN5 := by unfold tN4 tN5; norm_num
    have b1 : tN1 ≤ 1 / 10 := by unfold tN1; norm_num
    have b2 : tN2 ≤ 1 / 10 := by unfold tN2; norm_num
    have b3 : tN3 ≤ 1 / 10 := by unfold tN3; norm_num
    have b4 : tN4 ≤ 1 / 10 := by unfold tN4; norm_num
    have b5 : tN5 ≤ 1 / 10 := by unfold tN5; norm_num
    have q02 := le_trans q01 q12
    have q03 := le_trans q02 q23
    have q04 := le_trans q03 q34
    have un0 := unit_of_Fup tN1 unitLoN0 (by unfold tN1; norm_num) (by unfold tN1; norm_num) unitN0
    have un1 := unit_of_Fup tN2 unitLoN1 (by unfold tN2; norm_num) (by unfold tN2; norm_num) unitN1
    have un2 := unit_of_Fup tN3 unitLoN2 (by unfold tN3; norm_num) (by unfold tN3; norm_num) unitN2
    have un3 := unit_of_Fup tN4 unitLoN3 (by unfold tN4; norm_num) (by unfold tN4; norm_num) unitN3
    have un4 := unit_of_Fup tN5 unitLoN4 (by unfold tN5; norm_num) (by unfold tN5; norm_num) unitN4
    have zspFloN0 : (0 : ℚ) ≤ spFloN0 := by unfold spFloN0; norm_num
    have zspFloN1 : (0 : ℚ) ≤ spFloN1 := by unfold spFloN1; norm_num
    have zspFloN2 : (0 : ℚ) ≤ spFloN2 := by unfold spFloN2; norm_num
    have zspFloN3 : (0 : ℚ) ≤ spFloN3 := by unfold spFloN3; norm_num
    have zspFloN4 : (0 : ℚ) ≤ spFloN4 := by unfold spFloN4; norm_num
    have zcHN0 : (0 : ℚ) ≤ cHN0 := by unfold cHN0; norm_num
    have zcHN1 : (0 : ℚ) ≤ cHN1 := by unfold cHN1; norm_num
    have zcHN2 : (0 : ℚ) ≤ cHN2 := by unfold cHN2; norm_num
    have zcHN3 : (0 : ℚ) ≤ cHN3 := by unfold cHN3; norm_num
    have zcHN4 : (0 : ℚ) ≤ cHN4 := by unfold cHN4; norm_num
    have zunitLoN0 : (0 : ℚ) ≤ unitLoN0 := by unfold unitLoN0; norm_num
    have zunitLoN1 : (0 : ℚ) ≤ unitLoN1 := by unfold unitLoN1; norm_num
    have zunitLoN2 : (0 : ℚ) ≤ unitLoN2 := by unfold unitLoN2; norm_num
    have zunitLoN3 : (0 : ℚ) ≤ unitLoN3 := by unfold unitLoN3; norm_num
    have zunitLoN4 : (0 : ℚ) ≤ unitLoN4 := by unfold unitLoN4; norm_num
    have hF4 : ∀ (a b L : ℚ), 93 / 100 ≤ 1 - b → a ≤ b → tN0 ≤ a → Fup cfC (1 - a) (1 - a) < 17 * L →
        ∀ s : ℝ, ((1 - b : ℚ) : ℝ) ≤ s → s ≤ ((1 - a : ℚ) : ℝ) → Fc cfC s < 17 * (L : ℝ) := by
      intro a b L hb93 hab haN hpt
      exact hFbJ_of a b L hb93 hab (le_trans (by unfold tJ0 tN0; norm_num) haN) hpt
    by_cases k1 : t ≤ ((tN1 : ℚ) : ℝ)
    · exact piece tN0 tN1 lcpN0 sgN0 sigN0 (by unfold sgN0; norm_num) (le_refl _) q01 b1
        (tab_pieceN spF cstF tN0 tN1 lcpN0 cHN0 spFloN0 unitLoN0 zcHN0 zspFloN0 zunitLoN0 (le_refl _) q01 b1
          hspMono hcstMono sp0 cs0 un0 tabN0.1 tabN0.2)
        (hF4 tN0 tN1 LN0 (by unfold tN1; norm_num) q01 (le_refl _) ptN0) t ht k1
    by_cases k2 : t ≤ ((tN2 : ℚ) : ℝ)
    · exact piece tN1 tN2 lcpN1 sgN1 sigN1 (by unfold sgN1; norm_num) q01 q12 b2
        (tab_pieceN spF cstF tN1 tN2 lcpN1 cHN1 spFloN1 unitLoN1 zcHN1 zspFloN1 zunitLoN1 q01 q12 b2
          hspMono hcstMono sp1 cs1 un1 tabN1.1 tabN1.2)
        (hF4 tN1 tN2 LN1 (by unfold tN2; norm_num) q12 q01 ptN1) t (by push Not at k1; exact k1.le) k2
    by_cases k3 : t ≤ ((tN3 : ℚ) : ℝ)
    · exact piece tN2 tN3 lcpN2 sgN2 sigN2 (by unfold sgN2; norm_num) q02 q23 b3
        (tab_pieceN spF cstF tN2 tN3 lcpN2 cHN2 spFloN2 unitLoN2 zcHN2 zspFloN2 zunitLoN2 q02 q23 b3
          hspMono hcstMono sp2 cs2 un2 tabN2.1 tabN2.2)
        (hF4 tN2 tN3 LN2 (by unfold tN3; norm_num) q23 q02 ptN2) t (by push Not at k2; exact k2.le) k3
    by_cases k4 : t ≤ ((tN4 : ℚ) : ℝ)
    · exact piece tN3 tN4 lcpN3 sgN3 sigN3 (by unfold sgN3; norm_num) q03 q34 b4
        (tab_pieceN spF cstF tN3 tN4 lcpN3 cHN3 spFloN3 unitLoN3 zcHN3 zspFloN3 zunitLoN3 q03 q34 b4
          hspMono hcstMono sp3 cs3 un3 tabN3.1 tabN3.2)
        (hF4 tN3 tN4 LN3 (by unfold tN4; norm_num) q34 q03 ptN3) t (by push Not at k3; exact k3.le) k4
    · refine piece tN4 tN5 lcpN4 sgN4 sigN4 (by unfold sgN4; norm_num) q04 q45 b5
        (tab_pieceN spF cstF tN4 tN5 lcpN4 cHN4 spFloN4 unitLoN4 zcHN4 zspFloN4 zunitLoN4 q04 q45 b5
          hspMono hcstMono sp4 cs4 un4 tabN4.1 tabN4.2) ?_ t (by push Not at k4; exact k4.le) (by unfold tN5; push_cast; exact h10.le)
      intro s hs1' hs2'
      have e1 : (((1 - tN5 : ℚ)) : ℝ) = 9 / 10 := by unfold tN5; norm_num
      have e2 : (((1 - tN4 : ℚ)) : ℝ) = 93 / 100 := by unfold tN4; norm_num
      rw [e1] at hs1'; rw [e2] at hs2'
      have hq : (((17 * LN4 : ℚ)) : ℝ) = 17 * (((lcpN4 - 5 * sgN4 : ℚ)) : ℝ) := by unfold LN4; push_cast; ring
      by_cases hm : s ≤ 915 / 1000
      · have := Fc_le cfC cfC_ok (9 / 10) (915 / 1000) (by norm_num) (by norm_num) s (by push_cast; exact hs1') (by push_cast; exact hm)
        have h2 : ((Fup cfC (9 / 10) (915 / 1000) : ℚ) : ℝ) < (((17 * LN4 : ℚ)) : ℝ) := by exact_mod_cast boxN4a
        linarith
      · push Not at hm
        have := Fc_le cfC cfC_ok (915 / 1000) (93 / 100) (by norm_num) (by norm_num) s (by push_cast; exact hm.le) (by push_cast; exact hs2')
        have h2 : ((Fup cfC (915 / 1000) (93 / 100) : ℚ) : ℝ) < (((17 * LN4 : ℚ)) : ℝ) := by exact_mod_cast boxN4b
        linarith

end CongestionNative

#print axioms CongestionNative.tab_pieceN
#print axioms CongestionNative.ceiling_native_N96
