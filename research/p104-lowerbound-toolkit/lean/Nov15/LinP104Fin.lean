import Nov15.LinP104Base
import Nov15.LinP104Pat0
import Nov15.LinP104Pat1
import Nov15.LinP104Pat2
import Nov15.LinP104Pat3
import Nov15.LinP104Pat4
import Nov15.LinP104Pat5
import Nov15.LinP104Pat6
import Nov15.LinP104Pat7
open Matrix Finset LinCore LinFinal

namespace P104
open P104Data

lemma patRow_true (t : ℕ) (ht : t < 104) : patRow t = true := by
  have key : ∀ k : ℕ, k < 8 → ∀ u : ℕ, u < 13 → patRow (13 * k + u) = true := by
    intro k hk u hu
    interval_cases k
    · have h := patChunk0; rw [List.all_eq_true] at h; exact h u (List.mem_range.2 hu)
    · have h := patChunk1; rw [List.all_eq_true] at h; exact h u (List.mem_range.2 hu)
    · have h := patChunk2; rw [List.all_eq_true] at h; exact h u (List.mem_range.2 hu)
    · have h := patChunk3; rw [List.all_eq_true] at h; exact h u (List.mem_range.2 hu)
    · have h := patChunk4; rw [List.all_eq_true] at h; exact h u (List.mem_range.2 hu)
    · have h := patChunk5; rw [List.all_eq_true] at h; exact h u (List.mem_range.2 hu)
    · have h := patChunk6; rw [List.all_eq_true] at h; exact h u (List.mem_range.2 hu)
    · have h := patChunk7; rw [List.all_eq_true] at h; exact h u (List.mem_range.2 hu)
  have := key (t / 13) (by omega) (t % 13) (by omega)
  rwa [show 13 * (t / 13) + t % 13 = t from by omega] at this

lemma pat_nat (t s : Fin 104) :
    ((Qlab t s : ℤ) - 1 - (nform (xMasks.getD t.1 0) (xMasks.getD s.1 0) : ℤ)) % 2 = 0 := by
  have h1 := patRow_true t.1 t.2
  unfold patRow at h1
  rw [List.all_eq_true] at h1
  have h2 := h1 s.1 (List.mem_range.2 s.2)
  have ht : (⟨t.1 % 104, Nat.mod_lt _ (by norm_num)⟩ : Fin 104) = t := Fin.ext (Nat.mod_eq_of_lt t.2)
  have hs : (⟨s.1 % 104, Nat.mod_lt _ (by norm_num)⟩ : Fin 104) = s := Fin.ext (Nat.mod_eq_of_lt s.2)
  simp only [ht, hs, beq_iff_eq] at h2
  exact h2

lemma Qlab_pat : ∀ t s : Fin 104, (Qlab t s : F2) = 1 + (Bm *ᵥ lab t) ⬝ᵥ lab s := by
  intro t s
  rw [form_nat]
  have h := pat_nat t s
  have h2 : (2 : ℤ) ∣ ((Qlab t s : ℤ) - 1 - (nform (xMasks.getD t.1 0) (xMasks.getD s.1 0) : ℤ)) :=
    Int.dvd_of_emod_eq_zero h
  have h3 := (ZMod.intCast_zmod_eq_zero_iff_dvd _ 2).2 h2
  push_cast at h3
  have : ((Qlab t s : ℤ) : F2) = 1 + (nform (xMasks.getD t.1 0) (xMasks.getD s.1 0) : F2) := by
    have := sub_eq_zero.1 (by simpa [sub_sub] using h3 : ((Qlab t s : ℤ) : F2) -
      (1 + (nform (xMasks.getD t.1 0) (xMasks.getD s.1 0) : F2)) = 0)
    exact this
  exact this

lemma Qlab_01 : ∀ t s, Qlab t s = 0 ∨ Qlab t s = 1 := by
  intro t s; unfold Qlab; split_ifs <;> simp

lemma Qlab_diag : ∀ t, Qlab t t = 1 := by decide +kernel

/-! ### the quadric expansion and the HInj certificate -/

