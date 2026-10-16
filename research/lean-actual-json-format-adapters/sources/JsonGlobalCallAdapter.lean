import JsonOwnerFieldAdapter

/-!
Reusable selection of the actual GLOBAL-TEMPLATE calls array, followed by the
accepted strict owners-field decoder and checked ordered assignment gather.
The source emitter writes calls in its explicit call_order; this adapter selects
that array position, never an object iteration position or a stage/replica key.

The expected call count k is checked against the actual array before a Fin k
position is used. Missing fields, a nonarray calls field, and count mismatch fail.
The selected call is then processed by the existing complete two-field row and
route decoder. Its projected families are checked against assignment position.
The function assignment can be the existing source-matched certified owner table;
no owner literals or injectivity proofs are duplicated here.

Success derives the actual global-field lookup, exact indexed call, complete
selected owners AST and ordered logical payload output. Other calls and metadata
are not validated, and repeated owners remain allowed. Successful checking for an
actual selected artifact, byte parsing, duplicate-key/number-spelling policy,
stage/time semantics, physical L/C allocation, charts, executor and costs remain
separate. These generic statements do not establish a multiplication bound.
Author-checked context only: kappa=836330098538459/500000000000000000.
Credits: PR1094/T16 ordered emitter and owner-decoder lineage, accepted bank/frame
strict JSON/index/gather certificates, Lean and Mathlib. James Chang with OpenAI
assistance; Apache-2.0. Source prepared for independent review and bounded check.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.JsonGlobalCallAdapter
universe u v
open SelectedSourceSyntax (Value)
open JsonOwnerFieldAdapter (Row Matched rowValue callOwners gatherCall assignedCall)

/-- Exact array count is checked before selecting the original ordered position. -/
def selectCall (k : Nat) (global : Lean.Json) (position : Fin k) : Option Lean.Json :=
  match global.getObjVal? "calls" with
  | .error _ => none
  | .ok (.arr calls) => if calls.size = k then calls[position.val]? else none
  | .ok _ => none

theorem selectCall_missing {k : Nat} (global : Lean.Json) (position : Fin k)
    (message : String) (h : global.getObjVal? "calls" = .error message) :
    selectCall k global position = none := by
  simp only [selectCall, h]

theorem selectCall_wrong_count {k : Nat} (global : Lean.Json) (position : Fin k)
    (calls : Array Lean.Json) (h : global.getObjVal? "calls" = .ok (.arr calls))
    (hlen : calls.size ≠ k) : selectCall k global position = none := by
  simp only [selectCall, h, if_neg hlen]

/-- No successful selection can hide a wrong count or an out-of-range position. -/
theorem selectCall_sound {k : Nat} (global : Lean.Json) (position : Fin k)
    (call : Lean.Json) (h : selectCall k global position = some call) :
    ∃ calls : Array Lean.Json,
      global.getObjVal? "calls" = .ok (.arr calls) ∧ calls.size = k ∧
      ∃ hi : position.val < calls.size, calls[position.val]'hi = call := by
  cases hg : global.getObjVal? "calls" with
  | error message =>
      simp only [selectCall, hg] at h
      cases h
  | ok raw =>
      cases raw with
      | null =>
          simp only [selectCall, hg] at h
          cases h
      | bool b =>
          simp only [selectCall, hg] at h
          cases h
      | num z =>
          simp only [selectCall, hg] at h
          cases h
      | str s =>
          simp only [selectCall, hg] at h
          cases h
      | obj o =>
          simp only [selectCall, hg] at h
          cases h
      | arr calls =>
          by_cases hlen : calls.size = k
          · have hi : calls[position.val]? = some call := by
              simpa only [selectCall, hg, if_pos hlen] using h
            exact ⟨calls, rfl, hlen, Array.getElem?_eq_some_iff.mp hi⟩
          · simp only [selectCall, hg, if_neg hlen] at h
            cases h

