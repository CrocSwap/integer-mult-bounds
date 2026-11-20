/-
LevelCutDX (lane LEANDX, Nov 20).  NOGAIN NG.md sections 1-2, kernel only.
 (1) DX: the downward-crossing level cut.  A walk (v_0..v_m) is l-CROSSING if exists i <= j with da v_i >= l > db v_j.
     `Mstar` is the sum over l-crossing walks of G * (walk weight) * F, computed by the state automaton
        state 0 = no node with da >= l seen so far, state 1 = seen but not yet crossed, state 2 = crossed
     (a function of the walk prefix, so each walk is counted once; no walk is counted in two states).
     Theorem `dx_rank_le` : rank Mstar_l <= |C_l|;  `dx_D_ge` : sum_l rank Mstar_l <= sum_k (da k - db k).
 (2) zero-drop contraction: a node k with a_k <= b_k is contracted (made dead: zero F-row, G-column, H-row/column),
     `contract_identity` : G N F = G'' N'' F'' + G[.,k] F[k,.]; `NetW` legality is preserved (`contractW`),
     M unchanged on odd cells; iterating gives `exists_contracted`: every node dead or not (a <= b); with b <= a,
     #live nodes <= D.
-/
import Nov15.LevelCutRelay

open Matrix Module
set_option maxHeartbeats 0
namespace N8
open Classical

variable {n : ℕ}

/-! ### the crossing automaton -/

noncomputable def dg (f : Fin n → Prop) : Matrix (Fin n) (Fin n) ℚ :=
  diagonal fun d => if f d then 1 else 0

theorem dg_mul_dg (p q : Fin n → Prop) : dg p * dg q = dg (fun d => p d ∧ q d) := by
  ext i j
  simp only [dg, Matrix.diagonal_mul_diagonal, Matrix.diagonal_apply]
  by_cases h : i = j
  · subst h; by_cases hp : p i <;> by_cases hq : q i <;> simp [hp, hq]
  · simp [h]

theorem dg_absorb (p q : Fin n → Prop) (h : ∀ d, q d → p d) : dg p * dg q = dg q := by
  rw [dg_mul_dg]; congr 1; ext d; exact ⟨fun h' => h'.2, fun h' => ⟨h d h', h'⟩⟩

theorem dg_apply_mul (p : Fin n → Prop) (Y : Matrix (Fin n) (Fin n) ℚ) (d g : Fin n) :
    (dg p * Y) d g = if p d then Y d g else 0 := by
  simp only [dg, Matrix.diagonal_mul]; by_cases h : p d <;> simp [h]

theorem dgHdg_apply (p q : Fin n → Prop) (H : Matrix (Fin n) (Fin n) ℚ) (d c : Fin n) :
    (dg p * H * dg q) d c = if p d ∧ q c then H d c else 0 := by
  simp only [dg, Matrix.mul_diagonal, Matrix.diagonal_mul]
  by_cases hp : p d <;> by_cases hq : q c <;> simp [hp, hq]

/-- (state 0, state 1, state 2) walk sums of length exactly `i`, indexed `[end, start]`. -/
noncomputable def W0 (da db : Fin n → ℕ) (l : ℕ) :
    Matrix (Fin n) (Fin n) ℚ × Matrix (Fin n) (Fin n) ℚ × Matrix (Fin n) (Fin n) ℚ :=
  (dg fun d => da d < l, dg fun d => l ≤ da d ∧ l ≤ db d, ind (Cd da db l))

noncomputable def Wstep (H : Matrix (Fin n) (Fin n) ℚ) (da db : Fin n → ℕ) (l : ℕ)
    (w : Matrix (Fin n) (Fin n) ℚ × Matrix (Fin n) (Fin n) ℚ × Matrix (Fin n) (Fin n) ℚ) :
    Matrix (Fin n) (Fin n) ℚ × Matrix (Fin n) (Fin n) ℚ × Matrix (Fin n) (Fin n) ℚ :=
  ((dg fun d => da d < l) * H * w.1,
   (dg fun d => l ≤ da d ∧ l ≤ db d) * H * w.1 + (dg fun d => l ≤ db d) * H * w.2.1,
   ind (Cd da db l) * H * w.1 + (dg fun d => db d < l) * H * w.2.1 + H * w.2.2)

noncomputable def Wt (H : Matrix (Fin n) (Fin n) ℚ) (da db : Fin n → ℕ) (l : ℕ) : ℕ →
    Matrix (Fin n) (Fin n) ℚ × Matrix (Fin n) (Fin n) ℚ × Matrix (Fin n) (Fin n) ℚ
  | 0 => W0 da db l
  | i + 1 => Wstep H da db l (Wt H da db l i)

/-- the sum over l-crossing walks of `G (walk weight) F`. -/
noncomputable def Mstar {ι κ : Type} [Fintype ι] [Fintype κ] (G : Matrix ι (Fin n) ℚ)
    (H : Matrix (Fin n) (Fin n) ℚ) (F : Matrix (Fin n) κ ℚ) (da db : Fin n → ℕ) (l : ℕ) :
    Matrix ι κ ℚ := G * (∑ i ∈ Finset.range n, (Wt H da db l i).2.2) * F

/-! ### support lemmas -/

theorem Wt_succ (H : Matrix (Fin n) (Fin n) ℚ) (da db : Fin n → ℕ) (l i : ℕ) :
    Wt H da db l (i + 1) = Wstep H da db l (Wt H da db l i) := rfl

