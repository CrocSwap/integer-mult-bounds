import Init.Data.String.Extra
import CompactNatColumnAscii

/-!
Restricted logical UTF-8 round trips for arbitrary ASCII strings and the existing
compact Nat-column encoder. The proof follows the installed total well-founded
String.validateUTF8.loop and String.fromUTF8.loop, deriving exact decoded
characters, one-byte progress, validation and reconstruction of the full string.
No replacement decoder or JSON grammar is introduced.

The only new closed finite decision is the fixed 128-byte ASCII high-bit fact.
All strings, character lists, magnitudes and token-list lengths are arbitrary.
The accepted one-byte encoding theorem is reused unchanged. The runtime extern
implementations are separate refinement obligations; this proves their logical
Lean specifications only. Json.parse success, installed-parser spans, artifact
identity/digests, selected-file success, complex phases, physical execution and
costs remain separate. No existing accepted source is changed.
Author-checked source context: kappa=836330098538459/500000000000000000
=0.001672660197076918. Generic statements do not use or change kappa.
Credits: Leonardo de Moura and Lean String/UInt/List/Array authors; accepted
bank/frame compact ASCII components; Jeremy Kothe T16 and Rohan Arun PR1094.
James Chang with OpenAI assistance. Apache-2.0. Uncompiled source preparation.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.AsciiUtf8RoundTrip

/-- A fixed byte-alphabet property, not a selected data census. -/
private theorem ascii_mask : ∀ d : Fin 128,
    ((UInt8.ofNat d.val &&& 128) == 0) = true := by
  decide

private theorem decode_ascii_at (a : ByteArray) (i : Nat) (c : Char)
    (hread : a[i]? = some c.val.toUInt8) (hc : c.val ≤ 127) :
    String.utf8DecodeChar? a i = some c := by
  have hv : c.val.toNat ≤ 127 := hc
  have hb : c.val.toUInt8.toNat < 128 := by
    rw [UInt32.toNat_toUInt8]
    omega
  have hm : ((c.val.toUInt8 &&& 128) == 0) = true := by
    simpa only [UInt8.ofNat_toNat] using ascii_mask ⟨c.val.toUInt8.toNat, hb⟩
  have hc256 : c.val < 256 := by
    change c.val.toNat < 256
    omega
  have hback : c.val.toUInt8.toUInt32 = c.val := by
    rw [UInt32.toUInt32_toUInt8, UInt32.mod_eq_of_lt hc256]
  simp only [String.utf8DecodeChar?, hread]
  change (if ((c.val.toUInt8 &&& 128) == 0) = true then _ else _) = some c
  rw [if_pos hm]
  apply congrArg some
  apply Char.ext
  exact hback

/-- Cursor invariant for the actual installed total decoder loops. -/
private theorem loops (a : ByteArray) (cs : List Char) (i : Nat)
    (hlen : a.size = i + cs.length)
    (hdecode : ∀ j (hj : j < cs.length), String.utf8DecodeChar? a (i + j) = some cs[j])
    (hsize : ∀ c ∈ cs, c.utf8Size = 1) :
    String.validateUTF8.loop a i = some () ∧
    ∀ acc : String, String.fromUTF8.loop a i acc = String.mk (acc.data ++ cs) := by
  induction cs generalizing i with
  | nil =>
      have hi : ¬ i < a.size := by simp only [List.length_nil, Nat.add_zero] at hlen; omega
      constructor
      · rw [String.validateUTF8.loop]
        simp only [if_neg hi]
        rfl
      · intro acc
        rw [String.fromUTF8.loop]
        simp only [if_neg hi, List.append_nil]
  | cons c cs ih =>
      have hi : i < a.size := by simp only [List.length_cons] at hlen; omega
      have hd : String.utf8DecodeChar? a i = some c := by
        simpa only [Nat.add_zero, List.getElem_cons_zero] using hdecode 0 (by simp)
      have hs : c.utf8Size = 1 := hsize c List.mem_cons_self
      have htail : a.size = (i + 1) + cs.length := by
        simp only [List.length_cons] at hlen
        omega
      have hdt : ∀ j (hj : j < cs.length),
          String.utf8DecodeChar? a ((i + 1) + j) = some cs[j] := by
        intro j hj
        simpa only [List.getElem_cons_succ, Nat.add_assoc, Nat.add_comm 1 j] using
          hdecode (j + 1) (Nat.succ_lt_succ hj)
      have hst : ∀ d ∈ cs, d.utf8Size = 1 :=
        fun d hm => hsize d (List.mem_cons_of_mem c hm)
      obtain ⟨hvalid, hfrom⟩ := ih (i + 1) htail hdt hst
      constructor
      · rw [String.validateUTF8.loop]
        simp only [if_pos hi, hd]
        change String.validateUTF8.loop a (i + c.utf8Size) = some ()
        rw [hs]
        exact hvalid
      · intro acc
        rw [String.fromUTF8.loop]
        simp only [if_pos hi, hd, Option.getD_some, hs]
        rw [hfrom]
        apply String.ext
        simp only [String.data_push, List.append_assoc, List.singleton_append]

