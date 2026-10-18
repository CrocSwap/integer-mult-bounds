# One phase-A R420 quad: 19 → 11 gates, optimal in a monotone integer model

**Research contribution / finite circuit improvement. No new κ.**

This replaces quad 4 (zero based) in eumemic's PR543 R420 bit word with an
11-gate circuit, preserving its exact ordered six-register **integer** map.
The original needs 19 gates. Regenerating literal reverse cleanup saves eight
more gates: **26,916 → 26,900 binary ADDs** in the complete native word.

Eleven is minimal among circuits realizing this exact integer matrix with
only in-place operations `r[d] += r[s]`, `d != s`, on these same six registers.
The minimum is **not** asserted for arbitrary F2 circuits, signed additions,
extra workspace, output permutations or a different integer lift of the F2 map.

## Reproduce

From the repository root, Python 3.9+ with the standard library:

```sh
python3 -B research/r420-quad4-optimal/verify.py
python3 -I -B research/r420-quad4-optimal/independent.py
```

The first command prints:

```text
PASS_R420_QUAD4_OPTIMAL gates=19->11 minimum=11 states=165828 native_adds=26916->26900 columns=660 controls=10 kappa=unchanged
```

The second prints its exact BFS receipt and
`PASS_INDEPENDENT_QUAD4_MINIMUM minimum=11 truth_table=64`.
Both recompute their results and compare complete committed receipts. No
network, optimizer, external solver, C++ compiler or cached search is needed.
The primary command uses a temporary directory and leaves the checkout alone.
`--write-receipt NEW_PATH` writes an additional receipt and refuses overwrites;
it never modifies `EXPECTED.json` by default.

## Fixed object and circuit

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
PR543 source: `2065fe4f72a914d907f1046603f5a36f17018535`.
The source word and native checker are pinned by SHA-256 and Git blob ID in
[SOURCES.json](SOURCES.json), alongside the unchanged record exporter and
provenance files. Context-only hashes are separate from runtime source admission. The selected certificate at this base is #626/#543,
κ = `51110230636731/31250000000000000` = `0.001635527380375392`.
That certificate is context, not a bound newly proved by this package.

The scope is exactly phase `A[690:709]`, frame 306, with ordered registers
`[259,270,284,290,294,296]`. These are six existing dirty helper registers.
[CIRCUIT.json](CIRCUIT.json) carries the old and new literal operations.
Naming the six initial values `a,b,c,d,e,f`, execute:

```text
b += d
d += f
d += e
d += c
a += d
b += a
f += b
c += d
c += f
e += d
e += f
```

The exact integer endpoint, in that same register order, is

```text
[1 0 1 1 1 1]
[1 1 1 2 1 1]
[1 1 3 3 2 3]
[0 0 1 1 1 1]
[1 1 2 3 3 3]
[1 1 1 2 1 2]
```

applied to the initial column vector. Replaying the original 19 gates produces
the identical matrix. Reduction modulo two therefore preserves all six
symbolic inputs, including dirt, without recomputing the D preconditioner.
All eleven operations occur at the original quad frame and touch the same
six registers. The constructor regenerates C as the literal full-frame reverse
of every z-destination gate in A and B.

## Why the finite search proves this scoped minimum

Starting from the identity matrix, every allowed row addition leaves every
entry nonnegative and every diagonal entry at least one. If a circuit reaches
matrix M and its last gate is `row d += row s`, the predecessor is obtained by
subtracting row s from row d. It must have nonnegative entries and diagonal
at least one. Conversely, each such inverse step is an allowed forward gate
when reversed. Thus the inverse graph contains **every** circuit in the stated
class, including ones longer than the submitted witness.

Every inverse step strictly decreases the sum of all entries: row s has a
positive diagonal and hence is nonzero. Entries also stay between zero and
their target bounds. The reachable graph is finite and acyclic. With identity
cost zero and unreachable leaves cost infinity, the exact recurrence

```text
D(M) = 1 + min D(M with one admissible row subtraction)
```

computes the minimum, or infinity if no path reaches identity. No heuristic
pruning, floating-point bound, time cutoff or target gate limit is used in the
verification implementation.

`optimal.py` completes **165,828 states and 917,020 edges**, including 2,166
states from which identity is unreachable. It returns `D(M)=11`. The complete
sorted state/distance digest and distance histogram are in `EXPECTED.json`.
The witness above attains the lower bound.

`independent.py` separately reconstructs the integer map by column replay of
the pinned source slice, represents rows as packed base-4 integers, and uses
breadth-first inverse search. It imports none of the constructor, matrix
engine or primary search. The layer sizes at depths 0 through 11 are:

```text
1, 14, 110, 576, 2278, 6999, 16873, 31073, 40936, 35950, 20997, 8138
```

Identity first appears at depth 11, after 163,945 states have been generated.
It also exhausts all 64 Boolean inputs and their literal cleanup. These are
two computational implementations plus a written completeness argument, not a
proof-assistant formalization or independent human review.

