# Uniform preparation and rounded inversion of a neighboring cyclic kernel

This note combines PR621's circle lower bound, standard approximate
factorization, and the local two-scan rounding lemma. It concerns a
neighboring cyclic shift with gauge 1 and clean input/output work arrays.
It is not a complete multiplication algorithm, reversible word, arbitrary
stride tape schedule, or new kappa result. The proof uses the cited
factorization theorem; the accompanying numerical nomination program does
not implement that theorem's worst-case algorithm.

## Statement and model

Let r>=3 be a prime power, k coprime to r, zeta=exp(2 pi i k/r), and

    P(z)=sum_(j=0)^(r-1) h_j z^j,
    h_j=1/product_(s=1)^j(1-zeta^s).

Let S be either neighboring cyclic shift on L>=1 entries. Given p>=1
and an exactly supplied dyadic complex vector x with ||x||infinity<=1,
there is an algorithm producing y with

    ||y-P(S)^-1 x||infinity <= 2^-p.

Coefficient preparation is independent of L. Both the required coefficient
bit lengths and the execution precision are O(p+r^4), including magnitude
bits. The array execution uses O(rL) rounded scalar operations and O(r)
sequential full-array passes. With ordinary near-linear integer arithmetic,
including a conservative exact coefficient-product verification in setup,
the bit-operation bound is

    soft-O((Lr+r^3)(p+r^4)).

Here soft-O suppresses logarithms in the displayed parameters. Input
fractional precision is assumed at most the execution budget below;
longer exact inputs require their reading/rounding cost and a separately
charged input-error budget. Clean arrays and standard arithmetic scratch
are allowed. The scan layout is sequential for S=Z or Z^-1; this statement
does not assert that an arbitrary modular-stride permutation is free.
The setup bound uses the bit-complexity model of the cited factorization
result. A concrete fixed-tape implementation of its setup is not supplied.

## Explicit budgets

Put n=r-1, D=phi(r), ell=ceil(log2 r), and

    d=1+2 ell+r n D,
    g=d+ell+2r+2,              beta=2^-g,
    a=ell+n g,                Abar=2^a,
    e=max(d+1, a+1, p+2a+3), epsilon=2^-e,
    b=max(n ell, e+r+3),
    w=max(2g+ceil(log2(14n)),
          p+(n+2)g+ceil(log2(28n(r+1)))), u=2^-w.

All these are computable integer budgets. Their sizes satisfy
d,g=O(r^3) and a,e,b,w=O(p+r^4). No array length occurs in them.
The executable budget checker verifies the integer inequalities used below
for a range of radices and precisions; the algebra proves them generally.

## Approximate factorization and preparation

Define f=rP. Its leading coefficient is 1 and its coefficients are

    f_j=product_(s=j+1)^(r-1)(1-zeta^s).

Thus ||f||_1<=H=2^r-1, and Cauchy's bound places all roots inside
|z|<=1+H<2^(r+1). Its logarithmic root bound is O(r).

Pan's approximate-factorization theorem, in Theorem 2 and Corollary 1 of
Mehlhorn, Sagraloff and Wang [1], provides dyadics rho_1,...,rho_n with
||f-product_j(z-rho_j)||_1<=2^-b ||f||_1. Its factorization cost is
soft-O(n b+n^2 Gamma), with coefficient-oracle precision O(b+n Gamma),
where Gamma bounds the logarithmic root magnitudes. Repeated roots do not
require a distinct-root count for this factorization step.

Let Q=(1/r) product_j(z-rho_j). Our choice b>=e+r+3 gives

    ||P-Q||_1 < epsilon/8.

Only this coefficient error is needed. We do not isolate the true roots,
match approximate roots to true roots, or require simple roots.

The coefficient oracle is also charged. Compute zeta to the requested
precision, its first r powers, and the backward products defining f_j.
There are O(r) complex operations. Products have magnitude at most 2^r;
guarding by O(r+log r) bits bounds coefficient errors. Fast elementary
function evaluation [2] supplies the required pi, sine and cosine values
with near-linear precision cost up to logarithms. Hence the oracle fits
soft-O(r(p+r^4)). This is an algorithmic preparation argument, not a
complexity claim about the Fraction/Decimal reference scripts.