/-- Completeness for an actual matching array lookup, without a supplied result. -/
theorem selectCall_of_array {k : Nat} (global : Lean.Json) (position : Fin k)
    (calls : Array Lean.Json) (hg : global.getObjVal? "calls" = .ok (.arr calls))
    (hlen : calls.size = k) :
    selectCall k global position = some (calls[position.val]'(hlen.symm ▸ position.isLt)) := by
  have hi : position.val < calls.size := hlen.symm ▸ position.isLt
  simpa only [selectCall, hg, if_pos hlen] using (Array.getElem?_eq_getElem hi)

/-- Reuse an existing call-indexed owner assignment, with an executed comparison. -/
def assignedAt (fuel n m k : Nat) {ρ : Type u} (routeDecoder : Value → Option ρ)
    (assignment : Fin k → Fin m → Fin n) (global : Lean.Json) (position : Fin k) :
    Option (Matched n m routeDecoder (assignment position)) :=
  match selectCall k global position with
  | none => none
  | some call => assignedCall fuel n m routeDecoder (assignment position) call

/-- Logical reads remain out-of-place and unpriced, as in the accepted gather. -/
def gatherAt {n k : Nat} {ρ : Type u} {α : Type v} (fuel : Nat)
    (routeDecoder : Value → Option ρ) (store : Fin n → α)
    (global : Lean.Json) (position : Fin k) : Option (List α) :=
  match selectCall k global position with
  | none => none
  | some call => gatherCall fuel routeDecoder store call

/-- Actual composed success binds all selection and row data and derives output. -/
theorem assignedAt_sound {n m k : Nat} {ρ : Type u} {α : Type v} (fuel : Nat)
    (routeDecoder : Value → Option ρ) (assignment : Fin k → Fin m → Fin n)
    (store : Fin n → α) (global : Lean.Json) (position : Fin k)
    (r : Matched n m routeDecoder (assignment position))
    (h : assignedAt fuel n m k routeDecoder assignment global position = some r) :
    (∃ (calls : Array Lean.Json) (call raw : Lean.Json),
      global.getObjVal? "calls" = .ok (.arr calls) ∧ calls.size = k ∧
      (∃ hi : position.val < calls.size, calls[position.val]'hi = call) ∧
      callOwners fuel n routeDecoder call = some r.val ∧
      call.getObjVal? "owners" = .ok raw ∧
      StrictJsonValueBridge.reencode fuel (Value.array (r.val.map rowValue)) = raw) ∧
    gatherAt fuel routeDecoder store global position =
      some (List.ofFn (fun i => store (assignment position i))) := by
  cases hs : selectCall k global position with
  | none =>
      simp only [assignedAt, hs] at h
      cases h
  | some call =>
      have ha : assignedCall fuel n m routeDecoder (assignment position) call = some r := by
        simpa only [assignedAt, hs] using h
      obtain ⟨hc, ho⟩ := JsonOwnerFieldAdapter.assignedCall_sound fuel routeDecoder
        (assignment position) store call r ha
      obtain ⟨calls, hg, hlen, hi⟩ := selectCall_sound global position call hs
      obtain ⟨raw, hr, hv⟩ := JsonOwnerFieldAdapter.callOwners_sound fuel routeDecoder call r.val hc
      refine ⟨⟨calls, call, raw, hg, hlen, hi, hc, hr, hv⟩, ?_⟩
      simpa only [gatherAt, hs] using ho

end CurrentMain.JsonGlobalCallAdapter
#print axioms CurrentMain.JsonGlobalCallAdapter.selectCall_missing
#print axioms CurrentMain.JsonGlobalCallAdapter.selectCall_wrong_count
#print axioms CurrentMain.JsonGlobalCallAdapter.selectCall_sound
#print axioms CurrentMain.JsonGlobalCallAdapter.selectCall_of_array
#print axioms CurrentMain.JsonGlobalCallAdapter.assignedAt_sound
#check @CurrentMain.JsonGlobalCallAdapter.assignedAt_sound
