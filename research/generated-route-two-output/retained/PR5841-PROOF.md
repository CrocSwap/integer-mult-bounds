# Whole-word carry identity and complete G20 binding

Let q>1 be coprime to12, w>=1, and M=q^(w-1). Let S be one exact rational
RIGHT product from either released PR5820 catalogue. Both S and its inverse
have dyadic coefficients and determinant a signed power of two. Thus S is
invertible modulo q and modulo q^w. The stronger source modulus guard is kept.
The argument also applies to any rational matrix whose denominators and
determinant are units modulo q, with the corresponding denominator bounds.

Write a row uniquely as x=l+q*h, with canonical low digits0<=l_i<q and
0<=h_i<M. Put

    l' = canonical residue of l*S modulo q
    C_S(l) = (l*S-l')/q.

Each column has a common dyadic denominator D. If N is the numerator of its
low product, then l'_j=N*D^-1 mod q. The integer N-D*l'_j is divisible by q.
Consequently C_j=((N-D*l'_j)/q)/D is dyadic, with denominator dividing D.
There is no residual q in that denominator. Also

    abs(C_j) < sum_i abs(S_ij)+1.

This bounds the carry independently of q and w. The exact low/high map is

    (l,h) -> (l', h*S+C_S(l) mod M).

Indeed l*S=l'+q*C_S(l), so rejoining the displayed output gives x*S modulo
q^w. At w=1 the high ring has one value and the same formula applies. This
integer identity proves the all-width assertion; finite checks are evidence
for the emitted source binding and implementations.

## Composition and final correction

For a second admissible matrix T, with l'=l*S mod q, direct substitution gives

    C_(S*T)(l) = C_S(l)*T + C_T(l').

The final canonical low digit is the same on both sides. Thus all carries of
a complete elementary word can be transported through its remaining linear
suffix and added once at the end. Execute the original high-digit linear word
without intermediate carries, then add C_S(l). Compute that vector from the
saved entry low row and commit the final low row l'. This is an explicit
algorithm; it does not use a table of q^8 low rows or depend on w.

If a column of S is a positive coordinate unit, its carry is identically zero
and needs no translation. The verifier omits exactly those columns. Every
other column has one possible final correction site. The count is an upper
bound: a particular low row can have additional zero carries. No minimum over
all physical circuits, correlated translations or alternative low sections is
claimed. The source linear words and all their ADD/SCALE charges remain.

The two complete source catalogues contain444 directed routes. Every port and
direction occurs34 times in the actual7,548-marker stream. Their per-marker
potential correction counts sum to28,492 for either basis. The factor-by-factor
construction has74,460 sites for the tree and53,448 for the shear basis. After
N=127f lifting these count differences are5,837,936f^2 and3,169,412f^2 named
correction calls. Each correction has a positive coefficient-specific physical
tariff. Changing coefficients or adding cache work can change the total cost;
these counts alone do not prove a physical saving.

## Inverse, high fibers and fields

Put T=S^-1. The composition law gives

    C_T(l') = -C_S(l)*T.

The inverse must read the committed low row l', not a stale entry cache. It
then restores both low and high digits exactly for every input. For each fixed
low row, h -> h*S+C_S(l) is a bijection of all M^8 high rows. For an N by N
cover and a fixed low matrix, the tensor embedding is a bijection of all
M^(N^2) high completions. If the low matrix is invertible, all its high lifts
are invertible: a matrix over Z/q^w is invertible exactly when its determinant
is a unit modulo q. This also holds for the tested composite radix. No fresh
stock values are filtered out.

The18 actual stages have nonconsecutive numeric labels. Give the k-th source
stage, k=0..17, axes0 and1+7k through7+7k, as in the retained cover convention.
For row r and lane t, addresses are r*N+axis*f+t, where N=127f. They are distinct.
Each row has f disjoint active eight-entry blocks. The map is the identity on
all other columns. It reads no ancestor, role, head/data or unused-descendant
field, so it is the identity on those product factors for arbitrary values.
The chosen compatible axis convention is not a proved physical head layout.

ENTRY uses the inverse word and RETURN the forward word under the retained
single-cover convention h=gS. The checker rebuilds every marker index, stage,
owner bank, port and phase from the frozen call intervals. This binds the new
carry program to the exact source incidence. The physical reflected pairing
and native port action remain the source's proved contract; no second cover
or factor-of-two bill is introduced here.

## Verification and remaining obligations

The dense oracle multiplies full-width residues by S without splitting digits
or using a carry routine. The separate elementary interpreter uses integer
carry numerators at each factor. Both agree with the fused interpreter over
all emitted routes. A noncommuting next matrix tests the general cocycle,
not only inverse round trips. Full cover fixtures check source stage ordinals,
all rows and lanes, inactive coordinates and exact inverse restoration.
Controls reject missing carry, stale low type, wrong order, an omitted nonzero
correction, wrong owner and an ineligible modulus.

The algorithm is an exact row-index implementation. Low cache, type commit,
translation, preparation and cache erasure are not assumed free. Literal ROW
heads, tape execution, padding, borrowed-child return, physical coefficient
tariffs and the complete current caller binding remain separate obligations.
No selected framework assumption is discharged and no kappa change is claimed.
