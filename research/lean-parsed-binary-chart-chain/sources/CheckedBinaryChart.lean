import Mathlib.Data.ZMod.Basic
import Mathlib.LinearAlgebra.Pi

/-!
Executable scalar certificates for a reusable class of binary address charts.
The dimension, serialized columns, permutation, update vector and linear-form
coefficients are parameters. The certificate checks column bounds, vanishing
of the form on the update vector, and all scalar entries of the proposed
permutation/rank-one factorization. Soundness derives equality of the actual
serialized-column linear map with a constructed equivalence, both inverse
identities and transport of arbitrary payloads. Operator equality is a result,
not an input hypothesis.

The typed permutation already carries its bijection proof. Parsing bytes,
validating a raw permutation list, selecting a source instance and identifying
the actual physical chart remain earlier/later source suppliers. Failure of
this sufficient factorization checker does not imply that an arbitrary binary
matrix is singular. Complex phase, affine translations, rounding, cost and
physical execution are not modeled by this linear binary certificate.

Reuses Mathlib linear maps, finite-product coefficient completeness and
characteristic-two module laws. Concrete motivating source: Jeremy Kothe's
T16 helper routing, Rohan Arun PR1094, Hao Yan PR514/484/507 lineage. The frozen
L450 adapter remains separate. Apache-2.0; OpenAI assistance. UNCOMPILED.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.CheckedBinaryChart

abbrev Address (n : Nat) := Fin n → ZMod 2

structure Candidate (n : Nat) where
  columns : Fin n → Nat
  permutation : Equiv.Perm (Fin n)
  updateVector : Address n
  coefficients : Address n

def bits {n : Nat} (v : Nat) : Address n :=
  fun i => if v.testBit i.val then 1 else 0

/-- Independent linear interpretation of every serialized column. -/
def sourceLinear {n : Nat} (c : Candidate n) : Address n →ₗ[ZMod 2] Address n :=
  LinearMap.lsum (ZMod 2) (fun _ : Fin n => ZMod 2) (ZMod 2)
    (fun j => (LinearMap.id : ZMod 2 →ₗ[ZMod 2] ZMod 2).smulRight (bits (c.columns j)))

/-- The finite coefficient vector determines a computable linear form. -/
def form {n : Nat} (c : Candidate n) : Address n →ₗ[ZMod 2] ZMod 2 :=
  LinearMap.lsum (ZMod 2) (fun _ : Fin n => ZMod 2) (ZMod 2)
    (fun j => (LinearMap.id : ZMod 2 →ₗ[ZMod 2] ZMod 2).smulRight (c.coefficients j))

private theorem sourceLinear_single {n : Nat} (c : Candidate n) (j : Fin n)
    (a : ZMod 2) : sourceLinear c (Pi.single j a) = a • bits (c.columns j) := by
  rw [sourceLinear, LinearMap.lsum_piSingle]
  rfl

private theorem form_single {n : Nat} (c : Candidate n) (j : Fin n) :
    form c (Pi.single j 1) = c.coefficients j := by
  rw [form, LinearMap.lsum_piSingle]
  exact one_smul (ZMod 2) (c.coefficients j)

/-- Finite scalar obligations only; no equality of function-space operators. -/
def Checks {n : Nat} (c : Candidate n) : Prop :=
  (∀ j, c.columns j < 2 ^ n) ∧
  form c c.updateVector = 0 ∧
  ∀ j i, bits (c.columns j) i = (Pi.single (c.permutation j) 1 : Address n) i +
    c.coefficients (c.permutation j) * c.updateVector i

instance {n : Nat} (c : Candidate n) : Decidable (Checks c) := by
  unfold Checks
  infer_instance

def check {n : Nat} (c : Candidate n) : Bool := decide (Checks c)

theorem check_iff {n : Nat} (c : Candidate n) : check c = true ↔ Checks c := by
  simp only [check, decide_eq_true_eq]

theorem checked_column_bounds {n : Nat} (c : Candidate n) (h : check c = true) :
    ∀ j, c.columns j < 2 ^ n := ((check_iff c).mp h).1

/-- Linear coordinate push-forward: a unit at j moves to permutation(j). -/
def reorder {n : Nat} (p : Equiv.Perm (Fin n)) :
    Address n ≃ₗ[ZMod 2] Address n where
  toFun x i := x (p.symm i)
  invFun x i := x (p i)
  left_inv := by intro x; funext i; simp
  right_inv := by intro x; funext i; simp
  map_add' := by intro x y; rfl
  map_smul' := by intro a x; rfl

private theorem reorder_apply {n : Nat} (p : Equiv.Perm (Fin n))
    (x : Address n) (i : Fin n) : reorder p x i = x (p.symm i) := rfl

private theorem reorder_single {n : Nat} (p : Equiv.Perm (Fin n)) (j : Fin n) :
    reorder p (Pi.single j 1) = Pi.single (p j) 1 := by
  funext i
  simp only [reorder_apply, Pi.single_apply, Equiv.symm_apply_eq]

