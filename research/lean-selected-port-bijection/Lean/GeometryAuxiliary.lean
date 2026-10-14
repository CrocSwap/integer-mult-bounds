import GeometryExecution
import GeometryValues
namespace CurrentMain.ComplexGeometry
open CurrentMain.BinaryFrame

structure SourceRoute where
  target : Nat
  first : Nat
  common : Nat
  cap : Nat
  final : Nat
  firstEdge : Nat
  capEdge : Nat
  finalEdge : Nat
  deriving DecidableEq, Repr

def sourceRouteCheck (bases : Nat → BasisRecord) (frames : Nat → FrameRecord)
    (edges : Nat → EdgeRecord) (inputMask : Nat → Nat) (source : Nat) (r : SourceRoute) : Bool :=
  decide (r.target=(source ^^^ 1) ∧ r.target<1320 ∧
    frameRows bases frames r.first=[inputMask source] ∧
    (frameRows bases frames r.common).length=3 ∧
    (bases (frames r.cap).annihilator).rows=[inputMask r.target] ∧
    (frameRows bases frames r.cap).length=21 ∧
    (frameRows bases frames r.final).length=22) &&
  edgeMatches frames edges r.first r.common r.firstEdge &&
  edgeMatches frames edges r.common r.cap r.capEdge &&
  edgeMatches frames edges r.cap r.final r.finalEdge

theorem sourceRouteCheck_sound (bases : Nat → BasisRecord) (frames : Nat → FrameRecord)
    (edges : Nat → EdgeRecord) (catalog : ValidCatalog bases frames edges)
    (inputMask : Nat → Nat) (source : Nat) (r : SourceRoute)
    (checked : sourceRouteCheck bases frames edges inputMask source r=true) :
    (∀ n, Span (frameRows bases frames r.first) n → Span (frameRows bases frames r.common) n) ∧
    (∀ n, Span (frameRows bases frames r.common) n → Span (frameRows bases frames r.cap) n) ∧
    (∀ n, Span (frameRows bases frames r.cap) n → Span (frameRows bases frames r.final) n) := by
  have last := Bool.and_eq_true_iff.mp checked
  have middle := Bool.and_eq_true_iff.mp last.1
  have first := Bool.and_eq_true_iff.mp middle.1
  exact ⟨(checked_frame_edge bases frames edges catalog _ _ _ first.2).1,
    (checked_frame_edge bases frames edges catalog _ _ _ middle.2).1,
    (checked_frame_edge bases frames edges catalog _ _ _ last.2).1⟩

theorem sourceRouteCheck_ranks (bases : Nat → BasisRecord) (frames : Nat → FrameRecord)
    (edges : Nat → EdgeRecord) (inputMask : Nat → Nat) (source : Nat) (r : SourceRoute)
    (checked : sourceRouteCheck bases frames edges inputMask source r=true) :
    [(frameRows bases frames r.common).length-(frameRows bases frames r.first).length,
      (frameRows bases frames r.cap).length-(frameRows bases frames r.common).length,
      (frameRows bases frames r.final).length-(frameRows bases frames r.cap).length]=[2,18,1] := by
  have raw := (Bool.and_eq_true_iff.mp (Bool.and_eq_true_iff.mp (Bool.and_eq_true_iff.mp checked).1).1).1
  have facts : r.target=(source ^^^ 1) ∧ r.target<1320 ∧
    frameRows bases frames r.first=[inputMask source] ∧
    (frameRows bases frames r.common).length=3 ∧
    (bases (frames r.cap).annihilator).rows=[inputMask r.target] ∧
    (frameRows bases frames r.cap).length=21 ∧
    (frameRows bases frames r.final).length=22 := of_decide_eq_true raw
  simp only [facts.2.2.1,facts.2.2.2.1,facts.2.2.2.2.2.1,facts.2.2.2.2.2.2]
  rfl

structure CenterCharge where
  root : Nat
  frame : Nat
  deriving DecidableEq, Repr

def centerChargeCheck (bases : Nat → BasisRecord) (frames : Nat → FrameRecord)
    (rootPorts : Nat → OpRecord) (c : CenterCharge) : Bool :=
  decide ((rootPorts c.root).frame=c.frame ∧ (frameRows bases frames c.frame).length=20)

def rangeCheck (p : Nat → Bool) : Nat → Nat → Bool
  | _, 0 => true
  | start, count+1 => p start && rangeCheck p (start+1) count

theorem rangeCheck_sound (p : Nat → Bool) (start count i : Nat)
    (checked : rangeCheck p start count=true) (lo : start≤i) (hi : i<start+count) : p i=true := by
  induction count generalizing start with
  | zero => omega
  | succ count ih =>
    have both := Bool.and_eq_true_iff.mp checked
    by_cases same : i=start
    · simpa [same] using both.1
    · exact ih (start+1) both.2 (by omega) (by omega)

end CurrentMain.ComplexGeometry
#print axioms CurrentMain.ComplexGeometry.sourceRouteCheck_sound
#print axioms CurrentMain.ComplexGeometry.sourceRouteCheck_ranks
#print axioms CurrentMain.ComplexGeometry.rangeCheck_sound
