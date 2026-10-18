-- EXPECTED COMPILATION FAILURE: MP and the residual identity hold, but QP does not.
import fixtures.Positive
open PR1497 PR1497.Fixtures
example : matMul scalarZero scalarZero 0 0 = eye 1 0 0 := by
  decide