theorem W1_rows (H : Matrix (Fin n) (Fin n) ℚ) (da db : Fin n → ℕ) (l : ℕ) :
    ∀ i, (dg fun d => l ≤ db d) * (Wt H da db l i).2.1 = (Wt H da db l i).2.1 := by
  intro i
  induction i with
  | zero => exact dg_absorb _ _ (fun d h => h.2)
  | succ i ih =>
    rw [Wt_succ]
    simp only [Wstep]
    rw [Matrix.mul_add, ← Matrix.mul_assoc, ← Matrix.mul_assoc,
      dg_absorb _ _ (fun d h => h.2)]
    have : (dg fun d => l ≤ db d) * H * (Wt H da db l i).2.1 =
        (dg fun d => l ≤ db d) * (H * (Wt H da db l i).2.1) := by rw [Matrix.mul_assoc]
    rw [Matrix.mul_assoc, Matrix.mul_assoc, ← Matrix.mul_assoc, ← Matrix.mul_assoc,
      show ∀ A B : Matrix (Fin n) (Fin n) ℚ, A * B = A * B from fun _ _ => rfl]
    simp only [Matrix.mul_assoc]
    rw [← Matrix.mul_assoc (dg fun d => l ≤ db d) (dg fun d => l ≤ db d),
      dg_absorb _ _ (fun d h => h)]

theorem ind_eq_dg (C : Finset (Fin n)) : ind C = dg (fun d => d ∈ C) := by
  unfold ind dg; congr 1; ext d; congr 1

theorem tri_add {A B : Matrix (Fin n) (Fin n) ℚ} {P : Fin n → Fin n → Prop}
    (hA : ∀ d g, A d g ≠ 0 → P d g) (hB : ∀ d g, B d g ≠ 0 → P d g) :
    ∀ d g, (A + B) d g ≠ 0 → P d g := by
  intro d g h
  by_contra hP
  apply h
  have a := mt (hA d g) hP
  have b := mt (hB d g) hP
  simp only [not_not] at a b
  simp [a, b]

theorem tri_mul {Z Y : Matrix (Fin n) (Fin n) ℚ} {i : ℕ} (hZ : ∀ d c, Z d c ≠ 0 → c < d)
    (hY : ∀ c g, Y c g ≠ 0 → g.val + i ≤ c.val) : ∀ d g, (Z * Y) d g ≠ 0 → g.val + (i + 1) ≤ d.val := by
  intro d g h
  rw [Matrix.mul_apply] at h
  obtain ⟨c, _, hc⟩ := Finset.exists_ne_zero_of_sum_ne_zero h
  have h1 := Fin.lt_def.1 (hZ d c (left_ne_zero_of_mul hc))
  have h2 := hY c g (right_ne_zero_of_mul hc)
  omega

theorem dgH_lt (p : Fin n → Prop) (H : Matrix (Fin n) (Fin n) ℚ) (hH : ∀ k j, H k j ≠ 0 → j < k) :
    ∀ d c, (dg p * H) d c ≠ 0 → c < d := by
  intro d c h
  rw [dg_apply_mul] at h
  by_cases hp : p d
  · rw [if_pos hp] at h; exact hH d c h
  · rw [if_neg hp] at h; exact absurd rfl h

theorem diag_tri (v : Fin n → ℚ) : ∀ d g, (diagonal v : Matrix (Fin n) (Fin n) ℚ) d g ≠ 0 →
    g.val + 0 ≤ d.val := by
  intro d g h
  by_cases e : d = g
  · subst e; simp
  · exact absurd (Matrix.diagonal_apply_ne _ e) h

theorem Wt_tri (H : Matrix (Fin n) (Fin n) ℚ) (hH : ∀ k j, H k j ≠ 0 → j < k) (da db : Fin n → ℕ) (l : ℕ) :
    ∀ i, (∀ d g, (Wt H da db l i).1 d g ≠ 0 → g.val + i ≤ d.val) ∧
      (∀ d g, (Wt H da db l i).2.1 d g ≠ 0 → g.val + i ≤ d.val) ∧
      (∀ d g, (Wt H da db l i).2.2 d g ≠ 0 → g.val + i ≤ d.val) := by
  intro i
  induction i with
  | zero => exact ⟨diag_tri _, diag_tri _, diag_tri _⟩
  | succ i ih =>
    obtain ⟨h0, h1, h2⟩ := ih
    rw [Wt_succ]
    simp only [Wstep]
    refine ⟨tri_mul (dgH_lt _ H hH) h0, tri_add (tri_mul (dgH_lt _ H hH) h0) (tri_mul (dgH_lt _ H hH) h1),
      tri_add (tri_add ?_ (tri_mul (dgH_lt _ H hH) h1)) (tri_mul hH h2)⟩
    rw [ind_eq_dg]
    exact tri_mul (dgH_lt _ H hH) h0

theorem Wt_zero_of_ge (H : Matrix (Fin n) (Fin n) ℚ) (hH : ∀ k j, H k j ≠ 0 → j < k) (da db : Fin n → ℕ)
    (l : ℕ) : (Wt H da db l n).2.2 = 0 := by
  ext d g
  by_contra h
  have := (Wt_tri H hH da db l n).2.2 d g (by simpa using h)
  have := g.isLt
  omega

/-- the part of the state-2 recursion that is injected from states 0 and 1. -/
noncomputable def Sinj (H : Matrix (Fin n) (Fin n) ℚ) (da db : Fin n → ℕ) (l i : ℕ) :
    Matrix (Fin n) (Fin n) ℚ :=
  ind (Cd da db l) * H * (Wt H da db l i).1 + (dg fun d => db d < l) * H * (Wt H da db l i).2.1

theorem W2_succ (H : Matrix (Fin n) (Fin n) ℚ) (da db : Fin n → ℕ) (l i : ℕ) :
    (Wt H da db l (i + 1)).2.2 = H * (Wt H da db l i).2.2 + Sinj H da db l i := by
  rw [Wt_succ]; simp only [Wstep, Sinj]; abel

theorem ind_ind (C : Finset (Fin n)) : ind C * ind C = ind C := by
  rw [ind_eq_dg]; exact dg_absorb _ _ (fun d h => h)

