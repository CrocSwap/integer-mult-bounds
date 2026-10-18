import DecoderDuality

/-!
# General decoder rank-to-cost interface

This is the non-diagonal interface requested in PR2162's handoff. The rank-sum,
support-restriction and field-map helpers are DreamingOfClouds's unchanged
`DecoderDuality` source at 113a718265c62aec301c5695f4bfb9c421bef7ab.
No new mathematical rank principle is claimed.

Gareth Davidson, with substantial OpenAI Codex assistance. Apache-2.0.
-/

open Matrix

namespace DecoderRankBound

section General

variable {F K I J T : Type*} [Field F] [Field K]
  [Fintype I] [Fintype J] [Fintype T] [DecidableEq I] [DecidableEq J]

/-- The paid block-rank sum is measured over the original field `F`. -/
noncomputable def cost (B : Matrix I J F) (S : T → Finset I) (U : T → Finset J) : ℕ :=
  ∑ t, (B.submatrix ((↑) : S t → I) ((↑) : U t → J)).rank

/-- A rectangular weighted decoder matrix over an extension field. -/
noncomputable def weighted (f : F →+* K) (B : Matrix I J F)
    (p : T → I → K) (q : T → J → K) : Matrix I J K :=
  ∑ t, diagonal (p t) * B.map f * diagonal (q t)

/-- Entrywise form used by generic-rank and jet arguments. -/
def hadamard (f : F →+* K) (B : Matrix I J F)
    (p : T → I → K) (q : T → J → K) : Matrix I J K :=
  fun i j => f (B i j) * ∑ t, p t i * q t j

/-- The full weighted sum obeys the block cost bound, without assumptions
on its diagonal, invertibility or off-diagonal entries. -/
theorem rank_weighted_le_cost (f : F →+* K) (B : Matrix I J F)
    (p : T → I → K) (q : T → J → K) (S : T → Finset I) (U : T → Finset J)
    (hp : ∀ t i, p t i ≠ 0 → i ∈ S t) (hq : ∀ t j, q t j ≠ 0 → j ∈ U t) :
    (weighted f B p q).rank ≤ cost B S U := by
  classical
  calc
    (weighted f B p q).rank ≤ ∑ t, (diagonal (p t) * B.map f * diagonal (q t)).rank :=
      DecoderDuality.rank_sum_le _ _
    _ ≤ cost B S U := by
      apply Finset.sum_le_sum
      intro t _
      exact (DecoderDuality.rank_diag_mul_mul_diag_le (B.map f) (p t) (q t)
        (S t) (U t) (hp t) (hq t)).trans
        (DecoderDuality.rank_map_le f (B.submatrix ((↑) : S t → I) ((↑) : U t → J)))

theorem weighted_eq_hadamard (f : F →+* K) (B : Matrix I J F)
    (p : T → I → K) (q : T → J → K) : weighted f B p q = hadamard f B p q := by
  classical
  ext i j
  simp only [weighted, hadamard, Matrix.sum_apply, mul_diagonal, diagonal_mul, map_apply]
  rw [Finset.mul_sum]
  exact Finset.sum_congr rfl fun t _ => by ring

/-- Lemma GR's rank upper bound over any field extension, with the base-field
cost retained. The proof does not require a diagonal Hadamard product. -/
theorem rank_hadamard_le_cost (f : F →+* K) (B : Matrix I J F)
    (p : T → I → K) (q : T → J → K) (S : T → Finset I) (U : T → Finset J)
    (hp : ∀ t i, p t i ≠ 0 → i ∈ S t) (hq : ∀ t j, q t j ≠ 0 → j ∈ U t) :
    (hadamard f B p q).rank ≤ cost B S U := by
  rw [← weighted_eq_hadamard]
  exact rank_weighted_le_cost f B p q S U hp hq

/-- A nonzero selected square minor over `K` certifies a lower bound on the
original `F` block cost. No injectivity assumptions on the selectors are
needed: the nonzero determinant already rules out repeated rows or columns. -/
theorem minor_le_cost {D : Type*} [Fintype D] [DecidableEq D]
    (f : F →+* K) (B : Matrix I J F) (p : T → I → K) (q : T → J → K)
    (S : T → Finset I) (U : T → Finset J)
    (hp : ∀ t i, p t i ≠ 0 → i ∈ S t) (hq : ∀ t j, q t j ≠ 0 → j ∈ U t)
    (rows : D → I) (cols : D → J)
    (hdet : ((hadamard f B p q).submatrix rows cols).det ≠ 0) :
    Fintype.card D ≤ cost B S U := by
  have hrank := Matrix.rank_of_isUnit ((hadamard f B p q).submatrix rows cols)
    ((Matrix.isUnit_iff_isUnit_det _).mpr (isUnit_iff_ne_zero.mpr hdet))
  calc
    Fintype.card D = ((hadamard f B p q).submatrix rows cols).rank := hrank.symm
    _ ≤ (hadamard f B p q).rank := Matrix.rank_submatrix_le _ _ _
    _ ≤ cost B S U := rank_hadamard_le_cost f B p q S U hp hq

end General

/-- Characteristic-two specialization with exactly the original binary block
ranks on the right. No admissibility or unit-diagonal condition on `B` is
needed for this rank upper bound. Such conditions belong to later witnesses. -/
theorem charTwo_rank_le_cost {K I J T : Type*} [Field K] [CharP K 2]
    [Fintype I] [Fintype J] [Fintype T] [DecidableEq I] [DecidableEq J]
    (B : Matrix I J (ZMod 2)) (p : T → I → K) (q : T → J → K)
    (S : T → Finset I) (U : T → Finset J)
    (hp : ∀ t i, p t i ≠ 0 → i ∈ S t) (hq : ∀ t j, q t j ≠ 0 → j ∈ U t) :
    (hadamard (ZMod.castHom (dvd_refl 2) K) B p q).rank ≤ cost B S U :=
  rank_hadamard_le_cost _ B p q S U hp hq

end DecoderRankBound

#print axioms DecoderRankBound.rank_weighted_le_cost
#print axioms DecoderRankBound.weighted_eq_hadamard
#print axioms DecoderRankBound.rank_hadamard_le_cost
#print axioms DecoderRankBound.minor_le_cost
#print axioms DecoderRankBound.charTwo_rank_le_cost
