# Executed validation

Executed on 2026-10-13, Linux x86_64, at base
`f567884aeb8851b6e794af1184119a3bfbe1e631`.

## Complete verifier

Both commands exited zero and produced the identical complete deterministic
receipt in EXPECTED.json:

1. **CPython 3.14.4**, ordinary isolated execution:
   `python -I -B research/r439-four-wire-prefix/verify.py --output NEW --receipt NEW_JSON`.
2. **CPython 3.12.3**, optimized isolated execution, from `/tmp` against a
   **read-only minimal source closure whose path contains spaces**:
   `python3.12 -I -O -B /path/to/closure/research/r439-four-wire-prefix/verify.py --output NEW --receipt NEW_JSON`.

The relocated closure contained this package and precisely the 12 files in
SOURCES.json, with no Git metadata or additional repository files. All source
files were mode 0444 and directories 0555. Logs, fresh binaries and regenerated
artifacts were written outside that closure. Native helper subprocesses use
ordinary isolated Python; `-O` also exercises this package's explicit rejection
checks and the imported source checker in the parent interpreter.

Both runs rebuilt the seed-11 search, compared all decoded candidate fields,
independently checked 242,940 group edges and all 95 local maps/minima,
checked both-order positive domination, replayed the complete source words,
and compiled/reran unchanged native checkers on both words at 5/9/11 stages.
Native rank histograms, MOVE paths, copied-center lifecycles, column identities
and prefix bounds passed. All 12 local controls and all 96 omitted-bridge
controls rejected. The stale-C control retains the correct full endpoint and
all other interface conditions while failing literal H4, demonstrating that
semantic equivalence alone is not accepted as this package's interface.

## Toolchain and source binding

C++ compiler: `c++ (Ubuntu 15.2.0-16ubuntu1) 15.2.0`, with `-O2 -std=c++17`.
Native macros: HDIM=8, NCOPY=9, VPORTS=111, RHELP=439, KPAIRS=2/4/5.
All compiler and replay commands are retained in each run's
`native/commands.json`; raw reports and logs are alongside them.

The first compile found Boost absent from the host. The Ubuntu
`libboost1.83-dev` package, version `1.83.0-5ubuntu5`, was downloaded and
extracted under `/tmp`; no system package installation was needed. Its archive
SHA256 is `c17abc5a40a074c3d959655191ebec1561fa25f14f4948f6788be49417d4b234`.
Both successful runs set `BOOST_INCLUDE` to that extraction's `usr/include`.

All 12 source SHA256 pins were checked against the exact base Git objects.
The word and `xcheck_p.py` were additionally checked byte-for-byte against
their original paths in PR589 commit
`a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`.

Canonical full-word SHA256:

```text
baseline  5642fd0e35a1acc11acff8d0c08350c1617e95f310d4d35ad63a651f9eeeba0b
candidate cf2f2fc28bb6f7084ed993e008edeb762657330049b0a470c8a4ac8955251971
```

The generated candidate is compared after JSON decoding and canonicalization.
Every field is covered, including metadata; regenerated gzip bytes are not
used as a cross-environment equality condition.

## Package controls and scope

All **eight `test_package.py` tests** passed in the ordinary 3.14.4 environment
and in the optimized, isolated, read-only 3.12.3 closure. They check altered
and absent immutable sources; duplicate JSON keys, NaN and Infinity;
boolean-versus-integer receipts; distinct gzip encodings of identical payloads;
and refusal to overwrite existing builder outputs, verifier outputs or receipts.

The upstream branch was refreshed unchanged. The final open-PR inventory and
related original proposals were reviewed for overlap; this applies the credited
PR754 method to selected R439 prefix windows with literal paired cleanup.
Only `research/r439-four-wire-prefix/` is added. Changes to the selected
construction, full repository `make verify`, full supplier cold reconstruction,
global hosting/invoice/outer assembly, and a formal Lean multiplication theorem
are outside this local contribution and were not run or claimed.

Hosted CI results are reported separately on the PR at its published head;
these local passes do not imply hosted CI has run or passed.
