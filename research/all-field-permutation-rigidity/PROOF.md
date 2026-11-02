# Every shortest single-permutation word has one scalar projector

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement

Let K be any field, n>=2, and R>=1. Let w be a nonidentity element of S_n
and let E in M_R(K) satisfy E^2=E and rank E=1. Work in the full formal
group algebra M_R(K[S_n]), with products acting on columns, rightmost first.
The endpoint is

    T = I + ([w]-[e]) E.

A normalized paid factor is

    D_s(N) = I + ([s]-[e]) N,

where s is a simple adjacent transposition, N^2=N, and rank N=1.
Every register has arbitrary entrance data. Equality means equality of all
formal coefficients, including the return of all dirty spectators. Arbitrary
scalar GL_R(K) operations may occur between paid factors.

**Theorem.** The minimum paid length is inv(w). In every normalized word of
this length, every paid coupling is exactly E and the label sequence is a
reduced expression for w. Conversely, every reduced expression for w, with
E at every call, attains the endpoint.

This is a scoped algebraic proof, with finite corroboration. The theorem
does not price physical scalar mixing or construct a native supplier.

## What is inherited

Brian's PR4765 proves tight spectator elimination over F2 for the S4
ordered-pair module. Its Grassmann equality argument is the proof method
used below. Ross Richardson's PR1989 supplies the ordered-pair cut for
symmetric groups and the binary inversion tariff, retaining Adam Gall's
cut-method credit. Nick Petalas's PR4851 already proves the length-three S3
single-target rigidity theorem over every field, even with a larger scalar
coupling alphabet. That special case is inherited.

The new statement is the all-field, all-S_n single-target equality
classification in the stated idempotent alphabet. We prove the finite
ordered-pair geometry directly, rather than replaying predecessor searches.
No literature-priority claim is made.

## Normalize and choose the active line

Move each scalar GL_R(K) map through its neighboring paid factor by
conjugation. This preserves projector rank and idempotence. Augmentation,
which sends every [g] to 1, sends the endpoint and every paid factor to I.
It therefore forces the residual free scalar map to be I. The normalized
word has only the displayed paid factors.

Write A=im E and S=ker E, so K^R=A direct sum S. The endpoint acts by w
on A and by identity on S. This basis choice is only for the proof. The
conclusion in the original basis will be N=E. If R=1, S is zero and every
rank-one idempotent is already E=I; the argument also covers this case.

## Ordered-pair geometry over K

Let U have basis e_(a,b) for distinct a,b in {1,...,n}. The action of g sends
e_(a,b) to e_(g(a),g(b)); these are formal basis labels over K. Put

    U+ = span{e_(a,b): a<b},    U- = span{e_(a,b): a>b},
    V = K^R tensor U,          H = K^R tensor U+.

This is a representation of the group algebra over every field. No ordering
or positivity is imposed on K, and the geometric labels are not identified
in characteristic two. Representation equality is used only as a necessary
consequence of the full formal endpoint.

For an invertible represented matrix P define

    phi(P) = rank(pi_(K^R tensor U-) P|_H)
           = dim H - dim(H intersect P^(-1)H).

The second equality is rank-nullity. Both subspaces in the intersection
have dimension dim H. For equal-dimensional subspaces X,Y set

    d(X,Y) = dim X - dim(X intersect Y).

This is an invertible-map-invariant metric. If X,Y,Z all have dimension k
and d(X,Z)=d(X,Y)+d(Y,Z), then

    X intersect Z subset Y subset X+Z.                 (1)

Indeed, set a=dim(X intersect Y), b=dim(Y intersect Z),
c=dim(X intersect Z), and t=dim(X intersect Y intersect Z). The inclusions
(X intersect Y)+(Y intersect Z) subset Y and the inequality t<=c give
a+b-t<=k and a+b<=k+c. This proves the triangle inequality. Equality forces
t=c and dim((X intersect Y)+(Y intersect Z))=k, proving both inclusions in
(1). This is the inherited Grassmann equality lemma over an arbitrary field.

