# One all-five toggle has no favorable priced point

**Exact finite exclusion for one operation use; no new κ.** This package tests
one explicit extension of the five-source universal dirty connector: one
complete call

```text
Q5: z += B0 x0 + B1 x1 + B2 x2 + B3 x3 + B4 x4
```

may appear at most once. The four other source calls remain the original
singletons `Bj: z += Bj xj`. Q5 is charged as one dispatch and five elementary
source additions. All 31 nonzero five-bit output masks are required; every
source, connector and output row may start dirty; source rows are read-only;
operators and inputs are arbitrary, the schedule cannot depend on data contents,
and every complete call restores its private scratch and agreed heads. Every
output readout remains a complete `Ai: yi += Ai z` call. There are no extra
root connectors, copies, direct `Ai Bj` operations or uncharged readouts. The
price model is deliberately favorable to Q5: it pays the ordinary per-call
overhead once and exactly five source additions, with no additional frame or
implementation surcharge.

## Result

No completed schedule that uses Q5 has a strictly lower price than the pinned
singleton-alphabet witness for any per-query overhead `o >= 0` and elementary
addition price `p > 0`, with call cost `o + p` per singleton or output readout
and `o + 5p` for Q5. In the full batch, the singleton witness uses 74 complete
queries and 74 elementary additions. Every Q5 schedule has the lower bounds
below; the readout counts allow an output to use more than two A calls.

| Singleton calls `m` beside Q5 | Exact pair-mask result | A readouts at least | Total queries at least | Total elementary additions at least |
|---|---:|---:|---:|---:|
| 5 | At most 20 nonzero differences by the 7-prefix pair count | 84 | 90 | 94 |
| 7 | Exhaustive maximum 20 of 31 | 84 | 92 | 96 |
| 9 | Exhaustive maximum 27 of 31 | 70 | 80 | 84 |
| 11 or more | Parity lower bound; no census needed | 62 | 74 | 78 |

The restoration condition makes every singleton count `mj` positive and odd:
Q5 contributes each source once, so Q5 plus the singleton calls must use each
source an even number of times. Therefore `m = sum(mj)` is odd and at least 5.
The only values below 11 are 5, 7 and 9. At `m >= 11`, Q5 plus the singleton
calls already cost at least 12 dispatches and 16 source additions; even the
minimum 62 output readouts bring the complete bill to at least 74 queries and
78 additions.

This is a finite negative result for the one-Q5 alphabet extension in this
five-source batch. It neither changes the selected frontier nor gives a new
multiplication exponent. The conclusion is conditional on the stated ideal
price model: any implementation surcharge for Q5 would increase its cost.

## Why extra readouts are included

After `t` source calls let `qt` be the five-bit parity vector of source
contributions already added to `z`. Then

```text
zt = z_initial + sum_j qt[j] Bj xj.
```

If an output row is read `r` times, its dirty-connector term has coefficient
`r mod 2`. Correctness for arbitrary dirty `z_initial` forces `r` even. A
nonzero target mask also rules out `r = 0`, so each of the 31 output rows needs
at least two readouts. With exactly two, the produced source mask is a pairwise
prefix difference `qs XOR qt`. If a target mask is absent from the difference
set, that row needs at least four readouts. Thus if a source path exposes `c`
nonzero pairwise differences, the entire output batch needs at least
`62 + 2(31-c)` A calls. This bound covers schedules that use more than two
readouts per row.

Q5-containing paths are closed walks in `F2^5`. For `m=5`, there are seven
prefixes and at most 21 unordered prefix pairs; one pair is the zero difference
from the repeated start/end point, leaving at most 20 nonzero masks. For
`m=7`, the singleton multiplicities are `(3,1,1,1,1)`. For `m=9`, they are
either `(5,1,1,1,1)` or `(3,3,1,1,1)`. The census enumerates every distinct
singleton ordering and every Q5 insertion slot for one representative of each
multiplicity class. Coordinate permutations act transitively on each class,
and preserve both the all-mask target and the unit costs, so multiplying by
orbit sizes 5, 5 and 10 covers all labeled words.

