# A rounding margin for ordinary generators of Gaussian tensors

**No new kappa. A quantitative representation theorem, with no runtime or
general circuit lower bound and no foundational assumption discharge.**

The predecessor determined exact ordinary displacement rank for flattened
Gaussian tensors. Exact rank alone can be destroyed by rounding. This
package proves an explicit approximation margin and shows that it costs
only `O(g log p)=o(p)` guard bits in a source-compatible grouped regime.
Consequently Cp-bit coefficient rounding cannot remove the ordinary
generator obstruction there, even when the perturbation is unstructured.

## Exact result

For H=`A tensor B`, A invertible m-square and B a normalized shifted Gaussian
Toeplitz section of size n>=3 with |s|<=1/2, the selected 2m-square Stein
minor has an explicit block inverse. If `U>=||A||`, `V>=||A^-1||`, then

\[
 K=V\left(\frac m{b_{-1}}+\frac m{b_1}\right)
   +\frac{2UV^2m^2}{b_{-1}b_1}
\]

bounds its inverse norm. Any linear matrix X with `||X-H||<1/(2K)` needs
at least 2m ordinary lower-times-upper Toeplitz generator terms.

For a tensor H of invertible Toeplitz factors, bounds `U0>=||H||` and
`V0>=||H^-1||` give

\[
 K_{\rm inv}=\max(K,U_0)(1+U_0)^2(1+V_0)^2.
\]

Every approximation to the inverse with error below `1/(2K_inv)` has the
same generator lower bound. The inverse argument uses two exact Schur
factorizations and tensor persymmetry; it does not assume the inverse is
Toeplitz. [PROOF.md](PROOF.md) supplies the complete all-size proof.

The result is a lower bound on the minimum exact representation length of
the approximate matrix. An unstructured perturbation can increase rank;
the theorem says it cannot reduce it below `2T/n_fast` at this accuracy.

## Uniform source-compatible precision

Fix positive c0,C0,c1,xi and `0<=beta<1`. Suppose

\[
 g\le p^\beta,\quad 2\le n_i\le p^\xi,\quad n_{\rm fast}\ge3,
 \quad \frac{c_0}{\ln p}\le\gamma_i\le C_0\ln p,
 \quad1-2|s_i|\ge c_1p^{-2}.
\]

The retained accretive-symbol bound, restated with attribution, gives
one-factor norms and inverse norms bounded by fixed powers of p, uniformly
near the half-shift boundary. Thus `log K` and `log K_inv` are
`O(g log p)=o(p)`.

The proof gives explicit constants. With
`M0=4+pi^2/(3c0)` (or any larger value) and
`L=3xi+3+4M0+4C0`, entrywise rounding is protected when

`Cp > 7 + L g log2(p)`.

If the individual factor tables are rounded first, telescoping and the
Neumann inverse bound protect both their tensor and the tensor of their
exact inverses under the sufficient condition

`Cp > 7 + (L+2+2M0) g log2(p)`.

Both hold eventually for every fixed beta<1 and C>0. A concrete narrower
example uses c0=C0=1, c1=1/8, xi=1, g<=sqrt(p), M0=8. Direct entry rounding
to p bits is protected for p>=2^20; per-factor table rounding is protected
for p>=2^22. The finite endpoint budgets are checked exactly. These are
examples of the normalized-core precision regime, not substituted selected
outer parameters or a practical cutoff for its tiny exponent slacks.

The source relation is explicit: `CAPPED-GAUGE-AUDIT.md` states
`a=Theta(log p)` and sublinear grouped axis count; `GAUGEFREE-INTERIORS.md`
has narrow `gamma=a rho`, broad `gamma=(pi^2/a)lambda`, and polynomial
caps. Its fine-prime adaptation gives a shift gap at least `1/(8p^2)`.
These satisfy the stated uniform regime for fixed constants. Paid diagonal
gauges, actual Reference matrices, holes and physical source conversion
remain separate obligations.

