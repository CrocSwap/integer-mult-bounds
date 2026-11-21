/-
Net8 (lane LEAN-NET8, Nov 19).  THEOREM NET8 (cards/WILD/LUNCH/exchange/d56dir/realize/RZ.md sec 4), kernel-checked:
a P104 NetW with exactly 8 gathering and 8 depositing descents has D = sum of drops >= 56, ANY relay graph.
 (1) Phi: M = sum_k (G N)[:,k] F[k,:] over the gathering k  and  Lambda: M = sum_k G[:,k] (N F)[k,:] over the
     depositing k are two 8-row IsDecoders (after the c_s scaling);
 (2) DFR.dyadicRigidity8 gives dim a_k >= 8 (gathering k) and dim b_k <= 1 (depositing k);
 (3) NO Menger: for each level l in 2..8 the set C_l = {k : dim b_k < l <= dim a_k} meets every gather->deposit
     walk (relay b_j <= a_k keeps the level), so rank M <= |C_l| (Net8Cut.cut_rank), and rank M >= 8 (clique8);
 (4) drop_k >= #{l in [2,8] : k in C_l}, so D >= sum_l |C_l| >= 7*8 = 56.
NetW: F[k,p]!=0 -> q_p in a_k; H[k,j]!=0 -> j<k, b_j <= a_k; G[s,k]!=0 -> b_k ⊥ q_s;
M = G (1-H)^{-1} F = c_s delta on every odd pair (diagonal included), c_s != 0.   Kernel only.
-/
import Nov15.DecoderFactsRigid
import Nov15.Net8Cut
import Mathlib.LinearAlgebra.Matrix.BilinearForm
import Mathlib.LinearAlgebra.BilinearForm.Orthogonal

open Matrix Module
set_option maxHeartbeats 0
namespace N8
open Classical

abbrev W9 := Fin 9 → ZMod 2

structure NetW (n : ℕ) where
  a : Fin n → Submodule (ZMod 2) W9
  b : Fin n → Submodule (ZMod 2) W9
  F : Matrix (Fin n) (Fin 104) ℚ
  G : Matrix (Fin 104) (Fin n) ℚ
  H : Matrix (Fin n) (Fin n) ℚ
  c : Fin 104 → ℚ
  hF : ∀ k p, F k p ≠ 0 → DF.lq p ∈ a k
  hG : ∀ s k, G s k ≠ 0 → ∀ y ∈ b k, DecoderWall.dot y (DF.lq s) = 0
  hHlt : ∀ k j, H k j ≠ 0 → j < k
  hH : ∀ k j, H k j ≠ 0 → b j ≤ a k
  hc : ∀ s, c s ≠ 0
  hM : ∀ s p, DecoderWall.dot (DF.lq s) (DF.lq p) = 1 →
    (G * Nmat H * F) s p = if s = p then c s else 0

variable {n : ℕ}

noncomputable def gatS (N : NetW n) : Finset (Fin n) := Finset.univ.filter fun k => ∃ p, N.F k p ≠ 0
noncomputable def depS (N : NetW n) : Finset (Fin n) := Finset.univ.filter fun k => ∃ s, N.G s k ≠ 0
noncomputable def NetW.drop (N : NetW n) (k : Fin n) : ℕ :=
  finrank (ZMod 2) (N.a k) - finrank (ZMod 2) (N.b k)

theorem lq_diag (p : Fin 104) : DecoderWall.dot (DF.lq p) (DF.lq p) = 1 := by
  have h : ∀ p : Fin 104, DW4.dotb (DW4.lab p) (DW4.lab p) = true := by decide +kernel
  exact (DF.dotb_iff _ _).1 (h p)

/-! ### two factorizations -/

