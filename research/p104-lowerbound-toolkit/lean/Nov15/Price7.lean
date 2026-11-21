/- PRICE7: the PRICE7 reduction on top of Nov15.PriceLemma (the earlier standalone version embedded PriceLemma verbatim;
   here the embedded copy is replaced by the import so that both modules can be loaded together). -/
import Nov15.PriceLemma
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Algebra.Order.BigOperators.Group.Finset
open Matrix Module Submodule

namespace PriceLemma

variable {K : Type*} [Field K] {n : ℕ}

/-! ### PRICE7 reduction (P7.md item 2). -/
section Price7
variable {ιD ιS : Type*} [Fintype ιD] [Fintype ιS]

/-- rank Q[D,S] ≥ dim span lD + dim span lS - n. -/
lemma rank_ge (lD : ιD → Fin n → K) (lS : ιS → Fin n → K) :
    finrank K (span K (Set.range lD)) + finrank K (span K (Set.range lS)) ≤ (gram lD lS).rank + n := by
  rw [rank_gram_D]
  have h1 : finrank K (span K (Set.range lD) ⊓ perp (span K (Set.range lS)) : Submodule K _) ≤
      finrank K (perp (span K (Set.range lS))) := Submodule.finrank_mono inf_le_right
  rw [finrank_perp] at h1
  have := finrank_le_n (span K (Set.range lS))
  have h2 : finrank K (span K (Set.range lD) ⊓ perp (span K (Set.range lS)) : Submodule K _) ≤
      finrank K (span K (Set.range lD)) := Submodule.finrank_mono inf_le_left
  omega

/-- pure arithmetic: ≥ 8 rows, total ≤ 55 ⇒ some row ≤ 6. -/
lemma price7_core {κ : Type*} [Fintype κ] (hκ : 8 ≤ Fintype.card κ) (p : κ → ℕ)
    (hs : ∑ k, p k ≤ 55) : ∃ k, p k ≤ 6 := by
  by_contra h
  push_neg at h
  have h7 : ∀ k ∈ (Finset.univ : Finset κ), 7 ≤ p k := fun k _ => h k
  have := Finset.card_nsmul_le_sum Finset.univ p 7 h7
  rw [Finset.card_univ, smul_eq_mul] at this
  have hs' : Finset.univ.sum p ≤ 55 := hs
  omega

/-- PRICE7, wired to PriceLemma.exact_price: rows k with label families lD k, lS k, price = rank of
the Gram matrix.  If there are ≥ 8 rows and the total price is ≤ 55, some row has price ≤ 6, hence a
feasible pair (M,L) of the exact price lemma with dim M - dim L ≤ 6. -/
theorem price7 {κ : Type*} [Fintype κ] (hκ : 8 ≤ Fintype.card κ)
    (lD : κ → ιD → Fin n → K) (lS : κ → ιS → Fin n → K)
    (hs : ∑ k, (gram (lD k) (lS k)).rank ≤ 55) :
    ∃ k, (gram (lD k) (lS k)).rank ≤ 6 ∧
      ∃ M L : Submodule K (Fin n → K), span K (Set.range (lD k)) ≤ M ∧ L ≤ M ∧
        L ≤ perp (span K (Set.range (lS k))) ∧ finrank K M - finrank K L ≤ 6 := by
  obtain ⟨k, hk⟩ := price7_core hκ _ hs
  obtain ⟨M, L, h1, h2, h3, h4⟩ := (exact_price (lD k) (lS k)).1
  exact ⟨k, hk, M, L, h1, h2, h3, by omega⟩

/-- PRICE7 with the 7-dim-side consequence (n = 9, both spans ≥ 7 by the 8-row frame law):
some row has price ≤ 6 and a span of dimension exactly 7. -/
theorem price7_sevendim {κ : Type*} [Fintype κ] (hκ : 8 ≤ Fintype.card κ)
    (lD : κ → ιD → Fin 9 → K) (lS : κ → ιS → Fin 9 → K)
    (h7 : ∀ k, 7 ≤ finrank K (span K (Set.range (lD k))) ∧ 7 ≤ finrank K (span K (Set.range (lS k))))
    (hs : ∑ k, (gram (lD k) (lS k)).rank ≤ 55) :
    ∃ k, (gram (lD k) (lS k)).rank ≤ 6 ∧
      (finrank K (span K (Set.range (lD k))) = 7 ∨ finrank K (span K (Set.range (lS k))) = 7) := by
  obtain ⟨k, hk⟩ := price7_core hκ _ hs
  have := rank_ge (lD k) (lS k)
  have := h7 k
  exact ⟨k, hk, by omega⟩

/-! non-vacuity of the arithmetic core: 8 rows of price 5 (total 40 ≤ 55) has a row ≤ 6,
and 8 rows of price 7 (total 56) is the boundary that violates the hypothesis. -/
example : ∃ k : Fin 8, (fun _ : Fin 8 => 5) k ≤ 6 := price7_core (by simp) _ (by simp)
example : ¬ (∑ k : Fin 8, (fun _ : Fin 8 => 7) k ≤ 55) := by simp

end Price7

#print axioms price7
#print axioms price7_sevendim

end PriceLemma
