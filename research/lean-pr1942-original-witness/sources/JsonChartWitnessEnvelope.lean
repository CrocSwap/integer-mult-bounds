import JsonPackedColumnDictionary

/-!
Strict actual-format selection of a PR1942 chart witness. The executable wrapper
checks the format tag, a canonical bounded integer dimension, and the entries
object; it selects the same key as the source dictionary and invokes unchanged
certifyEntry at depth3 on that original five-array value. Missing/malformed
fields reject. Neither certificate arrays nor source columns are manufactured.

The upstream witness producer/auditor is Adam Gall with OpenAI assistance,
PR1942 at c7d8c9febf0fcc52d2002db657165cd206ff9cec. Its Python finite checks are
source context, not Lean assumptions or a selected execution result. This is an
AST interface: original-byte parsing, duplicate-key policy, whole-key coverage,
digest authentication and selected-instance success remain separate. Logical
binary operators/inverses do not supply complex phases or physical costs.
Author-checked context kappa=836330098538459/500000000000000000
=0.001672660197076918; generic statements do not use or change kappa.
Credits: Lean/Mathlib; bank/frame strict index/JSON/chart interfaces; Rohan Arun
PR1094 and Jeremy Kothe T16/PR514. James Chang with OpenAI assistance. Apache-2.0.
-/
set_option Elab.async false
set_option autoImplicit false
namespace CurrentMain.JsonChartWitnessEnvelope
open JsonPackedColumnDictionary (CheckedEntry certifyEntry columnOperator)
open ParsedBinaryChartCertificate (vectorValue)

/-- Exact upstream envelope identifier; dictionary ordering is irrelevant. -/
def formatTag : String := "pr1879-five-array-chart-witnesses-v1"

def certificateFor (n : Nat) (witnesses : Lean.Json) (key : String) : Option Lean.Json := do
  let rawTag ← (witnesses.getObjVal? "format").toOption
  let tag ← rawTag.getStr?.toOption
  if tag = formatTag then
    let rawDimension ← (witnesses.getObjVal? "dimension").toOption
    let dimension ← StrictJsonValueBridge.index (n + 1) rawDimension
    if dimension.val = n then
      let entries ← (witnesses.getObjVal? "entries").toOption
      (entries.getObjVal? key).toOption
    else none
  else none

private theorem toOption_sound {ε α : Type} (value : Except ε α) (a : α)
    (h : value.toOption = some a) : value = .ok a := by
  cases value with
  | error error => cases h
  | ok found => exact congrArg Except.ok (Option.some.inj h)

private theorem getStr_sound (raw : Lean.Json) (tag : String)
    (h : raw.getStr?.toOption = some tag) : raw = .str tag := by
  cases raw <;> simp_all [Lean.Json.getStr?, Except.toOption, Pure.pure, Except.pure]

/-- Selection preserves the actual format, dimension, entries AST and original
named five-array value; no object insertion order or global coverage is inferred. -/
theorem certificateFor_sound (n : Nat) (witnesses : Lean.Json) (key : String)
    (certificateJson : Lean.Json) (h : certificateFor n witnesses key = some certificateJson) :
    ∃ entries : Lean.Json,
      witnesses.getObjVal? "format" = .ok (.str formatTag) ∧
      witnesses.getObjVal? "dimension" = .ok (.num ⟨(n : Int), 0⟩) ∧
      witnesses.getObjVal? "entries" = .ok entries ∧
      entries.getObjVal? key = .ok certificateJson := by
  unfold certificateFor at h
  obtain ⟨rawTag, htag, h⟩ := Option.bind_eq_some_iff.mp h
  obtain ⟨tag, ht, h⟩ := Option.bind_eq_some_iff.mp h
  split at h
  · rename_i hformat
    subst tag
    obtain ⟨rawDimension, hdim, h⟩ := Option.bind_eq_some_iff.mp h
    obtain ⟨dimension, hi, h⟩ := Option.bind_eq_some_iff.mp h
    split at h
    · rename_i hn
      obtain ⟨entries, he, hc⟩ := Option.bind_eq_some_iff.mp h
      have ht' := getStr_sound rawTag formatTag ht
      have hd : rawDimension = .num ⟨(n : Int), 0⟩ := by
        simpa only [StrictJsonValueBridge.indexJson, hn] using
          (StrictJsonValueBridge.index_eq_some_iff (n + 1) rawDimension dimension).mp hi
      exact ⟨entries, ht' ▸ toOption_sound _ _ htag,
        hd ▸ toOption_sound _ _ hdim, toOption_sound _ _ he, toOption_sound _ _ hc⟩
    · cases h
  · cases h

