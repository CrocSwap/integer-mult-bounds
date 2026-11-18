# Two causal splits after all 33 helper restrictions

## Result

The literal chart-498 and chart-595 readouts and departure injections
from PR #7712 remain valid on the compact graph of PR #7713. They
compose in that order. The result has 1,470 public fields, all 400
original mains, 1,070 independent helper returns and the same 6,054
paid transfers with the same ordered chart routes.

This is a normalized rational construction, not a new multiplication
bound. The source construction, its two split witnesses and the
causal split method retain their original credit. The new result is
their verified compatibility with the changed helper-quotient graph.

## Source identities and actual cuts

The frozen compact input has SHA-256
`16e99893a2c669467ce74f214e8eb5150402f0267aaa8d67aad5d870aa4d5c18`.
The new graph has SHA-256
`5183479ecac34a1cb5c046f202e19d7161679265fe121b4a0af922fe344d8fc1`.
[Input pins](SOURCE-PINS.json) and [credit](CREDITS.md) give the exact
commits and byte records. The compact graph is a source-constructor
export whose normalized endpoint was separately checked in PR #7715.

The checker extracts each literal prefix formula from the source
split circuit's retired-role output. It extracts departure weights
from every read of the corresponding fresh entrance. It checks all
these keys and chart locations in the new graph. No split search or
new choice of readout/injection weights is made.

| Chart | Original role | Compact role | Fresh role | Target ranks |
| ---: | ---: | ---: | ---: | --- |
| 498 | 126 | 126 | 1468 | 9 becomes 4 and 5 |
| 595 | 281 | 278 | 1469 | 9 becomes 1 and 8 |

At chart 498 the prefix has 61 paid ancestors. Its expanded entrance
form has 14 terms and its exit-response direction has 46 terms.
At chart 595, after the first split, the prefix has eight ancestors;
the entrance form has 17 terms and the response has 30 terms.
Both exact pairings are one. In each case the prefix ancestry is
disjoint from every injected departure. Thus the fresh input cannot
change its own prefix readout. All entrance and response coefficients
are supported on the current helpers with route 3 to 127.

The same literal witnesses are positive controls on the unsplit
PR #7708 parent. The chart-498 entrance form there has 15 terms,
so retaining the old entrance coordinates without recalculation would
be wrong. The new certificate records the actual 14-term form.
The chart-595 response propagation also changes after restriction.

The chart-480 source split is excluded. Its original role 239 is no
longer public. Prefix bank 92659 and injection bank 93428 are absent.
That collision was already reported by the source; it is not claimed
as a new negative result or as an impossibility theorem for other cuts.

## Constructive identity

Let G be the current helper group entering chart E=3 and leaving
chart X=127. Its normalized operator is the identity, with no main
cross terms. At an intermediate chart C let the available prefix
compute `ell(x)`. Let injecting `c_k z` into the selected departures
change the complete public output by `v z`.

The exact basis checks establish that ell and v are supported only
on G, `ell(v)=1`, and the prefix has no injected departure as an
ancestor. Choose r in G with `ell_r!=0`. For new independent inputs u,
encode at E by

```text
x_j = u_j + v_j u_r                       (j != r)
x_r = v_r u_r - sum(j != r, ell_j u_j)/ell_r.
```

Then `ell(x)=u_r`. All old group coordinates are linear forms of
arbitrary independent new coordinates. The inverse is
`u_r=ell(x)` and `u_j=x_j-v_j ell(x)` for j other than r.
Thus this encoding does not restrict the input space.

Return u_r at chart C from the prefix. Introduce an independent fresh
input g at C. Add `c_k (g-ell(x))` to each selected departure.
Causality keeps the prefix unchanged. The old exit values become
`y=x+v(g-u_r)`. Therefore `ell(y)=g`. At X return this as the fresh
output and decode every other helper as `y_j-v_j ell(y)=u_j`.
The mains do not change because the response vanishes outside G.
All operations occur at their indicated common chart.

The paid graph retains every old key and ordered route. The scalar
formulas and public terminal rows change. The new graph passes a
complete locality and acyclicity check. The second split is checked
and constructed on this actual changed graph. Its readout and response
are not inferred from the first positive control.

In physical frame notation the two desired helper routes are
`T_C T_E^-1` and `T_X T_C^-1`. Their ranks are the positive dimension
differences shown above. The checker verifies strict binary-span
inclusions. It does not replay the physical phased recipes or prove
an owned-storage implementation of the new scalar program.

## Complete recursive invoice and implementation cost

Per native call, replace two rank-nine productive targets by targets
of ranks four, five, one and eight. No paid transfer is added or
removed. Using the unchanged published fixed caller/root rows and
16 native invocations gives:

| Quantity | Compact parent | Composed graph |
| --- | ---: | ---: |
| Paid jobs | 100416 | 100416 |
| Productive jobs | 20624 | 20656 |
| Paid rank mass | 268368 | 268368 |
| Productive rank mass | 269696 | 269696 |

The surplus stays 1,328. The complete productive-minus-paid power
margin increases by

```text
16 * (4^t + 5^t + 1^t + 8^t - 2*9^t),    0 < t < 1.
```

This is strictly positive: for positive a,b, divide by `(a+b)^t`
and use `u^t>u` on the two fractions in (0,1).
Both surrendered rank-nine targets are debited. Adding the four new
targets without these debits fails the literal graph count.

Local scalar terms rise from 175,927 to 178,845 per invocation,
an increase of 2,918, or 46,688 over 16 calls. This count is not a
physical service bill. Common grids, signed intermediate ranges,
owned homes, resets, moves, guides and complete compiler costs must
be recomputed for this graph. They are not assigned zero cost.
No numerical crossing or new kappa claim is supplied.

## Exact checks and controls

The compact parent uses 9,657,314 coefficient products. The complete
1,469-row first composition uses 9,758,827. The final 1,470-row check
uses 9,966,426. A separate traversal of the transposed final graph
uses 8,111,567 products and agrees with the transpose of the required
matrix. Every main output is compared with the pinned compact parent;
every helper output equals its own independent entrance.

Omitting prefix subtraction causes a unit input at role 126, or at
role 278 for the second step, to appear erroneously at the fresh
output. Omitting the exit decoder causes fresh input 1468 to leak
value 4 at output 238; fresh input 1469 leaks -2/7 at output 386.
Each expected value is zero. The checker constructs and evaluates
these four faulty circuits. It also rejects the undecremented target
bill. All arithmetic is rational; optimized Python retains every check.

The source proof and code were read. The exact basis engine is reused
from PR #7715 and retained byte for byte. This is author checking,
not blind, independent human or formal-kernel review. Native phases,
owned erasure, compiler closure, precision tape, analytic recovery,
full predecessor suites and selected cold replay remain outside scope.
