import Init

/-!
UNCOMPILED shared strict parsed-value boundary for selected current1094 source
rows and owner declarations. Integer tokens, booleans, strings and arrays stay
disjoint; other syntax (objects, null and decimal/exponent number tokens) is
rejected by these small scalar/array decoders. A correct byte/JSON parser and
its duplicate-key checks remain an explicit earlier obligation.

The selected register universe is704 ordinary L plus8 private C tags. C tags
are not carrier owners or numeric physical addresses. No label/chart, owner,
recipe or executor interpretation is assigned here. Prepared with OpenAI
assistance; Apache-2.0. Selected emitter/source attribution is preserved by
its consuming packets.
-/
namespace CurrentMain.SelectedSourceSyntax

inductive Value where
  | text (s : String)
  | integer (n : Int)
  | boolean (b : Bool)
  | array (xs : List Value)
  | other

abbrev Register := Fin 704 ⊕ Fin 8

def natValue : Value → Option Nat
  | .integer n => if 0 ≤ n then some n.toNat else none
  | _ => none

def bounded (n : Nat) (v : Value) : Option (Fin n) := do
  let a ← natValue v
  if h : a < n then some ⟨a,h⟩ else none

def register : Value → Option Register
  | .array [.text "L", v] => (bounded 704 v).map Sum.inl
  | .array [.text "C", v] => (bounded 8 v).map Sum.inr
  | _ => none

end CurrentMain.SelectedSourceSyntax
