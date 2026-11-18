import Nov15.CongestionNative
import Nov15.CongestionC56Sig0
import Nov15.CongestionC56Sig1
import Nov15.CongestionC56Sig2
import Nov15.CongestionC56Pt0
import Nov15.CongestionC56Pt1
import Nov15.CongestionC56Pt2
import Nov15.CongestionC56D
import Nov15.CongestionC56Unit

/-!
CONGESTION-C56: `ceiling_native` with the junk count hypothesis `hJ : 4166 ≤ |J|`, the certified class floor of the C = 56 flag model.
Conclusion: F(1 - t, invoice (caller 6 7) n 17) < 0 for t in [tK0, 1], tK0 = .0122445, i.e. kappa <= .0122445 (own56, m <= 5)
for every word satisfying the hypotheses.
* [tC0, 1]: `ceiling_native` itself (its hypotheses are restrictions of the ones here; its unit table is kernel-proved, `unit_of_Fup`).
* [tK0, tC0]: three pieces (CongestionC56{Defs,Sig*,Pt*,D,Unit}): kernel sigma certificates, kernel F_base point enclosures,
  kernel derivative bound of F_base on [.93, 1 - tK0], kernel unit lower bounds, norm_num table arithmetic with N = 4166.
Hypotheses that are data (same status as in ceiling_native): hcong*, hdist (on s in [.9, 1 - tK0]), hspMono/hcstMono (on [tK0, 1/10]),
hspTab/hcstTab (+ the three spF / cst endpoint brackets of this piece set).  hunitTab is kernel-proved.

THE JUNK COUNT `hJ : 4166 ≤ J.card` IS A HYPOTHESIS, justified outside Lean.  It is the Lagrangian certificate for the model class below
(frozen multipliers, per-chain exact flag DP over Q, two independent checkers; all 8 configs >= 4165.98, J integer).  Lean does not model
the flag class; the class is the scope of the hypothesis, and it is NOT proved in Lean:
 (a) the 8 chain pairs (z_k, z'_k) of the rank-8 Y-plane rows with C = 56 are one of 8 valid configurations (rank-8 flats; numerical
     rigidity of the row factorisation, quoted);
 (b) each chain is a monotone chain of frames <z'_k> = F_0 < ... < z_k^perp with ANY step sizes (multi-dimensional steps are dominated by a
     complete refinement: proved in the audit, so not a hypothesis);
 (c) each symbol is gathered in ONE piece per chain and each Y_t is read in ONE piece per chain (no split gathers, no split reads);
 (d) plane separation (no second owned plane carries plane-1 X content).
The junk count `hJ`, `hcong` and `hdist` all refer to the same `J`; Lean does not tie `J` to any word. The frontier words are not in the
class (rank 11, multi-dimensional lifetimes). -/
namespace CongestionNative
open NumCertK JointCeiling CallerCost CongestionI3 CongestionI3Dual Finset

/-- kernel unit lower bound: `lo <= 9^(1-t) - 8^(1-t)` from a `Fup` enclosure of `8^s - 9^s`. -/
theorem unit_of_Fup (t lo : ℚ) (h0 : 0 ≤ 1 - t) (h1 : 1 - t ≤ 1) (h : Fup unitCF (1 - t) (1 - t) < -lo) :
    (lo : ℝ) ≤ (9 : ℝ) ^ (1 - (t : ℝ)) - (8 : ℝ) ^ (1 - (t : ℝ)) := by
  have hF := Fc_le unitCF unitCF_ok (1 - t) (1 - t) h0 h1 (((1 - t : ℚ)) : ℝ) (le_refl _) (le_refl _)
  have h2 : ((Fup unitCF (1 - t) (1 - t) : ℚ) : ℝ) < ((-lo : ℚ) : ℝ) := by exact_mod_cast h
  have hc : (((1 - t : ℚ)) : ℝ) = 1 - (t : ℝ) := by push_cast; ring
  rw [hc] at hF
  have e : Fc unitCF (1 - (t : ℝ)) = (8 : ℝ) ^ (1 - (t : ℝ)) - (9 : ℝ) ^ (1 - (t : ℝ)) := by
    simp [Fc, unitCF]; ring
  rw [e] at hF
  push_cast at h2
  linarith

