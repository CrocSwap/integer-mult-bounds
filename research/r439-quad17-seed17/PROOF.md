# Fixed-transfer minimum and sharp restoration envelope

Let `E_ds = I + e_ds` on the six labelled registers, `d != s`. An elementary
positive ADD is left multiplication by `E_ds`. Let T be the exact matrix in
README and CERTIFICATE, extracted from the pinned PR952 frame283 program.

## All-length positive-ADD minimum

Every product of positive ADD matrices is entrywise at least I, and all its
entries are nonnegative integers. If a nonempty program has last gate `(d,s)`,
then `T = E_ds P`. Removing that gate subtracts row s from row d, giving P.
Every possible last gate is among the 30 ordered distinct pairs. Retain a
pair exactly when the residual matrix is entrywise at least I. Conversely,
any retained path from T to I supplies a positive program by reversing the
peeled gates. This remains valid when a retained residual has no path to I;
such a state is a dead end, not an accepted factorization.

Each edge strictly decreases the entry sum, since the subtracted source row
has a diagonal entry at least one. Starting with sum(T)=36, all paths have
length at most 30, and the finite graph contains every positive program of
any length. Requiring diagonal entries at least one never discards a valid
positive prefix. There are no arbitrary entry-size or program-length cutoffs.

For each residual M, define `D(I)=0`, and `D(M)=1+min D(P)` over its retained
row-subtraction children; an empty minimum is infinity. This acyclic Bellman
recurrence is exact by the last-gate bijection. The complete graph has 9,739
states and 43,454 edges, with D(T)=12. The pinned parent has 12 gates, so both
the lower bound and its attainment are checked. The finite search is exact
evidence for this explicitly fixed class, not a multiplication theorem.

An independent BFS removes the first gate instead. If `T = Q E_ds`, right
multiplication by `I-e_ds` subtracts column d from column s. It exhausts that
entire graph using contiguous column states, queue distances and path counts.
It also obtains minimum 12 and 1,008,032 shortest ordered programs. Discovery
uses last-gate memoized distances; the independent implementation imports no
discovery code. Equal graph totals here are observations, not an assumption
used to identify the two graphs.

The shortest count is the number of gate sequences, not the number of distinct
linear operators. For row discovery, propagate multiplicities along exactly
the edges with `D(P)=D(M)-1`. Track a second matrix by positive row addition in
peeled order. That is the positive majorant of literal signed inverse cleanup.
The independent implementation uses its own column graph and right-product
column addition. Their complete endpoint lists and multiplicities agree:
57 different reverse matrices, and 767,232 programs attaining the parent's B.
The sole entrywise Pareto minimum is B. This census is supplementary; the next
argument establishes the envelope floor without restricting program length.

## Universal independent-coordinate inverse envelope

Exact rational elimination gives the following integral inverse, with both
`T T^-1 = I` and `T^-1 T = I` checked:

```text
T^-1 = [ 3  3 -1 -1 -1  0]
       [ 3  3  0 -1 -1 -1]
       [ 0 -1  1  0  0  0]
       [-1 -1  0  1  0  0]
       [-1 -1  0  0  1  0]
       [-1  0  0  0  0  1]
```

Quantify over every nonnegative budget vector u and every independent input
vector y satisfying `|y_j| <= u_j`. In row i, the triangle inequality gives

`|(T^-1 y)_i| <= sum_j |(T^-1)_ij| u_j`.

This bound is attained: choose `y_j` to have the sign of `(T^-1)_ij` and
magnitude `u_j`. The choice can depend on i; simultaneous attainment of all
rows is unnecessary for a coordinatewise envelope. Hence the least valid
envelope matrix is exactly `|T^-1|`. Equivalently, choosing u to be each unit
vector forces every valid matrix B' to satisfy `B'_ij >= |(T^-1)_ij|`.

The parent's literal inverse uses the signed negatives of its 12 ADDs in
reverse order. Replacing those negative gates by positive additions, as in
the standard independent-coordinate majorant, gives exactly `B=|T^-1|`.
Thus its reverse endpoint envelope is optimal for **every** nonnegative u,
including nonuniform budgets. Its largest row sum is nine; the common-budget
bound cannot be reduced either. This algebraic conclusion covers any exact
realization of the same inverse with a universally valid independent-coordinate
endpoint bound. It does not say that every intermediate prefix or every bound
exploiting full-word input correlations has the same optimum.

## Cost and exclusions

In the fixed six-register positive class, at least 12 forward ADDs are needed.
Mandatory literal inverse cleanup has one signed ADD per forward gate, so the
pair costs at least 24 ADDs, attained by the existing word. No additional
source access, helper, frame, copy or recursive child is part of this local
class. No globally hosted supplier or paid-profile improvement is proposed.

Changing the integer lift can preserve the F2 map while escaping this graph.
Signed forward ADDs, extra workspaces and changed interfaces escape its gate
minimum as well. The inverse envelope remains an endpoint statement for the
particular fixed T and independent budgets. These restrictions are essential.
The package neither prices those extensions nor rules out useful improvements
through them, and does not change the selected conditional multiplication bound.
