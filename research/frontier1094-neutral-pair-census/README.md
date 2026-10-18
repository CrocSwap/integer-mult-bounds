# Exact neutral-then-improving two-move census for PR1094

The selected PR1094 owner map admits exactly **78 two-relocation paths that
lower the idle moment after a neutral first move**. They lead to 78 distinct final bin
allocations and all have the same paid-profile change:

`-H1 - H7 + H8`.

There are 3,484 legal neutral first moves. Only 78 enable an improving second
move. Thus the result also characterizes every improving path of at most two
legal relocations whose idle moment never increases: the initial map has no improving
single relocation. This is an exact optimum for that neighborhood, for every
real `0 < a < 1`; it is not a global packing optimum or a new kappa claim.

PR1343 already establishes the single-relocation obstruction. PR1407 already
constructs longer neutral paths and a stronger conditional candidate. This
package adds the complete two-move census, all attaining paths, a second
enumeration method and a direct small-domain oracle. It claims no priority for
the neutral-path mechanism. The selected record and predecessor files are unchanged.

## Domain and result

Start from main `ebedc0895eb4c06725af020bc1af165722b0a3ce`, selected PR1094 at
`0fc329d0bec93ca7cd288eaea1295172e8789810`. The exact live inputs and historical
provenance are in [SOURCES.json](SOURCES.json); the random assignment, scope
refinement, overlap heads and claim link are in [TASK.json](TASK.json).

A relocation moves one complete helper to a distinct original child bin.
Helper width, invocation, call order, physical families and actual source-event
windows stay fixed. Surviving slices in an affected bin are compacted in their
original offset order, then incoming roles are appended. Every intermediate map
must satisfy the retained whole-helper owner rules. These moves edit an
allocation; they do not reorder the executed invocations.

The domain contains 69,120 roles, 144 calls and 32,256 positive-capacity child
bins. Its original idle profile is `{1:2276, 3:377, 7:7, 48:4866}`.

| First move: source free rank, width, destination free rank | Legal prefixes |
| --- | ---: |
| `0, 7, 7` | 2,640 |
| `3, 4, 7` | 844 |
| Total | 3,484 |

The baseline has 19 capacity-feasible concentrating moves, all illegal under
the fixed owner rules, corroborating PR1343. Exactly 78 neutral prefixes are
productive, with one improving continuation each. Each final idle profile is
`{1:2275, 3:377, 7:6, 8:1, 48:4866}`. Rank mass remains 1,041,408 and deficit
remains 5,120. [RESULT.json](RESULT.json) lists every attaining sequence and
binds both complete enumerations with canonical SHA256 digests.

The receipt's role indices refer to the zero-based frozen `OWNERS.json.gz`
array. Bin indices enumerate `(owner_replica, child, port)` in ascending order.
One witness moves role 46308, width 7, from `(1,15,86)` to `(13,15,14)`;
then role 34306, also width 7, from `(11,8,103)` to `(1,15,86)`. The first move
exchanges free ranks 0 and 7. The second replaces free ranks 1 and 7 with 8 and 0.

## Why the search and comparison are exact

Write `p = 1-a`, so `0 < p < 1`. Moving width `w > 0` from a bin with free
rank `x` into one with free rank `y >= w` replaces `(x,y)` by `(x+w,y-w)`.
Strict concavity of `t^p`, with fixed sum, makes the cost strictly decrease
exactly when `x+w > y`. Equality occurs exactly when `x+w = y`, which exchanges
the two free ranks. A zero remainder has zero cost. This proves the sign
uniformly in `a`, without floating-point comparisons or root-ordering assumptions.

The primary census first exhausts all legal neutral relocations. After moving
one role from bin A to bin B, any newly legal improving second move must have
at least one of the following properties:

1. Its source is A or B, whose free ranks and membership changed.
2. Its destination is A or B, whose available capacity changed.
3. It targets the original family of A at the first role's invocation, whose
   occupancy may have been released.

Every other move keeps the same source, destination free rank, time window and
family occupancy. Since no original legal move improves the cost, such a move
cannot newly improve it. Occupying B's family can only remove eligibility.
The primary enumerator takes the union of these three candidate sets and tests
every candidate against the current state. It counts paths, not heuristic nominees.

The second enumerator does not use this pruning argument or the primary move
mutator. After each independently enumerated neutral prefix it updates the
rank/width classes and exhausts **every** capacity-feasible concentrating
role/destination product. It tests concentration using the exact change in the
sum of squared free ranks. It checks 52,558 candidate pairs across the 3,484
prefixes and agrees on every path, count, profile and digest. Input decoding
and the retained geometry are shared; these are separate enumeration methods,
not wholly independent source or mathematical audits.

