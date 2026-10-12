/- Mathematical rejection controls for the verified owner-table checker. -/
import OwnerTable
namespace OwnerTransport.OwnerTableControls
open OwnerTable

def fixture : Table where
  ports := 1
  children := 1
  replicas := 2
  helpers := 2
  calls := 2
  lanes := 1
  row := fun i =>
    (#[Role.mk 0 0 0 0 0 0 0 0 0 1 0 0,
       Role.mk 0 1 0 0 1 0 0 1 0 2 0 1,
       Role.mk 1 0 1 0 0 0 0 0 1 1 1 0,
       Role.mk 1 1 1 0 1 0 0 1 2 2 1 1][i]?).getD default
  group := fun g => if g = 0 then [0, 2] else [1, 3]
  byFamily := fun t => if t = 0 then [0, 1] else [2, 3]
  window := fun _ => ⟨4, [0, 1]⟩
  call := fun t => (t, 0)
  width := fun helper => helper + 1
  lane := fun _ => 0

theorem fixture_accepted : checkTable fixture = true := by decide

def changedRow (index : Nat) (change : Role → Role) : Table :=
  { fixture with row := fun i => if i = index then change (fixture.row i) else fixture.row i }

theorem overlapping_row_rejected :
    checkTable (changedRow 2 (fun r => {r with offset := 0})) = false := by decide

theorem orphaned_row_rejected :
    checkTable (changedRow 2 (fun r => {r with slot := 0})) = false := by decide

theorem missing_family_reference_rejected :
    checkTable (changedRow 1 (fun r => {r with familyRank := 0})) = false := by decide

theorem insufficient_capacity_rejected :
    checkTable {fixture with window := fun _ => ⟨1, [0, 1]⟩} = false := by decide

theorem wrong_window_rejected :
    checkTable {fixture with window := fun _ => ⟨4, [0]⟩} = false := by decide

theorem duplicate_helper_rejected :
    checkTable (changedRow 1 (fun r => {r with helper := 0})) = false := by decide

theorem changed_source_width_rejected :
    checkTable (changedRow 1 (fun r => {r with width := 1})) = false := by decide

theorem wrong_physical_family_rejected :
    checkTable (changedRow 1 (fun r => {r with family := 0})) = false := by decide

/-- A reordered family index is rejected, including its broken inverse links. -/
theorem reordered_families_rejected :
    checkTable {fixture with byFamily := fun _ => [1, 0]} = false := by decide

end OwnerTransport.OwnerTableControls
