# The exact theorem-to-source boundary

Write `P_g f(y)=f(g^-1 y)`. If `x` separates the labels, then
`(sum_g a_g P_g)(delta_x)(h x)=a_h`: two-sided inverses turn a hit into
`g x=h x`, separation gives `g=h`, and a duplicate-free complete sum retains
that term exactly once. For a matrix, put `delta_x` in input role `j` and zero
in the other roles, then observe output role `i` at `h x`. This extracts
`a[i,j,h]`. Equality for all dirty inputs yields equality of all coefficients.
These steps, including finite XOR cancellation, are kernel proofs rather than
an informal justification of an assumed faithfulness predicate.

For the explicit instance, `mv3` is the Boolean row/column formula for a
3-by-3 binary matrix. Applying it to basis column `j` gives matrix entry
`a[i,j]`. Therefore equality of images of all three basis columns implies
matrix equality. This proof applies to all matrices; restricting to those
with a two-sided inverse supplies a `PermFamily`. The inverse chosen from
the subtype is used only with its proved inverse laws. The theorem uses
exactly three point columns, with no unstated extension to all widths.

| Obligation | Evidence | Remaining assumption |
|---|---|---|
| Finite XOR coefficient extraction | `coefficient_extract` | Stated inverse, separation and list premises |
| All dirty input and output blocks | `complete_endpoint_faithful` | Every role occurs once in the role list |
| Concrete 3-by-3 action formula | `mv3`, `tupleAction3` | None beyond their definitions |
| Three basis columns separate matrices | `mv3_basis`, `basis_tuple_separates_matrices` | None |
| Invertible instance is inhabited | `identityGL3`, `gl3_identity_basis` | None |
| GL3 inverse permutation and separation | `gl3Perm`, `gl3_basis_separates` | GL3 is defined by existence of a two-sided linear inverse |
| GL3 complete endpoint faithfulness | `gl3_complete_endpoint_faithful` | Complete duplicate-free role and GL3 lists |
| All168 concrete GL3 labels | Python enumeration by bijection on all8 vectors, compared with pinned source | External, not a kernel-certified enumeration |
| PR2599 parser/action agrees | All168*512 encoded address comparisons and 2*168*512 inverse identities | Python execution and the explicit bit encoding are outside Lean |
| Arbitrary circuit words evaluate to the declared coefficient matrix | No proof supplied | Must be proved for a downstream application |
| PR1974 search/minimum certificate | Not rerun or formalized | Prior separately scoped evidence only |
| Physical operations, workspace, tapes, recursive admission | No evidence supplied | Entirely outside this result |

The conformance script independently enumerates all512 binary matrices,
retains precisely those bijective on the eight vectors, and compares its
literal Boolean formula against the authenticated PR2599 source bytes. It
checks every full three-column address, not merely the separating tuple.
Encoded columns use low-to-high three-bit blocks; the basis tuple is273.
The source acts forward on delta payloads; the Lean action uses inverse
pullback on functions. The checked inverse identities establish their usual
pointwise relationship on this finite domain, but that relationship is not a
formal parser theorem.

`FORMAL-RESULT.json` records a completed fresh local run. Binding that receipt
with Python verifies file integrity only. It cannot establish a kernel proof
on a machine where Lean has not been run. `formal_verify.py` is the separate
reproduction command and rejects unrecognized axioms and all four false
control statements after compiling the valid countermodels.

The controls are intentionally scoped. A colliding pair of identity actions
violates separation only. A repeated C2 label retains completeness and a
separating action but violates uniqueness. Omitting one C2 label retains
uniqueness and separation but violates completeness. The clean-role example
has a real off-diagonal leak invisible when that input is zero; its full dirty
endpoint is unequal. These are concrete countermodels, not a claim that the
formal runner has mechanically generalized every theorem by deleting each
hypothesis.
