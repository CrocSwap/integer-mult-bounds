import Nov15.CongestionReaderPiece
import Nov15.CTreeDataRDA
import Nov15.CTreeDataRDI
import Nov15.CongestionReaderCertRDDefs
import Nov15.CongestionReaderCertRDWt
import Nov15.CongestionReaderCertRDD
import Nov15.CongestionReaderCertRDDl
import Nov15.CongestionReaderCertRDS0
import Nov15.CongestionReaderCertRDT0
import Nov15.CongestionReaderCertRDU0
import Nov15.CongestionReaderCertRDL0
import Nov15.CongestionReaderCertRDS1
import Nov15.CongestionReaderCertRDT1
import Nov15.CongestionReaderCertRDU1
import Nov15.CongestionReaderCertRDL1
import Nov15.CongestionReaderCertRDS2
import Nov15.CongestionReaderCertRDT2
import Nov15.CongestionReaderCertRDU2
import Nov15.CongestionReaderCertRDL2

/-!
CONGESTION-READER.  Reader-charge refinement of the tree ceiling `ceiling_tree_GD` (#7678, Nov15/CongestionTree.lean):
CG2's per-reader endpoint charge (IN' = sum_t min(H_t + delta, K_t min(c18, capv)) - 15 delta, delta = beta(7) - beta(8)) in the audited shippable form.
`ceiling_reader_GD` (omega <= 0) : F(1 - t, invoice (caller 6 7) n 17) < 0 for t in [a0RD, 1], a0RD = 57631/5000000 = .01152620.  Lean-proved: the register identity
(`resid_V`, `resid_Z`, `tied_rho`: a tied register has residual >= delta), the payer summation (`sum_c2_pay`), the reader line bound
(`tree_lower_reader`), the piece lemma, all numerics (kernel).  NAMED hypotheses (see CongestionReader.md): hTied/hcase/hUc (reader structure =
CG2 sec. 2 + F2 lineage lemma + TL-a/b/c + own56 + X born at dim 1), plus the tree hypotheses of #7678 (CongestionTree.md there).
-/
namespace CongestionNative
open NumCertK JointCeiling CallerCost CongestionI3 CongestionI3Dual Finset

theorem hdelRD : ∀ s : ℝ, ((1 - tJ0 : ℚ) : ℝ) ≤ s → s ≤ ((1 - a0RD : ℚ) : ℝ) →
    (dIRD : ℝ) ≤ CTree.SCr * CongestionReader.deltaF s := by
  intro s h1 h2
  have hok : okR cfDelRD := by
    intro p hp
    simp only [cfDelRD, List.mem_cons, List.not_mem_nil, or_false] at hp
    rcases hp with rfl | rfl | rfl | rfl <;> norm_num
  have hd : 0 < dLo (CTree.negCF cfDelRD) (1 - tJ0) (1 - a0RD) := dlDRD
  have hp : Fup (CTree.negCF cfDelRD) (1 - a0RD) (1 - a0RD) ≤ -((dIRD : ℚ) / 10 ^ 14) := dlPRD
  have := CTree.cf_lower cfDelRD hok (1 - tJ0) (1 - a0RD) (by unfold tJ0; norm_num) (by unfold a0RD; norm_num) hd
    ((dIRD : ℚ) / 10 ^ 14) hp s h1 h2
  have e : Fc cfDelRD s = CongestionReader.deltaF s := by
    simp [Fc, cfDelRD, CongestionReader.deltaF, Real.one_rpow]
    ring
  rw [e] at this
  have hS : CTree.SCr = ((10 ^ 14 : ℚ) : ℝ) := by unfold CTree.SCr; push_cast; ring
  rw [hS]
  push_cast at this ⊢
  have := mul_le_mul_of_nonneg_left this (by norm_num : (0 : ℝ) ≤ 10 ^ 14)
  have h14 : (10 : ℝ) ^ 14 * ((dIRD : ℝ) / 10 ^ 14) = dIRD := by field_simp
  linarith

theorem corr_nonnegRD (cstF : ℝ → ℝ) (hcstLo : ∀ t : ℝ, ((a0RD : ℚ) : ℝ) ≤ t → t ≤ 1 / 10 → 0 ≤ cstF t) :
    ∀ s : ℝ, ((1 - tJ0 : ℚ) : ℝ) ≤ s → s ≤ ((1 - a0RD : ℚ) : ℝ) → 0 ≤ corrC cstF s := by
  intro s h1 h2
  unfold corrC
  have ha : ((a0RD : ℚ) : ℝ) ≤ 1 - s := by push_cast at h2 ⊢; linarith
  have hb : 1 - s ≤ 1 / 10 := by
    have : ((1 - tJ0 : ℚ) : ℝ) = 1 - 118103 / 10 ^ 7 := by unfold tJ0; push_cast; norm_num
    rw [this] at h1; linarith
  have := hcstLo (1 - s) ha hb
  linarith

