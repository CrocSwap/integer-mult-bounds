/- Exact data derived from pinned owner records; regenerate with generate.py. -/
import OwnerTransport
namespace OwnerTransport.PR531

def templates : List (Nat × List Nat) := [
  (8, [8]),
  (16, [8, 8]),
  (16, [9]),
  (32, [9, 9, 9]),
  (48, [9, 9, 9, 9, 9])]

def widthAt (ws : List Nat) (i : Nat) : Nat := (ws[i]?).getD 0

def Fits (t : Nat × List Nat) : Prop :=
  offset (widthAt t.2) t.2.length ≤ t.1

instance (t : Nat × List Nat) : Decidable (Fits t) :=
  inferInstanceAs (Decidable (offset (widthAt t.2) t.2.length ≤ t.1))

/-- Every extracted packing template passes the Lean kernel's arithmetic check. -/
theorem all_templates_fit : templates.all (fun t => decide (Fits t)) = true := by
  decide

/-- Membership in the checked table supplies the actual capacity hypothesis. -/
theorem listed_template_fits (t : Nat × List Nat) (h : t ∈ templates) : Fits t := by
  have ht := (List.all_eq_true.mp all_templates_fit) t h
  exact of_decide_eq_true ht

/-- Each listed template defines legal addresses for all its occupied coordinates. -/
theorem listed_address_lt (t : Nat × List Nat) (h : t ∈ templates)
    (i k : Nat) (hi : i < t.2.length) (hk : k < widthAt t.2 i) :
    offset (widthAt t.2) i + k < t.1 := by
  exact transported_address_lt (widthAt t.2) (widthAt t.2) t.2.length t.1 i k
    (fun _ _ => Nat.le_refl _) (listed_template_fits t h) hi hk

/-- The table's occupied coordinates form a nonaliasing, gap-free prefix. -/
theorem listed_template_correct (t : Nat × List Nat) (h : t ∈ templates) :
    offset (widthAt t.2) t.2.length ≤ t.1 ∧
    (∀ i j a b, a < widthAt t.2 i → b < widthAt t.2 j →
      offset (widthAt t.2) i + a = offset (widthAt t.2) j + b → i = j ∧ a = b) ∧
    (∀ x, x < offset (widthAt t.2) t.2.length →
      ∃ i, i < t.2.length ∧ ∃ k, k < widthAt t.2 i ∧ offset (widthAt t.2) i + k = x) := by
  exact compaction_correct (widthAt t.2) (widthAt t.2) t.2.length t.1
    (fun _ _ => Nat.le_refl _) (listed_template_fits t h)

end OwnerTransport.PR531