## Base, predecessor and provenance

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
The selected record and review, original task card and source sections have
exact Git-blob/SHA256 pins in [SOURCES.json](SOURCES.json). They are historical
provenance. There are no external runtime inputs.

The published predecessor is
[tensor-gaussian-displacement-rank at 326844a](https://github.com/CubeJerry/integer-mult-bounds/tree/326844a3e0c570fdafa4f3737095cd37154743a6/research/tensor-gaussian-displacement-rank),
on `research/tensor-gaussian-displacement-rank-20261114`.
The quantitative inverse-minor bound, stable approximation conclusion and
Cp-bit bridge are the additions here. The required boundary algebra is
restated and the verifier is standalone; it does not require the unmerged
predecessor commit to be present in a clean checkout. Its small rational
matrix utilities retain predecessor credit.

The selected #7000 value remains `363005817/100000000000`, conditional on
all five retained assumptions. This is an analytic-recovery representation
audit, not a completed grouped recovery service.

## Reproduce and executed checks

```sh
python3 -I -W error -B research/gaussian-generator-rounding-margin/verify.py
python3 -I -O -W error -B research/gaussian-generator-rounding-margin/verify.py
python3 scripts/research_package.py --package research/gaussian-generator-rounding-margin --check-only
python3 scripts/research_package.py --package research/gaussian-generator-rounding-margin
```

Both standalone commands were executed in Python 3.12.14 and return the
same `PASS` JSON. The registered hook declares Python 3.12 and no third-party
requirements. Checks use explicit exceptions, so optimization cannot remove
them.

The bounded domain is 27 arbitrary-A fixtures with `1<=m<=3`, `3<=n<=5`,
seed 642, and three rational Gaussian choices at each size. Two choices
approach opposite half-shift boundaries at rational distance `2^-20` in the
shift multiplier. Six tensor dimensions are `(3)`, `(4)`, `(2,3)`, `(3,3)`,
`(2,4)`, `(2,2,3)`.

The replay checks 39 exact rational positive-semidefinite certificates for
nonzero singular-value gaps, 39 protected unstructured perturbations,
39 direct entry roundings, and six factor-table roundings covering twelve
forward/inverse targets. Literal block inverses, geometric inverse norms,
both Schur factorizations and tensor error bounds are checked. Four explicit
precision budgets and the factor-rounding endpoint are evaluated with
integers. The universal proof, not these fixtures, establishes all sizes.

Six failure controls are substantive: the shifted two-point geometric bound
fails; coarse rounding reduces rank; a forged singular-gap certificate is
rejected; a zero-diagonal indefinite matrix is rejected; beta=1 is excluded
from the sublinear guard argument; and zero half-shift gap is excluded from
the uniform source conditioning estimate. The last two are scope controls,
not general impossibility claims.

## Limitations

This does not bound runtime, arbitrary regrouping, tensor circuits, arbitrary
coordinate permutations or nonlinear algorithms arising from rounding data
during arithmetic. It does not transfer an exact normalized-core calculation
through unpaid gauges, periodic tails, holes or source access. The shifted
two-point case is excluded from the polynomial geometric shortcut; its
exact rank result remains valid.

## Open next questions

The [structured next questions](TASK.json) ask for a quantitative extension
through the actual paid gauges, the effect of arbitrary coordinate
permutations, and a grouped multilevel algorithm with a complete physical
budget. Each requires a distinct source-bound argument; this theorem does
not settle them.

## Credit

Prepared for @CubeJerry with substantial OpenAI ChatGPT assistance. The
research worker derived the quantitative bounds and the orchestrator
independently checked the inverse Schur/singular-value argument. Preserve
the published boundary-minor package's credit, Vlado Vojdanovski's
capped-phase-fusion work, the fractional-shift source and Chafik Boukhalfa's
fine-prime work (#1786). The accretive symbol argument is retained source
material, with [NIST DLMF 20.5.9](https://dlmf.nist.gov/20.5.E9) as primary
background for the product identity. New files are Apache-2.0.
