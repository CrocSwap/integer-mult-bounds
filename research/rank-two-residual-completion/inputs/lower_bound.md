# Singular partial Pauli completion: the missing three/four-turn boundary

Krzysztof Wojt, with substantial OpenAI Codex assistance. Apache-2.0.

This is a scoped algebraic proof, not a physical supplier or a new kappa.
Nick Petalas's [PR #5085](https://github.com/CrocSwap/integer-mult-bounds/pull/5085),
head `d32b46c02387b3bc9dc0bea344b2c6271b08c5f9`, asks for the exact minimum
at singular displacement rank two. It already supplies the induced form and
the exact cutoff through two turns. JoyboyBrian's #5051 supplies the compatible
partial signed-Pauli setting. The elementary residual-form machinery is
classical (often called a Wall form); no literature-priority claim is made.
This proof is self-contained and does not depend on a predecessor executable.

## Statement and model

Let V be any finite-dimensional nondegenerate symplectic space over F2 with
pairing omega. Let h:U -> V be an injective linear isometry of a subspace U.
Put d=h+I, D=d(U), r=dim D, and define the residual bilinear form

    b(d(u),d(v)) = omega(u,d(v)).

Let ell(h) be the least number of nonzero-axis transvections
T_a(v)=v+omega(v,a)a whose product agrees with h on U. All axes lie in the
original V; no clean ancilla or new dimension is allowed. The action outside
U is unspecified. In particular, unprescribed spectators are not promised to
be fixed; a required fixed spectator belongs in U with h(v)=v.

**Theorem.** Every such partial map satisfies

    r + nullity(b) <= ell(h) <= 2r.

If b=0, the bound is sharp: **ell(h)=2r**, for every r, including r=0.
If r=2 and b has rank one, **ell(h)=3**. Consequently every singular
rank-two contract has the exact minimum **4-rank(b)**: three or four turns.
The proof supplies attaining words inside V.

Only the zero-form all-rank family and the singular rank-two family are
classified exactly here. The general upper bound is not asserted to be
optimal when b is nonzero. Transvection count is a formal tariff, not native
Gaussian paid rank, recursive-child rank, physical cost or a supplier invoice.

## The induced form

Write K=ker d. For k in K and u in U, isometry and h(k)=k imply
omega(k,d(u))=0. Thus K is orthogonal to D and b is well-defined. Expanding
omega(h(u),h(v))=omega(u,v) gives

    b(x,y)+b(y,x)=omega(x,y) for x,y in D.             (1)

These are the predecessor's induced-form facts, repeated to make the argument
checkable without importing that package.

## A displacement-plus-nullity lower bound

Take any full symplectic extension S of h, and put W=im(S-I). For every
v,z in V,

    omega(v,(S-I)z)=omega((S^-1-I)v,z).

Hence W-perp=ker(S-I). The full residual form

    B((S-I)v,w)=omega(v,w),  w in W,

is well-defined. If its left row at (S-I)v is zero, v belongs to W-perp,
so (S-I)v=0. Therefore B is nonsingular. Since D is contained in W and
S agrees with h on U, B restricted to D times D is exactly b.

Let R be the left radical of b. Each x in R defines a functional B(x,-)
on W/D, because B(x,D)=0. The map R -> (W/D)* is injective by
nonsingularity of B. Thus

    nullity(b)=dim R <= dim W-r.

Each transvection changes the identity by rank one, and
AB-I=A(B-I)+(A-I) implies rank(S-I) <= the number of turns in any word
for S. Combining the two inequalities proves ell(h)>=r+nullity(b).
This lower bound permits any completion on unspecified coordinates.

## Completing in at most two turns per displaced dimension

The following reduction is uniform in dim V and preserves the whole currently
fixed subspace, not merely a chosen list of previously treated vectors.

If r>0 choose u in U outside K, and let p=h(u)+u, so p is nonzero and
orthogonal to K. If omega(u,p)=1, T_p fixes K and exchanges u and h(u).

Otherwise choose a in V solving

    omega(k,a)=0 for every k in K,
    omega(u,a)=1,       omega(p,a)=0.                 (2)

These equations are consistent. Indeed u is not in K+<p>: membership in K
contradicts its choice, while u=k+p would give h(u)=k=h(k), contradicting
injectivity. Therefore the functional zero on K+<p> and one on u is
well-defined, extends to V, and is represented by a through nondegeneracy.
Also a and a+p are nonzero, since both have pairing one with u. They are
orthogonal to K and to each other. Their commuting turns give

    (T_(a+p) T_a)(u)=u+p=h(u).

The product is an involution, so it also sends h(u) to u. Let F be this
two-turn product, or the preceding single turn. Then h'=F h is again an
injective partial isometry and fixes K+<u>. Its displacement rank is at most
r-1. Repeat until it is the identity on U. There are at most r reductions,
each with at most two turns. Reversing the collected correction word gives
a full symplectic extension of h with at most 2r turns. Every step solves
linear equations in the original V. No auxiliary dimension is introduced.

When b=0 the lower bound is 2r, so this construction necessarily returns
exactly 2r turns. This proves the entire zero-form family, including the
four-turn rank-two case.

## Rank-one singular form at displacement rank two

Suppose dim D=2 and rank b=1. There is a in D with b(a,a)=1. Otherwise
b would be alternating, hence in any two-dimensional basis would have
matrix [[0,c],[c,0]], of rank zero or two, a contradiction.

Apply T_a on the left and put h'=T_a h. By (1), its displacement is

    d'(u) = d(u) + b(a,d(u)) a.                       (3)

The map P:x -> x+b(a,x)a has kernel <a>, since b(a,a)=1. Its image is
the line L=ker b(a,-), so d'(U)=L and has rank one. Choose its nonzero
c; in basis (a,c) the form has matrix

    [1 0]
    [s t].

Its rank is one, so t=0. For u_c with d(u_c)=c, formula (3) gives
d'(u_c)=c, and the new residual form has value
b'(c,c)=omega(u_c,c)=b(c,c)=0. Thus h' belongs to the rank-one zero-form
family and has a two-turn completion. Appending T_a gives three turns for
h. The lower bound r+nullity(b)=2+1=3 proves optimality.

## Signed contracts, evidence and remaining boundary

For compatible signed Hermitian Pauli constraints, each transvection has a
literal Clifford lift. The sign discrepancies on independent prescribed
generators define a binary functional on h(U); a Pauli conjugation implements
it. Under #5085's tariff of free arbitrary Pauli corrections, this does not
change the minimum. Compatibility of dependent central phase relations is a
premise, and equality to an absolute-phase target still needs an anchor.
These are cited predecessor implications; this contribution verifies unsigned
labels, not a new literal Gaussian matrix or signed-phase implementation.

The standalone verifier compares against complete symplectic-matrix Cayley
distances in dimensions two and four. Larger zero-form and rank-one-form
fixtures test the constructive algorithm and its fixed spectators; they are
not exhaustive. The finite checks corroborate this written all-dimensional
proof and do not replace it. No independent human or proof-kernel review,
native/physical cost, profitable caller, arbitrary dirty-owner schedule,
precision, stock, compiler/outer admission or new kappa is claimed.
