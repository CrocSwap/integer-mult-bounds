# Exact completion of a rounded band reference

This result is produced by Nick Petalas. Apache-2.0.

## Statement

Let G be an invertible integer N by N matrix with G[i,j]=0 whenever
|i-j|>w, where 0<=w<N. Let A=2^(-ell)G and let d>=0 be the output precision.
There is an exact algorithm returning every entry of

    R[i,j] = floor(2^d A^(-1)[i,j] + 1/2)

using at most

    N^2 + 2Nw + 4Nw^2 + 6N^2w

rational additions, subtractions, multiplications and divisions before
the final scaling and rounding. In particular, the rational work is
O(N^2(w+1)). Rounding adds O(N^2) integer arithmetic operations, whose bit
cost depends on the operand lengths. The algorithm stores O(N^2) rational
entries and retains the complete dense output. It requires no sign,
diagonal-dominance, total-positivity or nonzero-leading-minor hypothesis.

The theorem holds for every finite N. The supplied executable deliberately
limits N to 256 and integer entries and precision parameters to 4096 bits.
These implementation limits are not limits of the algebraic statement.

This is a classical band-elimination method applied to the exact fallback
left dense in Ali Romman's PR5677. Neither band elimination nor rational
Gaussian elimination is claimed as a new general algorithm. The contribution
is the standalone completion routine, its explicit bound and its connection
to that reference's unchanged certificate and signed rounding convention.

## Forward invariant and pivot existence

Apply row operations to [G | I], normalize each chosen pivot to one, and
eliminate only below it. At the start of column k, all earlier pivot columns
are zero in the remaining rows. On the remaining submatrix:

1. Column j has no nonzero entry below row j+w.
2. Row i>=k has no nonzero entry past column max(i+w,k-1+2w).

Both properties hold initially. The first follows from the input band.
For k=0 the second is weaker than the input upper band.

The remaining square submatrix is invertible, since the preceding row
operations are invertible and the upper-left block is unit upper triangular.
Its first column therefore has a nonzero entry. Property 1 places a pivot
in rows k through min(N-1,k+w). Exchange that row with row k, applying the
same exchange to the right half. Property 2 says the pivot row has no entry
past k+2w. Normalizing changes no support.

Only rows k+1 through min(N-1,k+w) need elimination. A newly introduced
entry lies in a column between k+1 and k+2w. Consequently it cannot violate
the lower-band condition, and every changed remaining row obeys the second
bound with the next k. The row exchanges also preserve the lower-band
condition on remaining columns, since their affected row positions are
at most k+w. This proves the two invariants inductively.

The final U is unit upper triangular with upper bandwidth at most 2w.
If the restricted pivot search finds no pivot, the entire remaining first
column is zero, so G is singular. Thus the same method rejects singular
inputs without an additional numerical pivot assumption.

Let E be the product of the row operations. Forward elimination constructs
U=EG and Y=E. Back substitution solves UX=Y, hence X=G^(-1).
It need inspect only the next 2w entries in a row of U, while updating all
N right-hand sides. Invertibility gives XG=GX=I as well.

## Operation count

The implementation counts each executed Fraction division as one rational
operation and each multiply-subtract as two, including operations on zeros.
No assertion, comparison, assignment, pointer exchange, input validation,
integer numerator/denominator rounding, or endpoint test is included in this
rational-operation counter. These are separately bounded finite work.

For N pivots, normalization divides at most 2w upper entries and N right-half
entries. This costs at most 2Nw+N^2 operations. There are at most Nw lower
eliminations, each updating at most 2w upper and N right-half entries with
a multiply-subtract. Their cost is at most 4Nw^2+2N^2w. Back substitution
has at most 2Nw upper entries, each updating N right-hand sides, at cost
4N^2w. Adding these gives the displayed bound. Input validation and fill
diagnostics inspect at most O(N^2) entries; pivot searches inspect at most
N(w+1). All loop bounds are explicit.

Since w<N, this is O(N^2(w+1)); for w>=1 it is O(N^2w). This statement is
an arithmetic bound, not a wall-clock benchmark or a comparison with every
possible dense or structured inversion method.

For polynomial bit bounds, let H bound the bit length of G's entries.
Every forward reduced fraction is a ratio of minors of [G | I], including
the normalized pivot row ratios. Hadamard's bound gives O(N(H+log N)) bits
for their numerators and denominators. In a back-substitution row, upper
entries have a common pivot-minor denominator and completed inverse entries
have denominator dividing det G. Thus partial sums have denominators
dividing the product of those two integers, and the same order of bit
length, including the O(log N) accumulation term. Unreduced products also
have this order of bit length. Final scaling and rounding require a further
O(ell+d) bits. Rational reduction and integer arithmetic remain positive
costs; no fixed-word or multitape speedup follows from the field count.

## Application to PR5677's unchanged acceptance contract

Ali Romman's retained PROOF.md constructs an invertible dyadic reference
A=2^(-ell)G with half-bandwidth w, proves its reference error delta, and
establishes a bound B on the exact Gaussian inverse. Those results are cited
premises. They are not recomputed or independently validated here.

Apply this completion to the same G, ell and output precision d. Since
A^(-1)=2^ell G^(-1), the output integer is computed directly as

    floor((2 x.numerator 2^(ell+d) + x.denominator)
          / (2 x.denominator)),  x=G^(-1)[i,j].

This is exactly the source fallback's nearest-grid rule, with ties toward
positive infinity, including negative ties. Exact inverses are unique, so
the new fallback produces the identical complete R, independent of pivot
choices. Consequently the same A,R,delta,B and precisions enter the source
residual and error predicates. No row, column, norm, accuracy guard or
failure obligation is removed. The source's proof that exact completion
passes those predicates therefore transfers without a new analytic claim.

The source has w=O(sqrt((t+log p)log p)). For w<N the exact completion work
changes from O(N^3) to O(N^2(w+1)) rational operations. Residual formation
can also multiply banded G by dense R in O(N^2(w+1)) integer operations;
the source residual routine already skips zero forward coefficients. Both
absolute row and column sums and the dense output norm still require every
output entry. If the prescribed band covers the entire cell, use w=N-1;
the bound is O(N^3), with no asymptotic gain asserted in that regime.

## Scope and credit

PR5677 by Ali Romman supplies the reference, open structured-completion
question, exact rounding rule and full error contract. JoyboyBrian PR5479
and its retained Gaussian/q-LDU sources supply the analytic lineage.
Dugongue PR4554 already supplies band-factor reuse in a near-identity
periodic inverse model; PR5566 supplies Beatty-run inversion with different
gauges and boundary solves. They retain those results. This application
uses an arbitrary invertible rounded band, including matrices requiring
row exchanges, and does not rely on or replay those scientific executables.
Ali Romman PR5284 already covers fixed-point cyclic-band solves under a
variable positive diagonal-dominance gap; that premise is absent here.
Classical pivoted band elimination and determinant-height bounds retain
their classical status.

The finite checks independently construct general integer bands; they do
not replay the predecessor's Gaussian cells. No original Gaussian cell,
selected scientific replay, native caller, tape implementation, supplier
admission, new kappa, complete multiplication theorem, independent human
review or proof-kernel acceptance is claimed. The source package is unchanged.
