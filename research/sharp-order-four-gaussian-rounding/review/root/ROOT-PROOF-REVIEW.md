# Root review of the sharp order-four Gaussian theorem

Canonical base: e54523517d0f03e58352e647c403a5af3e525a57.
Status: mathematical review passed; final author freezes and package checks
remain separate publication gates. No selected caller or kappa admission.

## Scope and proof roles

The root proposed the annular matching and 36-vertex parity mechanism, and
wrote check_candidate.py before reading either worker implementation. The
proof role supplied the reduction from an arbitrary exact-sum error-one map
whose square is wire swap to a quarter-equivariant matching on the fixed
sum-one fiber. The constructive review independently checked the full ring
partition, map identities, radial maximum, and matching-class lower bound.
Its review explicitly excludes the arbitrary-map reduction. Root reviewed
that reduction directly below. These are distinct AI checks of a shared
proposal, not blind, human or formal-kernel verification.

## Critical universal reduction

Let H=[[1,1],[1,-1]], T=H/2, J(x,y)=(-y,x), Q=-J. On the fixed
sum s=(1,0), integer pairs correspond exactly to d=(odd,even). The map
f of differences satisfies f^2=-I because F^2 is wire swap and the sum
is fixed. Thus f is a bijection; its fourth power is the identity.

The maps L=TJ and T carry this difference coset respectively onto the
even-sum and odd-sum colors A,B of the half-integer grid. Exact sum
and error at most one imply f(d)-Jd=(+/-1,+/-1). Consequently
M_A=T f L^{-1}:A -> B is a bijection, and M_A(t)-t is an axis unit
vector. The source color is even because sum(TJd)=-Im(d).

Since T J T^{-1}=-J, conjugating f by L gives g=Q M_A on A. From
g^2=Q^2, left multiplication by Q^{-1} gives M_A Q M_A=Q on A;
all intermediate color domains are defined. Define M on B by M_A^{-1}.
For a in A, the identity gives M_A^{-1}(Q a)=Q M_A(a). For b=M_A(a)
in B, it gives M_A(Q b)=Q a. These are precisely M Q=Q M on both
colors. No relationship between different fixed-sum fibers was assumed,
and no phase covariance or periodicity premise was added.

## Boundary lower bound and direction of slack

The box max(|t1|,|t2|)<=5/2 has 36 vertices. Every orbit of a matching
edge under quarter-turn consists of four distinct disjoint edges: a
half-turn-fixed edge would have antipodal half-grid endpoints at distance
at least sqrt(2), whereas edges have unit length. Overlapping geometric
orbits cannot be matching orbits. If every edge stayed in the box, the
box would split into 8-vertex blocks, contradicting 36 mod 8 = 4.

Any crossing unit edge changes |t_j| from 5/2 to 7/2, with the other
coordinate at most 5/2. At s=1 the pair norm squared is 1/2+|t|^2.
The crossing radial difference is minimized at the largest allowed other
coordinate, giving sqrt(19)-sqrt(13). Each matching edge has an A
endpoint. Its F step has this absolute radial change because Q preserves
norm. If the F step is inward, the next one is outward by the same amount,
since F^2 is wire swap. This proves the forward lower bound for every F
in the stated class, as well as the bilateral lower bound.

## Upper bound and interface checks

All ring vertices are covered: each pair of rings uses four connectors,
four inner arcs of length 4m, and four outer arcs of length 4m+2. The
inner m=0 arcs are empty. Rotation closes the edge set and each vertex
has a unique mate. The transformed next step is Q M, whose square is -I.
Tangential edges have radial jump below 1/sqrt(2). Connector jumps are
maximized over c>=1/2 at c=1/2; their derivative sign is
-2a^2+2a+1/2. Among a=1/2,5/2,9/2,... the largest occurs at 5/2.
The exact squared norms 13 and 19 occur on the displayed four-cycle.

The actual inverse is swap composed with F. At real input (1,0), an
additional conjugation-as-inverse identity would force the outputs to be
conjugates and their sum to have even real part, contradicting sum one.
This obstruction needs neither the error premise nor phase covariance.
The established global unit covariance and integral-image exactness also
trigger the previously proved #6778 same-map row/column obstruction.
These limitations do not imply an impossibility for ordered callers,
different per-axis maps, or changed representations.

## Evidence boundary

The root exact implementation uses doubled odd coordinates and a direct
ring/side/parity rule, not a generated matching table. Its recorded normal
and optimized runs cover 1,024 half-grid points, 6,561 Gaussian pairs,
40 deterministic large cases through 1,024 bits, and all 24 boundary edges.
The all-input theorem rests on the preceding argument and the supplied
proof. No machine-model cost follows from Python's unbounded integers.
