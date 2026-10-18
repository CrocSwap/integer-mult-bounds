# A sharp eight-query temporal cut in the native P104 itinerary

**Scoped obstruction, not a new supplier or exponent.** For the complete frozen
PR1972/PR1991 frame itinerary, even arbitrary additional common-frame linear
mixing at **all 4,059 chronological cuts** cannot raise the source-to-target
transfer rank above **eight arrays**. The original `G/2` channel attains eight.
Thus no zero-new-transport side correction can complete this itinerary to the
104-port identity. The selected result is unchanged.

This is not a terminal-cut estimate: additions may be inserted anywhere, and
all existing dirty helpers and private-copy lifetimes are included. Conversely,
new or retimed transports, new storage lifetimes and non-common-chart operations
are outside the theorem. In particular, the separately proposed terminal
`+208 H1` corrections are **not** excluded. The missing 96 array directions are
not a claim that 96 native children are necessary.

## Object and permitted relaxation

The source is Rohan Arun's [PR1972](https://github.com/CrocSwap/integer-mult-bounds/pull/1972),
head `fd82d172f46933fd253c2c6de4bd5eaff5429cfd`, as retained by Chafik
Boukhalfa's [PR1991](https://github.com/CrocSwap/integer-mult-bounds/pull/1991),
head `6e222517e182e98499239bc9a4009f540e1c5520`. Its exact 4,058-event witness is
SHA256 `0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e`.
There are 104 `X` sources, 104 `Y` targets, 32 `G` gather helpers, 32 `D` delivery
helpers and eight `Q` queries, with 280 arbitrary logical inputs in total.
The owned register `C` has eight separate allocate/copy/descend/discard lifetimes.

Fix every transport's register, position, old/new frame and native child rank,
and fix these private lifetimes. Permit an arbitrary finite number of linear
role operations among **all currently live registers with the same frame** at
every cut, not just the scalar additions in the witness. They may replace the
recorded additions, clear or mix dirty values and use the existing private
register when live. Restoring initial dirt is not imposed in the upper bound;
relaxing it only makes the exclusion stronger. The original attaining word does
restore all 72 arbitrary dirty helpers.

A frame is its exact binary subspace, computed by XOR closure, not its dimension,
its displayed basis or its register name. The compressed labels are those in
the witness; the invertible physical isometry in PR1991 preserves equality of
subspaces. No new native compiler or monomial-equivalence theorem is claimed.
Operations between different chart classes, even if someone could implement
one with free native wrappers, are not admitted by this common-chart theorem.

## Temporal graph certificate

At each cut make a complete directed graph on each common-frame class, with
register-preservation edges across events. A transport preserves its register's
logical information while changing which class it can join. Creation gives no
incoming information; erasure gives no outgoing information. COPY has a
source-to-destination edge. The reachability checker also preserves the old
COPY destination, a deliberately favorable relaxation of the zero-destination
contract. Arbitrarily many common-frame operations have exactly the same
possible causal edges as saturating each class once.

Cut `2429` is **after events 0 through 2428 and before event 2429**, the first
`D0` transport. Every original register is live, and `C` is not. Two complete
scans give:

| Cone at cut 2429 | Registers |
|---|---|
| Reachable from any initial `X` | all 104 `X`, 32 `G`, eight `Q` |
| Can reach any final `Y` | all 104 `Y`, 32 `D`, eight `Q` |
| Intersection | precisely `Q0,...,Q7` |

At this cut `X/G` are in the full frame, `Y/D` are in the zero frame, and the
queries occupy eight **distinct** rank-eight hyperplanes. The scans do not
infer disconnection merely from those cut frames: they include every earlier
and later class, including full-frame dirty helpers, and all eight private
lifetimes. Removing only the eight query wire crossings at this cut leaves
**no** final `Y` reachable from any initial `X`. Later source information can
reach full-frame `D/Q` registers; the scan retains it and still finds no target
path.

The verifier traverses all 4,059 cuts and 444 distinct frame subspaces. The
complete-class relaxation contains 106,254,468 directed common-frame edges
counted with their chronological occurrences, without allocating that entire
graph. It records both directional trace digests and the cut-deletion trace in
[RESULT.json](RESULT.json). These are reproducibility receipts, not substitutes
for the general argument below.

### Why the cut bounds every linear program in the domain

Fix an address space of finite dimension `d` over a characteristic-zero field.
A register carries one vector in that space; its native **frame dimension** and
the rank of a charged child are different notions. In particular, a rank-eight
query frame still carries **one** `d`-dimensional array, not eight independent
arrays or one scalar.

Set all initial non-`X` inputs to zero to isolate the `X -> Y` block. Every
causal path from an `X` input to a final `Y` crosses one of the eight query wires
at cut 2429. Therefore that linear block factors through their direct sum:

`X^(104d) -> (Q0,...,Q7)^(8d) -> Y^(104d)`.

Its rank is at most `8d`. One way to prove the factorization is to hold those
eight cut values fixed and set the direct source dependencies after the cut to
zero. The difference propagates only along paths avoiding the cut, and the
cut-deletion scan shows it cannot reach `Y`. This also accounts for all initial
dirty values: they affect the affine background but not this source derivative.
The reasoning covers arbitrarily many inserted linear operations; it does not
extrapolate a finite coefficient search.

The identity completion has source-to-target block `I_104 tensor I_d`, of rank
`104d`, so it is impossible in this domain. The full local bill is granted
before any cost comparison, and even arbitrary extra common-frame scalar work
is granted free. No moment root can repair this information deficit.

## Exact attainment and residual rank

