import CompactNatColumnFragment

/-!
Representation facts for the existing compact Nat-column encoder. The logical
Nat.repr definition uses decimal toDigitsCore; its arbitrary-length output has
only decimal digit characters. The existing array encoder adds only commas and
brackets. Every such character takes the one-byte UTF-8 branch, so the original
character order is preserved exactly in the emitted Array UInt8.

The generic string lemma uses only an explicit ASCII hypothesis; its application
to compact arrays derives that hypothesis. The validation corollary uses actual
accepted fragment validation to identify the original bytes. No selected data,
new JSON grammar, or general serializer/JSON parser round trip is introduced.
In particular the installed partial Json.parse success equation remains open.
No digest/key identity, dictionary-byte membership, runtime implementation
refinement, physical semantics or encoding/parsing cost is claimed.
Author-checked context: kappa=836330098538459/500000000000000000
=0.001672660197076918; these generic results do not use or change kappa.
Credits: Lean Nat/String/UTF-8 authors, Jeremy Kothe T16 compact sigma payload,
Rohan Arun PR1094, and accepted bank/frame fragment and column codecs.
James Chang with OpenAI assistance; Apache-2.0. UNCOMPILED preparation.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.CompactNatColumnAscii
open CompactNatColumnFragment (decimalTail natArrayText encode natValues payload validateFragment)
open JsonPackedColumnDictionary (Columns)

/-- Decimal digits are exactly the ten existing Nat.digitChar cases. -/
def Decimal (c : Char) : Prop := ∃ d : Fin 10, c = Nat.digitChar d.val

def Allowed (c : Char) : Prop := c = '[' ∨ c = ']' ∨ c = ',' ∨ Decimal c

private def SafeText (s : String) : Prop := ∀ c ∈ s.data, Allowed c

private theorem digit_ascii : ∀ d : Fin 10, (Nat.digitChar d.val).val ≤ 127 := by
  decide

/-- Only a fixed decimal alphabet and three punctuation characters are checked. -/
theorem allowed_ascii (c : Char) (h : Allowed c) : c.val ≤ 127 := by
  rcases h with h | h | h | ⟨d, h⟩
  · subst c; decide
  · subst c; decide
  · subst c; decide
  · subst c; exact digit_ascii d

private theorem decimal_core (fuel n : Nat) (acc : List Char)
    (ha : ∀ c ∈ acc, Decimal c) :
    ∀ c ∈ Nat.toDigitsCore 10 fuel n acc, Decimal c := by
  induction fuel generalizing n acc with
  | zero => exact ha
  | succ fuel ih =>
      have hd : Decimal (Nat.digitChar (n % 10)) :=
        ⟨⟨n % 10, Nat.mod_lt n (by decide)⟩, rfl⟩
      have ht : ∀ c ∈ Nat.digitChar (n % 10) :: acc, Decimal c := by
        intro c hc
        rcases List.mem_cons.mp hc with h | h
        · subst c; exact hd
        · exact ha c h
      by_cases hz : n / 10 = 0
      · simpa only [Nat.toDigitsCore, if_pos hz] using ht
      · simpa only [Nat.toDigitsCore, if_neg hz] using ih (n / 10) _ ht

/-- All natural magnitudes, not a selected finite numeric table. -/
theorem repr_decimal (n : Nat) : ∀ c ∈ (Nat.repr n).data, Decimal c := by
  change ∀ c ∈ Nat.toDigitsCore 10 (n + 1) n [], Decimal c
  apply decimal_core
  intro c hc
  cases hc

private theorem safe_singleton (c : Char) (hc : Allowed c) :
    SafeText (String.singleton c) := by
  intro d hd
  change d ∈ [c] at hd
  have he : d = c := List.mem_singleton.mp hd
  subst d
  exact hc

private theorem safe_append (a b : String) (ha : SafeText a) (hb : SafeText b) :
    SafeText (a ++ b) := by
  intro c hc
  rw [String.data_append] at hc
  rcases List.mem_append.mp hc with h | h
  · exact ha c h
  · exact hb c h

private theorem safe_repr (n : Nat) : SafeText (Nat.repr n) := by
  intro c hc
  exact Or.inr (Or.inr (Or.inr (repr_decimal n c hc)))

