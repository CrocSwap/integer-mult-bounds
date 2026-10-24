# Independent review of the correlated phase sector

Sections 3 and 4 pass this review. The stated signature subgroup is
correct. The actual 17-axis frame conditions have exactly `2^18`
solutions. Formula (6) gives the exact normalized dimension at every
positive tensor width. For the sufficient 73-axis sector, the limit is
`2^-2700`, and the ratio to this limit is below `101/100` exactly from
width 152 onward.

This result removes a restriction to a product of width-one sectors.
It does not supply a physical projector, source access, an encoding,
or a useful cost bound. Maximality is proved for the specified 17-axis
frame conditions. The 73-axis sector is sufficient; this review does
not assert its maximality for the full actual route group.

The reviewed proof has SHA256
`0e16a12d172ba215041c1096627772262863beca0c2296c8d773bdbac2d6c3d0`.
The reviewed producer receipt has SHA256
`b6d92578b2f7faff291855a92b7d5fa0570d0da9999cb11981333a0bc36d213d`.
`REVIEW.json` pins the producer, source archive, source member, and
other dependencies. No producer code is imported or run.

## Signature group and odd-constant sector

For a character tuple, expansion of binary parity modulo four gives

\[
f(v)=\sum_i a_iv_i+2\sum_{i<j}b_{ij}v_iv_j\pmod4.
\]

The coefficients are unique. Coordinate evaluations give `a_i`, and
pair evaluations give `b_ij`. Thus the group has
`4^n 2^(n(n-1)/2) = 2^(n(n+3)/2)` elements.

If `f` is constant with value `d` on odd vectors, evaluation at `e_i`
gives `a_i=d`. Evaluation at each odd triple gives

\[
b_{ij}+b_{ik}+b_{jk}=d\pmod2.
\]

Choose one coordinate, set its auxiliary coefficient to zero, and put
`b_j=b_1j+d` on the others. The triple equations then give
`b_ij=d+b_i+b_j`. Conversely these coefficients expand to

\[
f_{d,b}(v)=d\,p(v)+2(b\mathbin\cdot v)(1+p(v))\pmod4.
\]

Changing `b` by the all-ones vector does not change this function.
There is no other redundancy. The subgroup is therefore
`Z/4 x (F2)^(n-1)` and has order `2^(n+1)`. The small checks also
cover dimensions one and two, where there are no triple constraints.

An orthogonal map preserves odd vectors. It takes this subgroup to
itself and preserves `d`; it need not fix `b`. Each orthogonal odd
axis has phase `i^d`, so a rank-r orthogonal frame has phase `i^(rd)`.
Equal-rank complete owner frames therefore agree on the sector.
This conclusion does not apply to arbitrary internal canonical frames
of the old local program.

The five-column construction is exact. For even `v`, the first two
columns `b` and `omega+b` contribute `2(b.v)` and the other columns
contribute zero. For odd `v`, the first two contribute one and the
three `omega` columns contribute three. Their sum is zero modulo four.
Adding `d` copies of `omega` gives `f_(d,b)`. This proves the stated
eight-column bound and gives inputs outside `{0,omega}^lambda`.

## Actual 17-axis result

The independent checker reconstructs all 1,008 actual ordered routes
from the pinned port bases and mode charts. It uses conjugated
coordinate exchanges, rather than the producer's sum of orthogonal
swaps. The eight first-stage generators agree with the emitted records.
Their orbit contains all 65,535 nonzero even vectors in 17 dimensions.

The frame-sector check uses a different certificate from the producer.
For each rank 8, 9, and 17, it selects a fixed 600-letter word in the
eight actual generators. At every prefix it records the difference
between the resulting frame phase and the initial frame phase. These
are necessary conditions for the full generated frame orbit. They
are exact constraints, not estimates from sampled characters.

There are 153 polynomial coefficients when every mixed coefficient is
temporarily stored in `Z/4`. The checker adds the 136 constraints that
force mixed coefficients to be even. It uses dense unit elimination
over `Z/4`, followed by binary elimination of the remaining even
rows. Nine small exhaustive kernel counts check this elimination
method independently.

