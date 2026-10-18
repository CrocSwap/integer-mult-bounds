# P104 joint unit-step endpoint flags

One shared collection of **208 abstract flags** simultaneously realizes
PR2920's prescribed source-departure and target-arrival subspace covers.
The exact compatibility graph has 2,309 edges and a perfect matching. Each
matched pair extends to a complete binary flag with dimensions zero through
nine. This closes the static joint-nesting part of [PR2920's handoff][2920].

This is a finite geometric certificate, not a 208-lifetime correction program.
It supplies no chronological acquisition, coefficient identity, relay dependency,
dirty restoration, native lowering, physical hosting or complete supplier bill.
The selected frontier is unchanged. In particular, it does not refute the
reported program-level 216/219/234 lifetime floors discussed in [PR2924][2924].
Those floors have stronger execution hypotheses and are not replayed here.

## Exact result and proof

Use the original 4,058-event P104 channel retained by PR1991, with immutable
sources X, unread targets Y and the frozen increasing data-frame paths. The
ordered 104 source labels are `l_s`; target hyperplanes are `H_t = ker(n_t)`
in the nine-dimensional binary label space. Reconstruct the correction support
from the ordered root Gram matrix and reconstruct residual demands from the
actual data paths. There are 4,656 residual demands in each orientation.

PR2920 supplies two fixed affine-complement covers at each endpoint. Its
`plane_cover` chooses the smallest odd-section functional q and the first
functional f maximizing proper-hyperplane capacity. The pair is f and f+q.
We use those exact deterministic choices, without searching other covers.
Both planes have dimension seven; their intersections with the endpoint's
residual demands are disjoint and cover all of them.

At source s, the two departure cover planes in the normal space are

```
V_s,i = ker(l_s) intersect ker(f_s,i).
```

Their annihilators are dimension-two frames
`A_s,i = span(l_s, f_s,i)`, containing the source line. At target t, the two
arrival frames are dimension-seven spaces

```
B_t,j = ker(n_t) intersect ker(h_t,j), contained in H_t.
```

Make a bipartite graph with 208 departure slots and 208 arrival slots. An edge
joins `(s,i)` to `(t,j)` exactly when `A_s,i` is contained in `B_t,j`. Equivalently,
all four binary pairings between `{l_s,f_s,i}` and `{n_t,h_t,j}` vanish.
A perfect matching uses every prescribed cover slot once in both orientations.

[CERTIFICATE.json](CERTIFICATE.json) retains that matching as 208 records with
source/target indices, cover choices and nine-vector ordered bases. The graph
has 2,309 edges, departure degrees between two and 26, and a perfect matching.
For each matched pair, start with a basis of A, extend it to B, then H, then
FULL. Prefix spans have dimensions zero through nine. Conversely, a nested
flag with these prescribed dimension-two and dimension-seven frames requires
A to be contained in B. Thus the graph encodes exactly this compatibility test.

The same collection realizes both endpoint covers. The departure normal spaces
are the annihilators of its dimension-two frames; its dimension-seven frames
are the arrival covers. All 9,312 endpoint demand incidences are covered.
This does not assert that a demanded source coefficient travels to its target.
A static flag has no event times or scalar operations.

There are 1,872 formal rank-one steps, nine per abstract flag. This matches the
unit-step histogram priced by PR2920, whose optimistic transport/idle screen
passes. That inherited screen is not recomputed or promoted to an executable
cost upper bound here. Reported stronger lifetime floors already distinguish
programs from this 208-flag static witness. The joint cheap-flag contradiction
in [PR2953][2953] concerns a different profile, 232 cheap and 191 broad
lifetimes, and is unchanged.

## Reproduce and verification limits

Python 3.12 or later, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-joint-unit-flags
```

Direct optimized read-only checks also work without Git or network:

```sh
python3.12 -I -O -Werror -B research/p104-joint-unit-flags/verify.py
python3.12 -I -O -Werror -B research/p104-joint-unit-flags/independent.py
python3.12 -I -O -Werror -B research/p104-joint-unit-flags/test_verify.py
```

The primary marker is
`PASS_P104_JOINT_UNIT_FLAGS helpers=208 edges=2309 rank_one_steps=1872`.
The word `helpers` counts abstract flag records. `verify.py --emit` prints the
complete regenerated certificate without writing files. Default verification
compares every serialized certificate field, with duplicate keys rejected.

The primary checker authenticates the original JSON inputs and PR2920 geometry
source before compiling that source directly, bypassing bytecode caches. It
reconstructs covers, the complete graph, an iterative augmenting-path matching
and every ordered basis. The independent checker imports neither that producer
nor predecessor geometry. It reconstructs paths and residuals using integer
bitmaps, checks actual subspace inclusion, every prescribed frame, a bijection
of endpoint slots and exact demand coverage. It also accepts a different valid
intermediate basis, demonstrating a semantic check rather than byte equality.
It validates the submitted cover spaces and their maximum capacities; the
primary checker binds PR2920's deterministic functional tie-break choices.

Eight behavioral groups cover both actual CLIs, exact emission, an alternative
valid basis, duplicate slots, source/arrival/dimension/independence faults,
missing cover information, false graph counts, augmenting paths and Hall
failure, Git-free read-only source exports, source corruption before execution,
poisoned bytecode, duplicate keys and Boolean/integer schema confusion.

Local registered CPython 3.12.15 replay and optimized CPython 3.14.8 checks pass.
A separate internal mathematical review reconstructed the graph, matching,
flags and covers. This is not independent human review or a formal-kernel
proof. Hosted CI is separate. No full channel/native replay, new lifetime floor,
precision, restoration, chronological hosting, consumer or all-size proof, or
selected cold replay is supplied. Exact pins are in [SOURCES.json](SOURCES.json);
[TASK.json](TASK.json) records scope, freshness and the canonical claim.

## Open next questions

Which additional dependency or chronological condition eliminates static flag
assignments that cannot be correction programs? A feasible first step is to
attach acquisition/delivery times and source-dependency requirements to one
named collection, respecting the reported program-level lifetime floors.
The 208-record witness is a calibration fixture for that stronger test, not a
candidate executable correction. Coefficients, arbitrary dirty restoration and
the full physical/consumer bill remain blockers. The structured question is in
TASK.json. Family decision: finish this interface certificate and stop; no
construction expansion or further count/price search is included.

## Credit and engineering notes

Nick Petalas. Apache-2.0. Substantial automated assistance was used in analysis,
implementation, internal review and writing. No independent human review is
claimed. No predecessor construction or endpoint theorem is claimed as new.

Credit Nick Petalas/PR2920/2909/2896 for the fixed covers and residual geometry,
PR2953 for the joint cheap-flag obstruction, Sudarsh Chaturvedi/PR2924 for the
reported lifetime-floor screen, Hiroki Kumazaki/PR2889/2353 for endpoint spans
and the monotone model, ywz65/PR2614 for later-read-aware departures, Arham
Tahir/PR2675/2682 for the coupled budget, Sagar Thakrar for the mixer handoff,
and Philippe Van Velzen for relay constructions and pricing. Retain Rohan
Arun/PR1972, Chafik Boukhalfa/PR1991, Adam Gall/PR1940, Josie Elliston/PR1071,
Ali Romman/PR1125 and their geometry/native/compiler lineage.

Build the Lever changed the deliverable to a regenerated matching and explicit
bases. Prove It Works required a separate semantic checker of the original
input paths and all prescribed frames. Unslop guided the written scope.

Power of Ten inspection covers these three new Python files. All functions
are below 60 physical lines. Loops are bounded by 4,058 events, 104 endpoints,
208 slots, nine dimensions or 512 vectors. Matching uses at most 208 searches,
208 visited vertices per search and 208 augmentation steps. Checks use explicit
exceptions and remain enabled under optimized Python. Tests have 20-second
subprocess timeouts. Frozen inputs and shared configuration are unchanged.

Rules 3, 8 and 9 deviations: Python allocates managed objects and the primary
checker loads one authenticated geometry module. Inputs are capped at 2 MB,
frames at 512 members, and the graph at 208 squared edges. The loader compiles
only SHA256-authenticated bytes with a fixed module target and bypasses cache
reads; the independent checker executes no external implementation. Source and
poisoned-cache controls verify that boundary. A resident or untrusted-input
service would need fixed-capacity storage and a static geometry interface.
Warnings-as-errors, source compilation and lint cover the new code; no
repository-wide diagnostic configuration is changed.

[2920]: https://github.com/CrocSwap/integer-mult-bounds/blob/b9ea9def949f9d71d59e21294d0e6cfbe0692a73/research/p104-endpoint-geometric-budget/README.md
[2924]: https://github.com/CrocSwap/integer-mult-bounds/blob/d1660ed0a17b66ad0c86cd4aaea724926134e362/research/p104-two-history-lifetime-floor/README.md
[2953]: https://github.com/CrocSwap/integer-mult-bounds/blob/47d75253af05075cef86e804d9a89b770dea5265/research/p104-joint-endpoint-obstruction/README.md
