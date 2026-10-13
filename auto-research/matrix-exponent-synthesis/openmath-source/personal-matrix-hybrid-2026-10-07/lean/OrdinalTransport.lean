import BlockComposition
import Mathlib.Logic.Equiv.Fin.Basic

namespace PersonalMatrix.Ordinal
open PersonalMatrix.Hybrid
variable {K : Type*} [CommRing K] {a b r : ℕ}

def toFull (A : Matrix (Fin (a*b)) (Fin (a*b)) K) : Full (K := K) a b :=
  A.submatrix finProdFinEquiv finProdFinEquiv

def fromFull (A : Full (K := K) a b) : Matrix (Fin (a*b)) (Fin (a*b)) K :=
  A.submatrix finProdFinEquiv.symm finProdFinEquiv.symm

@[simp] theorem fromFull_toFull (A : Matrix (Fin (a*b)) (Fin (a*b)) K) :
    fromFull (toFull A) = A := by
  ext i j
  change A (finProdFinEquiv (finProdFinEquiv.symm i))
    (finProdFinEquiv (finProdFinEquiv.symm j)) = A i j
  rw [Equiv.apply_symm_apply, Equiv.apply_symm_apply]

theorem toFull_mul (A B : Matrix (Fin (a*b)) (Fin (a*b)) K) :
    toFull A * toFull B = toFull (A*B) :=
  Matrix.submatrix_mul_equiv A B finProdFinEquiv finProdFinEquiv finProdFinEquiv

def hybrid (o : Outer K a r) (l : Leaf K b (W b))
    (A B : Matrix (Fin (a*b)) (Fin (a*b)) K) : Matrix (Fin (a*b)) (Fin (a*b)) K :=
  fromFull (hybridEval o l (toFull A) (toFull B))

theorem sound_and_W_cost (o : Outer K a r) (l : Leaf K b (W b))
    (ho : BlockStable o b) (hl : LeafValid l)
    (A B : Matrix (Fin (a*b)) (Fin (a*b)) K) :
    hybrid o l A B = A*B ∧ scheduledGateCount o l = r*W b := by
  constructor
  · unfold hybrid
    rw [hybrid_sound o l ho hl, toFull_mul, fromFull_toFull]
  · exact hybrid_gate_count o l

#print axioms toFull_mul
#print axioms sound_and_W_cost
#check @sound_and_W_cost
end PersonalMatrix.Ordinal
