import Nov15.CongestionReaderCore
import Nov15.CongestionReaderTree

/-!
CONGESTION-READER-PIECE: one t-piece of the reader-charge ceiling (analogue of `CTree.tree_piece`).
Differences to `tree_piece`: the tree data `T` are the READERS' trees; the line bound is `tree_lower_reader` (allowance `dI <= SC delta` per tied reader,
15 allowances subtracted); the register side uses `sum_c2_pay` (residual of the payers) instead of `sum_all_c2_le`.
-/
namespace CTree
open NumCertK JointCeiling CallerCost CongestionI3 CongestionI3Dual CongestionNative CongestionReader Finset

theorem reader_regs_lower {σ ρ μ : Type} [DecidableEq σ] [DecidableEq ρ] [DecidableEq μ]
    (W : List (List ℕ)) (rsA rsB : List Row) (rootA rootB : Row) (nB : ℕ) (T : TreeData σ ρ μ rsA rsB rootA rootB nB)
    (hcA : ∀ r ∈ rsA, Row.check W rsA r = true) (hcB : ∀ r ∈ rsB, Row.check W rsB r = true)
    (hrA : rootA.m ≤ 48) (hrB : rootB.m ≤ 48) (capI dI lam gA gB NDL : ℕ) (hline : lineOKR rootA rootB capI dI lam gA gB = true)
    (lo hi : ℚ) (hwin : wtOK W lo hi = true) (hlo : 0 ≤ lo) (hhi : hi ≤ 1) (s : ℝ) (h1 : (lo : ℝ) ≤ s) (h2 : s ≤ (hi : ℝ))
    (capR corr Om regs δ : ℝ) (hcap : (capI : ℝ) ≤ SCr * capR) (hδ : (dI : ℝ) ≤ SCr * δ)
    (Q Uo : Finset σ) (hUo : Uo ⊆ T.S) (hUc : Uo.card ≤ NDL) (hQ : Q ⊆ T.S)
    (hcase : ∀ x ∈ T.S, x ∈ Q ∨ T.x x = (T.J.filter fun p => p.1 = x).card ∨ x ∈ Uo)
    (hP1 : ∑ e ∈ T.Mreg, c2 (gs s) (T.dA e : ℝ) (T.dB e : ℝ) + capR * ∑ x ∈ T.S, (T.x x : ℝ) ≤ regs + Om)
    (hP2 : ∑ e ∈ T.Mun, c2 (gs s) (T.dA e : ℝ) (T.dB e : ℝ) ≤ corr) :
    ((lam : ℝ) * 4962 - ((gA : ℝ) * 104 - ((gA : ℝ) - gB) * nB) - NDL * dI) / SCr - corr ≤ regs + Om + δ * Q.card := by
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
  have tl := tree_lower_reader W rsA rsB rootA rootB nB T hcA hcB hrA hrB capI dI lam gA gB NDL hline w hWl
    (fun e he => hw0 e (T.hMsub he)) capR δ hcap hδ Q Uo hUo hUc hQ hcase
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
  have hQc : (0 : ℝ) ≤ δ * Q.card := by
    have : (0 : ℝ) ≤ δ := by
      have : (0 : ℝ) ≤ SCr * δ := le_trans (by positivity) hδ
      exact nonneg_of_mul_nonneg_right (by linarith) hSC
    positivity
  have h4 : SCr * (∑ e ∈ T.Mv, w e + capR * ∑ x ∈ T.S, (T.x x : ℝ) + δ * Q.card) ≤ SCr * (regs + Om + corr + δ * Q.card) :=
    mul_le_mul_of_nonneg_left (by linarith) hSC.le
  rw [sub_le_iff_le_add, div_le_iff₀ hSC]
  nlinarith

