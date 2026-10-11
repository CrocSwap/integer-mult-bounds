import CurrentComplexPortLabelBlock00
import CurrentComplexPortLabelBlock01
import CurrentComplexPortLabelBlock02
import CurrentComplexPortLabelBlock03
import CurrentComplexPortLabelBlock04
import CurrentComplexPortLabelBlock05
import CurrentComplexPortLabelBlock06
import CurrentComplexPortLabelBlock07
import CurrentComplexPortLabelBlock08
set_option maxRecDepth 100000
set_option maxHeartbeats 16000000
namespace CurrentMain.CurrentComplexPortLabels
open CurrentMain.ComplexGeometryData CurrentMain.PairedCubeSourceLabels

/-- Empty final pair-triple blocks; no selected input lookup is evaluated. -/
theorem block09_empty : labelsFor 11 9 = [] := by decide
theorem block10_empty : labelsFor 11 10 = [] := by decide

attribute [local irreducible] inputMask labelsFor

/-- Exact core range concatenation, with every source lookup left opaque. -/
theorem source_decomposition : (List.range 1320).map inputMask =
    (List.range' 0 360).map inputMask ++
    (List.range' 360 288).map inputMask ++
    (List.range' 648 224).map inputMask ++
    (List.range' 872 168).map inputMask ++
    (List.range' 1040 120).map inputMask ++
    (List.range' 1160 80).map inputMask ++
    (List.range' 1240 48).map inputMask ++
    (List.range' 1288 24).map inputMask ++
    (List.range' 1312 8).map inputMask := by
  rw [List.range_eq_range']
  rw [← List.range'_append_1 (s := 0) (m := 360) (n := 960)]
  rw [← List.range'_append_1 (s := 360) (m := 288) (n := 672)]
  rw [← List.range'_append_1 (s := 648) (m := 224) (n := 448)]
  rw [← List.range'_append_1 (s := 872) (m := 168) (n := 280)]
  rw [← List.range'_append_1 (s := 1040) (m := 120) (n := 160)]
  rw [← List.range'_append_1 (s := 1160) (m := 80) (n := 80)]
  rw [← List.range'_append_1 (s := 1240) (m := 48) (n := 32)]
  rw [← List.range'_append_1 (s := 1288) (m := 24) (n := 8)]
  simp only [List.map_append, List.append_assoc]

/-- The existing1320 selected source ports are exactly the paired-cube labels11. -/
theorem canonical_labels : (List.range 1320).map inputMask = labels 11 := by
  rw [source_decomposition, block00, block01, block02, block03, block04, block05, block06, block07, block08, labels_eq_blocks]
  have range11 : List.range 11 = [0,1,2,3,4,5,6,7,8,9,10] := rfl
  rw [range11]
  simp only [List.flatMap_cons, List.flatMap_nil, block09_empty, block10_empty,
    List.append_nil, List.append_assoc]
end CurrentMain.CurrentComplexPortLabels
#print axioms CurrentMain.CurrentComplexPortLabels.block09_empty
#print axioms CurrentMain.CurrentComplexPortLabels.block10_empty
#print axioms CurrentMain.CurrentComplexPortLabels.source_decomposition
#print axioms CurrentMain.CurrentComplexPortLabels.canonical_labels
