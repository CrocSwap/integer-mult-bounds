# The exact positive-price frontier

Work over F2. Three source rows, seven target rows and two connector roots
are distinct and arbitrarily dirty. Source maps B_j and target maps A_m are
arbitrary fixed linear maps, possibly singular and noncommuting. The requested
endpoint is `y_m += A_m(sum_(j in m) B_j x_j)` for every nonzero three-bit
mask m. Sources and both roots restore; outputs are not read until completion.
Every child acts through physical root z0, restores disjoint private scratch
and prescribed heads, and has a fixed complete price. No other data operations
or hidden clean/persistent buffers are supplied.

We optimize formal words required to implement the endpoint for every
compatible choice of these maps, treating child maps as opaque. The lower
bound is for this universal interface, not for each concrete map separately:
known zero readers or other map-specific coincidences can reduce its cost.

The six B calls are fixed, in order `B0 B0 B1 B1 B2 B2`. Their normalized
colors are `v0=v1=(1,0)`, `v2=(0,1)`. Exactly as in PR2538, a source call is
legal only when the current physical frame G has `G v_j = (1,0)`. Root
transfers are `U: z0 += z1` and `V: z1 += z0`, with independent positive
complete prices u,v. All A reads use z0. There is no limit on the number
of transfers or target readouts; their positions are arbitrary.

The fixed source order/colors are hypotheses, not constraints inferred for
all connectors. Without them the theorem below is not asserted. U and V are
involutions in characteristic two. The frame starts and ends at identity.

Let a_m>0 price A_m, b_j>0 price B_j, and let r_m count reads of target m.
The three componentwise nondominated attainable invoices are

| U | V | r1,r2,r3,r4,r5,r6 | r7 |
|---:|---:|---|---:|
| 2 | 2 | 2,2,2,2,2,2 | 4 |
| 3 | 3 | 2,2,2,2,2,2 | 3 |
| 4 | 2 | 2,2,2,2,2,2 | 3 |

Thus the exact call tariff, for every choice of these positive prices, is

```
2 sum_j b_j + 2 sum_(m=1)^7 a_m
    + min(2u+2v+2a7, 3u+3v+a7, 4u+2v+a7).
```

The proof below is over all finite legal words, not a search up to a chosen
length. Executed finite state exploration corroborates it and supplies the
three explicit attaining words in RESULT.json.

## Lower bound for every word

Write the roots in normalized coordinates as `G(d + Q X)`, where d is their
arbitrary incoming dirt and `X_j=B_j x_j`. A read through z0 has formal
coefficient `(l, l Q)`, where l is the first row of G. This follows by direct
induction: transfers change G; a legal B_j toggles normalized column v_j;
output reads do neither. No A or B factors are commuted. To prove necessity,
specialize all maps to scalar identity with independent source and dirt bits.

The paired consecutive source order means every normalized cut is either
zero or has just one nonzero column: successively v0 X0, v1 X1, v2 X2.
Thus one read contributes at most one source label. Incoming dirt is a
nonzero functional l because G is invertible. Every nonzero target therefore
needs at least two reads. Target7 needs at least three, since all three
independent source labels must occur.

Any B2 requires the second row of G to be `(1,0)`, since its pairing with
v2 must vanish. It begins and ends at `(0,1)`, and only V changes this row,
so every legal complete word has at least two V transfers. At the same B2
the first row pairs nontrivially with v2, so differs from its initial/final
`(1,0)`. Only U changes the first row, so there are at least two U transfers.

If target7 uses **three** reads, each must contribute a different singleton
source. They therefore occur inside the three nonzero source intervals,
in order X0, X1, X2. Three nonzero dirt functionals in F2^2 sum to zero only
if they are the three distinct functionals `(1,0),(0,1),(1,1)`. The X0 and
X1 reads must pair to one with v0=v1=(1,0), so their functionals are `(1,0)`
and `(1,1)` in one order. The X2 read must consequently use `(0,1)`.

The first row of G thus visits `(1,1)` in one of the first two intervals,
then `(0,1)` in the third, while starting and finishing at `(1,0)`.
This requires at least three first-row changes, hence at least three U.
The order `(1,1),(1,0),(0,1)` in fact requires four, but that strengthening
is not needed below.

Both U and V act as transpositions on the three nonzero vectors of F2^2.
Their product is identity at return, so U+V is even. If U=3, V is odd and
V>=2 forces V>=3. If U>=4, V>=2 already holds. Therefore any word with
r7=3 is dominated by the second or third displayed invoice. Every word
with r7>=4 is dominated by the first. All other r_m>=2 and the six B calls
are fixed. This proves the lower bound, including arbitrary redundant
transfers and arbitrary numbers of repeated target reads.

## Attainment and price regions

The verifier emits one legal complete word for each invoice. Its formal
coefficient replay establishes every source, dirty-root and dirty-target
column, so the words work for arbitrary compatible linear maps and lengths.
A separate dense interpreter executes singular and noncommuting map examples
in both directions. The same A_m distributes over its selected source sum;
no relationship among different A_m or B_j is used.

Among the two minimum-read words, `(4,2)` is cheaper when u<v, and `(3,3)`
when u>v; both tie at equality. Put `delta=min(u+v,2u)`. The minimum-read
policy pays one less a7 but at least delta more transfer cost. The four-read
word is strictly cheaper exactly when `a7 < delta`, the three-read word is
cheaper when `a7 > delta`, and they tie at equality.

In particular, for u=v=tau the two count-Pareto points are `(reads,transfers)
`(16,4)` and `(15,6)`, with break at a7=2tau. At unit call prices the exact
total is 26, versus 27 under the minimum-read policy. This comparison
retains all six source calls and all proper-mask reads; it is not a free
transfer or source-fusion assumption.

## Full-cost boundary

The formula prices complete calls, not elapsed time or native child ranks.
An actual implementation must add its admission/root-stock cost I, map
preparation P, and any instruction emission/dispatch/hosting/precision cost
H not already included in a_m,b_j,u,v. The exact call-price optimum assumes
these extra terms are common to compared words or charged separately. If H
depends on the chosen word, its difference can reverse the small advantage;
no lower bound for such unspecified extra costs follows from the call model.

There is no selected-supplier caller, recursive contraction, general source
order/color optimum, arbitrary-root theorem, native runtime improvement or
new kappa here. This result answers the excluded read/transfer tariff question
for one explicit fixed interface. PR2538's lexicographic minimum-read result
remains correct and is credited, along with PR2208's root-frame formulation.
