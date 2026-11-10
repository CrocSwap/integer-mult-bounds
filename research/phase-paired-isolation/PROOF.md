# Common bases must isolate both cross blocks

This scoped written proof was produced by Nick Petalas. Apache-2.0.
All vector spaces below are finite dimensional. No algebraic closure is needed.

## 1. Exact two-map capacity

Let F be any field, let L,R be invertible n by n matrices over F, and put
A=L^-1 R and N=A-I. Define c(L,R) as the largest k for which invertible
matrices G,H satisfy

    G L H = diag(I_k, B),   G R H = diag(I_k, C),

with both cross blocks zero. B and C are unrestricted invertible matrices.
G and H must be the same for both maps. The requirement concerns every input
column, including arbitrary retained dirt. Then

    c(L,R) = 2 dim ker N - dim ker N^2
           = n - 2 rank N + rank N^2.                         (1)

This is the number of size-one blocks at eigenvalue one in the primary
decomposition of A. The proof below does not use a Jordan normal form.

First reduce simultaneous equivalence to similarity. If the displayed
equalities hold, their relative map is

    H^-1 A H = diag(I_k, B^-1 C).

Conversely, if H^-1 A H has that block form, G=H^-1 L^-1 makes the first
map identity and isolates the same block in the second. Thus c(L,R) is the
largest dimension of an A-invariant identity summand with an invariant
complement.

For an upper bound, write V=X direct-sum Y for any such decomposition.
Then X is contained in K=ker N, N(X)=0, and N(Y) is contained in Y.
Consequently im N is contained in Y, so X intersects im N trivially.
It follows that

    dim X <= dim K - dim(K intersect im N).                   (2)

For attainment, choose X to complement K intersect im N inside K.
Then X intersects im N trivially. Extend X direct-sum im N to a decomposition
V=X direct-sum Y, with im N contained in Y. Because all N-images are in Y,
Y is N-invariant. N vanishes on X, so this is the desired identity summand.
This construction uses only elimination over F and supplies literal bases.

Finally, the restriction of N from ker N^2 onto K intersect im N is onto:
if y=Nv is in K, then N^2 v=0. Its kernel is K. Rank-nullity gives

    dim(K intersect im N) = dim ker N^2 - dim ker N.

Substitute in (2), with equality from the construction, to obtain (1).

## 2. What a completed readout misses

A common unchanged row readout u for I and A requires only uN=0. Its maximum
independent dimension is dim ker N, using row-column rank equality.
It does not impose the other zero cross block. The exact excess over (1) is

    dim ker N^2 - dim ker N = dim(ker N intersect im N).

Thus the readout count is the isolation capacity exactly when eigenvalue one
has no block longer than one. This criterion is local to the stated two-map
contract. A consumer allowed to use the old input later has a different contract.

Adding b identity workspace coordinates replaces A by A direct-sum I_b.
Both nullities increase by b, so c increases by exactly b. If all b workspace
inputs must themselves return as independent unchanged outputs, they consume
those b identity summands. There is no increase in the number of additional
independent unchanged data channels, even if the bases mix data and workspace.
Indeed, any k additional isolated data channels plus b independently returned
workspace channels would give an identity summand of dimension k+b, to which
(1) applies. This is an endpoint statement, not a storage or physical-cost bound.

## 3. Even-q bases in the Gaussian central ring

Let K=Q(i), R=K[q]/(q^4-1), and E=K[q^2], considered as its even subalgebra.
The operation alphabet for this theorem grants arbitrary invertible input and
output matrices over E. This is an optimistic relaxation of dyadic ordinary
basis synthesis. It forbids odd q coefficients in either basis. A restriction
to dyadic coefficients cannot exceed the resulting capacity.

