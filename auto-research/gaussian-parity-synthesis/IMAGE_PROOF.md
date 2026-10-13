# An image-conditioned scalar rewrite for PR46's mixed centers

Pinned source: CrocSwap/integer-mult-bounds PR46, head
`71b6c960c89295e952522dd44111df9cfc51ae90` (chafreaky branch).
The underlying complex producer is retained from the preceding copied-center
work; PR46's new weighted bit carrier matching is not a new complex producer.
Credit all authors/licenses recorded in its NOTICE. The executable here
imports the credited producer only to regenerate its archived DAG. A separate
integer coefficient verifier reconstructs every root from that archive.

## Exact identity and its image assumption

Let X_U be arbitrary Gaussian integer numerators on the 3276 triples of
28 points, in one common scalar frame and one common incoming grid.
Set T=sum_U X_U and G_i=sum_(U contains i) X_U. Every source occurs in
three G_i, so sum_i G_i=3T. For the first d=19 points store D_i=T-G_i;
for the remaining nine store B_i=2G_i. Consequently

    N=sum_(i>=19) B_i - 2 sum_(i<19) D_i = -32T.

Recovering T by N/(-32) is exact on this producer image. Recovering G_i
by B_i/2 outside the first 19 points is exact; inside use T-D_i.
This removes five binary denominator obligations from the total-recovery
division. It is the ramified Gaussian ideal statement N in 2^5 Z[i],
equivalently N in (1+i)^10 Z[i] up to a unit.

For target triple S, let A_S be the sum of sources disjoint from S and
E_S the sum of sources intersecting S in exactly two points. The complete
scalar correction is

    F_S(PX)=(sum_(i in S) G_i - T + A_S - E_S)/2 = X_S.

For each source U, j=|U intersect S| gives twice its coefficient as
j-1+[j=0]-[j=2], which is 2 when U=S and 0 otherwise. Combining this
numerator before its final divide by 2 therefore makes that divide exact.
The complete scalar injection uses no extra fractional bits relative to
the incoming common grid. This does not remove ordinary magnitude growth.

## Arbitrary dirty auxiliaries

Let a be any dirty Gaussian vector of the retained root-role dimension.
The transparent old/new scalar wrapper uses F(a+PX)-F(a). Because F is
linear, this equals F(PX)=X. A common-frame reference implementation may
first form delta=(a+PX)-a, then apply the exact image divisions above.
All a cancel before division. Adding the returned X to arbitrary old output
values gives the prescribed scalar injection. Subtracting PX from the
updated auxiliary vector restores every a exactly.

The producer-image premise is essential. An arbitrary lone B center of
value 1 gives N=1 and T=-1/32; some scatter outputs need 1/64. Likewise,
forming the difference of old B=1 and differently phased new B=i when
there is no fresh source gives i-1, not a valid fresh producer vector.
The old and new values must be expressed in one common scalar frame.
Matching old/new phases separately on each role is not sufficient if their
phases differ across roles: an impulse at (0,1,19) has B_19=2, and rotating
that center alone to 2i changes N from -32 to -34+2i. The necessary image
condition fails. A common global Gaussian-unit phase commutes with the
scalar producer, but arbitrary role-dependent frames require transport.

The divisibility assertions are exact-arithmetic guards. They are not, by
themselves, a complete membership test for the whole producer image. The
identity theorem is conditioned on delta=PX, established by the source DAG.
The implemented `checked_fused_delta` obtains a complete image membership
test by reconstructing candidate X=F(delta), regenerating P(X), and checking
equality with delta. If QP=I, then delta belongs to the Gaussian integer
image of P exactly when P(Q(delta))=delta and Q(delta) is integral. Its
extra pass performs 78,608 Gaussian additions in this archived evaluator;
it is not included in the fast-path quotient count and is never claimed
free. `image_conditioned_fused_delta_fastpath` may skip it only when the
caller supplies the independently certified premise delta=P(X).

