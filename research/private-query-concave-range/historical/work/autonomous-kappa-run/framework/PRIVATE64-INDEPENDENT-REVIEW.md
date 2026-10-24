# Independent audit of the private scalar query optimum

Result: PASS in the stated model. For the fixed retained 112-port E8
matrix `G=R R^T/4` and its fixed binary source encoding, the minimum sum
of private scalar query-frame dimensions is exactly 64. Redundant query
rows do not reduce that minimum over Q, R or C. This is a finite algebraic
result. It supplies no new circuit or exponent saving.

The contract is explicit. In a factorization `G=sum_j u_j f_j`, each query
row f_j has a binary frame F_j that contains every source port in its
support. Cost is `sum_j dim(F_j)`. This becomes a physical copy-cost bound
only if the private transfer pays at least that dimension for each query.
Shared carriers, native blocks, productive ownership and a changed source
encoding or controller are outside this contract.

## Independent exact coverage

The checker imports no producer verifier. It reconstructs chamber
coefficients from the inverse simple-root matrix. It checks integer one-sign
root expansions, all simple reflection images, the 256 simple subsets and
all fundamental support counts. It recovers the quadratic indicator from
the literal 120 labels with a Boolean transform. It checks all 256 values,
its nonsingular polar form, a symplectic basis and positive Gauss sum 16.
It checks every one of the 120 root hyperplane quotients.

A separate projective two-plane enumeration covers all 43,435 rank-seven
frames. It checks every intersection with all 120 root supports. The
maximum is 32; if the root's self port is present, the maximum is 21.
All 1,806,336 large ordered frame-pair unions have size at most 66. The
uniform rank-seven pair-union bound is 68.

The profile checker uses rank multiplicities, descending from rank nine
to rank one. It differs from the producer's nondecreasing-prefix recursion.
It covers all 1,735,600 profiles of total cost at most 63 and reproduces
all rejection counts. It leaves exactly the two stated profiles. It also
checks discrete concavity for every `1<=k<=m<=63`.

The rank-five and rank-six capacities use the uniform argument below.
No second 3,309,747-frame census is claimed. The original census remains
separate evidence. A negative control complements the quadratic sign and
finds an affine four-space with 16 ones, so the positive-sign premise is
necessary for the capacity of twelve.

## Uniform source capacities

The full binary source set is the one-set of an affine quadratic function
q in eight dimensions. Its polar form B is nonsingular and its full
character sum is +16. A rank-r frame has either no odd labels or an affine
odd slice of dimension r-1.

Let a slice have direction L of dimension t, with `4<=t<=7`. Its polar
rank is at least `2t-8`. In the minimum-rank case, put
`A=L intersection L^perp`. Then `dim(A)=8-t` and `L=A^perp`.
The pairing map from `V/L` to `A*` is an isomorphism. Exactly one coset
of L has constant quadratic values along A. The character sum on every
other coset is zero, because translation by a radical vector cancels it.
The sum over all cosets is +16. Thus the one nonzero coset sum is +16,
not -16. This argument retains the constant term of an affine translation.

All higher polar ranks are at least `2t-8+2`. The character-sum magnitude
is at most `2^(t-rank/2)`. The maximum one-counts at t=4,5,6 are therefore
12,20,36. At t=7 only the minimum-rank branch is possible; its maximum
one-count is 64. Lower dimensions use the elementary point count. This
gives retained frame capacities

`[0,1,2,4,8,12,20,36,64,112]`.

Fix a root label p. Its nonself support is the one-set in the seven-dimensional
hyperplane `p^perp` inside odd parity. Exact checks give polar rank six,
constant radical of dimension one and character sum +16. Its quotient is
a six-dimensional quadratic space with character sum +8 and 28 ones.
An affine six-slice that excludes the radical projects onto that full
quotient and has 28 ones. A six-slice that contains the radical projects
onto a five-slice. The coisotropic argument in dimension six bounds that
five-slice by 16 ones, doubled to 32. Smaller slices have at most 32 points.
Thus a rank-seven source frame contained in `p^perp` meets the root support
in at most 32 points. Otherwise its nonself intersection has frame rank at
most six, and has at most 20 points; one self port raises that to at most 21.
Rank-six frames have total source capacity at most 20.

## Code support and the profile screen

The finite chamber argument applies to all real coefficient subspaces.
Choose a generic vector in the subspace so that its zero roots are exactly
the common zero roots. A maximum over its finite reflection orbit puts it
in a chamber. Its zero roots lie in the span of the simple roots with zero
pairing. This span has rank at most the codimension of the coefficient
subspace. The independently checked subset maxima are
`[0,1,3,6,12,20,36,63,120]`.

The unique fundamental direction with full support 57 is a root direction.
Every other active fundamental direction has full support at least 78.
Thus a real non-root query has retained support at least 70. Root directions
have retained support 53 or 56. For complex coefficients, common zeros equal
the common zeros of the real span of real and imaginary parts. That real
dimension is at least the complex dimension. The code support lower bounds
are therefore

`[53,76,92,100,106,109,111,112]`.

Drop zero and dependent query rows, and absorb their coefficients into the
decoder columns. This does not increase source frame cost. The remaining
N queries are independent and span a space U containing the eight-dimensional
Gram code W. Every k-query subset has intersection with W of dimension at
least `k+8-N`. Its support union must meet the corresponding code bound.

Every correction column is nonzero, and the 112 columns are pairwise
nonproportional. The exact identity `R^T R=56I` and distinct root lines prove
this. At most N columns have query incidence one. All others need incidence
at least two. Total query incidence is consequently at least `224-N`.

