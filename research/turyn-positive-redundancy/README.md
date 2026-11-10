# Positive redundancy cannot lower the fixed-label Turyn encoder bill

This scoped proof was produced by Nick Petalas. Apache-2.0.

For the full Turyn product kernel with its existing 27-bit labels, the exact
encoder support bill with R nonzero columns is B(R)=27R for every R>=512,
when K=A H A^T and H is positive definite. No such factorization exists with
R<512. The minimum over all finite positive redundancy is therefore 13,824.
Each additional nonzero column costs exactly 27, even with a dense positive
definite coupling metric. The metric and scalar operations are granted free.

DominikScholz's [PR598](https://github.com/CrocSwap/integer-mult-bounds/pull/598)
proves rank 512 and support rank 27 for every nonzero tensor encoder, then
bounds rank-minimal factorizations. This package cites those results as
premises. The new step extends the bill to arbitrary positive redundancy.
Its proof uses the classical positive Gram range identity. No general
linear-algebra priority is claimed, and no predecessor scientific suite is
replayed. [PROOF.md](PROOF.md) gives the theorem, attainers and exact limits.

This is a historical changed-geometry side result under the current decoder
card, rather than a changed selected P104 supplier. The complete signed
invoice, physical/native realization, ownership, restoration, precision,
compiler, analytic recovery and the five selected assumptions remain outside
scope. No new kappa or complete multiplication theorem is claimed. Independent
human and formal proof-kernel review are unclaimed.

## Reproduce

From the repository root with standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/turyn-positive-redundancy/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/turyn-positive-redundancy/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/turyn-positive-redundancy
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/turyn-positive-redundancy --check-source-history
```

Another CPython 3.12 executable can replace the absolute interpreter path.
Each direct command prints PASS_TURYN_POSITIVE_REDUNDANCY and generates a
SHA256 receipt for all six package files and the three cited source texts.
The registered launcher also prints PASS_REGISTERED_RESEARCH_PACKAGE.
Authentication of the texts is separate from proving their mathematical
premises. The direct scientific replay needs no Git or network.

## Evidence and verification design

The executed domains are 2,511 two-by-two Gram cases from all 81 ternary
encoder matrices and 31 positive definite metrics, 80 rectangular fixtures,
160 fixed-kernel attainers, two metric boundary counterexamples, nine
rejecting controls and one zero-column control. The two-by-two rank histogram
is 31 zero, 992 rank-one and 1,488 rank-two cases. These are enumerated test
cases, not claims about the number of Turyn objects.

The verifier checks new exact rational examples, including singular encoder
matrices, dense positive definite metrics, attaining duplicate columns and
changes of metric coordinates. Two literal counterexamples reject extending
the individual-column conclusion to singular or indefinite coupling metrics.
Zero columns and invalid support hypotheses have separate controls. The
all-size result comes from the written proof, not finite enumeration.

The full-label support premise for the small fixtures is checked independently
of the encoder columns: for each nonzero binary label functional, restricting
the kernel to rows on which it is one must retain full real rank. This is
equivalent to saying no nonzero range vector has its active labels in that
functional's kernel. It does not enumerate or test the Turyn ports.

All loops are bounded by fixed finite domains. Matrices have at most 32 rows
or columns including concatenations; label width is at most five. Functions
are shorter than 60 lines, there is no recursion or dynamic code execution,
and failures use explicit exceptions that remain active under optimization.
Files read for authentication and receipts are each bounded to one MiB.
Warning-strict normal and optimized replays are the available diagnostics.
No new static-analysis configuration or external dependency is needed.

Power of Ten rule 3 has a managed-runtime deviation in verify.py. Python
allocates integers, Fractions, lists and dictionaries during this bounded
finite replay. Fixed dimensions and coefficient grids, streamed cases, no
retained case history and a 120-second registered timeout constrain resources.
Normal and optimized replays check the same domains. A physical implementation
would need a separate fixed-capacity arithmetic and storage analysis.

## Open next questions

1. Can signed or asymmetric factorizations beat 13,824 with these labels?
   Start with explicit outside-range columns, an exact full kernel identity
   and every support charge. No such factorization or scalar word is supplied.
2. Can a singular positive semidefinite metric save complete circuit cost?
   Price its application and output restoration before counting sparse columns
   as a gain. The two-port example only demonstrates the theorem's boundary.

Structured questions and blockers are in [TASK.json](TASK.json).

## Credit, provenance and overlap

Credit DominikScholz / PR598 for the explicit opening, geometry, kernel, labels,
rank and support theorem; R. J. Turyn, J. H. Conway, N. J. A. Sloane, Gabriele
Nebe and the geometry/native lineage retained by that package. The classical
Gram range identity and duplication construction are methods, not general
priority claims. The original source files and their credit are unchanged.

[SOURCES.json](SOURCES.json) pins the three premise texts and the task and
selected-record provenance at canonical main
7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority revision 8. The source's
historical nominal kappa is not the selected result. The selected record at
this base is PR6030 with kappa 0.003125804.

The advance [CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19362323)
reserves the positive-redundancy question. Live open PRs, handoffs, local
reservations, recent account work, current main and merged object/formula
searches were checked. The cached refresh covered 387 open PRs and 6,319
Discussion records, with complete remote pagination; its local note coverage
was sparse, 106 of 8,917 HEAD paths. Direct Git searches supplemented those
omissions, including the predecessor's text files. Unpublished work and
arbitrary historical diffs are outside that coverage.
