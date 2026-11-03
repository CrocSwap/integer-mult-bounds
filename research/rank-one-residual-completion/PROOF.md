# Rank-one residual forms at every displacement rank

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped algebraic proof. The new cases have displacement rank
at least three. Krzysztof Wojt's [PR5097](https://github.com/CrocSwap/integer-mult-bounds/pull/5097)
provides the lower bound, zero-form construction and rank-two predecessor.
Nick Petalas's PR5085 provides the residual-form and low-length framework.
The present step is the dimension-independent rank-one pivot below.

Let V be a finite-dimensional nondegenerate symplectic space over F2, with
pairing omega. Let h:U -> V be an injective linear map preserving omega on U.
Set d=h+I, D=d(U), r=dim D, and define

    b(d(u), d(v)) = omega(u, d(v)).

This is well defined. If k is fixed by h, preservation of its pairing with
u implies omega(k,d(u))=0. Expanding the isometry identity also gives

    b(x,y) + b(y,x) = omega(x,y), for x,y in D.             (1)

Suppose b has rank exactly one. Then the least length ell(h) of a product
of nonzero-axis symplectic transvections extending h is

    ell(h) = 2r - 1.                                    (2)

Every axis lies in V. No ancillary dimension is adjoined. The extension is
free outside U. Required fixed spectators must therefore be included in U.

## Lower bound, credited predecessor argument

For any full symplectic extension S, put W=im(S+I). Its residual form B,
defined by B((S+I)v,w)=omega(v,w), is nonsingular and restricts to b on D.
Indeed W-perp=ker(S+I); this proves both well-definedness and nonsingularity.
The left radical of b injects into (W/D)* through B. Thus

    dim W >= r + nullity(b) = 2r-1.

Rank subadditivity applied to a transvection word gives length at least
rank(S+I)=dim W. This is PR5097's displacement-plus-nullity lower bound,
restated to make the present proof self-contained.

## One pivot leaves a zero form

A nonzero rank-one bilinear form factors as b(x,y)=lambda(x) mu(y), for
nonzero binary functionals lambda and mu. There is an a with
lambda(a)=mu(a)=1. If the functionals coincide, choose any vector on which
they are one. If they differ, they are independent and the two equations
are solvable. Therefore b(a,a)=1, and

    b(x,y) = b(x,a) b(a,y).                             (3)

Let T_a(v)=v+omega(v,a)a and h'=T_a h. Equations (1) give

    d'(u) = d(u) + b(a,d(u))a.

The map P:x -> x+b(a,x)a on D has kernel <a> and image
L=ker b(a,-). Hence dim d'(U)=r-1.

For x,y in L, choose u,v with d(u)=x and d(v)=y. Since P fixes L,
d'(u)=x and d'(v)=y. The residual form of h' is consequently

    b'(x,y)=omega(u,y)=b(x,y)=0,

where the final equality uses (3) and b(a,y)=0. Thus the new residual form
is identically zero on all r-1 displacement dimensions. This argument
uses rank one, without a restriction to a two-dimensional D.

PR5097 proves that a zero residual form of displacement rank s has an
attaining 2s-turn completion in the original V. Apply it with s=r-1 and
undo T_a. This yields at most 1+2(r-1)=2r-1 turns. The lower bound proves
equality. When r=1, h' is already the identity on U.

## Explicit completion of the zero-form remainder

For completeness, the constructor uses the predecessor's general at-most-2s
reduction. At a current partial isometry let K be its fixed subspace. Pick
u outside K and set p=h(u)+u. If omega(u,p)=1, the one turn T_p corrects u
and fixes K. Otherwise solve

    omega(K,a)=0, omega(u,a)=1, omega(p,a)=0.

The equations are consistent because u is not in K+<p>. Otherwise either
u is fixed, or h(u) is a member k of K with h(k)=k, contrary to injectivity.
Nondegeneracy represents this consistent functional by a in V.
The two nonzero orthogonal axes a and a+p give an involution correcting u
and fixing K. The new displacement rank decreases by at least one.
After at most s reductions the map is fixed on U. Reversing the correction
word gives its extension. On a zero-form input the lower bound 2s forces
this at-most-2s construction to attain exactly 2s.

## Interface and limits

The new theorem optimizes unsigned binary symplectic transvection count.
Under PR5085/PR5051's compatible signed-Pauli contract and free arbitrary
Pauli-correction tariff, the same minimum applies to the projective signed
lift. That is a cited interface implication, not a new phase implementation.
Absolute target phase needs an amplitude anchor. Every monomial pass and
native Gaussian service still needs pricing by an actual physical caller.

No improvement to native paid rank, recursive children, a complete supplier
invoice or kappa follows from (2) alone. Arbitrary higher-rank residual forms
remain open here. Finite checks corroborate the written proof; they do not
constitute independent human review or formal proof-kernel verification.
