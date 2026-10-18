# Late source acquisition reduces the P104 three-target word to 92 helpers

**Finite logical construction and sharp scoped acquisition bound. No new κ.**

One dirty helper can collect X6, then X1, then X0 along their existing frame
paths. Replacing only the Y2-exclusive correction group of
[ywz65's PR2460](https://github.com/CrocSwap/integer-mult-bounds/pull/2460)
reduces the complete three-target word from **94 to 92 new helper lifetimes**.
All 372 arbitrary input columns, all 138,384 endpoint coefficients, every
literal frame transition, and the restoration of every logical dirty input
are checked. The other six correction groups and all original channel events
retain their exact order, cuts and coefficients.

Ten lifetimes are necessary and sufficient for this **isolated twelve-source,
X-only monotone correction**. This is not an unrestricted lower bound of 92 for
three targets, a completed 104-target supplier, or a new multiplication bound.
The predecessor is pending work, not the selected frontier.

The pre-submission refresh found concurrent
[ywz65 / PR2496](https://github.com/CrocSwap/integer-mult-bounds/pull/2496),
which supplies a 39-helper correction for **Y2 alone** using later source
access. We do not claim priority for that mechanism. The contribution here is
its distinct three-target composition question: retain the other six shared
groups, identify the correct exclusive source set, and attain the sharp
ten-helper minimum for that isolated branch. PR2496's proposed three-chain
handoff cannot simply replace the twelve exclusive acquisitions: eight of its
twelve later-compatible sources belong to other incidence groups. Its full
single-target result is compatible with, and does not imply, this branch bound.

## Result and complete finite bill

The original native-channel witness has 4,058 events and 280 independent inputs.
The correction completes Y0, Y1 and Y2 as `Yt <- yt + xt`; the other 101 targets
retain the original `yt + (Gx)t/2` channel. Original X and all dirty helper
logical inputs are restored in their prescribed final frames. Eight original
owned private-copy lifetimes are inherited, with their allocate/copy/descend/
discard contract; no new clean register, private copy, or erasure is used.

| Quantity | PR2460 literal word | Initial-line direct control | New late-source word |
|---|---:|---:|---:|
| New helper lifetimes | 94 | 94 | **92** |
| Added logical ADDs | 532 | 521 | **517** |
| Added source reads, including cleanup | 180 | 180 | 180 |
| Added nested transports | 287 | 287 | **283** |
| Added dimension-gap rank mass | 846 | 846 | **828** |
| Full event count | 4,877 | 4,866 | **4,858** |
| Full dimension-gap rank mass | 3,214 | 3,214 | **3,196** |
| Independent input columns | 374 | 374 | 372 |

The direct control replaces the old exclusive group's optional gather/uncompute
by twelve independent deliveries. It is separately replayed, so the claimed
late-access mechanism does not take credit for that simpler 11-ADD reduction.
Late access itself saves **two lifetimes, 18 rank units, four ADDs and four
transports** relative to this control; it saves 15 ADDs relative to the literal
predecessor. No scalar or rank-profile optimality is asserted.

The added profile is

`146 H1 + 38 H2 + 7 H3 + H4 + 8 H5 + 40 H6 + 43 H7`.

The full profile is

`1220 H1 + 96 H2 + 93 H3 + 105 H4 + 56 H5 + 64 H6 + 51 H7 + 8 H8`.

Here Hr is an abstract nested frame transport of dimension gap r. These are
complete **finite local** counts, not global owner/idle/residual invoices or
physical scalar-operation counts. Maximum ideal logical row l1 is 106 and
maximum coefficient denominator is 4, unchanged from the original channel.
Neither quantity is a physical roundoff or recursive-precision proof.

## The source-set correction matters

Reconstructing the exact roots and `C = I-G/2` gives the actual Y2-exclusive set

`{0,1,3,6,8,11,16,19,25,28,97,99}`.

The sources with a later frame still contained in H2 are instead

`{0,1,3,6,7,12,15,20,24,29,96,100}`.

Their intersection is **{0,1,3,6}**. PR2460's README at the pinned head says the
second set is exactly the exclusive set. Its circuit and verifier distinguish
the sets correctly; that sentence in the prose does not. We reproduce the
94-helper circuit successfully and do not claim that this wording discrepancy
invalidates its restricted construction or collector-rank proof.

The first pilot followed the prose and found three paths for the wrong set.
It was rejected before packaging. RESULT.json records the correct two sets,
all twenty exclusive-source contact intervals, and the ten-path result.

## Construction and chronology

Cuts count completed events of the **original** 4,058-event channel. All new
operations at cut k execute before original event k, using zero-based indices.
The shared helper has arbitrary dirty logical value d and follows:

| Original cut | Source | Source frame basis | Dimension | Capture coefficient |
|---:|---|---|---:|---:|
| 0 | X6 | `[200]` | 1 | -1/2 |
| 669 | X1 | `[3,8,64,128,288]` | 5 | -1/2 |
| 842 | X0 | `[3,8,32,64,128,256]` | 6 | -1/2 |

These frames form a strict inclusion chain inside H2. The valid source-cut
intervals are respectively `[0,558]`, `[669,865]`, and `[842,1075]`.

At cut 0, subtract d from Y2 in the ZERO frame. The helper starts at ZERO,
climbs to X6's line, and captures `-x6/2`. At the two interior cuts it climbs
and captures `-x1/2` and `-x0/2`. At cut 4058 it climbs to H2, delivers
`d-(x6+x1+x0)/2` into Y2, climbs to FULL, and adds back each of the three
half-sources there. Its logical dirty value is restored. The original word
never reads a Y register and never changes an X logical value, so the initial
dirty compensation and delayed captures have the stated meanings.

The remaining nine exclusive sources each use the same ordinary one-source
scheme. No helper in this replacement reads an original G/Q/D/private role,
another correction group, or a Y input. The six retained groups are compared
literally with the pinned predecessor, not assumed equivalent from counts.

For the exclusive branch, twelve initial-line direct helpers cost
`24 H1 + 12 H7`, rank mass 108, and 48 ADDs. The ten-path construction costs
`21 H1 + H2 + H4 + 9 H7`, rank mass 90, and 44 ADDs. Every helper's boundary
transport telescopes from ZERO to FULL and is charged. For any common positive
child weighting `r^q`, `0 <= q <= 1`, the old-minus-new transport bill is

`3 + 3*7^q - 2^q - 4^q >= 3 + 7^q > 0`.

This is a favorable, fully charged **local** comparison before construction;
it is not a completed recursive moment. Global stock, hosting, idle work,
address/scalar lowering and the other 101 corrections remain unpriced here.
The experiment's target was to reduce this fixed partial word, not to promise
a stronger κ or to pass the full-supplier acceptance gate.

## Why ten acquisition lifetimes are necessary

The theorem concerns a correction submodule whose new helpers start with
source-independent arbitrary dirt, read original X registers on their frozen
paths, and move only upward through binary frames. ADDs require equal frames.
It may mix its own helpers, repeat source reads, and use arbitrary rational
coefficients independent of the inputs. Original registers cannot be written
by the submodule except for additive updates to Y2; the original transcript
and its frame paths stay fixed. Original G/Q/D/private roles and Y values are
unavailable as sources, and the other six correction groups are fixed and inaccessible.
Every new initialization or reset counts as a new lifetime. The submodule must
add exactly the twelve-source exclusive row to Y2. ZERO-to-FULL exits are an
additional premise for the rank-mass conclusion.

1. Each of the twelve required X inputs has a nonzero correction coefficient
   and is independent of every initial helper input. A dependence path from
   that X input to the added Y2 output must therefore start with an X read.
2. Along such a path, helper frame transport is monotone and an ADD connects
   equal frames. A contributing X read must consequently occur inside H2.
   The full original transcript determines every possible such source frame;
   there are twenty intervals. Direct X-to-Y2 equal-frame access does not occur
   at any original cut (separately checked).
3. The ten sources
   `{1,3,8,11,16,19,25,28,97,99}` have **pairwise incomparable available frames**:
   for any two different sources, neither frame is contained in the other,
   for every choice of their available frames. All 45 source pairs and 84
   frame pairs have explicit two-direction noncontainment witnesses.
4. One monotone helper lifetime cannot perform contributing acquisitions from
   two of these ten sources. Relaying or cancelling acquired information
   cannot eliminate their first acquisitions. Hence at least ten lifetimes
   are required. This argument covers arbitrary-length programs under the
   stated contract; it is not inferred solely from a bounded program search.
5. The literal construction uses ten. Under ZERO-to-FULL dimension-gap billing,
   each costs nine rank units by telescoping, so the branch's rank-mass minimum
   is also exactly 90.

An exact earliest-finish dynamic program corroborates the premise independently
of a program-length cutoff. It covers all 4,095 nonempty subsets of the twelve
sources over all twenty contact intervals. There are 28 reachable subset/last-
contact states and 17 one-helper source sets: twelve singletons, four pairs,
and the single triple `{0,1,6}`. Exact set-cover minimization returns ten.
Earlier arrival at the same final contact dominates later arrival because
waiting is allowed; skipped transports can be replaced by a direct upward
transport. These facts justify the finite state reduction. The antichain proof,
not this search alone, is the arbitrary-length lower bound.

Allowing the other groups to share acquisitions, changing original frame paths,
reading original helpers, downward transports, or a different lifetime contract
changes the theorem. No unrestricted 92-helper optimum is claimed.

## Reproduce

Python 3.12 and its standard library; no third-party packages or network needed:

```sh
python3.12 -B scripts/research_package.py --package research/p104-late-y2-acquisition-s34
```

Expected result: the primary marker reports `paths=10 helpers=92 adds=517
rank_mass=828 endpoint_coefficients=138384`; the independent audit reports a
10-source antichain, 84 frame pairs and zero direct contacts; the package runner
ends with `PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=completed`.

The primary replay uses sparse rational rows and enumerated binary subspaces.
The second implementation uses dense dyadic integer rows, Gaussian elimination
on binary bases, and the full 240-root construction. It imports neither the
producer nor the primary verifier, and independently compares every endpoint
coefficient and every receipt field for the original, predecessor and candidate
words. Both were written with AI assistance by the same contributor.

The primary ten rejecting controls remove compensation, capture, delivery or
cleanup; reverse a coefficient; move a capture outside its legal interval;
undercharge transport; break a FULL exit; or make antichain frames comparable.
The second checker independently rejects four circuit faults and accepts nearby
legal cuts. Equivalent frame bases and the twelve-helper initial-line floor are
positive controls. `test_verify.py` adds source-export and file-corruption checks.
Default verification is read-only and refuses missing or changed evidence.
`--regenerate` compares the complete parsed circuit, not a compressed container.

Direct commands are `python3.12 -I -O -B research/p104-late-y2-acquisition-s34/verify.py --regenerate`
and `python3.12 -I -O -B research/p104-late-y2-acquisition-s34/independent.py`.
No proof assistant, full selected-frontier cold replay, native phase/address
compiler, reverse-orientation admission, global owner/idle/residual invoice,
physical precision/tape proof or hosted CI pass is claimed.

## Provenance and credit

Exact base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
OS assignment seed **34**, complex-supplier track. The repository chooser was
run with the fixed complex track and zero-padded hexadecimal seed `22`.
The selected κ remains `836330098538459/500000000000000000`.

Direct construction predecessor: **ywz65 / PR2460**, head
`a0030819c6d0e89e133cd3e52cc748035d58e3c7`.
Its `research/p104-third-target-collector-rank/CIRCUIT.json` is retained unchanged
as `inputs/PR2460-CIRCUIT.json`, SHA256
`ce1b033ae8b826eec87d70246a13a6034e177ef4863bf7f7c24631c79e5202c9`.
The local replay requires no fetch of that pending branch. Its one-collector
per-target rank argument and six retained groups are not claimed new.

Credit **Ross Richardson / PR2445**, head
`6def43ad673b91dbd491389964d1dcd059bf2ac2`, for the two-target construction and
third-target sharing handoff. Concurrent **ywz65 / PR2496**, head
`f13badee663016e3e487e5183cc3cb03cd474cf4`, provides the single-Y2 late-access
construction and explicitly asks about composition with the three-target word.
Its README, task, circuit metadata and replay manifest were inspected at the
final overlap checkpoint; its own replay was not run and it is not a runtime
dependency. Credit **commdata2338 / PR2393**, **Hiroki Kumazaki /
PR2353** and **Philippe Van Velzen** for the relay/acquisition contract and
lifetime distinction. The native channel is **Rohan Arun / PR1972**, with
**Chafik Boukhalfa / PR1991** native realization, **Adam Gall / PR1940** schedule,
**Josie Elliston / PR1071** fixture, **Ali Romman / PR1125**, and the retained
PR968/717/446/595/620 lineage. Original notices remain in their packages.

SOURCES.json records the exact original-word and fixture pins. TASK.json records
selection, the corrected source-set premise, local-only claim and overlap limits.
Overlap used public HTML and Git under the initial access restriction; hidden
discussion comments and unindexed/new work may be missed. Absence of a match is not a
novelty guarantee. No upstream file, selected record or frozen ancestor is edited.

Prepared for **@CubeJerry**, with substantial **OpenAI Codex assistance** in
mathematics, code, testing and writing. New work is Apache-2.0, as is the retained
PR2460 artifact. No independent human review or formal-kernel proof is claimed.

## Open next questions

- Can cross-group sharing lower the 92-helper total? Start with the eight
  sources in the {0,1,2} group and its Y2 collector, testing chronological
  contacts against the four later-accessible exclusive sources. The groups
  must retain their other two outputs and restore arbitrary dirt; the isolated
  ten-lifetime theorem does not settle that changed interface.
- Can this exact word receive native phase/scalar/address admission and then
  a useful global bill? Compile its 283 new transports, keep every source read
  at the recorded cut, and price owners and idle/residual children. The original
  channel's native proof and two-target PR2454/2458 evidence do not automatically
  admit this different three-target circuit. The remaining 101 corrections and
  inherited all-size, precision, hosting and analytic obligations still block
  any supplier or κ claim.
