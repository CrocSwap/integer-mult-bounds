import SelectedR480ACData
import BitXorReversal

/-! A bounded current-source A/C inverse certificate. Only the last20 A gates
and first20 C gates are present. Frame IDs are retained by the ordered binding;
scalarization is used explicitly for their different metadata. The conclusion
is Boolean scalar inversion for arbitrary720 bits, with conditional off-target
cleanup across any target-only middle map. It is not the full2708-gate A/C
instance, D compensation, frame transport or a complete multiplier theorem. -/
namespace CurrentMain.SelectedR480ACBoundary
open Data
set_option Elab.async false
abbrev RawGate := Nat × Nat × List Nat
abbrev Register := Fin 720
abbrev State := BitXor.State Register

def IsTarget (r : Register) : Prop := 120 ≤ r.val ∧ r.val < 240
instance (r : Register) : Decidable (IsTarget r) := inferInstanceAs (Decidable (120 ≤ r.val ∧ r.val < 240))

def rawFrameOne (g : RawGate) : RawGate := (1, g.2.1, g.2.2)

theorem block_shape :
    phaseATail.length = 20 ∧ phaseCHead.length = 20 ∧
    (phaseATail.map (fun g => g.2.2.length)).foldl Nat.add 0 = 445 ∧
    (phaseCHead.map (fun g => g.2.2.length)).foldl Nat.add 0 = 445 ∧
    (phaseATail.map (fun g => g.2.2.length)).foldl Nat.max 0 = 54 := by decide +kernel

/-- All nine changed retained-total hosts occur in their exact source order. -/
theorem changed_hosts_binding :
    (phaseATail.drop 11).map (fun g => g.2.1) = SelectedR480Boundary.Data.ret := by
  decide +kernel

theorem raw_domains :
    (phaseATail ++ phaseCHead).all (fun g =>
      decide (g.1 < 672 ∧ g.2.1 < 720) &&
        g.2.2.all (fun r => decide (r < 720))) = true := by decide +kernel

/-- Exact ordered cleanup relation, without identifying unequal frame IDs. -/
theorem raw_cleanup_binding : phaseCHead = phaseATail.reverse.map rawFrameOne := by
  decide +kernel

theorem no_self_reads :
    phaseATail.all (fun g => g.2.2.all (fun r => decide (r ≠ g.2.1))) = true := by
  decide +kernel

theorem no_target_reads :
    phaseATail.all (fun g => g.2.2.all (fun r => decide (r < 120 ∨ 240 ≤ r))) = true := by
  decide +kernel

theorem no_target_writes :
    phaseATail.all (fun g => decide (g.2.1 < 120 ∨ 240 ≤ g.2.1)) = true := by
  decide +kernel

attribute [local irreducible] phaseATail phaseCHead

private theorem a_domains (g : RawGate) (hg : g ∈ phaseATail) :
    g.1 < 672 ∧ g.2.1 < 720 ∧ ∀ r ∈ g.2.2, r < 720 := by
  have hm : g ∈ phaseATail ++ phaseCHead := List.mem_append_left _ hg
  have h := Bool.and_eq_true_iff.mp ((List.all_eq_true.mp raw_domains) g hm)
  have hd := of_decide_eq_true h.1
  refine ⟨hd.1, hd.2, ?_⟩
  intro r hr
  exact of_decide_eq_true ((List.all_eq_true.mp h.2) r hr)

def decodeGate (g : RawGate) (hg : g ∈ phaseATail) : BitXor.Gate Register where
  frame := g.1
  dst := ⟨g.2.1, (a_domains g hg).2.1⟩
  sources := g.2.2.attach.map (fun r => ⟨r.val, (a_domains g hg).2.2 r.val r.property⟩)

def decodedA : List (BitXor.Gate Register) :=
  phaseATail.attach.map (fun g => decodeGate g.val g.property)

def frameOne (g : BitXor.Gate Register) : BitXor.Gate Register :=
  { frame := 1, dst := g.dst, sources := g.sources }

def decodedC : List (BitXor.Gate Register) := decodedA.reverse.map frameOne

def encodeGate (g : BitXor.Gate Register) : RawGate :=
  (g.frame, g.dst.val, g.sources.map Fin.val)

theorem decode_roundtrip (g : RawGate) (hg : g ∈ phaseATail) :
    encodeGate (decodeGate g hg) = g := by
  rcases g with ⟨f,d,rs⟩
  simp only [encodeGate, decodeGate, List.map_map, Function.comp_def]
  rw [List.attach_map_subtype_val]

theorem ordered_A_binding : decodedA.map encodeGate = phaseATail := by
  unfold decodedA
  rw [List.map_map]
  simp only [Function.comp_def, decode_roundtrip]
  exact List.attach_map_subtype_val _

theorem ordered_C_binding : decodedC.map encodeGate = phaseCHead := by
  calc
    decodedC.map encodeGate = (decodedA.map encodeGate).reverse.map rawFrameOne := by
      simp only [decodedC, List.map_map, List.map_reverse, Function.comp_def,
        encodeGate, frameOne, rawFrameOne]
    _ = phaseATail.reverse.map rawFrameOne := by rw [ordered_A_binding]
    _ = phaseCHead := raw_cleanup_binding.symm

