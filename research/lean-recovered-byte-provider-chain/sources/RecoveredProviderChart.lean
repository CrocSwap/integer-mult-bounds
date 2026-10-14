import JsonBinaryChartInterpreter

/-!
Recover a certificate for the restricted provider class: one involutive
rank-one binary update after a coordinate permutation. Inputs are only packed
columns, the update vector and the linear-form coefficients. Finite searches
recover the forward axes and inverse table. Actual round-trip and scalar checks
then construct the accepted certificate; no inverse table, permutation proof or
operator equality is an executable input.

Completeness is proved for that precise factorization class, not all invertible
binary matrices. This matches the source form of the T16 idle_basis construction
and its ordered column permutation. Instantiating its port/pivot/order conditions
and external artifact correspondence remains separate; no selected census runs.
The result provides a canonical auxiliary JSON certificate, not a claim that
the provider emitted that new grammar. Bytes, digest keys, complex phases,
affine shifts, physical chart direction, executor, precision and cost stay open.
Author-checked context: kappa=836330098538459/500000000000000000.
The generic theorem is independent of this number. Credits: Jeremy Kothe's
PR514/T16 emitter and PR484/507 lineage; Rohan Arun PR1094; accepted bank/frame
strict permutation/chart/JSON components; Lean/Mathlib. James Chang with OpenAI
assistance. Apache-2.0. UNCOMPILED source preparation.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.RecoveredProviderChart
open CheckedBinaryChart (Address Candidate bits)
open CheckedPermutationTables (Table tableAt)
open BinaryChartCanonicalEncoding (tableOfFunction tableAt_ofFunction)

structure Input (n : Nat) where
  columns : Fin n → Nat
  updateVector : Address n
  coefficients : Address n

def candidate {n : Nat} (d : Input n) (p : Equiv.Perm (Fin n)) : Candidate n :=
  ⟨d.columns, p, d.updateVector, d.coefficients⟩

def inputOf {n : Nat} (c : Candidate n) : Input n :=
  ⟨c.columns, c.updateVector, c.coefficients⟩

def axes (n : Nat) : List (Fin n) := List.ofFn id

private theorem mem_axes {n : Nat} (i : Fin n) : i ∈ axes n :=
  List.mem_ofFn.mpr ⟨i, rfl⟩

private theorem find_unique {α : Type} (xs : List α) (p : α → Bool) (a : α)
    (hm : a ∈ xs) (ha : p a = true) (hu : ∀ b, p b = true → b = a) :
    xs.find? p = some a := by
  cases h : xs.find? p with
  | none => exact False.elim (((List.find?_eq_none.mp h) a hm) ha)
  | some b => exact congrArg some (hu b (List.find?_some h))

private theorem mapM_exact {α β : Type} (xs : List α) (f : α → Option β)
    (g : α → β) (h : ∀ a, f a = some (g a)) : xs.mapM f = some (xs.map g) := by
  induction xs with
  | nil => rfl
  | cons a xs ih =>
      rw [List.mapM_cons, h a, ih, List.map_cons]
      all_goals rfl

/-- Exact-length traversal; missing axes fail rather than default to zero. -/
def recoverTable {n : Nat} (f : Fin n → Option (Fin n)) : Option (Table n) := do
  let xs ← (axes n).mapM f
  if h : xs.length = n then some ⟨xs, h⟩ else none

private theorem recoverTable_complete {n : Nat} (f : Fin n → Option (Fin n))
    (g : Fin n → Fin n) (h : ∀ i, f i = some (g i)) :
    recoverTable f = some (tableOfFunction g) := by
  unfold recoverTable
  rw [mapM_exact _ f g h]
  simp only [axes, List.map_ofFn, Function.comp_def, id_eq]
  change (if hlen : (List.ofFn g).length = n then
    some (⟨List.ofFn g, hlen⟩ : Table n) else none) = some (tableOfFunction g)
  rw [dif_pos List.length_ofFn]
  all_goals rfl

/-- The backward table is searched from the actual forward table. -/
def inverseLookup {n : Nat} (forward : Table n) (i : Fin n) : Option (Fin n) :=
  (axes n).find? (fun j => decide (tableAt forward j = i))

private theorem inverseLookup_complete {n : Nat} (p : Equiv.Perm (Fin n)) (i : Fin n) :
    inverseLookup (tableOfFunction p) i = some (p.symm i) := by
  apply find_unique _ _ _ (mem_axes _)
  · simp only [tableAt_ofFunction, Equiv.apply_symm_apply, decide_true]
  · intro j hj
    have he : p j = i := by simpa only [tableAt_ofFunction, decide_eq_true_eq] using hj
    exact p.injective (he.trans (p.apply_symm_apply i).symm)

