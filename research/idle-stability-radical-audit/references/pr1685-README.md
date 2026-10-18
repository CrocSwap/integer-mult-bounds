# Near-ceiling idle packing must concentrate at large ranks

**Scoped obstruction and exact unrestricted integer optimum. No new κ, supplier,
or selected-frontier change.** New work by Penguin (OpenAI) for Maximus Putnam,
Apache-2.0. Source hashes and base commit are in SOURCES.json.

## Model and results

Keep the selected complex local invoice, width m=73, W=14336 live families,
144 calls, coverage mass 72W+64N, and idle rank cap R=51. The residual idle
mass is M=237024. A child has cost f(r)=(r/m)^(1-a); its cost per unit mass is
c(r)=f(r)/r. The local cost L(a) is fixed. Only idle partitioning may change.
All results below are necessary conditions in this model, not realizability claims.

For 0<a<1, any accepted packing (total moment <=1) must obey

    mass in idle ranks <=K <= [W-L(a)-M*c(R)]/[c(K)-c(R)],  1<=K<R.

This is a quantitative stability refinement of the predecessor's fractional
packing ceiling. Near that ceiling, the allowable low-rank mass tends to zero.
At a=0.00169, the certified integer mass caps are:

| Maximum idle rank K | Necessary maximum mass at ranks <=K |
|---|---:|
| 1 | 24 |
| 3 | 34 |
| 7 | 48 |
| 16 | 83 |
| 32 | 208 |
| 48 | 1603 |

The selected idle histogram is `{1:2276, 3:377, 7:7, 48:4866}`.
Its entire idle mass is at ranks <=48. Thus reaching a=0.00169 with this
same local word requires moving at least **235421 of 237024 mass units
(99.32%)** above rank 48. Even its 3456 mass units at ranks <=7 exceed
the corresponding cap of 48. This identifies structural demands hidden by
an aggregate ceiling; it is not an algorithm for realizing such a packing.

The exact unrestricted integer optimum is `{51:4647, 27:1}`. This improves
the fractional relaxation by only about 2.78e-8 in normalized moment at
that target. Integer arithmetic alone scarcely closes the relaxation gap;
physical owner/hosting restrictions are the consequential next question.

At the selected published complex endpoint, the fractional moment is about
0.999957631192, the integer-optimal moment about 0.999957658715, and the
selected moment rounds to 1.0 in the display. Rounded displays are not sign
certificates. The predecessor's fixed-word cap remains
`a < 0.001690054109089`, with κ cap approximately 0.001687202646.
No packing gain or improved endpoint is claimed here.

## Proof 1: stability inequality

For a>0, c(r)=m^(a-1) r^(-a) strictly decreases with r. Split idle mass into
M_K at ranks <=K and the rest. Every unit in the first part costs at least
c(K), and every remaining unit at least c(R). Hence

    idle cost >= M*c(R) + M_K*[c(K)-c(R)].

Adding L(a), dividing by W, and imposing moment <=1 proves the bound.
If the numerator is negative, even M_K=0 is impossible; the calculator
rejects that case rather than dividing an outward numerator by a lower denominator. If it is zero,
all mass must be at R. At a=0, rank prices coincide and division is invalid;
the verifier rejects that use. A positive bound is necessary, not sufficient.

The implementation uses rational lower enclosures of L and c(R) in the
numerator, and a lower enclosure of c(K)-c(R) in the denominator, giving
an outward upper bound. Its floor is therefore a safe integer mass cap.

## Proof 2: exact integer optimum

For 0<a<1, f is strictly concave on [0,R], with f(0)=0. Given two positive
ranks x,y<R:

* If x+y<=R, concavity (or decreasing per-mass price) gives
  f(x)+f(y)>=f(x+y). Merge the children.
* If x+y>R, the function f(t)+f(x+y-t) is concave on [x+y-R,R].
  Its equal endpoint values are minima, so replace x,y by R,x+y-R.

Each replacement reduces the number of children whose rank is strictly
between 0 and R, and strictly reduces cost for the original interior pair.
After finitely many replacements there are only rank-R children and at most
one smaller child. Conservation of mass uniquely determines q=floor(M/R)
and s=M mod R. Thus q children of rank R and, if s>0, one child of rank s
are the unique optimum as a histogram. At a=0 all partitions tie; at a=1
strict concavity no longer applies. Neither endpoint is claimed by this proof.

No owner grouping, helper inventory, port compatibility or whole-call
hosting restriction is enforced by this optimum. Imposing those constraints
can only increase the minimum cost. Fractional local counts are not introduced.

## Evidence and reproduction

```sh
python3 -B research/idle-packing-stability/verify.py
python3 scripts/research_package.py --package research/idle-packing-stability
PYTHONOPTIMIZE=1 python3 -B research/idle-packing-stability/verify.py
```

Python 3.12, standard library only. `--write` regenerates RESULT.json.
The verifier checks source hashes, selected invoice equality and decomposition,
coverage mass, stability inequalities on the actual histogram at three savings,
and strict separation of its cost from the integer optimum. It enumerates
**11632** integer histograms across mass 0..24 and cap 2..7 at a=1/10,
checking every nonoptimal histogram against certified rational cost intervals.
Four rejection controls cover out-of-cap rank, wrong mass, fractional counts,
and zero-saving division. Runtime checks use explicit exceptions, not asserts.
Finite enumeration supports the implementation; the universal argument is above.

Exact pricing is explicitly **reused**, not independently reimplemented:
Douglas Colkitt / Claude's `complex-local-word-ceiling/ceiling.py`, with its
atanh log chains and bounded Taylor exponential. All transitive proof-relevant
inputs are declared in VERIFY.json. The result displays use floats; source-bound
interval checks and integer floors do not rely on those rounded displays.

## Scope, overlap and credit

This is a changed `selected-packing` scope: a structural obstruction and a
residual integer optimum, not a candidate supplier. The initial moment-curvature
idea overlapped Aaron Wang / navinor's pending PR1669 quadratic root screening,
so it was abandoned rather than duplicated. No mathematical source from that
PR is imported. A complete cached scan covered 439 open PRs and 326 discussions
on October 14, 2026; no matches for the refined stability terms are not a novelty
certificate. The sparse checkout limits local package coverage.

Predecessor: Douglas Colkitt / Claude's fixed-word ceiling, PR1012 coverage law,
Ali Romman's heterogeneous-owner-assembly, and the selected #1094 construction
and #1087/#589 supplier lineage credited in its retained review. Frozen artifacts
and the selected record remain unchanged. This does not reprove circuits,
surcharges, all-size/compiler, common-label/mutable-source, whole-call hosting,
precision/tape, analytic transfer, or bit H1-H5 assumptions. No full selected cold
replay, proof-assistant verification, speedup or complete multiplication theorem
is claimed.

## Open next questions

What optimum survives actual owner-family and hosting restrictions? Extract
one selected residual owner-family instance and enumerate only legal partitions
with the local invoice fixed. This matters because the unrestricted optimum
has negligible integer penalty but likely severe realization constraints.
The blocker is an explicit source-bound legal-group characterization; see the
structured question in TASK.json. The scope is not a mandate to repeat an
already-searched packing seed.
