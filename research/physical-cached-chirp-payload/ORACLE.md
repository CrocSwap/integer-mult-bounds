# Independent dyadic chirp source check

This review is by a separate source-aware OpenAI verifier for @CubeJerry.
It checks the actual phase tables produced by `chirp_tables.py`; it is not
a second physical multiplier or a replacement online coefficient supplier.

## Independent enclosure construction

`dyadic_chirp_oracle.py` imports only `math.isqrt`. It does not import the
producer, its pi enclosure, its Taylor functions, or floating trigonometry.
On the grid `2^-b`, an interval is represented by two integer endpoints.
Starting with the exact root `-1`, repeatedly use the positive square roots

\[
 c'=\sqrt{(1+c)/2},\qquad s'=\sqrt{(1-c)/2}.
\]

The resulting complex root is `c' - i s'`. At the first step it is `-i`;
subsequent steps lie in the fourth quadrant. The half-angle identities and
this quadrant choice uniquely identify `exp(-pi*i/t)` for every dyadic `t`.
Monotonicity gives endpoint enclosures for both square roots. For an integer
`v` representing `(1+c)*2^b`, the lower output endpoint is
`isqrt((v*2^b)//2)`; the upper is that integer plus one unless its square is
exact. The checked integer inequalities prove the directed rounding.

For the source coordinate `(t,s,x)`, reduce `k=s*x*x mod 2t` and enclose the
`k`th power by binary complex interval multiplication. Every real interval
product takes the extremum of all four endpoint products. Real subtraction
and imaginary addition are exact before outward division by `2^b`.
Induction on the powering loop therefore preserves containment. Quarter
roots are returned exactly using their independently specified clockwise
order. Negative and huge slopes enter only through exact modular arithmetic.

Given a stored pair `(a,b)` on the `2^-f` grid, the checker first uses the
exact integer condition `a*a+b*b <= 2^(2f)`. It then compares the pair to
the independent root enclosure. Distances to the nearest and farthest
enclosure endpoints respectively bound the possible component error below
and above. A lower bound above two ulps is a demonstrated failure; an upper
bound at most two ulps is a certificate. The inner-endpoint sign and
magnitude promise is checked separately. A coefficient near an unresolved
endpoint triggers increased oracle precision. Exhausting the fixed
refinement limit returns **inconclusive**, never acceptance or a mathematical
counterexample. Every acceptance is sound for any dyadic input on which it
returns; the finite replay does not establish termination for all parameters.

`check_tables` also checks the literal pair `(a,-b)` against slope `-s`.
This verifies the conjugation used by the consumer. It does not assume that
two independently rounded approximations must be bitwise conjugates.

## Executed finite coverage

`chirp_source_review.run(producer, make_interval_oracle)` runs five families:

| Radices | Slopes | Radius | Requested bits | Incoming precision |
|---|---|---:|---:|---:|
| `(8,4)` | `(7,3)` | 1 | 10 | 0 |
| `(16,8,2)` | `(-3,5,-7)` | 3 | 14 | 27 |
| `(32,4,8)` | `(63,-15,103)` | 2 | 12 | 0 |
| `(2,)` | `(-1,)` | 1 | 0 | 0 |
| `(256,2)` | `(10^30+1,-3)` | 2 | 11 | 0 |

The 342 source rows and their 342 conjugates cover unequal radices, an
unsorted slower-axis order, negative slopes, a large encoded slope, a
preexisting finer grid, exact axes and non-axis roots. The producer's
authenticated interval module is freshly loaded for each family and is used
only to generate the tested input. Six mutations must produce their
specific decisive rejection: wrong conjugation, a factor-two denominator,
wrong odd slope, wrong squared coordinate, a point outside the unit disk,
and swapped associations between an axis and its slope. The stand-alone
oracle also checks exact roots, an eighth-root square inequality, a
third-power quadrant identity, and four numerical negative controls.

The finite tests certify those source outputs and reject those mutations.
The all-parameter numerical/source theorem remains the accompanying source
proof, and the actual fixed-tape caller requires its own instruction and
cost review. No new multiplication exponent is claimed.
