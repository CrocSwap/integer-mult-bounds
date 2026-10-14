import CompactNatColumnAscii
import HexObjectLayout
import Lean.Elab.Tactic.Omega

/-!
Total quote-token candidate discovery for the already restricted compact layout.
The scanner splits at actual byte34 and selects alternate chunks, rejecting an
unmatched quote. Its ordered-region relation reconstructs every original byte
as quote-free gaps and quote-free tokens, in order. This is candidate discovery,
not JSON tokenization: escapes, nested objects, JSON key roles and syntax are not
interpreted. A later consumer must run the unchanged complete-layout checker.

The existing compact Nat-column payload contains no quote byte; this follows
from its independently accepted decimal alphabet and exact one-byte UTF-8
representation. The accepted hex-key policy similarly excludes quote bytes.
No UTF-8 decoding roundtrip, installed JSON parser equation, digest/file
identity, selected census or execution-cost theorem is assumed or proved.
Author-checked context: kappa=836330098538459/500000000000000000
=0.001672660197076918; generic results do not use or change kappa.
Credits: Lean/Mathlib and bank/frame compact ASCII, layout and byte checks;
Jeremy Kothe T16/PR514 and Rohan Arun PR1094. James Chang with OpenAI assistance,
Apache-2.0. Source preparation; kernel acceptance remains separate.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.QuoteTokenScan

/-- Quote-free chunks separated by every actual quote byte, retaining empty chunks. -/
def splitQuotes : List UInt8 → List (List UInt8)
  | [] => [[]]
  | b :: bs =>
      if b = 34 then [] :: splitQuotes bs else
        match splitQuotes bs with
        | [] => [[b]]
        | first :: rest => (b :: first) :: rest

def joinTail : List (List UInt8) → List UInt8
  | [] => []
  | first :: rest => 34 :: (first ++ joinTail rest)

def joinChunks : List (List UInt8) → List UInt8
  | [] => []
  | first :: rest => first ++ joinTail rest

private theorem splitQuotes_spec (bytes : List UInt8) :
    ∃ first rest, splitQuotes bytes = first :: rest ∧
      joinChunks (first :: rest) = bytes ∧
      ∀ piece ∈ first :: rest, (34 : UInt8) ∉ piece := by
  induction bytes with
  | nil =>
      refine ⟨[], [], rfl, rfl, ?_⟩
      intro piece hp
      have he : piece = [] := List.mem_singleton.mp hp
      rw [he]
      exact List.not_mem_nil
  | cons b bs ih =>
      obtain ⟨first, rest, hs, hj, hn⟩ := ih
      by_cases hb : b = 34
      · subst b
        refine ⟨[], first :: rest, ?_, ?_, ?_⟩
        · simp only [splitQuotes, if_pos rfl, if_true, hs]
        · change 34 :: joinChunks (first :: rest) = 34 :: bs
          exact congrArg (List.cons 34) hj
        · intro piece hp
          rcases List.mem_cons.mp hp with hp | hp
          · subst piece
            exact List.not_mem_nil
          · exact hn piece hp
      · refine ⟨b :: first, rest, ?_, ?_, ?_⟩
        · simp only [splitQuotes, if_neg hb, hs]
        · change b :: joinChunks (first :: rest) = b :: bs
          exact congrArg (List.cons b) hj
        · intro piece hp
          rcases List.mem_cons.mp hp with hp | hp
          · subst piece
            intro hq
            rcases List.mem_cons.mp hq with hq | hq
            · exact hb hq.symm
            · exact hn first List.mem_cons_self hq
          · exact hn piece (List.mem_cons_of_mem first hp)

/-- A final outside gap is required; paired quotes determine all selected tokens. -/
def selectTokens : List (List UInt8) → Option (List (List UInt8))
  | [] => none
  | [_] => some []
  | _ :: token :: rest => (selectTokens rest).map (fun tokens => token :: tokens)

def scan (bytes : List UInt8) : Option (List (List UInt8)) :=
  selectTokens (splitQuotes bytes)

/-- Exact original-byte decomposition and chronological token order. This is
not a JSON grammar or an assertion that tokens are object-field names. -/
inductive Regions : List UInt8 → List (List UInt8) → Prop where
  | done {gap : List UInt8} : (34 : UInt8) ∉ gap → Regions gap []
  | more {gap token rest : List UInt8} {tokens : List (List UInt8)} :
      (34 : UInt8) ∉ gap → (34 : UInt8) ∉ token → Regions rest tokens →
      Regions (gap ++ 34 :: (token ++ 34 :: rest)) (token :: tokens)

private theorem selectTokens_nonempty (pieces tokens : List (List UInt8))
    (h : selectTokens pieces = some tokens) : pieces ≠ [] := by
  intro he
  rw [he] at h
  cases h

