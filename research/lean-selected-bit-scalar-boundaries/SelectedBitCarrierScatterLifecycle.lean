import SelectedBitCarrierPhaseBXor
import BitCopyScatterWindow

/-! Source-bound Boolean projection of export_records.py's retained-major
COPY/ADD/ERASE slice. Reuses accepted ret/scatter literals. There are730 scalar
registers: the original729 plus disposable729. Frame fq, ZERO and COPY rank
remain physical obligations; no clean original input/helper premise is added.
The generated loop order is centre-major, not row-major. -/
namespace CurrentMain.SelectedBitCarrierScatterLifecycle
open SelectedBitCarrierPhaseB
set_option Elab.async false
abbrev Register := Fin 730
abbrev State := Register → Bool
abbrev RawWindow := Nat × List Nat

def temp : Register := ⟨729, by decide⟩
def IsTarget (r : Register) : Prop := 120 ≤ r.val ∧ r.val < 240

/-- Exact enumerate-ret, enumerate-scatter, membership-test scalar projection.
No default lookup is used. COPY/ERASE surround each returned destination list. -/
def rawWindows : List RawWindow :=
  Boundary.ret.zipIdx.map (fun q =>
    (q.1, Data.scatter.zipIdx.filterMap (fun row =>
      if q.2 ∈ row.1 then some (120 + row.2) else none)))

theorem raw_shape : rawWindows.length = 9 ∧
    rawWindows.map (fun w => w.2.length) = [120,56,56,56,56,56,56,56,56] ∧
    (rawWindows.map (fun w => w.2.length + 2)).foldl Nat.add 0 = 586 := by
  decide +kernel

theorem raw_domains : rawWindows.all (fun w =>
    decide (720 ≤ w.1 ∧ w.1 < 729) &&
    w.2.all (fun d => decide (120 ≤ d ∧ d < 240))) = true := by
  decide +kernel

/-- Membership emits each target once per retained index. The stored rows also
have no repeated indices, recorded separately without permuting the word. -/
theorem source_rows_no_duplicates : Data.scatter.all (fun row => decide row.Nodup) = true := by
  decide +kernel

attribute [local irreducible] rawWindows Data.scatter

private theorem raw_properties (w : RawWindow) (hw : w ∈ rawWindows) :
    (720 ≤ w.1 ∧ w.1 < 729) ∧ ∀ d ∈ w.2, 120 ≤ d ∧ d < 240 := by
  have h := Bool.and_eq_true_iff.mp ((List.all_eq_true.mp raw_domains) w hw)
  refine ⟨of_decide_eq_true h.1, ?_⟩
  intro d hd
  exact of_decide_eq_true ((List.all_eq_true.mp h.2) d hd)

def decodeWindow (w : RawWindow) (hw : w ∈ rawWindows) : BitCopyScatter.Window Register where
  centre := ⟨w.1, Nat.lt_trans (raw_properties w hw).1.2 (by decide : 729 < 730)⟩
  targets := w.2.attach.map (fun d =>
    ⟨d.val, Nat.lt_trans ((raw_properties w hw).2 d.val d.property).2 (by decide : 240 < 730)⟩)

def windows : List (BitCopyScatter.Window Register) :=
  rawWindows.attach.map (fun w => decodeWindow w.val w.property)

def encodeWindow (w : BitCopyScatter.Window Register) : RawWindow :=
  (w.centre.val, w.targets.map Fin.val)

theorem decode_roundtrip (w : RawWindow) (hw : w ∈ rawWindows) :
    encodeWindow (decodeWindow w hw) = w := by
  rcases w with ⟨centre, targets⟩
  simp only [encodeWindow, decodeWindow, List.map_map, Function.comp_def]
  rw [List.attach_map_subtype_val]

theorem ordered_window_binding : windows.map encodeWindow = rawWindows := by
  unfold windows
  rw [List.map_map]
  simp only [Function.comp_def, decode_roundtrip]
  exact List.attach_map_subtype_val _

theorem decoded_bounds (w : BitCopyScatter.Window Register) (hw : w ∈ windows) :
    (720 ≤ w.centre.val ∧ w.centre.val < 729) ∧
      ∀ d ∈ w.targets, IsTarget d := by
  obtain ⟨raw, hraw, heq⟩ := List.mem_map.mp hw
  subst w
  constructor
  · exact (raw_properties raw.val raw.property).1
  · intro d hd
    simp only [decodeWindow] at hd
    obtain ⟨target, htarget, heq⟩ := List.mem_map.mp hd
    subst d
    exact (raw_properties raw.val raw.property).2 target.val target.property