The crossing block of a permutation has one independent column for each
inversion. Consequently phi(T)=inv(w), since E has one-dimensional image.

For a simple s=(i,i+1), put alpha=e_(i,i+1), beta=e_(i+1,i), and let
H_other be the span of the remaining positive ordered-pair basis vectors.
The simple transposition permutes those remaining positive vectors.
Write N=u v with v(u)=1. On ker v the paid factor is identity, and on
span u it acts by s. Thus G=D_s(N) is invertible, G^2=I, and

    GH = (K^R tensor H_other)
         direct sum (ker v tensor span alpha)
         direct sum (span u tensor span beta).          (2)

It follows that d(H,GH)=phi(G)=1. These statements use idempotence and hold
unchanged in every characteristic.

## Tight peeling forces both scalar sides onto A

Suppose an invertible represented P fixes S tensor U pointwise and preserves
A tensor U, and suppose a right peel satisfies phi(PG)=phi(P)-1.
Put X=H, Y=GH, and Z=P^(-1)H. Since G is an involution,

    phi(PG)=d(H,G P^(-1)H)=d(GH,P^(-1)H)=d(Y,Z).

The hypothesis is equality in the triangle inequality, so (1) applies.
Since P is the identity on S tensor U,

    S tensor U+ subset X intersect Z,
    X+Z subset (A tensor U) direct sum (S tensor U+).    (3)

By (2), u tensor beta lies in Y. The second inclusion in (1) and (3) forces
the spectator part of u to vanish. Thus u is in A. For every x in S,
x tensor alpha lies in X intersect Z and hence in Y. In (2) every alpha
coefficient lies in ker v. Therefore v(x)=0 for every x in S.

Both sides matter: N has image in A and annihilates S. Because A is a
line and N is a nonzero idempotent, N acts as identity on A. Hence N=E.
This conclusion is about the full scalar coupling, not only its image in
the ordered-pair representation. Therefore the full formal factor fixes
every spectator exactly.

## Every peel in a shortest word is tight

For invertible represented P,Q, the triangle inequality and its invariance
give phi(PQ)<=phi(P)+phi(Q). Every paid factor has phi=1, so any m-factor
word with endpoint T satisfies m>=inv(w).

If m=inv(w), let P be the product of any initial j written factors.
Subadditivity gives phi(P)<=j and phi(T)<=phi(P)+(m-j), forcing phi(P)=j.
Starting at T, removing the rightmost written factor therefore drops phi
by one. The tight-peeling argument forces that factor's coupling to be E.
Its removal leaves a full formal endpoint acting only on A and fixing S.
Apply the same argument to the next peel. Induction forces all couplings
to be E. There is no bound on R in this reasoning.

With common projector E, the full formal product is

    I + ([s_1 ... s_m]-[e]) E.

Distinct permutations are distinct group-algebra basis elements, so formal
equality with T implies s_1 ... s_m=w. Its length m=inv(w) makes the
expression reduced. Finally, adjacent sorting gives a reduced expression
of length inv(w), and using E at every factor gives the displayed endpoint.
This proves the lower bound, rigidity and converse.

## Scope boundaries

The theorem requires a single active line, adjacent labels, rank-one
idempotents, the exact full endpoint and minimum unweighted length. Inserting
a mixed factor and its inverse creates a longer valid word using spectators.
Allowing the whole target permutation as a paid label can realize T in one
call. The verifier checks these boundaries. Higher-rank targets, nonidempotent
couplings and arbitrary separate generator prices are not classified here.

Finite checks corroborate the written proof and do not establish its universal
quantifiers by enumeration. Independent human and formal proof-kernel review
are unclaimed. Native hosting, precision, tape, recursive invoices, supplier
admission and the complete multiplication theorem remain outside scope.
