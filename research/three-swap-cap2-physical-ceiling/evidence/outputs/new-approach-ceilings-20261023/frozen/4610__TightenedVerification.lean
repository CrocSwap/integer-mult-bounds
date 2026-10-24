/-
Apache-2.0. Substantial OpenAI Codex assistance. Signed Cao Yifan.

Aggregator for scoped finite native-frame, profile and arithmetic evidence.
This is not a formal integer-multiplication theorem. JSON transcription,
native amplitude/phase semantics, controller semantics and the compiler
transfer retain their separately stated external proof boundaries.
-/
import Native
import AnalyticGain
import TightenedArithmetic
import TightenedCapacity
import TightenedNumerical

set_option maxRecDepth 100000
set_option maxHeartbeats 0

namespace KappaTightenedVerification

open NativeCertificate NativeData

/-- Positive-rank moment of the finite native census (all actual ranks ≤ 9). -/
noncomputable def censusMoment (c : Array Nat) (t : ℝ) : ℝ :=
  (c[1]! : ℝ) * (1 : ℝ) ^ t + (c[2]! : ℝ) * (2 : ℝ) ^ t +
    (c[3]! : ℝ) * (3 : ℝ) ^ t + (c[4]! : ℝ) * (4 : ℝ) ^ t +
    (c[5]! : ℝ) * (5 : ℝ) ^ t + (c[6]! : ℝ) * (6 : ℝ) ^ t +
    (c[7]! : ℝ) * (7 : ℝ) ^ t + (c[8]! : ℝ) * (8 : ℝ) ^ t +
    (c[9]! : ℝ) * (9 : ℝ) ^ t

noncomputable def nativePaidMoment (t : ℝ) : ℝ :=
  censusMoment (totalPaid forwardData) t

noncomputable def nativeHelperMoment (t : ℝ) : ℝ :=
  censusMoment NativeVerification.helperCensus t

/-- Literal retained controller diagonal. Its extraction is externally checked. -/
noncomputable def controllerDiagonalMoment (t : ℝ) : ℝ :=
  448 * (17 : ℝ) ^ t + 448 * (25 : ℝ) ^ t + 448 * (33 : ℝ) ^ t +
    448 * (41 : ℝ) ^ t + 448 * (49 : ℝ) ^ t + 448 * (57 : ℝ) ^ t +
    448 * (65 : ℝ) ^ t + 224 * (73 : ℝ) ^ t + 224 * (145 : ℝ) ^ t

/-- 15 × 112 rank-one queries, and all retained controller idle charges. -/
noncomputable def controllerFixedPaidMoment (t : ℝ) : ℝ :=
  (15 * 112) * (1 : ℝ) ^ t +
    448 * (16 : ℝ) ^ t + 448 * (24 : ℝ) ^ t + 448 * (32 : ℝ) ^ t +
    448 * (40 : ℝ) ^ t + 448 * (48 : ℝ) ^ t + 448 * (56 : ℝ) ^ t +
    448 * (64 : ℝ) ^ t + 224 * (72 : ℝ) ^ t

theorem local_paid_profile_binding (t : ℝ) :
    nativePaidMoment t = KappaChangedG.newPaidMoment t := by
  rw [nativePaidMoment, forward_paid]
  norm_num [censusMoment, KappaChangedG.newPaidMoment]

theorem local_helper_profile_binding (t : ℝ) :
    nativeHelperMoment t =
      28 * (4 : ℝ) ^ t + 7 * (7 : ℝ) ^ t + 47 * (8 : ℝ) ^ t + 326 * (9 : ℝ) ^ t := by
  rw [nativeHelperMoment, NativeVerification.complete_productive_helper_census]
  norm_num [censusMoment]

theorem complete_target_profile_binding (t : ℝ) :
    NumericalMoments.targetMoment t = 18 * nativeHelperMoment t + controllerDiagonalMoment t := by
  rw [local_helper_profile_binding]
  unfold NumericalMoments.targetMoment controllerDiagonalMoment
  ring

