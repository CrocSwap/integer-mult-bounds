import PairedCubeSourceLabels
namespace CurrentMain.PairedCubeSourceLabels
def labelsFor (pairs i : Nat) : List Nat :=
  (List.range pairs).flatMap fun j => (List.range pairs).flatMap fun k =>
    if i<j ∧ j<k then choices i j k else []
theorem labels_eq_blocks (pairs : Nat) : labels pairs=(List.range pairs).flatMap (labelsFor pairs) := rfl
end CurrentMain.PairedCubeSourceLabels
#print axioms CurrentMain.PairedCubeSourceLabels.labels_eq_blocks
