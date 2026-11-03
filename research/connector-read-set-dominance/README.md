# Prune 374 states from a joint dirty-connector search

A cost-aware superset rule reduces the complete six-transfer search from
463 expanded states to 89 on one new fixed instance, while preserving
every possible minimum-read continuation. Claim type: scoped written
algorithmic proof with an exact finite certificate. No new kappa.

At the same source cut and physical frame, label (S,c) dominates (T,b)
when S contains T and c <= b. S and T are historical sets of available
read vectors; c and b are paid root-transfer costs. Reject dominated
offers and retire dominated queue entries. [PROOF.md](PROOF.md) proves
the simulation and acceptance equivalence, including arbitrary dirty roots
and noncommuting opaque child maps.

This answers the dominance-pruning part of ywz65's
[PR2538](https://github.com/CrocSwap/integer-mult-bounds/pull/2538)
Open next questions. Its graph semantics and completeness are cited premises.
Its four published fixture optima and executable are not replayed or audited.
The new fixture has source order (0,0,1,1,2,2), colors (1,2,3), and all seven
nonzero target masks. The alphabet is unchanged, so [TASK.json](TASK.json)
records a changed scope from the connector-alphabet card to a search method.

## Exact result and evidence

The minimum read counts are two for masks 1 through 6 and three for mask 7.
At this total of 15 reads, the exact minimum is six root transfers. The
certificate enumerates every state through this accepting budget. It
independently postprocesses the unpruned graph to obtain its full undominated
frontier and compares every label with the incremental result.

| Transfer cost | Complete graph expansions | Pruned graph expansions |
| --- | ---: | ---: |
| 0 | 3 | 3 |
| 1 | 9 | 7 |
| 2 | 23 | 12 |
| 3 | 44 | 16 |
| 4 | 84 | 20 |
| 5 | 145 | 18 |
| 6 | 155 | 13 |
| Total | 463 | 89 |

The pruned run discovers 102 labels, retires 13 and rejects ten dominated
offers. Each of the complete graph's 463 states has a retained dominator
with the same cut/frame and no greater cost. The complete graph digest is
`18712a812ab2c5613dbb9486f1a5d0383883865d127ce59c2562429e883589e5`;
the retained frontier digest is
`7f457ff549506542344ea4297f089b3e7ed91fcfed45518869801ac9cc56963d`.
Both are regenerated from the entire sorted state/cost lists.

The five-transfer graph rejects the minimum-read target. The emitted
27-operation witness has six B calls, 15 A calls and six root shears.
A separate formal-polynomial interpreter checks its endpoint and inverse
for arbitrary dirty inputs without commuting any A and B operators.

Ten controls check subset direction, incomparable sets, the cost condition,
retirement, an omitted read, state-cap exhaustion, transfer-limit rejection
and two invalid instances. Checks use explicit exceptions under both normal
and optimized Python. The generated stdout receipt hashes every package file
and binds the complete graph, retained frontier and emitted word. No receipt
is handwritten or stored in the checkout.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/connector-read-set-dominance
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/connector-read-set-dominance --check-source-history
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/connector-read-set-dominance/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/connector-read-set-dominance/verify.py
```

Another CPython 3.12 executable can replace the local interpreter path.
The direct commands emit `PASS_CONNECTOR_READ_SET_DOMINANCE` inside a JSON
receipt. The registered runner executes both modes. No timing speedup is
claimed; state counts are the measured improvement.

Local checks used CPython 3.12.15, macOS 27.0.1 arm64 and no dependencies
beyond the standard library. The registered normal and optimized commands
were also timed directly at 0.037 s and 0.061 s, with empty stderr and identical
receipts. These are completion durations, not performance comparisons.

## Limits

The proof covers this fixed minimum-read interface. The implementation accepts
one through six sources, transfer budgets through 24 and a discovered-label
cap of 250,000. Exceeding a resource limit fails explicitly. Verification
certifies the displayed three-source fixture, not every accepted instance.
Python managed allocation is bounded by these finite input/resource caps,
rather than fixed preallocation. [PROOF.md](PROOF.md) states loop bounds.

No n9/n12 solver result, weighted read/transfer envelope, runtime speedup,
physical child tariff, recursive caller, native admission, hosting,
precision/tape proof, selected cold replay, Lean or Docker run is supplied.
No new supplier or complete multiplication theorem is claimed. The selected
frontier and all five framework assumptions retain their status. Independent
human and formal proof-kernel review are unclaimed.

## Open next questions

1. Can an indexed superset query make this exact pruning practical for the
   predecessor's n9/n12 walks? Start with one pinned word and measure the
   nondominated frontier. The present implementation's six-source and
   resource caps are blockers; this package claims no scaling result.
2. Can a concrete caller use the two-root interface at a favorable complete
   tariff? First bind its child ports and pay admission, preparation, routing,
   restoration, precision and tape return. Search-state reduction alone
   supplies none of those costs.

Structured questions and scope are in [TASK.json](TASK.json).

## Credit

This contribution was produced by Nick Petalas. Credit ywz65 / PR2538 for
the read-availability graph, the open pruning question and its retained
joint synthesis lineage; conorholds / PR2208 for fixed-color dirty-root
framing; Ross Richardson / PR934 and PR943 for the connector interface.
ywz65 / PR2561 studies the separate read/transfer tradeoff. Dominance and
shortest-path methods are classical. [SOURCES.json](SOURCES.json) pins the
predecessor statement and the originating catalogue and selected record.
Only the predecessor README is a live source input; no predecessor code is
imported. Apache-2.0.
