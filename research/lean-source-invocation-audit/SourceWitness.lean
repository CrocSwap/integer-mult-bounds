import ContractScope
import SourceWord

/-!
A source-word-backed diagnostic for the direct single-host comparison.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.

The actual stage-2, replica-0 forward word has helper 3 at local register243.
Its normalized execution below is the complete checked 19,002-event word,
not an assumed endpoint. Initializing that helper alone to one restores
exactly that helper and clears the temporary, as ActualWord proves.

The geometric observation uses the SOURCE'S DECLARED entry/exit residual:
empty local entrance frame, full rank-eight exit frame, owner family508,
pending interval [16,24). Binding each emitted frame operation and owner
selector to physical instructions is NOT proved here. Thus the final result
refutes the proposed direct contract IF it is required to reproduce these
declared observations; it is not a physical-compiler counterexample.

The address-coordinate type is arbitrary with two distinct elements. No
claim that a particular small prime is admitted by the supplier is needed.
-/

namespace SourceInvocation

open WholeHosting

/-- The literal selected slot's mask in the pending child's coordinate chart. -/
def secondResidual : Mask (Fin 64) :=
  fun i => decide (16 ≤ i.val ∧ i.val < 24)

/-- Read local register243 after the actual normalized forward word, starting
with this helper's Boolean value and every other logical register zero. -/
def helperResponse (value : Bool) : Bool :=
  (ActualWord.runForward (if value then (1 <<< 243) else 0)).testBit 243

theorem helperResponse_eq (value : Bool) : helperResponse value = value := by
  cases value
  · simp only [helperResponse, Bool.false_eq_true, ↓reduceIte, ActualWord.zero_output]
    decide
  · simp only [helperResponse, ↓reduceIte, ActualWord.basis243_output]
    decide

/-- The parent invocation does not name family508; its observation is unchanged. -/
def parentObservation {K : Type} (value : Stream (Fin 64) K Bool)
    (address : Address (Fin 64) K) : Bool := value address

/-- The declared hosted residual, with the concrete source word still executed
between its empty entrance and full local exit frames. This is the observation
on helper3's single physical owner, not the whole cover sweep. -/
def declaredHostedObservation {K : Type} (value : Stream (Fin 64) K Bool)
    (address : Address (Fin 64) K) : Bool :=
  helperResponse (value (swapAddress secondResidual address))

def witnessAddress {K : Type} (zero one : K) : Address (Fin 64) K :=
  fun _ => (zero, one)

def witnessStream {K : Type} [DecidableEq K] (zero : K) : Stream (Fin 64) K Bool :=
  fun address => decide ((address ⟨16, by decide⟩).1 = zero)

theorem parent_witness {K : Type} [DecidableEq K] (zero one : K) :
    parentObservation (witnessStream zero) (witnessAddress zero one) = true := by
  simp [parentObservation, witnessStream, witnessAddress]

theorem declared_hosted_witness {K : Type} [DecidableEq K]
    (zero one : K) (different : zero ≠ one) :
    declaredHostedObservation (witnessStream zero) (witnessAddress zero one) = false := by
  simp [declaredHostedObservation, helperResponse_eq, witnessStream,
    swapAddress, secondResidual, witnessAddress, Ne.symm different]

/-- A direct source bridge preserving the other final data cannot supply the
existing single-host contract with family507 as host and family508 in R.
The observation of family508 must be the same unmodified physical projection
in both layouts; a compensating layout-dependent decoding is a different bridge.
The two endpoint equalities are precisely the remaining physical-observation
refinement obligations; this theorem proves their incompatibility with that
contract, not their derivation from a physical compiler. -/
theorem direct_single_host_bridge_impossible {K R B C : Type} [DecidableEq K]
    (zero one : K) (different : zero ≠ one)
    {event : WindowEvent (Fin 64) R}
    (contract : PhysicalContract (K := K) (A := Bool) event B C)
    (state : WindowState (Fin 64) K Bool R) (oldBank : B) (newBank : C)
    (family508 : R → Stream (Fin 64) K Bool)
    (parent_endpoint : family508 (contract.original (state, oldBank)).1.2
        (witnessAddress zero one) =
      parentObservation (witnessStream zero) (witnessAddress zero one))
    (hosted_endpoint : family508 (contract.relocated (state, newBank)).1.2
        (witnessAddress zero one) =
      declaredHostedObservation (witnessStream zero) (witnessAddress zero one)) : False := by
  apply no_contract_for_different_rest contract state oldBank newBank
    (fun rest => family508 rest (witnessAddress zero one))
    _ _ parent_endpoint hosted_endpoint
  rw [parent_witness, declared_hosted_witness zero one different]
  decide

end SourceInvocation

#print axioms SourceInvocation.helperResponse_eq
#print axioms SourceInvocation.parent_witness
#print axioms SourceInvocation.declared_hosted_witness
#print axioms SourceInvocation.direct_single_host_bridge_impossible
