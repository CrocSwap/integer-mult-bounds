/-
CallerThin (lane THINQ).  Caller laws for the Q >= 1 (thin-unit) branch, in CallerSGram's general frame.
Setting: CallerSGram's frame over a field, columns `iota` with ANY time labelling `beta` (stages of any width):
rank-2 HOST stages and rank-1 THIN units (QUERY) are just blocks of width 2 and 1.  P = prod_t (1 + A Pi_t B^T) = -1.
(1) thin_count      : one host block with invertible K-block  ==>  n + 2 <= |iota|.   (n = 2k-2+Q, |iota| = 2k+T  ==>  Q <= T.)
(2) thin_blk_unit   : |iota| = n + 2 (T = Q, no excess thin), host blocks s /= t with invertible K-blocks
                      ==> the Gram block G_st (host columns) is invertible.  (rank K <= 2 is sgForward, unchanged.)
(3) rc2_pair_thin   : CALLERCUT's RC2 pair form holds verbatim in the thin frame (any piece data on host-stage masks).
(4) leaf_eig        : if B^T x vanishes on every column outside time slot s, then V_s x = -x.
(5) leaf_rank       : K's stage-s block nondegenerate (lambda_s /= -1) and the roles F have zero B-rows on every
                      column outside stage s except a column set Th  ==>  |F| <= |Th|.   (LEAF-RANK / LOCAL COUNT)
(6) non-vacuity     : CallerSGram's k = 3 instance (no thins) and a one-host + one-thin frame over Q (n = 1, a leaf).
-/
import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.FinCases
import Nov15.CallerSGram
import Nov15.CallerRC2

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace CallerThin
open Matrix Finset CallerSign

variable {K : Type*} [Field K] {ι : Type*} [Fintype ι] [DecidableEq ι] {n : ℕ}

/-! ## (1) count: Q <= T -/
theorem thin_count (A B : Matrix (Fin n) ι K) (β : ι → ℕ) (k : ℕ) (h2 : (2 : K) ≠ 0)
    (hβ : ∀ i, β i < k) (hP : sgProd A B β k = -1) (es : Fin 2 → ι)
    (hs : IsUnit ((sgK β (sgG A B)).submatrix es es).det) : n + 2 ≤ Fintype.card ι := by
  have hF := (sgForward A B β k h2 hβ hP).1
  have h1 : ((sgK β (sgG A B)).submatrix es es).rank = 2 := by
    have := Matrix.rank_of_isUnit _ ((Matrix.isUnit_iff_isUnit_det _).mpr hs)
    simpa using this
  have h3 := Matrix.rank_submatrix_le (sgK β (sgG A B)) es es
  omega

/-! ## (2) off-diagonal host blocks -/
theorem thin_K_blk_unit (M : Matrix ι ι K) (hr : M.rank ≤ 2) (es et : Fin 2 → ι)
    (hs : IsUnit (M.submatrix es es).det) (ht : IsUnit (M.submatrix et et).det) :
    IsUnit (M.submatrix es et).det := by
  have hF : fromBlocks (M.submatrix es es) (M.submatrix es et) (M.submatrix et es) (M.submatrix et et)
      = M.submatrix (Sum.elim es et) (Sum.elim es et) := by
    ext (i | i) (j | j) <;> simp
  have hrank : (fromBlocks (M.submatrix es es) (M.submatrix es et) (M.submatrix et es)
      (M.submatrix et et)).rank ≤ Fintype.card (Fin 2) := by
    rw [hF]; simpa using (Matrix.rank_submatrix_le M _ _).trans hr
  have h := schur_core' _ _ _ _ hs hrank
  have hd : (M.submatrix et et).det
      = (M.submatrix et es).det * ((M.submatrix es es)⁻¹).det * (M.submatrix es et).det := by
    rw [h, Matrix.det_mul, Matrix.det_mul]
  rw [hd] at ht
  exact (IsUnit.mul_iff.mp ht).2

