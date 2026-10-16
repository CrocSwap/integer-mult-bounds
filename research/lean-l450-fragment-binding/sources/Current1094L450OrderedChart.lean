import Current1094DecodedRouteLookup
import Mathlib.Data.ZMod.Basic
import Mathlib.LinearAlgebra.Pi
import Init.Data.Nat.Bitwise.Lemmas

/-!
Source-only binary chart construction for selected call000 ordinary L450,
borrowed helper226, family10216. The exact decoded route is narrow child2,
offset0, width7, ordered spectators[0,8]. Its literal ACTUAL-SIGMAS columns
are [386,4,8,16,32,64,259,385,131] followed by2^9 through2^72.

We factor these columns into the coordinate permutation
[0,2,3,4,5,6,7,1,8,9,...,72] followed by the even-support transvection387.
A finite73-column identity binds the integer serialization. LinearMap.pi_ext
then proves equality on every address using arbitrary scalar coefficients;
no all-payload conclusion is inferred from nine sampled vectors.
The two inverse directions and arbitrary-payload pullback are derived.

This constructs the binary source model. The emitter does not select whether
an actual physical executor uses this pullback or its inverse, nor does it
specify a complex phase in the column array. Residual2:999 right offset511 /
phase1 and left offset0 / phase0 remain distinct serialized recipe data.
No Hosting.chart, RecipesExact, actual executor, rounding, cost or full
multiplication theorem is supplied. The source-matched conditional context is
kappa=836330098538459/500000000000000000=0.001672660197076918.

Attribution: Rohan Arun PR1094; Jeremy Kothe's selected T16/hyperplane-ended
emitter; Hao Yan PR514/484/507 lineage; the accepted bank route decoder;
Mathlib finite-product linear-map and equivalence infrastructure. Apache-2.0.
Prepared with OpenAI assistance. UNCOMPILED candidate.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.Current1094L450OrderedChart

abbrev Coordinate := Fin 73
abbrev Address := Coordinate → ZMod 2

/-- Retains the exact constructor field order from the accepted decoder. -/
theorem selected_route :
    Current1094DecodedRouteLookup.decodedRowAt
      (Current1094SourceRoutes.selectedDecodedOwners 0) 450 =
    (⟨10216, Current1094OwnerDeclarationDecoder.Route.narrow 2 0 7 [0,8]⟩ :
      Current1094OwnerDeclarationDecoder.OwnerRow) :=
  Current1094DecodedRouteLookup.call000_L450_decoded

/-- Serialized columns, including all64 higher coordinate columns. -/
def sourceColumn (j : Coordinate) : Nat :=
  match j.val with
  | 0 => 386 | 1 => 4 | 2 => 8 | 3 => 16 | 4 => 32
  | 5 => 64 | 6 => 259 | 7 => 385 | 8 => 131
  | n => 2 ^ n

def bits (n : Nat) : Address := fun i => if n.testBit i.val then 1 else 0

theorem bits_xor (a b : Nat) : bits (a ^^^ b) = bits a + bits b := by
  funext i
  simp only [bits, Nat.testBit_xor, Pi.add_apply]
  cases a.testBit i.val <;> cases b.testBit i.val <;> decide +kernel

theorem bits_two_pow (j : Coordinate) : bits (2 ^ j.val) = Pi.single j 1 := by
  funext i
  simp [bits, Nat.testBit_two_pow, Pi.single_apply, Fin.ext_iff, eq_comm]

def u : Address :=
  Pi.single 0 1 + Pi.single 1 1 + Pi.single 7 1 + Pi.single 8 1

theorem bits_387 : bits 387 = u := by decide +kernel

def parity : Address →ₗ[ZMod 2] ZMod 2 :=
  (LinearMap.proj (0 : Coordinate) : Address →ₗ[ZMod 2] ZMod 2) +
  (LinearMap.proj (1 : Coordinate) : Address →ₗ[ZMod 2] ZMod 2) +
  (LinearMap.proj (7 : Coordinate) : Address →ₗ[ZMod 2] ZMod 2) +
  (LinearMap.proj (8 : Coordinate) : Address →ₗ[ZMod 2] ZMod 2)

private theorem parity_u : parity u = 0 := by decide +kernel

/-- The support has even cardinality, so its transvection is self-inverse. -/
def transvection : Address →ₗ[ZMod 2] Address :=
  LinearMap.id + parity.smulRight u

private theorem transvection_apply (x : Address) :
    transvection x = x + parity x • u := rfl

theorem transvection_involutive : Function.Involutive transvection := by
  intro x
  change (x + parity x • u) + parity (x + parity x • u) • u = x
  rw [map_add, map_smul, parity_u, smul_zero, add_zero,
    add_assoc, ZModModule.add_self, add_zero]

def reflection : Address ≃ₗ[ZMod 2] Address :=
  LinearEquiv.ofInvolutive transvection transvection_involutive

/-- j maps to the ambient standard-basis coordinate before the transvection. -/
def axis : Equiv.Perm Coordinate :=
  (((((Equiv.swap 6 7).trans (Equiv.swap 5 6)).trans (Equiv.swap 4 5)).trans
    (Equiv.swap 3 4)).trans (Equiv.swap 2 3)).trans (Equiv.swap 1 2)

def reorder : Address ≃ₗ[ZMod 2] Address where
  toFun x i := x (axis.symm i)
  invFun x i := x (axis i)
  left_inv := by intro x; funext i; simp
  right_inv := by intro x; funext i; simp
  map_add' := by intro x y; rfl
  map_smul' := by intro a x; rfl

private theorem reorder_apply (x : Address) (i : Coordinate) :
    reorder x i = x (axis.symm i) := rfl

