import MonomialRefinement
import PhaseWords
import Mathlib.Data.Complex.Basic

/-!
Compose PR2378's unchanged bit-word and coordinate theorems for every payload
field. Physical address primitives and the source/model correspondence remain
explicit boundaries. Gareth Davidson / OpenAI Codex, Apache-2.0.
-/

open scoped TensorProduct
open SelectedMonomial SelectedPhaseWords

namespace RecordPhaseBridge

abbrev WordPair := List Bool × List Bool

def gaussianValue (z : ℤ × ℤ) : ℂ := (z.1 : ℂ) + (z.2 : ℂ) * Complex.I
def decoded (z : WordPair) : ℂ := gaussianValue (decodePair z)

def scalar : Phase → ℂ
  | .one => 1
  | .imag => Complex.I
  | .minusOne => -1
  | .minusImag => -Complex.I

noncomputable def iUnit : ℂˣ := Units.mk0 Complex.I Complex.I_ne_zero

theorem iUnit_four : iUnit ^ 4 = 1 := by
  apply Units.ext
  simpa [iUnit] using Complex.I_pow_four

def Fits (w : Nat) (p : Phase) (z : WordPair) : Prop :=
  z.1.length = w + 1 ∧ z.2.length = w + 1 ∧
    phaseHeadroom p ((2 : ℤ) ^ w) (unsigned z.1) (unsigned z.2)

/-- The predecessor's signed-pair theorem, embedded into the coefficient field. -/
theorem decoded_rotate (w : Nat) (p : Phase) (z : WordPair) (h : Fits w p z) :
    decoded (rotateWords p z.1 z.2) = scalar p * decoded z := by
  unfold decoded
  rw [rotateWords_refines w p z.1 z.2 h.1 h.2.1 h.2.2]
  cases p <;> simp [gaussianValue, decodePair, rotateIntegers, scalar] <;>
    ring_nf <;> simp [Complex.I_sq]

theorem scalar_nat (k : Nat) : scalar (phaseOfNat k) = ((iUnit ^ k : ℂˣ) : ℂ) := by
  rw [SelectedMonomial.pow_mod_four iUnit iUnit_four k]
  have hm : k % 4 = 0 ∨ k % 4 = 1 ∨ k % 4 = 2 ∨ k % 4 = 3 := by omega
  rcases hm with h | h | h | h <;>
    simp [phaseOfNat, scalar, h, iUnit, pow_succ, Complex.I_mul_I]

theorem scalar_inverse_nat (k : Nat) :
    scalar (inversePhase (phaseOfNat k)) = (((iUnit ^ k)⁻¹ : ℂˣ) : ℂ) := by
  rw [SelectedMonomial.pow_mod_four iUnit iUnit_four k]
  have hm : k % 4 = 0 ∨ k % 4 = 1 ∨ k % 4 = 2 ∨ k % 4 = 3 := by omega
  rcases hm with h | h | h | h <;>
    simp [phaseOfNat, inversePhase, scalar, h, iUnit, pow_succ, Complex.I_mul_I, Complex.inv_I]

/-- Every Gaussian coefficient field is visited; no distinguished first field. -/
def scan (k : Nat) (record : List WordPair) : List WordPair :=
  record.map (fun z => rotateWords (phaseOfNat k) z.1 z.2)

theorem scan_length (k : Nat) (record : List WordPair) : (scan k record).length = record.length := by
  simp [scan]

theorem decode_scan (w k : Nat) (record : List WordPair)
    (h : ∀ z ∈ record, Fits w (phaseOfNat k) z) :
    (scan k record).map decoded = record.map (fun z => ((iUnit ^ k : ℂˣ) : ℂ) * decoded z) := by
  simp only [scan, List.map_map]
  apply List.map_congr_left
  intro z hz
  rw [Function.comp_apply, decoded_rotate w _ z (h z hz), scalar_nat]