The two methods also agree with a direct full-state brute-force oracle on a
complete small domain: three bins with capacities 2 through 4, helper widths
`(1,2,1)`, the three family assignments and two invocation assignments listed in
`test_verify.py`, and every allowed-call mask containing the initial role.
There are 2,013 legal initial maps with no improving single move; 147 admit an
improving two-move path. The oracle reconstructs capacities and collisions for
every possible first and second move.

## Paid cost and verification boundary

At the pinned selected record the complex saving is
`67018507072324140917/40000000000000000000000`, below the bit saving
`1733427039589844234749/1000000000000000000000000`; the complex side binds.
These are the retained selected endpoints, not newly computed endpoints.
The local supplier profiles and bit supplier stay fixed. For the complex
main moment, with `m=73` and `W=14336`, every attaining allocation has the exact
change

`Delta M(a) = (8^(1-a) - 7^(1-a) - 1) / (14336 * 73^(1-a)) < 0`.

The strict sign follows from `8^p < 7^p + 1` for `0<p<1`. With the other
charges held fixed this is a strict invoice improvement. No new endpoint or
outer assembly is claimed: this package does not run the native word, chart,
emitted controller, prefix/row reserve, full invoice, two moment engines or
outer inequalities for these allocations. It does not adopt a supplier.

Upstream adopted priority revision 3 during this session. At submission commit
`81e81af67714bdc8d1693b0bf5c29468b92f62ff`, a separate call to the retained
`ceiling.ceiling(local, 73, 896, 9, 64)` gives primitive upper bound
`1690054109089/10^15` and conditional kappa cap
`1690054109089/1001690054109089`, approximately `0.001687202645325402`.
The selected kappa realizes about **99.1381%** of that upper bound. All census
maps keep the same local word and cap. Their new endpoint and realized fraction
are not computed. This contextual calculation, its exact fractions and source
hashes are recorded separately in TASK.json; it is not part of the census replay.
The original revision-2 task assignment is retained without rerolling.

Josie Elliston's retained PR1091 auditor checks the initial map and **all 156
intermediate and final maps** from the 78 paths, each with all 69,120 roles.
Its geometry, word-width and actual-window derivations are reused explicitly.
For modified maps, the proposed idle profile is recounted from the new state;
the frozen PLAN supplies its unchanged order and windows.
The audit digest and one full representative report are saved in RESULT.json.
The eleven inherited negative controls and the new source/receipt corruption,
family/window, identity-preservation and local-compaction controls run as well.
All rejection checks remain active under Python optimization.

First-step worsening, longer paths, simultaneous exchanges, different slice
conventions, split helpers, idle-axis transfers, changed windows or local words
are outside the census. Inherited all-size/compiler, common-label/mutable-source
realization, whole-call hosting, precision/tape, analytic-transfer and bit H1-H5
obligations remain. No full Lean theorem, independent human review or hosted CI
success is asserted.

## Reproduce

Python 3.12 and the standard library, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/frontier1094-neutral-pair-census
```

This runs the source-bound census and all owner checks, the optimized all-class
cross-check, and the controls. Each verifier compares its fresh result with the
committed receipt and does not overwrite it. Direct commands are in
[VERIFY.json](VERIFY.json). `verify.py --write /path/to/new.json` writes a new
proposed receipt and refuses an existing filename; it does not validate that
proposal against RESULT.json. Metadata provenance checking needs the pinned Git
objects; direct mathematical replay works from a source export containing the
listed inputs.

## Open next questions

What is the complete improving neighborhood with two neutral relocations and
then one strict relocation? The two-move census has only one improving profile,
while PR1407's longer paths reach different profiles. A first step is to
canonicalize and deduplicate neutral depth-two states, compare with PR1407's
pinned paths, and extend both enumerators. Complete state deduplication and a
bounded runtime need a separate argument. Check live overlap before starting;
[TASK.json](TASK.json) records the structured question and blocker.

## Credit and disclosure

Rohan Arun supplied PR1094; Jeremy Kothe supplied PR1087 and preceding owner
packing. Josie Elliston supplied PR1091's geometry and owner audit. Douglas
Colkitt applied it to the selected composition. Hao Yan / FanPUYen supplied the
PR858 controller and window semantics; the PR1018/987/1005 local construction,
PR589 bit supplier and their retained ancestry remain credited.

[PR1343](https://github.com/CrocSwap/integer-mult-bounds/pull/1343), by
Arham Tahir with OpenAI Codex assistance, supplies the one-move obstruction and
explicit neutral-path question; entry head `489f9011862dcd53a7785e151d3af0a1cd08250a`.
[PR1407](https://github.com/CrocSwap/integer-mult-bounds/pull/1407), by
@pai-scaffolde with the disclosed OpenAI and Claude assistance, supplies the prior 24-move,
eleven-path construction; entry head `d8640f5b7ae99b43f5d56146cb94ca62b8b3835d`.
This package imports neither pending PR's executable code.

Prepared for Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance in
selection, proof, implementation, checking and writing. Both enumeration
implementations were written by the same agent. New material is Apache-2.0.
