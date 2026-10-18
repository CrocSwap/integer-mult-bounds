# One frame relation cannot amortize rank, with arbitrarily many roles

For any number W of scalar registers, consider paid factors
`I + ([A_j] - 1) N_j` over the formal group algebra of additive rational
matrices. Each nonzero A_j has rational rank one and each binary N_j is a
rank-one idempotent. Allow arbitrary free scalar GL_W(F2) changes of basis.
Suppose the target is `diag([C_1], ..., [C_W])`, including zero C_i for
arbitrary dirty roles restored exactly.

**If the k paid frames have rational span dimension at least k - 1, then
the sum of the rational ranks of the target frames is at most k.**
Thus an improvement below m times the number of active rank-m roles requires
at least two independent rational relations among the paid frames, regardless
of the number of restored dirty registers. This does not resolve the case of
two or more relations or establish a new multiplication constant.

## What is new and what is reused

Section 4 of the retained bit-three-register-lower-bound note treats the
eight-call, three-register instance by a Laurent-kernel derivative argument.
This package credits and reuses that argument. Its new step classifies a common
rank-one off-diagonal pattern in arbitrary dimension and uses a diagonal
idempotent argument to control every outside coordinate gate. It thereby
removes the register-count restriction from the one-relation lemma.

[PROOF.md](PROOF.md) supplies the complete arbitrary-W proof. A cyclic common
off-diagonal pattern uniquely determines its binary rank-one projector in any
dimension. An acyclic common pattern admits a common triangular order. In the
cyclic case, deleting outside independent variables forces the relation to be
the all-plus relation; conjugating one outside coordinate idempotent then
forces it either to commute with the common projector or to lie outside the
entire cancelling block. The remaining paid frames allocate disjointly among
target coordinates, and rank subadditivity gives the claimed bound.

The proof concerns the formal torsion-free group algebra. A specialization to
a finite torsion representation is not sufficient evidence for its premise.

## Reproduce and controls

`python -I -O -B research/bit-one-relation-any-registers/verify.py`

The checker exhausts all binary rank-one idempotents for W = 1 through 5:
1, 6, 28, 120 and 496 projectors. It checks the common-pattern classification
and all 3,057 coordinate-idempotent Laurent conjugations. Forty-eight exact
four-register placement fixtures exercise the one-relation block argument,
including cyclic projectors with incoming and outgoing tails. A torsion
countercontrol passes after unsafe reduction modulo 2 but fails the formal
diagonal target. These finite checks corroborate the lemmas; the written
proof establishes the arbitrary-W claim.

Python 3.12 registered replay, source metadata and selected-result integrity
pass. No verifier uses assertions, random sampling, floating arithmetic or
finite address aliasing as a substitute for formal equality.

## Open next questions

The first unaddressed regime has two independent frame relations. Its Laurent
kernel need not be principal, so the derivative no longer forces one common
off-diagonal pattern. A useful next experiment is to classify the possible
two-dimensional spaces of off-diagonal patterns for a bounded register count,
retaining exact relation signs and arbitrary dirty endpoints. The blocker is
the additional pattern interactions, not a deficiency in the finite controls
for the one-relation statement.

## Scope and credit

The result permits arbitrary rational target frames, arbitrary numbers of
restored dirty roles and free binary scalar basis changes. It requires nonzero
rank-one paid frames and at most one rational frame relation. It is not an
unrestricted lower bound, a physical helper schedule, a bridge into the native
compiler, a precision theorem or a new kappa claim.

Credit to Ali Romman and the retained bit-three-register-lower-bound source for the Laurent-kernel strategy and the original three-role
case. Exact source pins appear in SOURCES.json; overlap coverage and limits
appear in OVERLAP.json. Prepared for woklerx with substantial OpenAI Codex
assistance. Apache-2.0.
