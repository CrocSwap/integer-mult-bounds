# Selected routes exclude the four-six-cycle equality graph

This contribution was produced by Nick Petalas. It supplies a scoped written
proof with exact finite corroboration, with no new kappa.

The fifteen-owner repair boundary has an abstract equality graph with four
six-cycles. Krzysztof Wójt's [PR #5239](https://github.com/CrocSwap/integer-mult-bounds/pull/5239)
classifies the entire nonzero-six-cycle branch as this graph. The new result
excludes its realization by the selected historical calls-0/4 centre routes
and nonzero query coefficients.

dcharb78's [PR #3147](https://github.com/CrocSwap/integer-mult-bounds/pull/3147)
supplies the unique dependent-triple completion of every allowed braid pair.
Consequently every edge leaving a given six-cycle must
have the same port label. Edges between the four cycles force all those
external labels to agree. The two edges B3-D0 and B3-D7 would then have equal
labels, contrary to the distinct-port requirement at B3.

Thus a nonzero common-kernel perturbation on exactly fifteen source owners
must have a six-cycle-free incidence graph, conditional on the cited graph
classification, unique completion and source route premises. The support floor remains fifteen.
The six-cycle-free branch is unresolved.

[PROOF.md](PROOF.md) states the precise model, separates inherited premises
from the new finite lemma and proves the contradiction. The original route,
graph, dependent-triple and coset censuses are cited without replay.

## Reproduce

From the repository root, using the available CPython 3.12 interpreter:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/fifteen-owner-cycle-route-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/fifteen-owner-cycle-route-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/fifteen-owner-cycle-route-obstruction
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/fifteen-owner-cycle-route-obstruction --check-source-history
```

Substitute another installed absolute CPython 3.12 path elsewhere. In a sparse
checkout, first materialize this package and the graph input path declared in
[VERIFY.json](VERIFY.json). The input directory is `research/centre-equality-six-cycles`.

The direct verifier prints a generated JSON receipt bound to every package
file and the cited graph input, followed by
`PASS_FIFTEEN_OWNER_CYCLE_ROUTE_OBSTRUCTION assignments=256 legal=0 collision=B3`.
It checks the external-edge implication and three independent relabelings of
the graph's two parts. All 256 assignments of four colors to the four cycle
labels yield four assignments obeying the cycle links and zero with distinct
ports at B3. Renaming colors covers every equality pattern on four labels.

Controls reject a broken named cycle and repeated cycle vertices. A positive
fixture admits one cycle with separate external leaves, so a single cycle
alone does not trigger the collision test. Normal and optimized execution
retain every check. The replay does not enumerate a predecessor's result.

## Scope and sources

The original `centre-path-sharing` card is changed to a structural side result
at the older whole-later-query block-repair boundary. It removes one abstract
equality branch before a costly route search. It supplies no current caller
replacement or paid-profile gain. The selected binding orientation passed
with selected kappa `781451/250000000`, and is only a metadata control.

[SOURCES.json](SOURCES.json) pins all inputs at canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision eight.
The graph is the sole executable input. The route and coefficient premises,
including dcharb78's unique-completion result at exact head
`5cbc48b18cb05327a8dacab3f626412d3bc5e924`, are mathematical citations. The
registered command neither fetches that pending source nor validates it.
Source-byte authentication of the graph does not prove these premises.

The live overlap helper covered 744 open PRs and 6,863 Discussion records at
2026-11-06 13:44 UTC. Its local scan was sparse, so separate Git searches
covered all main-branch package READMEs for the graph, route-label and
completion terms. Merged and all-state PR searches, recent account work and
current claims were also checked. Arbitrary historical diffs and unpublished
work remain outside that coverage. The advance
[CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19441291)
states the delivered scope.

The code uses bounded collections, integer label comparisons and no
recursion, subprocesses, network, source compilation or write paths. Its main
domains are a fifteen-by-fifteen graph, four cycle labels and 256 assignments.
Functions stay below sixty physical lines. Python managed allocation replaces
fixed allocation. Input size and finite domains bound live memory; no static
allocation claim is made. The receipt hash walk scales with the package file
inventory. The failure controls have two fixed callback targets. Warning-strict
normal and optimized runs provide the available diagnostics. No static type
checker is configured for this isolated standard-library script.

## Open next questions

1. Can a six-cycle-free fifteen-owner equality graph carry the actual routes
   and coefficients? Begin with the classical duad/perfect-matching example
   and impose its eight-cycle route equations. A complete route labeling and
   nonzero coefficient solution remain missing. This result does not establish
   uniqueness of that abstract branch.
2. Can the external-label propagation criterion exclude a larger support
   graph with connected six-cycle components? First identify its cubic cycle
   vertices and exact boundary edges. Higher-degree vertices need a different
   coefficient argument, and no larger support exclusion follows here.

No physical acquisition, restoration, hosting, precision, stock, recursive
invoice, supplier admission or complete multiplication theorem is supplied.
The five selected framework assumptions remain. Independent human and formal
proof-kernel review, the selected cold replay, Lean and Docker are unrun.

## Credit

Credit dcharb78 #3147 for unique completion; Krzysztof Wójt #5239 for the
graph and nonzero-cycle classification;
Sagar Thakrar #3291 for the sharp abstract floor and route-to-graph theorem;
Nick Petalas #5182 for the equality reduction; and Matarener #3656 for the
distinct 4,080-owner construction. Retain Ross Richardson #3071, dcharb78
#3147, Gonzalo Mier #3097, Sudarsh Chaturvedi #3168, Aaron Wang/navinor,
ywz65 and the selected centre lineage for the observations, source extraction
and route premises. The new work is the forced-label exclusion and its
application to this graph. Predecessor files and notices remain unchanged.
Apache-2.0.
