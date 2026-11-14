# Universal arbitrary-order generic Stein-rank lower bound

Written universal theorem with finite corroboration. The canonical source base is
`e54523517d0f03e58352e647c403a5af3e525a57`. This theorem concerns an explicitly
defined unshifted two-point tensor family; it does not identify an actual
fine-prime caller or assert stability under rounding. No new kappa.

Let d>=1, N=2^d and let x_0,...,x_(N-1) be any ordering of F_2^d. Set
H(q)_ij=product_(k:(x_i xor x_j)_k=1) q_k and E(A)=A-ZAZ^T, where Z is
the ordinary nilpotent one-step lower shift. The claim is

`rank_(Q(q_1,...,q_d)) E(H(q)) >= 2 ceil((N+3)/5)`.

Every fixed d admits a proper real algebraic exceptional set outside which
the bound holds simultaneously for every vertex ordering and for the
corresponding exact inverses. In particular the simultaneous good set is
dense and full-measure in (0,1)^d. This does not prove full rank N, nor a
pointwise theorem for every distinct tuple. The proof below gives a minor
with an integer coefficient ±1, hence a formally nonzero polynomial over
every field. It does not assert the existence of a good point in each
finite field.

## 1. Translation matchings and an explicit minor

For each nonzero mask v, let M_v be the perfect matching on positions
whose vertices carry labels differing by v, and let P_v be its permutation
matrix. Let m_v count its edges joining consecutive positions. The path
directions x_i xor x_(i-1), i=1,...,N-1, therefore have multiplicities m_v,
with sum m_v=N-1 and m_v<=N/2.

Form a multigraph by putting the original matching M_v in color + and its
shift by one position in color -, dropping the unique original pair that
meets N-1 before shifting. The shifted matching misses exactly vertices 0
and mate_v(N-1)+1. Every other vertex has one edge of each color. There is
one open path and C_v closed alternating cycles; a double parallel edge is
a cycle of length 2. The open path has an even number of vertices because
both endpoints meet original matching edges. All cycles are even.

The signed adjacency matrix is E(P_v). A parallel cycle contributes the
zero 2-by-2 matrix. On each longer cycle, the alternating signs give recurrence
`z_(j+1)=z_(j-1)` in its kernel, leaving exactly two dimensions over every
field. The open even path is nonsingular. Consequently

`rank E(P_v)=N-2C_v`.

There is a stronger certificate: remove two adjacent vertices from each
closed cycle and keep the whole open path. The induced graph is a disjoint
union of even paths, with all edge coefficients ±1. Each even-path adjacency
determinant is ±1, by its unique perfect matching. Thus the retained
principal minor, of size r_v=N-2C_v, has determinant ±1. This includes
characteristic 2, where a parallel +/− pair still cancels.

Write q^v=product_(k:v_k=1) q_k. Since
`H(q)=sum_v q^v P_v`, the same principal minor of E(H(q)) has coefficient
±1 at monomial `(q^v)^r_v`. Indeed every determinant term uses r_v entries,
each entry is multilinear, and reaching exponent r_v on every selected
variable and zero on every other variable forces every selected entry to
use exactly q^v. Its coefficient is precisely the signed-adjacency minor.
Therefore generic rank is at least max_v (N-2C_v).

## 2. Two complementary cycle counts

Put m=max_v m_v. Every closed component contains an original matching
edge that is not adjacent in the linear ordering. If all its original edges
were adjacent, start at its least vertex k. Its original edge must lead to
k+1; the shifted edge then leads to k+2. The next original edge is forced
to k+3, and so on. This strict ascent cannot close inside a finite component.
Distinct cycles use distinct original edges, so

`C_v <= N/2-m_v`, and hence `max_v rank E(P_v) >= 2m`.

Let L_v be the number of parallel two-cycles. Each other cycle has at
least four vertices and the unique open path has at least two. Thus

`C_v <= (N-2)/4 + L_v/2`.

A parallel component on positions a,b, both positive, occurs exactly when
their path directions agree:

`x_a xor x_(a-1) = x_b xor x_(b-1)`.

Its unique translation mask is v=x_a xor x_b. Conversely each such pair
gives exactly that parallel component. Therefore

`sum_(v!=0) L_v = sum_(u!=0) binom(m_u,2)`.

Since every m_u<=m and their sum is N-1, this is at most
`(m-1)(N-1)/2`. Averaging the cycle bound over the N-1 masks gives

`min_v C_v <= (N+m-3)/4`,

and so `max_v rank E(P_v) >= (N-m+3)/2`. Combining both estimates yields

`max_v rank E(P_v) >= max(2m,(N-m+3)/2) >= (2N+6)/5`.

Every rank r_v is even. Rounding upward to an even integer proves
`max_v r_v >= 2 ceil((N+3)/5)`. The formula also gives the correct complete
rank 2 and 4 for N=2 and4. No asymptotic omission of small dimensions is used.

## 3. Quantifiers, inverse transfer and cost scope

