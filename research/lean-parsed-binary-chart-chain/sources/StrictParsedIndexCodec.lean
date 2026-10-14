import SelectedSourceSyntax
import Init.Data.List.Monadic
import Init.Data.Option.Lemmas

/-!
UNCOMPILED reusable correctness of the existing strict parsed-index primitives.
Bounds and both register-bank dimensions are parameters. Successful scalar and
ordered-list decoding preserves the exact Value constructor and integer; it
cannot identify a Boolean with an integer, wrap an out-of-range Fin index, or
forget list order/multiplicity. The tagged decoder is the existing L/C decoder
with only its dimensions generalized, and the selected704/8 implementation is
connected by definitional equality.

The denotation below is ordinary logical indexing into two supplied arrays.
No JSON-byte parser, physical family/address allocator, chart, recipe or scalar
executor is introduced. This closes a parsed-input correctness boundary shared
by owner/route fields and instruction operands, rather than assuming decoder
success implies an unproved physical interpretation.

The thin current source context is author-checked
kappa=836330098538459/500000000000000000=0.001672660197076918.
Credits: the accepted shared Value grammar and source emitter lineage retain
PR1094/Rohan Arun, Jeremy Kothe, icekylinx/PR425/433 and DreamingOfClouds;
Lean List/Option/Int infrastructure. Apache-2.0; OpenAI assistance.
-/
set_option Elab.async false
namespace CurrentMain.StrictParsedIndexCodec
universe u v
open SelectedSourceSyntax (Value natValue bounded)

/-- An integer token is canonical at this parsed boundary, not a JSON byte token. -/
def indexValue {n : Nat} (i : Fin n) : Value := .integer i.val

/-- Success excludes all other Value constructors and every negative integer. -/
theorem natValue_eq_some_iff (v : Value) (n : Nat) :
    natValue v = some n ↔ v = .integer (Int.ofNat n) := by
  cases v with
  | text s => simp [natValue]
  | integer z => cases z <;> simp [natValue, Int.ofNat_inj]
  | boolean b => simp [natValue]
  | array xs => simp [natValue]
  | other => simp [natValue]

/-- Arbitrary bounds: the successful index has exactly the input integer. -/
theorem bounded_eq_some_iff (n : Nat) (v : Value) (i : Fin n) :
    bounded n v = some i ↔ v = indexValue i := by
  constructor
  · intro h
    cases hv : natValue v with
    | none => simp [bounded, hv] at h
    | some a =>
        have he := (natValue_eq_some_iff v a).mp hv
        subst v
        by_cases ha : a < n
        · have hi : (⟨a, ha⟩ : Fin n) = i := by
            simpa [bounded, natValue, ha] using h
          cases hi
          rfl
        · simp [bounded, natValue, ha] at h
  · intro h
    subst v
    simp [indexValue, bounded, natValue, i.isLt]

/-- A partial inverse lifts through actual ordered Option.mapM evaluation.
No uniqueness assumption is made on xs: repeated elements are preserved. -/
theorem mapM_reencode {α : Type u} {β : Type v} (decode : α → Option β) (encode : β → α)
    (hsound : ∀ x y, decode x = some y → encode y = x)
    (xs : List α) (ys : List β) (h : xs.mapM decode = some ys) :
    ys.map encode = xs := by
  induction xs generalizing ys with
  | nil =>
      have he : ([] : List β) = ys := by simpa using h
      cases he
      rfl
  | cons x xs ih =>
      rw [List.mapM_cons] at h
      change (decode x >>= fun y =>
        xs.mapM decode >>= fun zs => some (y :: zs)) = some ys at h
      obtain ⟨y, hy, htail⟩ := Option.bind_eq_some_iff.mp h
      obtain ⟨zs, hzs, he⟩ := Option.bind_eq_some_iff.mp htail
      have hey : y :: zs = ys := Option.some.inj he
      cases hey
      rw [List.map_cons, hsound x y hy, ih zs hzs]

/-- Ordered spectator/owner index lists are preserved with all multiplicities. -/
theorem boundedList_eq_some_iff (n : Nat) (xs : List Value) (ys : List (Fin n)) :
    xs.mapM (bounded n) = some ys ↔ xs = ys.map indexValue := by
  constructor
  · intro h
    exact (mapM_reencode (bounded n) indexValue
      (fun x y hy => ((bounded_eq_some_iff n x y).mp hy).symm) xs ys h).symm
  · intro h
    subst xs
    induction ys with
    | nil => rfl
    | cons y ys ih =>
        simp only [List.map_cons, List.mapM_cons,
          (bounded_eq_some_iff n (indexValue y) y).mpr rfl, ih]
        rfl

