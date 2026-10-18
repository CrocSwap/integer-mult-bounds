# Actual width-one GL2 target minima survive a nonfaithful action

## Exact finite claim

An address is one point x in F2^2. Each of two scalar roles contains an
arbitrary binary payload at all four points. Thus the complete payload space
is F2^8. The two paid address labels are

```
a: (x0,x1) -> (x0+x1,x1),
b: (x0,x1) -> (x0,x1+x0).
```

A paid call applies one label to one role. Every inverse/restoration call
costs one. Arbitrary scalar GL2(F2) mixing of the two roles, identically at
each address, is free. There is no extra role, clean input, reset, erasure,
free address permutation or deferred restoration. Both roles begin dirty.

For any ordered pair g,h in GL2(F2), the required **actual** endpoint is
diag(P_g,P_h) on the full eight-dimensional payload space, including both
diagonal blocks and zero off-diagonal coupling. Let ell(g) be its shortest
single-role a/b address-word length.

**Finite theorem.** For all 36 ordered pairs, the minimum paid count is
ell(g)+ell(h), despite arbitrary interleaved free scalar mixing. This includes
arbitrarily long candidate words: the complete finite reachable graph is
certified, not a radius-limited search. The target-count histogram by minimum
0..6 is `1,4,8,10,8,4,1`.

