import GeometryExecution
import GeometryValues
import LivePortCore
namespace CurrentMain.ComplexGeometry
open CurrentMain.SignedTrace

/-- The two frame requests immediately preceding this scalar gate. Gaps between
anchors contain only separately certified center, gauge or terminal requests. -/
structure OperationAnchor where
  beforeGate : Nat
  afterGate : Nat
  deriving DecidableEq, Repr

def operationRequestCheck (operations : Nat → OpRecord) (eventAt : Nat → Move)
    (anchors : Nat → OperationAnchor) (a : Annotation) (source : Nat) : Bool :=
  let anchor := anchors source
  let common := (operations source).frame
  decide (anchor.afterGate=anchor.beforeGate+2 ∧
    (eventAt (anchor.beforeGate+1)).port=
      ⟨false,CurrentMain.LivePorts.representative a.step.src,common⟩) &&
  (if get CurrentMain.LivePorts.removedTable a.step.dst=1 then
    decide ((eventAt anchor.beforeGate).target=true ∧ (eventAt anchor.beforeGate).after=common)
   else decide ((eventAt anchor.beforeGate).port=
      ⟨false,CurrentMain.LivePorts.representative a.step.dst,common⟩))

def actualRequestsCheck (operations : Nat → OpRecord) (eventAt : Nat → Move)
    (anchors : Nat → OperationAnchor) (upper : Nat) : Nat → List Annotation → List Nat → Bool
  | lower, [], [] => decide (lower≤upper)
  | lower, a::rest, source::indices =>
      decide (lower≤(anchors source).beforeGate ∧ (anchors source).afterGate≤upper) &&
      operationRequestCheck operations eventAt anchors a source &&
      actualRequestsCheck operations eventAt anchors upper (anchors source).afterGate rest indices
  | _, _, _ => false

structure ActualRequestCertificate (operations : Nat → OpRecord) (eventAt : Nat → Move)
    (anchors : Nat → OperationAnchor) (lower upper : Nat)
    (annotations : List Annotation) (sourceIndices : List Nat) : Prop where
  checked : actualRequestsCheck operations eventAt anchors upper lower annotations sourceIndices=true

theorem operationRequest_source (operations : Nat → OpRecord) (eventAt : Nat → Move)
    (anchors : Nat → OperationAnchor) (a : Annotation) (source : Nat)
    (checked : operationRequestCheck operations eventAt anchors a source=true) :
    (anchors source).afterGate=(anchors source).beforeGate+2 ∧
    (eventAt ((anchors source).beforeGate+1)).port=
      ⟨false,CurrentMain.LivePorts.representative a.step.src,(operations source).frame⟩ :=
  of_decide_eq_true (Bool.and_eq_true_iff.mp checked).1

theorem operationRequest_destination (operations : Nat → OpRecord) (eventAt : Nat → Move)
    (anchors : Nat → OperationAnchor) (a : Annotation) (source : Nat)
    (checked : operationRequestCheck operations eventAt anchors a source=true)
    (retained : get CurrentMain.LivePorts.removedTable a.step.dst≠1) :
    (eventAt (anchors source).beforeGate).port=
      ⟨false,CurrentMain.LivePorts.representative a.step.dst,(operations source).frame⟩ := by
  have dest := (Bool.and_eq_true_iff.mp checked).2
  simpa only [if_neg retained] using of_decide_eq_true
    (show decide ((eventAt (anchors source).beforeGate).port=
      ⟨false,CurrentMain.LivePorts.representative a.step.dst,(operations source).frame⟩)=true by
      simpa only [if_neg retained] using dest)

def targetPortsCheck (eventAt : Nat → Move) (frame : Nat) : List Nat → List Nat → Bool
  | [], [] => true
  | target::rest, position::positions =>
      decide (target<1320 ∧ position<94919 ∧ (eventAt position).port=⟨true,target,frame⟩) &&
      targetPortsCheck eventAt frame rest positions
  | _, _ => false

theorem targetPortsCheck_length (eventAt : Nat → Move) (frame : Nat)
    (targets positions : List Nat) (checked : targetPortsCheck eventAt frame targets positions=true) :
    targets.length=positions.length := by
  induction targets generalizing positions with
  | nil => cases positions <;> simp_all [targetPortsCheck]
  | cons target rest ih =>
    cases positions with
    | nil => simp [targetPortsCheck] at checked
    | cons position tail =>
      exact congrArg Nat.succ (ih tail (Bool.and_eq_true_iff.mp checked).2)

theorem targetPortsCheck_covers (eventAt : Nat → Move) (frame : Nat)
    (targets positions : List Nat) (checked : targetPortsCheck eventAt frame targets positions=true)
    (target : Nat) (member : target∈targets) :
    ∃ position∈positions, target<1320 ∧ position<94919 ∧
      (eventAt position).port=⟨true,target,frame⟩ := by
  induction targets generalizing positions with
  | nil => simp at member
  | cons head rest ih =>
    cases positions with
    | nil => simp [targetPortsCheck] at checked
    | cons position tail =>
      have both := Bool.and_eq_true_iff.mp checked
      rcases List.mem_cons.mp member with same | inside
      · subst target
        exact ⟨position,by simp,of_decide_eq_true both.1⟩
      · rcases ih tail both.2 inside with ⟨p,hp,h⟩
        exact ⟨p,by simp [hp],h⟩

end CurrentMain.ComplexGeometry
#print axioms CurrentMain.ComplexGeometry.operationRequest_source
#print axioms CurrentMain.ComplexGeometry.operationRequest_destination
#print axioms CurrentMain.ComplexGeometry.targetPortsCheck_length
#print axioms CurrentMain.ComplexGeometry.targetPortsCheck_covers
