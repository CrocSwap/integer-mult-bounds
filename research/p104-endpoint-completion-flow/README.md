# P104 dependency obstruction for all intermediate flag completions

Changing intermediate bases cannot turn PR2981's fixed 208 matched endpoint
pairs into an X-only monotone correction program. Even an optimistic dependency
graph leaves **3,095 of the 4,992 required coefficients unreachable**. For example,
the correction requires coefficient `-1/2` from `X4` into `Y0`, while every
permitted completion forces that added coefficient to zero.

This is a scoped obstruction for one named endpoint pairing. PR2981 correctly
certifies static covers, without claiming a correction program. Other pairings,
other endpoint planes, extra lifetimes and changed access contracts are outside
this result. No new lifetime floor, supplier or kappa follows.

## Contract and exact statement

Pin PR2981 `3d24b92d8ba057b57cb2d480170ec407520e6882` and its original
PR1972/1991 P104 data paths. For each of its 208 helper records retain only:

- Its dimension-one source line `L`, dimension-two departure plane `A`,
  dimension-seven arrival plane `B` and dimension-eight target hyperplane `H`.
- ZERO and FULL at dimensions zero and nine.

Allow any complete unit-step flag between these frames. In particular, each
dimension-three through dimension-six frame may be any `V` with `A <= V <= B`.
The published intermediate bases are discarded. The source and target indices
and both endpoint cover choices remain fixed. Changing bases within the same
endpoint spaces is included; changing the endpoint matching is not.

Retain PR2920/2353's X-only monotone correction contract. X is immutable and
available at its original visited frames. Y is unread and receives additions
at its original visited frames. New helpers have independent arbitrary dirty
entrances and increasing frames. Scalar operations are equal-frame linear
operations with fixed rational coefficients, including mixing, copies, clears
and rescalings. Transports preserve logical coefficient rows. There are no
additional lifetimes, source writes, target feedback, original helper/private
reads, descending transports or uncharged storage. Restoration is required by
the original contract, but is dropped in the relaxation below.

Under this contract, no choice of intermediate flags, scalar coefficients or
chronological interleaving realizes the prescribed additive correction `I-G/2`.
The independently checked finite predicate is missing directed support, before
coefficient magnitudes, restoration and physical implementation are considered.

## A necessary dependency graph

Make nodes `(helper, d)` for dimensions one through eight, with a directed
edge from each node to the next dimension of that helper. At each dimension,
grant a bidirectional contact between two helpers whenever some permitted
common frame exists. Inject source `s` at every node that could equal any
visited frame of `X_s`. Deliver to `Y_t` from every node that could equal any
visited frame of `Y_t`. Also include direct X-to-Y common-frame contacts.
The graph permits every visited data snapshot without checking its time.

At fixed dimensions the permitted interval is `[V,V]`. At intermediate
dimensions it is `[A,B]`. Two intervals `[A,B]` and `[C,D]` admit a common
dimension-d frame exactly when

```text
A <= D, C <= B, and dim(A+C) <= d <= dim(B intersect D).
```

Necessity follows from `A+C <= V <= B intersect D`. Conversely, those
containments and dimension bounds let a basis of `A+C` extend to d independent
vectors in `B intersect D`. Every resulting V can extend to a full flag within
each helper's fixed A and B. We grant contacts independently, even if one
helper could not realize their different frame choices in a single flag.
This makes the graph more permissive than any actual completion.

For a particular legal word, map each register state to its helper/dimension
node. A nonzero source coefficient initially exists only on its immutable X
input. A transport follows an upward edge. An equal-frame linear operation
can propagate a source only through a granted contact; a copy, clear or
rescaling cannot create a missing source coefficient. Induction over the
scalar word therefore puts each actual coefficient's support inside graph
reachability. Cancellation can remove support but cannot create a path.
Independent dirty inputs have zero coefficients on all X coordinates, so
dropping their eventual restoration cannot invalidate this necessary test.
Unread targets are sinks and cannot supply further dependencies.

The checker saturates connected contact components in each dimension, then
propagates upwards. It never propagates a late acquisition backwards. Dimension
zero has no X injection. Dimension nine has no Y delivery and no descending
edge, so neither omitted layer can create an additional source-to-target path.

## Finite evidence and checks

[RESULT.json](RESULT.json) retains every target's optimistic source support,
all layer counts and the exact missing-coefficient witness. Contacts at
dimensions one through eight number
`104, 23, 78, 141, 141, 91, 29, 104`. Of 4,992 nonzero entries of `I-G/2`,
1,897 have paths and 3,095 do not. A path is only a necessary condition;
the 1,897 reachable entries are not claimed constructively realizable.

The primary checker reconstructs the original 4,058-event X/Y paths and uses
the interval criterion. A separately implemented checker enumerates all 374
subspaces of each five-dimensional quotient `B/A`, lifts them to literal
binary frames and checks common-frame contacts directly. It independently
traces each source through the graph and compares the complete receipt.
Neither checker executes a predecessor implementation.