For each ordering choose one of the certified nonzero minor polynomials.
There are finitely many orderings; their product is a nonzero polynomial
over R. Away from its zero set, every ordering obeys the bound. The zero
set of a nonzero real polynomial has empty interior and measure zero,
by induction on the number of variables and the one-variable root bound.
Thus the positive cube contains a dense full-measure set of simultaneous
good tuples. This is the precise meaning of generic here.

For any invertible A, the block matrix [[A,Z],[Z^T,A^-1]] has Schur
complements E(A) and Erev(A^-1)=A^-1-Z^T A^-1 Z. Its two rank factorizations
give rank E(A)=rank Erev(A^-1). With the reversal permutation J, JZJ=Z^T,
so rank E(A^-1)=rank E(JAJ). Reversal is another allowed ordering. Hence
the uniform all-order forward result implies the uniform all-order inverse
result, without a persymmetry premise. H(q) is positive definite for
0<q_i<1 since each 2-by-2 factor has eigenvalues1±q_i.

For the ordinary lower/upper triangular Toeplitz factors L(u),U(v),
`E(L(u)U(v))=u v^T`. Thus an exact sum of k such products requires
`k>=rank E(A)`. Materializing both full length-N generator vectors costs
2kN scalar slots, giving an all-order generic Ω(N^2) count for this format.
No general algorithmic runtime lower bound, free gauge, source-parameter admission,
conditioning margin, rounded theorem or multiplication-kappa change follows.

## 4. Discovery limits and controls to preserve

The stronger determinant-not-identically-zero claim remains unproved for arbitrary d.
Coordinate-only connected-graph certificates cover4368/5040 translated
normalized d3 orders. Allowing every nonzero translation mask covers all
5040, but explicit d4/d5 orders have every mask graph disconnected.
These are failures of a sufficient certificate, not generic counterexamples.

At the actual rational tuple q=(1/2,1/3,1/5), the ordering
[0,1,2,3,7,5,6,4] has exact rank 6, not 8. Its determinant is
`product_i(1-q_i^2)^2 (ab-ac-bc)^2 (ab+ac+bc)^2`.
The standard Gray ordering has different squared factors. Distinct
parameters alone do not certify full rank, and finite modular nonzero
checks do not settle a universal all-d determinant theorem.


## 5. Quantitative statement and relation to preceding work

For each fixed positive d, let N=2^d and r_N=2 ceil((N+3)/5). There is a
nonzero integer polynomial F_d in d variables such that, for every real
q in (0,1)^d with F_d(q) nonzero and every permutation of the N vertices,
both forward and inverse ordinary Stein ranks are at least r_N. The same
single exceptional set covers inverse ranks, because reversed orders were
already included in the finite product. For the formal forward theorem,
every characteristic has a certified minor with coefficient +1 or -1.
A single nonzero polynomial over a finite field can vanish at every point;
no finite-field pointwise conclusion is being inferred.

The bound is nontrivial in every positive dimension: for N=2,4,8,16,32,
the lower bounds are 2,4,6,8,14. It is a lower bound, not a formula for the
minimum rank. The finite all-mask check establishes full generic rank for
d<=3, but its observed coverage is not used in the all-d argument.

