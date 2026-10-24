# Tight words cannot use restored spectators

This is a written proof over F2. The all-workspace step is new; the final
four-role exclusion is the separately identified finite result of PR3888.
It is not a formal-kernel certificate.

## 1. Model, order and the target

Let R=A⊕S be the binary register space, where A has the four target
coordinates and S contains any finite number of dirty spectator coordinates.
Work in M_r(F2[S4]). The only paid labels are the adjacent transpositions
s1=(12), s2=(23), s3=(34), with prices (2,1,2). Each normalized factor is

    G_s(u,v) = I + ([s]+[e]) u v^T,     v^T u=1.

All inputs are arbitrary. The required full formal endpoint is

    T = diag([2143],[3142],[4231],[2143], [e],..., [e]).

Permutation words use one-line notation. Products are written in matrix order:
the rightmost factor acts first on columns. Peeling the rightmost written factor means
P -> P G, since G is an involution. Arbitrary interleaved free GL_r(F2)
changes are absorbed by conjugating projectors; augmentation [g]->1 forces
the residual free scalar map to be I. This inherited normal form classifies
normalized paid factors, not literal scalar gates in a presentation.

## 2. The finite Grassmann equality lemma

For k-dimensional subspaces X,Y of a finite-dimensional vector space put

    d(X,Y) = k - dim(X∩Y).

This distance is invariant under invertible linear maps. It obeys the
triangle inequality. More precisely, if

    d(X,Z) = d(X,Y) + d(Y,Z),

then

    X∩Z ⊆ Y ⊆ X+Z.                                      (1)

For completeness, let a=dim(X∩Y), b=dim(Y∩Z), c=dim(X∩Z),
and t=dim(X∩Y∩Z). Since (X∩Y)+(Y∩Z)⊆Y, a+b-t≤k, and t≤c.
Consequently a+b≤k+c, which is exactly the triangle inequality.
Equality gives a+b=k+c, so t=c and a+b-t=k. Thus X∩Z equals
the triple intersection, and Y=(X∩Y)+(Y∩Z). Both inclusions in (1)
follow. No positivity, probability, or assumption about the field is used.

## 3. Ordered-pair cut and one paid factor

Use the 12-dimensional permutation module U with basis e_(a,b) for
1≤a,b≤4, a≠b. S4 acts on both coordinates. Write

    H0 = span{e_(a,b): a<b},   K0 = span{e_(a,b): a>b},
    V = R⊗U,                 H = R⊗H0.

The action is only a necessary image of formal equality, never an oracle
for equality in F2[S4]. A simple generator s_i carries exactly one positive
basis vector α=e_(i,i+1) to its negative partner β=e_(i+1,i), and permutes
the other five positive basis vectors amongst themselves. Set
H_other=span of those other five vectors.

For P=u v^T with v^T u=1, R=ker(v^T)⊕span(u). On these two summands
G acts as I and s, respectively. Hence its represented image of H is exactly

    G H = (R⊗H_other) ⊕ (ker(v^T)⊗span(α))
                            ⊕ (span(u)⊗span(β)).          (2)

In particular d(H,GH)=1. This explicit subspace identity is the point where
the single-crossing simple-label and rank-one-idempotent hypotheses enter.

For any invertible represented M define its forward crossing rank

    φ(M) = rank(π_K M|_H) = dim H - dim(H∩M^(-1)H)
         = d(H,M^(-1)H).

Thus φ(PG)=d(GH,P^(-1)H), using G^(-1)=G and invariance of d.
This verifies the right-peeling orientation explicitly.

## 4. One-step spectator elimination

**Lemma.** Suppose P=Q_A⊕I_(S⊗U), with Q_A any invertible linear operator
on A⊗U. If a legal paid factor G satisfies φ(PG)=φ(P)-1, then both u and v
have zero spectator component. Consequently PG also has the form
Q'_A⊕I_(S⊗U).

Put X=H, Y=GH and Z=P^(-1)H. Section 3 gives d(X,Y)=1, and the hypothesis
gives d(X,Z)=1+d(Y,Z). Apply (1). Because P fixes every spectator vector,

    S⊗H0 ⊆ X∩Z,             X+Z ⊆ (A⊗U) ⊕ (S⊗H0).       (3)

The second inclusion contains no vector with nonzero spectator component
at any negative address. But u⊗β belongs to Y by (2). Since Y⊆X+Z,
its spectator component must vanish, so u∈A.

