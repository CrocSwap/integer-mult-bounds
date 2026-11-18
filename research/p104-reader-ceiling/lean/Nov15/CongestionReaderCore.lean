import Nov15.CongestionTreePiece

/-!
CONGESTION-READER-CORE.  Abstract half of the per-reader endpoint charge (CG2 + AUDIT-CG2 + EP3).
Part 1 (registers, EP3): the residual `rho r = ex r - sum of path c2` of a monotone register is a sum of positive parts of the `beta`-variation,
 `beta a = g a + g (9-a)`; a Z register (born 0) or a V register born at dim 1 that STOPS at a dim in [2,7] has `rho >= beta(7) - beta(8) = delta`.
Part 2 (payers): if distinct readers are tied to distinct registers with `rho >= delta`, then `regs + delta * |Q| <= sum ex + (#mixed) sigma`.
Part 3 (trees): `tree_lower_reader`: the line bound of `tree_lower` with the per-reader allowance `dI <= delta` for tied readers (set Q) and the
 allowance subtracted for the <= 15 untied readers (set Uo: <= 5 mixed + <= 10 owned last movers, AUDIT-CG2 F1).
No sorry, no native_decide.
-/
namespace CongestionReader
open Finset CongestionI3Dual CongestionNative CTree

/-! ### 1. residual of a register -/

def beta (g : ℝ → ℝ) (a : ℝ) : ℝ := g a + g (9 - a)

theorem h9_sub_k0 (g : ℝ → ℝ) (a b : ℝ) : h9 g a b - k0 g a b = beta g b - beta g a := by
  unfold h9 k0 beta; ring

theorem tel_Ico (u : ℕ → ℝ) (j : ℕ) : ∀ n, j ≤ n → ∑ i ∈ Finset.Ico j n, (u i - u (i + 1)) = u j - u n := by
  intro n hn
  induction n, hn using Nat.le_induction with
  | base => simp
  | succ n hn ih => rw [Finset.sum_Ico_succ_top hn, ih]; ring

/-- V-class (ends at 9): the residual is at least the net rise of `beta` from birth to any stop. -/
theorem resid_V (g : ℝ → ℝ) (hg0 : g 0 = 0) (d : ℕ → ℝ) (n : ℕ) (he : d n = 9) (j : ℕ) (hj : j ≤ n) :
    beta g (d j) - beta g (d 0) ≤ ex g d n - ∑ i ∈ range n, c2 g (d i) (d (i + 1)) := by
  have h1 := sum_h9_eq g hg0 d n he
  have hf : ∀ i, 0 ≤ h9 g (d i) (d (i + 1)) - c2 g (d i) (d (i + 1)) := fun i => by
    have : c2 g (d i) (d (i + 1)) ≤ h9 g (d i) (d (i + 1)) := min_le_left _ _
    linarith
  have hu : ∀ i, beta g (d (i + 1)) - beta g (d i) ≤ h9 g (d i) (d (i + 1)) - c2 g (d i) (d (i + 1)) := fun i => by
    have := h9_sub_k0 g (d i) (d (i + 1))
    have h2 : c2 g (d i) (d (i + 1)) ≤ k0 g (d i) (d (i + 1)) := min_le_right _ _
    linarith
  have hsub : ∑ i ∈ range j, (h9 g (d i) (d (i + 1)) - c2 g (d i) (d (i + 1))) ≤
      ∑ i ∈ range n, (h9 g (d i) (d (i + 1)) - c2 g (d i) (d (i + 1))) :=
    Finset.sum_le_sum_of_subset_of_nonneg (Finset.range_subset_range.2 hj) (fun i _ _ => hf i)
  have ht : ∑ i ∈ range j, (beta g (d (i + 1)) - beta g (d i)) = beta g (d j) - beta g (d 0) :=
    Finset.sum_range_sub (fun i => beta g (d i)) j
  have hle : ∑ i ∈ range j, (beta g (d (i + 1)) - beta g (d i)) ≤
      ∑ i ∈ range j, (h9 g (d i) (d (i + 1)) - c2 g (d i) (d (i + 1))) := Finset.sum_le_sum fun i _ => hu i
  have e : ∑ i ∈ range n, (h9 g (d i) (d (i + 1)) - c2 g (d i) (d (i + 1))) =
      ex g d n - ∑ i ∈ range n, c2 g (d i) (d (i + 1)) := by
    rw [Finset.sum_sub_distrib, h1]
  linarith

