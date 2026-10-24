# Rational size and bit cost of complete inverse-circuit certificates

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
This is a written proof with exact finite corroboration, not proof-kernel or
independent human acceptance.

## 1. Contract and result

Use the complete register grammar of Krzysztof Wójt's
[PR #5262](https://github.com/CrocSwap/integer-mult-bounds/pull/5262), pinned at
`6f92ccf1e61c4668c8ee687bd1df8b42932b8759`. Its code and proof are retained
unchanged in vendor. There are r independent input roles, s named invertible
operators and q unary occurrences across both programs. Put D=r+q. Every
output role is retained. Queries read the old source, including aliases.
Only named-generator inverse relations are imposed.

Coefficients are explicit rational numbers. The executable budget interface
accepts JSON integers and strings of the form signed-integer or
signed-integer/positive-integer. It rejects decimal and exponent strings
before the source parser expands them. Fractions need not be reduced.
Input size counts the original numerators, denominators, instruction and
name encoding. An external conversion from a compressed scalar syntax is
separate work. This restriction does not change the retained source parser.

**Theorem.** On these inputs, the unchanged rational producer and its separate
checker, applied to the produced certificate, take polynomial bit time and
space. Both an equality certificate and a shortest nonzero coefficient word
have polynomial encoding size. Explicit rational-height bounds and a coarse
operation bound are given below. No unit-cost rational-arithmetic assumption
is needed. This closes a stated limitation of the source; weighted-automata
equivalence and determinant bounds are classical.

Python's decimal integer-string limit must be disabled for unrestricted
explicit coefficients. The registered process uses the standard option
`-X int_max_str_digits=0`. This changes neither arithmetic nor source code.
The result is a mathematical complexity bound, not a runtime or optimality
claim. It does not support inverses of sums, additional native relations,
physical tapes, suppliers or a new complete kappa.

## 2. Integer parameters

Reduce each input coefficient c to n_c/d_c with d_c positive. Count each
written coefficient occurrence, including zero and repeated occurrences.
Set Q to the product of all d_c; an empty product is one. For an instruction,
set beta=max(1,sum |n_c|) for a scalar linear assignment, beta=1+|n_c| for
a query, and beta=1 for an apply. Let G be the product of all beta over both
programs. Thus Q,G are positive integers. Define

    R = Q^D,
    K = (1+D G)^D,
    M = 2 D G K R,
    Z = R^(D+1),
    N = D^D M^(D+1),
    Delta = D! N^D.                                         (1)

All these integers have polynomial binary length in the explicit input.
They are proof quantities; the budget calculator returns logarithmic bounds
and does not allocate N, Z or Delta.

For a rational x in lowest terms, its height is the maximum binary length of
its numerator's absolute value and positive denominator. Zero has height one.
The calculator uses integer bit_length as a strict upper bound on log2 for
positive integers. With bD=bit_length(D), bQ=bit_length(Q), bG=bit_length(G),
it returns

    bM = 1+bD+bG+D(1+bD+bG)+D bQ,
    bN = D bD+(D+1)bM+1,
    bDelta = D(bD+bN)+1,
    bCoeff = (D+1)bD+(D+2)bM+1.                             (2)

These bound, respectively, model entries, candidate path rows, stored
normalized rows and coordinates, and nonzero projected coefficients.
They are sufficient bounds, not minimal lengths.

## 3. Scalar compilation and the common denominator

The source represents each register by a row in r+q atoms. A unary call adds
one atom. A scalar instruction takes a linear combination of prior rows;
an apply replaces a row by a unit row; a query adds one coefficient times a
new unit row. Induction with the instruction beta factors bounds each
register or dependency row's absolute row sum by G. A final difference row
has absolute row sum at most 2G. In each scalar dependency path, a written
coefficient occurrence is used at most once. Therefore every denominator
in the dependency rows and final rows divides Q. Sums preserve divisibility
by this common denominator. This argument allows repeated source terms and
self-source assignments.

Use the source proof's strictly lower triangular dependency matrix E and
unary matrices A_a. Entries of E and A_a have magnitude at most G and
denominator dividing Q; inverse feedback contributes the integer -1.
The constant solve and compiled model are

    H=(I-E)^(-1)=I+E+...+E^(D-1),
    V=H V0,    T_a=H A_a,    U=left_final-right_final.

Each H entry has magnitude at most sum_(j=0)^(D-1)(DG)^j <= K and denominator
dividing Q^(D-1). It follows that all U,T_a,V entries have denominator
dividing R. Their magnitudes are at most max(2G,DKG,K). Thus RU,RT_a,RV are
integer matrices with entries of magnitude at most M. This also covers
intermediate completed rows of the source's triangular recurrence. No
Gaussian elimination or inverse of a matrix with variable entries occurs
in this compilation step.

The independent checker constructs E,H and A_a separately. The same bounds
apply to that reconstruction. The new audit compares both models and checks
the common denominator by exact modular powers; it does not replace either
compiler.

## 4. Path rows and output coefficients

The breadth-first search accepts at most D independent path rows U_o T_w.
Their lengths are less than D. Every candidate successor has length at most
D. These are the source's reachability facts; they are not new shortest-word
claims. A length-k row has denominator dividing R^(k+1). After scaling all
candidate rows by Z, it is integral with entries bounded by

    R^(D-k) D^k M^(k+1) <= D^D M^(D+1) = N,    0<=k<=D.    (3)

Here M>=R. Hence each reduced path-row numerator and denominator is at most
N, since Z<=N. This proves the bN bound.

A projected coefficient U_o T_w V_i uses one more matrix. Its common
denominator and integer numerator are bounded by

    R^(k+2),    D^(k+1) M^(k+2).

The bCoeff bound in (2) is sufficient for every accepted path and the emitted
nonzero coefficient. Infinite inverse-series tails do not change these
finite path lengths. No expansion of all words is required.

## 5. Exact elimination does not hide exponential bit growth

Scale every accepted and candidate path row by the same Z. Each integer
entry now has magnitude at most N. Consider the first j independent rows
and their chosen pivot columns, in the order used by the source. Their
j by j integer pivot matrix P_j has nonzero determinant. Every minor of
size at most D is bounded in absolute value by Delta, by the permutation
formula for a determinant. Pivot columns need not be in increasing order.

For a candidate row z/Z, elimination against these j rows solves the pivot
coordinates by Cramer's rule:

    removed = z[pivots] P_j^(-1).

Its numerators and denominator are j by j determinants, bounded by Delta.
For j<D, each remaining residual coordinate is a bordered determinant of
size j+1 divided by Z det(P_j). Thus the residual has numerator at most
Delta and denominator at most Z Delta. At j=D the residual is zero.
This also describes every completed prefix of the reduction loop.

On acceptance, the normalized echelon row is a ratio of two bordered
minors. Its coordinates in the original rational path rows are Z times
cofactors divided by the new pivot determinant. For j+1<=D,

    Z j! N^j <= (j+1)! N^(j+1) <= Delta.

Consequently every stored normalized entry and every stored original-row
coordinate has numerator and denominator at most Delta. The source's
`removed` and `coordinates` arrays have the same bounds. This proves bDelta
in (2) for the entire source basis routine, including near dependencies.
It also bounds the equality certificate's initial and transition-closure
coordinates, because their target rows are among the length-at-most-D rows
already covered by (3).

Small matrix entries alone would not prove this claim. For the rows (1,1)
and (1,1+1/L), the coordinates of (0,1) are (-L,L). The finite check uses
L=2^1024+1 and obtains 1,025-bit coordinates. The determinant argument pays
this amplification explicitly.

## 6. Primitive arithmetic and total bit work

Let h0 be the largest binary length of an original, possibly unreduced,
input numerator or denominator. Let ell be the largest number of scalar
terms in one assignment and L=max(2,D,ell). The calculator supplies

    B = 8(L+D+1)(h0+bM+bN+bDelta+1).                         (4)

This bounds primitive integer temporaries as well as completed rational
values. To check this, compilation uses bounded scalar rows and triangular
sums from Section 3. Search and checking use products and sums of at most
D entries with the heights in Sections 4-5. An unreduced product adds the
operand bit lengths. A sum of at most L such fractions can use their product
as a denominator, so its bit length is at most L times the sum of the operand
bounds, plus a carry bound. A reduction step uses two such products and a
sum. The larger residual bound is bN+bDelta. Normalization divides two
bounded rationals. Formula (4) exceeds each of these bounds. Rational
arithmetic reduces after each operation; it does not accumulate an unevaluated
product of all historical denominators. Raw scalar parsing uses h0, not only
the reduced coefficient height.

Let m be the number of instructions and t the number of written scalar
terms in both programs. A sufficient combined producer/checker bound on
rational elementary operations is

    F = 256(m+t+r+s+1)(D+1)^4.                              (5)

For clarity, the terms behind this loose bound are scalar compilation
O(tD+(s+1)D^3), at most r+sD candidate reductions of O(D^2) operations,
O(sD^3+rD^2) closure coordinates, and reconstruction of at most D paths
of length less than D in O(D^4) operations. The independent compiler and
finite certificate equations fit the same bound. Initialization, indexing,
name processing and input parsing are polynomial in the explicit encoding
size and these dimensions. The constant 256 exceeds the elementary
addition, multiplication, division and sign operations in these loops.

Classical integer multiplication, division and gcd on B-bit operands take
at most O(B^3) bit operations. Hence O(F B^3) plus polynomial input-parsing
work is a sufficient bit-time bound. O(F B) plus input storage is a sufficient
space bound. The output has at most rD+sD^2 rational coordinates and D^2
path labels, or one word of length less than D and one rational coefficient.
Its encoding is polynomial. The independent checker is bounded here on
produced certificates; arbitrary external certificates carry their own
input-size cost and must pass its existing schema and path checks.

## 7. Consumer effect and limits

The source already proves universal equality or provides a shortest
nonzero word. This result adds a rational bit-size bound to that producer;
it does not supply a new equivalence algorithm or faster implementation.
It removes the upstream representation-size qualification before that word
can enter the conditioned-witness and finite-precision interfaces.

In the orthogonal construction of
[PR #5315](https://github.com/CrocSwap/integer-mult-bounds/pull/5315), d<=D,
the grid has dq+1 points, and a rational cap a/b gives grid denominators at
most b(dq+1). Its Cayley matrices have integer determinant bounds of
polynomial binary length. The scalar operations, grid trials and exact
matrix replays therefore also have polynomial bit cost by the same minor
argument. The funded detector of
[PR #5339](https://github.com/CrocSwap/integer-mult-bounds/pull/5339) already
has a polynomial bound after the word is given. The present theorem closes
the producer part of that composition. The prior orthogonal and numerical
proofs are consumed for this corollary; their full replays are not rerun here.

These bounds can be very conservative. They are not practical resource
predictions or optimal guards. No finite native alphabet, extra relation,
rectangular type, phase, storage tariff, selected cold replay, physical
implementation or complete kappa calculation follows. The selected frontier
is unchanged. A native adapter still needs one pinned complete caller and
all of its additional contracts.

## Verification and attribution

The exact audit checks both compiled models, their common denominators,
all candidate and accepted rows in a complete reachable-basis traversal,
stored echelon coordinates, their exact original-row reconstruction, reduction
results and the unchanged producer's
certificate. The independent source checker checks that certificate. Small
programs also use separate reduced-group-word and literal invertible-matrix
oracles. The mathematical proof, rather than the finite corpus, supplies
the all-input bounds and primitive-temporary claim.

Krzysztof Wójt supplied the inverse compiler, basis routine, independent
checker, oracles and shortest-word theorem. The retained source credits
zxv's [PR #5235](https://github.com/CrocSwap/integer-mult-bounds/pull/5235),
the dirty-echo/tensor/phase lineage, and classical Magnus, rational-series
and weighted-automata theory. Cramer's rule, determinant height bounds and
polynomial exact linear algebra are classical. Ali Romman's #5315 and #5339
supply the downstream witness and precision proofs. No global literature
priority or independent scientific acceptance is claimed.