An independent certificate can expand the dyadic-root product exactly and
compare it with rigorous coefficient enclosures of total componentwise
error at most epsilon/8. Replacing complex moduli by the sum of absolute
real and imaginary parts costs at most a factor of 2, so the resulting
upper bound is still below epsilon. Exact expansion
of n B-bit roots has O(nB)-bit coefficients; a simple iterative expansion
costs soft-O(n^3 B) bit operations, B=O(p+r^4). This conservative setup
cost is included in the theorem. Faster expansion is unnecessary here.

## Stability without individual root certification

PR621 gives |P(z)|>=delta on |z|=1, where

    delta=1/[2rn H^(nD-1)] >= 2^-d.

The coefficient certificate and e>=d+1 imply |Q(z)|>=delta/2 on the
unit circle. Also ||Q||_1<=H/r+epsilon<=H/r+1<=2^r.

For any root rho of Q at radial distance t=||rho|-1|<1/2, integrate Q'
along the radial segment to the unit circle. On that segment |z|<2, so

    delta/2 <= t n 2^r 2^(n-1).

Roots farther than 1/2 already have a fixed gap. Therefore every root of
Q lies at radial distance at least

    eta=min(1/2, delta/[2n 2^r 2^(n-1)]).

Our g ensures beta<=eta/2. If |rho|>1, b_rho=1/rho has modulus at most
1-beta. If |rho|<1, b_rho=rho has modulus at most 1-beta. These comparisons
can be made exactly on the dyadic rho. Inverting an outer rho produces
an exact rational complex coefficient with O(p+r^4) numerator and
denominator bits; it need not be rounded to a dyadic.

For each factor,

    (S-rho I)^-1 = -rho^-1 (I-rho^-1 S)^-1       if |rho|>1,
    (S-rho I)^-1 = (I-rho S^-1)^-1 S^-1          if |rho|<1.

Each stable inverse has norm at most beta^-1. Outer scalar factors have
modulus less than 1, while the inner shift has norm 1. Apply the scalar r
to the input first. Exact stage-j values have norm at most r beta^-j.
In particular, ||Q(S)^-1||<=r beta^-n<=Abar, uniformly in L.

Since epsilon Abar<=1/2, a Neumann perturbation bound gives

    ||P(S)^-1-Q(S)^-1||
       <= Abar^2 epsilon/(1-Abar epsilon)
       <= 2 Abar^2 epsilon <= 2^(-p-2).

This is an operator bound for arbitrary input vectors, not just samples
or a particular Fourier mode.

## Rounded execution

Use the two-scan periodic first-order procedure proved in
SCAN-PROOF.md, with grid u and exact rational coefficients.
An inner factor scans in the opposite direction and includes the unit
cyclic shift. An outer factor includes a final rounded multiplication by
-rho^-1. The per-factor error is bounded by

    7(B+1)u/beta^3

for input norm B. The constant 7 includes the outer scalar multiplication;
the original scan constant is 6. Copying and shifting dyadic entries is
exact. Multiplying the original dyadic input by integer r is exact.

If E_j is the error after j factors, then E_0=0 and

    E_j <= E_(j-1)/beta
           +7(r beta^(-(j-1))+E_(j-1)+1)u/beta^3.

Set T_j=beta^j E_j. Since beta<=1 and j>=1,

    T_j <= (1+7u/beta^2)T_(j-1)+7(r+1)u/beta^2.

The budget u<=beta^2/(14n) implies
(1+7u/beta^2)^n<=exp(1/2)<2. Consequently

    E_n <= 14n(r+1)u beta^(-(n+2)) <= 2^(-p-1).

Adding the factorization perturbation yields at most 3*2^(-p-2)<2^-p.
All scan intermediates have O(p+r^4) bits including integer magnitude.
In particular, b_rho^L is accumulated with rounding at every step, so its
representation does not grow with L. The closure denominator stays at
least beta/2, by the single-factor proof.

Exact rational multiply/add followed by dyadic rounding and the one
closure division use integers of O(p+r^4) bits. Standard fast integer
multiplication and division give the stated scalar bit cost. A bounded
number of sequential passes suffices per factor, including rewinds and
the unit cyclic rotation. Two alternating clean data arrays suffice for
the streaming values. A conservative space allowance is
soft-O((L+r^2)(p+r^4)) bits, including setup and arithmetic scratch.

