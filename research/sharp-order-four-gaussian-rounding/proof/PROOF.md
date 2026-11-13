# Sharp radial cost of exact-sum Gaussian square-to-swap rounding

Let G=Z[i], S(u,v)=(v,u), K(u,v)=(conj(u),conj(v)), and
C_+(u,v)=((s+i d)/2,(s-i d)/2), s=u+v,d=u-v. Norms are Euclidean pair
norms. Put beta=sqrt(19)-sqrt(13).
For a bijection define forward outward slack as
Delta_+(F)=sup_x max(0,||F(x)||-||x||), inverse outward slack as
Delta_+(F^-1), and absolute radial slack as
R(F)=sup_x | ||F(x)||-||x|| |.

**Theorem.** Every total F:G^2→G^2 preserving exact sum, satisfying
||F(x)-C_+x||<=1 and F^2=S, has forward outward norm slack at least beta.
An explicit annular construction attains beta, preserves global Gaussian-
unit phase covariance and has an explicit inverse. Its absolute, forward
and inverse outward radial suprema all equal beta, attained at finite inputs.
No phase, periodicity or equivariance premise is used in the lower bound.

The optimum is for this exact-sum/order-constrained class, not for unrestricted
Gaussian bijections. Inverse-by-conjugation is incompatible with exact sum
and F^2=S. Same-map tensor commutation is blocked by the known #6778 theorem.
No selected caller or physical tariff is asserted.

## 1. Exact-sum fibers and unit dominoes

Write real two-vectors for s,d and let
J(x,y)=(-y,x), B(x,y)=(x+y,x-y), T=B/2, Q=-J.
Then T^-1=B, TJT^-1=Q, and ||Tz||^2=||z||^2/2.
On a fixed sum fiber, F induces f(d), where d and s have the same component
parities. Pair norm squared is c+||d||^2/2, c=|s|^2/2. The pair error
squared is ||f(d)-Jd||^2/2.

If s's component parities agree, the ideal output is integral and error<=1
forces exactness: the two Gaussian errors are e,-e with e∈G, so
2|e|^2<=1 implies e=0. For a mixed parity sum, f(d)-Jd has two odd integer
components, hence error<=1 forces them to be±1. With t=TJd, define
M_A(t)=T f(d). This is a unit-neighbor bijection between the two half-grid
colors in L=(Z+1/2)^2. Bijectivity follows from F^2=S, which gives F^4=id
on each exact-sum fiber.

For the lower bound fix s=1. Its d parity is(odd,even), and source color
A consists of half-grid points with EVEN coordinate sum, since sum(TJd)
=-d_im. The opposite color B_h has odd sum. The maps TJ and T biject
the corresponding d coset onto A and B_h respectively. Thus M_A:A→B_h
is a complete unit-neighbor bijection, not merely a partial selection.

## 2. The order identity forces quarter-turn equivariance

Let g=(TJ) f (TJ)^-1 on A. Then g=Q M_A, g^2=-I=Q^2. Multiplying
the latter identity by Q^-1 gives M_A Q M_A=Q on A. Extend M to all L
by M_A on A and M_A^-1 on B_h. It is an involutive perfect unit-domino
matching. For a∈A, the displayed identity gives
M_A^-1(Qa)=Q M_A(a), proving M Q=Q M there. For b=M_A(a)∈B_h,
M(Qb)=M_A(Q M_A(a))=Qa=Q M(b). Thus M commutes with quarter-turn Q on
both colors. Oddness follows from Q^2=-I; it is not an extra hypothesis.

This reduction applies to every candidate F, with no phase-covariance or
period condition on F. It is the missing implication needed before a
matching-orbit parity argument can yield an unrestricted class lower bound.

## 3. The 36-vertex obstruction

Take D={t∈L:max(|t_1|,|t_2|)<=5/2}, a quarter-turn-invariant set of36
vertices. No unit edge is fixed by a half-turn: that would put its midpoint
at the origin, impossible for a horizontal or vertical edge on L. Hence
every quarter-turn orbit of edges has size4. If an edge belongs to the
equivariant perfect matching, its four orbit edges are disjoint and consume
eight vertices. (A geometric edge orbit with overlapping endpoints cannot
belong to that matching.)

If no matching edge crossed D, its36 vertices would partition into these
eight-vertex orbits, contradicting36≡4 mod8. A crossing edge has the form
(±5/2,y)↔(±7/2,y), |y|<=5/2, or a quarter-turn thereof. At s=1,c=1/2,
its pair radial jump is

sqrt(1/2+49/4+y^2)-sqrt(1/2+25/4+y^2).

This decreases with y^2; its minimum is at |y|=5/2 and equals beta.
At least one absolute radial jump of F on this fiber is therefore >=beta.
If it is inward, the next F step reverses its radius change because F^2=S.
Equivalently F^-1=S F has the same output norm as F at each input, so
forward slack, inverse outward slack and absolute radial supremum coincide.
This proves the forward lower beta for the entire stated order class.

## 4. Explicit annular matching

The square ring of radius k+1/2 has8k+4 half-grid vertices. Group rings
k=2m and k+1=2m+1, m>=0. Write a=2m+1/2 and b=a+1.
Use four unit connector edges obtained by rotating
(a,a)↔(a+1,a) by quarter turns. They use all four inner corners and four
outer points. On the inner top side, the remaining arc is
(-a+1,a),(-a+2,a),...,(a-1,a), of4m vertices. Pair consecutive vertices.
On the outer top side, use
(b,b),(b-1,b),... ,(-a+1,b), of4m+2 vertices, again paired consecutively.
Rotate both lists and all their pairs by quarter turns.

