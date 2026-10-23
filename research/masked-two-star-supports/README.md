# Symmetric two-star masked P112 supports: bounded discovery checkpoint

**Exact finite support census and an inconclusive search; no new K.** One
single-thread MILP invocation with a 90-second solver limit found no incumbent
of cost at most 63. This does not exclude such a cover, even in this dictionary.
The unchanged dictionary is stopped; no coefficient synthesis was attempted.

For each of the 120 E8 root lines, form its nonorthogonal support C on P112
and its self-trimmed support N. The dictionary contains each original support
and each intersection of two originals. Left and right support caps are the
same set S. Distinct masks are deduplicated; the actual price is the binary
rank of B[S,S], with the retained dense orthogonality pairing B. There are
232 distinct original supports and **16,556** nonempty dictionary entries.

The census differs from the original C/N support theorem and the maximal
one-axis slices of rank-seven parents: it allows symmetric two-star
intersections and mixtures of ranks 6 through 9. It also differs from #5064's
nine-factor walk after a rank-one off-mask matrix update. See [OVERLAP.json](OVERLAP.json).

## Exact evidence and search limits

[RESULT.json](RESULT.json) binds the sorted complete dictionary by SHA256,
its rank/frame-hit census and the complete **262,928** orthogonal cliques.
Rank-six entries meet at most 1,020 of the 1,260 live eight-frames. This is a
finite statement about the declared dictionary, not all rank-six supports.

For an orthogonal clique F, any masked decoder restricts to an identity on F.
Each factor with support cap S contributes rank at most one there, and zero
when S misses F. Consequently the number of potentially active factors,
counted with multiplicity, must be at least |F|. These are necessary support
conditions for arbitrary complex coefficients under ordinary transpose.
Shrinking actual supports cannot repair a failed cap-level rank requirement.

The discovery model used all 112 singletons, 3,304 orthogonal pairs and 1,260
eight-frames: 4,676 rank constraints, plus the cost-at-most-63 constraint.
The 16,556 integer variables allow repeated occurrences of a support; every
occurrence pays its rank. The sparse matrix has 42,374,732 nonzeros. SciPy
1.18.1 / NumPy 2.5.4 returned time-limit status with no incumbent and no bound
in [SEARCH.json](SEARCH.json). The measured solver call took about 105 seconds,
and setup plus solve took about 124 seconds. A solver time limit is not a hard
wall-clock bound, and no second solve was run.

The standard-library verifier independently rebuilds the geometry, dictionary
and all clique sizes. Eight coordinate supports of total cost 64 pass every
clique constraint. Removing one coordinate fails; an underpriced COPY mutation
is rejected. Explicit row-span enumeration separately checks the coordinate
prices. With no incumbent, receipt fields for candidate cost and violations
are null, rather than a passing decoder claim. The full clique scan is a
candidate-validation facility; no missing incumbent is treated as a witness.

## Reproduce

From the repository root, Python 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/masked-two-star-supports
python3.12 -I -O -B research/masked-two-star-supports/verify.py
```

Expected marker: `PASS_MASKED_TWO_STAR_CENSUS`. Default replay is read-only
and compares the exact receipt. `--output NEW_PATH` exclusively writes a new
receipt; `--witness PATH` checks a proposed support collection against every
clique. The registered hook never reruns the solver. Discovery can be repeated
separately, with compatible NumPy/SciPy and an unused output path:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -B research/masked-two-star-supports/search.py --output /tmp/new-two-star-search.json
```

The first replay authenticates the declared live input pins. Direct verifier
execution needs no external files or Git beyond this directory. Geometry and
all allocation domains are finite; clique recursion has depth at most eight.
Python dynamic allocation is used for this bounded offline experiment. The
optional sparse solver used about 5.5 GiB resident memory at an observed sample;
it is discovery infrastructure, not a multiplier implementation.

## Boundary and remaining obligations

Even a successful support cover would leave the rational masked matrix
equations unsolved. There is no factorization, physical COPY program, native
word, restored dirty workspace, precision/tape bill, recursive moment,
compiler, outer admission or improved multiplication bound here. An exact
support screen cannot supply those costs. No selected cold replay, formal
kernel acceptance or independent human review is claimed.

Base main: `81e9bd69e4a5b00ba9c713a1620e36d576d5522e`, selected conditional
K 0.00302015, priority 7. [TASK.json](TASK.json) records the changed card and
stop rule. The historical card's positive-control command fails with
`KeyError: complex_profile` against the changed selected schema; the current
`research_selected_baseline.py` metadata control passes. Neither is a replay
of a new supplier. Historical fixed-invoice ceilings are not applied here.

## Open next questions

A changed non-symmetric completion or consumer could still give a lower-cost
decoder. Begin with its explicit coefficient/support contract and a complete
optimistic target/paid budget. The blockers are exact coefficient feasibility
and physical realization. This timed-out solve does not justify another
unchanged dictionary run, a universal floor or downstream supplier work.

## Credit

Credit DreamingOfClouds / PR717 for the masked decoder model; themilkman216 /
PR968 and the retained E8 geometry lineage; Navinor / PR1226, David Arias /
PR1236, Hanson Sun / PR1242, and the P112 rank-six and Hall-obstruction authors
for the support/frame questions and their explicitly narrower results;
Philippe Van Velzen and the masked-e8-padding-transfer authors for the
candidate ABI and puncture transfer. Frozen predecessor files are unchanged.

Prepared by Cinna Davis with substantial OpenAI Codex assistance in research,
implementation, verification and writing. New work is Apache-2.0. Publication,
a finite census and a replay pass are separate from scientific acceptance.
