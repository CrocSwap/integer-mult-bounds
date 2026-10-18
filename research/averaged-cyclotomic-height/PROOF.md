# Averaged coefficient heights for the prime-power cyclic inverse

Theorem and proof, 2026-10-13. This is a new derivation on top of
PR621's nonzero resultant and Bezout argument. It is not a new kappa,
a full transform, or a common-label implementation. The finite scripts
check examples and arithmetic; the argument below supplies the universal
claim. No independent human review or formal verification is claimed.

Let r>=3 be a prime power, n=r-1, D=phi(r), zeta=exp(2 pi i/r), and

    f_k(z) = sum_(j=0)^n a_(k,j) z^j,
    a_(k,j) = product_(s=j+1)^n (1-zeta^(ks)),
    H_k = sum_j |a_(k,j)|,

where k ranges over the units modulo r. Thus f_k=r P_k, as in PR621.
All logarithms in the analytic argument are natural. Write t=log r.
We prove

    sum_(k unit mod r) log H_k <= D (4t^2+8t+2).                  (1)

The existing proof used H_k<=2^r-1 separately at every embedding.
Using (1) in exactly the same determinant and cofactor argument gives

    |P_k(z)| >= exp[-n D (4t^2+8t+2)] / (2rn),  |z|=1.        (2)

Consequently, with ell=ceil(log2 r),

    d = 1+2ell+n D min(r,8ell^2)

is a valid integer exponent for |P_k(z)|>=2^-d. The minimum retains
PR621's cubic bound at small radices. The new exponent is
O(r phi(r) log^2 r), uniformly in the primitive embedding and circle
point. No average-over-embeddings assumption is imposed on the output.
The original uniform bound and its proof are retained in
[`vendor/pr621/PROOF.md`](vendor/pr621/PROOF.md).

## The discrete logarithm has small Fourier mass

Define L(0)=0 and L(s)=log|1-zeta^s| for 1<=s<r. Use the normalized
discrete Fourier coefficients

    Lhat(h) = (1/r) sum_s L(s) zeta^(-hs).

The cyclotomic product over all nonzero residues gives

    Lhat(0)=log(r)/r.                                         (3)

Put delta=1/r, rho=1-delta, and
Lrho(s)=log|1-rho zeta^s|, including s=0. Its absolutely convergent
Fourier series is

    -sum_(m>=1) rho^m cos(2 pi m s/r)/m.

Aliasing into r residues and the triangle inequality show that the
sum of the moduli of its discrete Fourier coefficients is at most
sum_(m>=1) rho^m/m=-log(1-rho)=log r.

For s!=0, set a_s=|1-zeta^s|. We have

    |1-rho zeta^s|^2/a_s^2 = rho(1+delta^2/(rho a_s^2)).

By the triangle inequality, -log(1-delta)<=delta/rho, and
log(1+x)<=x for x>=0, this gives

    |L(s)-Lrho(s)| <= delta/(2rho)+delta^2/(2rho a_s^2).

The difference can have either sign. Pair s with r-s. Concavity of
sine gives a_s>=4 min(s,r-s)/r, so comparison of the reciprocal-square
tail with its integral yields

    sum_(s=1)^(r-1) a_s^-2
      <= (r^2/8) sum_(j>=1) j^-2 <= r^2/4.

Consequently, since rho>=2/3,

    sum_(s=1)^(r-1) |L(s)-Lrho(s)|
      <= (r-1)delta/(2rho)+delta^2 r^2/(8rho)
       = 1/2+1/(8rho) <=11/16<1.

At s=0 the difference is log r. For any sampled function E, normalization gives
sum_h |Ehat(h)|<=sum_s |E(s)|. Applying this to L-Lrho gives

    sum_h |Lhat(h)| <= 2log r+11/16 <=2log r+1.                (4)

The value at zero is essential: silently omitting its correction would
undercharge the Fourier mass. We never evaluate L(0) in a coefficient
product; it is only a convenient finite Fourier extension.

## Average a geometric-sum bound over units

