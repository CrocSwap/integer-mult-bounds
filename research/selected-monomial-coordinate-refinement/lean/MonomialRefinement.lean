import TensorLift
import SelectedRecipe
import Mathlib.Tactic

/-!
Source-faithful coordinate refinement of PR2250's selected monomial staging.
The Compact/digit-permutation operations have an explicit completed endpoint
contract.  Their tape implementation, time bound and integer word encoding
are not axioms silently discharged by this module: they remain external
physical obligations.  The formal statements operate on full coordinate
arrays, with arbitrary dirty spectator coordinates.

The unchanged CommonLabelTensor coordinates are from Gareth Davidson's
PR2341, and the selected compiler and staging from Jose Manuel's PR2250.
Prepared with substantial OpenAI Codex assistance. Apache-2.0.
-/

open scoped TensorProduct

namespace SelectedMonomial

section PrimitiveContract

variable {P S J : Type*}

/-- Spaced selected bits and all remaining address data are decoded by this
equivalence.  The spectator component includes every dirty compact field. -/
def columnStep (g : Gate) (z : S × (J → Address)) : S × (J → Address) :=
  (z.1, fun j => gate g (z.2 j))

def physicalRun (step : Gate → P → P) : List Gate → P → P
  | [], p => p
  | g :: gs, p => physicalRun step gs (step g p)

/-- This is the completed Compact/digit-permutation contract, not an assumption
that the entire 22-operation word already has the desired endpoint.  Only
primitive gates actually occurring in the selected word are required. -/
def CompletedPrimitive (decode : P ≃ S × (J → Address))
    (step : Gate → P → P) : Prop :=
  ∀ g ∈ word, ∀ p, decode (step g p) = columnStep g (decode p)

theorem primitive_word (decode : P ≃ S × (J → Address))
    (step : Gate → P → P) (hstep : CompletedPrimitive decode step)
    (gs : List Gate) (hgs : ∀ g ∈ gs, g ∈ word) (p : P) :
    decode (physicalRun step gs p) =
      ((decode p).1, fun j => runAddress gs ((decode p).2 j)) := by
  induction gs generalizing p with
  | nil => rfl
  | cons g gs ih =>
    have hg : g ∈ word := hgs g (by simp)
    have htail : ∀ k ∈ gs, k ∈ word := by
      intro k hk
      exact hgs k (by simp [hk])
    rw [physicalRun, ih htail, hstep g hg]
    rfl

theorem selected_word (decode : P ≃ S × (J → Address))
    (step : Gate → P → P) (hstep : CompletedPrimitive decode step) (p : P) :
    decode (physicalRun step word p) =
      ((decode p).1, fun j => sigma ((decode p).2 j)) :=
  primitive_word decode step hstep word (by intro g hg; exact hg) p

theorem selected_inverse_word (decode : P ≃ S × (J → Address))
    (step : Gate → P → P) (hstep : CompletedPrimitive decode step) (p : P) :
    decode (physicalRun step word.reverse p) =
      ((decode p).1, fun j => sigma.symm ((decode p).2 j)) :=
  primitive_word decode step hstep word.reverse
    (by intro g hg; simpa only [List.mem_reverse] using hg) p

theorem spectator_fixed (decode : P ≃ S × (J → Address))
    (step : Gate → P → P) (hstep : CompletedPrimitive decode step) (p : P) :
    (decode (physicalRun step word p)).1 = (decode p).1 := by
  rw [selected_word decode step hstep]

end PrimitiveContract

section CoordinateSemantics

variable {R A J : Type*} [CommSemiring R] [Fintype J]

def unary (σ : A ≃ A) (μ : A → Rˣ) : (A → R) →ₗ[R] (A → R) where
  toFun h y := (μ (σ.symm y) : R) * h (σ.symm y)
  map_add' h k := by funext y; simp [mul_add]
  map_smul' c h := by funext y; simp [mul_left_comm]

def phases (μ : A → Rˣ) (x : J → A) : Rˣ := ∏ j, μ (x j)

/-- The physical phase scan occurs on input columns, before address movement. -/
def phasePass (μ : A → Rˣ) (h : (J → A) → R) (x : J → A) : R :=
  (phases μ x : R) * h x

def affinePass (σ : A ≃ A) (h : (J → A) → R) (y : J → A) : R :=
  h (fun j => σ.symm (y j))

def forward (σ : A ≃ A) (μ : A → Rˣ) (h : (J → A) → R) : (J → A) → R :=
  affinePass σ (phasePass μ h)

/-- Undo affine addresses first, then negate the phase on recovered inputs. -/
def backward (σ : A ≃ A) (μ : A → Rˣ) (h : (J → A) → R) : (J → A) → R :=
  phasePass (fun x => (μ x)⁻¹) (affinePass σ.symm h)

theorem forward_formula (σ : A ≃ A) (μ : A → Rˣ) (h : (J → A) → R) (y : J → A) :
    forward σ μ h y =
      (phases μ (fun j => σ.symm (y j)) : R) * h (fun j => σ.symm (y j)) := rfl

