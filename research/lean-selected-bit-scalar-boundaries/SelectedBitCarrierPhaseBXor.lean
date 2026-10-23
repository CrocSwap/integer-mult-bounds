import SelectedBitCarrierPhaseBCheck
import BitXorTargetTranslation

/-! The exact selected B tuples are decoded into actual Fin729 references using
accepted domain proofs. No default-valued register read is introduced. Frame IDs
and all operand occurrences are retained by the roundtrip theorem. The scalar
interpreter intentionally ignores frame metadata; physical transport, phase-B
entrance-state realization and the retained-major temporary729 COPY lifecycle
are separate. The raw scatter table is not executed by this B-only theorem. -/
namespace CurrentMain.SelectedBitCarrierPhaseBXor
open SelectedBitCarrierPhaseB
set_option Elab.async false
attribute [local irreducible] SelectedBitCarrierPhaseB.Data.phaseB

abbrev Register := Fin 729
abbrev State := BitXor.State Register
abbrev RawGate := Nat × Nat × List Nat

def IsTarget (r : Register) : Prop := 120 ≤ r.val ∧ r.val < 240
instance (r : Register) : Decidable (IsTarget r) := inferInstanceAs (Decidable (120 ≤ r.val ∧ r.val < 240))

private theorem raw_domains (g : RawGate) (hg : g ∈ Data.phaseB) :
    g.1 < 672 ∧ g.2.1 < 729 ∧ ∀ r ∈ g.2.2, r < 729 := by
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

theorem decoded_gate_properties (g : BitXor.Gate Register) (hg : g ∈ decodedPhaseB) :
    IsTarget g.dst ∧ ∀ r ∈ g.sources, ¬ IsTarget r := by
  obtain ⟨raw, hraw, heq⟩ := List.mem_map.mp hg
  subst g
  constructor
  · change 120 ≤ raw.val.2.1 ∧ raw.val.2.1 < 240
    exact of_decide_eq_true ((List.all_eq_true.mp target_destinations) raw.val raw.property)
  · intro r hr
    simp only [decodeGate] at hr
    obtain ⟨source, hsource, heq⟩ := List.mem_map.mp hr
    subst r
    change ¬ (120 ≤ source.val ∧ source.val < 240)
    have h := of_decide_eq_true ((List.all_eq_true.mp
      ((List.all_eq_true.mp no_target_operands) raw.val raw.property)) source.val source.property)
    rcases h with hlt | hge
    · exact fun ht => (Nat.not_le_of_lt hlt) ht.1
    · exact fun ht => (Nat.not_le_of_lt ht.2) hge

/-- Execute exactly the ordered B tuple list in the raw Boolean scalar model. -/
def executeB (s : State) : State := BitXor.run decodedPhaseB s

/-- Every source/helper bit is unchanged for arbitrary729 input bits. -/
theorem sources_helpers_preserved (s : State) (r : Register) (hr : ¬ IsTarget r) :
    executeB s r = s r :=
  BitXor.run_off_target IsTarget decodedPhaseB
    (fun g hg => (decoded_gate_properties g hg).1) s r hr

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

end CurrentMain.SelectedBitCarrierPhaseBXor
#print axioms CurrentMain.SelectedBitCarrierPhaseBXor.decode_roundtrip
#print axioms CurrentMain.SelectedBitCarrierPhaseBXor.ordered_word_binding
#print axioms CurrentMain.SelectedBitCarrierPhaseBXor.decoded_gate_properties
#print axioms CurrentMain.SelectedBitCarrierPhaseBXor.sources_helpers_preserved
#print axioms CurrentMain.SelectedBitCarrierPhaseBXor.target_translation
#print axioms CurrentMain.SelectedBitCarrierPhaseBXor.target_identity
#print axioms CurrentMain.SelectedBitCarrierPhaseBXor.contribution_independent_of_targets
