# Defining-characteristic point-column thresholds

The scoped proof and its application are produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

## Statement and boundary

Let q=p^e be any prime power, K any field of characteristic p, d>=1, and
w>=0. Addresses are ordered w-tuples of points of F_q^d. Every label in
G=GL_d(F_q) or G=AGL_d(F_q) acts diagonally, with the same matrix and, in the
affine case, the same translation on every point. Payloads range over the
entire vector space with these addresses as basis. Write rho_w for the
induced K-algebra map from K[G] to its payload endomorphisms. The least w
for which rho_w is injective is

| Group | d>=2 | d=1, q>2 | d=1, q=2 |
| --- | --- | --- | --- |
| GL_d(F_q) | d | 1 | 0 |
| AGL_d(F_q) | d+1 | 2 | 1 |

Faithfulness holds at every larger width. Applying this entrywise to a
finite matrix of group-algebra coefficients gives the same equivalence for
complete dirty-register endpoints. No clean-input restriction is permitted.

The binary cases and regular-orbit/norm method are credited to ywz65's
PR2599. The new scope is arbitrary q in defining characteristic, including
the different one-dimensional affine exception for q>2. The claim is a
written mathematical proof, corroborated by bounded exact computations.
It is not a supplier or complete multiplication theorem.

## Regular orbits give the upper bounds

If an address z has trivial stabilizer, then its images gz are distinct.
For c=sum_g c_g[g], applying rho_w(c) to delta_z gives sum_g c_g delta_gz.
Thus rho_w(c)=0 forces every c_g=0. This argument works over any K.

An ordered vector-space basis has trivial linear stabilizer, so width d
suffices for GL_d. The origin followed by an ordered basis has trivial
affine stabilizer, so width d+1 suffices for AGL_d. Extending either tuple
preserves its trivial stabilizer. GL_1(F_2) is the trivial group, so even
its action on the single empty tuple is algebra-faithful. AGL_1(F_2) is the
two-element translation group acting regularly on its two points; width
one therefore suffices. These observations prove every upper bound.

## Stabilizers and the lower bounds in dimension at least two

Define GL_0(F_q) to have order one. The pointwise stabilizer of a linear
tuple spanning an r-dimensional subspace has order

    q^(r(d-r)) |GL_(d-r)(F_q)|.

Indeed, choose its span as the first r coordinate directions. A fixing
matrix has blocks [I_r B; 0 C], where B is arbitrary and C is invertible.
There are q^(r(d-r)) choices for B. For completeness,

    |GL_s(F_q)| = product_(j=0,...,s-1) (q^s-q^j),

by choosing independent columns successively. For s>=2, the j=1 factor
is divisible by p.

Suppose d>=2 and w<d. Every tuple has r<=w<d. If r>=1, its stabilizer
order has a factor q. If r=0, its stabilizer is GL_d and has order
divisible by p. Hence every address stabilizer has order zero in K.

For a finite group acting on a finite address set, the group norm

    n_G = sum_(g in G) [g]

maps delta_z to |G_z| times the sum of basis vectors in the orbit of z.
Each coefficient counts the labels taking z to the specified image, a
coset of G_z. Thus rho_w(n_G)=0 whenever all stabilizers are divisible by
p. The formal element n_G is nonzero, since every coefficient is one.
This proves failure of faithfulness below width d for GL_d.

For affine tuples of positive width, translate their first point to the
origin and let r be the span dimension of the remaining differences.
The affine stabilizer is then the same block stabilizer above. At w<=d,
we have r<=w-1<d; for d>=2, the preceding divisibility argument applies.
At w=0 the entire affine group is the stabilizer, whose order has factor
q^d from its translations. The norm therefore annihilates every address
at every width below d+1. This proves the affine lower bound for d>=2.

## The one-dimensional exceptions

For GL_1 and q>2, choose a nonzero a other than one. At width zero the
nonzero formal element [a]-[1] acts as zero. A nonzero point has trivial
linear stabilizer, giving the stated least width one. For q=2 the group
is trivial, as already noted.

For AGL_1 and q>2, choose the same a and write g_(a,b)(x)=a x+b. Consider

    u_a = sum_(b in F_q) [g_(a,b)] - sum_(b in F_q) [g_(1,b)].

The two multiplier cosets are disjoint, so u_a is nonzero over every
field K, including characteristic two. On a single point x, each sum
visits every y exactly once. Both represented operators are the all-ones
matrix J, and their difference is zero. The element also acts as zero
at width zero. Width two has a regular orbit on pairs of distinct points,
since an affine line map is determined by two distinct images. Therefore
the least width is two. This separate argument is necessary: the
single-point stabilizer has order q-1, which is not divisible by p, and
the group norm does not annihilate that action.

