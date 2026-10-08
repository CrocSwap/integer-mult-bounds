import Outer48Scheme
import RosowskiLeaf4
import OrdinalTransport

/-! The denominator-cleared actual48 outer and the actual46 ring leaf.
All product gates and linear accumulation are integral; eight is divided out
only at the256 integer output entries. No numerator-correctness premise. -/
namespace PersonalMatrix.IntegerLate
open PersonalMatrix.Hybrid PersonalMatrix.Lifting PersonalMatrix.Outer48
open scoped BigOperators
variable {K : Type*} [CommRing K]
set_option maxHeartbeats 2000000
set_option backward.isDefEq.respectTransparency false
set_option backward.isDefEq.respectTransparency.types false

def scaledScheme : Outer K 4 48 where
  left t p := (alphaInteger t (finProdFinEquiv p) : K)
  right t q := (betaInteger t (finProdFinEquiv q) : K)
  output i j t := (gammaNumerator t (finProdFinEquiv (i,j)) : K)

theorem scaled_tensor (i j : Fin 4) (p q : Index 4) :
    tensorCoeff (scaledScheme (K := K)) i j p q =
      8 * (if p.1=i ∧ p.2=q.1 ∧ q.2=j then (1 : K) else 0) := by
  let pp : Fin 16 := finProdFinEquiv p
  let qq : Fin 16 := finProdFinEquiv q
  let oo : Fin 16 := finProdFinEquiv (i,j)
  have hsum : (∑ t : Fin 48, (alphaInteger t pp : K) *
      (betaInteger t qq : K) * (gammaNumerator t oo : K)) = 8 * (target pp qq oo : K) := by
    have hz := congrArg (fun z : ℤ => (z : K)) (brent_integer pp qq oo)
    simpa only [tensorNumerator, Int.cast_sum, Int.cast_mul, Int.cast_ofNat] using hz
  have htarget : (target pp qq oo : K) =
      if p.1=i ∧ p.2=q.1 ∧ q.2=j then (1 : K) else 0 := by
    dsimp [pp,qq,oo]
    rw [PersonalMatrix.Outer48Scheme.target_transport]
    split <;> norm_num
  calc
    tensorCoeff (scaledScheme (K := K)) i j p q =
        ∑ t : Fin 48, (alphaInteger t pp : K) *
          (betaInteger t qq : K) * (gammaNumerator t oo : K) := by
      unfold tensorCoeff
      apply Finset.sum_congr rfl
      intro t _
      dsimp [scaledScheme,pp,qq,oo]
      ring
    _ = 8 * (target pp qq oo : K) := hsum
    _ = 8 * (if p.1=i ∧ p.2=q.1 ∧ q.2=j then (1 : K) else 0) := by rw [htarget]

