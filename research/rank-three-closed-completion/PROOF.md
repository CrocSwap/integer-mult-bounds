# Exact rank-three alternating completion criterion

This proof and its finite corroboration were produced by Nick Petalas.
Apache-2.0.

## Statement and credited inputs

Let V be a finite nondegenerate symplectic vector space over F2 with pairing
w. Let h:U -> V be an injective linear isometry. Write d=h+I,
K=ker d, D=d(U), and

    b(d(u),d(v)) = w(u,d(v)).

Assume dim D=3 and b is alternating of rank two. Its radical R has
dimension one. Set U_R=d^-1(R), a subspace of U. All sums and inverse
images refer to the given V. Spectators required to remain fixed belong
to U with h(v)=v. Let L(h) be the minimum number of nonzero-axis
transvections in a symplectic extension of h in V.

**Theorem.** If U_R is contained in K+D, then L(h)=5. Otherwise L(h)=4.
Moreover, every four-turn extension in this setting has four linearly
independent, pairwise orthogonal axes.

The new result is the closed-case lower bound and the necessary commuting
structure. Ali Romman's [#6525](https://github.com/CrocSwap/integer-mult-bounds/pull/6525)
already proves 4<=L(h)<=5 and constructs four turns when U_R is not
contained in K+D. Those constructive upper bounds are used as premises;
they are not reconstructed or audited here. Its r=3 five-turn fixture
was already known. The new theorem treats every such contract in every
ambient dimension, rather than just that fixture. Its r>=4 closed case
remains open and can attain the lower endpoint.

Krzysztof Wojt's #5097 supplies the general displacement-plus-nullity
bound. Nick Petalas's #5085/#6494, Brian / JoyboyBrian's #5051 and the
native/compiler lineage retained in #6525 supply the earlier problem
and constructions. The following lower-bound argument is self-contained.
Wall forms and binary quadratic forms are classical mathematics; no
literature-priority claim is made.

## 1. Full displacement and its form

For any symplectic extension S of h, put W=im(S+I). Symplecticity gives

    ker(S+I) = W-perp.

For example, w(v,(S+I)x)=w((S^-1+I)v,x), so orthogonality to W is
equivalent to S(v)=v. Thus the form

    B((S+I)v,z) = w(v,z),     z in W,

is well-defined and nonsingular. If its left radical contained (S+I)v,
then v would be in W-perp and its displacement would vanish. Also

    B(x,y)+B(y,x)=w(x,y),     B restricted to D equals b.       (1)

The first identity follows by expanding w(Sv,Su)=w(v,u); the second
follows from S|U=h. Since b is singular and D has dimension three,
W cannot equal D. Hence dim W>=4.

A product of t transvections has displacement image contained in the
span of its t axes. Therefore L(h)>=4. If four turns extend h, their
axes a1,...,a4 are independent and W is exactly their span.

In execution order, write the intermediate update at turn i as c_i a_i.
For input v the coefficients obey

    c_i = w(v,a_i) + sum_(j<i) c_j w(a_j,a_i).

The coefficient transformation is triangular with diagonal one. Since
the axes are independent and V is nondegenerate, the four functionals
w(-,a_i) are independent, so these coefficients range over F2^4.
Consequently the matrix of B in the axis basis is upper triangular with
diagonal one. In particular, the quadratic form q(x)=B(x,x) satisfies

    q(a_i)=1 for every i,     q|D=0,     polar(q)=w|W.          (2)

Thus the vectors with q=1 span W.

## 2. A four-dimensional quadratic obstruction

Let q be a quadratic form on a four-dimensional binary space W, vanishing
on a three-dimensional subspace D. Suppose its polar form p is nonzero.
Since D is isotropic of codimension one, p has rank two. Its radical Z
has dimension two and lies in D. In particular q|Z=0.

The form descends to W/Z, a nondegenerate two-dimensional quadratic
space. D/Z is a nonzero singular line, so this is the split plane. In
a suitable basis its form is xy. Over F2 it has exactly one vector
with value one. Therefore {x:q(x)=1} is one coset of Z in W and spans
only a three-dimensional subspace. It cannot span W.

Apply this to (2). The anisotropic vectors do span W, so p=0. By (1),
W is totally isotropic. In particular the four axes commute. This proves
the extra assertion without assuming any special source coordinates.

## 3. Closed radical lifts contradict four turns

Let 0!=z in R. If U_R is contained in K+D, choose a lift u in U with
d(u)=z and write u=k+x with k in K and x in D. The extension fixes k.
Total isotropy gives W contained in W-perp=ker(S+I), and x is in D
contained in W. Hence S fixes x as well. It fixes u, contradicting
(S+I)u=d(u)=z!=0.

No four-turn extension exists in the closed case. Together with the
credited upper bound five this gives L(h)=5. In the escaping case the
credited four-turn construction attains the lower bound from section 1.

## Scope

This is an unsigned binary label-word theorem with fixed prescribed
spectators and no ambient enlargement. It does not price Gaussian rank,
sign or absolute-phase corrections, physical routing, owner cleanup,
precision, stock, tape, compiler closure or outer recursion. The five
selected assumptions remain. It supplies no multiplier or new kappa.
Independent human and formal proof-kernel acceptance are unclaimed.

The verifier checks the new quadratic obstruction and all independent
four-turn Gram topologies by exact finite arithmetic. It does not certify
the written arbitrary-dimension proof or replay the credited upper bounds.
