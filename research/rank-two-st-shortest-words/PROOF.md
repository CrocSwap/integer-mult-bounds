# All shortest words for the rank-two st endpoint

Prepared by ToikY with substantial OpenAI Codex assistance, including separate
AI implementations and static review. Apache-2.0. This is a written algebraic
proof with bounded exact corroboration, not a proof-kernel certificate or a
physical supplier construction.

## Exact statement and predecessor boundary

Let K be any field, R>=2, and E in M_R(K) be an idempotent of rank two.
Work in the full formal group algebra M_R(K[S4]). Put s=(12), t=(23),
u=(34), with permutation composition (ab)(i)=a(b(i)). Products of matrices
act on columns, rightmost first; st has one-line notation 2314. A paid factor
is D_r(N)=I+([r]-[e])N, where r is one of s,t,u and N is a rank-one
idempotent. Arbitrary interleaved scalar GL_R(K) operations are normalized
by conjugation. The required endpoint is T=I+([st]-[e])E, including exact
identity on every dirty spectator in ker E.

**Theorem.** The minimum normalized paid length is four. Every word of that
length belongs to exactly one of the following two families of written
factor lists:

    A: D_s(P) D_s(E-P) D_t(Q) D_t(E-Q),
    B: D_s(P) D_t(P) D_s(E-P) D_t(E-P).

In A, P and Q are arbitrary rank-one idempotents supported inside E:
EP=PE=P and EQ=QE=Q. They need not commute. In B, P is any such
projector. The families are disjoint because their label strings are sstt
and stst. No u-labelled call occurs in a shortest word. The statement
classifies normalized paid couplings, not arbitrary literal free scalar
gate presentations.

The minimum length and tight spectator elimination are inherited. Ross
Richardson PR1989 and Adam Gall's cut lineage give the binary inversion
tariff. Brian/JoyboyBrian PR4765 sections 2--5 give the general tight
active-block spectator elimination, whose proof uses no field assumption.
Nick Petalas PR6449 supplies the all-field ordered-pair argument and
rank-one shortest-word rigidity. PR4851 already covers its earlier S3
rank-one special case. We reproduce the needed short geometric argument to
make the bindings explicit; we do not claim those lemmas or the minimum as
new. The addition is the complete internal rank-two equality classification
for this one endpoint, answering a released next question of PR6449.

## Inherited geometry and normalization

Scalar conjugation carries a rank-one idempotent to another such projector.
Augmentation [g]->1 sends every paid factor and T to I, so the residual
free scalar map is I. Thus it suffices to classify the displayed factors.
Choose the decomposition K^R=A direct sum S, A=im E and S=ker E.

Let U have the twelve formal ordered-pair basis vectors e_(i,j), i!=j,
with g e_(i,j)=e_(g(i),g(j)). Let U+ span the pairs i<j, U- the pairs
i>j, and H=K^R tensor U+. For represented invertible M put

    phi(M)=dim H-dim(H intersect M^(-1)H).

For equal-dimensional subspaces set d(X,Y)=dim X-dim(X intersect Y).
This is an invertible-map invariant metric. Equality in its triangle
inequality implies

    d(X,Z)=d(X,Y)+d(Y,Z)  =>  X intersect Z subset Y subset X+Z.       (1)

Indeed, with a=dim(X intersect Y), b=dim(Y intersect Z),
c=dim(X intersect Z), and h=dim(X intersect Y intersect Z),
a+b-h<=dim X and h<=c. Equality forces h=c and the sum of the first
two intersections to equal Y. This proves both inclusions over every field.

For a simple label r=(i,i+1), write alpha=e_(i,i+1), beta=e_(i+1,i)
and let U_other span the other positive pairs. If N=xv with v(x)=1,
then D_r(N) is an involution and

    D_r(N) H = (K^R tensor U_other)
               direct sum (ker N tensor alpha)
               direct sum (im N tensor beta).                       (2)

Here r permutes the other positive pairs. Consequently each factor has
phi=1, phi is subadditive, and phi(T)=rank(E)*inv(st)=2*2=4.
This proves the inherited lower bound; either displayed family attains it.
If a four-factor product equals T, every written prefix has crossing rank
equal to its length by subadditivity applied to prefix and suffix. Removing
the rightmost factor is therefore a tight peel phi(MG)=phi(M)-1.
With X=H, Y=GH and Z=M^(-1)H, the involution G gives
phi(MG)=d(Y,Z), so (1) applies at each peel.

