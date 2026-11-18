# Receiver and complete-invoice audit

This package checks all 46 fixed recodings in
[PR #7708](https://github.com/CrocSwap/integer-mult-bounds/pull/7708),
scientific commit `f0e2db5b5b46b139da17d2b32fab6633164443a9`.
It answers the [receiver review request](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19710692).
The source's conditional kappa claim is unchanged. No new complete
multiplication bound follows from this audit alone.

The parent hash is
`8e7b755bd2d2d387bc3d3adfe48100985adf74775ca5acbb143170a3d16b5ccf`.
The final hash is
`db10e4ca7154b454f86bf404bc34b3a16d02de6cc008d5227e4eef2654cb0778`.
The exact word, relay constructor, cut certificate and source receipt
are pinned in [SOURCE-PINS.json](SOURCE-PINS.json). These pins establish
source identity, not ancestry or independent acceptance.

## What the separate basis check proves

For each cut, assign an independent rational variable x_r to every
entrance owner of the current orientation. There are 1501 owners.
In a transposed cut, these are the entrances of the transposed graph.
A negative token `~r` denotes x_r. Each nonnegative token denotes a
distinct paid bank. Each form is a rational linear combination of banks
at one chart. The separate Graph implementation checks every donor,
chart, terminal and dependency, then constructs its own topological
order. Every transfer has strictly nested chart subspaces.

Expand every bank and terminal as an exact vector in the x_r basis.
The evaluator stores a common integer denominator and a sparse integer
numerator. It uses no floating-point arithmetic or sampled inputs.
Vector equality is therefore equality for all rational inputs. The
normalized identity also holds on vector-valued inputs, coordinate by
coordinate. Its physical use still requires the inherited signed chart
and common-factor contracts.

The source constructor produces the candidate graph. This audit derives
the expected value of every surviving bank from the pre-cut values.
It compares every candidate bank and public output against that value.
It does not call the source's cut witness checker. It does reuse the
source transformation code, exact basis engine from PR7715, and signed
caller engine. Thus it is a separate arithmetic check after source
inspection, not a blind or independent human review.

For an elimination, let t be the removed bank, m the retained reader,
and Y the certified combination of old readers. The coefficient of t
in Y is s, which is nonzero. The certificate gives `S=Y+D`, where S is
available at the new sender and D at the receiver. The new retained bank
has value S. A different old reader with coefficient a on t becomes
`h'_k=h_k-(a/s)Y`. Every other surviving bank and public output must have
its old value after the decoder substitutions. The basis check tests
all these statements directly, including the source identity.

For a grouped or feedback reroute, let v_t=1 describe the removed
direction in the incoming group. Each other group bank becomes
`h'_k=h_k-v_k h_t`. Let Y be the transmitted signal and s its nonzero
response to v. An affected row has correction `z_m=L_m(v)/s` and new
value `h'_m=h_m-z_m Y`. The new incoming bank carries S. The outgoing
bank and every other unaffected bank and terminal retain their old
values. The group case has `S=Y` and outgoing value `Y+D`. The feedback
case has source equation `Y=S+sum(d_i h_i)`. Substitution gives

```text
(1-sum(d_i z_i))Y = S+sum(d_i h'_i).
```

The determinant must be nonzero. A valid local equation alone is not
sufficient: the full after-graph must be local and acyclic, and all
bank values must agree with the stated transformation. Those checks
run for each cut. The public outputs are unchanged at every step.
Transposition preserves equality of the complete public matrix, so
forward and transposed cuts can be composed in the published order.

There are 22 eliminations, 21 grouped reroutes and three feedback cuts.
The check covers 350961 after-cut bank/output values. Its exact basis
expansions use 468916850 coefficient products. Adjacent cuts with the
same orientation reuse an already checked basis; a change of orientation
causes a new expansion. All 46 signals have full coefficient lists in
[RESULT.json](RESULT.json).

## Cut 38: the denominator is five

The old route is `3 -> 772 -> 127`. Its ranks are four and five.
The new route is `3 -> 916 -> 127`, with ranks seven and two.
The affected tokens are incoming 100727 and outgoing 100729.
The outgoing response is 1/2. There is one correction:
`h'100744=h100744-2Y`. The sender has

```text
S = 2x1462+x1162-x731+x424.
Y = S+2h100694-2h100744.
5Y = S+2h100694-2h'100744.
```

The basis expansion has 276 nonzero coordinates. At entrance x2, Y has
coefficient one and the recovery numerator has coefficient five.
Division by six therefore gives coefficient 5/6 instead of one.
Omitting the division gives five instead of one. The checker rejects
the changed denominator in this equation. It also adds one to a literal
sender coefficient and records a nonzero residual at owner 1462.

## Cuts 40–42: the chart-778 route and elimination

At cut 40, tokens 99570 and 101132 form the old route
`722 -> 1067 -> 929`, with ranks two and two. The sender transmits
`S=h98900+h98902` to chart 778. Bank 98907 is already at that receiver.
There are no correction rows and the determinant is one. The exact
signal and sender expansions are

```text
Y = -x18/2+x55/2-x101/2+x447/2+x468.
S = -x342+x428+x447/2+x468+x941-x972.
Y = S+h98907.
```

The new route has ranks three and one. This check covers all inputs,
including the cancellations that make the signal sparse. Increasing
the coefficient on sender bank 98900 by one gives residual -1/16 at
input owner 3.

Cut 41 is a separate elimination at chart 595. It is checked in order;
the audit does not skip it when it reaches the chart-778 successor.
At cut 42, the same signal has sender representation
`h97596+h98422+h98900` at chart 722. There is no receiver side term.
The checker verifies that this expression is exactly the five-coordinate
Y above. Token 99570 is removed and token 101132 becomes one direct
rank-four transfer from chart 722 to chart 929. A changed coefficient
on sender bank 97596 gives residual 1/16 at owner 3.

Later cuts 43 and 46 change token 101132 again. Their values, routes and
transpose directions are checked in the same sequence. The local
rank-four observation at cut 42 is not treated as the final paid bill.

## Complete signed bill and strict moment comparison

The retained signed caller engine replays all 4192 events and checks
all 16 chronological invocations. Its exact endpoint, fixed caller jobs
and root targets agree with the source receipt. The audit independently
counts every native route and productive helper before and after the
cuts, then adds the full fixed caller and root terms.

| Quantity | Parent | Recoded graph |
| --- | ---: | ---: |
| Paid calls per native invocation | 6143 | 6121 |
| Complete paid calls | 101840 | 101488 |
| Complete productive targets | 21152 | 21152 |
| Complete paid rank mass | 271568 | 271568 |
| Complete productive rank mass | 272896 | 272896 |
| Signed rank surplus | 1328 | 1328 |

At ranks one through seven, the complete paid-count change is
`(-288,48,-368,96,80,48,32)`. Every other rank and every productive
target is unchanged. The per-native change is
`d=(-18,3,-23,6,5,3,2)`. Its sum is -22 and its rank-weighted sum is zero.

For `0<t<1`, put `s_j=j^t-(j-1)^t`. These slopes strictly decrease.
Let `D_j=sum(d_r: r>=j)` and `C_j=sum(D_i: i<=j)`. The exact lists are

```text
D = (-22,-4,-7,16,10,5,2)
C = (-22,-26,-33,-17,-7,-2,0).
```

Finite summation by parts gives
`sum(d_r*r^t)=sum((s_j-s_(j+1))*C_j: j=1..6)`.
Each summand is negative. Thus the complete paid-minus-target moment
strictly decreases throughout this exponent interval. The source's
numerical crossing, physical cost and compiler admission are separate
obligations; this audit does not claim a new value of kappa.

## Controls, scope and remaining obligations

For each of 46 certificates, increase one literal sender, receiver or
group coefficient by one. Expand the resulting identity error and
retain a nonzero entrance coefficient. All 46 errors are detected.
For each feedback cut, replace its determinant with determinant plus
one. The explicit recovery fails. These are equation controls; they
do not claim that a production schema rejects every possible bad file.

The initial fold trusts the published source word and its CLEAR
certificates. The role-1256 contraction is also inherited. Their exact
bytes and graph hash are checked, but this package does not repeat
their full proofs. The native Clifford catalogue, physical storage,
rounding grid, nested precision, complete compiler and selected cold
replay were not rerun. Lean and Docker were not run. The five interfaces
`native_all_columns`, `owned_erasure`, `compiler`, `precision_tape` and
`analytic_recovery` remain assumptions of the complete source claim.

Historical nine-stage hosted-coverage ceilings do not directly apply
to this sixteen-stage independent-helper contract. No such ceiling,
new supplier or selected-frontier change is asserted here.
