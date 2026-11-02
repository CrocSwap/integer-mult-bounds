# Alternating four-call lattice descent

This contribution was produced by Nick Petalas. Apache-2.0.

## Model and statement

Let K be any field of characteristic two, let n be a positive integer,
and let P,Q in M_n(K) be rank-one idempotents. Work over the Laurent
polynomial ring K[z,z^-1], with z an indeterminate. Put

    E_z(P) = I + (z-1)P,
    W(P,Q) = E_z(P) E_z(Q) E_z(P) E_z(Q),
    tau = tr(PQ).

Products act on columns with the rightmost factor acting first. A matrix
is even if every entry belongs to K[z^2,z^-2]. In address notation z=[s],
this is descent from Zs to its subgroup 2Zs. There are no intervening
address-dependent operations in the alternating word studied here.

**Theorem.** W(P,Q) is even if and only if

    P=Q or tau=0.

Every even W(P,Q) is a product of exactly two rank-one calls labelled z^2:

1. If P=Q, then W(P,P) = E_(z^2)(P) E_(z^2)(P).
2. If P!=Q and tau=0, put

       P' = P+PQ,       Q' = Q+QP.

   These are rank-one idempotents with P'Q'=Q'P'=0, and

       W(P,Q) = E_(z^2)(P') E_(z^2)(Q')
              = I+(z^2-1)(P'+Q').

The sum P'+Q' is a rank-two projector. The two-call count is minimal
among words of rank-one z^2 calls and arbitrary constant invertible maps.
This is an algebraic call count. It makes no assertion that a coarse
label has the same native price as a fine label.

## The odd coefficient determines descent

Write P=u v and Q=x y, where u,x are nonzero columns, v,y are rows,
and vu=yx=1. These factorizations exist for rank-one idempotents.
With alpha=vx and beta=yu, elementary multiplication gives

    tau=alpha beta,
    PQP=tau P,       QPQ=tau Q,       (PQ)^2=tau PQ.

Set a=z+1, N=P+Q and B=PQ. Then

    E_z(P) E_z(Q) = I+aN+a^2 B,
    N^2 = N+PQ+QP,
    NB+BN = tau N.

Squaring the first identity, keeping the matrix order, yields

    W(P,Q) = I + a^2(N+PQ+QP) + a^3 tau N + a^4 tau PQ.

In characteristic two a^2=1+z^2, a^4=1+z^4 and
a^3=1+z+z^2+z^3. Hence the coefficients of both z and z^3 in W
are exactly tau(P+Q). There are no other odd degrees. Since K is a
field, that coefficient vanishes precisely when tau=0 or P=Q. This
proves the necessary-and-sufficient criterion, for every finite n.

No reduction of a rational address label modulo the field characteristic
is used. The address exponent and the scalar coefficient field are
different objects.

## Constructive descent

If P=Q, idempotence gives E_z(P)^2=E_(z^2)(P), proving case 1.
Suppose tau=0. The displayed rank-one identities give

    (P+PQ)^2=P+PQ,       (Q+QP)^2=Q+QP,
    (P+PQ)(Q+QP)=0,      (Q+QP)(P+PQ)=0.

The image of P+PQ lies in the one-dimensional image of P. Also
(P+PQ)u=u, because PQP=0. Thus P' has rank one. The same argument
gives rank Q'=1. Orthogonality makes their images disjoint, so P'+Q'
is an idempotent of rank two. In particular tau=0 already implies P!=Q.

The odd-coefficient expansion now reduces to

    W(P,Q)=I+(z^2+1)(P+Q+PQ+QP).

Multiplying the two proposed coarse calls, their cross term vanishes by
P'Q'=0. Their product is this same matrix. This proves case 2 and its
complete action on arbitrary input columns, including all spectators.

For minimality, a rank-one idempotent is similar over K to
diag(1,0,...,0). Consequently det E_z(P)=z and det W=z^4.
A word with L rank-one z^2 calls and constant invertible maps has
determinant c z^(2L), for a nonzero constant c. Equality with W forces
L=2 and c=1. The argument allows free constant maps anywhere in the word.

## A smallest failure of adjacent-pair descent

Over F2 take

    P = [[1,0],       Q = [[0,1],
         [0,0]],          [0,1]].

Here QP=0 and PQ=[[0,1],[0,0]] is nonzero. In particular P and Q do
not commute. The theorem supplies

    P'=[[1,1],[0,0]],     Q'=Q,     P'+Q'=I,
    W(P,Q)=z^2 I_2.

No proper nonempty consecutive block of this four-call word is even.
Blocks of length one or three have determinant z or z^3, whereas the
determinant of an even matrix is even. Every length-two block is an
alternating pair of distinct projectors. Its coefficient of z is P+Q,
which is nonzero. These are all nine proper consecutive blocks.

This is the smallest example relevant to iterating a two-use reduction.
An odd number of positive rank-one z calls cannot have an even endpoint
by determinant parity. A two-call word is even exactly when its two
projectors agree, by the same coefficient calculation, and then the
two-use contraction already applies. Four calls therefore give the first
even endpoint with no even adjacent pair.

Embedding P,Q as zero on any additional coordinates gives this example at
every n>=2. W is diag(z^2,z^2,1,...,1), so the additional coordinates
are restored for arbitrary initial data. No zero-initialized scratch is
assumed.

The example does not contradict the two-use theorem of CubeJerry's
[PR6148](https://github.com/CrocSwap/integer-mult-bounds/pull/6148).
That theorem assumes exactly two odd calls in the block being contracted.
The example has four. It rules out a proposed shortcut that would require
every even four-call endpoint to expose an even adjacent pair. The new
coarse projectors show how this particular alternating class descends
despite the absence of such a pair.

## Scope and remaining obligations

The universal statement is this written proof. The verifier independently
multiplies full polynomial matrices and applies the literal factors to
basis columns over finite fields. Those checks corroborate the proof in
their stated finite domains. They are not its all-width justification.

The result assumes an infinite-order address generator, one repeated fine
label, constant rank-one projectors, characteristic two, and the alternating
four-factor order. Four unrelated projectors, arbitrary intervening even
operations, finite-order address collisions, and other characteristics are
outside its classification. It does not establish a universal four-use
descent rule or classify the surviving eight-call profiles of PR6111.

No complete supplier bill, native conversion for 2s, restored physical
caller, target inventory, stock, compiler, precision/tape implementation,
new kappa or complete multiplication theorem is supplied. The current
selected record and its five framework assumptions are unchanged.
Independent human and formal proof-kernel review are unclaimed.
