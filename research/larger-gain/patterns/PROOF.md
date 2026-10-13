# Capacity ceiling for the current providers

PR564 cannot reach the next `10^-18` kappa grid point by repacking or
remixing its current zero, four and eight promotion providers while keeping
the present pending capacities. This includes arbitrary finite copies of
that controller. The statement does not constrain new local words, a new
residual-width inventory, or different controller geometry.

The [exact dual certificate](CURRENT-ALPHABET-EXACT-CEILING.json) proves
rejection at complex rate `0.001595676284575998624255`, one rate tick above
the admitted PR564 endpoint. Its implied kappa ceiling is approximately
`0.001593134158181640233287`, below the next kappa grid point
`0.001593134158181641`. This is an endpoint ceiling, not a proof of exact
equality of the optimal real root.

## The relaxation contains every literal assignment

There are 5376 pending bins of capacity 8 and 3584 each of capacities 16,
32 and 48. These counts come directly from the 144 replica and child
windows, with 112 port families per window. Every helper occupies one
whole residual footprint of width 4, 5, 8 or 9. Enumerating all
nonnegative integer patterns within each capacity produces 545 patterns,
including empty bins. A pattern pays its unused rank as one idle child.

The three provider columns have respective promotion counts `p=0,4,8`.
Their complete helper inventories are `(p,56-p,157,291)` at widths
`(4,5,8,9)`. Their complete local paid profiles are read from the pinned
source plan. The optimization balances every helper width, every bin
capacity count, and the total of 72 complete calls. Provider and pattern
multiplicities may be fractional. Actual call times, owner uniqueness,
spectator requirements and order are omitted. These relaxations enlarge
the feasible set, so failure of the relaxed model excludes any literal
assignment within this scope. A controller with C finite copies divides
by C to give another feasible point of the same relaxation.

## The objective is the actual moment

For each provider, local paid rank minus its total residual width is
1856. Consequently every feasible packing has rank mass

```text
total pending capacity + 72*1856 = 520704.
73*7168 - 520704 = 2560.
```

For rate `b>0`, assign each paid child of rank r the coefficient

```text
c_b(r) = r*((73/r)^b - 1)/b,    c_b(0) = 0.
```

The native complex moment is below one exactly when the total coefficient
cost is below `2560/b`. The model charges every local child and every
remaining idle rank. No scalar-work reduction is counted as a rank gain.

With equality matrix A, inventory vector d and column costs c, every
rational vector y satisfying `A^T y <= c` gives the lower bound
`d^T y` on all feasible costs. The certificate lists nine exact rational
potentials and checks all 548 columns. Both independent rational moment
engines give outward lower bounds on each cost; the potentials satisfy
both sets of inequalities. The strict sign `b*d^T y > 2560` proves
rejection. Since every child rank is below 73, each candidate's moment
increases with b, so all larger rates also reject.

The exact nominated primal has the same histogram as PR564. This is a
consistency check; the exclusion rests on the dual inequalities, not the
floating solver's status. The earlier PR563 already used the 545-pattern
capacity screen for discovery. This receipt adds an independently
checkable dual exclusion at the pinned PR564 endpoint.

## Reproduction

Verification needs only Python's standard library and the unchanged
rational engines from pinned PR564. In a standalone publication checkout,
set `GAIN_PR564_SOURCE` to that external `research/complex-allcold` directory:

```sh
GAIN_PR564_SOURCE=/path/to/pinned-PR564/research/complex-allcold \
  python3 -B research/larger-gain/patterns/capacity_ceiling.py \
  --verify research/larger-gain/patterns/CURRENT-ALPHABET-EXACT-CEILING.json
```

Nominating a new receipt requires NumPy and SciPy. They nominate a basis;
the verifier uses exact rational arithmetic. Receipts with extra kernels
describe enlarged, hypothetical inventories and are not covered by the
current-provider exclusion. Local scalar and phase verification plus a
literal global owner audit are separate requirements for such candidates.
