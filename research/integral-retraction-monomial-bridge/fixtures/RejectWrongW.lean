-- EXPECTED COMPILATION FAILURE: a false residual entry, not a false new axiom.
import fixtures.Positive
open PR1497 PR1497.Fixtures
example : matSub (eye 2) (matMul P Q) 0 0 = matMul wrongW M 0 0 := by
  decide
