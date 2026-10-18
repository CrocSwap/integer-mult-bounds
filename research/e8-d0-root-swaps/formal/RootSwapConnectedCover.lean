/-
Copyright (c) 2026 conorholds. All rights reserved.
Released under Apache 2.0 license as described in the repository LICENSE.
Prepared with substantial OpenAI Codex assistance.
-/
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Lean.Elab.Tactic.Omega

/-!
# Connected deletion sets cannot have a positive tight cover

This formalizes the coefficient-independent covering step of EXTENSION.md,
Section 1. Supports may overlap arbitrarily. Their weights are actual label-span
ranks. The geometric connectedness inequality is an explicit premise; neither
its E8 certificate nor the root-only conclusion is asserted here.
-/

noncomputable section

open scoped BigOperators
open Submodule

namespace RootSwapConnectedCover

variable {F E J W : Type*} [Field F]
variable [AddCommGroup W] [Module F W] [FiniteDimensional F W]

/-- Rank of the labels on a finite coordinate set. -/
def supportRank (label : E → W) (s : Finset E) : ℕ :=
  Module.finrank F (Submodule.span F (label '' (s : Set E)))

variable (label : E → W)
local notation "rk" => supportRank (F := F) label

private theorem rank_mono {A B : Finset E} (h : A ⊆ B) : rk A ≤ rk B :=
  Submodule.finrank_mono (Submodule.span_mono (Set.image_mono h))

private theorem rank_sup_le (s : Finset J) (P : J → Submodule F W) :
    Module.finrank F (s.sup P : Submodule F W) ≤ ∑ j ∈ s, Module.finrank F (P j) := by
  classical
  induction s using Finset.induction_on with
  | empty => simp
  | @insert j s hj ih =>
    rw [Finset.sup_insert, Finset.sum_insert hj]
    exact (Submodule.finrank_add_le_finrank_add_finrank _ _).trans
      (Nat.add_le_add_left ih _)

/-- Any finite cover bounds rank by the sum of support ranks, even with overlap. -/
theorem cover_rank_le_sum (D : Finset E) (C : J → Finset E) (s : Finset J)
    (cover : ∀ t ∈ D, ∃ j ∈ s, t ∈ C j) : rk D ≤ ∑ j ∈ s, rk (C j) := by
  classical
  let P : J → Submodule F W := fun j => Submodule.span F (label '' (C j : Set E))
  have hspan : Submodule.span F (label '' (D : Set E)) ≤ s.sup P := by
    apply Submodule.span_le.mpr
    rintro _ ⟨t, ht, rfl⟩
    obtain ⟨j, hj, htj⟩ := cover t ht
    have hp : P j ≤ s.sup P := Finset.le_sup hj
    exact hp (Submodule.subset_span ⟨t, htj, rfl⟩)
  exact (Submodule.finrank_mono hspan).trans (rank_sup_le s P)

variable [Fintype J] [DecidableEq E]

/-- A connected rank-r set cannot be covered by two or more positive-weight
supports whose total weight is at most r. `i` and `j` exhibit distinct members.
This uses the given supports directly and never assumes disjointness. -/
theorem connected_cover_impossible (D : Finset E) (C : J → Finset E)
    (i j : J) (hji : j ≠ i)
    (positive : ∀ k, 0 < rk (C k))
    (cover : ∀ t ∈ D, ∃ k, t ∈ C k)
    (connected : ∀ A : Finset E, A ⊆ D → A.Nonempty → (D \ A).Nonempty →
      rk D < rk A + rk (D \ A))
    (budget : (∑ k, rk (C k)) ≤ rk D) : False := by
  classical
  let A := D ∩ C i
  let B := D \ C i
  let w : J → ℕ := fun k => rk (C k)
  have hrest : rk B ≤ ∑ k ∈ Finset.univ.erase i, w k := by
    apply cover_rank_le_sum label B C (Finset.univ.erase i)
    intro t ht
    obtain ⟨k, hk⟩ := cover t (Finset.mem_sdiff.mp ht).1
    refine ⟨k, Finset.mem_erase.mpr ⟨?_, Finset.mem_univ k⟩, hk⟩
    intro hki
    exact (Finset.mem_sdiff.mp ht).2 (hki ▸ hk)
  have hsum : (∑ k ∈ Finset.univ.erase i, w k) + w i = ∑ k, w k :=
    Finset.sum_erase_add Finset.univ w (Finset.mem_univ i)
  have hjmem : j ∈ Finset.univ.erase i := Finset.mem_erase.mpr ⟨hji, Finset.mem_univ j⟩
  have hjbound : w j ≤ ∑ k ∈ Finset.univ.erase i, w k :=
    Finset.single_le_sum (fun _ _ => Nat.zero_le _) hjmem
  have hAi : rk A ≤ w i := rank_mono label Finset.inter_subset_right
  have hi := positive i
  have hj := positive j
  change 0 < w i at hi
  change 0 < w j at hj
  change (∑ k, w k) ≤ rk D at budget
  by_cases hA : A.Nonempty
  · by_cases hB : B.Nonempty
    · have hpart : D \ A = B := Finset.sdiff_inter_self_left D (C i)
      have hc := connected A Finset.inter_subset_left hA (hpart.symm ▸ hB)
      rw [hpart] at hc
      omega
    · have hBempty : B = ∅ := Finset.not_nonempty_iff_eq_empty.mp hB
      have hDC : D ⊆ C i := Finset.sdiff_eq_empty_iff_subset.mp hBempty
      have hd := rank_mono (F := F) label hDC
      change rk D ≤ w i at hd
      omega
  · have hAempty : A = ∅ := Finset.not_nonempty_iff_eq_empty.mp hA
    have hBD : B = D := by
      ext t
      constructor
      · exact fun ht => (Finset.mem_sdiff.mp ht).1
      · intro ht
        apply Finset.mem_sdiff.mpr
        refine ⟨ht, ?_⟩
        intro hti
        have hmem : t ∈ A := Finset.mem_inter.mpr ⟨ht, hti⟩
        simp [hAempty] at hmem
    rw [hBD] at hrest
    omega

#print axioms connected_cover_impossible

end RootSwapConnectedCover