/-- Z-class (born at 0): the residual is at least the net fall of `beta` from any stop to the end. -/
theorem resid_Z (g : ℝ → ℝ) (hg0 : g 0 = 0) (d : ℕ → ℝ) (n : ℕ) (h0 : d 0 = 0) (j : ℕ) (hj : j ≤ n) :
    beta g (d j) - beta g (d n) ≤ ex g d n - ∑ i ∈ range n, c2 g (d i) (d (i + 1)) := by
  have h1 := sum_k0_eq g hg0 d n h0
  have hf : ∀ i, 0 ≤ k0 g (d i) (d (i + 1)) - c2 g (d i) (d (i + 1)) := fun i => by
    have : c2 g (d i) (d (i + 1)) ≤ k0 g (d i) (d (i + 1)) := min_le_right _ _
    linarith
  have hu : ∀ i, beta g (d i) - beta g (d (i + 1)) ≤ k0 g (d i) (d (i + 1)) - c2 g (d i) (d (i + 1)) := fun i => by
    have := h9_sub_k0 g (d i) (d (i + 1))
    have h2 : c2 g (d i) (d (i + 1)) ≤ h9 g (d i) (d (i + 1)) := min_le_left _ _
    linarith
  have hsub : ∑ i ∈ Finset.Ico j n, (k0 g (d i) (d (i + 1)) - c2 g (d i) (d (i + 1))) ≤
      ∑ i ∈ range n, (k0 g (d i) (d (i + 1)) - c2 g (d i) (d (i + 1))) := by
    apply Finset.sum_le_sum_of_subset_of_nonneg _ (fun i _ _ => hf i)
    intro i hi
    rw [Finset.mem_Ico] at hi
    exact Finset.mem_range.2 hi.2
  have ht := tel_Ico (fun i => beta g (d i)) j n hj
  have hle : ∑ i ∈ Finset.Ico j n, (beta g (d i) - beta g (d (i + 1))) ≤
      ∑ i ∈ Finset.Ico j n, (k0 g (d i) (d (i + 1)) - c2 g (d i) (d (i + 1))) := Finset.sum_le_sum fun i _ => hu i
  have e : ∑ i ∈ range n, (k0 g (d i) (d (i + 1)) - c2 g (d i) (d (i + 1))) =
      ex g d n - ∑ i ∈ range n, c2 g (d i) (d (i + 1)) := by
    rw [Finset.sum_sub_distrib, h1]
  linarith

/-! ### 2. the numeric core: beta(a) >= beta(7) on [2,7], beta(1) = beta(8) -/

/-- `delta s = beta(7) - beta(8)` for the price `gs s`. -/
noncomputable def deltaF (s : ℝ) : ℝ := (7 : ℝ) ^ s + (2 : ℝ) ^ s - (8 : ℝ) ^ s - 1

theorem delta_eq (s : ℝ) : beta (gs s) 7 - beta (gs s) 8 = deltaF s := by
  unfold beta deltaF gs
  norm_num
  ring

