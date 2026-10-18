# Exact coverage relief boundary for the selected local word

**A complete two-parameter boundary for one optimistic relaxation. No new
supplier, physical contract, or \(\kappa\) is claimed.**

## Scope and result

This package answers the `(u, c)` portion of the explicit open question in
[`complex-coverage-law-relief`](../complex-coverage-law-relief/README.md): find
the exact combined boundary at the chosen saving target \(a=1/99\). It refines
the catalogue's `coverage-law-change` task to the pricing question, holding the
selected local word, width, nine-stage template, family count, and rank cap
fixed. It does not propose or implement a changed template.

Let \(u\in[1,3]\) be the average number of unpaid coordinates per live family,
\(c\in[0,64]\) the centre charge per call, and \(w=896/9\) the families per
call. For every point in this rectangle, the coverage model is admissible:
the deficit \(uw-c\ge 320/9>0\), and idle mass is at least
\(12446/9>0\). The paid word stays fixed at
\(\{1:2412,2:418,3:432,4:142,5:82,8:8\}\), with rank mass 5586. The outer
halving guard gives maximum idle rank \(R=51\), since
\(73^2>2\cdot51^2\) but \(73^2\le2\cdot52^2\).

Define the exact real constants

\[
G=\sum_{r\in\{1,2,3,4,5,8\}}n_r(r/73)^{98/99},\qquad
p=(51/73)^{98/99}/51.
\]

For the favorable fractional relaxation, all idle rank mass can be put into
rank-51 children. Its moment at \(a=1/99\) is

\[
\rho(u,c)=\frac{G+p\big((73-u)w+c-5586\big)}{w}.
\]

The **exact** boundary is the line

\[
c_*(u)=5586-(73-u)w+(w-G)/p,
\qquad
\rho(u,c)-1=\frac{p}{w}\big(c-c_*(u)\big).
\]

Thus, throughout the stated rectangle, \(\rho<1\) exactly below this line,
\(\rho=1\) on it, and \(\rho>1\) above it. Equivalently,

\[
c_*(u)=64+\frac{896}{9}(u-u_{64}),
\]

where \(u_{64}\) is the unique unpaid-coordinate value at which the boundary
meets \(c=64\). Certified rational intervals give

| Boundary point | Certified interval |
|---|---:|
| \(u_{64}\), where \(c_*(u)=64\) | \((2.804078009,\;2.804078010)\) |
| \(u_0=u_{64}-9/14\), where \(c_*(u)=0\) | \((2.161220866,\;2.161220867)\) |
| \(c_*(1)\) | \((-115.605988495500,\;-115.605988495499)\) |
| \(c_*(2)\) | \((-16.050432939945,\;-16.050432939944)\) |
| \(c_*(3)\) | \((83.505122615611,\;83.505122615612)\) |

For example, at \(u=2\), every allowed \(c\ge0\) is above the line and fails
the target in this relaxation. At \(u=3\), every allowed \(c\le64\) is below
it and passes the relaxation. The original \((u,c)=(1,64)\) also fails. These
are statements about the fixed word and the parameters above.

## Why the boundary is exact

At positive \(a=1/99\), one unit of rank mass in a rank-\(r\) child costs

\[
\frac{(r/73)^{1-a}}{r}=73^{a-1}r^{-a},
\]

which strictly decreases with \(r\). Therefore among all fractional idle
histograms with ranks at most 51, rank 51 minimizes cost per unit mass. The
idle mass is exactly \((73-u)w+c-5586\), so this minimum is the formula
\(\rho\) above. Rearranging \(\rho-1\) gives the line identity; no sampled grid
is used to infer the continuum boundary.

Every allowed child rank is below 73, so its cost strictly increases with
\(a\). Also

\[
\rho_{a=0}(u,c)=1-u/73+c/(73w)\le1-5/1022<1.
\]

Consequently the relaxed packing ceiling has a unique root: below the line it
is strictly greater than \(1/99\), on the line it equals \(1/99\), and above
the line it is less. The interval endpoints in `RESULT.json` are exact rational
outward bounds, computed from the predecessor's pinned atanh/Taylor interval
engine. The proof-relevant constants \(G\) and \(p\) are defined exactly above;
their decimals are certified enclosures, not floating-point estimates.

## Verification

From the repository root:

```sh
python3 -B research/coverage-law-relief-pareto/verify.py
python3 scripts/research_package.py --package research/coverage-law-relief-pareto --check-only
python3.12 scripts/research_package.py --package research/coverage-law-relief-pareto
```

The verifier authenticates the two predecessor inputs, checks the fixed model
and all domain constraints, certifies both line-intersection brackets by the
source model's exact interval comparisons, and compares the affine formula
with the full relaxation on all 195 integer points \(u\in\{1,2,3\}\),
\(c\in\{0,\ldots,64\}\). This finite grid is a regression check; the proof
for all real \((u,c)\) in the rectangle is the algebraic identity and
monotonicity argument above. `verify.py --write` explicitly regenerates the
receipt; ordinary replay is read-only and compares against `RESULT.json`.

## Limits and current research state

The conclusion is a **necessary screen for every construction** obeying this
fixed profile, coverage identity, and rank cap: if \(\rho>1\), even the
fractional best case misses \(1/99\). A point with \(\rho\le1\) is only
optimistically affordable; this does not show an integer idle histogram,
template, endpoint contract, dirty-input implementation, restoration schedule,
or complete supplier exists. The original coverage-law question therefore
remains open. The selected record and \(\kappa\) are unchanged.

The advisory overlap search at 2026-10-17 21:39 UTC covered 361 open PRs and
2,159 discussion records with complete pagination. The live issue list had no
open issues at that snapshot. It returned no open-PR match
on this specific \((u,c)\) boundary. Discussion #1587 matched the broad card
terms, but its latest reported result concerns C5 physical-core charging, a
different predicate. The search does not inspect arbitrary code diffs, closed
PR bodies, or unpublished work, so it is not a novelty guarantee. The nearby
P112 and C5 work was not used as evidence for this result.

## Open next questions

1. **Can a concrete template or endpoint contract realize any point on the
   passing side while meeting dirty-input, restoration, hosting, and consumer
   obligations?** This is needed before optimistic affordability can affect a
   supplier. First step: name one complete contract and check its data endpoint
   on arbitrary dirty inputs, then price its complete bill against this line.
   Blocked by the absence of a proposed replacement contract in this scope.
2. **What is the combined \((F,s)\) frontier for family count \(F\) and local
   word scale \(s\)?** This is a separate lever pair listed by the predecessor.
   First step: derive its exact affine budget at the same target from the
   coverage identity. Blocked until a comparable template and scaled local
   profile are fixed.

## Credit

The coverage identity and moment model retain the attribution in PR1012/PR1240.
The pinned predecessor package and its interval engine are by Navinor with
OpenCode assistance; this result depends on, and preserves, that attribution.
The new proof and bounded verifier were prepared by the OpenAI Codex research
agent. No independent human or proof-assistant review is claimed.
