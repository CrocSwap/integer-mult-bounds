import JsonTableGather

/-!
A reusable adapter for the existing call-object owners field and its exact
[family, route] row shape. The family bound and route-decoder implementation
are parameters. Each successful row retains the complete raw route Value,
its decoded result and the actual route-decoder equation. The existing selected
route decoder can be passed unchanged; this module invents no route grammar.

The installed Lean.Json object lookup selects the named owners field. Its
array is traversed in order, with all repeated entries preserved. Missing fields,
nonobjects, nonarrays, wrong row arity, invalid families and failed route decoding
return none. Other call metadata is not checked or interpreted here. Objects
already use a tree representation: no insertion order or duplicate-byte-key
property is inferred from field lookup.

An optional executable assignment comparison checks the projected family list
against an existing finite owner function. Its success, rather than a desired
output premise, derives the ordered logical payload reads. No uniqueness is
required; an application's accepted owner-injection theorem remains reusable.
Byte parsing, selection of a call from the global template, physical allocation,
route/chart semantics, read/copy cost and actual executor refinement are separate.
Author-checked context only: kappa=836330098538459/500000000000000000.
The generic statements do not use kappa or establish a multiplier bound.
James Chang with OpenAI assistance; Apache-2.0. Credits: source-matched owner-row
format, accepted strict JSON/index/gather interfaces, and official Lean APIs.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.JsonOwnerFieldAdapter
universe u v
open SelectedSourceSyntax (Value bounded)
open StrictParsedIndexCodec (indexValue bounded_eq_some_iff mapM_reencode)

/-- Complete raw route retention is independent of any interpretation of it. -/
structure Row (n : Nat) {ρ : Type u} (routeDecoder : Value → Option ρ) where
  family : Fin n
  rawRoute : Value
  route : ρ
  route_ok : routeDecoder rawRoute = some route

def rowValue {n : Nat} {ρ : Type u} {routeDecoder : Value → Option ρ}
    (r : Row n routeDecoder) : Value := .array [indexValue r.family, r.rawRoute]

/-- Exact two-field source syntax, with no default or modulo family coercion. -/
def decodeRow (n : Nat) {ρ : Type u} (routeDecoder : Value → Option ρ) :
    Value → Option (Row n routeDecoder)
  | .array [fv, rv] =>
      match bounded n fv with
      | none => none
      | some f =>
          match h : routeDecoder rv with
          | none => none
          | some r => some ⟨f, rv, r, h⟩
  | _ => none

theorem decodeRow_sound {n : Nat} {ρ : Type u} (routeDecoder : Value → Option ρ)
    (raw : Value) (r : Row n routeDecoder) (h : decodeRow n routeDecoder raw = some r) :
    rowValue r = raw := by
  cases raw with
  | text s => cases h
  | integer z => cases h
  | boolean b => cases h
  | other => cases h
  | array xs =>
      cases xs with
      | nil => cases h
      | cons fv tail =>
          cases tail with
          | nil => cases h
          | cons rv rest =>
              cases rest with
              | cons x rest => cases h
              | nil =>
                  cases hf : bounded n fv with
                  | none =>
                      simp only [decodeRow, hf] at h
                      cases h
                  | some f =>
                      simp only [decodeRow, hf] at h
                      split at h
                      · cases h
                      · rename_i route hr
                        have he : (⟨f, rv, route, hr⟩ : Row n routeDecoder) = r := Option.some.inj h
                        cases he
                        have hv : fv = indexValue f := (bounded_eq_some_iff n fv f).mp hf
                        subst fv
                        rfl

/-- Failed rows fail the whole traversal; successful rows retain original order. -/
def decodeRows (n : Nat) {ρ : Type u} (routeDecoder : Value → Option ρ) :
    Value → Option (List (Row n routeDecoder))
  | .array xs => xs.mapM (decodeRow n routeDecoder)
  | _ => none

theorem decodeRows_sound {n : Nat} {ρ : Type u} (routeDecoder : Value → Option ρ)
    (raw : Value) (rows : List (Row n routeDecoder))
    (h : decodeRows n routeDecoder raw = some rows) :
    Value.array (rows.map rowValue) = raw := by
  cases raw with
  | text s => cases h
  | integer z => cases h
  | boolean b => cases h
  | other => cases h
  | array xs =>
      exact congrArg Value.array (mapM_reencode (decodeRow n routeDecoder) rowValue
        (decodeRow_sound routeDecoder) xs rows h)

/-- Lookup selects a field, never a position in a dictionary iteration order. -/
def callOwners (fuel n : Nat) {ρ : Type u} (routeDecoder : Value → Option ρ)
    (call : Lean.Json) : Option (List (Row n routeDecoder)) :=
  match call.getObjVal? "owners" with
  | .error _ => none
  | .ok raw =>
      match StrictJsonValueBridge.decode fuel raw with
      | none => none
      | some values => decodeRows n routeDecoder values

