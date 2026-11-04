import TreeReplay

/-!
Interpretation of the checked endpoint matrix of the selected bit invocation.
Roles 0..986 are arbitrary dirty inputs; role 987 is the clean temporary.
Rows 120..239 receive rows 0..119 by XOR, and every other row is retained.
This file states the formulas independently of the generated certificate.
-/
namespace SourceMatrix
set_option maxRecDepth 100000
open TreeReplay
open LinearReplay (evalRow evalRow_zero evalRow_xor evalRow_shift_basis)

-- Use the generic evaluator/tabulation lemmas in these proofs. Avoid eagerly
-- expanding the literal row count or the complete tabulated tree in Lean 4.21.
attribute [local irreducible] evalRow Tree.tabulate

def endpointRow (i : Nat) : Nat :=
  if i < 987 then
    if 120 ≤ i ∧ i < 240 then (1 <<< i) ^^^ (1 <<< (i - 120)) else 1 <<< i
  else 0

def endpointValue (u : Nat → Bool) (i : Nat) : Bool :=
  if i < 987 then
    if 120 ≤ i ∧ i < 240 then u i ^^ u (i - 120) else u i
  else false

theorem evalRow_endpoint (u : Nat → Bool) (i : Nat) :
    evalRow 987 u (endpointRow i) = endpointValue u i := by
  unfold endpointRow endpointValue
  by_cases h : i < 987
  · by_cases htarget : 120 ≤ i ∧ i < 240
    · have hsource : i - 120 < 987 := by omega
      simp [h, htarget, evalRow_xor, evalRow_shift_basis, hsource]
    · simp [h, htarget, evalRow_shift_basis]
  · simp [h]

theorem evalRows_endpoint (u : Nat → Bool) :
    evalRows 987 u (Tree.tabulate 10 endpointRow) = Tree.tabulate 10 (endpointValue u) := by
  simp only [evalRows, Tree.map_tabulate]
  have hf : (fun i => evalRow 987 u (endpointRow i)) = endpointValue u :=
    funext (evalRow_endpoint u)
  exact congrArg (Tree.tabulate 10) hf

def endpointPayload {X : Type u} (input : Nat → X → Bool) (i : Nat) : X → Bool :=
  if i < 987 then
    if 120 ≤ i ∧ i < 240 then fun x => input i x ^^ input (i - 120) x else input i
  else fun _ => false

theorem evalPayloadRows_endpoint {X : Type u} (input : Nat → X → Bool) :
    evalPayloadRows 987 input (Tree.tabulate 10 endpointRow) =
      Tree.tabulate 10 (endpointPayload input) := by
  simp only [evalPayloadRows, Tree.map_tabulate]
  apply congrArg (Tree.tabulate 10)
  funext i x
  by_cases h : i < 987 <;> by_cases ht : 120 ≤ i ∧ i < 240 <;>
    simpa [Function.comp_apply, endpointValue, endpointPayload, h, ht] using
      evalRow_endpoint (fun j => input j x) i

end SourceMatrix