theorem phases_inverse (μ : A → Rˣ) (x : J → A) :
    phases (fun a => (μ a)⁻¹) x = (phases μ x)⁻¹ := by
  simp [phases]

theorem backward_forward (σ : A ≃ A) (μ : A → Rˣ) (h : (J → A) → R) :
    backward σ μ (forward σ μ h) = h := by
  funext x
  simp [backward, forward, phasePass, affinePass, phases_inverse]

theorem forward_backward (σ : A ≃ A) (μ : A → Rˣ) (h : (J → A) → R) :
    forward σ μ (backward σ μ h) = h := by
  funext x
  simp [backward, forward, phasePass, affinePass, phases_inverse]

def coordinateLinear (σ : A ≃ A) (μ : A → Rˣ) :
    ((J → A) → R) →ₗ[R] ((J → A) → R) where
  toFun := forward σ μ
  map_add' h k := by funext y; simp [forward, affinePass, phasePass, mul_add]
  map_smul' c h := by
    funext y
    simp [forward, affinePass, phasePass, mul_left_comm]

variable [Fintype A]

/-- Concrete monomial coordinate action agrees with the tensor linear map on
every full array.  No decomposability assumption appears in the statement. -/
theorem tensor_coordinates (σ : A ≃ A) (μ : A → Rˣ)
    (h : (J → A) → R) :
    CommonLabelTensor.coordinates (fun _ : J => A)
        (PiTensorProduct.map (fun _ : J => unary σ μ)
          ((CommonLabelTensor.coordinates (R := R) (fun _ : J => A)).symm h)) =
      forward σ μ h := by
  classical
  let c := CommonLabelTensor.coordinates (R := R) (fun _ : J => A)
  have hm : c.toLinearMap.comp (PiTensorProduct.map (fun _ : J => unary σ μ)) =
      (coordinateLinear σ μ).comp c.toLinearMap := by
    apply PiTensorProduct.ext
    apply DFunLike.ext
    intro v
    change c ((PiTensorProduct.map (fun _ : J => unary σ μ))
        (PiTensorProduct.tprod R v)) =
      coordinateLinear σ μ (c (PiTensorProduct.tprod R v))
    funext y
    change c ((PiTensorProduct.map (fun _ : J => unary σ μ))
        (PiTensorProduct.tprod R v)) y =
      (phases μ (fun j => σ.symm (y j)) : R) *
        c (PiTensorProduct.tprod R v) (fun j => σ.symm (y j))
    simp only [PiTensorProduct.map_tprod, c, CommonLabelTensor.coordinates_tprod]
    change (∏ j, (μ (σ.symm (y j)) : R) * v j (σ.symm (y j))) =
      (phases μ (fun j => σ.symm (y j)) : R) * ∏ j, v j (σ.symm (y j))
    simp [phases, Finset.prod_mul_distrib]
  change c ((PiTensorProduct.map (fun _ : J => unary σ μ)) (c.symm h)) = forward σ μ h
  calc
    _ = coordinateLinear σ μ (c (c.symm h)) := DFunLike.congr_fun hm (c.symm h)
    _ = forward σ μ h := by rw [c.apply_symm_apply]; rfl

/-- An arbitrary spectator-indexed family may be correlated across columns
and spectators.  The operation acts separately on each unchanged spectator. -/
theorem tensor_coordinates_with_spectators {S : Type*} (σ : A ≃ A) (μ : A → Rˣ)
    (h : S → (J → A) → R) (s : S) :
    CommonLabelTensor.coordinates (fun _ : J => A)
        (PiTensorProduct.map (fun _ : J => unary σ μ)
          ((CommonLabelTensor.coordinates (R := R) (fun _ : J => A)).symm (h s))) =
      forward σ μ (h s) := tensor_coordinates σ μ (h s)

end CoordinateSemantics

section SelectedPhase

variable {R : Type*} [CommSemiring R]

def selectedPhase (ζ : Rˣ) (x : Address) : Rˣ := ζ ^ (2 + q x)

theorem selected_phase_product (ζ : Rˣ) (f : Nat) (x : Fin f → Address) :
    phases (selectedPhase ζ) x = ζ ^ (2 * f + ∑ j, q (x j)) := by
  classical
  have hp : ∀ s : Finset (Fin f),
      (∏ j ∈ s, ζ ^ (2 + q (x j))) = ζ ^ (∑ j ∈ s, (2 + q (x j))) := by
    intro s
    induction s using Finset.induction_on with
    | empty => simp
    | @insert a s ha ih =>
      rw [Finset.prod_insert ha, Finset.sum_insert ha, ih]
      exact (pow_add _ _ _).symm
  simpa [phases, selectedPhase, Finset.sum_add_distrib, Nat.mul_comm] using hp Finset.univ

theorem pow_mod_four (ζ : Rˣ) (hζ : ζ ^ 4 = 1) (n : Nat) : ζ ^ n = ζ ^ (n % 4) := by
  calc
    ζ ^ n = ζ ^ (n % 4 + 4 * (n / 4)) := by congr 1; omega
    _ = ζ ^ (n % 4) := by simp [pow_add, pow_mul, hζ]

