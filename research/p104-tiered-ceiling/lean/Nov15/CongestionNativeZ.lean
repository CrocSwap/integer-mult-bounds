import Nov15.CongestionNativeJ
import Nov15.CongestionNativeZDefs
import Nov15.CongestionNativeZSig0
import Nov15.CongestionNativeZSig1
import Nov15.CongestionNativeZSig2
import Nov15.CongestionNativeZSig3
import Nov15.CongestionNativeZSig4
import Nov15.CongestionNativeZPt
import Nov15.CongestionNativeZUnit

/-!
CONGESTION-NATIVE-Z0: `ceiling_native` / `ceiling_native_J` with the junk count hypothesis DROPPED (`hJ : 0 <= |J|` is trivial): the J-free ceiling: no junk-count assumption and no upper bound on owned mass (it keeps `hmass : 56 <= ks.sum`, `hk`, `hmd`, `hmr`, `hY` and the rest of class K).  Conclusion: F(1 - t, invoice (caller 6 7) n 17) < 0 for t in [tZ0, 1],
tZ0 = .0151869, i.e. kappa <= .0151869 (own56, m <= 5) for every word satisfying the hypotheses (see JunkLawA.md).
Pieces: [tZ0, tZ1, tZ2, tZ3, .07, .1] (4 point-form pieces with F_base monotone on [.93, 1 - tZ0], one box-form piece on s in [.9, .93]), then t >= .1 as in `ceiling_native`.
Hypotheses are those of `ceiling_native_J` with the hJ line removed and the new endpoint brackets (hspTabN, hcstTabN); all unit brackets, sigma certificates, F_base enclosures are kernel.
-/
namespace CongestionNative
open NumCertK JointCeiling CallerCost CongestionI3 CongestionI3Dual Finset

/-- one t-piece `[a, b]` with N = 0; `lcp` may be negative (only `0 <= spLo`, `0 <= unLo` are needed for `0 <= ell`). -/
theorem tab_pieceZ (spF cstF : ℝ → ℝ) (a b : ℚ) (lcp cH spLo unLo : ℚ) (hcH : 0 ≤ cH) (hsp0 : 0 ≤ spLo) (hun0 : 0 ≤ unLo)
    (ha0 : tZ0 ≤ a) (hab : a ≤ b) (hb : b ≤ 1 / 10)
    (hmS : MonotoneOn spF (Set.Icc ((tZ0 : ℚ) : ℝ) (1 / 10))) (hmC : MonotoneOn cstF (Set.Icc ((tZ0 : ℚ) : ℝ) (1 / 10)))
    (hsp : (spLo : ℝ) ≤ spF (a : ℝ)) (hcs : cstF (b : ℝ) ≤ cH)
    (hun : (unLo : ℝ) ≤ (9 : ℝ) ^ (1 - (b : ℝ)) - (8 : ℝ) ^ (1 - (b : ℝ)))
    (hn1 : lcp + 8 * cH ≤ 0 * spLo) (hn2 : lcp + 8 * cH ≤ 0 * (unLo / 48)) :
    ∀ s : ℝ, ((1 - b : ℚ) : ℝ) ≤ s → s ≤ ((1 - a : ℚ) : ℝ) → (lcp : ℝ) ≤ 0 * ellC spF s - corrC cstF s ∧ 0 ≤ ellC spF s := by
  intro s h1 h2
  push_cast at h1 h2
  have ha' : ((tZ0 : ℚ) : ℝ) ≤ a := by exact_mod_cast ha0
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
  have hn1' : (lcp : ℝ) + 8 * cH ≤ 0 * spLo := by exact_mod_cast hn1
  have hn2' : (lcp : ℝ) + 8 * cH ≤ 0 * ((unLo : ℝ) / 48) := by exact_mod_cast hn2
  have hs0' : (0 : ℝ) ≤ spLo := by exact_mod_cast hsp0
  have hu0' : (0 : ℝ) ≤ (unLo : ℝ) / 48 := by
    have h : (0 : ℝ) ≤ unLo := by exact_mod_cast hun0
    linarith
  have hc0 : (0 : ℝ) ≤ cH := by exact_mod_cast hcH
  have hmin0 : (0 : ℝ) ≤ min (spLo : ℝ) ((unLo : ℝ) / 48) := le_min hs0' hu0'
  rcases le_total (spLo : ℝ) ((unLo : ℝ) / 48) with hh | hh
  · rw [min_eq_left hh] at hell hmin0; exact ⟨by linarith, by linarith⟩
  · rw [min_eq_right hh] at hell hmin0; exact ⟨by linarith, by linarith⟩

