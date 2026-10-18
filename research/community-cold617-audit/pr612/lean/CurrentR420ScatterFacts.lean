import CurrentR420BBandCheck

/-! Six exact current R420 scatter/index facts, preserving the original statements
and proof bodies. They bind120 scatter rows/568 indices to nine retained helpers,
and the fresh Fin660 embedding in Fin661 with temporary660. This is only the
finite lookup/domain boundary; COPY overwrite/clear semantics, actual A/C/D
composition and physical transport remain separate. Prepared with OpenAI
assistance; supplier and accepted core attribution retained. -/
namespace CurrentMain.CurrentR420Boundary
open Data
set_option Elab.async false

theorem scatter_shape : scatter.length = 120 ∧
    (scatter.map List.length).foldl Nat.add 0 = 568 := by decide +kernel
#print axioms CurrentMain.CurrentR420Boundary.scatter_shape

theorem scatter_index_domain : scatter.all (fun row =>
    row.all (fun k => decide (k < ret.length))) = true := by decide +kernel
#print axioms CurrentMain.CurrentR420Boundary.scatter_index_domain

theorem scatter_helpers : scatter.all (fun row => row.all (fun k =>
    match ret[k]? with
    | none => false
    | some r => decide (240 ≤ r ∧ r < 660))) = true := by decide +kernel
#print axioms CurrentMain.CurrentR420Boundary.scatter_helpers

theorem temporary_index : temporary.val = 660 ∧ temporary.val < 661 := by decide +kernel
#print axioms CurrentMain.CurrentR420Boundary.temporary_index

theorem embed_preserves_index (r : Reg) : (embed r).val = r.val := rfl
#print axioms CurrentMain.CurrentR420Boundary.embed_preserves_index

theorem original_excludes_temporary (r : Reg) : embed r ≠ temporary := by
  intro h
  have hv : r.val = 660 := congrArg Fin.val h
  exact (Nat.ne_of_lt r.isLt) hv
#print axioms CurrentMain.CurrentR420Boundary.original_excludes_temporary

end CurrentMain.CurrentR420Boundary
