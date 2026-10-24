# Inversion-weighted spectator reduction

This contribution is produced by Nick Petalas. Apache-2.0.

This is a scoped algebraic proof. Its finite controls are corroboration,
not a proof of the universal quantifiers or a complete multiplication theorem.

## Statement

Let F be any field, n>=2, and R=A direct-sum S a finite-dimensional scalar
role space, with dim A=w. Work in M_R(F[S_n]). For a nonidentity permutation g
and scalar column u and row v with vu=1, define

    G_g(u,v) = I + ([g]-[e])uv.

The inverse is G_(g^-1)(u,v). Consider a nonempty normalized written word

    T = G_(g_1)(u_1,v_1) ... G_(g_m)(u_m,v_m) = Q_A direct-sum I_S.

The endpoint equality is coefficientwise in the full group algebra. It
includes arbitrary dirty inputs, every off-diagonal coefficient, and complete
spectator restoration. No restriction to diagonal active endpoints is made.
Put d_i=inv(g_i)>0 and d_*=min_i d_i. Let permutations act on ordered distinct
pairs, let H be the increasing-pair subspace tensored with R, and K the
decreasing-pair subspace. For the represented endpoint set

    L = rank(projection_K T restricted_to H).

**Theorem.** A single spectator-only scalar basis change, fixing the original
active coordinates, puts every original paid factor on at most

    w + floor((sum_i d_i - L)/d_*)

total roles. Restricting those same factors preserves their labels, order,
rank-one idempotents and full formal endpoint. The retained extra roles remain
arbitrary dirty inputs and are restored. In particular sum_i d_i>=L.

When all labels have inversion count d, the bound is
w+m-ceil(L/d). At d=1 this recovers Brian/JoyboyBrian's #4783 simple-label
bound. The new statement admits non-simple and non-involutive labels, varying
inversion counts, arbitrary symmetric groups, and every scalar field.

The empty word needs no dirty roles and is treated separately. Identity
labels can be deleted before defining d_*. This theorem does not price a label
as inv(g) physical calls; d_i is a geometric quantity used to bound workspace.

## The crossing decomposition

Write U_+ for the span of increasing pairs and U_- for decreasing pairs.
For any permutation h let C be the coordinate intersection U_+ intersect hU_+,
let X be the coordinate complement of C in U_+, and Y the negative coordinate
part of hU_+. Thus

    U_+ = C direct-sum X,    hU_+ = C direct-sum Y,
    dim X = dim Y = inv(h) = d.

This holds because the ordered-pair action is a permutation action. An inversion
is precisely an increasing pair sent to a decreasing one. No involution
assumption is used. Since R=ker(v) direct-sum span(u), the represented gate is
identity on ker(v) and h on span(u). Consequently

    G_h H = (R tensor C) direct-sum (ker(v) tensor X)
            direct-sum (span(u) tensor Y).                  (1)

In particular d(H,G_h H)=d, where d(B,C)=dim B-dim(B intersect C) is the
Grassmann distance for subspaces of the same dimension. Also

    H intersect G_h H = ker(ell),

where ell:H -> F^d applies v to each X-coordinate. Its quotient in G_h H
has dimension d. Formula (1) is the new replacement for the predecessor's
one-crossing decomposition.

## The local charge

Suppose the current residual P has full formal form P_A0 direct-sum I_S0.
Define phi(P)=rank(projection_K P restricted_to H). Equivalently
phi(P)=d(H,P^-1 H). Put Z=P^-1 H and D=H intersect Z.

Peel a rightmost factor G_g by multiplying P on the right by its inverse.
Set h=g^-1 and Y0=G_(g^-1) H. Invariance of Grassmann distance gives

    phi(P G_g^-1) - phi(P)
      = dim D - dim(Y0 intersect Z).                       (2)

Indeed phi(PG_g^-1)=d(H,G_g P^-1 H)=d(G_g^-1 H,P^-1 H).
In (1) use h=g^-1 throughout this local step. Both h and g have
inversion count d.

Write a for the S0 component of u, b for the restriction of v to S0, and
eta=1[a!=0]+1[b!=0]. Then

    d eta <= d + phi(P G_g^-1) - phi(P).                    (3)

To prove this, note that Z contains S0 tensor U_+ and has no negative
spectator component. If b!=0, ell restricted to D has rank exactly d,
because D contains S0 tensor X and b is a nonzero functional there.
Thus dim(D intersect ker ell)=dim D-d.

