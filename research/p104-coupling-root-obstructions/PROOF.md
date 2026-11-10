# A shortest-root obstruction to aligning opposite-sign arm idles

A scoped obstruction for a proposed changed root. No new κ.

The shortest-root rank-one Gram identity is also proved in concurrent
CrocSwap/integer-mult-bounds#6836, Section 2 Lemma 3.2, at head
`99b18108eda17764d55301aae12948b547b17635`. We repeat it to make the
actual coupling-idle alignment and extra-query obstruction self-contained;
we do not claim novelty for that common identity.

## Universal rank-one factorization lemma

Let V have dimension n over a field of characteristic other than two. Let
N=n+1, and let x_i be columns and y_i rows, with y_i x_i=0. Suppose

    (I-2 x_N y_N) ... (I-2 x_1 y_1) = -I_V.

Write X=[x_1 ... x_N], Y=[y_1; ...; y_N], G=YX, and
A=I_N+2 lower(G), where lower means strictly lower triangular part.
Successive rank-one multiplication gives

    product = I_V - 2 X A^{-1} Y.

One direct induction introduces rows w_j satisfying
w_j=y_j-2 sum_{i<j}(y_j x_i)w_i. Stacking them gives AW=Y,
and the accumulated product is I_V-2XW. This also fixes the
chronological convention in the displayed identity.

Thus X A^{-1}Y=I_V. The N-dimensional matrix
P=A^{-1}YX=A^{-1}G is an idempotent of rank n: P^2=P follows by
substituting X A^{-1}Y=I_V, and its image has dimension n because Y
has rank n. Therefore I_N-P has rank one and

    rank(A-G)=rank(A(I_N-P))=1.

Its diagonal entries are all one. Consequently A-G=v w for nonzero
scalars v_i and w_i=1/v_i. Its lower off-diagonal entries are G_ij,
and its upper entries are -G_ij. Therefore

    G_ij = sgn(i-j) v_i/v_j,
    G_ij G_ji = -1                    (i != j).

There is a useful general form: for any complete -I factorization with
N queries, the same proof gives rank(A-G)=N-n. In the arm application
below two principal 2-by-2 minors are 1+p and 1-p, where p is one
cross-Gram product. Their sum is 2, so rank(A-G)>=2 directly.

This conclusion does not assume a skew Gram matrix, positivity, an
integral basis, a special ordering of thin queries, or the sign-Gram
ansatz used by the source construction. It follows from a complete
arbitrary-input endpoint and exactly n+1 rank-one queries.

## Opposite-sign arm theorem

Consider full queries in three distinct arms L, R, and Z. Their chain
coordinates have disjoint supports; cross-arm pairings therefore come
entirely from a shared coupling space H. Write their coupling columns
and rows as u_L,v_L; u_R,v_R; and u_Z,v_Z. Suppose

    v_L u_L=1,       v_R u_R=-1.

The rank-one active coupling projectors are u_L v_L and -u_R v_R;
their complementary coupling idle projectors are

    E_L=I_H-u_L v_L,       E_R=I_H+u_R v_R.

These complements are forced if the idle remains entirely in H and
annihilates the active query on both sides: its image is ker(v), its
kernel is span(u), and H=span(u) direct-sum ker(v) since v(u) is
nonzero. In dimension two this is the unique rank-one pure coupling
idle. A carrier involving chain fields changes this premise.

Suppose the ACTUAL accumulated ordinary hub-only transport between
these sites aligns their entire complementary coupling idle projectors.
This is stronger than the existence of an unrelated abstract
conjugator. Move all ordinary hub changes to one end of the candidate
word and express every query in the resulting common gauge. In that
common gauge the alignment hypothesis means

    u_R v_R = -u_L v_L.

For any third-arm query Z, the cross-Gram products are then

    (v_L u_Z)(v_Z u_L) = tr((u_L v_L)(u_Z v_Z)),
    (v_R u_Z)(v_Z u_R) = tr((u_R v_R)(u_Z v_Z)).

They are negatives of one another. The universal lemma requires both
to equal -1 in a shortest root. This is impossible in characteristic
other than two. Hence such a hub-aligned three-or-more-arm caller
cannot be completed to -I with n+1 rank-one queries.

The same conclusion holds for alignment of ANY pair of distinct arms
in the stated four-arm family. If the two signs are equal, their
coupling rank-one matrices coincide after alignment; their mutual
cross-Gram product is tr((u v)^2)=(v u)^2=1, already contradicting -1.
If the signs are opposite, the preceding third-arm argument applies.
Thus a shortest caller with at least three disjoint arms cannot obtain
a cross-arm pure coupling-idle fusion through the actual ordinary
coupling-only transport. This does not exclude within-arm chain merges.

