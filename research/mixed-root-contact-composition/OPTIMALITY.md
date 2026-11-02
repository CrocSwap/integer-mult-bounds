# Exact raw limit of the fixed mixed-root family

The old value 0.00328623 was a strict exclusion bound. It was not a
feasible target. The exact raw funding limit is the unique zero k* of
the signed invoice below. Two rational engines enclose it in

```text
0.00328621476572836015146309 < k* < 0.00328621476572836015146310.
```

The complete conditional claim is
**kappa = 0.00328621476572836015146308**. Thus

```text
10^-26 < k* - kappa < 2*10^-26.
```

This last change refines the completion and compiler parameters. It
does not change the source, caller, paid profile or productive profile.
It is not a new construction step under the repository's hill-climbing
rule. The earlier mixed-root construction supplies the four-percent gain.

## Scope

Fix the exact PR6375 source and its complete helper interface. Consider
the classified six-field, seven-query roots with four independent forward
full stages at distinct sites and at most two extra whole idles. Every
output must contain the central involution S. Scalar bases must be
independent of S and all stage variables. Permit every positive binary
child size and every binary tree shape. The
[classification proof](../mixed-projector-root-headroom/PROOF.md) reduces
every such root to the same priced output pattern. The saving range is
0 <= k <= 0.0034, as in the retained BIT admission.
`SOURCES.json` pins the exact classification proof at local commit
`e87c230f231441e2b53dec846ae9496c8c8d5121`. Its structural statement
does not depend on the native source price.

This is the exact raw limit in that domain. It does not bound changed
sources, more costly roots, different queries, different child contracts
or all multiplication algorithms. The five inherited framework assumptions
remain. Exact equality at k* has no complete strict certificate here.
The family comparison fixes the recursive paid/productive invoice. It
does not assert equal ordinary-operation costs for all scalar bases.
Omitting extra ordinary work favors competitors and preserves the upper
bound. The complete ordinary budget is checked for the actual chosen word.

## The signed invoice

Put H(r)=r^(1-k). The productive moment minus the paid moment is

```text
F(k) = 104 H(145) + 208 H(73)
     + 416 [H(57)-H(56) + H(33)-H(32) + H(25)-H(24)]
     + 1872 [H(17)-H(16)] + 6552 H(9) + 666 H(8)
     - 90 H(6) - 2448 H(5) - 36 H(4)
     - 8766 H(3) - 8010 H(2) - 41678 H(1).
```

This bill includes all 18 native calls, all helper target debits, the
root queries and idles, and every binary node. `optimality.py` constructs
it from the literal child trees and compares it with the separate event
invoice. The complete native and caller replay remains in `verify.py`.

`pricing.py` bounds F' strictly below zero on the entire admitted range.
Both rational engines give a positive lower bound for F at the lower
endpoint above and a negative upper bound at the upper endpoint. Hence
F has exactly one zero in that interval. This argument does not depend
on a floating-point root finder.

## Why no other child bill has a later crossing

Let L(k) be the native paid moment minus the native helper moment,
divided by 104. For a binary child, define its minimum net cost by

```text
C(1) = 0
d(n) = 2 H(8n) + 1 - 2 H(8n+1)
C(n) = d(n) + min [C(a) + C(n-a)],  1 <= a < n.
```

The two root pairs can be priced separately. For a pair with total n,
let

```text
G(n) = H(8n+1) - n L
     + max [H(8b+1) - H(8b) - C(n-b) - C(b)],  1 <= b < n.
```

The complete per-port margin at total N and pair totals x,N-x is
H(8N+1)+G(x)+G(N-x)-2. The terms H(8b) charge the actual whole idles;
they are not fixed at the winning child size.

At the lower bracket endpoint, the exact recurrence gives these results:

| Competing choice | Outward upper bound or strict gap |
| --- | ---: |
| All 4,655 pair-total choices below N=100 other than (9,9) | Margin < -0.0010068 per port |
| Any split of a nine-leaf pair other than (7,2) | Margin < -0.00004433 per port, even with the other pair optimal |
| Any other seven-leaf tree histogram | Additional cost > 0.0014247 throughout the bracket |

