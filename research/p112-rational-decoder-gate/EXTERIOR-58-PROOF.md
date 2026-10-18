# Exterior-factor floor for decoders with at most 58 scalar terms

Fix the full-group scalar mask and physical tariff of this package's changed
P112 cover. The candidate's normalized LF SHA256 is
`dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b`.

**Theorem.** Every rational fitting decoder expressed using at most 58 nonzero
scalar rank-one terms has total full-group port-space charge at least 297.
Consequently it cannot meet the necessary positive-saving allowance
`C < 2672/9`, equivalently integer `C <= 296`. This bound is not claimed sharp.
A successful scalar decoder on this mask therefore needs at least 59 terms.

The theorem permits arbitrary rational denominators and exterior factor
components. It covers fitting matrices of either possible rank, 57 or 58.
It does not cover 59 or more terms, changed covers, block-valued messages, or
changed tariffs, and proves no native supplier or exponent improvement.

The [preceding proof](RANK-TIGHT-PROOF.md) establishes the principal identity
minor of order 57 and the sharp charge 334 for exactly 57 terms. Fewer than
57 terms are impossible. It therefore remains to prove the claim for 58 terms.
We use its 40-space tariff lemma, but impose neither of its canonical-span
hypotheses on the original 58-term factors.

## Setup and a compression lemma

Normalize the fitting diagonal to one, which changes no supports or tariffs.
Let I contain all ports of odd groups G1,G3,...,G37, and let R contain the even
groups and the residual group G0. Write

    K = [ I57  A ] = U V^T,       P=U_I, Q=V_I, P Q^T=I57.
        [ B    D ]

The retained coordinates form 19 blocks of size three. For paired component i,
write `H_i=E_(2i-1)+E_(2i)`; write `J=E37`. Every term is charged using the sums
of all complete physical group spaces it touches. Ignoring residual support
can only lower that charge.

Suppose dual blockwise coordinate maps produce a compressed identity of
dimension d, retain all three J coordinates, and have this property: any
nonzero compressed paired component forces its original physical factor to
touch the whole corresponding H_i. Components may retain one, two, or three
coordinates, or be deleted. Discard Z terms that become zero after compression.
The other `m'=58-Z` terms have excess `e=m'-d >= 0` over the identity's rank.

The preceding 40-space lemma applies to these component supports regardless
of their internal dimensions. A pure term, with one compressed factor confined
to J, costs at least three; restricting the identity to its other d-3 coordinates
bounds their count by `Ppure <= e+3`. Nonpure terms cost at least four. If L4,L5
count their actual charges four and five, the random-order, strictly triangular
subset argument gives `2 L4+L5 <= 4e`. This remains valid when actual charge five
has compressed tariff four: its selection probability is only larger.
Consequently

    C >= 6m' - 3Ppure - 2L4 - L5
      >= 6m' - 7e - 9 = 7d - 67 + Z >= 7d - 67.       (1)

No residual bonus is claimed. In particular, retaining d>=52 proves C>=297.
This is a dual compression of an identity, not necessarily a principal minor.

## Rank-57 fits: one canonical factor side and one exterior direction

If rank(K)=57, Sylvester's inequality gives
`rank(U)+rank(V) <= 57+58=115`. Both ranks are at least 57, so at least one
factor side has rank 57. Transpose if necessary and suppose rank(U)=57.
The preceding normal-form proof then gives

    D=BA,   U=[P;BP],   V=[Q;A^T Q+f z^T],

where z spans the one-dimensional kernel of P and f is an arbitrary rational
55-vector. The last formula follows because every row of `V_R-A^T Q` lies in
ker(P). Also `Q^T P=I58-z w^T` for a vector w with `w^T z=1`.

All paired maps in A,B are invertible inverse maps; the residual row and column
may use arbitrary vectors b,a with ba=1. No alignment of these vectors to a
coordinate is assumed. In paired component i, the reader blocks are

    q_i,t,    M_i q_i,t+f_i z_t

for an invertible M_i. Call t active when z_t is nonzero. Let F be the paired
components where f_i is nonzero; residual f_0 is unrestricted and excluded
from F. An active reader touches at least one complete triad in every pair F.

For each i in F, delete the reader direction `M_i^-1 f_i` and one dual source
coordinate. A nonzero retained reader component cannot be canceled by the
exterior shift, so both physical triads remain touched. Source components
already touch both triads. This gives the compression hypothesis with
`d=57-|F|`; by (1), `C>=332-7|F|`. Thus |F|<=5 implies C>=297.

