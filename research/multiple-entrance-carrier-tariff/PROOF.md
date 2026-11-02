# Exact transport price for distinct entrance lines

This contribution was produced by Nick Petalas. Apache-2.0.

## Model and result

Let V be a finite-dimensional vector space over any field. A frame is a
linear subspace. The declared transport rank is the subspace distance

    d(A,B) = dim A + dim B - 2 dim(A intersect B).

A route is any finite sequence of frames, starting at zero and ending at C.
It must visit each of m specified distinct one-dimensional subspaces at least
once. Arbitrary intermediate subspaces and repeated visits are allowed. Their
ordering is free. A rank-r transport costs H(r), where H is nonnegative,
nondecreasing and subadditive on the nonnegative integers, and H(0)=0.
The bill is the sum over every transport, including the final arrival at C.

Write c=dim C. If m=0, the exact minimum is H(c). If m>0, it is

    H(1) + (m-1) H(2) + H(c-1),   if some required line lies in C;
    H(1) + (m-1) H(2) + H(c+1),   otherwise.

The first case necessarily has c>=1. The second never has c=dim V.
This includes H(r)=r^s for every 0<s<=1. For linear cost, the minimum is
c+2(m-1) in the first case and c+2m in the second.

This is an exact theorem in the declared complete transport graph. For a
restricted native route table it remains a lower bound whenever each legal
transport costs at least H(d(A,B)); attaining the bound then needs a legal
realization of the displayed direct transitions. No such supplier admission
is inferred here.

## Proof

The subspace distance is a metric. For the triangle inequality, the subspaces
A intersect B and B intersect C inside B give

    dim(A intersect C)
      >= dim(A intersect B) + dim(B intersect C) - dim B.

Substituting this inequality proves d(A,C)<=d(A,B)+d(B,C).
Monotonicity and subadditivity therefore give

    H(d(A,C)) <= H(d(A,B)+d(B,C))
              <= H(d(A,B)) + H(d(B,C)).

Thus replacing any segment of a route by the direct transition between its
endpoints cannot raise its bill. Retain the first occurrence of each required
line, in its existing order, together with the start and final endpoint.
Shortcut everything else. This preserves all requirements, even if C occurred
earlier in the route. There is now one transition from zero to a line,
m-1 transitions between distinct lines, and a last transition to C.

The first transition has rank one. Every transition between distinct lines
has rank two. The last rank is c-1 if its line lies in C, and c+1 otherwise.
If at least one required line lies in C, monotonicity makes such a line a
cheapest possible last line. If none does, every possible last line has the
same last rank. These facts give the lower bounds above.

Choose any ordering with a contained line last when one is available. The
route zero, the ordered required lines, C attains the displayed bill in the
complete graph. With no requirements, direct travel attains H(c), and the
same shortcut argument proves its lower bound. This proves the theorem.

## Consequence for shared input-lift carriers

DreamingOfClouds' PR6375 shares one carrier between two helper responses at
the same entrance line. The native input-lift mechanism and all its word,
phase, target and caller claims remain credited premises. This result asks
about extending the transport contract to several distinct entrance lines.

Within the declared metric contract, a carrier with the same start zero and
destination C cannot visit two distinct entrance lines for the original
linear bill c, even when both lines lie in C. The exact minimum is c+2.
For m contained distinct lines, every additional line beyond the first costs
exactly two more rank units. Repeating the same line adds no visit requirement.
For a power tariff the precise bill is 1+(m-1)2^s+(c-1)^s, with 0^s=0.

This is a transport obstruction, not a sign conclusion for a complete signed
invoice. Productive target changes, other paid jobs and possible changes of
carrier identity still matter. A scalar response can also be changed so that
several responses use one common line; that changes the prescribed visits.
The theorem does not exclude that mechanism.

## Credit and proof obligations

The distance formula and one-detour inequality are predecessor work in
DreamingOfClouds' format-limits-corrected note, section C.2, with its retained
Clifford/endpoint-gauge lineage. Ali Romman's PR6349 supplies the native
input-lift move class. DreamingOfClouds' PR6375 supplies the shared-carrier
question and examples, retaining Ali Romman PR6372/6353/6348 and the P104
contributors. The new step is the exact multiple-required-line route tariff
over arbitrary intermediate frames and all stated tariffs.

No novelty is claimed for the subspace metric, triangle inequality or
subadditivity. Finite checks corroborate this written uniform proof; they do
not replace its quantifiers. Scalar delivery, native absolute phases, owned
restoration, a complete paid/productive profile, compiler closure, precision,
all-width implementation and analytic recovery remain outside this result.
There is no complete multiplication theorem, kappa claim or frontier change.
