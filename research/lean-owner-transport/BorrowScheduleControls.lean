/- Regression controls for controller-window certification; Apache-2.0.
Rohan Arun with substantial OpenAI Codex assistance. -/
import BorrowSchedule
import OwnerTableControls
namespace OwnerTransport.BorrowScheduleControls
open OwnerTable BorrowSchedule

def table : Table := { OwnerTableControls.fixture with
  replicas := 1
  children := 1
  calls := 1
  lanes := 4
  call := fun _ => (0, 0)
  lane := fun _ => 0
  window := fun _ => ⟨2, [0]⟩ }

def localEvent : Event := ⟨some 0, [1], [], some (0, 0), false⟩
def idleEvent : Event := ⟨some 0, [0], [0], none, false⟩
def trace : Trace where
  count := 2
  event := fun p => if p = 1 then localEvent else idleEvent
  callPosition := fun _ => 1
  bounds := fun _ => (0, 2)

theorem window_accepted : checkWindow table trace 0 = true := by decide

theorem unknown_effects_rejected : checkWindow table
    { trace with event := fun p => if p = 1 then {localEvent with unknownEffects := true} else idleEvent } 0 = false := by decide

theorem active_data_touch_rejected : checkWindow table
    { trace with event := fun p => if p = 1 then {localEvent with touchedPairs := [0]} else idleEvent } 0 = false := by decide

theorem wrong_child_deadline_rejected : checkWindow table
    { trace with event := fun p => if p = 1 then localEvent else {idleEvent with idleChildren := [1]} } 0 = false := by decide

theorem boundary_call_rejected : checkWindow table
    { trace with bounds := fun _ => (1, 2) } 0 = false := by decide

theorem omitted_admissible_call_rejected :
    checkWindow {table with window := fun _ => ⟨2, []⟩} trace 0 = false := by decide

theorem unscoped_unknown_event_rejected : checkWindow table
    { trace with event := fun p => if p = 1 then {localEvent with replica := none, unknownEffects := true} else idleEvent } 0 = false := by decide

end OwnerTransport.BorrowScheduleControls
