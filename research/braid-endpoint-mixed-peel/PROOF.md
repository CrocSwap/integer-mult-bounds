# Tight mixed peels for the braid endpoint 3214

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
This is a written argument together with an exact rank certificate re-executed
by [verify.py](verify.py). It is not a proof-kernel certificate, a shortest-word
census, or a physical caller invoice.

## Statement

Let K be any field and let A be a 2-dimensional vector space over K. Write
s=(1 2), t=(2 3) and u=(3 4), with permutation composition (ab)(i)=a(b(i)).
Matrix products act on columns, rightmost first. Both reduced words sts and tst
equal the permutation w with one-line notation 3214. Let T be the pure plane
operator [w], acting as the identity on A and by w on ordered pairs. For a
rank-one idempotent N on A and an adjacent label r, the paid factor is

    D_r(N) = I + ([r] - I) N.

It applies [r] on im N and the identity on ker N. Let U be the 12-dimensional
space of formal ordered pairs e_(i,j), i≠j, with g·e_(i,j)=e_(g(i),g(j)). Let
U+ be the span of the pairs i<j and let H = A ⊗ U+. For an invertible operator
M on A ⊗ U define

    phi(M) = dim H - dim(H ∩ M^{-1} H).

**Theorem.** phi(T)=6, and phi(D_r(N))=1 for every adjacent label and every
rank-one projector N. Every word in these factors that equals T therefore has
at least six factors. For every rank-one projector P the doubled words

    D_s(P) D_s(I-P) D_t(P) D_t(I-P) D_s(P) D_s(I-P),
    D_t(P) D_t(I-P) D_s(P) D_s(I-P) D_t(P) D_t(I-P)

equal [w]. In particular both right descents occur in a minimum word.

The rightmost factor of any minimum word is a tight peel, and so is the factor
immediately to its left. Those peels are completely described as follows.

1. The rightmost factor is D_s(P) or D_t(P) for an arbitrary rank-one
   projector P. For every rank-one N, phi(T D_u(N))=7.
2. After a rightmost D_s(P), write L=im P and M=ker P.
   - D_s(N) is tight if and only if N=I-P. The remainder is the pure
     permutation [st], whose one-line notation is 2314 and whose phi is 4.
   - D_t(N) is tight for every rank-one projector N, and the remainder has
     phi 4.
   - D_u(N) has phi 6 for every rank-one projector N.
3. After a rightmost D_t(P) the same statement holds with s and t exchanged.
   The forced repeated label is D_t(I-P), the remainder is [w∘t] with one-line
   notation 3124, and the free label is s.

Tight means that phi drops by exactly 1. The table constrains the last two
factors of every minimum word. It does not assert that every tight choice of
the free label extends to a six-factor word. That extension is the open census
named in the README.

The passage from a full formal rank-two endpoint, with spectators fixed, to
this plane operator is the tight spectator elimination of Brian/JoyboyBrian
PR4765. That lemma is used as a hypothesis and is not replayed. Ross Richardson
PR1989 and Adam Gall's cut lineage supply the binary inversion tariff. Nick
Petalas PR6449 supplies the ordered-pair defect and the rank-one rigidity used
by ToikY's PR6550 classification of the different endpoint st. The minimum
length and the spectator lemma are inherited. The addition is the mixed peel
table for this one braid endpoint, the question released by PR6550.

## The defect

For subspaces of equal finite dimension, write d(X,Y)=dim X - dim(X∩Y). If
a=dim(X∩Y), b=dim(Y∩Z), c=dim(X∩Z) and h=dim(X∩Y∩Z), then

    a + b = dim((X∩Y)+(Y∩Z)) + h ≤ dim Y + h ≤ dim Y + c.

Hence d(X,Z) ≤ d(X,Y)+d(Y,Z). Equality holds if and only if h=c and
(X∩Y)+(Y∩Z)=Y, which is exactly

    X ∩ Z ⊂ Y ⊂ X + Z.                                         (1)

