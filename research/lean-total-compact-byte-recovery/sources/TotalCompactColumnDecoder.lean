import DecimalReprValuation
import AsciiUtf8RoundTrip
import Mathlib.Data.List.SplitOn

/-!
Total strict decoding of the existing compact decimal Nat-array image. Actual
bytes pass through the logical UTF-8 decoder, exact outer brackets, ordered
comma splitting and an independently defined decimal accumulator. An executed
full byte equality against the canonical encoding rejects every noncanonical
candidate, including leading zeros and whitespace. No lexical correctness is
assumed for the accumulator. The complete canonical round trip is proved for
all Nat lists; the existing vector codec supplies arbitrary dimension, length
and packed-column bounds, with repeats and original order preserved.

This is a new restricted fragment admission path, not an equation for the
opaque partial Lean.Json.parse or the earlier validateFragment function. It
introduces no general JSON grammar or selected data. Actual whole-file named
field identity, external artifact origin/authentication, runtime extern
refinement, complex phases, physical execution and paid costs remain separate.
Author-checked context: kappa=836330098538459/500000000000000000
=0.001672660197076918; the generic results do not use or change kappa.
Credits: Lean/Mathlib list, decimal and UTF-8 authors; accepted bank/frame
column codecs; Jeremy Kothe compact sigma encoding; Rohan Arun PR1094.
James Chang with OpenAI assistance. Apache-2.0. Acceptance is separate.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.TotalCompactColumnDecoder
open CompactNatColumnFragment (decimalTail natArrayText encode natValues payload)
open JsonPackedColumnDictionary (Columns)
open SelectedSourceSyntax (Value)
open ParsedBinaryChartCertificate (vectorValue decodeVector)
open DecimalReprValuation (decimalValue decimalValue_repr)

/-- Strip exactly one opening and closing bracket, preserving interior order. -/
def interior : List Char → Option (List Char)
  | '[' :: tail =>
      match tail.reverse with
      | ']' :: revBody => some revBody.reverse
      | _ => none
  | _ => none

/-- Numeric interpretation of ordered tokens. Canonicality is checked on bytes later. -/
def values (body : List Char) : List Nat :=
  if body = [] then [] else (body.splitOn ',').map (fun digits => decimalValue digits 0)

/-- Total candidate extraction followed by an executed exact byte comparison. -/
def decodeNatArray (bytes : ByteArray) : Option (List Nat) :=
  match String.fromUTF8? bytes with
  | none => none
  | some text =>
      match interior text.data with
      | none => none
      | some body =>
          let xs := values body
          if bytes.data = (encode xs).data then some xs else none

/-- The already checked strict integer-array representation, with explicit Nat casts. -/
def natValue (xs : List Nat) : Value :=
  .array (xs.map (fun n : Nat => .integer (Int.ofNat n)))

def decodePacked (n : Nat) (bytes : ByteArray) : Option (Columns n) :=
  match decodeNatArray bytes with
  | none => none
  | some xs => decodeVector n (2 ^ n) (natValue xs)

private def body (xs : List Nat) : List Char :=
  [','].intercalate (xs.map (fun n => (Nat.repr n).data))

private theorem tail_body (x : Nat) (xs : List Nat) :
    (Nat.repr x ++ decimalTail xs).data = body (x :: xs) := by
  induction xs generalizing x with
  | nil => simp [decimalTail, body, List.intercalate]
  | cons y ys ih =>
      have he := ih y
      simp only [String.data_append] at he
      simp only [decimalTail, String.data_append, body, List.map_cons,
        List.intercalate, List.intersperse_cons₂, List.flatten_cons,
        List.append_assoc] at he ⊢
      change (Nat.repr x).data ++ ',' :: ((Nat.repr y).data ++ (decimalTail ys).data) =
        (Nat.repr x).data ++ ',' :: _
      rw [he]
      rfl

private theorem text_body (xs : List Nat) :
    (natArrayText xs).data = '[' :: (body xs ++ [']']) := by
  cases xs with
  | nil => rfl
  | cons x xs =>
      have he := tail_body x xs
      simp only [String.data_append] at he
      simp only [natArrayText, String.data_append]
      change '[' :: ((Nat.repr x).data ++ (decimalTail xs).data ++ [']']) =
        '[' :: (body (x :: xs) ++ [']'])
      rw [he]

private theorem interior_text (xs : List Nat) :
    interior (natArrayText xs).data = some (body xs) := by
  rw [text_body]
  simp only [interior, List.reverse_append, List.reverse_cons, List.reverse_nil,
    List.nil_append, List.singleton_append, List.reverse_reverse]

private theorem repr_ne_nil (n : Nat) : (Nat.repr n).data ≠ [] := by
  intro h
  have hn : n = 0 := by
    simpa only [h, decimalValue, List.foldl_nil] using (decimalValue_repr n).symm
  subst n
  cases h

private theorem body_cons_ne_nil (x : Nat) (xs : List Nat) : body (x :: xs) ≠ [] := by
  intro h
  have he := tail_body x xs
  rw [String.data_append, h] at he
  exact repr_ne_nil x (List.append_eq_nil_iff.mp he).1

private theorem decimal_ne_comma : ∀ d : Fin 10, Nat.digitChar d.val ≠ ',' := by
  decide