theorem decoded_no_self_reads (g : BitXor.Gate Register) (hg : g ∈ decodedA) :
    g.dst ∉ g.sources := by
  obtain ⟨raw, hraw, heq⟩ := List.mem_map.mp hg
  subst g
  intro hd
  simp only [decodeGate] at hd
  obtain ⟨source, hsource, heq⟩ := List.mem_map.mp hd
  have h := of_decide_eq_true ((List.all_eq_true.mp
    ((List.all_eq_true.mp no_self_reads) raw.val raw.property)) source.val source.property)
  exact h (congrArg Fin.val heq)

theorem decoded_no_target_reads (g : BitXor.Gate Register) (hg : g ∈ decodedA) :
    ∀ r ∈ g.sources, ¬ IsTarget r := by
  obtain ⟨raw, hraw, heq⟩ := List.mem_map.mp hg
  subst g
  intro r hr
  simp only [decodeGate] at hr
  obtain ⟨source, hsource, heq⟩ := List.mem_map.mp hr
  subst r
  change ¬ (120 ≤ source.val ∧ source.val < 240)
  have h := of_decide_eq_true ((List.all_eq_true.mp
    ((List.all_eq_true.mp no_target_reads) raw.val raw.property)) source.val source.property)
  rcases h with hlt | hge
  · exact fun ht => (Nat.not_le_of_lt hlt) ht.1
  · exact fun ht => (Nat.not_le_of_lt ht.2) hge

theorem decoded_no_target_writes (g : BitXor.Gate Register) (hg : g ∈ decodedA) :
    ¬ IsTarget g.dst := by
  obtain ⟨raw, hraw, heq⟩ := List.mem_map.mp hg
  subst g
  change ¬ (120 ≤ raw.val.2.1 ∧ raw.val.2.1 < 240)
  have h := of_decide_eq_true ((List.all_eq_true.mp no_target_writes) raw.val raw.property)
  rcases h with hlt | hge
  · exact fun ht => (Nat.not_le_of_lt hlt) ht.1
  · exact fun ht => (Nat.not_le_of_lt ht.2) hge

theorem cleanup_runs_reverse (s : State) :
    BitXor.run decodedC s = BitXor.run decodedA.reverse s := by
  have h : decodedC.map BitXorReversal.scalarize =
      decodedA.reverse.map BitXorReversal.scalarize := by
    simp only [decodedC, List.map_map, Function.comp_def, frameOne, BitXorReversal.scalarize]
    rfl
  calc
    BitXor.run decodedC s = BitXor.run (decodedC.map BitXorReversal.scalarize) s :=
      (BitXorReversal.run_scalarize decodedC s).symm
    _ = BitXor.run (decodedA.reverse.map BitXorReversal.scalarize) s := by rw [h]
    _ = BitXor.run decodedA.reverse s := BitXorReversal.run_scalarize decodedA.reverse s

/-- The exact isolated20+20 scalar word cancels on arbitrary720-bit state. -/
theorem isolated_block_inverse (s : State) :
    BitXor.run decodedC (BitXor.run decodedA s) = s := by
  rw [cleanup_runs_reverse]
  exact BitXorReversal.run_reverse_cancel decodedA decoded_no_self_reads s

/-- A target-only middle update does not prevent this block's off-target cleanup. -/
theorem conditional_off_target_cleanup (middle : State → State)
    (hmiddle : ∀ s r, ¬ IsTarget r → middle s r = s r)
    (s : State) (r : Register) (hr : ¬ IsTarget r) :
    BitXor.run decodedC (middle (BitXor.run decodedA s)) r = s r := by
  rw [cleanup_runs_reverse]
  exact BitXorReversal.cleanup_off_target IsTarget decodedA decoded_no_self_reads
    decoded_no_target_reads middle hmiddle s r hr

theorem conditional_target_value (middle : State → State)
    (s : State) (r : Register) (hr : IsTarget r) :
    BitXor.run decodedC (middle (BitXor.run decodedA s)) r =
      middle (BitXor.run decodedA s) r := by
  rw [cleanup_runs_reverse]
  exact BitXorReversal.cleanup_target_value IsTarget decodedA decoded_no_target_writes
    middle s r hr

end CurrentMain.SelectedR480ACBoundary
#print axioms CurrentMain.SelectedR480ACBoundary.block_shape
#print axioms CurrentMain.SelectedR480ACBoundary.changed_hosts_binding
#print axioms CurrentMain.SelectedR480ACBoundary.raw_domains
#print axioms CurrentMain.SelectedR480ACBoundary.raw_cleanup_binding
#print axioms CurrentMain.SelectedR480ACBoundary.no_self_reads
#print axioms CurrentMain.SelectedR480ACBoundary.no_target_reads
#print axioms CurrentMain.SelectedR480ACBoundary.no_target_writes
#print axioms CurrentMain.SelectedR480ACBoundary.decode_roundtrip
#print axioms CurrentMain.SelectedR480ACBoundary.ordered_A_binding
#print axioms CurrentMain.SelectedR480ACBoundary.ordered_C_binding
#print axioms CurrentMain.SelectedR480ACBoundary.decoded_no_self_reads
#print axioms CurrentMain.SelectedR480ACBoundary.decoded_no_target_reads
#print axioms CurrentMain.SelectedR480ACBoundary.decoded_no_target_writes
#print axioms CurrentMain.SelectedR480ACBoundary.cleanup_runs_reverse
#print axioms CurrentMain.SelectedR480ACBoundary.isolated_block_inverse
#print axioms CurrentMain.SelectedR480ACBoundary.conditional_off_target_cleanup
#print axioms CurrentMain.SelectedR480ACBoundary.conditional_target_value
