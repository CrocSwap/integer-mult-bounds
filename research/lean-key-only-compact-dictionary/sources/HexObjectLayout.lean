import CheckedArraySlice

/-!
A generic deterministic compact flat-object byte layout and its derived offsets.
Each field retains a String key and its exact payload ByteArray. The key checker
operates on actual UTF-8 bytes: nonempty lowercase hexadecimal keys and distinct
serialized key-byte lists. No UTF-8 injectivity assumption is used.

The structural append proof derives the exact selected payload prefix/offset/
suffix from the complete ordered field list. Full artifact equality transfers
that location to the original artifact and proves the existing slice check.
Repeated payloads are permitted; no external offset or skipped context is used.

Payloads here are generic bytes, so this module alone asserts no JSON grammar.
The separate typed consumer restricts every payload to the accepted compact
Nat-array encoder and retains actual parser/lookup/recovery computations. This
layout theorem does not describe the installed parser's internal spans, prove
Python serializer equivalence, authenticate a digest/file, or price execution.
Generic nonempty hex keys need not have the source-specific SHA-256 width64.
Author-checked context: kappa=836330098538459/500000000000000000
=0.001672660197076918; generic statements do not use or change kappa.
Credits: Lean Array/List authors, Jeremy Kothe T16, Rohan Arun PR1094 compact
ACTUAL-SIGMAS emitter, accepted bank/frame byte/slice/compact components.
James Chang with OpenAI assistance, Apache-2.0.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.HexObjectLayout

structure Field where
  key : String
  payload : ByteArray

/-- Inspect the bytes actually used between the literal quote bytes. -/
def keyBytes (key : String) : List UInt8 := key.toUTF8.data.toList

def isHexByte (b : UInt8) : Bool :=
  decide ((48 ≤ b.toNat ∧ b.toNat ≤ 57) ∨ (97 ≤ b.toNat ∧ b.toNat ≤ 102))

def keyPolicy (key : String) : Bool :=
  decide (0 < (keyBytes key).length) && (keyBytes key).all isHexByte

/-- Distinctness is checked on serialized bytes, not inferred from String keys. -/
def checkKeys (fields : List Field) : Bool :=
  fields.all (fun f => keyPolicy f.key) &&
    decide ((fields.map (fun f => keyBytes f.key)).Nodup)

theorem keyPolicy_iff (key : String) :
    keyPolicy key = true ↔ 0 < (keyBytes key).length ∧
      ∀ b ∈ keyBytes key,
        (48 ≤ b.toNat ∧ b.toNat ≤ 57) ∨ (97 ≤ b.toNat ∧ b.toNat ≤ 102) := by
  simp only [keyPolicy, isHexByte, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true]

theorem checkKeys_iff (fields : List Field) :
    checkKeys fields = true ↔
      (∀ f ∈ fields, keyPolicy f.key = true) ∧
      (fields.map (fun f => keyBytes f.key)).Nodup := by
  simp only [checkKeys, Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq]

def header (selected : Field) : List UInt8 :=
  [34] ++ keyBytes selected.key ++ [34, 58]

def fieldBytes (selected : Field) : List UInt8 :=
  header selected ++ selected.payload.data.toList

/-- Every following field includes exactly its leading comma. -/
def tailBytes : List Field → List UInt8
  | [] => []
  | f :: fs => [44] ++ fieldBytes f ++ tailBytes fs

def bodyBytes : List Field → List UInt8
  | [] => []
  | f :: fs => fieldBytes f ++ tailBytes fs

def objectBytes (fields : List Field) : List UInt8 :=
  [123] ++ bodyBytes fields ++ [125]

def encode (fields : List Field) : ByteArray :=
  ⟨(objectBytes fields).toArray⟩

/-- All preceding fields, their separators and the complete selected key header. -/
def prefixBytes (before : List Field) (selected : Field) : List UInt8 :=
  [123] ++ (match before with
    | [] => []
    | f :: fs => fieldBytes f ++ tailBytes fs ++ [44]) ++ header selected

def suffixBytes (after : List Field) : List UInt8 := tailBytes after ++ [125]

def offset (before : List Field) (selected : Field) : Nat :=
  (prefixBytes before selected).length

private theorem tailBytes_append (before after : List Field) :
    tailBytes (before ++ after) = tailBytes before ++ tailBytes after := by
  induction before with
  | nil => rfl
  | cons f fs ih =>
      simp only [List.cons_append, tailBytes, ih, List.append_assoc]

/-- Structural position in the complete restricted layout, with no parser premise. -/
theorem objectBytes_split (before : List Field) (selected : Field) (after : List Field) :
    objectBytes (before ++ selected :: after) =
      prefixBytes before selected ++ selected.payload.data.toList ++ suffixBytes after := by
  cases before with
  | nil =>
      simp only [List.nil_append, objectBytes, bodyBytes, prefixBytes, fieldBytes,
        suffixBytes, List.append_nil, List.append_assoc]
  | cons f fs =>
      simp only [List.cons_append, objectBytes, bodyBytes, prefixBytes, tailBytes_append,
        tailBytes, fieldBytes, suffixBytes, List.append_assoc]

theorem encode_decomposition (before : List Field) (selected : Field) (after : List Field) :
    (encode (before ++ selected :: after)).data =
      (prefixBytes before selected).toArray ++ selected.payload.data ++
        (suffixBytes after).toArray := by
  change (objectBytes (before ++ selected :: after)).toArray = _
  rw [objectBytes_split]
  rw [← List.append_toArray, ← List.append_toArray, Array.toArray_toList]

/-- The byte interval is derived from serialization, then proved within the full bound. -/
theorem encode_checkBytes (before : List Field) (selected : Field) (after : List Field) :
    CheckedArraySlice.checkBytes (encode (before ++ selected :: after))
      selected.payload (offset before selected) = true := by
  apply (CheckedArraySlice.checkBytes_iff _ _ _).mpr
  constructor
  · change (prefixBytes before selected).length + selected.payload.data.size ≤
      (encode (before ++ selected :: after)).data.size
    rw [encode_decomposition]
    simp only [Array.size_append, List.size_toArray]
    exact Nat.le_add_right _ _
  · change (encode (before ++ selected :: after)).data.extract
      (prefixBytes before selected).toArray.size
      ((prefixBytes before selected).toArray.size + selected.payload.data.size) =
        selected.payload.data
    rw [encode_decomposition, Array.append_assoc, Array.extract_append_right,
      Array.extract_append_left, Array.extract_size]

/-- Complete equality with the supplied artifact leaves no unvalidated surrounding bytes. -/
theorem artifact_checkBytes (before : List Field) (selected : Field) (after : List Field)
    (artifact : ByteArray)
    (h : artifact.data = (encode (before ++ selected :: after)).data) :
    CheckedArraySlice.checkBytes artifact selected.payload (offset before selected) = true := by
  change CheckedArraySlice.checkSlice artifact.data selected.payload.data
    (offset before selected) = true
  rw [h]
  exact encode_checkBytes before selected after

end CurrentMain.HexObjectLayout
#print axioms CurrentMain.HexObjectLayout.keyPolicy_iff
#print axioms CurrentMain.HexObjectLayout.checkKeys_iff
#print axioms CurrentMain.HexObjectLayout.objectBytes_split
#print axioms CurrentMain.HexObjectLayout.encode_decomposition
#print axioms CurrentMain.HexObjectLayout.encode_checkBytes
#print axioms CurrentMain.HexObjectLayout.artifact_checkBytes
#check @CurrentMain.HexObjectLayout.objectBytes_split
#check @CurrentMain.HexObjectLayout.artifact_checkBytes
