# The sharp binary dual-polar cut ceiling at every rank

This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

Claim type: scoped written proof with exact finite corroboration.
For the graph of Lagrangian subspaces of a binary symplectic space of
dimension 2m, the exact ratio of opposite-pair cut disagreement to
edge-pair cut disagreement is

    max_S p_m(S)/p_1(S) = 2 - 2^(1-m),   for every integer m>=1.

Point cuts attain it. The first nonconstant eigenspace uniquely maximizes
the corresponding spectral quotient. A factored distance-eigenvalue
polynomial proves the missing uniform maximization in Jacob Sussman's
[PR4628](https://github.com/CrocSwap/integer-mult-bounds/pull/4628),
Theorem 6 of its induction note. That note gives finite evidence through
rank 12 and explicitly leaves the all-rank comparison open. Its finite
results, point-cut witness and coordinate-family interpretation retain
predecessor credit. This contribution supplies the new all-rank proof,
without running predecessor scientific programs.

The resulting ceiling for constant-dimension coordinate certificates and
their nonnegative sums holds at every rank. It does not exclude general
noncoordinate certificates or prove a call-count bound for arbitrary
physical circuits. No new kappa or selected-frontier change is claimed.
The complete argument is in [PROOF.md](PROOF.md).

## Evidence and reproduction

The standalone standard-library checker generates all its scientific
fixtures. It compares 1,224 factored polynomials with 40,424 independent
intersection-recurrence equations through rank 48, then checks all 8,256
nonconstant spectral quotients through rank 128. Its separate geometric
oracle constructs the 3, 15 and 135 Lagrangians at ranks one through three
from literal binary symplectic spans and checks every pair's intersection
numbers. It enumerates all 6 and 32,766 nontrivial Boolean cuts at ranks
one and two, and checks 81 attaining point cuts across the three graphs.
The rank-two census has 170 attaining nontrivial subsets; no all-rank
classification is inferred from that count.

Fifteen controls reject altered polynomial coefficients, a changed edge
eigenvalue, smaller false ceilings and invalid checker domains. Explicit
exceptions keep the same checks active under optimized Python. Finite
checks corroborate the written proof; they are not its universal argument.

From the repository root with the local CPython 3.12.15 interpreter:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/binary-dual-polar-cut-ceiling/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/binary-dual-polar-cut-ceiling/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/binary-dual-polar-cut-ceiling
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/binary-dual-polar-cut-ceiling --check-source-history --check-modes
```

Any CPython 3.12 executable may replace that path. The direct marker is
`PASS_BINARY_DUAL_POLAR_CUT_CEILING`. Each run prints its computed counts
and a generated receipt binding all six package files by SHA256. It writes
no files. Both registered checks have a 120-second limit. Direct replay
also works from a Git-free package export with no predecessor files.

## Scope, sources and credit

The `complex-rank-shape-decoder` card explicitly changes to a certificate
limitation, rather than a physical supplier optimization. This helps delimit
what stronger lower-bound searches must change. It does not improve the
complete signed invoice. Canonical base is
`e54523517d0f03e58352e647c403a5af3e525a57`, priority revision eight. The
catalogue's #5599 context is historical; selected #7000 remains unchanged.
[TASK.json](TASK.json) records the scope change, evidence and next question.
[SOURCES.json](SOURCES.json) pins the exact predecessor induction note,
catalogue and selected record as historical provenance. None is a runtime
scientific input, and no predecessor file is copied or modified.

Credit Jacob Sussman, `jacobalansussman`, for PR4628's question, finite
evidence, point-cut count and coordinate-certificate application, and eumemic,
Swapnil Jain and the native/kept-subspace contributors credited there.
Dual-polar distance-regular spectra and spectral Dirichlet-form comparison
are classical. [Lee and Tanaka, SIGMA 14 (2018), 009](https://doi.org/10.3842/SIGMA.2018.009)
provide standard background; the proof here derives the binary formulas
directly. No global literature-priority claim is made.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19601539)
followed live PR/Discussion, account-history, local-reservation and
main/merged distinctive-term searches. The overlap cache covers 846 open
PRs and 7,482 Discussion records at its recorded timestamps, with incomplete
sparse local-note coverage. Distinctive searches also inspect main's README
and PROOF files. Unpublished work and arbitrary historical code remain
coverage limits.

## Limitations and unrun obligations

The theorem covers binary symplectic dual-polar graphs and their stated
cut/coordinate-certificate model. It does not classify every equality cut,
extend to other fields, construct a word or supply a physical consumer.
Native realization, legal access, ownership/restoration, stock, compiler,
precision/tape, analytic recovery and a complete supplier invoice remain
unproved here. All five selected framework assumptions remain. Selected
cold replay, Lean, Docker, independent human and formal proof-kernel review
are unrun or unclaimed.

## Open next questions

Which Boolean cuts attain equality at rank at least three? The proof
restricts their indicators to the constant and first adjacency eigenspaces,
but does not classify the resulting zero-one functions. Start with the
135-vertex rank-three graph. A complete census or a structural classification
would identify every sharp coordinate certificate; neither is supplied here.

## Code constraints

Every function is shorter than sixty physical lines. Loops have fixed
fixture bounds: rank at most 128 for scalar spectra, rank at most 48 for
polynomial checks, dimension at most six for literal geometry, at most
315 intermediate isotropic spaces and at most 32,766 cuts per graph. No
recursion, subprocess, network operation, callback registration or dynamic
code is used. Immutable tuples hold geometric spans; no shared mutable
cache exists. Explicit exceptions enforce all scientific checks.

Power of Ten rule 3 deviation: CPython and Fraction allocate during this
bounded exact offline check. At most 135 vertices and 18,225 pair cells
are retained for one graph; the largest enumerated subset family is
streamed. Polynomial degrees are bounded by 48 in the replay, and spectral
powers by 4,160 bits. Six regular package files of at most 128 KiB each
are read only for receipt hashes. These bounds constrain live mathematical
state, not interpreter internals. Rule 9's managed references and standard
iterator dispatch have fixed known targets and finite fixture sizes. Both
warning-strict registered modes and in-memory syntax checks supply the
available diagnostics. A fixed-allocation native implementation or external
static analysis is not claimed; revisit it only if this checker becomes
a resource bottleneck.