### Finite geometry for six or more affected pairs

Generate all binary spans of E1,...,E37, omitting the residual line. There are
exactly 1750, with dimension histogram

    {0:1, 3:37, 4:2, 5:59, 6:599, 7:657, 8:394, 9:1}.

For each reader span T put

    M(T)={i: E_(2i-1) is contained in T or E_(2i) is contained in T}.

The source-pinned checker proves:

1. If |M(T)|>=6 then `rho(H_i,T)>=5` for every i and `rho(J,T)>=2`.
2. For any fixed subset F of at least six pairs, the union

       L(F)={i: some generated T has F subset M(T) and rho(H_i,T)<6}

   has size at most 10. The union is over **all** compatible reader spans for
   the same F, not a separate bound for each reader.

Only 121 reader spans have |M(T)|>=6 and a paired tariff below six. Enumerating
every subset F of their coverage sets gives 2318 nonempty F-to-L cases; all
omitted F have empty L(F). The maximum union size 10 occurs at
`F={1,4,7,11,12,14}`, with `L={1,4,5,6,7,8,10,11,13,18}`.
Closure under all 37 generators certifies completeness. Adding actual residual
support can only raise every tariff used here.

### The large-F invoice

Assume |F|>=6. An active term with a paired source component costs at least
five. If it costs below six, every paired component of its source lies in
L(F). Such source columns lie in a space of dimension at most `3*10+3=33`,
including J. Since P has nullity one, there are at most 34 such columns.

For an inactive index, `q_t^T p_t=1` and its reader is canonical. The preceding
common-component argument gives tariff at least six unless the source or
reader is supported only in J. Let A be all pure-J source indices and B the
inactive pure-J reader indices. Put alpha=|A|, beta=|B|, gamma=|A intersect B|.
The rows `Q_B^T P` are the corresponding rows of I58, so Q_B consists of beta
independent vectors in J and its pairing on P_A has rank gamma. Also
`rank(P_A)>=alpha-1`. The annihilator of these beta independent covectors in J
has dimension 3-beta, giving

    alpha-1-gamma <= 3-beta,       |A union B|<=4.

Every exceptional term costs at least two: active pure-J sources use the
finite geometry lemma, and inactive ones cost three. Other than these four
possible exceptions and the 34 possible active cheap terms, every term costs
at least six. Thus

    C >= 6*58 - 34 - 4*4 = 298.                       (2)

This finishes rank-57 fits. This argument also tolerates arbitrary additional
physical residual entries on the source side: they only raise the lower bounds.
The source columns used in the count must have nonzero retained vectors; a
possible zero retained column in the next case is handled separately below.

## Rank-58 fits: a rank-one Schur complement

Now rank(K)=58. Choose z spanning ker(P) and w spanning ker(Q), normalized by
`w^T z=1`. The projection `Q^T P` has image im(Q^T) and kernel ker(P), so this
normalization exists and

    Q^T P=I58-z w^T,
    U_R=BP+g w^T,    V_R=A^T Q+f z^T,
    D=BA+g f^T.

Both g and f are nonzero; their outer product is the rank-one Schur complement.
Here A,B have only the original mask restrictions. The rank-57 normal form is
not assumed.

### The Schur-support forest

A block `(BA)_ij` can be nonzero only when the R-groups i,j share an allowed
odd neighbor. A fitting off-diagonal block K_ij can be nonzero only when those
full group spaces are orthogonal. These two tests show that `(g f^T)_ij` must
vanish except on diagonal blocks and the following nine undirected edges:

    0-2, 0-8, 0-10, 0-16, 0-20, 0-28, 4-24, 8-22, 12-30.

This graph is a forest. If G and F are the nonzero group supports of g and f,
then G times F is a nonempty rectangle in the forest with loops. If both sets
have at least two vertices, they must both equal one edge's two endpoints:
two distinct vertices have at least two common closed neighbors only when
adjacent, and those neighbors are exactly the endpoints. Otherwise one set is
a singleton and the other is in its closed neighborhood.

The checker enumerates all 314 ordered nonempty rectangles: 8 touch group4,
53 are ordinary, and 253 have one side supported only on residual group0.
The ordinary cases have at most four nonzero even blocks across g and f.
Only four rectangles have more than five: up to transposition, g is residual-only
and f touches all six even neighbors `{2,8,10,16,20,28}`, optionally also G0.

### A local dual compression allowing singular paired maps

For an ordinary paired block, suppose

    B_i A_i+g_i f_i^T=I3.