/-- two-sided I3 with a general junk count `Nn` in place of 1936. -/
theorem E_lower_cap_omN {ι : Type*} [DecidableEq ι] (R : Finset ι) (n : ι → ℕ) (d : ι → ℕ → ℕ) (J : Finset (ℕ × ℕ)) (dist : ℕ × ℕ → ℝ)
    (E s cap corr ell σ Om : ℝ) (m Nn : ℕ)
    (hmono : ∀ r ∈ R, ∀ i < n r, d r i ≤ d r (i + 1)) (hd9 : ∀ r ∈ R, d r (n r) ≤ 9)
    (hm : (R.filter fun r => Mixed d n r).card ≤ m) (hσ0 : 0 ≤ σ)
    (hσ : ∀ a b : ℕ, 1 ≤ a → a ≤ b → b ≤ 8 → c2 (gs s) (a : ℝ) (b : ℝ) ≤ σ)
    (hcong : ∑ p ∈ J, min (dist p) cap - corr ≤ ∑ r ∈ R, ∑ i ∈ range (n r), c2 (gs s) (lev d r i) (lev d r (i + 1)) + Om)
    (hEex : ∑ r ∈ R, ex (gs s) (lev d r) (n r) ≤ E) (hdist : ∀ p ∈ J, ell ≤ min (dist p) cap) (hJ : Nn ≤ J.card) (hell : 0 ≤ ell) :
    (Nn : ℝ) * ell - corr - m * σ ≤ E + Om := by
  have h1 := sum_all_c2_le (gs s) (gs_zero s) R n d hmono hd9 m hm σ hσ0 hσ
  have h2 := Finset.card_nsmul_le_sum J (fun p => min (dist p) cap) ell hdist
  rw [nsmul_eq_mul] at h2
  have hj : (Nn : ℝ) ≤ J.card := by exact_mod_cast hJ
  have h3 : (Nn : ℝ) * ell ≤ (J.card : ℝ) * ell := mul_le_mul_of_nonneg_right hj hell
  linarith

/-- one t-piece `[a, b]` with N = 4166 (copy of `tab_piece`, domain [tK0, 1/10]). -/
theorem tab_pieceK (spF cstF : ℝ → ℝ) (a b : ℚ) (lcp cH spLo unLo : ℚ) (hlcp : 0 ≤ lcp) (hcH : 0 ≤ cH) (ha0 : tK0 ≤ a) (hab : a ≤ b) (hb : b ≤ 1 / 10)
    (hmS : MonotoneOn spF (Set.Icc ((tK0 : ℚ) : ℝ) (1 / 10))) (hmC : MonotoneOn cstF (Set.Icc ((tK0 : ℚ) : ℝ) (1 / 10)))
    (hsp : (spLo : ℝ) ≤ spF (a : ℝ)) (hcs : cstF (b : ℝ) ≤ cH)
    (hun : (unLo : ℝ) ≤ (9 : ℝ) ^ (1 - (b : ℝ)) - (8 : ℝ) ^ (1 - (b : ℝ)))
    (hn1 : lcp + 8 * cH ≤ 4166 * spLo) (hn2 : lcp + 8 * cH ≤ 4166 * (unLo / 48)) :
    ∀ s : ℝ, ((1 - b : ℚ) : ℝ) ≤ s → s ≤ ((1 - a : ℚ) : ℝ) → (lcp : ℝ) ≤ 4166 * ellC spF s - corrC cstF s ∧ 0 ≤ ellC spF s := by
  intro s h1 h2
  push_cast at h1 h2
  have ha' : ((tK0 : ℚ) : ℝ) ≤ a := by exact_mod_cast ha0
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
  have hn1' : (lcp : ℝ) + 8 * cH ≤ 4166 * spLo := by exact_mod_cast hn1
  have hn2' : (lcp : ℝ) + 8 * cH ≤ 4166 * ((unLo : ℝ) / 48) := by exact_mod_cast hn2
  have hl0 : (0 : ℝ) ≤ lcp := by exact_mod_cast hlcp
  have hc0 : (0 : ℝ) ≤ cH := by exact_mod_cast hcH
  rcases le_total (spLo : ℝ) ((unLo : ℝ) / 48) with hh | hh
  · rw [min_eq_left hh] at hell; exact ⟨by linarith, by linarith⟩
  · rw [min_eq_right hh] at hell; exact ⟨by linarith, by linarith⟩

