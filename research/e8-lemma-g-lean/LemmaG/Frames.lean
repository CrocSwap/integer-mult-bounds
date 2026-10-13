/-
Lemma G, the frame instance: subspaces of F₂⁹ under inclusion, ranked by dimension, satisfy
the order hypotheses of `LemmaG.Schedule`.
Apache-2.0.  Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
-/
import LemmaG.Schedule
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.Algebra.Field.ZMod

namespace LemmaG

/-- Over any division ring, dimension is strictly monotone on the subspaces of a
finite-dimensional space. -/
theorem rank_strictMono {K V : Type*} [DivisionRing K] [AddCommGroup V] [Module K V]
    [FiniteDimensional K V] : StrictMono (fun E : Submodule K V => Module.finrank K E) :=
  Submodule.finrank_strictMono

instance fact_prime_two' : Fact (Nat.Prime 2) := ⟨Nat.prime_two⟩

/-- A frame of the word: a subspace of `F₂⁹`. -/
abbrev Frame := Submodule (ZMod 2) (Fin 9 → ZMod 2)

/-- The rank of a frame is its dimension. -/
noncomputable def frameRank (E : Frame) : ℕ := Module.finrank (ZMod 2) E

/-- Dimension is strictly monotone for inclusion. -/
theorem frameRank_strictMono : StrictMono frameRank :=
  rank_strictMono (K := ZMod 2) (V := Fin 9 → ZMod 2)

/-- The compensation segment on the frames of the word (`comp_segment` with `Λ = Frame`,
`rk = dim`).  Targets start at the zero frame `⊥`, which lies below every entrance. -/
theorem comp_segment_frames {ι K : Type*} [DecidableEq ι] [DecidableEq Frame]
    (its : List (Item ι Frame K)) (l : ι → Frame)
    (hdisj : ∀ a ∈ its, ∀ b ∈ its, b.mv ≠ a.pt)
    (hentr : ∀ a ∈ its, l a.pt = a.F)
    (hzero : ∀ a ∈ its, l a.mv = ⊥)
    (hchain : ∀ a ∈ its, ∀ b ∈ its, a.mv = b.mv → a.F ≤ b.F ∨ b.F ≤ a.F)
    (hsorted : its.Pairwise (fun a b => frameRank a.F ≤ frameRank b.F)) :
    Stream.WellLabelled (emit l its) l ∧
      (∀ r A B, Event.relabel r A B ∈ emit l its → A < B) ∧
      (∀ a ∈ its, a.F ≤ Stream.labRun (emit l its) l a.mv ∧
        ∃ b ∈ its, b.mv = a.mv ∧ Stream.labRun (emit l its) l a.mv = b.F) ∧
      (∀ m, (∀ a ∈ its, a.mv ≠ m) → Stream.labRun (emit l its) l m = l m) :=
  comp_segment frameRank frameRank_strictMono its l hdisj hentr
    (fun a ha => by rw [hzero a ha]; exact bot_le) hchain hsorted

end LemmaG
