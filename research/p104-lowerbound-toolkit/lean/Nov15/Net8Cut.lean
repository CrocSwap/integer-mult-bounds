/-
Net8Cut (lane LEAN-NET8, Nov 19).  Generic cut lemma for a relay DAG, no Menger.
H strictly lower triangular, N = sum_{i<n} H^i = (1-H)^{-1} (walk sums).  If C meets every walk g -> d with
G[.,d] != 0, F[g,.] != 0 (walk counted with all vertices, endpoints included), then rank (G N F) <= |C|.
Proof: with P = diag 1_C and N1 = (1 - H(1-P))^{-1}:  N = (1-P) N1 + N P N1  (first-visit-to-C decomposition),
the first term contributes 0 by the cut hypothesis, the second has a factor P.
Kernel only.
-/
import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.Algebra.Ring.GeomSum
import Mathlib.Tactic.NoncommRing

open Matrix Finset
set_option maxHeartbeats 0
namespace N8

variable {n : ℕ}

/-- `(1-H)^{-1}` as the walk sum (H is nilpotent when strictly lower triangular). -/
def Nmat (H : Matrix (Fin n) (Fin n) ℚ) : Matrix (Fin n) (Fin n) ℚ := ∑ i ∈ range n, H ^ i

theorem pow_ne_zero_le (X : Matrix (Fin n) (Fin n) ℚ) (hX : ∀ k j, X k j ≠ 0 → j < k) :
    ∀ m (d g : Fin n), (X ^ m) d g ≠ 0 → g.val + m ≤ d.val := by
  intro m
  induction m with
  | zero =>
    intro d g h
    by_cases e : d = g
    · subst e; simp
    · simp [Matrix.one_apply, e] at h
  | succ m ih =>
    intro d g h
    rw [pow_succ', Matrix.mul_apply] at h
    obtain ⟨j, _, hj⟩ := Finset.exists_ne_zero_of_sum_ne_zero h
    have h1 := hX d j (left_ne_zero_of_mul hj)
    have h2 := ih j g (right_ne_zero_of_mul hj)
    have := Fin.lt_def.1 h1
    omega

theorem pow_n_eq_zero (X : Matrix (Fin n) (Fin n) ℚ) (hX : ∀ k j, X k j ≠ 0 → j < k) : X ^ n = 0 := by
  ext d g
  by_contra h
  have h' : (X ^ n) d g ≠ 0 := by simpa using h
  have := pow_ne_zero_le X hX n d g h'
  have := d.isLt
  omega

theorem Nmat_mul (H : Matrix (Fin n) (Fin n) ℚ) (hH : ∀ k j, H k j ≠ 0 → j < k) :
    Nmat H * (1 - H) = 1 := by
  unfold Nmat; rw [geom_sum_mul_neg, pow_n_eq_zero H hH, sub_zero]

theorem mul_Nmat (H : Matrix (Fin n) (Fin n) ℚ) (hH : ∀ k j, H k j ≠ 0 → j < k) :
    (1 - H) * Nmat H = 1 := by
  unfold Nmat; rw [mul_neg_geom_sum, pow_n_eq_zero H hH, sub_zero]

open Classical in
/-- Diagonal indicator of `C`. -/
noncomputable def ind (C : Finset (Fin n)) : Matrix (Fin n) (Fin n) ℚ :=
  diagonal (fun j => if j ∈ C then (1 : ℚ) else 0)

open Classical in
theorem one_sub_ind (C : Finset (Fin n)) :
    (1 : Matrix (Fin n) (Fin n) ℚ) - ind C = diagonal (fun j => if j ∈ C then (0 : ℚ) else 1) := by
  ext i j
  simp only [Matrix.sub_apply, Matrix.one_apply, ind, Matrix.diagonal_apply]
  by_cases hij : i = j
  · subst hij; by_cases hi : i ∈ C <;> simp [hi]
  · simp [hij]

open Classical in
theorem mulQ_apply (H : Matrix (Fin n) (Fin n) ℚ) (C : Finset (Fin n)) (k j : Fin n) :
    (H * (1 - ind C)) k j = if j ∈ C then 0 else H k j := by
  rw [one_sub_ind, mul_diagonal]
  by_cases h : j ∈ C <;> simp [h]

open Classical in
theorem rank_ind (C : Finset (Fin n)) : (ind C).rank = C.card := by
  unfold ind
  rw [rank_diagonal]
  have : (Finset.univ.filter fun j : Fin n => (if j ∈ C then (1 : ℚ) else 0) ≠ 0) = C := by
    ext j; by_cases h : j ∈ C <;> simp [h]
  rw [Fintype.card_subtype, this]

open Classical in
theorem walk (H : Matrix (Fin n) (Fin n) ℚ) (C : Finset (Fin n)) :
    ∀ i (d g : Fin n), (((H * (1 - ind C)) ^ i : Matrix (Fin n) (Fin n) ℚ) d g) ≠ 0 →
      Relation.ReflTransGen (fun j k : Fin n => j ∉ C ∧ H k j ≠ 0) g d := by
  intro i
  induction i with
  | zero =>
    intro d g h
    by_cases e : d = g
    · subst e; exact Relation.ReflTransGen.refl
    · simp [Matrix.one_apply, e] at h
  | succ i ih =>
    intro d g h
    rw [pow_succ', Matrix.mul_apply] at h
    obtain ⟨j, _, hj⟩ := Finset.exists_ne_zero_of_sum_ne_zero h
    have h1 := left_ne_zero_of_mul hj
    have h2 := ih j g (right_ne_zero_of_mul hj)
    rw [mulQ_apply] at h1
    by_cases hjC : j ∈ C
    · simp [hjC] at h1
    · rw [if_neg hjC] at h1
      exact h2.tail ⟨hjC, h1⟩

open Classical in
theorem Nmat_walk (H : Matrix (Fin n) (Fin n) ℚ) (C : Finset (Fin n)) (d g : Fin n)
    (h : Nmat (H * (1 - ind C)) d g ≠ 0) :
    Relation.ReflTransGen (fun j k : Fin n => j ∉ C ∧ H k j ≠ 0) g d := by
  unfold Nmat at h
  rw [Matrix.sum_apply] at h
  obtain ⟨i, _, hi⟩ := Finset.exists_ne_zero_of_sum_ne_zero h
  exact walk H C i d g hi

theorem key_id (H N N1 P : Matrix (Fin n) (Fin n) ℚ) (hNA : N * (1 - H) = 1)
    (hN1 : (1 - H * (1 - P)) * N1 = 1) : N = (1 - P) * N1 + N * P * N1 := by
  have hNH : N * H = N - 1 := by
    have h := hNA
    rw [mul_sub, mul_one] at h
    rw [← h]; abel
  have h2 : N * (1 - H * (1 - P)) = 1 + (N - 1) * P := by
    have e : (1 : Matrix (Fin n) (Fin n) ℚ) - H * (1 - P) = (1 - H) + H * P := by noncomm_ring
    rw [e, mul_add, hNA, ← mul_assoc, hNH]
  calc N = N * ((1 - H * (1 - P)) * N1) := by rw [hN1, mul_one]
    _ = (N * (1 - H * (1 - P))) * N1 := by rw [mul_assoc]
    _ = (1 + (N - 1) * P) * N1 := by rw [h2]
    _ = (1 - P) * N1 + N * P * N1 := by noncomm_ring

open Classical in
/-- **Cut lemma.**  If every walk from a gathering node `g` to a depositing node `d` (all of whose
non-final vertices avoid `C`, and `d ∉ C`) is impossible, then `rank (G N F) <= |C|`. -/
theorem cut_rank {ι κ : Type} [Fintype ι] [Fintype κ] (H : Matrix (Fin n) (Fin n) ℚ)
    (hH : ∀ k j, H k j ≠ 0 → j < k) (G : Matrix ι (Fin n) ℚ) (F : Matrix (Fin n) κ ℚ)
    (C : Finset (Fin n))
    (hcut : ∀ s p d g, G s d ≠ 0 → F g p ≠ 0 → d ∉ C →
      Relation.ReflTransGen (fun j k : Fin n => j ∉ C ∧ H k j ≠ 0) g d → False) :
    (G * Nmat H * F).rank ≤ C.card := by
  have hQ : ∀ k j, (H * (1 - ind C)) k j ≠ 0 → j < k := by
    intro k j h
    rw [mulQ_apply] at h
    by_cases hj : j ∈ C
    · simp [hj] at h
    · rw [if_neg hj] at h; exact hH k j h
  have hN1 : (1 - H * (1 - ind C)) * Nmat (H * (1 - ind C)) = 1 := mul_Nmat _ hQ
  have key := key_id H (Nmat H) (Nmat (H * (1 - ind C))) (ind C) (Nmat_mul H hH) hN1
  have z : G * (1 - ind C) * Nmat (H * (1 - ind C)) * F = 0 := by
    ext s p
    rw [Matrix.mul_apply]
    simp only [Matrix.zero_apply]
    apply Finset.sum_eq_zero
    intro g _
    rw [Matrix.mul_apply, Finset.sum_mul]
    apply Finset.sum_eq_zero
    intro d _
    by_contra h
    have h1 := left_ne_zero_of_mul h
    have h3 := right_ne_zero_of_mul h
    have h4 := left_ne_zero_of_mul h1
    have h5 := right_ne_zero_of_mul h1
    rw [one_sub_ind, mul_diagonal] at h4
    by_cases hd : d ∈ C
    · simp [hd] at h4
    · rw [if_neg hd] at h4
      exact hcut s p d g (by simpa using h4) h3 hd (Nmat_walk H C d g h5)
  have eq : G * Nmat H * F = G * Nmat H * ind C * Nmat (H * (1 - ind C)) * F := by
    calc G * Nmat H * F = G * ((1 - ind C) * Nmat (H * (1 - ind C)) +
          Nmat H * ind C * Nmat (H * (1 - ind C))) * F := by rw [← key]
      _ = G * (1 - ind C) * Nmat (H * (1 - ind C)) * F +
          G * Nmat H * ind C * Nmat (H * (1 - ind C)) * F := by
        rw [Matrix.mul_add, Matrix.add_mul]; simp only [Matrix.mul_assoc]
      _ = _ := by rw [z, zero_add]
  rw [eq]
  calc (G * Nmat H * ind C * Nmat (H * (1 - ind C)) * F).rank
      ≤ (G * Nmat H * ind C * Nmat (H * (1 - ind C))).rank := Matrix.rank_mul_le_left _ _
    _ ≤ (G * Nmat H * ind C).rank := Matrix.rank_mul_le_left _ _
    _ ≤ (ind C).rank := Matrix.rank_mul_le_right _ _
    _ = C.card := rank_ind C

end N8

#print axioms N8.cut_rank
