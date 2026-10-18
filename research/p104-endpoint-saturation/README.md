# P104 endpoint demand saturation

The 253 cheap / 147 unit-step, 400-lifetime control in [PR2896][2896] cannot
realize the frozen X-only monotone correction. Even granting independent,
arbitrary endpoint assignments, it can cover at most **3,972 of 4,656**
residual demands in each orientation. The deficit is **684**.

This closes PR2896's explicit endpoint-specific assignment handoff. Its
aggregate calculation `253 + 30*147 = 4663` is correct as a necessary screen.
The new condition accounts for demand saturation at each endpoint. Capacity
left over at one endpoint cannot cover another endpoint's missing labels.

For a budget of 400 lifetimes using only these two history types, at least
**192 unit-step lifetimes** are necessary. This threshold is sharp for the
separate endpoint-count relaxations. With 191 units, at least 219 cheap
lifetimes are needed, totaling 410. With 192 units, 204 cheap lifetimes
suffice in each relaxation, totaling 396. Four further cheap lifetimes may
be left unproductive to give the stated 400 budget. No actual geometric,
chronological or simultaneous source/target construction is supplied.

## Contract and inherited implication

Use the same PR1972/1991 104-port correction `C = I-G/2` as PR2889 and
PR2896. Sources X are immutable, targets Y are unread, and their fixed frame
paths increase by inclusion. New helpers start source-independent at ZERO,
end at FULL with their logical dirt restored, and follow increasing frame
paths. Reinitialization starts another lifetime. Original helper/private
reads, target feedback, source writes, descending transport and changed
original paths are outside this model. Equal-frame rational mixing, relays,
singular mixing and cancellation remain allowed.

The two types are the dimension-jump histories `(1,7,1)`, called cheap below,
and `(1,1,1,1,1,1,1,1,1)`, called unit-step. Both visit dimension one and
dimension eight exactly once. A nested lifetime can meet at most one
specified source line and one specified target hyperplane.

We use PR2896's written dependency-path implication. Every residual source
label at a target endpoint must arrive on a new helper from a proper
subspace. The dual statement applies to residual target normals after a
source departure. A cheap lifetime carries at most one such label in each
orientation. A unit-step lifetime carries at most the endpoint's proper
subspace capacity. Logical dirt and cancellation cannot create a missing
source-dependence path. This package adds demand saturation to that necessary
implication, rather than claiming a new proof of the full network interface.

The checker reconstructs the original chronological X/Y paths and the
ordered root Gram correction directly from the two main-branch inputs. It
reconstructs all residual sets and enumerates all 510 ambient functionals
other than the endpoint annihilator. These give the 255 proper hyperplanes
inside each eight-dimensional endpoint, each twice. Every proper subspace
extends to one of these hyperplanes. The resulting 208 records exactly
match the pinned PR2896 receipt, without importing its implementation.

Both orientations have the same multiset of demand/capacity pairs:

| Demand d | Unit capacity b | Endpoint count |
|---:|---:|---:|
| 36 | 24 | 12 |
| 44 | 28 | 24 |
| 45 | 30 | 8 |
| 46 | 29 | 24 |
| 47 | 30 | 24 |
| 48 | 30 | 12 |

## Exact allocation bound

At endpoint i let `u_i` and `c_i` count assigned unit and cheap lifetimes.
Every permitted network satisfies the relaxed necessary inequalities

```text
d_i <= b_i*u_i + c_i
sum_i u_i <= U
sum_i c_i <= C.
```

An endpoint can usefully receive at most `d_i` distinct demands. Its first
unit therefore contributes at most `b_i`, its second at most `d_i-b_i`,
and later units contribute zero. Here `b_i < d_i <= 2*b_i`. The marginal
contributions decrease within every endpoint.

Sort all 208 marginals in decreasing order, placing a first unit before
its second in a tie. Let `F(U)` be the sum of the first `min(U,208)` entries.
The selected entries respect every endpoint prefix, so their allocation is
valid in this relaxation. Any U units have useful contribution at most
F(U), since no U entries can exceed the U largest. Therefore the exact
minimum number of cheap lifetimes in this relaxation is

