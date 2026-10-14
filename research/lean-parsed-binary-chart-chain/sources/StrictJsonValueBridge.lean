import StrictParsedIndexCodec
import Lean.Data.Json.Basic
import Init.Data.Array.Basic

/-!
A reusable bridge from the installed Lean.Json AST to strict parsed Values.
Numbers are accepted only in the exact JsonNumber representation (mantissa,0).
Booleans and strings keep their own tags; arrays are traversed in original order.
Null, objects and nonzero number exponents are rejected. In particular the AST
number (10,1), whose numeric value is 1.0, is not normalized into integer1.

This is an AST policy, not a lexical JSON-integer claim: the upstream byte parser
may map different spellings, including exponent syntax, to the same AST. Fuel
limits nesting; exhaustion rejects instead of inventing a partial value. Success
re-encodes to the complete input AST, including every ordered array occurrence.
The re-encoder's zero-fuel/default null is never a successful decoding witness.

The bounded index/array consumers call the actual bridge and existing strict
codec. Their success is characterized by full canonical AST equality, with no
assumed array result, uniqueness, dimensions or selected source table.
JSON byte-parser correctness, original file correspondence, physical reads,
allocation, runtime price and bit representation remain separate obligations.
James Chang with OpenAI assistance; Apache-2.0. Reuses the accepted strict codec
and Lean's official Json/Array/List/Option definitions. Author-checked context:
kappa=836330098538459/500000000000000000; the generic theorem does not use it.
Uncompiled source candidate.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.StrictJsonValueBridge
open SelectedSourceSyntax (Value bounded)
open StrictParsedIndexCodec (indexValue bounded_eq_some_iff mapM_reencode)

/-- Structurally fuel-bounded traversal of the actual installed JSON AST. -/
def decode : Nat → Lean.Json → Option Value
  | 0, _ => none
  | _ + 1, .str s => some (.text s)
  | _ + 1, .bool b => some (.boolean b)
  | _ + 1, .num ⟨m, 0⟩ => some (.integer m)
  | fuel + 1, .arr xs => do
      let ys ← xs.toList.mapM (decode fuel)
      some (.array ys)
  | _ + 1, _ => none

/-- Reconstruct the same AST at sufficient depth. Null is only an otherwise
unreachable default, not a representation accepted by decode. -/
def reencode : Nat → Value → Lean.Json
  | 0, _ => .null
  | _ + 1, .text s => .str s
  | _ + 1, .boolean b => .bool b
  | _ + 1, .integer m => .num ⟨m, 0⟩
  | fuel + 1, .array xs => .arr (xs.map (reencode fuel)).toArray
  | _ + 1, .other => .null

/-- Exact AST reconstruction includes all nested ordered array occurrences. -/
theorem decode_sound (fuel : Nat) (raw : Lean.Json) (v : Value)
    (h : decode fuel raw = some v) : reencode fuel v = raw := by
  induction fuel generalizing raw v with
  | zero => cases h
  | succ fuel ih =>
      cases raw with
      | null => cases h
      | bool b =>
          have hv : Value.boolean b = v := Option.some.inj h
          cases hv
          rfl
      | str s =>
          have hv : Value.text s = v := Option.some.inj h
          cases hv
          rfl
      | num number =>
          cases number with
          | mk m exponent =>
              cases exponent with
              | zero =>
                  have hv : Value.integer m = v := Option.some.inj h
                  cases hv
                  rfl
              | succ e => cases h
      | obj fields => cases h
      | arr xs =>
          change (xs.toList.mapM (decode fuel) >>= fun ys => some (Value.array ys)) = some v at h
          obtain ⟨ys, hys, hv⟩ := Option.bind_eq_some_iff.mp h
          have he : Value.array ys = v := Option.some.inj hv
          cases he
          have hr := mapM_reencode (decode fuel) (reencode fuel)
            (fun raw value hs => ih raw value hs) xs.toList ys hys
          change Lean.Json.arr (ys.map (reencode fuel)).toArray = Lean.Json.arr xs
          rw [hr]

/-- Nonzero exponent representations are rejected, even if numerically integral. -/
theorem positive_exponent_rejected (fuel : Nat) (m : Int) (e : Nat) :
    decode (fuel + 1) (.num ⟨m, e + 1⟩) = none := rfl

/-- Boolean values remain Boolean Values and never become numeric tokens. -/
theorem boolean_preserved (fuel : Nat) (b : Bool) :
    decode (fuel + 1) (.bool b) = some (.boolean b) := rfl

def indexJson {n : Nat} (i : Fin n) : Lean.Json := .num ⟨(i.val : Int), 0⟩

/-- Actual scalar conversion followed by the already accepted bounded decoder. -/
def index (n : Nat) (raw : Lean.Json) : Option (Fin n) := do
  let v ← decode 1 raw
  bounded n v

theorem index_eq_some_iff (n : Nat) (raw : Lean.Json) (i : Fin n) :
    index n raw = some i ↔ raw = indexJson i := by
  constructor
  · intro h
    obtain ⟨v, hv, hi⟩ := Option.bind_eq_some_iff.mp h
    have he : v = indexValue i := (bounded_eq_some_iff n v i).mp hi
    subst v
    exact (decode_sound 1 raw (indexValue i) hv).symm
  · intro h
    subst raw
    change bounded n (indexValue i) = some i
    exact (bounded_eq_some_iff n (indexValue i) i).mpr rfl

def indexArrayJson {n : Nat} (xs : List (Fin n)) : Lean.Json :=
  .arr (xs.map indexJson).toArray

/-- Order and repeated entries are retained; no permutation premise is imposed. -/
def indices (n : Nat) : Lean.Json → Option (List (Fin n))
  | .arr xs => xs.toList.mapM (index n)
  | _ => none

private theorem indices_canonical {n : Nat} (xs : List (Fin n)) :
    indices n (indexArrayJson xs) = some xs := by
  change (xs.map indexJson).mapM (index n) = some xs
  rw [List.mapM_map]
  have hread : index n ∘ indexJson = (fun i : Fin n => some i) := by
    funext i
    exact (index_eq_some_iff n (indexJson i) i).mpr rfl
  rw [hread]
  simpa only [List.map_id] using (List.mapM_pure (m := Option) (l := xs) (f := id))

/-- The complete original index array is recovered, including order/multiplicity. -/
theorem indices_eq_some_iff (n : Nat) (raw : Lean.Json) (xs : List (Fin n)) :
    indices n raw = some xs ↔ raw = indexArrayJson xs := by
  constructor
  · intro h
    cases raw with
    | null => cases h
    | bool b => cases h
    | num number => cases h
    | str s => cases h
    | obj fields => cases h
    | arr ys =>
        have he := mapM_reencode (index n) indexJson
          (fun raw i hi => ((index_eq_some_iff n raw i).mp hi).symm) ys.toList xs h
        change Lean.Json.arr ys = Lean.Json.arr (xs.map indexJson).toArray
        rw [he]
  · intro h
    subst raw
    exact indices_canonical xs

end CurrentMain.StrictJsonValueBridge
#print axioms CurrentMain.StrictJsonValueBridge.decode_sound
#print axioms CurrentMain.StrictJsonValueBridge.positive_exponent_rejected
#print axioms CurrentMain.StrictJsonValueBridge.boolean_preserved
#print axioms CurrentMain.StrictJsonValueBridge.index_eq_some_iff
#print axioms CurrentMain.StrictJsonValueBridge.indices_eq_some_iff
#check @CurrentMain.StrictJsonValueBridge.decode_sound
#check @CurrentMain.StrictJsonValueBridge.indices_eq_some_iff