The exact census is integer-only and exhaustive, not sampled. It checks 6,720
representative `m=7` words (33,600 labeled words total) and 30,240 plus 100,800
representative `m=9` words (1,159,200 labeled words total). The maximum
nonzero pair-difference counts are 20 and 27. `CERTIFICATE.json` records the
full coverage histograms, maximizing words and SHA256 hashes of the canonical
representative records. `independent.py` re-enumerates the same finite classes
using recursive multiset generation and a separate set-based difference
calculation.

## Reproduction

From the repository root, with Python 3.12 and only the standard library:

```sh
python3 -B research/quint-toggle-connector/generate.py
python3 -B research/quint-toggle-connector/independent.py
python3 -B research/quint-toggle-connector/verify.py
python3 scripts/research_package.py --package research/quint-toggle-connector --check-only
python3.12 scripts/research_package.py --package research/quint-toggle-connector
python3 -I -B research/universal-connector-boundary/verify.py
```

The first three commands check the primary census, the independent census and
the priced comparison. The package runner checks metadata and source pins, then
runs the three registered commands. The final command replays the predecessor
positive control; its expected output is
`PASS_UNIVERSAL_CONNECTOR_BOUNDARY pairings=945 max_coverage=31 queries=74 leaves=182`.
The baseline certificate used by the package is pinned in `SOURCES.json`.

## Assignment, current frontier and overlap

Selected at base `463113d675af7410ac91d53a4fed51ec6494eb9a` from card
`connector-alphabet-change`, priority revision 6, nonce
`f9384baf1db5ab998bf8643a7cf853d0`; scope refined to the named Q5 operation and
the existing five-source batch. At this base the selected record is #1094,
`κ = 836330098538459/500000000000000000`; this connector result leaves that
frontier unchanged.

The live overlap refresh at 2026-10-17 21:37 UTC covered 359 open PRs and 2,154
discussion records with complete pagination and no warnings. The live PR list
one minute later contained 361 open PRs; the only open issue was #913, “All
size/compiler is retained." No open PR matched the connector-alphabet overlap
terms. Exact searches for `Q5` and `all-five toggle` found no remote claim.
The broad literal `quint` search found only an unrelated P112 five-dimensional
port-decoder claim in discussion #2292; `arity-five` matched the unrelated R480
scalar-boundary PR #597. The closest completed alphabet extensions are the
two-source DUO (PR #1531) and three-source TRIO (PR #1518), which use different
operation vectors. The exact fixed-alphabet five-source path is the predecessor
`research/universal-connector-boundary` (PR #943 lineage). Discussion #1884's
paid connector-frame investigation was marked done and its remaining scopes
released; it concerns frame operations, not Q5. The latest active PRs and
handoffs were concentrated on P104/P112, QQ16, T740 and selected BIT work.
The overlap helper is a lead search, not a novelty certificate.

The proof covers one Q5 use, five source labels, all 31 nonzero output masks,
binary linear updates, arbitrary dirty rows and read-only sources. It does not
cover two or more Q5 calls, mixtures with DUO/TRIO, other source counts, extra
connectors, mutable source maps, frame operations, nonbinary arithmetic,
physical supplier realization, compiler/tape costs, or the selected
multiplication theorem. Those require separate models and proofs.

## Open next questions

Can two Q5 calls, or a mixed Q5/DUO/TRIO alphabet, create a new priced point?
That could change the recursive interface cost. The first step is a closed-walk
census with exactly two Q5 calls, followed by a readout-inclusive price check
against the same 31-mask batch. This is unblocked and outside the single-Q5
scope.

## Credit

Predecessor credit: Ross Richardson and the
`research/universal-connector-boundary` / PR #943 lineage. Related alphabet
extensions: PR #1518 and PR #1531; they are not used as proof inputs here.
Prepared by Cinna Davis with substantial OpenAI Codex assistance in scope
selection, proof development, enumeration, verification and writing. No
independent human or proof-assistant review is claimed. Apache-2.0.
