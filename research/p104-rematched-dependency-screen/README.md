# Where the P104 pooled matching test stops

Every one of PR2981's **2,309 compatibility edges** occurs in some perfect
matching. Pooling those possible pairs into PR2996's optimistic dependency graph
makes **all 4,992 required source-to-target dependencies reachable**. Consequently,
removing edges absent from every perfect matching and then applying this pooled
support test cannot exclude all matchings of these fixed covers. A stronger
obstruction must retain matching coherence or additional execution constraints.

This is a limit of a necessary-condition test, not a feasible correction. The
pooled graph uses 2,309 virtual helpers simultaneously, whereas a matching uses
208. It also grants contacts that need not coexist in any single flag and ignores
chronology. No supplier, lifetime optimum or new kappa is claimed.

## The finite certificate

The inputs are PR2981's fixed departure and arrival cover planes and the original
4,058-event P104 channel. [SOURCES.json](SOURCES.json) authenticates their bytes.
PR2981 is pinned at `3d24b92d8ba057b57cb2d480170ec407520e6882`.
The dependency test follows PR2996 at
`4d772802fe86e5185d5468db86b36472e6c81b96`. Arham Tahir's complementary PR2997 at
`16e790e10cc0bc737b9cd269020d3d967d36430f` checks the published full flags instead.
Neither pending audit is treated as supplier admission.

Slots have canonical indices `2*s+i` and `2*t+j`. Their prescribed frames are

```
L_s <= A_s,i <= B_t,j <= H_t
 dim 1    2       7      8
```

An edge exists exactly when `A_s,i <= B_t,j`. Intermediate dimension-d frames,
for d from three through six, range over the entire interval `[A_s,i,B_t,j]`.
A matching selects one edge per departure and arrival slot.

[RESULT.json](RESULT.json) records every target support mask, every missing
required-source mask, layer contact counts and the first missing coefficient.
There are three calibrated cases:

| Case | Virtual helpers | Missing required coefficients |
|---|---:|---:|
| PR2981's published pairing, all intermediate completions | 208 | 3,095 |
| Explicit alternative in [WITNESS.json](WITNESS.json), same relaxation | 208 | 45 |
| Union of all compatible pairs, same relaxation | 2,309 | 0 |

The alternative has all 104 source supports at 103 targets. Its only deficient
target is `Y40`, whose support is exactly `{X8,X41,X45}`. All 45 missing required
coefficients belong to that target. This is a concrete remaining obstruction for
that pairing, not a proof that 45 is optimal or that another pairing passes.
It also shows why the published pairing's numerical deficit cannot be extended
to every pairing without another argument. PR2996 itself makes no such extension.

In the union, the dimension-three contact graph is connected. After untimed
source injection it carries all 104 source supports. All 104 outputs eventually
receive them. This is the exact loss of information caused by pooling choices.

## Why every compatibility edge is matching-supported

Let M be the published perfect matching. Make a directed graph on departure
slots, with an arc `u -> v` whenever `(u,M(v))` is compatible. The checker finds
this graph strongly connected on all 208 vertices.

For any compatible edge `(u,b)`, put `v=M^-1(b)`. A directed simple path from v
to u, together with the arc from u to v, is an alternating cycle. Assign each
path vertex the next vertex's old arrival, then assign u the arrival b. Every
new edge is compatible, the arrivals remain a permutation, and `(u,b)` occurs.
When u equals v, the original matching already supplies the edge.

The verifier constructs and checks the complete 208-entry permutation for each
of the 2,309 edges. It records a deterministic digest of those checked witnesses.
No assertion of simultaneous availability of different witnesses follows.
Tests enumerate all 512 three-slot compatibility graphs and compare this
construction with literal perfect-matchings on the strongly connected cases.
An edge belonging to no perfect matching supplies a rejection control.

## Dependency contract and the pooling limit

Retain the X-only monotone, common-chart contract of PR2996 and its credited
predecessors. X is immutable; Y is unread. New helpers have arbitrary independent
dirty entrances. Their frames only increase, and scalar mixing requires equal
current frames. No original-helper reads, target feedback, source mutation,
descending transports or additional storage are supplied.

For each selected pair, make nodes at dimensions one through eight. Add upward
edges along that helper. At a dimension d, grant bidirectional contacts whenever
the two allowed frame intervals admit a common d-dimensional frame. For intervals
`[A,B]` and `[C,D]`, this is exactly

```
A <= D, C <= B, dim(A+C) <= d <= dim(B intersect D).
```

Indeed, any common V contains `A+C` and lies in `B intersect D`. Conversely,
a basis of `A+C` extends to dimension d inside that intersection. Granting these
contacts independently relaxes consistency of intermediate choices. Sources may
inject at every visited matching data frame without time restrictions. Targets
receive at every such matching frame. Independent dirty coordinates supply no
initial X coefficient. Induction over any legal scalar word confines its source
support to graph reachability. Cancellation can remove support, not create a path.
Thus a missing required path obstructs a correction, but a present path is not a
coefficient construction.

