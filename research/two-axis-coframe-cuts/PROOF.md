# Exact cut threshold for the two-axis binary chart menu

This scoped proof and its finite corroboration were produced by Nick Petalas.

## Object and theorem

Let V=F2^4 have ordered coordinates x1,x2,z1,z2 and alternating form

    <(x,z),(x',z')> = x.z' + z.x'.

Let X contain all two-dimensional totally isotropic subspaces of V. They
are Lagrangian planes. For L,M in X put d(L,M)=2-dim(L intersect M).
For 0<t<=1 put a=2^t. The tariff d^t has values 0,1,a.

For A a subset of X, the cut metric delta_A is 1 on pairs with exactly one
endpoint in A, and zero elsewhere. A nonnegative cut representation is a
finite sum rho=sum_A w_A delta_A with w_A>=0. For a finite set these are
exactly the metrics embeddable in a finite-dimensional real L1 space.
Indeed a cut is a single weighted binary coordinate. Conversely, sort the
finitely many values of each real coordinate and express each absolute
difference as the sum of the gaps at the thresholds it crosses.

**Theorem.** The full metric d^t has a nonnegative cut representation if
and only if a<=3/2, equivalently t<=log_2(3/2). Its least L1 distortion is

    D(t) = max(1, 2a/3) = max(1, 2^(t+1)/3).

Here distortion means the least D for which a cut metric rho satisfies
d^t<=rho<=D*d^t on every pair, after an arbitrary common rescaling. Thus
the claim is about the entire fifteen-label metric, not one graph instance.

## The chart and pencil counts

There are fifteen nonzero vectors in V, and a line over F2 has just one
nonzero vector. Fix v!=0. Its orthogonal space v-perp has eight vectors.
There are six choices w in v-perp outside span(v). Each plane containing
v is counted twice by w and w+v. Therefore exactly three Lagrangian
planes contain v. Each plane contains three nonzero vectors. Counting
incidences gives |X|=15*3/3=15.

For v!=0 let C_v={L in X:v in L}, a three-plane pencil. A pair at rank
distance one shares one nonzero vector; a pair at distance two shares
none. Since each plane belongs to three pencils, the number of pencil
cuts separating a pair is respectively four and six. In symbols,

    sum_(v!=0) delta_(C_v)(L,M) = 4 if d=1, and 6 if d=2.

The sum over all fifteen singleton cuts separates every distinct pair
exactly twice.

## Attaining the exact representation below the threshold

For 1<=a<=3/2 assign each singleton cut weight (3-2a)/2 and each pencil
cut weight (a-1)/2. Both weights are nonnegative. The resulting pair
values are

    d=1: 2*(3-2a)/2 + 4*(a-1)/2 = 1,
    d=2: 2*(3-2a)/2 + 6*(a-1)/2 = a.

This constructs the claimed representation, including the threshold.
For positive t, a>1; the formula also covers the equilateral limit a=1.

## An explicit five-chart lower bound

Write e1,e2,f1,f2 for the ordered basis above. Use

    A = span(e1,e2),
    B = span(f1,f2),
    C = span(e2+f1,e1+f2),
    D = span(e1,f2),
    E = span(e2,f1).

Each plane is isotropic. A,B,C are pairwise disjoint outside zero; D,E
are disjoint outside zero. Every plane in {A,B,C} meets each plane in
{D,E} in a line. Thus this is an isometric K3,2 with within-part distance
two and cross-part distance one.

Give A,B,C signs +1 and D,E signs -1. For every cut delta_S, let k be
the sum of those signs in S. The total sign sum is one, so

    Q(delta_S) = sum_(i<j) b_i*b_j*delta_S(i,j) = k*(1-k) <= 0.

The last inequality holds because k is an integer. Nonnegative sums of
cuts obey Q(rho)<=0. For d^t the four within-part pairs contribute 4a
and the six cross-part pairs contribute -6. Thus a>3/2 is impossible.

This is an explicit separation, not a failed embedding search. The
pentagonal inequality and its cut proof are classical. Jerry Chen's
PR907 already uses this inequality on different rank and Cayley metrics.

## The sharp distortion

Suppose d^t<=rho<=D*d^t. On the four within-part witness pairs rho>=a;
on the six cross pairs rho<=D. Hence 0>=Q(rho)>=4a-6D, so D>=2a/3.
Also D>=1. These are lower bounds for arbitrary real L1 embeddings.

For a>=3/2, give each pencil cut weight a/6 and use no singleton cuts.
The resulting rho is 2a/3 on rank-one pairs and a on rank-two pairs.
It satisfies d^t<=rho<=(2a/3)*d^t and attains the lower bound. Below
the threshold the exact construction already gives distortion one.

## Consequence for larger binary chart menus

In a 2m-dimensional symplectic direct sum with m>=2, append the same
fixed Lagrangian (m-2)-space to each of these fifteen planes. Intersections
gain exactly m-2 dimensions, so m-dim(L intersect M) retains all their
distances. Restricting any cut representation to these charts remains a
cut representation. Therefore the full binary Lagrangian menu in every
m>=2 fails exact cut representation when 2^t>3/2, and has L1 distortion
at least 2^(t+1)/3. No matching upper bound is claimed for larger m.

In particular, every tariff t=1-C with 0<=C<=1/100 is excluded. The
strict endpoint comparison 2^(99/100)>3/2 is equivalent to the integer
inequality 2^199>3^100, checked by the verifier. Monotonicity covers the
whole interval. At t=1 the two-axis distortion is exactly 4/3.

## What this does and does not obstruct

Dugongue's PR5693 uses the inverse computational Lagrangian and this rank
distance to price an actual coframe transition. Its common-anchor binary
cut theorem follows from a triangle inequality. Nothing here contradicts
that theorem. The new statement concerns representing all pairwise costs
of a full chart menu by fixed nonnegative cut coordinates.

It excludes that particular extension of the cut method near the current
power tariff. It does not exclude auxiliary-variable cut reductions,
restricted chart families, another optimization algorithm, approximate
optimization, or a source-specific favorable coframe word. It proves no
complexity lower bound. No phases, physical lowering, target delivery,
restoration, ordinary cost or complete caller invoice are supplied.

The unpowered generalized-quadrangle nonembedding is known, for example
Deza and Laurent, *L1-rigid graphs*, Journal of Algebraic Combinatorics 3
(1994), 153-175, Fact 5.10(ii). The powered threshold, attaining pencil
formula and exact distortion are derived here for the repository's chart
menu. No global literature-priority claim is made for these finite-metric
facts. The contribution is this explicit scoped classification and its
replayable application to the Gaussian coframe tariff.