For every w∈S, w⊗α belongs to X∩Z by (3), hence to Y. In (2), the
coefficient at α of every vector of Y lies in ker(v^T). Therefore
v^T w=0 for every w∈S: v annihilates the entire spectator subspace.
This is the second, independent condition; ruling out only u is insufficient.
The formal matrix u v^T consequently has zero spectator rows and columns,
so the paid factor itself is an active-block factor plus spectator identity.
The conclusion is about the full formal factor, not merely its represented
image. This proves the lemma.

## 5. Eliminate spectators from an inversion-tight word

Suppose a normalized m-factor word equals a formal endpoint
Q_A⊕I_S and that its represented crossing rank is m. Every legal factor
has φ=1. The triangle inequality gives φ of each prefix at most its length,
and φ(T)≤φ(prefix)+φ(suffix). Therefore every prefix of length j has
crossing rank exactly j. In particular the rightmost-factor peel drops φ by one.

Starting at T, section 4 forces the rightmost written factor to have zero spectator rows
and columns. The peeled endpoint still fixes spectators. Repeating at each
successive peel forces **every normalized paid factor** to be supported on A.
Restricting the original formal word to A gives the same m-factor word on
exactly the target roles, with the same labels, prices and full endpoint.
There is no bound on dim S. This is a dimension-independent implication,
not evidence extrapolated from a finite register census.

The tightness premise matters. A legal mixing factor G followed by G can be
inserted into a coordinate word, restoring all spectators while using them
internally. Such a word has two extra calls and is not inversion-tight.
The conclusion also requires spectator identity at the full endpoint;
a mixing factor alone is tight for its own endpoint but can leak into S.

## 6. Apply the lemma to the fixed mixed S4 tuple

The inherited cut values for this target are

    inversion cut = 12,   natural cut at position 1 = 4,
    natural cut at position 3 = 4.

They follow directly from the four permutation actions: their inversion
counts are 2,3,5,2, and each natural boundary count is 1 for each target.
Spectator identities contribute zero. Each adjacent paid factor charges one
to the inversion cut; only s1 charges the first natural cut and only s3
charges the third. Thus any word with label counts (n1,n2,n3) obeys

    n1+n2+n3≥12,   n1≥4,   n3≥4.

If 2n1+n2+2n3≤20, writing the cost as
(n1+n2+n3)+(n1+n3) forces equality throughout. Necessarily

    (n1,n2,n3)=(4,4,4),    m=12,    φ(T)=m.

Section 5 then eliminates every spectator, reducing this putative cost-20
word to an exact four-role word. PR3888's complete four-role search excludes
that word: all 360 first factors and every subsequent legal factor are
covered by necessary cut-window pruning, and the tree has node counts

    56, 1904, 28562, 207168, 571536, 648720, 381816, 0.

The source-bound independent explicit-matrix engine was completed afresh in
this package. It enumerates every nonzero u,v in F2^4 with v^T u=1 and each
simple label: 120 projectors times three labels, or 360 gates. The `all`
argument selects every first gate; recursion tries every gate with a remaining
label count. States are the right-peeled target in the natural and ordered-pair
representations. Its only pruning requires each forward and reverse cut rank
to lie between the target rank minus removed charge and the remaining charge.
Both inequalities follow from rank subadditivity, so no genuine formal word
can be pruned. The rank routine uses binary elimination and the represented
matrices have at most 48 rows, within the 64-bit storage used at r=4.

A nonfaithful representation may retain false candidates; it cannot lose a
formal word satisfying those necessary windows. The zero layer at depth eight
therefore excludes every twelve-factor formal candidate. No terminal formal
coefficient equality check is needed for an already empty search tree.
`finite/REPLAY.json` and `indep.stdout` record this completed independent run.
The extra primary cross-check was stopped before completion and is not used
as evidence. This finite premise remains indispensable to the corollary;
the spectator lemma alone does not prove the four-role exclusion.

Costs are integral, so every finite-workspace implementation costs at least
21. The inherited coordinate words of costs 4,5,8,4 attain 21 while leaving
all spectators unchanged. Therefore the exact optimum is **21 for every
finite number of restored dirty spectators**.

No claim follows for a non-simple paid label, a different target or price,
a word with inversion slack, nonlinear/free address operations, or a native
physical implementation. A representation is used only for the necessary
rank and elimination argument; full formal equality remains the boundary.
