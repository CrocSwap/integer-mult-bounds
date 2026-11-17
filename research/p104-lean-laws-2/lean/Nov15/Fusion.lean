/-
Fusion (lane LEAN-NEXT24, Nov 17): the fusion rank obstruction. See Fusion.md.
Source: cards/WILD/CANCELBUS/R2.md §2. Plain linear algebra over a field K (ZMod p is the mod-prime census).

`R` = span of the rows of Rest (co-present registers other than A, B); A, B ∈ V = row space.
`gain R S` := finrank (R ⊔ S) − finrank R is the number of NEW independent directions S adds.
* `span_carriers_le`: m carrier vectors add at most m directions to R.
* `gain_carriers`: if A_1..A_k are all contained in R ⊔ span(carriers) then k-gain ≤ #carriers.
* `fusion_obstruction`: finrank (R ⊔ span{A,B}) = finrank R + 2 ⇒ no single vector x has both
  A ∈ R ⊔ span{x} and B ∈ R ⊔ span{x}; i.e. no one register (Rest unchanged) can hold both contents.
* `fusion_obstruction_regs`: same in the "carrier register replaces A and B" form: any single x with
  span(R ∪ {A,B}) ≤ span(R ∪ {x}) is impossible; with two carriers it is possible (`two_carriers`).
-/
import Mathlib.LinearAlgebra.FiniteDimensional.Defs
import Mathlib.LinearAlgebra.Dimension.Finite
import Mathlib.LinearAlgebra.Dimension.Constructions
import Mathlib.LinearAlgebra.Dimension.FreeAndStrongRankCondition
import Mathlib.LinearAlgebra.Dimension.RankNullity
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas

set_option linter.unusedSectionVars false

namespace Fusion
open Module Submodule

variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V] [FiniteDimensional K V]

/-- adjoining the span of a finite set of m carriers raises rank by at most m. -/
theorem span_carriers_le (R : Submodule K V) (s : Finset V) :
    finrank K ↥(R ⊔ span K (s : Set V)) ≤ finrank K R + s.card := by
  have h1 := finrank_sup_add_finrank_inf_eq R (span K (s : Set V))
  have h2 : finrank K ↥(span K (s : Set V)) ≤ s.card := finrank_span_finset_le_card (R := K) s
  omega

/-- if S ≤ R ⊔ span(carriers) then the gain of S over R is at most the number of carriers. -/
theorem gain_carriers (R S : Submodule K V) (s : Finset V) (hS : S ≤ R ⊔ span K (s : Set V)) :
    finrank K ↥(R ⊔ S) ≤ finrank K R + s.card := by
  have h : R ⊔ S ≤ R ⊔ span K (s : Set V) := sup_le le_sup_left hS
  exact (Submodule.finrank_mono h).trans (span_carriers_le R s)

/-- **fusion rank obstruction**: gain 2 of A,B over Rest ⇒ no single carrier x holds both. -/
theorem fusion_obstruction (R : Submodule K V) (A B : V)
    (hgain : finrank K ↥(R ⊔ span K {A, B}) = finrank K R + 2) :
    ¬ ∃ x : V, A ∈ R ⊔ span K {x} ∧ B ∈ R ⊔ span K {x} := by
  rintro ⟨x, hA, hB⟩
  have hS : span K {A, B} ≤ R ⊔ span K (({x} : Finset V) : Set V) := by
    rw [span_le]
    intro v hv
    rcases hv with rfl | hv
    · simpa using hA
    · rw [Set.mem_singleton_iff.1 hv]; simpa using hB
  have := gain_carriers R _ {x} hS
  simp at this
  omega

/-- carrier-register form: with Rest unchanged, a single x cannot span everything R, A, B span. -/
theorem fusion_obstruction_regs (R : Submodule K V) (A B : V)
    (hgain : finrank K ↥(R ⊔ span K {A, B}) = finrank K R + 2) (x : V) :
    ¬ (R ⊔ span K {A, B} ≤ R ⊔ span K {x}) := by
  intro h
  apply fusion_obstruction R A B hgain
  have hA : A ∈ R ⊔ span K {A, B} := Submodule.mem_sup_right (subset_span (by simp))
  have hB : B ∈ R ⊔ span K {A, B} := Submodule.mem_sup_right (subset_span (by simp))
  exact ⟨x, h hA, h hB⟩

/-- sharpness: two carriers (x = A, y = B) always suffice. -/
theorem two_carriers (R : Submodule K V) (A B : V) :
    R ⊔ span K {A, B} ≤ R ⊔ span K {A} ⊔ span K {B} := by
  refine sup_le ?_ ?_
  · exact le_trans le_sup_left le_sup_left
  · rw [span_le]
    intro v hv
    rcases hv with rfl | hv
    · exact Submodule.mem_sup_left (Submodule.mem_sup_right (subset_span rfl))
    · rw [Set.mem_singleton_iff.1 hv]; exact Submodule.mem_sup_right (subset_span rfl)

end Fusion
