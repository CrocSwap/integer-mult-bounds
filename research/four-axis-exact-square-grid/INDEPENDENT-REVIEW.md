# Independent mathematical review of the four-axis square lift

Reviewer: Worker A, prepared for Jerry Chen / @CubeJerry with substantial
OpenAI assistance. Apache-2.0. This is a separate mathematical derivation
and exact arithmetic review, not external human or proof-kernel acceptance.

Reviewed compressed certificate: `CERTIFICATE.json`, SHA256
`44a950a62abec947b4c094c2c1f290bec2f8d7f41d3a108ab4c58b5bdfc46b56`.
The author's search was read for definitions but is not imported or executed
by this review's checker. The lead separately completed all 4096 finite transitions using the direct
integer implementation retained in `independent_square.py`. This review
establishes why the precisely listed finite conditions suffice on the entire
integer lattice. The compressed table is hash-bound here; this checker does
not expand it or import the author's certificate code.

The period and lifting argument are unchanged in the forced-cycle revision.
Its new full finite replay and direct tensor-bound attainment are independently
reviewed in [SHARPNESS-REVIEW.md](SHARPNESS-REVIEW.md); the earlier certificate
had SHA256 `9f7fa583cc8955e7f3129ff01db48dff849db6fd026f4205a0475f935ba174c7`.

## 1. Operators and exact phase conventions

Index the 16 coordinates by v in F2^4. Let W be the 16-by-16 Walsh matrix,
W_uv=(-1)^(u dot v), A=W/4, S_vv=(-1)^wt(v), and J the permutation
(Jz)_v=z_(v xor 15). Write B=SA and K=SJ. The Fourier identities give

    A²=I,   AS=JA,   SA=AJ,   SJ=JS,
    B²=K,   K²=I,   B⁴=I.

The equality SJ=JS uses the even dimension four: complementing all bits
preserves the parity of their weight. This sign is material.

The review checker constructs W by four tensor doublings, constructs the
lattice basis independently, inverts it over rational numbers, and verifies
the displayed square identities. It does not use the author's bit-dot
implementation or stored coordinate-action matrix.

## 2. The exact integrality lattice and its coordinates

Let L={z in Z^16: Az is integral}. Modulo four,

    W_uv = 1-2 sum_j u_j v_j.

Consequently z belongs to L exactly when its total coordinate sum is
divisible by four and each of its four bit sums is even. The necessity
follows by using the zero Walsh row and the four singleton rows; the same
formula proves sufficiency for all 16 rows.

An integer basis consists of 4e0; the four vectors 2(e_(2^j)-e0); and, for
every v of weight at least two, the vector

    e_v+(wt(v)-1)e0-sum_(j in v)e_(2^j).

In the coordinate order (zero, four singletons, eleven higher-weight
vertices), its determinant is 4*2^4=64. Its coefficient coordinates are
the total sum divided by four, the four bit sums divided by two, and the
eleven original higher-weight coordinates. Thus it spans all of L, not a
subgroup with an unaccounted index.

For z in L, Bz is integral; moreover ABz=Jz is integral. Hence B maps L
into itself. B⁴=I makes it an automorphism of L.

## 3. The period subgroup has the asserted index and is stable

For a vector's L-coordinate column t, define six parity checks by row masks

    0x21, 0x906, 0x6fde, 0x103, 0xa8ec, 0x29e.

Let Gamma be the kernel of these six checks inside L. The six rows have
rank six over F2, so [L:Gamma]=64 and [Z^16:Gamma]=4096. If rho_0,...,rho_5
denote the rows and M is the integer coordinate matrix of B on L, the
independently reconstructed exact action is

    rho_0 M = rho_0+rho_1,
    rho_1 M = rho_1+rho_2,
    rho_2 M = rho_2,
    rho_3 M = rho_3+rho_4,
    rho_4 M = rho_4+rho_5,
    rho_5 M = rho_5,                       over F2.

Therefore B(Gamma)=Gamma. Negation and K also preserve Gamma.