theorem complete_paid_profile_binding (t : ℝ) :
    NumericalMoments.paidMoment t = 18 * nativePaidMoment t + controllerFixedPaidMoment t := by
  rw [local_paid_profile_binding]
  unfold NumericalMoments.paidMoment KappaChangedG.newPaidMoment controllerFixedPaidMoment
  ring

theorem tested_real_rational_binding :
    (KappaChangedG.Arithmetic.tested : ℝ) = KappaChangedG.capacitySaving := by
  norm_num [KappaChangedG.Arithmetic.tested, KappaChangedG.capacitySaving]

theorem numerical_exponent_binding :
    (99697822419 / 100000000000 : ℝ) = 1 - (KappaChangedG.Arithmetic.tested : ℝ) := by
  norm_num [KappaChangedG.Arithmetic.tested]

theorem numerical_tail_exponent_binding :
    (119697822419 / 100000000000 : ℝ) =
      1 - (KappaChangedG.Arithmetic.tested : ℝ) + 1 / 5 := by
  norm_num [KappaChangedG.Arithmetic.tested]

theorem compiler_eta_binding :
    KappaChangedG.capacityEta =
      (1 - (KappaChangedG.Arithmetic.tested : ℝ)) *
        (145 : ℝ) ^ (-(1024 * (KappaChangedG.Arithmetic.tested : ℝ))) := by
  rw [tested_real_rational_binding]
  rfl

theorem uniform_saving_binding :
    KappaChangedG.Arithmetic.complexUniformSaving =
      KappaChangedG.Arithmetic.kappa +
        6 * ((KappaChangedG.Arithmetic.tested - KappaChangedG.Arithmetic.kappa) / 7) := by
  norm_num [KappaChangedG.Arithmetic.complexUniformSaving,
    KappaChangedG.Arithmetic.kappa, KappaChangedG.Arithmetic.tested]

/-- The precise finite frame/invoice statement imported from Native. -/
def nativeFrameInvoiceEvidence : Prop :=
  linked initialFrames finalFrames forwardData = true ∧
  linked initialFrames backwardFinalFrames backwardData = true ∧
  totalPaid forwardData = #[0,2201,412,510,127,40,0,0,8,0] ∧
  totalPaid backwardData = #[0,2201,412,510,127,40,0,0,8,0] ∧
  totalScalarCost forwardData = 158120 ∧
  totalScalarCost backwardData = 158168 ∧
  totalEvents forwardData = 21449 ∧ totalEvents backwardData = 21449 ∧
  backwardFinalFrames.toList.take 632 = finalFrames.toList.take 632

/-- All embedded catalogue checks and their exact raw-table bindings. -/
def nativeCatalogueEvidence : Prop :=
  (frames.wellFormed && operators.wellFormed && paid.wellFormed && warps.wellFormed) = true ∧
  frameEntries.map (·.data) = frames.toList ∧
  operatorEntries.map (·.data) = operators.toList ∧
  paidEntries.map (·.data) = paid.toList ∧
  warpEntries.map (·.data) = warps.toList ∧
  (∀ i : Fin frameEntries.length, independent (frameEntries.get i).data = true) ∧
  (∀ i : Fin operatorEntries.length, checkOperator (operatorEntries.get i).data = true) ∧
  (∀ i : Fin paidEntries.length, checkPaid frames (paidEntries.get i).data = true) ∧
  (∀ i : Fin warpEntries.length, checkWarp frames operators (warpEntries.get i).data = true) ∧
  (∀ i : Fin helperEntries.length, checkPaid frames (helperEntries.get i).data = true) ∧
  (∀ i : Fin forwardSegments.length, checkSegment frames paid warps (forwardSegments.get i).data = true) ∧
  (∀ i : Fin backwardSegments.length, checkSegment frames paid warps (backwardSegments.get i).data = true)

theorem native_catalogue_evidence : nativeCatalogueEvidence :=
  NativeVerification.all_embedded_catalogues_and_segments_checked