theorem hFbT_ofRRD (a0 a b L : ℚ) (hd : 0 < dLo cfC (93 / 100) (1 - a0)) (ha00 : 0 ≤ a0) (hb93 : 93 / 100 ≤ 1 - b) (hab : a ≤ b)
    (haJ : a0 ≤ a) (hpt : Fup cfC (1 - a) (1 - a) < 17 * L) :
    ∀ s : ℝ, ((1 - b : ℚ) : ℝ) ≤ s → s ≤ ((1 - a : ℚ) : ℝ) → Fc cfC s < 17 * (L : ℝ) := by
  intro s h1 h2
  have hb : (((93 / 100 : ℚ)) : ℝ) ≤ s := le_trans (by exact_mod_cast hb93) h1
  have haA : (1 - a : ℚ) ≤ 1 - a0 := by linarith
  have hA : ((1 - a : ℚ) : ℝ) ≤ ((1 - a0 : ℚ) : ℝ) := by exact_mod_cast haA
  have hm := Fc_monoOn cfC cfC_ok (93 / 100) (1 - a0) (by norm_num) (by linarith) hd s ((1 - a : ℚ) : ℝ) hb h2 hA
  exact lt_of_le_of_lt hm (pt_of_Fup cfC cfC_ok (1 - a) L (by linarith) (by linarith) hpt)