The six parity checks restricted to their first five coordinates have rank
five. A vector in L is coordinatewise even precisely when its eleven
higher-weight basis coordinates are even. If such a vector also lies in
Gamma, injectivity of those first five restricted checks forces every
basis coordinate even. Therefore

    Gamma intersect 2Z^16 is contained in 2L.

This rules out the immediate oddness obstruction at the half-periods.
For comparison the coarser lattice L does have that obstruction: 4e0 lies
in L intersect 2Z^16, while A(2e0) has half-integer entries. An odd map
affine on all of L with slope A would have 2R(2e0)=A(4e0), an impossible
odd integer output column. This comparison is a necessary-condition
control. The stronger minimality conclusion uses the predecessor theorem
reviewed below, rather than this necessary condition alone.

### Applicability of the predecessor's lower bound

The reviewed source is
`CrocSwap/integer-mult-bounds#6761`, head
`b78c8938b6d04b7c340c06d4e958947aeecd9270`,
`research/four-axis-exact-square-period-obstruction/PROOF.md`.
Its hypotheses are an odd integer map R commuting with K, with any
full-rank affine period of slope A. The proof first closes the period under
K, then studies V=L/2L and E=(L intersect 2Z^16)/2L. For C=K+I on V,
C restricted to E has rank one but E intersect im(C) has dimension at
least two. A K-invariant subspace H disjoint from E therefore cannot have
dimension eleven: otherwise E identifies with V/H, whose induced C would
simultaneously have rank one and contain two independent image vectors.
Thus dim(H)<=10 and the full period index is divisible by 4096.

The review independently checked these premises by matrix ranks, without
using the predecessor's supplied witnesses: C has rank six, E+im(C) has
rank nine, and hence dim(E intersect im(C))=5+6-9=2. Its first five columns
are (0,e0,e0,e0,e0), proving the rank-one restriction. The quotient argument
has no additional radius, sum, or bijectivity premise.

Our T commutes with K=T², and S commutes with K, so R=ST commutes with K.
The constructed Gamma is a full-rank affine period of R with slope A and
index exactly 4096. The source theorem therefore applies, and the new
construction attains its divisibility lower bound. This is a minimum for
the stated real affine-period architecture; it does not prove a minimum
for arbitrary coupled complex rounders, memory, or physical cost.

## 4. The 4096 labels classify every integer vector

The first six bits are the four-valued total sum and four two-valued bit
sums. Given those residues, choose the base representative with the four
singleton coordinates equal to the bit residues and zero coordinate equal
to the total residue minus their sum. Subtracting this representative puts
the vector in L. Apply the six parity checks to its integer L coordinates
for the second six bits.

Two integer vectors have the same complete label exactly when their
difference lies in Gamma. This follows directly from the two successive
quotients, Z^16/L and L/Gamma. All labels occur because both quotient maps
are surjective. The base representative section need not be a group
homomorphism, and labels must not be added by bitwise XOR across the full
4096-class quotient. XOR is valid only within the L/Gamma fiber.

## 5. Sufficient finite conditions and the all-integer square

Let c_s be the integer correction column stored at each Gamma coset s.
For one representative r_s of every coset, the complete finite verifier
must establish the following:

1. B r_s+c_s/4 is integral.
2. If p(s) is the class of that output, c_(p(s))=-B c_s as an exact vector.
3. If n(s) is the class of -r_s, c_(n(s))=-c_s as an exact vector.
4. Each c_s has squared norm at most 64 and lies in the complex linear
   kernel of the row d_v=(-i)^wt(v).

There is no rounding tolerance in these requirements. The second condition
in particular checks the integer divisibility implicit in B c_s.

Define, for every integer input,

    T(z)=Bz+c_([z])/4,             R(z)=S T(z).

For gamma in Gamma, B gamma lies in Gamma, so

    T(z+gamma)=T(z)+B gamma.

Thus the first finite condition proves integrality for every representative
translate, p([z])=[Tz] is well defined independently of the representative,
and the correction at the second call really is c_(p([z])). Consequently

    T²z = B²z+(B c_([z])+c_(p([z])))/4 = Kz.

The finite oddness condition likewise gives T(-z)=-T(z). Since K is a
bijection, T²=K makes T a bijection. R is therefore an odd bijection, and

    R S R = S T S S T = S T² = S K = J.

