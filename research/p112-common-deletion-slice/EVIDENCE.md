# Evidence and verification limits

## Established result

At canonical baseline `997e6a9ca7b4f95d50e366f61412fd640d72a88a`, priority
revision 6, this package proves the sharp shared-deletion span four for the
literal first space in FIXTURE.json, every six-dimensional partner and all
real or complex directions. README.md gives the coverage argument.

RESULT.json is a deterministic receipt, not a log copied from a predecessor.
It records 788,035 partner spaces, 776,806 distinct live masks, 5,680 parabolic
systems, 795,182 common-cut states and 197 nontrivial rational-rank checks.
The exact boundary trace is regenerated and independently checked on every
replay; its canonical SHA-256 is recorded in the receipt.

## Checks performed

The local environment was Linux x86-64 under WSL2, CPython 3.12.15 and 3.13.5,
GCC 14.2.0, with system Boost.Multiprecision headers.

- Registered CPython 3.12 replay passes, including all fifteen behavioral
  groups. The final native build uses `-std=c++17 -O3 -mpopcnt -Wall -Wextra
  -Wpedantic -Wconversion -Wshadow -Werror`.
- The second six-flat enumerator agrees on every live mask and the complete
  multiplicity histogram. It uses canonical least coset representatives;
  the first uses RREF pivot and free-entry enumeration.
- The Python checker separately evaluates every one of the 197 nontrivial
  scanner boundaries. Ascending-pivot binary ranks and Fraction elimination
  agree with descending-pivot binary ranks and arbitrary-precision integer
  elimination in C++.
- The literal sharpness witness has four independent directions, with
  residual ranks `[7,7,7,7]`. Removing its common cut fails. Duplicate directions,
  false claimed ranks, malformed deletion sets and dependent annihilators
  reject rather than reporting a theorem.
- All 512 subsets of a dependent nine-vector fixture agree with exhaustive
  XOR-span cardinalities. Root reconstruction, distinct labels and normal-plane
  coverage have separate behavioral checks.
- Three compiled mutants reject under scanner controls: a free cut at rank
  eight, a single-character cut at rank nine, and combining separate cuts
  into a six-line purported common budget. Malformed scanner streams, JSON
  shapes, oversized JSON and CLI inputs also reject.
- Ruff, formatting, warnings-as-errors Python compilation, package metadata
  and provenance validation, and the sixteen assignment tests pass locally.
- Before the final native optimization, normal Python 3.12 and optimized
  Python 3.13 full scans produced identical receipts. The final registered
  replay requires that same receipt. The POPCNT optimization changes only
  execution and has an explicit CPU-support guard.

Exact replay commands, from the repository root with external TMPDIR:

```sh
python3.12 -B scripts/research_package.py --package research/p112-common-deletion-slice
python3.13 -O -B research/p112-common-deletion-slice/verify.py
python3.12 -B tests/test_research_assignment.py
ruff check research/p112-common-deletion-slice
ruff format --check research/p112-common-deletion-slice
```

Two early outer command wrappers hit their wall limits. Their remaining child
scans or controls finished and were drained before further replay. Neither
wrapper is counted as a successful registered invocation.
The later registered command completed with exit zero. Temporary outputs and
compiled mutants stay outside the checkout and are disposable after publication.

## Resource and implementation decisions

The new scan has no recursion, global mutable state, dynamic evaluation or
unbounded search. Root geometry has 120 lines, eight simple reflections,
255 parabolic seeds, at most 4,000 members per orbit and 6,000 total systems.
The four actual orbit sizes are 1,120, 120, 3,360 and 1,080.

Scanner capacities are explicit: 788,035 flat records, 128 separately qualifying
systems, 256 admitted normal rows, 65,536 states per pair and 4,096 nontrivial
rank records. Every capacity breach fails the run. Observed maxima are 32
qualifying systems, 16 states per pair and 197 rank records. Python separately
bounds an emitted rank case to 120 rows. JSON/model input is at most two MiB.
Compile, scan and control subprocesses have finite timeouts. Standard sorting
and membership algorithms only operate on these bounded collections.

The first-space cardinality filter is a necessary condition, not a changed
acceptance gate. A partner contributes at most 20 live labels, so a system with
more than `20+36+4` residual lines after the first space cannot qualify. The
independent flat enumeration checks this 20-line premise before the scan.

Power-of-Ten rule 3 deviation: Python's managed runtime, C++ standard containers
and Boost integer arithmetic allocate during computation. They cannot meet a
literal allocation-free steady phase without replacing these language/library
facilities. The finite capacities above bound collection growth; rank arithmetic
has dimension eight and input entries bounded by 64. The Euclidean loop has a
4,096-step fail-closed cap. Compensating controls exercise malformed boundaries,
rank identities and input-size exhaustion. Any extension beyond this finite
model must reassess the capacities and memory use.

Rules 8 and 9 use the language's normal fixed-target standard-library algorithms,
not generated code or an extensible callback registry. Their comparator and
predicate targets are visible lambdas over bounded vectors. The only platform
extension is the documented fixed-width `unsigned __int128`, plus the guarded
x86-64 POPCNT instruction. No source files are rewritten by the native build.

Build the lever shaped the result into a rerunnable complete slice checker
rather than a failed search report. Prove it works required literal boundary
replays and independent arithmetic at every nontrivial rank decision. These
checks do not make the whole search engine an independently reimplemented proof.

## Not established

No full C5 census, orbit-representative coverage for other first spaces,
uniform exclusion of normal planes, decoder construction, supplier admission,
selected-frontier update, native outer compiler replay or multiplication
theorem is claimed. Concurrent PR3161 now reports closure of the historical
b=5 application by a different global rank-six theorem. This rank-seven slice
is not claimed as another new exclusion for that cell. The package reuses
PR3160 geometry with explicit attribution;
there is no independent human or proof-kernel review. Historical provenance
hashes were compared locally, but standalone replay does not fetch pending PR
heads. Hosted CI and maintainer review are separate from the local evidence.