theorem beta_ge (s : ℝ) (hs0 : 0 ≤ s) (hs1 : s ≤ 1) (a : ℝ) (ha : 2 ≤ a) (ha' : a ≤ 7) :
    beta (gs s) 7 ≤ beta (gs s) a := by
  have hc := (Real.concaveOn_rpow hs0 hs1).2
  have e1 : a = ((7 - a) / 5) * 2 + ((a - 2) / 5) * 7 := by ring
  have e2 : 9 - a = ((a - 2) / 5) * 2 + ((7 - a) / 5) * 7 := by ring
  have c1 := hc (x := 2) (y := 7) (by norm_num : (2 : ℝ) ∈ Set.Ici (0 : ℝ)) (by norm_num : (7 : ℝ) ∈ Set.Ici (0 : ℝ))
    (a := (7 - a) / 5) (b := (a - 2) / 5) (by linarith) (by linarith) (by ring)
  have c2' := hc (x := 2) (y := 7) (by norm_num : (2 : ℝ) ∈ Set.Ici (0 : ℝ)) (by norm_num : (7 : ℝ) ∈ Set.Ici (0 : ℝ))
    (a := (a - 2) / 5) (b := (7 - a) / 5) (by linarith) (by linarith) (by ring)
  simp only [smul_eq_mul] at c1 c2'
  rw [← e1] at c1
  rw [← e2] at c2'
  have p1 : 0 < a := by linarith
  have p2 : 0 < 9 - a := by linarith
  unfold beta gs
  rw [if_pos p1, if_pos p2, if_pos (by norm_num : (0 : ℝ) < 7), if_pos (by norm_num : (0 : ℝ) < 9 - 7)]
  norm_num
  linarith

theorem beta_one_eight (s : ℝ) : beta (gs s) 1 = beta (gs s) 8 := by
  unfold beta gs
  norm_num
  ring

/-! ### 3. tied registers have residual >= delta -/

/-- the residual of register `r` -/
noncomputable def rho {ι : Type*} (s : ℝ) (n : ι → ℕ) (d : ι → ℕ → ℕ) (r : ι) : ℝ :=
  ex (gs s) (lev d r) (n r) - ∑ i ∈ range (n r), c2 (gs s) (lev d r i) (lev d r (i + 1))

/-- A register TIED to a reader (the payer of CG2): either Z-class (born at {0}) ending at dim 8 with a stop at a dim in [2,7], or V-class born at
dim 1 ending at 9 with a stop in [2,7].  Its residual is at least `delta`.  (Lean-proved part of CG2 sec. 2; the existence of the tied register
is the hypothesis `hTied` of the theorems.) -/
def Tied {ι : Type*} (n : ι → ℕ) (d : ι → ℕ → ℕ) (r : ι) : Prop :=
  (d r 0 = 0 ∧ d r (n r) = 8 ∨ d r 0 = 1 ∧ d r (n r) = 9) ∧ ∃ j ≤ n r, 2 ≤ d r j ∧ d r j ≤ 7

theorem tied_rho {ι : Type*} (s : ℝ) (hs0 : 0 ≤ s) (hs1 : s ≤ 1) (n : ι → ℕ) (d : ι → ℕ → ℕ) (r : ι)
    (h : Tied n d r) : deltaF s ≤ rho s n d r := by
  obtain ⟨hc, j, hj, hj2, hj7⟩ := h
  have hb := beta_ge s hs0 hs1 (d r j) (by exact_mod_cast hj2) (by exact_mod_cast hj7)
  rw [← sub_nonneg] at hb
  have hb' : 0 ≤ beta (gs s) (lev d r j) - beta (gs s) 7 := hb
  have e := delta_eq s
  unfold rho
  rcases hc with ⟨h0, h8⟩ | ⟨h1, h9⟩
  · have := resid_Z (gs s) (gs_zero s) (lev d r) (n r) (by simp [lev, h0]) j hj
    have h8' : lev d r (n r) = 8 := by simp [lev, h8]
    rw [h8'] at this
    linarith
  · have := resid_V (gs s) (gs_zero s) (lev d r) (n r) (by simp [lev, h9]) j hj
    have h1' : lev d r 0 = 1 := by simp [lev, h1]
    rw [h1'] at this
    have := beta_one_eight s
    linarith

/-! ### 4. summing over registers with payers -/

section Pay
variable {ι : Type*} [DecidableEq ι]

theorem resid_ge (s : ℝ) (R : Finset ι) (n : ι → ℕ) (d : ι → ℕ → ℕ)
    (hmono : ∀ r ∈ R, ∀ i < n r, d r i ≤ d r (i + 1)) (hd9 : ∀ r ∈ R, d r (n r) ≤ 9)
    (σ : ℝ) (hσ0 : 0 ≤ σ) (hσ : ∀ a b : ℕ, 1 ≤ a → a ≤ b → b ≤ 8 → c2 (gs s) (a : ℝ) (b : ℝ) ≤ σ) :
    ∀ r ∈ R, -(if Mixed d n r then σ else 0) ≤ rho s n d r := by
  intro r hr
  have h1 := sum_c2_le (gs s) (lev d r) (n r)
  have hle : ∀ k ≤ n r, d r 0 ≤ d r k := by
    intro k
    induction k with
    | zero => intro _; exact le_refl _
    | succ k ih => intro hk; exact le_trans (ih (by omega)) (hmono r hr k (by omega))
  have h0e := hle (n r) (le_refl _)
  unfold rho
  by_cases hmx : Mixed d n r
  · rw [if_pos hmx]
    have := hσ (d r 0) (d r (n r)) hmx.1 h0e hmx.2
    simp only [lev] at h1 ⊢
    linarith
  · rw [if_neg hmx]
    have hne : d r (n r) = 9 ∨ d r 0 = 0 := by
      unfold Mixed at hmx
      have := hd9 r hr
      omega
    have h2 := c2_total_nonmixed (gs s) (gs_zero s) (lev d r 0) (lev d r (n r))
      (by
        rcases hne with h | h
        · left; simp [lev, h]
        · right; simp [lev, h])
    simp only [lev] at h1 h2 ⊢
    linarith

/-- **payers**: distinct readers `t in Q` tied to distinct registers `pi t` of residual >= delta.  Then
`sum of path c2 + delta |Q| <= sum ex + m sigma`. -/
theorem sum_c2_pay {κ : Type*} [DecidableEq κ] (s : ℝ) (R : Finset ι) (n : ι → ℕ) (d : ι → ℕ → ℕ)
    (hmono : ∀ r ∈ R, ∀ i < n r, d r i ≤ d r (i + 1)) (hd9 : ∀ r ∈ R, d r (n r) ≤ 9)
    (m : ℕ) (hm : (R.filter fun r => Mixed d n r).card ≤ m) (σ : ℝ) (hσ0 : 0 ≤ σ)
    (hσ : ∀ a b : ℕ, 1 ≤ a → a ≤ b → b ≤ 8 → c2 (gs s) (a : ℝ) (b : ℝ) ≤ σ)
    (δ : ℝ) (hδ0 : 0 ≤ δ) (Q : Finset κ) (π : κ → ι) (hπR : ∀ t ∈ Q, π t ∈ R) (hπinj : Set.InjOn π Q)
    (hπρ : ∀ t ∈ Q, δ ≤ rho s n d (π t)) :
    ∑ r ∈ R, ∑ i ∈ range (n r), c2 (gs s) (lev d r i) (lev d r (i + 1)) + δ * Q.card ≤
      ∑ r ∈ R, ex (gs s) (lev d r) (n r) + m * σ := by
  classical
  have hg := resid_ge s R n d hmono hd9 σ hσ0 hσ
  have hstep : ∀ r ∈ R, -(if Mixed d n r then σ else 0) + (if r ∈ Q.image π then δ else 0) ≤ rho s n d r := by
    intro r hr
    by_cases hq : r ∈ Q.image π
    · rw [if_pos hq]
      obtain ⟨t, ht, rfl⟩ := Finset.mem_image.1 hq
      have := hπρ t ht
      have : (0 : ℝ) ≤ (if Mixed d n (π t) then σ else 0) := by split_ifs <;> linarith
      linarith
    · rw [if_neg hq]; simpa using hg r hr
  have hsum := Finset.sum_le_sum hstep
  rw [Finset.sum_add_distrib, Finset.sum_neg_distrib] at hsum
  have e1 : ∑ r ∈ R, (if r ∈ Q.image π then δ else 0) = δ * Q.card := by
    rw [Finset.sum_ite_mem, Finset.inter_eq_right.2 (by
      intro r hr; obtain ⟨t, ht, rfl⟩ := Finset.mem_image.1 hr; exact hπR t ht),
      Finset.sum_const, nsmul_eq_mul, Finset.card_image_of_injOn hπinj]
    ring
  have e2 : ∑ r ∈ R, (if Mixed d n r then σ else 0) ≤ m * σ := by
    have : ∑ r ∈ R, (if Mixed d n r then σ else 0) = ((R.filter fun r => Mixed d n r).card : ℝ) * σ := by
      rw [← Finset.sum_filter]; simp
    rw [this]
    have hm' : ((R.filter fun r => Mixed d n r).card : ℝ) ≤ m := by exact_mod_cast hm
    nlinarith
  have e3 : ∑ r ∈ R, rho s n d r = ∑ r ∈ R, ex (gs s) (lev d r) (n r) -
      ∑ r ∈ R, ∑ i ∈ range (n r), c2 (gs s) (lev d r i) (lev d r (i + 1)) := by
    unfold rho; rw [Finset.sum_sub_distrib]
  linarith

end Pay

end CongestionReader

#print axioms CongestionReader.resid_V
#print axioms CongestionReader.resid_Z
#print axioms CongestionReader.beta_ge
#print axioms CongestionReader.tied_rho
#print axioms CongestionReader.sum_c2_pay
