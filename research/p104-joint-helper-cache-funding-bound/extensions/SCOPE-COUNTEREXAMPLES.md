# Positive fixture and counterexamples to broader statements

## Positive smooth nonlinear scalar graph

Take helpers (a,b,c)=(t,t^2,t+t^2), retain a and fully debit b,c. With
independent main m, observation A1=(m,a) determines target t1=m+b by
phi1(s,t)=s+t^2. Observation A2=(m+a,m-a) determines target t2=m+c by
phi2(s,t)=s+((s-t)/2)^2. The linear zero row c-a-b vanishes identically.
At p the common helper tangent is (v,2p*v,(1+2p)*v). Linear providers are
B1=(1,2p) and B2=(1+p,-p). The retained projection is onto and the b,c
pivot columns form an identity matrix for the tangent annihilator.

## Critical real point: constant-rank hypothesis at fixed p is necessary

S={(t,t^3):t in R}, observe t^3, target t. Cube root is exact deterministic
recovery. At0 the tangent is(1,0), observation derivative0 and target
derivative1, so no tangent factor exists THERE. Rank is not locally
constant at0. At any nonzero point the factor exists; this does not
contradict the nearby-common-point existence theorem.

## Smooth complex source, cusp observation at a critical point

S={(t,t^2,t^3):t in C}, retain t, observe(t^2,t^3), target t. Recovery is
z/y when y!=0 and0 at(y,z)=0, globally well-defined on the observed cusp.
The source graph is smooth, but at0 the observation differential is zero
while the target differential is1. This disproves a fixed-critical-point
claim even over C. The observation rank changes near0.

## Real-smooth complex promise is not complex-scalar linear

S={(z,conjugate(z)):z in C}, retain z. Observing the second helper determines
the first by conjugation. This is a smooth real graph and its real tangent
is itself; its complex span is C^2. No nonzero complex-scalar equation
annihilates it, and the observation does not determine the first coordinate
on that complex span. The real tangent theorem remains valid. Applying a
complex-scalar funding theorem to it is invalid without a real/block lift.

## Retained projection at an arbitrary critical point

S={(t^2,t)}, retain the first coordinate. At0 the tangent projects to zero
on the retained coordinate even though the source graph is smooth. An
observation of the second coordinate has constant rank and determines
the first. The derivative factors but the retained-coordinate funding
conclusion fails: the tangent annihilator is supported on the retained
coordinate. A nearby nonzero point restores submersivity.

## Discrete/exact-grid promises

On S={0,1}^2, retain both coordinates. The linear observation x+2y is
injective and determines target x by parity. Any real linear domain
surjecting onto both retained coordinates is all R^2, where observation
kernel(-2,1) changes x. Thus no desired linear domain exists. The grid is
not a manifold with a retained submersion into R^2. More digits give the
same exact encoding issue; these fixtures do not propose a native decoder.

## Nonregular promise with full retained-coordinate range

For x,y in(0,1), take their canonical binary expansions, not eventually1.
Encode E(x,y) by base4 digits 2*b_n(x)+b_n(y). These digits are not eventually3,
so E is injective and digit decoding recovers x,y. Promise S is the graph
(x,y,E(x,y)); its projection onto retained(x,y) is the full open square.
Observe the single coordinate z and target both x,y. Deterministic recovery
exists, but no linear domain with retained projection rank2 can preserve
both targets through a one-dimensional observation. This graph has no
eligible smooth/submersive patch to which the theorem could apply.

## Positive characteristic is not included

Over an algebraically closed field of characteristic p, use S={(t,t^p)}.
Retain t and observe t^p. Frobenius is bijective on points, so a unique
set-theoretic pth-root decoder recovers t. Its differential is zero
EVERYWHERE, despite a nonzero target differential. Constant differential
rank in positive characteristic does not give the required fiber-curve
statement: scheme fibers are nonreduced. Characteristic0 is essential.

## General arrays need a block-linear funding theorem

For two-entry helpers X,Y, retain X and promise Y=P X with P a nonscalar
swap matrix. This is a smooth complex-linear graph. Observing Y recovers
X, but its tangent admits no nonzero scalar equation aX+bY=0, since
that would require aI+bP=0. It is block-linear, not in scalar C40's model.
This is a scope counterexample to identifying the tangent as scalar;
it does not assert the eventual block funding bound is false.

## Main-independent helper promise is required

If a helper instead obeys h=m for arbitrary main m, observing h recovers m.
Its tangent is the diagonal in(main,helper), not full-main times a fixed
helper tangent. The direct-product hypothesis cannot be silently removed.

These are analytic/algebraic fixtures. Exact executable checks are in
fixtures.py, FIXTURES.json and CHECKS.json. No finite sample is claimed as
proof of a universal assertion. The subsequent block review explains why
conjugation and nonscalar block graphs are not counterexamples to the
expanded real/block funding route.
