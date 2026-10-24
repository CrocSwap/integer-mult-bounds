# Independent numerical error bound for the native radix-two FFT

Prepared by Dugongue with substantial OpenAI Codex assistance. Apache-2.0.
This argument is independent of the transform's arithmetic implementation.
It uses no TM computation or simulation.

## Assumptions and norms

Let N=2^h>=2 and let each input coefficient have complex modulus at most beta,
beta>=1. The exact forward and inverse butterflies are unnormalized, with
true twiddles of modulus one. The inverse is divided by N once at the end.
Let S=2^F. Suppose every supplied approximate twiddle differs from its true
value by at most rho=16N/S in each real/imaginary coordinate. Suppose each
complex multiplication's local fixed-grid rounding contributes at most 2/S
in each coordinate. Addition/subtraction at the common grid is exact, and
all actual word operations satisfy their no-overflow bounds.

Use complex modulus for this proof, and the maximum such modulus over an array.
The twiddle error is then at most delta=32N/S; every local multiplication or
final normalization rounding can be bounded by eta=4/S. Assume delta<=1 and
eta<=1; the final parameters below easily imply both. Conjugation of twiddles
for the inverse preserves these error bounds.

## One forward transform

If A_j bounds the approximate data modulus after j stages, then

    A_(j+1) <= (2+delta) A_j + eta <= 4 A_j + eta.

Since A_0<=beta, induction gives

    A_j <= 4^j(beta+eta/3) <= 2*4^j beta,
    A_h <= 2N^2 beta.

Let E_j be the error from the exact partial FFT. Subtract exact and approximate
butterflies, assigning the twiddle discrepancy to the approximate second input:

    E_(j+1) <= 2 E_j + delta A_j + eta,    E_0=0.

The elementary sum

    sum_(j=0)^(h-1) 2^(h-1-j) 4^j = N(N-1)/2

therefore gives

    E_h <= delta beta N(N-1) + eta(N-1)
        <= 36N^3 beta/S.                                      (1)

The exact forward data modulus is at most N beta. The same bounds hold for the
other operand's independent forward transform.

## Pointwise product

Let A,B be the exact forward arrays and Ahat,Bhat the computed arrays. A rounded
pointwise product has error

    |round(Ahat*Bhat)-A*B|
      <= |Ahat-A| |Bhat| + |A| |Bhat-B| + eta
      <= (36N^3 beta/S)(2N^2 beta + N beta) + eta
      <= 112N^5 beta^2/S.                                    (2)

The computed product modulus is at most

    (2N^2 beta)^2 + eta <= 5N^4 beta^2.                        (3)

No independence, random error cancellation or favorable data signs are used.

## Inverse transform and normalization

Applying the same amplitude recurrence to the approximate product input gives
an inverse-stage amplitude bound

    A'_j <= 6*4^j N^4 beta^2.

The inverse error recurrence now starts with (2), rather than zero. Thus

    E'_h <= N*(112N^5 beta^2/S)
            + delta*6N^4 beta^2*N(N-1)/2 + eta(N-1)
          <= 212N^7 beta^2/S.

Division by the exact integer N scales this preexisting error by 1/N. Its own
fixed-grid coordinate rounding contributes at most eta in complex modulus.
Consequently every normalized output coefficient has error at most

    216N^6 beta^2/S.                                         (4)

In particular, the more conservative requested envelope is valid:

    error <= 2^28 N^8 (F+1)^2 beta^4/S.                       (5)

Indeed N>=1, beta>=1 and F+1>=1, while 216<2^28. The factors (F+1)^2 are not
needed for this independent estimate; retaining them safely accommodates the
stated caller ledger. They must not stand in for an unproved twiddle or local
rounding premise.

## Parameters imply strict recovery error below 1/4

Let n>=1,

    ell = bitlength(n+2),
    b = max(1,floor(ell/8)),
    beta = 2^b,
    N = least power of two >= 2ceil(n/b),
    F = 24ell+64,  S=2^F.

Then ell>=2, b<=ell, and

    N < 4ceil(n/b) <= 4n < 2^(ell+2),
    beta^4 <= 2^(4ell).

The first inequality is the ordinary bound on rounding a positive integer up
to a power of two. Also

    F+1=24ell+65 <= 2^(ell+7).

For ell=2 the inequality is immediate; increasing ell by one adds only 24 to
the left while doubling the right, and the previous left side is already at
least 24. Substitute these bounds in (5):

    2^28 N^8(F+1)^2 beta^4/S
      < 2^[28+8(ell+2)+2(ell+7)+4ell-(24ell+64)]
      = 2^(-10ell-6)
      <= 2^-26 < 1/4.

The same parameter inequalities imply delta=32N/S<1 and eta=4/S<1, discharging
the earlier stability conditions. The empty-input case n=0 should be returned
as zero directly, rather than introducing an unnecessary FFT convention.

For zero-padded nonnegative digit arrays, N>=2ceil(n/b) prevents cyclic wrap
in the linear convolution. The exact normalized inverse coefficients are real
integers. Equation (5) therefore places each computed real coordinate strictly
within 1/4 of the right integer, and nearest-integer recovery is exact. The
linear carry theorem in ROOTS-RECOVERY.md then produces the exact product.

## Word-size sanity bound

The approximate inverse data modulus before normalization is at most
6N^6 beta^2. On the F-bit grid its signed integer coordinates have magnitude
at most 6S N^6 beta^2. Twiddle coordinates have magnitude at most 2S. A raw
real multiplication used in a complex multiply is consequently bounded by
12S^2 N^6 beta^2, and a constant additional factor covers combining two such
products. Thus a sufficient magnitude width is

    2F + 6ceil(log2 N) + 2b + 8,

plus caller addresses and a sign representation. This is O(log n) for the
chosen F. The independently generated root seed uses an even larger fixed
constant times F for its internal precision; one common global word width
must cover both stages. Allowing each subroutine an unaccounted private wider
word would not establish a single Word RAM implementation.

## Scope

This establishes numerical sufficiency for an actually implemented iterative
FFT whose twiddles, local rounding and word bounds meet the hypotheses. It does
not verify an arbitrary FFT routine by observing good samples, or prove that
an unrelated power-saving transform inherits these polynomial prefix norms.
The native implementation and its exact operation ledger remain separately
reviewable. No improved TM exponent or formal Lean proof is claimed.
