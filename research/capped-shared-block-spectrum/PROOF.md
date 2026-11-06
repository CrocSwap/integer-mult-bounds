# Sharp zero-primary capped spectra: corank one and cap two

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.

## Contract

Let F be any field of characteristic two, let r >= 1, and let D in M_r(F)
be an idempotent of rank r-1. Consider A+B=D. Write

    V_0(X) = ker(X^r),    z(X) = dim V_0(X),
    nu_0(X) = min {j >= 0 : ker(X^j) = ker(X^r)}.

Here X^0=I, so nu_0(X)=0 when X is invertible. On a nonzero zero-primary
space, nu_0(X) is the nilpotency index of the restriction of X to V_0(X),
equivalently the largest Jordan block at eigenvalue zero. This definition
does not require a splitting field: the zero-primary restriction is nilpotent
over F. We impose nu_0(A),nu_0(B) <= m for one integer 1 <= m <= r.
The nonzero-primary parts are unrestricted.

**Theorem 1 (corank one).** Let ell be the largest odd integer at most m. Then

    max {z(A)+z(B) : A+B=D, nu_0(A),nu_0(B) <= m} = r+ell.

The maximum is attained by matrices with entries in F2 after changing basis
so that D=diag(I_(r-1),0). Thus the maximum is field-independent within
characteristic two. The sharp cap-four answer at r=5,k=4 is eight. More
fully, at r=5 the maxima for m=1,2,3,4,5 are 6,6,8,8,10.

There is a distinct, stronger possible reading of a "nilpotency cap":
requiring A^m=B^m=0 on the entire space. Under that reading the domain is
empty unless r is odd and m=r (for 1 <= m <= r); the proof appears below.
In particular, no pair of globally nilpotent five-dimensional matrices with
indices at most four has a corank-one idempotent sum. The value eight above
belongs to the explicitly stated zero-primary contract, not that empty domain.

## A surviving primary subspace under a rank-one perturbation

Put E=I+D. Because D is idempotent of corank one, E is an idempotent of rank
one. Factor E=u f for a nonzero vector u and a linear functional f. Since
A+B=D and the characteristic is two, B=I+A+E.

Write a=z(A) and b=z(B), and restrict A to V=V_0(A). The cap gives A^m V=0.
Define the following subspace of V:

    W = {v in V : f(A^j v)=0 for every 0 <= j < m}.

At most m linear equations are imposed, so dim W >= a-m. The space W is
A-invariant: for j<m-1 the defining equation for Av is the next defining
equation for v; for j=m-1 it follows from A^m v=0. Also E vanishes on W,
since its j=0 defining equation is f(v)=0. Therefore W is B-invariant and

    B|_W = I_W+A|_W,    (B+I)^m|_W = 0.

Consequently W is contained in the one-primary subspace V_1(B). The zero
and one-primary subspaces are disjoint, by coprimality of t and t+1. Hence

    b + dim W <= r,       a+b <= r+m.                 (1)

This proof does not assume that V_0(A) is B-invariant. Only the specifically
constructed W must be invariant, and that invariance was checked above.

## Why an even cap loses one more dimension

If m is odd, inequality (1) is the claimed upper bound. Suppose m is even
and equality a+b=r+m were possible. The inequalities above force

    dim V_1(B) = dim W = a-m = r-b.

Thus V_0(B) and V_1(B) together fill the entire r-dimensional space. Apply
the same argument with A and B interchanged. It gives

    dim V_1(A) = b-m = r-a,

and A also has only zero and one primary parts. The traces of the nilpotent
zero parts vanish, and the trace of a one-primary part equals its dimension
as an element of F. Therefore

    tr(A)+tr(B) = (r-a)+(r-b) = 2r-(a+b) = r-m in F.

But tr(A)+tr(B)=tr(D)=r-1 in F. Their difference is 1-m, which is nonzero
in characteristic two because m is even. This is a contradiction. The
objective is an integer, so (1) strengthens to a+b <= r+m-1. Together with
the odd-cap case, the upper bound is r+ell.

## Binary attainment for every dimension and cap