Let M be invertible over R and let s be a unit scalar in R. An isolated scalar
block means G M H=diag(s I_k, D) with G,H invertible over E. At the four
roots q=1,-1,i,-i, put M_z=M(z) and s_z=s(z). All M_z and s_z are invertible.
For z=1,i define

    A_z = (M_z/s_z)^-1 (M_(-z)/s_(-z)),   N_z=A_z-I,
    k_z = 2 dim ker N_z - dim ker N_z^2.

The exact capacity in this relaxed alphabet is

    min(k_1,k_i).                                             (3)

Necessity follows by evaluating even G,H. They have equal values at z and -z,
so each pair has the two-map contract in Section 1 after scalar normalization.
For sufficiency, choose pair bases attaining the smaller k, truncating a larger
isolated block if necessary. The two even idempotents

    e_plus=(1+q^2)/2,   e_minus=(1-q^2)/2

interpolate their bases as G=e_plus G_1+e_minus G_i and similarly for H.
Each pair basis is invertible, so the interpolated bases are invertible over E.
The four endpoint evaluations have the required scalar block and both cross
blocks zero. Since q^4-1 has four distinct roots in K, these evaluations are
injective on R. They prove the full ring identity. Formula (3) follows.

This statement applies when ordinary charts are restricted to even q and both
zero cross blocks are actually required. It does not assert those hypotheses
for every compiler, retirement mechanism or current caller.

## 4. Sharp two-field obstruction

Let J=E_12 on K^2, so J^2=0, and set

    M(q)=I+((1+q)/2) J,   M(q)^-1=I-((1+q)/2) J,   s(q)=1.

The second output is exactly the second input at every q. Nevertheless, it
cannot be an independently isolated identity channel using even-q bases.
At q=-1 and q=1 the maps are I and I+J. Their relative defect is J,
which has nullity one and square nullity two. Formula (1) gives capacity zero.
That single pair already rules out a scalar identity block over R.

The explicit remaining dependence is y_1=x_1+((1+q)/2)x_2. Reading y_2=x_2
does not remove x_2 from the retained first output. The example has dyadic
coefficients and a literal inverse; allowing every Gaussian rational even
basis still cannot separate it.

For m independent copies and b restored identity workspace coordinates,
the q=-1,1 relative matrix is (I+J) direct-summed m times, then I_b.
Its nullities are m+b and 2m+b. Its exact simultaneous identity capacity is b,
attained by the workspace coordinates. Hence none of the m apparently
completed data readouts can become an additional independently isolated
channel under this contract, for any finite b. This is an all-dimension
scoped obstruction, not a finite search failure.

The same example can have a productive central Gaussian scalar rather than
identity. Set M_G(q)=q^-1 M(q), with desired scalar s(q)=q^-1. Its completed
second output is q^-1 x_2 and its literal inverse is (I-((1+q)/2)J)q.
Scalar normalization returns exactly the preceding data maps. If b arbitrary
dirty workspace coordinates are independently restored by identity, their
normalized maps at q=1,-1 are I_b and -I_b. The relative matrix therefore has
the data blocks I+J or their inverses, and workspace block -I_b. The latter
has no eigenvalue one in characteristic zero. Both data nullities are m and
2m, regardless of b, so the exact capacity for a q^-1 scalar block is zero.
Thus this stronger version has completed Gaussian readouts but no isolated
Gaussian channel, for every finite amount of restored identity workspace.

## 5. Evidence and credit boundaries

Invariant complements, rank-nullity, elementary divisors and interpolation by
orthogonal idempotents are classical linear algebra. No literature-wide
priority is claimed for these tools or the general direct-summand formula.
The contribution is their explicit sharp capacity criterion for the paired
ordinary-chart contract, its constructive bases and the workspace-stable
Gaussian example separating readout from independent isolation.

The small-field and rational computations in verify.py corroborate the written
theorem. They do not establish its universal quantifiers by enumeration.
No predecessor scientific result is replayed as a deliverable. No particular
published retirement is rejected. Physical caller binding, dyadic synthesis,
intermediate chronology, paid jobs, precision, ownership, compiler closure and
analytic recovery remain outside the theorem. No new kappa follows.
