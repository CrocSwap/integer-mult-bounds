import CoordinateSwap

/-!
Exact boundary examples for whole-residual hosting. Apache-2.0.
Prepared with substantial OpenAI Codex assistance.

These witnesses explain why endpoint independence, disjointness, containment,
and common-chart commutation appear as hypotheses. They are not tests of a
repository-generated word and do not assert a flaw in a particular template.
-/

namespace WholeHosting.Boundary

/-- This map preserves the host, but another output reads the host. -/
def readHost (s : Int × Int) : Int × Int := (s.1, s.2 + s.1)

def flipHost (s : Int × Int) : Int × Int := (-s.1, s.2)

theorem readHost_preserves_host (s : Int × Int) : (readHost s).1 = s.1 := rfl

/-- Merely preserving the host is weaker than commuting with its residual. -/
theorem host_preservation_not_commutation :
    readHost (flipHost (1, 0)) ≠ flipHost (readHost (1, 0)) := by
  decide

def fullMask : Mask Unit := fun _ => true

def witnessAddress : Address Unit Bool := fun _ => (false, true)

def witnessStream : Stream Unit Bool Bool := fun address => (address ()).1

theorem overlapping_masks_not_disjoint : ¬ MasksDisjoint fullMask fullMask := by
  intro h
  have impossible := h () rfl
  contradiction

/-- Repeating a bit factor cancels it; a union would count it once. -/
theorem overlapping_masks_not_union :
    bitAction fullMask (bitAction fullMask witnessStream) ≠
      bitAction (unionMask fullMask fullMask) witnessStream := by
  intro h
  have impossible := congrFun h witnessAddress
  contradiction

/-- Removing a hosted mask outside the pending child cannot recover the child. -/
theorem outside_pending_not_completion :
    bitAction (remainderMask (fun _ => false) fullMask)
        (bitAction fullMask witnessStream) ≠
      bitAction (fun _ => false) witnessStream := by
  intro h
  have impossible := congrFun h witnessAddress
  contradiction

/-- Four coordinate positions suffice to distinguish a common chart from
unrelated charts. The permutations below reindex these positions. -/
inductive Slot where
  | a | b | c | d
  deriving DecidableEq, Repr

def swapAB : Slot → Slot
  | .a => .b
  | .b => .a
  | .c => .c
  | .d => .d

def swapCD : Slot → Slot
  | .a => .a
  | .b => .b
  | .c => .d
  | .d => .c

def chartBC : Slot → Slot
  | .a => .a
  | .b => .c
  | .c => .b
  | .d => .d

/-- Each coordinate permutation is invertible, with itself as inverse. -/
theorem swapAB_involution (i : Slot) : swapAB (swapAB i) = i := by
  cases i <;> rfl

theorem swapCD_involution (i : Slot) : swapCD (swapCD i) = i := by
  cases i <;> rfl

theorem chartBC_involution (i : Slot) : chartBC (chartBC i) = i := by
  cases i <;> rfl

theorem same_chart_commute (i : Slot) : swapAB (swapCD i) = swapCD (swapAB i) := by
  cases i <;> rfl

/-- Change the chart of just one factor: (b c) (c d) (b c) = (b d). -/
def otherChartCD (i : Slot) : Slot := chartBC (swapCD (chartBC i))

/-- The factors originally commute, but independent conjugation can destroy it. -/
theorem different_charts_not_commute :
    swapAB (otherChartCD .a) ≠ otherChartCD (swapAB .a) := by
  decide

end WholeHosting.Boundary

#print axioms WholeHosting.Boundary.readHost_preserves_host
#print axioms WholeHosting.Boundary.host_preservation_not_commutation
#print axioms WholeHosting.Boundary.overlapping_masks_not_disjoint
#print axioms WholeHosting.Boundary.overlapping_masks_not_union
#print axioms WholeHosting.Boundary.outside_pending_not_completion
#print axioms WholeHosting.Boundary.swapAB_involution
#print axioms WholeHosting.Boundary.swapCD_involution
#print axioms WholeHosting.Boundary.chartBC_involution
#print axioms WholeHosting.Boundary.same_chart_commute
#print axioms WholeHosting.Boundary.different_charts_not_commute
