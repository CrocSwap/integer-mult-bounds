# Response-subspace banks at 64 replicas

Conditional kappa = **0.001013370540420331** = 1013370540420331/10^18.
This improves PR401 by 0.00588694 percent and the subsequently posted PR402 value (0.001013357935292321) by about 0.001244 percent.

PR401's raw word, entrance gauges, complete local programs, both orientations, exact Gaussian phases and two-sided normalization are unchanged. The change is a 64-replica global packing: 5983 banks per stage with 3863 rank-one paddings, replacing the scaled eight-replica packing's 5984 banks, 3856 rank-one and eight rank-ten paddings. Nine stages give 576 invocations, 115287 live and 116078 physical families. This does not include PR402's separate target re-synthesis.

Run from a fresh output directory outside research:

    python -B research/e8-response-bank64/verify.py /tmp/response-bank64

Python 3.11+ and the source package requirements, a C++17 compiler and Boost are required. The full verifier checks manifests, freshly reconstructs and verifies the entire PR401 complex component, expands the global skeleton, emits every bank and actual inverse owner factor, independently decodes the schedule and costs, recalculates every finite bridge inequality, runs two exact moment engines and 47 strict outer inequalities, then freshly replays the bit component at the new complex bound. No optimizer or network is needed for verification. CI runs Python 3.11 and 3.14 and retains outputs on failure.

PATTERNS.json is a finite witness, not a hard-coded pass result: all helper inventories, disjoint axes, rank complements, owners, profiles and invoices are regenerated and checked. The expected kappa is only a regression assertion after exact derivation. Search records include unsuccessful smaller replica packings.

All inherited all-size window, arbitrary correlated bank, recursive compiler, fixed-tape, common-grid, restored-row, precision and analytic interfaces remain conditional. This is not an unconditional multiplication exponent theorem or a Lean proof.
