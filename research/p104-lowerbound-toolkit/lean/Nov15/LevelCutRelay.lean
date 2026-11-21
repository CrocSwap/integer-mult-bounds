/-
LevelCutRelay (lane LEANLEVEL, Nov 20).  YCARRIER YC.md sec 2 (node-restricted LEVEL-CUT LAW, relays of ANY slack)
and its NET8 corollary, kernel only.
 ABSTRACT (any DAG H, any dimension functions da db with relay rule `H k j != 0 -> db j <= da k`; no subspaces, no ports):
  C_l = {k : db k < l <= da k};  M_l = (G diag[db<l]) N (diag[l<=da] F)   (YC's M_l: sum over gatherers dim a>=l, depositors dim b<l)
  (1) abstract_node_level_cut_rank : rank M_l <= |C_l|        (walk from a high gatherer to a low depositor meets C_l)
  (2) sum_Cd_le : sum_{l in L} |C_l| <= sum_k (da k - db k)
  (3) abstract_level_D_ge : sum_{l in L} rank M_l <= D
 NetW (da = finrank a, db = finrank b; hH : b_j <= a_k is the slack relay, any slack):
  (4) netw_level_D_ge   : sum_{l in L} rank M_l <= N.D
  (5) netw_gat_dep_ge8  : rank M >= 8 forces >= 8 gathering and >= 8 depositing nodes (via rank_ge8).
  (6) net8_node_corollary : <= 8 gathering and <= 8 depositing nodes  =>  56 <= D  (any carriers / relay slack).
  (7) level_rank_ge56 : [forall l in 2..8, 8 <= rank M_l]  =>  56 <= D.  (YC Cor. B shape)
 Non-vacuity: toy 2-node chain with a SLACK-3 relay (b_0 = 0 <= a_1 = 3), rank M_2 = 1 <= |C_2| = 2.
-/
import Nov15.Net8

open Matrix Module
set_option maxHeartbeats 0
namespace N8
open Classical

variable {n : ℕ}

/-! ### abstract level cut -/

noncomputable def Cd (da db : Fin n → ℕ) (l : ℕ) : Finset (Fin n) :=
  Finset.univ.filter fun k => db k < l ∧ l ≤ da k

noncomputable def lowD (db : Fin n → ℕ) (l : ℕ) : Matrix (Fin n) (Fin n) ℚ :=
  diagonal fun d => if db d < l then 1 else 0

noncomputable def highD (da : Fin n → ℕ) (l : ℕ) : Matrix (Fin n) (Fin n) ℚ :=
  diagonal fun g => if l ≤ da g then 1 else 0

/-- YC's `M_l`: gatherers with `l <= da`, depositors with `db < l`. -/
noncomputable def Mnode {ι κ : Type} [Fintype ι] [Fintype κ] (G : Matrix ι (Fin n) ℚ)
    (H : Matrix (Fin n) (Fin n) ℚ) (F : Matrix (Fin n) κ ℚ) (da db : Fin n → ℕ) (l : ℕ) :
    Matrix ι κ ℚ := (G * lowD db l) * Nmat H * (highD da l * F)

theorem abstract_node_level_cut_rank {ι κ : Type} [Fintype ι] [Fintype κ]
    (G : Matrix ι (Fin n) ℚ) (H : Matrix (Fin n) (Fin n) ℚ) (F : Matrix (Fin n) κ ℚ)
    (da db : Fin n → ℕ) (hHlt : ∀ k j, H k j ≠ 0 → j < k)
    (hH : ∀ k j, H k j ≠ 0 → db j ≤ da k) (l : ℕ) :
    (Mnode G H F da db l).rank ≤ (Cd da db l).card := by
  have hcut : ∀ (s : ι) (p : κ) (d g : Fin n), (G * lowD db l) s d ≠ 0 → (highD da l * F) g p ≠ 0 →
      d ∉ Cd da db l →
      Relation.ReflTransGen (fun j k : Fin n => j ∉ Cd da db l ∧ H k j ≠ 0) g d → False := by
    intro s p d g hGd hFg hdC hw
    have hdb : db d < l := by
      by_contra hlt
      apply hGd
      simp [lowD, Matrix.mul_diagonal, hlt]
    have hga : l ≤ da g := by
      by_contra hlt
      apply hFg
      simp [highD, Matrix.diagonal_mul, hlt]
    have key : ∀ x, Relation.ReflTransGen (fun j k : Fin n => j ∉ Cd da db l ∧ H k j ≠ 0) g x →
        l ≤ da x := by
      intro x hx
      induction hx with
      | refl => exact hga
      | @tail b' c' _ hbc ih =>
        have hn : ¬ (db b' < l ∧ l ≤ da b') := by simpa [Cd] using hbc.1
        have : l ≤ db b' := by
          by_contra hlt; exact hn ⟨not_le.1 hlt, ih⟩
        exact this.trans (hH c' b' hbc.2)
    apply hdC
    simp only [Cd, Finset.mem_filter, Finset.mem_univ, true_and]
    exact ⟨hdb, key d hw⟩
  exact cut_rank H hHlt (G * lowD db l) (highD da l * F) (Cd da db l) hcut

theorem sum_Cd_le (da db : Fin n → ℕ) (L : Finset ℕ) :
    ∑ l ∈ L, (Cd da db l).card ≤ ∑ k, (da k - db k) := by
  have e : ∑ l ∈ L, (Cd da db l).card = ∑ k, (L.filter fun l => db k < l ∧ l ≤ da k).card := by
    simp only [Cd, Finset.card_filter]; exact Finset.sum_comm
  rw [e]
  refine Finset.sum_le_sum fun k _ => ?_
  calc _ ≤ (Finset.Ioc (db k) (da k)).card := by
        apply Finset.card_le_card
        intro l hl
        simp only [Finset.mem_filter, Finset.mem_Ioc] at hl ⊢
        exact hl.2
    _ = da k - db k := by simp

theorem abstract_level_D_ge {ι κ : Type} [Fintype ι] [Fintype κ]
    (G : Matrix ι (Fin n) ℚ) (H : Matrix (Fin n) (Fin n) ℚ) (F : Matrix (Fin n) κ ℚ)
    (da db : Fin n → ℕ) (hHlt : ∀ k j, H k j ≠ 0 → j < k)
    (hH : ∀ k j, H k j ≠ 0 → db j ≤ da k) (L : Finset ℕ) :
    ∑ l ∈ L, (Mnode G H F da db l).rank ≤ ∑ k, (da k - db k) :=
  (Finset.sum_le_sum fun l _ => abstract_node_level_cut_rank G H F da db hHlt hH l).trans
    (sum_Cd_le da db L)

/-! ### NetW -/

/-- chart dimensions of a NetW. -/
noncomputable def NetW.da (N : NetW n) : Fin n → ℕ := fun k => finrank (ZMod 2) (N.a k)
noncomputable def NetW.db (N : NetW n) : Fin n → ℕ := fun k => finrank (ZMod 2) (N.b k)

theorem NetW.relay_dim (N : NetW n) : ∀ k j, N.H k j ≠ 0 → N.db j ≤ N.da k :=
  fun k j h => Submodule.finrank_mono (N.hH k j h)

noncomputable def NetW.Ml (N : NetW n) (l : ℕ) : Matrix (Fin 104) (Fin 104) ℚ :=
  Mnode N.G N.H N.F N.da N.db l

theorem netw_level_D_ge (N : NetW n) (L : Finset ℕ) :
    ∑ l ∈ L, (N.Ml l).rank ≤ ∑ k, (N.da k - N.db k) :=
  abstract_level_D_ge N.G N.H N.F N.da N.db N.hHlt N.relay_dim L

/-- `rank M >= 8` implies at least 8 gathering nodes (F is supported on the gathering rows). -/
theorem rank_le_gat (N : NetW n) : (N.G * Nmat N.H * N.F).rank ≤ (gatS N).card := by
  have e : N.F = ind (gatS N) * N.F := by
    ext k p
    rw [ind, Matrix.diagonal_mul]
    by_cases h : N.F k p = 0
    · simp [h]
    · have : k ∈ gatS N := by
        simp only [gatS, Finset.mem_filter, Finset.mem_univ, true_and]; exact ⟨p, h⟩
      simp [this]
  calc (N.G * Nmat N.H * N.F).rank ≤ N.F.rank := Matrix.rank_mul_le_right _ _
    _ = (ind (gatS N) * N.F).rank := congrArg Matrix.rank e
    _ ≤ (ind (gatS N)).rank := Matrix.rank_mul_le_left _ _
    _ = _ := rank_ind _

theorem rank_le_dep (N : NetW n) : (N.G * Nmat N.H * N.F).rank ≤ (depS N).card := by
  have e : N.G = N.G * ind (depS N) := by
    ext s k
    rw [ind, Matrix.mul_diagonal]
    by_cases h : N.G s k = 0
    · simp [h]
    · have : k ∈ depS N := by
        simp only [depS, Finset.mem_filter, Finset.mem_univ, true_and]; exact ⟨s, h⟩
      simp [this]
  calc (N.G * Nmat N.H * N.F).rank = (N.G * ind (depS N) * Nmat N.H * N.F).rank := by conv_lhs => rw [e]
    _ ≤ (N.G * ind (depS N) * Nmat N.H).rank := Matrix.rank_mul_le_left _ _
    _ ≤ (N.G * ind (depS N)).rank := Matrix.rank_mul_le_left _ _
    _ ≤ (ind (depS N)).rank := Matrix.rank_mul_le_right _ _
    _ = _ := rank_ind _

theorem netw_gat_dep_ge8 (N : NetW n) : 8 ≤ (gatS N).card ∧ 8 ≤ (depS N).card :=
  ⟨(rank_ge8 N).trans (rank_le_gat N), (rank_ge8 N).trans (rank_le_dep N)⟩

/-- **(7)** the per-level rank form: `rank M_l >= 8` on levels 2..8 gives `D >= 56`. -/
theorem level_rank_ge56 (N : NetW n) (h : ∀ l ∈ Finset.Icc 2 8, 8 ≤ (N.Ml l).rank) :
    56 ≤ ∑ k, (N.da k - N.db k) := by
  have := netw_level_D_ge N (Finset.Icc 2 8)
  calc 56 = ∑ _l ∈ Finset.Icc 2 8, 8 := by simp
    _ ≤ ∑ l ∈ Finset.Icc 2 8, (N.Ml l).rank := Finset.sum_le_sum h
    _ ≤ _ := this

/-- **(6) NET8 corollary** (YC Cor. A): at most 8 gathering and at most 8 depositing nodes, any relay slack. -/
theorem net8_node_corollary (N : NetW n) (hg : (gatS N).card ≤ 8) (hd : (depS N).card ≤ 8) :
    56 ≤ ∑ k, (N.da k - N.db k) := by
  have h8 := netw_gat_dep_ge8 N
  have hg8 : (gatS N).card = 8 := le_antisymm hg h8.1
  have hd8 : (depS N).card = 8 := le_antisymm hd h8.2
  have hga := gat_dim N hg8
  have hdb := dep_dim N hd8
  apply level_rank_ge56
  intro l hl
  have hl' := Finset.mem_Icc.1 hl
  have hGl : N.G * lowD N.db l = N.G := by
    ext s d
    rw [lowD, Matrix.mul_diagonal]
    by_cases h0 : N.G s d = 0
    · simp [h0]
    · have : N.db d < l := by
        have := hdb d (by simp only [depS, Finset.mem_filter, Finset.mem_univ, true_and]; exact ⟨s, h0⟩)
        have e : N.db d = finrank (ZMod 2) (N.b d) := rfl
        omega
      simp [this]
  have hFl : highD N.da l * N.F = N.F := by
    ext g p
    rw [highD, Matrix.diagonal_mul]
    by_cases h0 : N.F g p = 0
    · simp [h0]
    · have : l ≤ N.da g := by
        have := hga g (by simp only [gatS, Finset.mem_filter, Finset.mem_univ, true_and]; exact ⟨p, h0⟩)
        have e : N.da g = finrank (ZMod 2) (N.a g) := rfl
        omega
      simp [this]
  have : N.Ml l = N.G * Nmat N.H * N.F := by
    unfold NetW.Ml Mnode
    rw [hGl, hFl]
  rw [this]
  exact rank_ge8 N

/-! ### non-vacuity: a 2-node chain whose relay has slack 3 -/

namespace Toy

/-- node 0 gathers (a-dim 2, b-dim 0); relay (b_0 = 0 <= a_1 = 3, slack 3) to node 1 (a-dim 3, b-dim 1) which deposits. -/
def da : Fin 2 → ℕ := ![2, 3]
def db : Fin 2 → ℕ := ![0, 1]
def H : Matrix (Fin 2) (Fin 2) ℚ := !![0, 0; 1, 0]
def G : Matrix (Fin 1) (Fin 2) ℚ := !![0, 1]
def F : Matrix (Fin 2) (Fin 1) ℚ := !![1; 0]

theorem hHlt : ∀ k j, H k j ≠ 0 → j < k := by
  intro k j; fin_cases k <;> fin_cases j <;> simp [H]
theorem hH : ∀ k j, H k j ≠ 0 → db j ≤ da k := by
  intro k j; fin_cases k <;> fin_cases j <;> simp [H, da, db]

theorem N_eq : Nmat H = !![1, 0; 1, 1] := by
  have : H ^ 2 = 0 := by
    ext i j; fin_cases i <;> fin_cases j <;> simp [H, pow_two, Matrix.mul_apply, Fin.sum_univ_two]
  simp [Nmat, Finset.sum_range_succ, this, H]
  ext i j; fin_cases i <;> fin_cases j <;> simp

theorem M2 : Mnode G H F da db 2 = 1 := by
  have h1 : G * lowD db 2 = G := by
    ext i j; fin_cases i; fin_cases j <;> simp [G, lowD, db, Matrix.mul_diagonal]
  have h2 : highD da 2 * F = F := by
    ext i j; fin_cases i <;> fin_cases j <;> simp [F, highD, da, Matrix.diagonal_mul]
  unfold Mnode
  rw [h1, h2, N_eq]
  ext i j
  fin_cases i; fin_cases j
  simp only [G, F, Matrix.mul_apply, Fin.sum_univ_two]
  simp

theorem toy_rank : (Mnode G H F da db 2).rank = 1 := by rw [M2]; exact Matrix.rank_one

theorem toy_cut : (Cd da db 2).card = 2 := by
  have : Cd da db 2 = Finset.univ := by
    ext k; fin_cases k <;> simp [Cd, da, db]
  rw [this]; simp

/-- the cut bound is instantiated on the slack-relay toy, and is not an equality of zeros: `1 <= 2`, `D = 4`. -/
theorem toy_bound : (Mnode G H F da db 2).rank ≤ (Cd da db 2).card ∧
    ∑ l ∈ Finset.Icc 1 3, (Mnode G H F da db l).rank ≤ ∑ k, (da k - db k) :=
  ⟨abstract_node_level_cut_rank G H F da db hHlt hH 2,
   abstract_level_D_ge G H F da db hHlt hH _⟩

end Toy

end N8

#print axioms N8.abstract_node_level_cut_rank
#print axioms N8.sum_Cd_le
#print axioms N8.abstract_level_D_ge
#print axioms N8.netw_level_D_ge
#print axioms N8.netw_gat_dep_ge8
#print axioms N8.level_rank_ge56
#print axioms N8.net8_node_corollary
#print axioms N8.Toy.toy_rank
#print axioms N8.Toy.toy_bound