For q=2, the affine translation group is regular at width one and has
nonzero norm annihilating width zero in characteristic two. Its least
width is one. All exceptions are now proved.

## A literal two-dirty-role affine-line alias

Work over F_3 with two arbitrary payloads, X and Y. For an address label g,
let D_g apply rho_w(g) to X alone, and let S_c add cY to X. In chronological
order execute D_g^-1, S_c, D_g. Its complete formal matrix is

    I + c[g] E_(X,Y).

The complete own-input block remains identity. Such off-diagonal shears
multiply by adding their coefficients, since E_(X,Y)^2=0. Execute this
block once for each g_(2,b) with c=1 and once for each g_(1,b) with c=-1,
for b=0,1,2. Omit the identity address operations. The resulting formal
map is I+u_2 E_(X,Y), which differs from identity. Y is restored exactly
and no clean role, reset or erasure is used.

At w=1 the complete represented map is identity on every dirty input.
At w=2, the two sums on a source pair (x,y) have differences 2(y-x) and
y-x respectively. If x=y, they cancel. Otherwise they have disjoint
three-element supports, so the coupling is nonzero. There are exactly
six ordered off-diagonal source pairs. The verifier checks all six plus
the other twelve dirty basis columns at width two, and every basis
column at width one. It separately replays the formal group-algebra row.

The literal schedule has ten nonidentity full-address operations and six
scalar ADDs. These are logical records under a declared alphabet, not
elementary native costs or a target-call improvement. A faithful group
action on points must not be confused with a faithful group-algebra
action on payloads: the six affine maps are distinct already at w=1.

## Verification contract and implementation bounds

The verifier is self-contained except for an authenticated predecessor
README used for credit and scope. It imports no predecessor executable
and reruns no predecessor census. Its fifteen fixtures cover both groups
in dimension one for q=2,3,4,5,8,9, both groups in dimension two for q=3,
and GL_2(F_4). Fields use polynomial bases, with all field triples checked.
Every group is enumerated from all matrices and offsets; its permutations,
order, below-threshold stabilizer formula and explicit annihilator are
checked. A regular orbit and coefficient recovery check the positive side.
An independent full permutation-matrix span checks each line action.

The universal statement rests on the written proof. Finite enumeration
does not cover all prime powers or dimensions, and is not a kernel proof.
The checks do not establish native realization, physical layouts, arbitrary
cross-column actions, a selected caller, compiler/precision/tape funding,
any of the five framework assumptions, or a new kappa.

Power-of-ten inspection is scoped to verify.py. Functions are below sixty
physical lines. There is no recursion, dynamic code evaluation, process
creation or network access. CLI parsing rejects every unsupported argument.
All mathematical failure checks use explicit exceptions and remain active
under optimized Python. The only runtime callback is reject, whose targets
are the explicit local checks named at its call sites.

Managed Python allocation is a rule-3 deviation. Inputs are fixed: q<=9,
d<=2, at most 256 candidate matrices, at most 432 group elements, and at
most 91 below-threshold addresses per case. The largest literal matrix
is 18 by 18, and the largest line-action rank input is 72 by 81. Loops
are bounded by these finite collections. The generated JSON receipt is
printed to stdout; it records actual outcomes and package SHA256 values.
No replay output is written into the checkout. Source authentication uses
one declared documentation input, whose size is fixed by its SHA256 pin.

Rule 10 uses warning-strict normal and optimized registered replays and
AST/source inspection. No static type checker is configured for this
isolated standard-library package. Changing the fixture bounds or adding
runtime inputs requires revisiting the memory bounds and validation.

## Credit and scope of originality

ywz65 / PR2599 retains the binary thresholds, norm alias and regular-orbit
method. Its PR2629 supplies a distinct binary kernel-checked interface;
no such formalization is claimed here. Woklerx retains the finite-address
regular-action bridge. Gareth Davidson / PR1333 retains the distinction
between formal algebra and represented endpoints; Josie Elliston and
Hanson Sun retain the GL3 census context. Those results are cited premises
and context, not deliverables rechecked here. Orbit-stabilizer, regular
orbits and the group norm are classical. The new contribution is their
sharp defining-characteristic q-ary application, the affine-line coset
obstruction, and its complete two-dirty-role witness. No literature-wide
priority is claimed.
