# Cube-generated relations can miss a parity class at rank four

This result was produced by Nick Petalas. Apache-2.0.

## Statement

For a rational subspace V of Q^n, set L = V intersect Z^n. This is its
saturated integral lattice. A cube vector has every coordinate in
{-1,0,1}. A cube parity basis means cube vectors whose reductions form a
basis of L/2L.

There is a rank-four example in Z^10 for which:

1. The cube vectors span V over Q.
2. There are exactly eight nonzero cube vectors.
3. Their integral span has index two in L, and their reductions span only
   a three-dimensional subspace of the four-dimensional space L/2L.
4. Every representative of the missing coset has maximum absolute
   coordinate at least two. This bound is attained.

Consequently, rational generation by cube relations does not imply a cube
parity basis at rank four. The rank-three parity-basis argument already in
Ali Romman's three-register proof cannot extend to arbitrary relation rank.
The example does not assert minimality of the ambient dimension ten.

## The explicit matrix

Let B be the following four-by-ten integer matrix, with rows r_1,...,r_4:

```text
  1  1  1  1  1  1  1  1 | 1 1
  1  1  1  1 -1 -1 -1 -1 | 1 0
  1  1 -1 -1  1  1 -1 -1 | 0 1
  1 -1  1 -1  1 -1  1 -1 | 0 0
```

Its first eight columns are one representative of every antipodal pair
of sign vectors in {+1,-1}^4, chosen with first coordinate +1. Its last
two columns are e_1+e_2 and e_1+e_3. Put

    V = {qB : q in Q^4},
    h = (r_1+r_2+r_3+r_4)/2
      = (2,1,1,0,1,0,0,-1,1,1).

The first eight columns have row Gram matrix 8I_4. In particular B has
rank four, and q is a unique coordinate vector for qB in V.

## Determine the whole lattice

We claim

    {q in Q^4 : qB in Z^10}
       = Z^4 union ((1/2,1/2,1/2,1/2)+Z^4).             (1)

Suppose qB is integral. Subtracting two sign-column evaluations differing
only at coordinate i shows that 2q_i is integral for i=2,3,4. The
all-positive evaluation is integral, so 2q_1 is integral too. Write
a_i=2q_i in Z. The all-positive column and last two columns give

    a_1+a_2+a_3+a_4 = 0 mod 2,
    a_1+a_2 = 0 mod 2,
    a_1+a_3 = 0 mod 2.

These equations force all four a_i to have the same parity. Hence q is
either entirely integral or entirely half-integral with odd numerators.
Conversely, both alternatives make every sign-column evaluation integral,
because each such column has four odd entries. They also make the last
two evaluations integral. This proves (1).

Under the injection q -> qB, the integral row span M corresponds to Z^4,
while h corresponds to (1/2,1/2,1/2,1/2). Thus

    L = M + Zh,       L/M is Z/2Z,       2h = sum_i r_i. (2)

The four vectors r_1,r_2,r_3,h are an integral basis of L: they generate
r_4 by the last equation and generate both cosets in (1). Independence
follows from their nonzero determinant in the q coordinates. This proves
the saturation and index claims without a finite search.

## Determine every cube vector and the missing-class height

For every real q, the first eight column evaluations obey

    max_(j<8) |(qB)_j| = |q_1|+|q_2|+|q_3|+|q_4|.     (3)

Indeed, allowing the absolute value supplies both signs of every column,
so these evaluations cover all sixteen sign vectors. Choosing each sign
to match the corresponding q_i attains the triangle-inequality bound.
The last two evaluations are bounded by the same sum. Thus (3) also
equals the maximum over all ten coordinates.

If q is in the half-integral coset of (1), every |q_i| is at least 1/2,
so (3) is at least two. No vector in that coset is a cube vector. If q is
integral, the sum in (3) is at most one exactly when q is zero or one of
the eight vectors +/-e_i. Therefore

    L intersect {-1,0,1}^10 = {0, +/-r_1, +/-r_2, +/-r_3, +/-r_4}. (4)

The vector h attains maximum coordinate two, so the minimum height of
L minus M is exactly two. This is the claimed sharp coordinate enlargement.

## The parity defect

Reduce B modulo two. Every first-eight column becomes (1,1,1,1)^T.
Together with the two last columns, these span a three-dimensional binary
space. The unique row dependence is

    r_1+r_2+r_3+r_4 = 0 mod 2.

Since L is saturated, reduction L/2L -> F_2^10 is injective: if v=2w is
in L and w is integral, then w is in V and hence in L. The basis in (2)
shows dim_F2 L/2L=4. Equation (4) and the binary rank three above therefore
prove that no cube parity basis exists. The class of h is missing. Directly,
the first eight entries of every binary combination of the r_i are constant,
whereas h has both parities there.

## Relation-lattice interpretation and limits

The quotient Z^10/L is torsion-free because L is saturated. It is a valid
abstract free-abelian exponent quotient of rank six. Its cube relations
span the entire rational relation space, yet their binary reductions miss
one first-order relation direction. Thus a reduction from rational cube
generation to a parity-spanning cube basis needs an additional hypothesis
once relation rank reaches four.

The known rank-three argument is credited to Ali Romman's
`research/bit-three-register-lower-bound/README.md`, section 7, at the pinned
canonical base. CubeJerry's PR #6777 identifies cube saturation in the
arbitrary-register continuation as an open technical issue. Its two-relation
theorem is not rechecked here. The present construction is the new result.
The low-rank proof and (4) locate the first possible failure at relation
rank four; this does not locate the smallest ambient dimension.

No rank-one matrix realization of the ten exponent generators, scalar
projector word, target saving, native implementation, complete invoice,
compiler, dirty restoration or multiplication theorem follows. In
particular the eight-call span-five question has relation rank three and
is not excluded by this rank-four counterexample. The five selected
framework assumptions and the selected kappa remain unchanged.

## Evidence boundary

The argument above proves the full lattice identity and all-coordinate
height assertion. The standalone verifier exhausts all 3^10 ambient cube
vectors using a unit minor of the displayed saturated basis. It also
enumerates all 4-by-4 minors of B and of that basis, and a separate bounded
half-integral coefficient domain. Eight omission controls supply explicit
new cube vectors when any one of the eight sign columns is removed. These
checks concern this new example; they do not replay a predecessor result.
No proof-assistant or independent human acceptance is claimed.
