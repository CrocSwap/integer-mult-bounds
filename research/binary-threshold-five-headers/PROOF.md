# The five-request threshold is not row/column rigid

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement

Let U_1,...,U_5 be pairwise orthogonal rank-one idempotents on F_2^6.
Set P_t = I - U_t. Give every complete header G in GL_6(F_2) equal weight.
A header passes P_t when every leading principal minor of G P_t G^-1
of orders 1,...,5 is nonzero.

There are exactly 2,880 headers passing all five requests, a fraction
1/6,999,552 of GL_6(F_2). The exact count is a finite certificate supplied
by the exhaustive enumerator. The algebraic reduction and the explicit
counterexample below are scoped proofs. No all-k count is asserted.

This answers Open next question 1 of
[#4275](https://github.com/CrocSwap/integer-mult-bounds/pull/4275)
negatively. Its observations at k = 3,4 suggested 2 k! passing headers at
m = k+1. At k = 5 there are 24 unordered decompositions, giving
24*5! = 2,880 headers instead of 2*5! = 240.

## The header/decomposition bijection

We use the partial-Gram reduction and binary threshold argument of #4275,
produced by Nick Petalas. The following specialization makes the finite
certificate self-contained. Pairwise orthogonality permits one fixed basis
change taking U_t to e_t e_t^T. This change permutes the complete header
domain, so it preserves the count.

Let X be the first five columns of G and Y the first five rows of G^-1.
Then YX = I_5. Write x_i for row i of X, y_i for column i of Y, and
A_j = sum_(i<=j) y_i x_i. The determinant identity gives

```text
det((G P_t G^-1)[1..j,1..j]) = 1 - (A_j)_tt.
```

Over F_2 every guard passes precisely when every A_j has zero diagonal
for j = 1,...,5. Consequently each of the first five increments has zero
diagonal, and its factors have disjoint supports S_i and T_i. Since
A_6 = I_5, the last increment has all diagonal entries one. A binary
rank-one matrix with unit diagonal has both factors equal to the all-ones
vector, so it is J. Thus

```text
sum_(i=1)^5 1_(S_i) 1_(T_i)^T = J - I_5,
S_i intersect T_i = empty.
```

Conversely any such ordered decomposition defines X and Y by those factors
in their first five coordinates and by all ones in coordinate six. Their
product is YX = (J-I)+J = I. Hence both have rank five. The one-dimensional
kernel of Y has a unique nonzero vector z. The matrix G = [X,z] is
invertible, and its inverse has first five rows Y. This gives exactly one
header per ordered decomposition. Its full guard chain passes because all
five intermediate diagonals vanish. These constructions are inverse.

## Why only distinct nonzero rectangles need enumeration

Write E = J-I_5. It has rank four and E^2 = E over F_2. Suppose it were the
sum of n <= 4 disjoint-support rank-one matrices, E = BC, with B having n
columns and C having n rows. Rank forces n = 4, B injective and C
surjective. Idempotence gives B(CB-I)C = 0, so CB = I_4. But every diagonal
entry of CB is the scalar product of a disjoint-support pair, hence zero.
This contradicts CB = I_4.

A zero increment in a five-term decomposition would leave at most four
nonzero terms. A repeated rectangle cancels in characteristic two and
would leave at most three terms. Both are impossible. Every decomposition
therefore consists of five distinct nonzero rectangles, in any order.
There are

```text
3^5 - 2*2^5 + 1 = 180
```

possible nonzero rectangles with disjoint supports. A nonzero binary
rectangle has a unique support pair, so distinct support pairs are distinct
matrices.

## Exhaustive certificate and its coverage

The verifier encodes a 5 by 5 binary matrix as a 25-bit integer, with cell
(i,j) at bit 5*i+j, using zero-based indices. Matrix addition is XOR.
It lists all 180 support pairs in increasing order of S, then T.

For every pair of distinct indices a<b it stores the pair and the XOR of
its rectangles. There are 16,110 pairs. For every triple c<d<e, of which
there are 955,860, it looks up the complementary XOR needed to reach E.
It retains a match exactly when b<c.

Every five-element subset has exactly one split into its first two and
last three indices. Thus the strict inequality counts every admissible
subset once and excludes repeated indices. Every match has XOR E by
construction. The exhaustive run finds 24 subsets, and prints every one
as five integer support-mask pairs. Each has 120 distinct orderings.

The verifier constructs all 2,880 corresponding complete matrices G,
inverts each, forms all five full conjugated request matrices by generic
binary matrix multiplication, and checks every full guard chain by literal
no-pivot elimination. It also checks that all 2,880 headers are distinct.
It does not enumerate all of GL_6. Exhaustiveness follows from the
bijection and the exhaustive five-subset enumeration, rather than from a
sampling argument.

Finally,

```text
|GL_6(F_2)| = product_(i=0)^5 (64-2^i) = 20,158,709,760,
2880 / 20,158,709,760 = 1 / 6,999,552.
```

## A counterexample that can be checked by hand

Use one-based coordinate labels in this display:

```text
S             T
{1,2}         {3,4}
{2,3}         {1,5}
{1,4}         {2,5}
{3,5}         {2,4}
{4,5}         {1,3}
```

Each rectangle avoids the diagonal. In each row their column supports
partition the other four coordinates, so their sum is exactly J-I_5,
even before reducing modulo two. Every source and target support has size
two, so this is neither a row-star nor a column-star decomposition. In
least-significant-bit support notation, it is

```text
(3,12), (6,17), (9,18), (20,10), (24,5).
```

The verifier prints its literal 6 by 6 passing header and requires this
specific decomposition to occur in the exhaustive list. Only two of the
24 subsets are the row-star and column-star subsets. The other 22 produce
2,640 additional headers.

## Limits

The exact count is for five requests in dimension six over F_2, with the
complete equally weighted GL header domain and fixed orthogonal kernel
lines. No count at k >= 6, arbitrary nonorthogonal kernels, odd fields or
restricted header families follows. The explicit counterexample refutes
the proposed all-k pattern. It does not alter any theorem proved in #4275.

Header generation, selection, emission, dispatch, dirty restoration,
stock, precision and the full physical caller remain unpriced. Binary
algebra alone does not enter an odd-prime executable normalizer. There is
no supplier admission, selected-frontier change, new kappa or complete
multiplication theorem here. Independent human and formal proof-kernel
review are unclaimed.
