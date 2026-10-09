import FramedXor
import Mathlib.Algebra.Group.Hom.Defs
import Mathlib.LinearAlgebra.Matrix.ToLin
import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic

/-!
Concrete address gauges for the binary-payload transfer.

Address coordinates live in an arbitrary additive commutative group. They are
NOT the Boolean scalar payload. The selected circuit uses partial-swap gauges;
the additive shear gauges below also identify the original upstream interface.
No scalar-field extension of the XOR mixer is asserted or needed.
-/

namespace AddressGauges
open FramedXor DirtyWrapper

variable {E D R : Type}

def shearGauge [AddCommGroup E] (matrix : D → E) : Gauge (E × D) where
  forward p := (p.1 + matrix p.2, p.2)
  inverse p := (p.1 - matrix p.2, p.2)
  inverse_forward p := by cases p; simp
  forward_inverse p := by cases p; simp

/-- The position transport new * old^{-1} is the positive matrix difference. -/
theorem shear_position_transport [AddCommGroup E] (old new : D → E) (p : E × D) :
    (shearGauge new).forward ((shearGauge old).inverse p) =
      (shearGauge (fun d => new d - old d)).forward p := by
  apply Prod.ext <;> simp only [shearGauge]
  abel

/-- The payload reindexing has the opposite sign, exactly as in FramedXor.reframe. -/
theorem shear_payload_transport [AddCommGroup E] (old new : D → E) (p : E × D) :
    (shearGauge old).forward ((shearGauge new).inverse p) =
      (shearGauge (fun d => new d - old d)).inverse p := by
  apply Prod.ext <;> simp only [shearGauge]
  abel

theorem shear_endpoint_frames [AddCommGroup E] (first last : E → E)
    (difference : ∀ d, last d - first d = d) (p : E × E) :
    (shearGauge last).forward p =
      (shearGauge (fun d : E => d)).forward ((shearGauge first).forward p) := by
  apply Prod.ext <;> simp only [shearGauge]
  have value := sub_eq_iff_eq_add.mp (difference p.2)
  rw [value]
  abel

theorem shear_all_role_endpoint [AddCommGroup E] [DecidableEq R]
    (input output : R → E → E) (destination : R → R)
    (difference : ∀ r d, output (destination r) d - input r d = d)
    (trace : Trace (fun r => shearGauge (input r)) (fun r => shearGauge (output r)))
    (scalar_roles : ∀ (logical : Rows R (E × E)) (r : R) (address : E × E),
      runRows (scalarWord trace) logical (destination r) address = logical r address)
    (physical : Rows R (E × E)) (r : R) (h d : E) :
    execute trace physical (destination r) (h, d) = physical r (h - d, d) := by
  apply terminal_role_transport trace destination (shearGauge (fun x : E => x)) scalar_roles
  intro role address
  exact shear_endpoint_frames (input role) (output (destination role)) (difference role) address

def swapGauge (E : Type) : Gauge (E × E) where
  forward p := (p.2, p.1)
  inverse p := (p.2, p.1)
  inverse_forward p := by cases p; rfl
  forward_inverse p := by cases p; rfl

/-- The original ordered streaming / expensive shear / ordered streaming
schedule, in its actual chronological order, exchanges the two address chunks. -/
theorem ordered_shear_swap [AddCommGroup E] (h d : E) :
    let first : E × E := (h, d - h)
    let middle := (shearGauge (fun x : E => x)).forward first
    let last : E × E := (middle.1, middle.1 - middle.2)
    last = (d, h) := by
  dsimp [shearGauge]
  apply Prod.ext <;> dsimp <;> abel

/-- Selected partial-swap frame D_P, written without choosing coordinates.
For a linear projector P this equals ((I-P)x+Py, Px+(I-P)y). -/
def partialSwap [AddCommGroup E] (projector : E →+ E) (p : E × E) : E × E :=
  (p.1 + projector (p.2 - p.1), p.2 - projector (p.2 - p.1))

theorem partialSwap_involution [AddCommGroup E] (projector : E →+ E)
    (idempotent : ∀ x, projector (projector x) = projector x) (p : E × E) :
    partialSwap projector (partialSwap projector p) = p := by
  apply Prod.ext <;>
    simp only [partialSwap, map_sub, map_add, idempotent] <;> abel

