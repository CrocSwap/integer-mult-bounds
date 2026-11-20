import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.Algebra.BigOperators.Fin

/-!
# DecoderWall6Fac (lane RIGID): rank-8 factorisation through a frame.
If `M p r = ∑ k, W p k * U r k` with `card T = 8` and `M` restricted to 8 indices `c` is the identity,
then `M p r = ∑ i, M p (c i) * M (c i) r` for all `p r`.
-/
open Matrix

namespace DW6

variable {ι T K : Type*} [Fintype T] [DecidableEq T] [Field K]

/-- The completed matrix `M = W Uᵀ`. -/
def Mx (W U : ι → T → K) (p r : ι) : K := ∑ k, W p k * U r k

theorem factor (W U : ι → T → K) (c : Fin 8 → ι) (hT : Fintype.card T = 8)
    (hc : ∀ i j, Mx W U (c i) (c j) = if i = j then 1 else 0) (p r : ι) :
    Mx W U p r = ∑ i, Mx W U p (c i) * Mx W U (c i) r := by
  classical
  let e : Fin 8 ≃ T := (Fintype.equivFinOfCardEq hT).symm
  let A : Matrix (Fin 8) (Fin 8) K := Matrix.of fun i j => W (c i) (e j)
  let B : Matrix (Fin 8) (Fin 8) K := Matrix.of fun i j => U (c i) (e j)
  have hAB : A * Bᵀ = 1 := by
    ext i j
    have h := hc i j
    simp only [Mx] at h
    rw [← e.sum_comp] at h
    simpa [A, B, Matrix.mul_apply, Matrix.one_apply] using h
  have hBA : Bᵀ * A = 1 := mul_eq_one_comm.mp hAB
  have hsum : ∀ (f : T → K), ∑ k, f k = ∑ j, f (e j) := fun f => (e.sum_comp f).symm
  have key : ∀ j l : Fin 8, (∑ i, B i j * A i l) = if j = l then 1 else 0 := by
    intro j l
    have := congrFun (congrFun hBA j) l
    simpa [Matrix.mul_apply, Matrix.one_apply] using this
  calc Mx W U p r = ∑ j, W p (e j) * U r (e j) := hsum _
    _ = ∑ j, ∑ l, W p (e j) * (if j = l then 1 else 0) * U r (e l) := by
        refine Finset.sum_congr rfl fun j _ => ?_
        simp [Finset.sum_ite_eq]
    _ = ∑ j, ∑ l, W p (e j) * (∑ i, B i j * A i l) * U r (e l) := by
        simp only [key]
    _ = ∑ i, (∑ j, W p (e j) * B i j) * (∑ l, A i l * U r (e l)) := by
        simp only [Finset.mul_sum, Finset.sum_mul]
        conv_lhs => arg 2; ext j; rw [Finset.sum_comm]
        rw [Finset.sum_comm]
        refine Finset.sum_congr rfl fun i _ => ?_
        rw [Finset.sum_comm]
        refine Finset.sum_congr rfl fun j _ => ?_
        refine Finset.sum_congr rfl fun l _ => ?_
        ring
    _ = ∑ i, Mx W U p (c i) * Mx W U (c i) r := by
        refine Finset.sum_congr rfl fun i _ => ?_
        simp only [Mx, hsum (fun k => W p k * U (c i) k), hsum (fun k => W (c i) k * U r k), A, B,
          Matrix.of_apply]

end DW6