private theorem safe_tail (xs : List Nat) : SafeText (decimalTail xs) := by
  induction xs with
  | nil =>
      intro c hc
      cases hc
  | cons x xs ih =>
      change SafeText ("," ++ Nat.repr x ++ decimalTail xs)
      exact safe_append _ _
        (safe_append _ _ (safe_singleton ',' (Or.inr (Or.inr (Or.inl rfl)))) (safe_repr x)) ih

/-- The existing compact text contains no characters outside its source alphabet. -/
theorem text_allowed (xs : List Nat) : ∀ c ∈ (natArrayText xs).data, Allowed c := by
  cases xs with
  | nil =>
      change SafeText ("[" ++ "]")
      exact safe_append _ _ (safe_singleton '[' (Or.inl rfl))
        (safe_singleton ']' (Or.inr (Or.inl rfl)))
  | cons x xs =>
      change SafeText ("[" ++ Nat.repr x ++ decimalTail xs ++ "]")
      exact safe_append _ _
        (safe_append _ _ (safe_append _ _ (safe_singleton '[' (Or.inl rfl))
          (safe_repr x)) (safe_tail xs))
        (safe_singleton ']' (Or.inr (Or.inl rfl)))

private theorem ascii_flatMap (cs : List Char) (h : ∀ c ∈ cs, c.val ≤ 127) :
    cs.flatMap String.utf8EncodeChar = cs.map (fun c => c.val.toUInt8) := by
  induction cs with
  | nil => rfl
  | cons c cs ih =>
      have hc : c.val ≤ 127 := h c (List.mem_cons_self)
      have ht : ∀ d ∈ cs, d.val ≤ 127 := fun d hd => h d (List.mem_cons_of_mem _ hd)
      rw [List.flatMap_cons, List.map_cons]
      have he : String.utf8EncodeChar c = [c.val.toUInt8] := by
        simp only [String.utf8EncodeChar, if_pos hc]
      rw [he]
      change c.val.toUInt8 :: cs.flatMap String.utf8EncodeChar =
        c.val.toUInt8 :: cs.map (fun d => d.val.toUInt8)
      rw [ih ht]

/-- Generic exact logical UTF-8 lowering for any ASCII string. -/
theorem toUTF8_one_byte (s : String) (h : ∀ c ∈ s.data, c.val ≤ 127) :
    s.toUTF8.data.toList = s.data.map (fun c => c.val.toUInt8) := by
  change s.data.flatMap String.utf8EncodeChar = s.data.map (fun c => c.val.toUInt8)
  exact ascii_flatMap s.data h

/-- The ASCII premise is derived from the compact Nat-array construction. -/
theorem encode_one_byte (xs : List Nat) :
    (encode xs).data.toList = (natArrayText xs).data.map (fun c => c.val.toUInt8) := by
  apply toUTF8_one_byte
  intro c hc
  exact allowed_ascii c (text_allowed xs c hc)

/-- Actual validation transfers the representation facts to the original bytes. -/
theorem validate_representation {n : Nat} (bytes : ByteArray) (cols : Columns n)
    (h : validateFragment n bytes = some cols) :
    bytes.data.toList = (natArrayText (natValues cols)).data.map (fun c => c.val.toUInt8) ∧
    (∀ c ∈ (natArrayText (natValues cols)).data, Allowed c) := by
  have hb := (CompactNatColumnFragment.validate_sound bytes cols h).2.1
  rw [hb]
  exact ⟨encode_one_byte (natValues cols), text_allowed (natValues cols)⟩

end CurrentMain.CompactNatColumnAscii
#print axioms CurrentMain.CompactNatColumnAscii.allowed_ascii
#print axioms CurrentMain.CompactNatColumnAscii.repr_decimal
#print axioms CurrentMain.CompactNatColumnAscii.text_allowed
#print axioms CurrentMain.CompactNatColumnAscii.toUTF8_one_byte
#print axioms CurrentMain.CompactNatColumnAscii.encode_one_byte
#print axioms CurrentMain.CompactNatColumnAscii.validate_representation
#check @CurrentMain.CompactNatColumnAscii.toUTF8_one_byte
#check @CurrentMain.CompactNatColumnAscii.validate_representation
