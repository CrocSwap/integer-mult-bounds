/-
Copyright (c) 2026 conorholds. All rights reserved.
Released under Apache 2.0 license as described in the repository LICENSE.
Prepared with substantial OpenAI Codex assistance.
-/
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas

/-!
# Two quartet supports and one singleton

This is the coefficient argument for the low-overlap `(3,3,1)` profile in
Section 3 of `e8-d0-root-swaps/PROOF.md`. The identification of exceptional
weight-three supports as orthogonal quartets is not formalized here. Given
that geometry, the theorem proves that only the singleton coordinate can
be swap-eligible. Witnesses retain their actual three scalar coefficients.
-/

noncomputable section

namespace RootSwapQuartet

attribute [local instance] Classical.propDecidable

variable {K E : Type*} [Field K] [DecidableEq E]

/-- Four points cannot all be covered by the own coordinate, the singleton,
and an intersection containing at most one point. -/
theorem exists_private_coordinate (A B : Finset E)
    (hA : 4 ≤ A.card) (hAB : (A ∩ B).card ≤ 1) (t u : E) :
    ∃ s ∈ A, s ≠ t ∧ s ≠ u ∧ s ∉ B := by
  by_contra h
  have hsub : A ⊆ insert t (insert u (A ∩ B)) := by
    intro s hs
    by_cases hst : s = t
    · exact Finset.mem_insert.mpr (Or.inl hst)
    by_cases hsu : s = u
    · exact Finset.mem_insert_of_mem (Finset.mem_insert.mpr (Or.inl hsu))
    have hsB : s ∈ B := by
      by_contra hn
      exact h ⟨s, hs, hst, hsu, hn⟩
    exact Finset.mem_insert_of_mem (Finset.mem_insert_of_mem (Finset.mem_inter.mpr ⟨hs, hsB⟩))
  have hbound : (insert t (insert u (A ∩ B))).card ≤ 3 := by
    calc
      _ ≤ (insert u (A ∩ B)).card + 1 := Finset.card_insert_le _ _
      _ ≤ ((A ∩ B).card + 1) + 1 :=
        Nat.add_le_add_right (Finset.card_insert_le _ _) _
      _ ≤ (1 + 1) + 1 := Nat.add_le_add_right (Nat.add_le_add_right hAB _) _
      _ = 3 := rfl
  exact (by decide : ¬ 4 ≤ 3) (hA.trans ((Finset.card_le_card hsub).trans hbound))

/-- An actual member of the span of two words and one coordinate unit. -/
def combination (qA qB : E → K) (u : E) (a b c : K) (s : E) : K :=
  a * qA s + b * qB s + if s = u then c else 0

/-- Swap eligibility in that actual three-generator scalar span. -/
def Eligible (orthogonal : E → E → Prop) (qA qB : E → K)
    (u t : E) : Prop :=
  ∃ a b c : K, combination qA qB u a b c t ≠ 0 ∧
    ∀ s, s ≠ t → orthogonal s t → combination qA qB u a b c s = 0

/-- With two orthogonal supports of size at least four, overlap at most one,
and one singleton, every swap-eligible coordinate is the singleton.
No support-union relaxation of the coefficient space is used. -/
theorem eligible_eq_singleton
    (orthogonal : E → E → Prop) (A B : Finset E) (qA qB : E → K)
    (u : E) (hA : 4 ≤ A.card) (hB : 4 ≤ B.card)
    (hAB : (A ∩ B).card ≤ 1)
    (supportA : ∀ s, qA s ≠ 0 ↔ s ∈ A)
    (supportB : ∀ s, qB s ≠ 0 ↔ s ∈ B)
    (orthA : ∀ s ∈ A, ∀ t ∈ A, s ≠ t → orthogonal s t)
    (orthB : ∀ s ∈ B, ∀ t ∈ B, s ≠ t → orthogonal s t)
    (t : E) (ht : Eligible orthogonal qA qB u t) : t = u := by
  by_contra htu
  obtain ⟨a, b, c, hown, hzero⟩ := ht
  have ha : a * qA t = 0 := by
    by_cases htA : t ∈ A
    · obtain ⟨s, hsA, hst, hsu, hsB⟩ := exists_private_coordinate A B hA hAB t u
      have hsqa : qA s ≠ 0 := (supportA s).mpr hsA
      have hsqb : qB s = 0 := by
        by_contra hn
        exact hsB ((supportB s).mp hn)
      have hz : a * qA s = 0 := by
        simpa [combination, hsqb, hsu] using hzero s hst (orthA s hsA t htA hst)
      have hazero : a = 0 := (mul_eq_zero.mp hz).resolve_right hsqa
      simp [hazero]
    · have hqt : qA t = 0 := by
        by_contra hn
        exact htA ((supportA t).mp hn)
      simp [hqt]
  have hb : b * qB t = 0 := by
    by_cases htB : t ∈ B
    · have hBA : (B ∩ A).card ≤ 1 := by simpa [Finset.inter_comm] using hAB
      obtain ⟨s, hsB, hst, hsu, hsA⟩ := exists_private_coordinate B A hB hBA t u
      have hsqb : qB s ≠ 0 := (supportB s).mpr hsB
      have hsqa : qA s = 0 := by
        by_contra hn
        exact hsA ((supportA s).mp hn)
      have hz : b * qB s = 0 := by
        simpa [combination, hsqa, hsu] using hzero s hst (orthB s hsB t htB hst)
      have hbzero : b = 0 := (mul_eq_zero.mp hz).resolve_right hsqb
      simp [hbzero]
    · have hqt : qB t = 0 := by
        by_contra hn
        exact htB ((supportB t).mp hn)
      simp [hqt]
  exact hown (by simp [combination, ha, hb, htu])

#print axioms eligible_eq_singleton

end RootSwapQuartet