/-- **J-free ceiling (N = 0).**  Same statement as `ceiling_native_J` with no junk-count hypothesis (N = 0), hcong*/hdist on s in [.9, 1 - tZ0], monotonicity on [tZ0, 1/10], five spF and five cst endpoint brackets.
Conclusion on t in [tZ0, 1]: kappa <= .0151869. -/
theorem ceiling_native_Z0 {ι : Type*} [DecidableEq ι]
    (R : Finset ι) (nR : ι → ℕ) (dR : ι → ℕ → ℕ)
    (hmono : ∀ r ∈ R, ∀ i < nR r, dR r i ≤ dR r (i + 1)) (hd9 : ∀ r ∈ R, dR r (nR r) ≤ 9)
    (hmix : (R.filter fun r => Mixed dR nR r).card ≤ 5)
    (n : Inv) (ks : List ℕ) (mr st : ℕ) (E : ℝ → ℝ) (J : Finset (ℕ × ℕ)) (distF : ℝ → ℕ × ℕ → ℝ) (spF cstF : ℝ → ℝ)
    (hk : ∀ k ∈ ks, 1 ≤ k ∧ k ≤ 9) (hmass : 56 ≤ ks.sum) (hmd : 8 ≤ ks.length) (hmr : 8 ≤ mr)
    (hF : ∀ s, 0 ≤ s → s ≤ 1 → Finv s n ≤ -400 * (8 : ℝ) ^ s - dprice ks s - mr - E s)
    (hY : 104 ≤ st + (ks.length + mr))
    (hst : ∀ s, 0 ≤ s → s ≤ 1 → (2 - (2 : ℝ) ^ s) * st ≤ E s)
    (hEex : ∀ s, 0 ≤ s → s ≤ 1 → ∑ r ∈ R, ex (gs s) (lev dR r) (nR r) ≤ E s)
    (hcong : ∀ s, 9 / 10 ≤ s → s ≤ 1 - ((tZ0 : ℚ) : ℝ) →
      ∑ p ∈ J, min (distF s p) (capC s) - corrC cstF s ≤
        ∑ r ∈ R, ∑ i ∈ range (nR r), c2 (gs s) (lev dR r i) (lev dR r (i + 1)) + Omega ks mr s)
    (hdist : ∀ s, 9 / 10 ≤ s → s ≤ 1 - ((tZ0 : ℚ) : ℝ) → ∀ p ∈ J, spF (1 - s) ≤ distF s p)
    (hspMono : MonotoneOn spF (Set.Icc ((tZ0 : ℚ) : ℝ) (1 / 10)))
    (hcstMono : MonotoneOn cstF (Set.Icc ((tZ0 : ℚ) : ℝ) (1 / 10)))
    (hspTabN : ((spFloZ0 : ℚ) : ℝ) ≤ spF ((tZ0 : ℚ) : ℝ) ∧ ((spFloZ1 : ℚ) : ℝ) ≤ spF ((tZ1 : ℚ) : ℝ) ∧
      ((spFloZ2 : ℚ) : ℝ) ≤ spF ((tZ2 : ℚ) : ℝ) ∧ ((spFloZ3 : ℚ) : ℝ) ≤ spF ((tZ3 : ℚ) : ℝ) ∧
      ((spFloZ4 : ℚ) : ℝ) ≤ spF ((tZ4 : ℚ) : ℝ))
    (hcstTabN : cstF ((tZ1 : ℚ) : ℝ) ≤ ((cHZ0 : ℚ) : ℝ) ∧ cstF ((tZ2 : ℚ) : ℝ) ≤ ((cHZ1 : ℚ) : ℝ) ∧
      cstF ((tZ3 : ℚ) : ℝ) ≤ ((cHZ2 : ℚ) : ℝ) ∧ cstF ((tZ4 : ℚ) : ℝ) ≤ ((cHZ3 : ℚ) : ℝ) ∧
      cstF ((tZ5 : ℚ) : ℝ) ≤ ((cHZ4 : ℚ) : ℝ)) :
    ∀ t : ℝ, ((tZ0 : ℚ) : ℝ) ≤ t → t ≤ 1 → Finv (1 - t) (invoice (caller 6 7) n 17) < 0 := by
  have piece : ∀ (a b lcp σ : ℚ), sigOK (1 - b) (1 - a) σ = true → 0 ≤ σ → tZ0 ≤ a → a ≤ b → b ≤ 1 / 10 →
      (∀ s : ℝ, ((1 - b : ℚ) : ℝ) ≤ s → s ≤ ((1 - a : ℚ) : ℝ) → (lcp : ℝ) ≤ 0 * ellC spF s - corrC cstF s ∧ 0 ≤ ellC spF s) →
      (∀ s : ℝ, ((1 - b : ℚ) : ℝ) ≤ s → s ≤ ((1 - a : ℚ) : ℝ) → Fc cfC s < 17 * (((lcp - 5 * σ : ℚ)) : ℝ)) →
      ∀ t : ℝ, (a : ℝ) ≤ t → t ≤ (b : ℝ) → Finv (1 - t) (invoice (caller 6 7) n 17) < 0 := by
    intro a b lcp σ hσc hσ0 ha0 hab hb hLcp hFb t h1 h2
    have ha0q : (0 : ℚ) ≤ a := le_trans (by unfold tZ0; norm_num) ha0
    have ha0' : ((tZ0 : ℚ) : ℝ) ≤ a := by exact_mod_cast ha0
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
    have hshi : 1 - t ≤ 1 - ((tZ0 : ℚ) : ℝ) := by linarith
    have hell : 0 ≤ ellC spF (1 - t) := hLcp'.2
    have hE := E_lower_cap_omN R nR dR J (distF (1 - t)) (E (1 - t)) (1 - t) (capC (1 - t)) (corrC cstF (1 - t)) (ellC spF (1 - t))
      (σ : ℝ) (Omega ks mr (1 - t)) 5 0 hmono hd9 hmix (by exact_mod_cast hσ0) hσ (hcong (1 - t) hslo hshi) (hEex _ hs0 hs1)
      (fun p hp => le_min (le_trans (min_le_left _ _) (hdist (1 - t) hslo hshi p hp)) (min_le_right _ _)) (Nat.zero_le _) hell
    have hE' : (((lcp - 5 * σ : ℚ)) : ℝ) ≤ E (1 - t) + Omega ks mr (1 - t) := by
      push_cast; push_cast at hE; linarith [hLcp'.1]
    exact branchC_om n ks mr (E (1 - t)) _ (1 - t) (hF _ hs0 hs1) hE'
      (hFb (1 - t) (by push_cast; linarith) (by push_cast; linarith))
  intro t ht ht1
  have ht0 : (0 : ℝ) ≤ ((tZ0 : ℚ) : ℝ) := by unfold tZ0; norm_num
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
    have q01 : tZ0 ≤ tZ1 := by unfold tZ0 tZ1; norm_num
    have q12 : tZ1 ≤ tZ2 := by unfold tZ1 tZ2; norm_num
    have q23 : tZ2 ≤ tZ3 := by unfold tZ2 tZ3; norm_num
    have q34 : tZ3 ≤ tZ4 := by unfold tZ3 tZ4; norm_num
    have q45 : tZ4 ≤ tZ5 := by unfold tZ4 tZ5; norm_num
    have b1 : tZ1 ≤ 1 / 10 := by unfold tZ1; norm_num
    have b2 : tZ2 ≤ 1 / 10 := by unfold tZ2; norm_num
    have b3 : tZ3 ≤ 1 / 10 := by unfold tZ3; norm_num
    have b4 : tZ4 ≤ 1 / 10 := by unfold tZ4; norm_num
    have b5 : tZ5 ≤ 1 / 10 := by unfold tZ5; norm_num
    have q02 := le_trans q01 q12
    have q03 := le_trans q02 q23
    have q04 := le_trans q03 q34
    have un0 := unit_of_Fup tZ1 unitLoZ0 (by unfold tZ1; norm_num) (by unfold tZ1; norm_num) unitZ0
    have un1 := unit_of_Fup tZ2 unitLoZ1 (by unfold tZ2; norm_num) (by unfold tZ2; norm_num) unitZ1
    have un2 := unit_of_Fup tZ3 unitLoZ2 (by unfold tZ3; norm_num) (by unfold tZ3; norm_num) unitZ2
    have un3 := unit_of_Fup tZ4 unitLoZ3 (by unfold tZ4; norm_num) (by unfold tZ4; norm_num) unitZ3
    have un4 := unit_of_Fup tZ5 unitLoZ4 (by unfold tZ5; norm_num) (by unfold tZ5; norm_num) unitZ4
    have zspFloN0 : (0 : ℚ) ≤ spFloZ0 := by unfold spFloZ0; norm_num
    have zspFloN1 : (0 : ℚ) ≤ spFloZ1 := by unfold spFloZ1; norm_num
    have zspFloN2 : (0 : ℚ) ≤ spFloZ2 := by unfold spFloZ2; norm_num
    have zspFloN3 : (0 : ℚ) ≤ spFloZ3 := by unfold spFloZ3; norm_num
    have zspFloN4 : (0 : ℚ) ≤ spFloZ4 := by unfold spFloZ4; norm_num
    have zcHN0 : (0 : ℚ) ≤ cHZ0 := by unfold cHZ0; norm_num
    have zcHN1 : (0 : ℚ) ≤ cHZ1 := by unfold cHZ1; norm_num
    have zcHN2 : (0 : ℚ) ≤ cHZ2 := by unfold cHZ2; norm_num
    have zcHN3 : (0 : ℚ) ≤ cHZ3 := by unfold cHZ3; norm_num
    have zcHN4 : (0 : ℚ) ≤ cHZ4 := by unfold cHZ4; norm_num
    have zunitLoN0 : (0 : ℚ) ≤ unitLoZ0 := by unfold unitLoZ0; norm_num
    have zunitLoN1 : (0 : ℚ) ≤ unitLoZ1 := by unfold unitLoZ1; norm_num
    have zunitLoN2 : (0 : ℚ) ≤ unitLoZ2 := by unfold unitLoZ2; norm_num
    have zunitLoN3 : (0 : ℚ) ≤ unitLoZ3 := by unfold unitLoZ3; norm_num
    have zunitLoN4 : (0 : ℚ) ≤ unitLoZ4 := by unfold unitLoZ4; norm_num
    have hF4 : ∀ (a b L : ℚ), 93 / 100 ≤ 1 - b → a ≤ b → tZ0 ≤ a → Fup cfC (1 - a) (1 - a) < 17 * L →
        ∀ s : ℝ, ((1 - b : ℚ) : ℝ) ≤ s → s ≤ ((1 - a : ℚ) : ℝ) → Fc cfC s < 17 * (L : ℝ) := by
      intro a b L hb93 hab haN hpt
      exact hFbJ_of a b L hb93 hab (le_trans (by unfold tJ0 tZ0; norm_num) haN) hpt
    by_cases k1 : t ≤ ((tZ1 : ℚ) : ℝ)
    · exact piece tZ0 tZ1 lcpZ0 sgZ0 sigZ0 (by unfold sgZ0; norm_num) (le_refl _) q01 b1
        (tab_pieceZ spF cstF tZ0 tZ1 lcpZ0 cHZ0 spFloZ0 unitLoZ0 zcHN0 zspFloN0 zunitLoN0 (le_refl _) q01 b1
          hspMono hcstMono sp0 cs0 un0 tabZ0.1 tabZ0.2)
        (hF4 tZ0 tZ1 LZ0 (by unfold tZ1; norm_num) q01 (le_refl _) ptZ0) t ht k1
    by_cases k2 : t ≤ ((tZ2 : ℚ) : ℝ)
    · exact piece tZ1 tZ2 lcpZ1 sgZ1 sigZ1 (by unfold sgZ1; norm_num) q01 q12 b2
        (tab_pieceZ spF cstF tZ1 tZ2 lcpZ1 cHZ1 spFloZ1 unitLoZ1 zcHN1 zspFloN1 zunitLoN1 q01 q12 b2
          hspMono hcstMono sp1 cs1 un1 tabZ1.1 tabZ1.2)
        (hF4 tZ1 tZ2 LZ1 (by unfold tZ2; norm_num) q12 q01 ptZ1) t (by push Not at k1; exact k1.le) k2
    by_cases k3 : t ≤ ((tZ3 : ℚ) : ℝ)
    · exact piece tZ2 tZ3 lcpZ2 sgZ2 sigZ2 (by unfold sgZ2; norm_num) q02 q23 b3
        (tab_pieceZ spF cstF tZ2 tZ3 lcpZ2 cHZ2 spFloZ2 unitLoZ2 zcHN2 zspFloN2 zunitLoN2 q02 q23 b3
          hspMono hcstMono sp2 cs2 un2 tabZ2.1 tabZ2.2)
        (hF4 tZ2 tZ3 LZ2 (by unfold tZ3; norm_num) q23 q02 ptZ2) t (by push Not at k2; exact k2.le) k3
    by_cases k4 : t ≤ ((tZ4 : ℚ) : ℝ)
    · exact piece tZ3 tZ4 lcpZ3 sgZ3 sigZ3 (by unfold sgZ3; norm_num) q03 q34 b4
        (tab_pieceZ spF cstF tZ3 tZ4 lcpZ3 cHZ3 spFloZ3 unitLoZ3 zcHN3 zspFloN3 zunitLoN3 q03 q34 b4
          hspMono hcstMono sp3 cs3 un3 tabZ3.1 tabZ3.2)
        (hF4 tZ3 tZ4 LZ3 (by unfold tZ4; norm_num) q34 q03 ptZ3) t (by push Not at k3; exact k3.le) k4
    · refine piece tZ4 tZ5 lcpZ4 sgZ4 sigZ4 (by unfold sgZ4; norm_num) q04 q45 b5
        (tab_pieceZ spF cstF tZ4 tZ5 lcpZ4 cHZ4 spFloZ4 unitLoZ4 zcHN4 zspFloN4 zunitLoN4 q04 q45 b5
          hspMono hcstMono sp4 cs4 un4 tabZ4.1 tabZ4.2) ?_ t (by push Not at k4; exact k4.le) (by unfold tZ5; push_cast; exact h10.le)
      intro s hs1' hs2'
      have e1 : (((1 - tZ5 : ℚ)) : ℝ) = 9 / 10 := by unfold tZ5; norm_num
      have e2 : (((1 - tZ4 : ℚ)) : ℝ) = 93 / 100 := by unfold tZ4; norm_num
      rw [e1] at hs1'; rw [e2] at hs2'
      have hq : (((17 * LZ4 : ℚ)) : ℝ) = 17 * (((lcpZ4 - 5 * sgZ4 : ℚ)) : ℝ) := by unfold LZ4; push_cast; ring
      by_cases hm : s ≤ 915 / 1000
      · have := Fc_le cfC cfC_ok (9 / 10) (915 / 1000) (by norm_num) (by norm_num) s (by push_cast; exact hs1') (by push_cast; exact hm)
        have h2 : ((Fup cfC (9 / 10) (915 / 1000) : ℚ) : ℝ) < (((17 * LZ4 : ℚ)) : ℝ) := by exact_mod_cast boxZ4a
        linarith
      · push Not at hm
        have := Fc_le cfC cfC_ok (915 / 1000) (93 / 100) (by norm_num) (by norm_num) s (by push_cast; exact hm.le) (by push_cast; exact hs2')
        have h2 : ((Fup cfC (915 / 1000) (93 / 100) : ℚ) : ℝ) < (((17 * LZ4 : ℚ)) : ℝ) := by exact_mod_cast boxZ4b
        linarith

end CongestionNative

#print axioms CongestionNative.tab_pieceZ
#print axioms CongestionNative.ceiling_native_Z0