Both inclusions are valid over every field. For invertible A and B,

    phi(AB) = d(H, B^{-1} A^{-1} H)
            ≤ d(H, B^{-1} H) + d(B^{-1} H, B^{-1} A^{-1} H)
            = phi(B) + phi(A),

since left multiplication by B^{-1} preserves d. Also, for every invertible M,

    dim(H ∩ M H) = dim(M^{-1} H ∩ H),

so phi(M) may be computed from either M or M^{-1}. Applying an involution G
to both arguments gives phi(FG)=d(GH, F^{-1} H).

For a pure permutation, the pair conditions on the two scalar lines separate,
and dim(U+ ∩ σ^{-1} U+) = 6 - inv(σ). Thus on this plane

    phi([σ]) = 2 inv(σ).

The one-line notations and inversion counts are w=3214 with inv 3, st=2314
with inv 2, w∘t=3124 with inv 2, w∘u=3241 with inv 4, and each adjacent
transposition has inv 1. Therefore phi(T)=6 and phi([s])=2.

## Shape of one paid factor

Let r be an adjacent transposition, with positive pair α=e_(i,i+1) and
negative pair β=e_(i+1,i). The only inversion of r is α, so r permutes the
other five positive pairs among themselves and sends α to β. Let Q=I-N. Then

    D_r(N)(v ⊗ u) = Qv ⊗ u + Nv ⊗ (r·u).

The image of H is contained in

    (A ⊗ U_other) ⊕ (ker N ⊗ α) ⊕ (im N ⊗ β),                 (2)

where U_other is the span of the positive pairs other than α: the U_other
terms stay in A⊗U_other, and the α term contributes Qv ∈ ker N on α and
Nv ∈ im N on β. The displayed space has dimension 6 dim A = dim H. The same
calculation gives D_r(N)^2=I over every characteristic. Indeed [r] commutes
with N, and with R=[r]-I one has R^2=-2R, so the cross terms in
(I+RN)^2 cancel, including in characteristic 2 where both are zero. An
involution is bijective, so the image equals (2).

Intersecting (2) with H kills the β summand and cuts the α summand down to
ker N. Hence

    dim(H ∩ D_r(N) H) = 5 dim A + dim ker N = 11

when dim A=2 and N has rank one, and phi(D_r(N))=1. Subadditivity then says
that a word equal to T has at least six factors.

For complementary projectors the lines are invariant, [r] does not move
scalars, and each line receives [r] from exactly one of D_r(P) and D_r(I-P).
Thus D_r(P)D_r(I-P)=[r]=D_r(I-P)D_r(P) for every rank-one P. The two doubled
words are therefore [s][t][s] and [t][s][t], both equal to [w].

## First peel

Let P be any rank-one projector, L=im P and M=ker P. The remainder
F=T D_r(P) acts by w∘r on L and by w on M. A vector ℓ⊗u_L + m⊗u_M lies in H
when both pair vectors lie in U+, and its image under F lies in H when
(w∘r)·u_L and w·u_M lie in U+. The two lines contribute independently, so

    phi(F) = inv(w∘r) + inv(w).

The three right multiplications give phi 5, 5 and 7 respectively. Since each
factor has phi 1, the triangle inequality says phi(T D_r(P)) ≥ phi(T)-1 = 5.
Equality holds for every projector when r is s or t, and fails for every
projector when r is u.

Let W_k be the product of the rightmost k factors of a six-factor word equal
to T. Then phi(W_k) ≤ k. The remaining 6-k factors contribute at most 6-k, so
6 = phi(T) ≤ phi(W_k) + (6-k), hence phi(W_k)=k. Every right-hand prefix is
therefore a tight peel of the operator to its left. The rightmost factor of a
minimum word is one of the tight first peels above, and the next factor is a
tight peel of the remainder.

## Second-peel table

