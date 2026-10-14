import CurrentComplexPortLabels
import CGInputChecks

/-! Source-only selected port reindexing. Uses the accepted1320 ordered
label equality and existing inverse-table facts; no finite evaluation.
These maps retain complete payload rows and arbitrary helpers. Actual physical
stage routing, frames, full backward execution, normalization and costs are
separate source obligations. -/
namespace CurrentMain.CurrentComplexPortBijection

open CurrentMain.ComplexGeometryData CurrentMain.ComplexGeometryInputs
open CurrentMain.PairedCubeSourceLabels CurrentMain.SignedTrace

attribute [local irreducible] inputMask inverseTable

abbrev Label := {q : Nat // q ∈ labels 11}

theorem input_mem (i : Fin 1320) : inputMask i.val ∈ labels 11 := by
  rw [← CurrentComplexPortLabels.canonical_labels]
  exact List.mem_map.mpr ⟨i.val, List.mem_range.mpr i.isLt, rfl⟩

def toLabel (i : Fin 1320) : Label := ⟨inputMask i.val, input_mem i⟩

theorem label_has_index (q : Label) : ∃ i : Fin 1320, inputMask i.val = q.val := by
  have mem : q.val ∈ (List.range 1320).map inputMask := by
    rw [CurrentComplexPortLabels.canonical_labels]
    exact q.property
  obtain ⟨i, hi, equal⟩ := List.mem_map.mp mem
  exact ⟨⟨i, List.mem_range.mp hi⟩, equal⟩

theorem inverse_bound (q : Label) : get inverseTable q.val < 1320 := by
  obtain ⟨i, equal⟩ := label_has_index q
  have inverse := (input_facts i.val i.isLt).2
  rw [equal] at inverse
  rw [inverse]
  exact i.isLt

/-- The inverse is the existing actual inverse-table lookup, not a choice. -/
def fromLabel (q : Label) : Fin 1320 :=
  ⟨get inverseTable q.val, inverse_bound q⟩

theorem fromLabel_toLabel (i : Fin 1320) : fromLabel (toLabel i) = i := by
  apply Fin.ext
  change get inverseTable (inputMask i.val) = i.val
  exact (input_facts i.val i.isLt).2

theorem toLabel_fromLabel (q : Label) : toLabel (fromLabel q) = q := by
  obtain ⟨i, equal⟩ := label_has_index q
  have label_equal : toLabel i = q := Subtype.ext equal
  rw [← label_equal, fromLabel_toLabel]

theorem toLabel_injective (i j : Fin 1320) (equal : toLabel i = toLabel j) : i = j := by
  apply Fin.ext
  exact input_injective i.val i.isLt j.val j.isLt (congrArg Subtype.val equal)

universe u v w
variable {G : Type u} {V : Type v} {H : Type w}

/-- Reindex whole payload values without altering the vertex coordinate. -/
def gather (x : G → Label → V) : G → Fin 1320 → V :=
  fun g i => x g (toLabel i)

def scatter (x : G → Fin 1320 → V) : G → Label → V :=
  fun g q => x g (fromLabel q)

theorem scatter_gather (x : G → Label → V) : scatter (gather x) = x := by
  funext g q
  simp only [scatter, gather, toLabel_fromLabel]

theorem gather_scatter (x : G → Fin 1320 → V) : gather (scatter x) = x := by
  funext g i
  simp only [gather, scatter, fromLabel_toLabel]

/-- Both complete banks are reindexed; the entire helper/spectator value is kept. -/
def gatherState (z : ((G → Label → V) × (G → Label → V)) × H) :
    ((G → Fin 1320 → V) × (G → Fin 1320 → V)) × H :=
  ((gather z.1.1, gather z.1.2), z.2)

def scatterState (z : ((G → Fin 1320 → V) × (G → Fin 1320 → V)) × H) :
    ((G → Label → V) × (G → Label → V)) × H :=
  ((scatter z.1.1, scatter z.1.2), z.2)

theorem scatterState_gatherState (z : ((G → Label → V) × (G → Label → V)) × H) :
    scatterState (gatherState z) = z := by
  rcases z with ⟨⟨x, y⟩, h⟩
  simp only [scatterState, gatherState, scatter_gather]

theorem gatherState_scatterState (z : ((G → Fin 1320 → V) × (G → Fin 1320 → V)) × H) :
    gatherState (scatterState z) = z := by
  rcases z with ⟨⟨x, y⟩, h⟩
  simp only [gatherState, scatterState, gather_scatter]

theorem gatherState_helpers (z : ((G → Label → V) × (G → Label → V)) × H) :
    (gatherState z).2 = z.2 := rfl

theorem scatterState_helpers (z : ((G → Fin 1320 → V) × (G → Fin 1320 → V)) × H) :
    (scatterState z).2 = z.2 := rfl

end CurrentMain.CurrentComplexPortBijection

#print axioms CurrentMain.CurrentComplexPortBijection.input_mem
#print axioms CurrentMain.CurrentComplexPortBijection.label_has_index
#print axioms CurrentMain.CurrentComplexPortBijection.inverse_bound
#print axioms CurrentMain.CurrentComplexPortBijection.fromLabel_toLabel
#print axioms CurrentMain.CurrentComplexPortBijection.toLabel_fromLabel
#print axioms CurrentMain.CurrentComplexPortBijection.toLabel_injective
#print axioms CurrentMain.CurrentComplexPortBijection.scatter_gather
#print axioms CurrentMain.CurrentComplexPortBijection.gather_scatter
#print axioms CurrentMain.CurrentComplexPortBijection.scatterState_gatherState
#print axioms CurrentMain.CurrentComplexPortBijection.gatherState_scatterState
#print axioms CurrentMain.CurrentComplexPortBijection.gatherState_helpers
#print axioms CurrentMain.CurrentComplexPortBijection.scatterState_helpers
