import EligibleLocalization

/-! Rationally checked identities of finite localized matrix tables reduce
to every eligible commutative address ring. No reduced identity is a premise.
Including rational inverse witnesses preserves prescribed pivot/Gram units.
-/
namespace LocalizedMatrixTransfer
open EligibleLocalization
open scoped Kronecker

variable {n : Type} [Fintype n] [DecidableEq n]

omit [Fintype n] [DecidableEq n] in
theorem rational_zero_reduces (D : ℕ) (hD : 0 < D) (K : Type) [CommRing K]
    (eligible : IsUnit (D : K)) (x : Coeff D) (rational_zero : rationalView D hD x = 0) :
    reduction D K eligible x = 0 := by
  have hx : x = 0 := rationalView_injective D hD (by simpa using rational_zero)
  simp [hx]

omit [Fintype n] [DecidableEq n] in
theorem rational_lower_triangular_reduces [LT n] (D : ℕ) (hD : 0 < D)
    (K : Type) [CommRing K] (eligible : IsUnit (D : K)) (A : Matrix n n (Coeff D))
    (rational_lower : ∀ i j, i < j → rationalView D hD (A i j) = 0) :
    ∀ i j, i < j → reduction D K eligible (A i j) = 0 := by
  intro i j hij
  exact rational_zero_reduces D hD K eligible (A i j) (rational_lower i j hij)

theorem rational_matrix_injective (D : ℕ) (hD : 0 < D) :
    Function.Injective ((rationalView D hD).mapMatrix : Matrix n n (Coeff D) → Matrix n n ℚ) := by
  intro A B h
  ext i j
  apply rationalView_injective D hD
  exact congrFun (congrFun h i) j

/-- Equality is checked over Q and reflected into the denominator localization
before reduction; the target finite ring need not be a field. -/
theorem rational_equality_reduces (D : ℕ) (hD : 0 < D) (K : Type) [CommRing K]
    (eligible : IsUnit (D : K)) (A B : Matrix n n (Coeff D))
    (rational_identity : (rationalView D hD).mapMatrix A = (rationalView D hD).mapMatrix B) :
    (reduction D K eligible).mapMatrix A = (reduction D K eligible).mapMatrix B := by
  exact congrArg (reduction D K eligible).mapMatrix
    (rational_matrix_injective D hD rational_identity)

theorem rational_product_reduces (D : ℕ) (hD : 0 < D) (K : Type) [CommRing K]
    (eligible : IsUnit (D : K)) (A B C : Matrix n n (Coeff D))
    (rational_identity : (rationalView D hD).mapMatrix A * (rationalView D hD).mapMatrix B =
      (rationalView D hD).mapMatrix C) :
    (reduction D K eligible).mapMatrix A * (reduction D K eligible).mapMatrix B =
      (reduction D K eligible).mapMatrix C := by
  have h := rational_equality_reduces D hD K eligible (A * B) C (by simpa using rational_identity)
  simpa using h

theorem rational_projector_reduces (D : ℕ) (hD : 0 < D) (K : Type) [CommRing K]
    (eligible : IsUnit (D : K)) (P : Matrix n n (Coeff D))
    (rational_idempotent : (rationalView D hD).mapMatrix P * (rationalView D hD).mapMatrix P =
      (rationalView D hD).mapMatrix P) :
    (reduction D K eligible).mapMatrix P * (reduction D K eligible).mapMatrix P =
      (reduction D K eligible).mapMatrix P :=
  rational_product_reduces D hD K eligible P P P rational_idempotent

/-- Both absorption directions survive; these are the two obligations in
the selected partial-swap nested-frame transport theorem. -/
theorem rational_nested_reduces (D : ℕ) (hD : 0 < D) (K : Type) [CommRing K]
    (eligible : IsUnit (D : K)) (small large : Matrix n n (Coeff D))
    (left : (rationalView D hD).mapMatrix small * (rationalView D hD).mapMatrix large =
      (rationalView D hD).mapMatrix small)
    (right : (rationalView D hD).mapMatrix large * (rationalView D hD).mapMatrix small =
      (rationalView D hD).mapMatrix small) :
    (reduction D K eligible).mapMatrix small * (reduction D K eligible).mapMatrix large =
      (reduction D K eligible).mapMatrix small ∧
    (reduction D K eligible).mapMatrix large * (reduction D K eligible).mapMatrix small =
      (reduction D K eligible).mapMatrix small :=
  ⟨rational_product_reduces D hD K eligible small large small left,
    rational_product_reduces D hD K eligible large small small right⟩