If a!=0, any nonzero Y-coordinate in (1) has a nonzero negative spectator
component, so cannot lie in Z. Therefore
Y0 intersect Z=D intersect ker ell. If both a,b are nonzero, (2) is exactly
d, proving (3) with eta=2. If a!=0 and b=0, (2) is nonnegative, proving
(3) with eta=1.

If a=0 and b!=0, the quotient of Y0 intersect Z by D intersect ker ell
injects into Y0/(Y0 intersect H), a space of dimension d. Hence its dimension
is at most dim D, so (2) is nonnegative and again eta=1 is charged.
If a=b=0, the distance triangle gives (2)>=-d, completing the four cases.

The nonnegative local slack s=d+phi(PG_g^-1)-phi(P) therefore pays
eta<=s/d<=s/d_* dirty directions. This step is valid for arbitrary invertible
active represented maps. It does not use faithfulness to admit an endpoint.

## Nested splits and the global word

For a vector a in S0 and functional b on S0, choose S0=V direct-sum S1,
with a in V and b annihilating S1. Such a V has dimension at most eta.
If a=b=0 take V=0. If just one is nonzero, retain its vector or a vector
t with b(t)=1, respectively. If both are nonzero and b(a)!=0, take V=span(a)
and S1=ker b. If both are nonzero and b(a)=0, choose b(t)=1 and take
V=span(a,t), with S1 a complement to span(a) in ker b. These constructions
work over every field.

Enlarge A0 to A1=A0 direct-sum V. The peeled factor has u in A1 and v
annihilates S1. Both the old residual and its peeled successor preserve A1
and are identity on S1 in the full formal algebra. Repeat, starting at T
and peeling factors from right to left. The final residual is identity.
All retained V spaces lie inside the original spectator space. Telescoping
the local nonnegative slacks gives

    retained_dirty <= sum_i s_i/d_*
                   = (sum_i d_i + phi(I) - phi(T))/d_*
                   = (sum_i d_i - L)/d_*.

The retained dimension is an integer, giving the floor in the theorem.
The distance triangle also directly gives sum_i d_i>=L.

Take a basis of the retained V spaces in peeling order, followed by a basis
of the final discarded spectator space. This is one scalar basis of S, with
the original active basis fixed. Let J include the retained role space and
E project onto it along the discarded space. Every original factor satisfies
u_i=J u_i' and v_i=v_i' E, with EJ=I. Thus

    v_i' u_i'=1,    G_i J=J G_i',    E G_i=G_i' E,
    G_i = G_i' direct-sum I_discarded.

These identities hold coefficientwise in F[S_n], not just in the ordered-pair
representation. Multiplication gives the original complete endpoint on the
retained roles. Labels, order and every label-dependent tariff are preserved.

## Sharpness and scope

For any nonidentity g with d inversions, take one active axis e0 and two dirty
axes e1,e2. Let u=e0+e1 and v=e0*+e2*, so vu=1. The written word

    G_g(e0,e0*) G_g(u,v) G_(g^-1)(u,v)

has endpoint diag([g],1,1), total inversion mass 3d, L=d and d_*=d.
The theorem retains at most two dirty roles. Both are necessary if the actual
factors must survive one spectator-only basis change: their nonzero dirty
image and dirty functional have zero pairing. On a one-dimensional space,
a nonzero vector and functional have nonzero pairing. This proves sharpness
of the coefficient for this reduction, over every field, including a genuinely
non-involutive 3-cycle. The canceling pair makes no endpoint-optimal-workspace
or shortest-word claim.

The result answers #4783's non-simple-label charge question. Brian's nested
splits, positive-slack framework and preserved-factor sharpness mechanism
remain predecessor credit. Ross Richardson #1989 supplies the ordered-pair
inversion cut, following Adam Gall #1941 and Ross Richardson #1966. Credit
Sagar Thakrar #3888, Arham Tahir #2998 and Nick Petalas #2583/#3408 for the
retained weighted-register context. The proof is self-contained and imports
no pending executable or finite-exclusion receipt.

This is a fixed-word algebraic workspace reduction. It gives no physical
basis-conversion algorithm or native tariff, and permits neither nilpotent
couplings, unreturned spectators nor free address operations. Scalar mixing
is normalized into the given rank-one idempotents; augmentation forces any
remaining free scalar endpoint to be identity. Precision, tape, ownership,
hosting, complete supplier admission and all-size multiplication transfer
remain separate obligations. No new kappa is claimed.
