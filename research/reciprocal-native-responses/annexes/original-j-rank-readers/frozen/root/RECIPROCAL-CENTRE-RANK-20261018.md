# Exact division cuts the centre rank of reciprocal responses

The actual clean native response is J=I-KR, where R has eight rows,
K=R^T/4, and RK=14I. Consider two extensions of this same response:

    E=J+KMR,                 G=J+KNR.                    (1)

Here M and N are scalar eight-by-eight matrices. The centre information
needed for the extra terms is MRx and NRx. This note measures their
rational ranks. Native access, capture, storage, and restoration need
separate circuit checks.

If the coefficients of M and N are dyadic and EG=I, both M and N must
have rank eight. If exact division by 13 is allowed, the least possible
sum of the two ranks is eight. Every pair at this minimum has the form

    M=(12/13)P,              N=(12/13)(I-P),              (2)

where P is a projection. A coordinate projection of rank four gives four
centre queries in each direction. Thus the coefficient representation
changes which reciprocal responses are possible in this actual family.
It cuts the minimum total query rank from sixteen to eight.

This is not a lower bound for other native response families. In
particular, a new interior response need not have the form (1). This
result does not supply a routed controller or a complete supplier price.
The selected kappa value does not change.

## Ordered identity

Direct multiplication, using RK=14I, gives

    EG-I=K[12I-13(M+N)+14MN]R.                            (3)

The matrices K and R have full column and row rank over the rationals.
Thus EG=I if and only if the bracket in (3) is zero. Equivalently,

    (14M-13I)(14N-13I)=I.                                (4)

No commutation of M and N is assumed to derive (3). Equation (4)
implies it: the two factors are inverses of square matrices, so they
commute, and therefore MN=NM. Also GE=I.

## Dyadic necessity

Reduce (3) modulo 13. Reduction is defined for every dyadic coefficient
because 2 is invertible modulo 13. The result is

    MN=I over F_13.

Both reduced matrices are invertible. Their rational determinants are
therefore nonzero, and both rational ranks are eight. The choice
M=N=I gives E=G=I, so the lower bound of sixteen is sharp within (1).

The same proof applies to any rational coefficient ring that has a
reduction to F_13. In particular, admitting fixed odd denominators
coprime to 13 does not remove this obstruction. The proof does not cover
operator-valued coefficients unless their reduction and rank convention
are specified separately.

## Rational optimum and all equality cases

Equation (3) gives

    12I=13M+(13I-14M)N.

The rank of the right side is at most rank(M)+rank(N), so this sum is
at least eight. Suppose it equals eight. For v in ker(N), equation (3)
gives Mv=(12/13)v. Hence ker(N) is contained in im(M). Their dimensions
are equal, so im(M)=ker(N). In the same way im(N)=ker(M).

The two kernels have zero intersection: equation (3) applied to a
vector in both kernels gives 12v=0. Their dimensions sum to eight,
so they form a direct sum. Let P be the projection onto ker(N) along
ker(M). Then M=(12/13)P and N=(12/13)(I-P), as claimed.

Conversely, for any P with P^2=P, the matrices in (2) have MN=NM=0
and M+N=(12/13)I. Equation (3) is zero. Their rank sum is eight.

This proof also gives the general statement. If RK=rho I on an
r-dimensional centre space over a field of characteristic zero, and
rho is not 0, 1, or 2, then the minimum rank sum for reciprocal
extensions of J=I-KR is r. Its equality cases are

    M=((rho-2)/(rho-1))P,
    N=((rho-2)/(rho-1))(I-P).

If a coefficient ring reduces to a field where rho=1, each extension
instead has full centre rank r. For the actual supplier rho=14, so
the relevant prime is 13.

## What the construction does

On ker(R), both E and G act as the identity. On im(K), write a vector
as Kc and split c into Pc+(I-P)c. Then

    E Kc=K[-(1/13)Pc-13(I-P)c],
    G Kc=K[-13Pc-(1/13)(I-P)c].

Thus each map leaves the bulk unchanged and exchanges the two centre
scales with its reciprocal. For a coordinate rank-four P, each extra
term in (1) uses four rows of the actual R. The original rank-eight
centre capture can therefore be restricted to four coordinates if its
helper correction is changed with the same weights. That literal
native implementation is a separate packet.

The accepted odd-grid representation theorem permits exact division
by a fixed odd integer after root conversion, including arbitrary
borrowed fields. It requires the completed recursive children to have
their stated exact endpoints and charges unfinished prefixes along the
active recursion path. This note uses that theorem only to identify a
legal coefficient representation. It does not prove a precision bound
for an unspecified global controller.

The forward and reverse scalar responses can now be reciprocal in one
chart. Their physical maps still contain ordered port operators q.
For example, the forward response is qEq in the common full chart.
Changing charts, transporting the code, and the terminal remain open.
Replacing E^T by E^-1 without a separate reverse word is not valid.

## Verification and source evidence

The checker reads the pinned actual R from
../lanes/new-core-transfer-20261017/CLEAN-J-PROGRAMS.json.gz.
Its decompressed SHA256 is
a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa.
It checks RK=14I, every coordinate projection on the eight-dimensional
centre, and both full 112-field inverse orders for five coordinate
projections and one noncoordinate projection. It also checks two
mutations that break reciprocity. These exact calculations support the
proof; a finite list of examples is not the rank argument above.

Run from the workspace root:

    python3 work/centre-encoding-campaign-20261014/root/check_reciprocal_centre_rank_20261018.py

Expected status:

    PASS_EXACT_RECIPROCAL_CENTRE_RANK

The source R, clean J, and native capture are inherited from the current
supplier and the earlier clean-core work. The root lane derived the
reciprocal split and rank classification. Oblique-native supplied the
capture and helper-correction plan. The new-native-recipes lane is
checking its literal implementation. This work used OpenAI Codex under
the user's direction. Independent proof review is still required.
No publication is authorized.
