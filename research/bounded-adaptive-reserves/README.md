# Sharp adaptive contraction with bounded reserves

For arbitrary finite two-type nonnegative row menus, the best common
contraction rate under a reserve-weight imbalance cap has an explicit closed
form. This is a scoped written mathematical proof with exact finite
corroboration, produced by Nick Petalas. No new kappa is claimed.

Write first-type rows as (a,b), second-type rows as (c,d), and require
max(w1,w2)/min(w1,w2) <= B for positive weights and B>=1. Then

```text
best rate = max {
    max_(a,b) [a+b/B],
    max_(c,d) [d+c/B],
    max_(a,b),(c,d) [(a+d+sqrt((a-d)^2+4bc))/2]
}.
```

[PROOF.md](PROOF.md) also gives the complete feasible weight interval at
every rate. For rational rows and rational B, rational weights attain the
best rate exactly when that rate is rational. A new synthetic four-row
example has the sharp law max(1/(2B),sqrt(2)/4), including an irrational
plateau where rational weights approach but do not attain the optimum.
The same cap gives the all-depth abstract relative tail bound B*q^k in
the ordinary maximum norm whenever q<1.

This answers the bounded-reserve version of Open next question 2 in
Ali Romman's [#6472](https://github.com/CrocSwap/integer-mult-bounds/pull/6472).
Its independent adaptive row contract is a cited premise. No predecessor
executable, receipt or scientific census is imported or replayed.
Nick Petalas's older [#6555](https://github.com/CrocSwap/integer-mult-bounds/pull/6555)
solves one uncapped synthetic menu; its menu, identity and cutoff are
background, not the main step here. Classical two-by-two Perron roots,
positive diagonal scaling and weighted contraction retain their credit.
Global mathematical priority for these classical methods is unclaimed.

## Evidence and reproduction

The [verifier](verify.py) uses exact fractions. It decides a rational proposed
rate using the formula's boundary charges and determinant inequalities, then
constructs the entire feasible ratio interval. A separate oracle normalizes
w1+w2=1, enumerates all boundary vertices and tests the original row
inequalities directly. It uses no row-pair determinant.

The complete finite domain contains every singleton or two-distinct-row menu
drawn from {0,1/2,1} squared for each type, budgets 1,3/2,3, and rates
0,1/2,1,3/2,2. All 30,375 decisions agree: 11,831 feasible and 18,544
infeasible. Every delivered interval endpoint and midpoint is checked
against the original inequalities. Additional checks cover 455 exact phase
thresholds, 387 finite-depth tails, eleven malformed contracts and three
false certificates that expose the pair or reserve-boundary charges.

From the repository root, with standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/bounded-adaptive-reserves/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/bounded-adaptive-reserves/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/bounded-adaptive-reserves
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/bounded-adaptive-reserves --check-source-history
```

Another CPython 3.12 executable may replace the host-specific path. Each
direct replay prints a generated JSON receipt bound to all six package
files, followed by PASS_BOUNDED_ADAPTIVE_RESERVES. It writes no files.
Both registered commands have identical coverage and a 120-second deadline.
Exact provenance pins, including the cited predecessor proof, are in
[SOURCES.json](SOURCES.json). There are no live external proof inputs.

## Scope and implementation limits

The theorem covers all finite real nonnegative menus and all real B>=1.
The executable decides rational thresholds for at most sixteen rows per
type, with rational input numerators and denominators of at most 64 bits.
These executable bounds do not narrow the written theorem.

There is no recursion, subprocess or network call. A decision has at most
256 row pairs, and the independent oracle has at most 34 vertex candidates.
The replay domain is fixed. Every function is below sixty physical lines,
and explicit invariant failures remain enabled under optimized Python.
Managed allocation is a power-of-ten deviation: fractions and collections
allocate during execution, but the input sizes, menu counts, source-file
sizes and every iteration domain are bounded. The only source I/O reads
the fixed six-file receipt inventory. Warning-strict normal and optimized
execution and AST inspection are the available diagnostics; no separate
static type checker or repository-wide analysis is claimed.

No actual complete supplier menu, physical reserve, native delivery,
restoration, compiler, ownership, precision/tape or analytic recovery is
established. The five selected framework assumptions remain. There is no
selected-frontier change, complete multiplication theorem, selected cold
replay, Lean or Docker run. The universal result rests on the written proof,
not finite extrapolation. Independent human and formal proof-kernel review
are unclaimed.

## Open next questions

1. Bind one complete current two-type menu and its real reserve consumer.
   Start with every child, adapter and restoration charge and the permitted
   B. The missing source-to-row mapping blocks any physical improvement.
2. Retain an explicit reserve cap for three or more types. Start with a
   rational threshold, one normalized weight and all pairwise reserve
   inequalities. A useful higher-type formula and consumer remain open.

The structured first steps and blockers are in [TASK.json](TASK.json).
The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19542404)
records the scope. Source/author reservations, live PRs and Discussions,
recent account work, main README text and merged PRs were searched for
overlap. Sparse omitted notes, arbitrary historical diffs and unpublished
work remain limits; the search is not a novelty certificate.

## Credit

This contribution was produced by Nick Petalas. Ali Romman supplies PR6472's
row contract and optimization question, with its credited M-matrix,
Bellman, independent-row-uncertainty and typed-recursion lineage. The
predecessor's full attribution remains unchanged. New work is Apache-2.0.
