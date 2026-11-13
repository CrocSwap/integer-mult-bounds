# A numerical prefix bridge from the retained complete-root invariant

Status: reviewed conditional application lemma. This is not a
new precision theorem or a standalone publication. Exact canonical base is
`e54523517d0f03e58352e647c403a5af3e525a57`. The retained premise is section 5 of
`docs/research/pr-intake-evidence/pr7000-application/PROOF-REVIEW.md`, Git blob
`3dd1af2285e597676725e85ad4f65e7ad326d695`, SHA256
`4501502c2ceb9759b20372435fe4beb51082c5a5e2910c1fd5dbe6edca415055`.
Credit its common-grid induction, source constants and original authors.

## The exact retained premise

At one genuine external ROW fiber, keep the entire original selected D-bit
root factor, including completed remainders. The retained common-grid
induction represents an ideal row as

    y = sum_nu c_nu U_nu x_nu,

where every U_nu is a Gaussian-dyadic Clifford on that same complete factor.
All source-specific coefficient, unfinished-context, height, mass, input-grid
and root-boundary premises of that induction are retained. In particular this
note does not replace those premises by merely bounding absolute coefficient
values, or admit arbitrary rational coefficients. For the admissible class,
uniformly over its Clifford factors, the established bounds are fractional
bits at most p+D and magnitude bits strictly below h+D+2. The selected format
is F=p+D, signed component width W=p+h+2D+3 and temporary width W+26.

## Closure lemma

Let V_j be any finite prefix of exact elementary Gaussian-dyadic Clifford
gates on an injectively selected subset of the D retained root bits, extended
by identity on the remaining root bits. For a row y satisfying the preceding
invariant, V_j y satisfies the same invariant with the same coefficients,
input rows, height/mass parameters and unfinished exterior-context debt.
Consequently every exact completed prefix V_j y is integral on the same
common grid and fits the same signed W-bit format.

Proof: write

    V_j y = sum_nu c_nu (V_j U_nu) x_nu.

The Gaussian-dyadic Clifford class is closed under multiplication. Extension
by identity and permutation of named root coordinates preserve that class.
No exterior coefficient changes, and no new unfinished *exterior algebraic*
context is opened by absorbing V_j into U_nu. Physical subroutine nesting is
not the numerical debt counted by that invariant. Apply its uniform grid and
magnitude bounds to the new Clifford factors. There is no sum of fresh
per-gate denominator debts here: the existing theorem bounds the complete
Clifford row on the same D-bit factor. This argument does not assume that the
partially completed primitive has returned its final answer. QED.

## Application to the literal native joins

Suppose an actual selected source occurrence already supplies an identified,
packed native view of such a row, on an injective set of 9f root coordinates.
The complementary root coordinates remain in S_native and are not projected
or forgotten; genuine external controls/ROW coordinates remain spectators.
The source-to-packed view is a coordinate reordering, not an arbitrary
isometry or a deletion of axes.

Every complete fixed CNOT, affine X, linear S, quadratic CZ and constant
Gaussian-unit phase is a Clifford on those root coordinates. The central
C=(1/2)[[1+i,1-i],[1-i,1+i]] is H S H and is Gaussian-dyadic; each elementary
C on each column is therefore also in the class. Thus the closure lemma
applies at every mathematical C-prefix of the fixed-rho literal positive
service and of a source-bound monomial/positive/monomial join. The source
constant phase must still be lifted as i^(a f); numerical closure by itself
does not certify the correct source scalar or chronology.

A physical scan can leave a mixture of old and new component positions before
the entire corresponding gate returns. Such a mixed buffer need not be a
Clifford image. That fact is not used: after a numerical component has been fully assembled and committed, its
mathematical value belongs either to the preceding full prefix or to the next
full prefix, both of which satisfy the same bounds. This does not bound a
partially written bit string, an unfinished accumulator, a descriptor or any
scratch representation. Whole-record copies and
permutations preserve those values; unit phases only exchange or negate real
and imaginary components. Temporary arithmetic and its widened scratch must
still satisfy the independently retained helper proofs and complete costs.
This note does not replace those physical proofs with the semantic closure.

The resulting contract is conditional on an *actual row satisfying the
retained root invariant*, together with its correctly produced view/header,
owner, physical scratch, cutoff and all relevant helper promises. Under that
contract the separate assertion that every completed C-prefix is integral
and fits W is redundant: it follows from the retained numerical theorem.
An arbitrary W-bit body on grid 2^-F does not suffice. For example with F=1,
a one-hot numerator1 is on that grid but C produces half-integral numerators;
it need not arise from the required coarse-grid input/root-row class.

## Remaining obligations and scope

An actual producer/view bridge is still required. No header can be invented
from a successful isolated packet test. The cutoff rho*f<=cutoff remains a
separate source-controller obligation, as do paid packing/unpacking, B1
routing, creation/erasure, inherited helper validity and full history. The
closure lemma establishes neither the selected faster nonleaf tariff nor any
complete multiplication bound. All five selected framework assumptions remain.

The selected review already proves the uniform common-grid assertion. The
only proposed use here is to connect that assertion to the newly emitted
literal primitive's exact intermediate numerical contract, while separating
semantic prefix closure from physical mixed-buffer and scratch obligations.

## Review record

The independent algebra role checked the retained source and complete-prefix
closure, and requested the explicit partial-bit/scratch limitation above. Its
review is retained beside this note. Root accepted that correction. This is
disclosed AI review, not blind/human or formal-kernel verification. No new
precision theorem is claimed.
