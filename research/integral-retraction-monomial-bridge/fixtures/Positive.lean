/-
SPDX-License-Identifier: Apache-2.0
Locally kernel checked after source-only delivery; see REPLAY.json.
Independent synthetic tests; none is a hypothesis of the universal theorems.
-/
import PR1497Bridge

set_option autoImplicit false

namespace PR1497.Fixtures

-- m = 1, N = 2, d = 1.  Both rows of W are nonzero; Q has a negative entry.
-- M = [-2, 1], P = [1; 2], Q = [3, -1], W = [1; 3].
def M : Mat 1 2 := fun _ j => if j.val = 0 then -2 else 1
def P : Mat 2 1 := fun i _ => if i.val = 0 then 1 else 2
def Q : Mat 1 2 := fun _ j => if j.val = 0 then 3 else -1
def W : Mat 2 1 := fun i _ => if i.val = 0 then 1 else 3

theorem fixtureIdentities : MatrixIdentities M P Q W := by
  constructor
  · funext i j
    revert i j
    simp only [Fin.forall_fin_succ, Fin.forall_fin_zero] <;> decide
  · funext i j
    revert i j
    simp only [Fin.forall_fin_succ, Fin.forall_fin_zero] <;> decide
  · funext i j
    revert i j
    simp only [Fin.forall_fin_succ, Fin.forall_fin_zero] <;> decide

theorem nonzero_W : W 0 0 = 1 ∧ W 1 0 = 3 := by decide

theorem nontrivial_residual :
    matSub (eye 2) (matMul P Q) 0 0 = -2 ∧
    matSub (eye 2) (matMul P Q) 0 1 = 1 ∧
    matSub (eye 2) (matMul P Q) 1 0 = -6 ∧
    matSub (eye 2) (matMul P Q) 1 1 = 3 := by decide

-- Flip the witness sign while retaining MP = 0 and QP = I.
def wrongW : Mat 2 1 := fun i r => -(W i r)

theorem wrongW_rejected : ¬ MatrixIdentities M P Q wrongW := by
  intro h
  have hc := congrArg (fun A : Mat 2 2 => A 0 0) h.residual
  change (-2 : Int) = 2 at hc
  exact (by decide : (-2 : Int) ≠ 2) hc

-- Drop MP: the other two identities can hold while MP fails.
def scalarOne : Mat 1 1 := fun _ _ => 1
def scalarZero : Mat 1 1 := fun _ _ => 0

theorem missingMP_other_two :
    matMul scalarOne scalarOne = eye 1 ∧
    matSub (eye 1) (matMul scalarOne scalarOne) =
      matMul scalarZero scalarOne := by
  constructor
  · funext i j
    revert i j
    simp only [Fin.forall_fin_succ, Fin.forall_fin_zero] <;> decide
  · funext i j
    revert i j
    simp only [Fin.forall_fin_succ, Fin.forall_fin_zero] <;> decide

theorem missingMP_rejected :
    ¬ MatrixIdentities scalarOne scalarOne scalarOne scalarZero := by
  intro h
  have hc := congrArg (fun A : Mat 1 1 => A 0 0) h.mp
  change (1 : Int) = 0 at hc
  exact (by decide : (1 : Int) ≠ 0) hc

-- Drop QP: MP and the residual identity do not imply surjectivity.
theorem missingQP_other_two :
    matMul scalarOne scalarZero = zeroMat 1 1 ∧
    matSub (eye 1) (matMul scalarZero scalarZero) =
      matMul scalarOne scalarOne := by
  constructor
  · funext i j
    revert i j
    simp only [Fin.forall_fin_succ, Fin.forall_fin_zero] <;> decide
  · funext i j
    revert i j
    simp only [Fin.forall_fin_succ, Fin.forall_fin_zero] <;> decide

theorem missingQP_rejected :
    ¬ MatrixIdentities scalarOne scalarZero scalarZero scalarOne := by
  intro h
  have hc := congrArg (fun A : Mat 1 1 => A 0 0) h.qp
  change (0 : Int) = 1 at hc
  exact (by decide : (0 : Int) ≠ 1) hc

