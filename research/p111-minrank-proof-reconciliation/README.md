# Proof-carrying replay of the archived P111 decoder claims

**Research consolidation, seed 95; no new kappa.** PR620 reported, without
proof logs, that its archived 111-root pattern has minimum F2 fitting rank
nine and only one fitting matrix of rank nine. This package confirms those
two claims with retained deduction traces and an independent standard-library
checker. The numerical conclusions are credited to Joel Pulikkan / GamingPuzzled.

The object is the **archived sorted Hamming-root order** with indices
`39, 52, 57, 71, 76, 78, 103, 109, 114` removed. As PR757 and PR761 already
showed, using this numeric list in a supplier's different root order selects
a different puncture. This package does not transfer the uniqueness result
to those suppliers. It also does not re-prove the separate copy-cost floor
63 or close PR620's wider partial review.

Run offline from the repository root, using Python 3.12 or newer:

```sh
python3 -B research/p111-minrank-proof-reconciliation/verify.py
python3 -B research/p111-minrank-proof-reconciliation/test_package.py
```

Expected: `PASS`, `minrank: 9`, `unique_rank_nine_fitting_matrix: true`,
**37,044 proof additions**, **1,409,475 propagation hints** and
`new_kappa: false`. Cold replay requires no SAT solver, NumPy, compiler or
network. It reconstructs every original formula clause, checks every retained
deduction, and compares a complete regenerated receipt with `EXPECTED.json`.
The second command tests source/proof/receipt rejection and accepts equivalent
gzip containers with different compression and timestamps.

| Fixed claim | Variables | Initial clauses | Retained deductions | Checked hints |
| --- | ---: | ---: | ---: | ---: |
| No fitting matrix of rank at most eight | 89,541 | 310,231 | 2 | 1,338 |
| No rank-at-most-nine fitting matrix unequal to B0 | 211,455 | 732,935 | 37,042 | 1,408,137 |

Both traces derive the empty clause using only reverse unit propagation
(RUP), the positive-hint subset of LRAT. The independent Python checker
does not call the solver or native checker. Separately, the pinned native
`lrat-check.c` accepts both complete formulas and traces. The committed
compressed traces total **1,850,891 bytes**; their decoded payloads, rather
than gzip container bytes, determine mathematical equality.

A literal nine-bit label construction supplies a positive fitting matrix
`B0 = (J+G) mod 2` of rank nine. Its assignment satisfies every rank-nine
CNF clause except the final demand that the matrix differ from B0. Thus the
uniqueness refutation is calibrated against a genuine admitted matrix.
Source and sink labels remain independent variables in the negative query;
symmetry is not assumed.

The original PR620 clause-building methods are also run on every cold replay.
Only their two optional-library imports are removed in memory, and the solver
constructor is intercepted after receiving the complete formula. Sorting the
constraint iteration makes the numbering deterministic. Every resulting clause
and its order match the new generator. Original source files remain unchanged.

[PROOF.md](PROOF.md) states the matrix model, justifies the eight-port gauge
and the proof checker, and separates matrix uniqueness from nonunique
factorizations. [VALIDATION.md](VALIDATION.md) records cross-version replay,
negative controls, source-order scope and the native check. [SOURCES.json](SOURCES.json)
pins the exact base, source commits/Git blobs, implementation and decoded traces.
[NOTICE.md](NOTICE.md) retains contributor and tool attribution and licenses.

The base is `2921874911956718fcaaaf9396fe8267b3cfa9f0`. Selected PR942 retains
conditional kappa `1661960547713947 / 1000000000000000000`. No supplier,
frontier, physical COPY construction or all-size multiplication theorem is
changed or proved here.
