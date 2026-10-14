import StrictParsedIndexCodec
import CheckedBinaryChart

/-!
UNCOMPILED reusable finite permutation certificates from strict parsed tables.
Both dimensions and all entries are parameters. The decoder checks the exact
array length and every integer bound using the accepted parsed-index codec.
The Boolean certificate then checks both ordered table round trips. An actual
permutation, with executable forward and inverse lookup, is constructed from
those checks; no bijectivity proof or operator equality is an input.

The final bridge supplies that checked permutation to CheckedBinaryChart.
Its independent scalar column certificate still must pass. JSON-byte parsing,
source selection, physical chart convention, complex phase, affine shifts,
rounding and cost remain separate. The dimension zero case is included.

Author-checked context only:
kappa=836330098538459/500000000000000000=0.001672660197076918.
The generic theorem does not depend on this number or prove multiplication.
Credits: accepted SelectedSourceSyntax/StrictParsedIndexCodec, Lean List/Option
and Mathlib Equiv infrastructure; existing selected emitter lineage retains
PR1094/Rohan Arun, Jeremy Kothe, icekylinx and DreamingOfClouds. Apache-2.0;
OpenAI assistance. No literal source census or new byte parser is introduced.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.CheckedPermutationTables
open SelectedSourceSyntax (Value bounded)
open StrictParsedIndexCodec (indexValue boundedList_eq_some_iff)