A divisible off-image negative control sets just one disjoint root to 2
and every other root to zero. Every local division succeeds and yields a
candidate with one source coefficient equal to 1. Regenerating its producer
roots gives many nonzero centers and side roots, so P(Q(delta))!=delta.
The full guard rejects it, proving why local parity checks alone are weaker.

## Scope of the rewrite

The published physical network has role-dependent phase frames, child
transformations, copied streams, and a paid ordered tape schedule. This
reference scalar rewrite does not demonstrate that those physical
operations can be reordered so the two scatters fuse at zero cost.
Implementing it inside that network requires a matched-frame boundary or
explicitly paid transports and updated magnitude/stream accounting.
No new kappa, asymptotic complexity, or measured physical-network speedup
follows from the scalar algebra alone. It is a concrete, verified candidate
rewrite and an audit of a real fixed producer, not a replacement network.

## Full fixed producer verification

`verify_mixed_center_image.py` calls the pinned h=28,d=19 generator, then
reads its portable binary archive independently. Every addition is replayed
using two integer coefficient bitplanes. Bitplanes hold exact coefficients
0,1,2; overlap checks reject a coefficient exceeding two. The verifier
proves, for every input simultaneously, the disjoint roots, pair-star roots,
doubled G centers and disjoint D centers, with no finite-field arithmetic.
It separately checks every one of the 3276^2=10,732,176 source/target
coefficient identities. The producer archive has 81,885 nodes and 78,608
addition nodes, of which 78,437 are active; the 13,132 retained output
roots include the 28 centers. The scalar producer's unmatched role count
is 91,569; the physical matched count 78,790 is a separate inherited
carrier-compilation certificate and is not re-proved by this program.

Six deterministic trials use an impulse or signed Gaussian source vectors,
arbitrary dirty root vectors, and arbitrary dirty output vectors. All
3276 targets in every trial agree with an independent exact Fraction
evaluation of F(a+PX)-F(a). All auxiliaries restore exactly. The generic
common-frame reference reaches six extra fractional bits; the fused
image-conditioned reference uses zero. An off-image root, mismatched phase
frame, mutually incoherent role phases, and a locally divisible off-image
role vector are rejected; removing the intersection-two correction fails
the complete coefficient identity.

## Explicit reference operation count, without a runtime claim

For one coefficient over all targets, the generic reference evaluates old
and new scatters separately. Each evaluation shares T, T/2, nine B_i/4,
nineteen D_i/2, and half of each of 13,104 side roots. This is

    2 * (1+1+9+19+13104) = 26,268 Gaussian quotient calls.

The fused reference performs one N/(-32), nine B_i/2, and one complete
numerator/2 for each target:

    1+9+3276 = 3,286 Gaussian quotient calls.

These are calls in two specified reference schedules, not a lower bound
on the published program or an optimal compiler. In particular a different
reference could collect each F_S numerator over 64 and use fewer quotient
calls while retaining the six-bit denominator; quotient counts alone are
not a tape cost. The stable demonstrated gain is the removal of six extra
fractional-bit obligations in this exact common-frame scalar wrapper.

## Reproduction

With standard-library Python, the bundled files in `references/pr46`, and
the mandatory expected SHA-256 manifest `SOURCES.json`:

    python verify_mixed_center_image.py --output <fresh directory>

Alternatively, use Git to provide a full pinned upstream checkout:

    python verify_mixed_center_image.py --upstream <PR46 checkout at pinned head> --output <fresh directory>

An explicit external checkout must have the pinned Git head as well as
every expected source hash; an uncommitted source mutation is rejected.
The output `receipt.json` records hashes of the manifest, source, generated archive,
counts, precision results, negative controls, and elapsed evaluation time.
The run is an independent arithmetic verification of this fixed scalar
producer. Universal image-conditioned identities are also being formalized
separately in Lean; neither artifact formalizes the general physical network.
