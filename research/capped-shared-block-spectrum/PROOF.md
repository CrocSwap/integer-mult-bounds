# The sharp zero-primary capped spectrum at every idempotent rank

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.

## Contract and theorem

Let F be any field of characteristic two, r >= 1, and D in M_r(F) an
idempotent of rank k, where 0 <= k <= r. Write s=r-k. For a matrix X define

    V_0(X)=ker(X^r),       z(X)=dim V_0(X),
    nu_0(X)=min {j>=0 : ker(X^j)=ker(X^r)}.

Thus nu_0(X) is the longest zero-primary Jordan chain, and is zero for an
invertible matrix. The nilpotent restriction to V_0(X) is defined over F;
no splitting field is needed. Nonzero-primary parts remain unrestricted.
Fix 1 <= m <= r, and let ell be the largest odd integer at most m.

**Theorem.** Among all A+B=D with nu_0(A),nu_0(B) <= m, the sharp maximum is

    H(r,k,m) = min(2r-(k mod 2), r+(r-k)*ell).

The maximum is attained by binary matrices after changing basis so that
D=diag(I_k,0). The formula includes k=0, k=r, m=1, and r=1. In particular,
k=r gives r; corank one gives r+ell; cap two gives 2r-k. At r=5,k=4, the
maxima for caps 1,2,3,4,5 are 6,6,8,8,10. At r=12,k=10,m=6 the maximum is
22: even caps need not be powers of two.

