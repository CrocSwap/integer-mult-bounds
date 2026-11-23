# Independent review of the uniform dyadic mass enclosure

## Decision and reviewed boundary

**Accepted as a source-bound numerical lemma and its stated production
application.** I independently checked the algebra against the complete
`Measure` implementation and the three mass call sites in `Plan`, then
checked the production grades and the `Recipe.open` / `Plan` constructor
bindings against authenticated source. This review is model-assisted
mathematical review with independent exact checks, not a proof-assistant
certificate or a human review.

The reviewed proof is `mass/PROOF.md`, SHA-256
`b92516aaa39192c6713654fa6f41b4c4f8367b1f71c7e374b95fd31687464c1b`.
The literal source is Ali Romman's #8042 `transport.py`, SHA-256
`98bdb540233794338b426d1b0d0e72cff7fcbbd08be702af0d81e237dbecaae9`.
The source and original transfer proof retain their attribution. The
review does not claim that the source's enclosure assertion was new.

The theorem applies to rational `x`, rational mass endpoints and rational
nonnegative volume, reduced dyadic `0<t<=1`, and an integer precision
`p>=0`. These are hypotheses of the review; the API does not validate all
of them. In particular `x>=1` is essential to the simple bounded-product
error estimate. The proof's initial wording was clarified to state the
rational API domain explicitly before this acceptance.

## Algebra checked independently

Write `t=k/2^d`, `g=2^p` and `y_j=x^(-1/2^j)`. There are exactly `d+1`
iterations. The first numerator bit read is bit `d`, not bit zero. The
selected product therefore has exponent
`sum_j bit_(d-j)(k)/2^j=k/2^d`. This also covers `t=1`, for which `d=0`
and no square-root update occurs.

The initial interval is the exact directed rounding of `g/x`. Because
`x>=1`, both integer endpoints are in `[0,g]`, and the upper endpoint is
at least one. For an integer `n>=1`, `isqrt(n-1)+1` is precisely
`ceil(sqrt(n))`, including when `n` is a perfect square. Consequently the
source's upper update is valid even at `x=1`; all its square-root inputs
are defined. The lower endpoint may be zero and can remain zero throughout.
That is a valid enclosure, not an exceptional failure of the proof.

Let `a_j/g <= y_j <= b_j/g`. The relative base errors satisfy

\[
0\le 1-a_j/(g y_j)\le1,\qquad b_j/(g y_j)-1\ge0.
\]

Taking a square root does not increase these errors: the lower statement
uses `1-sqrt(1-u)<=u` on `[0,1]`, and the upper statement uses
`sqrt(1+u)-1<=u` for all `u>=0`. Rounding the new root adds at most
`1/(g*y_(j+1))<=X/g`. Thus each base's relative error is at most
`(j+1)X/g`. This argument does not require that this displayed bound be
less than one or that the rounded lower endpoint be positive. Since
`y_j<=1`, the same number also bounds absolute base error.

For the accumulated products, write `l<=Y<=h` and `a<=y<=b`, with all
six real quantities in `[0,1]`. The identities

\[
Yy-la=y(Y-l)+l(y-a),\qquad
hb-Yy=h(b-y)+y(h-Y)
\]

show that either error increases by at most its previous value plus the
corresponding base error. The source then adds less than one grid unit
through directed multiplication rounding. Summing over the selected bits,
or more conservatively over all `d+1` possible bits, proves the stated

\[
E_d(X)=\frac{(d+1)(d+2)}2X+d+1.
\]

This avoids a derivative estimate near a small reciprocal and avoids an
unjustified relative-error estimate for a zero lower product.

Subtracting the right endpoint interval from the left endpoint interval
adds at most two copies of `E_d(X)/g` in either directed error. Multiplying
by `V/t>=0` preserves orientation. If the raw lower difference is negative,
clamping it to zero reduces its gap from the nonnegative true mass.
The result is exactly the claimed one-sided error
`Delta=2V E_d(X)/(t g)`.

For `right<=left`, the literal routine returns `(0,0)` before calling
`inverse_power`. The relevant object is the empty-intersection mass, zero;
the theorem does not identify this return with an oriented negative
integral. Degenerate endpoints and zero volume have the correct behavior.

If `Delta<1/4`, ceiling the upper enclosure gives a count at least the
true mass and less than `5/4` above it. Flooring `pi` times the lower
enclosure gives a nonnegative allocation at most `pi` times the true mass,
with loss less than `1+pi*Delta<=5/4` for `0<=pi<=1`. In `Plan`, positive
cells and the complete probability-row check imply each per-port share is
at most one. No approximate probability or unspecified rounding is used.

## Actual production binding

`PRODUCTION-BINDING.json` records the separately reconstructed source
grades, their hashes, and literal constructor-expression evaluation. The
Gaussian graph and layout were authenticated before calling the original
grade construction, and the binary source and caller authenticate their
own retained artifacts. The source's `source_ranks` function was extracted
unchanged and applied to those authentic Gaussian grades.

