# Scoped validation and handoff

Development base: `bbc600db2fc15007b7c914f4f2b2ed55fa909c87`.
Submission refresh: `407d52ff15b2217b6e22bce44728b4c3907b6515`.
The selected certificate and current-status files are identical between these
two commits. The selected conditional exponent remains
`1661960547713947/10^18`. The contribution adds only this research directory.

## Executed checks

On macOS 26.5.2 arm64, CPython 3.14.6 and the system CPython 3.9.6 reproduce
the same complete EXPECTED.json. Standard-library-only commands:

```sh
python3 -I -B research/output-borrowed-fanout/verify.py
/usr/bin/python3 -I -O -B research/output-borrowed-fanout/verify.py
python3 -I -O -B research/output-borrowed-fanout/test_package.py
make selected-record-check
python3 -B -m unittest discover -s tests -p 'test_selected_result.py'
```

Expected markers are `PASS_OUTPUT_BORROWED_FANOUT` and
`PASS_OUTPUT_BORROWED_PACKAGE`; selected-record integrity passes and all five
existing selected-result tests pass. All runtime guards use explicit exceptions
and remain active with optimized Python. No other package is imported.

Coverage in each mathematical replay:

- 40 prescribed grid cases and the heterogeneous seed fixture, each with three
  explicit schedules: **123** schedules, **1,550** complete child invocations,
  **27,020** leaf occurrences in those forward words.
- Exact free noncommutative identities, complete child boundaries, all-role
  inverses, and exclusion of other outputs from each child's scratch.
- **369** dense forward and **369** inverse executions across dimensions 1..3,
  using identical input matrices and common-role data for the three comparators.
  Every forward/inverse prefix is checked against a sufficient common width.
- Three positive per-factor price vectors per schedule; independent recurrence
  counts, per-factor multiplicities, storage bills, and 123 one-tape trace versus
  closed-summation comparisons at L=3.
- All **40,320** possible minimum-query words for two outputs; **224** pass the
  complete free-polynomial identity. The supporting unbounded lower-bound proof
  is in PROOF.md, not inferred from a capped search.
- Eight mathematical/price corruption controls reject. Two additional nonlinear
  scope controls demonstrate failure of linearity and dirty independence while
  retaining a successful literal inverse.

The package test runs from an isolated temporary directory, regenerates two
decompressed certificate payloads and the complete expected receipt, and rejects
eight on-disk corruptions: omitted restoration, aliased leaf ports, changed
factor order, understated private rows, missing domain coverage, a missing
comparator, altered predecessor bytes and an incomplete receipt. Clean replay
after the corruptions passes. Compressed-stream bytes are not compared across
environments.

All four retained reference files match both pinned Git blob identities and
SHA256. The five base-context files match their exact Git objects and recorded
SHA256. Git whitespace checks pass. A final mathematical/package replay is run
after code changes; publication-only claim metadata does not alter certificates.

## Overlap, scope, and remaining gates

The initial queue was inspected through PR971. The submission refresh covered
new arrivals through PR978 and targeted all-state searches for output/connector,
fanout, and borrowing work. PR889 and PR822 remained at their pinned heads and
open. No pinned sprint coordination issue existed in either check, so the claim
is local. The new ownership contract and its extra B pair distinguish this work
from the credited dedicated fanout, sibling-pool, incidence and cyclic-inverse
contributions. No same-scope duplicate was identified.

The selected record and `upstream/` are unchanged. Root `make verify` and native
supplier cold replay are not claimed: this isolated research package changes no
existing generator, selected supplier, or global artifact. The applicable new
package checks and existing selected-record gates were run. Hosted CI, human
peer review and proof-assistant validation are separate and are not asserted.

No larger kappa, supplier integration, unrestricted circuit optimum, or measured
runtime improvement is claimed. Review should focus on the complete-child
ownership contract, the restricted lower-bound alphabet and the full cost of
the extra B pair. Physical hosting, common labels, tape routing/precision,
all-size compilation and outer transfer remain unresolved for integration.

GitHub has neither a `codex` nor a `codex-automation` label at submission; no
substitute automation-status label is invented. The local sprint claim is
updated once with the submitted result and link. No merge is requested.
