# Verification and handoff

Executed on Ross Richardson's macOS host on 2026-10-14 Australia/Melbourne
(2026-10-13 UTC). Exact source base:
`91a2094f2e022930069e8cfdc810a3ea1b81cd09`.

- CPython **3.14.6**, isolated normal mode: complete census and all **11** test
  groups pass through `python3 -I -B research/historical-j-order-reconciliation/validate.py`.
- CPython **3.12.12**, isolated optimized mode: the same census and controls
  pass through `python3.12 -I -O -B research/historical-j-order-reconciliation/validate.py`.
- CPython 3.14.6, isolated optimized mode, package-only copy relocated to a
  temporary directory containing spaces: the complete validation passes with
  an unrelated working directory. Every input/package byte remains unchanged.
- CLI controls under optimized Python reject `--check` against a false `{}`
  result and refuse `--output` to an existing file. The sentinel file is
  unchanged after both failures.
- `make selected-record-check` passes with the selected #799 kappa
  `1661634653669567/10^18`; all **five** existing `test_selected_result.py`
  tests pass. The selected source inventory, certificate and proof remain intact.
- Eight remote Git blob IDs (seven source snapshots plus the original archive)
  match GitHub's contents API at their pinned commits. Both extracted archive
  members match their original payload digests. The checks are retained in
  [SOURCE-VERIFICATION.json](SOURCE-VERIFICATION.json).

The finite census checks all **289,180** unordered record pairs. All **496**
distinct histogram roots have strict rational moment brackets. All comparisons
between different histograms have disjoint J, root and nominal-kappa intervals.
**1,511** identical-histogram pairs are exact ties, **287,660** pairs agree, and
**nine** pairs reverse. The reversals represent **eight** distinct histogram
pairs. The generated result includes endpoint signs and a hash of every pair's
classification in deterministic order.

The eleven test groups cover high-precision transcendental cross-checks,
three comparisons with the historical moment engine (records 0, 96 and 760),
poisoned saved floating scores, the omitted-fallback failure, the stock-floor
trap, a wrong root proposal, an exact J-tie example with different histograms,
missing/duplicate records, bad histogram types/metadata, source corruption,
and the concrete counterexample to the report's `9/10` gap claim. The primary
census never imports the historical evaluator. Decimal values in the numerical
cross-check test are supplementary checks, not the exact proof mechanism.

## Boundaries

No full `make verify`, current-supplier cold replay, 761-design regeneration,
full historical 47-constraint re-admission, proof-assistant run or remote CI
success is claimed. This standalone package changes no generator, existing
certificate, selected supplier, archived source, or `upstream/` file. Required
source-record checks and all checks affected by this package were run. The
large unrelated construction suites would not establish historical design
admissibility for these 761 records.

No performance improvement or new multiplication exponent is claimed. This
is exact finite evidence for the stated archived arithmetic model, with the
conditional physical/compiler/analytic obligations left intact. The ordinary
kappa formula is interval-bounded sufficiently to decide order; individual
stored `10^-18` ticks are not all independently recertified.

## Coordination and overlap

OS-random assignment seed **96**, research consolidation. The three candidate
scopes, bounded hypothesis and local claim are in [CLAIM.json](CLAIM.json).
No pinned coordination issue existed. A refreshed inventory contained **713**
open PR titles and bodies through **#923**. Searches for the archived dataset,
surrogates and ranking claims found the source #368 and unrelated #895, not an
independent exact replay of this census. Related #743, #828, #867 and #907 were
inspected and concern different archive/provenance objects. This result credits
and corroborates the original nine-reversal finding while adding the exact
coverage partition, eight-histogram-pair accounting and gap correction.