theorem ind_Sinj (H : Matrix (Fin n) (Fin n) ℚ) (da db : Fin n → ℕ)
    (hH : ∀ k j, H k j ≠ 0 → db j ≤ da k) (l i : ℕ) :
    ind (Cd da db l) * Sinj H da db l i = Sinj H da db l i := by
  have hC : ind (Cd da db l) * ((dg fun d => db d < l) * H * dg (fun d => l ≤ db d)) =
      (dg fun d => db d < l) * H * dg (fun d => l ≤ db d) := by
    ext d c
    rw [ind_eq_dg, dg_apply_mul, dgHdg_apply]
    by_cases h1 : db d < l ∧ l ≤ db c
    · rw [if_pos h1]
      by_cases h0 : H d c = 0
      · simp [h0]
      · have : d ∈ Cd da db l := by
          simp only [Cd, Finset.mem_filter, Finset.mem_univ, true_and]
          exact ⟨h1.1, h1.2.trans (hH d c h0)⟩
        rw [if_pos this]
    · rw [if_neg h1]; split_ifs <;> rfl
  have e2 : (dg fun d => db d < l) * H * (Wt H da db l i).2.1 =
      ((dg fun d => db d < l) * H * dg (fun d => l ≤ db d)) * (Wt H da db l i).2.1 := by
    conv_lhs => rw [← W1_rows H da db l i]
    simp only [Matrix.mul_assoc]
  unfold Sinj
  rw [e2, Matrix.mul_add, ← Matrix.mul_assoc, ← Matrix.mul_assoc, ← Matrix.mul_assoc,
    ind_ind, hC]

theorem dx_rank_le {ι κ : Type} [Fintype ι] [Fintype κ]
    (G : Matrix ι (Fin n) ℚ) (H : Matrix (Fin n) (Fin n) ℚ) (F : Matrix (Fin n) κ ℚ)
    (da db : Fin n → ℕ) (hHlt : ∀ k j, H k j ≠ 0 → j < k)
    (hH : ∀ k j, H k j ≠ 0 → db j ≤ da k) (l : ℕ) :
    (Mstar G H F da db l).rank ≤ (Cd da db l).card := by
  set X : Matrix (Fin n) (Fin n) ℚ := ∑ i ∈ Finset.range n, (Wt H da db l i).2.2 with hX
  set S : Matrix (Fin n) (Fin n) ℚ := ∑ i ∈ Finset.range n, Sinj H da db l i with hS
  set P := ind (Cd da db l) with hP
  have hsh : ∑ i ∈ Finset.range n, (Wt H da db l (i + 1)).2.2 + P = X := by
    have h1 := Finset.sum_range_succ' (fun i => (Wt H da db l i).2.2) n
    have h2 := Finset.sum_range_succ (fun i => (Wt H da db l i).2.2) n
    rw [Wt_zero_of_ge H hHlt da db l, add_zero] at h2
    have h0 : (Wt H da db l 0).2.2 = P := rfl
    rw [h0] at h1
    rw [← hX] at h2
    rw [← h2, h1]
  have hrec : ∑ i ∈ Finset.range n, (Wt H da db l (i + 1)).2.2 = H * X + S := by
    simp only [W2_succ, Finset.sum_add_distrib, ← Finset.mul_sum]
    rfl
  have h3 : (1 - H) * X = P + S := by
    rw [hrec] at hsh
    rw [Matrix.sub_mul, one_mul]
    rw [sub_eq_iff_eq_add]; exact hsh.symm.trans (by abel)
  have hPS : P * S = S := by
    rw [hS, Finset.mul_sum]
    exact Finset.sum_congr rfl fun i _ => ind_Sinj H da db hH l i
  have hPPS : P * (P + S) = P + S := by
    rw [Matrix.mul_add, hP, ind_ind, ← hP, hPS]
  have hX2 : X = Nmat H * P * (P + S) := by
    calc X = (Nmat H * (1 - H)) * X := by rw [Nmat_mul H hHlt, one_mul]
      _ = Nmat H * ((1 - H) * X) := by rw [Matrix.mul_assoc]
      _ = Nmat H * (P * (P + S)) := by
          rw [h3, hPPS]
      _ = _ := by rw [Matrix.mul_assoc]
  have hM : Mstar G H F da db l = G * (Nmat H * P * (P + S)) * F := by
    unfold Mstar; rw [← hX, hX2]
  rw [hM]
  calc (G * (Nmat H * P * (P + S)) * F).rank ≤ (G * (Nmat H * P * (P + S))).rank :=
        Matrix.rank_mul_le_left _ _
    _ ≤ (Nmat H * P * (P + S)).rank := Matrix.rank_mul_le_right _ _
    _ ≤ (Nmat H * P).rank := Matrix.rank_mul_le_left _ _
    _ ≤ P.rank := Matrix.rank_mul_le_right _ _
    _ = _ := rank_ind _

theorem dx_D_ge {ι κ : Type} [Fintype ι] [Fintype κ]
    (G : Matrix ι (Fin n) ℚ) (H : Matrix (Fin n) (Fin n) ℚ) (F : Matrix (Fin n) κ ℚ)
    (da db : Fin n → ℕ) (hHlt : ∀ k j, H k j ≠ 0 → j < k)
    (hH : ∀ k j, H k j ≠ 0 → db j ≤ da k) (L : Finset ℕ) :
    ∑ l ∈ L, (Mstar G H F da db l).rank ≤ ∑ k, (da k - db k) :=
  (Finset.sum_le_sum fun l _ => dx_rank_le G H F da db hHlt hH l).trans (sum_Cd_le da db L)

theorem netw_dx_D_ge (N : NetW n) (L : Finset ℕ) :
    ∑ l ∈ L, (Mstar N.G N.H N.F N.da N.db l).rank ≤ ∑ k, (N.da k - N.db k) :=
  dx_D_ge N.G N.H N.F N.da N.db N.hHlt N.relay_dim L

/-! ### non-vacuity 1: lwcx-type toy (gatherer -> hub), DX sum 2 > YC level sum 0, D = 2 -/

