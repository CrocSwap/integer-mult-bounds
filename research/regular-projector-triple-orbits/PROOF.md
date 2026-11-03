# Regular fully coupled rank-one triples

This proof was produced by Nick Petalas. Apache-2.0. It is a scoped written
linear-algebra proof. Finite corroboration is separate from its universal
quantifiers. Independent human and formal proof-kernel review are unclaimed.

## Contract and result

Let F be any field, n>=3, and let P1,P2,P3 be an ordered triple of rank-one
idempotents on V=F^n. Put S=P1+P2+P3. Require

1. rank(S)=rank(S^2)=3;
2. p=tr(P1 P2), q=tr(P1 P3), r=tr(P2 P3) are all nonzero.

Two triples are equivalent exactly when one invertible linear map
simultaneously conjugates all three, preserving their order. No transpose,
projector permutation or field automorphism is included in this equivalence.
Set u=tr(P1 P2 P3). Then u is nonzero. The complete invariant is

    (F,n,p,q,r,u).

The admissible quadruples are exactly p,q,r,u in F* such that

    Delta = 1-p-q-r+u+pqr/u != 0.                       (1)

A unique representative on the three active coordinates is obtained from

    G = [ 1  1    1  ]
        [ p  1    u/q]
        [ q  rq/u 1  ]                                (2)

by setting Pi=e_i times row i of G, and adjoining n-3 zero coordinates.
Over a finite field of order Q, the exact number of these conjugacy classes
is

    N(Q)=Q^4-5Q^3+9Q^2-9Q+6.                          (3)

This is one fixed algebraic state class, not a classification of arbitrary
triples or a bound on a complete physical register search.

## Rank-one factorization and the active space

Write Pi=x_i y_i with x_i nonzero and y_i a row covector. Idempotence says
y_i x_i=1. Put C=[x_1 x_2 x_3], D=[y_1;y_2;y_3] and G=DC. Then S=CD.
The first rank condition implies rank C=rank D=3. Thus C is injective and
D is surjective, so rank(S^2)=rank(C G D)=rank G. The second rank equality
therefore makes G invertible.

Consequently W=im C and N=ker D have dimensions 3 and n-3 and intersect
only at zero. Thus V=W direct-sum N. All Pi preserve W and kill N. In the
basis x_1,x_2,x_3 of W, Pi has exactly row i of G in its ith row and zero
in the other rows. Conversely any invertible unit-diagonal G constructs
rank-one idempotents with rank(S)=rank(S^2)=3, including after adjoining zero
spectators.

## Completeness of the four traces

The factorization Pi=x_i y_i is unique up to x_i -> d_i x_i,
y_i -> d_i^(-1) y_i, with d_i in F*. Its Gram matrix therefore changes as

    G -> diag(d)^(-1) G diag(d).                       (4)

Ambient simultaneous conjugation preserves G when the factors are carried
along. Conversely, equal G gives an intertwiner by mapping the three image
basis vectors to their counterparts and extending by any isomorphism between
the common kernels. Thus simultaneous conjugacy is exactly diagonal similarity
of these Grams, together with equal ambient n and field F. This argument is
direct and does not assume a predecessor's two-projector classification.

Write g_ij=y_i x_j. Rank-one multiplication gives

    p=g_12 g_21, q=g_13 g_31, r=g_23 g_32,
    u=g_12 g_23 g_31,
    v=tr(P1 P3 P2)=g_13 g_32 g_21,
    uv=pqr.                                           (5)

The nonzero pair traces imply that all six off-diagonal g_ij are nonzero,
and hence u is nonzero. Apply (4) with
d_1=1, d_2=1/g_12, d_3=1/g_13. The first row becomes (1,1,1). Equations
(5) then force exactly (2). Any further diagonal similarity preserving this
first row has d_1=d_2=d_3 and acts trivially. This proves uniqueness and
completeness over every field. Expanding the determinant of (2) gives (1),
which proves that there are no further realizability restrictions.

The ambient centralizer of a representative is F* on W times GL(N).
Indeed a commuting map preserves each image line and each kernel, so it
preserves W and N. On W it is diagonal; the six nonzero couplings force
its three diagonal entries to agree. Conversely these maps commute.
Over a finite field each ambient class thus has size

    |GL_n(F)| / ((Q-1)|GL_(n-3)(F)|).                  (6)

Use |GL_0|=1. Formula (6) counts actual ordered triples in one class, not
additional conjugacy classes.

## Exact count over every finite field

There are (Q-1)^4 candidate quadruples. Count those with Delta=0. For fixed
p,q,u, rewrite that equation as

    A+B r=0,  A=1-p-q+u, B=pq/u-1.                    (7)

If u!=pq, then B!=0, so exactly one r solves (7). This r is nonzero exactly
when A!=0. Before excluding A=0 there are (Q-1)^2(Q-2) choices of p,q,u.
For A=0 we must have u=p+q-1, nonzero and unequal to pq. The inequality
u!=pq is equivalent to (p-1)(q-1)!=0. There are (Q-2)^2 pairs with
p,q outside {0,1}, of which Q-2 have p+q=1. Therefore the number to remove
is (Q-2)(Q-3). This case contributes

    (Q-1)^2(Q-2) - (Q-2)(Q-3).

If u=pq, then B=0 and A=(1-p)(1-q). Thus Delta=0 exactly when p=1 or
q=1, independently of the nonzero r. This contributes

    (2Q-3)(Q-1).

Adding the two contributions gives Q^3-3Q^2+5Q-5. Subtracting this from
(Q-1)^4 proves (3). The argument uses only field arithmetic and applies to
every prime power, including characteristic two. At Q=2 the intermediate
products containing Q-2 are zero, so the same counting argument remains valid.

## Why pair data alone is insufficient

Over F5 take (p,q,r)=(1,1,1). The choices u=2 and u=3 give the invertible
Grams

    [1 1 1]           [1 1 1]
    [1 1 2]     and   [1 1 3].
    [1 3 1]           [1 2 1]

Both determinants equal 3. They have the same pair traces. Their oriented
triple traces differ, so they are not simultaneously conjugate. This also
shows why transposition or reversing a word cannot silently be included in
the stated equivalence. The witness is a distinction between states, not a
paid-call lower bound.

## Finite evidence and scope

The checker enumerates every unit-diagonal Gram with nonzero off-diagonal
entries over F2,F3,F4,F5,F7. Its diagonal orbits are compared as complete sets
with a second enumeration that starts from four trace parameters. A six-term
determinant and row reduction separately check invertibility. Actual matrix
multiplication checks idempotence and the projector traces. F4 uses
F2[t]/(t^2+t+1), rather than integers modulo four.

For every canonical ternary class, another check enumerates every GL3(F3)
basis change, computes all three conjugated matrices and their traces, and
counts the distinct endpoints. Zero spectators of dimensions one and two,
ten invalid-domain cases and the pair-trace ambiguity witness exercise the
boundaries. These finite checks corroborate the proof; they do not replace
its all-field argument or establish a physical caller. Singular active
systems, missing pair couplings, unordered equivalence, native implementation,
dirty-helper programs and a complete recursive invoice are outside scope.