def recoverPermutation {n : Nat} (forward : Table n) : Option (Equiv.Perm (Fin n)) := do
  let backward ← recoverTable (inverseLookup forward)
  let cert : CheckedPermutationTables.Certificate n := ⟨forward, backward⟩
  if h : CheckedPermutationTables.check cert = true then
    some (CheckedPermutationTables.checkedEquiv cert h) else none

private theorem recoverPermutation_complete {n : Nat} (p : Equiv.Perm (Fin n)) :
    recoverPermutation (tableOfFunction p) = some p := by
  unfold recoverPermutation
  rw [recoverTable_complete _ p.symm (inverseLookup_complete p)]
  change (if h : CheckedPermutationTables.check
    (BinaryChartCanonicalEncoding.permutationCertificate p) = true then
      some (CheckedPermutationTables.checkedEquiv
        (BinaryChartCanonicalEncoding.permutationCertificate p) h) else none) = some p
  rw [dif_pos (BinaryChartCanonicalEncoding.permutation_check p)]
  apply congrArg some
  apply Equiv.ext
  intro i
  exact tableAt_ofFunction p i

/-- Standard-axis image under the proposed rank-one factor. -/
def factor {n : Nat} (d : Input n) (i : Fin n) : Address n :=
  Pi.single i 1 + d.coefficients i • d.updateVector

/-- Every comparison is a finite scalar-coordinate equality. -/
def axisLookup {n : Nat} (d : Input n) (j : Fin n) : Option (Fin n) :=
  (axes n).find? (fun i => decide (bits (d.columns j) = factor d i))

private theorem factor_apply {n : Nat} (d : Input n) (i : Fin n) :
    factor d i = CheckedBinaryChart.transvection d.updateVector
      (CheckedBinaryChart.form (candidate d (Equiv.refl _))) (Pi.single i 1) := by
  change Pi.single i 1 + d.coefficients i • d.updateVector = Pi.single i 1 +
    CheckedBinaryChart.form (candidate d (Equiv.refl _)) (Pi.single i 1) • d.updateVector
  rw [CheckedBinaryChart.form, LinearMap.lsum_piSingle]
  simp only [LinearMap.smulRight_apply, LinearMap.id_apply, one_smul]
  all_goals rfl

private theorem single_axis_injective {n : Nat} :
    Function.Injective (fun i : Fin n => (Pi.single i 1 : Address n)) := by
  intro i j h
  by_contra hn
  have he := congrFun h i
  simp only [Pi.single_apply, if_pos rfl, if_neg hn] at he
  exact one_ne_zero he

private theorem factor_injective {n : Nat} (d : Input n)
    (h : CheckedBinaryChart.form (candidate d (Equiv.refl _)) d.updateVector = 0) :
    Function.Injective (factor d) := by
  intro i j he
  rw [factor_apply, factor_apply] at he
  exact single_axis_injective
    ((CheckedBinaryChart.transvection_involutive _ _ h).injective he)

