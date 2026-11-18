import Nov15.CongestionTreePiece
import Nov15.CTreeDataCG
import Nov15.CTreeDataGA
import Nov15.CTreeDataGB
import Nov15.CongestionTreeCertCGDefs
import Nov15.CongestionTreeCertCGWt
import Nov15.CongestionTreeCertCGD
import Nov15.CongestionTreeCertCGS0
import Nov15.CongestionTreeCertCGT0
import Nov15.CongestionTreeCertCGU0
import Nov15.CongestionTreeCertCGL0
import Nov15.CongestionTreeCertCGS1
import Nov15.CongestionTreeCertCGT1
import Nov15.CongestionTreeCertCGU1
import Nov15.CongestionTreeCertCGL1
import Nov15.CongestionTreeCertGDDefs
import Nov15.CongestionTreeCertGDWt
import Nov15.CongestionTreeCertGDD
import Nov15.CongestionTreeCertGDS0
import Nov15.CongestionTreeCertGDT0
import Nov15.CongestionTreeCertGDU0
import Nov15.CongestionTreeCertGDL0
import Nov15.CongestionTreeCertGDS1
import Nov15.CongestionTreeCertGDT1
import Nov15.CongestionTreeCertGDU1
import Nov15.CongestionTreeCertGDL1

/-!
CONGESTION-TREE.  Tree-refined ceilings on top of `ceiling_native_J` (kappa <= .0118103).
* `ceiling_tree_CG` : the node-partition tree bound with the class-min over source counts (|J| >= 4962, <= 48 partners, <= 104 sources).
* `ceiling_tree_GD` : the port-realised refinement (48 of the 104 sources restricted to the realised shape edges `E48`).
Both: F(1 - t, invoice (caller 6 7) n 17) < 0 for t in [a0, 1], a0 = .0117694 (CG), .0116750 (GD).  Lean text: see CongestionTree.md for every hypothesis.
-/
namespace CongestionNative
open NumCertK JointCeiling CallerCost CongestionI3 CongestionI3Dual Finset

theorem hFbT_of (a0 a b L : ℚ) (hd : 0 < dLo cfC (93 / 100) (1 - a0)) (ha00 : 0 ≤ a0) (hb93 : 93 / 100 ≤ 1 - b) (hab : a ≤ b)
    (haJ : a0 ≤ a) (hpt : Fup cfC (1 - a) (1 - a) < 17 * L) :
    ∀ s : ℝ, ((1 - b : ℚ) : ℝ) ≤ s → s ≤ ((1 - a : ℚ) : ℝ) → Fc cfC s < 17 * (L : ℝ) := by
  intro s h1 h2
  have hb : (((93 / 100 : ℚ)) : ℝ) ≤ s := le_trans (by exact_mod_cast hb93) h1
  have haA : (1 - a : ℚ) ≤ 1 - a0 := by linarith
  have hA : ((1 - a : ℚ) : ℝ) ≤ ((1 - a0 : ℚ) : ℝ) := by exact_mod_cast haA
  have hm := Fc_monoOn cfC cfC_ok (93 / 100) (1 - a0) (by norm_num) (by linarith) hd s ((1 - a : ℚ) : ℝ) hb h2 hA
  exact lt_of_le_of_lt hm (pt_of_Fup cfC cfC_ok (1 - a) L (by linarith) (by linarith) hpt)