theorem rotated_width (w : Nat) (p : Phase) (z : WordPair)
    (hr : z.1.length = w + 1) (hi : z.2.length = w + 1) :
    (rotateWords p z.1 z.2).1.length = w + 1 ∧
      (rotateWords p z.1 z.2).2.length = w + 1 := by
  cases p <;> simp [rotateWords, negate_length, hr, hi]

def serialized (record : List WordPair) : List Bool :=
  record.flatMap (fun z => z.1 ++ z.2)

/-- Exact record extent: each visited field preserves both coefficient widths. -/
theorem serialized_scan_length (w k : Nat) (record : List WordPair)
    (h : ∀ z ∈ record, z.1.length = w + 1 ∧ z.2.length = w + 1) :
    (serialized (scan k record)).length = record.length * (2 * (w + 1)) := by
  induction record with
  | nil => simp [serialized, scan]
  | cons z zs ih =>
    have hz := h z (by simp)
    have ht : ∀ y ∈ zs, y.1.length = w + 1 ∧ y.2.length = w + 1 := by
      intro y hy
      exact h y (by simp [hy])
    have hw := rotated_width w (phaseOfNat k) z hz.1 hz.2
    have hh := congrArg (fun n => 2 * (w + 1) + n) (ih ht)
    simp [serialized, scan, List.length_cons, Nat.add_mul, hw.1, hw.2,
      Nat.add_comm, Nat.add_left_comm, Nat.add_assoc, two_mul] at hh ⊢
    omega

section Physical
variable {P S C : Type*} {f : Nat}

def exponent (decode : P ≃ S × (Fin f → Address)) (p : P) : Nat :=
  2 * f + ∑ j, q ((decode p).2 j)

def valueField (h : P → C → WordPair) (c : C) : P → ℂ := fun p => decoded (h p c)

def encodedPhase (decode : P ≃ S × (Fin f → Address))
    (h : P → C → WordPair) (p : P) (c : C) : WordPair :=
  rotateWords (phaseOfNat (exponent decode p)) (h p c).1 (h p c).2

def encodedForward (decode : P ≃ S × (Fin f → Address)) (step : Gate → P → P)
    (h : P → C → WordPair) (p : P) (c : C) : WordPair :=
  encodedPhase decode h (physicalRun step word.reverse p) c

def ForwardFits (w : Nat) (decode : P ≃ S × (Fin f → Address))
    (h : P → C → WordPair) : Prop :=
  ∀ p c, Fits w (phaseOfNat (exponent decode p)) (h p c)

theorem forward_refines (w : Nat) (decode : P ≃ S × (Fin f → Address))
    (step : Gate → P → P) (h : P → C → WordPair) (hv : ForwardFits w decode h) (c : C) :
    valueField (encodedForward decode step h) c = physicalForward iUnit decode step (valueField h c) := by
  funext p
  simp only [valueField, encodedForward, encodedPhase, physicalForward, physicalPhase]
  rw [decoded_rotate w _ _ (hv _ c), scalar_nat, selected_phase_product]
  rfl

/-- The bit-word encoding premise of the selected tensor action is discharged
for every field under its exact signed guard. Completed address gates remain. -/
theorem forward_tensor (w : Nat) (decode : P ≃ S × (Fin f → Address))
    (step : Gate → P → P) (hstep : CompletedPrimitive decode step)
    (h : P → C → WordPair) (hv : ForwardFits w decode h) (c : C) (p : P) :
    decoded (encodedForward decode step h p c) =
      CommonLabelTensor.coordinates (fun _ : Fin f => Address)
        (PiTensorProduct.map (fun _ : Fin f => unary sigma (selectedPhase iUnit))
          ((CommonLabelTensor.coordinates (R := ℂ) (fun _ : Fin f => Address)).symm
            (fun x => decoded (h (decode.symm ((decode p).1, x)) c)))) (decode p).2 := by
  calc
    _ = physicalForward iUnit decode step (valueField h c) p :=
      congrFun (forward_refines w decode step h hv c) p
    _ = _ := physical_tensor_refinement iUnit decode step hstep (valueField h c) p

