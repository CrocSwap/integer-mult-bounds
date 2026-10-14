import GeometryRequests
import AliasLifetimeCore
import AllSinkBase
import SignedTraceFinalSupport
namespace CurrentMain.ComplexGeometry
open CurrentMain.SignedTrace

structure RootRequest where
  role : Nat
  targets : List Nat
  physicalPosition : Nat
  targetPositions : List Nat
  deriving DecidableEq, Repr

structure GaugeRequest where
  frame : Nat
  physicalPosition : Nat
  targets : List Nat
  targetPositions : List Nat
  previousSource : Nat
  nextSource : Nat
  deriving DecidableEq, Repr

structure SinkRequest where
  rootIndex : Nat
  postPosition : Nat
  deriving DecidableEq, Repr

def rootRequestCheck (eventAt : Nat → Move) (rootPorts : Nat → OpRecord)
    (requests : Nat → RootRequest) (r : RootBinding) : Bool :=
  let request := requests r.rootIndex
  let frame := (rootPorts r.rootIndex).frame
  decide (r.rootIndex<3157 ∧ request.role=r.role ∧ (rootPorts r.rootIndex).node=r.node ∧
    request.targets.Nodup) &&
  (if get CurrentMain.LivePorts.removedTable r.role=1 then true else
    decide ((eventAt request.physicalPosition).port=
      ⟨false,CurrentMain.LivePorts.representative r.role,frame⟩) &&
    (if r.rootIndex<3135 then
      decide (73592≤request.physicalPosition ∧ request.physicalPosition<82913 ∧
        request.targetPositions.all (fun p => decide (request.physicalPosition<p ∧ p<82913))=true) &&
      targetPortsCheck eventAt frame request.targets request.targetPositions
     else decide (request.targets=List.range 1320 ∧ request.targetPositions=[] ∧
        request.physicalPosition<20334)))

def gaugeRequestCheck (eventAt : Nat → Move) (anchors : Nat → OperationAnchor)
    (requests : Nat → GaugeRequest) (r : CurrentMain.AliasLifetimes.Row) : Bool :=
  let q := requests r.recipient
  decide (q.targets.Nodup ∧ (anchors q.previousSource).afterGate≤q.physicalPosition ∧
    q.physicalPosition<(anchors q.nextSource).beforeGate ∧ q.physicalPosition<73592 ∧
    (eventAt q.physicalPosition).port=⟨false,r.donor,q.frame⟩ ∧
    q.targetPositions.all (fun p => decide (q.physicalPosition<p ∧ p<(anchors q.nextSource).beforeGate))=true) &&
  targetPortsCheck eventAt q.frame q.targets q.targetPositions

def sinkWriteRequestCheck (eventAt : Nat → Move) (anchors : Nat → OperationAnchor)
    (sink : CurrentMain.AllSinkData.SinkRecord) (w : CurrentMain.AllSinkData.SinkWrite) : Bool :=
  let a := anchors w.index
  decide (20334≤a.beforeGate ∧ a.afterGate≤73592 ∧
    (eventAt a.beforeGate).target=true ∧ (eventAt a.beforeGate).role=sink.pivot ∧
    (eventAt a.beforeGate).after=(eventAt (a.beforeGate+1)).after)

def sinkRequestCheck (eventAt : Nat → Move) (anchors : Nat → OperationAnchor)
    (rootPorts : Nat → OpRecord) (rootRequests : Nat → RootRequest)
    (requests : Nat → SinkRequest) (sink : CurrentMain.AllSinkData.SinkRecord) : Bool :=
  let q := requests sink.role
  let lastSource := (sink.writes.getLast?.map CurrentMain.AllSinkData.SinkWrite.index).getD 0
  let positions := (List.range sink.targets.length).map (q.postPosition+·)
  decide (q.rootIndex<3135 ∧ (rootRequests q.rootIndex).role=sink.role ∧
    (rootRequests q.rootIndex).targets=sink.targets ∧ sink.targets.Nodup ∧
    sink.targets.length=8 ∧ sink.pivot∈sink.targets ∧ sink.writes.length>0 ∧
    q.postPosition=(anchors lastSource).afterGate ∧ q.postPosition+8≤73592) &&
  sink.writes.all (sinkWriteRequestCheck eventAt anchors sink) &&
  targetPortsCheck eventAt (rootPorts q.rootIndex).frame sink.targets positions

theorem gaugeRequest_targets (eventAt : Nat → Move) (anchors : Nat → OperationAnchor)
    (requests : Nat → GaugeRequest) (r : CurrentMain.AliasLifetimes.Row)
    (checked : gaugeRequestCheck eventAt anchors requests r=true)
    (target : Nat) (member : target∈(requests r.recipient).targets) :
    ∃ position∈(requests r.recipient).targetPositions, target<1320 ∧ position<94919 ∧
      (eventAt position).port=⟨true,target,(requests r.recipient).frame⟩ :=
  targetPortsCheck_covers eventAt _ _ _ (Bool.and_eq_true_iff.mp checked).2 target member

theorem sinkRequest_targets (eventAt : Nat → Move) (anchors : Nat → OperationAnchor)
    (rootPorts : Nat → OpRecord) (rootRequests : Nat → RootRequest)
    (requests : Nat → SinkRequest) (sink : CurrentMain.AllSinkData.SinkRecord)
    (checked : sinkRequestCheck eventAt anchors rootPorts rootRequests requests sink=true)
    (target : Nat) (member : target∈sink.targets) :
    ∃ position, target<1320 ∧ position<94919 ∧
      (eventAt position).port=⟨true,target,(rootPorts (requests sink.role).rootIndex).frame⟩ := by
  rcases targetPortsCheck_covers eventAt _ _ _ (Bool.and_eq_true_iff.mp checked).2 target member with
    ⟨position,_,facts⟩
  exact ⟨position,facts⟩

end CurrentMain.ComplexGeometry
#print axioms CurrentMain.ComplexGeometry.gaugeRequest_targets
#print axioms CurrentMain.ComplexGeometry.sinkRequest_targets
