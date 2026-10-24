# A positive diagonal metric can destroy a full rational anchor box

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped exact obstruction.** There is a rational three-column weighted Gram
factorization `M=P D P^T`, with the fixed positive definite metric
`D=diag(1,3,1)`, four rows, nonzero diagonal and matched nonempty canonical
anchors, whose retained directed anchor box is exactly **three**.

Sagar Thakrar's [#3612](https://github.com/CrocSwap/integer-mult-bounds/pull/3612)
proves full boxes for rational factors `P P^T`, and already gives an asymmetric
four-row matched-anchor obstruction. The new restriction here is `Q=P D`
for one positive diagonal metric. Thus a positive metric and matched anchors
together still do not extend the full-box theorem. This answers one concrete
higher-valuation boundary question from that package. It does not settle its
unrestricted asymmetric question or the F-star conjecture.

## Construction and proof

Use zero-based row indices and coordinate masks `1,2,4`. Put

```text
P = [(1, 1, 0), (3, -1, 2), (3, -1, -6), (1, 0, 1)]
D = diag(1, 3, 1)
Q = P D = [(1, 3, 0), (3, -3, 2), (3, -3, -6), (1, 0, 1)]

M = P Q^T = [ 4   0   0   1 ]
            [ 0  16   0   5 ]
            [ 0   0  48  -3 ]
            [ 1   5  -3   2 ]
```

The metric is positive definite, so `M` is positive semidefinite. Its rank
is exactly three: the factorization gives an upper bound of three, and the
principal minor on rows `0,1,2` has determinant `4*16*48=3072`.

For completeness, the retained canonical normalization from #3612 is as
follows. Delete any factor column that contributes identically zero. Let
`m_j=min_i v2(P_ij)`, `n_j=min_i v2(Q_ij)`, and
`gamma=min_j(m_j+n_j)`, ignoring zero entries in the minima. Normalize
`p_ij=2^(-m_j) P_ij` and `q_ij=2^(m_j-gamma) Q_ij`. The canonical anchors
`A_i,B_i` are their odd-coordinate supports, and the tied set is their
intersection. All column minima in this example are zero, so

```text
A = B = (3, 3, 3, 5),    gamma = 0.
```

Every tied set has two coordinates. The normalized diagonal valuations are
`(2,4,4,1)`. In particular the first three rows are outside #3612's sufficient
matched-row condition `v2(M_ii)=gamma+1`.

A retained box consists of distinct kept rows, an order, and labels
`a_i subset A_i`, `b_i subset B_i`, with binary dot product
`a_i dot b_i=1`. For each earlier row `i` and later row `j`, the only
additional requirement is `M_ij=0 => a_i dot b_j=0`.

Suppose a full four-row box existed. Restrict its order and labels to rows
`0,1,2`. Every off-diagonal scalar entry on that triple is zero. Its binary
label-dot matrix therefore has zero entries above the diagonal and ones
on the diagonal, and has rank three over F2. But all those source and target
labels lie in the same two-coordinate plane, so that matrix has rank at
most two. This contradiction proves `box<=3`, for every order and label.

Rows `(0,1,3)` in that order with labels
`(a,b)=((1,1),(2,2),(1,1))` give a three-row witness. The only forward scalar
zero between those rows is `M_01=0`, and its labels are orthogonal. All
supports and diagonal parities hold. Hence **box=3**.

This matrix cannot be reinterpreted as `R R^T` with rational `R` having
three columns: the displayed principal minor would then be the square of
a rational determinant, whereas `3072=3*32^2` is not a rational square.
Allowing more columns changes the three-total contract. Positivity alone
therefore does not recover the predecessor's hypothesis.

## Exact corroboration

The self-contained verifier recomputes `Q`, every matrix entry, canonical
anchors, the rank-three minor and the explicit witness. A separate exhaustive
pass through the definition enumerates every ordered subset and every
supported self-certifying label assignment. Each row has six label pairs.
The assignment counts include different orders and labels on the same subset;
they are not counts of distinct subsets or distinct boxes.

| Kept rows | Assignments examined | Admissible assignments |
|---|---:|---:|
| 0 | 1 | 1 |
| 1 | 24 | 24 |
| 2 | 432 | 288 |
| 3 | 5,184 | 1,296 |
| 4 | 31,104 | 0 |

