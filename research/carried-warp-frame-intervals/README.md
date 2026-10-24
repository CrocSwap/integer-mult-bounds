# Carried frame intervals for the PR4971 native word

This package computes sharp per-contact binary frame bounds for the weighted
field swaps of [PR4971](https://github.com/CrocSwap/integer-mult-bounds/pull/4971)
while also carrying frames through the actual invertible native warp maps.
It preserves the source's scalar word, helper boundaries and owned-cell contacts.
No new κ, physical phase admission or selected-frontier change is claimed.

The source is PR4971 head `0130b196145a43a7d305de41f49e56e8e8556378`, which
retains Cao Yifan's round-three word beyond PR4610. It is a different native word from the selected PR4470 supplier. PR4971 was
merged while this investigation was running; its retained source remains in
this branch’s ancestry. No separate pending-PR fetch is needed for a cold replay.

## What is established

[PROOF.md](PROOF.md) defines the exact binary schedule class and proves sharp
marginal bounds for every finite acyclic graph with invertible linear maps on
its edges. The graph propagates subspace sums forward and inverse-image
intersections backward. Every feasible contact frame lies between those bounds.
For each single contact, every intermediate subspace extends to a feasible
binary schedule by adding that prescription and propagating again. Different
contacts' choices remain coupled by the graph edges.

On the actual source, each orientation has:

- 15,935 graph vertices and 29,790 mapped edges;
- 14,671 scalar-contact vertices, of which 14,487 are variable;
- 13,148 rigid variable contacts and 1,339 flexible contacts;
- a maximum interval dimension difference of five.

The checker independently executes the source, the reconstruction from its
original contact labels, both extremal schedules and one strict intermediate
pinned frame. Every execution checks the 632 independent-input normalized
endpoints, all 408 arbitrary helper inputs, actual signed G-image warp frames,
scalar contacts, paid ranks and owned C0 clearing. The emitted schedules retain
534 weighted field swaps and 240 warp events per orientation.

The least and greatest schedules give no paid improvement. Their profiles are:

| Schedule | Rank 1 | Rank 2 | Rank 3 | Rank 4 | Rank 5 | Rank 8 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Source / original contacts | 2201 | 412 | 510 | 127 | 40 | 8 |
| Least frames | 2520 | 755 | 225 | 127 | 10 | 8 |
| Greatest frames | 2774 | 651 | 301 | 36 | 28 | 8 |

All have total paid rank 5,327. Exact min-rank cut differences show that the
source costs no more for every concave price f with f(0)=0, and costs strictly
less for every power price r^t with 0<t<1. This is an all-price comparison of
these profiles, not a numerical power sample. The proof uses the standard
discrete curvature decomposition of a concave sequence.

`RESULT.json` contains the complete interval dimension census, profiles,
integer cut differences and controls. It also records an exhaustive two-variable
three-bit example: all 256 subspace pairs are checked, six are feasible, and
all seven feasible marginal pins are extended constructively. Five toy controls
and four actual-word controls per orientation reject wrong map direction,
independently chosen incompatible marginals, an impossible pin, a changed fixed
node, a singular map, a false paid rank, false warp frames and lost swap frame
carry and an incorrect swap sign. The separate exact row replay imports no retained row primitives.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/carried-warp-frame-intervals --check-only
python3 -B scripts/research_package.py --package research/carried-warp-frame-intervals
python3 -I -OO -B research/carried-warp-frame-intervals/verify.py
```

The registered replay authenticates the seven live source files. Its retained
constructor runs in an isolated subprocess with an empty private bytecode-cache
namespace. `verify.py --write` regenerates the deterministic receipt.

`frame_dag.py` exposes `FrameDAG.bounds()` and `FrameDAG.extend(node, subspace)`.
`NativeSchedule(canonical, program)` builds the actual mapped graph, and
`realize(values)` emits the corresponding sufficient binary schedule with
strictly nested paid climbs. The implementation accepts ambient dimensions one through nine; this caller
uses nine. Frames are exact subspaces encoded as point bitsets.
The interval computations and registered proof replay use no floating-point
optimization. A separate optional numerical screen is recorded in
[discovery/README.md](discovery/README.md). It returned the source unchanged
after considering all 4,684 coupled marginal choices, without an exact global
optimality certificate.

## Scope and provenance

Only ascending live-field climbs, fixed scalar/weighted-swap order, fixed warp
maps, fixed helper/main entrances and exits, and fixed owned-cell contacts are
covered by the sharp bounds. The theorem includes every binary subspace in
that contract. It establishes no global price optimum over their coupled
assignments. The finite replays are normalized exact linear checks; physical
Clifford absolute phases, new whole-job lowering, all-column implementation,
movement, precision, the complete controller invoice and multiplication remain
separate obligations. The two losing extrema do not justify those larger runs.

Sources, Git blobs and SHA256 pins are in `SOURCES.json`. The catalogue and
selected record are historical provenance. The task card is explicitly changed
from historical four-provider admission to this carried-frame interface.
Canonical main was refreshed at `bee95ce88f9f19802f0613f92838895cd0e14a1f`, priority
revision 7. All seven scientific source files match that refreshed main byte
for byte. The scientific source pin remains the original PR4971 head. Overlap checks found PR4971 as the direct predecessor and PR340 as
older fixed-word free-form frame retiming. Earlier packages also enumerate local
frame intervals. This package applies the standard graph recurrence to the new
carried-swap/native-map contract; it claims no invention of lattice propagation
or concave-price comparison. Remote coverage and sparse local limits are recorded
in TASK.json, and no exhaustive novelty claim is made.

## Open next questions

The optional full coupled numerical screen returned the source unchanged; an
exact optimality certificate remains open. First test whether a stronger
local-pair LP permits a checkable rational dual, or name a changed native word,
map or boundary before another search. A favorable new profile is required
before physical phase and controller/compiler validation. No improving
assignment has been established. See TASK.json and discovery/README.md.

## Credit

Dugongue's PR4971 supplies the weighted frame-carrying swap construction and its
retained source. Cao Yifan supplies the round-three native word beyond PR4610.
Cinna Davis supplies the scalar/helper and selected-result lineage, including
PR4440/4470. Dugongue's PR4935/4948, zxv, Jacob Alan Sussman and the remaining
native/compiler authors retain their original credit in the source NOTICE.
The retained LICENSE and NOTICE are declared export inputs. James Reed's issue4571
motivates checking actual G-image warp events in the separate replay.

Prepared by 1337isnot1337 with substantial OpenAI Codex assistance, without
subagents. New material is Apache-2.0. This is written mathematics and exact
finite evidence, without formal-kernel or independent human acceptance.
