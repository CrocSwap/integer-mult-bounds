/-
CallerDecomp (lane DECOMP, Nov 20).  Conjecture DECOMP (TIGHTPAD salvage): "every non-tight Q = 0 caller frame with
invertible diagonal K-blocks is a direct sum of tight frames".  It is FALSE.  Notes: cards/WILD/NOVEL/decomp/DC.md.

Frame = CallerSGram model: A B : n x (Fin k x Fin 2), stage t = 1 + A Pi_t B^T, P = V_{k-1} ... V_0 = -1,
K = sgK, lambda /= -1 = every diagonal 2x2 K-block invertible, tight = n + 2 = 2k (Q = 0, no thin columns).
A direct sum of >= 2 frames needs a SPLIT: a nontrivial 2-colouring of the stages and a colouring of the roles such that
every role meets only stages of its own colour.  `Splittable` below; a frame with no split is not a direct sum of
anything, so a non-tight frame with no split refutes DECOMP.

* `k1_n0`        : k = 1 with lambda /= -1 forces n = 0, i.e. every k = 1 frame is tight.  (minimality)
* `w1_*`         : MINIMAL witness, k = 2, n = 1 (e = 2k - n - 2 = 1): V = 2, -1/2; one role on both stages.
* `w2_*`         : EVEN witness, k = 3, n = 2 (e = 2; PARITY of Q = 0 words forces n even): V_t = lambda_t I,
                   lambda = (2, 2, -1/4).  Every role meets every stage, and every OFF-diagonal K-block is invertible
                   too (so K has no block decomposition along any stage partition: indecomposable also up to
                   role-basis change, see DC.md section 2).
* `decomp_false` : the packaged refutation.
Word level (DC.md, [C exact] dc1.log): a legal Q = 0 caller word with k = 3, n = 2 and the same properties exists.
Kernel only.
-/
import Nov15.CallerSGram

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace CallerDecomp
open Finset Matrix CallerSign

/-- a direct-sum split of a frame: stages coloured by `σ` (both colours used), roles by `ρ`, and every role meets only
    stages of its own colour. -/
def Splittable {n k : ℕ} (A B : Matrix (Fin n) (Fin k × Fin 2) ℚ) : Prop :=
  ∃ (σ : Fin k → Bool) (ρ : Fin n → Bool), (∃ s, σ s = true) ∧ (∃ s, σ s = false) ∧
    ∀ r s, meets A B r s → ρ r = σ s

/-- a frame in which every role meets every stage has no split. -/
theorem not_split_of_meets {n k : ℕ} (A B : Matrix (Fin n) (Fin k × Fin 2) ℚ) (hn : 0 < n)
    (h : ∀ r s, meets A B r s) : ¬ Splittable A B := by
  rintro ⟨σ, ρ, ⟨s1, h1⟩, ⟨s2, h2⟩, hs⟩
  have e1 := hs ⟨0, hn⟩ s1 (h _ _)
  have e2 := hs ⟨0, hn⟩ s2 (h _ _)
  rw [h1] at e1; rw [h2] at e2; rw [e1] at e2; exact Bool.noConfusion e2

/-! ## minimality: k = 1 frames are tight -/
section k1
variable {K : Type*} [Field K] {n : ℕ}

theorem k1_n0 (A B : Matrix (Fin n) (Fin 1 × Fin 2) K) (h2 : (2 : K) ≠ 0)
    (hP : sgProd A B (fun i => (i.1 : ℕ)) 1 = -1)
    (hlam : IsUnit (blkOf (sgK (fun i => (i.1 : ℕ)) (sgG A B)) 0 0).det) : n = 0 := by
  have hF := (sgForward A B (fun i => (i.1 : ℕ)) 1 h2 (fun i => i.1.isLt) hP).1
  simp only [Fintype.card_prod, Fintype.card_fin] at hF
  set M := sgK (fun i : Fin 1 × Fin 2 => (i.1 : ℕ)) (sgG A B)
  have e : blkOf M 0 0 = M.submatrix (fun a => ((0 : Fin 1), a)) (fun a => ((0 : Fin 1), a)) := by
    ext a b; simp [blkOf]
  have h1 : (blkOf M 0 0).rank = 2 := by
    have := Matrix.rank_of_isUnit _ ((Matrix.isUnit_iff_isUnit_det _).mpr hlam)
    simpa using this
  have h3 := Matrix.rank_submatrix_le M (fun a => ((0 : Fin 1), a)) (fun a => ((0 : Fin 1), a))
  rw [← e] at h3
  omega

