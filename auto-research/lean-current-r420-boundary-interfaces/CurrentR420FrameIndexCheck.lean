import CurrentR420BoundaryData
import Init.Data.List.Sort.Lemmas
import Init.Data.List.Nat.Range

/-! Exact first three declarations from the preserved R420 domain Check.
This bounded index diagnostic places each original axiom probe immediately
behind its declaration. It does not localize the earlier allocation failure
until an actual diagnostic result is observed. Remaining groups and the
original-name composition wrapper stay planned and unactivated.
Prepared with OpenAI assistance; supplier and core attribution retained. -/
namespace CurrentMain.CurrentR420Boundary
open Data
set_option Elab.async false

theorem selected_shape :
    h = 8 ∧ v = 120 ∧ R = 420 ∧ registers = 660 ∧
    format = "bitE8/1+mut" ∧ form = "<x,y>/2" ∧ coords = "ham" := by decide +kernel
#print axioms CurrentMain.CurrentR420Boundary.selected_shape

theorem line_shape :
    lines.length = 120 ∧ lines.all (fun row => row.length == 8) = true :=
  SelectedBitCarrierBoundary.line_shape
#print axioms CurrentMain.CurrentR420Boundary.line_shape

theorem frame_index_permutation :
    (frameOrder.map Fin.val).mergeSort (fun a b => decide (a ≤ b)) = List.range 672 := by
  have hc : (frameOrder.map Fin.val).isPerm (List.range 672) = true := by
    decide +kernel
  have hp : List.Perm (frameOrder.map Fin.val) (List.range 672) :=
    List.isPerm_iff.mp hc
  have hs : List.Pairwise (fun a b : Nat => a ≤ b)
      ((frameOrder.map Fin.val).mergeSort (fun a b => decide (a ≤ b))) := by
    have h := List.sorted_mergeSort (le := fun a b : Nat => decide (a ≤ b))
      (fun a b c hab hbc => decide_eq_true
        (Nat.le_trans (of_decide_eq_true hab) (of_decide_eq_true hbc)))
      (fun a b => by
        apply Bool.or_eq_true_iff.mpr
        rcases Nat.le_total a b with h | h
        · exact Or.inl (decide_eq_true h)
        · exact Or.inr (decide_eq_true h))
      (frameOrder.map Fin.val)
    exact h.imp (fun hab => of_decide_eq_true hab)
  exact List.Perm.eq_of_sorted
    (fun a b _ _ hab hba => Nat.le_antisymm hab hba)
    hs List.pairwise_le_range
    ((List.mergeSort_perm _ _).trans hp)
#print axioms CurrentMain.CurrentR420Boundary.frame_index_permutation

end CurrentMain.CurrentR420Boundary
