# Selected routes exclude the four-six-cycle equality graph

This contribution was produced by Nick Petalas. It supplies a scoped written
proof with exact finite corroboration, with no new kappa.

The fifteen-owner repair boundary has an abstract equality graph with four
six-cycles. Krzysztof Wójt's [PR #5239](https://github.com/CrocSwap/integer-mult-bounds/pull/5239)
classifies the entire nonzero-six-cycle branch as this graph. The new result
excludes its realization by the selected historical calls-0/4 centre routes
and nonzero query coefficients.

For each of the fifty allowed braid pairs, exactly one other query column
lies in their span. Consequently every edge leaving a given six-cycle must
have the same port label. Edges between the four cycles force all those
external labels to agree. The two edges B3-D0 and B3-D7 would then have equal
labels, contrary to the distinct-port requirement at B3.

Thus a nonzero common-kernel perturbation on exactly fifteen source owners
must have a six-cycle-free incidence graph, conditional on the cited graph
classification and source route premises. The support floor remains fifteen.
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
checkout, first materialize this package and the four input paths declared in
[VERIFY.json](VERIFY.json). Their directories are `centre-block-moore-bound`,
`centre-block-repair-information`, `centre-equality-six-cycles` and
`community-frontier1094-audit`, all under `research/`.

The direct verifier prints a generated JSON receipt bound to every package
file and all four input files, followed by
`PASS_FIFTEEN_OWNER_CYCLE_ROUTE_OBSTRUCTION pairs=50 tests=5500 collision=B3`.
It enumerates the 110 candidate third columns for each of fifty cited braid
pairs, tests all eight coordinates exactly, and prints the complete completion
table. It checks the new external-edge implication on the cited graph and
three independent relabelings of its two parts.

Controls distinguish full-coordinate span membership from a false test using
only two coordinates, detect a nonunique completion, reject a parallel pair
and a broken named cycle, and admit a single cycle with separate external
leaves. That last fixture shows that one cycle alone does not trigger the
new collision test. Normal and optimized execution retain every check.

## Scope and sources

The original `centre-path-sharing` card is changed to a structural side result
at the older whole-later-query block-repair boundary. It removes one abstract
equality branch before a costly route search. It supplies no current caller
replacement or paid-profile gain. The selected binding orientation passed
with selected kappa `781451/250000000`, and is only a metadata control.

[SOURCES.json](SOURCES.json) pins all inputs at canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision eight.
The predecessor row extractor prepares the exact query matrix from the pinned
canonical archive. Its main verifier and historical scientific comparisons
do not run. The fifty braid pairs and the graph classification remain cited
mathematical premises. Source-byte authentication does not independently
prove those premises.

The live overlap helper covered 744 open PRs and 6,863 Discussion records at
2026-11-06 13:44 UTC. Its local scan was sparse, so separate Git searches
covered all main-branch package READMEs for the graph, route-label and
completion terms. Merged and all-state PR searches, recent account work and
current claims were also checked. Arbitrary historical diffs and unpublished
work remain outside that coverage. The advance
[CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19441291)
states the delivered scope.

The code uses bounded collections, exact arithmetic and no recursion,
subprocesses, network or write paths. Its main domains are fifty pairs,
112 columns of height eight and a fifteen-by-fifteen graph with four named
cycles. The single pinned extractor uses source compilation; its authenticated
bytes and explicit calls bound that exception to the metaprogramming rule.
Python managed allocation replaces fixed allocation. Input sizes and finite
domains bound live memory; no static-allocation claim is made. The receipt
hash walk scales with the package file inventory. Warning-strict normal and
optimized runs provide the available diagnostics. No static type checker is
configured for this isolated standard-library script.

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

Credit Krzysztof Wójt #5239 for the graph and nonzero-cycle classification;
Sagar Thakrar #3291 for the sharp abstract floor and route-to-graph theorem;
Nick Petalas #5182 for the equality reduction; and Matarener #3656 for the
distinct 4,080-owner construction. Retain Ross Richardson #3071, dcharb78
#3147, Gonzalo Mier #3097, Sudarsh Chaturvedi #3168, Aaron Wang/navinor,
ywz65 and the selected centre lineage for the observations, source extraction
and route premises. The new work is the unique-completion property and the
forced-label exclusion. Predecessor files and notices remain unchanged.
Apache-2.0.
