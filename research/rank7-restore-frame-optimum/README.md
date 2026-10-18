# Exact restore-frame optimum for the six-skip words

Neither pinned PR3042 word admits a cheaper monotone restore-frame assignment
with its scalar operations, order, prefix and endpoints fixed. The finite
census covers **2,160,000 legal assignments per provider**, including frame
contractions and rotations. There are exactly 32 equal-cost assignments.
This is a scoped optimality result, with **no new κ or supplier admission**.

This follows [PR3053's frame-reassignment handoff][3053] on the newer
[PR3042 six-skip words][3042], exported without modification from
[PR3054][3054] at `4773c3ea67b471415870e38411fae313ec44a675`.
Canonical main was `d8e0f83f00191df62174b641e9fff055c357f641`, priority
revision 6. The selected record is unchanged.

## Exact claim and price

Keep both words' A/B operations and warps, restore scalar operations and order,
live-register set, entrance frames and terminal frames fixed. Replace any or
all of the 212 restore frames by arbitrary subspaces of F₂⁹. Each scalar gate
must have a common frame for its operands, and every register's frame chain
from its fixed restore entrance to its terminal frame must be monotone.

This defines a relaxation of native admissibility. It does not assert that
every assignment passes the native cone, phase or operator checks.

The complete source local profile, independently recounted from the fixed
prefix and all frame transitions, is

```text
{1:2433, 2:712, 3:232, 4:108, 5:18, 8:8}.
```

Every legal assignment has profile difference

```text
d * (2 H1 - H2),     d = 0,...,9,
```

where `Hr(b) = r(73/r)^b`. Consequently

```text
2 H1(b) - H2(b) = 2 * 73^b * (1 - 2^(-b)) > 0   for every b > 0.
```

There is no numerical root calculation or floating-point acceptance gate.
All assignments have the same rank mass; every nonzero difference is strictly
dearer at every positive saving exponent. Counts for `d=0,...,9` are

```text
32, 1056, 12936, 79408, 274560,
558000, 661824, 430272, 130248, 11664.
```

Both variants have identical restore problems and these exact multiplicities.
The helper width inventory remains
`{4:26, 5:2, 6:16, 7:52, 8:99, 9:213}`, with all 91 private returns retained.
Under the unchanged inventory/owner contract, the idle bill cannot supply a
new saving from these restore-only frame choices. This package does not replay
the literal allocation or independently admit its physical contract.

## Why the census is complete

1. Trace the literal A/B prefix and its fixed warps to each register's restore
   entrance. Keep the original terminal frame for each live register. The
   complete local profile and helper widths must match the source declarations.
2. Propagate forward, assigning each gate the join of its operands' current
   lower bounds. Induction gives a lower bound on every feasible gate frame.
   Propagate backward with intersections of the operands' future upper bounds
   to obtain an upper bound. These implications apply to arbitrary subspaces,
   without requiring containment in or containment of the original gate frame.
3. In this instance, 185 intervals are singletons and 27 are variable. Every
   quotient has dimension at most two. Repeatedly adjoining one vector to the
   lower subspace exhausts all intermediate subspaces in at most two rounds.
   In particular, a two-dimensional quotient includes its three distinct lines.
4. Join variable gates whenever they are consecutive on one register. This
   produces nine components. Every variable-dependent containment condition
   and transition cost belongs to exactly one component. All other edges have
   fixed endpoints and zero cost difference. Thus no constraint or cost term
   couples different components through a forced node.
5. Enumerate each component's Cartesian product, rejecting every noncontained
   register transition. There are 542 component candidates, of which 62 are
   legal. The product of the nine legal counts is 2,160,000. Every retained
   assignment has delta `d(2H1-H2)` with `d >= 0`. Convolving their integer
   multiplicities gives the displayed distribution.

Any globally legal assignment lies in these intervals and passes these edge
tests. Conversely, any combination of accepted component assignments has all
required containments, so it is legal in the stated relaxation. This proves
completeness and component independence, rather than relying on failed search.

## All minimum-cost assignments

Every ADD frame and every other SCALE frame equals its source frame. Only
these five independent SCALE choices remain, each at either interval endpoint:

| Restore index, zero-based | Register | Lower rank | Upper rank | Source endpoint |
|---|---:|---:|---:|---|
| 12 | 311 | 6 | 8 | Upper |
| 67 | 554 | 6 | 8 | Upper |
| 98 | 428 | 7 | 8 | Upper |
| 101 | 412 | 7 | 8 | Upper |
| 210 | 96 | 8 | 9 | Lower |

The two rank-six to rank-eight intervals also have three intermediate frames;
each intermediate choice costs an additional `2H1-H2`. The 32 ties are counted
frame assignments in the relaxation, not 32 newly certified native programs.

## Reproduction and evidence

Python 3.12, standard library only. Each command takes about one second on the
recorded macOS host:

```sh
python3.12 -B -W error research/rank7-restore-frame-optimum/verify.py
python3.12 -B -W error -m unittest discover \
  -s research/rank7-restore-frame-optimum -p 'test_*.py' -v
python3.12 -O -B -W error research/rank7-restore-frame-optimum/verify.py
python3.12 -B scripts/research_package.py --package research/rank7-restore-frame-optimum
```

The final verifier line is

```text
PASS_RESTORE_FRAME_OPTIMUM providers=2 legal_each=2160000 optimal_each=32 component_attempts_each=542 no_new_kappa
```

[RESULT.json](RESULT.json) contains the recomputed component receipts and
complete multiplicities. To regenerate it, add `--output /path/to/RESULT.json`.
The verifier does not consume that receipt. [SOURCES.json](SOURCES.json) binds
the two literal gzip exports to their public head, original paths, Git blobs
and SHA256s. Source hashes are checked before parsing. No Git, network, solver,
predecessor Python import or cached numerical receipt is needed for the proof
replay. The generic metadata checker separately checks base/catalog provenance.

Eleven behavioral groups include an easy case where the harness really finds
a cheaper profile, two-gate coordinated choices, independent components,
rotated subspaces, equal-rank wrong-axis rejection, input/capacity failures,
source drift, nonmonotone frames, stale profiles and false helper widths.
The checks remain active with `-O`. Python 3.12 and 3.14 produce identical
receipts. A separate internal implementation independently reconstructed all
component counts, the global distribution and the five-scale classification.
This is author-checked evidence with internal review, not independent human
or formal-kernel validation.

## Scope and stopping decision

Single-gate promotions had no improving candidate. Complete restore-frame
reassignment was then small enough to exhaust, so it replaced the planned
commuting-order pivot. The strict-improvement target was not met. This package
retains the useful exact negative result and stops construction work here.

This does not exclude changing A/B frames jointly with restore frames,
reordering or replacing scalar gates, adding operations or helpers, changing
endpoints or entrances, using nonmonotone transforms, changing physical
contracts, or changing the coverage law. Arbitrary dirty-input scalar/operator
correctness, cleanup, source/native realization, allocation, precision/tape,
stock/caller, analytic and all-size/compiler obligations remain inherited.
No full cold replay or outer release was run for this unchanged-word bound.

[PR1995/2013][2013] gives earlier fixed-word frame bounds, with credit to
Gareth Davidson. Its selected scalar word and cleanup contract differ from
these six-skip words. This result supplies the new restore-only instance and
does not replace that broader work or close the full PR3053 handoff.

## Open next questions

Can a changed scalar block or a coupled A/B/restore assignment save work?
The theorem identifies the premise that must change. Start with one exact
changed block or prefix boundary, prove its arbitrary dirty-input identity,
and derive its complete frame bill before expanding a search. Changed
semantics or prefix bounds, followed by native/admission/outer review, are
the blockers. See [TASK.json](TASK.json) for the structured handoff.

## Credit and engineering choices

Credit dcharb78 for PR3042's literal six-skip words, Sagar Thakrar for PR3053's
independent R1 audit and handoff, Jeremy Kothe for R1 and the inherited frame
accounting/cleanup conventions, Marius-Paul Dumitrean for PR2979's coordinated
rank-seven construction, Nick Petalas for the PR3054 export, and Gareth
Davidson for interval propagation and fixed-word monotone-frame bounds.
The retained lineage includes Mason Hale, Jeremy Diviney, Yiyang Lu,
Ross Richardson, Tekalign, Dugongue, icekylinx and themilkman216.
The original [notice](inputs/NOTICE-PR2979) remains unchanged. Apache-2.0.

Build the Lever led to the rerunnable exact census. Foundational Thinking
led to explicit vector sets, making containment and rotated frames visible.
Prove It Works led to an improvable control and a separate complete
reconstruction, rather than treating a PASS receipt as independent evidence.

Power of Ten review found no recursion, generated code, hidden dispatch or
mutable shared state in the proof path. Functions fit within 60 physical
lines. Explicit limits bound frames to 512 vectors, 704 registers, 212 restore
events, 32 variables, five choices per interval and 4,096 candidates per
component. Contract checks use exceptions and survive optimization.

Managed-memory deviation, rule 3: Python allocates sets, decoded JSON and
temporary counters during replay. Fixed input-byte limits and authenticated
exports bound those allocations; components stream one assignment at a time.
This deviation covers this finite proof replay only. Verification includes
input/capacity rejection and a recorded allocation measurement. Reassess
the bounds before supporting a larger input family; use fixed-capacity
storage if a runtime without managed allocation is required. Warning and
lint commands and the measured environment are in [ENVIRONMENT.json](ENVIRONMENT.json).

[3042]: https://github.com/CrocSwap/integer-mult-bounds/pull/3042
[3053]: https://github.com/CrocSwap/integer-mult-bounds/pull/3053
[3054]: https://github.com/CrocSwap/integer-mult-bounds/pull/3054
[2013]: https://github.com/CrocSwap/integer-mult-bounds/pull/2013