This is not a theorem for additional roles, affine translations, other
alphabets or a physical tape supplier. Its new domain is exactly two roles
and one binary point column (d=2,w=1 in PR2599's notation).

## Why this is a missing implication

PR2599 at `cfafdd633cf4e2e534704ec3ddd684cb0c32734f` proves that this stream
action of F2[GL2(F2)] is **not faithful**. Its 18-paid-call, ten-free-XOR word
is formally I+n_G E01 but actually identity at w=1. Consequently a formal
lower bound cannot simply be transferred by equating the endpoint tests.
That package explicitly leaves cheaper monomial targets as an open question.

The credited symmetric-adjacent cut theorem on main proves ell(g)+ell(h)
for formal S3 endpoints even with arbitrary restored dirty roles. Identify
GL2(F2) with its action on the three nonzero points, ordered (1,3,2), where
binary point bits encode x0 as the low bit. In that order a and b are adjacent
transpositions and ell is the inversion count. That formal result and
PR2544's related coordinate-SWAP tariff are credited. The present census
establishes the missing actual-stream conclusion in the smaller specified
domain; it does not repeat a formal search or claim a new general cut method.

## Removing free scalar mixing without changing the actual endpoint

The point 0 is fixed by every address label. On the two payload coordinates
at address 0, every paid call is identity, while each free scalar operation
acts by its actual two-by-two matrix Q. The desired endpoint is also identity
there. Thus the chronological product of all free Q factors must be I.
This uses arbitrary zero-address payloads, not a clean-zero promise. Constant
payload streams give the same necessary condition.

Conjugating a single-role call by Q replaces its coordinate projector by
N=Q E_jj Q^-1. Over F2 these are exactly the six binary rank-one idempotents
N=u v^T with u,v nonzero and v^T u=1. Each such N is a conjugate: its image
and kernel are complementary one-dimensional spaces and supply a basis.
Moving all free factors to one end therefore leaves no residual free factor
and gives a word in exactly twelve paid maps

```
D_N(s) = I + N tensor (P_s+I),    s in {a,b}.
```

Conversely each normalized map is implemented by free conjugation around one
paid role call. Hence this is an exact cost-preserving normalization for the
declared actual-stream model, even though its group-algebra representation
is nonfaithful. No formal augmentation inference is required. The direction
and order of factors are preserved by conjugation; maps need not commute.

## An independently enumerable complete domain

In one four-point stream, let e_x denote a delta at point x. Decompose

```
F2^4 = span(e_0, c) direct-sum E,
c=e_1+e_2+e_3,  E=span(e_1+e_3, e_2+e_3).
```

E is the even-parity subspace on the nonzero points. This is a direct sum
because c has odd parity. Address permutations fix e_0 and c individually
and preserve E. Every normalized D_N(s) consequently fixes the four-dimensional
F=span(e_0,c) on both roles **pointwise**, and preserves the four-dimensional
active space E on both roles. It is invertible (indeed an involution), so its
full operator lies in `I_F direct-sum GL4(F2)`.

There are exactly `(16-1)(16-2)(16-4)(16-8)=20,160` active invertible maps.
The independent checker enumerates them by choosing four independent columns;
it does not use BFS to determine its domain. For active columns a,b on a role,
the corresponding full columns at points 0,1,2,3 are

```
e_0, c+b, c+a, c+a+b.
```

These formulas use e_1=c+(e_2+e_3), e_2=c+(e_1+e_3), and
e_3=c+(e_1+e_3)+(e_2+e_3). They uniquely embed each active map as a full
eight-column operator. Independent enumeration therefore provides every
possible normalized state and an injective full-payload representation.

The producer instead performs BFS using six packed rows for the nonzero
addresses, with the two zero-address coordinates implicitly fixed. Its
20,160 distinct states match the independent domain exactly. Thus these
twelve paid maps actually generate the entire active GL4, a finite fact
checked here rather than assumed from the group order.

## The distance certificate proves all-length optimality

DISTANCES.json assigns a nonnegative integer d(M) to every state. The
independent checker uses full eight-column generator maps, not the producer's
packed-row transition routine, and verifies all of the following:

1. Its independently enumerated domain and the certificate's states agree
   exactly; each state occurs once and only identity has distance zero.
2. Every one of the 241,920 directed paid transitions stays in that domain
   as the same full operator and obeys `|d(sM)-d(M)|<=1`.
3. Each nonidentity state has a neighbor with distance one smaller.

Along any word from identity, item 2 bounds the final label by the word length.
Repeated descending edges from item 3 give a word of exactly the label's length,
ending at identity by item 1. The generators are involutions, so reversing that
path realizes the state from identity at the same cost. Thus every label is
its exact shortest distance, independent of the producer's search algorithm.

The complete layer sizes at distances 0..8 are

```
1,12,80,454,2033,6558,8750,2170,102.
```

For every pair g,h the checker independently forms diag(P_g,P_h), computes
the two single-role inversion counts, reads the now-certified distance, and
checks equality. It replays each recorded attaining word on all eight input
columns. All 36 targets and all 288 columns are checked. A basis check suffices
because these are explicitly linear operators on all arbitrary inputs.

Independent code and representations are used, but the graph-distance proof
principle is shared. Standard finite-graph distance certificates and the
repository's earlier exact XOR-circuit checks are credited; no new general
shortest-path method is claimed. In particular, the 20,160-state ordinary
four-wire XOR and block-shear packages use different paid alphabets and
target contracts. Their group cardinality alone does not settle these minima.

## Controls and limits

The retained PR2599 word still acts as identity in this graph, so the finite
negative result does not silently assume faithfulness. The producer separately
authenticates that unchanged source before replaying its actual alias. The
formal nonidentity and all-width threshold proof remain credited to PR2599.

Failure controls remove a domain state, corrupt a nonzero distance, omit a
target's paid call, and duplicate a target. They fail domain, edge-distance,
full-column or coverage checks, rather than only a digest. Other tests reject
source drift, typed receipt corruption and existing-output replacement.

No result here covers a third dirty role: its active space already has a
different dimension and alphabet. Width zero has one empty address and
trivial address action, so it would not satisfy the stated minima. For widths
at least two, PR2599's faithful-action argument and the credited formal theorem
are separate existing evidence; this census neither reruns nor extends them.
Free scalar mixing is an optimistic price convention, not unpriced real tape
work. No native carry arithmetic, fixed-tape layout, supplier, reserve,
selected frontier or multiplication exponent is changed.

This is a finite computational certificate with a written reduction and
independent checker, not human or formal-kernel verification. Prepared for
ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
