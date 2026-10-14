import StrictJsonValueBridge
import CheckedTableGather

/-!
Reusable ordered logical payload reads from the actual Lean.Json AST.
The executable composition first runs the accepted strict AST decoder at the
array-of-scalars depth, then invokes the unchanged checked Value gather.
Successful bounded JSON-index decoding determines every returned payload in
original order, including repeated indices and arbitrary array lengths.

There is no permutation, uniqueness, length-equals-dimension or desired-output
premise. The array may be empty, including when the logical store dimension is
zero. Scalar tags and exponent-zero numeric representation are inherited from
the accepted AST bridge. This is not a claim about lexical integer spellings,
byte-parser correctness, current provider-field extraction or physical access.
The two functional traversals have no assigned time, copy or allocation price.

Author-checked context only:
kappa=836330098538459/500000000000000000=0.001672660197076918.
The generic theorem is independent of kappa and proves no multiplier bound.
Credits: accepted StrictJsonValueBridge, StrictParsedIndexCodec and
CheckedTableGather; Lean List/Option APIs. James Chang with OpenAI assistance;
Apache-2.0. Source preparation; native acceptance remains separate.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.JsonTableGather
universe u
open SelectedSourceSyntax (Value bounded)
open StrictParsedIndexCodec (indexValue bounded_eq_some_iff)

/-- Execute the actual AST conversion and then the existing ordered read program.
Fuel two covers the outer array and its scalar entries; it is not a cost bound. -/
def gather {n : Nat} {α : Type u} (store : Fin n → α) (raw : Lean.Json) :
    Option (List α) :=
  match StrictJsonValueBridge.decode 2 raw with
  | none => none
  | some v => CheckedTableGather.gather store v

/-- Actual bounded index-decoder success fixes the complete actual read output.
No distinctness or exact-length restriction is imposed on the ordered indices. -/
theorem gather_of_indices {n : Nat} {α : Type u} (store : Fin n → α)
    (raw : Lean.Json) (xs : List (Fin n))
    (h : StrictJsonValueBridge.indices n raw = some xs) :
    gather store raw = some (xs.map store) := by
  have hraw := (StrictJsonValueBridge.indices_eq_some_iff n raw xs).mp h
  subst raw
  have hdecode : StrictJsonValueBridge.decode 2 (StrictJsonValueBridge.indexArrayJson xs) =
      some (Value.array (xs.map indexValue)) := by
    change ((xs.map StrictJsonValueBridge.indexJson).mapM (StrictJsonValueBridge.decode 1)
      >>= fun vs => some (Value.array vs)) = some (Value.array (xs.map indexValue))
    rw [List.mapM_map]
    have hd : StrictJsonValueBridge.decode 1 ∘ StrictJsonValueBridge.indexJson =
        (fun i : Fin n => some (indexValue i)) := rfl
    have hm : xs.mapM (fun i => some (indexValue i)) = some (xs.map indexValue) :=
      List.mapM_pure
    rw [hd, hm]
    all_goals rfl
  unfold gather
  rw [hdecode]
  change CheckedTableGather.gather store (Value.array (xs.map indexValue)) =
    some (xs.map store)
  change (xs.map indexValue).mapM (fun v => (bounded n v).map store) =
    some (xs.map store)
  rw [List.mapM_map]
  have hread : (fun v : Value => (bounded n v).map store) ∘ indexValue =
      (fun i : Fin n => some (store i)) := by
    funext i
    change (bounded n (indexValue i)).map store = some (store i)
    rw [(bounded_eq_some_iff n (indexValue i) i).mpr rfl]
    rfl
  rw [hread]
  exact List.mapM_pure

end CurrentMain.JsonTableGather
#print axioms CurrentMain.JsonTableGather.gather_of_indices
#check @CurrentMain.JsonTableGather.gather_of_indices
