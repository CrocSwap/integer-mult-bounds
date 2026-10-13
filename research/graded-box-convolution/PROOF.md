# A carry-count grade for box-truncated convolution

This removes the exponential **slot-padding factor** in the previous recentered
Gaussian fixture. It does not establish a fast tape implementation, certified
transcendental setup, a complete tensor Schur solve or any new kappa.

Let the box have positive axis lengths `n_0,...,n_(D-1)`, with `D>=1`, and let
`N=product n_i`. Put `P_0=1`, `P_(i+1)=n_i P_i`, and encode a coordinate by
`I(a)=sum a_i P_i`. Set `T=D` and choose residues modulo T by

    w_0=1,    w_(i+1)=n_i w_i-1 (mod T).
    g(a)=sum w_i a_i (mod T), represented in {0,...,T-1}.

For D=1 the sole residue is zero. Axes of length one are allowed.

## Exact carry filter

Take two box coordinates a,b whose ordinary encoded sum is less than N. Let
c be the mixed-radix coordinate of `I(a)+I(b)`. The usual carries satisfy

    a_i+b_i+e_(i-1)=c_i+n_i e_i,
    e_(-1)=e_(D-1)=0,    e_i in {0,1}.

The last carry is zero because the encoded sum is below N. Multiplying by w_i,
summing and using the defining recurrence gives

    g(a)+g(b)-g(c) = sum_(i=0)^(D-2) e_i (mod T).

The sum on the right lies between zero and D-1. Therefore grades agree exactly
when every carry is zero. This is equivalent to componentwise `a+b=c` inside
the box. In particular, flattened products with an internal digit overflow are
excluded without padding each axis separately. This proof also covers radix one:
a carry can pass through that axis, and is still counted positively.

## Four actual signed integer products

Let `X=2N-1` and assign input coordinate a the slot

    J(a)=I(a)+X*g(a).

An ordinary product of two packed coefficient polynomials cannot carry its
index into the grade digit: the sum of two indices is at most `2N-2<X`.
For output c, add the product coefficients in slots

    I(c)+X*g(c),
    I(c)+X*(g(c)+T), if g(c)+T <= 2T-2.

These are exactly the two possible sums of the input grade residues congruent
to g(c). The carry-filter identity proves that the resulting coefficient is

    h(c)=sum_(a+b=c componentwise) f(a) q(b).

Ordinary index sums at least N never match an output index, so a final overflow
cannot be mistaken for a grade carry. Dropping the one-dimensional index padding
is unsafe; the verifier rejects that variant.

For signed integer coefficients, pack positive and negative parts separately
and form `f+q+ + f-q- - f+q- - f-q+`. This is four integer products. If input
magnitudes are bounded by A and B, every individual nonnegative packed-product
coefficient is at most `N*A*B`: for each first index there is at most one second
index with a specified encoded sum. A binary slot width strictly above
`log2(N*A*B)` prevents integer carries between coefficient slots.

The maximum input slot is at most

    (N-1)+(2N-1)(D-1).

Thus a whole product occupies fewer than `4DN` coefficient slots. With P-bit
input coefficients the operand length is `O(DN*(P+log N))`. This is a bound on
representation size and an exact reduction to four integer products. It does
not make packing, extraction, permutation or those integer products free, and
it is not a noncircular multiplication-time theorem.

## Application to the existing recentered weighted fixtures

Use the previous local recentering identity and its unchanged rounded kernel,
residual weights and predivision. Replace only the tensor convolution layout by
the carry-filter packing. Upper triangular convolution reflects input and output
coordinates. The integer convolution is exact, so the previous per-entry
rounding bound remains unchanged:

    Emax * [N*(H*eta + eta/Emin + eta^2) + eta] + eta,
    H=(15/14)^D, eta=2^(-P), |input|<=1.

No extra approximate transform or cancellation stage is introduced. The finite
weighted cases use the earlier rational analogue, not certified transcendental
tables for every admissible phase cell.

For the previously exhibited family

    a>=26, p=2^(10a), D=2^(4a)-1, k=2^(3a-11), n_i=k+1,

the old independent-axis padding had ratio at least `(3/2)^D`, hence greater
than `2^(D/2)`. The new product-slot ratio is below `4D < 4*p^(2/5)`.
This replaces that specific exponential representation overhead by a polynomial
one, including ragged boxes because the grade recurrence permits unequal radices.
It does not pay for the number of recentering tiles, cross-tile interactions,
phase-cell routing, tensor Schur boundaries, table construction or the remaining
dimension-dependent exposure in the outer argument.

## Evidence and attribution

The executable verifies the carry identity on all below-N input-index pairs
for nine shapes, compares actual signed integer products against independent
quadratic convolution oracles, and tests larger separable inputs against the
product of one-dimensional convolution oracles. Eight weighted cases check
every basis vector and two signed dense vectors at 32 and 64 fractional bits,
in both orientations. Five invalid layout/sign controls must fail.

Rank-filtered convolution is established prior work: Bjorklund, Husfeldt, Kaski
and Koivisto, [Fourier meets Mobius](https://arxiv.org/abs/cs/0611101), and Stoian,
[Did Fourier Really Meet Mobius?](https://arxiv.org/abs/2404.18522). The latter
filters binary sequence convolutions by subset cardinality. Here we give the
mixed-radix carry-count recurrence and an exact integer-packing implementation
for the rectangular weighted fixture. No global originality claim is made.
The Gaussian factorization and its unresolved all-size conditions come from
PR489 at 8922e3b3f0fd7772b0fb42028eb2532984c3ab42.