private theorem reorder_single (j : Coordinate) :
    reorder (Pi.single j 1) = Pi.single (axis j) 1 := by
  funext i
  simp only [reorder_apply, Pi.single_apply, Equiv.symm_apply_eq]

def supported (j : Coordinate) : Prop := j = 0 ∨ j = 1 ∨ j = 7 ∨ j = 8
instance (j : Coordinate) : Decidable (supported j) := by
  unfold supported
  infer_instance

private theorem parity_single (j : Coordinate) :
    parity (Pi.single j 1) = if supported j then 1 else 0 := by
  by_cases h0 : j = 0
  · subst j; simp [parity, LinearMap.proj_apply, supported]
  by_cases h1 : j = 1
  · subst j; simp [parity, LinearMap.proj_apply, supported]
  by_cases h7 : j = 7
  · subst j; simp [parity, LinearMap.proj_apply, supported]
  by_cases h8 : j = 8
  · subst j; simp [parity, LinearMap.proj_apply, supported]
  simp [parity, LinearMap.proj_apply, Pi.single_apply, supported, h0, h1, h7, h8,
    eq_comm]

def factorColumn (j : Coordinate) : Nat :=
  if supported (axis j) then (2 ^ (axis j).val) ^^^ 387 else 2 ^ (axis j).val

/-- Exactly73 small integer/coordinate reductions; no matrix or payload census. -/
theorem all_columns_factor : ∀ j : Coordinate, sourceColumn j = factorColumn j := by
  decide +kernel

def addressEquiv : Address ≃ₗ[ZMod 2] Address := reorder.trans reflection

theorem column_action (j : Coordinate) :
    bits (sourceColumn j) = addressEquiv (Pi.single j 1) := by
  rw [all_columns_factor]
  change bits (factorColumn j) = reflection (reorder (Pi.single j 1))
  rw [reorder_single]
  change bits (factorColumn j) = transvection (Pi.single (axis j) 1)
  rw [transvection_apply, parity_single]
  by_cases h : supported (axis j)
  · simp only [factorColumn, h, if_true, bits_xor, bits_387, bits_two_pow, one_smul]
  · simp only [factorColumn, h, if_false, bits_two_pow, zero_smul, add_zero]

/-- Independent linear interpretation of the complete literal column array. -/
def sourceLinear : Address →ₗ[ZMod 2] Address :=
  LinearMap.lsum (ZMod 2) (fun _ : Coordinate => ZMod 2) (ZMod 2)
    (fun j => (LinearMap.id : ZMod 2 →ₗ[ZMod 2] ZMod 2).smulRight (bits (sourceColumn j)))

private theorem sourceLinear_single (j : Coordinate) (a : ZMod 2) :
    sourceLinear (Pi.single j a) = a • bits (sourceColumn j) := by
  rw [sourceLinear, LinearMap.lsum_piSingle]
  rfl

/-- Coefficient completeness extends the bound columns to every73-bit address. -/
theorem sourceLinear_eq : sourceLinear = addressEquiv.toLinearMap := by
  apply LinearMap.pi_ext
  intro j a
  have hs : Pi.single j a = a • (Pi.single j 1 : Address) := by
    rw [← Pi.single_smul']
    simp
  rw [hs]
  simp only [map_smul]
  apply congrArg (fun x : Address => a • x)
  rw [sourceLinear_single, one_smul]
  exact column_action j

def sourceAddress (x : Address) : Address := sourceLinear x

def inverseAddress (x : Address) : Address := addressEquiv.symm x

theorem inverse_source (x : Address) : inverseAddress (sourceAddress x) = x := by
  unfold sourceAddress inverseAddress
  rw [sourceLinear_eq]
  exact addressEquiv.symm_apply_apply x

theorem source_inverse (x : Address) : sourceAddress (inverseAddress x) = x := by
  unfold sourceAddress inverseAddress
  rw [sourceLinear_eq]
  exact addressEquiv.apply_symm_apply x

section Payload
variable (K : Type*) [Semiring K]

/-- Explicit pullback convention, with its inverse derived. Actual Hosting
must separately select/bind a direction and any complex phase. -/
def sourcePullback : (Address → K) ≃ₗ[K] (Address → K) where
  toFun f x := f (sourceAddress x)
  invFun f x := f (inverseAddress x)
  left_inv := by
    intro f; funext x
    change f (sourceAddress (inverseAddress x)) = f x
    rw [source_inverse]
  right_inv := by
    intro f; funext x
    change f (inverseAddress (sourceAddress x)) = f x
    rw [inverse_source]
  map_add' := by intro f g; rfl
  map_smul' := by intro a f; rfl

/-- Arbitrary payloads and every spectator fiber, not selected test values. -/
theorem pullback_inverse (f : Address → K) :
    (sourcePullback K).symm (sourcePullback K f) = f :=
  (sourcePullback K).symm_apply_apply f

end Payload
end CurrentMain.Current1094L450OrderedChart

#print axioms CurrentMain.Current1094L450OrderedChart.selected_route
#print axioms CurrentMain.Current1094L450OrderedChart.all_columns_factor
#print axioms CurrentMain.Current1094L450OrderedChart.transvection_involutive
#print axioms CurrentMain.Current1094L450OrderedChart.column_action
#print axioms CurrentMain.Current1094L450OrderedChart.sourceLinear_eq
#print axioms CurrentMain.Current1094L450OrderedChart.inverse_source
#print axioms CurrentMain.Current1094L450OrderedChart.source_inverse
#print axioms CurrentMain.Current1094L450OrderedChart.pullback_inverse
#check @CurrentMain.Current1094L450OrderedChart.sourceLinear_eq