theorem factor_Phi (N : NetW n) (s p : Fin 104) :
    ∑ k : {k // k ∈ gatS N}, (N.G * Nmat N.H) s k.1 / N.c s * N.F k.1 p
      = (N.G * Nmat N.H * N.F) s p / N.c s := by
  calc _ = ∑ k ∈ gatS N, (N.G * Nmat N.H) s k / N.c s * N.F k p :=
        Finset.sum_coe_sort (gatS N) (fun k => (N.G * Nmat N.H) s k / N.c s * N.F k p)
    _ = ∑ k, (N.G * Nmat N.H) s k / N.c s * N.F k p := by
        apply Finset.sum_subset (Finset.subset_univ _)
        intro k _ hk
        have : N.F k p = 0 := by
          by_contra h; exact hk (by simp only [gatS, Finset.mem_filter, Finset.mem_univ, true_and]; exact ⟨p, h⟩)
        rw [this, mul_zero]
    _ = _ := by
        have e : (N.G * Nmat N.H * N.F) s p = ∑ k, (N.G * Nmat N.H) s k * N.F k p := Matrix.mul_apply
        rw [e, div_eq_mul_inv, Finset.sum_mul]
        exact Finset.sum_congr rfl fun k _ => by ring

theorem factor_Lam (N : NetW n) (s p : Fin 104) :
    ∑ k : {k // k ∈ depS N}, N.G s k.1 / N.c s * (Nmat N.H * N.F) k.1 p
      = (N.G * Nmat N.H * N.F) s p / N.c s := by
  calc _ = ∑ k ∈ depS N, N.G s k / N.c s * (Nmat N.H * N.F) k p :=
        Finset.sum_coe_sort (depS N) (fun k => N.G s k / N.c s * (Nmat N.H * N.F) k p)
    _ = ∑ k, N.G s k / N.c s * (Nmat N.H * N.F) k p := by
        apply Finset.sum_subset (Finset.subset_univ _)
        intro k _ hk
        have : N.G s k = 0 := by
          by_contra h; exact hk (by simp only [depS, Finset.mem_filter, Finset.mem_univ, true_and]; exact ⟨s, h⟩)
        rw [this, zero_div, zero_mul]
    _ = _ := by
        have e : (N.G * Nmat N.H * N.F) s p = ∑ k, N.G s k * (Nmat N.H * N.F) k p := by
          rw [Matrix.mul_assoc]; exact Matrix.mul_apply
        rw [e, div_eq_mul_inv, Finset.sum_mul]
        exact Finset.sum_congr rfl fun k _ => by ring

theorem decPhi (N : NetW n) : DecoderWall.IsDecoder DF.lq
    (fun s (k : {k // k ∈ gatS N}) => (N.G * Nmat N.H) s k.1 / N.c s) (fun p k => N.F k.1 p) where
  diag := fun t => by
    show ∑ k : {k // k ∈ gatS N}, (N.G * Nmat N.H) t k.1 / N.c t * N.F k.1 t = 1
    rw [factor_Phi, N.hM t t (lq_diag t), if_pos rfl]
    exact div_self (N.hc t)
  odd := fun t s hts ho => by
    show ∑ k : {k // k ∈ gatS N}, (N.G * Nmat N.H) t k.1 / N.c t * N.F k.1 s = 0
    rw [factor_Phi, N.hM t s ho, if_neg hts, zero_div]

theorem decLam (N : NetW n) : DecoderWall.IsDecoder DF.lq
    (fun s (k : {k // k ∈ depS N}) => N.G s k.1 / N.c s) (fun p k => (Nmat N.H * N.F) k.1 p) where
  diag := fun t => by
    show ∑ k : {k // k ∈ depS N}, N.G t k.1 / N.c t * (Nmat N.H * N.F) k.1 t = 1
    rw [factor_Lam, N.hM t t (lq_diag t), if_pos rfl]
    exact div_self (N.hc t)
  odd := fun t s hts ho => by
    show ∑ k : {k // k ∈ depS N}, N.G t k.1 / N.c t * (Nmat N.H * N.F) k.1 s = 0
    rw [factor_Lam, N.hM t s ho, if_neg hts, zero_div]

/-! ### orthogonal complement dimension -/

noncomputable def Bd : LinearMap.BilinForm (ZMod 2) W9 := Matrix.toBilin' (1 : Matrix (Fin 9) (Fin 9) (ZMod 2))

theorem Bd_apply (x y : W9) : Bd x y = DecoderWall.dot x y := by
  simp [Bd, Matrix.toBilin'_apply', DecoderWall.dot]

theorem orth_dim (W : Submodule (ZMod 2) W9) :
    finrank (ZMod 2) W + finrank (ZMod 2) (Bd.orthogonal W) ≤ 9 := by
  have h := LinearMap.BilinForm.finrank_add_finrank_orthogonal' (B := Bd) W
  have hk : LinearMap.ker Bd = ⊥ := by
    rw [LinearMap.ker_eq_bot']
    intro x hx
    funext i
    have := congrArg (fun f => f (Pi.single i 1)) hx
    simpa [Bd_apply, DecoderWall.dot, dotProduct, Pi.single_apply] using this
  have h9 : finrank (ZMod 2) W9 = 9 := by simp
  rw [hk, inf_bot_eq, finrank_bot, h9] at h
  omega

/-! ### rigidity consequences -/

theorem gat_dim (N : NetW n) (hg : (gatS N).card = 8) : ∀ k ∈ gatS N, 8 ≤ finrank (ZMod 2) (N.a k) := by
  intro k hk
  have hr := DFR.dyadicRigidity8 {k // k ∈ gatS N} _ _ (decPhi N) (by rw [Fintype.card_coe]; exact hg)
  have h3 := DF.row_span_ge_eight _ (hr ⟨k, hk⟩).2
  refine h3.trans (Submodule.finrank_mono (Submodule.span_le.2 ?_))
  rintro _ ⟨t, rfl⟩
  have ht := t.2
  simp only [DecoderWall.gat, Finset.mem_filter, Finset.mem_univ, true_and] at ht
  exact N.hF k t ht

theorem dep_dim (N : NetW n) (hd : (depS N).card = 8) : ∀ k ∈ depS N, finrank (ZMod 2) (N.b k) ≤ 1 := by
  intro k hk
  have hr := DFR.dyadicRigidity8 {k // k ∈ depS N} _ _ (decLam N) (by rw [Fintype.card_coe]; exact hd)
  have h3 := DF.row_span_ge_eight _ (hr ⟨k, hk⟩).1
  have h4 : finrank (ZMod 2) (Submodule.span (ZMod 2) (Set.range fun t : DecoderWall.dep
      (fun s (k : {k // k ∈ depS N}) => N.G s k.1 / N.c s) ⟨k, hk⟩ => DF.lq t))
      ≤ finrank (ZMod 2) (Bd.orthogonal (N.b k)) := by
    refine Submodule.finrank_mono (Submodule.span_le.2 ?_)
    rintro _ ⟨t, rfl⟩
    have ht := t.2
    simp only [DecoderWall.dep, Finset.mem_filter, Finset.mem_univ, true_and] at ht
    have ht' : N.G t k ≠ 0 := fun h0 => ht (by simp [h0])
    show DF.lq t.1 ∈ Bd.orthogonal (N.b k)
    rw [LinearMap.BilinForm.mem_orthogonal_iff]
    intro y hy
    rw [Bd_apply]
    exact N.hG t k ht' y hy
  have := orth_dim (N.b k)
  omega

/-! ### level cuts -/

noncomputable def Cl (N : NetW n) (l : ℕ) : Finset (Fin n) :=
  Finset.univ.filter fun k => finrank (ZMod 2) (N.b k) < l ∧ l ≤ finrank (ZMod 2) (N.a k)

theorem cl_cut (N : NetW n) (hga : ∀ k ∈ gatS N, 8 ≤ finrank (ZMod 2) (N.a k))
    (hdb : ∀ k ∈ depS N, finrank (ZMod 2) (N.b k) ≤ 1) (l : ℕ) (h2 : 2 ≤ l) (h8 : l ≤ 8) :
    ∀ (s : Fin 104) (p : Fin 104) (d g : Fin n), N.G s d ≠ 0 → N.F g p ≠ 0 → d ∉ Cl N l →
      Relation.ReflTransGen (fun j k : Fin n => j ∉ Cl N l ∧ N.H k j ≠ 0) g d → False := by
  intro s p d g hGd hFg hdC hw
  have hg : g ∈ gatS N := by simp only [gatS, Finset.mem_filter, Finset.mem_univ, true_and]; exact ⟨p, hFg⟩
  have hd : d ∈ depS N := by simp only [depS, Finset.mem_filter, Finset.mem_univ, true_and]; exact ⟨s, hGd⟩
  have key : ∀ x, Relation.ReflTransGen (fun j k : Fin n => j ∉ Cl N l ∧ N.H k j ≠ 0) g x →
      l ≤ finrank (ZMod 2) (N.a x) := by
    intro x hx
    induction hx with
    | refl => exact h8.trans (hga g hg)
    | @tail b' c' _ hbc ih =>
      have hb : b' ∉ Cl N l := hbc.1
      have hn : ¬ (finrank (ZMod 2) (N.b b') < l ∧ l ≤ finrank (ZMod 2) (N.a b')) := by
        simpa [Cl] using hb
      have : l ≤ finrank (ZMod 2) (N.b b') := by
        by_contra hlt; exact hn ⟨not_le.1 hlt, ih⟩
      exact this.trans (Submodule.finrank_mono (N.hH c' b' hbc.2))
  apply hdC
  simp only [Cl, Finset.mem_filter, Finset.mem_univ, true_and]
  have := hdb d hd
  exact ⟨by omega, key d hw⟩

theorem rank_ge8 (N : NetW n) : 8 ≤ (N.G * Nmat N.H * N.F).rank := by
  have hs : (N.G * Nmat N.H * N.F).submatrix DF.clique8 DF.clique8 =
      diagonal (fun i => N.c (DF.clique8 i)) := by
    ext i j
    have ho : DecoderWall.dot (DF.lq (DF.clique8 i)) (DF.lq (DF.clique8 j)) = 1 := by
      by_cases e : i = j
      · subst e; exact lq_diag _
      · exact DF.clique8_odd i j e
    simp only [Matrix.submatrix_apply, Matrix.diagonal_apply]
    rw [N.hM _ _ ho]
    simp [DF.clique8_inj.eq_iff]
  have h1 := Matrix.rank_submatrix_le (N.G * Nmat N.H * N.F) DF.clique8 DF.clique8
  rw [hs, Matrix.rank_diagonal] at h1
  have : Fintype.card {i : Fin 8 // N.c (DF.clique8 i) ≠ 0} = 8 := by
    rw [Fintype.card_congr (Equiv.subtypeUnivEquiv (fun i => N.hc (DF.clique8 i)))]; simp
  omega

/-- **THEOREM NET8.** -/
theorem net8 (N : NetW n) (hg : (gatS N).card = 8) (hd : (depS N).card = 8) :
    56 ≤ ∑ k, N.drop k := by
  have hga := gat_dim N hg
  have hdb := dep_dim N hd
  have hrank := rank_ge8 N
  have hC : ∀ l ∈ Finset.Icc 2 8, 8 ≤ (Cl N l).card := fun l hl => by
    have hl' := Finset.mem_Icc.1 hl
    have := cut_rank N.H N.hHlt N.G N.F (Cl N l) (cl_cut N hga hdb l hl'.1 hl'.2)
    omega
  calc 56 = ∑ _l ∈ Finset.Icc 2 8, 8 := by simp
    _ ≤ ∑ l ∈ Finset.Icc 2 8, (Cl N l).card := Finset.sum_le_sum hC
    _ = ∑ k, ((Finset.Icc 2 8).filter fun l =>
          finrank (ZMod 2) (N.b k) < l ∧ l ≤ finrank (ZMod 2) (N.a k)).card := by
        simp only [Cl, Finset.card_filter]; exact Finset.sum_comm
    _ ≤ ∑ k, N.drop k := by
        refine Finset.sum_le_sum fun k _ => ?_
        calc _ ≤ (Finset.Ioc (finrank (ZMod 2) (N.b k)) (finrank (ZMod 2) (N.a k))).card := by
              apply Finset.card_le_card
              intro l hl
              simp only [Finset.mem_filter, Finset.mem_Icc, Finset.mem_Ioc] at hl ⊢
              exact ⟨hl.2.1, hl.2.2⟩
          _ = N.drop k := by simp [NetW.drop]

end N8

#print axioms N8.net8
