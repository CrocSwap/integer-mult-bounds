import Mathlib.Data.Matrix.Kronecker
import Mathlib.Tactic

/-! Exact ambient tensor frame identities for the selected two-stage circuit.
These are identities of actual matrices over any commutative ring, including
eligible ZMod(q^f) rings. Local schedules and pivot certificates are separate. -/
namespace TensorStageFrames
open scoped Kronecker
variable {K A B : Type} [CommRing K] [Fintype A] [Fintype B]
  [DecidableEq A] [DecidableEq B]

def first (Q : Matrix B B K) (U : Matrix A A K) : Matrix (A × B) (A × B) K := U ⊗ₖ Q

def second (P : Matrix A A K) (U : Matrix B B K) : Matrix (A × B) (A × B) K :=
  (1 - P) ⊗ₖ (1 : Matrix B B K) + P ⊗ₖ U

omit [Fintype A] [Fintype B] [DecidableEq A] [DecidableEq B] in
lemma sub_kronecker (U V : Matrix A A K) (Q : Matrix B B K) :
    (U - V) ⊗ₖ Q = U ⊗ₖ Q - V ⊗ₖ Q := by
  ext i j
  simp only [Matrix.kroneckerMap_apply, Matrix.sub_apply]
  exact sub_mul _ _ _

omit [Fintype A] [Fintype B] [DecidableEq A] [DecidableEq B] in
lemma kronecker_sub (P : Matrix A A K) (U V : Matrix B B K) :
    P ⊗ₖ (U - V) = P ⊗ₖ U - P ⊗ₖ V := by
  ext i j
  simp only [Matrix.kroneckerMap_apply, Matrix.sub_apply]
  exact mul_sub _ _ _

omit [DecidableEq A] [DecidableEq B] in
theorem first_idempotent (Q : Matrix B B K) (U : Matrix A A K)
    (hQ : Q * Q = Q) (hU : U * U = U) :
    first Q U * first Q U = first Q U := by
  simp only [first, ← Matrix.mul_kronecker_mul, hQ, hU]

theorem second_multiplication (P : Matrix A A K) (U V : Matrix B B K) (hP : P * P = P) :
    second P U * second P V = second P (U * V) := by
  have hC : (1-P)*(1-P) = 1-P := by simp [sub_mul, mul_sub, hP]
  have hCP : (1-P)*P = 0 := by simp [sub_mul, hP]
  have hPC : P*(1-P) = 0 := by simp [mul_sub, hP]
  simp only [second, add_mul, mul_add, ← Matrix.mul_kronecker_mul,
    hC, hCP, hPC, hP, mul_one, one_mul, Matrix.zero_kronecker, add_zero, zero_add]

theorem second_idempotent (P : Matrix A A K) (U : Matrix B B K)
    (hP : P * P = P) (hU : U * U = U) :
    second P U * second P U = second P U := by
  rw [second_multiplication P U U hP, hU]

omit [DecidableEq A] [DecidableEq B] in
theorem first_absorption (Q : Matrix B B K) (U V : Matrix A A K)
    (hQ : Q * Q = Q) (hUV : U * V = U) :
    first Q U * first Q V = first Q U := by
  simp only [first, ← Matrix.mul_kronecker_mul, hQ, hUV]

theorem second_absorption (P : Matrix A A K) (U V : Matrix B B K)
    (hP : P * P = P) (hUV : U * V = U) :
    second P U * second P V = second P U := by
  rw [second_multiplication P U V hP, hUV]

theorem first_residual (Q : Matrix B B K) (U V : Matrix A A K) :
    first Q V - first Q U = (V - U) ⊗ₖ Q := by
  exact (sub_kronecker V U Q).symm

theorem second_residual (P : Matrix A A K) (U V : Matrix B B K) :
    second P V - second P U = P ⊗ₖ (V - U) := by
  rw [kronecker_sub]
  simp only [second]
  abel

omit [Fintype A] [Fintype B] in
theorem second_zero (P : Matrix A A K) : second P (0 : Matrix B B K) = (1-P) ⊗ₖ (1 : Matrix B B K) := by
  simp [second, Matrix.kronecker_zero]

