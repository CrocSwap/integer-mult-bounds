import JsonGlobalCallAdapter
import Lean.Data.Json.Parser
import Init.Data.String.Extra

/-!
Reusable executable byte-input boundary for the actual calls/owners adapter.
The entrypoint first uses String.fromUTF8?, then Lean.Json.parse, then the
unchanged counted/indexed calls and complete owners/assignment checker.
Malformed UTF-8 and parser errors are returned distinctly. No fallback string,
default JSON value, assumed parser output or new source grammar is introduced.

Success derives the actual UTF-8 and parser equations together with the complete
selected calls/owners AST and ordered arbitrary-payload result. This is a
composition theorem about those installed functions, not a proof of their
implementation against a Unicode or JSON standard. In particular it does not
establish duplicate-key rejection, lexical integer-only acceptance, canonical
serialization, artifact digest identity or success on any selected file.
Logical reads remain out-of-place and unpriced. No allocation, phase, physical
executor, precision or full multiplication theorem is inferred.
Author-checked context: kappa=836330098538459/500000000000000000
=0.001672660197076918; the generic statements do not use or change kappa.
Credits: Lean UTF-8/JSON parser authors, public parser/gather/call-adapter work,
Rohan Arun PR1094 and Jeremy Kothe T16 format lineage. James Chang with OpenAI
assistance; Apache-2.0. Source prepared for independent review.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.ByteJsonGlobalCall
universe u v
open SelectedSourceSyntax (Value)
open JsonOwnerFieldAdapter (Matched rowValue callOwners)

inductive InputError where
  | invalidUtf8
  | invalidJson (message : String)

/-- The real installed conversions execute on the original byte sequence. -/
def parseBytes (bytes : ByteArray) : Except InputError Lean.Json :=
  match String.fromUTF8? bytes with
  | none => .error .invalidUtf8
  | some text =>
      match Lean.Json.parse text with
      | .error message => .error (.invalidJson message)
      | .ok raw => .ok raw

theorem parseBytes_invalidUtf8 (bytes : ByteArray)
    (h : String.fromUTF8? bytes = none) :
    parseBytes bytes = .error .invalidUtf8 := by
  simp only [parseBytes, h]

theorem parseBytes_invalidJson (bytes : ByteArray) (text message : String)
    (hu : String.fromUTF8? bytes = some text)
    (hp : Lean.Json.parse text = .error message) :
    parseBytes bytes = .error (.invalidJson message) := by
  simp only [parseBytes, hu, hp]

/-- No successful byte parse hides either intermediate computation. -/
theorem parseBytes_sound (bytes : ByteArray) (raw : Lean.Json)
    (h : parseBytes bytes = .ok raw) :
    ∃ text : String, String.fromUTF8? bytes = some text ∧ Lean.Json.parse text = .ok raw := by
  cases hu : String.fromUTF8? bytes with
  | none =>
      simp only [parseBytes, hu] at h
      cases h
  | some text =>
      cases hp : Lean.Json.parse text with
      | error message =>
          simp only [parseBytes, hu, hp] at h
          cases h
      | ok parsed =>
          have he : parsed = raw := Except.ok.inj (by simpa only [parseBytes, hu, hp] using h)
          cases he
          exact ⟨text, rfl, hp⟩

/-- Execution uses the existing source-matched assignment for this call index. -/
def assignedBytes (fuel n m k : Nat) {ρ : Type u} (routeDecoder : Value → Option ρ)
    (assignment : Fin k → Fin m → Fin n) (bytes : ByteArray) (position : Fin k) :
    Option (Matched n m routeDecoder (assignment position)) :=
  match parseBytes bytes with
  | .error _ => none
  | .ok global => JsonGlobalCallAdapter.assignedAt fuel n m k routeDecoder assignment global position

/-- Functional output reads; this is not a physical memory-access cost model. -/
def gatherBytes {n k : Nat} {ρ : Type u} {α : Type v} (fuel : Nat)
    (routeDecoder : Value → Option ρ) (store : Fin n → α)
    (bytes : ByteArray) (position : Fin k) : Option (List α) :=
  match parseBytes bytes with
  | .error _ => none
  | .ok global => JsonGlobalCallAdapter.gatherAt fuel routeDecoder store global position

theorem assignedBytes_parse_error {n m k : Nat} {ρ : Type u} (fuel : Nat)
    (routeDecoder : Value → Option ρ) (assignment : Fin k → Fin m → Fin n)
    (bytes : ByteArray) (position : Fin k) (error : InputError)
    (h : parseBytes bytes = .error error) :
    assignedBytes fuel n m k routeDecoder assignment bytes position = none := by
  simp only [assignedBytes, h]

/-- The only success premise is actual execution on the original bytes. -/
theorem assignedBytes_sound {n m k : Nat} {ρ : Type u} {α : Type v} (fuel : Nat)
    (routeDecoder : Value → Option ρ) (assignment : Fin k → Fin m → Fin n)
    (store : Fin n → α) (bytes : ByteArray) (position : Fin k)
    (r : Matched n m routeDecoder (assignment position))
    (h : assignedBytes fuel n m k routeDecoder assignment bytes position = some r) :
    (∃ (text : String) (global : Lean.Json) (calls : Array Lean.Json) (call raw : Lean.Json),
      String.fromUTF8? bytes = some text ∧ Lean.Json.parse text = .ok global ∧
      global.getObjVal? "calls" = .ok (.arr calls) ∧ calls.size = k ∧
      (∃ hi : position.val < calls.size, calls[position.val]'hi = call) ∧
      callOwners fuel n routeDecoder call = some r.val ∧
      call.getObjVal? "owners" = .ok raw ∧
      StrictJsonValueBridge.reencode fuel (Value.array (r.val.map rowValue)) = raw) ∧
    gatherBytes fuel routeDecoder store bytes position =
      some (List.ofFn (fun i => store (assignment position i))) := by
  cases hp : parseBytes bytes with
  | error error =>
      simp only [assignedBytes, hp] at h
      cases h
  | ok global =>
      have ha : JsonGlobalCallAdapter.assignedAt fuel n m k routeDecoder assignment global position =
          some r := by
        simpa only [assignedBytes, hp] using h
      obtain ⟨text, hu, hj⟩ := parseBytes_sound bytes global hp
      obtain ⟨⟨calls, call, raw, hg, hlen, hi, hc, ho, hv⟩, hout⟩ :=
        JsonGlobalCallAdapter.assignedAt_sound fuel routeDecoder assignment store global position r ha
      refine ⟨⟨text, global, calls, call, raw, hu, hj, hg, hlen, hi, hc, ho, hv⟩, ?_⟩
      simpa only [gatherBytes, hp] using hout

end CurrentMain.ByteJsonGlobalCall
#print axioms CurrentMain.ByteJsonGlobalCall.parseBytes_invalidUtf8
#print axioms CurrentMain.ByteJsonGlobalCall.parseBytes_invalidJson
#print axioms CurrentMain.ByteJsonGlobalCall.parseBytes_sound
#print axioms CurrentMain.ByteJsonGlobalCall.assignedBytes_parse_error
#print axioms CurrentMain.ByteJsonGlobalCall.assignedBytes_sound
#check @CurrentMain.ByteJsonGlobalCall.assignedBytes_sound