namespace ToyDX

/-- node 0: gatherer (a-dim 1, b-dim 0); node 1: hub (a-dim 2, b-dim 1) that deposits; relay 0 -> 1. -/
def da : Fin 2 → ℕ := ![1, 2]
def db : Fin 2 → ℕ := ![0, 1]
def H : Matrix (Fin 2) (Fin 2) ℚ := !![0, 0; 1, 0]
def G : Matrix (Fin 1) (Fin 2) ℚ := !![0, 1]
def F : Matrix (Fin 2) (Fin 1) ℚ := !![1; 0]

theorem hHlt : ∀ k j, H k j ≠ 0 → j < k := by
  intro k j; fin_cases k <;> fin_cases j <;> simp [H]
theorem hH : ∀ k j, H k j ≠ 0 → db j ≤ da k := by
  intro k j; fin_cases k <;> fin_cases j <;> simp [H, da, db]

theorem Cd1 : Cd da db 1 = {0} := by
  ext k; fin_cases k <;> simp [Cd, da, db]
theorem Cd2 : Cd da db 2 = {1} := by
  ext k; fin_cases k <;> simp [Cd, da, db]

theorem W1a : (Wt H da db 1 0).2.2 = !![1, 0; 0, 0] := by
  simp only [Wt, W0, Cd1, ind]
  ext i j; fin_cases i <;> fin_cases j <;> simp [Matrix.diagonal_apply]
theorem W1b : (Wt H da db 1 1).2.2 = !![0, 0; 1, 0] := by
  simp only [Wt, Wstep, W0, Cd1, ind, dg]
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [Matrix.mul_apply, Fin.sum_univ_two, Matrix.diagonal_apply, H, da, db, Matrix.vecMul, dotProduct]
theorem W2a : (Wt H da db 2 0).2.2 = !![0, 0; 0, 1] := by
  simp only [Wt, W0, Cd2, ind]
  ext i j; fin_cases i <;> fin_cases j <;> simp [Matrix.diagonal_apply]
theorem W2b : (Wt H da db 2 1).2.2 = !![0, 0; 1, 0] := by
  simp only [Wt, Wstep, W0, Cd2, ind, dg]
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [Matrix.mul_apply, Fin.sum_univ_two, Matrix.diagonal_apply, H, da, db, Matrix.vecMul, dotProduct]

theorem Mstar1 : Mstar G H F da db 1 = 1 := by
  unfold Mstar
  rw [Finset.sum_range_succ, Finset.sum_range_succ, Finset.sum_range_zero, W1a, W1b]
  ext i j; fin_cases i; fin_cases j
  simp [Matrix.mul_apply, Fin.sum_univ_two, G, F]
theorem Mstar2 : Mstar G H F da db 2 = 1 := by
  unfold Mstar
  rw [Finset.sum_range_succ, Finset.sum_range_succ, Finset.sum_range_zero, W2a, W2b]
  ext i j; fin_cases i; fin_cases j
  simp [Matrix.mul_apply, Fin.sum_univ_two, G, F]

theorem Mnode1 : Mnode G H F da db 1 = 0 := by
  have : G * lowD db 1 = 0 := by
    ext i j; fin_cases i; fin_cases j <;> simp [G, lowD, db, Matrix.mul_diagonal]
  unfold Mnode; rw [this]; simp
theorem Mnode2 : Mnode G H F da db 2 = 0 := by
  have : highD da 2 * F = 0 := by
    ext i j; fin_cases i <;> fin_cases j <;> simp [F, highD, da, Matrix.diagonal_mul]
  unfold Mnode; rw [this]; simp

/-- DX sum over levels 1,2 is 2 (= D = 2, tight); the node-restricted YC sum is 0. -/
theorem dx_gt_yc :
    ∑ l ∈ Finset.Icc 1 2, (Mnode G H F da db l).rank = 0 ∧
    ∑ l ∈ Finset.Icc 1 2, (Mstar G H F da db l).rank = 2 ∧
    ∑ l ∈ Finset.Icc 1 2, (Mstar G H F da db l).rank ≤ ∑ k, (da k - db k) := by
  refine ⟨?_, ?_, dx_D_ge G H F da db hHlt hH _⟩
  · have : Finset.Icc 1 2 = {1, 2} := by decide
    rw [this, Finset.sum_pair (by decide), Mnode1, Mnode2]; simp
  · have : Finset.Icc 1 2 = {1, 2} := by decide
    rw [this, Finset.sum_pair (by decide), Mstar1, Mstar2]; simp

end ToyDX

/-! ### zero-drop contraction -/

/-- node `k` is isolated: no gathering, no depositing, no relay in or out. -/
def NetW.Dead (N : NetW n) (k : Fin n) : Prop :=
  (∀ p, N.F k p = 0) ∧ (∀ s, N.G s k = 0) ∧ (∀ j, N.H j k = 0) ∧ (∀ i, N.H k i = 0)


section ring
variable {R : Type*} [Ring R]