Behavioral controls check the contact criterion against every subspace interval
in a three-dimensional binary space, actual CLI replay, an upward relay,
forbidden backward flow, direct X-to-Y access, changed intermediate bases,
Git-free exports, source corruption, changed support masks, duplicate JSON keys
and Boolean/integer confusion. These controls test access semantics and the
real verifier boundary rather than a new multiplication construction.

The concurrent [fixed-full-flag audit][concurrent] concerns PR2981's exact
published intermediate bases. This contribution instead proves failure for
every intermediate completion of the same endpoint pairs. The two tests are
complementary. The reported program-level lifetime floors in PR2924 would
also exclude 208 helpers under their hypotheses; they are not replayed or
strengthened here. This explicit basis-sensitive test supplies a calibration
and a concrete failed dependency independently of those reported floors.

## Reproduce and verification limits

Python 3.12 or later, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-endpoint-completion-flow
```

Direct checks also work on a Git-free source export:

```sh
python3.12 -I -O -Werror -B research/p104-endpoint-completion-flow/verify.py
python3.12 -I -O -Werror -B research/p104-endpoint-completion-flow/independent.py
python3.12 -I -O -Werror -B research/p104-endpoint-completion-flow/test_verify.py
```

The primary marker is `PASS_P104_ENDPOINT_COMPLETION_FLOW required=4992
unreachable=3095 all_intermediate_completions no_new_kappa`.
`verify.py --emit` regenerates the receipt to stdout without changing files.
[SOURCES.json](SOURCES.json) pins exact input bytes and historical provenance;
[TASK.json](TASK.json) records scope, live overlap and verification environment.
Evidence is locally checked with independent internal arithmetic/code review,
without independent human review or formal-kernel proof. Hosted CI is separate.
No native replay, rounded producer, physical hosting, complete cost invoice,
all-size proof or selected cold replay is supplied or required by this scoped
support obstruction. Frozen scientific packages and selected inputs are unchanged.

## Open next questions

Does a different compatible endpoint matching pass this necessary contact
test? It matters because static containment alone did not ensure acquisition
for the published matching. A first step is to choose one explicitly named
alternative and evaluate this same optimistic graph before scalar synthesis.
The current proof does not show that every matching fails. Passing this test
would still leave joint flag consistency, chronological acquisition, exact
coefficients, arbitrary dirty restoration and the complete physical bill open.
Do not start another construction campaign from a path-only positive result.
The structured handoff is in TASK.json. Family decision: finish this calibration
and stop; no matching search or construction expansion is included.

## Credit and engineering notes

Nick Petalas. Apache-2.0. Substantial automated assistance in analysis,
implementation, internal review and writing is disclosed in TASK.json.
No independent human review is claimed.

Credit Nick Petalas/PR2981/2920/2909/2896 for the pinned covers and flags;
Arham Tahir's concurrent fixed-flag information-flow audit for the exact-basis
scope; Sudarsh Chaturvedi/PR2924 and Sagar Thakrar's mixer handoff for the
reported program-level floors; Hiroki Kumazaki/PR2889/2353 for the monotone
model; ywz65/PR2614 for departure access; Arham Tahir/PR2675/2682 for coupled
budgets; Philippe Van Velzen for relay constructions and pricing. Retain
Rohan Arun/PR1972, Chafik Boukhalfa/PR1991, Adam Gall/PR1940, Josie
Elliston/PR1071, Ali Romman/PR1125 and their geometry/native/compiler lineage.
No predecessor construction, cover theorem or lifetime floor is claimed as new.

Build the Lever changed the deliverable to a rerunnable necessary-condition
checker. Prove It Works required literal subspace enumeration independent of
the interval formula. Test Behavior, Not Implementation required positive
relay/direct-access cases alongside rejected controls. Unslop shaped the prose.

Power of Ten inspection covers only the new package's Python files. Loops are
bounded by 4,058 original events, 104 sources/targets, 208 helpers, eight useful
layers, nine basis vectors or 512 binary points. Each component search visits
at most 208 helper nodes. Checks remain enabled under optimized Python;
subprocess tests have 60-second timeouts and the registered commands are bounded.
Functions remain below 60 physical lines after formatting. No shared source or
repository diagnostic configuration is changed.

Rule 3 deviation: Python allocates managed objects while checking. The fixed
domains, 2 MB JSON limits and at most 208 helpers bound collections; a resident
service would require fixed-capacity storage. The independent checker retains
at most 376 frames per helper, 78,208 literal masks of at most 512 bits, and
1,664 graph vertices. Its 104 source traversals each queue at most 1,664 nodes.
Rules 8/9 deviation: tests load one local verifier through Python's module
loader; the registered runner gives it a fresh bytecode namespace. JSON parsing
uses one fixed duplicate-key callback. The two mathematical CLIs import only
standard library code and read three authenticated JSON inputs. A stricter
untrusted service would need a static module boundary and a separate capacity audit.
Ruff, warning-as-error compilation and optimized replay cover touched code.

[concurrent]: https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-18977808
