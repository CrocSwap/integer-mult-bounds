import CurrentPR589BCheck
import BitXorTargetTranslation

/-! Exact current PR589 B scalar interpretation on all661 original registers.
The middle499 gates write sources and three helpers. Preservation therefore
excludes helpers465,466,468. Ordered decoding retains all712 gates/934 operands.
Arbitrary initial target perturbations pass through unchanged; erased targets
are a comparison state rather than a clean-input premise. Frame realization,
A/C/D and the Fin662 temporary-copy lifecycle remain separate.
Prepared with OpenAI assistance; original package attribution retained. -/
namespace CurrentMain.CurrentPR589PhaseBXor
open CurrentPR589B
set_option Elab.async false
attribute [local irreducible] CurrentPR589B.Data.phaseB

abbrev Register := Fin 661
abbrev State := BitXor.State Register
abbrev RawGate := Nat × Nat × List Nat

def IsTarget (r : Register) : Prop := 111 ≤ r.val ∧ r.val < 222
instance (r : Register) : Decidable (IsTarget r) := inferInstanceAs (Decidable (111 ≤ r.val ∧ r.val < 222))

private theorem raw_domains (g : RawGate) (hg : g ∈ Data.phaseB) :
    g.1 < 636 ∧ g.2.1 < 661 ∧ ∀ r ∈ g.2.2, r < 661 := by
  have h := Bool.and_eq_true_iff.mp ((List.all_eq_true.mp phase_domains) g hg)
  have hfd := of_decide_eq_true h.1
  refine ⟨hfd.1, hfd.2, ?_⟩
  intro r hr
  exact of_decide_eq_true ((List.all_eq_true.mp h.2) r hr)

def decodeGate (g : RawGate) (hg : g ∈ Data.phaseB) : BitXor.Gate Register where
  frame := g.1
  dst := ⟨g.2.1, (raw_domains g hg).2.1⟩
  sources := g.2.2.attach.map (fun r => ⟨r.val, (raw_domains g hg).2.2 r.val r.property⟩)

def decodedPhaseB : List (BitXor.Gate Register) :=
  Data.phaseB.attach.map (fun g => decodeGate g.val g.property)

def encodeGate (g : BitXor.Gate Register) : RawGate :=
  (g.frame, g.dst.val, g.sources.map Fin.val)

theorem decode_roundtrip (g : RawGate) (hg : g ∈ Data.phaseB) :
    encodeGate (decodeGate g hg) = g := by
  rcases g with ⟨f, d, rs⟩
  simp only [encodeGate, decodeGate, List.map_map, Function.comp_def]
  rw [List.attach_map_subtype_val]

theorem ordered_word_binding : decodedPhaseB.map encodeGate = Data.phaseB := by
  unfold decodedPhaseB
  rw [List.map_map]
  simp only [Function.comp_def, decode_roundtrip]
  exact List.attach_map_subtype_val _

private theorem raw_write_region (g : RawGate) (hg : g ∈ Data.phaseB) :
    g.2.1 < 222 ∨ g.2.1 = 465 ∨ g.2.1 = 466 ∨ g.2.1 = 468 := by
  exact of_decide_eq_true ((List.all_eq_true.mp write_region) g hg)

theorem decoded_gate_properties (g : BitXor.Gate Register) (hg : g ∈ decodedPhaseB) :
    (g.dst.val < 222 ∨ g.dst.val = 465 ∨ g.dst.val = 466 ∨ g.dst.val = 468) ∧
      ∀ r ∈ g.sources, ¬ IsTarget r := by
  obtain ⟨raw, hraw, heq⟩ := List.mem_map.mp hg
  subst g
  constructor
  · change raw.val.2.1 < 222 ∨ raw.val.2.1 = 465 ∨
        raw.val.2.1 = 466 ∨ raw.val.2.1 = 468
    exact raw_write_region raw.val raw.property
  · intro r hr
    simp only [decodeGate] at hr
    obtain ⟨source, hsource, heq⟩ := List.mem_map.mp hr
    subst r
    change ¬ (111 ≤ source.val ∧ source.val < 222)
    have h := of_decide_eq_true ((List.all_eq_true.mp
      ((List.all_eq_true.mp no_target_operands) raw.val raw.property)) source.val source.property)
    rcases h with hlt | hge
    · exact fun ht => (Nat.not_le_of_lt hlt) ht.1
    · exact fun ht => (Nat.not_le_of_lt ht.2) hge

/-- Execute exactly the ordered B tuple list in the raw Boolean scalar model. -/
def executeB (s : State) : State := BitXor.run decodedPhaseB s

/-- Helpers outside the three actual helper destinations are unchanged.
No source-register or all-helper preservation is claimed. -/
theorem helpers_preserved_except (s : State) (r : Register) (hr : 222 ≤ r.val)
    (h465 : r.val ≠ 465) (h466 : r.val ≠ 466) (h468 : r.val ≠ 468) :
    executeB s r = s r := by
  apply BitXor.run_off_target
    (fun q : Register => q.val < 222 ∨ q.val = 465 ∨ q.val = 466 ∨ q.val = 468)
    decodedPhaseB (fun g hg => (decoded_gate_properties g hg).1) s r
  intro h
  rcases h with hlt | heq | heq | heq
  · exact (Nat.not_lt_of_ge hr) hlt
  · exact h465 heq
  · exact h466 heq
  · exact h468 heq

/-- The full initial-target perturbation passes unchanged through the actual XOR word. -/
theorem target_translation (s delta : State) :
    executeB (BitXor.shift IsTarget s delta) =
      BitXor.shift IsTarget (executeB s) delta :=
  BitXor.run_shift IsTarget decodedPhaseB
    (fun g hg => (decoded_gate_properties g hg).2) s delta

/-- Each target is its original bit XOR a contribution independent of initial targets. -/
theorem target_identity (s : State) (r : Register) (hr : IsTarget r) :
    executeB s r = (s r ^^ executeB (BitXor.eraseTargets IsTarget s) r) :=
  BitXor.target_identity IsTarget decodedPhaseB
    (fun g hg => (decoded_gate_properties g hg).2) s r hr

theorem contribution_independent_of_targets (s t : State)
    (h : ∀ r, ¬ IsTarget r → s r = t r) :
    executeB (BitXor.eraseTargets IsTarget s) =
      executeB (BitXor.eraseTargets IsTarget t) := by
  rw [BitXor.erased_eq_of_agree_off_target IsTarget s t h]

end CurrentMain.CurrentPR589PhaseBXor
#print axioms CurrentMain.CurrentPR589PhaseBXor.decode_roundtrip
#print axioms CurrentMain.CurrentPR589PhaseBXor.ordered_word_binding
#print axioms CurrentMain.CurrentPR589PhaseBXor.decoded_gate_properties
#print axioms CurrentMain.CurrentPR589PhaseBXor.helpers_preserved_except
#print axioms CurrentMain.CurrentPR589PhaseBXor.target_translation
#print axioms CurrentMain.CurrentPR589PhaseBXor.target_identity
#print axioms CurrentMain.CurrentPR589PhaseBXor.contribution_independent_of_targets