| Frame rank | Unit pivots | Even pivots | Solution order |
|---|---:|---:|---:|
| 8 | 136 | 16 | `2^18` |
| 9 | 136 | 16 | `2^18` |
| 17 | 0 | 152 | `2^154` |

For ranks 8 and 9, the universal odd-constant subgroup already gives
`2^18` solutions to every orthogonal frame condition. The finite
constraint bound therefore proves equality for the entire generated
orbit. No enumeration of the full group is needed. The combined
rank-8, rank-9, and rank-17 conditions have the same exact sector.

The rank-17 count also has a direct lower bound. For any orthogonal
17-by-17 matrix, the difference between its full frame phase and the
coordinate full frame phase is a translation phase
`2 delta . (a mod2)`. Orthogonality makes the mixed contributions
zero on legal even mixed coefficients. Invariance of the parity
signature makes `delta` even. Thus arbitrary mixed coefficients,
arbitrary high bits of `a`, and a common low bit of `a` satisfy every
full-frame condition. This gives `2^(136+17+1)=2^154` solutions and
matches the independent finite bound.

A separate check imposes equality of each whole signature under each
of the eight generators. Evaluation at coordinates and coordinate
pairs suffices to specify that equality. It gives 152 unit pivots
and exactly four solutions, namely `d p`. This checks the distinction
between a stable sector and an individually fixed signature.

## Quotient and the sign of the random-walk step

Put `m=n-1` and use the odd affine parameterization

\[
v(t)=(t,1+p(t)),\qquad
\psi(f)(t)=f(v(t))-f(e_n).
\]

Substitution preserves the class of modulo-four quadratic polynomials
with even mixed coefficients. The map is onto: a polynomial in the
first m coordinates alone is an extension of any element of `Gamma_m`.
Its kernel consists exactly of functions constant on the odd affine
hyperplane, hence is `S_n`.

For a column `x`, put `epsilon=x_n` and `y_i=x_i+x_n`. Then

\[
\psi(s_x)(t)
 = (\epsilon\mathbin\oplus(y\mathbin\cdot t))-\epsilon
 =(-1)^\epsilon\operatorname{parity}(y\mathbin\cdot t).
\]

The subtraction is in `Z/4`. In particular, the epsilon-one case is
a negative step; replacing it by a positive step would change the
distribution. The map from `x` to `(y,epsilon)` is a bijection, so
the sign and `y` are independent and uniform.

The independent checker enumerates the quotient map on every signature
through n=4. Every fibre has size `2^(n+1)`, and the zero fibre is
exactly the odd-constant set. It also checks the step identity at every
column and argument through n=6. Literal walks use the full quotient
function on its nonzero arguments, rather than the producer's packed
polynomial coefficients. They give the formula's probabilities through
width six for ambient dimensions two, three, and four.

## Gauss sums and multiplicities

For a dual coefficient pair `(alpha,beta)`, the symmetric walk has
eigenvalue

\[
\mu=2^{-m}\sum_y\cos\bigl(\pi q(y)/2\bigr),\qquad
q(y)=\alpha\mathbin\cdot y+2\sum_{i<j}\beta_{ij}y_iy_j.
\]

For even `alpha`, this is the normalized binary Gauss sum of `q/2`.
Fix an alternating polar matrix of rank `2r` in dimension d. Exactly
`2^(2r)` of the `2^d` linear terms cancel the restriction to its
radical. Their Gauss-sum magnitudes are `2^-r`. The sum of the
normalized Gauss sums over all linear terms is one, by character
orthogonality at the zero vector. Therefore the positive and negative
multiplicities are

\[
\frac{2^{2r}+2^r}{2},\qquad
\frac{2^{2r}-2^r}{2},
\]

with `2^d-2^(2r)` zero values.

For a nonzero parity vector `l=alpha mod2`, the cosine is zero outside
`l`-perpendicular. On that hyperplane, `q/2` is a binary quadratic
polynomial with zero constant term. For fixed `l`, its linear and
mixed parameters map onto all quadratic polynomials in dimension
`m-1`. Any such polynomial extends through a linear projection onto
the hyperplane. Comparing parameter counts gives exactly `2^m`
preimages for each polynomial. Its contribution is one half of the
binary Gauss sum. There are `2^m-1` choices of `l`, so the second
spectrum has the required factor `(2^m-1)2^m`.

