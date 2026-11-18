import Nov15.CongestionTreePiece

/-!
CONGESTION-READER-TREE: the line bound of `tree_lower` with a per-reader allowance.
`T.S` are the READERS (IN side; the IN DP table is the reflection of the OUT table, c2 is reflection symmetric), `T.J` the junk cells (reader, source).
`Q` = readers tied to a register with residual >= delta, `Uo` = the <= NDL = 15 + omega untied readers (mixed payers / owned last movers).
Every reader is tied, all-transported (x = k), or in Uo.  `lineOKR` has the allowance `dI <= SC delta` in the tied case.
-/
namespace CTree
open Finset

def lineOKR (rA rB : Row) (capI dI lam gA gB : ℕ) : Bool :=
  (List.range 49).all (fun x => (List.range 49).all (fun r =>
    decide (lam * min 48 (x + r) ≤ gv rA r + x * capI + dI + gA) &&
      decide (lam * min 48 (x + r) ≤ gv rB r + x * capI + dI + gB)))
  && decide (gB ≤ gA) && decide (lam ≤ capI)

theorem tree_lower_reader {σ ρ μ : Type} [DecidableEq σ] [DecidableEq ρ] [DecidableEq μ]
    (W : List (List ℕ)) (rsA rsB : List Row) (rootA rootB : Row) (nB : ℕ) (T : TreeData σ ρ μ rsA rsB rootA rootB nB)
    (hcA : ∀ r ∈ rsA, Row.check W rsA r = true) (hcB : ∀ r ∈ rsB, Row.check W rsB r = true)
    (hrA : rootA.m ≤ 48) (hrB : rootB.m ≤ 48) (capI dI lam gA gB NDL : ℕ)
    (hline : lineOKR rootA rootB capI dI lam gA gB = true)
    (w : μ → ℝ)
    (hW : ∀ e, 1 ≤ T.dA e → T.dA e < T.dB e → T.dB e ≤ 8 →
      (((W.getD (T.dA e) []).getD (T.dB e) 0 : ℕ) : ℝ) ≤ SCr * w e)
    (hw0 : ∀ e ∈ T.Mv, 0 ≤ w e) (cap δ : ℝ) (hcap : (capI : ℝ) ≤ SCr * cap) (hδ : (dI : ℝ) ≤ SCr * δ)
    (Q Uo : Finset σ) (hUo : Uo ⊆ T.S) (hUc : Uo.card ≤ NDL) (hQ : Q ⊆ T.S)
    (hcase : ∀ s ∈ T.S, s ∈ Q ∨ T.x s = (T.J.filter fun p => p.1 = s).card ∨ s ∈ Uo) :
    (lam : ℝ) * 4962 - ((gA : ℝ) * 104 - ((gA : ℝ) - gB) * nB) - NDL * dI ≤
      SCr * (∑ e ∈ T.Mv, w e + cap * ∑ s ∈ T.S, (T.x s : ℝ) + δ * Q.card) := by
  have hred := reduction T.S T.ms T.nm w T.Mv T.hnd T.hMv T.hcap hw0
  have hSC : (0 : ℝ) < SCr := by unfold SCr; positivity
  unfold lineOKR at hline
  simp only [Bool.and_eq_true, List.all_eq_true, List.mem_range, decide_eq_true_eq] at hline
  obtain ⟨⟨hline, hBA⟩, hlc⟩ := hline
  set k : σ → ℕ := fun s => (T.J.filter fun p => p.1 = s).card with hk
  set γ : σ → ℕ := fun s => if s ∈ T.Bset then gB else gA with hγ
  have hlcR : (lam : ℝ) ≤ capI := by exact_mod_cast hlc
  have per : ∀ s ∈ T.S, (lam : ℝ) * k s - γ s - (if s ∈ Uo then (dI : ℝ) else 0) ≤
      SCr * (((T.ms s).map fun e => w e / T.nm e).sum + cap * T.x s) + (if s ∈ Q then (dI : ℝ) else 0) := by
    intro s hs
    have hk48 : k s ≤ 48 := T.hfib s hs
    have hx := T.hxk s hs
    have hc := T.hcell s hs
    have key : ∀ (root : Row) (rs : List Row) (g : ℕ), (∀ r ∈ rs, Row.check W rs r = true) → root.m ≤ 48 →
        (∀ x < 49, ∀ r < 49, lam * min 48 (x + r) ≤ gv root r + x * capI + dI + g) →
        Tr rs T.nm T.dA T.dB root (T.R s) (T.ms s) →
        (lam : ℝ) * k s - g - (if s ∈ Uo then (dI : ℝ) else 0) ≤
          SCr * (((T.ms s).map fun e => w e / T.nm e).sum + cap * T.x s) + (if s ∈ Q then (dI : ℝ) else 0) := by
      intro root rs g hcert hr48 hl htr
      have hcost := tree_cost_ge W rs hcert T.nm T.dA T.dB w hW htr
      have hrc := htr.card_le
      have hgv : (0 : ℝ) ≤ ((gv root (T.R s).card : ℕ) : ℝ) := Nat.cast_nonneg _
      have hcx : (T.x s : ℝ) * capI ≤ SCr * (cap * T.x s) := by
        have : (0 : ℝ) ≤ T.x s := by positivity
        nlinarith
      have hdQ : (0 : ℝ) ≤ (if s ∈ Q then (dI : ℝ) else 0) := by split_ifs <;> positivity
      have hdU : (0 : ℝ) ≤ (if s ∈ Uo then (dI : ℝ) else 0) := by split_ifs <;> positivity
      have hl' := hl (T.x s) (by have := T.hfib s hs; omega) (T.R s).card (by omega)
      have hn : lam * k s ≤ gv root (T.R s).card + T.x s * capI + dI + g := by
        have : k s ≤ min 48 (T.x s + (T.R s).card) := le_min hk48 hc
        exact le_trans (Nat.mul_le_mul_left _ this) hl'
      have hr : (lam : ℝ) * k s ≤ ((gv root (T.R s).card : ℕ) : ℝ) + T.x s * capI + dI + g := by exact_mod_cast hn
      by_cases hU : s ∈ Uo
      · rw [if_pos hU]; linarith
      · rw [if_neg hU]
        rcases hcase s hs with hq | hxk | hu
        · rw [if_pos hq]; linarith
        · -- all transported: k <= x, lam <= capI
          have hkx : (k s : ℝ) ≤ T.x s := by
            have : k s ≤ T.x s := hxk ▸ le_refl _
            exact_mod_cast this
          have hlk : (lam : ℝ) * k s ≤ capI * T.x s := by
            have h0 : (0 : ℝ) ≤ k s := by positivity
            have h1 : (0 : ℝ) ≤ T.x s := by positivity
            nlinarith
          have hg0 : (0 : ℝ) ≤ g := by positivity
          have : (0 : ℝ) ≤ SCr * (((T.ms s).map fun e => w e / T.nm e).sum) := le_trans hgv hcost
          split_ifs <;> nlinarith
        · exact absurd hu hU
    by_cases hb : s ∈ T.Bset
    · have := key rootB rsB gB hcB hrB (fun x hx r hr => (hline x hx r hr).2) (T.htreeB s hb)
      simpa [hγ, hb] using this
    · have := key rootA rsA gA hcA hrA (fun x hx r hr => (hline x hx r hr).1) (T.htreeA s hs hb)
      simpa [hγ, hb] using this
  have hsum := Finset.sum_le_sum per
  have hJ : (T.J.card : ℝ) = ∑ s ∈ T.S, (k s : ℝ) := by
    have := Finset.card_eq_sum_card_fiberwise (f := Prod.fst) (s := T.J) (t := T.S) T.hJS
    exact_mod_cast this
  have hJge : (4962 : ℝ) ≤ ∑ s ∈ T.S, (k s : ℝ) := by rw [← hJ]; exact_mod_cast T.hJcard
  have hγs : ∑ s ∈ T.S, (γ s : ℝ) ≤ gA * 104 - (gA - gB) * nB := by
    have e : ∀ s, (γ s : ℝ) = gA - (if s ∈ T.Bset then ((gA : ℝ) - gB) else 0) := by
      intro s; simp only [hγ]; split_ifs <;> push_cast <;> ring
    rw [Finset.sum_congr rfl (fun s _ => e s), Finset.sum_sub_distrib, Finset.sum_const, Finset.sum_ite_mem,
      Finset.inter_eq_right.2 T.hB, Finset.sum_const, nsmul_eq_mul, nsmul_eq_mul]
    have h1 : (T.S.card : ℝ) ≤ 104 := by exact_mod_cast T.hScard
    have h2 : (nB : ℝ) ≤ T.Bset.card := by exact_mod_cast T.hBcard
    have h3 : (gB : ℝ) ≤ gA := by exact_mod_cast hBA
    have h4 : (0 : ℝ) ≤ gA := by positivity
    nlinarith [mul_nonneg h4 (sub_nonneg.2 h1), mul_nonneg (sub_nonneg.2 h3) (sub_nonneg.2 h2)]
  have hlam : (0 : ℝ) ≤ lam := by positivity
  have hgl : (lam : ℝ) * 4962 ≤ lam * ∑ s ∈ T.S, (k s : ℝ) := mul_le_mul_of_nonneg_left hJge hlam
  have eU : ∑ s ∈ T.S, (if s ∈ Uo then (dI : ℝ) else 0) = Uo.card * dI := by
    rw [Finset.sum_ite_mem, Finset.inter_eq_right.2 hUo, Finset.sum_const, nsmul_eq_mul]
  have eQ : ∑ s ∈ T.S, (if s ∈ Q then (dI : ℝ) else 0) = Q.card * dI := by
    rw [Finset.sum_ite_mem, Finset.inter_eq_right.2 hQ, Finset.sum_const, nsmul_eq_mul]
  have e1 : ∑ s ∈ T.S, ((lam : ℝ) * k s - γ s - (if s ∈ Uo then (dI : ℝ) else 0)) =
      lam * ∑ s ∈ T.S, (k s : ℝ) - ∑ s ∈ T.S, (γ s : ℝ) - Uo.card * dI := by
    rw [Finset.sum_sub_distrib, Finset.sum_sub_distrib, ← Finset.mul_sum, eU]
  have e2 : ∑ s ∈ T.S, (SCr * (((T.ms s).map fun e => w e / T.nm e).sum + cap * T.x s) +
      (if s ∈ Q then (dI : ℝ) else 0)) =
      SCr * (∑ s ∈ T.S, ((T.ms s).map fun e => w e / T.nm e).sum + cap * ∑ s ∈ T.S, (T.x s : ℝ)) + Q.card * dI := by
    rw [Finset.sum_add_distrib, eQ, ← Finset.mul_sum, Finset.sum_add_distrib, ← Finset.mul_sum]
  rw [e1, e2] at hsum
  have h5 : SCr * (∑ s ∈ T.S, ((T.ms s).map fun e => w e / T.nm e).sum + cap * ∑ s ∈ T.S, (T.x s : ℝ)) ≤
      SCr * (∑ e ∈ T.Mv, w e + cap * ∑ s ∈ T.S, (T.x s : ℝ)) :=
    mul_le_mul_of_nonneg_left (add_le_add_left hred _ |> fun h => by linarith) hSC.le
  have hUc' : (Uo.card : ℝ) ≤ NDL := by exact_mod_cast hUc
  have hdI0 : (0 : ℝ) ≤ dI := by positivity
  have hQd : (Q.card : ℝ) * dI ≤ SCr * (δ * Q.card) := by
    have h0 : (0 : ℝ) ≤ (Q.card : ℝ) := by positivity
    have := mul_le_mul_of_nonneg_left hδ h0
    nlinarith
  have hC : (Uo.card : ℝ) * dI ≤ NDL * dI := mul_le_mul_of_nonneg_right hUc' hdI0
  have h6 : SCr * (∑ e ∈ T.Mv, w e + cap * ∑ s ∈ T.S, (T.x s : ℝ) + δ * Q.card) =
      SCr * (∑ e ∈ T.Mv, w e + cap * ∑ s ∈ T.S, (T.x s : ℝ)) + SCr * (δ * Q.card) := by ring
  rw [h6]
  linarith

end CTree

#print axioms CTree.tree_lower_reader
