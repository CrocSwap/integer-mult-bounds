# Saturated cubic shared-block pairs have one normal form

This proof was produced by Nick Petalas. Apache-2.0.

## Statement

Let F be any field of characteristic two, let s be a positive integer, and
let V have dimension 3s. Suppose D is an idempotent of rank 2s and

    A+B=D,                 A^3=B^3=0.                         (1)

There is exactly one simultaneous similarity class of ordered pairs
satisfying (1). In suitable coordinates on F^s + F^s + F^s, it is

         [0 I 0]              [0 I 0]              [I 0 0]
    A0 = [0 0 I],        B0 = [I I I],        E0 = [I 0 0],  (2)
         [0 0 0]              [I 0 I]              [I 0 0]

where E0=I+A0+B0. Each summand has exactly s Jordan blocks, all of size
three. Reordering the coordinate triples gives a direct sum of s identical
three-dimensional ordered pairs.

For a fixed idempotent D over F_q, q a power of two, the number of ordered
pairs in (1) is exactly

    |GL_(2s)(F_q)| = product_(j=0..2s-1) (q^(2s)-q^j).        (3)

Thus dimension six and endpoint rank four give exactly 20,160 ordered
binary pairs for each fixed D. This is a scoped local classification and
counting theorem. No chronological native program or new kappa is claimed.

## Relation to the open equality question

CubeJerry's [PR #6768](https://github.com/CrocSwap/integer-mult-bounds/pull/6768),
at `48233eac64d0645e385407bee33195d78deb2e52`, proves the sharp common-cap
zero-primary spectrum and leaves its equality cases open. Its second next
question suggests corank two and cap three. The maximum and attaining
construction are cited predecessors, not replay targets.

At dimension 3s and endpoint rank 2s the cited cap-three maximum is 6s.
Every maximizer therefore has both matrices globally nilpotent. The cap
then gives (1). The new result classifies every such maximizer, rather
than producing another attaining example. The argument below is
self-contained and needs no predecessor executable or foreign Git object.

## The equality observation map

Set E=I+D and S=im(E). Then E^2=E and dim(S)=s. Consider

    Phi: V -> S^3,       v |-> (Ev,EAv,EA^2v).

Its kernel W is A-invariant: applying A shifts the defining conditions,
and the final condition becomes EA^3v=0. E kills W, so B=I+A+E preserves
W and acts there as I+A. This restriction is invertible, with inverse
I+A+A^2, and its cube is zero because B^3=0. An invertible nilpotent
endomorphism acts only on the zero space. Thus W=0. Equal dimensions now
make Phi an isomorphism.

In these coordinates A becomes A0. Define M=EA|_S and N=EA^2|_S. Since
E^2=E, applying E to v with Phi(v)=(x0,x1,x2) gives the coordinates
(x0,Mx0,Nx0). Therefore E and B have the block forms

        [I 0 0]              [0 I 0]
    E = [M 0 0],        B = [M I I].                         (4)
        [N 0 0]              [N 0 I]

All blocks act on S. No commutativity of M and N is assumed.

## The cubic equation determines the free blocks

Ordered block multiplication gives

    first block row of B^2 = [M, I, I],
    first block row of B^3 = [M+N, M+I, 0].

Thus B^3=0 forces M=N=I. Conversely, these values give B0^3=0 by direct
multiplication. Also A0^3=0, E0^2=E0 and rank(I+E0)=2s. This proves
existence and uniqueness of (2).

The kernels of A0 and B0 have dimension s. For B0, its first equation
sets x1=0 and its second sets x2=x0. Thus the cubic nilpotence and total
dimension 3s force exactly s blocks of size three for each matrix.

The surviving-kernel idea follows #6768's cap proof. The new equality step
turns it into complete coordinates; the first row of the cubic equation
then determines the whole pair.

## Joint centralizer and finite count

Solving XA0=A0X gives the block Toeplitz form

        [P Q R]
    X = [0 P Q].
        [0 0 P]

Such an X commutes with B0 if and only if it commutes with E0. The second
and third block columns of XE0 and E0X force Q=R=0. Conversely every
diag(P,P,P) commutes with both matrices. The joint endomorphism
centralizer is M_s(F) in this embedding. Its invertible part is GL_s(F).

For fixed D, the invertible endpoint centralizer is
GL_(2s)(F) times GL_s(F), acting on im(D) and ker(D). The simultaneous
classification makes it transitive on pairs having this endpoint: any
similarity between two pairs also preserves their sum D. The pair
stabilizer is GL_s(F). Orbit-stabilizer proves (3).

For the literal endpoint D=diag(I_s,I_s,0), change from endpoint
coordinates to (2) by

    (u,v,w) |-> (w,u+w,v+w).

The inverse is (x0,x1,x2) |-> (x1+x0,x2+x0,x0). In endpoint coordinates
the representative is

          [I I 0]               [0 I 0]
    A* =  [I 0 I],        B* =  [I I I].                      (5)
          [I 0 I]               [I 0 I]

The basis change has scalar blocks, so the stabilizer is still
diag(P,P,P). Each endpoint-centralizer element diag(C,R) has a unique
right coset representative diag(H,I_s), H in GL_(2s)(F): multiply it on
the right by diag(R^-1,R^-1,R^-1). Conjugating (5) by these representatives
therefore enumerates every fixed-endpoint pair exactly once. The count
is for ordered pairs and does not quotient by exchanging A and B.

## Credit, classical context and limits

The equality question, sharp capped spectrum, surviving-subspace argument
and odd-core family belong to CubeJerry's #6768. Nick Petalas's earlier
#5928 supplies the unrestricted spectral envelope and corank-one context.
Credit JoyboyBrian's #5507 for the two-owner four-support model, Ali
Romman's #5456 for the early-helper model, and the retained
#5452/#5388/#589/#555 native, owner and compiler lineage.

Ferrero, Puczylowski and Sidki,
[On the Representation of an Idempotent as a Sum of Nilpotent Elements](https://doi.org/10.4153/CMB-1996-022-0),
Canadian Mathematical Bulletin 39 (1996), 178-185, Example 1, already
give a positive-characteristic triangular construction. Proposition 2
excludes a nonzero idempotent with one globally square-zero summand.
Those facts, Jordan theory, observation coordinates and orbit-stabilizer
are classical. The contribution answers the repository's saturated cubic
equality question and counts its fixed-endpoint solutions. No general
literature-priority claim is made; the literature search was bounded.

The universal theorem rests on this written proof. Finite checks
corroborate it and do not constitute formal proof-kernel acceptance.
Other dimensions, higher caps, nonzero-primary parts and other
characteristics are outside the classification. Physical realization,
ownership, dirty restoration, complete paid/target accounting,
precision/tape, compiler closure and supplier admission remain open.
The selected frontier and all five selected assumptions are unchanged.
Independent human and formal proof-kernel review are unclaimed.