theorem certificateFor_complete (n : Nat) (witnesses entries certificateJson : Lean.Json)
    (key : String)
    (hf : witnesses.getObjVal? "format" = .ok (.str formatTag))
    (hd : witnesses.getObjVal? "dimension" = .ok (.num ⟨(n : Int), 0⟩))
    (he : witnesses.getObjVal? "entries" = .ok entries)
    (hc : entries.getObjVal? key = .ok certificateJson) :
    certificateFor n witnesses key = some certificateJson := by
  let i : Fin (n + 1) := ⟨n, Nat.lt_succ_self n⟩
  have hi : StrictJsonValueBridge.index (n + 1) (.num ⟨(n : Int), 0⟩) = some i :=
    (StrictJsonValueBridge.index_eq_some_iff _ _ i).mpr rfl
  simp only [certificateFor, hf, hd, he, hc, Except.toOption, Lean.Json.getStr?,
    Option.bind_some, if_pos rfl, hi, i, Bind.bind, Pure.pure, Option.bind, Except.pure, if_true]

/-- Both the source and certificate are selected under the same original key. -/
def certify (n : Nat) (dictionary witnesses : Lean.Json) (key : String) :
    Option (CheckedEntry n) := do
  let certificateJson ← certificateFor n witnesses key
  certifyEntry 3 n dictionary key certificateJson

/-- Actual wrapper success derives field correspondence and the already proved
all-address binary operator/inverse laws. No selected-success premise is inserted. -/
theorem certify_sound {n : Nat} (dictionary witnesses : Lean.Json) (key : String)
    (r : CheckedEntry n) (h : certify n dictionary witnesses key = some r) :
    ∃ entries certificateJson : Lean.Json,
      witnesses.getObjVal? "format" = .ok (.str formatTag) ∧
      witnesses.getObjVal? "dimension" = .ok (.num ⟨(n : Int), 0⟩) ∧
      witnesses.getObjVal? "entries" = .ok entries ∧
      entries.getObjVal? key = .ok certificateJson ∧
      certifyEntry 3 n dictionary key certificateJson = some r ∧
      (∃ raw, dictionary.getObjVal? key = .ok raw ∧
        StrictJsonValueBridge.reencode 2 (vectorValue r.columns) = raw) ∧
      (∃ w : ParsedBinaryChartCertificate.Witness n,
        StrictJsonValueBridge.reencode 3 (ParsedBinaryChartCertificate.witnessValue w) =
          certificateJson ∧ ParsedBinaryChartCertificate.Binds r.certificate.val w) ∧
      columnOperator r.columns =
        (CheckedBinaryChart.checkedEquiv r.certificate.val r.certificate.property).toLinearMap ∧
      (∀ x, CheckedBinaryChart.inverseAddress r.certificate.val (columnOperator r.columns x) = x) ∧
      (∀ x, columnOperator r.columns (CheckedBinaryChart.inverseAddress r.certificate.val x) = x) := by
  obtain ⟨certificateJson, hc, hr⟩ := Option.bind_eq_some_iff.mp h
  obtain ⟨entries, hf, hd, he, hk⟩ := certificateFor_sound n witnesses key certificateJson hc
  exact ⟨entries, certificateJson, hf, hd, he, hk, hr,
    JsonPackedColumnDictionary.certifyEntry_sound 3 dictionary key certificateJson r hr⟩

/-- Completeness retains the explicit downstream selected-certificate execution;
this wrapper proves only the additional actual envelope selection. -/
theorem certify_complete {n : Nat} (dictionary witnesses entries certificateJson : Lean.Json)
    (key : String) (r : CheckedEntry n)
    (hf : witnesses.getObjVal? "format" = .ok (.str formatTag))
    (hd : witnesses.getObjVal? "dimension" = .ok (.num ⟨(n : Int), 0⟩))
    (he : witnesses.getObjVal? "entries" = .ok entries)
    (hc : entries.getObjVal? key = .ok certificateJson)
    (hr : certifyEntry 3 n dictionary key certificateJson = some r) :
    certify n dictionary witnesses key = some r := by
  have hs := certificateFor_complete n witnesses entries certificateJson key hf hd he hc
  simp only [certify, hs, Option.bind_some, hr, Bind.bind, Option.bind]

end CurrentMain.JsonChartWitnessEnvelope
#print axioms CurrentMain.JsonChartWitnessEnvelope.certificateFor_sound
#print axioms CurrentMain.JsonChartWitnessEnvelope.certificateFor_complete
#print axioms CurrentMain.JsonChartWitnessEnvelope.certify_sound
#print axioms CurrentMain.JsonChartWitnessEnvelope.certify_complete
#check @CurrentMain.JsonChartWitnessEnvelope.certify_sound
#check @CurrentMain.JsonChartWitnessEnvelope.certify_complete