The alternating-matrix count in formula (5) is also correct. An
independent count uses extension by one row and column. If the old
matrix has rank `2r`, a new column in its image gives `2^(2r)` choices
that keep the rank. A column outside that image gives
`2^(d-1)-2^(2r)` choices that increase the rank by two. Hence

\[
A_d(r)=2^{2r}A_{d-1}(r)
 +(2^{d-1}-2^{2r-2})A_{d-1}(r-1).
\]

This recurrence agrees with the stated product formula at every
dimension from zero through 72. The checker separately enumerates
all alternating matrices and binary quadratic sums through dimension
five, and all `Z/4` cosine sums through dimension four.

Only the zero dual coefficient has eigenvalue one. Every other value
has magnitude at most one half. The zero step and generation argument
in the proof also gives an independent irreducible, aperiodic walk.

## Exact density and threshold

For positive width, zero eigenvalues contribute zero. At even width,
the positive and negative multiplicities add to `2^(2r)`. At odd
width, they subtract to `2^r`. This gives exactly

\[
k_\lambda=\lambda-2+(\lambda\bmod2)
\]

and the two sums in formula (6). The quotient order is
`I_n=2^((n-1)(n+2)/2)`. All terms in the ratio to `1/I_n` are
nonnegative. The `r=0` term in the first sum is one; the second sum
is positive at every finite positive width when n is at least two.
The ratio is therefore strictly above one.

As width increases, `k_lambda` does not decrease, and the positive
second sum has an additional factor `2^-lambda`. The ratio strictly
decreases. The nontrivial spectral bound also gives formula (7):

\[
0\le I_n\Pr[f\in S_n]-1\le(I_n-1)2^{-\lambda}.
\]

All stated producer spectrum multiplicities and finite-width samples
agree with the independent recurrence and exact rational arithmetic.
The checker adds the adjacent widths needed to locate the sharp
one-percent threshold:

| Ambient n | Limit | Last width above `101/100` | First width below `101/100` |
|---|---|---:|---:|
| 17 | `2^-152` | 39 | 40 |
| 73 | `2^-2700` | 151 | 152 |

The exact fractions are in `REVIEW.json`. Monotonicity proves the
claim for every width after the displayed threshold, rather than
only at one sampled width. Formula (6) has 73 terms at n=73.

Uniform convergence on the full signature group also holds. For a
nontrivial modulo-four quadratic dual phase, its complex Gauss sum
is zero or has magnitude `2^(-r/2)` for the rank r of its binary
polar form. If the polar form is zero, a nontrivial residual linear
character gives zero. Otherwise r is at least one. This proves the
stated upper bound `1/sqrt(2)` and convergence for each fixed-d coset.
The limiting fixed-d fractions are therefore `2^-154` and `2^-2702`.

The three nonzero-d sectors have three times the fixed-d limit. Their
query factor `I-Q` need not vanish. This is a real distinction from
the zero-query sector, but gives no implementation cost by itself.

## Scope clarifications and reproduction

The Section 5 inverse formula `I+(H0^-1-I)E` is valid for every
idempotent E that commutes with the scalar mode action. Equality of
the operator's order with the order of H0 requires a nonzero range
of E. A short-width fixed-d sector can be empty, for example d=3 at
width one. For `lambda >= d`, d copies of omega and zero columns
give a nonzero fixed-d sector. This qualification does not affect
the subgroup, density formula, or limiting claims reviewed above.

For the displayed right action `g -> gh`, the orbits are `gH`.
Using the phrase "right-action orbit gH" avoids the left-coset versus
right-coset terminology ambiguity. The ordered operator identities
are consistent with `S_a S_b = S_(ab)`.

Run from the workspace root:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/residual-syndrome/physical-algebra/correlated-sector-review/review_sector.py
```

The last line is `PASS_INDEPENDENT_CORRELATED_SECTOR`.

No new native program, projector, masked cover access, finite-grid
bound, or full supplier was checked. In particular, positive relative
dimension is not zero-cost physical access. The integral cover-sum
construction is credited to the pinned predecessor note; the present
review checks the correlated-sector extension and its exact dimension.
AI assistance was used to write this review and checker. No publication
is authorized.