theorem selected_phase_mod_four (ζ : Rˣ) (hζ : ζ ^ 4 = 1)
    (f : Nat) (x : Fin f → Address) :
    phases (selectedPhase ζ) x = ζ ^ ((2 * f + ∑ j, q (x j)) % 4) := by
  rw [selected_phase_product, pow_mod_four ζ hζ]

theorem selected_full_array (ζ : Rˣ) (f : Nat)
    (h : (Fin f → Address) → R) :
    CommonLabelTensor.coordinates (fun _ : Fin f => Address)
        (PiTensorProduct.map (fun _ : Fin f => unary sigma (selectedPhase ζ))
          ((CommonLabelTensor.coordinates (R := R) (fun _ : Fin f => Address)).symm h)) =
      forward sigma (selectedPhase ζ) h := tensor_coordinates sigma (selectedPhase ζ) h

end SelectedPhase

section PhysicalTensor

variable {R P S : Type*} [CommSemiring R] {f : Nat}

/-- A completed phase pass on the original physical coordinates.  Exact word
encoding of multiplication by a fourth root of unity remains an external
obligation, just as the completed permutation endpoint does. -/
def physicalPhase (ζ : Rˣ) (decode : P ≃ S × (Fin f → Address))
    (h : P → R) (p : P) : R :=
  (phases (selectedPhase ζ) (decode p).2 : R) * h p

/-- Forward data movement scatters by the literal affine word, hence its
coefficient action pulls back by the literal reversed word after phasing. -/
def physicalForward (ζ : Rˣ) (decode : P ≃ S × (Fin f → Address))
    (step : Gate → P → P) (h : P → R) (p : P) : R :=
  physicalPhase ζ decode h (physicalRun step word.reverse p)

/-- Undo affine movement first; only then undo the phase at the recovered
input address.  It is deliberately not phase inversion at the output address. -/
def physicalBackward (ζ : Rˣ) (decode : P ≃ S × (Fin f → Address))
    (step : Gate → P → P) (h : P → R) (p : P) : R :=
  (↑((phases (selectedPhase ζ) (decode p).2)⁻¹) : R) *
    h (physicalRun step word p)

theorem selected_physical_roundtrip (decode : P ≃ S × (Fin f → Address))
    (step : Gate → P → P) (hstep : CompletedPrimitive decode step) (p : P) :
    physicalRun step word.reverse (physicalRun step word p) = p := by
  apply decode.injective
  rw [selected_inverse_word decode step hstep, selected_word decode step hstep]
  simp

theorem selected_physical_reverse_roundtrip (decode : P ≃ S × (Fin f → Address))
    (step : Gate → P → P) (hstep : CompletedPrimitive decode step) (p : P) :
    physicalRun step word (physicalRun step word.reverse p) = p := by
  apply decode.injective
  rw [selected_word decode step hstep, selected_inverse_word decode step hstep]
  simp

theorem physical_backward_forward (ζ : Rˣ)
    (decode : P ≃ S × (Fin f → Address)) (step : Gate → P → P)
    (hstep : CompletedPrimitive decode step) (h : P → R) :
    physicalBackward ζ decode step (physicalForward ζ decode step h) = h := by
  funext p
  simp only [physicalBackward, physicalForward, physicalPhase,
    selected_physical_roundtrip decode step hstep]
  simp [← mul_assoc]

theorem physical_forward_backward (ζ : Rˣ)
    (decode : P ≃ S × (Fin f → Address)) (step : Gate → P → P)
    (hstep : CompletedPrimitive decode step) (h : P → R) :
    physicalForward ζ decode step (physicalBackward ζ decode step h) = h := by
  funext p
  simp only [physicalForward, physicalPhase, physicalBackward,
    selected_physical_reverse_roundtrip decode step hstep]
  simp [← mul_assoc]

/-- The completed literal primitive sequence, phase before affine movement,
refines the tensor map on every physical coefficient array.  Arbitrary dirty
spectators are represented by S and retained without a separability premise. -/
theorem physical_tensor_refinement (ζ : Rˣ)
    (decode : P ≃ S × (Fin f → Address)) (step : Gate → P → P)
    (hstep : CompletedPrimitive decode step) (h : P → R) (p : P) :
    physicalForward ζ decode step h p =
      CommonLabelTensor.coordinates (fun _ : Fin f => Address)
        (PiTensorProduct.map (fun _ : Fin f => unary sigma (selectedPhase ζ))
          ((CommonLabelTensor.coordinates (R := R) (fun _ : Fin f => Address)).symm
            (fun x => h (decode.symm ((decode p).1, x))))) (decode p).2 := by
  rw [selected_full_array]
  have hp : physicalRun step word.reverse p =
      decode.symm ((decode p).1, fun j => sigma.symm ((decode p).2 j)) := by
    apply decode.injective
    rw [Equiv.apply_symm_apply]
    exact selected_inverse_word decode step hstep p
  simp only [physicalForward, physicalPhase, hp, Equiv.apply_symm_apply,
    forward, affinePass, phasePass]

end PhysicalTensor

end SelectedMonomial