/-- A common exact grid scale commutes with every Gaussian unit. -/
theorem scaled_forward_refines (scale : ℂ) (w : Nat)
    (decode : P ≃ S × (Fin f → Address)) (step : Gate → P → P)
    (h : P → C → WordPair) (hv : ForwardFits w decode h) (c : C) :
    (fun p => scale * decoded (encodedForward decode step h p c)) =
      physicalForward iUnit decode step (fun p => scale * decoded (h p c)) := by
  funext p
  have hf := congrFun (forward_refines w decode step h hv c) p
  simp only [valueField, physicalForward, physicalPhase] at hf ⊢
  rw [hf]
  ring

/-- In particular, a fixed dyadic root-grid unit may be carried through unchanged. -/
theorem scaled_forward_tensor (scale : ℂ) (w : Nat)
    (decode : P ≃ S × (Fin f → Address)) (step : Gate → P → P)
    (hstep : CompletedPrimitive decode step) (h : P → C → WordPair)
    (hv : ForwardFits w decode h) (c : C) (p : P) :
    scale * decoded (encodedForward decode step h p c) =
      CommonLabelTensor.coordinates (fun _ : Fin f => Address)
        (PiTensorProduct.map (fun _ : Fin f => unary sigma (selectedPhase iUnit))
          ((CommonLabelTensor.coordinates (R := ℂ) (fun _ : Fin f => Address)).symm
            (fun x => scale * decoded (h (decode.symm ((decode p).1, x)) c)))) (decode p).2 := by
  calc
    _ = physicalForward iUnit decode step (fun p => scale * decoded (h p c)) p :=
      congrFun (scaled_forward_refines scale w decode step h hv c) p
    _ = _ := physical_tensor_refinement iUnit decode step hstep
      (fun p => scale * decoded (h p c)) p

/-- Inverse phasing uses the recovered input address, after the affine undo. -/
def encodedBackward (decode : P ≃ S × (Fin f → Address)) (step : Gate → P → P)
    (h : P → C → WordPair) (p : P) (c : C) : WordPair :=
  let z := h (physicalRun step word p) c
  rotateWords (inversePhase (phaseOfNat (exponent decode p))) z.1 z.2

def BackwardFits (w : Nat) (decode : P ≃ S × (Fin f → Address)) (step : Gate → P → P)
    (h : P → C → WordPair) : Prop :=
  ∀ p c, Fits w (inversePhase (phaseOfNat (exponent decode p))) (h (physicalRun step word p) c)

theorem backward_refines (w : Nat) (decode : P ≃ S × (Fin f → Address))
    (step : Gate → P → P) (h : P → C → WordPair)
    (hv : BackwardFits w decode step h) (c : C) :
    valueField (encodedBackward decode step h) c = physicalBackward iUnit decode step (valueField h c) := by
  funext p
  simp only [valueField, encodedBackward, physicalBackward]
  rw [decoded_rotate w _ _ (hv p c), scalar_inverse_nat, selected_phase_product]
  rfl

theorem decoded_roundtrip (w : Nat) (decode : P ≃ S × (Fin f → Address))
    (step : Gate → P → P) (hstep : CompletedPrimitive decode step)
    (h : P → C → WordPair) (hf : ForwardFits w decode h)
    (hb : BackwardFits w decode step (encodedForward decode step h)) (c : C) :
    valueField (encodedBackward decode step (encodedForward decode step h)) c = valueField h c := by
  rw [backward_refines w decode step _ hb c, forward_refines w decode step h hf c]
  exact physical_backward_forward iUnit decode step hstep (valueField h c)

end Physical

def oneWord : WordPair := ([true, false, false], [false, false, false])

/-- Checking one coefficient cannot stand in for traversing the complete record. -/
theorem skipped_field_changes_record :
    (scan 1 [oneWord, oneWord]).map decodePair ≠
      [rotateWords .imag oneWord.1 oneWord.2, oneWord].map decodePair := by decide

end RecordPhaseBridge