private theorem axisLookup_complete {n : Nat} (c : Candidate n)
    (h : CheckedBinaryChart.check c = true) (j : Fin n) :
    axisLookup (inputOf c) j = some (c.permutation j) := by
  have hc := (CheckedBinaryChart.check_iff c).mp h
  have hf : Function.Injective (factor (inputOf c)) := factor_injective _ hc.2.1
  have he : bits (c.columns j) = factor (inputOf c) (c.permutation j) := by
    funext i
    exact hc.2.2 j i
  apply find_unique _ _ _ (mem_axes _)
  · exact (decide_eq_true_eq).mpr he
  · intro i hi
    have hi' : bits (c.columns j) = factor (inputOf c) i := of_decide_eq_true hi
    exact hf (hi'.symm.trans he)

/-- No permutation or inverse data is provided to this executable constructor. -/
def recover {n : Nat} (d : Input n) : Option (ParsedBinaryChartCertificate.Certified n) := do
  let forward ← recoverTable (axisLookup d)
  let p ← recoverPermutation forward
  let c := candidate d p
  if h : CheckedBinaryChart.check c = true then some ⟨c, h⟩ else none

/-- Completeness for the exact restricted class accepted by the old checker.
The candidate is a proof-side specification; execution receives only inputOf c. -/
theorem recover_complete {n : Nat} (c : Candidate n) (h : CheckedBinaryChart.check c = true) :
    recover (inputOf c) = some (⟨c, h⟩ : ParsedBinaryChartCertificate.Certified n) := by
  unfold recover
  rw [recoverTable_complete _ c.permutation (axisLookup_complete c h)]
  change (recoverPermutation (tableOfFunction c.permutation) >>= fun p =>
    if h' : CheckedBinaryChart.check (candidate (inputOf c) p) = true then
      some (⟨candidate (inputOf c) p, h'⟩ : ParsedBinaryChartCertificate.Certified n) else none) =
    some (⟨c, h⟩ : ParsedBinaryChartCertificate.Certified n)
  rw [recoverPermutation_complete c.permutation]
  change (if h' : CheckedBinaryChart.check c = true then
    some (⟨c, h'⟩ : ParsedBinaryChartCertificate.Certified n) else none) =
    some (⟨c, h⟩ : ParsedBinaryChartCertificate.Certified n)
  rw [dif_pos h]

/-- Explicit scalar/provider criterion, with no inverse-table assumption. -/
theorem recover_of_factorization {n : Nat} (d : Input n) (p : Equiv.Perm (Fin n))
    (hb : ∀ j, d.columns j < 2 ^ n)
    (hz : CheckedBinaryChart.form (candidate d p) d.updateVector = 0)
    (hc : ∀ j i, bits (d.columns j) i =
      (Pi.single (p j) 1 : Address n) i + d.coefficients (p j) * d.updateVector i) :
    ∃ r : ParsedBinaryChartCertificate.Certified n,
      recover d = some r ∧ r.val = candidate d p := by
  have h : CheckedBinaryChart.check (candidate d p) = true :=
    (CheckedBinaryChart.check_iff _).mpr ⟨hb, hz, hc⟩
  exact ⟨⟨candidate d p, h⟩, recover_complete (candidate d p) h, rfl⟩

/-- Success retains the actual input columns and produces a certificate that the
accepted actual-JSON interpreter accepts, with full operator/inverse laws. -/
theorem recover_sound {n : Nat} (d : Input n)
    (r : ParsedBinaryChartCertificate.Certified n) (h : recover d = some r) :
    r.val.columns = d.columns ∧ r.val.updateVector = d.updateVector ∧
    r.val.coefficients = d.coefficients ∧
    JsonBinaryChartInterpreter.certify 3 n
      (JsonBinaryChartInterpreter.canonicalJson r.val r.property) = some r ∧
    CheckedBinaryChart.sourceLinear r.val =
      (CheckedBinaryChart.checkedEquiv r.val r.property).toLinearMap ∧
    (∀ x, CheckedBinaryChart.inverseAddress r.val (CheckedBinaryChart.sourceLinear r.val x) = x) ∧
    (∀ x, CheckedBinaryChart.sourceLinear r.val (CheckedBinaryChart.inverseAddress r.val x) = x) := by
  unfold recover at h
  obtain ⟨forward, _, ht⟩ := Option.bind_eq_some_iff.mp h
  obtain ⟨p, _, hr⟩ := Option.bind_eq_some_iff.mp ht
  change (if hcheck : CheckedBinaryChart.check (candidate d p) = true then
    some (⟨candidate d p, hcheck⟩ : ParsedBinaryChartCertificate.Certified n) else none) = some r at hr
  split at hr
  · rename_i hcheck
    have he : (⟨candidate d p, hcheck⟩ : ParsedBinaryChartCertificate.Certified n) = r :=
      Option.some.inj hr
    cases he
    exact ⟨rfl, rfl, rfl, JsonBinaryChartInterpreter.certify_canonical (candidate d p) hcheck,
      CheckedBinaryChart.sourceLinear_eq_checked (candidate d p) hcheck,
      CheckedBinaryChart.inverse_source (candidate d p) hcheck,
      CheckedBinaryChart.source_inverse (candidate d p) hcheck⟩
  · cases hr

end CurrentMain.RecoveredProviderChart
#print axioms CurrentMain.RecoveredProviderChart.recover_complete
#print axioms CurrentMain.RecoveredProviderChart.recover_of_factorization
#print axioms CurrentMain.RecoveredProviderChart.recover_sound
#check @CurrentMain.RecoveredProviderChart.recover_of_factorization
#check @CurrentMain.RecoveredProviderChart.recover_sound
