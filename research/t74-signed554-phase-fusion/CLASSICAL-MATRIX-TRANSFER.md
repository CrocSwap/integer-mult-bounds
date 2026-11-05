# Established matrix exponent suffices for the faster boundary variant

## Proposition and dependency

Assume the inherited supplier, compiler, precision/tape, exact-recovery and
analytic hypotheses of PR1673. Its matrix-boundary construction can use the
established square-matrix exponent theorem with a fixed target exponent
**tau=12/5**, rather than the additional omega_C<=9/4 premise. With the
signed-554 T74 supplier and parameters in COMPOSITION.md it gives the
conditional saving 0.001677641731343354.

The external mathematical input is Francois Le Gall,
[Powers of Tensors and Fast Matrix Multiplication](https://arxiv.org/html/1401.7714v1),
ISSAC 2014, pp. 296-303, DOI 10.1145/2608628.2627493. Its Table 1 and Section
6.3 give omega<2.3728639; Section 2 specifies the field setting, including C.
Only the weaker consequence omega_C<12/5 is used. The paper is cited as an
established theorem. This package does not independently re-prove its optimization.
`outer/PUBLISHED-THEOREM-SOURCE.json` records the exact version, inspected
sections and hash of a privately cached HTML copy; the paper is not redistributed.

The relevant predecessor is PR1673 head
d449b822c8a74ffa01b22058cfc042374b1a45cd, preserved under vendor/pr1673.
Its ALGEBRAIC-STABILITY-INDEPENDENT.md begins with the general hypothesis
omega_C<tau; the later 9/4-to-19/8 example is one specialization.
Its PHASE-LAYOUT-AUDIT.md and MATRIX-LAYOUT-SIGNOFF.md provide the sparse
union schedule. The proof below explains the changed specialization explicitly.

## A fixed computable bilinear formula

Choose rational sigma with 2.3728639<sigma<12/5. The exponent definition
and bilinearization imply the existence of fixed integers m>=2 and R with
an exact rank-R formula for m-square multiplication and R<m^sigma. Any
constant overhead in bilinearizing an arithmetic circuit is absorbed by
first choosing its exponent below sigma and then choosing sufficiently large
fixed m. This uses strict slack, and never asserts that an exponent infimum
is attained by a finite formula.

The rank equations are finitely many polynomial equations over Z. A complex
solution can be replaced by one over Qbar: otherwise the weak Nullstellensatz
over Qbar would express 1 in their ideal and yield the same contradiction
over C. Enumerate finite algebraic tuples with isolating descriptions and
check these equations exactly, dovetailing over m and R. The search halts
by the cited existence statement. Its entire description and search cost
are fixed independently of the growing input. It is not a practical algorithm
for discovering competitive constants, and no finite rank tuple is claimed
as generated in this contribution.

## Bit precision, stability and tape work

Fix that one formula. Its coefficients have fixed degree, height and root
separation. Approximate their chosen algebraic embeddings once using
precision-doubling Newton iteration; this costs O(M(P')) for P' bits with
formula-dependent constants.

Recursive block multiplication obeys T(N)<=R T(N/m)+O(N^2) arithmetic work.
At each node the fixed number of linear combinations and output accumulations
can be formed by complete block scans. Depth-first evaluation, fixed block
permutations and tape repositioning add O(N^2) work per node up to logarithms.
Choose the finite formula strictly below the target tau so these logarithms
are absorbed. Padding the current square matrix to the next m-power changes
its size by a fixed factor; it does not pad any tensor axis or coarse-label range.

For a fixed bilinear recursion, an absolute roundoff envelope satisfies
E_j<=K E_(j-1)+K m^(j-1), with K fixed by the chosen formula. Thus E_j is
polynomial in N. Input magnitudes at most 2^h require fractional precision
P+2h+O(log N) to achieve absolute output error 2^-P. Intermediate magnitudes
are N^O(1) max(1,2^(2h)), so total record width is O(P+h+log N). The bound
is absolute, including cancellation; no relative-error condition is assumed.
Consequently a W-square product costs O(W^(12/5) M(P+h+log W)). At the
retained boundary interface P,h=O(p), W=O(sqrt(p) polylog p), this is
O(W^(12/5) M(p)), with O(p)-bit records and the same polynomial residual
envelope used by PR1673's no-pivot boundary updates. A larger fixed guard
constant absorbs the formula-dependent stability constants.

## Boundary normalization and the paid union schedule

The retained boundary calculation processes W right-hand sides per square
block product. There are O(V W/B) boundary bit positions per axis and d axes.
A product handles W^2 scalar entries. Since each entry occupies Theta(p)
bits, the total is

    O(V (d/B) W^(tau-1) [M(p)/p] polylog p).

The retained short multiplier gives M(p)/p=polylog p. With d=p^epsilon,
B=p^xi and W=p^(1/2) polylog p, the boundary power is

    epsilon - xi + (tau-1)/2 = epsilon - xi + 7/10.

Its saving is 3/10+xi-epsilon. This row is safely above the binding main
saving at the chosen parameters. The Gaussian matrix, factor pages, local
norm bounds and completed operator interface do not change.

The larger group uses the same union routine already proved in PR1673.
For each axis i, E_i contains its boundary and all interior coordinates
incident to the original sparse off-diagonal factors. The sparse factors
fix E_i's complement and preserve U={x: some x_i is in E_i}. Each
U_i=E_i x [L]^(g-1) is a complete rectangle inside U. Scan U, extract U_i
in order, rename its E_i coordinate by a counter, transpose only that
polynomial-size field, perform its boundary operation, undo that transpose,
and merge in original order. No full union-key sort occurs. Dense interior
stages use separate gather/scatter windows; the union is not falsely claimed
to remain invariant under those dense stages.

The costs across groups are the paid group scans, sparse-union movement,
boundary arithmetic, dense compiler/router and separate sparse microhalo
corrections. Membership fits the p-bit record because beta+2(1-epsilon)<1;
union density decays because xi-beta-1/2>0. Support completeness and the
original global q-image/gather ordering are retained. Adding a full-key sort
to this union is an explicit rejecting control; its omission follows from
the rectangle schedule, not from a matrix-exponent assertion.

## Review boundary

The contribution substitutes an established exponent into an already general
transfer lemma and checks its full cost ledger. It neither certifies the
published exponent from scratch nor constructs a practical finite matrix
scheme. All inherited all-size assumptions and the written Gaussian/layout
proof remain necessary. Finite tensor or arithmetic tests cannot by themselves
prove this asymptotic argument.