The independent checker reconstructs all 120 E8 root lines in doubled integer
coordinates and removes the two pinned eight-line frames. With `R` the resulting
104-by-eight real root matrix and `G = R R^t`, it checks exactly

`R^t R = 26 I_8`, hence `G^2 = 26 G`.

It also replays all 280 input columns of the original word using exact rational
arithmetic, obtains `Y <- Y + (G/2) X`, closes every private lifetime and restores
all 72 dirty helper inputs and all source inputs. The source matrix in the
queries at the cut has rank eight. A `G/2` principal minor on port indices
`[0,1,2,3,7,14,22,33]` has determinant **1/256**. Consequently the rank-eight
upper bound is sharp, attained by the original dirty-restored channel, not by a
new construction claimed here.

The desired residual is not another rank-eight map. The same tight-frame
identity gives the exact inverse

`(I - G/2)^(-1) = I - G/24`,

so the standalone residual has full rank 104. The checker also checks all
10,816 entries of `G^2 = 26 G` and this inverse identity. This is an exact
algebraic statement, not a numerical eigenvalue test.

## Optimistic complete bill and boundary

The entire unchanged local profile is

`1074 H1 + 58 H2 + 86 H3 + 104 H4 + 48 H5 + 24 H6 + 8 H7 + 8 H8`,

with rank mass **2368 = 2312 boundary coverage + COPY56**, 2,624 recorded scalar
additions and eight allocate/copy/discard lifetimes. The tested completion
budget adds **zero** transports, copies or helper lifetimes and grants all
extra common-frame scalar work, hosting, idle remainder and precision cost
free. This deliberately favorable completion fails the exact communication
condition before a recursive moment is relevant. It would be misleading to
quote a root of this incomplete channel's histogram as an admitted supplier.

No physical lower bound for changed itineraries follows. In particular, the
96 missing directions are **not** converted into 96 child-rank units: a new
transport can change later class membership, which requires a new graph and a
complete invoice. Global ownership, all-size lifting, precision and the outer
multiplication theorem are not proved or replayed here. Native phase identities
are inherited from the pinned PR1991 source, not independently recompiled.

## Reproduce and evidence

Standard-library CPython 3.12, read-only by default, no network, no producer or
Clifford-compiler imports:

```sh
uv run --python 3.12 --no-project python -I -O -B research/p104-temporal-query-cut/verify.py
uv run --python 3.12 --no-project python scripts/research_package.py --package research/p104-temporal-query-cut
```

Default execution authenticates every declared live source, regenerates every
proof-relevant result and compares the complete canonical JSON payload with
`RESULT.json`. `--emit` prints the regenerated payload without that comparison.
The registered hook requests the optimized replay so checks cannot rely on
Python assertions.

Eleven semantic negative controls are exercised: leaving any one of the eight
queries uncut reopens a source-target path; a deliberately prohibited
cross-frame bypass reopens a target path; removing initial dirty-query
compensation or final query cleanup rejects the full endpoint identity. A
positive control reverses query basis order and preserves the exact frame.
The required source-bound baseline command also reported
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`; that is not a selected cold replay.

[TASK.json](TASK.json) records the pre-computation scope, budget, priority and
overlap limits. [SELECTION.json](SELECTION.json) preserves the single independent
selection with seed `5e89c7275a4bd70898735aea8ad1e35d`. Scientific base:
`564148b82ae9df72163f22106f15e73efca8aff2`, priority revision 4. The later
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2` checkpoint changed only workflow
guidance; the catalogue, selected record and scientific inputs are unchanged.

## Open next questions

1. **Change the transport itinerary rather than its scalar coefficients.** A
   first step is to identify a priced excursion or interleaving that moves source
   information around the eight-query separator. It matters because the zero-
   added-transport relaxation is now closed. The blocker is an actual native
   identity with restored frames and a complete hosting/precision bill.
2. **Extend the communication model to non-common-chart free native operations.**
   First characterize the exact logical operator carried by one proposed
   monomial-wrapped cross-chart addition. Its identity must be checked, not
   inferred from equal frame dimensions. Such operations may escape this graph;
   this package neither implements nor excludes them.

## Predecessors and attribution

Rohan Arun's PR1972 supplies the entire scalar/frame channel. Chafik Boukhalfa's
PR1991 supplies its native realization. Adam Gall's PR1940 supplies the
32-chain schedule; Josie Elliston's PR1071 supplies the P104 fixture, and Ali
Romman's PR1125 supplies the fixed-term carrier bound, with their retained
PR968/717/446/595/620 geometry lineage. No schedule, native recipe, geometry,
tight-frame identity or general linear cut lemma is claimed as newly invented.
The contribution is the source-bound sharp temporal cut under **all-cut arbitrary
common-frame mixing**, its exact attaining rank and explicit correction boundary.

The nearest active alternative at the initial live read was the terminal
`+208 H1` construction in discussion1167 comments
[18931708](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18931708)
and [18931718](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18931718).
Those proposals change the itinerary and are outside this result. The submission
read also inspected their successor [discussion2080](https://github.com/CrocSwap/integer-mult-bounds/discussions/2080):
it reports an author-checked finite correction, not a hosted supplier. The refreshed
snapshot covers 353 open PRs and 738 discussion/comment/reply records with complete
pagination; an offline query still warns about possible later changes. Cached and
targeted live/local checks are not a novelty or literature-priority guarantee.

Prepared by Adam Gall with substantial OpenAI Codex assistance. Apache-2.0.
No formal-kernel proof, independent human review or hosted CI pass is claimed.