theorem fin_one (i : Fin 1) : i = 0 := by
  apply Fin.eq_of_val_eq
  omega

-- A lawful multiplicative-group interface whose operation is integer addition.
-- It is NOT a field, nor claimed to be a field/unit API instantiation.
def signedAddGroup : CommGroup Int where
  one := 0
  mul := (· + ·)
  inv := Neg.neg
  mul_assoc := Int.add_assoc
  one_mul := Int.zero_add
  mul_one := Int.add_zero
  mul_comm := Int.add_comm
  inv_mul := Int.add_left_neg
  mul_inv := Int.add_right_neg

def signedPoint : Fin 2 → Int := fun i => if i.val = 0 then 5 else 10

theorem negative_power_numeric : signedAddGroup.zpow 5 (-3) = -15 := by decide

theorem signed_relation : MonomialBridge.Relations signedAddGroup M signedPoint := by
  intro r
  have hr := fin_one r
  subst r
  decide

theorem signed_parameter :
    MonomialBridge.parameters signedAddGroup Q signedPoint 0 = 5 := by decide

theorem signed_reconstruction :
    signedPoint = MonomialBridge.realization signedAddGroup P
      (MonomialBridge.parameters signedAddGroup Q signedPoint) :=
  MonomialBridge.reconstruction signedAddGroup fixtureIdentities signedPoint signed_relation

def wrongQ : Mat 1 2 := fun _ j => if j.val = 0 then 3 else 1

theorem wrong_parameter_sign :
    MonomialBridge.parameters signedAddGroup wrongQ signedPoint 0 ≠ 5 := by decide

-- A torsion group: XOR on Bool. This checks a case with no root uniqueness.
def xorGroup : CommGroup Bool where
  one := false
  mul := Bool.xor
  inv := fun a => a
  mul_assoc := by intro a b c; cases a <;> cases b <;> cases c <;> rfl
  one_mul := by intro a; cases a <;> rfl
  mul_one := by intro a; cases a <;> rfl
  mul_comm := by intro a b; cases a <;> cases b <;> rfl
  inv_mul := by intro a; cases a <;> rfl
  mul_inv := by intro a; cases a <;> rfl

def torsionPoint : Fin 2 → Bool := fun i => i.val == 0

theorem torsion_relation : MonomialBridge.Relations xorGroup M torsionPoint := by
  intro r
  have hr := fin_one r
  subst r
  decide

theorem torsion_reconstruction :
    torsionPoint = MonomialBridge.realization xorGroup P
      (MonomialBridge.parameters xorGroup Q torsionPoint) :=
  MonomialBridge.reconstruction xorGroup fixtureIdentities torsionPoint torsion_relation


/-! Repair regressions: these call the repaired public interfaces, rather than
    substituting numerical checks for the universal proof obligations. -/

theorem repeated_addition_step (n : Nat) (a : Int) :
    intGroup.nsmul (n + 1) a = intGroup.add (intGroup.nsmul n a) a := rfl

theorem synthetic_kernel (v : Row 2) :
    MatrixBridge.Lattice (M := M) v ↔ rowMul v P = (rowGroup 1).zero :=
  MatrixBridge.lattice_eq_kernel fixtureIdentities v

theorem synthetic_surjectivity :
    ∀ z : Row 1, ∃ v : Row 2, rowMul v P = z :=
  MatrixBridge.phi_surjective fixtureIdentities

theorem synthetic_quotient_roundtrip
    (x : (matrixRetraction fixtureIdentities).LQuot) :
    (MatrixBridge.quotientIso fixtureIdentities).backward.run
      ((MatrixBridge.quotientIso fixtureIdentities).forward.run x) = x :=
  MatrixBridge.quotient_left_inverse fixtureIdentities x

theorem synthetic_parameter_roundtrip (z : Row 1) :
    (MatrixBridge.quotientIso fixtureIdentities).forward.run
      ((MatrixBridge.quotientIso fixtureIdentities).backward.run z) = z :=
  MatrixBridge.quotient_right_inverse fixtureIdentities z