/-- Decode an arbitrary complete one-byte ASCII representation using the actual decoder. -/
theorem fromUTF8_of_one_byte (a : ByteArray) (cs : List Char)
    (ha : a.data.toList = cs.map (fun c => c.val.toUInt8))
    (hc : ∀ c ∈ cs, c.val ≤ 127) :
    String.fromUTF8? a = some (String.mk cs) := by
  have hlen : a.size = 0 + cs.length := by
    have h := congrArg List.length ha
    simpa only [Array.length_toList, List.length_map, Nat.zero_add] using h
  have hdecode : ∀ j (hj : j < cs.length),
      String.utf8DecodeChar? a (0 + j) = some cs[j] := by
    intro j hj
    have hread : a[j]? = some (cs[j]).val.toUInt8 := by
      change a.data[j]? = some (cs[j]).val.toUInt8
      rw [← Array.getElem?_toList, ha, List.getElem?_map, List.getElem?_eq_getElem hj]
      rfl
    simpa only [Nat.zero_add] using decode_ascii_at a j cs[j] hread (hc cs[j] (List.getElem_mem hj))
  have hsize : ∀ c ∈ cs, c.utf8Size = 1 := by
    intro c hm
    change (if c.val ≤ 127 then (1 : Nat) else _) = 1
    rw [if_pos (hc c hm)]
  obtain ⟨hvalid, hfrom⟩ := loops a cs 0 hlen hdecode hsize
  have hv : String.validateUTF8 a = true := by
    unfold String.validateUTF8
    rw [hvalid]
    rfl
  simp only [String.fromUTF8?, dif_pos hv, String.fromUTF8]
  simpa only [List.nil_append] using congrArg some (hfrom "")

/-- The original ASCII string is recovered, including empty strings and repeated characters. -/
theorem ascii_roundtrip (s : String) (h : ∀ c ∈ s.data, c.val ≤ 127) :
    String.fromUTF8? s.toUTF8 = some s := by
  exact fromUTF8_of_one_byte s.toUTF8 s.data
    (CompactNatColumnAscii.toUTF8_one_byte s h) h

/-- The accepted compact text supplies its own ASCII hypothesis for all Nat lists. -/
theorem compact_roundtrip (xs : List Nat) :
    String.fromUTF8? (CompactNatColumnFragment.encode xs) =
      some (CompactNatColumnFragment.natArrayText xs) := by
  apply ascii_roundtrip
  intro c hc
  exact CompactNatColumnAscii.allowed_ascii c (CompactNatColumnAscii.text_allowed xs c hc)

/-- Complete bounded column payloads inherit the logical UTF-8 result; JSON remains separate. -/
theorem payload_roundtrip {n : Nat} (cols : JsonPackedColumnDictionary.Columns n) :
    String.fromUTF8? (CompactNatColumnFragment.payload cols) =
      some (CompactNatColumnFragment.natArrayText (CompactNatColumnFragment.natValues cols)) := by
  exact compact_roundtrip (CompactNatColumnFragment.natValues cols)

/-- Ordered token lists recover the same original ASCII keys, without length or distinctness assumptions. -/
theorem tokens_roundtrip (keys : List String)
    (h : ∀ key ∈ keys, ∀ c ∈ key.data, c.val ≤ 127) :
    (keys.map String.toUTF8).mapM String.fromUTF8? = some keys := by
  induction keys with
  | nil => rfl
  | cons key keys ih =>
      have hk := ascii_roundtrip key (h key List.mem_cons_self)
      have ht := ih (fun k hm => h k (List.mem_cons_of_mem key hm))
      simp only [List.map_cons, List.mapM_cons, hk, ht]
      rfl

end CurrentMain.AsciiUtf8RoundTrip
#print axioms CurrentMain.AsciiUtf8RoundTrip.fromUTF8_of_one_byte
#print axioms CurrentMain.AsciiUtf8RoundTrip.ascii_roundtrip
#print axioms CurrentMain.AsciiUtf8RoundTrip.compact_roundtrip
#print axioms CurrentMain.AsciiUtf8RoundTrip.payload_roundtrip
#print axioms CurrentMain.AsciiUtf8RoundTrip.tokens_roundtrip
#check @CurrentMain.AsciiUtf8RoundTrip.ascii_roundtrip
#check @CurrentMain.AsciiUtf8RoundTrip.tokens_roundtrip