private theorem selectTokens_sound (pieces tokens : List (List UInt8))
    (h : selectTokens pieces = some tokens)
    (hsafe : ∀ piece ∈ pieces, (34 : UInt8) ∉ piece) :
    Regions (joinChunks pieces) tokens := by
  cases hp : pieces with
  | nil => simp only [hp, selectTokens] at h; cases h
  | cons gap following =>
      rw [hp] at h hsafe
      cases hf : following with
      | nil =>
          rw [hf] at h hsafe
          have he : tokens = [] := (Option.some.inj h).symm
          rw [he]
          simpa only [joinChunks, joinTail, List.append_nil] using
            Regions.done (hsafe gap List.mem_cons_self)
      | cons token rest =>
          rw [hf] at h hsafe
          obtain ⟨tokens', hr, he⟩ := Option.map_eq_some_iff.mp h
          rw [← he]
          have hrest : Regions (joinChunks rest) tokens' :=
            selectTokens_sound rest tokens' hr (fun piece hp =>
              hsafe piece (List.mem_cons_of_mem gap (List.mem_cons_of_mem token hp)))
          have hn := selectTokens_nonempty rest tokens' hr
          have hj : joinChunks (gap :: token :: rest) =
              gap ++ 34 :: (token ++ 34 :: joinChunks rest) := by
            cases rest with
            | nil => exact False.elim (hn rfl)
            | cons next rest => rfl
          rw [hj]
          exact Regions.more (hsafe gap List.mem_cons_self)
            (hsafe token (List.mem_cons_of_mem gap List.mem_cons_self)) hrest
termination_by pieces.length
decreasing_by simp_all only [List.length_cons]; omega

/-- Successful discovery preserves exact quoted regions and their full input order. -/
theorem scan_sound (bytes : List UInt8) (tokens : List (List UInt8))
    (h : scan bytes = some tokens) : Regions bytes tokens := by
  obtain ⟨first, rest, hs, hj, hn⟩ := splitQuotes_spec bytes
  have ht : selectTokens (first :: rest) = some tokens := by
    simpa only [scan, hs] using h
  have hr := selectTokens_sound (first :: rest) tokens ht hn
  rw [hj] at hr
  exact hr

private theorem splitQuotes_plain (gap : List UInt8) (h : (34 : UInt8) ∉ gap) :
    splitQuotes gap = [gap] := by
  induction gap with
  | nil => rfl
  | cons b bs ih =>
      have hb : b ≠ 34 := fun he => h (by rw [he]; exact List.mem_cons_self)
      have ht : (34 : UInt8) ∉ bs := fun hm => h (List.mem_cons_of_mem b hm)
      simp only [splitQuotes, if_neg hb, ih ht]

private theorem splitQuotes_gap (gap rest : List UInt8) (h : (34 : UInt8) ∉ gap) :
    splitQuotes (gap ++ 34 :: rest) = gap :: splitQuotes rest := by
  induction gap with
  | nil => simp only [List.nil_append, splitQuotes, if_pos rfl, if_true]
  | cons b bs ih =>
      have hb : b ≠ 34 := fun he => h (by rw [he]; exact List.mem_cons_self)
      have ht : (34 : UInt8) ∉ bs := fun hm => h (List.mem_cons_of_mem b hm)
      simp only [List.cons_append, splitQuotes, if_neg hb, ih ht]

/-- Completeness for exactly the quoted-region relation, without a JSON parser claim. -/
theorem scan_complete {bytes : List UInt8} {tokens : List (List UInt8)}
    (h : Regions bytes tokens) : scan bytes = some tokens := by
  induction h with
  | done hgap =>
      simp only [scan, splitQuotes_plain _ hgap, selectTokens]
  | more hgap htoken hrest ih =>
      unfold scan
      rw [splitQuotes_gap _ _ hgap, splitQuotes_gap _ _ htoken]
      change (scan _).map (fun ts => _ :: ts) = _
      rw [ih]
      rfl

private theorem allowed_not_quote (c : Char) (h : CompactNatColumnAscii.Allowed c) :
    c.val.toUInt8 ≠ (34 : UInt8) := by
  rcases h with h | h | h | ⟨d, h⟩
  · subst c; decide
  · subst c; decide
  · subst c; decide
  · subst c
    exact (by decide : ∀ d : Fin 10, (Nat.digitChar d.val).val.toUInt8 ≠ (34 : UInt8)) d

/-- The accepted arbitrary-size compact Nat payload cannot contain a quote byte. -/
theorem compact_quote_free (xs : List Nat) :
    (34 : UInt8) ∉ (CompactNatColumnFragment.encode xs).data.toList := by
  rw [CompactNatColumnAscii.encode_one_byte]
  intro hm
  obtain ⟨c, hc, he⟩ := List.mem_map.mp hm
  exact allowed_not_quote c (CompactNatColumnAscii.text_allowed xs c hc) he

theorem payload_quote_free {n : Nat} (cols : JsonPackedColumnDictionary.Columns n) :
    (34 : UInt8) ∉ (CompactNatColumnFragment.payload cols).data.toList :=
  compact_quote_free (CompactNatColumnFragment.natValues cols)

/-- The executed key policy excludes the delimiter in actual serialized key bytes. -/
theorem hex_key_quote_free (key : String) (h : HexObjectLayout.keyPolicy key = true) :
    (34 : UInt8) ∉ HexObjectLayout.keyBytes key := by
  intro hm
  have hb := ((HexObjectLayout.keyPolicy_iff key).mp h).2 34 hm
  change (48 ≤ 34 ∧ 34 ≤ 57) ∨ (97 ≤ 34 ∧ 34 ≤ 102) at hb
  omega