## Scope and endpoint accounting

The result applies after arbitrary constant invertible changes on H,
provided their total ordinary endpoint is the identity and they do not
mix the disjoint chain coordinates. Inserted normalized thin queries
can occur anywhere; they are included in N. Empty spectator fields
increase n but do not affect the cross-arm contradiction. The result
does not rule out n+2 or more queries, changed chain supports, maps
mixing coupling and chain fields, S-dependent carriers, or a different
non-scalar endpoint. In particular, it does not cover initialized
ancillas whose allowed input subspace or restored non-scalar endpoint
weakens the full arbitrary-input -I identity on the counted space.

For the normalized caller in the pinned source, the required scalar
specialization is Q=-1 and every fresh stage D_j=1. Its
lambda=(1+i)/2+((1-i)/2)Q^2 is then one, so S=lambda Q^{-1}=-1,
the final lambda correction is identity, and each full or thin
normalized query is exactly I-2xy. Thus the necessary endpoint used
here is an actual specialization of the caller's arbitrary-input
identity. It is not inferred from a favorable cost model.

The other required specialization is Q=1 and D_j=1. It gives
lambda=S=1, every normalized query is identity, the final lambda
correction is identity, and the required caller endpoint is identity.
Consequently the product of all additional ordinary maps is I. Moving
those maps to one end is therefore legitimate and leaves an actual
rank-one query word, rather than an unpriced ordinary endpoint.

For a two-dimensional coupling space, equality of the complementary
projectors is precisely equality of the single hub idle carrier and
its dual. If a proposed uniform transport includes normalized thin
queries, evaluate it at S=1: those queries become identity, so the
actual ordinary transport must still satisfy the stated alignment.

More generally any rank-one-query factorization of -I needs at least
n+1 queries. With N<n, rank(I-product)<=N contradicts rank(2I)=n.
With N=n, X A^{-1}Y=I forces square invertible X,Y, hence G=A,
contradicting their respective diagonal entries zero and one.
Therefore the excluded equality N=n+1 implies N>=n+2 here.

Let G count root child groups and m count native leaves. In the
four-arm root n=G+2+e includes e untouched spectator fields; G=m
for direct-native children. If q counts effective root thin queries,
N=G+q and the obstruction requires q>=4+e. Binary child internal
queries and their auxiliary targets are charged separately in the
complete price proof, so they are not omitted from the invoice. The e
productive rank-one spectator targets cancel e rank-one thin charges,
leaving at least four uncompensated thin charges rather than the
proposed three. This conclusion does not rely on holding e fixed.

The exact root under investigation has four arms with coupling data

    u=(A,B,B,-A),
    v=(A*-B*,A*-B*,A*+B*,A*+B*).

Within each left arm x=u+f_i+2 sum_{j<i} f_j and y=v-f_i*;
within each right arm x=u+h_i+2 sum_{j>i} h_j and y=v+h_i*.
Thus the hypotheses hold for its proposed whole-pair coupling-idle
alignment. This is a structural limitation of that proposed extension,
not a global obstruction to improving the multiplication exponent.

## Provenance

Canonical base: 7c49fe32c55de02c2c873655c804b16e4c3fef0a.
Source question: CrocSwap/integer-mult-bounds#6833, exact head
ad24ad966b857dbfed50d9121624db84b2eccc92, research/p104-chain-nested-root.
The chain-root construction is by DreamingOfClouds, building on thu-nmrc,
zxv, Cinna Davis, Ali Romman and preceding contributors. This analysis
is contributed by @CubeJerry with OpenAI ChatGPT assistance.


The corank-one Gram mechanism has characteristic-two predecessors: Cinna Davis's CrocSwap/integer-mult-bounds#4666 [minimum-query simplex proof](../productive-controller-basis-search/GLOBAL-PROOF.md) and Ali Romman's CrocSwap/integer-mult-bounds#5617 [query-frame and stage-capacity cuts](../shortest-controller-stage-capacity/PROOF.md). Those notes explicitly delimit their characteristic-two scope. Here `A=I+2 lower(G)` comes from the exact ordered characteristic-zero endpoint, and the opposite-arm trace contradiction applies to pure coupling-idle fusion. This extends that mechanism without reducing arbitrary complex callers modulo two. No worldwide priority is claimed for the elementary rank tools.
