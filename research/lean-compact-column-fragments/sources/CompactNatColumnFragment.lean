import ByteJsonGlobalCall
import JsonPackedColumnDictionary

/-!
Schema-specific compact decimal Nat-array payload, following the selected
emitter's json.dumps(sigma,separators=(',',':')).encode() shape. This is a
structural encoder for ordered natural columns: brackets, decimal Nat.repr,
commas, and UTF-8. It is not Json.compress and does not serialize objects.
No general Python/Lean serializer equivalence is asserted.

Execution parses the original bytes, reuses the accepted strict column-vector
decoder, then compares all original bytes with the encoding of those decoded
columns. Successful validation derives both parser/AST correspondence and
exact payload equality, with original vector order, length and bounds. The
required parser round-trip equation remains explicit in completeness; it is
not inferred from an equality test or supplied as an axiom.

This is a standalone fragment boundary. Its relationship to a named entry of
the original dictionary, a digest key or file identity remains separate. No
all-valid-JSON equivalence, duplicate-key rejection, general JSON grammar,
selected census, physical execution or encoding/parsing cost is claimed.
Author-checked context: kappa=836330098538459/500000000000000000
=0.001672660197076918; these generic facts do not use or change kappa.
Credits: Jeremy Kothe T16 compact sigma payload, Rohan Arun PR1094, accepted
bank/frame byte parser and ordered column codec, Lean/Mathlib. James Chang
with OpenAI assistance; Apache-2.0. Source prepared for independent review.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.CompactNatColumnFragment
open JsonPackedColumnDictionary (Columns decodeColumns)
open ParsedBinaryChartCertificate (vectorValue columnFunction)

/-- Remaining comma-separated values, without spaces or reordering. -/
def decimalTail : List Nat → String
  | [] => ""
  | x :: xs => "," ++ Nat.repr x ++ decimalTail xs

def natArrayText : List Nat → String
  | [] => "[]"
  | x :: xs => "[" ++ Nat.repr x ++ decimalTail xs ++ "]"

def encode (xs : List Nat) : ByteArray := (natArrayText xs).toUTF8

def natValues {n : Nat} (cols : Columns n) : List Nat := cols.val.map Fin.val

def payload {n : Nat} (cols : Columns n) : ByteArray := encode (natValues cols)

theorem encode_nil : encode [] = "[]".toUTF8 := rfl

theorem encode_singleton (x : Nat) : encode [x] = ("[" ++ Nat.repr x ++ "]").toUTF8 := by
  simp only [encode, natArrayText, decimalTail, String.append_empty]

private theorem bytes_ext {a b : ByteArray} (h : a.data = b.data) : a = b := by
  cases a
  cases b
  cases h
  rfl

/-- Parse and decode first, then execute the exact whole-fragment byte comparison.
The equality decision is on the underlying Array UInt8, with no hash shortcut. -/
def validateFragment (n : Nat) (bytes : ByteArray) : Option (Columns n) :=
  match ByteJsonGlobalCall.parseBytes bytes with
  | .error _ => none
  | .ok raw =>
      match decodeColumns n raw with
      | none => none
      | some cols => if bytes.data = (payload cols).data then some cols else none

theorem validate_parse_error {n : Nat} (bytes : ByteArray) (error : ByteJsonGlobalCall.InputError)
    (h : ByteJsonGlobalCall.parseBytes bytes = .error error) :
    validateFragment n bytes = none := by
  simp only [validateFragment, h]

private theorem validate_witness {n : Nat} (bytes : ByteArray) (cols : Columns n)
    (h : validateFragment n bytes = some cols) :
    ∃ raw : Lean.Json, ByteJsonGlobalCall.parseBytes bytes = .ok raw ∧
      decodeColumns n raw = some cols ∧ bytes = payload cols := by
  cases hp : ByteJsonGlobalCall.parseBytes bytes with
  | error error =>
      simp only [validateFragment, hp] at h
      cases h
  | ok raw =>
      cases hd : decodeColumns n raw with
      | none =>
          simp only [validateFragment, hp, hd] at h
          cases h
      | some found =>
          by_cases he : bytes.data = (payload found).data
          · have hc : found = cols := Option.some.inj
              (by simpa only [validateFragment, hp, hd, if_pos he] using h)
            cases hc
            exact ⟨raw, rfl, hd, bytes_ext he⟩
          · simp only [validateFragment, hp, hd, if_neg he] at h
            cases h

/-- Even successfully parsed/decoded values are rejected when the actual bytes
are not exactly the compact payload of the decoded ordered vector. -/
theorem validate_mismatch {n : Nat} (bytes : ByteArray) (raw : Lean.Json) (cols : Columns n)
    (hp : ByteJsonGlobalCall.parseBytes bytes = .ok raw)
    (hd : decodeColumns n raw = some cols) (hne : bytes ≠ payload cols) :
    validateFragment n bytes = none := by
  have hdata : bytes.data ≠ (payload cols).data := fun h => hne (bytes_ext h)
  simp only [validateFragment, hp, hd, if_neg hdata]

/-- Actual validation, not a desired result premise, gives both the complete
parsed field and exact original bytes. Repetitions retain their positions. -/
theorem validate_sound {n : Nat} (bytes : ByteArray) (cols : Columns n)
    (h : validateFragment n bytes = some cols) :
    (∃ (text : String) (raw : Lean.Json),
      String.fromUTF8? bytes = some text ∧ Lean.Json.parse text = .ok raw ∧
      decodeColumns n raw = some cols ∧
      StrictJsonValueBridge.reencode 2 (vectorValue cols) = raw) ∧
    bytes = payload cols ∧ (natValues cols).length = n ∧
    (∀ j, columnFunction cols j < 2 ^ n) := by
  obtain ⟨raw, hp, hd, he⟩ := validate_witness bytes cols h
  obtain ⟨text, hu, hj⟩ := ByteJsonGlobalCall.parseBytes_sound bytes raw hp
  obtain ⟨hv, hb⟩ := JsonPackedColumnDictionary.decodeColumns_sound raw cols hd
  refine ⟨⟨text, raw, hu, hj, hd, hv⟩, he, ?_, hb⟩
  simpa only [natValues, List.length_map] using cols.property

/-- The missing installed-parser round trip is a visible, restricted premise.
It is not claimed for arbitrary JSON values or all valid spellings. -/
theorem validate_complete {n : Nat} (cols : Columns n)
    (hparse : ByteJsonGlobalCall.parseBytes (payload cols) =
      .ok (StrictJsonValueBridge.reencode 2 (vectorValue cols))) :
    validateFragment n (payload cols) = some cols := by
  simp only [validateFragment, hparse, JsonPackedColumnDictionary.decodeColumns_canonical,
    if_pos rfl, if_true]

end CurrentMain.CompactNatColumnFragment
#print axioms CurrentMain.CompactNatColumnFragment.encode_nil
#print axioms CurrentMain.CompactNatColumnFragment.encode_singleton
#print axioms CurrentMain.CompactNatColumnFragment.validate_parse_error
#print axioms CurrentMain.CompactNatColumnFragment.validate_mismatch
#print axioms CurrentMain.CompactNatColumnFragment.validate_sound
#print axioms CurrentMain.CompactNatColumnFragment.validate_complete
#check @CurrentMain.CompactNatColumnFragment.validate_sound
#check @CurrentMain.CompactNatColumnFragment.validate_complete