These four inner arcs and four outer arcs are disjoint after connector
endpoints are removed. Their even lengths cover every remaining point of
the two rings. At m=0 the inner arcs are empty, not exceptional unmatched
vertices. Different ring pairs are disjoint and exhaust L. Therefore these
edges define a global perfect unit matching M. The edge set is closed under
quarter-turns, so M commutes with Q and is an involution.

## 5. From the matching to the Gaussian map

For equal component parity sums use f(d)=Jd, the exact ideal map. For
mixed sums define f(d)=B M(TJd). If d parity is(p,1-p), t=TJd has sum
parity1-p; M flips it to p. Thus B M(t) has component parities(p,1-p),
and F(u,v)=((s+f(d))/2,(s-f(d))/2) is Gaussian integral and preserves sum.
It has pair error exactly1 in the mixed case because M(t)-t is a unit.

In transformed coordinates the map is g=Q M. Since M^2=id and M Q=Q M,
g^2=Q^2=-I, hence f^2=-I and F^2=S. Its inverse is S F, and F^4=id.
It is a total bijection. Also f(Jd)=Jf(d) follows from quarter-turn
equivariance, so F commutes with all global Gaussian units. The same M is
used on both colors and every mixed-sum fiber; no sum-dependent table is
silently chosen. Common translation and equal-input/zero preservation follow.

## 6. Uniform upper beta and finite attainment

For mixed sums c>=1/2. A tangential edge on a ring has, at its lower
absolute changing coordinate, magnitudes u and u+1, with the other coordinate
r>=u+1. Its lower squared pair radius is at least
1/2+r^2+u^2>=(2u+1)^2/2+1. Rationalizing the radius difference gives a
jump strictly below1/sqrt(2). A central sign-toggle has zero radial jump.

For a connector the jump is at most
delta(a)=sqrt(2a^2+2a+3/2)-sqrt(2a^2+1/2), a=2m+1/2,
because increasing c decreases a fixed squared-radius jump. The sign of
delta'(a) is the sign of-2a^2+2a+1/2. Thus delta decreases for all a>=5/2.
The first two values are delta(1/2)=sqrt3-1 and delta(5/2)=beta, and the
second is larger: sqrt19+1>sqrt13+sqrt3 reduces by positive squaring to
sqrt19>4. Also sqrt3-1>1/sqrt2 reduces to9>8. Hence every tangential
or connector edge has pair radial jump<=beta.

The edge(5/2,5/2)↔(7/2,5/2) is present. At s=1 it gives the exact
four-cycle of Gaussian pairs

(3,-2)→(3i,1-3i)→(-2,3)→(1-3i,3i)→(3,-2).

The squared norms alternate13 and19. Both forward and inverse outward
slack therefore attain beta, proving sharpness. For this constrained class
the three radial notions coincide, but no new unrestricted forward-only
lower bound is being asserted for maps without F^2=S.

## 7. Unavoidable conjugacy and tensor limitations

Let K conjugate each Gaussian coordinate. Exact sum plus F^2=S can never
also satisfy K F K=F^-1. At real input(1,0), that identity and F^-1=S F
would force the two outputs to be conjugates, whose Gaussian-integer sum
has even real part, contradicting sum1. No error or phase premise is used.
The actual negative provider is S F, not the conjugated positive provider.

The map is exact whenever the ideal pair image is integral and is globally
Gaussian-unit covariant. Therefore #6778's known all-n obstruction applies
at n=1: applying this same stateless map independently to rows and columns
cannot commute. This is a known universal incompatibility, not left open
and not newly established here. Exact pair square/fourth power does not
establish native graph flatness, linearity or a selected tensor/caller.

## 8. Provenance, source limits and reproducibility

The current CubeJerry workstream proposed the annular matching and boundary
parity mechanism. This role supplied the complementary all-input reduction
from arbitrary F to an equivariant matching, checked both color domains,
and proved the sharp lower/upper argument. The original explicit quarter-
cycle construction of radial cost1 is frozen separately as a superseded
checkpoint, not counted as another contribution.

The allowed root conserved-half-grid/check_candidate.py was inspected,
including its reference matching, to fix the B/2 convention after the original
construction was derived. It was not imported or used as an independent
oracle. This role is not blind to that supplied reference. No C source file
was read. The annular checker generates its own finite edges and tests;
separate root implementation evidence retains its attribution.

#6509 a4173e810c4d34a1d13b9745af123ad0ec6cfed5 already supplies exact sum,
nearest error, phase covariance, inverse and fourth power, but not the square
to swap. #6619 eaa967e7e8aa12cc53ec246a5fc00c5f8873a50b supplies the radial
norm-contracting question, crediting ywz65/#2589. #6534/#6536/#6574 concern
larger blocks and their distinct contracts. #6776 already constructs an
exact-square bounded-error map at n=4; this result is the n=1 sharp radial
classification and does not claim first Gaussian exact-square existence.
#6778 f711bd201a037ba6a7e3fed72d00bfcbf4f0420a is the known tensor
noncommutation obstruction applied above. Exact pins and bounded overlap
coverage are retained; no universal priority claim is made.

The pairing rules are elementary constructive matching, not a generic
new rounding method. A partner is determined by the ring pair, one of four
rotated connector/arc cases and position parity; no growing matching table
or search is an implementation premise. The finite checker is corroboration
of the explicit all-ring proof, not an extrapolation from sampled radii.
No physical graph, clean scratch/head restoration, accelerated native rate,
all-width tensor error propagation, caller admission, selected assumption
discharge or new kappa is claimed. Prior Gaussian/native/compiler notices
remain credited. Substantial OpenAI Codex assistance, Apache-2.0; no human
or formal-kernel acceptance. No remote mutation or independent publication.
