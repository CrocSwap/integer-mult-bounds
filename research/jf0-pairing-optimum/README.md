# The exact pairing cost of jf0 is 19

The eleven-line `jf0` configuration from DreamingOfClouds's
[PR2162](https://github.com/CrocSwap/integer-mult-bounds/pull/2162), at
`113a718265c62aec301c5695f4bfb9c421bef7ab`, has minimum raw pairing cost
**19**, attained with coordinate ranks **(6,6,7)**. That predecessor reported
only a lower bound of 16 and requested the exact value in
[handoff item 4](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18934590).
The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2170)
tracks this successor result. No new supplier or multiplication exponent is claimed.

## Short proof

Let `P,Q` be the pinned rational vectors, `R_j=supp(P_j)`, `A_j=supp(Q_j)`.
An admissible binary pairing has `B_ii=1` and `B_ik=0` whenever `i!=k` and
the **rational** dot product `P_i dot Q_k` is nonzero. Its cost is
`sum_j rank_F2 B[R_j,A_j]`. No symmetry restriction is imposed.

These three ordered principal minors are always upper triangular with unit
diagonal; every entry below the diagonal is forced zero by a nonzero rational
dot product:

| Coordinate | Ordered indices (zero based) | Forced rank |
|---:|---|---:|
| 0 | 0,6,4,7,8,10 | 6 |
| 1 | 1,6,4,7,8,10 | 6 |
| 2 | 0,1,4,5,7,8,10 | 7 |

Thus every admissible pairing costs at least 19. For the upper bound, take
the identity and set both directions of `(2,8)`, `(3,4)`, `(9,10)` to one.
All six entries are allowed. The resulting matrix is the equivalence-relation
matrix of three pairs and five singletons. In each coordinate block, every
class meeting both supports gives one disjoint all-ones rectangle. There are
6, 6, and 7 such classes, respectively, so the cost is exactly 19.

[PROOF.md](PROOF.md) gives the complete configuration, incidence lists and
argument. It is a universal written proof for this fixed instance. The
instance has `2^41` admissible pairings; the proof covers them without
enumerating them. The source's earlier extra floor is absent from this raw
rank-sum objective. Higher-order jet existence and the general three-total
conjecture are not decided.

## Reproduce and evidence

From the repository root, using only Python's standard library:

```sh
python3.12 -B scripts/research_package.py --package research/jf0-pairing-optimum
```

The registered replay runs the primary certificate checker, a separately
written oracle, and semantic controls with and without Python optimization.
`verify.py` authenticates the source, checks all 51 forced zeros in the three
lower minors, and uses exact binary elimination for the attaining matrix.
`oracle.py` independently computes all rational incidences and full row spans
by XOR-set closure: their cardinalities are 64,64,128. Neither checker imports
predecessor code or invokes a SAT solver. `CERTIFICATE.json`,
`candidate-witness.json` and `RESULT.json` are fixed inputs; replay does not
regenerate missing evidence.

Controls cover forbidden rational incidences (including an even nonzero dot
product), diagonal and binary-domain defects, changed rank, bad minor support
and ordering, source and receipt corruption, and missing evidence. A removed
triangularity guard makes its behavioral control fail. Positive controls
include another asymmetric optimum and equivalent label/coordinate/gauge
presentations. These checks do not constitute a formal-kernel proof, human
review, or full selected-supplier cold replay.

`PREDECESSOR.json` pins the exact copied source bytes, Git blobs and PR head;
`SOURCES.json` pins the unchanged main/catalogue/selected provenance.
The source files in `source/` retain their original bytes and notice. Package
local files supply all mathematical replay inputs, so no external dependency
paths are declared in `VERIFY.json`. The generic metadata check additionally
needs the pinned main Git history; direct mathematical replay works from a
copy of this package.

## Open next questions

Can fixed triangular minors also give compact independent lower certificates
for the predecessor's `jf1` and `jf2` examples? Their exact costs are already
known; this would improve verification, not discover new minima. Pin those
two datasets, compute support-restricted acyclic minors and compare their
sum with 12 and 14. Stop if insufficient: failure of this method is not a
counterexample to the known values. This package has not investigated them.
The question, first step and boundary are structured in [TASK.json](TASK.json).

## Attribution and scope change

DreamingOfClouds, with Claude Opus 5.5 assistance, supplied `jf0`, the prior
SAT lower bound and the independent-check request. The model descends from
PR1590/PR2111 and the earlier PR446/PR595 pairing framework; the retained
[source notice](source/NOTICE.md) records that lineage. No predecessor
verifier, jet theorem or SAT lower bound is needed for the proof here.

Ross Richardson prepared this result with substantial OpenAI Codex assistance.
Separate structural-decoder and exact-circuit specialists supplied the written
minor/class proof and independently coded row-span oracle; the parent supplied
the elimination checker, controls and source bindings. This is independent
agent verification, not independent human review. New work is Apache-2.0.

The task selector drew `portable-replay` in the verifier-engineering track.
[TASK.md](TASK.md) and [TASK.json](TASK.json) explicitly record the scope change
to this live mathematical handoff. This finite decoder side result does not
claim a change to the selected recursive profile, physical COPY price,
dirty-workspace contract, precision requirements or exponent saving.
