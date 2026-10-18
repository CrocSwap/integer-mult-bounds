# Four paid transfers for the two-root signed connector

**Finite complex circuit construction and a scoped minimum theorem; no new
kappa.** This package reduces Charles Bethin's PR1637 two-root connector from
six paid root transfers to **four**, keeping its twelve ordinary child queries,
two dirty roots, and exact source/output map. Only unit additions/subtractions
between roots are needed; the two root-doubling passes disappear.

At twelve signed child queries, four transfers are also minimal among words
using **arbitrary fixed one-way scalar shears** `z += a*w` over Q or C. This
does not cover reverse-direction shears, scaled queries, extra roots, source
mutation or a trade for more child queries. It closes PR1637's root-pass
question in this stated one-way interface, not in every two-root architecture.

| Same balanced factor fixture and physical layout | PR1637 | This word |
|---|---:|---:|
| Ordinary child queries | 12 | 12 |
| Paid root passes | 6 | 4 |
| Primitive factor calls, including all inverses | 300 | 300 |
| Total expanded instructions | 306 | 304 |
| Dirty root / private child rows | 2 / 3 | 2 / 3 |

For the explicitly charged dense integer tape realization, the saving is
`24 L^3 + 4 L^2 + 20 L - 4` head moves for every integer L>=1, including all
changed port bindings. Source reads, target updates, additions and work clears
each decrease by 2L; root doublings decrease by 2L. These are operation counts,
not a benchmark or selected-supplier runtime claim. [COST.md](COST.md) gives
port-specific tariffs, the complete recurrence, layout, precision, admission,
preparation and controller charges.

## Reproduce

From the repository root, Python 3.10+ with only the standard library:

```sh
python3 -I -O -B research/signed-connector-transfer-minimum/verify.py
```

Expected final line:

```text
PASS_SIGNED_CONNECTOR_FOUR_TRANSFERS queries=12 transfers=4 minimum_one_way=4 factor_calls=300 controls=44 no_new_kappa
```

The command checks exact source pins, both literal words and inverses in a free
noncommutative module, the entire expanded dirty-scratch maps, all 720 one-root
paths, and all symbolic short-transfer shapes. It then runs a separately
written integer block-matrix/tape checker on 24 fixtures, 660 independent basis
columns per direction, and six tape lengths. Every receipt field is compared.
Forty-four short-word omission/sign/port controls and two dense factor-order/
scratch controls detect broken circuits; the symbolic proof checks include
four-transfer and dropped-hypothesis controls. Both implementations were
written by the same AI agent; this is code/method separation, not human review.

Package relocation, on-disk corruption rejection, and negative-control
sensitivity can be checked with:

```sh
python3 -I -O -B research/signed-connector-transfer-minimum/test_package.py
```

The registered Python 3.12 replay uses these two commands. It needs no native
compiler. To additionally reproduce the original C++ discovery and its coverage
log, use `verify.py --search` with a C++17 compiler. Default replay is read-only;
`--record` explicitly rewrites only the package certificate.

## What is proved and what was searched

[PROOF.md](PROOF.md) gives the all-input identity and transfer lower bound.
At twelve queries each operator must occur exactly twice. With at most three
restored one-way shears, each nonzero cumulative shear height has only one
segment. Paired queries then cannot transmit a source product across roots.
Connected support of the target forces all six operators onto a single root,
where PR944's 720-path obstruction excludes twelve queries. Four explicit
unit transfers attain the bound. The proof allows arbitrary scalar shear
coefficients, not just the discovery alphabet.

The discovery used coefficients {-2,-1,1,2}, every restored root word of lengths
0 through 5, every interleaving with six paired source calls, and every first
source port/sign. Exactly 1,641,024 valid completed source traces were exhausted
through length three. Search stopped at the first four-transfer witness, after
6,691,365 valid length-four traces; length four is **not** completely enumerated
and length five was not reached. [DISCOVERY.txt](DISCOVERY.txt) and search.cpp
retain that boundary. The general minimum is supported by the written
reduction and finite one-root certificate, not an uncompleted length-four search.

OS assignment seed **32** selected the complex-supplier track and the third of
three candidate scopes (32 mod 3 = 2). It also seeds the separate dense matrix
fixtures. The search itself is deterministic. [CLAIM.md](CLAIM.md) records
the candidates, stopped domain and local coordination claim; there was no
pinned coordination issue. [OVERLAP.json](OVERLAP.json) records live coverage
and its limits; no-match results are not a novelty proof.

## Sources, attribution and limits

Base: `858771bcca3b8dd5d4ef4aa682a13cc9b7e23920`.
The selected result at that base is PR1094's conditional
`836330098538459/500000000000000000`, supported by its actual selected manifest
and maintainer review; it is unchanged. This package adds no supplier admission
or new moment and does not rerun the selected cold construction.

Credit **Charles Bethin / PR1637**, head
`9bee6cc01f151b92ccfe147046855715843f066a`, for the two-root twelve-query
construction, lower bound, complete factor fixture and dense layout.
Credit **Ross Richardson / PR944** for the signed target and one-root finite
obstruction; **martinxxx9 / PR1088** for its weighted repairs; and **Hanson Sun /
PR1526** for the paid one-root scaling alternative. The two-connector lineage
of **woklerx / PR1438**, **Gareth Davidson / PR1498**, **Hanson Sun / PR1615** and
**Cinna Davis / Discussion1412** remains credited through the retained notices.
PR1438 already gives a characteristic-two source-port separation argument
with two XOR transfers and a four-transfer two-source fixture. Our lower
bound extends that method to arbitrary characteristic-zero one-way shears,
including the three-shear case; the attained signed three-output word is a
different target. PR1498's four-transfer obstruction concerns universal
five-source binary masks and is not contradicted by this construction.
No priority is claimed for two dirty roots or the twelve-query child minimum.
Exact source pins and unchanged retained notices are in SOURCES.json and sources/.

The general identity assumes exact restored additive child interfaces and
unobserved intermediate outputs. The integer example supplies a complete
finite model, not arbitrary Q/C precision or selected native ports. All-size
compilation, common labels/mutable sources, hosting, frame/precision adapters,
tape integration and analytic transfer into multiplication remain uninstantiated.
Neither a full multiplication theorem nor independent human/proof-assistant
review is claimed. New work is Apache-2.0, prepared for **Ross Richardson**
with substantial **OpenAI Codex assistance** in reasoning, implementation,
verification and writing. Frozen predecessors and `upstream/` are unchanged.

## Open next questions

- Does allowing both `z += a*w` and `w += a*z` reduce the four-transfer floor
  at twelve queries? First classify restored products of at most three 2x2
  shears and their paired-query directions. The current height proof is
  one-way only; this is a different alphabet and not an exclusion here.
- Is there an actual selected-supplier interval exposing these six immutable
  additive ports? Pin one emitted interval and price both roots, each changed
  query port, precision and hosting. No such embedding is supplied, so the
  local saving alone does not establish a better recursive moment.
- With nonuniform port tariffs, when does this word beat the one-root 13/14
  query alternatives? Evaluate the explicit cost formulas on an admitted
  physical interface. Equal port prices or a common dense layout are model
  assumptions, not evidence about a native supplier.

TASK.json gives structured first steps and blockers. VALIDATION.md separates
the local checks, discovery replay, selected-record bindings and unrun gates.