private theorem repr_no_comma (n : Nat) : ',' ∉ (Nat.repr n).data := by
  intro h
  obtain ⟨d, hd⟩ := CompactNatColumnAscii.repr_decimal n ',' h
  exact decimal_ne_comma d hd.symm

private theorem split_body (xs : List Nat) (h : xs ≠ []) :
    (body xs).splitOn ',' = xs.map (fun n => (Nat.repr n).data) := by
  apply List.splitOn_intercalate
  · intro token ht
    obtain ⟨n, _, hn⟩ := List.mem_map.mp ht
    subst token
    exact repr_no_comma n
  · intro hm
    exact h (List.map_eq_nil_iff.mp hm)

private theorem values_body (xs : List Nat) : values (body xs) = xs := by
  cases xs with
  | nil => rfl
  | cons x xs =>
      rw [values, if_neg (body_cons_ne_nil x xs), split_body _ (List.cons_ne_nil _ _)]
      simp only [List.map_map, decimalValue_repr, Function.comp_def, List.map_id']

/-- Canonical decoding is proved for every length and magnitude, including []. -/
theorem decodeNatArray_encode (xs : List Nat) : decodeNatArray (encode xs) = some xs := by
  simp only [decodeNatArray, AsciiUtf8RoundTrip.compact_roundtrip, interior_text, values_body,
    if_pos rfl, if_true]

private theorem bytes_ext {a b : ByteArray} (h : a.data = b.data) : a = b := by
  cases a
  cases b
  cases h
  rfl

/-- Actual success determines every original byte, without a digest shortcut. -/
theorem decodeNatArray_sound (bytes : ByteArray) (xs : List Nat)
    (h : decodeNatArray bytes = some xs) : bytes = encode xs := by
  cases hu : String.fromUTF8? bytes with
  | none => simp only [decodeNatArray, hu] at h; cases h
  | some text =>
      cases hi : interior text.data with
      | none => simp only [decodeNatArray, hu, hi] at h; cases h
      | some chars =>
          by_cases hb : bytes.data = (encode (values chars)).data
          · have he : values chars = xs := Option.some.inj
              (by simpa only [decodeNatArray, hu, hi, if_pos hb] using h)
            rw [← he]
            exact bytes_ext hb
          · simp only [decodeNatArray, hu, hi, if_neg hb] at h
            cases h

/-- This total decoder accepts exactly the existing canonical compact-array image. -/
theorem decodeNatArray_eq_some_iff (bytes : ByteArray) (xs : List Nat) :
    decodeNatArray bytes = some xs ↔ bytes = encode xs := by
  constructor
  · exact decodeNatArray_sound bytes xs
  · intro h
    rw [h]
    exact decodeNatArray_encode xs

private theorem vector_natValue {n : Nat} (cols : Columns n) :
    vectorValue cols = natValue (natValues cols) := by
  unfold vectorValue natValue natValues
  apply congrArg Value.array
  simp only [List.map_map, StrictParsedIndexCodec.indexValue, Function.comp_def]
  rfl

private theorem natValue_injective : Function.Injective natValue := by
  intro xs ys h
  apply ((List.map_injective_iff (f := fun n : Nat => Value.integer (Int.ofNat n))).mpr ?_)
    (Value.array.inj h)
  intro m n he
  exact Int.ofNat.inj (Value.integer.inj he)

/-- Complete ordered column payloads decode without any logical JSON parser premise. -/
theorem decodePacked_payload {n : Nat} (cols : Columns n) :
    decodePacked n (payload cols) = some cols := by
  unfold decodePacked payload
  rw [decodeNatArray_encode]
  change decodeVector _ _ (natValue (natValues cols)) = some cols
  rw [← vector_natValue]
  exact ParsedBinaryChartCertificate.decodeVector_complete cols

/-- Exact length, bounds and multiplicity are inherited from the accepted vector codec. -/
theorem decodePacked_eq_some_iff {n : Nat} (bytes : ByteArray) (cols : Columns n) :
    decodePacked n bytes = some cols ↔ bytes = payload cols := by
  constructor
  · intro h
    cases hd : decodeNatArray bytes with
    | none => simp only [decodePacked, hd] at h; cases h
    | some xs =>
        have hv : decodeVector n (2 ^ n) (natValue xs) = some cols := by
          simpa only [decodePacked, hd] using h
        have he : xs = natValues cols := natValue_injective
          (((ParsedBinaryChartCertificate.decodeVector_eq_some_iff _ cols).mp hv).trans
            (vector_natValue cols))
        change bytes = encode (natValues cols)
        rw [← he]
        exact decodeNatArray_sound bytes xs hd
  · intro h
    rw [h]
    exact decodePacked_payload cols

end CurrentMain.TotalCompactColumnDecoder
#print axioms CurrentMain.TotalCompactColumnDecoder.decodeNatArray_encode
#print axioms CurrentMain.TotalCompactColumnDecoder.decodeNatArray_sound
#print axioms CurrentMain.TotalCompactColumnDecoder.decodeNatArray_eq_some_iff
#print axioms CurrentMain.TotalCompactColumnDecoder.decodePacked_payload
#print axioms CurrentMain.TotalCompactColumnDecoder.decodePacked_eq_some_iff
#check CurrentMain.TotalCompactColumnDecoder.decodeNatArray_eq_some_iff
#check @CurrentMain.TotalCompactColumnDecoder.decodePacked_eq_some_iff