theorem ceiling_reader_GD
    {ι : Type*} [DecidableEq ι]
    (R : Finset ι) (nR : ι → ℕ) (dR : ι → ℕ → ℕ)
    (hmono : ∀ r ∈ R, ∀ i < nR r, dR r i ≤ dR r (i + 1)) (hd9 : ∀ r ∈ R, dR r (nR r) ≤ 9)
    (hmix : (R.filter fun r => Mixed dR nR r).card ≤ 5)
    (n : Inv) (ks : List ℕ) (mr st : ℕ) (E : ℝ → ℝ) (J : Finset (ℕ × ℕ)) (distF : ℝ → ℕ × ℕ → ℝ) (spF cstF : ℝ → ℝ)
    (hk : ∀ k ∈ ks, 1 ≤ k ∧ k ≤ 9) (hmass : 56 ≤ ks.sum) (hmd : 8 ≤ ks.length) (hmr : 8 ≤ mr)
    (hF : ∀ s, 0 ≤ s → s ≤ 1 → Finv s n ≤ -400 * (8 : ℝ) ^ s - dprice ks s - mr - E s)
    (hY : 104 ≤ st + (ks.length + mr))
    (hst : ∀ s, 0 ≤ s → s ≤ 1 → (2 - (2 : ℝ) ^ s) * st ≤ E s)
    (hEex : ∀ s, 0 ≤ s → s ≤ 1 → ∑ r ∈ R, ex (gs s) (lev dR r) (nR r) ≤ E s)
    (hcong : ∀ s, 9 / 10 ≤ s → s ≤ 1 - ((tJ0 : ℚ) : ℝ) →
      ∑ p ∈ J, min (distF s p) (capC s) - corrC cstF s ≤
        ∑ r ∈ R, ∑ i ∈ range (nR r), c2 (gs s) (lev dR r i) (lev dR r (i + 1)) + Omega ks mr s)
    (hdist : ∀ s, 9 / 10 ≤ s → s ≤ 1 - ((tJ0 : ℚ) : ℝ) → ∀ p ∈ J, spF (1 - s) ≤ distF s p)
    (hJ : 4962 ≤ J.card)
    (hspMono : MonotoneOn spF (Set.Icc ((tJ0 : ℚ) : ℝ) (1 / 10)))
    (hcstMono : MonotoneOn cstF (Set.Icc ((tJ0 : ℚ) : ℝ) (1 / 10)))
    (hspTab : ((spFloC0 : ℚ) : ℝ) ≤ spF ((tC0 : ℚ) : ℝ) ∧ ((spFloC1 : ℚ) : ℝ) ≤ spF ((tC1 : ℚ) : ℝ) ∧
      ((spFloC2 : ℚ) : ℝ) ≤ spF ((tC2 : ℚ) : ℝ) ∧ ((spFloC3 : ℚ) : ℝ) ≤ spF ((tC3 : ℚ) : ℝ))
    (hcstTab : cstF ((tC1 : ℚ) : ℝ) ≤ ((cHC0 : ℚ) : ℝ) ∧ cstF ((tC2 : ℚ) : ℝ) ≤ ((cHC1 : ℚ) : ℝ) ∧
      cstF ((tC3 : ℚ) : ℝ) ≤ ((cHC2 : ℚ) : ℝ) ∧ cstF (1 / 10) ≤ ((cHC3 : ℚ) : ℝ))
    (hspTabJ : ((spFloJ0 : ℚ) : ℝ) ≤ spF ((tJ0 : ℚ) : ℝ) ∧ ((spFloJ1 : ℚ) : ℝ) ≤ spF ((tJ1 : ℚ) : ℝ) ∧
      ((spFloJ2 : ℚ) : ℝ) ≤ spF ((tJ2 : ℚ) : ℝ))
    (hcstTabJ : cstF ((tJ1 : ℚ) : ℝ) ≤ ((cHJ0 : ℚ) : ℝ) ∧ cstF ((tJ2 : ℚ) : ℝ) ≤ ((cHJ1 : ℚ) : ℝ) ∧
      cstF ((tC0 : ℚ) : ℝ) ≤ ((cHJ2 : ℚ) : ℝ))
    {σ ρ μ : Type} [DecidableEq σ] [DecidableEq ρ] [DecidableEq μ]
    (T : CTree.TreeData σ ρ μ CTree.rdaR CTree.rdiR CTree.rdar0 CTree.rdir0 48)
    (hcstLo : ∀ t : ℝ, ((a0RD : ℚ) : ℝ) ≤ t → t ≤ 1 / 10 → 0 ≤ cstF t)
    (hcstMonoT : MonotoneOn cstF (Set.Icc ((a0RD : ℚ) : ℝ) (1 / 10)))
    (hcst0 : cstF ((tRD1 : ℚ) : ℝ) ≤ ((cHRD0 : ℚ) : ℝ))
    (hcst1 : cstF ((tRD2 : ℚ) : ℝ) ≤ ((cHRD1 : ℚ) : ℝ))
    (hcst2 : cstF ((tRD3 : ℚ) : ℝ) ≤ ((cHRD2 : ℚ) : ℝ))
    (hP1 : ∀ s : ℝ, ((1 - tJ0 : ℚ) : ℝ) ≤ s → s ≤ ((1 - a0RD : ℚ) : ℝ) →
      ∑ e ∈ T.Mreg, c2 (gs s) (T.dA e : ℝ) (T.dB e : ℝ) + capC s * ∑ x ∈ T.S, (T.x x : ℝ) ≤
        ∑ r ∈ R, ∑ i ∈ range (nR r), c2 (gs s) (lev dR r i) (lev dR r (i + 1)) + Omega ks mr s)
    (hP2 : ∀ s : ℝ, ((1 - tJ0 : ℚ) : ℝ) ≤ s → s ≤ ((1 - a0RD : ℚ) : ℝ) →
      ∑ e ∈ T.Mun, c2 (gs s) (T.dA e : ℝ) (T.dB e : ℝ) ≤ corrC cstF s)
    (ω : ℕ) (hω : ω ≤ 0) (Q Uo : Finset σ) (hUo : Uo ⊆ T.S) (hUc : Uo.card ≤ 15 + ω) (hQ : Q ⊆ T.S)
    (hcase : ∀ x ∈ T.S, x ∈ Q ∨ T.x x = (T.J.filter fun p => p.1 = x).card ∨ x ∈ Uo)
    (π : σ → ι) (hπR : ∀ t ∈ Q, π t ∈ R) (hπinj : Set.InjOn π Q) (hTied : ∀ t ∈ Q, CongestionReader.Tied nR dR (π t)) :
    ∀ t : ℝ, ((a0RD : ℚ) : ℝ) ≤ t → t ≤ 1 → Finv (1 - t) (invoice (caller 6 7) n 17) < 0 := by
  have eJ : tTJ0RD = tJ0 := rfl
  have hwin := wtRD
  rw [eJ] at hwin
  have hdd := cfC_dRD
  have hdel := hdelRD
  have hUc' : Uo.card ≤ 15 := by omega
  intro t ht ht1
  rcases le_or_gt ((tJ0 : ℚ) : ℝ) t with hC | hC
  · exact ceiling_native_J R nR dR hmono hd9 hmix n ks mr st E J distF spF cstF hk hmass hmd hmr hF hY hst hEex hcong hdist hJ hspMono hcstMono hspTab hcstTab hspTabJ hcstTabJ t hC ht1
  have p0 := CTree.reader_piece R nR dR hmono hd9 hmix n ks mr E cstF hF hEex CTree.rdaW CTree.rdaR CTree.rdiR CTree.rdar0 CTree.rdir0 48 T
    CTree.rda_all (by have h := CTree.rdi_all; rwa [show CTree.rdiW = CTree.rdaW from rfl] at h) (by decide) (by decide) a0RD tRD0 tRD1 lcpRD0 sgRD0 cHRD0 unLoRD0 capIRD0 dIRD lamRD0 gARD0 gBRD0 15
    hwin (by unfold tRD0 a0RD; norm_num) (by unfold tRD0 tRD1; norm_num) (by unfold tRD1 tJ0; norm_num) (by unfold a0RD; norm_num) sigRD0 (by unfold sgRD0; norm_num) lineRD0 numRD0 capRD0
    (unit_of_Fup tRD1 unLoRD0 (by unfold tRD1; norm_num) (by unfold tRD1; norm_num) (by have := unRD0; exact this)) hcst0 hcstMonoT hdel hP1 hP2
    Q Uo hUo hUc' hQ hcase π hπR hπinj hTied
    (hFbT_ofRRD a0RD tRD0 tRD1 _ hdd (by unfold a0RD; norm_num) (by unfold tRD1; norm_num) (by unfold tRD0 tRD1; norm_num) (by unfold tRD0 a0RD; norm_num) ptRD0)
  have p1 := CTree.reader_piece R nR dR hmono hd9 hmix n ks mr E cstF hF hEex CTree.rdaW CTree.rdaR CTree.rdiR CTree.rdar0 CTree.rdir0 48 T
    CTree.rda_all (by have h := CTree.rdi_all; rwa [show CTree.rdiW = CTree.rdaW from rfl] at h) (by decide) (by decide) a0RD tRD1 tRD2 lcpRD1 sgRD1 cHRD1 unLoRD1 capIRD1 dIRD lamRD1 gARD1 gBRD1 15
    hwin (by unfold tRD1 a0RD; norm_num) (by unfold tRD1 tRD2; norm_num) (by unfold tRD2 tJ0; norm_num) (by unfold a0RD; norm_num) sigRD1 (by unfold sgRD1; norm_num) lineRD1 numRD1 capRD1
    (unit_of_Fup tRD2 unLoRD1 (by unfold tRD2; norm_num) (by unfold tRD2; norm_num) (by have := unRD1; exact this)) hcst1 hcstMonoT hdel hP1 hP2
    Q Uo hUo hUc' hQ hcase π hπR hπinj hTied
    (hFbT_ofRRD a0RD tRD1 tRD2 _ hdd (by unfold a0RD; norm_num) (by unfold tRD2; norm_num) (by unfold tRD1 tRD2; norm_num) (by unfold tRD1 a0RD; norm_num) ptRD1)
  have p2 := CTree.reader_piece R nR dR hmono hd9 hmix n ks mr E cstF hF hEex CTree.rdaW CTree.rdaR CTree.rdiR CTree.rdar0 CTree.rdir0 48 T
    CTree.rda_all (by have h := CTree.rdi_all; rwa [show CTree.rdiW = CTree.rdaW from rfl] at h) (by decide) (by decide) a0RD tRD2 tRD3 lcpRD2 sgRD2 cHRD2 unLoRD2 capIRD2 dIRD lamRD2 gARD2 gBRD2 15
    hwin (by unfold tRD2 a0RD; norm_num) (by unfold tRD2 tRD3; norm_num) (tRDend.trans eJ).le (by unfold a0RD; norm_num) sigRD2 (by unfold sgRD2; norm_num) lineRD2 numRD2 capRD2
    (unit_of_Fup tRD3 unLoRD2 (by unfold tRD3; norm_num) (by unfold tRD3; norm_num) (by have := unRD2; exact this)) hcst2 hcstMonoT hdel hP1 hP2
    Q Uo hUo hUc' hQ hcase π hπR hπinj hTied
    (hFbT_ofRRD a0RD tRD2 tRD3 _ hdd (by unfold a0RD; norm_num) (by unfold tRD3; norm_num) (by unfold tRD2 tRD3; norm_num) (by unfold tRD2 a0RD; norm_num) ptRD2)
  rcases le_or_gt t ((tRD1 : ℚ) : ℝ) with h1 | h1
  · exact p0 t (by rw [tRDstart]; exact ht) h1
  rcases le_or_gt t ((tRD2 : ℚ) : ℝ) with h2 | h2
  · exact p1 t h1.le h2
  exact p2 t h2.le (by rw [show tRD3 = tJ0 from tRDend.trans eJ]; exact hC.le)

end CongestionNative

#print axioms CongestionNative.corr_nonnegRD
#print axioms CongestionNative.hdelRD
#print axioms CongestionNative.ceiling_reader_GD