theorem thin_G_blk_unit (A B : Matrix (Fin n) ι K) (β : ι → ℕ) (k : ℕ) (h2 : (2 : K) ≠ 0)
    (hβ : ∀ i, β i < k) (hP : sgProd A B β k = -1) (hn : n + 2 = Fintype.card ι)
    (es et : Fin 2 → ι) (s t : ℕ) (hes : ∀ a, β (es a) = s) (het : ∀ a, β (et a) = t) (hst : s ≠ t)
    (hs : IsUnit ((sgK β (sgG A B)).submatrix es es).det)
    (ht : IsUnit ((sgK β (sgG A B)).submatrix et et).det) :
    IsUnit ((sgG A B).submatrix es et).det := by
  have hF := (sgForward A B β k h2 hβ hP).1
  have hr : (sgK β (sgG A B)).rank ≤ 2 := by omega
  have hu := thin_K_blk_unit _ hr es et hs ht
  rcases lt_or_gt_of_ne hst with h | h
  · have e : (sgG A B).submatrix es et = (sgK β (sgG A B)).submatrix es et := by
      ext a b
      have h1 : β (es a) < β (et b) := by rw [hes, het]; exact h
      have hne : es a ≠ et b := fun e => by rw [e] at h1; exact lt_irrefl _ h1
      simp [sgK, sgDiag, sgUp, sgLow, one_apply, hne, h1, h1.ne, not_lt.mpr h1.le]
    rw [e]; exact hu
  · have e : (sgG A B).submatrix es et = - (sgK β (sgG A B)).submatrix es et := by
      ext a b
      have h1 : β (et b) < β (es a) := by rw [hes, het]; exact h
      have hne : es a ≠ et b := fun e => by rw [e] at h1; exact lt_irrefl _ h1
      simp [sgK, sgDiag, sgUp, sgLow, one_apply, hne, h1, h1.ne', not_lt.mpr h1.le]
    rw [e, Matrix.det_neg]
    exact (IsUnit.pow _ (IsUnit.neg isUnit_one)).mul hu

/-! ## (3) RC2 in the thin frame.  `hc s` = the two columns of host stage s (time `ht s`). -/
open Classical in
noncomputable def hmask {k : ℕ} (A B : Matrix (Fin n) ι K) (hc : Fin k → Fin 2 → ι) (r : Fin n) : Finset (Fin k) :=
  Finset.univ.filter fun s => ∃ a, A r (hc s a) ≠ 0 ∨ B r (hc s a) ≠ 0

theorem rc2_pair_thin {k kt : ℕ} (A B : Matrix (Fin n) ι K) (β : ι → ℕ) (h2 : (2 : K) ≠ 0)
    (hβ : ∀ i, β i < kt) (hP : sgProd A B β kt = -1) (hn : n + 2 = Fintype.card ι)
    (hc : Fin k → Fin 2 → ι) (tm : Fin k → ℕ) (htm : ∀ s a, β (hc s a) = tm s) (hinj : Function.Injective tm)
    (hdiag : ∀ s, IsUnit ((sgK β (sgG A B)).submatrix (hc s) (hc s)).det)
    (P : Pieces (hmask A B hc) (fun r s a => B r (hc s a)))
    (s t : Fin k) (hst : s ≠ t) (l : ℕ) (hl : 2 ≤ l) :
    2 ≤ rcDeep (hmask A B hc) P.pc s t l + rcShal (hmask A B hc) P.pc s t l := by
  classical
  refine rc2_pair (hmask A B hc) (fun r s a => B r (hc s a)) (fun r s a => A r (hc s a)) ?_ ?_ P s t hst l hl ?_
  · intro r s hs a
    by_contra h
    exact hs (Finset.mem_filter.mpr ⟨Finset.mem_univ _, a, Or.inr h⟩)
  · intro r s hs a
    by_contra h
    exact hs (Finset.mem_filter.mpr ⟨Finset.mem_univ _, a, Or.inl h⟩)
  · have e : gBlk (fun r s a => B r (hc s a)) (fun r s a => A r (hc s a)) s t = (sgG A B).submatrix (hc s) (hc t) := by
      ext a b
      simp [gBlk, sgG, Matrix.mul_apply, Matrix.transpose_apply]
    rw [e]
    exact thin_G_blk_unit A B β kt h2 hβ hP hn (hc s) (hc t) (tm s) (tm t) (htm s) (htm t)
      (fun h => hst (hinj h)) (hdiag s) (hdiag t)

/-! ## (4) leaf lemma -/
theorem stage_fix (A B : Matrix (Fin n) ι K) (β : ι → ℕ) (t : ℕ) (x : Fin n → K)
    (hx : ∀ i, β i = t → (Bᵀ *ᵥ x) i = 0) : (sgStage A B β t) *ᵥ x = x := by
  have hz : (blkPi β t * Bᵀ) *ᵥ x = 0 := by
    rw [← Matrix.mulVec_mulVec]
    ext i
    simp only [blkPi, Matrix.mulVec_diagonal, Pi.zero_apply]
    by_cases h : β i = t
    · simp [h, hx i h]
    · simp [h]
  simp only [sgStage, Matrix.add_mulVec, Matrix.one_mulVec]
  rw [Matrix.mul_assoc, ← Matrix.mulVec_mulVec, hz, Matrix.mulVec_zero, add_zero]

theorem leaf_eig (A B : Matrix (Fin n) ι K) (β : ι → ℕ) (k s : ℕ) (hs : s < k)
    (hP : sgProd A B β k = -1) (x : Fin n → K) (hx : ∀ i, β i ≠ s → (Bᵀ *ᵥ x) i = 0) :
    (sgStage A B β s) *ᵥ x = -x := by
  -- before s: x fixed
  have hpre : ∀ t, t ≤ s → (sgProd A B β t) *ᵥ x = x := by
    intro t ht
    induction t with
    | zero => simp [sgProd]
    | succ t ih =>
      rw [sgProd, ← Matrix.mulVec_mulVec, ih (by omega)]
      exact stage_fix A B β t x (fun i hi => hx i (by omega))
  -- after s: P_t = L P_{s+1}, L x = x
  have hpost : ∀ t, s + 1 ≤ t → ∃ L : Matrix (Fin n) (Fin n) K,
      sgProd A B β t = L * sgProd A B β (s + 1) ∧ L *ᵥ x = x := by
    intro t ht
    induction t with
    | zero => omega
    | succ t ih =>
      rcases Nat.eq_or_lt_of_le ht with h | h
      · refine ⟨1, ?_, by simp⟩
        rw [← h]; simp
      · obtain ⟨L, hL, hLx⟩ := ih (by omega)
        refine ⟨sgStage A B β t * L, ?_, ?_⟩
        · rw [sgProd, hL, Matrix.mul_assoc]
        · rw [← Matrix.mulVec_mulVec, hLx]
          exact stage_fix A B β t x (fun i hi => hx i (by omega))
  obtain ⟨L, hL, hLx⟩ := hpost k (by omega)
  have hPs : sgProd A B β (s + 1) *ᵥ x = sgStage A B β s *ᵥ x := by
    rw [sgProd, ← Matrix.mulVec_mulVec, hpre s le_rfl]
  have hLP : L * sgProd A B β (s + 1) = -1 := by rw [← hL, hP]
  have hPL : sgProd A B β (s + 1) * L = -1 := by
    have h1 : L * (-sgProd A B β (s + 1)) = 1 := by rw [Matrix.mul_neg, hLP, neg_neg]
    have h2 := mul_eq_one_comm.mp h1
    rw [Matrix.neg_mul] at h2
    exact neg_eq_iff_eq_neg.mp h2
  have e1 : L *ᵥ (sgStage A B β s *ᵥ x) = -x := by
    rw [← hPs, Matrix.mulVec_mulVec, hLP, Matrix.neg_mulVec, Matrix.one_mulVec]
  have e2 : L *ᵥ (sgStage A B β s *ᵥ x + x) = 0 := by
    rw [Matrix.mulVec_add, e1, hLx, neg_add_cancel]
  have e3 : sgStage A B β s *ᵥ x + x = 0 := by
    have := congrArg (fun v => sgProd A B β (s + 1) *ᵥ v) e2
    simp only [Matrix.mulVec_mulVec, hPL, Matrix.neg_mulVec, Matrix.one_mulVec, Matrix.mulVec_zero] at this
    exact neg_eq_zero.mp this
  exact eq_neg_of_add_eq_zero_left e3

/-- `lambda_s /= -1` in block-free form: no nonzero `w` supported on time slot `s` is killed by `K` on slot `s`. -/
def KNondeg (β : ι → ℕ) (G : Matrix ι ι K) (s : ℕ) : Prop :=
  ∀ w : ι → K, (∀ j, β j ≠ s → w j = 0) → (∀ i, β i = s → (sgK β G *ᵥ w) i = 0) → w = 0

theorem leaf_zero (A B : Matrix (Fin n) ι K) (β : ι → ℕ) (k s : ℕ) (hs : s < k) (h2 : (2 : K) ≠ 0)
    (hP : sgProd A B β k = -1) (hK : KNondeg β (sgG A B) s)
    (x : Fin n → K) (hx : ∀ i, β i ≠ s → (Bᵀ *ᵥ x) i = 0) : x = 0 := by
  have hV := leaf_eig A B β k s hs hP x hx
  obtain ⟨w, hw⟩ : ∃ w : ι → K, w = Bᵀ *ᵥ x := ⟨_, rfl⟩
  have hx' : ∀ i, β i ≠ s → w i = 0 := by rw [hw]; exact hx
  have hz : (blkPi β s : Matrix ι ι K) *ᵥ w = w := by
    ext i
    simp only [blkPi, Matrix.mulVec_diagonal]
    by_cases h : β i = s
    · simp [h]
    · simp [h, hx' i h]
  have h1 : (sgStage A B β s) *ᵥ x = x + A *ᵥ w := by
    simp only [sgStage, Matrix.add_mulVec, Matrix.one_mulVec]
    rw [← Matrix.mulVec_mulVec, ← Matrix.mulVec_mulVec, ← hw, hz]
  have hAw : A *ᵥ w = -(2 : K) • x := by
    rw [h1] at hV
    have : A *ᵥ w = -x - x := by
      calc A *ᵥ w = (x + A *ᵥ w) - x := by abel
        _ = -x - x := by rw [hV]
    rw [this]; module
  have hG : sgG A B *ᵥ w = -(2 : K) • w := by
    rw [sgG, ← Matrix.mulVec_mulVec, hAw, Matrix.mulVec_smul, ← hw]
  have hw0 : w = 0 := by
    apply hK w hx'
    intro i hi
    have hd : (sgDiag β (sgG A B) *ᵥ w) i = (sgG A B *ᵥ w) i := by
      simp only [Matrix.mulVec, dotProduct, sgDiag, of_apply]
      refine Finset.sum_congr rfl fun j _ => ?_
      by_cases h : β j = s
      · simp [hi, h]
      · simp [hi, h, hx' j h, Ne.symm h]
    have hu : (sgUp β (sgG A B) *ᵥ w) i = 0 := by
      simp only [Matrix.mulVec, dotProduct, sgUp, of_apply]
      refine Finset.sum_eq_zero fun j _ => ?_
      by_cases h : β j = s
      · simp [hi, h]
      · simp [hx' j h]
    have hl : (sgLow β (sgG A B) *ᵥ w) i = 0 := by
      simp only [Matrix.mulVec, dotProduct, sgLow, of_apply]
      refine Finset.sum_eq_zero fun j _ => ?_
      by_cases h : β j = s
      · simp [hi, h]
      · simp [hx' j h]
    have hKw : (sgK β (sgG A B) *ᵥ w) i = 2 * w i + (sgG A B *ᵥ w) i := by
      simp only [sgK, Matrix.add_mulVec, Matrix.sub_mulVec, Matrix.smul_mulVec, Matrix.one_mulVec,
        Pi.add_apply, Pi.sub_apply, Pi.smul_apply, smul_eq_mul]
      rw [hd, hu, hl]; ring
    rw [hKw, hG]
    simp only [Pi.smul_apply, smul_eq_mul]
    ring
  have h3 : -(2 : K) • x = 0 := by rw [← hAw, hw0, Matrix.mulVec_zero]
  have h4 : (2 : K) • x = 0 := by rw [← neg_eq_zero, ← neg_smul]; exact h3
  exact (smul_eq_zero.mp h4).resolve_left h2

/-! ## (5) LEAF-RANK / local count -/
theorem leaf_rank (A B : Matrix (Fin n) ι K) (β : ι → ℕ) (k s : ℕ) (hs : s < k) (h2 : (2 : K) ≠ 0)
    (hP : sgProd A B β k = -1) (hK : KNondeg β (sgG A B) s)
    (F : Finset (Fin n)) (Th : Finset ι)
    (hF : ∀ r ∈ F, ∀ i, β i ≠ s → i ∉ Th → B r i = 0) : F.card ≤ Th.card := by
  classical
  -- linear map (F -> K) -> (Th -> K), x |-> (sum_{r in F} B r i x r)_{i in Th}
  let ext : (F → K) → (Fin n → K) := fun c r => if h : r ∈ F then c ⟨r, h⟩ else 0
  let f : (F → K) →ₗ[K] (Th → K) :=
    { toFun := fun c i => (Bᵀ *ᵥ ext c) i.1
      map_add' := by
        intro c d; funext i
        simp only [Pi.add_apply]
        rw [← Pi.add_apply (Bᵀ *ᵥ ext c), ← Matrix.mulVec_add]
        congr 2; funext r; simp only [ext, Pi.add_apply]; split_ifs <;> simp
      map_smul' := by
        intro a c; funext i
        simp only [Pi.smul_apply, smul_eq_mul, RingHom.id_apply]
        rw [← smul_eq_mul, ← Pi.smul_apply a (Bᵀ *ᵥ ext c), ← Matrix.mulVec_smul]
        congr 2; funext r; simp only [ext, Pi.smul_apply, smul_eq_mul]; split_ifs <;> simp }
  have hinj : Function.Injective f := by
    rw [← LinearMap.ker_eq_bot, LinearMap.ker_eq_bot']
    intro c hc
    have hx : ∀ i, β i ≠ s → (Bᵀ *ᵥ ext c) i = 0 := by
      intro i hi
      by_cases hT : i ∈ Th
      · exact congrFun hc ⟨i, hT⟩
      · simp only [Matrix.mulVec, dotProduct, Matrix.transpose_apply]
        refine Finset.sum_eq_zero fun r _ => ?_
        by_cases hr : r ∈ F
        · simp [hF r hr i hi hT]
        · simp [ext, hr]
    have h0 := leaf_zero A B β k s hs h2 hP hK (ext c) hx
    funext r
    have := congrFun h0 r.1
    simpa [ext, r.2] using this
  have := LinearMap.finrank_le_finrank_of_injective hinj
  simpa using this

/-! ## (6) non-vacuity -/
/-- one host (time 0, columns 0,1) and one thin (time 1, column 2) on n = 1 coordinate:
    host V_0 = 1 + a b^T with a = (1,0), b = (1,0): V_0 = 2;  thin V_1 = 1 + (1)(-3/2) = -1/2;  product = -1. -/
def A1 : Matrix (Fin 1) (Fin 3) ℚ := !![1, 0, 1]
def B1 : Matrix (Fin 1) (Fin 3) ℚ := !![1, 0, -3/2]
def beta1 : Fin 3 → ℕ := ![0, 0, 1]

theorem prod1 : sgProd A1 B1 beta1 2 = -1 := by
  ext i j
  fin_cases i; fin_cases j
  simp [sgProd, sgStage, blkPi, A1, B1, beta1, Matrix.mul_apply, Fin.sum_univ_succ, Matrix.diagonal_apply,
    Matrix.vecMul, dotProduct, Matrix.transpose_apply, Matrix.add_apply, Matrix.one_apply]
  norm_num

theorem knondeg1 : KNondeg beta1 (sgG A1 B1) 0 := by
  intro w hw hk
  have h2 : w 2 = 0 := hw 2 (by simp [beta1])
  have e0 := hk 0 (by simp [beta1])
  have e1 := hk 1 (by simp [beta1])
  simp [sgK, sgG, sgDiag, sgUp, sgLow, A1, B1, beta1, Matrix.mulVec, dotProduct, Fin.sum_univ_succ,
    Matrix.mul_apply, one_apply, h2] at e0 e1
  have h0 : w 0 = 0 := by
    rcases e0 with h | h
    · norm_num at h
    · exact h
  funext j; fin_cases j
  · simpa using h0
  · simpa using e1
  · simpa using h2

/-- the leaf (role 0, touched by host 0 and the thin column 2) is allowed: |F| = 1 <= |Th| = 1. -/
theorem inst_leaf : (Finset.univ : Finset (Fin 1)).card ≤ ({2} : Finset (Fin 3)).card :=
  leaf_rank A1 B1 beta1 2 0 (by norm_num) (by norm_num) prod1 knondeg1 _ {2}
    (fun r _ i hi hT => by fin_cases i <;> simp_all [beta1])

/-- without the thin column the same leaf would need |F| <= 0: the lemma is sharp (Th must contain the thin). -/
theorem inst_thin_needed : ¬ ((Finset.univ : Finset (Fin 1)).card ≤ (∅ : Finset (Fin 3)).card) := by simp

/-- count law on the instance: n + 2 = 3 = |iota| (T = Q = 1, n = 2k - 2 + Q with k = 1). -/
theorem inst_count : 1 + 2 ≤ Fintype.card (Fin 3) :=
  thin_count A1 B1 beta1 2 (by norm_num) (fun i => by fin_cases i <;> simp [beta1]) prod1 ![0, 1]
    (by
      rw [isUnit_iff_ne_zero, Matrix.det_fin_two]
      simp [ sgK, sgG, sgDiag, sgUp, sgLow, A1, B1, beta1, Matrix.mul_apply,
        one_apply, Matrix.transpose_apply]
      norm_num)

end CallerThin

#print axioms CallerThin.thin_count
#print axioms CallerThin.thin_G_blk_unit
#print axioms CallerThin.rc2_pair_thin
#print axioms CallerThin.leaf_eig
#print axioms CallerThin.leaf_zero
#print axioms CallerThin.leaf_rank
#print axioms CallerThin.prod1
#print axioms CallerThin.inst_leaf
#print axioms CallerThin.inst_count
