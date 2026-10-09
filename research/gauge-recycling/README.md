# Gauge refinement through recycled bit registers

Under the interfaces retained by #144 and #150, this composition gives
`T(n) = O(n (log n)^(1-kappa))`, with
**kappa = 472154791/10^12 = 0.000472154791**.
This is a conditional construction, not an unconditional multiplication theorem.

The branch is stacked on #150 at
`40d4038760ebb6d6d3d702ce88fa3645de29f0c1`. The only additional files are
in this directory. No existing producer, certificate, or checker is modified.

## Mechanism and proof

Restore 187 omitted entrance gauges (165 of rank 16 and 22 of rank 17),
retaining #150's 1,549 terminal eliminations and all 3,338 handoffs.
The old read times remain unchanged and every donor still dies before its
recipient's read. Thus better entrance/target charges need not cost recycling
opportunities. This is not true for arbitrary added gauges: the timetable
and the new frame transitions must be checked.

Each restored read belongs to an original first occupant and precedes its
first update. Subtracting that initial value at the delayed read instead of
in the zero prelude preserves dirty-state cancellation. A recycled recipient
still subtracts its donor's final value. Inverse updates run in exact reverse
order, including source injections. All initial auxiliary values are arbitrary.
The verifier checks this identity on all 27,521 formal inputs over Z and F2.

The physical-register ledger checks common frames for gates and ordered
movement, and reconstructs the complete row. Its set of 4,878 non-inherited
frame transitions is exactly #150's, so #150's exact Q nesting and
nondegeneracy checks transport without an additional geometric assumption.
Inherited chains and the shared-core/interface arguments retain the same
dependencies as #150. Optional `--frames` checks every fresh pair directly.

The histogram delta relative to #150 is:

| Width | 1 | 2 | 3 | 4 | 16 | 17 | 18 | 19 | 20 | 48 | 51 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Delta |339|597|405|45|693|-183|-489|-495|-87|165|22|

Total rank is unchanged; there are 1,012 additional positive children.
Their rare-class costs are charged, not discarded. R=23,979, W=27,521,
deficit=2,024 and largest child=60. The coarse bit saving is
`c=472806533/10^12`.

## Recurrence and assembly

With the same volume-normalized stopped supplier as #144, atom exponent
theta, and ordinary leaf saving `d=384599/10^10`, the cost is

```
O(e^(1-theta) + e^((1-theta)(1-c)+theta*(1-d))
  + e^(theta*(1-d)) + e^theta log e).
```

At `theta=473/10^6`, `a=(1-theta)c+theta*d` equals
`472601087042591/10^18`; the required strict inequalities
`a < theta < 1-a` hold. All inherited coefficient preparation, precision,
addressing, copies, restoration, cleanup, phase-stop and uniformity contracts
are retained, not re-proved here. Pricing uses #150's unchanged exact #144
assembly functions, checking 47 constraints and seven margins.

| Row | theta | conditional kappa |
|---|---:|---:|
| #150 | .0005 | .000472026274 |
| Composition | .0005 | .000472143085 |
| #150 repriced | .000473 | .000472037976 |
| Composition | .000473 | **.000472154791** |

The structural contribution at identical theta is .000000116815; the further
wrapper change contributes .000000011706 on the composed row. Bit supply
still limits the assembly. Failed next-grid upper-enclosure tests mean only
failure of that certificate, not a mathematical optimality result.

## Reproduce

Python stdlib only; do not use `-O`. From the repository root:

```sh
python3 research/bit-reuse-147/verify.py
python3 research/gauge-recycling/verify.py
# Alternatively rebuild the composition's fresh geometry directly:
python3 research/gauge-recycling/verify.py --frames
```

The first command verifies the baseline geometry used by the default second
command. Saved plan and row are exact witnesses, not solver logs. No search
or external workspace is needed. The script validates the plan, rebuilds
the ledger/row, checks complete formal identities and three negative controls,
and independently reprices the two reported atom choices. No new Lean theorem
or whole-repository formal check is claimed.

## Provenance and scope

The refined gauge set was found in our Round19 search; concurrent #146
(Th0rgal) supplies the public min-cut gauge refinement. No priority is claimed
for gauge optimization. Credits: DaysSky #150 for the late-read recycling
implementation and complete scalar checker; jamesyc #124 for birth-read reuse;
hpst3r #147 and SovereignSteak #122 for terminal elimination; icekylinx #144
for the paired-cube/shared-core construction and assembly; gupt1156 #148 for
atom tightening; Swapnil Jain and Zhihao Chen for inherited word/frame tools;
an664 #128 for completed-core sharing. This contribution is compatible
composition, its exact accounting, and the timetable-neutral mechanism.
Prepared by SovereignSteak with AI assistance. No broad novelty or optimality
claim is made.