The earlier published lexicographic theorem at
[326844a3e0c570fdafa4f3737095cd37154743a6](https://github.com/CubeJerry/integer-mult-bounds/commit/326844a3e0c570fdafa4f3737095cd37154743a6)
only controls lexicographic flattenings. The orbit constructor at
[8f1a09fb4f696bd5f20e1953210936308571416e](https://github.com/CubeJerry/integer-mult-bounds/commit/8f1a09fb4f696bd5f20e1953210936308571416e)
shows that changing the order can drastically reduce displacement rank in
homogeneous factors. The optimal symmetry-cycle scale at
[2ae2fa14eeefe301652f62313b137a97036ab13d](https://github.com/CubeJerry/integer-mult-bounds/commit/2ae2fa14eeefe301652f62313b137a97036ab13d)
and the heterogeneous classification at
[be76d6ae53fc887f977a04ceaa6ef56bb9e98fb7](https://github.com/CubeJerry/integer-mult-bounds/commit/be76d6ae53fc887f977a04ceaa6ef56bb9e98fb7)
control certificates built from one global permutation symmetry. The present
proof removes that ordering restriction for its explicit generic binary
family. It does not replace those results' pointwise parameter statements.
For d>=2, equal factors form a proper algebraic subfamily, so this generic
theorem alone gives no pointwise conclusion there. There is no conflict
with the constructive homogeneous orderings.

Classical displacement generators, Schur complements, alternating matching
components, polynomial coefficient extraction and the zero-set argument are
background. The contribution is their stated all-order binary-tensor
combination and the explicit cycle-count bound, rather than a claim that
these ingredients were invented here. For multilevel tensor/displacement
background, see Olshevsky, Oseledets and Tyrtyshnikov, *Tensor properties of
multilevel Toeplitz and related matrices*, Linear Algebra and its
Applications 412 (2006), 1-21,
[DOI 10.1016/j.laa.2005.03.040](https://doi.org/10.1016/j.laa.2005.03.040).
Their tensor separation setting is not a proof of the theorem above.
The bounded repository/literature check is recorded in OVERLAP.md; no
worldwide priority or exhaustive-search claim is made.

## 6. Why the representation floor is a scoped obstruction

For an N-vector u, L(u) has entry u_(i-j) when i>=j and zero otherwise;
U(v) has entry v_(j-i) when j>=i and zero otherwise. In their product,
subtracting the (i-1,j-1) entry cancels all summands except u_i v_j.
The same statement at the first row or column follows because the shifted
matrix is zero there. This proves E(L(u)U(v))=uv^T with the stated one-step
shift and no cyclic wrap. Rank subadditivity then gives the term lower
bound for an exact sum of such products.

Conversely, the identity A=sum_(t=0)^(N-1) Z^t E(A) (Z^T)^t follows by
telescoping and Z^N=0. A rank factorization E(A)=sum_j u_j v_j^T therefore
recovers an exact sum of that many L(u_j)U(v_j) terms. Thus this ordinary
minimal term count equals the ordinary Stein rank over a field. If both
vectors of every term are stored densely and separately, the format uses
2kN scalar slots. This is the only storage lower bound asserted here.
It permits sharing, implicit formulae, sparse/compressed vectors, tensor
operations, alternative displacement operators and different algorithms
outside this format. Transport, source access, generator construction,
coefficient precision, restoration and recursive calls require their own
paid analysis even when a representation exists.

This theorem does not discharge any of `native_all_columns`,
`owned_erasure`, `compiler`, `precision_tape` or `analytic_recovery` at the
selected multiplication caller. A generic open dense set need not contain
a prescribed discrete fine-prime parameter sequence; an algebraic
exceptional set may contain that entire sequence. No minimum singular
value, tolerance radius, rounded rank, physical implementation, full-system
recurrence or kappa improvement is supplied. The proof only narrows one
possible constant-generator route for the explicitly stated family.

## 7. Failure controls and exact finite evidence

The standalone standard-library verifier checks all translation-normalized
orders in dimensions one through three, all nonzero masks and the two
cycle inequalities. Its signed displacement is formed directly from a
permutation matrix rather than reconstructed from graph components. It
checks each retained principal determinant exactly by integer Bareiss
elimination and checks the predicted rank over characteristic 2. Small
cases also use rational elimination and explicit polynomial expansion.
These computations corroborate the proof; they do not supply its universal
quantifier.

The preserved negative controls serve different purposes:

- All q_i=0 gives H=I and Stein rank 1. All q_i=1 gives the all-ones
  matrix and rank 2 when N>=2. Genericity is essential.
- At q=(1/2,1/3,1/5), the stated order and the standard Gray order both
  have rank 6. Distinct positive parameters do not imply full rank.
  Replacing 1/5 by 1/7 makes both exact ranks 8.
- The order [0,1,2,3,4,6,5,7] has no connected coordinate-mask graph,
  yet an arbitrary translation mask supplies a full-rank coefficient.
- The recorded d=4 and d=5 orders have no connected graph even when
  every nonzero mask is allowed. The weaker certified rank still obeys
  the theorem. This blocks promotion of the connected-graph sufficient
  test to an all-d full-rank proof.
- Ignoring a parallel pair's cancellation, deleting just one vertex of
  a cycle, replacing the nilpotent shift with a cyclic shift, or dropping
  a determinant entry causes the corresponding exact certificate check
  to fail. These are semantic mutations, not alternative theorems.

For i,j>0, the polynomial E(H)_ij is zero exactly when the consecutive
path directions at i and j coincide. The resulting generic support is a
complete multipartite graph, with position 0 connected to every other
position. Each direction class has size at most N/2, so the support admits
a perfect matching. That observation only establishes structural rank:
its entries share variables and determinant terms can cancel. It is not
used instead of the explicit coefficient +1/-1 certificate.

## 8. Credit and remaining proof obligations

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
The lead researcher proposed the initial all-order question, the
coordinate-specialization/matching route and complementary support and
inverse observations. The worker derived the all-mask principal-minor
certificate and the combined counting bound, wrote the proof and primary
replay, and retained failed stronger criteria. The lead and a separate
research agent independently checked the critical proof. Their reports
are separate review evidence, not independent human or formal-kernel
certification. Earlier scoped tensor, orbit and source packages retain the
credit and exact pins listed above; their scientific programs are not
replayed as this contribution's deliverable.

The full generic rank-N conjecture remains open for arbitrary d. A stronger
rank bound or a generic deficient-order family would be material progress.
Source-specific parameter nonvanishing and a quantitative rounding margin
would each require a new theorem. A useful algorithmic successor must
price an implicit or alternative-format application at an actual caller,
including setup, precision, access and restoration; the dense-format
obstruction alone is not a multiplication lower bound.
