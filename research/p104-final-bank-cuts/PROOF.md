# Two free bank cuts

## Result and scope

The last two bank cuts in the pinned PR #7776 graph preserve its full rational
public operator. Each cut removes one paid position. The cuts commute. Each
replaces the paid-rank multiset `{2,3}` by `{5}`. No public owner, chart frame,
input chart, output chart or productive target changes.

This is an independent local audit. It gives no new kappa and no complete
supplier admission. The ordinary BIT service still binds the source claim.
The audit uses the published source constructors to obtain the input graph.
It uses separate cut code and the exact operator engine from PR #7777 to
check the final operations. It is not blind or independent human review.

## Exact local equations

Write the two parallel arrivals as `a,b`, the other retained arrival as `c`,
and the moved arrival as `d`. In each source chart the four local rows are
`c`, `a-c-b`, `d+b` and `b`. The first two rows stay. The last two rows move.

| Source chart | New chart | a | b | c | d | Removed row | Other moved row |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1037 | 918 | 95049 | 96263 | 95050 | 96262 | 101272 | 20005 |
| 1038 | 921 | 95055 | 96274 | 95056 | 96273 | 101228 | 20006 |

Use new arrivals `A=b` and `B=-a+s*b`. The matrix and its inverse are
`M(s)=[[0,1],[-1,s]]` and `M(s)^(-1)=[[s,-1],[1,0]]`. Their product is the
identity for every rational `s`. An old reader `u*a+v*b` becomes
`(s*u+v)*A-u*B`. Thus the four rows become

```text
c, (s-1)*A-c-B, d+A, A.
```

Move `A,d` to the new chart. Keep `B,c` at the source chart. The staying
second row has no crossing term exactly when `s=1`. This proves uniqueness
within this rational family. The two moving rows already use only moved
arrivals. The removed paid row now has the same source and target chart.
Substitute its form in every reader and delete it. These operations preserve
the rational value for every public input. They need no additional transfer.

The changed arrival IDs, local rows and retired positions for the two cuts
are disjoint. Both orders produce the same canonical graph. The checker also
verifies this equality directly. It checks every donor at its use, every
strict chart inclusion and a causal order for each of the four graphs.

## Complete output and paid profile

Expand every public input as a separate formal variable. Reduce each row to
an integer coefficient vector and a positive common denominator. Compare all
1,264 output vectors for the original graph, each individual cut and both
cuts. All four operators agree. The final graph digest agrees with the
published journal. `RESULT.json` records the digests and exact work count.

Each cut has paid-rank change `2:-1, 3:-1, 5:+1`. The native paid count goes
from 5,703 to 5,701. For recursive exponent `1-k`, the combined native paid
moment decreases by `2*(2^(1-k)+3^(1-k)-5^(1-k))`. This is positive for
`0<k<1`: strict subadditivity of `x^t` for `0<t<1` gives
`(2+3)^t<2^t+3^t`. At `k=0` the change is zero; at `k=1` it is two.

If the source's same 48-call assembly is retained, its paid moment decreases
by `96*(2^(1-k)+3^(1-k)-5^(1-k))`. Its paid count is then 282,960 before
these cuts and 282,864 after them. Its 51,312 productive targets do not
change. This is an invoice implication of the unchanged caller, not a new
caller or ordinary-service replay. The chart rank is the dimension
difference; it is not an exponential of that difference.

## Controls and limits

Set `s=0`. Each cut then has a crossing coefficient `-1` in its staying
row. Omit the inverse reader change. Each cut then has three forbidden
crossings. Both controls fail the cut condition. A separate same-chart
terminal coefficient mutation passes the chart checks and changes an exact
output coefficient. The checker records its input and output witness.

The full input graph is reconstructed from pinned journals. No earlier edit
is re-proved here. Signed Pauli realization, physical integer execution,
caller traversal, ordinary services, directed price bounds and compiler
closure are outside this audit. No selected cold replay, Lean or Docker
ran. All five framework assumptions remain. The result does not prove a
global optimum over other bases, bank interfaces or supplier graphs.

## Open next questions

Can a changed bank interface improve the complete paid profile? Such a
construction must include the public operators, physical word, caller and
ordinary-service bill. Can the binary service improve as well? That service
still limits the current conditional claim.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