## Paid unit phases

The same factor certificate works for U=tau S when tau is an exactly
supplied rational complex number of modulus 1. In an outer factor, the
scan coefficient becomes tau/rho and the final scalar remains -1/rho.
In an inner factor, it becomes rho/tau; after the backward scan and unit
shift, multiply by tau^-1. Both new coefficients retain the same margin
beta. The inner scalar has modulus 1, so the same constant 7 covers its
rounded multiplication. If tau has T representation bits, scalar
arithmetic costs use O(p+r^4+T)-bit operands; T is not silently free.

More generally suppose a unit tau has a charged approximation oracle.
Choose a rational unit sigma with |tau-sigma|<=nu, where

    nu <= epsilon/(n 2^r).

Then ||P(tau S)-Q(sigma S)||<=epsilon+n||Q||_1 nu<=2 epsilon.
Because e>=p+2a+3, we still have 2 epsilon Abar<=1/2 and

    ||P(tau S)^-1-Q(sigma S)^-1||
      <=4 Abar^2 epsilon<=2^(-p-1).

The same rounded execution budget contributes at most 2^(-p-1), giving
the original target 2^-p. The phase needs O(p+r^4) approximation bits,
in addition to reading whatever representation defines it.

Here is a constructive way to obtain sigma with exact unit modulus.
Choose C in {1,-1,i,-i} so v=C^-1 tau has Re(v)>=1/2. A coarse enclosure
suffices to choose such a chart: one coordinate of a unit vector has
absolute value at least 1/sqrt(2). Put t=Im(v)/(1+Re(v)). Its denominator
is at least 3/2. Approximate t by a dyadic t0 with |t-t0|<=nu/2 and set

    sigma=C (1-t0^2+2i t0)/(1+t0^2).

This is exactly rational and unit. The stereographic map's derivative
has modulus 2/(1+t^2)<=2, proving |tau-sigma|<=nu. Obtaining t0 costs
the oracle request plus scalar arithmetic at the stated precision.
For a phase exp(2 pi i h/m), [2] supplies that oracle after the cost of
reading/reducing the integer phase description; a very long h or m is
an extra input cost and is not covered by a bound that omits its length.

This section treats a single constant unit phase. WEIGHTED-PROOF.md
extends the same bounds to a unit-weighted neighboring shift with an
independent phase at each position. The full transform's collection of
phases still needs its composition and preparation accounting.

## Scope and finite evidence

For r bounded by a fixed power of log p, the cost is quasi-linear in p
up to polylogarithmic factors and polynomial dependence on that radix.
There is no extra factor proportional to p in the number of full-array
passes. This removes the repeated-Neumann-pass obstruction for this
neighboring, clean-array inverse primitive.

The mixed-factor reference certificate at CERTIFICATE-PROOF.md checks
ten kernel/embedding cases through radix 16, including inner roots, exact
rational unit phases, and a certified rational approximation of
exp(2 pi i/7). It uses exact coefficient enclosures, exact factor products,
and an explicit rounding budget. These finite certificates do not implement Pan's
worst-case factorizer or prove its complexity. The uniform argument above
depends on [1], [2], PR621, and the proved scan lemma.

Remaining work for a multiplication application includes the complete
collection of phase gauges and their paid preparation, the actual strides/layout of every kernel,
composition across the complete transform and recursion, its total
precision guard, input/output normalization, and restoration of dirty
scratch where required. None is inferred from this standalone theorem.

## Sources and attribution

[1] K. Mehlhorn, M. Sagraloff, P. Wang, *From Approximate Factorization to
Root Isolation with Application to Cylindrical Algebraic Decomposition*,
Theorem 2 and Corollary 1 (crediting V. Pan),
https://arxiv.org/pdf/1301.4870, PDF page 8.

[2] R. P. Brent, *Fast multiple-precision evaluation of elementary
functions*, J. ACM 23 (1976), 242-251,
https://maths-people.anu.edu.au/~brent/pub/pub034.html.

PR621 by aliromman, head 520774462b19b29af41554b74def31f9d01e997e,
supplies the kernel and circle bound. Causal/anticausal filtering and
approximate factorization are standard methods. The explicit budget
composition and reference certificates here were prepared with OpenAI
Codex for chafreaky. No literature-priority claim is made.
