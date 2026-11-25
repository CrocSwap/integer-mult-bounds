import CheckedPermutationTables

/-!
UNCOMPILED reusable strict parsed binary-chart certificate interpretation.
The proposed certificate grammar is exactly five arrays, in order: forward
indices, inverse indices, serialized columns, update bits, coefficient bits.
This is an explicit new certificate format, not a claim about any historical
supplier JSON layout. Every array has length n. Indices are below n, columns
below 2^n, and bits below 2. The existing strict integer decoder is reused.

Successful decoding preserves the complete parsed value and constructs all
Candidate fields. The accepted round-trip checker constructs the permutation;
the accepted scalar chart check constructs the equivalence. Their joined
soundness derives the serialized linear operator and both inverse identities.
No typed coefficient/vector/permutation or operator-equality supplier remains
in the top-level parsed check. No concrete certificate is checked here.

The earlier byte-to-Value parser, actual artifact selection, physical chart
convention, affine shifts, complex phase, recipes, execution, rounding and cost
remain separate. Author-checked context only:
kappa=836330098538459/500000000000000000=0.001672660197076918.
No generic statement depends on this number or proves multiplication.
Credits: accepted StrictParsedIndexCodec, CheckedPermutationTables and
CheckedBinaryChart, Lean List/Option/Fin, Mathlib ZMod/linear infrastructure.
Motivating emitter lineage: PR1094/Rohan Arun, Jeremy Kothe, icekylinx and
DreamingOfClouds. Apache-2.0; OpenAI assistance.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.ParsedBinaryChartCertificate
open SelectedSourceSyntax (Value bounded)
open StrictParsedIndexCodec (indexValue boundedList_eq_some_iff)

