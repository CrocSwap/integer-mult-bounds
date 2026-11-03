# Shared-denominator sliding principal inverses

A new exact cache stores each principal-window inverse using one signed
determinant and an integer adjugate. Every one-index slide uses integer
arithmetic with exact divisions. The inverse coefficient state removes m^2-1
per-entry denominator fields at width m. Stored and temporary bit heights are
bounded independently of the number of slides.

This contribution was produced by Nick Petalas. Claim type: scoped written
construction with finite exact corroboration. No new kappa or selected-frontier
change. The representation count is not a total-bit-space or runtime guarantee;
common cofactors can exceed individually reduced numerators.

[PROOF.md](PROOF.md) states the arbitrary finite-dimension theorem, full
rational-source contract, both update identities, height bounds and limitations.
`cache.py` implements a bounded reusable constructor and slide API. `verify.py`
uses independent literal determinants and cofactors, including signed nonsymmetric
sources and rational row scaling. It produces a hash-bound JSON receipt on stdout
and writes no files.

## Reproduce

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -B -W error research/shared-denominator-window-cache/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -B -W error research/shared-denominator-window-cache/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/shared-denominator-window-cache
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/shared-denominator-window-cache --check-source-history
```

Any CPython 3.12 interpreter may replace that local path. The direct status is
`PASS_SHARED_DENOMINATOR_WINDOW_CACHE`; the registered hook reports
`PASS_REGISTERED_RESEARCH_PACKAGE`.

## New step and predecessor credit

David Ganz / Dugongue's [PR3872](https://github.com/CrocSwap/integer-mult-bounds/pull/3872)
supplies the fixed-global-source, ordered principal-window preparation interface
and rational Schur cache. Its page-integration question motivates the smaller
cache-representation subproblem here. Its scientific results and counts are
cited, not audited or replayed. The new code imports no predecessor code.

Credit Jose Manuel / jmbarrancoml's PR3851 for the exact old-H preparation
boundary, Chafik Boukhalfa, RaD and the retained Gaussian/FFT lineage. Adjugates,
Schur complements, Bareiss elimination and determinantal condensation are
classical. This package claims the concrete shared-denominator sliding
construction and contract, without a global literature-priority claim.
Apache-2.0. Every predecessor source and credit line remains unchanged.

The earlier PR5119 comparison barrier concerns residual error bounds on the same
preparation family. It does not supply this integer cache representation and is
not a mathematical dependency here.

## Scope and costs

The cache first clears each GLOBAL source row once. Thereafter it retains the
integer source, the row scales, ordered labels, m^2 cofactors and one determinant.
It supports N<=32, m<=16 and 256-bit reduced input coefficients. Its mathematical
identities hold in all finite dimensions with the stated nonsingular principal
blocks. Returning the outgoing index is permitted. A zero retained or incoming
determinant fails without changing the previous state.

Dense initialization, global source storage/scaling, integer bit arithmetic,
optional inverse materialization and retained output storage remain payable.
Materialization creates ordinary Fractions and reinstates their per-entry
denominators. Physical protected-page production, precision/tapes/stock,
ownership/restoration, native implementation, complete invoices and all five
framework assumptions remain open. Independent human and formal proof-kernel
review are unclaimed.

## Overlap and scope change

The supplier-boundary-audit card is retained verbatim in TASK.json. Its scope
changes from admission auditing to this constructive arithmetic preparation
subproblem. The selected binding-only first example passed. Main and merged PR
searches covered sliding inverses, adjugate caches, shared denominators and the
general fraction-free form. Live handoffs, active Discussions, open PRs, recent
account submissions and local reservations were checked before the advance
[CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19376727).
PR3872 is the question source and main predecessor. This is not a claim of
exhaustive novelty; sparse notes, arbitrary historical diffs and unpublished work
remain coverage limits. The broad cached report covered 598 open PRs and 6,677
Discussion records with complete remote pagination. The local corpus searched
136 of 8,917 HEAD notes. Exact freshness and coverage limits are in TASK.json.

## Open next questions

1. Can one actual protected factor-page consumer use the integer numerator/common
   denominator stream without materializing every rational inverse entry?
   Freeze its matrix, page format and access sequence, then price normalization,
   coefficient creation, output ownership and cleanup. No physical adapter is
   supplied by this arithmetic cache.
2. When does row-cleared adjugate storage use fewer total bits than separately
   reduced entries for a production source family? Begin with one authenticated
   source and charge initialization plus every output conversion. The field-count
   improvement alone does not answer that question.
