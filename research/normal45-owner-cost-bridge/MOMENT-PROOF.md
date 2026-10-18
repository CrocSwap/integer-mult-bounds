# Complete-profile moment comparison by a positive binomial series

This is an independent exact-rational check of the **fixed finite moment** of
PR #2942, head `a027b0f6fdb0ab2b42ba10fc31b53960166bf2bf`, against PR #2930,
head `81f3b5d12977eba09e06fbff729167d59faabe90`. The construction and allocation
remain the cited authors' work. This check introduces no construction, new
headline, selected frontier, all-size recurrence, or formal-kernel theorem.

The new enclosure implementation was prepared with substantial AI assistance
from OpenAI Codex (GPT-6.1 Sol). It imports no predecessor numerical code. Its
arithmetic uses a positive generalized-binomial series, independently of the
source auditor's atanh logarithm and exponential Taylor series.

## Fixed model and inputs

The stipulated live stock is `W = 896 * 74 = 66304`, ambient width is `m = 73`,
and there are `9 * 74 = 666` calls. For the **complete paid child histogram** H,
the exact normalized bill is

\[
 M_H(b)=\frac{1}{73\cdot66304}\sum_{r=1}^{72}H[r]r(73/r)^b.
\]

The corresponding unnormalized power bill is
`sum H[r]*(r/73)^(1-b)`, divided by W above. This is the specified recurrence
coefficient test; a proof that a native/all-size algorithm realizes that
recurrence is a separate premise, not an output of this calculation.

The new complete histogram must be reconstructed from raw words and whole-role
ownership before this test is used as construction evidence. `certify(profile,
baseline_profile, baseline_claim)` accepts that reconstruction as an argument;
the standalone `moments.py` command only reads the saved input profiles. Input
byte authentication and the raw reconstruction belong to the enclosing checker.

The fixed profiles and their difference are:

| r | PR2930 | PR2942 | PR2942 minus PR2930 |
|---:|---:|---:|---:|
| 1 | 1626372 | 1638360 | 11988 |
| 2 | 426240 | 420912 | -5328 |
| 3 | 192474 | 196337 | 3863 |
| 4 | 73260 | 69264 | -3996 |
| 5 | 24198 | 23531 | -667 |
| 8 | 5328 | 5328 | 0 |
| 14 | 0 | 1 | 1 |
| 48 | 27158 | 27291 | 133 |

Both rank masses are `65088 * 74 = 4816512`, hence
`M_H(0) = 1017/1022 < 1`. Equality of the rank masses is a necessary complete-bill
check, not a reconstruction proof. The API also binds the baseline histogram to
the baseline claim and checks its fixed stock, replica and call conventions.

Endpoint semantics are taken from the pinned source `tools/root.py` and
`tools/audit_allocation_moment.py`: **`complex_lower` is b itself** in the formula
above. There is no substitution `b = kappa/(1-kappa)` for this contract. Define

\[
 b_0=\frac{1722499906443274564357}{10^{24}}-10^{-46}-10^{-70},\qquad
 b_1=\frac{430704079965803581999}{250000000000000000000000}.
\]

Here b0 is PR2930's **full guarded headline**, exactly as stored in its pinned
claim, and b1 is PR2942's pinned `complex_lower`. The API does not replace b0 by
a displayed rounded decimal or by the larger baseline `complex_lower`. The
upper sign probe is `b2 = b1 + 10^-20`; it checks a sign and does not propose a
new headline or run a root search.

The live stock W used by this moment is distinct from physical family counts,
private buffer counts and numerical storage. Those counts cannot be inserted
interchangeably into this normalization.

## Positive binomial identity and explicit tail

For `0 <= b <= 1`, let `c0=1` and

\[
 c_{n+1}=c_n\frac{b+n}{n+1}.
\]

All coefficients are nonnegative and `c_(n+1) <= c_n <= 1`. Thus the power
series `F(z)=sum_(n>=0) c_n z^n` and its termwise derivative converge uniformly
on every compact subset of `[0,1)`. The coefficient recurrence gives
`(1-z)F'(z)=bF(z)` and `F(0)=1`. Solving this elementary differential identity
gives `F(z)=(1-z)^(-b)`.

For `t_n=c_n*z^n`, with `0 <= z <= 1/2`, the exact term recurrence is

\[
 t_0=1,\qquad t_{n+1}=t_n z\frac{b+n}{n+1}.
\]

Its ratios are at most z. Therefore, writing `P_N=sum_(n=0)^N t_n`,

\[
 P_N\le (1-z)^{-b}
 \le P_N+\frac{t_{N+1}}{1-z}
 =P_N+t_N\frac{z(b+N)}{(N+1)(1-z)}.
\]

This includes the first omitted term. It holds at b=0 and z=0, where the
function is exactly one. The code handles these exact cases directly. There is
no alternating-series assumption, omitted negative coefficient or numerical
logarithm in this bound.

For `q>=1` rational, write `q=2^k*u` with integer `k>=0` and `1<=u<2`. Then

\[
 q^b=(2^b)^k u^b,
\]

and each factor is of the preceding form: `2^b=(1-1/2)^(-b)` and
`u^b=(1-(1-1/u))^(-b)`. Both z values lie in `[0,1/2]`. The enclosing API uses
192 nonconstant terms for each factor and scale `S=2^256`.

## Directed integer arithmetic

The implementation stores lower and upper scaled integers. Suppose
`L_n <= S*t_n <= U_n`. Multiplication by the nonnegative exact rational
`a_n=z*(b+n)/(n+1)` gives

\[
 \lfloor L_n a_n\rfloor\le S t_{n+1}
 \le\lceil U_n a_n\rceil.
\]

