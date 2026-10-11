import Lean
namespace CurrentMain.AliasLifetimes
structure Row where
 donor : Nat
 recipient : Nat
 physicalSlot : Nat
 readTick : Nat
 donorLast : Nat
 recipientFirst : Nat
 deriving DecidableEq, Repr

def Valid (r : Row) : Prop := r.donor < 10732 ∧ 10732 ≤ r.recipient ∧ r.recipient < 13042 ∧ r.physicalSlot < 10686 ∧ r.donorLast < r.readTick ∧ r.readTick ≤ r.recipientFirst ∧ r.recipientFirst < 32971
instance (r : Row) : Decidable (Valid r) := by unfold Valid; infer_instance
def check (rows : List Row) : Bool := rows.all (fun r => decide (Valid r))
theorem checked_valid (rows : List Row) (h : check rows = true) (r : Row) (hr : r ∈ rows) : Valid r := by
 exact of_decide_eq_true ((List.all_eq_true.mp h) r hr)
theorem donor_recipient_distinct (r : Row) (h : Valid r) : r.donor ≠ r.recipient := by
 unfold Valid at h
 omega
end CurrentMain.AliasLifetimes
#print axioms CurrentMain.AliasLifetimes.checked_valid
#print axioms CurrentMain.AliasLifetimes.donor_recipient_distinct
