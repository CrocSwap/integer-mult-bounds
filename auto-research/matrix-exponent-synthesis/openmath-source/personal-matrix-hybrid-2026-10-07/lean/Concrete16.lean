import Outer48Scheme
import RosowskiLeaf4
import OrdinalTransport
import Mathlib.Tactic.NormNum

namespace PersonalMatrix.Concrete16
open PersonalMatrix.Hybrid
variable {K : Type*} [CommRing K] [Invertible (2 : K)]

def algorithm (A B : Matrix (Fin 16) (Fin 16) K) : Matrix (Fin 16) (Fin 16) K :=
  PersonalMatrix.Ordinal.hybrid (PersonalMatrix.Outer48Scheme.scheme (K := K))
    (PersonalMatrix.Leaf46.leaf (K := K)) A B

/-- Actual coefficient certificate and actual leaf proof close the concrete
instance. Neither outer/leaf validity nor the desired product is a premise. -/
theorem algorithm_correct (A B : Matrix (Fin 16) (Fin 16) K) : algorithm A B = A*B :=
  (PersonalMatrix.Ordinal.sound_and_W_cost _ _
    (PersonalMatrix.Outer48Scheme.all_block_sizes 4) PersonalMatrix.Leaf46.valid A B).1

theorem gate_count : scheduledGateCount (PersonalMatrix.Outer48Scheme.scheme (K := K))
    (PersonalMatrix.Leaf46.leaf (K := K)) = 2208 := by
  rw [hybrid_gate_count]

theorem certified_2208 (A B : Matrix (Fin 16) (Fin 16) K) :
    algorithm A B = A*B ∧
      scheduledGateCount (PersonalMatrix.Outer48Scheme.scheme (K := K))
        (PersonalMatrix.Leaf46.leaf (K := K)) = 2208 :=
  ⟨algorithm_correct A B,gate_count⟩

#print axioms algorithm_correct
#print axioms gate_count
#print axioms certified_2208
#check @certified_2208
end PersonalMatrix.Concrete16
