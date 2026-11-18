import Mathlib.Order.Basic
import Mathlib.Data.Finset.Card
import Mathlib.Data.Finset.Union
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.IntervalCases
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Data.Finset.Lattice.Fold
import Mathlib.Order.Interval.Finset.Nat
import Mathlib.Algebra.Order.BigOperators.Group.Finset

/-! PATH-CUT: the abstract core of internal notes section 3 (with AUD2 FIX A).
Charts form a preorder `alpha` (`C <= C'` = ascent).  `Hold C` stands for "u_s lies in the chart C" and is preserved by ascent.  A path is a sequence of charts
`c 0 .. c n`; every PUBLIC edge ascends; every OWNED edge is NESTED (comparable ends: rise or descent) -- FIX A.
Conclusion: either the path is legal (every chart holds u_s), or there is a FIRST owned strict descent `c i > c (i+1)` that drops u_s, all earlier charts hold u_s, and c i <= G
(the confinement chart G_t).  Not formalised here: the register-machine facts that produce such a path (SP span law, ADD paths inside D_t = Dn(G_t));
they are the premises of the abstract hypothesis `hcong` of CongestionNative.  `nested_needed` shows the nestedness premise cannot be dropped. -/
namespace PathCut

theorem path_cut {α : Type*} [Preorder α] (c : ℕ → α) (n : ℕ) (Hold : α → Prop) (G : α) (owned : ℕ → Prop)
    (hHold : ∀ C C' : α, C ≤ C' → Hold C → Hold C')
    (hpub : ∀ i < n, ¬ owned i → c i ≤ c (i + 1))
    (hnest : ∀ i < n, owned i → (c i ≤ c (i + 1) ∨ c (i + 1) ≤ c i))
    (hconf : ∀ i ≤ n, c i ≤ G) (hstart : Hold (c 0)) :
    (∀ i ≤ n, Hold (c i)) ∨
      ∃ i < n, owned i ∧ Hold (c i) ∧ ¬ Hold (c (i + 1)) ∧ c (i + 1) < c i ∧ c i ≤ G ∧ ∀ j ≤ i, Hold (c j) := by
  classical
  by_cases h : ∀ i ≤ n, Hold (c i)
  · exact Or.inl h
  · right
    push Not at h
    have hex : ∃ j, j ≤ n ∧ ¬ Hold (c j) := h
    obtain ⟨j, hj, hmin⟩ : ∃ j, (j ≤ n ∧ ¬ Hold (c j)) ∧ ∀ k < j, ¬ (k ≤ n ∧ ¬ Hold (c k)) :=
      ⟨Nat.find hex, Nat.find_spec hex, fun k hk => Nat.find_min hex hk⟩
    have hj0 : j ≠ 0 := by
      intro h0; apply hj.2; rw [h0]; exact hstart
    obtain ⟨i, hi⟩ : ∃ i, j = i + 1 := Nat.exists_eq_succ_of_ne_zero hj0
    have hin : i < n := by have := hj.1; omega
    have hHi : Hold (c i) := by
      by_contra hc; exact hmin i (by omega) ⟨by omega, hc⟩
    have hall : ∀ k ≤ i, Hold (c k) := fun k hk => by
      by_contra hc; exact hmin k (by omega) ⟨by omega, hc⟩
    have hnot : ¬ Hold (c (i + 1)) := by have := hj.2; rwa [hi] at this
    have hnasc : ¬ c i ≤ c (i + 1) := fun hle => hnot (hHold _ _ hle hHi)
    have howned : owned i := by
      by_contra ho; exact hnasc (hpub i hin ho)
    have hle : c (i + 1) ≤ c i := (hnest i hin howned).resolve_left hnasc
    exact ⟨i, hin, howned, hHi, hnot, lt_of_le_not_ge hle hnasc, hconf i hin.le, hall⟩

/-- without nestedness the cut is not a descent: a LATERAL owned move can drop `u_s` (AUD2 FIX A). -/
theorem nested_needed : ∃ (c : ℕ → Finset ℕ) (Hold : Finset ℕ → Prop) (G : Finset ℕ) (owned : ℕ → Prop),
    (∀ C C' : Finset ℕ, C ≤ C' → Hold C → Hold C') ∧ (∀ i < 1, ¬ owned i → c i ≤ c (i + 1)) ∧
    (∀ i ≤ 1, c i ≤ G) ∧ Hold (c 0) ∧
    ¬ ((∀ i ≤ 1, Hold (c i)) ∨
      ∃ i < 1, owned i ∧ Hold (c i) ∧ ¬ Hold (c (i + 1)) ∧ c (i + 1) < c i ∧ c i ≤ G ∧ ∀ j ≤ i, Hold (c j)) := by
  refine ⟨fun i => if i = 0 then {0} else {1}, fun C => 0 ∈ C, {0, 1}, fun _ => True, ?_, ?_, ?_, ?_, ?_⟩
  · intro C C' h h0; exact h h0
  · intro i hi h; exact absurd trivial h
  · intro i hi
    interval_cases i <;> simp [Finset.subset_iff]
  · simp
  · rintro (h | ⟨i, hi, -, -, hn, hlt, -⟩)
    · have := h 1 le_rfl; simp at this
    · have : i = 0 := by omega
      subst this
      simp at hlt

/-- the transported cells of all N_f visits: `|Jt| <= 48 * |V|` when every visit has at most 48 cells (the 48-law) and every transported cell lies in the cells of some visit. -/
theorem transported_card_le {ν : Type*} [DecidableEq ν] (V : Finset ν) (cells : ν → Finset (ℕ × ℕ)) (Jt : Finset (ℕ × ℕ))
    (h48 : ∀ v ∈ V, (cells v).card ≤ 48) (hcut : ∀ p ∈ Jt, ∃ v ∈ V, p ∈ cells v) :
    Jt.card ≤ 48 * V.card := by
  classical
  have hsub : Jt ⊆ V.biUnion cells := by
    intro p hp; obtain ⟨v, hv, hpv⟩ := hcut p hp; exact Finset.mem_biUnion.2 ⟨v, hv, hpv⟩
  calc Jt.card ≤ (V.biUnion cells).card := Finset.card_le_card hsub
    _ ≤ ∑ v ∈ V, (cells v).card := Finset.card_biUnion_le
    _ ≤ ∑ _v ∈ V, 48 := Finset.sum_le_sum h48
    _ = 48 * V.card := by simp [mul_comm]

end PathCut

#print axioms PathCut.path_cut
#print axioms PathCut.nested_needed
#print axioms PathCut.transported_card_le
