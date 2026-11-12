# True source-rank buckets and whole complement invocation ports

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
This is an offline logical interface theorem. No new kappa, physical
permutation, actual selected template or complete assumption discharge is
claimed.

## 1. Pinned obligation and exact domain

Use the separated finite rule and source-row codec at CubeJerry commit
`c5bcb6dc792f5fe4d8abe89a2a2854f148b09f2c`,
`research/lockstep-source-row-index/`. Its occurrence-codec dependency is
`91246e5131152ccb1f64a969c36706360861f821`. Both executable inputs are retained
unchanged and checked by hash. The parent note is canonical
`research/kappa-rebuild/architecture/FINITE-PRECOMPILATION.md`, sections 3-4,
Git blob `4badb40f0919c515823cb07e44c6470d4d6469ca`.

Let k_i>=2 be d distinct target ranks with productive-role multiplicities
W_i; W=sum W_i. There are P actual ordered paid positions, with q distinct
positive ranks r and multiplicities P_r, all strictly below k_min. Actual
productive role names, paid positions and owned roles retain their identities.
Let A>=k_max be the ambient cap, N>=A, and

    G=max{g: A*k_min^g<=N}.

The source note uses A=k_max; the inherited source codec also admits the
displayed larger ambient cap, which we retain explicitly. At path p of
depth h, put rho=product_(j in p) r_j. A unit has multiindex alpha with
|alpha|=G-h, column rho*c(alpha), multiplicity ordinal v<u(alpha), and fit
A*rho*c(alpha)<=N. The actual job rank of productive role i is

    s = rho*c(alpha)*k_i.                                  (1)

This s is neither a multiindex degree, a role's bare k_i, nor the array's
physical row integer. A slot is a fresh source exactly when p is empty or

    A*(rho/r_last)*c(alpha)*k_i > N.                        (2)

These are inherited exact flow identities, not a new interpretation of
the finite compiler.

Write S_s for the number of actual fresh sources with job rank s and
S=sum_s S_s. The source note requires each of the a*S_s corresponding
independent arrays to receive its complementary rank-(N-s) job before the
flow starts. For each positive e=N-s, the supplied smaller program has a
positive productive width B_e, so whole invocations require

    B_(N-s) divides a*S_s.                                 (3)