Ten control groups cover the metric, shape, support, diagonal parity,
zero entries, distinct rows and directed order. All 125 dual column
rescalings with exponents in `{-2,-1,0,1,2}^3` preserve the recomputed matrix
and anchors. These are controls on this fixed example, not a broader metric
classification. Every check uses explicit exceptions and remains active under
`-O`. The verifier writes no files and emits a generated receipt bound to
SHA256 hashes of all five package files. There is no handwritten receipt.

From the worktree root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/weighted-gram-box/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -B -W error research/weighted-gram-box/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/weighted-gram-box
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/weighted-gram-box --check-source-history
```

Another CPython 3.12 interpreter may replace that local path. The expected
markers are `PASS_WEIGHTED_GRAM_BOX`, `PASS_REGISTERED_RESEARCH_PACKAGE` and
`PASS_RESEARCH_COMMIT_BYTES`. Source documents are provenance only; no
predecessor executable is imported or replayed.

## Scope, overlap and credit

The claim is the written proof for this exact rational factorization. It is
also an exact finite counterexample to the stated positive-metric extension.
It is not a multiplication theorem, a physical decoder or a new kappa.
Native implementation, COPY pricing, frames, owners, dirty restoration,
precision, tape costs and supplier admission remain outside scope. Independent
human and formal proof-kernel review are unclaimed. Lean, Docker and the
selected supplier's operator replay were not run.

The historical `complex-rank-shape-decoder` card is explicitly changed to
this algebraic side result. No complete paid-profile gain is claimed. Entry
orientation used the current selected-binding positive control. The source
first example and existing asymmetric obstruction in #3612 were read as
premises and motivation, without running its verifier. The new metric is the
changed premise; no family implementation expansion is proposed.

Scientific base is `a5df48c55ea806d7952b65acc9c76d878ff09b13`, priority revision
7. The advance [claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19144846)
records the target. Live open PRs, recent account work, handoffs, local
reservations, distinctive main README and merged-PR searches were checked.
The entry overlap helper covered 331 open PRs and 4,340 Discussion records
with complete pagination. Sparse local notes were incomplete. Neither
coverage nor a no-match search proves absence of unpublished overlap.

Credit Sagar Thakrar #3612 for the rational Gram theorem, the modulo-four
matched-row condition, the earlier asymmetric matched-anchor obstruction and
the open boundary question. Credit Aaron Wang/navinor #2914/#2978/#3031 for
the directed sub-anchor framework, asymmetric obstruction and valuation
lineage; DreamingOfClouds #1590/#2111 for the F-star/certificate lineage; and
the #3409/#3420/#3445 labeling predecessors retained by #3612. The binary
triangular-rank obstruction is inherited, not a new general method. The new
artifact is its explicit fixed-positive-metric realization. Predecessor
credit and source files are unchanged.

## Open next questions

Which positive rational diagonal metrics have the universal full-box property
for all rational three-column factors with nonempty canonical ties? Start
with `diag(1,d,1)`, distinguishing rational square classes and recomputing the
original canonical anchors. This example excludes `d=3`; it does not provide
a classification. The blocker is a uniform metric-sensitive invariant, rather
than another replay of this four-row example.

## Implementation bounds

Power of Ten inspection is confined to `verify.py`. Control flow is
nonrecursive, functions are below 60 lines, inputs have at most four rows and
three columns, rational input integers have at most 32 bits, and rescaling
exponents are bounded. The oracle's loops have an explicit bound
`sum_{k=0}^4 4!/(4-k)! * 28^k`; the actual fixture has six choices per row.
State is local apart from immutable fixture constants. Source files have
scoped reads and failures propagate. There is no generated code or dynamic
import. Rule 3 has a managed-runtime deviation: Python/Fraction allocate
within these fixed bounds during this finite command. Revisit fixed storage
before admitting unbounded input or using it in a steady service. Rule 10
uses warning-strict normal/optimized execution and in-memory compilation.
External Python linters were unavailable locally; no repository-wide analyzer
configuration is changed. The registered timeout is 120 seconds per mode.
