# Locate expanded compiler leaves with their persistent field identities

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
Written logical-emission theorem with finite exact corroboration. No new kappa.

## 1. Exact domain and emitted object

Use sections 3--4 of the retained
[FINITE-PRECOMPILATION.md](reference/FINITE-PRECOMPILATION.md) and the exact
occurrence/source/source-complement codecs in CrocSwap/integer-mult-bounds#7346,
CrocSwap/integer-mult-bounds#7347 and CrocSwap/integer-mult-bounds#7348.
`SOURCES.json` pins their unchanged code, commits, Git blobs and SHA256 hashes.
Their logical bijections and metadata-cost proofs are imported; no payload
access is free merely because its source row is known.

A rule has ordered productive roles of ranks k>=2, J ordered paid positions
of positive ranks r(j)<k_min, and disjoint named owned banks. Each paid site
acts on one specified productive role or owned bank. Let d,q count distinct
target/paid ranks, W count productive roles, and A>=k_max be the actual
ambient cap. A need not be a target rank. At n>=A put

`G_n=max{g:A*k_min^g<=n}`.

Units have the inherited descriptors `(p,alpha,v)`, with
`|p|+|alpha|=G_n`, `v<u(alpha)` and `A*rho(p)*c(alpha)<=n`.
Equal ranks never identify distinct roles, paid positions or physical fields.

Supply evaluated positive integer library rows `(a_n,B_n,P_n)` through N.
Base rows 1<=n<A are `(1,1,n)`: a width-one sequential program on its n
canonical axes. At nonbase n let S_(n,s) be the exact fresh-source count
at true job rank s, and S_n its sum. Require

```
B_n=a_n*S_n;
B_(n-s) divides a_n*S_(n,s)                  (s<n);
B_e divides a_n                             (each individual exit cut);
P_n=sum_(s<n) (a_n*S_(n,s)/B_(n-s))*P_(n-s)
    +sum_(individual exit cuts c) (a_n/B_e(c))*P_e(c).
```

The gcd/LCM policy and recurrences are prior results of
CrocSwap/integer-mult-bounds#4507 and CrocSwap/integer-mult-bounds#5071.
The evaluated library of CrocSwap/integer-mult-bounds#7345 supplies them in
its default specialization A=k_max. We do not transfer its stronger width
bound to arbitrary A. Our larger-A interface accepts supplied valid rows
and charges their actual bit lengths; separate literal tests cover that case.

Declare a permitted order: first source-complement groups by increasing s,
with replica-major stable source order and consecutive whole B_(n-s)-port
invocations; then the original lockstep paid-position order, completing each
exit before resuming its parent. At an exit, group replicas increasingly into
whole B_e-port calls. Use this same order recursively in every smaller call.

The indexed object is the **chronological projection onto the P_N rank-one
paid leaves** of the fully expanded program. A leaf descriptor contains its
complete smaller-call path, base rank, axis in that base program's canonical
order, and physical field identity. Native scalar, phase/adapter, owned
initialization/erasure and return instructions remain in the actual program
but are absent from this projection. Global axis embeddings remain supplied
adapter obligations. No complete native instruction stream is claimed.

## 2. Separate cuts and a weighted suffix table

At depth G_n, alpha=0 and u(0)=1. Every such class is present since
`A*r_max^G_n<=A*k_min^G_n<=n`. Hence every exit is one full ordered path
`c=(j_0,...,j_G)` of length G+1 and rank `e(c)=product r(j_t)`.
Before replication it has one array. Its local invocation/slot is
`divmod(replica,B_e)`, qualified by that full cut. These facts already follow
from the predecessors. The initial exit-only division-wrapper idea was
rejected as too thin; the new result below composes complete recursive
instruction locations and persistent ownership through smaller programs.

Fix n, G=G_n and a=a_n. For each paid product rho reachable after h sites set

```
H(G+1,rho)=(a/B_rho)*P_rho;
H(h,rho)=sum_j H(h+1,rho*r(j)).
```

Every bottom division is integral. Induction on the suffix length proves
that H is the exact number of expanded leaves below that prefix. A bottom
cut has a/B_rho whole smaller calls; each earlier site contributes its own
chronological child interval. Equal ranks share count arithmetic only.
There are at most `binom(h+q-1,q-1)` products at depth h, so at most
`binom(G+q+1,q)` stored records. Sorted product/count tables add multiplicative
collisions without factoring ranks, enumerating paid paths, or relying on
expected hash dispersion. Bottom weights use actual smaller-program costs.

