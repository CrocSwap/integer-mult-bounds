# Independent review of reciprocal centre rank

The scalar theorem passes independent proof review. It applies to the
specified extensions of the actual clean response,

    J=I-KR,  E=J+KMR,  G=J+KNR,  K=R^T/4,  RK=14I_8.

For this family, dyadic M and N in a reciprocal pair each have rank eight.
Over the rationals, their least total rank is eight. The stated projection
formula gives every pair at that minimum. A coordinate projection of rank
four uses four actual R rows in each added correction.

This is a rank theorem for the two specified correction terms. It is not
a query or native-cost lower bound for every implementation of E and G.
For example, M=N=I has two rank-eight correction terms but E=G=I. A new
implementation of the identity need not form either term. The native
capture, frame, phase, and helper obligations need their own word review.
This packet does not establish a complete controller or a kappa change.

## Pinned input and method

The reviewed root proof is
`../../../root/RECIPROCAL-CENTRE-RANK-20261018.md`, SHA256
`d2209a60d45d52b6b1d8fed622820acd3468330cc0af926719c3a8747a2606b9`.
The root freeze is SHA256
`c8eff152a353492c41fd783429723adebddebdca93db20e3eeaf837594ba6dab`.
The source R is read from
`../../new-core-transfer-20261017/CLEAN-J-PROGRAMS.json.gz`.
Its decompressed SHA256 is
`a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa`.
These source files were not changed.

The new checker does not import a producer checker. It uses dense centre
matrices and a separate vector interpreter for the 112-field maps. It
checks RK=14I directly from the source entries. It also checks that every
R row has norm 56 and every K row has norm one in the row-sum norm.
The prior clean-core review binds this R to the literal native J. That
complete native replay was not repeated for this scalar theorem.

## Ordered proof

For a vector x, the new interpreter applies a response as

    E x = x + K(M-I)R x.

Apply G first and then E. The coefficient between K and R is

    (M-I)+(N-I)+14(M-I)(N-I)
      = 12I-13(M+N)+14MN.

This computation retains the order MN. Since RK=14I over the rationals,
K is injective and R is onto. Thus K C R=0 is equivalent to C=0.
One can also multiply on the left by R/14 and on the right by K/14.
There is no unstated loss of a centre equation.

The equation for reciprocity is equivalent to

    (14M-13I)(14N-13I)=I.

For square matrices over a field, a one-sided inverse is a two-sided
inverse. Subtract the reversed product equation. It gives MN=NM. Thus
commutation is a consequence, and GE=I follows. The checker also tests
the ordered identity for a pair with MN different from NM. Reversing
that test pair changes its residual, as it must.

Reduction modulo 13 is defined on Z[1/2]. The centre equation reduces
to MN=I over F_13. Both determinants are nonzero after reduction. They
were therefore nonzero before reduction. This proves each rank is eight.
The same proof works on a rational subring whose denominators are coprime
to 13. No rank statement for a noncommutative operator ring follows from
this argument without a separate module and reduction theorem.

Over the rationals, rewrite the equation as

    12I=13M+(13I-14M)N.

The rank of the right side is at most rank(M)+rank(N). For equality in
that bound, v in ker(N) satisfies Mv=(12/13)v. Hence ker(N) is contained
in im(M), and equality of dimensions gives ker(N)=im(M). To obtain the
other equality, use the reversed reciprocal equation proved above. It
gives ker(M)=im(N). This use of the reversed equation makes the phrase
"In the same way" in the source proof explicit.

The two kernels meet only at zero and their dimensions sum to eight.
Let P project onto ker(N) along ker(M). On these two summands M acts as
12/13 and zero, respectively. N acts as zero and 12/13. Therefore

    M=(12/13)P,  N=(12/13)(I-P).

This proves all equality cases. It does not require P to be orthogonal
or self-adjoint. The converse follows from P^2=P. The same proof, with
12,13,14 replaced by rho-2,rho-1,rho, proves the stated characteristic-zero
field result when rho is not 0, 1, or 2. In that version the coefficient
ring must contain the coefficients in use before a reduction is applied.

## A stronger denominator consequence

Call a rational matrix 13-integral if every entry has denominator coprime
to 13. Suppose M is 13-integral and E,G are reciprocal. The equation gives

    N=(14M-13I)^-1(13M-12I).

The first factor exists by the reciprocal equation. The second factor is
invertible: its reduction modulo 13 is I. Thus N has full rank eight,
even if N itself has a denominator divisible by 13. Interchanging M and
N proves the corresponding statement on the other side.

Consequently, a rank-four/rank-four reciprocal pair has a denominator
divisible by 13 in at least one entry of M and in at least one entry of N.
Allowing this denominator on only one side cannot give that split. This
is a coefficient statement, not a lower bound on scans or native calls.

## Exact checks and limits

The independent checker covers all 256 coordinate projections. It checks
both inverse orders on all 112 input basis vectors for nine pairs: five
coordinate ranks, one noncoordinate rank-four projection, one general
centre unit, one nontrivial dyadic reciprocal pair, and one 13-integral
rank-four correction with a full-rank partner. It also checks that
rank(MR)=rank(M) and rank(NR)=rank(N) in these cases.

The noncoordinate example is not self-adjoint. The dyadic example uses
M=I+S and N=I-S with S^2=0. These cases test assumptions that the proof
does not make. The noncommuting residual test covers all 112 columns.
Wrong weights, a repeated response, and an arbitrary noncommuting pair
are rejected as reciprocal pairs. The proof, not these finite examples,
establishes the universal rank bounds and equality classification.

The companion `ODD-GRID-COMPOSITION.md` proves a conditional representation
theorem. It permits these rational maps as finite parent operations while
completed recursive children retain exact Gaussian-dyadic endpoints.
It does not supply those endpoints for a changed global controller. It
does not replace the existing binary and magnitude guard by a count of
odd denominators.

Run from the workspace root:

    python3 work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/reciprocal-centre-rank-review-20261018/check_reciprocal.py
    python3 work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/reciprocal-centre-rank-review-20261018/check_grid.py

Expected statuses are `PASS_INDEPENDENT_RECIPROCAL_CENTRE_RANK` and
`PASS_INDEPENDENT_ODD_GRID_COMPOSITION_CHECKS`. Both commands also pass
with Python assertions disabled. The source pins and output hashes are
recorded in `FREEZE.json`.

The root lane supplied the rank theorem. Earlier clean-core and
odd-grid work supplied the actual J and the representation method.
This review supplied a separate interpreter, the explicit reversed-kernel
step, the one-sided denominator consequence, and the stated composition
conditions. This work used OpenAI Codex under the user's direction.
No publication is authorized.
