# Verification and handoff

Verified on macOS arm64, CPython 3.14.6. This is a standalone research package;
only `research/universal-connector-boundary/` is added. Discovery base was
`91a2094f2e022930069e8cfdc810a3ea1b81cd09`; final checks use refreshed main
`47481c89fd30a43f8f882eb4b391e89c29273fd0`. The certificate retains the original
discovery base, and SOURCES.json separates original and submission contexts.

## Reproduction

From the repository root:

```sh
python3 -I -O -B research/universal-connector-boundary/verify.py
python3 -I -O -B research/universal-connector-boundary/test_package.py
```

Expected:

```text
PASS_UNIVERSAL_CONNECTOR_BOUNDARY pairings=945 max_coverage=31 queries=74 leaves=182
PASS_UNIVERSAL_CONNECTOR_PACKAGE relocation=1 regeneration=2 corruptions=6
```

Normal and optimized verification agree. Proof-relevant conditions use explicit
exceptions, so `-O` does not erase the checks. The verifier imports no generator
code. Its free noncommutative interpreter checks literal words, every initial
data/scratch symbol, expected products and inverses. The separate endpoint-
matching census uses a different combinatorial representation from the generator.

## Completed coverage and stopping rule

- Generator: restricted-growth words with each source label occurring twice.
  Independent checker: all perfect matchings of 2n labelled endpoints, followed
  by canonical source naming. Both exhaust 105 objects at n=4 and 945 at n=5,
  stop only when enumeration ends, and agree on every canonical word/coverage
  pair through a SHA256 of the sorted exact records and the coverage histogram.
- Four-source universality is also proved directly using two complementary
  two-dimensional subspaces. The five-source maximum of 31 is an exact finite
  exclusion, not a sampled failure to find a path. No claim is made about
  arbitrary reversible programs or general multiplication lower bounds.
- Literal construction: all 15 nonzero four-source rows and all 31 nonzero
  five-source rows, the two 74-query repairs, and the complete 182-/200-leaf
  expansions. Both ordinary star comparators pass symbolic maps/inverses and
  have independently recounted bills, including 278/1950 primitive calls.
- Dense replay: all basis initial bits and 25 distinct mixed states for each
  schedule at L=1,2,3. There are 564 basis cases and 225 mixed cases: 789 forward
  and 789 inverse checks. Both five-source schedules deliberately share their
  matrix banks; there are six distinct banks across nine schedule/bank
  combinations, with noncommuting/nonsymmetric witnesses at L>=2.
- Eight symbolic/accounting controls reject omitted restoration, a readout
  crossing a source toggle, an unpaid missing-mask readout, a wrong target,
  underpriced scratch/child, aliased ports and swapped factor order. Three dense
  controls reject restoration, destination and target faults independently.
- A relocated copy in a path containing spaces passes without the repository
  or network. Regenerating both certificate and evidence preserves every byte.
  Six on-disk corruptions fail with their expected diagnostics: false coverage,
  omitted census, missing connector restoration, unpaid child, false evidence,
  and changed retained predecessor bytes. The restored package passes again.

Seed 52 is the OS assignment draw and selects the four/five-source boundary
and the repeated-source label `52 mod 5 = 2`. It also fixes the finite dense
fixtures. The census is exhaustive, not random; its stopping rule and coverage
do not depend on the seed. Optional exploratory checks at n=1,2,3,6 did not
produce any additional contribution or claimed exclusion here.

## Provenance and repository gates

Both retained PR934 files match their exact remote Git blobs and local SHA256
pins. Original context hashes were checked against Git objects at the discovery
base; refreshed context hashes were checked against the submission base.
PR934's head was still `f3100aec6ce6a7b061987875d5e9a8b93801ac0b` at refresh.

`make selected-record-check` and all five tests in
`python3 -B tests/test_selected_result.py` pass on both bases. Python source
syntax and staged whitespace checks pass. The refreshed selected record is
PR890's conditional 1661957774647029/10^18; its T21 construction and maintainer
review were read. The selected files and `upstream/` have no contribution diff.

The final full open-PR inventory covered 710 PRs through #939. New #938 counts
one-source dirty-fanout equality cases and is credited; it does not duplicate
the multi-source universal source-path criterion or its five-source boundary.
The immediate prepublication refresh also inspected #940's Fourier-layout
audit and #941's R439 matching construction; neither overlaps this scope.
No pinned sprint issue existed at the initial or final query. The claim and
result link are local in CLAIM.md.

## Limits

Repository-wide regeneration, selected-supplier cold replay, hosted CI and
proof-assistant formalization were not run. This addition changes no existing
supplier, selected construction or shared generator; its exact standalone
replays and selected-record checks are the relevant validation performed.
Finite tests do not discharge the inherited all-size, physical hosting, tape,
precision or outer analytic obligations. The dense tape invoice is an explicit
upper bound with paid macro/control work, not a measured execution trace.

Review can focus on the prefix-difference reduction, completeness of the
945-matching quotient, scalar specialization proving the lower bound, and
the independence of the three interpreters. Substantial AI assistance and
predecessor attribution are recorded in NOTICE.md.
