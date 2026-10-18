-- EXPECTED COMPILATION FAILURE: QP and the residual identity hold, but MP does not.
import fixtures.Positive
open PR1497 PR1497.Fixtures
example : matMul scalarOne scalarOne 0 0 = zeroMat 1 1 0 0 := by
  decide
