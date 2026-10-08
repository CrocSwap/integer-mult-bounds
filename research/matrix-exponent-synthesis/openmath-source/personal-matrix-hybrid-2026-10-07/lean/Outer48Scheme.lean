import Outer48Data
import OuterLifting
import Mathlib.Logic.Equiv.Fin.Basic
import Mathlib.Algebra.Group.Invertible.Basic
import Mathlib.Tactic.NormNum

namespace PersonalMatrix.Outer48Scheme
open PersonalMatrix.Hybrid PersonalMatrix.Lifting PersonalMatrix.Outer48
open scoped BigOperators
variable {K : Type*} [CommRing K] [Invertible (2 : K)]

def scheme : Outer K 4 48 where
  left t p := (alphaInteger t (finProdFinEquiv p) : K)
  right t q := (betaInteger t (finProdFinEquiv q) : K)
  output i j t := (gammaNumerator t (finProdFinEquiv (i,j)) : K) * (⅟(2 : K))^3

/-- Pure coordinate transport of the actual row-major integer target. -/
theorem target_transport : ∀ (i j : Fin 4) (p q : Index 4),
    target (finProdFinEquiv p) (finProdFinEquiv q) (finProdFinEquiv (i,j)) =
      if p.1=i ∧ p.2=q.1 ∧ q.2=j then (1 : ℤ) else 0 := by
  decide +kernel

theorem inverse_eight : (⅟(2 : K))^3 * 8 = 1 := by
  calc
    (⅟(2 : K))^3 * 8 = (⅟(2 : K) * 2)^3 := by ring
    _ = 1 := by rw [invOf_mul_self]; norm_num

/-- The actual integer certificate supplies the scalar equations over every
commutative ring with2invertible, including odd characteristic. -/
theorem tensor_correct : TensorCorrect (scheme (K := K)) := by
  intro i j p q
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
    rw [target_transport]
    split <;> norm_num
  calc
    tensorCoeff (scheme (K := K)) i j p q = (⅟(2 : K))^3 *
        (∑ t : Fin 48, (alphaInteger t pp : K) *
          (betaInteger t qq : K) * (gammaNumerator t oo : K)) := by
      unfold tensorCoeff
      rw [Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro t _
      dsimp [scheme,pp,qq,oo]
      ring
    _ = (⅟(2 : K))^3 * (8 * (target pp qq oo : K)) := by rw [hsum]
    _ = (target pp qq oo : K) := by rw [← mul_assoc, inverse_eight, one_mul]
    _ = if p.1=i ∧ p.2=q.1 ∧ q.2=j then (1 : K) else 0 := htarget

theorem all_block_sizes : ∀ b : ℕ, BlockStable (scheme (K := K)) b :=
  block_stable_from_tensor _ tensor_correct

#print axioms target_transport
#print axioms inverse_eight
#print axioms tensor_correct
#print axioms all_block_sizes
#check @all_block_sizes
end PersonalMatrix.Outer48Scheme
