# Exact stagewise lattice closure for rounded shears

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped mathematical proof. The executable supplies finite
corroboration, not a proof-kernel formalization.

## Model and statement

Write R(t)=floor(t+1/2), including for negative t. For rational a,b define

    U_a(x,y) = (x, y + R(a x)),
    V_b(x,y) = (x + R(b y), y).

Both are bijections of Z^2. Their inverses subtract the same rounded
increment. In particular U_a^-1 need not be U_(-a) at ties.

Let L be any full-rank additive sublattice of Z^2. Its unique column
Hermite form can be written

    L = { (h n, r n + k m) : n,m in Z },
    h,k >= 1, 0 <= r < k.

Set g=gcd(r,k) and ell=hk/g. Then the exact closure conditions are

    U_a(L)=L  iff  k=1 or a h / k is an integer,
    V_b(L)=L  iff  ell=1 or b g / ell is an integer.       (1)

Consequently, if a and b are both nonintegral, a proper full-rank L
preserved by both maps exists if and only if ab is an integer. If such
an L exists, both rounded maps equal their ideal linear shears on L.

For sufficiency, if a=p/q in lowest terms, q>=2, the explicit lattice

    L = q Z x |p| Z                                      (2)

works whenever ab is an integer. Its index q|p| is greater than one.
These statements include negative slopes and arbitrary lattice index.

## Scalar lemma

For rational c and integer d>=2,

    R(c n) belongs to d Z for every n in Z
        iff c belongs to d Z.                           (3)

The reverse implication follows because rounding fixes integers.
For necessity, integral c gives R(c)=c, so d divides c.

Otherwise write c=t+s/q with t an integer, 1<=s<q, q>=2.
For n=0,...,q-1 the successive differences

    delta_n = R(c(n+1)) - R(c n)

are each t or t+1. This follows by writing R(cn) as a floor: adding
t+s/q changes a floor by t or t+1, including at ties. Their sum is
R(cq)-R(0)=tq+s. Therefore exactly s of the differences equal t+1
and q-s equal t. If all R(cn) belonged to dZ, all differences would
belong to dZ. The consecutive integers t and t+1 cannot both be
divisible by d>=2. This proves (3), using only n=0,...,q in the
nonintegral case. The d=1 exception is essential.

## Proof of the closure criterion

The x-coordinate projection of L is hZ. Its vertical fiber is

    L intersect ({0} x Z) = {0} x kZ.

At a point with x=hn, U_a changes only y by R(ahn). Thus U_a(L)
is contained in L exactly when all these increments belong to kZ.
For k=1 this is automatic; for k>=2 apply (3) with c=ah and d=k.
The same increment can be subtracted, so containment also implies
equality and closure under the literal inverse.

The y-coordinate projection is gZ because rZ+kZ=gZ. A horizontal
vector (x,0) belongs to L precisely when x=hn and k divides rn.
The least positive such x is ell=hk/g. Therefore the horizontal
fiber is ellZ x {0}. Apply the same argument to V_b, now with
c=bg and d=ell. This proves both equivalences in (1), without
assuming that L is rectangular or that the shears are linear.

## Proof of the integer-product equivalence

Suppose L is proper and both slopes are nonintegral.
If k=1, then r=0, g=1, ell=h and properness gives h>1.
Closure under V_b would force b/h to be an integer, contradicting
nonintegrality of b. Hence k>1.

If ell=1, the positive integers h and k/g must both equal one.
Then g=k, r=0, h=1 and properness gives k>1. Closure under U_a
would force a/k to be an integer, another contradiction. Thus ell>1.

By (1), there are integers m,n with

    ah = km,  bg = ell n.

Put t=k/g, a positive integer. Since ell=ht, multiplication gives

    ab = (km/h)(ell n/g) = t^2 mn,                      (4)

an integer. Moreover every source x lies in hZ and every source y
lies in gZ; ah and bg are integers. No rounding occurs on L.

Conversely let ab=N be an integer and a=p/q be reduced, q>=2.
Since a is nonintegral, p is nonzero. For x=qz and y=|p|w,

    ax = pz belongs to |p|Z,
    by = sign(p) N q w belongs to qZ.

Both increments are already integers in the required fibers of (2).
Both shears and their literal inverses preserve this proper lattice.
This proves sufficiency and the complete equivalence.

## A precision-domain obstruction

For a=1/2 and b=-4/5, ab=-2/5 is not integral. Therefore Z^2 is
the only full-rank additive sublattice of Z^2 invariant under both
rounded directions. These are the two slopes in the familiar lifting
factorization of the rotation with cosine 3/5 and sine 4/5:

    [[1,1/2],[0,1]] [[1,0],[-4/5,1]] [[1,1/2],[0,1]]
        = [[3/5,4/5],[-4/5,3/5]].

Requiring one proper additive entrance lattice to survive every
rounded substep cannot support a correlated precision policy for
this lifting pair. This is a scoped closure obstruction. It says
nothing about changing the domain between stages, affine cosets,
nonadditive domains, a whole-word exactness domain, or periodic
translation-equivariance lattices. It does not assert any violation
of a selected caller's contract.

## Why the finite oracle is complete for each tested lattice

Fix one slope a=p/q and lattice index D=hk. D Z^2 is contained in L.
Take M=qD. Translating an input coordinate by M changes a rounded
increment by pD, because R(t+j)=R(t)+j for integer j. Both the input
translation and the resulting output changes lie in D Z^2, hence L.
Membership after either shear consequently depends only on the input
modulo M Z^2. This is a periodicity argument, not an assumption that
the rounded shear preserves M Z^2.

All representatives in L modulo M Z^2 are enumerated exactly once by

    0 <= u < M/h, 0 <= v < M/k,
    x=hu, y=(ru+kv) mod M.

There are (M/h)(M/k)=q^2D representatives. The oracle literally
applies both rounded updates to each one and tests HNF membership.
It uses neither projected spacings nor (1) to decide closure. Thus
each finite one-shear verdict is exhaustive for that entire tested
lattice, even though the lattice has infinitely many points.

The universal claims above rest on the written scalar and fiber
proofs. The finite range of lattice parameters and slopes is not
used to extrapolate a universal result.