For an exit-phase ordinal, subtract complete preceding child intervals in
actual paid-site order and descend G+1 times. Division by P_e then gives its
whole invocation and local leaf ordinal. Conversely sum every preceding
H interval along the full cut, add the entire complement-phase count and
`invocation*P_e`. This is that smaller invocation's exact parent offset.

Complement offsets are successive intervals of lengths
`(a*S_(n,s)/B_(n-s))*P_(n-s)`. Divide within the selected interval by P_(n-s).
The supplied recurrence proves these intervals and all exits partition
`[0,P_n)`. Count equality alone would not supply this ordered partition.

## 3. Child ports and persistent owner identities

At a complement call of rank e=n-s, input i in invocation v has grouped
ordinal `v*B_e+i`. The unchanged #7348 inverse returns the exact parent source
row. Its bijection proves distinctness and specifies inverse return order.

At exit c, input i in invocation v has replica `b=v*B_e+i`. Its parent field
is exactly the inherited `paid_owner` of the unique unit `(c[:-1],0,0)` at
paid site `c[-1]`, in replica b. Different i have different replicas, which
are part of every source/owned tag. Hence the ports of this whole invocation
are distinct. The inverse reads b, verifies that the exact owner belongs to
this cut at b, and returns `divmod(b,B_e)`. Equal rank or value is insufficient.

Global identities are

```
SourceRow(root_namespace, root_row),
OwnedBank(root_namespace, call_prefix, replica, unit_path, alpha, v, bank_name).
```

A root namespace identifies one actual root invocation; simultaneous distinct
roots need distinct namespaces. An inherited parent-owned field retains its
original parent's tag. It is not relabelled as a newly allocated child bank.

Resolve a nested productive port by walking its call path upward. Translate
the local row across the immediate complement/exit boundary. A parent source
becomes a parent row via #7347 and continues upward. A parent-owned field
stops the walk with that parent's call-prefix namespace. Reaching the root
returns its input-row identity. Every step is the exact caller relation.

For any **one whole invocation**, this map is injective. Its immediate
boundary is injective as above; parent productive rows remain injective by
induction, and parent internal banks are disjoint from them and each other
by their occurrence tags. This is not global leaf-to-owner injection.
One rank-two role x with two paid rank-one sites on x has two distinct exit
leaves on the same source row. Their full cut paths and ordinals differ.

Under the retained completed-child contract, outputs return in the same
ordered ports. The inverse correspondence therefore returns each output to
the identical parent field. Completing before resumption preserves pending
parent state and bank lifetime. This is the address/identity implication,
not a payload scatter or erasure implementation. Correlated current owned
values still use the inherited arbitrary-input child correctness contract.

## 4. Expanded-leaf bijection

At each nonbase rank, select one complete smaller call and local leaf ordinal
using section 2; append `(parent,kind,source-rank/full-cut,invocation)` and
continue at its child rank. At a base rank n<A the remaining ordinal is
the axis in `[0,n)`, and the local input row is zero. Section 3 resolves its
field. The inverse validates the call path, base axis and reconstructed field,
then adds exact before-call offsets from inside out.

Section 5 proves strict rank descent. Strong induction on rank and the local
interval partition proves both inverse identities and equality with the
chronological paid-leaf projection, including actual fields. Equal ranks,
counts, owner identities or contents never merge distinct instruction paths.
The theorem supplies a lazy logical-emission interface, not a native program.

## 5. Rank descent, description sizes and complete metadata costs

The inherited source band is `n/A<s<=n`, so positive complements are below
`(A-1)n/A`. At an exit,

`e<=r_max^(G+1)<=r_max*k_min^G<=r_max*n/A<=(A-1)n/A`.

Writing alpha=(A-1)/A, the elementary `alpha^A<1/2` implies fewer than
`D=A*ceil(log2(N+1))` smaller-call edges. Each cut has length <=G_N+1.
A and the alphabets are fixed in fixed-rule complexity claims. The A factor
is not a polynomial in the bit length of a variable ambient cap.

Let b bound the bit lengths of all supplied `a_n,B_n,P_n` and n through N.
Let S encode the full role/paid-position/owned lists and root namespace.
Take

```
Z=4*(b+S+(G_N+2)*ceil(log2(A+W+J+G_N+2))
     +ceil(log2(D+2))+1).
```

This is an O(Z)-bit arithmetic bound. Source counts are at most B_n; H values
and offsets are at most P_n. Products before capacity tests are at most
fixed rank factors to degree G_N+1; division temporaries use sums of these
bit lengths. Replicas, row indices, axes and path entries fit. A complete
valid path occupies O(DZ) bits. Oversized malformed input reading additionally
costs its supplied length. Astronomical replication is never unit-cost.