theorem reduction_complement (D : ℕ) (K : Type) [CommRing K]
    (eligible : IsUnit (D : K)) (P : Matrix n n (Coeff D)) :
    (reduction D K eligible).mapMatrix (1 - P) = 1 - (reduction D K eligible).mapMatrix P := by
  rw [map_sub, map_one]

theorem reduction_difference (D : ℕ) (K : Type) [CommRing K]
    (eligible : IsUnit (D : K)) (P Q : Matrix n n (Coeff D)) :
    (reduction D K eligible).mapMatrix (P - Q) =
      (reduction D K eligible).mapMatrix P - (reduction D K eligible).mapMatrix Q := by
  exact map_sub ((reduction D K eligible).mapMatrix) P Q

/-- Exact lower/partial-permutation/upper (or lower/lower) factorizations
survive with the same middle pattern; no rank approximation is used. -/
theorem rational_factorization_reduces (D : ℕ) (hD : 0 < D) (K : Type) [CommRing K]
    (eligible : IsUnit (D : K)) (A L pattern R : Matrix n n (Coeff D))
    (rational_identity : (rationalView D hD).mapMatrix A =
      (rationalView D hD).mapMatrix L * (rationalView D hD).mapMatrix pattern *
        (rationalView D hD).mapMatrix R) :
    (reduction D K eligible).mapMatrix A = (reduction D K eligible).mapMatrix L *
      (reduction D K eligible).mapMatrix pattern * (reduction D K eligible).mapMatrix R := by
  have h := rational_equality_reduces D hD K eligible A (L * pattern * R)
    (by simpa using rational_identity)
  simpa using h

theorem integral_pattern_reduces (D : ℕ) (K : Type) [CommRing K]
    (eligible : IsUnit (D : K)) (pattern : Matrix n n ℤ) :
    (reduction D K eligible).mapMatrix ((algebraMap ℤ (Coeff D)).mapMatrix pattern) =
      (Int.castRingHom K).mapMatrix pattern := by
  ext i j
  simp

theorem reduction_kronecker {l m o q : Type} (D : ℕ) (K : Type) [CommRing K]
    (eligible : IsUnit (D : K)) (A : Matrix l m (Coeff D)) (B : Matrix o q (Coeff D)) :
    (A ⊗ₖ B).map (reduction D K eligible) =
      (A.map (reduction D K eligible)) ⊗ₖ (B.map (reduction D K eligible)) := by
  ext i j
  simp [Matrix.kroneckerMap_apply]

/-- Stored triangular/conjugating inverses remain genuine two-sided inverses
over the address ring; rational invertibility is not substituted for a unit. -/
theorem rational_inverse_reduces (D : ℕ) (hD : 0 < D) (K : Type) [CommRing K]
    (eligible : IsUnit (D : K)) (A B : Matrix n n (Coeff D))
    (left : (rationalView D hD).mapMatrix A * (rationalView D hD).mapMatrix B = 1)
    (right : (rationalView D hD).mapMatrix B * (rationalView D hD).mapMatrix A = 1) :
    (reduction D K eligible).mapMatrix A * (reduction D K eligible).mapMatrix B = 1 ∧
    (reduction D K eligible).mapMatrix B * (reduction D K eligible).mapMatrix A = 1 := by
  constructor
  · simpa using rational_product_reduces D hD K eligible A B 1 (by simpa using left)
  · simpa using rational_product_reduces D hD K eligible B A 1 (by simpa using right)