def partialSwapGauge [AddCommGroup E] (projector : E →+ E)
    (idempotent : ∀ x, projector (projector x) = projector x) : Gauge (E × E) where
  forward := partialSwap projector
  inverse := partialSwap projector
  inverse_forward := partialSwap_involution projector idempotent
  forward_inverse := partialSwap_involution projector idempotent

theorem difference_idempotent [AddCommGroup E] (small large : E →+ E)
    (small_idem : ∀ x, small (small x) = small x)
    (large_idem : ∀ x, large (large x) = large x)
    (small_large : ∀ x, small (large x) = small x)
    (large_small : ∀ x, large (small x) = small x) (x : E) :
    (large - small) ((large - small) x) = (large - small) x := by
  simp only [AddMonoidHom.sub_apply, map_sub, small_idem, large_idem,
    small_large, large_small]
  abel

/-- One direction of the selected nested-frame identity needs the displayed
absorption equation. The reverse direction below uses the other equation. -/
theorem partialSwap_nested [AddCommGroup E] (small large : E →+ E)
    (large_small : ∀ x, large (small x) = small x) (p : E × E) :
    partialSwap large (partialSwap small p) = partialSwap (large - small) p := by
  apply Prod.ext <;>
    simp only [partialSwap, AddMonoidHom.sub_apply, map_sub, map_add,
      large_small] <;> abel

theorem partialSwap_nested_reverse [AddCommGroup E] (small large : E →+ E)
    (small_large : ∀ x, small (large x) = small x) (p : E × E) :
    partialSwap small (partialSwap large p) = partialSwap (large - small) p := by
  apply Prod.ext <;>
    simp only [partialSwap, AddMonoidHom.sub_apply, map_sub, map_add,
      small_large] <;> abel

theorem complement_idempotent [AddCommGroup E] (projector : E →+ E)
    (idempotent : ∀ x, projector (projector x) = projector x) (x : E) :
    (AddMonoidHom.id E - projector) ((AddMonoidHom.id E - projector) x) =
      (AddMonoidHom.id E - projector) x := by
  simp only [AddMonoidHom.sub_apply, AddMonoidHom.id_apply, map_sub, idempotent]
  abel

/-- Complementing and reversing a nested path preserves the residual matrix,
not just its rank. This is the profile-preserving reverse-orientation law. -/
theorem complement_difference [AddCommGroup E] (small large : E →+ E) :
    (AddMonoidHom.id E - small) - (AddMonoidHom.id E - large) = large - small := by
  ext x
  simp only [AddMonoidHom.sub_apply, AddMonoidHom.id_apply]
  abel

theorem reverse_complement_residual [AddCommGroup E] (small large : E →+ E)
    (large_small : ∀ x, large (small x) = small x) (p : E × E) :
    partialSwap (AddMonoidHom.id E - large)
      (partialSwap (AddMonoidHom.id E - small) p) = partialSwap (large - small) p := by
  have absorption : ∀ x, (AddMonoidHom.id E - large) ((AddMonoidHom.id E - small) x) =
      (AddMonoidHom.id E - large) x := by
    intro x
    simp only [AddMonoidHom.sub_apply, AddMonoidHom.id_apply, map_sub, large_small]
    abel
  rw [partialSwap_nested_reverse _ _ absorption, complement_difference]

/-- The complement endpoint relation needed by terminal_role_transport. -/
theorem partialSwap_complement_frame [AddCommGroup E] (projector : E →+ E) (p : E × E) :
    partialSwap (AddMonoidHom.id E - projector) p =
      (swapGauge E).forward (partialSwap projector p) := by
  apply Prod.ext <;>
    simp only [partialSwap, AddMonoidHom.sub_apply, AddMonoidHom.id_apply, swapGauge] <;> abel

theorem partialSwap_complement_product [AddCommGroup E] (projector : E →+ E)
    (idempotent : ∀ x, projector (projector x) = projector x) (p : E × E) :
    partialSwap (AddMonoidHom.id E - projector) (partialSwap projector p) =
      (swapGauge E).forward p := by
  rw [partialSwap_complement_frame, partialSwap_involution projector idempotent]

