# Signed packed convolution: exact scalar obligation

This is an elementary written proof of the arithmetic primitive in PR #489,
not a machine-checked proof, a Gaussian inverse theorem, or a tape-cost proof.
The source is `code/branchfree.py` at
`8922e3b3f0fd7772b0fb42028eb2532984c3ab42`. The finite checker is separate
supporting evidence and does not establish the universal quantifiers below.

## Statement and domain

Let n >= 1, b >= 0 be integers, S = 2^b, and let H and X be arbitrary
length-n integer vectors. The primitive receives h_j = H_j/S and
x_j = X_j/S. Write trunc(z) for rounding a real number toward zero to an
integer. For every retained coefficient 0 <= i < n, the claimed result is

    y_i = trunc((sum_{j=0}^i H_(i-j) X_j)/S) / S.

Equivalently this is one completed-coordinate rounding of T(h)x to the
b-fractional-bit grid. There is no Gaussian-form assumption on H, no sign
restriction, and no magnitude restriction in this arithmetic statement.
The inputs are nonempty and on the specified grid. The inherited function
uses assertions for length and grid admission; this checker refuses -O.
No claim is made for empty vectors, negative b, off-grid data or malformed
counter dictionaries.

## Carry invariant, including zero inputs

Put Hmax = max |H_j|, Xmax = max |X_j|, M = n Hmax Xmax. The source selects

    w = max(1, bit_length(M) + 1), B = 2^w.

If M = 0, one entire vector is zero. Both packed integers for that vector
are zero, all four products are zero, and the claimed output follows.
This case matters: a digit in the *other* packed operand may then exceed B,
but it multiplies zero, so a digit-bound assumption is unnecessary.

Suppose M > 0. Then Hmax, Xmax <= M, and M < B. Split every integer A into
A+ = max(A,0), A- = max(-A,0), so A = A+ - A-. For each choice of signs,
form a nonnegative packed integer sum_j A_j^sign B^j. Multiplying two
such integers gives, by distributivity, a polynomial evaluated at B.
Every coefficient is a sum of at most n nonnegative terms, each at most
Hmax Xmax. Thus every coefficient, including the non-retained tail, is
between zero and M, strictly below B.

Consequently the base-B digits are exactly those polynomial coefficients:
there is no inter-slot carry. `(product >> (w*i)) & (B-1)` extracts the
coefficient of degree i. Higher degrees cannot affect the retained lower
ones. Extracting each of the four nonnegative products BEFORE signed
recombination yields

    C++_i + C--_i - C+-_i - C-+_i
      = sum_{j=0}^i H_(i-j) X_j.

Subtracting signed packed integers before extraction would require a
different borrow analysis; that is not what the source does.

## One final rounding, not four partial roundings

Each input had denominator S, so the exact coefficient has denominator
S^2. Rounding c/S^2 toward zero to the 1/S grid yields
trunc(c/S)/S, exactly the independent integer-dot-product oracle.
Reducing the Fraction representation does not alter this value. Each
coordinate's absolute rounding error is less than 1/S, including negative
coordinates and exact zero. A coefficient divisible by S has zero error.

Rounding individual nonnegative products before their signed cancellation
is not equivalent. For b=1, H=(1,1), X=(1,-2), the coefficient of degree
one is -1/4 and rounds to zero. Separately rounding the positive 1/4 and
negative contribution -2/4 gives -1/2. The mutant in EXPECTED.json executes
this alteration and is rejected by the independent oracle.

## Upper triangular orientation

Let R reverse a length-n vector. The source upper-stage convention is
R T(h) R; it reverses input and output, NOT h. At output i it gives

    sum_{j=i}^{n-1} h_(j-i) x_j,

by substituting j = n-1-k in the lower sum at n-1-i. Coordinatewise
rounding commutes with reversal. The independent upper oracle directly
sums these terms and never uses R. Its two wrapper mutations omit the
output reversal or incorrectly reverse h; both produce concrete wrong
answers. The checker exercises this wrapper around the pinned primitive,
not the complete seven-step `apply` program.

## What the finite evidence adds

The original PR's rounded Gaussian cases compare packed products to a
Fraction dense sum for its prepared h tables. This audit instead works in
integer-grid numerators, using a direct dot product and divmod, with a
complete declared finite input domain and non-Gaussian adversarial vectors.
Its oracle imports none of `rounded`, `factors`, `prepare`, `apply`, or the
source's `bits=None` path. The source function under test is retained
verbatim and checked against both SHA256 and Git blob pins before and after
execution. Full deterministic receipts are compared, not only a PASS flag.

The result corroborates the signed-packing primitive and its reversal
convention. It does not discharge q-Gaussian factorization, approximation of
the independently rounded/truncated old matrix, Schur composition, weighted
tensor precision, all-size layout, host operations, or multiplication's
analytic transfer. It leaves the selected conditional kappa unchanged.
