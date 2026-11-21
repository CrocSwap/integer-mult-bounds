/-
CallerThinDel (lane LEANTHIN, Nov 20).  THIN DELETION for LEAF-CHANNEL (cards/WILD/NOVEL/tribuild/TB.md §1(1), thinq/TQ.md §2).
Setting = CallerSGram's thin frame: columns ι, time slots β i < m (host stages have <= 2 columns, thin columns are rank-1
units in slots of their own), P = sgProd A B β m = -1 (full frame), Th = the thin columns.
Host-only frame = delete the thin columns from A and B (right multiplication by the 0/1 diagonal `hostD Th`).
(1) `stage_sub`    V_t - V_t^h = A E_t B^T with E_t = diag(1_{β i = t ∧ i ∈ Th})  (rank <= #thins in slot t).
(2) `prod_rank`    rank (P_t - P_t^h) <= #{thins in slots < t}.      (telescoping, rank-subadditivity)
(3) `thin_deletion` P = -1  ==>  rank (P_h + 1) <= |Th|.
(4) `S1_le_live`   finrank S1 <= #live slots when every non-live slot has zero columns (generalises `S1_le`).
(5) `leaf_channel_thin`  #Lf <= k + T:   Lf leaves (A,B vanish off one slot on HOST columns), k = #host slots, T = |Th|,
                         K-block of every host slot injective (lambda != -1), <= 2 columns per slot.
(6) non-vacuity `inst_thin`: k = 1 host stage (2 hub columns) + 1 thin slot, 1 leaf, over Q: bound 1 <= 1 + 1; hypotheses checked.
Kernel only.
-/
import Nov15.CallerLeafChannel

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace CallerLeaf
open Matrix Finset CallerSign Module

section thin
variable {K : Type*} [Field K] {ι : Type*} [Fintype ι] [DecidableEq ι] {n : ℕ}

/-- 0/1 diagonal keeping the host columns. -/
def hostD (Th : Finset ι) : Matrix ι ι K := diagonal fun i => if i ∈ Th then 0 else 1
/-- delete the thin columns. -/
def del (Th : Finset ι) (M : Matrix (Fin n) ι K) : Matrix (Fin n) ι K := M * hostD Th

theorem stage_sub (Th : Finset ι) (A B : Matrix (Fin n) ι K) (β : ι → ℕ) (t : ℕ) :
    sgStage A B β t - sgStage (del Th A) (del Th B) β t
      = A * diagonal (fun i => if β i = t ∧ i ∈ Th then (1 : K) else 0) * Bᵀ := by
  have hT : (del Th B)ᵀ = hostD Th * Bᵀ := by
    simp [del, hostD, Matrix.transpose_mul]
  have hE : (blkPi β t : Matrix ι ι K) - hostD Th * blkPi β t * hostD Th
      = diagonal (fun i => if β i = t ∧ i ∈ Th then (1 : K) else 0) := by
    simp only [blkPi, hostD, diagonal_mul_diagonal]
    ext i j
    simp only [Matrix.sub_apply, Matrix.diagonal_apply]
    by_cases hij : i = j
    · subst hij
      by_cases h1 : β i = t <;> by_cases h2 : i ∈ Th <;> simp [h1, h2]
    · simp [hij]
  rw [← hE]
  unfold sgStage
  rw [hT]
  simp only [del, Matrix.mul_sub, Matrix.sub_mul, Matrix.mul_assoc]
  abel

theorem rank_diag_thin (Th : Finset ι) (β : ι → ℕ) (t : ℕ) :
    (diagonal (fun i => if β i = t ∧ i ∈ Th then (1 : K) else 0) : Matrix ι ι K).rank
      = (Th.filter (fun i => β i = t)).card := by
  classical
  rw [Matrix.rank_diagonal, Fintype.card_subtype]
  congr 1
  ext i
  simp only [Finset.mem_filter, Finset.mem_univ, true_and]
  by_cases h1 : β i = t <;> by_cases h2 : i ∈ Th <;> simp [h1, h2]

theorem rank_add_le' {m o : Type*} [Fintype m] [Fintype o] [DecidableEq o] (M N : Matrix m o K) :
    (M + N).rank ≤ M.rank + N.rank := by
  unfold Matrix.rank
  calc finrank K (LinearMap.range (M + N).mulVecLin)
      ≤ finrank K (↥(LinearMap.range M.mulVecLin ⊔ LinearMap.range N.mulVecLin)) :=
        Submodule.finrank_mono (by
          rintro _ ⟨x, rfl⟩
          exact Submodule.mem_sup.2 ⟨M *ᵥ x, ⟨x, rfl⟩, N *ᵥ x, ⟨x, rfl⟩, by simp [add_mulVec]⟩)
    _ ≤ _ := Submodule.finrank_add_le_finrank_add_finrank _ _

theorem rank_neg' {m o : Type*} [Fintype m] [DecidableEq m] [Fintype o] [DecidableEq o] (M : Matrix m o K) :
    (-M).rank ≤ M.rank := by
  have : -M = (-1 : Matrix m m K) * M := by simp
  rw [this]; exact Matrix.rank_mul_le_right _ _

theorem prod_rank (Th : Finset ι) (A B : Matrix (Fin n) ι K) (β : ι → ℕ) (t : ℕ) :
    (sgProd A B β t - sgProd (del Th A) (del Th B) β t).rank ≤ (Th.filter (fun i => β i < t)).card := by
  induction t with
  | zero => simp [sgProd]
  | succ t ih =>
    have e : sgProd A B β (t + 1) - sgProd (del Th A) (del Th B) β (t + 1)
        = sgStage A B β t * (sgProd A B β t - sgProd (del Th A) (del Th B) β t)
          + (sgStage A B β t - sgStage (del Th A) (del Th B) β t) * sgProd (del Th A) (del Th B) β t := by
      simp only [sgProd, Matrix.mul_sub, Matrix.sub_mul]; abel
    have h1 : (sgStage A B β t * (sgProd A B β t - sgProd (del Th A) (del Th B) β t)).rank
        ≤ (Th.filter (fun i => β i < t)).card := (Matrix.rank_mul_le_right _ _).trans ih
    have h2 : ((sgStage A B β t - sgStage (del Th A) (del Th B) β t) * sgProd (del Th A) (del Th B) β t).rank
        ≤ (Th.filter (fun i => β i = t)).card := by
      refine (Matrix.rank_mul_le_left _ _).trans ?_
      rw [stage_sub, ← rank_diag_thin Th β t (K := K)]
      exact (Matrix.rank_mul_le_left _ _).trans (Matrix.rank_mul_le_right _ _)
    have hc : (Th.filter (fun i => β i < t + 1)).card
        = (Th.filter (fun i => β i < t)).card + (Th.filter (fun i => β i = t)).card := by
      rw [← Finset.card_union_of_disjoint]
      · congr 1; ext i; simp only [Finset.mem_union, Finset.mem_filter]
        by_cases h : i ∈ Th <;> simp [h] <;> omega
      · rw [Finset.disjoint_left]; intro i hi hj
        simp only [Finset.mem_filter] at hi hj; omega
    rw [e, hc]
    exact (rank_add_le' _ _).trans (Nat.add_le_add h1 h2)

/-- (3) THIN DELETION: with the full product `-1`, the host-only product has rank (P_h + 1) <= T. -/
theorem thin_deletion (Th : Finset ι) (A B : Matrix (Fin n) ι K) (β : ι → ℕ) (m : ℕ) (hβ : ∀ i, β i < m)
    (hP : sgProd A B β m = -1) :
    (sgProd (del Th A) (del Th B) β m + 1).rank ≤ Th.card := by
  have e : sgProd (del Th A) (del Th B) β m + 1 = -(sgProd A B β m - sgProd (del Th A) (del Th B) β m) := by
    rw [hP]; abel
  rw [e]
  exact (rank_neg' _).trans ((prod_rank Th A B β m).trans (Finset.card_le_card (Finset.filter_subset _ _)))


/-! ## (4) live slots -/
theorem dead_K {β : ι → ℕ} {Lf : Finset (Fin n)} {A B : Matrix (Fin n) ι K} {t : ℕ}
    (hd : ∀ r i, β i = t → A r i = 0 ∧ B r i = 0) {v : ι → K} (hv : v ∈ W β t) (i : ι) (hi : β i = t) :
    (sgK β (sgG A B) *ᵥ v) i = 2 * v i ∧ (GH Lf A B *ᵥ v) i = 0 := by
  constructor
  · simp only [Matrix.mulVec, dotProduct]
    have : ∀ j, sgK β (sgG A B) i j * v j = if i = j then 2 * v j else 0 := by
      intro j
      by_cases hj : β j = t
      · have hG : sgG A B i j = 0 := by
          simp only [sgG, Matrix.mul_apply, Matrix.transpose_apply]
          exact Finset.sum_eq_zero (fun r _ => by rw [(hd r j hj).1, mul_zero])
        have : sgK β (sgG A B) i j = if i = j then 2 else 0 := by
          by_cases hij : i = j
          · subst hij
            simp [sgK, sgDiag, sgUp, sgLow, Matrix.one_apply, hG]
          · have hne : ¬ (β i < β j) := by omega
            have hne2 : ¬ (β j < β i) := by omega
            simp [sgK, sgDiag, sgUp, sgLow, Matrix.one_apply, hG, hij, hne, hne2]
        rw [this]; split_ifs <;> simp
      · have := hv j hj
        simp [this]
    rw [Finset.sum_congr rfl (fun j _ => this j)]
    simp
  · simp only [Matrix.mulVec, dotProduct]
    apply Finset.sum_eq_zero
    intro j _
    by_cases hj : β j = t
    · have : GH Lf A B i j = 0 := by
        simp only [GH, hub, Matrix.mul_apply, Matrix.transpose_apply, Matrix.of_apply]
        exact Finset.sum_eq_zero (fun r _ => by
          by_cases hr : r ∈ Lf <;> simp [hr, (hd r j hj).1])
      rw [this, zero_mul]
    · rw [hv j hj, mul_zero]

theorem Zlo_dead {β : ι → ℕ} {Lf : Finset (Fin n)} {A B : Matrix (Fin n) ι K} {t : ℕ} (h2 : (2 : K) ≠ 0)
    (hd : ∀ r i, β i = t → A r i = 0 ∧ B r i = 0) : Zlo β Lf A B t = ⊥ := by
  rw [Submodule.eq_bot_iff]
  rintro v ⟨hw, hz⟩
  have hz' : blk β t ((sgK β (sgG A B) - GH Lf A B) *ᵥ v) = 0 := hz
  funext i
  by_cases hi : β i = t
  · have a := congrFun hz' i
    obtain ⟨k1, k2⟩ := dead_K (Lf := Lf) hd hw i hi
    simp only [blk_apply, hi, if_true, sub_mulVec, Pi.sub_apply, Pi.zero_apply, k1, k2, sub_zero] at a
    rcases mul_eq_zero.1 a with h | h
    · exact absurd h h2
    · exact h
  · exact hw i hi

theorem Zhi_dead {β : ι → ℕ} {Lf : Finset (Fin n)} {A B : Matrix (Fin n) ι K} {t : ℕ} (h2 : (2 : K) ≠ 0)
    (hd : ∀ r i, β i = t → A r i = 0 ∧ B r i = 0) : Zhi β Lf A B t = ⊥ := by
  rw [Submodule.eq_bot_iff]
  rintro v ⟨hw, hz⟩
  have hz' : blk β t ((sgK β (sgG A B) + GH Lf A B) *ᵥ v) = 0 := hz
  funext i
  by_cases hi : β i = t
  · have a := congrFun hz' i
    obtain ⟨k1, k2⟩ := dead_K (Lf := Lf) hd hw i hi
    simp only [blk_apply, hi, if_true, add_mulVec, Pi.add_apply, Pi.zero_apply, k1, k2, add_zero] at a
    rcases mul_eq_zero.1 a with h | h
    · exact absurd h h2
    · exact h
  · exact hw i hi

/-- (4) finrank S1 <= #live slots. -/
theorem S1_le_live {β : ι → ℕ} {m : ℕ} (hβ : ∀ i, β i < m) (Hs : Finset ℕ) (hHs : Hs ⊆ range m)
    {Lf : Finset (Fin n)} {A B : Matrix (Fin n) ι K}
    (h2 : (2 : K) ≠ 0) (hL : LeafSet Lf A B β) (hK : ∀ t ∈ Hs, KInj β (sgG A B) t)
    (hdead : ∀ t < m, t ∉ Hs → ∀ r i, β i = t → A r i = 0 ∧ B r i = 0)
    (hw : ∀ t < m, Fintype.card {i // β i = t} ≤ 2) : finrank K (S1 β Lf A B) ≤ Hs.card := by
  have hlo : finrank K (S1 β Lf A B) ≤ ∑ t ∈ range m, finrank K (Zlo β Lf A B t) := by
    apply count_le β m hβ
    intro c hc t ht hz
    refine ⟨blk_mem_W β t c, ?_⟩
    change blk β t ((sgK β (sgG A B) - GH Lf A B) *ᵥ blk β t c) = 0
    funext i
    simp only [blk_apply, sub_mulVec, Pi.sub_apply, Pi.zero_apply]
    split_ifs with hi
    · exact lower hL hc t hz i hi
    · rfl
  let β' : ι → ℕ := fun i => m - 1 - β i
  have hβ' : ∀ i, β' i < m := fun i => by have := hβ i; simp only [β']; omega
  have hhi : finrank K (S1 β Lf A B) ≤ ∑ t ∈ range m, finrank K (Zhi β Lf A B (m - 1 - t)) := by
    apply count_le β' m hβ'
    intro c hc t ht hz
    have hb : blk β' t c = blk β (m - 1 - t) c := by
      funext i; simp only [blk_apply, β']
      have := hβ i
      by_cases h : β i = m - 1 - t
      · rw [if_pos (by omega), if_pos h]
      · rw [if_neg (by omega), if_neg h]
    rw [hb]
    refine ⟨blk_mem_W β _ c, ?_⟩
    change blk β (m - 1 - t) ((sgK β (sgG A B) + GH Lf A B) *ᵥ blk β (m - 1 - t) c) = 0
    funext i
    simp only [blk_apply, add_mulVec, Pi.add_apply, Pi.zero_apply]
    split_ifs with hi
    · refine upper hL hc (m - 1 - t) (fun j hj => hz j ?_) i hi
      have := hβ j; simp only [β']; omega
    · rfl
  rw [Finset.sum_range_reflect (fun t => finrank K (Zhi β Lf A B t)) m] at hhi
  have hsum : ∑ t ∈ range m, (finrank K (Zlo β Lf A B t) + finrank K (Zhi β Lf A B t))
      ≤ ∑ t ∈ range m, (if t ∈ Hs then 2 else 0) := by
    apply Finset.sum_le_sum
    intro t ht
    have ht' := Finset.mem_range.1 ht
    by_cases hH : t ∈ Hs
    · rw [if_pos hH]
      exact (Z_sum_le h2 (hK t hH)).trans ((finrank_W_le β t).trans (hw t ht'))
    · rw [if_neg hH, Zlo_dead h2 (hdead t ht' hH), Zhi_dead h2 (hdead t ht' hH)]
      simp
  have hcount : ∑ t ∈ range m, (if t ∈ Hs then 2 else 0) = 2 * Hs.card := by
    rw [← Finset.sum_filter, Finset.sum_const, smul_eq_mul, mul_comm]
    congr 2
    ext t; simp only [Finset.mem_filter]
    exact ⟨fun h => h.2, fun h => ⟨hHs h, h⟩⟩
  rw [Finset.sum_add_distrib] at hsum
  omega


/-! ## (5) LEAF-CHANNEL with thin deletion -/
theorem del_apply (Th : Finset ι) (M : Matrix (Fin n) ι K) (r : Fin n) (i : ι) :
    del Th M r i = if i ∈ Th then 0 else M r i := by
  simp only [del, hostD, Matrix.mul_diagonal]
  by_cases h : i ∈ Th <;> simp [h]

theorem sgG_del (Th : Finset ι) (A B : Matrix (Fin n) ι K) {i j : ι} (hi : i ∉ Th) (hj : j ∉ Th) :
    sgG (del Th A) (del Th B) i j = sgG A B i j := by
  simp [sgG, Matrix.mul_apply, Matrix.transpose_apply, del_apply, hi, hj]

/-- the host K-block of a thin-free slot is unchanged by deletion (lambda != -1 transfers). -/
theorem kinj_host (Th : Finset ι) (A B : Matrix (Fin n) ι K) (β : ι → ℕ) (t : ℕ)
    (ht : ∀ i, β i = t → i ∉ Th) (hK : KInj β (sgG A B) t) : KInj β (sgG (del Th A) (del Th B)) t := by
  intro v hv hz
  apply hK v hv
  intro i hi
  rw [← hz i hi]
  simp only [Matrix.mulVec, dotProduct]
  apply Finset.sum_congr rfl
  intro j _
  by_cases hj : β j = t
  · have hG := sgG_del Th A B (ht i hi) (ht j hj)
    simp only [sgK, sgDiag, sgUp, sgLow, Matrix.add_apply, Matrix.sub_apply, Matrix.smul_apply,
      Matrix.of_apply, hG]
  · rw [hv j hj, mul_zero, mul_zero]

/-- (5) LEAF-CHANNEL + THIN DELETION: #leaves <= k + T.
`Th` = thin columns (T = |Th|), `Hs` = the k host slots (every host column lies in one), leaves are roles whose
host-column entries (A and B) vanish off one slot, the full frame has product -1, each host slot has an injective
K-block (lambda != -1) in the host-only frame, and every slot has <= 2 columns. -/
theorem leaf_channel_thin {β : ι → ℕ} {m : ℕ} (hβ : ∀ i, β i < m) (Th : Finset ι) (Hs : Finset ℕ)
    (hHs : Hs ⊆ range m) (hhost : ∀ i, i ∉ Th → β i ∈ Hs)
    {Lf : Finset (Fin n)} {A B : Matrix (Fin n) ι K} (h2 : (2 : K) ≠ 0)
    (hP : sgProd A B β m = -1)
    (hL : ∀ r ∈ Lf, ∃ s, ∀ i, i ∉ Th → β i ≠ s → A r i = 0 ∧ B r i = 0)
    (hK : ∀ t ∈ Hs, KInj β (sgG (del Th A) (del Th B)) t)
    (hw : ∀ t < m, Fintype.card {i // β i = t} ≤ 2) :
    Lf.card ≤ Hs.card + Th.card := by
  set A' := del Th A with hA'
  set B' := del Th B with hB'
  have hL' : LeafSet Lf A' B' β := by
    intro r hr
    obtain ⟨s, hs⟩ := hL r hr
    refine ⟨s, fun i hi => ?_⟩
    by_cases hT : i ∈ Th
    · simp [hA', hB', del_apply, hT]
    · simp only [hA', hB', del_apply, hT, if_false]; exact hs i hT hi
  have hdead : ∀ t < m, t ∉ Hs → ∀ r i, β i = t → A' r i = 0 ∧ B' r i = 0 := by
    intro t ht hH r i hi
    have : i ∈ Th := by
      by_contra hT
      exact hH (hi ▸ hhost i hT)
    simp [hA', hB', del_apply, this]
  have hS := (reduce_le (Lf := Lf) (A := A') (B := B') hβ h2).trans
    (S1_le_live hβ Hs hHs h2 hL' hK hdead hw)
  have hrank : (sgProd A' B' β m + 1).rank ≤ Th.card := thin_deletion Th A B β m hβ hP
  have e1 := Submodule.finrank_sup_add_finrank_inf_eq
    (LinearMap.ker (sgProd A' B' β m + 1).mulVecLin) (Lsp (K := K) Lf)
  have e2 := LinearMap.finrank_range_add_finrank_ker (sgProd A' B' β m + 1).mulVecLin
  have e3 := Submodule.finrank_le (LinearMap.ker (sgProd A' B' β m + 1).mulVecLin ⊔ Lsp (K := K) Lf)
  have e4 := card_le_finrank_Lsp (K := K) Lf
  have hr : (sgProd A' B' β m + 1).rank = finrank K (LinearMap.range (sgProd A' B' β m + 1).mulVecLin) := rfl
  simp only [Module.finrank_fintype_fun_eq_card, Fintype.card_fin] at e2 e3
  omega

/-! ## (6) non-vacuity: CallerThin's one-host + one-thin frame (k = 1 host slot {0,1}, T = 1 thin column 2, n = 1 leaf). -/
def A1 : Matrix (Fin 1) (Fin 3) ℚ := !![1, 0, 1]
def B1 : Matrix (Fin 1) (Fin 3) ℚ := !![1, 0, -3/2]
def beta1 : Fin 3 → ℕ := ![0, 0, 1]

theorem prod1 : sgProd A1 B1 beta1 2 = -1 := by
  ext i j
  fin_cases i; fin_cases j
  simp [sgProd, sgStage, blkPi, A1, B1, beta1, Matrix.mul_apply, Fin.sum_univ_succ, Matrix.diagonal_apply,
    Matrix.vecMul, dotProduct, Matrix.transpose_apply, Matrix.add_apply, Matrix.one_apply]
  norm_num

theorem inst_kinj1 : ∀ t ∈ ({0} : Finset ℕ), KInj beta1 (sgG (del ({2} : Finset (Fin 3)) A1) (del ({2} : Finset (Fin 3)) B1)) t := by
  intro t ht v hv hz
  have ht0 : t = 0 := by simpa using ht
  subst ht0
  have hv' : ∀ i, beta1 i ≠ 0 → v i = 0 := hv
  have v2 := hv' 2 (by simp [beta1])
  have e0 := hz 0 (by simp [beta1])
  have e1 := hz 1 (by simp [beta1])
  simp [sgK, sgG, sgDiag, sgUp, sgLow, A1, B1, beta1, del_apply, Matrix.mulVec, dotProduct,
    Fin.sum_univ_succ, Matrix.mul_apply, Matrix.one_apply, v2] at e0 e1
  funext j; fin_cases j
  · rcases e0 with h | h
    · norm_num at h
    · simpa using h
  · simpa using e1
  · simpa using v2

/-- the theorem applies: 1 leaf <= 1 host slot + 1 thin. -/
theorem inst_thin : (Finset.univ : Finset (Fin 1)).card ≤ ({0} : Finset ℕ).card + ({2} : Finset (Fin 3)).card :=
  leaf_channel_thin (β := beta1) (m := 2) (fun i => by fin_cases i <;> simp [beta1]) {2} {0}
    (by intro t ht; simp at ht; simp [ht])
    (by intro i hi; fin_cases i <;> simp_all [beta1]) (A := A1) (B := B1) (by norm_num) prod1
    (fun r _ => ⟨0, fun i hi hne => by fin_cases i <;> simp_all [beta1]⟩) inst_kinj1
    (by intro t ht; interval_cases t <;> decide)

end thin
end CallerLeaf

#print axioms CallerLeaf.thin_deletion
#print axioms CallerLeaf.S1_le_live
#print axioms CallerLeaf.kinj_host
#print axioms CallerLeaf.leaf_channel_thin
#print axioms CallerLeaf.inst_thin