Starting at `L_0=U_0=S` proves every term enclosure by induction. Summing the
integer endpoints encloses `S*P_N` exactly. Adding
`ceil(U_N*z*(b+N)/((N+1)*(1-z)))` to the upper sum bounds the entire tail by the
previous inequality. Every division is an integer floor or ceiling; no rounding
mode outside Python integer arithmetic is assumed.

For positive enclosures `Lx <= S*x <= Ux` and `Ly <= S*y <= Uy`, the product
enclosure is

\[
 \lfloor L_xL_y/S\rfloor\le Sxy
 \le\lceil U_xU_y/S\rceil.
\]

Repeated application proves the range-reduced `q^b` bounds. Finally all moment
weights `H[r]*r/(73W)` are positive. The code sums the scaled bounds with
integer weights and divides once, downward for the lower endpoint and upward
for the upper endpoint. At b=0 it returns the exact rational rank-mass identity.
These steps prove that every returned interval contains the exact real value.
Its width need not be estimated in advance: the final strict rational endpoint
comparisons directly certify the required signs.

## Certified signs and conditional cost sensitivity

All intervals emitted by `certify` are exact rational numbers. For readability,
the following deliberately coarser rational bounds are also tested:

| Quantity | Strict lower bound | Strict upper bound |
|---|---:|---:|
| `1 - M_new(b0)` | `901400918/10^15` | `901400920/10^15` |
| `1 - M_new(b1)` | `6/10^26` | `61/10^27` |
| `M_new(b2) - 1` | `284/10^22` | `285/10^22` |
| one rank14 charge at b0 | `290068663/10^14` | `290068664/10^14` |
| rank14 charge / complete slack at b0 | `321797612/10^8` | `321797614/10^8` |
| `1 - M_(new+e4)(b0)` | `7/10^8` | `72/10^9` |
| `M_(new+e5)(b0) - 1` | `136/10^9` | `137/10^9` |

The full exact certificate also verifies:

- `M_old(b0) < 1` and `M_new(b0)-M_old(b0) < 0` using directed interval
  subtraction `[new_lower-old_upper, new_upper-old_lower]`.
- `M_(new+e32)(b0) > 1` and `M_(new+e32)(b1) > 1` by **lower** bounds above one.
- Removing the one rank14 residual reduces the invoice by its positive charge,
  but violates the complete rank-mass identity by 14. Its apparent numerical
  favorability is therefore not a valid complete-profile certificate. The
  removed charge is more than three times the entire complete-bill slack at b0.

For any fixed b in `(0,1)`, a single rank-r child costs
`73^(b-1)*r^(1-b)/W`, which increases strictly with r. The rank4 and rank5 signs
therefore give a **sharp integer spare-child threshold in this isolated moment
model at b0**: one added child of rank 1..4 still has moment below one; one added
child of rank 5..72 has moment above one. This is a conditional tolerance for a
specified child charge. It does not claim that an extra physical buffer costs
one such child, that the altered bill obeys the original rank mass, or that an
adapter/precision/storage obligation can be ignored.

Every nonzero charged rank is below 73, so each summand is strictly increasing
and continuous in b. Thus the two **true** signs at b1 and b2 place the unique
moment crossing between them. This is only a consistency check of the pinned
candidate endpoint. A failed sufficient upper-bound test alone would give no
rejection; a deliberately weak enclosure that straddles one is tested as
inconclusive.

This check does not claim uniform ordering of the two profiles for all b. Their
equal-mass truncated-rank difference at the first knot is positive:
`sum DeltaH[r]*min(r,1) = 5994`. Thus the usual sufficient concavity/majorization
test does not establish such a uniform order. The endpoint signs above are
established directly, with negative profile differences propagated correctly.

## Reproduction and limits

From the repository root, with Python 3.12 or later and the standard library:

```sh
python3.12 -O -B research/normal45-owner-cost-bridge/moments.py
python3.12 -O -B -m unittest discover -s research/normal45-owner-cost-bridge -p test_moments.py -v
```

The first command reads saved profiles and writes the certificate only to
stdout. The enclosing raw-ownership checker must call the three-argument API
with its reconstructed complete profile. Neither command writes a receipt,
changes any source input, dispatches a job or accesses the network. The controls
use `ValueError` checks and `unittest` methods, which remain active under `-O`.
Tests compare rational square/cube/seventh-root enclosures by exact integer
powers and exercise interval precision, complete-bill omission, the full guarded
comparator, domain errors and inconclusive intervals.

Covered domain: these exact finite T74 histograms and parameters, with the
enclosure functions proved for positive integer counts, ranks 1..72, positive
integer stock and `0<=b<=1`. This is a written arithmetic proof with executable
exact checks; it is not a formal-kernel proof. Arbitrary dirty-input operator
identities, literal restoration, ownership realization, private namespaces,
physical placement and all live storage, prefix/coefficient access, precision,
all-size compilation, native supplier compatibility and outer assembly remain
distinct obligations of their respective constructions and auditors.

Credit for the moment convention and source endpoints follows the pinned
package's notices: Jeremy Diviney (PR2908), Mason Hale (PR2917), and Marius-Paul
Dumitrean (PR2930 comparator and PR2942 four paired extractions/allocation),
with their supplier, frame, flow, owner-engine and audit predecessors credited
in `inputs/CREDITS.md` and `inputs/NOTICE`. This independent binomial arithmetic
does not rerun or endorse their complete native/outer release receipts.

The enclosing package connects this bill to independently checked raw frame
words, chronological whole-helper ownership and residual children, including
the rank14 remainder. Open next question: connect that finite combinatorial
invoice to independently checked native operators, physical placement, all
live storage, prefix/coefficient access and precision under the intended outer
interface. Those stronger claims require their separate evidence; this moment
check and the enclosing finite invoice cannot alone resolve them.