Any actual matching's graph embeds in the pooled graph by its selected pairs.
Every compatibility edge is matching-supported, so deleting edges that cannot
occur in a perfect matching deletes none. The resulting pooled graph has no
missing required paths. Therefore this particular matching-independent pooling
method cannot prove a universal support obstruction for the fixed covers.
This does not exclude stronger matching-coherent cuts, rank conditions, the
reported program-level lifetime floors, or any chronological obstruction.

## Reproduce and limits

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-rematched-dependency-screen
```

The registered replay runs both contact engines and eight behavioral test groups.
The interval engine takes about nine seconds locally; literal enumeration takes
about two seconds. These are replay timings, not multiplication benchmarks.
Direct optimized checks work without Git or network:

```sh
python3.12 -I -O -Werror -B research/p104-rematched-dependency-screen/verify.py
python3.12 -I -O -Werror -B research/p104-rematched-dependency-screen/verify.py --literal
python3.12 -I -O -Werror -B research/p104-rematched-dependency-screen/test_verify.py
```

`verify.py --emit` regenerates the complete receipt on stdout. The interval engine
uses the dimension criterion. The literal engine enumerates all 374 quotient
subspaces between each two-dimensional A and seven-dimensional B and compares
actual frame-membership masks. Both check all three cases and every receipt field.
They share input parsing, the matching-cycle check, correction arithmetic and
support propagation. They are distinct contact implementations, not independent
complete replays. Tiny direct interval enumeration and forward/backward/relay
controls separately test those boundaries. Actual CLI controls reject source
changes, duplicate targets, wrong receipt types, missing relation entries and a
contact-dropping oracle mutant. A Git-free export is checked too.

The search only proposed the retained witness. It found no passing pairing and
establishes no exhaustive exclusion. [TASK.json](TASK.json) records its finite
caps and the subsequent scope change to certifying the pooling limit. No search
is required for replay. There is no chronological schedule, consistent full flag
assignment, scalar coefficient fit, dirty restoration, native execution, physical
hosting, precision, complete consumer bill or all-size proof here. No selected
cold replay was run. Unknown implementation costs are not zero. Registered
CPython 3.12.15 replay and optimized CPython 3.13.5 checks pass on Linux/WSL2
x86_64. The selected record and frozen inputs are unchanged; hosted CI and
independent human or formal-kernel review remain separate.

## Open next questions

Can a matching-coherent necessary test decide the remaining fixed-cover question?
The pooled graph has discarded the one-edge-per-slot constraint, so it
cannot answer that question. A feasible first step is to analyze the named
`Y40` obstruction of WITNESS.json while keeping those constraints, or exhibit a
compatible alternating cycle that repairs it without losing the other required
paths. Stop at a proved cut or an explicitly checked passing pairing. Neither
would supply the missing chronological, coefficient, restoration or cost ledger.
The structured question is in TASK.json. Family decision: retain this calibration
and stop. No further matching census or construction expansion follows from
the positive union result.

## Credit and engineering notes

Nick Petalas. Apache-2.0. Credit PR2981/2920/2909/2896 for the fixed covers and
PR2996 for the interval dependency test and explicit rematching handoff. Credit
Arham Tahir/PR2997 for the complementary exact-full-flag audit, and Adam Gall/2090
and Jeremy Diviney/2113 for earlier information-flow work. Retain Sudarsh
Chaturvedi/2924 and Sagar Thakrar's lifetime-floor handoff; Hiroki Kumazaki/2889/2353,
ywz65/2614, Arham Tahir/2675/2682 and Philippe Van Velzen for the monotone,
departure, budget and relay lineage. The original channel and geometry retain
Rohan Arun/1972, Chafik Boukhalfa/1991, Adam Gall/1940, Josie Elliston/1071,
Ali Romman/1125 and their native/compiler predecessors. No predecessor cover,
channel construction or lifetime bound is claimed as new.

Power of Ten inspection covers the three new Python files. Functions fit within
60 physical lines. Loops are bounded by 4,058 events, 104 endpoints, 208 matching
vertices, 2,309 virtual pairs, eight layers, 512 binary points or 374 quotient
subspaces. Each component visits at most 2,309 nodes; each alternating path has
at most 208 vertices. Tests use 60-second child timeouts. Explicit checks remain
enabled under optimization. Source reads are bounded at 2 MB.

Rule 3 deviation: Python allocates managed objects during checking. The fixed
domains bound every collection. A literal layer indexes at most `2309*155`
frames, each with at most 2,309 host bits and 512 membership bits. A resident
service would need fixed-capacity storage instead. Rules 8/9 deviation: the
literal mode loads one fixed package-local module through runpy; tests likewise
load fixed local files, and JSON uses one duplicate-key hook. No predecessor
implementation or arbitrary user-selected module executes. Package publication
checks, optimized replay, lint and warnings-as-errors compilation cover these
boundaries. An untrusted plugin service would require a static interface and
separate resource audit. No shared diagnostic configuration is changed.
