# Independent expanded accounting for the direct mixed compiler

The complete recursive accounting in zxv's [PR4436](https://github.com/CrocSwap/integer-mult-bounds/pull/4436)
passes this independent check. Every source complement and exit receives an
integer number of smaller uniform batches. Counting their repeated instances
gives

```
B_n n − P_n = Δ Q_n,       U_n ≤ Q_n ≤ B_n n / Δ   (Δ > 0).
```

Here `B` is productive width, `P` counts rank-one paid leaves, `U` counts
expanded raw invocation instances, and `Q` sums their positive integer column
multiplicities. [PROOF.md](PROOF.md) gives the induction and its assumptions.
This corroborates the predecessor's theorem; it is not a new construction or
κ improvement. In particular, the large example below is not a winning supplier.

## Coverage added

Ryanson Jonathan's [PR4456](https://github.com/CrocSwap/integer-mult-bounds/pull/4456)
checks individual flow mass and normalized leaf costs.
[PR4476](https://github.com/CrocSwap/integer-mult-bounds/pull/4476) adds widths,
routing identities and finite growth measurements, while explicitly excluding
the fully expanded identity above. This package checks that remaining count
boundary, including raw instances and column multiplicities that cannot be
recovered from a normalized leaf count alone.

The checker is separate from the producer. `forest.py` labels units by ordered
target words, matches the last target letter to a child slot, then counts equal
products by exact convolution. It does not import the producer's multinomial
matcher. Individually enumerated words check the compression, including
collisions such as `2·8 = 4·4`.

`accounting.py` constructs a counted call graph and evaluates every edge with
its full multiplicity. A second evaluation propagates invocation weights from
the root toward the leaves. `literal.py` separately builds small programs and
visits every raw instance, routing slot, leaf and child invocation. These paths
share the new local forest generator; they are not mutually independent local
flow implementations. None computes `Q` by rearranging the identity under test.
The literal traversal is an accounting traversal, not a native execution schedule.

## Exact evidence

All five expanded totals match the immutable predecessor receipt: productive
width, paid leaves, raw instances, raw column mass and routing slots.

| Domain | Checked scope |
| --- | --- |
| Two overlap examples | Every compiled rank through 100; complete final counts match PR4436 |
| Raw p7, surplus 608 | All 880 nonbase ranks 121–1000; all five rank-1000 totals match |
| Four small rule families | 44 complete literal expansions, including rank zero |
| Local source controls | All nine released flow fixtures; five equal-product collision fixtures |
| Failure controls | 14 named semantic rejections, after source authentication |

The larger literal examples make the difference between `U` and `Q` visible:

| Rule and final rank | Width `B` | Leaves `P` | Instances `U` | Column mass `Q` | Visited records |
| --- | ---: | ---: | ---: | ---: | ---: |
| Strict overlap, 13 | 8,192 | 91,904 | 12,544 | 14,592 | 265,025 |
| Source-open equality, 6 | 3,500 | 18,500 | 1,750 | 2,500 | 71,421 |
| Separated control, 13 | 6,400 | 51,200 | 10,880 | 16,000 | 202,501 |

The p7 width at rank 1,000 has 17,504 bits. Its complete program is counted
through an exact finite call graph, not literally enumerated. Full integer
hashes, counts and rejected faults are in [RESULT.json](RESULT.json).
Faults include omitted complements/exits, missing replication, deduplicated
child instances, incorrect raw columns, a missing base leaf and a nonintegral
batch. Zero and negative surplus reject the division-bound guard.

For a hand-checkable example, a rank-two target with one paid rank-one job has
`Δ=1`. At rank three the complete program needs a rank-one complement and a
rank-one exit: `3−2=1`. Omitting the complement gives `3−1≠1`, even though
the unchanged local flow still passes its own conservation check.

## Reproduction and sources

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/direct-flow-expanded-audit
python3.12 -I -O -B research/direct-flow-expanded-audit/verify.py
```

Expected marker: `PASS_DIRECT_FLOW_EXPANDED_ACCOUNTING`. The default recomputes
and compares the full saved receipt. `--emit` prints a newly computed receipt.
Direct replay also works from an exported package without Git or network.

`SOURCE-EXPORT.json` records exact original commits, paths, Git blobs and
SHA256 hashes for the unchanged exports. Their bytes were compared directly
with the original Git objects before retention. PR4436 is pinned at
`56003680aee2871773de408e5f01cc5dd46b144c`; PR4476 at
`4e7022aa9128c8673d3e2024052b2deaa18cb6e4`. `SOURCES.json` additionally pins
the retained bytes to this contribution's source commit. No pending source
commit is represented as publication ancestry. The p7 tariff comes from the
original native receipt; native correctness is inherited, not rechecked.

This work starts from canonical main
`2a13eb1827784206202db90e5dc8327cf8a250db`, priority revision 7. Live PR and
bounded Discussion overlap coverage is recorded in `TASK.json`. The later
[PR4483](https://github.com/CrocSwap/integer-mult-bounds/pull/4483) changes
the height and exponent argument; that theorem is outside this audit.

## Limits

The written induction applies to every finite local flow satisfying its stated
integer, rank-descent and conservation assumptions. Finite tests corroborate
the implementation; they are not a formal proof of those assumptions for every
native caller. An `O_local·U` center-bank bound further assumes at most
`O_local` separately owned banks per invocation. It does not measure bank
capacity, peak-optimal storage or extra router scratch.

The record/description grammar, encoded precision constants, native correctness,
physical movement, ownership, exponent convergence, analytic transfer and full
multiplication theorem are not verified. No selected-frontier file changes.

## Open next questions

The next useful check is to bind one small expanded program to its actual
native executor: identify each bank allocation, adapter, movement and erasure,
and charge all router scratch. That would test whether this accounting model
matches physical use. The missing native and physical contracts are the blocker;
larger count scans would not discharge them. Structured details are in `TASK.json`.

## Credit

Prepared by Dillon (@dillona) with substantial OpenAI Codex assistance, including
separate implementation and mathematical review agents. No independent human
or formal-kernel review is claimed. Apache-2.0.

Credit zxv for PR4436's construction and expanded-count theorem; Jacob Alan
Sussman for the lockstep/Pascal compiler; Ryanson Jonathan for PR4456 and PR4476
and their explicit coverage boundary; Cinna Davis for the raw p7 construction;
and the native, controller, BIT, Clifford, geometry and outer predecessors
credited by those sources. Original Sussman LICENSE and NOTICE are retained.