/-- one t-piece [a, b] of the reader-charge ceiling, inside [a0, tJ0] (shape of `tree_piece`).  New hypotheses: `hdel` (certified `dI <= SC delta` on the window),
`hline` (`lineOKR`), `hnum` (15 allowances subtracted), and the READER STRUCTURE `Q, Uo, pi` with `hTied` (named hypothesis, F2 lineage lemma + TL-a/b/c +
CG1 + own56 + X-born-at-1; see CongestionReader.md). -/
theorem reader_piece {ι : Type*} [DecidableEq ι] {σ' ρ' μ' : Type} [DecidableEq σ'] [DecidableEq ρ'] [DecidableEq μ']
    (R : Finset ι) (nR : ι → ℕ) (dR : ι → ℕ → ℕ)
    (hmono : ∀ r ∈ R, ∀ i < nR r, dR r i ≤ dR r (i + 1)) (hd9 : ∀ r ∈ R, dR r (nR r) ≤ 9)
    (hmix : (R.filter fun r => Mixed dR nR r).card ≤ 5)
    (n : Inv) (ks : List ℕ) (mr : ℕ) (E : ℝ → ℝ) (cstF : ℝ → ℝ)
    (hF : ∀ s, 0 ≤ s → s ≤ 1 → Finv s n ≤ -400 * (8 : ℝ) ^ s - dprice ks s - mr - E s)
    (hEex : ∀ s, 0 ≤ s → s ≤ 1 → ∑ r ∈ R, ex (gs s) (lev dR r) (nR r) ≤ E s)
    (W : List (List ℕ)) (rsA rsB : List Row) (rootA rootB : Row) (nB : ℕ) (T : TreeData σ' ρ' μ' rsA rsB rootA rootB nB)
    (hcA : ∀ r ∈ rsA, Row.check W rsA r = true) (hcB : ∀ r ∈ rsB, Row.check W rsB r = true)
    (hrA : rootA.m ≤ 48) (hrB : rootB.m ≤ 48)
    (a0 a b lcp σc cH unLo : ℚ) (capI dI lam gA gB NDL : ℕ)
    (hwin : wtOK W (1 - tJ0) (1 - a0) = true) (ha0 : a0 ≤ a) (hab : a ≤ b) (hb : b ≤ tJ0) (ha00 : 0 ≤ a0)
    (hσc : sigOK (1 - b) (1 - a) σc = true) (hσ0 : 0 ≤ σc)
    (hline : lineOKR rootA rootB capI dI lam gA gB = true)
    (hnum : lcp + 8 * cH ≤ (((lam : ℚ) * 4962 - ((gA : ℚ) * 104 - ((gA : ℚ) - gB) * nB) - NDL * dI) / 10 ^ 14))
    (hcapI : (capI : ℚ) ≤ unLo * 10 ^ 14 / 48) (hun : (unLo : ℝ) ≤ (9 : ℝ) ^ (1 - (b : ℝ)) - (8 : ℝ) ^ (1 - (b : ℝ)))
    (hcst : cstF (b : ℝ) ≤ (cH : ℝ)) (hcstMono : MonotoneOn cstF (Set.Icc ((a0 : ℚ) : ℝ) (1 / 10)))
    (hdel : ∀ s : ℝ, ((1 - tJ0 : ℚ) : ℝ) ≤ s → s ≤ ((1 - a0 : ℚ) : ℝ) → (dI : ℝ) ≤ SCr * deltaF s)
    (hP1 : ∀ s : ℝ, ((1 - tJ0 : ℚ) : ℝ) ≤ s → s ≤ ((1 - a0 : ℚ) : ℝ) →
      ∑ e ∈ T.Mreg, c2 (gs s) (T.dA e : ℝ) (T.dB e : ℝ) + capC s * ∑ x ∈ T.S, (T.x x : ℝ) ≤
        ∑ r ∈ R, ∑ i ∈ range (nR r), c2 (gs s) (lev dR r i) (lev dR r (i + 1)) + Omega ks mr s)
    (hP2 : ∀ s : ℝ, ((1 - tJ0 : ℚ) : ℝ) ≤ s → s ≤ ((1 - a0 : ℚ) : ℝ) →
      ∑ e ∈ T.Mun, c2 (gs s) (T.dA e : ℝ) (T.dB e : ℝ) ≤ corrC cstF s)
    (Q Uo : Finset σ') (hUo : Uo ⊆ T.S) (hUc : Uo.card ≤ NDL) (hQ : Q ⊆ T.S)
    (hcase : ∀ x ∈ T.S, x ∈ Q ∨ T.x x = (T.J.filter fun p => p.1 = x).card ∨ x ∈ Uo)
    (π : σ' → ι) (hπR : ∀ t ∈ Q, π t ∈ R) (hπinj : Set.InjOn π Q) (hTied : ∀ t ∈ Q, Tied nR dR (π t))
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
  have hlo : (0 : ℚ) ≤ 1 - tJ0 := by unfold tJ0; norm_num
  have hhi : (1 - a0 : ℚ) ≤ 1 := by linarith
  have hw1 : ((1 - tJ0 : ℚ) : ℝ) ≤ 1 - t := by push_cast; linarith
  have hw2 : 1 - t ≤ ((1 - a0 : ℚ) : ℝ) := by push_cast; linarith
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
  have hδs := hdel (1 - t) hw1 hw2
  have hSC : (0 : ℝ) < SCr := by unfold SCr; positivity
  have hδ0 : 0 ≤ deltaF (1 - t) := by
    have : (0 : ℝ) ≤ SCr * deltaF (1 - t) := le_trans (by positivity) hδs
    exact nonneg_of_mul_nonneg_right (by linarith) hSC
  have hT := reader_regs_lower W rsA rsB rootA rootB nB T hcA hcB hrA hrB capI dI lam gA gB NDL hline (1 - tJ0) (1 - a0) hwin hlo hhi
    (1 - t) hw1 hw2 (capC (1 - t)) (corrC cstF (1 - t)) (Omega ks mr (1 - t))
    (∑ r ∈ R, ∑ i ∈ range (nR r), c2 (gs (1 - t)) (lev dR r i) (lev dR r (i + 1))) (deltaF (1 - t)) hcap hδs
    Q Uo hUo hUc hQ hcase (hP1 (1 - t) hw1 hw2) (hP2 (1 - t) hw1 hw2)
  have hnum' : (lcp : ℝ) + 8 * cH ≤ ((lam : ℝ) * 4962 - ((gA : ℝ) * 104 - ((gA : ℝ) - gB) * nB) - NDL * dI) / SCr := by
    have := (Rat.cast_le (K := ℝ)).mpr hnum
    push_cast at this
    unfold SCr; linarith
  have hpay := sum_c2_pay (1 - t) R nR dR hmono hd9 5 hmix (σc : ℝ) (by exact_mod_cast hσ0) hσ (deltaF (1 - t)) hδ0 Q π hπR hπinj
    (fun t' ht' => tied_rho (1 - t) hs0 hs1 nR dR (π t') (hTied t' ht'))
  push_cast at hpay
  have hE' : (((lcp - 5 * σc : ℚ)) : ℝ) ≤ E (1 - t) + Omega ks mr (1 - t) := by
    have := hEex (1 - t) hs0 hs1
    push_cast
    linarith
  exact branchC_om n ks mr (E (1 - t)) _ (1 - t) (hF _ hs0 hs1) hE' (hFb (1 - t) (by push_cast; linarith) (by push_cast; linarith))

end CTree

#print axioms CTree.reader_regs_lower
#print axioms CTree.reader_piece
