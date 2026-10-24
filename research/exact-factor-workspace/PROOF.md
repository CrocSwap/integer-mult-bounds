# Exact workspace under a single spectator basis change

This contribution is produced by Nick Petalas. Apache-2.0.
This is a written scoped proof, with finite exact controls.

## 1. Boundary and theorem

Let F be any field and let R=A⊕S be a finite dimensional scalar role space.
The original active coordinates A are fixed. Write n=dim S. Consider a fixed
list of nonzero rank-one scalar couplings x_i y_i, with x_i∈R and y_i∈R*.
Its paid factors may be I+λ_i x_i y_i over any unital F-algebra, with scalar
coefficients central and λ_i nonzero. No commutativity between λ_i is needed.
Idempotent couplings additionally satisfy y_i(x_i)=1.

A permitted restriction chooses S=K⊕N, changes only the spectator basis,
and discards the identity block N. Every original factor must be block
diagonal on (A⊕K)⊕N, with its N block equal to identity. Thus the operation
retains the actual couplings through a single invertible change of coordinates.
It does not replace them by new couplings with the same contractions.

Let u_i be the S component of x_i and v_i=y_i|_S. Set

    U=span{u_i},  V=span{v_i},
    u=dim U,  v=dim V,  t=rank(V×U→F),
    d=u+v-t,  k=n-d.

**Theorem.** The smallest possible dim K is exactly d. All optimal discarded
spaces N are precisely the complements of U∩ann(V) inside ann(V). For each
such N, all complements K to N in S containing U are optimal and permitted.

If F has q elements, the numbers of distinct optimal discarded subspaces
and ordered optimal retained/discarded decompositions are respectively

    q^((u-t)k),                  q^(k(u+v-2t)).             (1)

These count subspaces and ordered pairs of subspaces, not choices of bases.
The theorem includes zero dimensional spaces, empty lists, arbitrary finite
word lengths and dirty inputs. It requires no endpoint assumption.

## 2. Factor support and the lower bound

A nonzero rank-one outer product is supported on A⊕K precisely when its column
lies in A⊕K and its functional vanishes on N. One direction follows by taking
the outer product. For the other, any nonzero functional value exposes the
column as the image of an input, and a nonzero column exposes every nonzero
functional value. Multiplication by a nonzero scalar in F is injective even
when the ambient F-algebra has zero divisors. A nonzero λ_i therefore does not
hide a nonzero scalar coefficient of an off-diagonal block or N-block update.

Consequently a split is permitted exactly when

    U⊂K,                       N⊂F_0:=ann(V).             (2)

Now dim F_0=n-v and W:=U∩F_0 has dimension u-t, by rank-nullity applied to
U→V*. Since K∩N=0 and U⊂K, any permitted N is disjoint from W. Hence

    dim N ≤ dim F_0-dim W = n-v-u+t = k.

Since dim K=n-dim N, this proves dim K≥d. In particular d≤n once a permitted
split is constructed. The full split K=S,N=0 also shows existence directly.

## 3. Attainment and exact classification

Choose any complement N of W in F_0. It has dimension k and is disjoint from
U because N∩U=N∩W=0. Extend a basis of U together with a basis of N to a
basis of S. Assign the added vectors to K along with U. This gives S=K⊕N,
with dim K=n-k=d, and (2) makes every original factor legal after restriction.

Conversely, an optimal split has dim N=k. Its inclusion in F_0 and trivial
intersection with W imply F_0=W⊕N by dimensions. Thus these are all optimal
discarded spaces. For each such N, exactly the complements K containing U
satisfy the factor-support condition. This proves the stated classification.

For F of size q, complements N to W in F_0 are graphs of arbitrary linear
maps from one fixed k-dimensional complement to W. There are q^(k(u-t)).
Fix N. The complements K to N in S are sections of S→S/N. The condition
U⊂K fixes the section on the u-dimensional image of U. The remaining d-u
directions can be lifted independently by any vector of N. There are
q^(k(d-u))=q^(k(v-t)) choices. Multiply the two counts to obtain (1).
The usual graph-of-a-linear-map complement count is standard linear algebra.

## 4. Full words, endpoint restoration and the two contracts

Choose any bases of an optimal K and N and prepend the unchanged basis of A.
This is one scalar spectator-only basis change B. Each factor has the form

    B^(-1) G_i B = G_i' ⊕ I_N.

Therefore the same identity holds for every chronological partial product and
the complete word, with the same ordered coefficient list. Self-contractions,
nonzero rank-one status and idempotence are unchanged. If the original full
endpoint is Q_A⊕I_S, the restricted endpoint is Q_A⊕I_K. This includes all
dirty inputs and both off-diagonal endpoint blocks. Label-only prices and
call counts are unchanged. B is a coordinate witness, not a priced physical
conversion or an additional operation executed by the word.

Brian's PR4783 proves that a normalized simple-label S4 word with m calls and
ordered-pair crossing rank L admits such a restriction with dim K≤m-L.
That theorem is a cited premise, not replayed here. The new exact answer d
therefore satisfies d≤m-L on that domain. Computing d uses only the scalar
couplings, and gives the exact dimension for this same restriction boundary.
This proof itself also applies to other labels and fields. It does not
extend Brian's inversion-slack inequality to those other alphabets.

Gareth Davidson's PR2323 preserves active components and all contractions
while replacing couplings. Its optimum is t, already proved there. It need
not arise by a single invertible spectator basis change. The difference is

    d-t=(u-t)+(v-t).

Thus the new result counts the two pairing radicals that the stricter
coordinate restriction must keep. It does not improve PR2323's resynthesis.

The difference can be arbitrarily large even for restored words. For s≥1,
take one active role e_0 and 2s dirty roles. For j=1,...,s use the idempotent

    P_j=(e_0+e_j)(e_0*+e_(s+j)*).

Over F2[S3], for two adjacent transpositions a,b, the formal factors
G_a(P)=I+([a]+1)P and G_b(P)=I+([b]+1)P satisfy
(G_a(P)G_b(P))^3=I. Concatenate these six-call relators for all P_j.
Every dirty input is restored. Here u=v=s,t=0, so a single basis restriction
requires 2s dirty roles, while contraction-preserving resynthesis needs zero.
The endpoint itself is identity and has an empty word. This is a separation
of preservation contracts, never an endpoint-workspace or paid-call lower bound.

## 5. Verification and limits

The finite verifier enumerates every scalar subspace pair in the declared
small prime-field domains. A separate exhaustive oracle tries every ordered
direct-sum decomposition and independently finds its minimum and both counts.
It does not use the predicted minimum to prune candidates. Pairing rank is
computed from the literal evaluation image rather than Gaussian elimination.

Full-word controls use the faithful six-dimensional regular representation
of S3, with every regular input column in every role. They check each original
factor under an explicit invertible spectator basis, the discarded identity
block, and both complete restored endpoints. The regular representation is
faithful on the group algebra, so these are full formal equalities for those
fixtures. General quantifiers follow from the proof above, not the census.

Native address implementation, restricted scalar mixing, physical conversions,
precision, tape costs, ownership, geometry, supplier admission and multiplication
transfer remain separate obligations. No new κ or selected-frontier update is
claimed. The result does not optimize workspace when factors can change.