Use the explicit odd-dimensional construction credited to Nick Petalas's
[#5928](https://github.com/CrocSwap/integer-mult-bounds/pull/5928). In dimension
ell, let J be the all-ones matrix, and let U,L be its strict upper and lower
triangular parts. Then

    U+L=I+J,       J^2=ell J=J,       (I+J)^2=I+J.

Both U,L are nilpotent with index at most ell. The idempotent I+J has kernel
the all-ones line and rank ell-1. Thus z(U)+z(L)=2ell. This remains true
at ell=1, where U=L=0 and the endpoint is zero.

Adjoin r-ell scalar coordinates with (A,B)=(0,1). The new endpoint is
(I_ell+J_ell) direct-sum I_(r-ell), an idempotent of rank r-1. On the added
coordinates only A contributes to zero multiplicity. Consequently

    z(A)+z(B)=2ell+(r-ell)=r+ell,
    nu_0(A),nu_0(B) <= ell <= m.

Every rank-(r-1) idempotent is similar over F to diag(I_(r-1),0), because its
image and kernel give complementary one and zero eigenspaces. Conjugating
both matrices by the same basis map gives the required endpoint without
changing zero multiplicity or the cap. The verifier uses the explicit binary
core basis e_1+e_ell,...,e_(ell-1)+e_ell,(1,...,1), then moves its kernel
coordinate to the final position. This proves the theorem without a search.

For r=5,m=4, one coordinate witness, with bit j encoding column j, is

    A=(19,1,0,0,18),        B=(18,3,4,8,18).

The verifier independently checks its endpoint, multiplicities and caps;
the documented numbers are required to agree with the constructor.

## The globally nilpotent interpretation

If A and B are both nilpotent, their traces vanish. Since tr(D)=r-1 in
characteristic two, r must be odd. Let v lie in ker A intersect ker E.
Then Bv=(I+A+E)v=v. Nilpotence of B forces v=0. Thus E is injective on
ker A, so dim ker A <= rank E=1. Nilpotence implies dim ker A >=1, hence
A has one nilpotent Jordan block of length r. Interchanging A,B proves the
same assertion for B. This is precisely the corank-one rigidity argument
of #5928, restated to make the contract boundary explicit. The indices
are both r. Conversely, for odd r the preceding construction with ell=r
provides such a pair. No new rigidity priority is claimed.

## Theorem 2: cap two at every idempotent rank

Let D instead have any rank k, with 0 <= k <= r, still over a field of
characteristic two. Impose nu_0(A),nu_0(B) <= 2 and A+B=D. Then

    max [z(A)+z(B)] = 2r-k.

In fact every such idempotent sum, without any chain cap, obeys

    rank(D) <= rank(A^2)+rank(B^2).                    (2)

To prove (2), substitute B=A+D and use D^2=D. Characteristic two gives

    A^2+B^2 = AD+DA+D,
    D(A^2+B^2)D = DAD+DAD+D = D.

Rank cannot increase under left or right multiplication, and rank is
subadditive. Therefore k <= rank(A^2+B^2) <= rank(A^2)+rank(B^2).
Under the stated cap, ker(X^2)=ker(X^r): the zero-primary restriction is
killed by the square and every nonzero-primary restriction is invertible.
This remains true when r=1. Thus rank(X^2)=r-z(X) for X=A,B. Substitution
into (2) proves the upper bound. The pair A=0,B=D attains 2r-k and already
has zero-primary caps at most one. This completes the proof for every r,k.

The hypothesis cannot simply be raised to cap three. The binary r=3,k=2
pair from the credited odd-block construction is

    A=(7,1,6),        B=(6,3,6),
    A+B=diag(1,1,0),  nu_0(A)=nu_0(B)=3,  z(A)+z(B)=6>4=2r-k.

The cap-two theorem supplies a complementary sharp slice to Theorem 1:
one allows every cap at corank one, the other every rank at cap two.
The compression identity is an elementary matrix calculation; no general
rank-inequality priority is asserted. The new use is the exact capped
spectral envelope in the shared-block contract.

## Scope, evidence and predecessor credit

#5928 supplies the unrestricted sharp envelope, binary odd-block
construction, corank-one full-chain rigidity and this open cap question.
This package adds the surviving-primary-subspace bound, the even-cap parity
exclusion, the resulting exact corank-one capped law, and the compression
identity's sharp cap-two consequence at every rank. Rank-one
perturbation, primary decomposition, trace and nilpotent Jordan methods are
classical; no general linear-algebra priority is asserted.

Credit JoyboyBrian's #5507 for the two-owner four-support funding model,
its genuine triple exception and global native-chain compensation; Ali
Romman's #5456 for the early-helper support model; and the retained
#5452/5388/589/555 BIT, native, owner and compiler lineage. These references
are context and attribution, not executable dependencies or a replay claim.

The universal quantifiers rest on the written argument. The standalone
standard-library verifier checks every binary A through dimension four for
every coordinate endpoint rank at cap two and for every cap at corank one,
a separate characteristic-polynomial oracle, explicit witnesses through dimension 33 and
adversarial domain/witness controls. It is exact finite corroboration, not
formal verification of the proof. No larger-support global compensation,
chronological native realization, full target/paid invoice, supplier
admission, compiler/precision/tape/dirty-workspace guarantee, new kappa or
selected-frontier change follows. Independent human and proof-kernel
review are unclaimed.