/-- An additional quote-free outside gap changes no discovered token. -/
theorem Regions.prepend {bytes : List UInt8} {tokens : List (List UInt8)}
    (h : Regions bytes tokens) (extra : List UInt8) (he : (34 : UInt8) ∉ extra) :
    Regions (extra ++ bytes) tokens := by
  cases h with
  | done hgap =>
      apply Regions.done
      simpa only [List.mem_append, not_or] using And.intro he hgap
  | @more gap token rest tokens hgap htoken hrest =>
      have hg : (34 : UInt8) ∉ extra ++ gap := by
        simpa only [List.mem_append, not_or] using And.intro he hgap
      simpa only [List.append_assoc] using Regions.more hg htoken hrest

private theorem payload_gap_free (payload : ByteArray)
    (h : (34 : UInt8) ∉ payload.data.toList) :
    (34 : UInt8) ∉ 58 :: payload.data.toList := by
  simp only [List.mem_cons, not_or]
  exact ⟨by decide, h⟩

private theorem tail_regions (fields : List HexObjectLayout.Field)
    (hk : ∀ f ∈ fields, HexObjectLayout.keyPolicy f.key = true)
    (hp : ∀ f ∈ fields, (34 : UInt8) ∉ f.payload.data.toList) :
    Regions (HexObjectLayout.tailBytes fields ++ [125])
      (fields.map (fun f => HexObjectLayout.keyBytes f.key)) := by
  induction fields with
  | nil => exact Regions.done (by decide)
  | cons f fs ih =>
      have hr := ih (fun g hg => hk g (List.mem_cons_of_mem f hg))
        (fun g hg => hp g (List.mem_cons_of_mem f hg))
      have hafter := hr.prepend (58 :: f.payload.data.toList)
        (payload_gap_free f.payload (hp f List.mem_cons_self))
      have hm := Regions.more (gap := [44]) (by decide)
        (hex_key_quote_free f.key (hk f List.mem_cons_self)) hafter
      simpa only [HexObjectLayout.tailBytes, HexObjectLayout.fieldBytes,
        HexObjectLayout.header, List.map_cons, List.singleton_append,
        List.cons_append, List.nil_append, List.append_assoc] using hm

/-- Complete braces, separators, keys and payloads instantiate the ordered-region
invariant. No prefix, suffix or field may be omitted. -/
theorem layout_regions (fields : List HexObjectLayout.Field)
    (hk : ∀ f ∈ fields, HexObjectLayout.keyPolicy f.key = true)
    (hp : ∀ f ∈ fields, (34 : UInt8) ∉ f.payload.data.toList) :
    Regions (HexObjectLayout.objectBytes fields)
      (fields.map (fun f => HexObjectLayout.keyBytes f.key)) := by
  cases fields with
  | nil => exact Regions.done (by decide)
  | cons f fs =>
      have hr := tail_regions fs (fun g hg => hk g (List.mem_cons_of_mem f hg))
        (fun g hg => hp g (List.mem_cons_of_mem f hg))
      have hafter := hr.prepend (58 :: f.payload.data.toList)
        (payload_gap_free f.payload (hp f List.mem_cons_self))
      have hm := Regions.more (gap := [123]) (by decide)
        (hex_key_quote_free f.key (hk f List.mem_cons_self)) hafter
      simpa only [HexObjectLayout.objectBytes, HexObjectLayout.bodyBytes,
        HexObjectLayout.fieldBytes, HexObjectLayout.header, List.map_cons,
        List.singleton_append, List.cons_append, List.nil_append, List.append_assoc] using hm

/-- Actual scanner success for a complete accepted restricted layout. -/
theorem scan_layout (fields : List HexObjectLayout.Field)
    (hk : HexObjectLayout.checkKeys fields = true)
    (hp : ∀ f ∈ fields, (34 : UInt8) ∉ f.payload.data.toList) :
    scan (HexObjectLayout.encode fields).data.toList =
      some (fields.map (fun f => HexObjectLayout.keyBytes f.key)) := by
  have hr := layout_regions fields ((HexObjectLayout.checkKeys_iff fields).mp hk).1 hp
  simpa only [HexObjectLayout.encode, List.toList_toArray] using scan_complete hr

end CurrentMain.QuoteTokenScan
#print axioms CurrentMain.QuoteTokenScan.scan_sound
#print axioms CurrentMain.QuoteTokenScan.scan_complete
#print axioms CurrentMain.QuoteTokenScan.compact_quote_free
#print axioms CurrentMain.QuoteTokenScan.payload_quote_free
#print axioms CurrentMain.QuoteTokenScan.hex_key_quote_free
#check @CurrentMain.QuoteTokenScan.scan_sound
#check @CurrentMain.QuoteTokenScan.scan_complete
#print axioms CurrentMain.QuoteTokenScan.layout_regions
#print axioms CurrentMain.QuoteTokenScan.scan_layout