theorem ceiling_tree_CG
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
    (T : CTree.TreeData σ ρ μ CTree.cgR CTree.cgR CTree.cgr0 CTree.cgr0 0)
    (hcstMonoT : MonotoneOn cstF (Set.Icc ((a0CG : ℚ) : ℝ) (1 / 10)))
    (hcst0 : cstF ((tCG1 : ℚ) : ℝ) ≤ ((cHCG0 : ℚ) : ℝ))
    (hcst1 : cstF ((tCG2 : ℚ) : ℝ) ≤ ((cHCG1 : ℚ) : ℝ))
    (hP1 : ∀ s : ℝ, ((1 - tJ0 : ℚ) : ℝ) ≤ s → s ≤ ((1 - a0CG : ℚ) : ℝ) →
      ∑ e ∈ T.Mreg, c2 (gs s) (T.dA e : ℝ) (T.dB e : ℝ) + capC s * ∑ x ∈ T.S, (T.x x : ℝ) ≤
        ∑ r ∈ R, ∑ i ∈ range (nR r), c2 (gs s) (lev dR r i) (lev dR r (i + 1)) + Omega ks mr s)
    (hP2 : ∀ s : ℝ, ((1 - tJ0 : ℚ) : ℝ) ≤ s → s ≤ ((1 - a0CG : ℚ) : ℝ) →
      ∑ e ∈ T.Mun, c2 (gs s) (T.dA e : ℝ) (T.dB e : ℝ) ≤ corrC cstF s) :
    ∀ t : ℝ, ((a0CG : ℚ) : ℝ) ≤ t → t ≤ 1 → Finv (1 - t) (invoice (caller 6 7) n 17) < 0 := by
  have eJ : tTJ0 = tJ0 := rfl
  have hwin := wtCG
  rw [eJ] at hwin
  have hdd := cfC_dCG
  intro t ht ht1
  rcases le_or_gt ((tJ0 : ℚ) : ℝ) t with hC | hC
  · exact ceiling_native_J R nR dR hmono hd9 hmix n ks mr st E J distF spF cstF hk hmass hmd hmr hF hY hst hEex hcong hdist hJ hspMono hcstMono hspTab hcstTab hspTabJ hcstTabJ t hC ht1
  have p0 := CTree.tree_piece R nR dR hmono hd9 hmix n ks mr E cstF hF hEex CTree.cgW CTree.cgR CTree.cgR CTree.cgr0 CTree.cgr0 0 T
    CTree.cg_all CTree.cg_all (by decide) (by decide) a0CG tCG0 tCG1 lcpCG0 sgCG0 cHCG0 unLoCG0 capICG0 lamCG0 gACG0 gBCG0
    hwin (by unfold tCG0 a0CG; norm_num) (by unfold tCG0 tCG1; norm_num) (by unfold tCG1 tJ0; norm_num) (by unfold a0CG; norm_num) sigCG0 (by unfold sgCG0; norm_num) lineCG0 numCG0 capCG0
    (unit_of_Fup tCG1 unLoCG0 (by unfold tCG1; norm_num) (by unfold tCG1; norm_num) (by have := unCG0; exact this)) hcst0 hcstMonoT hP1 hP2
    (hFbT_of a0CG tCG0 tCG1 _ hdd (by unfold a0CG; norm_num) (by unfold tCG1; norm_num) (by unfold tCG0 tCG1; norm_num) (by unfold tCG0 a0CG; norm_num) ptCG0)
  have p1 := CTree.tree_piece R nR dR hmono hd9 hmix n ks mr E cstF hF hEex CTree.cgW CTree.cgR CTree.cgR CTree.cgr0 CTree.cgr0 0 T
    CTree.cg_all CTree.cg_all (by decide) (by decide) a0CG tCG1 tCG2 lcpCG1 sgCG1 cHCG1 unLoCG1 capICG1 lamCG1 gACG1 gBCG1
    hwin (by unfold tCG1 a0CG; norm_num) (by unfold tCG1 tCG2; norm_num) (tCGend.trans eJ).le (by unfold a0CG; norm_num) sigCG1 (by unfold sgCG1; norm_num) lineCG1 numCG1 capCG1
    (unit_of_Fup tCG2 unLoCG1 (by unfold tCG2; norm_num) (by unfold tCG2; norm_num) (by have := unCG1; exact this)) hcst1 hcstMonoT hP1 hP2
    (hFbT_of a0CG tCG1 tCG2 _ hdd (by unfold a0CG; norm_num) (by unfold tCG2; norm_num) (by unfold tCG1 tCG2; norm_num) (by unfold tCG1 a0CG; norm_num) ptCG1)
  rcases le_or_gt t ((tCG1 : ℚ) : ℝ) with h1 | h1
  · exact p0 t (by rw [tCGstart]; exact ht) h1
  · exact p1 t h1.le (by rw [show tCG2 = tJ0 from tCGend.trans eJ]; exact hC.le)

