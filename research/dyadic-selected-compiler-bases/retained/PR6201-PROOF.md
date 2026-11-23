# Intrinsic primes for the ordered shear factorization

This scoped proof was produced by Nick Petalas. Classical Bruhat elimination,
rank profiles and determinantal divisors are background. The contribution is
their precise prime-admissibility consequence for the retained ordered shear
compiler, including the sharp finite-width obstruction below.

## Contract

Let A be an integer m by m matrix. A northeast block A[i,j] consists of rows
1 through i and columns j through m. Let r[i,j] be its rational rank. A partial
permutation has only zero and one entries, at most one one in each row and
column. Write Z_(q) for rational numbers with denominator coprime to the prime q.

The retained source `upstream/build/sections/04-swap.tex`, lemmas
`lower-lower` and `matrix-shear`, factors A as L P R with invertible lower
triangular rational L and R. Its physical order makes both triangular factors
lower. Its sufficient prime choice avoids factor denominators and nonunit
diagonals. This proof does not change that cost theorem or its physical leaves.
The source independently requires q to be odd. That requirement is retained;
the algebraic theorem below also applies at 2, which supplies small test cases.

The rational partial permutation P is unique. Indeed, left lower and right
lower multiplication preserve every northeast rank. For a partial permutation,
that rank is its number of ones in the block. The mixed differences

    P[i,j] = r[i,j] - r[i-1,j] - r[i,j+1] + r[i-1,j+1]

recover all its entries, using zero ranks at the empty boundaries. Existence
comes from the credited rational ordered elimination in the source.

## The admissible-prime theorem

The following conditions are equivalent.

1. A=L P R for invertible lower triangular L,R over Z_(q).
2. Every northeast block has the same rank over F_q as over Q.
3. q divides none of the top determinantal divisors of the northeast blocks.

For a nonzero integer block of rational rank r, its top determinantal divisor
is the positive gcd of all its r by r minors. For a zero block set it to one.
Thus the exact forbidden-prime set is the prime support of the product of
these finitely many positive divisors. No factor table is needed to define it.

The good factors specialize to every Z/q^b Z, b>=1, with the same P and
invertible lower factors. Conversely even a factorization at b=1 with that
same rational P forces condition 2. A rational input has the same criterion
after multiplication by a common denominator coprime to q. Primes dividing
that chosen denominator are outside this specialization statement.

### Necessity

If B=L A R with lower invertible L,R over a field, then

    B[i,j] = L[1:i,1:i] A[i,j] R[j:m,j:m].

Both square factors are invertible. This identity also holds after reducing
invertible lower factors over Z_(q) modulo q. Therefore the northeast ranks
of A over Q and F_q both equal the corresponding counts of ones of P.

### Sufficiency

Run the source's ordered elimination over Q. In the still active rows, choose
the topmost nonzero row, and in that row the rightmost nonzero active column.
Call their entry u. Use its column to clear the entries to its left, its row
to clear the entries below it, normalize u to one, and remove its row and
column from the active sets. The transformations are lower triangular in the
original physical order. Previous isolated pivot rows and columns stay isolated.

Inductively suppose all previous operations and their inverses are defined
over Z_(q), with unit diagonal. They preserve the equality of every northeast
rank over Q and F_q. The transformed matrix is the direct sum, after merely
grouping indices for this argument, of its isolated pivot entries and its
active submatrix. In any northeast block, isolated pivots contribute their
number to rank, independently of the active block. Subtracting these identical
contributions shows that all northeast ranks of the active submatrix still
agree over the two fields. Active indices retain their original orders.

For the chosen u, take the active northeast block ending at its row and
starting at its column. It contains just that one possibly nonzero entry:
earlier active rows are zero, and entries to its right in that row are zero.
Its rational rank is one. Its residue-field rank must also be one. Thus u
has nonzero reduction and is a unit in Z_(q). Dividing by u, clearing and
normalizing consequently use only invertible lower operations over Z_(q).
This proves the induction. There are at most m pivots; the final identity is
X A Y=P over Z_(q). Taking L=X^-1 and R=Y^-1 proves condition 1.

### Determinantal divisors

Reduction cannot increase the rational rank of an integer matrix: all larger
minors are already zero over Z. Its residue-field rank is r precisely when
some r by r minor is nonzero modulo q. This holds precisely when q does not
divide the gcd of those minors. This proves the equivalence with condition 3,
including the zero-block convention. No assertion about the size of the least
admissible prime or the complexity of a full selected compiler is made.

## Sharp first failure at a prime-power width

For N>0 put

    A_N = [[1,N],[0,0]],       B_N = [[1,N],[0,1]].

Their total rank is respectively one and two over Q and over every F_q.
Moreover det B_N=1. Their rational northeast profiles nevertheless change
at every prime dividing N, since the top-right one-entry block has rank one
over Q and zero over F_q. Thus even determinant one does not certify this ordered factorization.

Here is the exact finite-ring version, allowing ANY partial permutation and
factors chosen separately for each b. In Z/q^b Z either family admits L P R
with lower invertible L,R if and only if N is zero or a unit in that ring.
If q divides N and v=v_q(N), the first failing width is exactly v+1.

To prove necessity, the first row of L is (ell,0), with ell a unit.
The first row of A_N or B_N is (1,N), so P has a one in its first row.
If that one is in column 1, the first row of L P R has second entry zero.
If it is in column 2, its second entry is ell times the unit R[2,2].
Thus a nonzero nonunit N is impossible. This reasoning allows all seven
two-dimensional partial permutations, not only the rational one.

If N=0 in the ring, the matrices themselves are respectively E_11 and I.
If N is a unit, set

    X = [[1/N,0],[-d/N,1]],    Y = [[1,0],[-1/N,1]],

where d=0 for A_N and d=1 for B_N. Direct multiplication gives

    X [[1,N],[0,d]] Y = [[0,1],[-d/N,0]].

For d=0 this is already E_12. For d=1, multiply the second row by -N to
obtain the swap permutation. All operations are lower invertible. This proves
sufficiency. When q divides N, N is zero modulo q^b exactly for b<=v and
is a nonzero nonunit for b>v, proving the sharp width threshold.

For example both [[1,3],[0,0]] and [[1,3],[0,1]] admit an ordered factorization
modulo 3 and admit none modulo 9. The second matrix has determinant one at
both widths. A width-one rank check cannot establish a uniform ordered lift.

## What this changes

The source's finite factor-table avoidance remains sufficient. This result
provides its factorization-independent admissibility boundary, and identifies
why total-rank-only specialization is too weak. It does not allege that an
existing source or contributor used that weaker test. The failure excludes
this lower/partial-permutation/lower route, not every implementation of the
same shear at the same recursive-call cost. Native gates, ordered affine
streams, dirty restoration, fixed tapes, the complete compiler and its five
selected framework assumptions remain separate obligations.

commdata2338's PR2160 already treats a unit-pivot generic local-ring branch
and warns against interpreting residue-zero entries as zero at higher width.
That distinction is credited context. This package adds the intrinsic
all-northeast-block criterion and the exact first failing width for the two
displayed families; it does not recheck that package's selected residual.

The universal conclusions above use the written proof. The finite checker
corroborates them using rational elimination, independent minor expansions,
modular elimination, and exhaustive finite-ring factor enumeration. None is
an independent human review or a formal proof-kernel certificate.