/-- Length and entry bound are independent parameters. -/
abbrev BoundedVector (length bound : Nat) :=
  { xs : List (Fin bound) // xs.length = length }

def vectorAt {n b : Nat} (v : BoundedVector n b) (i : Fin n) : Fin b :=
  v.val.get (Fin.cast v.property.symm i)

def vectorValue {n b : Nat} (v : BoundedVector n b) : Value :=
  .array (v.val.map indexValue)

def decodeVector (n b : Nat) : Value → Option (BoundedVector n b)
  | .array xs => do
      let ys ← xs.mapM (bounded b)
      if h : ys.length = n then some ⟨ys, h⟩ else none
  | _ => none

/-- Strict exact ordered preservation, for arbitrary length and entry bound. -/
theorem decodeVector_sound {n b : Nat} (raw : Value) (v : BoundedVector n b)
    (h : decodeVector n b raw = some v) : vectorValue v = raw := by
  cases raw with
  | text s => cases h
  | integer z => cases h
  | boolean bit => cases h
  | other => cases h
  | array xs =>
      change (xs.mapM (bounded b) >>= fun ys =>
        if hlen : ys.length = n then some (⟨ys, hlen⟩ : BoundedVector n b) else none) = some v at h
      obtain ⟨ys, hys, hv⟩ := Option.bind_eq_some_iff.mp h
      split at hv
      · rename_i hlen
        have he : (⟨ys, hlen⟩ : BoundedVector n b) = v := Option.some.inj hv
        cases he
        exact congrArg Value.array ((boundedList_eq_some_iff b xs ys).mp hys).symm
      · cases hv

theorem decodeVector_complete {n b : Nat} (v : BoundedVector n b) :
    decodeVector n b (vectorValue v) = some v := by
  rcases v with ⟨ys, hlen⟩
  change ((ys.map indexValue).mapM (bounded b) >>= fun zs =>
    if hz : zs.length = n then some (⟨zs, hz⟩ : BoundedVector n b) else none) = some ⟨ys, hlen⟩
  rw [(boundedList_eq_some_iff b (ys.map indexValue) ys).mpr rfl]
  change (if hz : ys.length = n then some (⟨ys, hz⟩ : BoundedVector n b) else none) = some ⟨ys, hlen⟩
  rw [dif_pos hlen]

/-- Integer/Boolean distinction, bounds, length, order and multiplicity are exact. -/
theorem decodeVector_eq_some_iff {n b : Nat} (raw : Value) (v : BoundedVector n b) :
    decodeVector n b raw = some v ↔ raw = vectorValue v := by
  constructor
  · intro h
    exact (decodeVector_sound raw v h).symm
  · intro h
    rw [h]
    exact decodeVector_complete v

structure RawFields where
  forward : Value
  backward : Value
  columns : Value
  update : Value
  coefficients : Value

def fieldsValue (r : RawFields) : Value :=
  .array [r.forward, r.backward, r.columns, r.update, r.coefficients]

def decodeShape : Value → Option RawFields
  | .array [f, b, c, u, a] => some ⟨f, b, c, u, a⟩
  | _ => none

theorem decodeShape_sound (raw : Value) (r : RawFields)
    (h : decodeShape raw = some r) : fieldsValue r = raw := by
  unfold decodeShape at h
  split at h
  · rename_i f b c u a
    have he : RawFields.mk f b c u a = r := Option.some.inj h
    cases he
    rfl
  · cases h

def columnFunction {n : Nat} (v : BoundedVector n (2 ^ n)) : Fin n → Nat :=
  fun i => (vectorAt v i).val

def binaryFunction {n : Nat} (v : BoundedVector n 2) : CheckedBinaryChart.Address n :=
  fun i => ((vectorAt v i).val : ZMod 2)

/-- All finite fields retained after decoding; permutation soundness is checked,
not stored as an assumed proof in this data structure. -/
structure Witness (n : Nat) where
  permutation : CheckedPermutationTables.Certificate n
  columns : BoundedVector n (2 ^ n)
  update : BoundedVector n 2
  coefficients : BoundedVector n 2

def witnessValue {n : Nat} (w : Witness n) : Value :=
  .array [CheckedPermutationTables.tableValue w.permutation.forward,
    CheckedPermutationTables.tableValue w.permutation.backward,
    vectorValue w.columns, vectorValue w.update, vectorValue w.coefficients]

/-- Exact data interpretation, with actual checked forward/inverse table lookup. -/
def Binds {n : Nat} (c : CheckedBinaryChart.Candidate n) (w : Witness n) : Prop :=
  CheckedPermutationTables.check w.permutation = true ∧
  (∀ i, c.permutation i = CheckedPermutationTables.tableAt w.permutation.forward i) ∧
  (∀ i, c.permutation.symm i = CheckedPermutationTables.tableAt w.permutation.backward i) ∧
  c.columns = columnFunction w.columns ∧
  c.updateVector = binaryFunction w.update ∧
  c.coefficients = binaryFunction w.coefficients

def decodeFields (n : Nat) (r : RawFields) : Option (CheckedBinaryChart.Candidate n) := do
  let p ← CheckedPermutationTables.decodePermutation n r.forward r.backward
  let cols ← decodeVector n (2 ^ n) r.columns
  let upd ← decodeVector n 2 r.update
  let coeff ← decodeVector n 2 r.coefficients
  some (CheckedBinaryChart.Candidate.mk (columnFunction cols) p
    (binaryFunction upd) (binaryFunction coeff))

private theorem decodeFields_sound {n : Nat} (r : RawFields)
    (c : CheckedBinaryChart.Candidate n) (h : decodeFields n r = some c) :
    ∃ w : Witness n, witnessValue w = fieldsValue r ∧ Binds c w := by
  change (CheckedPermutationTables.decodePermutation n r.forward r.backward >>= fun p =>
    decodeVector n (2 ^ n) r.columns >>= fun cols =>
    decodeVector n 2 r.update >>= fun upd =>
    decodeVector n 2 r.coefficients >>= fun coeff =>
    some (CheckedBinaryChart.Candidate.mk (columnFunction cols) p
      (binaryFunction upd) (binaryFunction coeff))) = some c at h
  obtain ⟨p, hp, hcols⟩ := Option.bind_eq_some_iff.mp h
  obtain ⟨cols, hc, hupd⟩ := Option.bind_eq_some_iff.mp hcols
  obtain ⟨upd, hu, hcoeff⟩ := Option.bind_eq_some_iff.mp hupd
  obtain ⟨coeff, ha, he⟩ := Option.bind_eq_some_iff.mp hcoeff
  have hcandidate : CheckedBinaryChart.Candidate.mk (columnFunction cols) p
    (binaryFunction upd) (binaryFunction coeff) = c := Option.some.inj he
  cases hcandidate
  obtain ⟨t, _, ht, hf, hb, hforward, hbackward⟩ :=
    CheckedPermutationTables.decodePermutation_sound r.forward r.backward p hp
  refine ⟨⟨t, cols, upd, coeff⟩, ?_, ?_⟩
  · change Value.array [CheckedPermutationTables.tableValue t.forward,
      CheckedPermutationTables.tableValue t.backward, vectorValue cols,
      vectorValue upd, vectorValue coeff] =
      Value.array [r.forward, r.backward, r.columns, r.update, r.coefficients]
    rw [hf, hb, decodeVector_sound r.columns cols hc,
      decodeVector_sound r.update upd hu, decodeVector_sound r.coefficients coeff ha]
  · exact ⟨ht, hforward, hbackward, rfl, rfl, rfl⟩

def decode (n : Nat) (raw : Value) : Option (CheckedBinaryChart.Candidate n) := do
  let r ← decodeShape raw
  decodeFields n r

/-- Every accepted Candidate field comes from the complete strict parsed input. -/
theorem decode_sound {n : Nat} (raw : Value) (c : CheckedBinaryChart.Candidate n)
    (h : decode n raw = some c) :
    ∃ w : Witness n, witnessValue w = raw ∧ Binds c w := by
  change (decodeShape raw >>= fun r => decodeFields n r) = some c at h
  obtain ⟨r, hr, hc⟩ := Option.bind_eq_some_iff.mp h
  obtain ⟨w, hw, hbind⟩ := decodeFields_sound r c hc
  exact ⟨w, hw.trans (decodeShape_sound raw r hr), hbind⟩

abbrev Certified (n : Nat) :=
  { c : CheckedBinaryChart.Candidate n // CheckedBinaryChart.check c = true }

/-- The final scalar check is executed after all parsed fields are constructed. -/
def certify (n : Nat) (raw : Value) : Option (Certified n) := do
  let c ← decode n raw
  if h : CheckedBinaryChart.check c = true then some ⟨c, h⟩ else none

/-- A successful parsed certificate derives exact all-coordinate operator
identity and both inverse laws, retaining the full parsed-data witness. -/
theorem certify_sound {n : Nat} (raw : Value) (r : Certified n)
    (h : certify n raw = some r) :
    ∃ w : Witness n,
      witnessValue w = raw ∧ Binds r.val w ∧
      CheckedBinaryChart.sourceLinear r.val =
        (CheckedBinaryChart.checkedEquiv r.val r.property).toLinearMap ∧
      (∀ x, CheckedBinaryChart.inverseAddress r.val
        (CheckedBinaryChart.sourceLinear r.val x) = x) ∧
      (∀ x, CheckedBinaryChart.sourceLinear r.val
        (CheckedBinaryChart.inverseAddress r.val x) = x) := by
  change (decode n raw >>= fun c =>
    if hc : CheckedBinaryChart.check c = true then some (⟨c, hc⟩ : Certified n) else none) = some r at h
  obtain ⟨c, hc, hr⟩ := Option.bind_eq_some_iff.mp h
  split at hr
  · rename_i hcheck
    have he : (⟨c, hcheck⟩ : Certified n) = r := Option.some.inj hr
    cases he
    obtain ⟨w, hw, hbind⟩ := decode_sound raw c hc
    exact ⟨w, hw, hbind, CheckedBinaryChart.sourceLinear_eq_checked c hcheck,
      CheckedBinaryChart.inverse_source c hcheck, CheckedBinaryChart.source_inverse c hcheck⟩
  · cases hr

def checkParsed (n : Nat) (raw : Value) : Bool := (certify n raw).isSome

/-- The Boolean entry point returns a real accepted interpreter output. -/
theorem checkParsed_sound {n : Nat} (raw : Value) (h : checkParsed n raw = true) :
    ∃ r : Certified n, certify n raw = some r ∧
      ∃ w : Witness n, witnessValue w = raw ∧ Binds r.val w := by
  cases hr : certify n raw with
  | none => simp only [checkParsed, hr, Option.isSome_none, Bool.false_eq_true] at h
  | some r =>
      obtain ⟨w, hw, hbind, _⟩ := certify_sound raw r hr
      exact ⟨r, rfl, w, hw, hbind⟩

end CurrentMain.ParsedBinaryChartCertificate
#print axioms CurrentMain.ParsedBinaryChartCertificate.decodeVector_sound
#print axioms CurrentMain.ParsedBinaryChartCertificate.decodeVector_complete
#print axioms CurrentMain.ParsedBinaryChartCertificate.decodeVector_eq_some_iff
#print axioms CurrentMain.ParsedBinaryChartCertificate.decodeShape_sound
#print axioms CurrentMain.ParsedBinaryChartCertificate.decode_sound
#print axioms CurrentMain.ParsedBinaryChartCertificate.certify_sound
#print axioms CurrentMain.ParsedBinaryChartCertificate.checkParsed_sound
#check @CurrentMain.ParsedBinaryChartCertificate.certify_sound