/-- algebraic core: `P` idempotent with `P H P = 0` (node `k` has no self-loop).
`T = (1-P) + P H`, `U = (1-P) + H P`, `H'' = (1-P) H (1-P) + H P H`.  If `N` inverts `1 - H` and
`N'` is a right inverse of `1 - H''` then `N = T N' U + P`. -/
theorem contract_core (P H N N' : R) (hPP : P * P = P) (hPHP : P * H * P = 0)
    (hN : N * (1 - H) = 1) (hN' : (1 - ((1 - P) * H * (1 - P) + H * P * H)) * N' = 1)
    :
    N = ((1 - P) + P * H) * N' * ((1 - P) + H * P) + P := by
  have h1 : P * P * H = P * H := by rw [hPP]
  have h2 : P * P * (H * P) = 0 := by rw [hPP, ← mul_assoc, hPHP]
  have h3 : P * H * P * H = 0 := by rw [hPHP, zero_mul]
  have hF1 : (1 - H) * ((1 - P) + P * H) = (1 - P) * (1 - ((1 - P) * H * (1 - P) + H * P * H)) := by
    have key : (1 - H) * ((1 - P) + P * H) - (1 - P) * (1 - ((1 - P) * H * (1 - P) + H * P * H))
        = (P * P * H - P * H) + (P * H * P) + (P * H * P) - P * P * (H * P) - P * H * P * H := by
      noncomm_ring
    rw [h1, h2, h3, hPHP] at key
    simpa [sub_eq_zero] using key
  have hQU : (1 - P) * ((1 - P) + H * P) = (1 - P) + H * P := by
    have key : (1 - P) * ((1 - P) + H * P) - ((1 - P) + H * P) = (P * P - P) - (P * H * P) := by
      noncomm_ring
    rw [hPP, hPHP] at key
    simpa [sub_eq_zero] using key
  have hR : (1 - H) * (((1 - P) + P * H) * N' * ((1 - P) + H * P) + P) = 1 := by
    have e : (1 - H) * (((1 - P) + P * H) * N' * ((1 - P) + H * P) + P)
        = ((1 - H) * ((1 - P) + P * H)) * N' * ((1 - P) + H * P) + (1 - H) * P := by
      noncomm_ring
    rw [e, hF1]
    have e2 : (1 - P) * (1 - ((1 - P) * H * (1 - P) + H * P * H)) * N' * ((1 - P) + H * P)
        = (1 - P) * ((1 - (( 1 - P) * H * (1 - P) + H * P * H)) * N') * ((1 - P) + H * P) := by
      noncomm_ring
    rw [e2, hN', mul_one, hQU]
    noncomm_ring
  calc N = N * ((1 - H) * (((1 - P) + P * H) * N' * ((1 - P) + H * P) + P)) := by rw [hR, mul_one]
    _ = (N * (1 - H)) * (((1 - P) + P * H) * N' * ((1 - P) + H * P) + P) := (mul_assoc _ _ _).symm
    _ = _ := by rw [hN, one_mul]
end ring

noncomputable def Pk (k : Fin n) : Matrix (Fin n) (Fin n) ℚ := ind {k}

/-- contracted relay matrix (node `k` bypassed, then isolated). -/
noncomputable def cH (H : Matrix (Fin n) (Fin n) ℚ) (k : Fin n) : Matrix (Fin n) (Fin n) ℚ :=
  (1 - Pk k) * H * (1 - Pk k) + H * Pk k * H
noncomputable def cG {ι : Type} [Fintype ι] (G : Matrix ι (Fin n) ℚ) (H : Matrix (Fin n) (Fin n) ℚ)
    (k : Fin n) : Matrix ι (Fin n) ℚ := G * ((1 - Pk k) + Pk k * H)
noncomputable def cF {κ : Type} [Fintype κ] (F : Matrix (Fin n) κ ℚ) (H : Matrix (Fin n) (Fin n) ℚ)
    (k : Fin n) : Matrix (Fin n) κ ℚ := ((1 - Pk k) + H * Pk k) * F

theorem Pk_apply (k i j : Fin n) : Pk k i j = if i = k ∧ j = k then 1 else 0 := by
  unfold Pk ind
  simp only [Matrix.diagonal_apply, Finset.mem_singleton]
  by_cases h : i = j <;> by_cases hk : i = k <;> by_cases hj : j = k <;> simp_all

theorem Qk_eq (k : Fin n) : (1 - Pk k : Matrix (Fin n) (Fin n) ℚ) = dg (fun d => d ≠ k) := by
  ext i j
  rw [Matrix.sub_apply, Pk_apply, Matrix.one_apply]
  unfold dg
  rw [Matrix.diagonal_apply]
  by_cases h : i = j <;> by_cases hk : i = k <;> by_cases hj : j = k <;> simp_all

theorem HPH_apply (H : Matrix (Fin n) (Fin n) ℚ) (k j i : Fin n) :
    (H * Pk k * H) j i = H j k * H k i := by
  simp [Matrix.mul_apply, Pk_apply, ite_and, ite_mul, Finset.sum_ite_eq, Finset.sum_ite_eq']
  done

theorem cH_apply (H : Matrix (Fin n) (Fin n) ℚ) (k j i : Fin n) :
    cH H k j i = (if j ≠ k ∧ i ≠ k then H j i else 0) + H j k * H k i := by
  unfold cH
  rw [Qk_eq, Matrix.add_apply, dgHdg_apply, HPH_apply]
  by_cases h1 : j = k <;> by_cases h2 : i = k <;> simp [h1, h2]

theorem dgF_apply {κ : Type} [Fintype κ] (p : Fin n → Prop) (F : Matrix (Fin n) κ ℚ) (j : Fin n) (c : κ) :
    (dg p * F) j c = if p j then F j c else 0 := by
  simp only [dg, Matrix.diagonal_mul]; by_cases h : p j <;> simp [h]

theorem Gdg_apply {ι : Type} [Fintype ι] (p : Fin n → Prop) (G : Matrix ι (Fin n) ℚ) (s : ι) (i : Fin n) :
    (G * dg p) s i = if p i then G s i else 0 := by
  simp only [dg, Matrix.mul_diagonal]; by_cases h : p i <;> simp [h]

theorem GPH_apply {ι : Type} [Fintype ι] (G : Matrix ι (Fin n) ℚ) (H : Matrix (Fin n) (Fin n) ℚ)
    (k : Fin n) (s : ι) (i : Fin n) : (G * Pk k * H) s i = G s k * H k i := by
  simp [Matrix.mul_apply, Pk_apply, ite_and, ite_mul, Finset.sum_ite_eq, Finset.sum_ite_eq']

theorem HPF_apply {κ : Type} [Fintype κ] (F : Matrix (Fin n) κ ℚ) (H : Matrix (Fin n) (Fin n) ℚ)
    (k : Fin n) (j : Fin n) (p : κ) : (H * Pk k * F) j p = H j k * F k p := by
  simp [Matrix.mul_apply, Pk_apply, ite_and, ite_mul, Finset.sum_ite_eq, Finset.sum_ite_eq']

theorem GPF_apply {ι κ : Type} [Fintype ι] [Fintype κ] (G : Matrix ι (Fin n) ℚ)
    (F : Matrix (Fin n) κ ℚ) (k : Fin n) (s : ι) (p : κ) : (G * Pk k * F) s p = G s k * F k p := by
  simp [Matrix.mul_apply, Pk_apply, ite_and, ite_mul, Finset.sum_ite_eq, Finset.sum_ite_eq']

theorem cG_apply {ι : Type} [Fintype ι] (G : Matrix ι (Fin n) ℚ) (H : Matrix (Fin n) (Fin n) ℚ)
    (k : Fin n) (s : ι) (i : Fin n) :
    cG G H k s i = (if i ≠ k then G s i else 0) + G s k * H k i := by
  unfold cG
  rw [Matrix.mul_add, ← Matrix.mul_assoc, Matrix.add_apply, Qk_eq, Gdg_apply, GPH_apply]
  by_cases h : i = k <;> simp [h]

theorem cF_apply {κ : Type} [Fintype κ] (F : Matrix (Fin n) κ ℚ) (H : Matrix (Fin n) (Fin n) ℚ)
    (k : Fin n) (j : Fin n) (p : κ) :
    cF F H k j p = (if j ≠ k then F j p else 0) + H j k * F k p := by
  unfold cF
  rw [Matrix.add_mul, Matrix.add_apply, Qk_eq, dgF_apply, HPF_apply]
  by_cases h : j = k <;> simp [h]

theorem Pk_mul_Pk (k : Fin n) : Pk k * Pk k = Pk k := ind_ind _

theorem Pk_H_Pk (H : Matrix (Fin n) (Fin n) ℚ) (k : Fin n) (hkk : H k k = 0) :
    Pk k * H * Pk k = 0 := by
  ext i j
  show (ind ({k} : Finset (Fin n)) * H * ind ({k} : Finset (Fin n))) i j = 0
  rw [ind_eq_dg, dgHdg_apply]
  by_cases h : i ∈ ({k} : Finset (Fin n)) ∧ j ∈ ({k} : Finset (Fin n))
  · rw [if_pos h]
    simp only [Finset.mem_singleton] at h
    rw [h.1, h.2, hkk]
  · rw [if_neg h]

theorem cH_lt (H : Matrix (Fin n) (Fin n) ℚ) (hH : ∀ k j, H k j ≠ 0 → j < k) (k : Fin n) :
    ∀ j i, cH H k j i ≠ 0 → i < j := by
  intro j i h
  rw [cH_apply] at h
  by_contra hij
  apply h
  have a : (if j ≠ k ∧ i ≠ k then H j i else 0) = 0 := by
    split_ifs with hc
    · by_contra hne; exact hij (hH j i hne)
    · rfl
  have b : H j k * H k i = 0 := by
    by_contra hne
    have h1 := hH j k (left_ne_zero_of_mul hne)
    have h2 := hH k i (right_ne_zero_of_mul hne)
    exact hij (h2.trans h1)
  rw [a, b, add_zero]

theorem contract_identity {ι κ : Type} [Fintype ι] [Fintype κ] (G : Matrix ι (Fin n) ℚ)
    (H : Matrix (Fin n) (Fin n) ℚ) (F : Matrix (Fin n) κ ℚ) (hH : ∀ k j, H k j ≠ 0 → j < k) (k : Fin n) :
    G * Nmat H * F = cG G H k * Nmat (cH H k) * cF F H k + G * Pk k * F := by
  have hkk : H k k = 0 := by
    by_contra h; exact lt_irrefl _ (hH k k h)
  have core := contract_core (Pk k) H (Nmat H) (Nmat (cH H k)) (Pk_mul_Pk k) (Pk_H_Pk H k hkk)
    (Nmat_mul H hH) (mul_Nmat (cH H k) (cH_lt H hH k))
  conv_lhs => rw [core]
  unfold cG cF
  simp only [Matrix.add_mul, Matrix.mul_add, Matrix.mul_assoc]

/-- the correction term `G[.,k] F[k,.]` vanishes on odd cells when `a_k <= b_k`. -/
theorem corr_odd (N : NetW n) (k : Fin n) (hk : N.a k ≤ N.b k) (s p : Fin 104)
    (ho : DecoderWall.dot (DF.lq s) (DF.lq p) = 1) : N.G s k * N.F k p = 0 := by
  by_contra h
  have h1 := N.hG s k (left_ne_zero_of_mul h) (DF.lq p) (hk (N.hF k p (right_ne_zero_of_mul h)))
  rw [DF.dot_comm'] at ho
  rw [ho] at h1
  exact one_ne_zero h1

/-- **contraction of one zero-drop node** (`a_k <= b_k`): the network with `k` bypassed and isolated is again a
legal `NetW` with the same charts `a b`, same constants `c`, hence the same `M` on odd cells. -/
noncomputable def contractW (N : NetW n) (k : Fin n) (hk : N.a k ≤ N.b k) : NetW n where
  a := N.a
  b := N.b
  F := cF N.F N.H k
  G := cG N.G N.H k
  H := cH N.H k
  c := N.c
  hF := by
    intro j p h
    rw [cF_apply] at h
    by_cases h1 : (if j ≠ k then N.F j p else 0) = 0
    · have h2 : N.H j k * N.F k p ≠ 0 := by rwa [h1, zero_add] at h
      exact N.hH j k (left_ne_zero_of_mul h2) (hk (N.hF k p (right_ne_zero_of_mul h2)))
    · split_ifs at h1 with hj
      · exact N.hF j p (fun e => h1 (by simp [e]))
      · exact absurd rfl h1
  hG := by
    intro s i h y hy
    rw [cG_apply] at h
    by_cases h1 : (if i ≠ k then N.G s i else 0) = 0
    · have h2 : N.G s k * N.H k i ≠ 0 := by rwa [h1, zero_add] at h
      exact N.hG s k (left_ne_zero_of_mul h2) y (hk (N.hH k i (right_ne_zero_of_mul h2) hy))
    · split_ifs at h1 with hj
      · exact N.hG s i (fun e => h1 (by simp [e])) y hy
      · exact absurd rfl h1
  hHlt := cH_lt N.H N.hHlt k
  hH := by
    intro j i h
    rw [cH_apply] at h
    by_cases h1 : (if j ≠ k ∧ i ≠ k then N.H j i else 0) = 0
    · have h2 : N.H j k * N.H k i ≠ 0 := by rwa [h1, zero_add] at h
      exact (N.hH k i (right_ne_zero_of_mul h2)).trans
        (hk.trans (N.hH j k (left_ne_zero_of_mul h2)))
    · split_ifs at h1 with hj
      · exact N.hH j i (fun e => h1 (by simp [e]))
      · exact absurd rfl h1
  hc := N.hc
  hM := by
    intro s p ho
    have hid := contract_identity N.G N.H N.F N.hHlt k
    have e : (cG N.G N.H k * Nmat (cH N.H k) * cF N.F N.H k) s p =
        (N.G * Nmat N.H * N.F) s p - N.G s k * N.F k p := by
      rw [hid, Matrix.add_apply, GPF_apply]; ring
    show (cG N.G N.H k * Nmat (cH N.H k) * cF N.F N.H k) s p = _
    rw [e, corr_odd N k hk s p ho, sub_zero]
    exact N.hM s p ho

theorem contractW_dead (N : NetW n) (k : Fin n) (hk : N.a k ≤ N.b k) : NetW.Dead (contractW N k hk) k := by
  have hkk : N.H k k = 0 := by
    by_contra h; exact lt_irrefl _ (N.hHlt k k h)
  refine ⟨?_, ?_, ?_, ?_⟩
  · intro p; show cF N.F N.H k k p = 0; rw [cF_apply, hkk]; simp
  · intro s; show cG N.G N.H k s k = 0; rw [cG_apply, hkk]; simp
  · intro j; show cH N.H k j k = 0; rw [cH_apply, hkk]; simp
  · intro i; show cH N.H k k i = 0; rw [cH_apply, hkk]; simp

theorem contractW_dead_keep (N : NetW n) (k : Fin n) (hk : N.a k ≤ N.b k) (j : Fin n)
    (hj : NetW.Dead N j) : NetW.Dead (contractW N k hk) j := by
  obtain ⟨hF, hG, hHc, hHr⟩ := hj
  refine ⟨?_, ?_, ?_, ?_⟩
  · intro p; show cF N.F N.H k j p = 0; rw [cF_apply, hHr k, hF p]; simp
  · intro s; show cG N.G N.H k s j = 0; rw [cG_apply, hG s, hHc k]; simp
  · intro i; show cH N.H k i j = 0; rw [cH_apply, hHc i, hHc k]; simp
  · intro i; show cH N.H k j i = 0; rw [cH_apply, hHr i, hHr k]; simp

/-- live zero-drop nodes: not dead and `a_k <= b_k`. -/
noncomputable def liveZ (N : NetW n) : Finset (Fin n) :=
  Finset.univ.filter fun k => ¬ NetW.Dead N k ∧ N.a k ≤ N.b k

theorem exists_contracted (N : NetW n) :
    ∃ N' : NetW n, N'.a = N.a ∧ N'.b = N.b ∧ N'.c = N.c ∧ liveZ N' = ∅ := by
  have main : ∀ m : ℕ, ∀ N : NetW n, (liveZ N).card ≤ m →
      ∃ N' : NetW n, N'.a = N.a ∧ N'.b = N.b ∧ N'.c = N.c ∧ liveZ N' = ∅ := by
    intro m
    induction m with
    | zero =>
      intro N h
      exact ⟨N, rfl, rfl, rfl, Finset.card_eq_zero.1 (Nat.le_zero.1 h)⟩
    | succ m ih =>
      intro N h
      by_cases hex : (liveZ N).Nonempty
      · obtain ⟨k, hkm⟩ := hex
        have hk : ¬ NetW.Dead N k ∧ N.a k ≤ N.b k := by simpa [liveZ] using hkm
        let N1 := contractW N k hk.2
        have hsub : liveZ N1 ⊆ (liveZ N).erase k := by
          intro j hj
          simp only [liveZ, Finset.mem_filter, Finset.mem_univ, true_and] at hj
          rw [Finset.mem_erase]
          refine ⟨?_, ?_⟩
          · rintro rfl; exact hj.1 (contractW_dead N j hk.2)
          · simp only [liveZ, Finset.mem_filter, Finset.mem_univ, true_and]
            exact ⟨fun hd => hj.1 (contractW_dead_keep N k hk.2 j hd), hj.2⟩
        have hcard : (liveZ N1).card ≤ m := by
          have := Finset.card_le_card hsub
          rw [Finset.card_erase_of_mem hkm] at this
          omega
        obtain ⟨N', ha, hb, hc, hl⟩ := ih N1 hcard
        exact ⟨N', ha, hb, hc, hl⟩
      · exact ⟨N, rfl, rfl, rfl, Finset.not_nonempty_iff_eq_empty.1 hex⟩
  exact main _ N le_rfl

/-- **zero-drop contraction theorem**: if every chart satisfies `b_k <= a_k`, there is a legal `NetW` `N'` with the
same charts and constants (hence the same odd-cell `M`, and the same `D`) in which every live node has drop >= 1;
therefore the number of live nodes is `<= D`.  A counterexample to `D >= 56` has at most 55 live nodes. -/
theorem contracted_live_le_D (N : NetW n) (hba : ∀ k, N.b k ≤ N.a k) :
    ∃ N' : NetW n, N'.a = N.a ∧ N'.b = N.b ∧ N'.c = N.c ∧
      (∀ k, ¬ NetW.Dead N' k → 1 ≤ N'.drop k) ∧
      (Finset.univ.filter fun k => ¬ NetW.Dead N' k).card ≤ ∑ k, N.drop k := by
  obtain ⟨N', ha, hb, hc, hl⟩ := exists_contracted N
  have hdrop : ∀ k, ¬ NetW.Dead N' k → 1 ≤ N'.drop k := by
    intro k hd
    have hn : ¬ (N'.a k ≤ N'.b k) := by
      intro hle
      have : k ∈ liveZ N' := by simp [liveZ, hd, hle]
      rw [hl] at this; simp at this
    have hlt : N'.b k < N'.a k := by
      rw [ha, hb] at hn ⊢
      exact lt_of_le_of_ne (hba k) (fun e => hn (by rw [e]))
    have := Submodule.finrank_lt_finrank_of_lt hlt
    unfold NetW.drop; rw [ha, hb] at this ⊢; omega
  refine ⟨N', ha, hb, hc, hdrop, ?_⟩
  have hdrop' : ∀ k, N'.drop k = N.drop k := by intro k; unfold NetW.drop; rw [ha, hb]
  calc (Finset.univ.filter fun k => ¬ NetW.Dead N' k).card
      = ∑ k ∈ Finset.univ.filter (fun k => ¬ NetW.Dead N' k), 1 := by simp
    _ ≤ ∑ k ∈ Finset.univ.filter (fun k => ¬ NetW.Dead N' k), N'.drop k :=
        Finset.sum_le_sum fun k hk => hdrop k (by simpa using hk)
    _ ≤ ∑ k, N'.drop k := Finset.sum_le_sum_of_subset (Finset.filter_subset _ _)
    _ = ∑ k, N.drop k := Finset.sum_congr rfl fun k _ => hdrop' k

/-! ### non-vacuity 2: contraction toy (chain 0 -> 1 -> 2, node 1 has a = b) -/

namespace ToyContract

def da : Fin 3 → ℕ := ![1, 1, 1]
def db : Fin 3 → ℕ := ![0, 1, 0]
def H : Matrix (Fin 3) (Fin 3) ℚ := !![0, 0, 0; 1, 0, 0; 0, 1, 0]
def G : Matrix (Fin 1) (Fin 3) ℚ := !![0, 0, 1]
def F : Matrix (Fin 3) (Fin 1) ℚ := !![1; 0; 0]

theorem hHlt : ∀ k j, H k j ≠ 0 → j < k := by
  intro k j; fin_cases k <;> fin_cases j <;> simp [H]
theorem hH : ∀ k j, H k j ≠ 0 → db j ≤ da k := by
  intro k j; fin_cases k <;> fin_cases j <;> simp [H, da, db]

theorem cH_eq : cH H 1 = !![0, 0, 0; 0, 0, 0; 1, 0, 0] := by
  ext j i
  rw [cH_apply]
  fin_cases j <;> fin_cases i <;> simp [H]

/-- the contracted relay graph is still legal (strictly lower triangular, relay dimension rule),
`D = sum (da - db) = 2` is unchanged, and `G N F = 1` is preserved with correction term 0. -/
theorem toy_contract :
    (∀ k j, cH H 1 k j ≠ 0 → j < k) ∧ (∀ k j, cH H 1 k j ≠ 0 → db j ≤ da k) ∧
    ∑ k, (da k - db k) = 2 ∧ (da 1 ≤ db 1) ∧
    (G * Nmat H * F : Matrix (Fin 1) (Fin 1) ℚ) = 1 ∧
    (cG G H 1 * Nmat (cH H 1) * cF F H 1 : Matrix (Fin 1) (Fin 1) ℚ) = 1 ∧
    (G * Pk 1 * F : Matrix (Fin 1) (Fin 1) ℚ) = 0 := by
  have hN : Nmat H = !![1, 0, 0; 1, 1, 0; 1, 1, 1] := by
    unfold Nmat
    simp only [Finset.sum_range_succ, Finset.sum_range_zero, zero_add]
    ext i j; fin_cases i <;> fin_cases j <;>
      simp [H, pow_succ, Matrix.mul_apply, Fin.sum_univ_three]
  have hN' : Nmat (cH H 1) = !![1, 0, 0; 0, 1, 0; 1, 0, 1] := by
    rw [cH_eq]; unfold Nmat
    simp only [Finset.sum_range_succ, Finset.sum_range_zero, zero_add]
    ext i j; fin_cases i <;> fin_cases j <;>
      simp [pow_succ, Matrix.mul_apply, Fin.sum_univ_three]
  refine ⟨cH_lt H hHlt 1, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · intro k j h
    rw [cH_eq] at h
    fin_cases k <;> fin_cases j <;> simp_all [da, db]
  · simp [Fin.sum_univ_three, da, db]
  · simp [da, db]
  · rw [hN]; ext i j; fin_cases i; fin_cases j; simp [G, F, Matrix.mul_apply, Fin.sum_univ_three]
  · rw [hN']; ext i j; fin_cases i; fin_cases j
    simp [cG_apply, cF_apply, G, F, H, Matrix.mul_apply, Fin.sum_univ_three]
  · ext i j; fin_cases i; fin_cases j
    rw [GPF_apply]; simp [G, F]

end ToyContract

#print axioms N8.dx_rank_le
#print axioms N8.dx_D_ge
#print axioms N8.netw_dx_D_ge
#print axioms N8.ToyDX.dx_gt_yc
#print axioms N8.contract_identity
#print axioms N8.contractW
#print axioms N8.exists_contracted
#print axioms N8.contracted_live_le_D
#print axioms N8.ToyContract.toy_contract

end N8