theorem synthetic_saturation (k : Int) (hk : k ≠ 0) (v : Row 2)
    (hv : MatrixBridge.Lattice (M := M) (scale k v)) :
    MatrixBridge.Lattice (M := M) v :=
  MatrixBridge.lattice_saturated fixtureIdentities k hk v hv

theorem signed_all_exponents (v : Row 2) :
    monomial signedAddGroup signedPoint v =
      monomial signedAddGroup
        (MonomialBridge.parameters signedAddGroup Q signedPoint) (rowMul v P) :=
  MonomialBridge.reconstruction_all_exponents
    signedAddGroup fixtureIdentities signedPoint signed_relation v

theorem signed_converse (theta : Fin 1 → Int) :
    MonomialBridge.Relations signedAddGroup M
      (MonomialBridge.realization signedAddGroup P theta) :=
  MonomialBridge.converse_relations signedAddGroup fixtureIdentities theta

theorem signed_recovery (theta : Fin 1 → Int) :
    MonomialBridge.parameters signedAddGroup Q
      (MonomialBridge.realization signedAddGroup P theta) = theta :=
  MonomialBridge.parameters_recover signedAddGroup fixtureIdentities theta

theorem signed_residual_product (x : Fin 2 → Int) (i : Fin 2) :
    signedAddGroup.div (x i)
      (monomial signedAddGroup (MonomialBridge.parameters signedAddGroup Q x) (P i)) =
      signedAddGroup.prod 1
        (fun r => signedAddGroup.zpow (monomial signedAddGroup x (M r)) (W i r)) :=
  MonomialBridge.residual_relations_formula signedAddGroup fixtureIdentities x i

end PR1497.Fixtures

/-! ## Complete axiom-query inventory (output requires actual Lean replay). -/
set_option pp.fullNames true
#print axioms PR1497.Fixtures.M
#print axioms PR1497.Fixtures.P
#print axioms PR1497.Fixtures.Q
#print axioms PR1497.Fixtures.W
#print axioms PR1497.Fixtures.fixtureIdentities
#print axioms PR1497.Fixtures.nonzero_W
#print axioms PR1497.Fixtures.nontrivial_residual
#print axioms PR1497.Fixtures.wrongW
#print axioms PR1497.Fixtures.wrongW_rejected
#print axioms PR1497.Fixtures.scalarOne
#print axioms PR1497.Fixtures.scalarZero
#print axioms PR1497.Fixtures.missingMP_other_two
#print axioms PR1497.Fixtures.missingMP_rejected
#print axioms PR1497.Fixtures.missingQP_other_two
#print axioms PR1497.Fixtures.missingQP_rejected
#print axioms PR1497.Fixtures.fin_one
#print axioms PR1497.Fixtures.signedAddGroup
#print axioms PR1497.Fixtures.signedPoint
#print axioms PR1497.Fixtures.negative_power_numeric
#print axioms PR1497.Fixtures.signed_relation
#print axioms PR1497.Fixtures.signed_parameter
#print axioms PR1497.Fixtures.signed_reconstruction
#print axioms PR1497.Fixtures.wrongQ
#print axioms PR1497.Fixtures.wrong_parameter_sign
#print axioms PR1497.Fixtures.xorGroup
#print axioms PR1497.Fixtures.torsionPoint
#print axioms PR1497.Fixtures.torsion_relation
#print axioms PR1497.Fixtures.torsion_reconstruction
#print axioms PR1497.Fixtures.repeated_addition_step
#print axioms PR1497.Fixtures.synthetic_kernel
#print axioms PR1497.Fixtures.synthetic_surjectivity
#print axioms PR1497.Fixtures.synthetic_quotient_roundtrip
#print axioms PR1497.Fixtures.synthetic_parameter_roundtrip
#print axioms PR1497.Fixtures.synthetic_saturation
#print axioms PR1497.Fixtures.signed_all_exponents
#print axioms PR1497.Fixtures.signed_converse
#print axioms PR1497.Fixtures.signed_recovery
#print axioms PR1497.Fixtures.signed_residual_product