/-- so a k = 1 frame with lambda /= -1 satisfies the tightness equation n + 2 = |iota|. -/
theorem k1_tight (A B : Matrix (Fin n) (Fin 1 × Fin 2) K) (h2 : (2 : K) ≠ 0)
    (hP : sgProd A B (fun i => (i.1 : ℕ)) 1 = -1)
    (hlam : IsUnit (blkOf (sgK (fun i => (i.1 : ℕ)) (sgG A B)) 0 0).det) :
    n + 2 = Fintype.card (Fin 1 × Fin 2) := by
  rw [k1_n0 A B h2 hP hlam]; simp

end k1

/-! ## minimal witness: k = 2, n = 1, e = 1 -/
section w1

def a1 : Fin 2 → ℚ := ![1, -3/2]
def A1 : Matrix (Fin 1) (Fin 2 × Fin 2) ℚ := Matrix.of fun _ c => if c.2 = 0 then a1 c.1 else 0
def B1 : Matrix (Fin 1) (Fin 2 × Fin 2) ℚ := Matrix.of fun _ c => if c.2 = 0 then 1 else 0

theorem w1_stage (t : ℕ) (ht : t < 2) :
    sgStage A1 B1 (fun i => (i.1 : ℕ)) t = (1 + a1 ⟨t, ht⟩) • (1 : Matrix (Fin 1) (Fin 1) ℚ) := by
  ext i j
  interval_cases t <;> fin_cases i <;> fin_cases j <;>
    simp [sgStage, blkPi, A1, B1, a1, Matrix.mul_apply, Matrix.one_apply,
      Matrix.diagonal_apply, Fintype.sum_prod_type, Fin.sum_univ_succ]

theorem w1_prod : sgProd A1 B1 (fun i => (i.1 : ℕ)) 2 = -1 := by
  simp only [sgProd, w1_stage 0 (by norm_num), w1_stage 1 (by norm_num), Matrix.mul_one]
  ext i j
  fin_cases i <;> fin_cases j <;> simp [a1] <;> norm_num

theorem w1_diag : ∀ t, IsUnit (blkOf (sgK (fun i => (i.1 : ℕ)) (sgG A1 B1)) t t).det := by
  intro t
  rw [isUnit_iff_ne_zero]
  fin_cases t <;>
    simp [Matrix.det_fin_two, blkOf, sgK, sgDiag, sgUp, sgLow, sgG, A1, B1, a1, Matrix.mul_apply,
      Matrix.one_apply, Fin.sum_univ_succ, Matrix.transpose_apply] <;> norm_num

theorem w1_nontight : 1 + 2 < Fintype.card (Fin 2 × Fin 2) := by simp

theorem w1_meets : ∀ r s, meets A1 B1 r s := by
  intro r s
  exact ⟨0, Or.inr (by simp [B1])⟩

theorem w1_not_split : ¬ Splittable A1 B1 := not_split_of_meets A1 B1 (by norm_num) w1_meets

end w1

/-! ## even witness: k = 3, n = 2, e = 2 (V_t = lambda_t I) -/
section w2

def v2 : Fin 3 → ℚ := ![1, 1, -5/4]
def A2 : Matrix (Fin 2) (Fin 3 × Fin 2) ℚ := Matrix.of fun r c => if r = c.2 then 1 else 0
def B2 : Matrix (Fin 2) (Fin 3 × Fin 2) ℚ := Matrix.of fun r c => if r = c.2 then v2 c.1 else 0

theorem w2_stage (t : ℕ) (ht : t < 3) :
    sgStage A2 B2 (fun i => (i.1 : ℕ)) t = (1 + v2 ⟨t, ht⟩) • (1 : Matrix (Fin 2) (Fin 2) ℚ) := by
  ext i j
  interval_cases t <;> fin_cases i <;> fin_cases j <;>
    simp [sgStage, blkPi, A2, B2, v2, Matrix.mul_apply, Matrix.one_apply,
      Matrix.diagonal_apply, Fintype.sum_prod_type, Fin.sum_univ_succ]

