import AsciiUtf8RoundTrip
import HexObjectLayout
import Init.Data.UInt.Bitwise

/-!
The byte-based accepted hex-key policy supplies the character-level premise of
the accepted logical ASCII UTF-8 round trip. Every non-ASCII logical encoder
branch has a leading byte with the 192, 224 or 240 mask; monotonicity of bitwise
or therefore excludes an all-ASCII byte encoding. This proves a general converse
for arbitrary String values, then applies it to actual checked key bytes.

Ordered quoted tokens encoded from checked hex keys recover the same String
keys. There is no new decoder, scanner, JSON grammar or selected literal table.
Logical String/ByteArray specifications are used; runtime extern refinement,
JSON parser equations, field spans, artifact/digest authentication, selected-file
success, physical semantics and costs remain separate.
Author-checked context: kappa=836330098538459/500000000000000000
=0.001672660197076918; the generic statements do not use or change kappa.
Credits: Lean String/UInt/List authors; accepted bank/frame ASCII, layout and
strict parser components; Jeremy Kothe T16 and Rohan Arun PR1094.
James Chang with OpenAI assistance. Apache-2.0. Uncompiled source preparation.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.HexKeyUtf8RoundTrip

private theorem high_prefix_not_ascii (bits tag : UInt8)
    (htag : 128 ≤ tag.toNat) (h : (bits ||| tag).toNat ≤ 127) : False := by
  have ht : tag ≤ bits ||| tag := UInt8.right_le_or
  have hn : tag.toNat ≤ (bits ||| tag).toNat := ht
  omega

private theorem char_ascii_of_encoded_bytes (c : Char)
    (h : ∀ b ∈ String.utf8EncodeChar c, b.toNat ≤ 127) : c.val ≤ 127 := by
  by_cases h1 : c.val ≤ 127
  · exact h1
  · by_cases h2 : c.val ≤ 2047
    · have hh := h ((c.val >>> 6).toUInt8 &&& 31 ||| 192) (by
        simp only [String.utf8EncodeChar, if_neg h1, if_pos h2]
        exact List.mem_cons_self)
      exact False.elim (high_prefix_not_ascii _ 192 (by decide) hh)
    · by_cases h3 : c.val ≤ 65535
      · have hh := h ((c.val >>> 12).toUInt8 &&& 15 ||| 224) (by
          simp only [String.utf8EncodeChar, if_neg h1, if_neg h2, if_pos h3]
          exact List.mem_cons_self)
        exact False.elim (high_prefix_not_ascii _ 224 (by decide) hh)
      · have hh := h ((c.val >>> 18).toUInt8 &&& 7 ||| 240) (by
          simp only [String.utf8EncodeChar, if_neg h1, if_neg h2, if_neg h3]
          exact List.mem_cons_self)
        exact False.elim (high_prefix_not_ascii _ 240 (by decide) hh)

/-- An all-ASCII logical UTF-8 byte representation forces every original character to be ASCII. -/
theorem ascii_of_ascii_bytes (s : String)
    (h : ∀ b ∈ s.toUTF8.data.toList, b.toNat ≤ 127) :
    ∀ c ∈ s.data, c.val ≤ 127 := by
  intro c hc
  apply char_ascii_of_encoded_bytes
  intro b hb
  apply h b
  change b ∈ s.data.flatMap String.utf8EncodeChar
  exact List.mem_flatMap.mpr ⟨c, hc, hb⟩

/-- No additional character-level assumption is needed beyond the actual accepted hex-byte check. -/
theorem key_policy_ascii (key : String) (h : HexObjectLayout.keyPolicy key = true) :
    ∀ c ∈ key.data, c.val ≤ 127 := by
  apply ascii_of_ascii_bytes
  intro b hb
  have ht := ((HexObjectLayout.keyPolicy_iff key).mp h).2 b hb
  rcases ht with ht | ht <;> omega

/-- The exact serialized key-byte token decodes back to its original String. -/
theorem key_policy_roundtrip (key : String) (h : HexObjectLayout.keyPolicy key = true) :
    String.fromUTF8? (⟨(HexObjectLayout.keyBytes key).toArray⟩ : ByteArray) = some key := by
  change String.fromUTF8? key.toUTF8 = some key
  exact AsciiUtf8RoundTrip.ascii_roundtrip key (key_policy_ascii key h)

/-- Original order and every key are preserved for arbitrary finite checked key lists. -/
theorem hex_tokens_roundtrip (keys : List String)
    (h : ∀ key ∈ keys, HexObjectLayout.keyPolicy key = true) :
    (keys.map (fun key => (⟨(HexObjectLayout.keyBytes key).toArray⟩ : ByteArray))).mapM
      String.fromUTF8? = some keys := by
  change (keys.map String.toUTF8).mapM String.fromUTF8? = some keys
  exact AsciiUtf8RoundTrip.tokens_roundtrip keys (fun key hm => key_policy_ascii key (h key hm))

end CurrentMain.HexKeyUtf8RoundTrip
#print axioms CurrentMain.HexKeyUtf8RoundTrip.ascii_of_ascii_bytes
#print axioms CurrentMain.HexKeyUtf8RoundTrip.key_policy_ascii
#print axioms CurrentMain.HexKeyUtf8RoundTrip.key_policy_roundtrip
#print axioms CurrentMain.HexKeyUtf8RoundTrip.hex_tokens_roundtrip
#check @CurrentMain.HexKeyUtf8RoundTrip.key_policy_roundtrip
#check @CurrentMain.HexKeyUtf8RoundTrip.hex_tokens_roundtrip
