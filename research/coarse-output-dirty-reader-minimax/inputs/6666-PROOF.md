# Approximate unit channels and exact dirty restoration

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped constructive mathematical proof with finite exact
corroboration. All operations below are exact over D = Z[1/2]. Approximation
refers to the desired source response, not to rounding the executed gates.

## A changed normalization contract

For a finite dyadic matrix K and 0 < epsilon < 1, call t channels
epsilon-normalized when dyadic matrices X,Y satisfy

    ||X K Y - I_t||_infinity <= epsilon.

The norm is the induced maximum absolute row-sum norm. The maximum t is
exactly rank_Q(K). Zero rank gives zero channels. In particular, unlike
exact dyadic unit capacity, this maximum does not depend on odd Smith
factors. This statement concerns algebraic response capacity; it supplies
no independent productive target credit or physical carrier.

For the upper bound, suppose t > rank_Q(K) and put W=XKY. Then W is
singular. Choose a nonzero vector z in its real kernel. The norm inequality
gives ||z||_infinity = ||(I-W)z||_infinity <= epsilon ||z||_infinity,
which contradicts epsilon < 1. Thus t cannot exceed rational rank.

For attainment, let r=rank_Q(K)>0. Select r independent rows with a
zero-one row selector E, and write A=EK. Choose r columns whose r-by-r
minor is invertible over Q. Invert that minor and put its rows into those
positions of an otherwise zero matrix R. Then AR=I_r. This uses rational
division only to prepare finite constants; runtime division by an odd
number is not granted.

Round each entry of R to a nearest multiple of 2^-b, obtaining the
dyadic matrix Y_b. Each entry changes by at most delta=2^(-b-1), so

    ||A Y_b - I_r||_infinity
      = ||A(Y_b-R)||_infinity
      <= r ||A||_infinity 2^(-b-1).                 (1)

Here each row of Y_b-R has r entries. Choose b sufficiently large for
the last bound to be <= epsilon, and use X=E. Every smaller t follows by
restricting the attained r-channel response to t rows and columns; the
corresponding principal error submatrix has no larger row-sum norm.
All constants are finite. This proves the claimed maximum.

## Four shears cancel arbitrary dirt exactly

Fix any full-row-rank dyadic A of size r by n and a dyadic Y of size n by r.
There are disjoint source x in D^r, dirty helper h in D^n and accumulator
y in D^r. Their initial values are arbitrary. Only x has the optional
magnitude promise ||x||_infinity <= B. Execute chronologically

    h += Y x
    y += A h
    h -= Y x
    y -= A h.                                      (2)

After the second line the accumulator is y_in+A h_in+A Y x. The third
line restores h_in exactly, and the fourth subtracts A h_in. The endpoint is

    x_out = x_in,
    h_out = h_in,
    y_out = y_in + A Y x_in.                        (3)

Consequently Y=Y_b from (1) gives absolute increment error at most
epsilon B, independent of the magnitude or value of the arbitrary dirty
helper and initial accumulator. The word is invertible on every input;
reversing the order and signs gives its exact inverse. No zero helper,
rounded cancellation, saved dirty copy or erased information is used.

There is a matching lower bound on the number of block shears in this
declared alphabet. Permit any H(U): h+=Ux and O(V): y+=Vh, with x unchanged,
and charge each nonzero block shear one. Exact helper restoration forces
the sum of the H coefficients to vanish. Independence from arbitrary
initial dirt forces the sum of the O coefficients to vanish. A nonzero
source-to-accumulator response requires at least one nonzero shear of each
kind, and hence at least two of each. Thus at least four are necessary.
For epsilon<1, AY is invertible and nonzero, so (2) attains four.
This lower bound does not price scalar gates or an enlarged alphabet that
allows direct source-to-accumulator updates.

## Exact scalar precision barrier

For the scalar cut A=[q], where q>1 is odd, fix the reader A and allow
only the insertion coefficient c=a/2^b with integer a. No exact unit
response is possible. Reduction modulo any odd prime factor of q proves
that q c cannot equal one in D.

