# A near-optimal parameter-only refinement of the paired witness

By Aurel Prosz (Paureel), developed in the “Improve Integer Mult Bounds” project
with assistance from OpenAI ChatGPT and integrated with assistance from OpenAI
Codex, 7 October 2026. Conditional on the existing paired-network,
nonadjacent-routing, stopped-guard, tight-Gaussian, and upstream algorithmic
interfaces. This is not an independent proof of the integer multiplication
algorithm and does not introduce a new finite network.

## Result

Retain the declared exponents from `scripts/paired_network.py`:

$$
a=1-\tau=\frac{296}{10^{11}},\qquad
b=1-\sigma=\frac{1}{10^{11}},\qquad h=50.
$$

Here the letter $b$ denotes the complex exponent saving. It is not the
manuscript's input-length parameter also named $b$.

The proposed conditional bound is

$$
T(n)=O\!\left(n(\log n)^{1-\kappa}\right),\qquad
\kappa=\frac{17523184}{10^{25}}=1.7523184\times10^{-18}.
$$

This is a factor **1.0101427831391313610145792** larger than the repository's
newer dyadic witness $2^{-59}$, an improvement of
**1.01427831391313610145792% in the exponent saving**. It is not a measured
runtime improvement. The fair incremental baseline is the margin already
supported by the preceding paired parameters:

$$
G_{\rm old}=0.199\cdot0.999\cdot a^2
=1.7418148416\times10^{-18}.
$$

The proposed advertised saving exceeds this margin by approximately **0.6030238%**.
The 1.014% comparison includes the preceding witness's unused headline slack.
Most of the cumulative gain over the original manuscript belongs to the earlier
constructions. This is a conditional technical refinement, with no global
novelty or priority claim.

## Explicit rational parameters

Set

$$
\begin{aligned}
\beta&=\frac{99999912384}{10^{11}}=0.99999912384,\\
\epsilon&=\frac{1999999999999}{10^{13}}=0.1999999999999,\\
\delta&=10^{-14},\qquad C_1=2,\\
c&=\beta a,\\
\lambda&=1-\frac{1+\beta}{2}a^2,\\
\lambda'&=1-\beta a^2.
\end{aligned}
$$

The new values keep $\tau,\sigma,h$ and the finite circuits unchanged.
The original paired parameter recipe is retained, with its stopping exponent,
dimension exponent, and positive scalar-cost slack moved closer to their
joint admissible boundary.

The seven existing margins are