Keep F=T D_s(P), so rho_L=w∘s=st=2314 and rho_M=w=3214. Let S_L be the set of
ordered pairs whose image under rho_L is increasing, and define S_M likewise.
These are the supports of F^{-1}H:

    S_L = {(1,2),(1,4),(2,4),(3,1),(3,2),(3,4)},
    S_M = {(1,4),(2,1),(2,4),(3,1),(3,2),(3,4)}.

The same listing after a first factor D_t(P), where rho_L=w∘t=3124, is

    S_L = {(1,4),(2,1),(2,3),(2,4),(3,1),(3,4)},
    S_M = {(1,4),(2,1),(2,4),(3,1),(3,2),(3,4)}.

There is no cancellation between L and M or between distinct pair addresses.
The α-component of H ∩ F^{-1}H, and the β-component of H + F^{-1}H, are
therefore the lines whose support contains that address. For the next label
this gives the following pairs (α component, β component).

| first peel | next label | α of H∩F^{-1}H | β of H+F^{-1}H | tight projectors |
|---|---|---|---|---|
| s | s | L | M | only I-P |
| s | t | 0 | A | every rank-one N |
| s | u | A | 0 | none |
| t | t | L | M | only I-P |
| t | s | 0 | A | every rank-one N |
| t | u | A | 0 | none |

The st endpoint, whose first peel is t and whose lines carry s and st, has
rows (M,L), (L,M) and (A,0). Its s-row is the reverse of the s-row above, so
that table does not transfer to w.

A tight second peel is equality in the triangle, hence (1) applies with
Y=D_r(N)H. Combined with (2), the α-component of the intersection must lie in
ker N and im N must lie in the β-component. The rows with β=0 are impossible.
The row (L,M) forces ker N=L and im N=M, hence N=I-P. The row (0,A) holds for
every rank-one N and does not select one.

## The forced continuation

D_s(P)D_s(I-P)=[s], so

    T D_s(P) D_s(I-P) = [w][s] = [st].

The remainder is the pure permutation of inversion count 2, and phi([st])=4.
The same identity with t gives the remainder [w∘t] of phi 4. Both identities
hold for every rank-one P and every field. Together with the table, the
repeated label is tight exactly for the complementary projector.

## The free continuation

The inclusion test allows every rank-one t-factor after D_s(P). Sufficiency
is a rank calculation after a basis reduction.

Choose a basis with e1 in L and e2 in M. Conjugation by that basis change
preserves phi and carries F to the operator which applies st on the first
coordinate line and w on the second. It is therefore enough to take P as the
coordinate projector onto span e1 along span e2, and to let N be an arbitrary
rank-one projector in that basis.

A further diagonal matrix g=diag(λ,ν) preserves each coordinate line. On each
line F acts by a permutation of pairs and by a scalar on A, so g commutes
with F. Conjugation by g preserves phi and multiplies slopes by ν/λ. Here the
slope of a line span(x,y) is y/x when x≠0, and infinity when the line is
span e2.

Every rank-one projector is one of the following, and the diagonal action
reduces each family to one matrix.

- im=span e1 and ker=span e2, the coordinate projector P.
- im=span e2 and ker=span e1, the complement I-P.
- im=span e1 and ker=span(1,b) for b≠0. Scaling b to 1 gives
  [[1,-1],[0,0]].
- im=span e2 and ker=span(1,b) for b≠0. Scaling gives [[0,0],[-1,1]].
- im=span(1,a) for a≠0 and ker=span e1. Scaling gives [[0,1],[0,1]].
- im=span(1,a) for a≠0 and ker=span e2. Scaling gives [[1,0],[1,0]].
- both lines tilted: im=span(1,a) and ker=span(1,b) with a,b≠0 and a≠b.
  Scaling the image slope to 1 carries this to

      N_μ = 1/(μ-1) [[μ,-1],[μ,-1]],    μ=b/a ∉ {0,1}.

  The value μ=0 reproduces [[0,1],[0,1]], already listed. Over F2 there is no
  such μ, and the six projectors are exactly the two monomial matrices and
  the four line-preserving matrices.