lemma quad_expand {n : ℕ} (A : Matrix (Fin n) (Fin n) F2) (y : Fin n → F2) :
    y ⬝ᵥ (A *ᵥ y) = ∑ i, A i i * y i +
      ∑ e : Eix n, (A e.1.1 e.1.2 + A e.1.2 e.1.1) * (y e.1.1 * y e.1.2) := by
  classical
  have hL : y ⬝ᵥ (A *ᵥ y) = ∑ p : Fin n × Fin n, y p.1 * A p.1 p.2 * y p.2 := by
    simp only [dotProduct, mulVec, Fintype.sum_prod_type, Finset.mul_sum, mul_assoc]
  set T1 : Fin n × Fin n → F2 := fun p => if p.1 < p.2 then y p.1 * A p.1 p.2 * y p.2 else 0 with hT1
  set T2 : Fin n × Fin n → F2 := fun q => if q.1 < q.2 then y q.2 * A q.2 q.1 * y q.1 else 0 with hT2
  set T3 : Fin n × Fin n → F2 := fun p => if p.1 = p.2 then y p.1 * A p.1 p.2 * y p.2 else 0 with hT3
  have hsplit : ∀ p : Fin n × Fin n, y p.1 * A p.1 p.2 * y p.2 = T1 p + T2 p.swap + T3 p := by
    intro p
    obtain ⟨i, j⟩ := p
    simp only [hT1, hT2, hT3, Prod.swap_prod_mk]
    rcases lt_trichotomy i j with h | h | h
    · simp [h, not_lt.2 h.le, h.ne]
    · subst h; simp
    · simp [h, not_lt.2 h.le, h.ne']
  have hswap : ∑ p : Fin n × Fin n, T2 p.swap = ∑ p : Fin n × Fin n, T2 p :=
    Equiv.sum_comp (Equiv.prodComm (Fin n) (Fin n)) T2
  have h3 : ∑ p : Fin n × Fin n, T3 p = ∑ i, A i i * y i := by
    simp only [hT3, Fintype.sum_prod_type]
    refine Finset.sum_congr rfl fun i _ => ?_
    rw [Finset.sum_ite_eq]
    simp only [Finset.mem_univ, if_true]
    calc y i * A i i * y i = A i i * (y i * y i) := by ring
      _ = _ := by rw [f2_sq]
  have hR : ∑ e : Eix n, (A e.1.1 e.1.2 + A e.1.2 e.1.1) * (y e.1.1 * y e.1.2) =
      ∑ p : Fin n × Fin n, if p.1 < p.2 then (A p.1 p.2 + A p.2 p.1) * (y p.1 * y p.2) else 0 := by
    rw [← Finset.sum_filter]
    rw [Finset.sum_subtype (Finset.univ.filter (fun p : Fin n × Fin n => p.1 < p.2))
      (p := fun p : Fin n × Fin n => p.1 < p.2) (by simp)]
  have hsum : ∑ p : Fin n × Fin n, y p.1 * A p.1 p.2 * y p.2 =
      ∑ p : Fin n × Fin n, T1 p + ∑ p : Fin n × Fin n, T2 p + ∑ p : Fin n × Fin n, T3 p := by
    simp only [hsplit]
    rw [Finset.sum_add_distrib, Finset.sum_add_distrib, hswap]
  have hmix : ∑ p : Fin n × Fin n, T1 p + ∑ p : Fin n × Fin n, T2 p =
      ∑ p : Fin n × Fin n, if p.1 < p.2 then (A p.1 p.2 + A p.2 p.1) * (y p.1 * y p.2) else 0 := by
    rw [← Finset.sum_add_distrib]
    refine Finset.sum_congr rfl fun p _ => ?_
    simp only [hT1, hT2]
    split_ifs <;> ring
  rw [hL, hsum, h3, hR, ← hmix]
  ring

/-- the monomial evaluation: 8 linear + 28 quadratic monomials -/
def monv {n : ℕ} (x : Fin n → F2) : Fin n ⊕ Eix n → F2
  | Sum.inl i => x i
  | Sum.inr e => x e.1.1 * x e.1.2

/-- the coefficient vector of the quadric x ↦ x^T A x -/
def uco {n : ℕ} (A : Matrix (Fin n) (Fin n) F2) : Fin n ⊕ Eix n → F2
  | Sum.inl i => A i i
  | Sum.inr e => A e.1.1 e.1.2 + A e.1.2 e.1.1

lemma quad_mon {n : ℕ} (A : Matrix (Fin n) (Fin n) F2) (y : Fin n → F2) :
    y ⬝ᵥ (A *ᵥ y) = ∑ col, monv y col * uco A col := by
  rw [quad_expand, Fintype.sum_sum_type]
  simp only [monv, uco]
  congr 1
  · exact Finset.sum_congr rfl fun i _ => mul_comm _ _
  · exact Finset.sum_congr rfl fun e _ => mul_comm _ _

/-- index of a monomial in the python order (8 linear, then pairs i<j lexicographically) -/
def midx : Fin 8 ⊕ Eix 8 → ℕ
  | Sum.inl i => i.1
  | Sum.inr e => 8 + (7 * e.1.1.1 - e.1.1.1 * (e.1.1.1 - 1) / 2) + (e.1.2.1 - e.1.1.1 - 1)

def selL (r : Fin 36) : Fin 104 := ⟨sel.getD r.1 0 % 104, Nat.mod_lt _ (by norm_num)⟩
def Linv (col : Fin 8 ⊕ Eix 8) (r : Fin 36) : F2 :=
  if (linvMasks.getD (midx col) 0).testBit r.1 then 1 else 0

/-- the certificate: Linv * (monomials on the 36 selected labels) = identity -/
lemma Linv_Mon_c0 : ∀ col col' : Fin 8 ⊕ Eix 8, 0 ≤ midx col → midx col < 9 →
    ∑ r : Fin 36, Linv col r * monv (lab (selL r)) col' = if col = col' then 1 else 0 := by
  decide +kernel

lemma Linv_Mon_c1 : ∀ col col' : Fin 8 ⊕ Eix 8, 9 ≤ midx col → midx col < 18 →
    ∑ r : Fin 36, Linv col r * monv (lab (selL r)) col' = if col = col' then 1 else 0 := by
  decide +kernel

lemma Linv_Mon_c2 : ∀ col col' : Fin 8 ⊕ Eix 8, 18 ≤ midx col → midx col < 27 →
    ∑ r : Fin 36, Linv col r * monv (lab (selL r)) col' = if col = col' then 1 else 0 := by
  decide +kernel

lemma Linv_Mon_c3 : ∀ col col' : Fin 8 ⊕ Eix 8, 27 ≤ midx col → midx col < 36 →
    ∑ r : Fin 36, Linv col r * monv (lab (selL r)) col' = if col = col' then 1 else 0 := by
  decide +kernel

lemma midx_lt : ∀ col : Fin 8 ⊕ Eix 8, midx col < 36 := by decide +kernel

lemma Linv_Mon : ∀ col col' : Fin 8 ⊕ Eix 8,
    ∑ r : Fin 36, Linv col r * monv (lab (selL r)) col' = if col = col' then 1 else 0 := by
  intro col col'
  have h := midx_lt col
  by_cases h0 : midx col < 9
  · exact Linv_Mon_c0 col col' (Nat.zero_le _) h0
  by_cases h1 : midx col < 18
  · exact Linv_Mon_c1 col col' (by omega) h1
  by_cases h2 : midx col < 27
  · exact Linv_Mon_c2 col col' (by omega) h2
  exact Linv_Mon_c3 col col' (by omega) h

/-- HNoQuadric for P104: a quadratic form vanishing on all 104 labels vanishes identically. -/
theorem hinj104 : HInj lab := by
  intro A hA y
  have hu : ∀ r : Fin 36, ∑ col, monv (lab (selL r)) col * uco A col = 0 := by
    intro r; rw [← quad_mon]; exact hA _
  have hc : ∀ col, uco A col = 0 := by
    intro col
    have h1 : uco A col = ∑ col', (if col = col' then (1 : F2) else 0) * uco A col' := by
      simp
    calc uco A col = ∑ col', (if col = col' then (1 : F2) else 0) * uco A col' := h1
      _ = ∑ col', (∑ r : Fin 36, Linv col r * monv (lab (selL r)) col') * uco A col' := by
          refine Finset.sum_congr rfl fun col' _ => ?_
          rw [Linv_Mon]
      _ = ∑ r : Fin 36, Linv col r * ∑ col', monv (lab (selL r)) col' * uco A col' := by
          simp only [Finset.sum_mul, Finset.mul_sum]
          rw [Finset.sum_comm]
          refine Finset.sum_congr rfl fun r _ => Finset.sum_congr rfl fun col' _ => ?_
          ring
      _ = 0 := Finset.sum_eq_zero fun r _ => by rw [hu r, mul_zero]
  rw [quad_mon]
  exact Finset.sum_eq_zero fun col _ => by rw [hc col, mul_zero]

