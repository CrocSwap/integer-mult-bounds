/-
Bridge7761P0 .  Generic lemmas for the packed proof of hO (outVec Recipe7761 .. = O7761):
  BT / BT.get        : binary lookup tree (kernel lookups in O(depth));
  digits_zero        : sum_{i<n} v_i X^i = 0 with |v_i| < X  =>  all v_i = 0   (digit uniqueness, integers);
  EB                 : the block-packing linear functional v |-> sum_{i<W} v(b0+i) X^i,  EB_single;
  packed_ind         : per-bank packed recursion D_k*fld + sum (D_k c/D_j) Q_j = Q_k  =>  D_k * E(dRec k) = Q_k;
  bound_ind          : integer multipliers + l-infinity bound recursion => D_k * dRec k g is an integer of size <= beta_k;
  filter_slice       : monotone start table => List.filter by owner = a contiguous List.range' slice.
Kernel only (no sorry / native_decide / new axioms).
-/
import Nov15.BankTieD
import Nov15.Bridge7761PBT
import Mathlib.Tactic.FieldSimp

namespace BridgeP
open Finset BankNC0

theorem digits_zero (X : ℤ) (hX : 0 < X) : ∀ (n : ℕ) (v : ℕ → ℤ), (∀ i < n, |v i| < X) →
    ∑ i ∈ range n, v i * X ^ i = 0 → ∀ i < n, v i = 0 := by
  intro n
  induction n with
  | zero => intro v _ _ i hi; omega
  | succ n ih =>
    intro v hv hs
    rw [Finset.sum_range_succ'] at hs
    have h1 : ∑ i ∈ range n, v (i+1) * X ^ (i+1) = X * ∑ i ∈ range n, v (i+1) * X ^ i := by
      rw [Finset.mul_sum]; exact Finset.sum_congr rfl fun i _ => by ring
    rw [h1, pow_zero, mul_one] at hs
    have h0 : v 0 = 0 := by
      have hv0 := hv 0 (by omega)
      have hc : v 0 = X * (-(∑ i ∈ range n, v (i+1) * X ^ i)) := by linarith
      set c := -(∑ i ∈ range n, v (i+1) * X ^ i)
      rw [hc, abs_lt] at hv0
      rcases lt_trichotomy c 0 with h | h | h
      · exfalso; nlinarith [hv0.1]
      · rw [hc, h, mul_zero]
      · exfalso; nlinarith [hv0.2]
    rw [h0, add_zero] at hs
    have hs' : ∑ i ∈ range n, v (i+1) * X ^ i = 0 := by
      rcases mul_eq_zero.1 hs with h | h
      · exact absurd h hX.ne'
      · exact h
    intro i hi
    cases i with
    | zero => exact h0
    | succ i => exact ih (fun i => v (i+1)) (fun i hi => hv (i+1) (by omega)) hs' i (by omega)

/-- block-packing functional: v |-> sum_{i<W} v(b0+i) X^i (slots past m count 0). -/
noncomputable def EB (m b0 W : ℕ) (X : ℚ) : (Fin m → ℚ) →ₗ[ℚ] ℚ where
  toFun v := ∑ i ∈ range W, (if h : b0 + i < m then v ⟨b0 + i, h⟩ else 0) * X ^ i
  map_add' v w := by
    rw [← Finset.sum_add_distrib]
    refine Finset.sum_congr rfl fun i _ => ?_
    split_ifs <;> simp [add_mul]
  map_smul' c v := by
    simp only [RingHom.id_apply, smul_eq_mul]
    rw [Finset.mul_sum]
    refine Finset.sum_congr rfl fun i _ => ?_
    split_ifs <;> simp [mul_assoc]

theorem EB_apply (m b0 W : ℕ) (X : ℚ) (v : Fin m → ℚ) :
    EB m b0 W X v = ∑ i ∈ range W, (if h : b0 + i < m then v ⟨b0 + i, h⟩ else 0) * X ^ i := rfl

theorem EB_single (m b0 W : ℕ) (X : ℚ) (g : Fin m) :
    EB m b0 W X (Pi.single g 1) = if b0 ≤ g.val ∧ g.val < b0 + W then X ^ (g.val - b0) else 0 := by
  rw [EB_apply]
  have key : ∀ i ∈ range W, (if h : b0 + i < m then (Pi.single g (1:ℚ) : Fin m → ℚ) ⟨b0 + i, h⟩ else 0) * X ^ i
      = if b0 + i = g.val then X ^ i else 0 := by
    intro i _
    by_cases h : b0 + i < m
    · rw [dif_pos h]
      by_cases hg : b0 + i = g.val
      · have : (⟨b0 + i, h⟩ : Fin m) = g := Fin.ext hg
        rw [this, Pi.single_eq_same, one_mul, if_pos hg]
      · have : (⟨b0 + i, h⟩ : Fin m) ≠ g := fun e => hg (congrArg Fin.val e)
        rw [Pi.single_eq_of_ne this, zero_mul, if_neg hg]
    · rw [dif_neg h, zero_mul, if_neg]; have := g.isLt; omega
  rw [Finset.sum_congr rfl key]
  by_cases hb : b0 ≤ g.val ∧ g.val < b0 + W
  · rw [if_pos hb, Finset.sum_eq_single (g.val - b0)]
    · rw [if_pos (by omega)]
    · intro i _ hi; rw [if_neg]; omega
    · intro h; exact absurd (Finset.mem_range.2 (by omega)) h
  · rw [if_neg hb]
    exact Finset.sum_eq_zero fun i hi => by
      rw [Finset.mem_range] at hi; rw [if_neg]; omega

theorem lsum_apply {ι α : Type} (l : List ι) (f : ι → α → ℚ) (a : α) :
    (l.map f).sum a = (l.map fun x => f x a).sum := by
  induction l with
  | nil => rfl
  | cons x l ih => simp [List.map_cons, List.sum_cons, Pi.add_apply, ih]

variable {m nb : ℕ}

theorem packed_ind (R : Recipe ℚ (Fin m) (Fin nb)) (E : (Fin m → ℚ) →ₗ[ℚ] ℚ) (D : Fin nb → ℕ) (Q : Fin nb → ℚ)
    (hD : ∀ k, D k ≠ 0)
    (hlt : ∀ k p, p ∈ R.ref k → p.2 < k)
    (hstep : ∀ k, (D k : ℚ) * ((R.fld k).map fun p => p.1 * E (Pi.single p.2 1)).sum +
        ((R.ref k).map fun p => ((D k : ℚ) * p.1 / D p.2) * Q p.2).sum = Q k) :
    ∀ k, (D k : ℚ) * E (dRec R k) = Q k := by
  intro k
  refine WellFoundedLT.induction (motive := fun k => (D k : ℚ) * E (dRec R k) = Q k) k ?_
  intro k ih
  have hF : E ((R.fld k).map fun p => p.1 • (Pi.single p.2 (1:ℚ) : Fin m → ℚ)).sum
      = ((R.fld k).map fun p => p.1 * E (Pi.single p.2 1)).sum := by
    rw [map_list_sum, List.map_map]
    congr 1; apply List.map_congr_left; intro p _; simp [map_smul]
  have hR : (D k : ℚ) * E ((R.ref k).map fun p => if p.2 < k then p.1 • dRec R p.2 else 0).sum
      = ((R.ref k).map fun p => ((D k : ℚ) * p.1 / D p.2) * Q p.2).sum := by
    rw [map_list_sum, List.map_map, ← List.sum_map_mul_left]
    congr 1; apply List.map_congr_left; intro p hp
    have hl := hlt k p hp
    simp only [Function.comp, if_pos hl, map_smul, smul_eq_mul]
    rw [← ih p.2 hl]
    have := hD p.2
    field_simp
  rw [dRec_eq, map_add, mul_add, hF, hR]; exact hstep k

/-- `x` is an integer of absolute value at most `b`. -/
def IB (x : ℚ) (b : ℤ) : Prop := ∃ z : ℤ, x = z ∧ |z| ≤ b

theorem IB_sum {ι : Type} (l : List ι) (f : ι → ℚ) (b : ι → ℤ) (h : ∀ x ∈ l, IB (f x) (b x)) :
    IB (l.map f).sum (l.map b).sum := by
  induction l with
  | nil => exact ⟨0, by simp, by simp⟩
  | cons a l ih =>
    obtain ⟨z, hz, hb⟩ := h a List.mem_cons_self
    obtain ⟨w, hw, hb'⟩ := ih (fun x hx => h x (List.mem_cons_of_mem _ hx))
    refine ⟨z + w, by simp [hz, hw], ?_⟩
    simp only [List.map_cons, List.sum_cons]
    exact (abs_add_le z w).trans (add_le_add hb hb')

theorem IB_mono {x : ℚ} {b b' : ℤ} (h : IB x b) (hb : b ≤ b') : IB x b' :=
  let ⟨z, hz, h⟩ := h; ⟨z, hz, h.trans hb⟩

theorem IB_mul {x : ℚ} {b : ℤ} (h : IB x b) (c : ℤ) : IB (c * x) (|c| * b) := by
  obtain ⟨z, hz, h⟩ := h
  exact ⟨c * z, by simp [hz], by rw [abs_mul]; exact mul_le_mul_of_nonneg_left h (abs_nonneg c)⟩

theorem bound_ind (R : Recipe ℚ (Fin m) (Fin nb)) (D : Fin nb → ℕ) (β : Fin nb → ℤ) (hD : ∀ k, D k ≠ 0)
    (hlt : ∀ k p, p ∈ R.ref k → p.2 < k)
    (mf : Fin nb → ℚ × Fin m → ℤ) (mr : Fin nb → ℚ × Fin nb → ℤ)
    (hmf : ∀ k p, p ∈ R.fld k → (D k : ℚ) * p.1 = mf k p)
    (hmr : ∀ k p, p ∈ R.ref k → (D k : ℚ) * p.1 / D p.2 = mr k p)
    (hβ : ∀ k, ((R.fld k).map fun p => |mf k p|).sum + ((R.ref k).map fun p => |mr k p| * β p.2).sum ≤ β k) :
    ∀ k g, IB ((D k : ℚ) * dRec R k g) (β k) := by
  intro k
  refine WellFoundedLT.induction (motive := fun k => ∀ g, IB ((D k : ℚ) * dRec R k g) (β k)) k ?_
  intro k ih g
  refine IB_mono ?_ (hβ k)
  rw [dRec_eq, Pi.add_apply, lsum_apply, lsum_apply, mul_add, ← List.sum_map_mul_left, ← List.sum_map_mul_left]
  obtain ⟨z1, h1, b1⟩ := IB_sum (R.fld k) _ (fun p => |mf k p|) (fun p hp => by
    show IB ((D k : ℚ) * (p.1 • (Pi.single p.2 (1:ℚ) : Fin m → ℚ)) g) |mf k p|
    rw [Pi.smul_apply, smul_eq_mul, ← mul_assoc, hmf k p hp]
    by_cases hg : g = p.2
    · subst hg; rw [Pi.single_eq_same, mul_one]; exact ⟨mf k p, rfl, le_rfl⟩
    · rw [Pi.single_eq_of_ne hg, mul_zero]; exact ⟨0, by simp, by simp⟩)
  obtain ⟨z2, h2, b2⟩ := IB_sum (R.ref k) _ (fun p => |mr k p| * β p.2) (fun p hp => by
    have hl := hlt k p hp
    show IB ((D k : ℚ) * (if p.2 < k then p.1 • dRec R p.2 else 0) g) (|mr k p| * β p.2)
    rw [if_pos hl, Pi.smul_apply, smul_eq_mul]
    have e : (D k : ℚ) * (p.1 * dRec R p.2 g) = (mr k p : ℚ) * ((D p.2 : ℚ) * dRec R p.2 g) := by
      rw [← hmr k p hp]; have := hD p.2; field_simp
    rw [e]; exact IB_mul (ih p.2 hl g) _)
  exact ⟨z1 + z2, by rw [h1, h2]; push_cast; ring, (abs_add_le _ _).trans (add_le_add b1 b2)⟩

theorem mono_le (S : ℕ → ℕ) (M : ℕ) (h : ∀ i < M, S i ≤ S (i+1)) : ∀ i j, i ≤ j → j ≤ M → S i ≤ S j := by
  intro i j hij hjM
  induction j with
  | zero => have : i = 0 := by omega
            subst this; exact le_rfl
  | succ j ih =>
    rcases Nat.eq_or_lt_of_le hij with h' | h'
    · rw [h']
    · exact (ih (by omega) (by omega)).trans (h j (by omega))

theorem filter_slice (N M : ℕ) (b S : ℕ → ℕ) (hS : ∀ i < M, S i ≤ S (i+1)) (hSM : S M ≤ N)
    (hb : ∀ t < N, b t < M ∧ S (b t) ≤ t ∧ t < S (b t + 1)) (k : ℕ) (hk : k < M) :
    (List.range N).filter (fun t => decide (b t = k)) = List.range' (S k) (S (k+1) - S k) := by
  have hmono := mono_le S M hS
  have h1 : S k ≤ S (k+1) := hS k hk
  have h2 : S (k+1) ≤ N := (hmono (k+1) M (by omega) le_rfl).trans hSM
  have hsplit : List.range N = List.range' 0 (S k) ++ (List.range' (S k) (S (k+1) - S k) ++
      List.range' (S (k+1)) (N - S (k+1))) := by
    have e : N = S k + ((S (k+1) - S k) + (N - S (k+1))) := by omega
    have e2 : S k + (S (k+1) - S k) = S (k+1) := by omega
    conv_lhs => rw [List.range_eq_range', e, ← List.range'_append_1, ← List.range'_append_1]
    simp only [Nat.zero_add, e2]
  rw [hsplit, List.filter_append, List.filter_append]
  have e1 : (List.range' 0 (S k)).filter (fun t => decide (b t = k)) = [] := by
    rw [List.filter_eq_nil_iff]; intro t ht; rw [List.mem_range'_1] at ht
    obtain ⟨_, h3, _⟩ := hb t (by omega)
    simp only [decide_eq_true_eq]; intro e; rw [e] at h3; omega
  have e3 : (List.range' (S (k+1)) (N - S (k+1))).filter (fun t => decide (b t = k)) = [] := by
    rw [List.filter_eq_nil_iff]; intro t ht; rw [List.mem_range'_1] at ht
    obtain ⟨_, _, h4⟩ := hb t (by omega)
    simp only [decide_eq_true_eq]; intro e; rw [e] at h4; omega
  have e2 : (List.range' (S k) (S (k+1) - S k)).filter (fun t => decide (b t = k)) =
      List.range' (S k) (S (k+1) - S k) := by
    rw [List.filter_eq_self]; intro t ht; rw [List.mem_range'_1] at ht
    obtain ⟨hbM, h3, h4⟩ := hb t (by omega)
    simp only [decide_eq_true_eq]
    by_contra hne
    rcases Nat.lt_or_gt_of_ne hne with h | h
    · have := hmono (b t + 1) k (by omega) hk.le; omega
    · have := hmono (k+1) (b t) (by omega) hbM.le; omega
  rw [e1, e2, e3, List.nil_append, List.append_nil]

end BridgeP
#print axioms BridgeP.digits_zero
#print axioms BridgeP.EB_single
#print axioms BridgeP.packed_ind
#print axioms BridgeP.bound_ind
#print axioms BridgeP.filter_slice