/-- Every productive helper is the corresponding actual persistent endpoint. -/
def nativeHelperEndpointEvidence : Prop :=
  (helperEntries.zipIdx).all (fun (h, i) =>
    h.data.input == initialFrames.get (224+i) &&
    h.data.output == finalFrames.get (224+i)) = true

theorem native_helper_endpoint_evidence : nativeHelperEndpointEvidence :=
  NativeVerification.helpers_are_actual_endpoint_interfaces

/-- A conjunction of the actual finite/profile/arithmetic results. It makes
no implication from this conjunction to a multiplication algorithm theorem. -/
theorem complete_scoped_evidence :
    KappaChangedG.Arithmetic.kappa = (15108879 / 5000000000 : ℚ) ∧
    (9443 / 3125000 : ℚ) < KappaChangedG.Arithmetic.kappa ∧
    KappaChangedG.Arithmetic.kappa < KappaChangedG.Arithmetic.tested ∧
    KappaChangedG.Arithmetic.outerSlacks.all (fun p => decide (0 < p.2)) = true ∧
    KappaChangedG.Arithmetic.functionalSlacks.all (fun p => decide (0 < p.2)) = true ∧
    NumericalMoments.paidMoment (99697822419 / 100000000000 : ℝ) <
      (1 - (1 / 100000000000 : ℝ)) * NumericalMoments.targetMoment (99697822419 / 100000000000 : ℝ) ∧
    NumericalMoments.paidMoment (119697822419 / 100000000000 : ℝ) <
      (97 / 100 : ℝ) * (20 : ℝ) ^ (1 / 5 : ℝ) *
        NumericalMoments.targetMoment (99697822419 / 100000000000 : ℝ) ∧
    (10928 * 21 : ℝ) <
      (97 / 100 : ℝ) * (20 : ℝ) ^ (302177581 / 100000000000 : ℝ) *
        NumericalMoments.targetMoment (99697822419 / 100000000000 : ℝ) ∧
    (63 / 64 : ℝ) ^ (1000 : ℕ) < KappaChangedG.capacityEta ∧
    (145 : ℝ) ^ KappaChangedG.capacityExponent < (2 : ℝ) ^ (1000 : ℕ) ∧
    (((700000000000 : ℕ) * 55099 + 1) ^ 1000 < 2 ^ 55099) ∧
    nativeFrameInvoiceEvidence ∧ nativeCatalogueEvidence ∧ nativeHelperEndpointEvidence :=
  ⟨KappaChangedG.Arithmetic.claimed_saving,
    KappaChangedG.Arithmetic.strict_improvement,
    KappaChangedG.Arithmetic.tested_above_kappa,
    KappaChangedG.Arithmetic.outerSlacks_all_positive,
    KappaChangedG.Arithmetic.functionalSlacks_all_positive,
    NumericalMoments.contraction,
    NumericalMoments.paid_tail,
    NumericalMoments.completion_tail,
    KappaChangedG.compiler_eta_capacity,
    KappaChangedG.compiler_initial_range,
    KappaChangedG.Arithmetic.finite_compiler_wins,
    NativeVerification.complete_finite_native_certificate,
    native_catalogue_evidence,
    native_helper_endpoint_evidence⟩

end KappaTightenedVerification

#print axioms KappaTightenedVerification.local_paid_profile_binding
#print axioms KappaTightenedVerification.local_helper_profile_binding
#print axioms KappaTightenedVerification.complete_target_profile_binding
#print axioms KappaTightenedVerification.complete_paid_profile_binding
#print axioms KappaTightenedVerification.tested_real_rational_binding
#print axioms KappaTightenedVerification.numerical_exponent_binding
#print axioms KappaTightenedVerification.numerical_tail_exponent_binding
#print axioms KappaTightenedVerification.compiler_eta_binding
#print axioms KappaTightenedVerification.uniform_saving_binding
#print axioms KappaTightenedVerification.native_catalogue_evidence
#print axioms KappaTightenedVerification.native_helper_endpoint_evidence
#print axioms KappaTightenedVerification.complete_scoped_evidence
