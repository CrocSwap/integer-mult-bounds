import Nov15.CongestionNativeJ
import Nov15.CongestionTreeW

/-!
CONGESTION-TREE-PIECE: generic piece lemma of the whole-meeting tree ceiling.
`tree_regs_lower` : tree reduction + the two I2-charge premises  =>  `LT/SC - corr <= sum of register c2 + Omega`.
`tree_piece`      : one t-piece [a, b] inside [a0, tJ0]: the tree bound replaces `hcong`/`hdist`/`hJ` of `ceiling_native_J`.
-/
namespace CTree
open NumCertK JointCeiling CallerCost CongestionI3 CongestionI3Dual CongestionNative Finset

theorem tree_regs_lower {σ ρ μ : Type} [DecidableEq σ] [DecidableEq ρ] [DecidableEq μ]
    (W : List (List ℕ)) (rsA rsB : List Row) (rootA rootB : Row) (nB : ℕ) (T : TreeData σ ρ μ rsA rsB rootA rootB nB)
    (hcA : ∀ r ∈ rsA, Row.check W rsA r = true) (hcB : ∀ r ∈ rsB, Row.check W rsB r = true)
    (hrA : rootA.m ≤ 48) (hrB : rootB.m ≤ 48) (capI lam gA gB : ℕ) (hline : lineOK rootA rootB capI lam gA gB = true)
    (lo hi : ℚ) (hwin : wtOK W lo hi = true) (hlo : 0 ≤ lo) (hhi : hi ≤ 1) (s : ℝ) (h1 : (lo : ℝ) ≤ s) (h2 : s ≤ (hi : ℝ))
    (capR corr Om regs : ℝ) (hcap : (capI : ℝ) ≤ SCr * capR)
    (hP1 : ∑ e ∈ T.Mreg, c2 (gs s) (T.dA e : ℝ) (T.dB e : ℝ) + capR * ∑ x ∈ T.S, (T.x x : ℝ) ≤ regs + Om)
    (hP2 : ∑ e ∈ T.Mun, c2 (gs s) (T.dA e : ℝ) (T.dB e : ℝ) ≤ corr) :
    ((lam : ℝ) * 4962 - ((gA : ℝ) * 104 - ((gA : ℝ) - gB) * nB)) / SCr - corr ≤ regs + Om := by
  have hSC : (0 : ℝ) < SCr := by unfold SCr; positivity
  set w : μ → ℝ := fun e => c2 (gs s) (T.dA e : ℝ) (T.dB e : ℝ) with hw
  have hWl : ∀ e, 1 ≤ T.dA e → T.dA e < T.dB e → T.dB e ≤ 8 →
      (((W.getD (T.dA e) []).getD (T.dB e) 0 : ℕ) : ℝ) ≤ SCr * w e := by
    intro e ha hab hb
    have := W_lower W lo hi hwin hlo hhi s h1 h2 (T.dA e) (T.dB e) ha hab hb
    have h' := (div_le_iff₀ hSC).1 this
    simp only [hw]
    rw [mul_comm]; exact h'
  have hw0 : ∀ e ∈ T.Mreg ∪ T.Mun, 0 ≤ w e := by
    intro e he
    obtain ⟨ha, hab, hb⟩ := T.hdim e he
    have := W_lower W lo hi hwin hlo hhi s h1 h2 (T.dA e) (T.dB e) ha hab hb
    exact le_trans (div_nonneg (Nat.cast_nonneg _) hSC.le) this
  have tl := tree_lower W rsA rsB rootA rootB nB T hcA hcB hrA hrB capI lam gA gB hline w hWl
    (fun e he => hw0 e (T.hMsub he)) capR hcap
  have u1 : ∑ e ∈ T.Mv, w e ≤ ∑ e ∈ T.Mreg ∪ T.Mun, w e :=
    Finset.sum_le_sum_of_subset_of_nonneg T.hMsub (fun e he _ => hw0 e he)
  have u2 : ∑ e ∈ T.Mreg ∪ T.Mun, w e ≤ ∑ e ∈ T.Mreg, w e + ∑ e ∈ T.Mun, w e := by
    have h := Finset.sum_union_inter (s₁ := T.Mreg) (s₂ := T.Mun) (f := w)
    have h0 : 0 ≤ ∑ e ∈ T.Mreg ∩ T.Mun, w e :=
      Finset.sum_nonneg (fun e he => hw0 e (Finset.mem_union_left _ (Finset.mem_of_mem_inter_left he)))
    linarith
  have h3 : ∑ e ∈ T.Mv, w e + capR * ∑ x ∈ T.S, (T.x x : ℝ) ≤ regs + Om + corr := by
    have : ∑ e ∈ T.Mreg, w e = ∑ e ∈ T.Mreg, c2 (gs s) (T.dA e : ℝ) (T.dB e : ℝ) := rfl
    have : ∑ e ∈ T.Mun, w e = ∑ e ∈ T.Mun, c2 (gs s) (T.dA e : ℝ) (T.dB e : ℝ) := rfl
    linarith
  have h4 := mul_le_mul_of_nonneg_left h3 hSC.le
  rw [sub_le_iff_le_add, div_le_iff₀ hSC]
  nlinarith