```text
C_min(U) = 4656 - F(U).
```

The lower bound follows by summing the remaining demands. It is attained
in the relaxed count problem by placing one cheap lifetime on each remaining
demand. This attainment does not assert that actual subspaces realize the
capacities or that the assignments in opposite orientations can be joined.

For U=147, the first 104 marginals sum to 2,976. The next 43 are
`12*18 + 31*17 = 743`, so `F(147)=3719` and `C_min(147)=937`.
With C=253, the total useful contribution is at most 3,972. This is already
an obstruction in either orientation separately.

A second implementation uses integer dynamic programming. After each
endpoint it minimizes the cheap count for each exact unit count, considering
zero, one or two units there. It does not use the sorted marginals. The two
methods agree at all 209 budgets in both orientations. RESULT.json records
the complete curve and explicit relaxed allocations at the 192-unit threshold.

## Reproduce and evidence

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-endpoint-saturation
```

The main command prints
`PASS_P104_ENDPOINT_SATURATION deficit=684 minimum_units_at_400=192`.
Use `verify.py --emit` to print the recomputed receipt without changing files.
The registered normal and optimized checks compare the complete typed receipt.
Five behavioral test groups cover 780 exhaustive small allocation problems,
the literal rejection/threshold, invalid domain bounds, a semantic mutant
that removes demand saturation, a Git-free export, source corruption and an
integer-to-float receipt corruption. Subprocesses have 30-second timeouts.

Evidence is author-checked. The allocation algorithms are separate
implementations, while both use the same reconstructed geometry and inherited
program-to-endpoint implication. No independent human or formal-kernel review
is claimed. Source hashes, the exact PR2896 snapshot and main provenance are
in SOURCES.json; scope and freshness are in TASK.json.

No moment or new exponent is claimed for any replacement profile. The
selected frontier and frozen predecessors are unchanged. Native execution,
rounded restoration, physical hosting/movement, all-size lifting and a complete
consumer/supplier invoice remain open. The selected cold replay is not run
because this package does not change the selected construction.

Engineering choices follow Build the Lever, through the reproducible integer
certificate, and Prove It Works, through original-input reconstruction and
rejecting controls. All functions are below 60 lines. Loop bounds come from
104 endpoints, 4,058 events, 512 frame vectors, 209 DP states and the explicitly
enumerated 780 toy cases. The input boundary limits each JSON file to 2 MB.
Python's managed allocation is a Power of Ten rule 3 deviation; the fixed
finite domains bound live collections, and temporary test exports are cleaned
on success and failure. A fixed-array port would be appropriate if this checker
became a resident or streaming service. The inherited source contract and
all-size theorem are not strengthened by these implementation checks.

## Open next questions

Can a named two-type profile with at least 192 unit-step lifetimes satisfy
actual subspace-union coverage, joint source/target incidence and chronology,
while retaining a favorable complete cost? First price a concrete candidate
against the inherited optimistic budget, then test its actual endpoint sets.
The count relaxation supplies neither that budget nor a construction.

Family decision: stop after the endpoint-assignment audit. Do not start another
construction round merely because the 192-unit count threshold passes. Any
continuation needs a stated candidate, complete boundary/cost ledger and an
identified geometric or chronological constraint that can change the decision.

## Credit and provenance

Nick Petalas. New work is Apache-2.0. The source-bound allocation implication
and checker are the contribution here. Credit Nick Petalas/PR2896 for the
residual endpoint capacities and handoff, Hiroki Kumazaki/PR2889/2353 for the
endpoint-span and monotone-history model, ywz65/PR2614 for source-departure
handling, Arham Tahir/PR2675/2682 for coupled screens, Sagar Thakrar for the
mixer handoff, and Philippe Van Velzen for the relay construction/window bill.
Retain Rohan Arun/PR1972, Chafik Boukhalfa/PR1991, Adam Gall/PR1940,
Josie Elliston/PR1071, Ali Romman/PR1125 and the geometry/native lineage.
The byte-exact predecessor RESULT.json is data from PR2896, not a new result
of this package. Substantial AI assistance was used; details are in TASK.json.

[2896]: https://github.com/CrocSwap/integer-mult-bounds/pull/2896