theorem ceiling_tree_GD
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
    (T : CTree.TreeData σ ρ μ CTree.gaR CTree.gbR CTree.gar0 CTree.gbr0 48)
    (hcstMonoT : MonotoneOn cstF (Set.Icc ((a0GD : ℚ) : ℝ) (1 / 10)))
    (hcst0 : cstF ((tGD1 : ℚ) : ℝ) ≤ ((cHGD0 : ℚ) : ℝ))
    (hcst1 : cstF ((tGD2 : ℚ) : ℝ) ≤ ((cHGD1 : ℚ) : ℝ))
    (hP1 : ∀ s : ℝ, ((1 - tJ0 : ℚ) : ℝ) ≤ s → s ≤ ((1 - a0GD : ℚ) : ℝ) →
      ∑ e ∈ T.Mreg, c2 (gs s) (T.dA e : ℝ) (T.dB e : ℝ) + capC s * ∑ x ∈ T.S, (T.x x : ℝ) ≤
        ∑ r ∈ R, ∑ i ∈ range (nR r), c2 (gs s) (lev dR r i) (lev dR r (i + 1)) + Omega ks mr s)
    (hP2 : ∀ s : ℝ, ((1 - tJ0 : ℚ) : ℝ) ≤ s → s ≤ ((1 - a0GD : ℚ) : ℝ) →
      ∑ e ∈ T.Mun, c2 (gs s) (T.dA e : ℝ) (T.dB e : ℝ) ≤ corrC cstF s) :
    ∀ t : ℝ, ((a0GD : ℚ) : ℝ) ≤ t → t ≤ 1 → Finv (1 - t) (invoice (caller 6 7) n 17) < 0 := by
  have eJ : tTJ0GD = tJ0 := rfl
  have hwin := wtGD
  rw [eJ] at hwin
  have hdd := cfC_dGD
  intro t ht ht1
  rcases le_or_gt ((tJ0 : ℚ) : ℝ) t with hC | hC
  · exact ceiling_native_J R nR dR hmono hd9 hmix n ks mr st E J distF spF cstF hk hmass hmd hmr hF hY hst hEex hcong hdist hJ hspMono hcstMono hspTab hcstTab hspTabJ hcstTabJ t hC ht1
  have p0 := CTree.tree_piece R nR dR hmono hd9 hmix n ks mr E cstF hF hEex CTree.gaW CTree.gaR CTree.gbR CTree.gar0 CTree.gbr0 48 T
    CTree.ga_all (by have h := CTree.gb_all; rwa [show CTree.gbW = CTree.gaW from rfl] at h) (by decide) (by decide) a0GD tGD0 tGD1 lcpGD0 sgGD0 cHGD0 unLoGD0 capIGD0 lamGD0 gAGD0 gBGD0
    hwin (by unfold tGD0 a0GD; norm_num) (by unfold tGD0 tGD1; norm_num) (by unfold tGD1 tJ0; norm_num) (by unfold a0GD; norm_num) sigGD0 (by unfold sgGD0; norm_num) lineGD0 numGD0 capGD0
    (unit_of_Fup tGD1 unLoGD0 (by unfold tGD1; norm_num) (by unfold tGD1; norm_num) (by have := unGD0; exact this)) hcst0 hcstMonoT hP1 hP2
    (hFbT_of a0GD tGD0 tGD1 _ hdd (by unfold a0GD; norm_num) (by unfold tGD1; norm_num) (by unfold tGD0 tGD1; norm_num) (by unfold tGD0 a0GD; norm_num) ptGD0)
  have p1 := CTree.tree_piece R nR dR hmono hd9 hmix n ks mr E cstF hF hEex CTree.gaW CTree.gaR CTree.gbR CTree.gar0 CTree.gbr0 48 T
    CTree.ga_all (by have h := CTree.gb_all; rwa [show CTree.gbW = CTree.gaW from rfl] at h) (by decide) (by decide) a0GD tGD1 tGD2 lcpGD1 sgGD1 cHGD1 unLoGD1 capIGD1 lamGD1 gAGD1 gBGD1
    hwin (by unfold tGD1 a0GD; norm_num) (by unfold tGD1 tGD2; norm_num) (tGDend.trans eJ).le (by unfold a0GD; norm_num) sigGD1 (by unfold sgGD1; norm_num) lineGD1 numGD1 capGD1
    (unit_of_Fup tGD2 unLoGD1 (by unfold tGD2; norm_num) (by unfold tGD2; norm_num) (by have := unGD1; exact this)) hcst1 hcstMonoT hP1 hP2
    (hFbT_of a0GD tGD1 tGD2 _ hdd (by unfold a0GD; norm_num) (by unfold tGD2; norm_num) (by unfold tGD1 tGD2; norm_num) (by unfold tGD1 a0GD; norm_num) ptGD1)
  rcases le_or_gt t ((tGD1 : ℚ) : ℝ) with h1 | h1
  · exact p0 t (by rw [tGDstart]; exact ht) h1
  · exact p1 t h1.le (by rw [show tGD2 = tJ0 from tGDend.trans eJ]; exact hC.le)

end CongestionNative

#print axioms CongestionNative.hFbT_of
#print axioms CongestionNative.ceiling_tree_CG
#print axioms CongestionNative.ceiling_tree_GD