theorem scaled_delta (i j : Fin 4) (x y : Index 4 → K) :
    (∑ p, ∑ q, (8 * (if p.1=i ∧ p.2=q.1 ∧ q.2=j then (1 : K) else 0)) * x p * y q) =
      8 * ∑ k : Fin 4, x (i,k) * y (k,j) := by
  calc
    _ = 8 * (∑ p, ∑ q, (if p.1=i ∧ p.2=q.1 ∧ q.2=j then (1 : K) else 0) * x p * y q) := by
      simp only [Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro p _
      apply Finset.sum_congr rfl
      intro q _
      ring
    _ = _ := by rw [delta_contraction]

/-- This is derived from the actual integer coefficient equations, not assumed. -/
theorem scaled_all_block_sizes (b : ℕ) (X Y : Blocked (K := K) 4 b) :
    outerEval scaledScheme X Y = (8 : K) • (X*Y) := by
  ext i j x y
  calc
    outerEval scaledScheme X Y i j x y = ∑ z : Fin b, ∑ p : Index 4, ∑ q : Index 4,
        tensorCoeff scaledScheme i j p q * X p.1 p.2 x z * Y q.1 q.2 z y :=
      outer_entry scaledScheme X Y i j x y
    _ = ∑ z : Fin b, 8 * ∑ k : Fin 4, X i k x z * Y k j z y := by
      apply Finset.sum_congr rfl
      intro z _
      simp_rw [scaled_tensor]
      exact scaled_delta i j (fun p => X p.1 p.2 x z) (fun q => Y q.1 q.2 z y)
    _ = 8 * (∑ z : Fin b, ∑ k : Fin 4, X i k x z * Y k j z y) := by rw [Finset.mul_sum]
    _ = ((8 : K) • (X*Y)) i j x y := by
      simp only [Matrix.smul_apply, smul_eq_mul, Matrix.mul_apply, Matrix.sum_apply]
      congr 1
      exact Finset.sum_comm

theorem hybrid_equals_outer {a b r ell : ℕ} (o : Outer K a r) (l : Leaf K b ell)
    (hl : LeafValid l) (A B : Full (K := K) a b) :
    hybridEval o l A B = flatten (outerEval o (blocks A) (blocks B)) := by
  have hleaf : ∀ t, leafReconstruct l (fun g => hybridProducts o l A B (t,g)) =
      blockLinear (o.left t) (blocks A) * blockLinear (o.right t) (blocks B) := by
    intro t
    simpa only [leafEval, hybridProducts] using
      hl (blockLinear (o.left t) (blocks A)) (blockLinear (o.right t) (blocks B))
  unfold hybridEval outerEval
  congr 1
  funext i j
  apply Finset.sum_congr rfl
  intro t _
  rw [hleaf]

def numerator (A B : Matrix (Fin 16) (Fin 16) K) : Matrix (Fin 16) (Fin 16) K :=
  PersonalMatrix.Ordinal.fromFull (hybridEval (scaledScheme (K := K))
    (PersonalMatrix.Leaf46.leaf (K := K)) (PersonalMatrix.Ordinal.toFull (a := 4) (b := 4) A)
      (PersonalMatrix.Ordinal.toFull (a := 4) (b := 4) B))

theorem numerator_correct (A B : Matrix (Fin 16) (Fin 16) K) :
    numerator A B = (8 : K) • (A*B) := by
  unfold numerator
  rw [hybrid_equals_outer _ _ PersonalMatrix.Leaf46.valid, scaled_all_block_sizes]
  rw [← blocks_mul]
  change PersonalMatrix.Ordinal.fromFull ((8 : K) •
    (PersonalMatrix.Ordinal.toFull (a := 4) (b := 4) A * PersonalMatrix.Ordinal.toFull (a := 4) (b := 4) B)) = _
  rw [PersonalMatrix.Ordinal.toFull_mul]
  change (8 : K) • PersonalMatrix.Ordinal.fromFull (PersonalMatrix.Ordinal.toFull (a := 4) (b := 4) (A*B)) = _
  rw [PersonalMatrix.Ordinal.fromFull_toFull]

theorem gate_count : scheduledGateCount (scaledScheme (K := K))
    (PersonalMatrix.Leaf46.leaf (K := K)) = 2208 := hybrid_gate_count _ _

def integerAlgorithm (A B : Matrix (Fin 16) (Fin 16) ℤ) : Matrix (Fin 16) (Fin 16) ℤ :=
  fun i j => numerator A B i j / 8

theorem numerator_divisible (A B : Matrix (Fin 16) (Fin 16) ℤ) (i j : Fin 16) :
    (8 : ℤ) ∣ numerator A B i j := by
  rw [numerator_correct]
  exact ⟨(A*B) i j, rfl⟩

theorem integer_correct (A B : Matrix (Fin 16) (Fin 16) ℤ) : integerAlgorithm A B = A*B := by
  ext i j
  change numerator A B i j / 8 = (A*B) i j
  rw [numerator_correct]
  exact Int.mul_ediv_cancel_left _ (by decide)

theorem certified_integer2208 (A B : Matrix (Fin 16) (Fin 16) ℤ) :
    integerAlgorithm A B = A*B ∧
      scheduledGateCount (scaledScheme (K := ℤ)) (PersonalMatrix.Leaf46.leaf (K := ℤ)) = 2208 :=
  ⟨integer_correct A B, gate_count⟩

#print axioms scaled_tensor
#print axioms scaled_all_block_sizes
#print axioms numerator_correct
#print axioms gate_count
#print axioms numerator_divisible
#print axioms integer_correct
#print axioms certified_integer2208
#check @numerator_correct
#check @certified_integer2208
end PersonalMatrix.IntegerLate