For the coordinate projectors the remainder is monomial. Direct inversion
counts give phi=1+3=4 for the second factor P and phi=2+2=4 for I-P. The
other four matrices, and N_μ, are handled by the negative-pair equations on
Z=F^{-1}H. That space has the 12 coordinates consisting of the L-component
on S_L and the M-component on S_M. For z in Z, D_t(N)z lies in H exactly when
its six negative pair addresses vanish, twelve scalar equations in all.
Because D_t(N) is an involution,

    phi(F D_t(N)) = 12 - dim{z in Z : D_t(N) z ∈ H}.

The same count with the label s gives the free branch after a first peel by t.

Row reduction uses the first nonzero entry of each column, without rescaling
the pivot row. On each of the six listed matrices, for both free branches,
the four pivots lie in {±1}. The rank is therefore 4 over every field, and
phi=4. For N_μ the same elimination on the s-first, t-labelled branch has
pivots

    1/(μ-1),  -μ,  1/μ,  -1/(μ-1).

On the t-first, s-labelled branch the pivots are

    -1/(μ-1),  -1/(μ-1),  1,  1.

Each numerator and denominator is ±μ^a(μ-1)^b. No pivot is an integer other
than ±1, so none vanishes because of the characteristic. For μ∉{0,1} every
pivot is nonzero in every characteristic, the rank is 4, and phi=4. The same
reduction over F_p(μ) for p=2,3,5,7 reproduces these pivots modulo p.

Thus every rank-one projector on the free label is a tight second peel.

## The forbidden label

The table already excludes u. The same twelve equations give a sharper value.
On each of the six matrices the u-labelled elimination has six pivots in {±1},
on both sides of the first peel. For N_μ, after the s-peel, the six pivots are

    1,  -1/(μ-1),  1,  -1/(μ-1),  1,  μ/(μ-1),

and after the t-peel they are

    1,  1,  -1/(μ-1),  1,  1/(μ-1),  μ/(μ-1).

Again the only zeros and poles are μ=0 and μ=1. The rank is 6 for every
allowed μ and on every normal form, over every field. Hence phi=6 for every
rank-one u-factor.

## What the finite census checks

The census is corroboration of the two engines, not the source of the
all-field quantifier. Over F2, F3 and F5 there are q(q+1) rank-one projectors.
For the axis splitting, both engines give the same phi, the first-peel values
are 5, 5 and 7, exactly one repeated-label projector is tight and it equals
I-P, every free-label projector is tight, and every u-factor has phi 6. The
same count holds after the t-peel with the labels exchanged. Every projector
matches the diagonal transport of the normal form with its slope pair. The
complement identity D_r(P)D_r(I-P)=[r], the doubled words, and D_r(N)^2=I are
checked as matrices on these fields. A separate dense calculation over Q
accepts N_2, N_3 and the projector [[0,0],[-1,1]] onto span e2 along
span(1,1), and it rejects the non-idempotent matrix [[0,0],[1,-1]], whose
t-continuation has phi 5.

## Limits

The result is the plane peel table and the length count that follows from it.
Spectator elimination is assumed from PR4765 and is not replayed. The ordered
defect and the st classification are predecessor theorems. No shortest-word
list is claimed, and the count m^2+m from the st endpoint is not used. A tight
free second peel may still fail to extend to six factors. Nonidempotent
couplings, other alphabets, other ranks, weighted prices and slack words are
outside the statement. Scalar conjugation is algebraic and is not a physical
basis change. Caller access, restoration outside this formal operator, tapes,
precision, stock, compiler cost and supplier admission remain open. All five
selected framework assumptions remain. The selected conditional value stays
781451/250000000. There is no new κ.