omit [Fintype A] [Fintype B] in
theorem second_one (P : Matrix A A K) : second P (1 : Matrix B B K) = 1 := by
  rw [second, ← Matrix.add_kronecker, sub_add_cancel, Matrix.one_kronecker_one]

theorem second_complement_formula (P : Matrix A A K) (Q : Matrix B B K) :
    second P Q = 1 - P ⊗ₖ (1-Q) := by
  rw [second, sub_kronecker, kronecker_sub, Matrix.one_kronecker_one]
  abel

theorem source_data_front (P : Matrix A A K) (Q : Matrix B B K) :
    second P Q - first Q (1 : Matrix A A K) = (1-P) ⊗ₖ (1-Q) := by
  rw [second, first, kronecker_sub, sub_kronecker (1 : Matrix A A K) P Q]
  abel

theorem target_data_front (P : Matrix A A K) (Q : Matrix B B K) :
    second P (0 : Matrix B B K) - first Q (1-P) = (1-P) ⊗ₖ (1-Q) := by
  rw [second_zero, first, kronecker_sub]

theorem second_source_growth (P : Matrix A A K) (Q : Matrix B B K) :
    second P (1 : Matrix B B K) - second P Q = P ⊗ₖ (1-Q) :=
  second_residual P Q 1

theorem second_target_growth (P : Matrix A A K) (Q : Matrix B B K) :
    second P (1-Q) - second P (0 : Matrix B B K) = P ⊗ₖ (1-Q) := by
  rw [second_residual, sub_zero]

theorem data_target_endpoint (P : Matrix A A K) (Q : Matrix B B K) :
    second P (1-Q) = 1 - P ⊗ₖ Q := by
  rw [second_complement_formula, sub_sub_cancel]

theorem first_auxiliary_exterior (Q : Matrix B B K) :
    (1 : Matrix (A × B) (A × B) K) - first Q (1 : Matrix A A K) = (1 : Matrix A A K) ⊗ₖ (1-Q) := by
  rw [first, kronecker_sub, Matrix.one_kronecker_one]

theorem second_auxiliary_exterior (P : Matrix A A K) :
    second P (1 : Matrix B B K) - P ⊗ₖ (1 : Matrix B B K) = (1-P) ⊗ₖ (1 : Matrix B B K) := by
  rw [second_one, sub_kronecker, Matrix.one_kronecker_one]

theorem second_auxiliary_complementary_endpoints (P : Matrix A A K) :
    P ⊗ₖ (1 : Matrix B B K) = 1 - second P (0 : Matrix B B K) := by
  rw [second_zero, sub_kronecker, Matrix.one_kronecker_one, sub_sub_cancel]

theorem paid_correction_residual (P : Matrix A A K) (Q : Matrix B B K) :
    (1 : Matrix (A × B) (A × B) K) - second P (1-Q) = P ⊗ₖ Q := by
  rw [data_target_endpoint, sub_sub_cancel]

end TensorStageFrames

#print axioms TensorStageFrames.sub_kronecker
#print axioms TensorStageFrames.kronecker_sub
#print axioms TensorStageFrames.first_idempotent
#print axioms TensorStageFrames.second_multiplication
#print axioms TensorStageFrames.second_idempotent
#print axioms TensorStageFrames.first_absorption
#print axioms TensorStageFrames.second_absorption
#print axioms TensorStageFrames.first_residual
#print axioms TensorStageFrames.second_residual
#print axioms TensorStageFrames.second_zero
#print axioms TensorStageFrames.second_one
#print axioms TensorStageFrames.second_complement_formula
#print axioms TensorStageFrames.source_data_front
#print axioms TensorStageFrames.target_data_front
#print axioms TensorStageFrames.second_source_growth
#print axioms TensorStageFrames.second_target_growth
#print axioms TensorStageFrames.data_target_endpoint
#print axioms TensorStageFrames.first_auxiliary_exterior
#print axioms TensorStageFrames.second_auxiliary_exterior
#print axioms TensorStageFrames.second_auxiliary_complementary_endpoints
#print axioms TensorStageFrames.paid_correction_residual
