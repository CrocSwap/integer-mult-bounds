## Result and why it matters

The exact rank-library generator in #7345 explicitly assumes that the
ambient cap equals the largest productive target. The selected compiler
instead uses the actual cap `A=153^1920`, above its maximum target.
This package proves and implements the evaluated least-chronological
library for every fixed separated rule with independent `A>=m`, retaining
every individual exit divisor and all recursive costs.

It also proves a necessary qualification on uniform complexity. For the
fixed targets 2 and 3 and one paid rank-1 site, every A>=4 satisfies
`B_n=2^(floor((n-A)/2)+1)` on `A<=n<2A`. The width outputs on that plateau
alone contain exactly `floor((A-1)^2/4)+2A` bits. At `N=2A-1`, a uniform
near-linear explicit all-rank bit-output bound is therefore impossible.
This does not contradict the retained selected construction: its finite
template is fixed before multiplication input size varies.

## Change and exact scope

Adds only `research/ambient-rank-library/`, containing the proof, bounded
integer evaluator, separately written explicit-occurrence/prime-valuation
oracle, semantic controls, source pins, receipt and registered replay.

The ambient-cap flow is inherited from the retained #6916 compiler proof
§6. The new quantitative analysis proves uniform contraction by `(A-1)/A`,
an all-prime plateau divisor with exponent `A*ceil(log2 k_min)`, and
explicit binary/indexed and sequential-tape metadata costs. The default
constant m cannot be substituted for A: for A=64 the actual width B_127 is
2^32 while that false one-plateau divisor is 8.

For each fixed A and fixed histograms, evaluated row lengths remain
polylogarithmic in N, indexed construction is `N*polylog N`, and the
sequential companion is `N^2*polylog N`. The proof exposes every A-dependent
factor when A is supplied in binary. Initialization, arithmetic lengths,
sorting, child-table access, copying, head restoration and historical cells
are charged. These are metadata bounds, not native payload-movement claims.

## Novelty and predecessor credit

Credit #4507/#5071 for least chronological gcd/LCM integrality, #4638 for
the default plateau-visit argument, #6916 and the selected source lineage
for independent ambient geometry, and #7345 at
`022461f115369efd988ef8c459907f5544bb8bb3` for product aggregation and the
quantitative default-library framework. The new evaluator adapts that code;
its frozen original is used only for separately labelled regression checks.
The ambient extension and varying-A lower bound are the delta.

This supplies a valid numerical library premise for the separately
published [chronological leaf/owner locator](https://github.com/CubeJerry/integer-mult-bounds/tree/81f0b0b9a920bd1c9da583cbc3612efd5e75ea94/research/chronological-leaf-owner-index).
That companion is contextual credit, not a runtime dependency or an
invented upstream PR reference. Canonical tested base is
`e54523517d0f03e58352e647c403a5af3e525a57`; exact nine-file provenance is
retained in `SOURCES.json`.

## Reproduction and evidence

From the repository root with Python 3.12 and the standard library:

```sh
python -I -W error -B research/ambient-rank-library/verify.py
python -I -O -W error -B research/ambient-rank-library/verify.py
python -B scripts/research_package.py --package research/ambient-rank-library --check-only
```

Direct marker: `PASS_AMBIENT_RANK_LIBRARY`. Both direct commands compare
the complete computed hash-bound receipt without writing to the package.
The independent oracle explicitly constructs role words, paid paths and
target ports, then uses prime valuations for widths and exact rational
per-array costs. It imports no production evaluator. All fields agree on
1,267 ranks, 21,442 units, 31,124 cuts and 35,141 constraints; exact
all-prime divisibility holds at every checked rank. The lower-bound family
is checked on 4,000 plateau rows across 81 ambient values. Fifteen semantic
and domain controls reject. Separately, 146 default-A rows agree with the
frozen predecessor. Six frozen local source copies are authenticated.

The large-A test uses the number `153^1920` only with toy histograms and
evaluates bounds/bit-count descriptors. It materializes zero library rows.
Finite checks corroborate the written universal proof, not replace it.
The separate reviewer accepted the universal argument and checked 269 complete
rows using a positive source census and brute-force least replication, plus
260 plateau widths and three semantic mutations. Normal and optimized
receipts match. The unchanged review and checker are retained under
`independent/`; the root authenticated all nine exact commit/path bindings.

## Limitations, open obligations and kappa

**No new kappa.** Selected `0.00363005817` and all five assumptions remain.
The actual selected evaluated target/paid manifest and winning library are
not materialized. This package proves neither native correctness nor full
scalar/phase/adapter instruction emission, physical owner routing, owned
erasure, precision/tape admission or analytic recovery. It supplies metadata
to those interfaces. Open questions are source-specific gcd-sensitive
widths, actual selected manifest binding, and full instruction emission
with all physical costs. No selected cold replay, Lean, Docker, human or
proof-kernel acceptance is claimed.

Prepared for **@CubeJerry**, with substantial OpenAI assistance. Credit
Jacob Alan Sussman, zxv, Mihir Srivastava, the #4638/#5071 authors and all
retained native/outer lineage as detailed in `NOTICE.md`. Predecessor
notices remain. New material is Apache-2.0.

## Merge scope

One isolated package. No predecessor, shared implementation, fork main or
selected-frontier changes. This text is a proposed PR description; the run
publishes a checked fork branch for user review and does not submit an
upstream PR.