Define its bad source and reader subspaces by

    X_i={p: B_i p lies in span(g_i)},
    Y_i={q: A_i^T q lies in span(f_i)}.

If g_i=0, X_i is zero; otherwise `[B_i,g_i]` has row rank three by the identity,
so X_i has dimension one. Likewise Y_i has dimension zero or one according as
f_i is zero or nonzero. This works even when A_i or B_i is singular.

The standard pairing between `X_i^perp` and `Y_i^perp` has rank at least
`3-dim(X_i)-dim(Y_i)`. Choose dual row maps L_i,R_i of that size, with
`L_i R_i^T=I`, whose kernels contain X_i,Y_i. A nonzero compressed source
`L_i p` cannot have its even block canceled by `g_i w_t`; a nonzero compressed
reader `R_i q` cannot be canceled by `f_i z_t`. Thus the compression implication
for the complete H_i holds. At most one coordinate is lost for each nonzero
even block of g and for each nonzero even block of f.

### Ordinary and exceptional branches

If neither g nor f touches group4, the diagonal at group4 gives
`B_4,3 A_3,4=I3`. Its maps are invertible; the forbidden 4/24 blocks, with zero
Schur corrections, force `A_3,24=B_24,3=0`. Every even group now has only its
matching odd contribution, so the local compression applies to every pair.
When at most five even blocks of g,f are nonzero, it retains d>=52, proving
C>=297 by (1). Residual row and column formulas are irrelevant to this estimate.

If either g or f touches group4, the forest rectangle property puts both
supports inside `{4,24}`. This includes a Schur complement supported only on
the diagonal block4, where its maps can be singular. Do not discard the extra
odd3/group24 couplings. Instead delete all three odd23 coordinates, and apply
the local compression to odd3/group4, which still has only its matching odd
neighbor and satisfies `B_4,3 A_3,4+g_4 f_4^T=I3`. This loses at most two more
coordinates. Every other pair retains all three, and J retains three; again
d>=52. Any group24 support of the surviving factors only increases cost.

### The residual-only six-neighbor branch

The only remaining case has, up to transposition, g residual-only and f nonzero
in all six even neighbors of G0. Every paired A_i,B_i is now invertible and the
4/24 extra coupling is zero. Sources touch both triads exactly when their
retained paired component is nonzero; their residual entries may be arbitrary.

If no retained source column is zero, the large-F argument (2) applies and
gives C>=298. It used only these paired support implications, the identity
`P Q^T=I57`, and the unique reader shift; additional source residual support
cannot lower its tariff estimates.

If a retained source column is zero, there is exactly one, because P has rank
57 and 58 columns. Then z is supported only on that index. The other 57 retained
source/reader columns are square dual bases, with canonical paired physical
supports. Ignoring all residual entries, the preceding 57-term argument allows
at most three pure-J exceptions of cost at least three and has 54 other terms
of cost at least six. Their subtotal is 333; the last term has nonnegative
cost. This finishes rank-58 fits and the theorem.

## Replay, limits, and credit

Run from the repository root, using Python 3.12 standard library only:

```sh
python3 -I -O -B research/p112-rational-decoder-gate/check_exterior_58.py
python3 -I -O -B research/p112-rational-decoder-gate/independent_exterior_58.py
```

The checker is read-only and prints JSON. It authenticates this candidate,
the selected replay archive and its payload, reconstructs the 1750 physical
reader spaces, enumerates all 2318 affected-set unions, and derives all 314
Schur support rectangles directly from the original mask. Semantic controls
reject missing closure spaces, weakening whole-triad containment to nonzero
intersection, and adding an edge that destroys the Schur forest. Replay the
preceding [rank-tight checks](RANK-TIGHT-PROOF.md#replay-and-credit) as well for
the principal identity and 40-space acyclic lemma used here.

A separate AI agent audited this proof and independently reconstructed the
finite geometry using explicit vector sets and annihilator-intersection ranks;
its Schur check independently enumerates all 314 rectangles. The two
implementations agree. These are scoped symbolic proofs supported by finite
checks, not proof-assistant
formalization or independent human review.

The selected P112 labels, changed cover, strict mask and physical tariff retain
the predecessor attribution in the [README](README.md). Prepared by flyingviper
with substantial OpenAI Codex assistance and separate AI-agent checking. New
work is Apache-2.0. The next constructive question remains a full-group scalar
decoder with at least 59 terms and charge at most 296, or a changed interface
outside this fixed scalar mask.
