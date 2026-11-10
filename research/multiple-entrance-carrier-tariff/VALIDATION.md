# Local validation and implementation bounds

The scientific checks ran on CPython 3.12.15, macOS 27.0.1 arm64, using
`/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12` and the standard library.

The direct warning-strict normal and optimized commands in README.md passed
in 0.043 s and 0.047 s. These are completion times, not speedup measurements.
Each registered command is therefore below its 120 s timeout and the CI limit.
The package runner passed both registered commands and printed
`PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=completed` in 0.364 s total.
Metadata/pin validation passed separately. `verify.py --emit` generated a
hash-bound receipt from the actual checks. Normal execution writes nothing.

## Exact finite coverage

- All 16 subspaces of F2^3 and all 6 subspaces of F3^2 are generated from
  spanning sets. Independent modular row reduction checks each dimension
  and every join/intersection distance; every triangle is checked.
- For each of six integer-scaled exact tariffs, the checker compares every
  entrance-line subset and every endpoint against Dijkstra on the full
  frame/visited-lines graph. The binary geometry has 2,048 requirements per
  tariff and the ternary geometry has 96, for 12,864 formula comparisons.
- The tariffs are linear, cap-one, cap-two, ceil-half, zero and 420r/(r+1).
  Their relevant integer values and the monotonicity/subadditivity premises
  are checked exactly. The proof, not finite tariff sampling, gives the
  theorem for every stated H and every field/dimension.
- Controls distinguish false free sharing, false containment and omission
  of the destination cost. A squared tariff has a cheaper subdivided route,
  demonstrating the need for subadditivity. In F2^3 a nonmonotone subadditive
  tariff has a cheaper detour, demonstrating the need for monotonicity.

The complete graph includes all intermediate subspaces and repetitions.
Dijkstra keeps a finite visited-line mask and frame index, rather than
assuming an upper bound on route length. Nonnegative weights permit a
shortest path without repeated expanded states. The superset minimum allows
extra visits, including lines that are not required by the particular query.

## Implementation limits

The executable supports exactly F2^3 and F3^2. It has no recursion, network,
subprocess, or package write operation. Its main shortest-path table has at
most 2,048 entries, its heap has at most 32,769 entries by the explicit
edge-relaxation bound, and each adjacency scan has at most 16 targets.
All file reads are capped at 1 MiB plus one overflow byte. All functions
are at most 35 physical lines. AST parsing and compilation passed; no
repository-configured Python static type checker was found in this checkout.
Warning-strict normal/optimized runs provide the available runtime diagnostics.

Power-of-Ten rule 3 has a managed-runtime deviation. Python allocates bounded
integers, tuples, matrices and heap entries during checking. The fixed domains
and loop/heap limits bound live algorithmic storage; allocator internals are
not instrumented. Raw-pointer/preprocessor restrictions have no direct Python
equivalent. Calls are direct except fixed standard-library iterator and JSON
operations. Exceptions enforce scientific predicates under optimized Python.

## Limits and publication checks

The written theorem concerns the declared complete subspace-distance graph.
Its physical metric applicability and attainment in a restricted native
route table are unrun obligations. No predecessor scientific replay, selected
supplier cold replay, native phase/all-column check, compiler build, Lean
build, physical restoration/stock/precision proof or analytic transfer was run.
Independent human and formal proof-kernel review are unclaimed. No new kappa.

The separate publication byte/history command is listed in README.md and
must pass before push. It checks source availability, not the mathematics.
Hosted CI is pending at submission and will be recorded in the PR body.