theorem callOwners_missing (fuel n : Nat) {ρ : Type u} (routeDecoder : Value → Option ρ)
    (call : Lean.Json) (message : String) (h : call.getObjVal? "owners" = .error message) :
    callOwners fuel n routeDecoder call = none := by
  simp only [callOwners, h]

theorem callOwners_sound {n : Nat} {ρ : Type u} (fuel : Nat)
    (routeDecoder : Value → Option ρ) (call : Lean.Json) (rows : List (Row n routeDecoder))
    (h : callOwners fuel n routeDecoder call = some rows) :
    ∃ raw, call.getObjVal? "owners" = .ok raw ∧
      StrictJsonValueBridge.reencode fuel (Value.array (rows.map rowValue)) = raw := by
  cases ho : call.getObjVal? "owners" with
  | error message =>
      simp only [callOwners, ho] at h
      cases h
  | ok raw =>
      cases hd : StrictJsonValueBridge.decode fuel raw with
      | none =>
          simp only [callOwners, ho, hd] at h
          cases h
      | some values =>
          have hr : decodeRows n routeDecoder values = some rows := by
            simpa only [callOwners, ho, hd] using h
          refine ⟨raw, rfl, ?_⟩
          rw [decodeRows_sound routeDecoder values rows hr]
          exact StrictJsonValueBridge.decode_sound fuel raw values hd

/-- Logical read execution through the accepted actual-AST gather interface. -/
def gatherCall {n : Nat} {ρ : Type u} {α : Type v} (fuel : Nat)
    (routeDecoder : Value → Option ρ) (store : Fin n → α) (call : Lean.Json) :
    Option (List α) :=
  match callOwners fuel n routeDecoder call with
  | none => none
  | some rows => JsonTableGather.gather store
      (StrictJsonValueBridge.indexArrayJson (rows.map Row.family))

theorem gatherCall_of_success {n : Nat} {ρ : Type u} {α : Type v} (fuel : Nat)
    (routeDecoder : Value → Option ρ) (store : Fin n → α) (call : Lean.Json)
    (rows : List (Row n routeDecoder)) (h : callOwners fuel n routeDecoder call = some rows) :
    gatherCall fuel routeDecoder store call = some ((rows.map Row.family).map store) := by
  unfold gatherCall
  rw [h]
  exact JsonTableGather.gather_of_indices store _ _
    ((StrictJsonValueBridge.indices_eq_some_iff n _ _).mpr rfl)

/-- Existing certified assignments can be supplied without copying their tables. -/
def Matched (n m : Nat) {ρ : Type u} (routeDecoder : Value → Option ρ)
    (assignment : Fin m → Fin n) :=
  { rows : List (Row n routeDecoder) // rows.map Row.family = List.ofFn assignment }

def assignedCall (fuel n m : Nat) {ρ : Type u} (routeDecoder : Value → Option ρ)
    (assignment : Fin m → Fin n) (call : Lean.Json) : Option (Matched n m routeDecoder assignment) :=
  match callOwners fuel n routeDecoder call with
  | none => none
  | some rows =>
      if h : rows.map Row.family = List.ofFn assignment then some ⟨rows, h⟩ else none

theorem assignedCall_sound {n m : Nat} {ρ : Type u} {α : Type v} (fuel : Nat)
    (routeDecoder : Value → Option ρ) (assignment : Fin m → Fin n) (store : Fin n → α)
    (call : Lean.Json) (r : Matched n m routeDecoder assignment)
    (h : assignedCall fuel n m routeDecoder assignment call = some r) :
    callOwners fuel n routeDecoder call = some r.val ∧
    gatherCall fuel routeDecoder store call = some (List.ofFn (fun i => store (assignment i))) := by
  cases hc : callOwners fuel n routeDecoder call with
  | none =>
      simp only [assignedCall, hc] at h
      cases h
  | some rows =>
      by_cases hmatch : rows.map Row.family = List.ofFn assignment
      · have he : (⟨rows, hmatch⟩ : Matched n m routeDecoder assignment) = r :=
          Option.some.inj (by simpa only [assignedCall, hc, dif_pos hmatch] using h)
        cases he
        refine ⟨rfl, ?_⟩
        rw [gatherCall_of_success fuel routeDecoder store call rows hc, hmatch, List.map_ofFn]
        all_goals rfl
      · simp only [assignedCall, hc, dif_neg hmatch] at h
        cases h

end CurrentMain.JsonOwnerFieldAdapter
#print axioms CurrentMain.JsonOwnerFieldAdapter.decodeRow_sound
#print axioms CurrentMain.JsonOwnerFieldAdapter.decodeRows_sound
#print axioms CurrentMain.JsonOwnerFieldAdapter.callOwners_missing
#print axioms CurrentMain.JsonOwnerFieldAdapter.callOwners_sound
#print axioms CurrentMain.JsonOwnerFieldAdapter.gatherCall_of_success
#print axioms CurrentMain.JsonOwnerFieldAdapter.assignedCall_sound
#check @CurrentMain.JsonOwnerFieldAdapter.callOwners_sound
#check @CurrentMain.JsonOwnerFieldAdapter.assignedCall_sound
