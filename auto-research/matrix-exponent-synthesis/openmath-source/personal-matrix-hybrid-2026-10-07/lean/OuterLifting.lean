import BlockComposition
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Tactic.Ring

namespace PersonalMatrix.Lifting
open PersonalMatrix.Hybrid
open scoped BigOperators
variable {K : Type*} [CommRing K] {a b r : ℕ}
set_option maxHeartbeats 2000000
set_option backward.isDefEq.respectTransparency false
set_option backward.isDefEq.respectTransparency.types false

def tensorCoeff (o : Outer K a r) (i j : Fin a) (p q : Index a) : K :=
  ∑ t : Fin r, o.output i j t * o.left t p * o.right t q

def TensorCorrect (o : Outer K a r) : Prop :=
  ∀ i j p q, tensorCoeff o i j p q = if p.1=i ∧ p.2=q.1 ∧ q.2=j then 1 else 0

theorem weighted_contraction {T P Q : Type*} [Fintype T] [Fintype P] [Fintype Q]
    (c : T → K) (aa : T → P → K) (bb : T → Q → K) (x : P → K) (y : Q → K) :
    (∑ t, c t * (∑ p, aa t p * x p) * (∑ q, bb t q * y q)) =
      ∑ p, ∑ q, (∑ t, c t * aa t p * bb t q) * x p * y q := by
  calc
    (∑ t, c t * (∑ p, aa t p * x p) * (∑ q, bb t q * y q)) =
        ∑ t, ∑ p, ∑ q, (c t * aa t p * bb t q) * x p * y q := by
      simp only [Finset.sum_mul, Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro t _
      rw [Finset.sum_comm]
      apply Finset.sum_congr rfl
      intro p _
      apply Finset.sum_congr rfl
      intro q _
      ring
    _ = ∑ p, ∑ q, ∑ t, (c t * aa t p * bb t q) * x p * y q := by
      rw [Finset.sum_comm]
      apply Finset.sum_congr rfl
      intro p _
      rw [Finset.sum_comm]
    _ = ∑ p, ∑ q, (∑ t, c t * aa t p * bb t q) * x p * y q := by
      simp_rw [Finset.sum_mul]

theorem delta_contraction (i j : Fin a) (x y : Index a → K) :
    (∑ p, ∑ q, (if p.1=i ∧ p.2=q.1 ∧ q.2=j then (1 : K) else 0) * x p * y q) =
      ∑ k : Fin a, x (i,k) * y (k,j) := by
  simp [Fintype.sum_prod_type, ite_and, ite_mul]

theorem blockLinear_apply (c : Index a → K) (X : Blocked (K := K) a b) (x y : Fin b) :
    blockLinear c X x y = ∑ p : Index a, c p * X p.1 p.2 x y := by
  simp only [blockLinear, Matrix.sum_apply, Matrix.smul_apply, smul_eq_mul]

theorem outer_entry (o : Outer K a r) (X Y : Blocked (K := K) a b)
    (i j : Fin a) (x y : Fin b) :
    outerEval o X Y i j x y = ∑ z : Fin b, ∑ p : Index a, ∑ q : Index a,
      tensorCoeff o i j p q * X p.1 p.2 x z * Y q.1 q.2 z y := by
  have he : outerEval o X Y i j x y =
      ∑ t : Fin r, ∑ z : Fin b, o.output i j t *
        (∑ p : Index a, o.left t p * X p.1 p.2 x z) *
        (∑ q : Index a, o.right t q * Y q.1 q.2 z y) := by
    unfold outerEval
    rw [Matrix.sum_apply]
    apply Finset.sum_congr rfl
    intro t _
    rw [Matrix.smul_apply, smul_eq_mul, Matrix.mul_apply]
    simp only [blockLinear_apply]
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro z _
    ring
  rw [he, Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro z _
  exact weighted_contraction (o.output i j) o.left o.right
    (fun p => X p.1 p.2 x z) (fun q => Y q.1 q.2 z y)

/-- Scalar coefficient equations lift to the actual noncommuting matrix blocks;
no matrix-valued outer correctness premise is required here. -/
theorem block_stable_from_tensor (o : Outer K a r) (hc : TensorCorrect o) :
    ∀ b : ℕ, BlockStable o b := by
  intro b X Y
  ext i j x y
  calc
    outerEval o X Y i j x y = ∑ z : Fin b, ∑ p : Index a, ∑ q : Index a,
        tensorCoeff o i j p q * X p.1 p.2 x z * Y q.1 q.2 z y := outer_entry o X Y i j x y
    _ = ∑ z : Fin b, ∑ k : Fin a, X i k x z * Y k j z y := by
      apply Finset.sum_congr rfl
      intro z _
      calc
        (∑ p : Index a, ∑ q : Index a,
          tensorCoeff o i j p q * X p.1 p.2 x z * Y q.1 q.2 z y) =
            ∑ p : Index a, ∑ q : Index a,
              (if p.1=i ∧ p.2=q.1 ∧ q.2=j then (1 : K) else 0) *
                X p.1 p.2 x z * Y q.1 q.2 z y := by
          apply Finset.sum_congr rfl
          intro p _
          apply Finset.sum_congr rfl
          intro q _
          exact congrArg (fun c : K => c * X p.1 p.2 x z * Y q.1 q.2 z y) (hc i j p q)
        _ = ∑ k : Fin a, X i k x z * Y k j z y :=
          delta_contraction i j (fun p => X p.1 p.2 x z) (fun q => Y q.1 q.2 z y)
    _ = (X*Y) i j x y := by
      simp only [Matrix.mul_apply, Matrix.sum_apply]
      exact Finset.sum_comm

#print axioms weighted_contraction
#print axioms delta_contraction
#print axioms block_stable_from_tensor
#check @block_stable_from_tensor
end PersonalMatrix.Lifting
