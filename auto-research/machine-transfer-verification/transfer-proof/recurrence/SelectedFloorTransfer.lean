import FloorRecurrence
import SelectedProfileReal

/-! Exact floor recurrence and row-stock specialization to the certified
27-row ranked-pair profile. The characteristic inequality is a proved real
theorem; physical_recurrence is the one remaining cost contract below.
-/
namespace SelectedFloorTransfer
open SelectedProfileCertificate

def maxChild : ℕ := 529

theorem maxChild_lt : maxChild < m := by norm_num [maxChild, m]

theorem all_widths_le_max : rows.all (fun r => decide (r.width ≤ maxChild)) = true := by
  decide +kernel

theorem width_le_max (r : Row) (hr : r ∈ rows) : r.width ≤ maxChild := by
  exact of_decide_eq_true (List.all_eq_true.mp all_widths_le_max r hr)

def depth (e : ℕ) : ℕ := FloorDepth.depth m maxChild maxChild_lt e

theorem depth_below_base (e : ℕ) (he : e < m) : depth e = 0 :=
  FloorDepth.depth_base m maxChild maxChild_lt e he

theorem depth_internal (e : ℕ) (he : m ≤ e) :
    depth e = 1 + depth (maxChild * (e / m)) :=
  FloorDepth.depth_step m maxChild maxChild_lt e he

theorem depth_monotone : Monotone depth := FloorDepth.depth_mono m maxChild maxChild_lt

theorem child_depth_drop (r : Row) (hr : r ∈ rows) (e : ℕ) (he : m ≤ e) :
    depth (r.width * (e / m)) + 1 ≤ depth e :=
  FloorDepth.child_depth_drop m maxChild r.width e maxChild_lt (width_le_max r hr) he

theorem depth_logarithmic (e : ℕ) (he : 0 < e) :
    (depth e : ℝ) ≤ 1 + Real.log (e : ℝ) / Real.log ((575 : ℝ) / 529) := by
  exact FloorRecurrence.depth_log_bound m maxChild maxChild_lt (by norm_num [maxChild]) e he

theorem exact_row_split (e R : ℕ) (he : m ≤ e) (stock : W ^ depth e ∣ R) :
    W * (R / W) = R := FloorDepth.row_split_exact m maxChild e W R maxChild_lt he stock

theorem child_row_stock (r : Row) (hr : r ∈ rows) (e R : ℕ) (he : m ≤ e)
    (stock : W ^ depth e ∣ R) : W ^ depth (r.width * (e / m)) ∣ R / W :=
  FloorDepth.child_row_stock m maxChild r.width e W R maxChild_lt (width_le_max r hr) he
    (by norm_num [W]) stock

noncomputable def costConstant (f : ℕ → ℝ) (C : ℝ) : ℝ :=
  FloorRecurrence.boundConstant m f C SelectedProfileReal.powerCharacteristic

theorem costConstant_nonneg (f : ℕ → ℝ) (C : ℝ) : 0 ≤ costConstant f C :=
  FloorRecurrence.boundConstant_nonneg m f C SelectedProfileReal.powerCharacteristic
    SelectedProfileReal.actual_power_characteristic_lt_one

/-- An unconditional analytic characteristic and a constructive finite-base
constant reduce every integer-width power bound to this exact cost contract.
No monotonicity assumption on f or ceiling-envelope cost is present. -/
theorem all_width_cost_bound (f : ℕ → ℝ) (C : ℝ)
    (physical_recurrence : ∀ e, m ≤ e →
      f e ≤ C + (rows.map (fun r => (r.multiplicity : ℝ) / W *
        f (r.width * (e / m)))).sum) :
    ∀ e, 0 < e → f e ≤ costConstant f C * (e : ℝ) ^ (1 - (saving : ℝ)) := by
  apply FloorRecurrence.finite_base_all_width rows
    (fun r => (r.multiplicity : ℝ) / W) (fun r => r.width) m f
    (1 - (saving : ℝ)) C SelectedProfileReal.powerCharacteristic
  · norm_num [m]
  · norm_num [saving]
  · intro r hr; positivity
  · intro r hr; exact (SelectedProfileReal.row_valid r hr).1
  · intro r hr; exact (SelectedProfileReal.row_valid r hr).2.1
  · rfl
  · exact SelectedProfileReal.actual_power_characteristic_lt_one
  · exact physical_recurrence

end SelectedFloorTransfer

#print axioms SelectedFloorTransfer.maxChild_lt
#print axioms SelectedFloorTransfer.all_widths_le_max
#print axioms SelectedFloorTransfer.width_le_max
#print axioms SelectedFloorTransfer.depth_below_base
#print axioms SelectedFloorTransfer.depth_internal
#print axioms SelectedFloorTransfer.depth_monotone
#print axioms SelectedFloorTransfer.child_depth_drop
#print axioms SelectedFloorTransfer.depth_logarithmic
#print axioms SelectedFloorTransfer.exact_row_split
#print axioms SelectedFloorTransfer.child_row_stock
#print axioms SelectedFloorTransfer.costConstant_nonneg
#print axioms SelectedFloorTransfer.all_width_cost_bound
