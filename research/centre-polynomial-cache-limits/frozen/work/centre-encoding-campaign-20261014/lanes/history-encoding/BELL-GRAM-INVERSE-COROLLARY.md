# A limit for scalar-polynomial inverse formulas

`BELL-GRAM-DEGREE-PROOF.md` and its independent review prove that the
actual doubled centre Gram A_lambda has minimal-polynomial degree at
least 409 for every positive tensor size lambda.

Let `aI+bA_lambda` be invertible over a characteristic-zero coefficient
field, with `b!=0`. If a scalar polynomial q satisfies

    q(A_lambda)=(aI+bA_lambda)^-1,

then q has degree at least 408. Indeed, the nonzero polynomial
`(a+bt)q(t)-1` annihilates A_lambda. Its degree is at most `deg(q)+1`,
so the degree lower bound gives the claim. The polynomial is nonzero
because a nonconstant linear polynomial has no polynomial reciprocal.

This result concerns exact scalar-polynomial representations only. It
does not rule out a rational expression, a factorized matrix-valued
encoding, an algorithm that uses native frame access, or a direct ADD
circuit for the weighted Gram. It does not assign a native cost to one
polynomial evaluation. The interface-proof lane supplied this corollary.
The work used AI assistance.
