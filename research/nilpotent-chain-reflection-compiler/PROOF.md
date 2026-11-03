# Optimal fixed-involution compilation of a nilpotent chain

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract and theorem

Work over the full formal group algebra F2[C2], where C2={1,g} and g is a
fixed nonidentity involution. Put Q=1+[g], so Q is nonzero and Q^2=0.
Let J_n have ones immediately above its diagonal and zero elsewhere.
The complete endpoint on n arbitrary input roles is

    D_n = I + Q J_n.

Any finite number of additional arbitrary dirty roles is permitted, but the
endpoint on all roles must be I+Q(J_n direct-sum 0). Every extra role must
be restored without residual couplings. Clean initialization, erasure,
discarded roles, other address labels and address-dependent free maps are
excluded. A paid call is I+Q P for a binary rank-one idempotent P.
Arbitrary constant binary invertible scalar maps may occur freely anywhere.

For every positive integer n, the exact minimum paid-call count is

    L_n = 2 floor(n/2).

Thus L_n=n-1 for odd n and L_n=n for even n. This includes L_1=0.
An explicit stream needs no extra role, uses exactly 2(n-1) scalar XORs,
and contains every scalar conjugator and its inverse. Scalar optimality is
not claimed. The executable emits this stream for 1<=n<=64; that bound is
an implementation limit, not a restriction of the proof.

## Lower bound with arbitrary restored dirty workspace

The normalization here is the standard register-model argument retained in
PR2716 and the earlier register lineage. Conjugating a paid call by a constant
binary invertible scalar matrix conjugates P, preserving rank-one
idempotence. Commute all scalar maps to one end. Augmentation [g] -> 1
makes every paid call and the required endpoint the identity, so their
remaining scalar product must be the identity as well.

Because Q is central and Q^2=0, the complete word now satisfies

    product_j (I+Q P_j) = I+Q sum_j P_j.

Comparing the coefficient of [g] in the full formal algebra gives

    J_n direct-sum 0 = sum_(j=1)^L P_j.

Rank subadditivity gives L>=rank(J_n)=n-1. Each rank-one idempotent has trace
one over F2, whereas J_n has trace zero. Consequently L is even. The
smallest even integer at least n-1 is 2 floor(n/2). Dirty padding changes
neither rank nor trace, so the lower bound covers every finite allowed
workspace and every placement of free scalar maps.

The rank, trace and normalization tools are credited background. The new
step is a matching stream for these non-square-zero chain targets.

## Pair adjacent edges

For three consecutive coordinates a,b,c, write e_a,e_b,e_c for the coordinate
columns. The two matrices

    P = (e_a+e_b)e_b^T,
    R = e_b(e_b^T+e_c^T)

are rank-one idempotents. Their defining column/row pairings both equal one.
Their sum is

    P+R = e_a e_b^T + e_b e_c^T.

The repeated diagonal term e_b e_b^T cancels in characteristic two.
It follows in the complete formal algebra that

    (I+Q R)(I+Q P) = I+Q(e_a e_b^T+e_b e_c^T).

No commutation of P and R is assumed. Every cross term vanishes because
it contains Q^2. These two adjacent chain edges therefore cost two calls.

Here is the full chronological coordinate stream, where each addition is
a scalar whole-role XOR and g acts only on the indicated role:

    a += b
    b <- g(b)
    a += b
    b += c
    b <- g(b)
    b += c

For arbitrary initial a,b,c, the first three operations leave
(a+b+g(b), g(b), c). The last three leave

    (a+b+g(b), b+c+g(c), c).

This derives the full dirty-state endpoint without assuming any input is
zero. The stream has exactly two reflections and four scalar additions.

## Complete chain and invoice

Partition the n-1 edges into consecutive pairs, starting with edges
(0,1),(1,2), then (2,3),(3,4), and so on. Use the six-operation stream for
each pair. If n is even, one edge (n-2,n-1) remains. For that edge use the
retained factorwise four-operation stream

    a += b; b <- g(b); a += b; b <- g(b).

It maps (a,b) to (a+b+g(b),b), using two reflections and two scalar additions.
The paired streams can share endpoint roles. Their formal product is still
I+Q times the sum of their edge matrices, since all cross terms contain Q^2.
Thus they compose to D_n in any order and leave every spectator untouched.

There are floor((n-1)/2) pairs and one remaining edge exactly when n is even.
The reflection total is 2 floor((n-1)/2)+2*1_(n even)=2 floor(n/2).
The scalar total is 4 floor((n-1)/2)+2*1_(n even)=2(n-1).
This attains the lower bound and proves the theorem. Reversing the complete
stream gives its inverse, and D_n^2=I by Q^2=0.

At complete stationary primitive prices R for a coordinate reflection and
C for a whole-role scalar XOR, the specified local bills are

    factorwise PR2716 lowering: 2(n-1)R + 2(n-1)C;
    supplied joint lowering:  2 floor(n/2)R + 2(n-1)C.

The exact reduction is (n-1)R for odd n and (n-2)R for even n. It is strictly
positive for n>=3 and R>0. These are primitive-count identities, not measured
runtime or admitted recursive supplier prices. A supplied scalar change of
basis S transports the construction to S J_n S^-1, but S and S^-1 must be
charged. No method for finding or physically hosting a favorable S is supplied.

## Scope and predecessors

ywz65's PR2716 supplies the arbitrary-coupling motivation, Q^2 product identity
and factorwise dirty lowering. Its dihedral tariff and executable are cited,
not audited or replayed. Adam Gall PR1911 and the retained eumemic PR288,
Ali Romman PR468, woklerx PR1443, Gareth Davidson PR1333, Arham Tahir PR1589
and Cinna Davis PR2290 register-model lineage retain credit.

Nick Petalas's older PR4912 proves a different tariff for square-zero
couplings. Its extra rank-saturation obstruction is inapplicable to J_n for
n>=3, because J_n^2 is nonzero. JoyboyBrian's PR5007 changes the workspace
contract to returned clean roles. Nick Petalas's PR5857 reduces scalar work
in that clean square-zero stream. The present result has arbitrary dirty
inputs, requires no clean role, and changes both the endpoint and the
reflection-count question. None of those predecessor executables is imported.

The universal conclusion rests on the written proof. The finite exact checks
corroborate it. Native legality, complete routing/frame/basis/ownership,
precision/tape/stock costs, recursive child admission and the multiplication
theorem remain open. No new kappa, selected-frontier change, independent human
review or formal proof-kernel acceptance is claimed.
