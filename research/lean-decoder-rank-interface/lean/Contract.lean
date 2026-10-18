import DecoderRankBound

/-!
Explicit type contracts: conclusions expand the matrix and cost definitions.
There are no output-diagonal, invertibility, cardinality-positivity, or
selector-injectivity hypotheses hidden in these applications.
Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
-/

open Matrix DecoderRankBound

namespace DecoderRankContract

variable {F K I J T : Type*} [Field F] [Field K]
  [Fintype I] [Fintype J] [Fintype T] [DecidableEq I] [DecidableEq J]

theorem weighted_signature (f : F →+* K) (B : Matrix I J F)
    (p : T → I → K) (q : T → J → K) (S : T → Finset I) (U : T → Finset J)
    (hp : ∀ t i, p t i ≠ 0 → i ∈ S t) (hq : ∀ t j, q t j ≠ 0 → j ∈ U t) :
    (∑ t, diagonal (p t) * B.map f * diagonal (q t)).rank ≤
      ∑ t, (B.submatrix ((↑) : S t → I) ((↑) : U t → J)).rank :=
  rank_weighted_le_cost f B p q S U hp hq

theorem hadamard_signature (f : F →+* K) (B : Matrix I J F)
    (p : T → I → K) (q : T → J → K) (S : T → Finset I) (U : T → Finset J)
    (hp : ∀ t i, p t i ≠ 0 → i ∈ S t) (hq : ∀ t j, q t j ≠ 0 → j ∈ U t) :
    (Matrix.of fun i j => f (B i j) * ∑ t, p t i * q t j).rank ≤
      ∑ t, (B.submatrix ((↑) : S t → I) ((↑) : U t → J)).rank :=
  rank_hadamard_le_cost f B p q S U hp hq

theorem minor_signature {D : Type*} [Fintype D] [DecidableEq D]
    (f : F →+* K) (B : Matrix I J F) (p : T → I → K) (q : T → J → K)
    (S : T → Finset I) (U : T → Finset J)
    (hp : ∀ t i, p t i ≠ 0 → i ∈ S t) (hq : ∀ t j, q t j ≠ 0 → j ∈ U t)
    (rows : D → I) (cols : D → J)
    (hdet : ((Matrix.of fun i j => f (B i j) * ∑ t, p t i * q t j).submatrix
      rows cols).det ≠ 0) :
    Fintype.card D ≤ ∑ t, (B.submatrix ((↑) : S t → I) ((↑) : U t → J)).rank :=
  minor_le_cost f B p q S U hp hq rows cols hdet

end DecoderRankContract

#print axioms DecoderRankContract.weighted_signature
#print axioms DecoderRankContract.hadamard_signature
#print axioms DecoderRankContract.minor_signature