For m selected rows, a port occurring x times is covered in a random
k-subset with probability
`g(x)=1-choose(m-x,k)/choose(m,k)`.
Its successive increments are nonnegative and decrease. An exchange of
incidence from a larger multiplicity to a smaller one can only increase
the sum of g. The maximum mean union at total incidence `I=112t+r` is

`112-((112-r)choose(m-t,k)+r choose(m-t-1,k))/choose(m,k)`.

Capacities give an upper bound on I. Since g is nondecreasing, that upper
bound is valid even when the actual incidence is smaller. Apply the bound
to the m smallest frames, since every k-subset there is still a subset of
the independent query basis. This proves the average test used in both
enumerations. It is not a heuristic assumption about disjoint supports.

For N=9, a pair of queries intersects W nontrivially. Ranks at most six
and seven have union size at most 56, so such a code vector is a root
direction. Their root intersections cover at most `20+32=52` support ports,
fewer than the minimum 53. This excludes the additional short-pair cases.
The two surviving profiles are nine sevens and one one, one six, eight sevens.

## Nine rank-seven queries

No query lies in W, since its support has size at most 36. The quotient
`U/W` has dimension one. Scale the nine queries to have the same quotient
image. Their eight differences from one query form a basis of W. Every
pair difference has support at most 68. A complex query with independent
real and imaginary coefficient directions would have support at least 76;
a real non-root direction would have support at least 70. Each difference
is therefore a complex scalar times a real root.

Three noncollinear differences lie in a real root plane. The exact norm
equation permits no third line for an orthogonal pair and precisely the
A2 third line for a nonorthogonal pair. Its coefficients force all scales
to agree up to root orientation. Dividing by one common nonzero complex
scalar gives nine real points whose pair differences are norm-four roots.
They form a regular eight-dimensional simplex.

The eight edge labels in a star are orthonormal over F2. Their norm-one
orthogonal complement gives the exact label model
`p_ab=J+e_a+e_b` in nine coordinates. The star at j spans the hyperplane
with coordinate j zero. Every nonincident edge label lies outside it.
The removed coordinate root lines are pairwise orthogonal, so their
simplex edges form a matching of at most four edges. Every star retains
at least seven independent labels; some star retains all eight.

A rank-seven frame at that vertex misses a retained incident port. At this
port, simplex query values have two endpoint values and a common value for
the other seven vertices. Relative endpoint offsets are nonzero opposites.
If one endpoint query is zero, all other eight query values are nonzero.
The missed port is outside its own frame and inside every other frame.

At each of the seven nonendpoint vertices, this port is outside the full
star span. A frame containing it cannot also contain all seven retained
incident star labels. Each such vertex therefore has another missed port
with the same separating property. At least eight vertices are forced.
For each forced port choose a functional that kills its own frame and
has value one on that port. It kills all other forced ports. They are
independent. If eight vertices are forced, the remaining frame contains
eight independent ports; if nine are forced, every frame contains eight.
Both contradict frame rank seven. This closes the nine-query case.

## One rank-one, one rank-six and eight rank-seven queries

For each rank-seven query, its triple with the first two rows intersects W.
No pair in the triple can contain a nonzero code vector: a pair with the
singleton has support below 53, and the six/seven pair has the short-root
contradiction above. Thus the triple intersection is one-dimensional and
uses all three rows with nonzero coefficients. The eight resulting code
vectors are independent because each has a nonzero coefficient of its own
rank-seven row and none of the other seven such rows.

Each vector has support at most `1+20+36=57`, so it is a root direction.
The three frames meet its root support in at most `1+20+32=53` points.
An omitted axis-root direction has support 56 and is impossible. Each
vector is a retained root direction with support exactly 53. Equality
forces disjoint intersections of sizes 1,20,32.

Its self port has binary norm one. If that port belongs to a rank-six
frame, the other nonself ports lie in its rank-five orthogonal subframe;
the intersection is at most `1+12=13`. In a rank-seven frame it is at most
`1+20=21`. Neither can attain the required twenty or 32. Hence the self
port must be the singleton query's port. All eight independent code vectors
are then multiples of that same root direction, a contradiction. This
closes the ten-query case.

## Attainment, extensions and verification limits

Both cases are impossible, so total private frame rank at most 63 is
impossible. The eight coordinate gathers have frame ranks eight each.
They factor G with decoder R/4 and gather R^T. Their total 64 attains the
lower bound. The independent checker reconstructs all eight support ranks.

The published combined note also uses previously reviewed fitting rigidity
to allow other minimal rank-nine binary factors and rank-eight scalar
fitting matrices. Invertible binary changes preserve frame dimensions;
nonzero diagonal scalar input changes preserve all supports. Those
implications are valid. Their separate finite rigidity certificates were
read and remain cited dependencies; this audit does not claim another
full replay of those certificates. The new closures themselves require
only the fixed current G and source labels.

This is a hand proof with exact finite checks, not a Lean proof of the
complete multiplication theorem. No initializer, shared-carrier execution,
native block or productive source interface has been supplied. There is
no new kappa value, runtime measurement or PR claim.

Run the two standard-library checks with assertions enabled:

```sh
venv/bin/python -B framework/private64_geometry.py . framework/PRIVATE64-GEOMETRY.json
venv/bin/python -B framework/private64_profiles.py . framework/PRIVATE64-PROFILES.json
```

Both passed. Commands, exit codes and hashes are in `PRIVATE64-COMMANDS.json`.
Reviewed source hashes are in `PRIVATE64-SOURCE-BINDING.json`. Existing
failed exploratory bounds and the weaker historical q57 screen stay saved.

Prepared with OpenAI Codex assistance.