Fix h!=0 modulo r and put d0=r/gcd(h,r). For any interval I of
consecutive integers, and any unit k modulo r,

    |sum_(s in I) zeta^(hks)| <= 2/|1-zeta^(hk)|.

As k ranges over the units modulo r, zeta^(hk) ranges uniformly over
the primitive d0-th roots. This follows from the surjection of the
unit groups for prime-power moduli, followed by multiplication by
h/gcd(h,r), a unit modulo d0. The fibers have equal size. In particular
d0 is a prime power and d0/phi(d0)<=2, including d0=2.

Pairing j with d0-j and using sin(pi j/d0)>=2j/d0 for
1<=j<=floor(d0/2) gives

    sum_(j=1)^(d0-1) 1/sin(pi j/d0)
        <= d0 H_floor(d0/2) <= d0 (1+log d0).

The middle term is overcounted when d0 is even, which is harmless.
Hence the average over primitive k of the geometric-sum bound is
at most 2(1+log r). This bound holds simultaneously for every I;
the right-hand side for each k does not depend on I.

Let M_k be the maximum of zero and all logarithms log|a_(k,j)|.
Fourier inversion, (3), and the triangle inequality give the pointwise
upper bound

    M_k <= log r + sum_(h=1)^(r-1) |Lhat(h)| 2/|1-zeta^(hk)|.

Average this inequality and apply (4). Because H_k<=r exp(M_k),

    average_k log H_k
      <= 2log r+2(2log r+1)(1+log r)
       = 4t^2+8t+2,

which is (1). This averages an upper bound on the maximum; it does
not exchange an average and a maximum.

## Resultant and cofactor cancellation

Use PR621's Sylvester matrix for f and its conjugate reciprocal f*.
Let R be its determinant in Q(zeta). The prime-power ideal argument
from that proof establishes R!=0. For each embedding k, every
column has Euclidean norm at most H_k, so |R_k|<=H_k^(2n).
The chosen embedding and its complex conjugate have the same H and
the same |R|; they are distinct since r>=3. The nonzero algebraic
integer norm therefore gives

    |R| >= product_(k excluding chosen pair) H_k^(-n).

The coefficients of the two Bezout polynomials are cofactors. Each
cofactor at the chosen embedding has modulus at most H^(2n-1).
For |z|=1, |f*(z)|=|f(z)|, so

    |P(z)| >= |R|/[2rn H^(2n-1)]
            >= H/[2rn product_(all k) H_k^n]
            >= 1/[2rn product_(all k) H_k^n].                 (5)

Here H>=1 because f is monic. The local cofactor powers cancel the
two removed embeddings exactly, leaving a favorable numerator H.
Equation (1) now proves (2). No rationality or Galois invariance of R
is assumed; such invariance is false already at r=5.

## Dyadic exponent and inherited precision budgets

Since 2/3<log 2<3/4 and t<=ell log 2,

    (4t^2+8t+2)/log 2 <=3ell^2+8ell+3 <=8ell^2.

For ell>=2 the second difference is
5ell^2-8ell-3=1+12(ell-2)+5(ell-2)^2>=0. Also
2rn<=2^(1+2ell). These inequalities prove the displayed d.

PR862's perturbation and partial-inverse estimates, and PR977's
effective-depth stride theorem, use the circle theorem only through
d. Set T=n D min(r,8ell^2) and use their unchanged definitions:

    d=1+2ell+T, a0=2d+r+2, g=d+ell+2r+2, h=a0+2r,
    c=ceil(log2(r-1)),
    e=max(d+1,a0+1,p+2a0+m+3), b=max((r-1)ell,e+r+3),
    J=c+2h+3g+ell+m+5, W=p+J+2, G=m+ell+h+g+8.

In particular, PR621's Fourier inverse estimate with the unchanged
coefficient bound H=2^r-1 gives ||P(U)^-1||<=2^a0. The bound applies
to every isometry with ||U^j||=1 for all integer j, by the absolutely
convergent Laurent series argument retained in PR862. This includes
arbitrary-stride cyclic unit shifts. The inherited proofs are retained
as [`vendor/pr862/PROOF.md`](vendor/pr862/PROOF.md) and
[`vendor/pr977/PROOF.md`](vendor/pr977/PROOF.md).

