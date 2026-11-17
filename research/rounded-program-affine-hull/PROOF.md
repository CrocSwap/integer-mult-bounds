# Exact images and affine-lattice hulls of rounded-linear programs

## 1. Contract

Let the independent parameters be `z in Z^k`, with finite `k >= 1`.
A program has finitely many scalar registers. Its initial registers and
every unrounded assignment are rational affine combinations of `z` and
previous registers. A rounded assignment applies

    R(t) = floor(t + 1/2)

to such a rational affine combination. Outputs are any fixed list of
registers. Write the resulting map as `F: Z^k -> Q^m`.

This includes a rational affine entrance `x=x0+Bz`, correlated or redundant
parameters, separately rounded shears and rational rescaling. A fixed
rational-grid rounder is a composition of rational scaling, R and scaling
back. No variable products, data-dependent branches, unbounded iteration,
overflow or saturation are included. A finite unrolled sequence is allowed.

An affine lattice means `y+Lambda`, where Lambda is a finitely generated
additive subgroup of `Q^m`. Its rank may be less than m. These groups are
discrete in their real linear spans because their generators are rational.
All integer combinations use signed, unbounded integer coefficients.

## 2. A computable translation lattice

Replace each occurrence of R by the identity map. Propagate the linear
coefficient row of each register with respect to z through this idealized
program. Let `d_j in Q^(1 x k)` be the idealized coefficient row of the
argument of rounded assignment j, and let `M in Q^(m x k)` be the final
output coefficient matrix. Affine constants do not enter these rows.

Choose any finite-index subgroup `H <= Z^k` such that

    d_j h is an integer for every rounded assignment j and every h in H.  (1)

Such a subgroup always exists. If q is the least common multiple of all
denominators in all d_j, with q=1 when there are no rounded assignments,
then `q Z^k` satisfies (1). Alternatively, the kernel of the finite-image
map `h -> (d_j h mod Z)_j` gives a possibly larger H. Neither choice is
asserted to be the maximal translation subgroup of F.

**Translation lemma.** For every z in `Z^k` and h in H,

    F(z+h) = F(z) + M h.                                           (2)

Proof. Induct through the actual program. Initially each register has
exactly its idealized linear drift on replacing z by z+h. Rational affine
combinations preserve this property. At rounded assignment j, the induction
hypothesis makes the actual argument drift exactly `d_j h`. This is an
integer by (1), and `R(t+n)=R(t)+n` for every real t and integer n, including
negative t and half-integer ties. Thus the rounded register has the same
drift as its idealized counterpart. The output rows give (2). No linearity
of the rounded program has been assumed.

## 3. Exact output set and its smallest affine lattice

Let C be any complete set of representatives of `Z^k/H`, containing 0,
and let `h_1,...,h_k` be an integer basis of H. Define

    L0 = M H = sum_i Z (M h_i),
    G  = L0 + sum_(c in C) Z (F(c)-F(0)).

**Theorem.** The complete, unbounded output set and its smallest containing
affine lattice are exactly

    F(Z^k) = union_(c in C) (F(c) + L0),                            (3)
    hull_Z(F(Z^k)) = F(0) + G.                                    (4)

Proof of (3). Every z is uniquely c+h with c in C and h in H. Equation
(2) gives `F(z)=F(c)+Mh`. Conversely every element of `F(c)+MH` equals
`F(c+h)` for some h in H. Both inclusions therefore hold, even when M
has a kernel or L0 has smaller rank than the output space.

Proof of (4). Formula (3) places every output in `F(0)+G`. Conversely,
suppose an affine lattice contains all outputs. Since it contains F(0),
write it as `F(0)+Lambda`. It contains each difference `F(c)-F(0)`.
It also contains `F(h_i)-F(0)=M h_i`. Therefore `G <= Lambda`.
This proves minimality among all affine lattices, including skew lattices
and lattices with lower rank. It proves independence from C, its basis and
the permissible H used to compute the answer.

