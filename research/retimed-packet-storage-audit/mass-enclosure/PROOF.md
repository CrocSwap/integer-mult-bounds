# Uniform error for the actual dyadic bin-mass routine

## Result, source, and scope

This independently audits `Measure.inverse_power` and `Measure.mass` in the
resolved `transport.py` used by Ali Romman's #8042 at
`dfd25d553a843a946ca0b94130a5ff8943e98fdd`. The source SHA-256 is
`98bdb540233794338b426d1b0d0e72cff7fcbbd08be702af0d81e237dbecaae9`.
The original `TRANSFER.md` already states an enclosure and its production
consequence. The present contribution supplies an independent uniform proof
for the literal directed-rounding loop, with a substantially smaller error
envelope and explicit domain boundaries. It does not claim priority for
dyadic root evaluation or interval arithmetic.

Let `t=k/2^d` be the reduced exponent accepted by the source, with
`0<t<=1`, let the integer grid be `g=2^p` with `p>=0`, and suppose
`1<=x<=X`, with rational `x` as accepted by `Fraction`. Define

\[
C_d=(d+1)(d+2)/2,\qquad E_d(X)=C_d X+(d+1).
\]

If the actual source returns the integers `(lo,hi)`, then

\[
0\le lo/g\le x^{-t}\le hi/g\le1,\qquad
x^{-t}-lo/g\le E_d(X)/g,\quad hi/g-x^{-t}\le E_d(X)/g.       \tag{1}
\]

For rational `1<=left<right<=X` and nonnegative rational volume `V`, the source's returned mass
interval contains

\[
M=\frac Vt(left^{-t}-right^{-t}),
\]

and each endpoint differs from `M` by at most

\[
\Delta=\frac{2V E_d(X)}{t g}.                              \tag{2}
\]

No derivative bound at a small reciprocal or lower positive rounded base is
needed. The finite checks corroborate these universal statements; they do
not supply them by extrapolation.

## 1. Exact source recurrence

The denominator is a power of two, so its bit length is `d+1`. Before
iteration `j`, the base represents
`y_j=x^(-1/2^j)`. The source processes numerator bits in the order
`d,d-1,...,0`, multiplying by `y_j` precisely when that bit is set.
The final selected exponent is therefore
`sum_j bit_(d-j)(k)*2^(-j)=k/2^d=t`.

Initially the base bounds are the floor and ceiling of `g/x`. After every
iteration except the last, the lower base is `isqrt(a*g)` and the upper is
`isqrt(b*g-1)+1`. For positive integer `b*g`, the latter is exactly the
integer ceiling of its square root, including the perfect-square case.
Since `x>=1`, initial bounds lie in `[0,g]` with upper at least one.
All subsequent base and accumulated-product bounds remain in `[0,g]`.
All isqrt inputs are consequently valid. A lower bound equal to zero is
allowed and is handled by the proof.

Monotonicity of square root and nonnegative multiplication, followed by
directed rounding, proves enclosure at every step. A selected product's
floor loses less than `1/g`, and its ceiling gains less than `1/g`.

## 2. Relative base error avoids repeated derivative losses

For the exact positive `y_j`, define

\[
e_j^- = 1-a/(g y_j),\qquad e_j^+ = b/(g y_j)-1.
\]

Enclosure gives `0<=e_j^-<=1` and `e_j^+>=0`. Initially both errors are at
most `x/g<=X/g`. The elementary inequalities

\[
1-\sqrt{1-u}\le u\quad(0\le u\le1),\qquad
\sqrt{1+u}-1\le u\quad(u\ge0)
\]

show that exact square rooting does not increase either relative error.
The subsequent grid rounding adds at most `1/(g*y_(j+1))<=X/g`, because
`y_(j+1)>=1/X`. Thus, by induction,

\[
e_j^-,e_j^+\le(j+1)X/g.                                  \tag{3}
\]

This proof remains valid if the displayed upper bound exceeds one; only
the actual lower error needs to lie in `[0,1]`. Since `y_j<=1`, (3) also
bounds each absolute base error by `(j+1)X/g`.

## 3. Accumulated products

