import IntegerLateDivision

/-! Arbitrary leaf order and gate count. The actual48 outer certificate is fixed;
only the ordinary correctness of the supplied explicit leaf is a hypothesis. -/
namespace PersonalMatrix.IntegerGeneral
open PersonalMatrix.Hybrid PersonalMatrix.IntegerLate
variable {K : Type*} [CommRing K] {b ell : ℕ}

def numerator (l : Leaf K b ell) (A B : Matrix (Fin (4*b)) (Fin (4*b)) K) :
    Matrix (Fin (4*b)) (Fin (4*b)) K :=
  PersonalMatrix.Ordinal.fromFull (hybridEval (scaledScheme (K := K)) l
    (PersonalMatrix.Ordinal.toFull (a := 4) (b := b) A)
    (PersonalMatrix.Ordinal.toFull (a := 4) (b := b) B))

theorem numerator_correct (l : Leaf K b ell) (hl : LeafValid l)
    (A B : Matrix (Fin (4*b)) (Fin (4*b)) K) : numerator l A B = (8 : K) • (A*B) := by
  unfold numerator
  rw [hybrid_equals_outer _ _ hl, scaled_all_block_sizes, ← blocks_mul]
  change PersonalMatrix.Ordinal.fromFull ((8 : K) •
    (PersonalMatrix.Ordinal.toFull (a := 4) (b := b) A *
      PersonalMatrix.Ordinal.toFull (a := 4) (b := b) B)) = _
  rw [PersonalMatrix.Ordinal.toFull_mul]
  change (8 : K) • PersonalMatrix.Ordinal.fromFull
    (PersonalMatrix.Ordinal.toFull (a := 4) (b := b) (A*B)) = _
  rw [PersonalMatrix.Ordinal.fromFull_toFull]

def integerAlgorithm (l : Leaf ℤ b ell)
    (A B : Matrix (Fin (4*b)) (Fin (4*b)) ℤ) : Matrix (Fin (4*b)) (Fin (4*b)) ℤ :=
  fun i j => numerator l A B i j / 8

/-- The actual product vector has Fin48×Finell indices. All intermediate values
are integers and only the final output entries are divided by8. -/
theorem integer_correct_and_cost (l : Leaf ℤ b ell) (hl : LeafValid l)
    (A B : Matrix (Fin (4*b)) (Fin (4*b)) ℤ) :
    integerAlgorithm l A B = A*B ∧ scheduledGateCount (scaledScheme (K := ℤ)) l = 48*ell := by
  constructor
  · ext i j
    change numerator l A B i j / 8 = (A*B) i j
    rw [numerator_correct l hl]
    exact Int.mul_ediv_cancel_left _ (by decide)
  · exact hybrid_gate_count _ _

/-- This does not assert existence of a valid W(b)-leaf for everyb. Its validity
is the explicit normal component hypothesis, never the desired hybrid conclusion. -/
theorem integer_W_cost (l : Leaf ℤ b (W b)) (hl : LeafValid l)
    (A B : Matrix (Fin (4*b)) (Fin (4*b)) ℤ) :
    integerAlgorithm l A B = A*B ∧ scheduledGateCount (scaledScheme (K := ℤ)) l = 48*W b :=
  integer_correct_and_cost l hl A B

#print axioms numerator_correct
#print axioms integer_correct_and_cost
#print axioms integer_W_cost
#check @numerator_correct
#check @integer_correct_and_cost
#check @integer_W_cost
end PersonalMatrix.IntegerGeneral
