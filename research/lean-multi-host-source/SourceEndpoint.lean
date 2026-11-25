import MatrixCertificate
import SourceTables
import PayloadGuards

/-!
The literal 19,002-event normalized word is correct for every assignment to
all 987 dirty original roles, including arbitrary dirty helper values.
There is exactly one designated clean temporary (role 987). The result
also holds for entire arbitrary Boolean-valued streams, pointwise in an
address of any type. Physical frames and role ownership are separate
source obligations and are not inferred from this normalized identity.
-/
namespace SourceMatrix
open TreeReplay
set_option maxRecDepth 100000
set_option maxHeartbeats 0

theorem arbitrary_dirty_bools (input : Nat → Bool) :
    runBools forwardWord (dirtyInput 10 987 input) =
      Tree.tabulate 10 (endpointValue input) := by
  have hi := (congrArg (evalRows 987 input) initial_formula).trans
    (evalRows_basisRows 10 987 input)
  have ho := (congrArg (evalRows 987 input) expected_formula).trans
    (evalRows_endpoint input)
  exact (congrArg (runBools forwardWord) hi).symm.trans
    ((evalRows_run 987 input forwardWord initial).symm.trans
      ((congrArg (evalRows 987 input) literal_word_rows).trans ho))

theorem arbitrary_dirty_guards (input : Nat → Bool) :
    (runCheckedBools forwardWord (dirtyInput 10 987 input, true)).2 = true := by
  have h : (runCheckedRows forwardWord (initial, true)).2 = true :=
    congrArg Prod.snd literal_word_checked
  have hs := checked_guards_sound 987 input forwardWord (initial, true) h
  have hi := (congrArg (evalRows 987 input) initial_formula).trans
    (evalRows_basisRows 10 987 input)
  exact (congrArg (fun s => (runCheckedBools forwardWord (s, true)).2) hi).symm.trans hs

theorem arbitrary_dirty_payloads {X : Type u} (input : Nat → X → Bool) :
    runPayloads forwardWord
      (Tree.tabulate 10 (fun i => if i < 987 then input i else fun _ => false)) =
      Tree.tabulate 10 (endpointPayload input) := by
  have hi := (congrArg (evalPayloadRows 987 input) initial_formula).trans
    (evalPayloadRows_basisRows 10 987 input)
  have ho := (congrArg (evalPayloadRows 987 input) expected_formula).trans
    (evalPayloadRows_endpoint input)
  exact (congrArg (runPayloads forwardWord) hi).symm.trans
    ((evalPayloadRows_run 987 input forwardWord initial).symm.trans
      ((congrArg (evalPayloadRows 987 input) literal_word_rows).trans ho))

theorem actual_payload_clean {X : Type u} (input : Nat → X → Bool) :
    PayloadCleanRun forwardWord
      (Tree.tabulate 10 (fun i => if i < 987 then input i else fun _ => false)) := by
  have h : (runCheckedRows forwardWord (initial, true)).2 = true :=
    congrArg Prod.snd literal_word_checked
  have hs := checked_payload_guards_sound 987 input forwardWord (initial, true) h
  have hi := (congrArg (evalPayloadRows 987 input) initial_formula).trans
    (evalPayloadRows_basisRows 10 987 input)
  exact Eq.mp (congrArg (PayloadCleanRun forwardWord) hi) hs

/-- The temporary is restored for every dirty payload assignment. -/
theorem arbitrary_dirty_temp_restored {X : Type u} (input : Nat → X → Bool) :
    (runPayloads forwardWord
      (Tree.tabulate 10 (fun i => if i < 987 then input i else fun _ => false))).get 987 =
      fun _ => false := by
  rw [arbitrary_dirty_payloads, Tree.get_tabulate 10 _ 987 (by decide)]
  rfl

/-- Every original role is accounted for in the endpoint equation. -/
theorem arbitrary_dirty_original_roles {X : Type u} (input : Nat → X → Bool)
    (i : Nat) (hi : i < 987) :
    (runPayloads forwardWord
      (Tree.tabulate 10 (fun i => if i < 987 then input i else fun _ => false))).get i =
      if 120 ≤ i ∧ i < 240 then fun x => input i x ^^ input (i - 120) x else input i := by
  rw [arbitrary_dirty_payloads, Tree.get_tabulate 10 _ i (by omega)]
  simp only [endpointPayload, hi, ↓reduceIte]

#print axioms arbitrary_dirty_bools
#print axioms arbitrary_dirty_guards
#print axioms arbitrary_dirty_payloads
#print axioms actual_payload_clean
#print axioms arbitrary_dirty_temp_restored
#print axioms arbitrary_dirty_original_roles

end SourceMatrix