For completeness, if M fixes S tensor U pointwise and preserves A tensor U,
then S tensor U+ is in X intersect Z, whereas X+Z has no spectator
component at any negative address. Equation (2) and (1) force im N subset A
and N|_S=0. Both conditions matter. The full formal factor consequently
fixes S and preserves A, not merely its represented image. Induction through
all tight peels eliminates every spectator (the inherited PR4765 lemma).
We can now restrict to the two-dimensional plane A, where E=I_2.

## First peel and the mixed-endpoint equality table

For a permutation w, the beta_r coordinate of w^(-1)U+ is nonzero
exactly when w(i)>w(i+1), that is, r is a right descent of w.
At st=2314 the only right descent is t. For r=s or u, X+T^(-1)H
contains no beta_r component, contradicting the nonzero image in (2).
Thus the rightmost factor is D_t(P) for some rank-one plane projector P.
Put L=im P, Q=I_2-P and M=im Q=ker P. The remaining endpoint is

    F=T D_t(P)=[s]P+[st]Q.                                          (3)

It acts by s on L and st on M. Since both permutations simply permute
ordered-pair basis labels, their inverse images of U+ give the following
literal coordinate subspaces for Z=F^(-1)H:

| next label r | scalar alpha_r component of X intersect Z | scalar beta_r component of X+Z |
|---|---|---|
| s | M | L |
| t | L | M |
| u | A | 0 |

For example, s reverses the pair (1,2) but st does not; st reverses
(2,3) but s does not; neither reverses (3,4). These tests use w acting
on the pair, consistently with Z=w^(-1)H. There are no cancellations
between these independent address basis vectors or between L and M.

For the next factor D_r(N), (1)--(2) force the table's middle column
inside ker N and im N inside its last column. At r=s this forces
ker N=M and im N=L, hence N=P. At r=t it forces N=Q.
At r=u it would force im N=0, impossible. These conclusions use both
the image and kernel constraints; just a dimension count is insufficient.

## Finish the two cases

If the second peel is D_t(Q), (3) becomes [s]I_2. Its two remaining
factors are tight. The only right descent is s, so the next peel is
D_s(V) for an arbitrary rank-one plane projector V. The remainder is
I on im V and s on ker V. The final factor is D_s(I_2-V), either by
formal coefficients directly or by the inherited rank-one rigidity theorem.
Restoring written order gives

    D_s(I_2-V) D_s(V) D_t(Q) D_t(P),

which is exactly family A after renaming its freely chosen projectors.

If the second peel is D_s(P), (3) becomes [e]P+[st]Q. This is a
rank-one st endpoint on Q with two factors remaining. The all-field
rank-one rigidity of PR6449 forces both remaining couplings to be Q and
their labels to form a reduced expression for st. That expression is
uniquely st in the adjacent S4 alphabet: a reduced two-letter product
equal to the 3-cycle st cannot involve u or repeat a generator.
The complete written word is

    D_s(Q) D_t(Q) D_s(P) D_t(P),

which is family B after renaming Q as its parameter. These exhaust all
tight peel possibilities, proving necessity.

Conversely, D_r(P)D_r(I_2-P)=[r]I_2, so family A has endpoint [st]I_2
even when P and Q fail to commute. In B, factors supported on complementary
projectors multiply independently; each active line receives st. Restoring
the spectator identity gives T in both cases. No division by two, field
ordering, finite cardinality or characteristic restriction was used.

## Consequences, evidence and limits

Over F_q, there are m=q(q+1) rank-one projectors on a fixed plane:
q+1 image lines and q distinct complementary kernel lines for each image.
Each projector is determined by its ordered image/kernel pair. Family A has
m^2 distinct factor lists and B has m; therefore the exact total is m^2+m.
This count is a consequence of the written classification, not its finite
verification premise. Arbitrary restored spectator dimension adds no shortest
normalized words. The count is in fixed coordinates, without quotienting by
scalar conjugation, commuting adjacent calls or any word equivalence.

The finite engines use full formal coefficients or an equivalent faithful
regular-action representation. The ordered-pair representation above is only
a necessary rank/equality argument; it is not substituted for formal endpoint
equality in the word census. Finite checks cover only the named prime fields
and fixtures in VALIDATION.md. The all-field quantifier rests on this proof.

No conclusion is asserted for nonidempotent couplings, a different paid
alphabet, arbitrary separate prices, nonminimum words, rank greater than two,
other target permutations or mixed endpoints. Free scalar GL normalization
does not price physical basis changes. Native hosting, actual caller access,
dirty restoration outside this exact formal ABI, precision, stock, tapes,
compiler, full signed recursive/outer invoices and supplier admission remain
unproved. All five selected framework assumptions remain. No new kappa,
selected-frontier update, independent human review or kernel acceptance is
claimed. Open next questions are in README.md and TASK.json.
