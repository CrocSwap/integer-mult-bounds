# Executed verification

Windows / CPython 3.14.5, standard library; client date 2026-10-13.

- Producer normal and `-I -O -B` executions passed every source pin, all
  20,160 invertible binary 4x4 matrices, 604,800 cross-shear transitions,
  complete weighted Dijkstra labels, every Bellman inequality, predecessor
  equalities and exact call layers through five calls.
- Independent dense rank-one BFS passed normally and under `-I -O -B`.
  All 20,160 distance labels matched, not only the endpoint minimum. All
  12 rank-two decompositions and 12 cyclic rotations over F2/F3/F5 passed.
- Five omitted-call mutants, unconjugated rotation, partial exchange, false
  rank metadata and an impermissible free cross-bank bridge were rejected.
- Eight package controls passed under `-I -O -B`: missing/extra source pin,
  wrong source digest, wrong base, changed selected snapshot, repinned wrong
  kappa, typed receipt change and changed rank-floor receipt.
- The selected-record integrity checker passed. Staged whitespace checking
  passed before commit. No selected/predecessor/upstream file changed.

The written proof is field-independent; these finite executions corroborate
it and verify the explicit GL4 instance. Neither is represented as a formal
proof in Lean or as supplier installation. Full native physical replay,
global supplier invoices, cold/frontier/full repository suites and hosted CI
were not run. No compiler, environment or dependency was installed or changed.