This completes the specified local cap question from Nick Petalas's
[#5928](https://github.com/CrocSwap/integer-mult-bounds/pull/5928). It imposes
no chronological native program, ownership condition or physical caller.

## The universal trace bound

Always z(A)+z(B)<=2r. If k is odd, equality would make A and B nilpotent,
so their traces would vanish. But tr(A)+tr(B)=tr(D)=1 in F. The integer
objective is therefore at most 2r-1. This proves the first term of H.

## Odd caps: a surviving primary subspace

Put E=I+D, an idempotent of rank s. Then B=I+A+E. Let a=z(A), b=z(B), and
V=V_0(A). The cap gives A^m V=0. Define

    W={v in V : E A^j v=0 for 0<=j<m}.

Each of the m maps has image in im E, of dimension s, so dim W>=a-ms.
The space W is A-invariant: the next defining equation handles A v until
the final one, where A^m v=0 applies. Since E kills W, it is B-invariant
and B|_W=I_W+A|_W. Therefore W belongs to the one-primary subspace of B.
That space has zero intersection with V_0(B), by coprimality of t and t+1.
Thus b+dim W<=r, giving

    z(A)+z(B)<=r+ms.

For odd m this is the second term of H. No invariance of the whole V_0(A)
under B is asserted; only the constructed W is invariant.

## Every even cap: an injective intersection map

The following stronger lemma needs no primary-chain assumption. For every
positive even m, with U=ker A^m intersect ker B^m,

    dim U <= (m-1)s,
    k <= rank(A^m)+rank(B^m)+(m-2)s.                 (1)

Set C=I+A, so B=C+E. Define

    Phi: U -> (im E)^(m-1),
    Phi(u)=(Eu,EAu,...,EA^(m-2)u).

We prove injectivity. Suppose Phi(u)=0. Binomial expansion of C^i gives
EC^i u=0 for i<=m-2 and EC^(m-1)u=EA^(m-1)u. The ordered identity

    B^m+C^m = sum_(i=0..m-1) B^(m-1-i) E C^i         (2)

holds without commutation: substituting E=B+C makes interior words occur
twice, leaving only B^m and C^m in characteristic two. Apply (2) to u.
Since B^m u=0 and the lower moments vanish, only i=m-1 remains:

    C^m u=EA^(m-1)u.                                 (3)

In C^m=(I+A)^m, the coefficient of A^(m-1) is m, hence zero. The top term
A^m u is zero, and E kills every remaining power of A applied to u.
Consequently EC^m u=0. Applying E to (3), using E^2=E, gives
EA^(m-1)u=0 and therefore C^m u=0. On the A-invariant space ker A^m,
I+A is invertible with inverse sum_(j=0..m-1) A^j. Thus u=0, proving
injectivity. The intersection U itself need not be A- or B-invariant.

Its codomain has dimension (m-1)s. Also

    dim U >= r-rank(A^m)-rank(B^m).

Together these prove (1). Under the primary caps, ker A^m=V_0(A) and
ker B^m=V_0(B), so (1) becomes z(A)+z(B)<=r+(m-1)s. Since ell=m-1 for
even m, this is precisely the second term of H. The proof covers m=6 and
all other positive even integers, not just powers of two.

Evenness is necessary for (1). The binary three-dimensional witness with
rows A=(7,1,6), B=(6,3,6) has D=diag(1,1,0), A^3=B^3=0 and s=1.
Extending (1) to m=3 would assert 2<=1.

## Binary attainment for all ranks and caps

Use the odd-dimensional construction from #5928. In an odd dimension n,
let J be the all-ones matrix and U,L its strict upper/lower triangular
parts. Then U,L are nilpotent of index at most n and

    U+L=I+J,    J^2=nJ=J,    (I+J)^2=I+J.

The endpoint has rank n-1, with kernel the all-ones line. Its coordinate
basis is e_1+e_n,...,e_(n-1)+e_n,(1,...,1). This is a binary basis, giving
an explicit pair with endpoint diag(I_(n-1),0). At n=1 both matrices are zero.

Put c=(ell-1)/2 and T=min(floor(k/2),s*c). Distribute T units among s
integers a_i in [0,c], for example greedily; this is possible since T<=s*c.
Use s odd cores of dimensions n_i=2a_i+1, and t=k-2T scalar coordinates
with (A,B)=(0,1). For s=0 there are no cores, T=0 and t=k=r. In all cases,

    total dimension = s+2T+t = r,
    endpoint rank   = 2T+t = k,
    z(A)+z(B)       = 2(s+2T)+t = 2r-t,
    nu_0(A),nu_0(B) <= ell <= m.

The minimal leftover scalar count is

    t = max(k mod 2, k-s*(ell-1)).

Hence 2r-t=min(2r-(k mod 2),r+s*ell), as required. The verifier places
all rank coordinates first and all core kernels last, giving the literal
coordinate endpoint diag(I_k,0). Every rank-k idempotent over F is similar
to that endpoint, since its image and kernel are complementary fixed and
zero subspaces. Simultaneous conjugation transports the pair to the stated D.
This proves attainment over every characteristic-two field, without search.

## Distinct globally nilpotent contract

Requiring A^m=B^m=0 on the entire space is stronger than the zero-primary
cap. By the theorem and its construction, such a pair exists exactly when

    k is even and r <= (r-k)*ell.

At corank one this reduces to r odd and m=r; thus the globally nilpotent
r=5,m=4 domain is empty, whereas the zero-primary capped maximum is eight.
The corank-one rigidity proof from #5928 also shows each globally nilpotent
summand then has a single full-length chain: E is injective on ker A, since
Av=Ev=0 would imply Bv=v, and likewise after exchanging A,B.

## Useful alternative special-case arguments

The earlier corank-one proof gave the weak bound r+m, then excluded equality
for even m: equality forces both A and B to have only zero and one primary
parts, so tr(A)+tr(B)=r-m disagrees with tr(D)=r-1. The intersection proof
above replaces that parity step for general corank. The prior version and
its exact reviewed hashes are retained in REVIEW.md and Git history.

For cap two, the simpler identity remains useful:

    A^2+B^2=AD+DA+D,       D(A^2+B^2)D=D.

It yields k<=rank A^2+rank B^2 and hence the same sharp 2r-k bound. The
triple witness above has zero multiplicity six, exceeding 2r-k=4, so that
cap-two conclusion cannot simply be extended to cap three.

## Classical context, credit and evidence boundary

Nick Petalas/#5928 supplies the unrestricted envelope, odd-block construction,
corank-one rigidity and capped-envelope question. The new content is the
rank-s surviving-subspace bound, the even-m intersection injection and the
explicit bounded odd-core allocation proving the complete capped formula.
Credit JoyboyBrian/#5507 for the two-owner four-support funding model and
triple compensation, Ali Romman/#5456 for the early-helper model, and the
retained #5452/#5388/#589/#555 BIT/native/owner/compiler lineage.

Triangular nilpotent constructions and restrictions on idempotent sums are
classical. See Ferrero, Puczyłowski and Sidki, *On the Representation of an
Idempotent as a Sum of Nilpotent Elements*, Canadian Mathematical
Bulletin 39 (1996), 178–185,
[DOI 10.4153/CMB-1996-022-0](https://doi.org/10.4153/CMB-1996-022-0).
Their Example 1 gives a positive-characteristic triangular construction;
Proposition 2 concerns globally nilpotent summands when one is square-zero.
That global contract differs from our zero-primary cap allowing nonzero
spectral parts. The present proof uses no result from that paper. The
literature check was bounded, and no general mathematical priority is claimed.

The universal quantifiers rest on the written proof. Exact standard-library
checks cover every binary A through dimension four, every coordinate endpoint
rank and every cap, separate characteristic polynomials, explicit constructors
through dimension 33, and independent finite-field engines. They corroborate
rather than formally verify the theorem. No native chronological realization,
complete target/paid invoice, supplier admission, precision/tape/compiler
claim, new kappa or selected-frontier change follows. Independent human and
proof-kernel acceptance are unclaimed.