| Installation | Actual ambient | Largest target | Smallest paid grade | Exponent denominator |
|---|---:|---:|---:|---:|
| Gaussian, two scales | 1,224 | 1,032 | 1/2 | `2^29` |
| Binary | 134 | 127 | 1 | `2^60` |

Both literal exponents exceed `1/2`; the Gaussian exponent also exceeds
`3/4`. The grade inventory contains 105,216 Gaussian targets and 564,144
paid labels, and 18,906 binary targets and 104,904 paid labels. These
inventories bind the maximum grade ratio, not an execution of a large
calendar or a physical-memory claim.

For each actual installation, the unchanged `Recipe.open` method was
called with a capture function standing in for `Plan`. The returned
arguments confirm `N=2^rank_log`, `L=2^15`,
`U=2*floor(N/(2048*ambient))<=N`, volume `N^6`, and the correct `t`.
The exact `Measure(...)` expression extracted from the actual `Plan`
constructor was then evaluated on those captured arguments; at
`rank_log=1024` it selects precision 65,600. This establishes the bindings
without constructing a production-size calendar or using a substitute
constructor. The all-size statement `g>N^64` follows directly from
`N<2^N.bit_length()`.

The three literal source call forms are covered as follows.

1. A direct bin `[e,e+2]` lies in `[L,U]` because `e` ranges from `L` to
   `U-2` in steps of two.
2. An interior call is clipped to the same bin. If it is nonempty, both
   endpoints lie in `[L,U]`; if empty, the source returns zero immediately.
3. An exterior call has right endpoint `(e+2)*k/r`. The authentic
   `k<=1032`, `r>=1/2` give this endpoint at most `2064U<=2064N`.
   The left endpoint is at least `U>L>1`; if it exceeds the right endpoint,
   the empty-interval branch again applies before any inverse-power call.

Thus every nonempty call is in the asserted domain with `X=2064N`.
Unrestricted user-created `Plan` values are outside this production
corollary. In particular changing volume or grade ratios without changing
the error calculation is not licensed by the theorem.

For `d<=60`,

\[
E_d(2064N)\le3903024N+61<2^{22}N\quad(N\ge2).
\]

Together with `V=N^6`, `t>=1/2` and `g>N^64`, this gives
`Delta<2^24*N^-57<=2^-33<1/4`. All inequalities have the directions
needed for the count and allocation corollaries.

The bin-sum consequence also checks. The exact ideal masses telescope to
`V/t*(L^-t-U^-t)<=V/(t L^t)`. There are `(U-L)/2<U` bins. Summing the
strict error `<2` per bin therefore gives the advertised, deliberately
loose bound `sum_e count[e]<V/(t L^t)+2U`. This statement counts replicas;
it does not by itself count owners, bytes, schedules, pending loans or
temporary tapes. It discharges the named local bin-enclosure premise when
combined with the existing, independently proved census contracts.

## Independent exact oracle and evidence

`check_review.py` imports neither the author's checker nor its numerical
oracle. It executes the authenticated literal source, but its reference
values come from a different mathematical construction. For rational
perfect-power cases it uses monotone integer-root bisection. Otherwise it
normalizes `x=2^m q` with `1<=q<2` and bounds

\[
\log q=2\sum_{j=0}^{109}\frac{z^{2j+1}}{2j+1}+R,
\qquad z=(q-1)/(q+1),\quad
0\le R\le\frac{2z^{221}}{221(1-z^2)}.
\]

It then bounds `exp(t log x)` using a positive Taylor series through degree
64 after scaling the argument into `[0,1/4]`. The tail is at most the
degree-65 term divided by `1-a/66`; repeated squaring and reciprocation
preserve interval orientation. Every calculation is rational, with
directed rounding to a 384-bit grid only to limit fraction growth. This
oracle does not use `isqrt`, source bit traversal, or the source's repeated
square-root products.

The strict replay passed 600 inverse-power cases (including 216 zero-lower
returns), 1,080 mass cases, 360 empty intervals, and 1,320 directed
allocation checks. It includes both production exponents, `t=1`, `x=1`,
precision zero, fractional endpoints, nonintegral rational volume and a
very small exponent with denominator `2^60`. It rejected four literal
source mutations: downward upper-root rounding, reversed bit order,
downward upper-product rounding, and upward lower-root rounding. Witnesses
are retained in `EVIDENCE.json`.

These finite checks independently stress the claim and error directions;
the universal proof above and in the reviewed document establishes the
all-input statement. No production-size calendar was executed, no integer
recovery theorem follows from the tests, and the canonical
`analytic_recovery` assumption and selected multiplier exponent are
unchanged.

## Replay

```sh
python3 -I -W error -B norm/mass-review/check_review.py \
  --source /workspace/scratch/5b0914ccc34e/work-storage/runtime-exact/transport.py \
  --proof /workspace/scratch/e64488edfaad/mass/PROOF.md
python3 -I -W error -B norm/mass-review/bind_production.py
```

The binding command needs the retained local runtime and authenticated
stock artifact paths declared at the top of that script. The mathematical
review and receipts are standalone; this replay requirement is explicit.
Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