The least factor B_e/gcd(B_e,S_s), and the LCM across these and the separate
chronological exit batches, are predecessor results: chronological-batch-width
([#4507](https://github.com/CrocSwap/integer-mult-bounds/pull/4507)) and
symbolic-integer-batch-width/PROOF.md
([#5071](https://github.com/CrocSwap/integer-mult-bounds/pull/5071)). They are not claimed anew.
This package accepts a supplied a and tests (3). It does not treat a factor
clearing only complements as sufficient for exits, or pool separate exits.

When s=N the complementary rank is zero. Section 4 says zero-rank terms
vanish. **No B_0 is supplied, constructed or invoked.** Such sources receive
an explicit `NoComplement` label below.

## 2. A true-rank local count without a profile scan

Fix a proposed job rank s. At a state (h,rho,r), the fresh-source test (2)
simplifies exactly to

    h=0 or A*s>N*r.                                       (4)

For a role of rank k_i, the unit-fit test simplifies to

    A*s<=N*k_i.                                          (5)

Both statements follow by substituting (1), with positive r at h>0.
Neither test depends on the unit ordinal or on the particular target
multiindex once s, rho and i are fixed. The last paid rank remains essential
in (4); equal-depth equal-dilation states may still differ.

Let F_g(c) count ordered words of g productive role names whose rank product
is c. It is the inherited multiplicative-polynomial census:

    F_0(1)=1,
    F_g(c)=sum_i W_i*F_(g-1)(c/k_i),

with a noninteger argument or an absent product contributing zero. Equivalently
F_g(c)=sum_(|alpha|=g,c(alpha)=c) u(alpha). Product coincidences add their
counts; they do not identify different words, role names or source arrays.

Define C_s(h,rho,r) to be zero if (4) fails. Otherwise put

    C_s(h,rho,r)
      = sum_(i: A*s<=N*k_i) W_i * F_(G-h)(s/(rho*k_i)).      (6)

Equation (6) counts exactly the fresh sources of true rank s in that
class. For each role type i, the quotient fixes the unit column product;
F sums precisely its eligible multiindices and their u(alpha) ordinals;
W_i restores the distinct native role names. Condition (5) guarantees fit
for every such multiindex, while (4) guarantees freshness for every slot.
The converse assigns each actual source to exactly one term.

Thus one C_s value needs d product-table lookups rather than scanning all
multiindices. This identity is the useful additional count interface; the
inherited total-source recurrence alone does not identify true-rank ports.

## 3. Candidate ranks and per-bucket subtree counts

Every source lies in the band

    N/A < s <= N.                                        (7)

For a nonroot source, (4) and r>=1 give the strict lower bound. At the root,
c(alpha)*k_i>=k_min^(G+1)>N/A by the definition of G. For the upper bound,
unit fit and k_i<=A give rho*c(alpha)*k_i<=N. Equality at either capacity
test must be treated as a fitting parent, not a new source.

Every possible s is the product of a depth-h paid dilation and a target
word product of degree G-h+1, because alpha+e_i has that degree. Distinct
paid dilations at depth h number at most binom(h+q-1,q-1); target products
of the latter degree number at most binom(G-h+d,d-1). Therefore the entire
candidate list before coincidence deduplication has length at most

    Q0 = sum_(h=0..G) binom(h+q-1,q-1)*binom(G-h+d,d-1)
       = binom(G+q+d,q+d-1)-binom(G+q,q-1).                (8)

The equality counts weak compositions of G+1 across q paid types and d
target types, excluding those with zero target degree. In particular G=0
gives Q0=d, and q=d=1 gives Q0=G+1. Multiplicative coincidences only lower
the actual number. The implementation extracts distinct (h,rho) from the
already sorted state keys, forms these products, applies (7), sorts and
deduplicates. It does not enumerate paid paths. Some remaining candidates
can still have no source; their work is charged using Q0.

For one candidate s, retain the predecessor's state keys (h,rho,r), at most

    R=1+q*binom(G+q-1,q),                                 (9)

with value one at G=0. Set T_s=C_s at h=G, and otherwise use

    T_s(h,rho,r)=C_s(h,rho,r)+sum_t P_t*T_s(h+1,rho*t,t).   (10)

Induction down the finite class tree proves (10). Equal paid ranks may
share statistical counts; their actual paid positions retain separate child
intervals. The root total is S_s. Candidates with S_s=0 are dropped only
after this work. The catalogue satisfies sum_s S_s=S because true job rank
partitions the inherited source set.

The implementation builds each bucket's two count arrays separately and
stores only (s,S_s) in the catalogue. At most one bucket remains cached
after a query. Constructing its replacement can briefly retain both the
old and new buckets, still using O(R) count storage; the construction
loop can similarly retain the preceding temporary bucket. Holding every
bucket simultaneously is not included in the stated workspace bound.

## 4. Canonical within-rank order

For each s, restrict the predecessor's source order to actual rank-s slots:
depth-first class preorder with actual paid-site order; then lexicographic
multiindex, ordinal, and native role-list order. This is stable filtering
of occurrences, not a reordering of native jobs or a change to owner identity.

At a class state, scan its stored degree-G-h multiindices. A point contributes
only if k=s/(rho*c(alpha)) is an existing target rank, the quotient is an
integer, unit fit holds and (4) holds. Its block contains u(alpha)*W_k slots
in ordinal/native-role order. All coincident-product multiindices retain
their separate positions in this scan.

To rank a source, descend its actual paid path, adding the current class's
C_s and each preceding actual child's T_s. At the destination add preceding
point blocks, then v*W_k and the role's index among native names of rank k.
Reject a matched slot, a different true job rank or an invalid unit.

To unrank j in [0,S_s), first distinguish the local interval C_s from the
ordered child intervals T_s. In the local interval scan the point blocks,
then use division by W_k to recover the unit ordinal and native role. In
a child interval descend that actual paid position. Each descent increases
h and there are at most G. Zero-size blocks are skipped.

The same finite half-open interval induction as the inherited codec proves
both inverses. Write r_s(u) for this rank of a source occurrence u. Neither
an equal true rank nor equal count-state statistics merge two occurrences.

## 5. Whole complement ports and their inverse

Let r(u) in [0,S) be the already published source-row index. Its replicated
row order is replica-major:

    row(b,u)=b*S+r(u), 0<=b<a.

For source u of true rank s, define its grouped ordinal

    x=b*S_s+r_s(u), 0<=x<a*S_s.                           (11)

For s<N, use the supplied width B=B_(N-s) and map

    invocation,slot=divmod(x,B).                          (12)

Because (3) holds, the image is exactly
`[0,a*S_s/B) x [0,B)`. The namespace and true source rank qualify this
invocation/slot identifier. Its complement-program rank is N-s. For s=N,
return `NoComplement(namespace,N,x)` and perform no supplier invocation.

Conversely, a valid positive-complement port gives x=invocation*B+slot;
a valid NoComplement gives x directly. Division by S_s recovers b and
r_s(u). The bucket inverse recovers u; the old source index then returns
b*S+r(u). These operations are mutually inverse. Their disjoint image
has cardinality

    sum_(s<N) (a*S_s/B_(N-s))*B_(N-s) + sum_(s=N) a*S_s = a*S.

The second sum is empty if the rank-N bucket is absent. Every original
productive input appears once. Owned
banks are excluded by the inherited source-row domain. A matched interior
target slot is not a new independent input.

**Cross-replica example.** Take roles (small,2),(large,5), paid sites
(1,small),(1,bank), A=5,N=10. The source ranks in canonical row order are
4,10,5,5. At a=3 choose B_5=3 and B_6=1 as supplied smaller widths. The two
rank-5 complement invocations have old input rows (2,3,6) and (7,10,11).
Each uses a complete B_5 batch, crossing replica boundaries where needed.
Rows 1,5,9 have source rank N and receive NoComplement labels. This is
not accomplished by dividing the original replica-major row number by B_5.

This theorem supplies an exact address permutation and its inverse as
metadata. Executing it on arrays still needs the retained whole-job
adapters, actual copying/routing, restoration and erasure. Equal job ranks
alone do not identify coordinate frames. A positive library width is not
a proof that its smaller native program satisfies those contracts.

## 6. Complete deterministic metadata costs

Let M=binom(G+d,d) be the predecessor point-profile bound, and put
M_plus=binom(G+d+1,d). Ordered product tables through degree G+1 have at
most M_plus entries in total. Their next layer is formed by sorting at
most d times the preceding layer's contributions and summing adjacent
equal products. Its temporary memory is O(d*M_plus) records. No growing
hash set or dictionary is used by the new algorithm. The retained codec's
hash collections are confined to its finite input specification and their
worst-case quadratic input cost remains charged.

Let S_bit be the complete bit length of the supplied metadata other than N:
native rule/role labels, namespace, replication a, and the explicit smaller
width library. This includes all bits of every supplied B_e; they need not
be small or efficiently generated. Let ell(x)=ceil(log2(x+1)) and define

    B=S_bit+ell(N)+(G+2)*ell(A+W+P+G+2)+ell(Q0+2)+1.

Candidate products have at most (G+1)*ell(A) bits. Word counts are bounded
by W^(G+1). Every bucket and subtree count is at most the total source count
S<=(G+1)*W*max(W,P)^G. Replicated indices add ell(a), and the library widths
are already represented in S_bit. Thus all arithmetic operands have O(B)
bits. Valid query descriptors and outputs have O(B) bits with ordinary
variable-length integer encodings; oversized malformed-query reading costs
are additionally charged by their supplied length.

The following loose operation envelopes include the prior source index:

    K_old=(S_bit+1)^2*[M(G+d+1)+R(M(d+1)+q+1)],
    K_setup=K_old+(S_bit+1)^2*[d*M_plus+Q0+Q0*R*(d+q+1)],
    K_bucket=(S_bit+1)^2*R*(d+q+1),
    K_query=(S_bit+1)^2*[M(d+1)+G*P+G+d+1].

K_setup covers the source-index setup, product tables, candidate generation
and sorting, every zero or positive candidate's full DP, catalogue and
library validation. Equation (6) costs d sorted product lookups per state;
(10) costs q sorted count lookups. Preparing a later bucket costs K_bucket.
Its rank/unrank scan and composition with the old row index cost K_query.
A query changing bucket pays both; no constant-time bucket switch is claimed.
For repeated queries in one bucket only its already-paid table is reused.

In the indexed arithmetic/comparison model of the predecessor, each sorted
lookup uses O(B) comparisons of O(B)-bit keys; sorting contributions is
charged similarly. Schoolbook products/divisions, replication, capacity
tests, point/path copies and index arithmetic fit O(B^2) per logical
operation. Consequently the respective indexed work bounds are
O(K_setup*B^2), O(K_bucket*B^2), and O(K_query*B^2). Total retained metadata
and one active bucket occupy

    O((S_bit+R+d*M_plus+Q0+1)*B) bits.                     (13)

These bounds do not grant free tape travel. For an explicit conservative
serialized-table implementation, let L be the expression inside O in (13).
Keep sorted records on a fixed number of binary tapes and use full scans
for lookup/update. Produce product contributions and state candidates one
at a time with scan/copy insertion and adjacent equality aggregation; the
displayed record bounds still hold. A key comparison, index/cursor update,
record copy, head return, shift or overwrite is charged O(L^2), which also
dominates O(B^2) arithmetic. The same operation envelopes therefore give
O(K_setup*L^2), O(K_bucket*L^2) and O(K_query*L^2) fixed-tape metadata time,
with O(L) workspace. Optional final erasure costs O(L) and is included.
This is a companion simulation construction, not an assertion that Python
is that machine or a payload dispatcher.

For fixed native rank alphabets d,q these are polynomial in G, log N and
the bit length of the supplied library/replication data. They do not bound
the work of producing that smaller library, of expanding the selected
1920-fold word, or of moving a single productive array.

## 7. Evidence, novelty and remaining obligations

The unchanged literal finite-DAG oracle supplies actual source fields and
job ranks. The verifier compares every within-rank ordering, local and
subtree bucket count, replicated row and complement port on 26 bounded
flows. It includes product collisions, repeated native/paid ranks, a larger
ambient cap, G=0, q=d=1, the strict source boundary and last-rank dependence.
Mutations and contract failures cover zero complements, missing/invalid
library widths, nonintegrality, index endpoints, wrong namespaces/ranks,
matched slots, overwritten product coincidences and merged replicas/sites.

A height-24 fixture retains 601 states and 266 candidate ranks, of which
206 have sources. It indexes 216,192,013,559,808 sources per replica without
enumerating 423,644,304,721 class paths. A separate global method verifies
all rank counts by counting ordered native target words and actual paid
paths, then subtracting all incoming paid jobs from the complete target
census. It uses no per-bucket freshness predicate or subtree DP. Six large
replicated row positions round-trip. These finite checks support code;
the universal claims are the identities and interval arguments above.

The new result is the true-rank local-count reduction plus an exact
occurrence-to-whole-complement-port bijection with deterministic complete
metadata costs. The source census, product polynomial, Pascal matching,
minimal gcd/LCM factors and permission to pre-group complements are credited
predecessor results. This does not complete separate ordered exit ports,
smaller-rank substitutions, physical source grouping, owned-bank allocation,
native normalization or the five selected assumptions. Kappa is unchanged.