/-- one t-piece [a, b] of the tree ceiling, inside [a0, tJ0].  Same shape as `piece` of `ceiling_native_J`; the junk-count/`hcong`/`hdist`
hypotheses are replaced by the tree data `T`, the weight certificate `hwin`, the line certificate `hline`, and the two I2-charge premises
`hP1`, `hP2` (on the window s in [1 - tJ0, 1 - a0]). -/
theorem tree_piece {ι : Type*} [DecidableEq ι] {σ' ρ' μ' : Type} [DecidableEq σ'] [DecidableEq ρ'] [DecidableEq μ']
    (R : Finset ι) (nR : ι → ℕ) (dR : ι → ℕ → ℕ)
    (hmono : ∀ r ∈ R, ∀ i < nR r, dR r i ≤ dR r (i + 1)) (hd9 : ∀ r ∈ R, dR r (nR r) ≤ 9)
    (hmix : (R.filter fun r => Mixed dR nR r).card ≤ 5)
    (n : Inv) (ks : List ℕ) (mr : ℕ) (E : ℝ → ℝ) (cstF : ℝ → ℝ)
    (hF : ∀ s, 0 ≤ s → s ≤ 1 → Finv s n ≤ -400 * (8 : ℝ) ^ s - dprice ks s - mr - E s)
    (hEex : ∀ s, 0 ≤ s → s ≤ 1 → ∑ r ∈ R, ex (gs s) (lev dR r) (nR r) ≤ E s)
    (W : List (List ℕ)) (rsA rsB : List Row) (rootA rootB : Row) (nB : ℕ) (T : TreeData σ' ρ' μ' rsA rsB rootA rootB nB)
    (hcA : ∀ r ∈ rsA, Row.check W rsA r = true) (hcB : ∀ r ∈ rsB, Row.check W rsB r = true)
    (hrA : rootA.m ≤ 48) (hrB : rootB.m ≤ 48)
    (a0 a b lcp σc cH unLo : ℚ) (capI lam gA gB : ℕ)
    (hwin : wtOK W (1 - tJ0) (1 - a0) = true) (ha0 : a0 ≤ a) (hab : a ≤ b) (hb : b ≤ tJ0) (ha00 : 0 ≤ a0)
    (hσc : sigOK (1 - b) (1 - a) σc = true) (hσ0 : 0 ≤ σc)
    (hline : lineOK rootA rootB capI lam gA gB = true)
    (hnum : lcp + 8 * cH ≤ (((lam : ℚ) * 4962 - ((gA : ℚ) * 104 - ((gA : ℚ) - gB) * nB)) / 10 ^ 14))
    (hcapI : (capI : ℚ) ≤ unLo * 10 ^ 14 / 48) (hun : (unLo : ℝ) ≤ (9 : ℝ) ^ (1 - (b : ℝ)) - (8 : ℝ) ^ (1 - (b : ℝ)))
    (hcst : cstF (b : ℝ) ≤ (cH : ℝ)) (hcstMono : MonotoneOn cstF (Set.Icc ((a0 : ℚ) : ℝ) (1 / 10)))
    (hP1 : ∀ s : ℝ, ((1 - tJ0 : ℚ) : ℝ) ≤ s → s ≤ ((1 - a0 : ℚ) : ℝ) →
      ∑ e ∈ T.Mreg, c2 (gs s) (T.dA e : ℝ) (T.dB e : ℝ) + capC s * ∑ x ∈ T.S, (T.x x : ℝ) ≤
        ∑ r ∈ R, ∑ i ∈ range (nR r), c2 (gs s) (lev dR r i) (lev dR r (i + 1)) + Omega ks mr s)
    (hP2 : ∀ s : ℝ, ((1 - tJ0 : ℚ) : ℝ) ≤ s → s ≤ ((1 - a0 : ℚ) : ℝ) →
      ∑ e ∈ T.Mun, c2 (gs s) (T.dA e : ℝ) (T.dB e : ℝ) ≤ corrC cstF s)
    (hFb : ∀ s : ℝ, ((1 - b : ℚ) : ℝ) ≤ s → s ≤ ((1 - a : ℚ) : ℝ) → Fc cfC s < 17 * (((lcp - 5 * σc : ℚ)) : ℝ)) :
    ∀ t : ℝ, (a : ℝ) ≤ t → t ≤ (b : ℝ) → Finv (1 - t) (invoice (caller 6 7) n 17) < 0 := by
  intro t h1 h2
  have hbJ : b ≤ tJ0 := hb
  have htJ : tJ0 ≤ 1 / 10 := by unfold tJ0; norm_num
  have hbq : (b : ℝ) ≤ ((tJ0 : ℚ) : ℝ) := by exact_mod_cast hb
  have hbq' : (b : ℝ) ≤ 1 / 10 := by
    have := (Rat.cast_le (K := ℝ)).mpr (le_trans hb htJ); push_cast at this; exact this
  have haq : ((a0 : ℚ) : ℝ) ≤ a := by exact_mod_cast ha0
  have hab' : (a : ℝ) ≤ b := by exact_mod_cast hab
  have hA0 : (0 : ℝ) ≤ a0 := by exact_mod_cast ha00
  have hs0 : 0 ≤ 1 - t := by linarith
  have hs1 : 1 - t ≤ 1 := by linarith
  have hσ : ∀ a' b' : ℕ, 1 ≤ a' → a' ≤ b' → b' ≤ 8 → c2 (gs (1 - t)) (a' : ℝ) (b' : ℝ) ≤ (σc : ℝ) := by
    intro a' b' h1' h2' h3'
    have hb0 : 0 ≤ 1 - b := by
      have : b ≤ 1 := le_trans hb (by unfold tJ0; norm_num)
      linarith
    exact sig_of_ok (1 - b) (1 - a) σc hσc hb0 (by linarith) hσ0 (1 - t)
      (by push_cast; linarith) (by push_cast; linarith) a' b' h1' h2' h3'
  -- window
  have hlo : (0 : ℚ) ≤ 1 - tJ0 := by unfold tJ0; norm_num
  have hhi : (1 - a0 : ℚ) ≤ 1 := by linarith
  have hw1 : ((1 - tJ0 : ℚ) : ℝ) ≤ 1 - t := by push_cast; linarith
  have hw2 : 1 - t ≤ ((1 - a0 : ℚ) : ℝ) := by push_cast; linarith
  -- cap and corr
  have hcap : (capI : ℝ) ≤ SCr * capC (1 - t) := by
    have hu : (unLo : ℝ) ≤ (9 : ℝ) ^ (1 - t) - (8 : ℝ) ^ (1 - t) := by
      have := unit_mono (1 - (b : ℝ)) (1 - t) (by linarith) (by linarith)
      linarith
    have hc : (capI : ℝ) ≤ (unLo : ℝ) * 10 ^ 14 / 48 := by exact_mod_cast hcapI
    unfold SCr capC
    have : (unLo : ℝ) * 10 ^ 14 / 48 ≤ 10 ^ 14 * (((9 : ℝ) ^ (1 - t) - (8 : ℝ) ^ (1 - t)) / 48) := by nlinarith
    linarith
  have hcorr : corrC cstF (1 - t) ≤ 8 * (cH : ℝ) := by
    unfold corrC
    have e : 1 - (1 - t) = t := by ring
    rw [e]
    have : cstF t ≤ cstF (b : ℝ) :=
      hcstMono ⟨le_trans haq h1, by linarith⟩ ⟨le_trans haq hab', hbq'⟩ h2
    linarith
  have hT := tree_regs_lower W rsA rsB rootA rootB nB T hcA hcB hrA hrB capI lam gA gB hline (1 - tJ0) (1 - a0) hwin hlo hhi
    (1 - t) hw1 hw2 (capC (1 - t)) (corrC cstF (1 - t)) (Omega ks mr (1 - t))
    (∑ r ∈ R, ∑ i ∈ range (nR r), c2 (gs (1 - t)) (lev dR r i) (lev dR r (i + 1))) hcap
    (hP1 (1 - t) hw1 hw2) (hP2 (1 - t) hw1 hw2)
  have hnum' : (lcp : ℝ) + 8 * cH ≤ ((lam : ℝ) * 4962 - ((gA : ℝ) * 104 - ((gA : ℝ) - gB) * nB)) / SCr := by
    have := (Rat.cast_le (K := ℝ)).mpr hnum
    push_cast at this
    unfold SCr; linarith
  have hreg := sum_all_c2_le (gs (1 - t)) (gs_zero (1 - t)) R nR dR hmono hd9 5 hmix (σc : ℝ) (by exact_mod_cast hσ0) hσ
  push_cast at hreg
  have hE' : (((lcp - 5 * σc : ℚ)) : ℝ) ≤ E (1 - t) + Omega ks mr (1 - t) := by
    have := hEex (1 - t) hs0 hs1
    push_cast
    linarith
  exact branchC_om n ks mr (E (1 - t)) _ (1 - t) (hF _ hs0 hs1) hE' (hFb (1 - t) (by push_cast; linarith) (by push_cast; linarith))

end CTree

#print axioms CTree.tree_regs_lower
#print axioms CTree.tree_piece
