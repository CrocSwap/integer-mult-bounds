# Checkable caller coverage for the historical P112 (6,4) cell

This package reconciles all 69 original TWOSIDE `(b,t)=(6,4)` survivors
against six pinned published contracts. Conditional on those contracts,
62 are certified and seven are outside this inventory. The new artifact is
the source-bound composition and exact caller coverage. Earlier exclusions
retain their credit and are not claimed as new mathematical results.

The historical count 69 is reproduced on all 7,546 multisets by the retained
DreamingOfClouds/PR3154 filter and a separate implementation. Every row in
[RESULT.json](RESULT.json) names its successful contracts, indexed role
assignments, surviving code dimension and one common support cap. All failed
attempts are retained. [PROOF.md](PROOF.md) proves the deletion, restriction,
monotonicity and seven-flat caller implications.

The six contracts are Nick Petalas's PR3262, PR3205, PR3260, PR3186, PR3192
and PR3253. Their exact proof bytes and PR3154's original filter are retained
under vendor/, with heads, blobs, hashes and fixed usages in
[SOURCES.json](SOURCES.json). The full inventory is checked before retained
code runs. A source cannot bypass authentication by changing its usage.
Their prior E8/P112, root-simplex, SMALL2/Pencil and joaqcoo lineage keeps
the attribution in the retained sources.

## Reproduce

Python 3.12 or later and the standard library suffice. No pending PR Git
objects, network, native compiler or historical census outputs are needed.
From the repository root:

```sh
python3.12 -W error -B scripts/research_package.py \
  --package research/p112-b6-t4-reconciliation
```

The registered runner gives each command a private bytecode namespace.
The direct commands are `verify.py`, `independent.py` and
`python -O test_verify.py` in this package, with `-W error -B`. Run direct
checks from a source-only export or with a fresh private
`PYTHONPYCACHEPREFIX`. All replays compare committed receipts without
regenerating them. The controls reject inventory/usage/provenance changes,
changed executable source, invalid weights, an incorrect deletion dimension
and extending a five-cut theorem to six. A non-prefix assignment control
checks that choosing the smallest pieces first is not assumed complete.

The primary attribution counts are 55,2,1,1,1,2 in the contract order above.
The seven uncertified rows are `2^3,7^7`, `2^2,3,6,7^6`, `2^2,4,5,7^6`,
`2,3^2,5,7^6`, `2,3,4^2,7^6`, `2,5,6^8` and `4,5^3,6^6`.
These are not a complete current public frontier. The inventory omits
other original alpha/cover rules and later results. No counterexample or
new threshold is inferred from a failed contract.

## Open next questions

First audit another published alpha/cover contract against these seven
literal rows before launching a new geometric census. A feasible first
step is to pin the full original FINITE alpha statement and certify its
actual quotient cover. Its implementation and source binding are absent
from this inventory, so its coverage remains unclaimed here.

For `2,5,6^8` and `4,5^3,6^6`, the best common-support caps with three
rank-six endpoints are 34 and 32, while the mixed 5,5,6 contract needs
60 and 40. Actual support overlap, a changed mixed-rank lemma or another
endpoint count could help. Neither a uniform rank-five improvement nor a
larger historical survivor count supplies those missing hypotheses.

The predecessor mathematical suites and complete decoder reduction are
inherited and unrun. This is a conditional caller audit with internal
automated review, not independent human or proof-kernel approval. There is
no full C5, supplier, kappa or selected-frontier change. New work is
Apache-2.0; retained source notices remain unchanged.
