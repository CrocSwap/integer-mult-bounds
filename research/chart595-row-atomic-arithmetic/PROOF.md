# Exact row accumulation at the stored-row grid

This construction changes the normalized scalar evaluation contract of the
fixed PR #7697 graph. It preserves every completed row and every paid chart
operation. It does not change the physical provider or its complete price.

## Row program

Let the fixed row be `sum(q_j * x_j)`. Compute its positive common denominator
`D = lcm(den(q_j))` and integer coefficients `a_j = D*q_j` once from the
source graph. The runtime program reads immutable integer donor values X_j,
forms `A = sum(a_j * X_j)` in their literal order, then performs one exact
integer division `A/D`. Reject a nonzero remainder. There is no intermediate
rounding or division. D and the a_j are fixed row constants.

The common stored scale is `S = 161280`. The complete independent-input
replay starts with S times each standard basis vector. Every final division
has remainder zero. Each completed vector agrees, after multiplication by
280, with the complete literal-product trace at scale 45158400 from PR #7701.
All 7644 rows and 8738317 nonzero basis products are covered. This includes
both split-owner columns and the early output row.

The proof of exactness is induction on the literal acyclic schedule. If all
donors equal S times their exact normalized values, then A/D equals S times
the exact next row. The full coefficient check proves that value is integral
for every independent integer entrance. Linearity extends the basis result
to arbitrary integer entrance vectors. The same scalar statement applies
componentwise and after an external common dyadic input scale.

The gcd of all stored coefficients is one at S. Thus no smaller positive
common integer scale can represent all stored values of this fixed graph
for arbitrary independent entrances. The new contract attains this minimum.
The literal-product lower bound 45158400 remains correct: A is an integer
numerator with a pending row divisor, not a stored logical scalar product.
A smaller grid requires this changed arithmetic representation.

## All-width arithmetic bound

For signed W-bit donors, W at least two, `|X_j| <= 2^(W-1)`. The exact
source census gives these maxima, all attained at row 151738:

| Quantity | Maximum |
| --- | ---: |
| D | 6720 |
| absolute integer coefficient | 84840 |
| B = sum(abs(a_j)) | 683350 |

In particular, B is below `2^20`. Every term, partial numerator and complete
numerator has magnitude at most `B * 2^(W-1)`, strictly below `2^(W+19)`.
Therefore a signed word of width W+20 holds all such values, including their
positive magnitudes. This proof includes the most negative W-bit donor.

The kernel multiplies a donor magnitude by abs(a_j) with binary shifts and
additions. Every shifted multiplicand and intermediate product sum is at
most the full product magnitude. It then adds the signed result to A.
The same W+20 bound covers every value, independent of cancellation.

Binary long division scans W+19 magnitude positions. Before each optional
subtraction, the remainder is below `2D <= 13440`. Each quotient prefix is
at most the complete magnitude quotient, which is at most abs(A). The
shifted quotient prefix is no larger than the next completed prefix.
Thus every remainder, quotient, sign conversion and constant also fits
W+20. A zero final remainder proves exact division. No multiplication or
division machine instruction is assumed by the runtime kernel.

The output fits W+20; installation in a W-bit bank still needs the actual
row amplitude bound. The two full finite fixtures check that separate
condition at W=64. This does not prove a universal W-bit amplitude bound.

The extra 20 bits are a sufficient uniform bound for this full-numerator
program. They cannot be replaced uniformly by 19: at row 151738, set each
donor to the sign of its a_j times the largest multiple of 6720 below
`2^31`. This is a legal W=32 input and makes A divisible by D. Its positive
numerator needs 52 signed bits. RESULT.json retains the exact value.
This is a lower control for this accumulator representation, not a lower
bound for every arithmetic algorithm or every reachable bank state.

## Explicit arithmetic work

The 170652 scalar terms have 903276 coefficient-bit loop iterations and
245747 conditional product additions. There is one accumulator addition
per term. Exactly 3607 rows have D greater than one; the other 4037 rows
need no division. For the nontrivial rows there are 3607 times (W+19)
long-division iterations per real component per full normalized graph.
Each iteration has two shifts, one input-bit read, a comparison, and at
most one subtraction and one quotient increment. These are word-operation
counts for this program, not measured speed or a bit-tape tariff.

Each coefficient has at most 17 bits. Fixed-coefficient shift/add passes,
addition and fixed-denominator remainder scans admit linear work in W
when implemented as serial bit operations with bounded carry. The explicit
reference uses Python integers and checked word values. It is not a tape
emitter and does not charge bank selection, staging, dirty initialization,
layout, head returns or cleanup. The 20-bit arithmetic allowance is below
the source's 26-bit temporary allowance, but that comparison alone does
not prove a valid physical substitution or a lower full allocation.

## Evidence and limits

The full basis replay uses integer common numerators and checks every final
division. Its row-vector digest agrees with the pinned earlier product
trace. Two complete scalar runs execute the shift/add and long-division
kernel, preserve every donor, and agree at every row with an independent
Fraction oracle. Every row has exact signed boundary fixtures at widths
16 and 32. The largest row is also checked at widths 128, 2048 and 4096.
Five controls reject a narrower word, nonzero remainder, out-of-range
input, boolean input and excess coefficient mass.

This is a local arithmetic construction and written all-width proof with
finite corroboration. It is not full supplier admission or a new kappa.
The graph, paid/target invoice and selected frontier are unchanged. All
five framework assumptions remain. Common-denominator accumulation and
binary arithmetic are prior methods, as recorded in CREDITS.md.

## Open next questions

Bind the new accumulator to the actual guarded streams and complete root
representation. Prove every physical row division and installation at its
actual width, and count all movement, head returns, dirty state and cleanup.
Only that substitution can justify an ordinary-cost or storage claim for
the complete native caller.
