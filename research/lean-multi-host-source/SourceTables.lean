import MatrixData
import EndpointInterpretation

/-!
Kernel comparisons bind the generated literal matrices to their intended
initial and endpoint formulas. These equalities are not assumptions supplied
by the generator.
-/
namespace SourceMatrix
open TreeReplay
set_option maxRecDepth 100000
set_option maxHeartbeats 0

theorem initial_formula : initial = basisRows 10 987 := by rfl

theorem expected_formula : expected = Tree.tabulate 10 endpointRow := by rfl

#print axioms initial_formula
#print axioms expected_formula

end SourceMatrix