lemma card_Eix8 : Fintype.card (Eix 8) = 28 := by decide

/-- P104, every half-integer LINEAR decoder (any number of rows): cost >= 56.
Hypotheses beyond the decoder law: parities of rows e j are the linear functionals α_j·c_t (w side) and
(Bm p_j)·c_t (v side) [definition of "linear"], and the 8x8 matrix M = (α_j·p_k) is invertible [hMu,
Cauchy-Binet consequence of Kbar = B, kept as a named hypothesis]. -/
theorem p104_linear_cost_ge {κ : Type*} [DecidableEq κ] (J : Finset κ) (w v : κ → Fin 104 → ℤ)
    (e : Fin 8 → κ) (α p : Fin 8 → Fin 8 → F2)
    (hdec : ∀ t s, ∑ k ∈ J, w k t * v k s * Qlab t s = if t = s then 2 else 0)
    (einj : Function.Injective e) (eJ : ∀ j, e j ∈ J)
    (parw : ∀ j t, Doubling.par (w (e j)) t = α j ⬝ᵥ lab t)
    (parv : ∀ j t, Doubling.par (v (e j)) t = (Bm *ᵥ p j) ⬝ᵥ lab t)
    (hMu : IsUnit (Matrix.of fun j k => α j ⬝ᵥ p k).det) :
    56 ≤ ∑ k ∈ J, (Doubling.Qk Qlab (w k) (v k)).rank := by
  have h := linear_cost_ge (Mz := Qlab) (J := J) (w := w) (v := v) (e := e) (α := α) (p := p)
    Qlab_01 Qlab_diag hdec Bm_symm Bm_unit hinj104 (by rw [card_Eix8]; simp)
    ⟨Qlab_pat, einj, eJ, parw, parv⟩ hMu
  rw [card_Eix8] at h
  omega

end P104

#print axioms P104.p104_linear_cost_ge
#print axioms P104.hinj104
#print axioms P104.Qlab_pat