For the rectangular choice `H=q Z^k`, (4) gives an explicit finite
generating list with at most `q^k - 1 + k` vectors:

    F(c)-F(0) for c in {0,...,q-1}^k except 0,
    q M e_i for i=1,...,k.                                        (5)

This is an exact finite reduction, not a polynomial-time bound. The
denominator product or the number of input parameters can make q^k large.
No optimality of this generating-list length or period is claimed.

## 4. Necessary and sufficient closure test

For a proposed rational target affine lattice `y0+Lambda`, the following
three finite conditions are jointly necessary and sufficient:

    F(0)-y0 belongs to Lambda;
    M h_i belongs to Lambda for every basis vector h_i of H;
    F(c)-F(0) belongs to Lambda for every c in C.                    (6)

This follows directly from (4), or from both inclusions of (3). Membership
in a rational finitely generated lattice is an exact integer-module
problem after clearing denominators. Thus (6) is a decision procedure,
with no numerical tolerance and no bounded-reachability assumption.

For a sequence of separately specified input and target lattices, applying
(6) at every boundary proves preservation by induction from an admitted
entrance. This is a conditional interface implication. It neither proves
that the chosen entrance describes an actual selected caller nor states
that replacing a nonlinear reachable set by its hull preserves all its
nonlattice information. The lattice hull is the strongest *affine-lattice*
consequence of the given complete parameter domain.

## 5. Why residue outputs alone are insufficient

Consider the separately rounded shear on a new input domain

    x=3n, y=2m,
    F(n,m) = (3n, 2m + R(3n/2)).

Here q=2 is a valid rectangular period and

    M = [[3,0],[3/2,2]],
    F(0,0) = (0,0),
    q M e_1 = (6,3),    q M e_2 = (0,4).

All four residue outputs for `n,m in {0,1}` have even second coordinate.
Checking only these outputs would incorrectly admit target `3Z x 2Z`.
The actual output `F(2,0)=(6,3)` rejects it. The missing obligation is the
drift generator, not another residue representative.

The residue difference `(3,2)`, the generator `(6,3)` and the residue
difference `(0,2)` generate precisely `3Z x Z`: subtract twice `(3,2)`
from `(6,3)` to obtain `(0,-1)`, then obtain `(3,0)`. Every output has
first coordinate divisible by 3, proving the reverse containment.
Consequently the exact hull is `3Z x Z`, while `(0,1)` belongs to this
hull and is not an output. This distinguishes the hull from the output set.
The idealized output lattice contains `(3,3/2)`, so it would incorrectly
reject the actually valid target `3Z x Z`. Thus ideal-image-only testing
can also give a false closure verdict, in the other direction.

For this example the larger H with basis `(2,0),(0,1)` uses just two
residue representatives, with drift generators `(6,3),(0,2)`. It yields
the same hull. The proof does not require the rectangular period to be
minimal.

## 6. Evidence and scope

The written induction and subgroup argument prove the quantified result.
The companion verifier corroborates it on nested and two-input rational
programs. Its second route computes the integer lattice generated by
literal outputs in a larger signed parameter box, without idealizing any
rounding node. It also checks actual translation identities and explicit
failures of residue-only and ideal-image-only shortcuts.

woklerx #1848 supplies the source question about closure under intervening
updates and the separate mixed-precision cancellation interface. Adam Gall
#1908 already shows that ideal closure does not imply actual rounded-leaf
closure. Nick Petalas #6446 classifies common invariant planar lattices for
opposite rounded shears. Their results are cited rather than replayed, and
the theorem here does not depend on any of their numerical certificates.
Integer-translation equivariance, lattice normal forms and finite-coset
reasoning are classical. No literature-wide priority is claimed for those
ingredients. The new contribution is this exact output-set/hull formula
and finite closure criterion for the stated rounded-program interface.

No particular selected native program is admitted. Actual reachable input
domains, physical owners, restoration, movement/storage/precision charges,
the full recursive invoice and the selected five framework assumptions
remain separate. There is no new kappa or complete multiplication theorem.