theorem cfC_monoOnK (s s' : ℝ) (h1 : (93 / 100 : ℝ) ≤ s) (hss : s ≤ s') (h2 : s' ≤ ((1 - tK0 : ℚ) : ℝ)) : Fc cfC s ≤ Fc cfC s' :=
  Fc_monoOn cfC cfC_ok (93 / 100) (1 - tK0) (by norm_num) (by unfold tK0; norm_num) cfC_dK s s'
    (by rw [show (((93 / 100 : ℚ)) : ℝ) = 93 / 100 by norm_num]; exact h1) hss h2

theorem hFbK_of (a b L : ℚ) (hb93 : 93 / 100 ≤ 1 - b) (hab : a ≤ b) (haJ : tK0 ≤ a)
    (hpt : Fup cfC (1 - a) (1 - a) < 17 * L) :
    ∀ s : ℝ, ((1 - b : ℚ) : ℝ) ≤ s → s ≤ ((1 - a : ℚ) : ℝ) → Fc cfC s < 17 * (L : ℝ) := by
  intro s h1 h2
  have hb : (((93 / 100 : ℚ)) : ℝ) ≤ s := le_trans (by exact_mod_cast hb93) h1
  have hb' : (93 / 100 : ℝ) ≤ s := by rwa [show (((93 / 100 : ℚ)) : ℝ) = 93 / 100 by norm_num] at hb
  have haA : (1 - a : ℚ) ≤ 1 - tK0 := by linarith
  have hm := cfC_monoOnK s ((1 - a : ℚ) : ℝ) hb' h2 (by exact_mod_cast haA)
  have hJ0 : (0 : ℚ) ≤ tK0 := by unfold tK0; norm_num
  exact lt_of_le_of_lt hm (pt_of_Fup cfC cfC_ok (1 - a) L (by linarith) (by linarith) hpt)

/-- **C = 56 class ceiling at the certified junk floor.**  Same statement as `ceiling_native` with `hJ : 4166 ≤ |J|`; hcong*/hdist on
s in [.9, 1 - tK0]; monotonicity on [tK0, 1/10]; three more endpoint brackets of spF / cst.  Conclusion on t in [tK0, 1]: kappa <= .0122445. -/
theorem ceiling_c56 {ι : Type*} [DecidableEq ι]
    (R : Finset ι) (nR : ι → ℕ) (dR : ι → ℕ → ℕ)
    (hmono : ∀ r ∈ R, ∀ i < nR r, dR r i ≤ dR r (i + 1)) (hd9 : ∀ r ∈ R, dR r (nR r) ≤ 9)
    (hmix : (R.filter fun r => Mixed dR nR r).card ≤ 5)
    (n : Inv) (ks : List ℕ) (mr st : ℕ) (E : ℝ → ℝ) (J : Finset (ℕ × ℕ)) (distF : ℝ → ℕ × ℕ → ℝ) (spF cstF : ℝ → ℝ)
    (hk : ∀ k ∈ ks, 1 ≤ k ∧ k ≤ 9) (hmass : 56 ≤ ks.sum) (hmd : 8 ≤ ks.length) (hmr : 8 ≤ mr)
    (hF : ∀ s, 0 ≤ s → s ≤ 1 → Finv s n ≤ -400 * (8 : ℝ) ^ s - dprice ks s - mr - E s)
    (hY : 104 ≤ st + (ks.length + mr))
    (hst : ∀ s, 0 ≤ s → s ≤ 1 → (2 - (2 : ℝ) ^ s) * st ≤ E s)
    (hEex : ∀ s, 0 ≤ s → s ≤ 1 → ∑ r ∈ R, ex (gs s) (lev dR r) (nR r) ≤ E s)
    (hcong : ∀ s, 9 / 10 ≤ s → s ≤ 1 - ((tK0 : ℚ) : ℝ) →
      ∑ p ∈ J, min (distF s p) (capC s) - corrC cstF s ≤
        ∑ r ∈ R, ∑ i ∈ range (nR r), c2 (gs s) (lev dR r i) (lev dR r (i + 1)) + Omega ks mr s)
    (hdist : ∀ s, 9 / 10 ≤ s → s ≤ 1 - ((tK0 : ℚ) : ℝ) → ∀ p ∈ J, spF (1 - s) ≤ distF s p)
    (hJ : 4166 ≤ J.card)
    (hspMono : MonotoneOn spF (Set.Icc ((tK0 : ℚ) : ℝ) (1 / 10)))
    (hcstMono : MonotoneOn cstF (Set.Icc ((tK0 : ℚ) : ℝ) (1 / 10)))
    (hspTab : ((spFloC0 : ℚ) : ℝ) ≤ spF ((tC0 : ℚ) : ℝ) ∧ ((spFloC1 : ℚ) : ℝ) ≤ spF ((tC1 : ℚ) : ℝ) ∧
      ((spFloC2 : ℚ) : ℝ) ≤ spF ((tC2 : ℚ) : ℝ) ∧ ((spFloC3 : ℚ) : ℝ) ≤ spF ((tC3 : ℚ) : ℝ))
    (hcstTab : cstF ((tC1 : ℚ) : ℝ) ≤ ((cHC0 : ℚ) : ℝ) ∧ cstF ((tC2 : ℚ) : ℝ) ≤ ((cHC1 : ℚ) : ℝ) ∧
      cstF ((tC3 : ℚ) : ℝ) ≤ ((cHC2 : ℚ) : ℝ) ∧ cstF (1 / 10) ≤ ((cHC3 : ℚ) : ℝ))
    (hspTabK : ((spFloK0 : ℚ) : ℝ) ≤ spF ((tK0 : ℚ) : ℝ) ∧ ((spFloK1 : ℚ) : ℝ) ≤ spF ((tK1 : ℚ) : ℝ) ∧
      ((spFloK2 : ℚ) : ℝ) ≤ spF ((tK2 : ℚ) : ℝ))
    (hcstTabK : cstF ((tK1 : ℚ) : ℝ) ≤ ((cHK0 : ℚ) : ℝ) ∧ cstF ((tK2 : ℚ) : ℝ) ≤ ((cHK1 : ℚ) : ℝ) ∧
      cstF ((tC0 : ℚ) : ℝ) ≤ ((cHK2 : ℚ) : ℝ)) :
    ∀ t : ℝ, ((tK0 : ℚ) : ℝ) ≤ t → t ≤ 1 → Finv (1 - t) (invoice (caller 6 7) n 17) < 0 := by
  have qJC : tK0 ≤ tC0 := by unfold tK0 tC0; norm_num
  have eJC : ((tK0 : ℚ) : ℝ) ≤ ((tC0 : ℚ) : ℝ) := by exact_mod_cast qJC
  intro t ht ht1
  rcases le_or_gt ((tC0 : ℚ) : ℝ) t with hC | hC
  · -- [tC0, 1]: the shipped `ceiling_native`
    have u0 := unit_of_Fup tC1 unitLoC0 (by unfold tC1; norm_num) (by unfold tC1; norm_num) unitC0'
    have u1 := unit_of_Fup tC2 unitLoC1 (by unfold tC2; norm_num) (by unfold tC2; norm_num) unitC1'
    have u2 := unit_of_Fup tC3 unitLoC2 (by unfold tC3; norm_num) (by unfold tC3; norm_num) unitC2'
    have u3 := unit_of_Fup (1 / 10) unitLoC3 (by norm_num) (by norm_num) unitC3'
    have h110 : (((1 / 10 : ℚ)) : ℝ) = 1 / 10 := by norm_num
    rw [h110] at u3
    exact ceiling_native R nR dR hmono hd9 hmix n ks mr st E J distF spF cstF hk hmass hmd hmr hF hY hst hEex
      (fun s h1 h2 => hcong s h1 (by linarith)) (fun s h1 h2 => hdist s h1 (by linarith)) (le_trans (by norm_num) hJ)
      (hspMono.mono (Set.Icc_subset_Icc eJC (le_refl _))) (hcstMono.mono (Set.Icc_subset_Icc eJC (le_refl _)))
      hspTab hcstTab ⟨u0, u1, u2, u3⟩ t hC ht1
  · -- [tK0, tC0]: three new pieces with N = 4166
    have piece : ∀ (a b lcp σ : ℚ), sigOK (1 - b) (1 - a) σ = true → 0 ≤ σ → tK0 ≤ a → a ≤ b → b ≤ tC0 → 0 ≤ lcp →
        (∀ s : ℝ, ((1 - b : ℚ) : ℝ) ≤ s → s ≤ ((1 - a : ℚ) : ℝ) → (lcp : ℝ) ≤ 4166 * ellC spF s - corrC cstF s ∧ 0 ≤ ellC spF s) →
        (∀ s : ℝ, ((1 - b : ℚ) : ℝ) ≤ s → s ≤ ((1 - a : ℚ) : ℝ) → Fc cfC s < 17 * (((lcp - 5 * σ : ℚ)) : ℝ)) →
        ∀ t : ℝ, (a : ℝ) ≤ t → t ≤ (b : ℝ) → Finv (1 - t) (invoice (caller 6 7) n 17) < 0 := by
      intro a b lcp σ hσc hσ0 ha0 hab hb hl0 hLcp hFb t h1 h2
      have ha0q : (0 : ℚ) ≤ a := le_trans (by unfold tK0; norm_num) ha0
      have ha0' : ((tK0 : ℚ) : ℝ) ≤ a := by exact_mod_cast ha0
      have hbC : (b : ℝ) ≤ ((tC0 : ℚ) : ℝ) := by exact_mod_cast hb
      have hC1 : ((tC0 : ℚ) : ℝ) ≤ 1 / 10 := by
        have : tC0 ≤ 1 / 10 := by unfold tC0; norm_num
        have := (Rat.cast_le (K := ℝ)).mpr this
        push_cast at this; exact this
      have hb' : (b : ℝ) ≤ 1 / 10 := le_trans hbC hC1
      have hA0 : (0 : ℝ) ≤ a := by exact_mod_cast ha0q
      have hs0 : 0 ≤ 1 - t := by linarith
      have hs1 : 1 - t ≤ 1 := by linarith
      have hbq : b ≤ 1 / 10 := le_trans hb (by unfold tC0; norm_num)
      have hσ : ∀ a' b' : ℕ, 1 ≤ a' → a' ≤ b' → b' ≤ 8 → c2 (gs (1 - t)) (a' : ℝ) (b' : ℝ) ≤ (σ : ℝ) := by
        intro a' b' h1' h2' h3'
        exact sig_of_ok (1 - b) (1 - a) σ hσc (by linarith) (by linarith) hσ0 (1 - t)
          (by push_cast; linarith) (by push_cast; linarith) a' b' h1' h2' h3'
      have hLcp' := hLcp (1 - t) (by push_cast; linarith) (by push_cast; linarith)
      have hslo : (9 / 10 : ℝ) ≤ 1 - t := by linarith
      have hshi : 1 - t ≤ 1 - ((tK0 : ℚ) : ℝ) := by linarith
      have hell : 0 ≤ ellC spF (1 - t) := hLcp'.2
      have hE := E_lower_cap_omN R nR dR J (distF (1 - t)) (E (1 - t)) (1 - t) (capC (1 - t)) (corrC cstF (1 - t)) (ellC spF (1 - t))
        (σ : ℝ) (Omega ks mr (1 - t)) 5 4166 hmono hd9 hmix (by exact_mod_cast hσ0) hσ (hcong (1 - t) hslo hshi) (hEex _ hs0 hs1)
        (fun p hp => le_min (le_trans (min_le_left _ _) (hdist (1 - t) hslo hshi p hp)) (min_le_right _ _)) hJ hell
      have hE' : (((lcp - 5 * σ : ℚ)) : ℝ) ≤ E (1 - t) + Omega ks mr (1 - t) := by
        push_cast; push_cast at hE; linarith [hLcp'.1]
      exact branchC_om n ks mr (E (1 - t)) _ (1 - t) (hF _ hs0 hs1) hE'
        (hFb (1 - t) (by push_cast; linarith) (by push_cast; linarith))
    obtain ⟨sp0, sp1, sp2⟩ := hspTabK
    obtain ⟨cs0, cs1, cs2⟩ := hcstTabK
    have q01 : tK0 ≤ tK1 := by unfold tK0 tK1; norm_num
    have q12 : tK1 ≤ tK2 := by unfold tK1 tK2; norm_num
    have q2C : tK2 ≤ tC0 := by unfold tK2 tC0; norm_num
    have qC : tC0 ≤ 1 / 10 := by unfold tC0; norm_num
    have un0 := unit_of_Fup tK1 unitLoK0 (by unfold tK1; norm_num) (by unfold tK1; norm_num) unitK0
    have un1 := unit_of_Fup tK2 unitLoK1 (by unfold tK2; norm_num) (by unfold tK2; norm_num) unitK1
    have un2 := unit_of_Fup tC0 unitLoK2 (by unfold tC0; norm_num) (by unfold tC0; norm_num) unitK2
    have l0 : (0 : ℚ) ≤ lcpK0 := by unfold lcpK0; norm_num
    have l1 : (0 : ℚ) ≤ lcpK1 := by unfold lcpK1; norm_num
    have l2 : (0 : ℚ) ≤ lcpK2 := by unfold lcpK2; norm_num
    have c0 : (0 : ℚ) ≤ cHK0 := by unfold cHK0; norm_num
    have c1 : (0 : ℚ) ≤ cHK1 := by unfold cHK1; norm_num
    have c2' : (0 : ℚ) ≤ cHK2 := by unfold cHK2; norm_num
    have e1 : ((tK1 : ℚ) : ℝ) ≤ ((tK2 : ℚ) : ℝ) := by exact_mod_cast q12
    by_cases k1 : t ≤ ((tK1 : ℚ) : ℝ)
    · exact piece tK0 tK1 lcpK0 sgK0 sigK0 (by unfold sgK0; norm_num) (le_refl _) q01 (le_trans q12 q2C) l0
        (tab_pieceK spF cstF tK0 tK1 lcpK0 cHK0 spFloK0 unitLoK0 l0 c0 (le_refl _) q01 (le_trans (le_trans q12 q2C) qC)
          hspMono hcstMono sp0 cs0 un0 tabK0.1 tabK0.2)
        (hFbK_of tK0 tK1 LK0 (by unfold tK1; norm_num) q01 (le_refl _) ptK0) t ht k1
    by_cases k2 : t ≤ ((tK2 : ℚ) : ℝ)
    · exact piece tK1 tK2 lcpK1 sgK1 sigK1 (by unfold sgK1; norm_num) q01 q12 q2C l1
        (tab_pieceK spF cstF tK1 tK2 lcpK1 cHK1 spFloK1 unitLoK1 l1 c1 q01 q12 (le_trans q2C qC)
          hspMono hcstMono sp1 cs1 un1 tabK1.1 tabK1.2)
        (hFbK_of tK1 tK2 LK1 (by unfold tK2; norm_num) q12 q01 ptK1) t (by push Not at k1; exact k1.le) k2
    · exact piece tK2 tC0 lcpK2 sgK2 sigK2 (by unfold sgK2; norm_num) (le_trans q01 q12) q2C (le_refl _) l2
        (tab_pieceK spF cstF tK2 tC0 lcpK2 cHK2 spFloK2 unitLoK2 l2 c2' (le_trans q01 q12) q2C qC
          hspMono hcstMono sp2 cs2 un2 tabK2.1 tabK2.2)
        (hFbK_of tK2 tC0 LK2 (by unfold tC0; norm_num) q2C (le_trans q01 q12) ptK2) t (by push Not at k2; exact k2.le) hC.le

end CongestionNative

#print axioms CongestionNative.unit_of_Fup
#print axioms CongestionNative.E_lower_cap_omN
#print axioms CongestionNative.tab_pieceK
#print axioms CongestionNative.ceiling_c56