/-- Unit determinant of any stored square minor follows from its rational
inverse witness. This applies to Gram blocks and prescribed pivot minors. -/
theorem rational_minor_unit_reduces (D : ℕ) (hD : 0 < D) (K : Type) [CommRing K]
    (eligible : IsUnit (D : K)) (A B : Matrix n n (Coeff D))
    (right : (rationalView D hD).mapMatrix A * (rationalView D hD).mapMatrix B = 1) :
    IsUnit ((reduction D K eligible).mapMatrix A).det := by
  apply Matrix.isUnit_det_of_right_inverse
  simpa using rational_product_reduces D hD K eligible A B 1 (by simpa using right)

/-- A nonzero rational Gram/pivot minor and the table entry for its exact
inverse imply a unit determinant after reduction. The inverse's denominators
must be included in D, which is the necessary finite exceptional-prime data. -/
theorem nonsingular_stored_minor_reduces (D : ℕ) (hD : 0 < D) (K : Type) [CommRing K]
    (eligible : IsUnit (D : K)) (A inverseTable : Matrix n n (Coeff D))
    (nonzero : ((rationalView D hD).mapMatrix A).det ≠ 0)
    (stored_inverse : (rationalView D hD).mapMatrix inverseTable =
      ((rationalView D hD).mapMatrix A)⁻¹) :
    IsUnit ((reduction D K eligible).mapMatrix A).det := by
  apply rational_minor_unit_reduces D hD K eligible A inverseTable
  rw [stored_inverse]
  exact Matrix.mul_nonsing_inv _ (isUnit_iff_ne_zero.mpr nonzero)

/-- Scalar pivot inverses can also be stored directly, without matrix inversion. -/
theorem rational_scalar_unit_reduces (D : ℕ) (hD : 0 < D) (K : Type) [CommRing K]
    (eligible : IsUnit (D : K)) (x y : Coeff D)
    (rational_inverse : rationalView D hD x * rationalView D hD y = 1) :
    IsUnit (reduction D K eligible x) := by
  have hxy : x * y = 1 := rationalView_injective D hD (by simpa using rational_inverse)
  have hred : reduction D K eligible x * reduction D K eligible y = 1 := by
    simpa using congrArg (reduction D K eligible) hxy
  exact ⟨⟨_, _, hred, by simpa [mul_comm] using hred⟩, rfl⟩

theorem table_reciprocal_unit {ι : Type} [Fintype ι] (values : ι → ℚ) (i j : ι)
    (nonzero : values i ≠ 0) (reciprocal : values j = (values i)⁻¹)
    (K : Type) [CommRing K] (eligible : IsUnit (denominatorProduct values : K)) :
    IsUnit (reduction _ K eligible (liftTable values i)) := by
  apply rational_scalar_unit_reduces _ (denominatorProduct_positive values) K eligible
    (liftTable values i) (liftTable values j)
  rw [liftTable_exact, liftTable_exact, reciprocal, mul_inv_cancel₀ nonzero]

end LocalizedMatrixTransfer

#print axioms LocalizedMatrixTransfer.rational_matrix_injective
#print axioms LocalizedMatrixTransfer.rational_zero_reduces
#print axioms LocalizedMatrixTransfer.rational_lower_triangular_reduces
#print axioms LocalizedMatrixTransfer.rational_equality_reduces
#print axioms LocalizedMatrixTransfer.rational_product_reduces
#print axioms LocalizedMatrixTransfer.rational_projector_reduces
#print axioms LocalizedMatrixTransfer.rational_nested_reduces
#print axioms LocalizedMatrixTransfer.reduction_complement
#print axioms LocalizedMatrixTransfer.reduction_difference
#print axioms LocalizedMatrixTransfer.rational_factorization_reduces
#print axioms LocalizedMatrixTransfer.integral_pattern_reduces
#print axioms LocalizedMatrixTransfer.reduction_kronecker
#print axioms LocalizedMatrixTransfer.rational_inverse_reduces
#print axioms LocalizedMatrixTransfer.rational_minor_unit_reduces
#print axioms LocalizedMatrixTransfer.nonsingular_stored_minor_reduces
#print axioms LocalizedMatrixTransfer.rational_scalar_unit_reduces
#print axioms LocalizedMatrixTransfer.table_reciprocal_unit