There are 11 distinct internal-node histograms for seven-leaf binary
trees. The selected histogram is {2:3, 3:1, 4:1, 7:1}. Different planar
trees can have this same histogram and bill; no unique tree shape is
claimed. The two-leaf tree has only one histogram. Thus the selected
tree bills are optimal at those sizes.

These comparisons extend in the required direction. The checker proves
L' > 0 on the admitted range. Each H(r), r>1, decreases with k. The
increment H(r+1)-H(r) also decreases: its derivative is
r^(1-k) log(r) - (r+1)^(1-k) log(r+1), which is negative for r>=1.
Each d(n), and therefore each fixed tree cost, increases. A minimum over
these increasing tree costs is increasing. Thus a competing profile
that loses at the lower endpoint also loses at every larger admitted k.
The interval comparison of all 11 histograms retains their signed
differences; it does not subtract two separately rounded optima.

To prove dominance across the bracket, one further comparison is needed.
The selected margin becomes negative above its zero, so negativity of
the alternatives alone does not prove that it is larger there. Since
F decreases, F(upper)/104 bounds the selected per-port margin from below
throughout the bracket. Each competing margin is bounded from above
by its bound at the lower endpoint. The replay compares these rational
bounds directly, including the infinite tail below, and proves a gap
greater than 0.00004433 per port. Together with the histogram comparisons,
this proves that sizes 7,2,2,7 and their selected tree bills maximize the
margin throughout the bracket.

For N>=100, concavity gives the bound

```text
H(8N+1) + 2 H(4N+1) - N(L-1) + 2[H(9)-H(8)] - 6.
```

This follows from d(n)>=-1, the N-4 internal child nodes, and Jensen's
inequality for the pair outputs. The same exact endpoint and derivative
checks exclude this whole tail at both bracket endpoints. Concavity in
N makes its derivative nonincreasing. The monotonicity in k above then
excludes all larger savings. The separate `ceiling.py` recurrence also
checks every finite pair choice at the upper bracket endpoint.

It follows that the largest raw crossing in the whole stated family is
exactly k*, the zero of the displayed invoice. This is stronger than
giving a nearby numerical exclusion bound.

## A complete point immediately below the bracket

Use tested saving 0.003286214765728360151463085, tensor power 1920,
cutoff 12, floor 13, moment offset 1/7, reserve 10^-29, and decay 31/32.
For the three retained ratios alpha, gamma and delta, exact intervals
give alpha < 1-reserve and gamma,delta < 31/32. The complete normalized
paid bound is

```text
1 / (1 + 1920 * 10^-29) + 4 * (31/32)^1920 < 1.
```

The first term bounds alpha^1920 by Bernoulli's inequality. The second
term charges both completion and splitting tails. The older estimate
(31/32)^128 < 1/16 gives a bound that is too loose at this precision.
The new check uses the exact rational power, and rejects that coarse
bound as insufficient. No paid tail term is removed.

The compiler uses logarithm power 2100. All source work, routes, ordinary
operations, BIT stock and 54 strict plus four functional outer conditions
remain charged. Both interval engines check the tested saving and both
raw bracket endpoints. `RESULT.json` records every exact parameter and
the very large integer threshold. No uniform word is materialized.

The two tail ratios stay below 31/32 throughout the raw bracket. For
each k<k* in this bracket, alpha<1. One can then choose a positive
reserve below 1-alpha and a finite power large enough to make the
displayed type of completion bound strict. Thus the raw limit can be
approached by finite suppliers. This is a statement about strictification,
not an extra outer-endpoint certificate.

At k* itself, alpha=1. The completion bound has a term equal to one
and additional positive tail bounds. This strict funding argument does
not certify equality. More decimal places cannot remove that limitation.
A construction gain beyond this exact raw limit must change a hypothesis
of the family or its fixed source.

## Open next questions

- Independently check the family classification, full invoice and exact
  optimum. The arithmetic replay is an author check.
- Change the source or an excluded root or child contract, then check
  the complete paid and productive bill before further construction.
- Reduce the completion and compiler constants for a specified distance
  below k*. That is a constant improvement, not a larger raw crossing.

Ali Romman with substantial OpenAI Codex assistance; no subagents.
The interval engines, strictification and compiler retain their original
credit in `NOTICE`. Apache-2.0.