Let the exact current product be `Y`, enclosed by `l,h`, with all listed
quantities `Y,l,h,y_j,a/g,b/g` in `[0,1]`. Then

\[
Yy_j-l(a/g)\le(Y-l)+(y_j-a/g),
\]

and

\[
h(b/g)-Yy_j\le(h-Y)+(b/g-y_j).
\]

For example the second difference is
`h*(b/g-y_j)+y_j*(h-Y)`, and its coefficients are at most one. Each
selected source multiplication adds at most one further grid unit to
each endpoint's absolute error. At most `d+1` selections occur. Summing
(3) over all possible iterations gives at most
`[X*sum_(j=0)^d(j+1)+(d+1)]/g=E_d(X)/g`. This proves (1).
Skipping a zero bit adds no error; no rounding after an unexecuted
multiplication is charged as a premise.

## 4. Subtraction, nonnegativity, and integer allocations

The upper mass endpoint is `V/t*(b_left/g-a_right/g)`, hence is above `M`
by at most (2). The untruncated lower expression is below `M` by at most
(2). Replacing that lower expression by zero preserves both conclusions:
when it was negative, `M>=0` and its old gap was at least `M`.
For `right<=left` the literal source returns `(0,0)`; its intended empty
intersection mass is zero, and no oriented negative integral is claimed.

If `Delta<1/4`, a bin count `m=ceil(upper)` obeys

\[
0\le m-M<5/4<2.                                          \tag{4}
\]

For any `0<=pi<=1`, the source's allocation
`floor(pi*lower)` is nonnegative, is at most `pi*M`, and loses fewer than
`1+pi*Delta<=5/4` replicas. These are separate directed statements;
an undirected numerical approximation would not suffice for custody or
capacity.

## 5. Production source application

On the #8042 Gaussian installation `d=29`; the binary exponent has `d=60`.
Both have `t>=1/2`. The declared production volume is `V=N^6`, and the
actual `Plan` constructor selects `p=max(256,64*N.bit_length())`, so
`g>N^64` for integer `N>=2`.

The installed largest target is at most 1,032 and the smallest positive
paid grade is at least 1/2. The scale upper endpoint satisfies `U<=N`.
The direct bin calls use `[e,e+2]` inside `[L,U]`; interior intersections
are further clipped to that bin. An exterior source interval ends at
`(e+2)*k/r<=2064*N`. Nonempty intersections start at least at `L>1`.
Thus `X=2064*N` covers every call made by this constructor. This bound
uses the actual installed grade domain; it is not a guarantee for an
arbitrary user-supplied `Plan` with unrestricted grades, volume or exponent.

For `d<=60`,

\[
E_d(2064N)\le1891\cdot2064N+61
=3903024N+61<2^{22}N\quad(N\ge2).
\]

Consequently

\[
\Delta <2^{24}N^{-57}\le2^{-33}<1/4.                     \tag{5}
\]

This holds already for `N>=2`; it therefore covers the far larger
installed admissible carriers. It replaces the use of the separate
universal bin-enclosure premise in the recovered Gaussian owner census,
once that census's existing source grades, volume and constructor
bindings are retained. In particular its sum of integer counts remains
`sum_e m[e] < N^6/(t*L^t)+2U`, now with (4) derived from the literal loop.
The owner-census scheduling, free-first allocation and other physical
contracts still need their own proofs.

## 6. What is not claimed

The source API checks the dyadic exponent, but does not validate all domain
hypotheses above. No bound is claimed for `x<1`, negative volume, a negative
precision or an unrestricted larger grade ratio under the same production
constant. In particular the convenient `[0,1]` product estimate must not be
used outside `x>=1`. Empty intervals retain their explicit source behavior.

This lemma removes one local numerical premise from a particular owner
count, not the full `analytic_recovery` assumption. It does not prove the
bin funding inequalities, physical storage for all tapes, integer recovery,
prime avoidance or a new multiplier exponent. Production-size calendars
are not executed. Credit remains with Ali Romman for the source and original
transfer proof, and all retained contributors. Prepared for Jerry Chen /
@CubeJerry with substantial OpenAI assistance; independent review is pending.