/-- The same strict two-tag syntax, with both finite sizes left arbitrary. -/
def taggedIndex (ordinary privateCount : Nat) : Value → Option (Fin ordinary ⊕ Fin privateCount)
  | .array [.text "L", v] => (bounded ordinary v).map Sum.inl
  | .array [.text "C", v] => (bounded privateCount v).map Sum.inr
  | _ => none

def taggedValue {ordinary privateCount : Nat} : Fin ordinary ⊕ Fin privateCount → Value
  | .inl i => .array [.text "L", indexValue i]
  | .inr i => .array [.text "C", indexValue i]

private theorem taggedIndex_sound {ordinary privateCount : Nat} (v : Value)
    (r : Fin ordinary ⊕ Fin privateCount) (h : taggedIndex ordinary privateCount v = some r) :
    taggedValue r = v := by
  unfold taggedIndex at h
  split at h
  · obtain ⟨i, hi, hr⟩ := Option.map_eq_some_iff.mp h
    cases hr
    exact congrArg (fun x => Value.array [.text "L", x])
      ((bounded_eq_some_iff _ _ _).mp hi).symm
  · obtain ⟨i, hi, hr⟩ := Option.map_eq_some_iff.mp h
    cases hr
    exact congrArg (fun x => Value.array [.text "C", x])
      ((bounded_eq_some_iff _ _ _).mp hi).symm
  · cases h

private theorem taggedIndex_complete {ordinary privateCount : Nat}
    (r : Fin ordinary ⊕ Fin privateCount) :
    taggedIndex ordinary privateCount (taggedValue r) = some r := by
  cases r with
  | inl i => simp [taggedIndex, taggedValue, indexValue, bounded, natValue, i.isLt]
  | inr i => simp [taggedIndex, taggedValue, indexValue, bounded, natValue, i.isLt]

/-- Actual parser success is equivalent to the exact canonical tagged input. -/
theorem taggedIndex_eq_some_iff (ordinary privateCount : Nat) (v : Value)
    (r : Fin ordinary ⊕ Fin privateCount) :
    taggedIndex ordinary privateCount v = some r ↔ v = taggedValue r := by
  constructor
  · intro h
    exact (taggedIndex_sound v r h).symm
  · intro h
    subst v
    exact taggedIndex_complete r

/-- A dimension-parametric logical read, following the decoder's actual branch. -/
def readParsed {α : Type u} {ordinary privateCount : Nat}
    (ordinaryValues : Fin ordinary → α) (privateValues : Fin privateCount → α)
    (v : Value) : Option α :=
  (taggedIndex ordinary privateCount v).map (Sum.elim ordinaryValues privateValues)

/-- The denotation is derived from the executable decoder. Both banks and all
indices remain tagged; equal stored values do not imply equal register tags. -/
theorem readParsed_eq_some_iff {α : Type u} {ordinary privateCount : Nat}
    (ordinaryValues : Fin ordinary → α) (privateValues : Fin privateCount → α)
    (v : Value) (a : α) :
    readParsed ordinaryValues privateValues v = some a ↔
      ∃ r : Fin ordinary ⊕ Fin privateCount,
        v = taggedValue r ∧ Sum.elim ordinaryValues privateValues r = a := by
  simp only [readParsed, Option.map_eq_some_iff, taggedIndex_eq_some_iff]

/-- Thin current application: this is the unchanged decoder used by the
accepted owner/route/instruction packages, not a new implementation claim. -/
theorem selected_register_eq_some_iff (v : Value) (r : SelectedSourceSyntax.Register) :
    SelectedSourceSyntax.register v = some r ↔ v = taggedValue r := by
  change taggedIndex 704 8 v = some r ↔ v = taggedValue r
  exact taggedIndex_eq_some_iff 704 8 v r

end CurrentMain.StrictParsedIndexCodec
#print axioms CurrentMain.StrictParsedIndexCodec.natValue_eq_some_iff
#print axioms CurrentMain.StrictParsedIndexCodec.bounded_eq_some_iff
#print axioms CurrentMain.StrictParsedIndexCodec.mapM_reencode
#print axioms CurrentMain.StrictParsedIndexCodec.boundedList_eq_some_iff
#print axioms CurrentMain.StrictParsedIndexCodec.taggedIndex_eq_some_iff
#print axioms CurrentMain.StrictParsedIndexCodec.readParsed_eq_some_iff
#print axioms CurrentMain.StrictParsedIndexCodec.selected_register_eq_some_iff