/-- Length and bounded entries are checked data, not a permutation premise. -/
abbrev Table (n : Nat) := { xs : List (Fin n) // xs.length = n }

def tableAt {n : Nat} (t : Table n) (i : Fin n) : Fin n :=
  t.val.get (Fin.cast t.property.symm i)

def tableValue {n : Nat} (t : Table n) : Value :=
  .array (t.val.map indexValue)

def decodeTable (n : Nat) : Value → Option (Table n)
  | .array xs => do
      let ys ← xs.mapM (bounded n)
      if h : ys.length = n then some ⟨ys, h⟩ else none
  | _ => none

/-- Success preserves the complete ordered parsed array and every integer. -/
theorem decodeTable_sound {n : Nat} (v : Value) (t : Table n)
    (h : decodeTable n v = some t) : tableValue t = v := by
  cases v with
  | text s => cases h
  | integer z => cases h
  | boolean b => cases h
  | other => cases h
  | array xs =>
      change (xs.mapM (bounded n) >>= fun ys =>
        if hlen : ys.length = n then some (⟨ys, hlen⟩ : Table n) else none) = some t at h
      obtain ⟨ys, hys, ht⟩ := Option.bind_eq_some_iff.mp h
      split at ht
      · rename_i hlen
        have he : (⟨ys, hlen⟩ : Table n) = t := Option.some.inj ht
        cases he
        exact congrArg Value.array ((boundedList_eq_some_iff n xs ys).mp hys).symm
      · cases ht

/-- The decoder accepts every exact-length, bounded table in canonical syntax. -/
theorem decodeTable_complete {n : Nat} (t : Table n) :
    decodeTable n (tableValue t) = some t := by
  rcases t with ⟨ys, hlen⟩
  change ((ys.map indexValue).mapM (bounded n) >>= fun zs =>
    if hz : zs.length = n then some (⟨zs, hz⟩ : Table n) else none) = some ⟨ys, hlen⟩
  rw [(boundedList_eq_some_iff n (ys.map indexValue) ys).mpr rfl]
  change (if hz : ys.length = n then some (⟨ys, hz⟩ : Table n) else none) = some ⟨ys, hlen⟩
  rw [dif_pos hlen]

theorem decodeTable_eq_some_iff {n : Nat} (v : Value) (t : Table n) :
    decodeTable n v = some t ↔ v = tableValue t := by
  constructor
  · intro h
    exact (decodeTable_sound v t h).symm
  · intro h
    rw [h]
    exact decodeTable_complete t

structure Certificate (n : Nat) where
  forward : Table n
  backward : Table n

def decodeCertificate (n : Nat) (forward backward : Value) : Option (Certificate n) := do
  let f ← decodeTable n forward
  let b ← decodeTable n backward
  some ⟨f, b⟩

theorem decodeCertificate_sound {n : Nat} (forward backward : Value)
    (c : Certificate n) (h : decodeCertificate n forward backward = some c) :
    tableValue c.forward = forward ∧ tableValue c.backward = backward := by
  change (decodeTable n forward >>= fun f =>
    decodeTable n backward >>= fun b => some (Certificate.mk f b)) = some c at h
  obtain ⟨f, hf, htail⟩ := Option.bind_eq_some_iff.mp h
  obtain ⟨b, hb, he⟩ := Option.bind_eq_some_iff.mp htail
  have hc : Certificate.mk f b = c := Option.some.inj he
  cases hc
  exact ⟨decodeTable_sound forward f hf, decodeTable_sound backward b hb⟩

/-- Scalar finite-index equations; there is no permutation or function-equality input. -/
def RoundTrips {n : Nat} (c : Certificate n) : Prop :=
  ∀ i : Fin n,
    tableAt c.backward (tableAt c.forward i) = i ∧
    tableAt c.forward (tableAt c.backward i) = i

instance {n : Nat} (c : Certificate n) : Decidable (RoundTrips c) := by
  unfold RoundTrips
  infer_instance

def check {n : Nat} (c : Certificate n) : Bool := decide (RoundTrips c)

theorem check_iff {n : Nat} (c : Certificate n) : check c = true ↔ RoundTrips c := by
  simp only [check, decide_eq_true_eq]

/-- The inverse is the supplied checked table, not a choice-based inverse. -/
def checkedEquiv {n : Nat} (c : Certificate n) (h : check c = true) : Equiv.Perm (Fin n) where
  toFun := tableAt c.forward
  invFun := tableAt c.backward
  left_inv i := ((check_iff c).mp h i).1
  right_inv i := ((check_iff c).mp h i).2

/-- Strict parsed arrays plus successful round trips construct the permutation. -/
def decodePermutation (n : Nat) (forward backward : Value) : Option (Equiv.Perm (Fin n)) := do
  let c ← decodeCertificate n forward backward
  if h : check c = true then some (checkedEquiv c h) else none

/-- Successful decoding proves the actual forward/inverse lookup behavior and
exact ordered source arrays. Nothing assumes either table was a permutation. -/
theorem decodePermutation_sound {n : Nat} (forward backward : Value)
    (p : Equiv.Perm (Fin n)) (h : decodePermutation n forward backward = some p) :
    ∃ c : Certificate n,
      decodeCertificate n forward backward = some c ∧ check c = true ∧
      tableValue c.forward = forward ∧ tableValue c.backward = backward ∧
      (∀ i, p i = tableAt c.forward i) ∧
      (∀ i, p.symm i = tableAt c.backward i) := by
  change (decodeCertificate n forward backward >>= fun c =>
    if hc : check c = true then some (checkedEquiv c hc) else none) = some p at h
  obtain ⟨c, hc, hp⟩ := Option.bind_eq_some_iff.mp h
  split at hp
  · rename_i hcheck
    have he : checkedEquiv c hcheck = p := Option.some.inj hp
    cases he
    have hs := decodeCertificate_sound forward backward c hc
    exact ⟨c, hc, hcheck, hs.1, hs.2, (fun _ => rfl), (fun _ => rfl)⟩
  · cases hp

/-- Actual parser output feeds the accepted scalar chart checker. -/
def decodeChart (n : Nat) (forward backward : Value) (columns : Fin n → Nat)
    (updateVector coefficients : CheckedBinaryChart.Address n) :
    Option (CheckedBinaryChart.Candidate n) :=
  (decodePermutation n forward backward).map fun p =>
    { columns := columns, permutation := p,
      updateVector := updateVector, coefficients := coefficients }

/-- The joined source boundary retains raw ordered tables and derives operator
identity using the independent finite scalar check, with no supplied Equiv. -/
theorem decoded_chart_sound {n : Nat} (forward backward : Value) (columns : Fin n → Nat)
    (updateVector coefficients : CheckedBinaryChart.Address n)
    (c : CheckedBinaryChart.Candidate n)
    (hdecode : decodeChart n forward backward columns updateVector coefficients = some c)
    (hcheck : CheckedBinaryChart.check c = true) :
    (∃ t : Certificate n,
      decodeCertificate n forward backward = some t ∧ check t = true ∧
      tableValue t.forward = forward ∧ tableValue t.backward = backward ∧
      (∀ i, c.permutation i = tableAt t.forward i) ∧
      (∀ i, c.permutation.symm i = tableAt t.backward i)) ∧
    c.columns = columns ∧ c.updateVector = updateVector ∧ c.coefficients = coefficients ∧
    CheckedBinaryChart.sourceLinear c = (CheckedBinaryChart.checkedEquiv c hcheck).toLinearMap ∧
    (∀ x, CheckedBinaryChart.inverseAddress c (CheckedBinaryChart.sourceLinear c x) = x) ∧
    (∀ x, CheckedBinaryChart.sourceLinear c (CheckedBinaryChart.inverseAddress c x) = x) := by
  unfold decodeChart at hdecode
  obtain ⟨p, hp, he⟩ := Option.map_eq_some_iff.mp hdecode
  cases he
  exact ⟨decodePermutation_sound forward backward p hp, rfl, rfl, rfl,
    CheckedBinaryChart.sourceLinear_eq_checked _ hcheck,
    CheckedBinaryChart.inverse_source _ hcheck,
    CheckedBinaryChart.source_inverse _ hcheck⟩

end CurrentMain.CheckedPermutationTables
#print axioms CurrentMain.CheckedPermutationTables.decodeTable_sound
#print axioms CurrentMain.CheckedPermutationTables.decodeTable_complete
#print axioms CurrentMain.CheckedPermutationTables.decodeTable_eq_some_iff
#print axioms CurrentMain.CheckedPermutationTables.decodeCertificate_sound
#print axioms CurrentMain.CheckedPermutationTables.check_iff
#print axioms CurrentMain.CheckedPermutationTables.decodePermutation_sound
#print axioms CurrentMain.CheckedPermutationTables.decoded_chart_sound
#check @CurrentMain.CheckedPermutationTables.decoded_chart_sound
