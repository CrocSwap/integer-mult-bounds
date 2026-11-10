# Smaller bulk guards for cyclic-band elimination

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written mathematical proof with exact finite corroboration.
For a real dyadic cyclic-band matrix of half-width W and row-dominance gap
delta>0, natural-order elimination can use lower factor precision on its first
N-W rows. Its final W border rows retain the full-length guard:

```text
predecessor factor residual: N K 2^(-q) in every row
new factor residual:        max_i m_i K 2^(-q_i)
bulk support count:         m_i <= min(N,3W+1)
border support count:       m_i <= N
```

[PROOF.md](PROOF.md) proves the mixed-grid update identity, stability induction,
separate solve precision, integer ranges and all-size cyclic support bound.
The precisions q_i must be nondecreasing. This is an original precision
allocation step on Ali Romman's [PR5284](https://github.com/CrocSwap/integer-mult-bounds/pull/5284)
algorithm, not an audit of that result.

On the first strict 65-row tridiagonal fixture, bulk factor precision is 34
fractional bits instead of the matched uniform allocation's 39; the final row
uses 39. The abstract factor fraction-bit total is 11,171 instead of 12,441.
Exact residuals certify the same 2^-16 solution target. No optimality,
wall-time, native/tape bill, Gaussian-family admission, new kappa or selected-
frontier change is claimed. The five selected framework assumptions remain.

## Reproduce

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/row-adaptive-band-precision
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/row-adaptive-band-precision --check-source-history
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/row-adaptive-band-precision/verify.py
```

The absolute interpreter path records the local environment. A different
CPython 3.12 executable can replace it. VERIFY.json registers normal and
optimized warning-strict runs. Each must print
`PASS_ROW_ADAPTIVE_BAND_PRECISION`, `errors=0`, 252 small exact solve comparisons,
1,125 symbolic patterns, and the strict 65-row precision reduction. JSON stdout
also binds all package-file hashes. Receipts are generated, not handwritten.
No output files or bytecode caches are created by the verifier.

The all-size theorem is written mathematics. Finite fixtures are real,
N<=129 for pattern checks and N<=65 for numerical checks; the implementation's
explicit capacity is N<=257, W<=8, q<=512. Small numerical systems are checked
against an independently transcribed pivoted rational solver. This does not
claim independent human or formal proof-kernel review. The complex extension
is a written two-real-solve argument. No full predecessor, selected supplier,
Lean, Docker, native backend or physical-tape replay is required or claimed.

## Scope and credit

Ali Romman / PR5284 supplies the variable-gap solver, one-round factor-entry
method, diagonal-dominance stability estimates and cyclic fill. The new work
is the monotone row-grid theorem, its support-priced residual and reduced bulk
allocation. Dugongue / PR4554 supplies the earlier band/Woodbury interface;
Ryanson Jonathan / PR4556 supplies its independent check, cited as context and
not replayed. PR5260 and PR5326 are prior fixed-source and Gaussian Reference
consumers. Classical Gaussian elimination and row dominance retain their
classical status. No worldwide novelty claim is made for those methods.
Frozen predecessor files and their credit lines are unchanged.

The assigned uniform-transfer-audit card is explicitly changed to this
numerical-interface result. It addresses precision costs that a future paid
Gaussian caller must fund; it does not discharge the selected precision_tape
assumption. SOURCES.json pins the exact predecessor proof and originating
catalogue. The verifier imports no predecessor code.

The advance [CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19363375)
reserved this question. Live overlap covered 430 open PR bodies and 6,404
Discussion records with complete remote pagination at the recorded snapshot.
The initial sparse local search covered 115 of 8,917 tracked notes. Relevant
proofs were then read directly, and main/merged searches covered mixed row
precision and cyclic-band terms. Arbitrary diffs, unmaterialized notes and
unpublished work remain outside that coverage. No novelty certificate is
claimed.

## Open next questions

Can an actual Gaussian production caller use the row allocation to reduce its
paid precision/storage bill? First freeze its coefficient error, row gap,
symbolic fill and record representation, then account for the W high-precision
border rows and solve buffers. Source generation, fixed-tape layout, native
operations and the complete recursive invoice remain blockers. A single common
machine-word representation may obtain no storage benefit.

Can a different elimination order lower the number of high-precision rows
without increasing fill or the required row-residual budget? First derive its
symbolic row counts and a valid mixed-grid schedule. The monotone grid rule in
this result may prevent a naive permutation from applying directly. No such
optimization is included here.

## Verifier constraints

Every loop is bounded by explicit matrix, bandwidth, precision or fixture
limits. Functions are under 60 lines. Invalid shapes, grids and divisors fail
with explicit errors retained under optimized Python. The verifier uses no
recursion, dynamic code generation, subprocesses or network calls. Python's
managed allocation is a Power of Ten rule 3 deviation, bounded here by N<=257,
W<=8, q<=512, finite fixture counts and a registered 60-second timeout.
Package hashing is bounded to eight files of at most one MiB each. There is no
claim of a fixed physical Python heap. Reassess storage if those limits change.
Warnings-as-errors in both interpreter modes are the available diagnostics;
no additional static analyzer is configured for this isolated standard-library
research verifier.
