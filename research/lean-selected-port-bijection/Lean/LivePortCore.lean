import LivePortBirthData
import LivePortDeathData
import LivePortDonorData
import LivePortRemovedData
namespace CurrentMain.LivePorts
open CurrentMain.SignedTrace CurrentMain.SignedWord

def representative (r : Nat) : Nat := if r < 10732 then r else get donorTable (r-10732)
def activeAt (tick role : Nat) : Prop := get birthTable role ≤ tick ∧ tick < get deathTable role
instance (t r : Nat) : Decidable (activeAt t r) := by unfold activeAt; infer_instance
def portCheck (tick : Nat) (a : Annotation) : Bool :=
  decide (a.step.dst < 13042 ∧ a.step.src < 13042 ∧ get removedTable a.step.src = 0) &&
  (if get removedTable a.step.dst = 1 then true else
    decide (activeAt tick a.step.dst ∧ activeAt tick a.step.src ∧
      representative a.step.dst ≠ representative a.step.src))
def blockCheck (start : Nat) (as : List Annotation) : Bool :=
  (as.zipIdx start).all (fun p => portCheck p.2 p.1)
theorem retained_ports_sound (tick : Nat) (a : Annotation)
    (h : portCheck tick a = true) (retained : get removedTable a.step.dst ≠ 1) :
    activeAt tick a.step.dst ∧ activeAt tick a.step.src ∧
      representative a.step.dst ≠ representative a.step.src := by
  have hh := Bool.and_eq_true_iff.mp h
  simpa only [portCheck, if_neg retained] using of_decide_eq_true (show decide (activeAt tick a.step.dst ∧ activeAt tick a.step.src ∧ representative a.step.dst ≠ representative a.step.src) = true by simpa only [if_neg retained] using hh.2)
end CurrentMain.LivePorts
#print axioms CurrentMain.LivePorts.retained_ports_sound