theorem windows_well_formed (w : BitCopyScatter.Window Register) (hw : w ∈ windows) :
    BitCopyScatter.WellFormed temp w := by
  have h := decoded_bounds w hw
  constructor
  · intro he
    have hv := congrArg Fin.val he
    exact (Nat.ne_of_lt h.1.2) hv
  · intro d hd
    have ht := h.2 d hd
    constructor
    · intro he
      have hv := congrArg Fin.val he
      exact (Nat.ne_of_lt (Nat.lt_trans ht.2 (by decide : 240 < 729))) hv
    · intro he
      have hv := congrArg Fin.val he
      exact (Nat.ne_of_lt (Nat.lt_of_lt_of_le ht.2
        (Nat.le_trans (by decide : 240 ≤ 720) h.1.1))) hv

theorem windows_nonempty : windows ≠ [] := by
  have hl : windows.length = 9 := by
    simpa only [windows, List.length_map, List.length_attach] using raw_shape.1
  intro he
  rw [he] at hl
  contradiction

def executeScatter (s : State) : State := BitCopyScatter.runWindows temp windows s
def directScatter (s : State) : State := BitCopyScatter.directWindows windows s

/-- Every original coordinate follows the direct retained-major XOR scatter;
the temporary is explicitly discarded to false for every incoming value. -/
theorem exact_lifecycle (s : State) :
    executeScatter s = BitCopyScatter.clear temp (directScatter s) :=
  BitCopyScatter.runWindows_eq_clear_direct temp windows windows_nonempty windows_well_formed s

theorem final_temp_zero (s : State) : executeScatter s temp = false := by
  rw [exact_lifecycle]
  exact BitCopyScatter.clear_at_temp temp (directScatter s)

theorem original_coordinate (s : State) (r : Register) (hr : r ≠ temp) :
    executeScatter s r = directScatter s r := by
  rw [exact_lifecycle]
  simp [BitCopyScatter.clear, hr]

/-- Arbitrary original source/helper dirt is retained across the copy slice. -/
theorem sources_helpers_preserved (s : State) (r : Register)
    (hr : ¬ IsTarget r) (ht : r ≠ temp) : executeScatter s r = s r := by
  rw [original_coordinate s r ht]
  exact BitCopyScatter.directWindows_untouched windows s r
    (fun w hw hmem => hr ((decoded_bounds w hw).2 r hmem))

theorem incoming_temp_independent (s t : State)
    (h : ∀ r, r ≠ temp → s r = t r) : executeScatter s = executeScatter t :=
  BitCopyScatter.runWindows_independent_of_temp temp windows windows_nonempty windows_well_formed s t h

/-- This restoration statement requires the disposable slot to start at zero.
No restoration of an arbitrary dirty730th coordinate follows. -/
theorem clean_temp_restored (s : State) (h : s temp = false) :
    executeScatter s temp = s temp := by
  rw [final_temp_zero, h]

end CurrentMain.SelectedBitCarrierScatterLifecycle
#print axioms CurrentMain.SelectedBitCarrierScatterLifecycle.raw_shape
#print axioms CurrentMain.SelectedBitCarrierScatterLifecycle.raw_domains
#print axioms CurrentMain.SelectedBitCarrierScatterLifecycle.source_rows_no_duplicates
#print axioms CurrentMain.SelectedBitCarrierScatterLifecycle.decode_roundtrip
#print axioms CurrentMain.SelectedBitCarrierScatterLifecycle.ordered_window_binding
#print axioms CurrentMain.SelectedBitCarrierScatterLifecycle.decoded_bounds
#print axioms CurrentMain.SelectedBitCarrierScatterLifecycle.windows_well_formed
#print axioms CurrentMain.SelectedBitCarrierScatterLifecycle.windows_nonempty
#print axioms CurrentMain.SelectedBitCarrierScatterLifecycle.exact_lifecycle
#print axioms CurrentMain.SelectedBitCarrierScatterLifecycle.final_temp_zero
#print axioms CurrentMain.SelectedBitCarrierScatterLifecycle.original_coordinate
#print axioms CurrentMain.SelectedBitCarrierScatterLifecycle.sources_helpers_preserved
#print axioms CurrentMain.SelectedBitCarrierScatterLifecycle.incoming_temp_independent
#print axioms CurrentMain.SelectedBitCarrierScatterLifecycle.clean_temp_restored
