# Three relations make the irreducible five-core bridge cancel

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
A separately audited all-length word lemma. The pool theorem is in PROOF.md.

## Exact model and result

Let H be the subgroup of a torsion-free abelian exponent group generated
by the finitely many paid exponents A_j, and put R=F2[H]. Equivalently,
H=Z^m/L for their saturated relation lattice. Replacing an ambient group
by this paid-generated subgroup loses no endpoint monomial: every product
coefficient is supported on paid subset sums. This reduction is essential
for the degree-one kernel assertion below. Rational address ranks are
unchanged. On five scalar coordinates let P,Q
be the two lifts of E12 and T,U the lifts of E34; B is the bridge in the
pool theorem, now 1-based. S=(I+E12)(I+E34) sends the alphabet to
{E11,E22,E33,E44,J5}. Calls are I+([A_j]-1)N_j.

Lemma: if all five projector types occur, the exponent relation lattice
has rank at most three, and the whole endpoint is diagonal monomial, then
deleting all B calls leaves the same endpoint. Each original target is a
sum of a disjoint subset of paid exponents, so total rational target rank
cannot exceed paid rank. Word length and address ranks are unrestricted.
If one projector type is absent, actual joint image has dimension at most
four; no four-dimensional no-saving theorem is asserted.

## Linear kernel

Use independent universal variables u_j=t_j-1. Saturation of the integral
relation lattice L identifies the linear substitution kernel with L/2L
in the associated graded Laurent algebra Sym(H/2H).

The original three independent nonzero off-patterns are E12,E34,off(B).
Their coefficient vectors are LJ=sum bridge variables, M12=sum P/Q
variables, M34=sum T/U variables. Diagonal endpoint puts these forms in
L/2L; their nonempty disjoint supports make them independent. Thus rankL=3
and they form the ENTIRE degree-one relation kernel.

After the shear the endpoint may have off-diagonal entries only E12,E34.
These allowed positions must not be assumed zero during the argument.

## Quadratic quotient

Quotient off-diagonal matrix space by span(off(J5),E12,E34). Universal
constant and linear terms vanish identically in this quotient BEFORE
exponent substitution. Therefore nonlinear substitution terms cannot
repair the universal degree-two term. Its associated-graded image uses
only the linear substitution, whose full kernel ideal is
(LJ,M12,M34). No claim that the actual Laurent relation ideal is linear
is made. This is the #720/#6777 associated-graded step.

For i=1,...,4 define Ki=off(J5 Eii+Eii J5) and
qi=sum_{coordinate calls j of type i} uj*(sum of preceding bridge ua).
The four stars Ki are independent modulo off(J5),E12,E34. If
sum ai Ki=lambda off(J5)+mu E12+nu E34, entries (5,i) give ai=lambda;
entry (1,3) gives a1+a3=lambda, hence lambda=0 and all ai=0.

Bridge/bridge quadratic terms are multiples of off(J5); coordinate pairs
are diagonal. Mixed terms at a coordinate call have prefix and suffix
bridge coefficients. Modulo LJ, these are equal, leaving Ki times the
prefix. Thus qi lies in (LJ,M12,M34) for every i.

## Elimination and chronology

Eliminate the LAST bridge variable using LJ=0. Remaining bridge variables
and all coordinate-call variables are independent. Write qbar_i for the
result. It lies in (M12,M34), but uses only bridge variables and its own
coordinate-call group. That polynomial subring meets this ideal trivially:
choose a variable in the partner group (2 for i1, 1 for i2, 4 for i3, 3
for i4), and a variable in the OTHER pair. Solve M12 and M34 for those
chosen variables. Both generators become zero, while every variable of
qbar_i is fixed. Thus qbar_i is the zero polynomial. Partner nonemptiness
is exactly where the assumption that all four coordinate types occur is
used.

Every proper nonempty bridge prefix is a nonzero linear form in the first
h-1 bridge variables. Each coordinate call has a separate universal
variable. Its coefficient in qbar_i is that prefix, nonzero precisely
when the call lies strictly between the first and last bridge calls.
Hence no coordinate calls are internal, including the h=1 empty-gap case.
All bridge calls are consecutive.

Combine that block. The sheared word is Dleft*[I+([Z]-1)J5]*Dright, with
invertible monomial diagonal Dleft,Dright, and Z the bridge exponent sum.
Entry (5,1), outside the two allowed endpoint positions, is an invertible
monomial times ([Z]-1). Its vanishing forces Z=0 in the torsion-free group.
Thus the bridge block is identity and deleting it preserves the endpoint.

The sheared endpoint is now diagonal, d1,...,d5, with d5=1. Undoing S
produces edge entries d1+d2 and d3+d4. Original diagonality forces d1=d2
and d3=d4; hence S leaves this diagonal unchanged. Assign coordinate type
i's exponents to original target i, with target5 zero. These subsets are
pairwise disjoint. Rational rank subadditivity gives the paid-rank bound.

## Arbitrary-width application

Restrict the whole noncoordinate word to the invariant joint image V.
Every call restricts to a nonzero rank-one idempotent because its image
lies in V and is fixed by it. Thus no call disappears and the exponent
relation lattice is unchanged. The restricted alphabet is exactly the
five-projector normal form of the pool theorem, or a subset if some types
do not occur. Apply the fixed five-projector lemma to this restricted word.

The basis E,w chosen before the shear preserves a diagonal endpoint:
E is four original coordinate axes, V/E is one binary line, and endpoint
invariance plus independence of group-algebra monomials forces all outside
coordinates in w's support to have the same monomial label. The action on
w is that label. Thus the five-dimensional lemma applies. Bridge deletion is an
endpoint-preserving edit of this RESTRICTED word only. It is not asserted
that deleting those calls in the full ambient program preserves all dirty
spectator inputs. For the rank conclusion, the full diagonal endpoint has
identity quotient, and the adapted equal-label basis preserves its target
monomial multiset. Match the restricted targets, with multiplicity, to the
original labels; all remaining labels are zero and receive empty subsets.
Restore free coordinate generators to their original target labels only
via the separately proved split in PROOF.md.

If a projector type is missing from the actual word, its actual joint
image has dimension at most four (at most four rank-one image lines).
If all five occur, bridge deletion gives the disjoint-subset endpoint.
So the two-edge, pattern-rank-three, relation-rank-three candidate either
reduces to at most four active scalar dimensions or has no rank saving.
One-edge/zero-edge and remaining four-dimensional cases stay open.