Let s be the remainder of 2^b modulo q. The exact optimal relative error
at this prescribed maximum fractional depth is

    min_a |q a/2^b - 1| = min(s,q-s)/2^b.            (4)

Indeed the numerator is the distance of 2^b to the nearest multiple of q.
The two neighboring multiples attain that distance; all others are farther
away. Denominators dividing 2^b are included by choosing even numerators.
Since q is odd, s is nonzero. The error is at least 2^-b. At q=3, s is
always one or two, so equality holds at every b>=0. For a desired relative
error 2^-p with integer p>=0, p fractional bits are necessary and sufficient
for this fixed reader and one insertion coefficient. At p>=1 the response
is nonzero, and the four-block lower bound also applies.

This is not a bound on an alphabet that can change both coefficients,
directly read x into y, or alter the source grid. It makes the precision
cost of this particular odd-torsion escape explicit.

## Logical gates and intermediate magnitudes are payable

The four blocks in (2) contain exactly 2 nnz(A)+2 nnz(Y) nonzero scalar
coefficient shears if each matrix entry is expanded independently. Neither
this count nor the block count declares arbitrary scalar multiplication free.

There is an explicit elementary lowering. For c=a/2^b in lowest terms,
a nonzero and ell=bit_length(|a|), implement z+=cu by halving u b times,
then visiting the ell binary digits from low to high, adding sign(a)u
when the digit is one and doubling u between digits. Restore u's net
scale at the end. The source returns exactly and the destination receives
cu. This construction uses exactly

    L(c) = popcount(|a|) + 2 max(b,ell-1)

signed unit ADDs plus SCALE-2/SCALE-half events in total. Take L(0)=0.
Thus the complete explicit elementary-event upper bound for (2) is

    2 sum_ij L(A_ij) + 2 sum_ij L(Y_ij).             (5)

It is a construction count, not a scalar optimality theorem or a native
recursive invoice. The circuit has exactly 2r+n roles. The source scaling
within a coefficient shear can require additional fractional bits.

Put C=||Y||_infinity and D=||A||_infinity. At the four block boundaries,

    ||h||_infinity <= ||h_in||_infinity + C B,
    ||y||_infinity <= ||y_in||_infinity
                     + D (||h_in||_infinity + C B).

The second bound covers the second line, and also the final line because
||AYx||<=DCB. Entrywise execution of each block is bounded by these absolute
row sums, including each inverse block's remaining suffix. In an individual
lowered coefficient shear the scaled source has magnitude at most
2^max(0,ell-1-b) times its incoming magnitude; the destination partial sum
is bounded by its incoming magnitude plus |cu|. These give explicit
finite guards whenever the incoming dirty values have specified finite
widths. Arbitrarily large dirt has no uniform finite storage bound.

## Scope, provenance and limits

Ali Romman's PR5615 proves exact dyadic unit-pairing capacity using Smith
factors, with PR5602/5611/5599, Nick Petalas's PR5115 and the retained
helper/native/controller/compiler lineage. That theorem is a cited premise
for the contrast with exact capacity; it is not audited here. Density of
dyadic rationals, matrix inversion, the four-shear commutator and binary
coefficient synthesis are classical. The contribution is the changed
approximate-capacity contract, its quantitative normalizer, exact-dirty
composition and matching four-block/odd-scalar bounds.

Ali Romman's PR1135 already distinguishes an additive same-grid child
from an approximate rational map and identifies grid refinement as an
escape. This construction takes that escape explicitly. It does not claim
to beat PR1135's same-grid integer-slope obstruction. Logical gates act
exactly on D; no pre-existing fixed grid is silently assumed closed.

The source and destination accesses and the two uses of each block must
be legal and paid in an actual caller. The two h observations must see the
specified chronological states in compatible native charts. Native costs,
input/output bases, stock, movement, rounded gate execution, complete error
propagation, target independence and the full signed invoice remain open.
No actual P104 cut, finite native certificate, supplier, kappa improvement
or complete multiplication theorem is supplied. The five selected
framework assumptions remain. Independent human and formal proof-kernel
review are unclaimed.
