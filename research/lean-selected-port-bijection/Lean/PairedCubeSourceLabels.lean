import Lean

namespace CurrentMain.PairedCubeSourceLabels

/-- One coordinate from each of three distinct ordered pairs. -/
def mask (i j k a b c : Nat) : Nat :=
  2^(2*i+a) + 2^(2*j+b) + 2^(2*k+c)

def choices (i j k : Nat) : List Nat :=
  (List.range 2).flatMap fun a =>
    (List.range 2).flatMap fun b =>
      (List.range 2).map fun c => mask i j k a b c

/-- Lexicographic pair triples, then the three binary coordinate choices. -/
def labels (pairs : Nat) : List Nat :=
  (List.range pairs).flatMap fun i =>
    (List.range pairs).flatMap fun j =>
      (List.range pairs).flatMap fun k =>
        if i<j ∧ j<k then choices i j k else []

theorem choices_mem (i j k x : Nat) : x ∈ choices i j k ↔
    ∃ a, a<2 ∧ ∃ b, b<2 ∧ ∃ c, c<2 ∧ mask i j k a b c=x := by
  simp only [choices,List.mem_flatMap,List.mem_map,List.mem_range]

theorem labels_mem (pairs x : Nat) : x ∈ labels pairs ↔
    ∃ i, i<pairs ∧ ∃ j, j<pairs ∧ ∃ k, k<pairs ∧
      i<j ∧ j<k ∧ ∃ a, a<2 ∧ ∃ b, b<2 ∧ ∃ c, c<2 ∧ mask i j k a b c=x := by
  simp only [labels,List.mem_flatMap,List.mem_range,List.mem_ite_nil_right,choices_mem]
  constructor
  · rintro ⟨i,hi,j,hj,k,hk,⟨hij,hjk⟩,rest⟩
    exact ⟨i,hi,j,hj,k,hk,hij,hjk,rest⟩
  · rintro ⟨i,hi,j,hj,k,hk,hij,hjk,rest⟩
    exact ⟨i,hi,j,hj,k,hk,⟨hij,hjk⟩,rest⟩

end CurrentMain.PairedCubeSourceLabels
#print axioms CurrentMain.PairedCubeSourceLabels.choices_mem
#print axioms CurrentMain.PairedCubeSourceLabels.labels_mem
