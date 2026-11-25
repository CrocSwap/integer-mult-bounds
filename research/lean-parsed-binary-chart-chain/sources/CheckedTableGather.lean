import CheckedPermutationTables
import Init.Data.List.Monadic
import Init.Data.List.OfFn

/-!
UNCOMPILED reusable interpretation of parsed index arrays as ordered reads.
The executable gather below independently visits each actual parsed token,
checks its integer bound and reads the supplied finite logical store. Existing
strict table/permutation decoding is used to prove what that read sequence
returns. No equality of complete output lists is a premise.

The store value type and dimension are parameters. General gathers retain
ordered repetitions; successful permutation checking additionally supplies the
forward and backward reindexings. Empty dimensions are included. This is an
out-of-place functional read semantics, without a physical address model or
any price for lookup, copying, allocation or parsing. It does not implement an
in-place permutation or restore an overwritten destination. Byte parsing,
physical charts and actual executor/bit-cost refinement remain separate.

Credits: accepted StrictParsedIndexCodec and CheckedPermutationTables;
Lean List/Option/Fin infrastructure. Their upstream lineage and notices remain
unchanged. Apache-2.0; prepared with OpenAI assistance.
Author-checked context only: kappa=836330098538459/500000000000000000.
No selected literal table or kappa premise occurs in these generic theorems.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.CheckedTableGather
universe u
open SelectedSourceSyntax (Value bounded)
open StrictParsedIndexCodec (indexValue bounded_eq_some_iff)
open CheckedPermutationTables

/-- Visit the actual ordered tokens. Every read follows a successful bound check.
There is deliberately no length restriction here: the checker supplies it when
this general read sequence is used as a permutation application. -/
def gather {n : Nat} {α : Type u} (store : Fin n → α) : Value → Option (List α)
  | .array xs => xs.mapM (fun v => (bounded n v).map store)
  | _ => none

/-- Canonical checked entries execute as the same ordered list of logical reads. -/
theorem gather_table {n : Nat} {α : Type u} (store : Fin n → α) (t : Table n) :
    gather store (tableValue t) = some (t.val.map store) := by
  change (t.val.map indexValue).mapM (fun v => (bounded n v).map store) =
    some (t.val.map store)
  rw [List.mapM_map]
  have hread : (fun v : Value => (bounded n v).map store) ∘ indexValue =
      (fun i : Fin n => some (store i)) := by
    funext i
    change (bounded n (indexValue i)).map store = some (store i)
    rw [(bounded_eq_some_iff n (indexValue i) i).mpr rfl]
    rfl
  rw [hread]
  exact List.mapM_pure

/-- Actual decoder success derives actual gather success and every output value. -/
theorem gather_decoded_table {n : Nat} {α : Type u} (store : Fin n → α)
    (raw : Value) (t : Table n) (h : decodeTable n raw = some t) :
    gather store raw = some (t.val.map store) := by
  rw [← decodeTable_sound raw t h]
  exact gather_table store t

private theorem table_map_eq_ofFn {n : Nat} {α : Type u}
    (t : Table n) (store : Fin n → α) :
    t.val.map store = List.ofFn (fun i => store (tableAt t i)) := by
  apply List.ext_getElem
  · simp only [List.length_map, List.length_ofFn, t.property]
  · intro i hi₁ hi₂
    simp only [List.getElem_map, List.getElem_ofFn, tableAt,
      List.get_eq_getElem, Fin.cast]

/-- Both actual parsed read programs agree with the checked permutation's
forward and inverse lookups, in index order, for arbitrary stored payloads.
This identifies the pullback convention: output i reads old store (p i). -/
theorem gather_checked_permutation {n : Nat} {α : Type u} (store : Fin n → α)
    (forward backward : Value) (p : Equiv.Perm (Fin n))
    (h : decodePermutation n forward backward = some p) :
    gather store forward = some (List.ofFn (fun i => store (p i))) ∧
    gather store backward = some (List.ofFn (fun i => store (p.symm i))) := by
  obtain ⟨c, _hc, _hcheck, hf, hb, hforward, hbackward⟩ :=
    decodePermutation_sound forward backward p h
  constructor
  · rw [← hf, gather_table, table_map_eq_ofFn]
    simp only [hforward]
  · rw [← hb, gather_table, table_map_eq_ofFn]
    simp only [hbackward]

end CurrentMain.CheckedTableGather
#print axioms CurrentMain.CheckedTableGather.gather_table
#print axioms CurrentMain.CheckedTableGather.gather_decoded_table
#print axioms CurrentMain.CheckedTableGather.gather_checked_permutation
#check @CurrentMain.CheckedTableGather.gather_checked_permutation