$$
\begin{aligned}
g_1&=1-\epsilon(1+c),&
g_2&=\epsilon ca,&
g_3&=\epsilon(1-\lambda'),\\
g_4&=a(1-\epsilon),&
g_5&=\frac14-\delta-\frac54\epsilon,&
g_6&=1-\delta-\epsilon,&
g_7&=\epsilon.
\end{aligned}
$$

Exact rational calculation gives

$$
\begin{aligned}
G=\min_i g_i=g_2=g_3
 &=1.7523184646864326407676563456\times10^{-18},\\
G-\kappa
 &=6.46864326407676563456\times10^{-26}>0.
\end{aligned}
$$

Thus the final logarithmic absorption has a strictly positive margin.
In particular, neither $\lambda$ nor $\lambda'$ should be represented
using ordinary binary floating-point arithmetic: their deficits from one
are much smaller than machine epsilon.

The three delicate recurrence checks simplify to

$$
\begin{aligned}
\lambda-\tau(1+c/\beta)&=\frac{1-\beta}{2}a^2>0,\\
\lambda'-\lambda&=\frac{1-\beta}{2}a^2>0,\\
\lambda'-[\sigma+\beta(1-\sigma)]
  &=(1-\beta)b-\beta a^2>0.
\end{aligned}
$$

The last inequality is essential. Moving $\beta$ arbitrarily close to
one while holding the two motif exponents fixed would eventually violate
it. Retuning $\epsilon$ without shrinking $\delta$ would also fail:
the old $\delta=10^{-4}$ is incompatible with the new $\epsilon$.
Both failures are regression tests in this add-on.

## Guard and Gaussian dependencies

The stopped-depth argument accepts $\beta\ge9/10$. For these parameters,

$$
5-4\beta=1.00000350464,\qquad
5-4\beta+\frac12=1.50000350464<2.
$$

The independent numerical checker re-evaluates the unchanged $h=50$
complex counting formulas, $2\le s_c<m^5$, its positive residual deficit,
and the constants used in the repository's stopped-guard certificate.
This confirms the numerical applicability of $C_1=2$; it does not prove
the construction to which those formulas refer.

With the existing tighter Gaussian choice, its exponent is

$$
\frac12+\frac32\epsilon=0.79999999999985<\frac45.
$$

A useful simplification avoids enormous integer powers when checking the
stated finite cutoff. Denote the manuscript's input-length parameter by
$B_0$. Since $184<256=2^8$, for $B_0\ge2^{40}$,

$$
\gamma<46 B_0^{1/2+3\epsilon/2}
 <46 B_0^{4/5}<B_0/4.
$$

The last comparison follows from $B_0^{1/5}\ge2^8>184=4\cdot46$.
This preserves the earlier rounding requirement, including its factor of four,
using small exact comparisons.
The Gaussian margin is $g_5=1.15\times10^{-13}$, much larger than $G$.
All thirty strict numerical side conditions in the repository's revised
parameter system pass in the independent checker.

As with the original asymptotic construction, the new rational powers
are fixed. For example, computing $d=\lfloor B_0^\epsilon\rfloor$ uses
integer comparisons
$d^{10^{13}}\le B_0^{1999999999999}$. These are fixed exponents, so the
setup remains polynomial in the logarithmic input-size parameter. No
claim of practical efficiency is made for those constants.

## Exact supremum for the declared motif exponents

This section allows all admissible $\beta,c,\lambda,\lambda',\epsilon,\delta$
under the existing nonadjacent, stopped-guard, tight-Gaussian inequalities,
while fixing $a=296/10^{11}$, $b=1/10^{11}$, and $C_1=2$.
It is not an optimality claim about other motif exponents or networks.

Let

$$
z=\min\{ac,1-\lambda'\}.
$$

The packed-overhead and leaf inequalities imply

$$
z<\frac{\beta a^2}{1-a+a\beta},\qquad
z<(1-\beta)b.
$$

To see the first inequality, use $c\ge z/a$,
$1-\lambda'\ge z$, and
$\tau(1+c/\beta)<\lambda<\lambda'$. Rearrangement gives
$z(1-a+a\beta)<\beta a^2$.

The first upper bound is strictly increasing in $\beta$; its derivative is
$a^2(1-a)/(1-a+a\beta)^2>0$. The second bound is strictly decreasing.
Their crossing has $\beta\ge9/10$, because
$a^2<b/10$. The supremal capacity is the smaller positive
root $z_*$ of

$$
\boxed{a z_*^2-(b+a^2)z_*+a^2b=0.}
$$

Equivalently, a numerically stable expression is

$$
z_*=
\frac{2a^2b}
{b+a^2+\sqrt{(b+a^2)^2-4a^3b}}.
$$

Because $G\le\epsilon z$ and
$G<1/4-(5/4)\epsilon$, maximizing over $\epsilon$ yields

$$
\boxed{G_* = \frac{z_*}{5+4z_*}.}
$$

This upper bound is a supremum, not an attained maximum. For an
approaching family, choose the crossing $\beta_*$, take positive
$z<z_*$ approaching it, put $c=z/a$, $\lambda'=1-z$, and select
$\lambda$ strictly between
$\max\{\tau,\sigma,\tau(1+c/\beta_*)\}$ and $\lambda'$.
Choose positive $\delta\to0$ and

$$
\epsilon=\frac{1/4-\delta}{5/4+z}.
$$

This balances the Gaussian and recurrence margins. In a sufficiently
small neighborhood of the limit, the other margins and side conditions
remain strictly positive with much larger slack. Their exact limiting values
use

$$
\epsilon_* = \frac{1}{5+4z_*}<\frac15,\qquad
c_* = z_*/a<a,\qquad
g_{4,*}=a(1-\epsilon_*)>\frac{4a}{5}.
$$

In particular, $z_*<a^2<\min\{a,b\}$ keeps $\lambda'_*=1-z_*$
strictly above both $\tau$ and $\sigma$. The guard and prime-interval
slacks exceed $3/5$, the dimension slack exceeds $2/15$, and the
alpha and gamma slacks exceed $1/5$. The remaining cost margins obey
$g_{1,*}>(4-a)/5>G_*$, $g_{6,*}>4/5>G_*$, and
$g_{7,*}=\epsilon_*>\epsilon_*z_*=G_*$. Also
$g_{4,*}>4a/5>a^2/5>G_*$. Thus these conditions do not lower the
supremum. Rational approximations inside this open feasible
region attain the same supremum with fixed rational parameters.

The supplied checker encloses $z_*$ with 160 exact bisections on
$[0,a^2]$. The polynomial is strictly decreasing there, positive at
zero and negative at $a^2$. Consequently its sign certifies every
bisection step without a floating-point square root. This gives

$$
G_*\approx1.7523184646886585106200710664\times10^{-18}.
$$

The explicit advertised $\kappa$ exceeds **99.999996%** of this
supremum. The same enclosure proves $G_*<2^{-58}$ in this fixed-exponent
parameter problem. Improving the finite-network exponent, the recurrence
inequality, or the assembly cost changes this optimization problem and
is not excluded by this result.

## A concrete next-network target, not an achieved improvement

The same h=50 counting formula is

$$
\eta_{\rm bit}=\frac{v-6h^2}{2h^3(v+R+h)},\qquad v=\binom h3,
$$

where $R$ is the side-role count per invocation. Under the same circuit
and frame interface, **R <= 356295** would suffice to certify
$a=4.17\times10^{-9}$, using the existing upper bound
$\log(h^3)<11.737$.

With that stronger bit exponent, set $\beta=0.999998$,
$\epsilon=0.1999999$, $\delta=10^{-8}$, and use the same formulas
for $c,\lambda,\lambda'$. All numerical downstream inequalities pass,
and their minimum margin would be

$$
3.47777130555347778\times10^{-18}>2^{-58}.
$$

The checker records this as an **unachieved design target**. No circuit
meeting that budget and its frame conditions is supplied. This separates
a useful quantitative goal for further circuit work from the actually
verified parameter improvement above.

## What the files verify

`python3 scripts/tune_paired_parameters.py --output /tmp/paired-tuned-standalone.json`
is self-contained and uses only
Python's standard library. It checks the thirty exact parameter slacks,
seven margins, strict absorption gap, unchanged complex count and guard
constants, the Gaussian cutoff, and the fixed-exponent capacity enclosure.
It explicitly records that the paired bit circuit has not been rerun.

`python3 scripts/tune_paired_parameters.py --upstream` also calls the existing
`paired_network.certificate()`. That certificate checks the repository's
bit circuit, frames, and pinned source hashes. The adapter then submits the
new parameters to `certify.certify_parameters()` and requires exact equality
with this add-on's independently computed slacks and margins. It also calls
the existing guard checker with the new stopping exponent.

The default mode cannot certify that the circuit meets its sufficient
side-role budget of 509975. It records that budget as an assumption to be
checked by the optional integration, not as a verified circuit count.

The original chat package was prepared with twenty-three numerical regression
tests and without access to a complete checkout. This repository integration
reconstructs the checker from that audit, adds feasibility-boundary and supremum
tests, and integrates it into `make verify` with the real paired verifier.
The checked-in certificate uses `--upstream`, rather than standalone mode.

`scripts/make_tuned_paired_patch.py` generates
`patches/h50-paired-tuned.patch` against the unchanged pinned manuscript,
including all inherited paired, routing, guard, and Gaussian dependencies.
It also updates the exact rational stopping and dimension comparisons and
retains the strict logarithmic absorption gap. `make verify` regenerates the
certificate and patch, runs the complete test suite, and checks all alternative
patches. The inherited PDF describes the original paired construction; this
Markdown audit describes the new parameters and scoped supremum.

Local integration verification on 7 October 2026, using Python 3.12.14:
`make verify` passed all 103 tests, including 18 new refinement tests, and
all seventeen independent source-patch application checks. Regeneration left
the inherited certificates, patches, and pinned manuscript unchanged.
These checks validate the arithmetic and supplied finite interfaces; they do
not independently prove the complete multiplication theorem.

## Contribution review and dependency ledger

The contribution review checked the proposed parameters against the written
recurrence and assembly costs, rather than relying only on agreement between
two transcriptions of the numerical inequalities. Paths below refer to the
patched copy of the pinned manuscript, whose original files remain unchanged.

| Source anchor | Obligation under the new parameters | Review result |
| --- | --- | --- |
| `03-motifs.tex`, `eq:explicit-motif-exponents` | Retain declared bit and complex savings, paired graph, and frames | Both savings unchanged; paired coefficients, frames, and source hashes rechecked |
| `05-layers.tex`, Unrolling the recurrence | Internal exponent `tau*(1+c/beta)<lambda`; leaf exponent `sigma+beta*(1-sigma)<lambda-prime` | Both strict gaps checked exactly; `lambda<lambda-prime` absorbs the fixed logarithmic group count |
| `05-layers.tex`, `sec:stopped-guard` | `9/10<=beta<1`, `2<=s_c<m^5`, `2*epsilon<1` | All hold; the complex network and depth constants are unchanged |
| `07-resampling.tex`, `lem:no-sort-resampling` | Fixed `0<delta<1/8`, admissible width, and resampling separation | `delta=10^-14` is allowed; `alpha^4*theta_i>8*b>6*b=p` |
| `08-assembly.tex`, `eq:sizes` and rational setup | Fixed positive rational powers, `K=o(ell)`, superpolynomial `r`, and growing prime intervals | Strict growth margins remain positive; both exact integer setup and stopping comparisons are updated |
| `08-assembly.tex`, `eq:gamma` and final rounding | Keep `gamma<=b/4` beyond the declared cutoff and `p=6*b` | `gamma<46*b^(4/5)<b/4` for `b>=2^40`; precision and rounding proof retained |
| `08-assembly.tex`, `tab:costs` and `eq:margin-list` | Derive each exponent from `d`, `K`, `ell`, and `alpha` | A separate test reconstructs all seven cost powers from these factors; every power is strictly below `1-kappa` |
| `08-assembly.tex`, final absorption | Absorb remaining fixed powers of `log p` | Exact positive `rho=G-kappa`; `(log p)^C=O(p^rho)` for every fixed `C` |

The review corrected an exact limiting statement in the original audit:
`epsilon` approaches `1/(5+4*z*)`, rather than exactly `1/5`, and the limiting
layout margin is `a*(1-epsilon*)`, rather than exactly `4*a/5`. The supplied
supremum formula and explicit rational witness were already consistent with
the corrected limits. A regression test checks the exact balancing identity.

A disposable copy of the tuned manuscript patch was applied to the pinned
source. A flattened syntax preview compiled successfully with the desktop
LaTeX compiler. Only that preview omitted pdfTeX-specific metadata commands
and used bibliography labels in place of external BibTeX files; neither
adjustment is part of the contribution patch. Successful compilation is a
syntax check; it does not establish mathematical correctness.

## Source basis and attribution

The original audit inspected `CrocSwap/integer-mult-bounds` through public web
pages on 7 October 2026. This integration uses the complete checkout at CrocSwap
commit `bcd4ebde8692383539f8a48734e5fbf3a18a32c2`.
The repository's upstream manuscript is pinned to
`adc7f1241b42e322a6451854ab7e4b4c146bf78a`.

The formulas and conditional interfaces used here come from:

* `scripts/paired_network.py`: the declared paired exponent savings,
  prior parameter recipe, stopped guard, and tight Gaussian accounting.
* `scripts/certify.py`: the thirty strict conditions and seven margins.
* `scripts/shared_point_network.py`: the side-role rank-deficit formula.
* `scripts/search_network.py`: rational logarithm enclosures.

The base repository is by Douglas Colkitt, with assistance from OpenAI
Codex, and credits the OpenAI manuscript. This add-on does not imply
independent review, endorsement, priority, or an unconditional theorem.