## Physical paths, bills and coverage

The positive integer transfer of the forward quad is equal to the baseline.
For reversed operation lists, the new positive transfer matrix is entrywise
no larger than the old one; both exact matrices are in the receipt. Therefore,
for **every nonnegative entering bound vector**, neither direction has a larger
endpoint envelope. Within a block, positive additions only increase row bounds,
so every intermediate row is bounded by the block endpoint. The replacement
has no copies, resets, extra registers or changed frame in its interior.
Consequently substitution in both the quad and its cleanup cannot increase
the full word's positive-prefix bill, in either orientation.

The complete replays corroborate that argument:

| Quantity | Original | Replacement |
|---|---:|---:|
| Quad gates | 19 | 11 |
| Native scalar ADDs | 26,916 | 26,900 |
| Exported records | 29,874 | 29,858 |
| Forward positive prefix | 144,651 | 144,651 |
| Reverse positive prefix | 2,270,064 | 2,261,508 |
| Prefix payload bits | 100 | 100 |
| Helpers / retained copies | 420 / 9 | 420 / 9 |
| Rank mass | 5,112 | 5,112 |

The unchanged native PR543 checker verifies E8 labels, all 672 closed frames,
frame legality, all 660 symbolic input columns, H1–H5, and the decomposed
restoration conclusion. The original and replacement are both freshly checked.
Every register's ordered frame path is equal between them. The local paid
histogram stays `{1:1320, 2:1440, 4:60, 5:120, 8:9}`.

The unchanged predecessor exporter produces the actual record streams. A new
set-valued record interpreter independently checks both orientations on all
660 columns, all nine COPY/ERASE lifecycles, and integer positive-prefix bills.
Its representation differs from the native checker's integer bitsets.

Ten negative controls reject: a missing local gate; a wrong source; F2-neutral
integer inflation; an **18-gate integer-correct circuit with an excessive
reverse envelope**; stale cleanup; an illegal low frame; missing dirt
compensation; F2-correct nonliteral cleanup; a dropped exported ADD; and an
odd-coefficient record mutation preserving F2 but exceeding the prefix budget.
The last control prevents confusing F2 correctness with an admissible bill.

## Search scope, overlap and limits

OS assignment seed **4** selects quad `4 mod 60`. The three candidate tasks,
stopping rule and local sprint claim are recorded in [CLAIM.json](CLAIM.json).
A capped exploratory inverse search completed the entire graph; the final
checker has no cap. No other quad is searched and no global optimality or
practical runtime speedup is claimed.

Concurrent PR691 (@mtpsl) independently shortens phase-A **quad 13** from 19
to 12 gates, with no gate-minimum claim. PR823 (Hao Yan / @FanPUYen) shortens
a quad in the different historical R480 word. Their integer-transfer and
reverse-domination work is related; this package adds quad 4 and complete
monotone-model minimality by two different exhaustive algorithms.

Before publication, all 1,051 open and closed PRs through #1052 were refreshed.
PR925 (Ross Richardson), PR1002 (@woklerx) and PR1027 (Hanson Sun / @bbMisk)
already use the same inverse-subtraction DAG and independent breadth-first
approach on other transfers. **No novelty of the search method is claimed.**
PR986 also establishes an exact guarded/unguarded boundary for a different
transfer. [OVERLAP.json](OVERLAP.json) records the exact comparison matrices and
source hashes: none of the #691/#925/#986/#1002/#1027 targets equals this target
under any of the 720 simultaneous register relabelings. PR789's exact schedule
minimum concerns phase-B block 7 and a different restricted circuit class.
PR904/#936/#952 optimize the later R439 word; their broader savings are not
added here. This submission retains its historical R420 scope. All seven
runtime/provenance source pins remain unchanged at publication refresh
`2921874911956718fcaaaf9396fe8267b3cfa9f0`.

Concurrent PR670 and PR674 resynthesize **phase-B 12-register blocks**. PR661
fixes the phase-B gate order and excludes circuit changes. PR686 changes
frame-zero D sharing and its interface. This package changes a six-register
phase-A quad, preserves the integer endpoint and H1–H5, and supplies an exact
monotone-model minimum. None of those concurrent implementations is imported;
composition with them has not been checked. See [NOTICE.md](NOTICE.md).

The unchanged child histogram provides **no new recurrence exponent**. This
package does not rebuild the multistage C++ cohort, hosted parent, supplier
invoice, or outer assembly for the changed word. Those remain integration
checks. The unchanged selected-record binding check passes; a full repository
`make verify`, selected cold replay, Linux CI and Lean proof are not claimed.
All inherited uniform/compiler, common-label/mutable-source, physical hosting,
precision/tape, exact recovery and analytic-transfer assumptions remain.
`upstream/` and every existing tracked file are unchanged.