def transvection {n : Nat} (u : Address n) (f : Address n →ₗ[ZMod 2] ZMod 2) :
    Address n →ₗ[ZMod 2] Address n := LinearMap.id + f.smulRight u

/-- Valid for arbitrary update vectors/forms, with the actual scalar condition. -/
theorem transvection_involutive {n : Nat} (u : Address n)
    (f : Address n →ₗ[ZMod 2] ZMod 2) (h : f u = 0) :
    Function.Involutive (transvection u f) := by
  intro x
  change (x + f x • u) + f (x + f x • u) • u = x
  rw [map_add, map_smul, h, smul_zero, add_zero,
    add_assoc, ZModModule.add_self, add_zero]

def checkedEquiv {n : Nat} (c : Candidate n) (h : check c = true) :
    Address n ≃ₗ[ZMod 2] Address n :=
  (reorder c.permutation).trans
    (LinearEquiv.ofInvolutive (transvection c.updateVector (form c))
      (transvection_involutive c.updateVector (form c) ((check_iff c).mp h).2.1))

private theorem checked_column_action {n : Nat} (c : Candidate n)
    (h : check c = true) (j : Fin n) :
    bits (c.columns j) = checkedEquiv c h (Pi.single j 1) := by
  change bits (c.columns j) =
    transvection c.updateVector (form c) (reorder c.permutation (Pi.single j 1))
  rw [reorder_single]
  change bits (c.columns j) = Pi.single (c.permutation j) 1 +
    form c (Pi.single (c.permutation j) 1) • c.updateVector
  rw [form_single]
  funext i
  exact ((check_iff c).mp h).2.2 j i

/-- Coefficient completeness turns finite scalar checks into equality on all
addresses. Each coordinate's coefficient is arbitrary, not sampled. -/
theorem sourceLinear_eq_checked {n : Nat} (c : Candidate n)
    (h : check c = true) : sourceLinear c = (checkedEquiv c h).toLinearMap := by
  apply LinearMap.pi_ext
  intro j a
  have hs : Pi.single j a = a • (Pi.single j 1 : Address n) := by
    rw [← Pi.single_smul']
    simp
  rw [hs]
  simp only [map_smul]
  apply congrArg (fun x : Address n => a • x)
  rw [sourceLinear_single, one_smul]
  exact checked_column_action c h j

/-- Explicit executable inverse candidate: undo the rank-one map, then reorder. -/
def inverseAddress {n : Nat} (c : Candidate n) (x : Address n) : Address n :=
  (reorder c.permutation).symm (transvection c.updateVector (form c) x)

theorem inverse_source {n : Nat} (c : Candidate n) (h : check c = true)
    (x : Address n) : inverseAddress c (sourceLinear c x) = x := by
  change (checkedEquiv c h).symm (sourceLinear c x) = x
  rw [sourceLinear_eq_checked c h]
  exact (checkedEquiv c h).symm_apply_apply x

theorem source_inverse {n : Nat} (c : Candidate n) (h : check c = true)
    (x : Address n) : sourceLinear c (inverseAddress c x) = x := by
  change sourceLinear c ((checkedEquiv c h).symm x) = x
  rw [sourceLinear_eq_checked c h]
  exact (checkedEquiv c h).apply_symm_apply x

section Payload
variable {n : Nat} (K : Type*) [Semiring K] (c : Candidate n) (h : check c = true)

/-- Explicit pullback convention over arbitrary payloads and all coordinates. -/
def checkedPullback : (Address n → K) ≃ₗ[K] (Address n → K) where
  toFun f x := f (sourceLinear c x)
  invFun f x := f (inverseAddress c x)
  left_inv := by
    intro f; funext x
    change f (sourceLinear c (inverseAddress c x)) = f x
    rw [source_inverse c h]
  right_inv := by
    intro f; funext x
    change f (inverseAddress c (sourceLinear c x)) = f x
    rw [inverse_source c h]
  map_add' := by intro f g; rfl
  map_smul' := by intro a f; rfl

theorem arbitrary_payload_inverse (f : Address n → K) :
    (checkedPullback K c h).symm (checkedPullback K c h f) = f :=
  (checkedPullback K c h).symm_apply_apply f

end Payload
end CurrentMain.CheckedBinaryChart

#print axioms CurrentMain.CheckedBinaryChart.check_iff
#print axioms CurrentMain.CheckedBinaryChart.checked_column_bounds
#print axioms CurrentMain.CheckedBinaryChart.transvection_involutive
#print axioms CurrentMain.CheckedBinaryChart.sourceLinear_eq_checked
#print axioms CurrentMain.CheckedBinaryChart.inverse_source
#print axioms CurrentMain.CheckedBinaryChart.source_inverse
#print axioms CurrentMain.CheckedBinaryChart.arbitrary_payload_inverse
#check @CurrentMain.CheckedBinaryChart.sourceLinear_eq_checked
