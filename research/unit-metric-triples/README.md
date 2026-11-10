# Exact full-retention criterion for positive unit metric triples

This contribution was produced by Nick Petalas. Apache-2.0.

For positive rational 2-adic units a,b,c, the metric D=diag(a,b,c) has a
full retained directed anchor box for every rational three-column factor
with nonempty original canonical ties exactly when

    a = b = c modulo four.

For every other residue pattern, the new rational four-row family has box
exactly three. Its third metric coefficient is independent. This removes
the repeated-weight restriction from JoyboyBrian's
[PR5213](https://github.com/CrocSwap/integer-mult-bounds/pull/5213) in the
unit domain and answers that part of its arbitrary-triple opening.

Claim type: scoped written algebraic proof with exact finite corroboration.
[PROOF.md](PROOF.md) proves both directions and preserves the original
whole-instance anchors. The source theorem, coloring and box definitions
are cited inputs, rather than audit or replay deliverables.

For example, D=diag(1,3,5) has the obstruction

    P = [(1,1,0), (3,-1,2), (3,-1,-6/5), (1,0,1)],
    M = [[4,0,0,1], [0,32,0,13], [0,0,96/5,-3], [1,13,-3,6]],
    A = B = (3,3,3,5),  box=3.

The first three mutually orthogonal rows force an impossible rank-three
binary pairing inside a two-coordinate label plane. Three rows attain the
bound. In contrast, every admissible factor for D=diag(3,7,11) retains all
its rows by the new criterion.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/unit-metric-triples/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/unit-metric-triples/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/unit-metric-triples
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/unit-metric-triples --check-source-history
```

Another CPython 3.12 path may replace the absolute interpreter path.
Expected markers are `PASS_UNIT_METRIC_TRIPLES`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.
The direct verifier prints a newly generated receipt with all seven package
file hashes and writes no files. To save it, add
`--receipt /absolute/external/scratch/receipt.json`; the destination must not
exist and must be outside the package.

## Evidence

The finite domain consists of all 216 ordered triples from
{1,3,5,7,1/3,3/7}. Positive cases exercise rational factors with mixed column
minima, negative valuations, opposite coloring classes and inactive columns.
The 54 admitted metrics give 810 full witnesses comprising 13,446 rows.
The verifier checks these against literal normalized rational factors,
with no row-subset renormalization.

For every complementary metric it constructs the four-row obstruction,
checks all actual orthogonal-core products and positive diagonals, and
enumerates every ordered subset and supported label assignment in the box
definition. The full histogram is (1,24,288,1296,0). Each enumeration visits
36,745 assignments. Six additional coordinate permutations reject full
retention. The 162 complementary metrics account for 5,952,690 ordered
assignments, apart from those additional permutations. These are finite
corroborations of the quantified written proof.

Twenty-one controls reject invalid or nonunit metrics, inexact arithmetic, capacity
violations, empty ties, the wrong residue class, duplicate rows, unsupported
labels and a wrong directed-zero pairing. All contracts remain active under
optimized Python. No predecessor scientific verifier is imported or run.

## Scope, provenance and limits

The task card `complex-rank-shape-decoder` is marked changed in
[TASK.json](TASK.json). This is an algebraic decoder side result. It does
not construct a physical coframe or a favorable complete signed invoice.
Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority
revision 8. The selected source-binding first command passed and reported
selected kappa 781451/250000000; the selected frontier is unchanged.

[SOURCES.json](SOURCES.json) pins the two source proofs, catalogue and
selected record as provenance. They are not runtime inputs. Verification
needs only these seven package files. Live open PRs and claims, main-tree
README searches and merged-PR searches were checked. The cached overlap
report had complete remote pagination but incomplete sparse local-note
coverage. Unpublished work and arbitrary historical diffs remain limits.

The theorem permits arbitrarily many rational rows, with all three metric
valuations zero. It gives no classification for unequal metric valuations.
The finite implementation admits at most 64 rows, 128-bit exact metric
numerators/denominators and 1,024-bit row numerators/denominators. Its
exhaustive oracle admits at most four rows and 28 label pairs per row.
The mathematical proof has none of these finite implementation limits.

All loops have finite bounds from these capacities or the fixed replay
domain. There is no recursion or dynamic code generation. Functions are
under 60 physical lines. Python/Fraction allocation is a managed-runtime
deviation from fixed-allocation discipline, bounded by these capacities.
Warning-strict normal and optimized execution provide the available
diagnostics. External Python linters and type checkers were unavailable
locally. No project-wide analyzer configuration is changed.

The rule 3 deviation covers `metric.py` and `verify.py` for each terminating
replay. Python and Fraction require runtime allocation. At most 64 rows,
4,096 matrix entries and 112 oracle label pairs are live per fixture;
the exhaustive assignments are streamed rather than retained. The fixed
domain and invalid-capacity controls verify these bounds. A future steady
runtime integration must replace this reference implementation with fixed
storage before relying on allocation restrictions.

No native realization, arbitrary dirty-state implementation, COPY/routing,
precision/tape, stock, compiler, supplier admission or outer multiplication
claim is supplied. Lean, Docker and the selected operator cold replay were
not run. Independent human and formal proof-kernel review are unclaimed.

## Open next questions

- Classify positive diagonal triples with unequal valuations. First track
  original anchors under dual power-of-two column scaling and separate the
  valuation parity patterns. The present unit proof does not settle them.
- Bind a newly admitted unit metric to one actual weighted decoder and
  price its complete physical bill. Every target, owner, native change,
  restoration and precision cost remains required.

[TASK.json](TASK.json) records the relevance, first step and blocker for each.
Work stops at the unit-domain classification.

## Credit

JoyboyBrian / PR5213 supplies the diag(1,d,1) classification, its
original-anchor discipline and the arbitrary-triple opening. Sagar Thakrar /
PR3612 supplies the rational Gram theorem, modulo-four coloring and F/O/L
labels. Nick Petalas / PR5172 supplies the fixed diag(1,3,1) obstruction.
Credit Aaron Wang/navinor / PR2914, PR2978 and PR3031, DreamingOfClouds's
F-star lineage and the labeling predecessors retained by PR3612. Their
proof files and credit lines remain unchanged. The new contribution is the
exact unit-triple criterion and independent-third-weight obstruction family.