/-- Actual partial-swap endpoint specialization. Its payload is still Bool;
the address coordinates can be ZMod(q^f) vectors or any additive module. -/
theorem selected_partial_swap_endpoint [AddCommGroup E] [DecidableEq R]
    (input output : R → E →+ E)
    (input_idem : ∀ r x, input r (input r x) = input r x)
    (output_idem : ∀ r x, output r (output r x) = output r x)
    (destination : R → R)
    (complement : ∀ r, output (destination r) = AddMonoidHom.id E - input r)
    (trace : Trace (fun r => partialSwapGauge (input r) (input_idem r))
      (fun r => partialSwapGauge (output r) (output_idem r)))
    (scalar_roles : ∀ (logical : Rows R (E × E)) (r : R) (address : E × E),
      runRows (scalarWord trace) logical (destination r) address = logical r address)
    (physical : Rows R (E × E)) (r : R) (h d : E) :
    execute trace physical (destination r) (h, d) = physical r (d, h) := by
  apply terminal_role_transport trace destination (swapGauge E) scalar_roles
  intro role address
  change partialSwap (output (destination role)) address =
    (swapGauge E).forward (partialSwap (input role) address)
  rw [complement]
  exact partialSwap_complement_frame (input role) address

section Matrices

variable {K n : Type} [CommRing K] [Fintype n] [DecidableEq n]

def matrixEndomorphism (matrix : Matrix n n K) : (n → K) →+ (n → K) :=
  matrix.mulVecLin.toAddMonoidHom

omit [DecidableEq n] in
theorem matrix_idempotent (projector : Matrix n n K) (idempotent : projector * projector = projector)
    (vector : n → K) :
    matrixEndomorphism projector (matrixEndomorphism projector vector) = matrixEndomorphism projector vector := by
  change projector.mulVec (projector.mulVec vector) = projector.mulVec vector
  rw [Matrix.mulVec_mulVec, idempotent]

omit [DecidableEq n] in
theorem matrix_absorption (left right : Matrix n n K) (absorption : left * right = right)
    (vector : n → K) :
    matrixEndomorphism left (matrixEndomorphism right vector) = matrixEndomorphism right vector := by
  change left.mulVec (right.mulVec vector) = right.mulVec vector
  rw [Matrix.mulVec_mulVec, absorption]

theorem matrix_complement (projector : Matrix n n K) :
    matrixEndomorphism (1 - projector) = AddMonoidHom.id (n → K) - matrixEndomorphism projector := by
  apply AddMonoidHom.ext
  intro vector
  change (1 - projector).mulVec vector = vector - projector.mulVec vector
  rw [Matrix.sub_mulVec, Matrix.one_mulVec]

/-- A rational or reduced modular projector supplies a concrete permutation
gauge; both inverse laws follow from the matrix equation P*P=P. -/
def matrixPartialSwapGauge (projector : Matrix n n K) (idempotent : projector * projector = projector) :
    Gauge ((n → K) × (n → K)) :=
  partialSwapGauge (matrixEndomorphism projector) (matrix_idempotent projector idempotent)

theorem matrix_partialSwap_involution (projector : Matrix n n K)
    (idempotent : projector * projector = projector) (p : (n → K) × (n → K)) :
    (matrixPartialSwapGauge projector idempotent).forward
      ((matrixPartialSwapGauge projector idempotent).forward p) = p :=
  partialSwap_involution (matrixEndomorphism projector) (matrix_idempotent projector idempotent) p

end Matrices

/-- Concrete address domain ZMod(q^f)^m. Neither q's primality nor its
characteristic is a payload-field assumption. Eligibility is used separately
to obtain the supplied reduced projector equation from the rational table. -/
def modularPartialSwapGauge {n : Type} [Fintype n] [DecidableEq n]
    (q f : ℕ) (projector : Matrix n n (ZMod (q ^ f)))
    (idempotent : projector * projector = projector) :
    Gauge ((n → ZMod (q ^ f)) × (n → ZMod (q ^ f))) :=
  matrixPartialSwapGauge projector idempotent

#print axioms shear_position_transport
#print axioms shear_payload_transport
#print axioms shear_endpoint_frames
#print axioms shear_all_role_endpoint
#print axioms ordered_shear_swap
#print axioms partialSwap_involution
#print axioms difference_idempotent
#print axioms partialSwap_nested
#print axioms partialSwap_nested_reverse
#print axioms complement_idempotent
#print axioms complement_difference
#print axioms reverse_complement_residual
#print axioms partialSwap_complement_frame
#print axioms partialSwap_complement_product
#print axioms selected_partial_swap_endpoint
#print axioms matrix_idempotent
#print axioms matrix_absorption
#print axioms matrix_complement
#print axioms matrix_partialSwap_involution

end AddressGauges
