# A smaller arithmetic width for once-rounded rational gates

This scoped construction and proof were produced by Nick Petalas. Apache-2.0.

## Statement

Let B>=2 and C>=1 be integers. Four signed input grid numerators X_j satisfy

    -2^(B-1) <= X_j < 2^(B-1),  0<=j<4.

A rational row has coefficients p_j/d_j, with integer p_j and d_j such that

    |p_j| < 2^C,  1 <= d_j < 2^C.

The coefficients need not be reduced. There is a constant-word arithmetic
program that computes

    floor(sum_j (p_j/d_j) X_j + 1/2)

with every signed data-arithmetic temporary fitting

    W = B + 4C + 2 bits.                                      (1)

The program uses shifts, bit tests, addition, subtraction and comparisons.
Multiplication and division below are implemented by bounded binary loops.
They are not assumed machine instructions. Four applications to saved inputs
implement any two-coordinate Gaussian rational matrix gate, rounding each
real and imaginary output once with ties toward positive infinity.

This is an upper bound, not a minimum-width theorem. It concerns arithmetic
words after coefficients and input data are supplied. No reversible circuit,
bit-tape running time, memory layout or coefficient-preparation bound follows.

## Common-denominator accumulation

Set

    D = product_j d_j,
    N_j = p_j X_j product_(k!=j) d_k,
    S = sum_j N_j.

Compute D by four successive products starting from one. Compute each N_j
from p_j X_j and then the three other denominators. Accumulate its exact
integer value before proceeding to the next term. No product is rounded.

We have

    1 <= D < 2^(4C),
    |N_j| < 2^(B+4C-1),
    |sum_(j in J) N_j| < 4 * 2^(B+4C-1) = 2^(W-1)           (2)

for every partial sum occurring in this fixed four-term order. The bound
uses |X_j|<=2^(B-1), including the most negative B-bit input. Strictness
comes from the four coefficient numerator/denominator factors, each strictly
below 2^C. Signs and cancellation are unrestricted.

Each nonzero partial product has magnitude at most the corresponding full
product: every remaining denominator is at least one. A zero numerator
remains zero. All these intermediate values fit (1), by (2). D and its
partial products fit as well. The exact rational row value is S/D.

For signed multiplication, retain the result sign and use unsigned
magnitudes. Scan the multiplier's binary digits from low to high, adding
the shifted multiplicand when a digit is one. Every shifted multiplicand
and every partial sum is at most the full magnitude product. Hence the
same word bound applies to the shift/add implementation, including its
positive magnitude words. None of these constructed products is the most
negative W-bit integer, so taking its absolute value is safe.

## Division and signed ties

Put t=|S|. Binary long division scans exactly W-1 positions of t, from
most significant to least significant. Maintain a quotient prefix q and
remainder r. At each position with digit b, replace

    r by 2r+b,
    q by 2q,
    if r>=D, subtract D from r and add one to q.

The ordinary prefix-division induction proves that the final pair satisfies
t=qD+r and 0<=r<D. Before conditional subtraction, the remainder is below
2D, which is below 2^(4C+1). Since B>=2, this is below 2^(W-1).
Each quotient prefix is at most the final quotient, which is at most t.
The shifted quotient prefix before its next digit is no larger than the
next completed quotient prefix. Thus every quotient and remainder word
fits (1). The Python helper enforces the sufficient additional contract
D<2^(W-2), which holds here by the stronger D<2^(4C).

The final rounded integer is

    q + [2r>=D],     if S>=0,
    -q - [2r>D],     if S<0.                               (3)

For S>=0, this is floor(q+r/D+1/2). For S<0, it is
floor(-q-r/D+1/2). The strict inequality in the negative branch is
essential: -1/2 rounds to zero. The positive halfway value 1/2 rounds to
one. The word 2r is below 2D, so its comparison is also safe.

If D=1, r=0 and rounding changes nothing. If D>=2 and t>=1, the rounded
result's magnitude is at most q+1<=t. At t=0 it is zero. Therefore the
final result also fits W signed bits. Equations (2) and (3), rather than
finite extrapolation, prove the all-B, all-C construction.

## Complex gates, input snapshots and the cited allowance

For a complex row a_0 z_0+a_1 z_1, expand its real and imaginary parts
using the four real input coordinates. Each real row has exactly four
rational coefficients, with signs but no increased component height.
If the inputs are 2^-F X_j, multiplying a rounded output by 2^F gives
exactly the integer expression above. The arithmetic bound depends on
B=F+I, not separately on F. The input grid cancels before arithmetic.

Save all four inputs, compute all four output integers, then overwrite
the four stored coordinates. This gives the same saved-input,
exact-local-sum, once-per-output rounding contract as Jose Manuel's
`rational-unitary-fft/exact.py:apply`. Armin Pourshafeie's PR5240 asks for
such a concrete arithmetic implementation. Its layer and stored-state
theorems are cited premises, not re-proved or audited here.

The same source's `engine.py:certificate` and FULL-PROOF.md use the
conservative temporary allowance

    2F + 8C + 2I + 32 = 2B + 8C + 32.

The new arithmetic construction uses

    B + 4C + 2 = (2B + 8C + 32)/2 - 14.                     (4)

This reduces a sufficient maximum arithmetic-word width. It does not
establish a reduction in total live bits, elapsed time or a complete
caller's allocation. Output data still need that caller's independent
amplitude bound before they can be stored back in B bits. The kernel
permits W-bit outputs and makes no unconditional B-bit output claim.

## One source-produced butterfly

The verifier calls the retained `Phases(4, source)` and
`Builder.butterfly` with the exact phase i. They produce

    [ 13575/19193,   13568 i/19193 ]
    [ 13568/19193,  -13575 i/19193 ].

The maximum component height is C=15. For B=18, the new bound is 80 bits.
Evaluating the cited allowance at these same parameters gives 188 bits.
This comparison does not assert that a complete source caller selected
C=15 or allocated an 188-bit word. It is a same-parameter comparison of
two sufficient formulas. Actual coefficient production is used to supply
this finite fixture; its approximation theorem is not an audit target.

The independent Fraction oracle, source executor comparisons, large-height
fixtures and controls corroborate the implementation. They do not replace
the proof or establish any physical supplier or multiplication theorem.