theorem w2_prod : sgProd A2 B2 (fun i => (i.1 : ℕ)) 3 = -1 := by
  simp only [sgProd, w2_stage 0 (by norm_num), w2_stage 1 (by norm_num), w2_stage 2 (by norm_num), Matrix.mul_one]
  ext i j
  fin_cases i <;> fin_cases j <;> simp [v2, Matrix.one_apply] <;> norm_num

theorem w2_diag : ∀ t, IsUnit (blkOf (sgK (fun i => (i.1 : ℕ)) (sgG A2 B2)) t t).det := by
  intro t
  rw [isUnit_iff_ne_zero]
  fin_cases t <;>
    simp [Matrix.det_fin_two, blkOf, sgK, sgDiag, sgUp, sgLow, sgG, A2, B2, v2, Matrix.mul_apply,
      Matrix.one_apply, Fin.sum_univ_succ, Matrix.transpose_apply] <;> norm_num

/-- every off-diagonal K-block is invertible as well: K admits no block decomposition along a stage partition. -/
theorem w2_offdiag : ∀ s t, IsUnit (blkOf (sgK (fun i => (i.1 : ℕ)) (sgG A2 B2)) s t).det := by
  intro s t
  rw [isUnit_iff_ne_zero]
  fin_cases s <;> fin_cases t <;>
    simp [Matrix.det_fin_two, blkOf, sgK, sgDiag, sgUp, sgLow, sgG, A2, B2, v2, Matrix.mul_apply,
      Matrix.one_apply, Fin.sum_univ_succ, Matrix.transpose_apply] <;> norm_num

theorem w2_nontight : 2 + 2 < Fintype.card (Fin 3 × Fin 2) := by simp

theorem w2_meets : ∀ r s, meets A2 B2 r s := by
  intro r s
  exact ⟨r, Or.inl (by simp [A2])⟩

theorem w2_not_split : ¬ Splittable A2 B2 := not_split_of_meets A2 B2 (by norm_num) w2_meets

end w2

/-- DECOMP is false: a P = -1, lambda /= -1, Q = 0 frame (k = 3, n = 2, n even as Q = 0 words require) that is NOT tight
    (n + 2 < 2k) and admits NO direct-sum split at all (so it is not a direct sum of tight frames), and whose K has every
    2x2 block invertible. -/
theorem decomp_false :
    ∃ (A B : Matrix (Fin 2) (Fin 3 × Fin 2) ℚ), sgProd A B (fun i => (i.1 : ℕ)) 3 = -1 ∧
      (∀ t, IsUnit (blkOf (sgK (fun i => (i.1 : ℕ)) (sgG A B)) t t).det) ∧
      2 + 2 < Fintype.card (Fin 3 × Fin 2) ∧ ¬ Splittable A B ∧
      (∀ s t, IsUnit (blkOf (sgK (fun i => (i.1 : ℕ)) (sgG A B)) s t).det) :=
  ⟨A2, B2, w2_prod, w2_diag, w2_nontight, w2_not_split, w2_offdiag⟩

/-- the minimal (k = 2, n = 1, e = 1) refutation. -/
theorem decomp_false_min :
    ∃ (A B : Matrix (Fin 1) (Fin 2 × Fin 2) ℚ), sgProd A B (fun i => (i.1 : ℕ)) 2 = -1 ∧
      (∀ t, IsUnit (blkOf (sgK (fun i => (i.1 : ℕ)) (sgG A B)) t t).det) ∧
      1 + 2 < Fintype.card (Fin 2 × Fin 2) ∧ ¬ Splittable A B :=
  ⟨A1, B1, w1_prod, w1_diag, w1_nontight, w1_not_split⟩

end CallerDecomp

#print axioms CallerDecomp.k1_n0
#print axioms CallerDecomp.k1_tight
#print axioms CallerDecomp.decomp_false
#print axioms CallerDecomp.decomp_false_min