Use the explicit `K_setup,K_bucket,K_query` envelopes and storage formula
from the retained [#7348 proof, section 6](reference/source-port-PROOF.md).
Instantiate its S_bit with this complete rule, a, and every needed `(e,B_e)`
pair, including all their bits. Let K_s,K_b,K_q and L_s be maxima of those
three operation envelopes and its retained metadata-bit bound for n<=N,
with operands O(Z). This retains work for zero candidate ranks, product
coincidences, transient old/new bucket tables and all stored count records.
Source-row/port work is not free or silently amortized.

Let `H=binom(G_N+q+1,q)` and let Q be #7348 equation (8)'s candidate-rank
bound. After the supplied library is available in indexed metadata storage,
preparing one new node costs

`O((K_s+qH+Q+S^2+1) Z^2)`.

The extra terms construct sorted paid-product levels, every bottom quotient
weight and H recurrence, ordered complement offsets and validity checks.
Sorting and binary-search lookup cost O(Z^2) per logical record operation:
log H and log Q are O(Z). Schoolbook products/divisions also cost O(Z^2).
Predecessor hash collections concern only the finite input rule; their worst
case is covered by S^2. New growing tables use sorted comparisons.

A query traverses at most D ranks. Per rank, source translation may rebuild
one bucket and use its rank/unrank query. Suffix selection scans at most
`(G_N+1)J` actual paid positions; complement selection scans at most Q groups.
Conservatively charge D extra record operations per rank for path copying.
After the necessary node tables exist, a leaf query with owner resolution
therefore costs

`O(D*(K_b+K_q+Q+(G_N+1)J+D+1) Z^2)`.

An initial query additionally pays the displayed node setup for each newly
reached rank, at most D. The inverse has the same conservative envelope.
The implementation starts with N supplied rows and an N-entry cache directory;
reading, checking and copying them costs O(NZ). This initialization is not
polylogarithmic and is included. Repeated queries can eventually retain all
N source/node tables, so a safe complete historical metadata bound is

`L=O(N*(Z+L_s+(q+1)HZ+QZ)+DZ)`.

For fixed native alphabets, node preparation and indexed queries are polynomial
in log N, S and the **supplied** library bit cap b. The N-row library has its
own reading and generation cost. #7345 separately bounds default-library
generation/bit sizes. No such bound is transferred here to the unmaterialized
selected `153^1920` library, and no array payload is included in L.

For a conservative sequential companion, serialize the library, cache,
source tables and descriptors on a fixed number of binary tapes within L.
Implement each logical table operation by full key scans, copy/insertion,
explicit cursor returns and at most O(L^2) local actions; elementary scalar
arithmetic fits this allowance. Replace each O(Z^2) logical-operation charge
above by O(L^2), include O(L) input/output/optional retirement scans, and keep
the full historical L bound after erasure. This pays metadata travel, even
when a library scan is much larger than indexed lookup. It is a companion
simulation construction, not a claim that Python is a literal transition
table. Native work, full-field gathering/return, adapters, suspension/parking
and numerical precision remain separately priced obligations. There is no
new multiplier tariff or exponent conclusion.

## 6. Evidence and scientific boundary

`literal_oracle.py` imports no production codec, source DP, owner resolver
or suffix table. It expands target-role words, materializes every class,
builds actual child-slot buckets, matches ordered parent supplies to them,
assigns fresh fields, and recursively expands each whole smaller call.
The verifier compares every leaf and complete input vector on the declared
small domains, including A>k_max, repeated roles/sites, coincident products,
cross-replica complements, inherited banks and ungrouped native role lists.
It also compares default-library integers with the unchanged #7345 generator.

A large singleton-rank fixture has 68,719,476,736 cuts. Base-eight digits and
the last owned paid site give a distinct direct oracle for selected queries
without expansion. Another fixture queries a library with huge replication
and row counts. These formal metadata rules are not asserted realizable
native suppliers. Executed coverage is recorded exactly in `VALIDATION.json`.

Controls detect lost paid multiplicity, merged cuts/replicas, dropped owned
call namespaces, wrong totals/axes/returns, invalid zero complements and
range errors. A same-owner/different-cut fixture refutes the stronger global
leaf-owner injection. Universal force comes from the interval, identity
and rank-induction proofs, not extrapolation from finite checks.

This closes a recursive logical-emission obligation: counts and source ports
compose into the complete ordered rank-one leaf projection with persistent
field names and inverse locations. The selected actual role manifest/library,
full scalar/phase/adapter stream, physical gather/return, numerical endpoints,
owned-storage realization and complete fixed-tape dispatcher remain open.
All five selected assumptions and kappa remain unchanged.
