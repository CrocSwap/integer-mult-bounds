# Independent orchestration review and a second remainder proof

The root checked the complete argument, including the literal source
curves, prime-gap derivative bounds, reverse order, inverse determinant
identity, all perturbation constants and the qualified prime-availability
argument. No blocking flaw was found in the stated separated-family,
two-order theorem. The next paragraphs supply an independent route to
its crucial leading term and a sufficient remainder bound.

## Complementary-minor leading term

Write the displacement as A0+A1+A2+A3, where the subscript is total
degree in the three lower entries. At lower entries zero, the last row
of A0 is zero; rows five and six have only their final entries x and u.
Consequently u row5 - x row6 is identically zero and rank(A0)<=6 over
the rational-function field. Every seven-by-seven cofactor vanishes.
This also proves absence of determinant terms of degrees zero and one.

In degree two, a single entry from A2 has a vanishing cofactor. The
remaining terms are exactly the complementary-minor sum

    sum_(|I|=|J|=2) (-1)^(sum I+sum J)
        det A1[I,J] det A0[I-complement,J-complement].

A nonzero six-row minor must delete row seven and one of rows five
or six. Thus there are only two possible row pairs and 28 column pairs.
The independent `review/check_leading_minors.py` constructs these minors
from the tensor bit labels, without importing either author checker.
It recovers the exact sixteen-term polynomial

    (u-r)(ur+x^2)(xy-uv)(xy-rz).

The computation expands only upper-only six-by-six minors, not the full
six-variable determinant. The polynomial identities prove the generic
rank/cofactor statements; no source-number sample is substituted for them.

## A coarse independent bound also pays the full remainder

The exact weighted mass 7,682,848 in the primary proof is useful but
not needed for acceptance of the theorem. Each tensor entry is one
monomial, of weighted magnitude at most 8 when upper variables have
weight one and lower variables weight two. Each displacement entry
contains at most two such monomials and has coefficient mass at most 16.
The complete determinant expansion therefore has weighted absolute mass
at most 8! 16^8 < 2^48. Collection and omission of degree-two terms can
only decrease the sum of absolute coefficients.

With upper entries <=1, lower entries <=2w and 0<w<=1, the full
degree-at-least-three remainder is thus at most 2^48 w^3. On the source
family, a>=4 ln(16p)>32 and p>=4096. Hence p^2 a^3 >=2^39>2^32, giving

    w <= 2^-32 p^-8 <= a^3/(2^64 p^6) = h^3/2^49,
    h = a/(32p^2).

This coarser bound still leaves at least half the leading magnitude,
h^3 w^2/2 = D. It provides an independent analytic acceptance path
without relying on the exact higher-degree mass table.

## Remaining numerical and source checks

The common-target source derivative bounds give all three required
gaps without prescribing the prime ordering. Axis reversal and full
bit complementation explain the paired order; they do not assume
arbitrary order invariance. The inverse Schur identity needs precisely
that reverse-order determinant. Norm bounds 8 and 128 then give the
displayed forward and inverse singular-value margins.

The factor-to-tensor loss is at most 7 zeta. Neumann inversion costs
2^16 times the tensor maximum-entry error, followed by another factor
two for displacement. The stated allowances pay both losses. The
periodic alias estimate follows directly from |u|<=3/2, |beta|<=1/2
and |tm+u|>=|m|t/2 for nonzero aliases. The exponential tail is far
below 2^-73 D under t>=p^4. The p-bit sufficient precision follows
from the derivative of p-233-42 log2 p and its value at 4096.

The root checked [Trudgian's exact theorem 2](https://arxiv.org/html/1401.2689v2#S2)
directly, including its constant 0.2795, denominator 6.455 and x>=229
threshold. The three interval argument uses both endpoint errors and
its stated eventual logarithmic scale; it does not assert a finite
uniform existence threshold at every p>=4096.

Finite source fixtures and the complete author polynomial replays are
corroborating evidence. This root review is independent model-assisted
mathematical work, not human peer review or formal-kernel acceptance.
It supplies no table-production runtime, complete caller, all-order
margin, foundational-assumption discharge or new kappa.

Reviewed for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
