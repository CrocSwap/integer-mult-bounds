import Mathlib

/-!
# Lemma OC (overcomplete coupling), IDEAL2 §2.1

If `X : T × m` and `Y : T × m` satisfy `X * Yᵀ = 1` (an `m`-term exact decomposition of the
identity, `Σⱼ xⱼ yⱼᵀ = I_T`), then the `m × m` cross matrix `K = Yᵀ * X` (entries `⟨y_i, x_j⟩`) is
idempotent with trace `T`; hence `Π = 1 - K` is idempotent with trace `m - T`.
-/

open Matrix
set_option linter.unusedSectionVars false

namespace DecoderDuality

variable {K : Type*} [Field K] {T m : Type*} [Fintype T] [Fintype m] [DecidableEq T] [DecidableEq m]

theorem oc_idempotent (X Y : Matrix T m K) (h : X * Yᵀ = 1) :
    (Yᵀ * X) * (Yᵀ * X) = Yᵀ * X := by
  calc (Yᵀ * X) * (Yᵀ * X) = Yᵀ * (X * Yᵀ) * X := by simp only [Matrix.mul_assoc]
    _ = Yᵀ * X := by rw [h, Matrix.mul_one]

theorem oc_trace (X Y : Matrix T m K) (h : X * Yᵀ = 1) :
    (Yᵀ * X).trace = (Fintype.card T : K) := by
  rw [Matrix.trace_mul_comm, h, Matrix.trace_one]

theorem oc_complement_idempotent (X Y : Matrix T m K) (h : X * Yᵀ = 1) :
    (1 - Yᵀ * X) * (1 - Yᵀ * X) = 1 - Yᵀ * X := by
  have hK := oc_idempotent X Y h
  rw [sub_mul, mul_sub, mul_sub, Matrix.one_mul, Matrix.mul_one, Matrix.one_mul, hK]
  abel

theorem oc_complement_trace (X Y : Matrix T m K) (h : X * Yᵀ = 1) :
    (1 - Yᵀ * X).trace = (Fintype.card m : K) - (Fintype.card T : K) := by
  rw [Matrix.trace_sub, Matrix.trace_one, oc_trace X Y h]

/-- Square case (biorthogonality): if moreover `Yᵀ * X` has an inverse-side identity, it is `1`.
For `m = T` with `X * Yᵀ = 1` we get `Yᵀ * X = 1`, i.e. `⟨y_i, x_j⟩ = δ_ij`. -/
theorem oc_square (X Y : Matrix T T K) (h : X * Yᵀ = 1) : Yᵀ * X = 1 :=
  mul_eq_one_comm.mp h

end DecoderDuality

#print axioms DecoderDuality.oc_idempotent
#print axioms DecoderDuality.oc_complement_trace
#print axioms DecoderDuality.oc_square