R is affine on Gamma with slope A because SB=A. This proof supplies the
infinite quantifier. Replaying only the chosen representatives without
Gamma stability would not establish it.

## 6. Complex lift, square, inverse and global unit covariance

Extend R to Gaussian integer vectors by applying it separately to real
and imaginary parts; call the extension R_C. Oddness implies
R_C(i z)=i R_C(z), so R_C commutes with each global Gaussian unit. This
does not assert covariance under separately chosen coordinate phases.

Set D_vv=(-i)^wt(v) and

    F(z)=-D R_C(Dz).

Then D²=S and D J D=J, the latter because the weights at complementary
vertices sum to four. Keeping the outer minus signs gives

    F²z = -D R_C(-S R_C(Dz))
         = D R_C(S R_C(Dz))
         = D J D z
         = Jz.

This uses oddness exactly once and uses R_C S R_C=J; it does not assume
that R_C commutes with D or with S. Hence F⁴=I, F is bijective, and its
inverse is JF=FJ. F commutes with global Gaussian units as well.

## 7. Error, weighted sum, and sharpness

The real error is Rz-Az=S c_([z])/4. It has Euclidean norm at most two.
The certificate tests d-transpose c=0. For the error actually used by R,
the required row is d-transpose S=conjugate(d)-transpose. Since each c is
real, its annihilation by d also implies annihilation by conjugate(d).
Thus d-transpose(Rz-Az)=0. Both integer real/imaginary weighted equations are among the finite table
checks. The earlier review also checked them on the expanded table; this
retained script avoids a redundant expanded artifact and leaves the complete
table replay to `verify.py` and `independent_square.py`.

The ideal complex map is H=-DAD. Its matrix entry is

    H_uv=-(1/4)(-i)^wt(u xor v).

Its row and column sums are one because
-(1/4)(1-i)^4=1. Thus preserving the d-weighted error of R_C gives
sum(Fz)=sum(Hz)=sum(z), including its full complex phase. Both pre- and
postmultiplication by D preserve Euclidean norm, so

    ||Fz-Hz||² <= 4+4 = 8.

The representative 2e0 has label 128 and correction squared norm 64.
For z=(2+2i)e0 the same maximum real correction occurs in both components,
and the complex bound sqrt(8) is attained. H²=J by the identical linear
calculation, so F^-1-H^-1=J(F-H), proving the same sharp inverse bound.
The maximum absolute correction-table entry is five: actual real-component
error coordinates are bounded by 5/4, not five.

All 64 classes in the L/Gamma fiber have zero correction, and no other
class does. Hence Rz=Az whenever Az is integral, not merely when z is a
chosen representative. For the complex map, Hz is Gaussian-integral
exactly when the real and imaginary parts of Dz lie in L, because D is a
Gaussian unit diagonal. Therefore Fz=Hz on every Gaussian-integer input
whose ideal image is already integral. The author verifier checks this zero fiber explicitly; it is an additional
exactness property of the published table.

## 8. Scope and execution record

`python -I -B research/four-axis-exact-square-grid/review_lift.py` and its
`-O` counterpart passed. They check the independent tensor/rational lattice
derivation, exact B-action, parity ranks, predecessor lower-bound matrix
ranks, and complementary-coordinate phase. The retained checker does not
claim to replace the separate complete finite transition replay.

The lead's separate finite verifier passed the four conditions in Section 5
on the same pinned table. Combining those exact finite checks with the
derivation above, I find no gap in the claimed
all-integer map, exact square, inverse, error, weighted-sum, or global unit
phase argument. The map is not proved nearest-point or norm-inward. No
all-size multiplication bound, native graph flatness, compiler admission,
or kappa improvement follows merely from this finite block identity.

The 32 KiB number is the logical payload of 4096*16 signed four-bit entries;
the compressed certificate is 26,889 bytes. A fast Walsh implementation uses 160
real additions/subtractions and 32 divisions by four for the two transforms
and correction additions. Classifier arithmetic, lookup addressing, signs,
storage, source access and movement are additional work. Those operations
need a complete invoice before integration into a multiplication caller.