Here p,m>=0, input infinity norm is <=2^m, and target error is
2^-p. Direct substitution gives

    W=p+m+7T+12r+18ell+c+24,
    G=m+3T+5r+8ell+15,
    b=p+m+4T+3r+8ell+14.

The last equality follows because p+2a0+m+3 dominates the other e
terms, and its resulting b term exceeds (r-1)ell. For the latter,
d>=n D min(r,8ell^2)>=n ell: D>=1, r>=ell and
8ell^2>=ell. With N=r^2 ell^2, T<=8N and r>=3, ell>=2,
ell<=r, N>=12r, these give convenient universal bounds

    W<=p+m+60N, G<=m+26N, b<=p+m+34N.

For example, the non-T W terms are <=31r+24<=39r<4N;
the G terms are <=13r+15<=18r<2N; the b terms are
<=11r+14<=16r<2N. All previous cubic bounds remain valid because
d did not increase. The admission W>=2g+8 and the common-error
contraction exponents remain unchanged algebraically. Thus the
existing clean-scratch arbitrary-stride solver has the same 40L
record bound per first-order inverse and an O(r^2 log^2 r) precision
overhead. This statement inherits all phase-oracle, coefficient
preparation, word-size, and clean-workspace charges from PR977;
it is not a new bit-reversible or dirty-array circuit.

## Evidence and attribution

`interval_check.py` uses 192-bit outward-rounded rational enclosures
to check 17 prime-power radices through 32. It checks regularization,
Fourier mass, primitive-character fiber multiplicities, geometric
averages, each pointwise maximum bound before averaging, total averaged
height, and dyadic conversion. A separate exact enclosure at r=4096
proves that the average bound is false if assigned to every embedding
individually. That negative control uses sin(x)<=x and AM-GM, not a
floating-point sample of a large polynomial.

`resultants.py` independently compares SymPy polynomial resultants and
Sylvester determinants with PR621's rational field arithmetic for
r=3,4,5,7,8,9. It checks all Galois conjugates and norms, and rejects
the rational-resultant shortcut explicitly at r=5. The retained unit-root
and missing-conjugation controls are replayed in all six cases.

`budgets.py` checks 752 exact integer budgets, including dyadic orders
through 2^128, the dyadic-conversion polynomial identity and a
rational enclosure of log 2. Those large orders test exponent arithmetic;
no enormous polynomial, array or working word is allocated. No actual
inverse execution at the reduced large-radix precision is claimed.

The full package additionally rejects eleven packaging/receipt faults
and replays from a read-only relocated copy. The finite checks support
specific identities and failure modes. They do not prove the analytic
theorem for all radices; that is the role of the argument above.

The kernel is from the pinned OpenAI exact-DFT preprint, with its
classical Newton and q-Pochhammer provenance retained in PR621's
NOTICE. The ideal/resultant/cofactor proof is retained from Ali
Romman's PR621. The partial-inverse precision framework is retained
from Chafik's PR862; the arbitrary-stride solver is Rohan Guliani's
PR846, with the effective-depth argument in Chafik's PR977. Classical
ingredients here are the logarithm Fourier series, finite Fourier
inversion, geometric sums, cyclotomic embeddings, Hadamard's
inequality, and the algebraic norm. A search found related Sudler
product literature, including [Bence Borda, arXiv:2104.06716](https://arxiv.org/abs/2104.06716), but the
finite rational-unit average above is derived in full and does not
rely on an irrational-rotation theorem. No priority claim is made.

The immutable source objects and notices are retained in `vendor/` and
bound by `SOURCE-PINS.json`. Common-label and bit-reversible compilation,
full-transform normalization and traffic, supplier hosting, and the
multiplication reduction remain open. The new averaged-height estimate
does not discharge those obligations.
